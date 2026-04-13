#!/usr/bin/env python3
"""
Replicate-Aware Promoter Calibration System v1.0
================================================

Milestone: Move from job-level calibration to replicate-aware promoter calibration.

Features:
1. Capture richer metadata (promoter ID, replicate index, backend, shots, 
   transpiled depth, layout, measured phi, calibrated phi, residual, timestamp)
2. Estimate variance structure (within-promoter, between-promoter, residual distributions)
3. Test transferability across backends (portable vs batch-specific calibration)

Usage:
    python replicate_aware_promoter_calibration.py --manifest raw_hardware/test_replicate_schedule_manifest.json
"""

import argparse
import json
import hashlib
from collections import defaultdict
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import warnings

import numpy as np
from scipy import stats


# ─────────────────────────────────────────────────────────────────────────────
# Data Classes for Rich Metadata Capture
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class PromoterCalibrationRecord:
    """
    Rich metadata for a single calibration measurement.
    Captures all required fields for replicate-aware analysis.
    
    Schema follows layered provenance pattern:
    - Raw layer: Original instrument measurements (immutable)
    - Derived layer: Calibrated values with explicit offsets
    - Provenance layer: Transformation metadata for reproducibility
    """
    # Identity fields
    record_id: str
    promoter_id: str
    replicate_index: int
    backend: str
    
    # Execution parameters
    shots: int
    transpiled_depth: Optional[int] = None
    qubit_layout: List[int] = field(default_factory=list)
    
    # ─────────────────────────────────────────────────────────────────────────
    # RAW LAYER (immutable audit trail)
    # ─────────────────────────────────────────────────────────────────────────
    predicted_phi: float = 0.0
    raw_measured_phi: Optional[float] = None  # Original instrument reading
    measured_phi: Optional[float] = None  # Alias for backward compatibility
    
    # ─────────────────────────────────────────────────────────────────────────
    # DERIVED LAYER (calibrated values)
    # ─────────────────────────────────────────────────────────────────────────
    backend_calibrated_phi: Optional[float] = None  # After backend offset
    promoter_backend_calibrated_phi: Optional[float] = None  # After promoter-backend offset
    calibrated_phi: Optional[float] = None  # Final calibrated value (preferred)
    residual: Optional[float] = None
    
    # ─────────────────────────────────────────────────────────────────────────
    # OFFSET TRACKING (explicit transformation parameters)
    # ─────────────────────────────────────────────────────────────────────────
    backend_offset_applied: float = 0.0
    promoter_backend_offset_applied: float = 0.0
    calibration_offset_applied: float = 0.0  # Selected offset applied (renamed from total_offset_applied)
    calibration_source: str = "none"  # none, backend_default, promoter_specific, unified_reference
    
    # ─────────────────────────────────────────────────────────────────────────
    # PROVENANCE LAYER (transformation metadata)
    # ─────────────────────────────────────────────────────────────────────────
    calibration_version: str = "1.0"
    calibration_method: str = "replicate_aware_mean_offset"
    calibration_scope: str = "backend"  # backend, promoter_backend, unified
    calibration_reference_backend: str = "ibm_fez"
    
    # Timestamps
    timestamp: Optional[str] = None
    job_id: Optional[str] = None
    
    # Quality metrics
    entropy: Optional[float] = None
    fidelity: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Export with layered structure for clarity."""
        data = asdict(self)
        # Organize into layers for JSON output
        return {
            # Identity
            "record_id": data["record_id"],
            "promoter_id": data["promoter_id"],
            "replicate_index": data["replicate_index"],
            "backend": data["backend"],
            # Execution
            "shots": data["shots"],
            "transpiled_depth": data["transpiled_depth"],
            "qubit_layout": data["qubit_layout"],
            # Raw layer
            "raw": {
                "predicted_phi": data["predicted_phi"],
                "measured_phi": data["raw_measured_phi"] or data["measured_phi"],
            },
            # Derived layer
            "derived": {
                "backend_calibrated_phi": data["backend_calibrated_phi"],
                "promoter_backend_calibrated_phi": data["promoter_backend_calibrated_phi"],
                "calibrated_phi": data["calibrated_phi"],
                "residual": data["residual"],
            },
            # Offsets applied
            "offsets": {
                "backend_offset_applied": data["backend_offset_applied"],
                "promoter_backend_offset_applied": data["promoter_backend_offset_applied"],
                "selected_offset_applied": data["calibration_offset_applied"],
                "calibration_source": data["calibration_source"],
            },
            # Provenance layer
            "provenance": {
                "calibration_version": data["calibration_version"],
                "calibration_method": data["calibration_method"],
                "calibration_scope": data["calibration_scope"],
                "calibration_reference_backend": data["calibration_reference_backend"],
            },
            # Timestamps
            "timestamp": data["timestamp"],
            "job_id": data["job_id"],
            # Quality metrics
            "entropy": data["entropy"],
            "fidelity": data["fidelity"],
        }
    
    def to_flat_dict(self) -> Dict[str, Any]:
        """Export as flat dict for backward compatibility."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PromoterCalibrationRecord':
        """Import from dict, handling both flat and layered formats."""
        # Handle layered format
        if "raw" in data:
            raw = data["raw"]
            derived = data.get("derived", {})
            offsets = data.get("offsets", {})
            provenance = data.get("provenance", {})
            return cls(
                record_id=data.get('record_id', ''),
                promoter_id=data.get('promoter_id', ''),
                replicate_index=data.get('replicate_index', 0),
                backend=data.get('backend', ''),
                shots=data.get('shots', 0),
                transpiled_depth=data.get('transpiled_depth'),
                qubit_layout=data.get('qubit_layout', []),
                predicted_phi=raw.get('predicted_phi', 0.0),
                raw_measured_phi=raw.get('measured_phi'),
                measured_phi=raw.get('measured_phi'),
                backend_calibrated_phi=derived.get('backend_calibrated_phi'),
                promoter_backend_calibrated_phi=derived.get('promoter_backend_calibrated_phi'),
                calibrated_phi=derived.get('calibrated_phi'),
                residual=derived.get('residual'),
                backend_offset_applied=offsets.get('backend_offset_applied', 0.0),
                promoter_backend_offset_applied=offsets.get('promoter_backend_offset_applied', 0.0),
                calibration_offset_applied=offsets.get('selected_offset_applied', offsets.get('total_offset_applied', 0.0)),  # Support both names
                calibration_source=offsets.get('calibration_source', 'none'),
                calibration_version=provenance.get('calibration_version', '1.0'),
                calibration_method=provenance.get('calibration_method', 'replicate_aware_mean_offset'),
                calibration_scope=provenance.get('calibration_scope', 'backend'),
                calibration_reference_backend=provenance.get('calibration_reference_backend', 'ibm_fez'),
                timestamp=data.get('timestamp'),
                job_id=data.get('job_id'),
                entropy=data.get('entropy'),
                fidelity=data.get('fidelity')
            )
        # Handle flat format (backward compatibility)
        return cls(
            record_id=data.get('record_id', ''),
            promoter_id=data.get('promoter_id', ''),
            replicate_index=data.get('replicate_index', 0),
            backend=data.get('backend', ''),
            shots=data.get('shots', 0),
            transpiled_depth=data.get('transpiled_depth'),
            qubit_layout=data.get('qubit_layout', []),
            predicted_phi=data.get('predicted_phi', 0.0),
            raw_measured_phi=data.get('raw_measured_phi') or data.get('measured_phi'),
            measured_phi=data.get('measured_phi'),
            backend_calibrated_phi=data.get('backend_calibrated_phi'),
            promoter_backend_calibrated_phi=data.get('promoter_backend_calibrated_phi'),
            calibrated_phi=data.get('calibrated_phi'),
            residual=data.get('residual'),
            backend_offset_applied=data.get('backend_offset_applied', 0.0),
            promoter_backend_offset_applied=data.get('promoter_backend_offset_applied', 0.0),
            calibration_offset_applied=data.get('calibration_offset_applied', 0.0),
            calibration_source=data.get('calibration_source', 'none'),
            calibration_version=data.get('calibration_version', '1.0'),
            calibration_method=data.get('calibration_method', 'replicate_aware_mean_offset'),
            calibration_scope=data.get('calibration_scope', 'backend'),
            calibration_reference_backend=data.get('calibration_reference_backend', 'ibm_fez'),
            timestamp=data.get('timestamp'),
            job_id=data.get('job_id'),
            entropy=data.get('entropy'),
            fidelity=data.get('fidelity')
        )


@dataclass
class VarianceStructure:
    """
    Variance structure estimates for calibration analysis.
    """
    # Within-promoter variance (replicate variability)
    within_promoter_variance: Dict[str, float] = field(default_factory=dict)
    within_promoter_mean: float = 0.0
    within_promoter_std: float = 0.0
    
    # Between-promoter variance (promoter separation)
    between_promoter_variance: Dict[str, float] = field(default_factory=dict)
    between_promoter_mean: float = 0.0
    between_promoter_std: float = 0.0
    
    # Calibration residual distributions
    residual_distribution: Dict[str, Dict[str, float]] = field(default_factory=dict)
    residual_mean: float = 0.0
    residual_std: float = 0.0
    
    # Backend-specific variance components
    backend_variance_components: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TransferabilityResult:
    """
    Results of calibration transferability testing across backends.
    """
    reference_backend: str
    reference_offset: float
    reference_variance: float
    
    # Transfer metrics for each target backend
    backend_transfer_metrics: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    # Overall assessment
    is_portable: bool = False
    portability_score: float = 0.0
    recommendation: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ─────────────────────────────────────────────────────────────────────────────
# Calibration Engine
# ─────────────────────────────────────────────────────────────────────────────

class ReplicateAwareCalibrator:
    """
    Advanced calibration engine with replicate-aware promoter calibration.
    """
    
    def __init__(self, tolerance: float = 0.15, min_replicates: int = 2):
        self.tolerance = tolerance
        self.min_replicates = min_replicates
        self.records: List[PromoterCalibrationRecord] = []
        self.backend_offsets: Dict[str, float] = {}
        self.promoter_offsets: Dict[str, Dict[str, float]] = {}
        self.variance_structure: Optional[VarianceStructure] = None
        self.transferability_result: Optional[TransferabilityResult] = None
        
    def load_from_manifest(self, manifest_path: Path) -> int:
        """
        Load calibration records from a schedule manifest.
        Returns number of records loaded.
        
        Populates raw layer fields from manifest data.
        Derived fields are populated later by apply_calibration().
        """
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        
        records_loaded = 0
        for run in manifest.get('scheduled_runs', []):
            planned = run.get('planned_metrics', {})
            observed = run.get('observed_metrics', {})
            execution = run.get('execution', {})
            
            # Generate unique record ID
            record_id = run.get('run_id', f"{run.get('promoter_id')}_{run.get('backend')}_r{run.get('replicate_index')}")
            
            # Extract raw measured phi (immutable audit trail)
            raw_measured = observed.get('measured_phi')
            
            record = PromoterCalibrationRecord(
                record_id=record_id,
                promoter_id=run.get('promoter_id', ''),
                replicate_index=run.get('replicate_index', 0),
                backend=run.get('backend', ''),
                shots=run.get('shots', 0),
                transpiled_depth=execution.get('transpiled_depth'),
                qubit_layout=execution.get('qubit_layout', []),
                # Raw layer
                predicted_phi=planned.get('predicted_phi', 0.0),
                raw_measured_phi=raw_measured,
                measured_phi=raw_measured,  # Alias for backward compatibility
                # Derived layer (populated by apply_calibration)
                backend_calibrated_phi=None,
                promoter_backend_calibrated_phi=None,
                calibrated_phi=None,
                residual=observed.get('residual'),
                # Provenance layer
                calibration_version="1.0",
                calibration_method="replicate_aware_mean_offset",
                calibration_scope="none",  # Set by apply_calibration
                calibration_reference_backend="ibm_fez",
                # Timestamps
                timestamp=observed.get('timestamp') or execution.get('submitted_at'),
                job_id=execution.get('job_id'),
                # Quality metrics
                entropy=planned.get('entropy_shannon'),
                fidelity=planned.get('phi_alignment_score')
            )
            
            self.records.append(record)
            records_loaded += 1
        
        return records_loaded
    
    def add_record(self, record: PromoterCalibrationRecord):
        """Add a single calibration record."""
        self.records.append(record)
    
    def fit_backend_offsets(self) -> Dict[str, float]:
        """
        Fit backend-specific calibration offsets.
        Returns dict mapping backend -> offset.
        """
        backend_deltas: Dict[str, List[float]] = defaultdict(list)
        
        for record in self.records:
            if record.measured_phi is not None and record.predicted_phi is not None:
                delta = record.measured_phi - record.predicted_phi
                backend_deltas[record.backend].append(delta)
        
        self.backend_offsets = {}
        for backend, deltas in backend_deltas.items():
            if deltas:
                self.backend_offsets[backend] = float(np.mean(deltas))
            else:
                self.backend_offsets[backend] = 0.0
        
        return self.backend_offsets
    
    def fit_promoter_backend_offsets(self) -> Dict[str, Dict[str, float]]:
        """
        Fit promoter-specific offsets for each backend.
        Returns dict mapping promoter_id -> {backend -> offset}.
        """
        promoter_backend_deltas: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))
        
        for record in self.records:
            if record.measured_phi is not None and record.predicted_phi is not None:
                delta = record.measured_phi - record.predicted_phi
                promoter_backend_deltas[record.promoter_id][record.backend].append(delta)
        
        self.promoter_offsets = {}
        for promoter_id, backend_dict in promoter_backend_deltas.items():
            self.promoter_offsets[promoter_id] = {}
            for backend, deltas in backend_dict.items():
                if deltas:
                    self.promoter_offsets[promoter_id][backend] = float(np.mean(deltas))
        
        return self.promoter_offsets
    
    def estimate_variance_structure(self) -> VarianceStructure:
        """
        Estimate variance structure: within-promoter, between-promoter, and residual.
        """
        variance = VarianceStructure()
        
        # Within-promoter variance (across replicates)
        promoter_measurements: Dict[str, List[float]] = defaultdict(list)
        for record in self.records:
            if record.measured_phi is not None:
                promoter_measurements[record.promoter_id].append(record.measured_phi)
        
        within_variances = []
        for promoter_id, measurements in promoter_measurements.items():
            if len(measurements) >= self.min_replicates:
                var = float(np.var(measurements, ddof=1))
                variance.within_promoter_variance[promoter_id] = var
                within_variances.append(var)
            else:
                variance.within_promoter_variance[promoter_id] = 0.0
        
        if within_variances:
            variance.within_promoter_mean = float(np.mean(within_variances))
            variance.within_promoter_std = float(np.std(within_variances))
        
        # Between-promoter variance (for each backend)
        backend_promoter_means: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))
        for record in self.records:
            if record.measured_phi is not None:
                backend_promoter_means[record.backend][record.promoter_id].append(record.measured_phi)
        
        between_variances = []
        for backend, promoter_dict in backend_promoter_means.items():
            means = [np.mean(vals) for vals in promoter_dict.values() if vals]
            if len(means) >= 2:
                var = float(np.var(means, ddof=1))
                variance.between_promoter_variance[backend] = var
                between_variances.append(var)
            else:
                variance.between_promoter_variance[backend] = 0.0
        
        if between_variances:
            variance.between_promoter_mean = float(np.mean(between_variances))
            variance.between_promoter_std = float(np.std(between_variances))
        
        # Residual distribution (after calibration)
        residuals_by_backend: Dict[str, List[float]] = defaultdict(list)
        for record in self.records:
            if record.residual is not None:
                residuals_by_backend[record.backend].append(record.residual)
        
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
                    'count': len(residuals)
                }
                all_residuals.extend(residuals)
        
        if all_residuals:
            variance.residual_mean = float(np.mean(all_residuals))
            variance.residual_std = float(np.std(all_residuals))
        
        # Backend variance components (ANOVA-style decomposition)
        total_measurements = sum(len(m) for m in promoter_measurements.values())
        if total_measurements > 0:
            for backend in set(r.backend for r in self.records):
                backend_records = [r for r in self.records if r.backend == backend and r.measured_phi is not None]
                if backend_records:
                    variance.backend_variance_components[backend] = float(
                        np.var([r.measured_phi for r in backend_records], ddof=1)
                    )
        
        self.variance_structure = variance
        return variance
    
    def test_transferability(self, reference_backend: str = "ibm_fez") -> TransferabilityResult:
        """
        Test calibration transferability across backends.
        Determines if calibration is portable or batch-specific.
        """
        result = TransferabilityResult(
            reference_backend=reference_backend,
            reference_offset=self.backend_offsets.get(reference_backend, 0.0),
            reference_variance=self.variance_structure.backend_variance_components.get(reference_backend, 0.0) if self.variance_structure else 0.0
        )
        
        # Get reference offset
        reference_deltas = []
        for record in self.records:
            if (record.backend == reference_backend and 
                record.measured_phi is not None and 
                record.predicted_phi is not None):
                reference_deltas.append(record.measured_phi - record.predicted_phi)
        
        if not reference_deltas:
            result.recommendation = "Insufficient reference backend data for transferability test"
            return result
        
        reference_offset = float(np.mean(reference_deltas))
        reference_std = float(np.std(reference_deltas))
        result.reference_offset = reference_offset
        result.reference_variance = reference_std ** 2
        
        # Test transfer to each other backend
        other_backends = set(r.backend for r in self.records) - {reference_backend}
        
        transfer_scores = []
        for target_backend in other_backends:
            target_records = [r for r in self.records if r.backend == target_backend and r.measured_phi is not None]
            
            if not target_records:
                continue
            
            # Apply reference offset to target backend predictions
            residuals_with_reference = []
            residuals_with_native = []
            
            for record in target_records:
                if record.predicted_phi is not None:
                    # Residual using reference offset
                    calibrated_reference = record.predicted_phi + reference_offset
                    residual_reference = record.measured_phi - calibrated_reference
                    residuals_with_reference.append(residual_reference)
                    
                    # Residual using native offset
                    native_offset = self.backend_offsets.get(target_backend, 0.0)
                    calibrated_native = record.predicted_phi + native_offset
                    residual_native = record.measured_phi - calibrated_native
                    residuals_with_native.append(residual_native)
            
            if residuals_with_reference:
                rmse_reference = float(np.sqrt(np.mean(np.square(residuals_with_reference))))
                rmse_native = float(np.sqrt(np.mean(np.square(residuals_with_native))))
                
                # Transfer efficiency: how much worse is reference offset vs native?
                transfer_efficiency = 1.0 - (rmse_reference - rmse_native) / (rmse_native + 1e-10)
                transfer_efficiency = max(0.0, min(1.0, transfer_efficiency))
                
                result.backend_transfer_metrics[target_backend] = {
                    'rmse_with_reference_offset': rmse_reference,
                    'rmse_with_native_offset': rmse_native,
                    'transfer_efficiency': transfer_efficiency,
                    'offset_difference': abs(reference_offset - self.backend_offsets.get(target_backend, 0.0)),
                    'sample_count': len(residuals_with_reference)
                }
                transfer_scores.append(transfer_efficiency)
        
        # Overall portability assessment
        if transfer_scores:
            result.portability_score = float(np.mean(transfer_scores))
            result.is_portable = result.portability_score >= 0.9  # 90% efficiency threshold
            
            if result.is_portable:
                result.recommendation = (
                    f"Calibration is PORTABLE (score: {result.portability_score:.2%}). "
                    f"Reference backend {reference_backend} offset transfers well to other backends."
                )
            else:
                result.recommendation = (
                    f"Calibration is BATCH-SPECIFIC (score: {result.portability_score:.2%}). "
                    f"Each backend requires its own calibration. "
                    f"Reference offset does not transfer efficiently."
                )
        else:
            result.recommendation = "Insufficient data for transferability assessment"
        
        self.transferability_result = result
        return result
    
    def apply_calibration(self, record: PromoterCalibrationRecord, 
                          calibration_type: str = "backend",
                          calibration_version: str = "1.0") -> PromoterCalibrationRecord:
        """
        Apply calibration to a record with full provenance tracking.
        
        Populates derived layer fields while preserving raw layer.
        
        Args:
            record: The record to calibrate
            calibration_type: "backend" (backend-specific), "promoter" (promoter-specific), 
                            or "unified" (use reference backend offset)
            calibration_version: Version string for provenance tracking
        
        Returns:
            Calibrated record with updated derived and provenance fields
        """
        if record.raw_measured_phi is None and record.measured_phi is None:
            return record
        
        if record.predicted_phi is None:
            return record
        
        # Get raw measurement (preserve immutable)
        raw_measured = record.raw_measured_phi or record.measured_phi
        
        # Calculate backend-specific calibration
        backend_offset = self.backend_offsets.get(record.backend, 0.0)
        backend_calibrated = record.predicted_phi + backend_offset
        
        # Calculate promoter-backend-specific calibration
        promoter_backend_offset = self.promoter_offsets.get(record.promoter_id, {}).get(record.backend, 0.0)
        promoter_backend_calibrated = record.predicted_phi + promoter_backend_offset
        
        # Determine which calibration to use based on type
        if calibration_type == "backend":
            final_offset = backend_offset
            record.calibration_source = "backend_default"
            record.calibration_scope = "backend"
            final_calibrated = backend_calibrated
        elif calibration_type == "promoter":
            final_offset = promoter_backend_offset
            record.calibration_source = "promoter_specific"
            record.calibration_scope = "promoter_backend"
            final_calibrated = promoter_backend_calibrated
        elif calibration_type == "unified":
            # Use reference backend offset for portable calibration
            ref_offset = self.backend_offsets.get("ibm_fez", 0.0)
            final_offset = ref_offset
            record.calibration_source = "unified_reference"
            record.calibration_scope = "unified"
            final_calibrated = record.predicted_phi + ref_offset
        else:
            final_offset = 0.0
            record.calibration_source = "none"
            record.calibration_scope = "none"
            final_calibrated = record.predicted_phi
        
        # Populate derived layer
        record.backend_calibrated_phi = backend_calibrated
        record.promoter_backend_calibrated_phi = promoter_backend_calibrated
        record.calibrated_phi = final_calibrated
        
        # Populate offset tracking
        record.backend_offset_applied = backend_offset
        record.promoter_backend_offset_applied = promoter_backend_offset
        record.calibration_offset_applied = final_offset
        
        # Calculate residual (from raw measurement)
        record.residual = raw_measured - final_calibrated
        
        # Populate provenance layer
        record.calibration_version = calibration_version
        record.calibration_method = "replicate_aware_mean_offset"
        record.calibration_reference_backend = "ibm_fez"
        
        return record
    
    def apply_calibration_to_all(self, calibration_type: str = "backend",
                                  calibration_version: str = "1.0") -> int:
        """
        Apply calibration to all records in the dataset.
        
        Args:
            calibration_type: "backend", "promoter", or "unified"
            calibration_version: Version string for provenance
        
        Returns:
            Number of records calibrated
        """
        calibrated_count = 0
        for record in self.records:
            self.apply_calibration(record, calibration_type, calibration_version)
            if record.calibrated_phi is not None:
                calibrated_count += 1
        return calibrated_count
    
    def generate_calibration_report(self, calibration_type: str = "backend",
                                     calibration_version: str = "1.0") -> Dict[str, Any]:
        """
        Generate comprehensive calibration report with layered provenance.
        
        Args:
            calibration_type: "backend", "promoter", or "unified"
            calibration_version: Version string for provenance tracking
        
        Returns:
            Complete calibration report with raw, derived, and provenance layers
        """
        # Ensure all analyses are run
        if not self.backend_offsets:
            self.fit_backend_offsets()
        if not self.promoter_offsets:
            self.fit_promoter_backend_offsets()
        if self.variance_structure is None:
            self.estimate_variance_structure()
        if self.transferability_result is None:
            self.test_transferability()
        
        # Apply calibration to all records
        self.apply_calibration_to_all(calibration_type, calibration_version)
        
        # Convert records to layered dict format
        records_data = [r.to_dict() for r in self.records]
        
        report = {
            "report_type": "replicate_aware_promoter_calibration",
            "report_version": "2.0",
            "generated_at": datetime.now().isoformat(),
            "schema": {
                "version": "2.0",
                "layers": ["raw", "derived", "offsets", "provenance"],
                "description": "Layered provenance schema: raw measurements are immutable, derived values are calibrated, provenance tracks transformations"
            },
            "metadata": {
                "total_records": len(self.records),
                "records_with_observations": sum(1 for r in self.records if r.measured_phi is not None),
                "records_calibrated": sum(1 for r in self.records if r.calibrated_phi is not None),
                "unique_promoters": len(set(r.promoter_id for r in self.records)),
                "unique_backends": len(set(r.backend for r in self.records)),
                "min_replicates_required": self.min_replicates,
                "tolerance": self.tolerance,
                "calibration_type_applied": calibration_type,
                "calibration_version": calibration_version
            },
            "backend_offsets": self.backend_offsets,
            "promoter_backend_offsets": self.promoter_offsets,
            "variance_structure": self.variance_structure.to_dict() if self.variance_structure else {},
            "transferability": self.transferability_result.to_dict() if self.transferability_result else {},
            "calibration_records": records_data,
            "recommendations": self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> Dict[str, Any]:
        """Generate actionable recommendations based on analysis."""
        recommendations = {
            "calibration_strategy": "",
            "backend_selection": "",
            "replicate_policy": "",
            "quality_gates": []
        }
        
        if self.transferability_result:
            if self.transferability_result.is_portable:
                recommendations["calibration_strategy"] = (
                    "Use unified calibration across backends. "
                    f"Reference backend {self.transferability_result.reference_backend} "
                    "offset is portable."
                )
            else:
                recommendations["calibration_strategy"] = (
                    "Use backend-specific calibration. "
                    "Each backend requires independent offset fitting."
                )
        
        if self.variance_structure:
            # Recommend replicate count based on within-promoter variance
            mean_within_var = self.variance_structure.within_promoter_mean
            if mean_within_var > 0:
                # Estimate required replicates for 95% CI width < tolerance
                required_replicates = int(np.ceil(4 * np.sqrt(mean_within_var) / self.tolerance))
                recommendations["replicate_policy"] = (
                    f"Recommend {max(self.min_replicates, required_replicates)} replicates "
                    f"per promoter-backend combination for stable calibration."
                )
            
            # Quality gates based on residual distribution
            if self.variance_structure.residual_std:
                recommendations["quality_gates"] = [
                    f"Residual |z-score| < 2.0 (95% CI)",
                    f"Within-promoter variance < {self.variance_structure.within_promoter_mean * 2:.6f}",
                    f"Transfer efficiency > 90% for portable calibration"
                ]
        
        # Backend selection
        if self.backend_offsets:
            best_backend = min(self.backend_offsets.items(), key=lambda x: abs(x[1]))
            recommendations["backend_selection"] = (
                f"Preferred backend: {best_backend[0]} "
                f"(offset magnitude: {abs(best_backend[1]):.4f})"
            )
        
        return recommendations
    
    def save_calibration_database(self, output_path: Path, calibration_type: str = "backend",
                                   calibration_version: str = "1.0"):
        """
        Save calibration records to JSON database with layered provenance.
        
        Args:
            output_path: Path to save the report
            calibration_type: "backend", "promoter", or "unified"
            calibration_version: Version string for provenance tracking
        """
        report = self.generate_calibration_report(calibration_type, calibration_version)
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"Calibration database saved to: {output_path}")
        print(f"  Schema version: 2.0 (layered provenance)")
        print(f"  Calibration type: {calibration_type}")
        print(f"  Calibration version: {calibration_version}")


# ─────────────────────────────────────────────────────────────────────────────
# CLI Entry Point
# ─────────────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Replicate-Aware Promoter Calibration System v2.0 (Layered Provenance)"
    )
    parser.add_argument(
        "--manifest",
        action="append",
        required=True,
        help="Path to schedule manifest JSON (repeatable for multiple manifests)"
    )
    parser.add_argument(
        "--output",
        default="raw_hardware/replicate_aware_calibration_report.json",
        help="Output calibration report path"
    )
    parser.add_argument(
        "--tolerance",
        type=float,
        default=0.15,
        help="Calibration tolerance threshold"
    )
    parser.add_argument(
        "--min-replicates",
        type=int,
        default=2,
        help="Minimum replicates required for variance estimation"
    )
    parser.add_argument(
        "--reference-backend",
        default="ibm_fez",
        help="Reference backend for transferability testing"
    )
    parser.add_argument(
        "--calibration-type",
        choices=["backend", "promoter", "unified"],
        default="backend",
        help="Calibration type: backend (backend-specific), promoter (promoter-backend), unified (reference backend)"
    )
    parser.add_argument(
        "--calibration-version",
        default="1.0",
        help="Calibration version string for provenance tracking"
    )
    
    args = parser.parse_args()
    
    # Initialize calibrator
    calibrator = ReplicateAwareCalibrator(
        tolerance=args.tolerance,
        min_replicates=args.min_replicates
    )
    
    # Load manifests
    manifest_paths = [Path(p) for p in args.manifest]
    missing = [str(p) for p in manifest_paths if not p.exists()]
    
    if missing:
        print("ERROR: Missing manifest files:")
        for path in missing:
            print(f"  - {path}")
        return 1
    
    total_records = 0
    for manifest_path in manifest_paths:
        records_loaded = calibrator.load_from_manifest(manifest_path)
        print(f"Loaded {records_loaded} records from: {manifest_path}")
        total_records += records_loaded
    
    # Run calibration pipeline
    print("\n" + "=" * 80)
    print("REPLICATE-AWARE PROMOTER CALIBRATION v2.0")
    print("=" * 80)
    print(f"Schema: Layered provenance (raw/derived/offsets/provenance)")
    print(f"Calibration type: {args.calibration_type}")
    print(f"Calibration version: {args.calibration_version}")
    
    # Fit offsets
    backend_offsets = calibrator.fit_backend_offsets()
    print(f"\nBackend Offsets:")
    for backend, offset in backend_offsets.items():
        print(f"  {backend}: {offset:+.6f}")
    
    promoter_offsets = calibrator.fit_promoter_backend_offsets()
    print(f"\nPromoter-Backend Offsets:")
    for promoter, offsets in promoter_offsets.items():
        print(f"  {promoter}:")
        for backend, offset in offsets.items():
            print(f"    {backend}: {offset:+.6f}")
    
    # Estimate variance structure
    variance = calibrator.estimate_variance_structure()
    print(f"\nVariance Structure:")
    print(f"  Within-promoter mean variance: {variance.within_promoter_mean:.6e}")
    print(f"  Between-promoter mean variance: {variance.between_promoter_mean:.6e}")
    print(f"  Residual std: {variance.residual_std:.6f}")
    
    # Test transferability
    transfer = calibrator.test_transferability(args.reference_backend)
    print(f"\nTransferability:")
    print(f"  Reference backend: {transfer.reference_backend}")
    print(f"  Portability score: {transfer.portability_score:.2%}")
    print(f"  Is portable: {transfer.is_portable}")
    print(f"  Recommendation: {transfer.recommendation}")
    
    # Apply calibration and show sample
    calibrated_count = calibrator.apply_calibration_to_all(args.calibration_type, args.calibration_version)
    print(f"\nCalibration Applied:")
    print(f"  Records calibrated: {calibrated_count}/{total_records}")
    if calibrator.records:
        sample = calibrator.records[0]
        print(f"  Sample record ({sample.record_id}):")
        print(f"    Raw measured_phi: {sample.raw_measured_phi:.6f}")
        print(f"    Backend calibrated: {sample.backend_calibrated_phi:.6f}")
        print(f"    Final calibrated: {sample.calibrated_phi:.6f}")
        print(f"    Offset applied: {sample.calibration_offset_applied:+.6f}")
    
    # Save report
    output_path = Path(args.output)
    calibrator.save_calibration_database(output_path, args.calibration_type, args.calibration_version)
    
    print("\n" + "=" * 80)
    print("CALIBRATION COMPLETE")
    print("=" * 80)
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())