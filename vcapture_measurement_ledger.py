#!/usr/bin/env python3
"""
VCapture Measurement Ledger System v1.0
======================================

Canonical measurement schema for calibration-quality dataset generation.
Transforms promoter replicate manifests into a structured ledger with:

1. Rich Metadata Capture:
   - Per-run: promoter_id, replicate_index, backend, job_id, shots, transpiled_depth, layout
   - Measured/predicted/calibrated phi values with residuals
   - Timestamps, queue_time, circuit_duration, calibration_version
   
2. Experiment Context Fields:
   - panel_id, manifest_id, calibration_type, offset_model_version
   - pass_manager_version, calibration_method (raw/backend/biomimetic)

3. Variance Structure Analysis:
   - Within-promoter variance (replicate stability)
   - Between-promoter separation (identity recoverability)
   - Residual variance (calibration effectiveness)

4. Cross-Backend Transferability:
   - Train on source backend, test on target backend
   - Residual mean shift, spread change, ranking stability
   - Portability assessment

5. Mixed-Effects Model Formulation:
   - phi ~ promoter + backend + promoter:backend + calibration_offset
   - Separates identity, hardware, and interaction effects

Usage:
    python vcapture_measurement_ledger.py --manifest raw_hardware/promoter_replicate_schedule_manifest.json
"""

import argparse
import json
import hashlib
from collections import defaultdict
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union
import warnings

import numpy as np
from scipy import stats
from scipy.stats import f as f_dist
import pandas as pd


# ─────────────────────────────────────────────────────────────────────────────
# VCAPTURE SCHEMA v1.0
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class VCaptureRecord:
    """
    Canonical measurement record for calibration-quality dataset.
    
    Schema follows the layered provenance pattern with full experiment context.
    One row per execution event - the fundamental unit of analysis.
    """
    # ═══════════════════════════════════════════════════════════════════════════
    # IDENTITY FIELDS (immutable)
    # ═══════════════════════════════════════════════════════════════════════════
    record_id: str                          # Unique identifier
    promoter_id: str                        # Gene/promoter identifier
    replicate_index: int                    # Replicate number (1-indexed)
    backend: str                            # Quantum backend name
    
    # ═══════════════════════════════════════════════════════════════════════════
    # EXECUTION PARAMETERS
    # ═══════════════════════════════════════════════════════════════════════════
    shots: int                              # Number of measurement shots
    transpiled_depth: Optional[int] = None  # Circuit depth after transpilation
    qubit_layout: List[int] = field(default_factory=list)  # Physical qubit mapping
    
    # ═══════════════════════════════════════════════════════════════════════════
    # RAW LAYER (immutable audit trail)
    # ═══════════════════════════════════════════════════════════════════════════
    predicted_phi: float = 0.0              # Theoretical phi value
    measured_phi: Optional[float] = None    # Raw instrument reading
    
    # ═══════════════════════════════════════════════════════════════════════════
    # DERIVED LAYER (calibrated values)
    # ═══════════════════════════════════════════════════════════════════════════
    backend_calibrated_phi: Optional[float] = None      # After backend offset
    promoter_backend_calibrated_phi: Optional[float] = None  # After promoter-backend offset
    calibrated_phi: Optional[float] = None              # Final calibrated value
    residual: Optional[float] = None                    # measured - predicted (raw)
    calibrated_residual: Optional[float] = None         # calibrated - predicted
    
    # ═══════════════════════════════════════════════════════════════════════════
    # OFFSET TRACKING (explicit transformation parameters)
    # ═══════════════════════════════════════════════════════════════════════════
    backend_offset_applied: float = 0.0
    promoter_backend_offset_applied: float = 0.0
    calibration_offset_applied: float = 0.0
    calibration_source: str = "none"  # none, backend_default, promoter_specific, unified_reference
    
    # ═══════════════════════════════════════════════════════════════════════════
    # EXPERIMENT CONTEXT (required for variance decomposition)
    # ═══════════════════════════════════════════════════════════════════════════
    panel_id: str = ""                      # Panel identifier
    manifest_id: str = ""                   # Source manifest ID
    calibration_type: str = "raw"            # raw, backend_calibrated, biomimetic_calibrated
    offset_model_version: str = "1.0"        # Version of offset model used
    pass_manager_version: str = ""           # Qiskit pass manager version
    calibration_method: str = "replicate_aware_mean_offset"
    
    # ═══════════════════════════════════════════════════════════════════════════
    # TIMESTAMPS
    # ═══════════════════════════════════════════════════════════════════════════
    timestamp: Optional[str] = None         # Measurement timestamp
    job_id: Optional[str] = None            # IBM Quantum job ID
    queue_time: Optional[float] = None      # Time in queue (seconds)
    circuit_duration: Optional[float] = None  # Execution duration (seconds)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # QUALITY METRICS
    # ═══════════════════════════════════════════════════════════════════════════
    entropy: Optional[float] = None         # Shannon entropy
    fidelity: Optional[float] = None        # Quantum fidelity
    coherence: Optional[float] = None       # Coherence metric
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PROVENANCE
    # ═══════════════════════════════════════════════════════════════════════════
    calibration_version: str = "1.0"
    calibration_scope: str = "none"         # none, backend, promoter_backend, unified
    calibration_reference_backend: str = "ibm_fez"
    
    def to_dict(self) -> Dict[str, Any]:
        """Export as flat dict for DataFrame compatibility."""
        return asdict(self)
    
    def to_layered_dict(self) -> Dict[str, Any]:
        """Export with layered structure for JSON clarity."""
        return {
            # Identity
            "record_id": self.record_id,
            "promoter_id": self.promoter_id,
            "replicate_index": self.replicate_index,
            "backend": self.backend,
            # Execution
            "shots": self.shots,
            "transpiled_depth": self.transpiled_depth,
            "qubit_layout": self.qubit_layout,
            # Raw layer
            "raw": {
                "predicted_phi": self.predicted_phi,
                "measured_phi": self.measured_phi,
            },
            # Derived layer
            "derived": {
                "backend_calibrated_phi": self.backend_calibrated_phi,
                "promoter_backend_calibrated_phi": self.promoter_backend_calibrated_phi,
                "calibrated_phi": self.calibrated_phi,
                "residual": self.residual,
                "calibrated_residual": self.calibrated_residual,
            },
            # Offsets applied
            "offsets": {
                "backend_offset_applied": self.backend_offset_applied,
                "promoter_backend_offset_applied": self.promoter_backend_offset_applied,
                "calibration_offset_applied": self.calibration_offset_applied,
                "calibration_source": self.calibration_source,
            },
            # Experiment context
            "context": {
                "panel_id": self.panel_id,
                "manifest_id": self.manifest_id,
                "calibration_type": self.calibration_type,
                "offset_model_version": self.offset_model_version,
                "pass_manager_version": self.pass_manager_version,
                "calibration_method": self.calibration_method,
            },
            # Timestamps
            "timestamps": {
                "timestamp": self.timestamp,
                "job_id": self.job_id,
                "queue_time": self.queue_time,
                "circuit_duration": self.circuit_duration,
            },
            # Quality metrics
            "quality": {
                "entropy": self.entropy,
                "fidelity": self.fidelity,
                "coherence": self.coherence,
            },
            # Provenance
            "provenance": {
                "calibration_version": self.calibration_version,
                "calibration_scope": self.calibration_scope,
                "calibration_reference_backend": self.calibration_reference_backend,
            },
        }


# ─────────────────────────────────────────────────────────────────────────────
# VARIANCE STRUCTURE DATA CLASSES
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class PromoterBackendSummary:
    """Summary statistics for a promoter-backend pair."""
    promoter_id: str
    backend: str
    replicate_count: int
    mean_measured_phi: float
    std_measured_phi: float
    mean_calibrated_phi: float
    std_calibrated_phi: float
    mean_residual: float
    residual_mad: float  # Median absolute deviation
    signal_to_separation: float  # Distance to nearest promoter / pooled std
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class VarianceDecomposition:
    """
    Variance structure decomposition for calibration analysis.
    
    Decomposes variance into three practical pieces:
    1. Within-promoter variance: measurement stability across replicates
    2. Between-promoter variance: identity recoverability above noise
    3. Residual variance: calibration model effectiveness
    """
    # Within-promoter variance (replicate variability)
    within_promoter_variance: Dict[str, float] = field(default_factory=dict)
    within_promoter_mean: float = 0.0
    within_promoter_std: float = 0.0
    
    # Between-promoter variance (promoter separation)
    between_promoter_variance: Dict[str, float] = field(default_factory=dict)
    between_promoter_mean: float = 0.0
    between_promoter_std: float = 0.0
    
    # Residual distributions (after calibration)
    residual_distribution: Dict[str, Dict[str, float]] = field(default_factory=dict)
    residual_mean: float = 0.0
    residual_std: float = 0.0
    
    # Backend-specific variance components
    backend_variance_components: Dict[str, float] = field(default_factory=dict)
    
    # Promoter-backend summaries
    promoter_backend_summaries: List[PromoterBackendSummary] = field(default_factory=list)
    
    # Signal-to-separation statistics
    separation_matrix: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "within_promoter_variance": self.within_promoter_variance,
            "within_promoter_mean": self.within_promoter_mean,
            "within_promoter_std": self.within_promoter_std,
            "between_promoter_variance": self.between_promoter_variance,
            "between_promoter_mean": self.between_promoter_mean,
            "between_promoter_std": self.between_promoter_std,
            "residual_distribution": self.residual_distribution,
            "residual_mean": self.residual_mean,
            "residual_std": self.residual_std,
            "backend_variance_components": self.backend_variance_components,
            "promoter_backend_summaries": [s.to_dict() for s in self.promoter_backend_summaries],
            "separation_matrix": self.separation_matrix,
        }


@dataclass
class TransferabilityReport:
    """
    Cross-backend calibration transferability report.
    
    Tests portability by fitting offset on source backend
    and applying unchanged to target backend.
    """
    source_backend: str
    target_backend: str
    
    # Source backend statistics
    source_offset: float
    source_variance: float
    source_sample_count: int
    
    # Transfer metrics
    rmse_with_source_offset: float
    rmse_with_native_offset: float
    transfer_efficiency: float  # 1.0 = perfect transfer
    
    # Residual analysis
    residual_mean_shift: float  # Mean residual change after transfer
    residual_spread_ratio: float  # Std ratio (target/source)
    
    # Ranking stability
    promoter_ranking_correlation: float  # Spearman correlation
    ranking_preserved: bool
    
    # Overall assessment
    is_portable: bool
    portability_score: float
    recommendation: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MixedEffectsResult:
    """
    Mixed-effects model results for variance decomposition.
    
    Model: phi ~ promoter + backend + promoter:backend + calibration_offset
    Separates identity, hardware, and interaction effects.
    """
    # Fixed effects
    promoter_effects: Dict[str, float] = field(default_factory=dict)
    backend_effects: Dict[str, float] = field(default_factory=dict)
    interaction_effects: Dict[Tuple[str, str], float] = field(default_factory=dict)
    
    # Variance components
    promoter_variance: float = 0.0
    backend_variance: float = 0.0
    interaction_variance: float = 0.0
    residual_variance: float = 0.0
    
    # Model statistics
    r_squared: float = 0.0
    adjusted_r_squared: float = 0.0
    f_statistic: float = 0.0
    p_value: float = 0.0
    
    # Effect significance
    promoter_significant: bool = False
    backend_significant: bool = False
    interaction_significant: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "promoter_effects": self.promoter_effects,
            "backend_effects": self.backend_effects,
            "interaction_effects": {f"{k[0]}:{k[1]}": v for k, v in self.interaction_effects.items()},
            "variance_components": {
                "promoter": self.promoter_variance,
                "backend": self.backend_variance,
                "interaction": self.interaction_variance,
                "residual": self.residual_variance,
            },
            "model_statistics": {
                "r_squared": self.r_squared,
                "adjusted_r_squared": self.adjusted_r_squared,
                "f_statistic": self.f_statistic,
                "p_value": self.p_value,
            },
            "significance": {
                "promoter_significant": self.promoter_significant,
                "backend_significant": self.backend_significant,
                "interaction_significant": self.interaction_significant,
            },
        }


# ─────────────────────────────────────────────────────────────────────────────
# VCAPTURE LEDGER CLASS
# ─────────────────────────────────────────────────────────────────────────────

class VCaptureLedger:
    """
    Canonical measurement ledger for calibration-quality dataset.
    
    Transforms promoter replicate manifests into structured analysis-ready format.
    """
    
    def __init__(self, 
                 calibration_version: str = "1.0",
                 offset_model_version: str = "1.0",
                 pass_manager_version: str = "1.0"):
        self.calibration_version = calibration_version
        self.offset_model_version = offset_model_version
        self.pass_manager_version = pass_manager_version
        
        self.records: List[VCaptureRecord] = []
        self.variance_decomposition: Optional[VarianceDecomposition] = None
        self.transferability_reports: List[TransferabilityReport] = []
        self.mixed_effects_result: Optional[MixedEffectsResult] = None
        
        # Cached indices for fast lookup
        self._by_promoter: Dict[str, List[int]] = defaultdict(list)
        self._by_backend: Dict[str, List[int]] = defaultdict(list)
        self._by_promoter_backend: Dict[Tuple[str, str], List[int]] = defaultdict(list)
    
    def load_from_manifest(self, manifest_path: Path) -> int:
        """
        Load records from a promoter replicate schedule manifest.
        Returns number of records loaded.
        """
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        manifest_id = manifest.get('manifest_type', 'unknown')
        panel_id = manifest.get('panel_id', 'unknown')
        
        records_loaded = 0
        for run in manifest.get('scheduled_runs', []):
            planned = run.get('planned_metrics', {})
            observed = run.get('observed_metrics', {})
            execution = run.get('execution', {})
            
            record_id = run.get('run_id', f"{run.get('promoter_id')}_{run.get('backend')}_r{run.get('replicate_index')}")
            
            record = VCaptureRecord(
                record_id=record_id,
                promoter_id=run.get('promoter_id', ''),
                replicate_index=run.get('replicate_index', 0),
                backend=run.get('backend', ''),
                shots=run.get('shots', 8192),
                transpiled_depth=execution.get('transpiled_depth'),
                qubit_layout=execution.get('qubit_layout', []),
                # Raw layer
                predicted_phi=planned.get('predicted_phi', 0.0),
                measured_phi=observed.get('measured_phi'),
                # Derived layer (populated by calibration)
                residual=observed.get('residual'),
                # Experiment context
                panel_id=panel_id,
                manifest_id=manifest_id,
                calibration_type="raw",  # Will be updated by calibration
                offset_model_version=self.offset_model_version,
                pass_manager_version=self.pass_manager_version,
                # Timestamps
                timestamp=observed.get('timestamp') or execution.get('submitted_at'),
                job_id=execution.get('job_id'),
                # Quality metrics
                entropy=planned.get('entropy_shannon'),
                fidelity=planned.get('phi_alignment_score'),
                # Provenance
                calibration_version=self.calibration_version,
                calibration_reference_backend=manifest.get('reference_backend', 'ibm_fez'),
            )
            
            self._add_record(record)
            records_loaded += 1
        
        return records_loaded
    
    def _add_record(self, record: VCaptureRecord):
        """Add record and update indices."""
        idx = len(self.records)
        self.records.append(record)
        
        self._by_promoter[record.promoter_id].append(idx)
        self._by_backend[record.backend].append(idx)
        self._by_promoter_backend[(record.promoter_id, record.backend)].append(idx)
    
    def add_record(self, record: VCaptureRecord):
        """Public method to add a single record."""
        self._add_record(record)
    
    def to_dataframe(self) -> pd.DataFrame:
        """Export all records as a pandas DataFrame."""
        return pd.DataFrame([r.to_dict() for r in self.records])

    def _get_analysis_phi(self, record: VCaptureRecord) -> Optional[float]:
        """Return the best available phi for calibration analysis."""
        if record.calibrated_phi is not None:
            return record.calibrated_phi
        return record.measured_phi

    def _get_analysis_residual(self, record: VCaptureRecord) -> Optional[float]:
        """Return the best available residual for calibration analysis."""
        if record.calibrated_residual is not None:
            return record.calibrated_residual
        return record.residual
    
    def to_canonical_table(self) -> Dict[str, Any]:
        """
        Export as canonical VCapture table with one row per execution event.
        """
        return {
            "schema_version": "1.0",
            "generated_at": datetime.now().isoformat(),
            "total_records": len(self.records),
            "unique_promoters": len(self._by_promoter),
            "unique_backends": len(self._by_backend),
            "records": [r.to_layered_dict() for r in self.records],
        }
    
    # ─────────────────────────────────────────────────────────────────────────
    # CALIBRATION METHODS
    # ─────────────────────────────────────────────────────────────────────────
    
    def apply_backend_calibration(self, 
                                   offsets: Optional[Dict[str, float]] = None,
                                   reference_backend: str = "ibm_fez") -> Dict[str, float]:
        """
        Apply backend-specific calibration offsets.
        
        Args:
            offsets: Dict mapping backend -> offset. If None, computed from data.
            reference_backend: Backend to use as reference for unified calibration.
        
        Returns:
            Dict of backend offsets applied.
        """
        # Compute offsets if not provided
        if offsets is None:
            offsets = self._compute_backend_offsets()
        
        # Apply offsets to records
        for record in self.records:
            if record.measured_phi is not None:
                offset = offsets.get(record.backend, 0.0)
                record.backend_calibrated_phi = record.measured_phi - offset
                record.calibrated_phi = record.backend_calibrated_phi
                record.backend_offset_applied = offset
                record.calibration_offset_applied = offset
                record.calibration_source = "backend_default"
                record.calibration_type = "backend_calibrated"
                record.calibration_scope = "backend"
                record.calibrated_residual = record.calibrated_phi - record.predicted_phi
        
        return offsets
    
    def _compute_backend_offsets(self) -> Dict[str, float]:
        """Compute backend-specific offsets from measured - predicted deltas."""
        backend_deltas: Dict[str, List[float]] = defaultdict(list)
        
        for record in self.records:
            if record.measured_phi is not None and record.predicted_phi is not None:
                delta = record.measured_phi - record.predicted_phi
                backend_deltas[record.backend].append(delta)
        
        return {backend: float(np.mean(deltas)) for backend, deltas in backend_deltas.items() if deltas}
    
    def apply_promoter_backend_calibration(self) -> Dict[str, Dict[str, float]]:
        """
        Apply promoter-specific offsets for each backend.
        Returns dict mapping promoter_id -> {backend -> offset}.
        """
        # Compute promoter-backend offsets
        promoter_backend_deltas: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))
        
        for record in self.records:
            if record.measured_phi is not None and record.predicted_phi is not None:
                delta = record.measured_phi - record.predicted_phi
                promoter_backend_deltas[record.promoter_id][record.backend].append(delta)
        
        offsets = {}
        for promoter_id, backend_dict in promoter_backend_deltas.items():
            offsets[promoter_id] = {
                backend: float(np.mean(deltas)) 
                for backend, deltas in backend_dict.items() if deltas
            }
        
        # Apply offsets
        for record in self.records:
            if record.measured_phi is not None:
                promoter_offsets = offsets.get(record.promoter_id, {})
                offset = promoter_offsets.get(record.backend, 0.0)
                record.promoter_backend_calibrated_phi = record.measured_phi - offset
                record.calibrated_phi = record.promoter_backend_calibrated_phi
                record.promoter_backend_offset_applied = offset
                record.calibration_offset_applied = offset
                record.calibration_source = "promoter_specific"
                record.calibration_type = "promoter_backend_calibrated"
                record.calibration_scope = "promoter_backend"
                record.calibrated_residual = record.calibrated_phi - record.predicted_phi
        
        return offsets
    
    # ─────────────────────────────────────────────────────────────────────────
    # VARIANCE ANALYSIS
    # ─────────────────────────────────────────────────────────────────────────
    
    def estimate_variance_structure(self) -> VarianceDecomposition:
        """
        Estimate variance structure: within-promoter, between-promoter, and residual.
        
        Answers three scientific questions:
        1. Within-promoter variance: measurement stability
        2. Between-promoter variance: identity recoverability above noise
        3. Residual variance: calibration model effectiveness
        """
        variance = VarianceDecomposition()
        
        # ─────────────────────────────────────────────────────────────────────
        # WITHIN-PROMOTER VARIANCE (replicate stability)
        # ─────────────────────────────────────────────────────────────────────
        promoter_measurements: Dict[str, List[float]] = defaultdict(list)
        promoter_calibrated: Dict[str, List[float]] = defaultdict(list)
        
        for record in self.records:
            analysis_phi = self._get_analysis_phi(record)
            if analysis_phi is not None:
                promoter_measurements[record.promoter_id].append(analysis_phi)
                if record.calibrated_phi is not None:
                    promoter_calibrated[record.promoter_id].append(record.calibrated_phi)
        
        within_variances = []
        for promoter_id, measurements in promoter_measurements.items():
            if len(measurements) >= 2:
                var = float(np.var(measurements, ddof=1))
                variance.within_promoter_variance[promoter_id] = var
                within_variances.append(var)
        
        if within_variances:
            variance.within_promoter_mean = float(np.mean(within_variances))
            variance.within_promoter_std = float(np.std(within_variances))
        
        # ─────────────────────────────────────────────────────────────────────
        # BETWEEN-PROMOTER VARIANCE (identity separation)
        # ─────────────────────────────────────────────────────────────────────
        backend_promoter_means: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))
        
        for record in self.records:
            analysis_phi = self._get_analysis_phi(record)
            if analysis_phi is not None:
                backend_promoter_means[record.backend][record.promoter_id].append(analysis_phi)
        
        between_variances = []
        for backend, promoter_dict in backend_promoter_means.items():
            means = [np.mean(vals) for vals in promoter_dict.values() if vals]
            if len(means) >= 2:
                var = float(np.var(means, ddof=1))
                variance.between_promoter_variance[backend] = var
                between_variances.append(var)
        
        if between_variances:
            variance.between_promoter_mean = float(np.mean(between_variances))
            variance.between_promoter_std = float(np.std(between_variances))
        
        # ─────────────────────────────────────────────────────────────────────
        # RESIDUAL DISTRIBUTIONS (calibration effectiveness)
        # ─────────────────────────────────────────────────────────────────────
        residuals_by_backend: Dict[str, List[float]] = defaultdict(list)
        raw_residuals_by_backend: Dict[str, List[float]] = defaultdict(list)
        calibrated_residuals_by_backend: Dict[str, List[float]] = defaultdict(list)
        
        for record in self.records:
            if record.residual is not None:
                raw_residuals_by_backend[record.backend].append(record.residual)
            analysis_residual = self._get_analysis_residual(record)
            if analysis_residual is not None:
                residuals_by_backend[record.backend].append(analysis_residual)
            if record.calibrated_residual is not None:
                calibrated_residuals_by_backend[record.backend].append(record.calibrated_residual)
        
        all_residuals = []
        for backend, residuals in residuals_by_backend.items():
            if residuals:
                variance.residual_distribution[backend] = {
                    'mean': float(np.mean(residuals)),
                    'std': float(np.std(residuals)),
                    'min': float(np.min(residuals)),
                    'max': float(np.max(residuals)),
                    'median': float(np.median(residuals)),
                    'q25': float(np.percentile(residuals, 25)),
                    'q75': float(np.percentile(residuals, 75)),
                    'count': len(residuals),
                    'raw_mean': float(np.mean(raw_residuals_by_backend.get(backend, []))) if raw_residuals_by_backend.get(backend) else None,
                    'raw_std': float(np.std(raw_residuals_by_backend.get(backend, []))) if raw_residuals_by_backend.get(backend) else None,
                    'calibrated_mean': float(np.mean(calibrated_residuals_by_backend.get(backend, []))) if calibrated_residuals_by_backend.get(backend) else None,
                    'calibrated_std': float(np.std(calibrated_residuals_by_backend.get(backend, []))) if calibrated_residuals_by_backend.get(backend) else None,
                }
                all_residuals.extend(residuals)
        
        if all_residuals:
            variance.residual_mean = float(np.mean(all_residuals))
            variance.residual_std = float(np.std(all_residuals))
        
        # ─────────────────────────────────────────────────────────────────────
        # BACKEND VARIANCE COMPONENTS
        # ─────────────────────────────────────────────────────────────────────
        for backend in self._by_backend.keys():
            backend_records = [self.records[i] for i in self._by_backend[backend]]
            measurements = [self._get_analysis_phi(r) for r in backend_records]
            measurements = [value for value in measurements if value is not None]
            if measurements:
                variance.backend_variance_components[backend] = float(np.var(measurements, ddof=1))
        
        # ─────────────────────────────────────────────────────────────────────
        # PROMOTER-BACKEND SUMMARIES
        # ─────────────────────────────────────────────────────────────────────
        variance.promoter_backend_summaries = self._compute_promoter_backend_summaries()
        
        # ─────────────────────────────────────────────────────────────────────
        # SEPARATION MATRIX (signal-to-noise)
        # ─────────────────────────────────────────────────────────────────────
        variance.separation_matrix = self._compute_separation_matrix()
        
        self.variance_decomposition = variance
        return variance
    
    def _compute_promoter_backend_summaries(self) -> List[PromoterBackendSummary]:
        """Compute summary statistics for each promoter-backend pair."""
        summaries = []
        
        for (promoter_id, backend), indices in self._by_promoter_backend.items():
            records = [self.records[i] for i in indices]
            
            measured = [r.measured_phi for r in records if r.measured_phi is not None]
            calibrated = [r.calibrated_phi for r in records if r.calibrated_phi is not None]
            residuals = [self._get_analysis_residual(r) for r in records]
            residuals = [value for value in residuals if value is not None]
            
            if measured and calibrated:
                mean_measured = float(np.mean(measured))
                std_measured = float(np.std(measured)) if len(measured) > 1 else 0.0
                mean_calibrated = float(np.mean(calibrated))
                std_calibrated = float(np.std(calibrated)) if len(calibrated) > 1 else 0.0
                mean_residual = float(np.mean(residuals)) if residuals else 0.0
                residual_mad = float(np.median(np.abs(residuals - np.median(residuals)))) if len(residuals) > 1 else 0.0
                
                # Signal-to-separation: distance to nearest promoter / pooled std
                signal_to_separation = self._compute_signal_to_separation(promoter_id, backend)
                
                summaries.append(PromoterBackendSummary(
                    promoter_id=promoter_id,
                    backend=backend,
                    replicate_count=len(records),
                    mean_measured_phi=mean_measured,
                    std_measured_phi=std_measured,
                    mean_calibrated_phi=mean_calibrated,
                    std_calibrated_phi=std_calibrated,
                    mean_residual=mean_residual,
                    residual_mad=residual_mad,
                    signal_to_separation=signal_to_separation,
                ))
        
        return summaries
    
    def _compute_signal_to_separation(self, promoter_id: str, backend: str) -> float:
        """
        Compute signal-to-separation statistic.
        Distance to nearest other promoter mean divided by pooled within-promoter std.
        """
        # Get this promoter's mean
        this_indices = self._by_promoter_backend.get((promoter_id, backend), [])
        this_measured = [self._get_analysis_phi(self.records[i]) for i in this_indices]
        this_measured = [value for value in this_measured if value is not None]
        
        if not this_measured:
            return 0.0
        
        this_mean = np.mean(this_measured)
        this_std = np.std(this_measured) if len(this_measured) > 1 else 0.0
        
        # Find nearest other promoter
        other_promoters = set(self._by_promoter.keys()) - {promoter_id}
        min_distance = float('inf')
        
        for other_id in other_promoters:
            other_indices = self._by_promoter_backend.get((other_id, backend), [])
            other_measured = [self._get_analysis_phi(self.records[i]) for i in other_indices]
            other_measured = [value for value in other_measured if value is not None]
            
            if other_measured:
                other_mean = np.mean(other_measured)
                distance = abs(this_mean - other_mean)
                min_distance = min(min_distance, distance)
        
        # Pooled std
        pooled_std = this_std if this_std > 0 else 1e-10
        
        return float(min_distance / pooled_std) if min_distance != float('inf') else 0.0
    
    def _compute_separation_matrix(self) -> Dict[str, Dict[str, float]]:
        """
        Compute promoter separation matrix using calibrated phi.
        Returns pairwise distances between promoter means.
        """
        promoters = list(self._by_promoter.keys())
        separation_matrix = {}
        
        # Compute mean calibrated phi for each promoter
        promoter_means = {}
        for promoter_id in promoters:
            indices = self._by_promoter[promoter_id]
            calibrated = [self.records[i].calibrated_phi for i in indices if self.records[i].calibrated_phi is not None]
            if calibrated:
                promoter_means[promoter_id] = np.mean(calibrated)
        
        # Compute pairwise distances
        for p1 in promoters:
            separation_matrix[p1] = {}
            for p2 in promoters:
                if p1 in promoter_means and p2 in promoter_means:
                    separation_matrix[p1][p2] = float(abs(promoter_means[p1] - promoter_means[p2]))
                else:
                    separation_matrix[p1][p2] = None
        
        return separation_matrix
    
    # ─────────────────────────────────────────────────────────────────────────
    # TRANSFERABILITY TESTING
    # ─────────────────────────────────────────────────────────────────────────
    
    def test_transferability(self, 
                              source_backend: str = "ibm_kingston",
                              target_backend: str = "ibm_fez") -> TransferabilityReport:
        """
        Test calibration transferability from source to target backend.
        
        Fits offset on source backend and applies unchanged to target backend,
        then compares residual mean, spread, and ranking stability.
        """
        # Get source offset
        source_records = [self.records[i] for i in self._by_backend.get(source_backend, [])]
        source_deltas = []
        for r in source_records:
            if r.measured_phi is not None and r.predicted_phi is not None:
                source_deltas.append(r.measured_phi - r.predicted_phi)
        
        if not source_deltas:
            return TransferabilityReport(
                source_backend=source_backend,
                target_backend=target_backend,
                source_offset=0.0,
                source_variance=0.0,
                source_sample_count=0,
                rmse_with_source_offset=0.0,
                rmse_with_native_offset=0.0,
                transfer_efficiency=0.0,
                residual_mean_shift=0.0,
                residual_spread_ratio=1.0,
                promoter_ranking_correlation=0.0,
                ranking_preserved=False,
                is_portable=False,
                portability_score=0.0,
                recommendation="Insufficient source backend data",
            )
        
        source_offset = float(np.mean(source_deltas))
        source_variance = float(np.var(source_deltas, ddof=1))
        
        # Get target records
        target_records = [self.records[i] for i in self._by_backend.get(target_backend, [])]
        
        # Compute native offset for target
        target_deltas = []
        for r in target_records:
            if r.measured_phi is not None and r.predicted_phi is not None:
                target_deltas.append(r.measured_phi - r.predicted_phi)
        
        native_offset = float(np.mean(target_deltas)) if target_deltas else 0.0
        
        # Compute residuals with source offset vs native offset
        residuals_source = []
        residuals_native = []
        
        for r in target_records:
            if r.measured_phi is not None and r.predicted_phi is not None:
                # Residual using source offset
                calibrated_source = r.predicted_phi + source_offset
                residual_source = r.measured_phi - calibrated_source
                residuals_source.append(residual_source)
                
                # Residual using native offset
                calibrated_native = r.predicted_phi + native_offset
                residual_native = r.measured_phi - calibrated_native
                residuals_native.append(residual_native)
        
        if not residuals_source:
            return TransferabilityReport(
                source_backend=source_backend,
                target_backend=target_backend,
                source_offset=source_offset,
                source_variance=source_variance,
                source_sample_count=len(source_deltas),
                rmse_with_source_offset=0.0,
                rmse_with_native_offset=0.0,
                transfer_efficiency=0.0,
                residual_mean_shift=0.0,
                residual_spread_ratio=1.0,
                promoter_ranking_correlation=0.0,
                ranking_preserved=False,
                is_portable=False,
                portability_score=0.0,
                recommendation="Insufficient target backend data",
            )
        
        rmse_source = float(np.sqrt(np.mean(np.square(residuals_source))))
        rmse_native = float(np.sqrt(np.mean(np.square(residuals_native))))
        
        # Transfer efficiency: how close is source offset to native performance
        transfer_efficiency = 1.0 - (rmse_source - rmse_native) / (rmse_native + 1e-10)
        transfer_efficiency = max(0.0, min(1.0, transfer_efficiency))
        
        # Residual analysis
        residual_mean_shift = float(np.mean(residuals_source) - np.mean(residuals_native))
        residual_spread_ratio = float(np.std(residuals_source) / (np.std(residuals_native) + 1e-10))
        
        # Ranking stability
        ranking_correlation = self._compute_ranking_correlation(source_backend, target_backend)
        ranking_preserved = abs(ranking_correlation) >= 0.8  # Spearman correlation threshold
        
        # Overall assessment
        is_portable = transfer_efficiency >= 0.9 and ranking_preserved
        portability_score = (transfer_efficiency + abs(ranking_correlation)) / 2
        
        if is_portable:
            recommendation = (
                f"Calibration is PORTABLE (score: {portability_score:.2%}). "
                f"Source backend {source_backend} offset transfers well to {target_backend}."
            )
        else:
            recommendation = (
                f"Calibration is NOT PORTABLE (score: {portability_score:.2%}). "
                f"Consider backend-conditioned offsets or hierarchical calibration."
            )
        
        report = TransferabilityReport(
            source_backend=source_backend,
            target_backend=target_backend,
            source_offset=source_offset,
            source_variance=source_variance,
            source_sample_count=len(source_deltas),
            rmse_with_source_offset=rmse_source,
            rmse_with_native_offset=rmse_native,
            transfer_efficiency=transfer_efficiency,
            residual_mean_shift=residual_mean_shift,
            residual_spread_ratio=residual_spread_ratio,
            promoter_ranking_correlation=ranking_correlation,
            ranking_preserved=ranking_preserved,
            is_portable=is_portable,
            portability_score=portability_score,
            recommendation=recommendation,
        )
        
        self.transferability_reports.append(report)
        return report
    
    def _compute_ranking_correlation(self, source_backend: str, target_backend: str) -> float:
        """
        Compute Spearman correlation of promoter rankings between backends.
        """
        # Get promoter means for source backend
        source_means = {}
        for promoter_id in self._by_promoter.keys():
            indices = [i for i in self._by_promoter_backend.get((promoter_id, source_backend), [])]
            measured = [self.records[i].measured_phi for i in indices if self.records[i].measured_phi is not None]
            if measured:
                source_means[promoter_id] = np.mean(measured)
        
        # Get promoter means for target backend
        target_means = {}
        for promoter_id in self._by_promoter.keys():
            indices = [i for i in self._by_promoter_backend.get((promoter_id, target_backend), [])]
            measured = [self.records[i].measured_phi for i in indices if self.records[i].measured_phi is not None]
            if measured:
                target_means[promoter_id] = np.mean(measured)
        
        # Find common promoters
        common_promoters = set(source_means.keys()) & set(target_means.keys())
        
        if len(common_promoters) < 2:
            return 0.0
        
        # Compute Spearman correlation
        source_ranks = [source_means[p] for p in sorted(common_promoters)]
        target_ranks = [target_means[p] for p in sorted(common_promoters)]
        
        correlation, _ = stats.spearmanr(source_ranks, target_ranks)
        return float(correlation) if not np.isnan(correlation) else 0.0
    
    # ─────────────────────────────────────────────────────────────────────────
    # MIXED-EFFECTS MODEL
    # ─────────────────────────────────────────────────────────────────────────
    
    def fit_mixed_effects_model(self) -> MixedEffectsResult:
        """
        Fit mixed-effects model: phi ~ promoter + backend + promoter:backend + calibration_offset
        
        Separates identity, hardware, and interaction effects.
        Uses ANOVA-style variance decomposition.
        """
        result = MixedEffectsResult()
        
        # Collect data
        data = []
        for record in self.records:
            analysis_phi = self._get_analysis_phi(record)
            if analysis_phi is not None:
                data.append({
                    'promoter': record.promoter_id,
                    'backend': record.backend,
                    'phi': analysis_phi,
                    'predicted': record.predicted_phi,
                    'replicate': record.replicate_index,
                })
        
        if len(data) < 3:
            return result
        
        df = pd.DataFrame(data)
        
        # Get unique levels
        promoters = df['promoter'].unique()
        backends = df['backend'].unique()
        
        # ─────────────────────────────────────────────────────────────────────
        # FIXED EFFECTS (promoter and backend means)
        # ─────────────────────────────────────────────────────────────────────
        grand_mean = df['phi'].mean()
        
        # Promoter effects
        for promoter in promoters:
            promoter_mean = df[df['promoter'] == promoter]['phi'].mean()
            result.promoter_effects[promoter] = float(promoter_mean - grand_mean)
        
        # Backend effects
        for backend in backends:
            backend_mean = df[df['backend'] == backend]['phi'].mean()
            result.backend_effects[backend] = float(backend_mean - grand_mean)
        
        # Interaction effects
        for promoter in promoters:
            for backend in backends:
                subset = df[(df['promoter'] == promoter) & (df['backend'] == backend)]
                if len(subset) > 0:
                    interaction_mean = subset['phi'].mean()
                    expected = grand_mean + result.promoter_effects[promoter] + result.backend_effects[backend]
                    result.interaction_effects[(promoter, backend)] = float(interaction_mean - expected)
        
        # ─────────────────────────────────────────────────────────────────────
        # VARIANCE COMPONENTS (ANOVA-style)
        # ─────────────────────────────────────────────────────────────────────
        
        # Total sum of squares
        total_ss = ((df['phi'] - grand_mean) ** 2).sum()
        
        # Promoter sum of squares
        promoter_ss = sum(
            len(df[df['promoter'] == p]) * (df[df['promoter'] == p]['phi'].mean() - grand_mean) ** 2
            for p in promoters
        )
        
        # Backend sum of squares
        backend_ss = sum(
            len(df[df['backend'] == b]) * (df[df['backend'] == b]['phi'].mean() - grand_mean) ** 2
            for b in backends
        )
        
        # Interaction sum of squares
        interaction_ss = 0
        for p in promoters:
            for b in backends:
                subset = df[(df['promoter'] == p) & (df['backend'] == b)]
                if len(subset) > 0:
                    expected = grand_mean + result.promoter_effects[p] + result.backend_effects[b]
                    interaction_ss += len(subset) * (subset['phi'].mean() - expected) ** 2
        
        # Residual sum of squares
        residual_ss = 0
        for p in promoters:
            for b in backends:
                subset = df[(df['promoter'] == p) & (df['backend'] == b)]
                if len(subset) > 0:
                    group_mean = subset['phi'].mean()
                    residual_ss += ((subset['phi'] - group_mean) ** 2).sum()
        
        # Degrees of freedom
        n = len(df)
        df_promoter = len(promoters) - 1
        df_backend = len(backends) - 1
        df_interaction = df_promoter * df_backend
        df_residual = n - len(promoters) * len(backends)
        
        # Mean squares
        ms_promoter = promoter_ss / df_promoter if df_promoter > 0 else 0
        ms_backend = backend_ss / df_backend if df_backend > 0 else 0
        ms_interaction = interaction_ss / df_interaction if df_interaction > 0 else 0
        ms_residual = residual_ss / df_residual if df_residual > 0 else 0
        
        # Variance components
        result.promoter_variance = float(max(0, (ms_promoter - ms_residual) / (len(backends) * df_residual / df_promoter if df_promoter > 0 else 1)))
        result.backend_variance = float(max(0, (ms_backend - ms_residual) / (len(promoters) * df_residual / df_backend if df_backend > 0 else 1)))
        result.interaction_variance = float(max(0, (ms_interaction - ms_residual) / (df_residual / df_interaction if df_interaction > 0 else 1)))
        result.residual_variance = float(ms_residual)
        
        # R-squared
        explained_ss = promoter_ss + backend_ss + interaction_ss
        result.r_squared = float(explained_ss / total_ss) if total_ss > 0 else 0
        result.adjusted_r_squared = float(1 - (residual_ss / df_residual) / (total_ss / (n - 1))) if n > 1 and df_residual > 0 else 0
        
        # F-statistics
        result.f_statistic = float(ms_promoter / ms_residual) if ms_residual > 0 else 0
        result.p_value = float(1 - f_dist.cdf(result.f_statistic, df_promoter, df_residual)) if df_promoter > 0 and df_residual > 0 else 1
        
        # Effect significance (using F-test)
        result.promoter_significant = result.p_value < 0.05
        result.backend_significant = ms_backend > ms_residual * 4 if ms_residual > 0 else False  # Approximate F-test
        result.interaction_significant = ms_interaction > ms_residual * 4 if ms_residual > 0 else False
        
        self.mixed_effects_result = result
        return result
    
    # ─────────────────────────────────────────────────────────────────────────
    # REPORT GENERATION
    # ─────────────────────────────────────────────────────────────────────────
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive VCapture report."""
        return {
            "report_type": "vcapture_measurement_ledger",
            "report_version": "1.0",
            "generated_at": datetime.now().isoformat(),
            "schema": {
                "version": "1.0",
                "layers": ["raw", "derived", "offsets", "context", "provenance"],
                "description": "Canonical VCapture measurement ledger with full experiment context",
            },
            "metadata": {
                "total_records": len(self.records),
                "unique_promoters": len(self._by_promoter),
                "unique_backends": len(self._by_backend),
                "calibration_version": self.calibration_version,
                "offset_model_version": self.offset_model_version,
            },
            "variance_structure": self.variance_decomposition.to_dict() if self.variance_decomposition else None,
            "transferability": [r.to_dict() for r in self.transferability_reports],
            "mixed_effects": self.mixed_effects_result.to_dict() if self.mixed_effects_result else None,
            "records": [r.to_layered_dict() for r in self.records],
        }


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="VCapture Measurement Ledger System")
    parser.add_argument("--manifest", type=str, required=True, help="Path to promoter replicate manifest")
    parser.add_argument("--output", type=str, default="vcapture_ledger_report.json", help="Output report path")
    parser.add_argument(
        "--calibration-type",
        type=str,
        default="backend",
        choices=["backend", "promoter_backend", "hierarchical"],
        help="Calibration strategy to apply before analysis",
    )
    parser.add_argument("--calibration-version", type=str, default="1.0", help="Calibration version tag")
    parser.add_argument("--offset-model-version", type=str, default="1.0", help="Offset model version")
    parser.add_argument("--reference-backend", type=str, default="ibm_fez", help="Reference backend for calibration")
    parser.add_argument("--source-backend", type=str, default="ibm_kingston", help="Source backend for transferability test")
    parser.add_argument("--target-backend", type=str, default="ibm_fez", help="Target backend for transferability test")
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("VCapture Measurement Ledger System v1.0")
    print("=" * 70)
    
    # Initialize ledger
    ledger = VCaptureLedger(
        calibration_version=args.calibration_version,
        offset_model_version=args.offset_model_version,
    )
    
    # Load from manifest
    manifest_path = Path(args.manifest)
    print(f"\nLoading manifest: {manifest_path}")
    records_loaded = ledger.load_from_manifest(manifest_path)
    print(f"Loaded {records_loaded} records")
    
    # Apply calibration
    if args.calibration_type == "backend":
        print(f"\nApplying backend calibration...")
        offsets = ledger.apply_backend_calibration(reference_backend=args.reference_backend)
        print(f"Backend offsets: {offsets}")
    else:
        print(f"\nApplying {args.calibration_type} calibration...")
        offsets = ledger.apply_promoter_backend_calibration()
        print(f"Promoter-backend offsets computed for {len(offsets)} promoters")
    
    # Estimate variance structure
    print("\nEstimating variance structure...")
    variance = ledger.estimate_variance_structure()
    print(f"Within-promoter variance (mean): {variance.within_promoter_mean:.6e}")
    print(f"Between-promoter variance (mean): {variance.between_promoter_mean:.6e}")
    print(f"Residual std: {variance.residual_std:.6f}")
    
    # Test transferability
    print(f"\nTesting transferability: {args.source_backend} -> {args.target_backend}...")
    transfer = ledger.test_transferability(
        source_backend=args.source_backend,
        target_backend=args.target_backend,
    )
    print(f"Transfer efficiency: {transfer.transfer_efficiency:.2%}")
    print(f"Portability score: {transfer.portability_score:.2%}")
    print(f"Is portable: {transfer.is_portable}")
    print(f"Recommendation: {transfer.recommendation}")
    
    # Fit mixed-effects model
    print("\nFitting mixed-effects model...")
    mixed = ledger.fit_mixed_effects_model()
    print(f"R-squared: {mixed.r_squared:.4f}")
    print(f"Promoter variance: {mixed.promoter_variance:.6e}")
    print(f"Backend variance: {mixed.backend_variance:.6e}")
    print(f"Interaction variance: {mixed.interaction_variance:.6e}")
    print(f"Residual variance: {mixed.residual_variance:.6e}")
    
    # Generate report
    report = ledger.generate_report()
    
    output_path = Path(args.output)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\nReport saved to: {output_path}")
    
    # Print summary table
    print("\n" + "=" * 70)
    print("PROMOTER-BACKEND SUMMARY TABLE")
    print("=" * 70)
    print(f"{'Promoter':<10} {'Backend':<15} {'N':>4} {'Mean φ':>10} {'Std φ':>10} {'Residual':>10} {'S/S':>8}")
    print("-" * 70)
    for summary in variance.promoter_backend_summaries:
        print(f"{summary.promoter_id:<10} {summary.backend:<15} {summary.replicate_count:>4} "
              f"{summary.mean_measured_phi:>10.4f} {summary.std_measured_phi:>10.6f} "
              f"{summary.mean_residual:>10.4f} {summary.signal_to_separation:>8.2f}")
    
    print("\n" + "=" * 70)
    print("SEPARATION MATRIX (Calibrated φ)")
    print("=" * 70)
    promoters = list(variance.separation_matrix.keys())
    print(f"{'':>12}", end="")
    for p in promoters:
        print(f"{p:>12}", end="")
    print()
    for p1 in promoters:
        print(f"{p1:>12}", end="")
        for p2 in promoters:
            val = variance.separation_matrix[p1].get(p2)
            if val is not None:
                print(f"{val:>12.4f}", end="")
            else:
                print(f"{'N/A':>12}", end="")
        print()


if __name__ == "__main__":
    main()