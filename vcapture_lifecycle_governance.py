#!/usr/bin/env python3
"""
VCapture Lifecycle Governance System v2.0
=========================================

Full calibration lifecycle management with:
- Promotion state machine (development → candidate → staging → production → retired)
- Warning bands for monitoring (pass/warning/fail)
- Downgrade conditions and automatic demotion
- Additional metrics: held-out performance, backend drift, rank stability CI, cohort coverage

This transforms VCapture from a governance layer into a complete
calibration lifecycle management system.

State Machine:
    development → candidate → staging → production → retired
         ↑______________|__________|__________|
                    (downgrade conditions)

Usage:
    python vcapture_lifecycle_governance.py --ledger raw_hardware/vcapture_ledger_report.json
"""

import argparse
import json
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import warnings

import numpy as np
from scipy import stats


# =============================================================================
# PROMOTION STATE MACHINE
# =============================================================================

class CalibrationState(str, Enum):
    """
    Calibration model lifecycle states.
    
    State transitions:
    - development → candidate: Passes all development gates
    - candidate → staging: Passes all candidate gates
    - staging → production: Passes all production gates
    - production → retired: Deprecated or replaced
    - Any state → development: Fails critical gates (downgrade)
    - Any state → retired: Explicit deprecation
    """
    DEVELOPMENT = "development"  # Initial state, not ready for use
    CANDIDATE = "candidate"      # Ready for cross-validation
    STAGING = "staging"          # Ready for limited deployment
    PRODUCTION = "production"    # Ready for full deployment
    RETIRED = "retired"          # Deprecated, should be replaced


class GateStatus(str, Enum):
    """Gate evaluation status with warning bands."""
    PASS = "pass"          # Meets threshold with margin
    WARNING = "warning"    # Within warning band, needs attention
    FAIL = "fail"          # Below threshold, blocks promotion


# =============================================================================
# WARNING BAND THRESHOLDS
# =============================================================================

@dataclass
class WarningBandThresholds:
    """
    Three-tier thresholds: pass, warning, fail.
    
    This enables proactive monitoring instead of binary pass/fail.
    """
    # Pass threshold: value must be at least this good
    pass_threshold: float
    
    # Warning threshold: between pass and warning = needs attention
    warning_threshold: float
    
    # Fail threshold: below this = blocked
    # (implicit: anything below warning_threshold is fail)
    
    # Higher-is-better or lower-is-better?
    higher_is_better: bool = True
    
    def evaluate(self, value: float) -> GateStatus:
        """Evaluate a value against warning bands."""
        if self.higher_is_better:
            if value >= self.pass_threshold:
                return GateStatus.PASS
            elif value >= self.warning_threshold:
                return GateStatus.WARNING
            else:
                return GateStatus.FAIL
        else:
            # Lower is better (e.g., residual std)
            if value <= self.pass_threshold:
                return GateStatus.PASS
            elif value <= self.warning_threshold:
                return GateStatus.WARNING
            else:
                return GateStatus.FAIL


@dataclass
class LifecycleThresholds:
    """
    Complete threshold configuration for all states and gates.
    
    Each gate has:
    - pass_threshold: Required for promotion
    - warning_threshold: Triggers monitoring alert
    - fail_threshold: Blocks promotion (implicit from warning)
    """
    # Replicate Count Gate
    min_replicates_per_cell: WarningBandThresholds = field(
        default_factory=lambda: WarningBandThresholds(3, 2, higher_is_better=True)
    )
    min_total_records: WarningBandThresholds = field(
        default_factory=lambda: WarningBandThresholds(20, 15, higher_is_better=True)
    )
    
    # Residual Spread Gate
    max_residual_std: WarningBandThresholds = field(
        default_factory=lambda: WarningBandThresholds(0.10, 0.15, higher_is_better=False)
    )
    max_residual_mean_abs: WarningBandThresholds = field(
        default_factory=lambda: WarningBandThresholds(0.05, 0.08, higher_is_better=False)
    )
    max_residual_mad: WarningBandThresholds = field(
        default_factory=lambda: WarningBandThresholds(0.08, 0.12, higher_is_better=False)
    )
    
    # Signal-to-Separation Gate
    min_ss_ratio: WarningBandThresholds = field(
        default_factory=lambda: WarningBandThresholds(2.0, 1.5, higher_is_better=True)
    )
    min_promoters_above_threshold: WarningBandThresholds = field(
        default_factory=lambda: WarningBandThresholds(0.5, 0.4, higher_is_better=True)
    )
    
    # Portability Gate
    min_transfer_efficiency: WarningBandThresholds = field(
        default_factory=lambda: WarningBandThresholds(0.90, 0.85, higher_is_better=True)
    )
    min_ranking_correlation: WarningBandThresholds = field(
        default_factory=lambda: WarningBandThresholds(0.80, 0.70, higher_is_better=True)
    )
    min_portability_score: WarningBandThresholds = field(
        default_factory=lambda: WarningBandThresholds(0.85, 0.75, higher_is_better=True)
    )
    
    # Stability Gate
    max_output_stability: WarningBandThresholds = field(
        default_factory=lambda: WarningBandThresholds(0.01, 0.02, higher_is_better=False)
    )
    max_convergence_stability: WarningBandThresholds = field(
        default_factory=lambda: WarningBandThresholds(0.1, 0.2, higher_is_better=False)
    )
    
    # Model Fit Gate
    min_r_squared: WarningBandThresholds = field(
        default_factory=lambda: WarningBandThresholds(0.70, 0.60, higher_is_better=True)
    )
    max_interaction_variance_ratio: WarningBandThresholds = field(
        default_factory=lambda: WarningBandThresholds(0.1, 0.2, higher_is_better=False)
    )
    
    # NEW: Held-Out Performance Gate
    min_heldout_correlation: WarningBandThresholds = field(
        default_factory=lambda: WarningBandThresholds(0.75, 0.65, higher_is_better=True)
    )
    max_heldout_mae: WarningBandThresholds = field(
        default_factory=lambda: WarningBandThresholds(0.10, 0.15, higher_is_better=False)
    )
    
    # NEW: Backend Drift Gate
    max_backend_drift: WarningBandThresholds = field(
        default_factory=lambda: WarningBandThresholds(0.05, 0.08, higher_is_better=False)
    )
    
    # NEW: Rank Stability CI Gate
    min_rank_stability_ci_lower: WarningBandThresholds = field(
        default_factory=lambda: WarningBandThresholds(0.70, 0.60, higher_is_better=True)
    )
    
    # NEW: Cohort Coverage Gate
    min_cohort_coverage: WarningBandThresholds = field(
        default_factory=lambda: WarningBandThresholds(0.80, 0.70, higher_is_better=True)
    )


# State-specific thresholds (relaxed for lower states)
STATE_THRESHOLDS = {
    CalibrationState.DEVELOPMENT: LifecycleThresholds(
        min_replicates_per_cell=WarningBandThresholds(1, 1, True),
        min_total_records=WarningBandThresholds(5, 3, True),
        max_residual_std=WarningBandThresholds(0.20, 0.30, False),
        max_residual_mean_abs=WarningBandThresholds(0.10, 0.15, False),
        min_ss_ratio=WarningBandThresholds(1.0, 0.8, True),
        min_transfer_efficiency=WarningBandThresholds(0.70, 0.60, True),
        min_ranking_correlation=WarningBandThresholds(0.50, 0.40, True),
        min_r_squared=WarningBandThresholds(0.50, 0.40, True),
    ),
    CalibrationState.CANDIDATE: LifecycleThresholds(
        min_replicates_per_cell=WarningBandThresholds(2, 1, True),
        min_total_records=WarningBandThresholds(15, 10, True),
        max_residual_std=WarningBandThresholds(0.15, 0.20, False),
        max_residual_mean_abs=WarningBandThresholds(0.08, 0.10, False),
        min_ss_ratio=WarningBandThresholds(1.5, 1.2, True),
        min_transfer_efficiency=WarningBandThresholds(0.85, 0.75, True),
        min_ranking_correlation=WarningBandThresholds(0.70, 0.60, True),
        min_r_squared=WarningBandThresholds(0.60, 0.50, True),
    ),
    CalibrationState.STAGING: LifecycleThresholds(
        min_replicates_per_cell=WarningBandThresholds(3, 2, True),
        min_total_records=WarningBandThresholds(20, 15, True),
        max_residual_std=WarningBandThresholds(0.12, 0.15, False),
        max_residual_mean_abs=WarningBandThresholds(0.06, 0.08, False),
        min_ss_ratio=WarningBandThresholds(1.8, 1.5, True),
        min_transfer_efficiency=WarningBandThresholds(0.88, 0.82, True),
        min_ranking_correlation=WarningBandThresholds(0.75, 0.68, True),
        min_r_squared=WarningBandThresholds(0.65, 0.55, True),
    ),
    CalibrationState.PRODUCTION: LifecycleThresholds(),  # Default strict thresholds
}


# =============================================================================
# GATE RESULTS WITH WARNING BANDS
# =============================================================================

@dataclass
class EnhancedGateResult:
    """Gate result with warning band status."""
    gate_name: str
    status: GateStatus  # pass, warning, or fail
    value: float
    pass_threshold: float
    warning_threshold: float
    margin_to_pass: float  # value - pass_threshold
    margin_to_warning: float  # value - warning_threshold
    message: str
    
    # For tracking over time
    trend: Optional[str] = None  # "improving", "stable", "degrading"
    previous_value: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "gate_name": self.gate_name,
            "status": self.status.value,
            "value": self.value,
            "pass_threshold": self.pass_threshold,
            "warning_threshold": self.warning_threshold,
            "margin_to_pass": self.margin_to_pass,
            "margin_to_warning": self.margin_to_warning,
            "message": self.message,
            "trend": self.trend,
            "previous_value": self.previous_value,
        }


@dataclass
class CohortCoverage:
    """Coverage metrics for the calibration cohort."""
    total_promoters: int
    promoters_above_ss_threshold: int
    fraction_promoters_above_ss: float
    
    total_backend_pairs: int
    backend_pairs_tested: int
    fraction_backend_pairs_tested: float
    
    total_cells: int  # promoter × backend combinations
    cells_with_min_replicates: int
    fraction_cells_covered: float
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BackendDriftReport:
    """Backend drift detection results."""
    backend_name: str
    baseline_date: str
    current_date: str
    drift_magnitude: float
    drift_components: Dict[str, float]  # e.g., {"t1": 0.02, "t2": 0.03}
    is_significant: bool
    p_value: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RankStabilityCI:
    """Ranking correlation with confidence interval."""
    point_estimate: float
    ci_lower: float
    ci_upper: float
    confidence_level: float
    n_observations: int
    method: str  # "bootstrap", "fisher_z", "permutation"
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class HeldOutPerformance:
    """Performance on held-out promoters."""
    heldout_promoters: List[str]
    correlation_with_observed: float
    mae: float
    rmse: float
    coverage: float  # Fraction of held-out with predictions
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# =============================================================================
# LIFECYCLE ASSESSMENT
# =============================================================================

@dataclass
class LifecycleAssessment:
    """Complete lifecycle assessment with state machine."""
    # Current state
    current_state: str
    target_state: str
    eligible_for_promotion: bool
    requires_downgrade: bool
    
    # Gate results (enhanced with warning bands)
    replicate_gate: EnhancedGateResult
    residual_gate: EnhancedGateResult
    separation_gate: EnhancedGateResult
    portability_gate: EnhancedGateResult
    stability_gate: EnhancedGateResult
    model_fit_gate: EnhancedGateResult
    
    # NEW gates
    heldout_gate: Optional[EnhancedGateResult] = None
    drift_gate: Optional[EnhancedGateResult] = None
    rank_ci_gate: Optional[EnhancedGateResult] = None
    coverage_gate: Optional[EnhancedGateResult] = None
    
    # Additional metrics
    cohort_coverage: Optional[CohortCoverage] = None
    backend_drift: Optional[BackendDriftReport] = None
    rank_stability_ci: Optional[RankStabilityCI] = None
    heldout_performance: Optional[HeldOutPerformance] = None
    
    # State transition log
    state_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Summary
    blocking_issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    # Metadata
    assessed_at: str = ""
    ledger_path: str = ""
    calibration_version: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "current_state": self.current_state,
            "target_state": self.target_state,
            "eligible_for_promotion": self.eligible_for_promotion,
            "requires_downgrade": self.requires_downgrade,
            "gates": {
                "replicate": self.replicate_gate.to_dict(),
                "residual": self.residual_gate.to_dict(),
                "separation": self.separation_gate.to_dict(),
                "portability": self.portability_gate.to_dict(),
                "stability": self.stability_gate.to_dict(),
                "model_fit": self.model_fit_gate.to_dict(),
                "heldout": self.heldout_gate.to_dict() if self.heldout_gate else None,
                "drift": self.drift_gate.to_dict() if self.drift_gate else None,
                "rank_ci": self.rank_ci_gate.to_dict() if self.rank_ci_gate else None,
                "coverage": self.coverage_gate.to_dict() if self.coverage_gate else None,
            },
            "cohort_coverage": self.cohort_coverage.to_dict() if self.cohort_coverage else None,
            "backend_drift": self.backend_drift.to_dict() if self.backend_drift else None,
            "rank_stability_ci": self.rank_stability_ci.to_dict() if self.rank_stability_ci else None,
            "heldout_performance": self.heldout_performance.to_dict() if self.heldout_performance else None,
            "state_history": self.state_history,
            "blocking_issues": self.blocking_issues,
            "warnings": self.warnings,
            "recommendations": self.recommendations,
            "assessed_at": self.assessed_at,
            "ledger_path": self.ledger_path,
            "calibration_version": self.calibration_version,
        }


# =============================================================================
# LIFECYCLE GOVERNANCE ENGINE
# =============================================================================

class VCaptureLifecycleGovernance:
    """
    Full lifecycle governance for calibration models.
    
    Features:
    - State machine with explicit transitions
    - Warning bands for proactive monitoring
    - Downgrade conditions for automatic demotion
    - Additional metrics for comprehensive assessment
    """
    
    def __init__(self,
                 current_state: CalibrationState = CalibrationState.DEVELOPMENT,
                 target_state: CalibrationState = CalibrationState.PRODUCTION,
                 thresholds: Optional[LifecycleThresholds] = None):
        self.current_state = current_state
        self.target_state = target_state
        self.thresholds = thresholds or STATE_THRESHOLDS[current_state]
        self.state_history: List[Dict[str, Any]] = []
    
    def assess_ledger(self, ledger_path: Path, 
                      previous_assessment: Optional[Dict] = None) -> LifecycleAssessment:
        """
        Assess a VCapture ledger with full lifecycle governance.
        
        Args:
            ledger_path: Path to VCapture ledger JSON
            previous_assessment: Previous assessment for trend tracking
            
        Returns:
            LifecycleAssessment with state machine evaluation
        """
        with open(ledger_path, 'r', encoding='utf-8') as f:
            ledger = json.load(f)
        
        # Extract metrics
        metadata = ledger.get('metadata', {})
        variance = ledger.get('variance_structure', {})
        transfer = ledger.get('transferability', [])
        mixed = ledger.get('mixed_effects', {})
        
        # Run enhanced gates
        replicate_gate = self._assess_replicate_gate_enhanced(
            metadata, variance, previous_assessment
        )
        residual_gate = self._assess_residual_gate_enhanced(
            variance, previous_assessment
        )
        separation_gate = self._assess_separation_gate_enhanced(
            variance, previous_assessment
        )
        portability_gate = self._assess_portability_gate_enhanced(
            transfer, previous_assessment
        )
        stability_gate = self._assess_stability_gate_enhanced(
            variance, previous_assessment
        )
        model_fit_gate = self._assess_model_fit_gate_enhanced(
            mixed, previous_assessment
        )
        
        # NEW: Additional gates
        heldout_gate = self._assess_heldout_gate(variance, previous_assessment)
        drift_gate = self._assess_drift_gate(metadata, previous_assessment)
        rank_ci_gate = self._assess_rank_ci_gate(transfer, previous_assessment)
        coverage_gate = self._assess_coverage_gate(variance, metadata, previous_assessment)
        
        # Compute additional metrics
        cohort_coverage = self._compute_cohort_coverage(variance, metadata)
        backend_drift = self._compute_backend_drift(metadata)
        rank_stability_ci = self._compute_rank_stability_ci(transfer)
        heldout_performance = self._compute_heldout_performance(variance)
        
        # Collect all gates
        gates = [
            replicate_gate, residual_gate, separation_gate,
            portability_gate, stability_gate, model_fit_gate,
            heldout_gate, drift_gate, rank_ci_gate, coverage_gate
        ]
        gates = [g for g in gates if g is not None]
        
        # Determine state transition
        eligible, requires_downgrade = self._evaluate_state_transition(gates)
        
        # Generate summary
        blocking_issues = [
            g.message for g in gates if g.status == GateStatus.FAIL
        ]
        warnings = [
            g.message for g in gates if g.status == GateStatus.WARNING
        ]
        recommendations = self._generate_recommendations(gates)
        
        return LifecycleAssessment(
            current_state=self.current_state.value,
            target_state=self.target_state.value,
            eligible_for_promotion=eligible,
            requires_downgrade=requires_downgrade,
            replicate_gate=replicate_gate,
            residual_gate=residual_gate,
            separation_gate=separation_gate,
            portability_gate=portability_gate,
            stability_gate=stability_gate,
            model_fit_gate=model_fit_gate,
            heldout_gate=heldout_gate,
            drift_gate=drift_gate,
            rank_ci_gate=rank_ci_gate,
            coverage_gate=coverage_gate,
            cohort_coverage=cohort_coverage,
            backend_drift=backend_drift,
            rank_stability_ci=rank_stability_ci,
            heldout_performance=heldout_performance,
            state_history=self.state_history,
            blocking_issues=blocking_issues,
            warnings=warnings,
            recommendations=recommendations,
            assessed_at=datetime.now().isoformat(),
            ledger_path=str(ledger_path),
            calibration_version=metadata.get('calibration_version', 'unknown'),
        )
    
    def _evaluate_state_transition(self, gates: List[EnhancedGateResult]) -> Tuple[bool, bool]:
        """
        Evaluate state transition based on gate results.
        
        Returns:
            (eligible_for_promotion, requires_downgrade)
        """
        # Count gate statuses
        n_pass = sum(1 for g in gates if g.status == GateStatus.PASS)
        n_warning = sum(1 for g in gates if g.status == GateStatus.WARNING)
        n_fail = sum(1 for g in gates if g.status == GateStatus.FAIL)
        
        # Critical gates that trigger downgrade
        critical_gates = ["residual_spread", "stability", "model_fit"]
        critical_failures = [
            g for g in gates 
            if g.gate_name in critical_gates and g.status == GateStatus.FAIL
        ]
        
        # Determine eligibility
        if n_fail == 0:
            eligible_for_promotion = True
        elif n_fail <= 2 and n_pass >= 6:
            eligible_for_promotion = True  # Minor failures, mostly passing
        else:
            eligible_for_promotion = False
        
        # Determine downgrade
        if len(critical_failures) > 0:
            requires_downgrade = True
        elif n_fail > 4:
            requires_downgrade = True
        else:
            requires_downgrade = False
        
        return eligible_for_promotion, requires_downgrade
    
    def _assess_replicate_gate_enhanced(self, metadata: Dict, variance: Dict,
                                         previous: Optional[Dict]) -> EnhancedGateResult:
        """Assess replicate count with warning bands."""
        total_records = metadata.get('total_records', 0)
        summaries = variance.get('promoter_backend_summaries', [])
        
        min_replicates = min(
            (s.get('replicate_count', 0) for s in summaries),
            default=0
        )
        
        # Evaluate against thresholds
        cell_status = self.thresholds.min_replicates_per_cell.evaluate(min_replicates)
        record_status = self.thresholds.min_total_records.evaluate(total_records)
        
        # Use worse status
        status = cell_status if cell_status.value > record_status.value else record_status
        # (FAIL > WARNING > PASS in terms of severity)
        status_order = {GateStatus.FAIL: 2, GateStatus.WARNING: 1, GateStatus.PASS: 0}
        status = cell_status if status_order[cell_status] > status_order[record_status] else record_status
        
        value = float(min_replicates)
        previous_value = previous.get('gates', {}).get('replicate', {}).get('value') if previous else None
        trend = self._compute_trend(value, previous_value, higher_is_better=True)
        
        return EnhancedGateResult(
            gate_name="replicate_count",
            status=status,
            value=value,
            pass_threshold=self.thresholds.min_replicates_per_cell.pass_threshold,
            warning_threshold=self.thresholds.min_replicates_per_cell.warning_threshold,
            margin_to_pass=value - self.thresholds.min_replicates_per_cell.pass_threshold,
            margin_to_warning=value - self.thresholds.min_replicates_per_cell.warning_threshold,
            message=f"Replicate count: {min_replicates} per cell, {total_records} total ({status.value})",
            trend=trend,
            previous_value=previous_value,
        )
    
    def _assess_residual_gate_enhanced(self, variance: Dict,
                                        previous: Optional[Dict]) -> EnhancedGateResult:
        """Assess residual spread with warning bands."""
        residual_mean = abs(variance.get('residual_mean', 1.0))
        residual_std = variance.get('residual_std', 1.0)
        
        # Evaluate both metrics
        mean_status = self.thresholds.max_residual_mean_abs.evaluate(residual_mean)
        std_status = self.thresholds.max_residual_std.evaluate(residual_std)
        
        # Use worse status
        status_order = {GateStatus.FAIL: 2, GateStatus.WARNING: 1, GateStatus.PASS: 0}
        status = mean_status if status_order[mean_status] > status_order[std_status] else std_status
        
        value = float(residual_std)
        previous_value = previous.get('gates', {}).get('residual', {}).get('value') if previous else None
        trend = self._compute_trend(value, previous_value, higher_is_better=False)
        
        return EnhancedGateResult(
            gate_name="residual_spread",
            status=status,
            value=value,
            pass_threshold=self.thresholds.max_residual_std.pass_threshold,
            warning_threshold=self.thresholds.max_residual_std.warning_threshold,
            margin_to_pass=self.thresholds.max_residual_std.pass_threshold - value,
            margin_to_warning=self.thresholds.max_residual_std.warning_threshold - value,
            message=f"Residual spread: std={residual_std:.4f}, mean={residual_mean:.4f} ({status.value})",
            trend=trend,
            previous_value=previous_value,
        )
    
    def _assess_separation_gate_enhanced(self, variance: Dict,
                                          previous: Optional[Dict]) -> EnhancedGateResult:
        """Assess signal-to-separation with warning bands."""
        summaries = variance.get('promoter_backend_summaries', [])
        
        if not summaries:
            return EnhancedGateResult(
                gate_name="signal_to_separation",
                status=GateStatus.FAIL,
                value=0.0,
                pass_threshold=self.thresholds.min_ss_ratio.pass_threshold,
                warning_threshold=self.thresholds.min_ss_ratio.warning_threshold,
                margin_to_pass=-self.thresholds.min_ss_ratio.pass_threshold,
                margin_to_warning=-self.thresholds.min_ss_ratio.warning_threshold,
                message="No promoter-backend summaries available",
            )
        
        ss_values = [s.get('signal_to_separation', 0) for s in summaries]
        mean_ss = float(np.mean(ss_values)) if ss_values else 0
        
        status = self.thresholds.min_ss_ratio.evaluate(mean_ss)
        
        previous_value = previous.get('gates', {}).get('separation', {}).get('value') if previous else None
        trend = self._compute_trend(mean_ss, previous_value, higher_is_better=True)
        
        return EnhancedGateResult(
            gate_name="signal_to_separation",
            status=status,
            value=mean_ss,
            pass_threshold=self.thresholds.min_ss_ratio.pass_threshold,
            warning_threshold=self.thresholds.min_ss_ratio.warning_threshold,
            margin_to_pass=mean_ss - self.thresholds.min_ss_ratio.pass_threshold,
            margin_to_warning=mean_ss - self.thresholds.min_ss_ratio.warning_threshold,
            message=f"Signal-to-separation: mean S/S={mean_ss:.2f} ({status.value})",
            trend=trend,
            previous_value=previous_value,
        )
    
    def _assess_portability_gate_enhanced(self, transfer: List[Dict],
                                            previous: Optional[Dict]) -> EnhancedGateResult:
        """Assess portability with warning bands."""
        if not transfer:
            return EnhancedGateResult(
                gate_name="portability",
                status=GateStatus.FAIL,
                value=0.0,
                pass_threshold=self.thresholds.min_portability_score.pass_threshold,
                warning_threshold=self.thresholds.min_portability_score.warning_threshold,
                margin_to_pass=-self.thresholds.min_portability_score.pass_threshold,
                margin_to_warning=-self.thresholds.min_portability_score.warning_threshold,
                message="No transferability data available",
            )
        
        tr = transfer[0]
        transfer_efficiency = tr.get('transfer_efficiency', 0)
        ranking_corr = abs(tr.get('promoter_ranking_correlation', 0))
        portability_score = tr.get('portability_score', 0)
        
        # Evaluate all three metrics
        eff_status = self.thresholds.min_transfer_efficiency.evaluate(transfer_efficiency)
        corr_status = self.thresholds.min_ranking_correlation.evaluate(ranking_corr)
        score_status = self.thresholds.min_portability_score.evaluate(portability_score)
        
        # Use worst status
        status_order = {GateStatus.FAIL: 2, GateStatus.WARNING: 1, GateStatus.PASS: 0}
        status = max([eff_status, corr_status, score_status], 
                     key=lambda s: status_order[s])
        
        value = float(portability_score)
        previous_value = previous.get('gates', {}).get('portability', {}).get('value') if previous else None
        trend = self._compute_trend(value, previous_value, higher_is_better=True)
        
        return EnhancedGateResult(
            gate_name="portability",
            status=status,
            value=value,
            pass_threshold=self.thresholds.min_portability_score.pass_threshold,
            warning_threshold=self.thresholds.min_portability_score.warning_threshold,
            margin_to_pass=value - self.thresholds.min_portability_score.pass_threshold,
            margin_to_warning=value - self.thresholds.min_portability_score.warning_threshold,
            message=f"Portability: efficiency={transfer_efficiency:.1%}, ranking={ranking_corr:.2f}, score={portability_score:.1%} ({status.value})",
            trend=trend,
            previous_value=previous_value,
        )
    
    def _assess_stability_gate_enhanced(self, variance: Dict,
                                         previous: Optional[Dict]) -> EnhancedGateResult:
        """Assess stability with warning bands."""
        within_var = variance.get('within_promoter_variance', {})
        
        if not within_var:
            return EnhancedGateResult(
                gate_name="stability",
                status=GateStatus.FAIL,
                value=1.0,
                pass_threshold=self.thresholds.max_output_stability.pass_threshold,
                warning_threshold=self.thresholds.max_output_stability.warning_threshold,
                margin_to_pass=self.thresholds.max_output_stability.pass_threshold - 1.0,
                margin_to_warning=self.thresholds.max_output_stability.warning_threshold - 1.0,
                message="No within-promoter variance data available",
            )
        
        within_stds = [np.sqrt(v) for v in within_var.values() if v > 0]
        mean_stability = float(np.mean(within_stds)) if within_stds else 1.0
        
        status = self.thresholds.max_output_stability.evaluate(mean_stability)
        
        previous_value = previous.get('gates', {}).get('stability', {}).get('value') if previous else None
        trend = self._compute_trend(mean_stability, previous_value, higher_is_better=False)
        
        return EnhancedGateResult(
            gate_name="stability",
            status=status,
            value=mean_stability,
            pass_threshold=self.thresholds.max_output_stability.pass_threshold,
            warning_threshold=self.thresholds.max_output_stability.warning_threshold,
            margin_to_pass=self.thresholds.max_output_stability.pass_threshold - mean_stability,
            margin_to_warning=self.thresholds.max_output_stability.warning_threshold - mean_stability,
            message=f"Stability: within-promoter std={mean_stability:.6f} ({status.value})",
            trend=trend,
            previous_value=previous_value,
        )
    
    def _assess_model_fit_gate_enhanced(self, mixed: Dict,
                                         previous: Optional[Dict]) -> EnhancedGateResult:
        """Assess model fit with warning bands."""
        if not mixed:
            return EnhancedGateResult(
                gate_name="model_fit",
                status=GateStatus.FAIL,
                value=0.0,
                pass_threshold=self.thresholds.min_r_squared.pass_threshold,
                warning_threshold=self.thresholds.min_r_squared.warning_threshold,
                margin_to_pass=-self.thresholds.min_r_squared.pass_threshold,
                margin_to_warning=-self.thresholds.min_r_squared.warning_threshold,
                message="No mixed-effects model data available",
            )
        
        model_stats = mixed.get('model_statistics', {})
        var_components = mixed.get('variance_components', {})
        
        r_squared = model_stats.get('r_squared', 0)
        
        # Check interaction variance ratio
        total_var = sum(var_components.values()) if var_components else 1
        interaction_var = var_components.get('interaction', 0)
        interaction_ratio = interaction_var / total_var if total_var > 0 else 0
        
        # Evaluate both metrics
        r2_status = self.thresholds.min_r_squared.evaluate(r_squared)
        int_status = self.thresholds.max_interaction_variance_ratio.evaluate(interaction_ratio)
        
        # Use worse status
        status_order = {GateStatus.FAIL: 2, GateStatus.WARNING: 1, GateStatus.PASS: 0}
        status = r2_status if status_order[r2_status] > status_order[int_status] else int_status
        
        value = float(r_squared)
        previous_value = previous.get('gates', {}).get('model_fit', {}).get('value') if previous else None
        trend = self._compute_trend(value, previous_value, higher_is_better=True)
        
        return EnhancedGateResult(
            gate_name="model_fit",
            status=status,
            value=value,
            pass_threshold=self.thresholds.min_r_squared.pass_threshold,
            warning_threshold=self.thresholds.min_r_squared.warning_threshold,
            margin_to_pass=value - self.thresholds.min_r_squared.pass_threshold,
            margin_to_warning=value - self.thresholds.min_r_squared.warning_threshold,
            message=f"Model fit: R²={r_squared:.4f}, interaction ratio={interaction_ratio:.4f} ({status.value})",
            trend=trend,
            previous_value=previous_value,
        )
    
    # =========================================================================
    # NEW GATES
    # =========================================================================
    
    def _assess_heldout_gate(self, variance: Dict,
                              previous: Optional[Dict]) -> Optional[EnhancedGateResult]:
        """Assess held-out promoter performance."""
        # This would require actual held-out data
        # For now, return None if not available
        heldout = variance.get('heldout_performance', {})
        
        if not heldout:
            return None
        
        correlation = heldout.get('correlation', 0)
        mae = heldout.get('mae', 1.0)
        
        # Evaluate
        corr_status = self.thresholds.min_heldout_correlation.evaluate(correlation)
        mae_status = self.thresholds.max_heldout_mae.evaluate(mae)
        
        status_order = {GateStatus.FAIL: 2, GateStatus.WARNING: 1, GateStatus.PASS: 0}
        status = corr_status if status_order[corr_status] > status_order[mae_status] else mae_status
        
        return EnhancedGateResult(
            gate_name="heldout_performance",
            status=status,
            value=float(correlation),
            pass_threshold=self.thresholds.min_heldout_correlation.pass_threshold,
            warning_threshold=self.thresholds.min_heldout_correlation.warning_threshold,
            margin_to_pass=correlation - self.thresholds.min_heldout_correlation.pass_threshold,
            margin_to_warning=correlation - self.thresholds.min_heldout_correlation.warning_threshold,
            message=f"Held-out performance: correlation={correlation:.2f}, MAE={mae:.4f} ({status.value})",
        )
    
    def _assess_drift_gate(self, metadata: Dict,
                            previous: Optional[Dict]) -> Optional[EnhancedGateResult]:
        """Assess backend drift."""
        drift = metadata.get('backend_drift', {})
        
        if not drift:
            return None
        
        drift_magnitude = drift.get('magnitude', 0)
        
        status = self.thresholds.max_backend_drift.evaluate(drift_magnitude)
        
        return EnhancedGateResult(
            gate_name="backend_drift",
            status=status,
            value=float(drift_magnitude),
            pass_threshold=self.thresholds.max_backend_drift.pass_threshold,
            warning_threshold=self.thresholds.max_backend_drift.warning_threshold,
            margin_to_pass=self.thresholds.max_backend_drift.pass_threshold - drift_magnitude,
            margin_to_warning=self.thresholds.max_backend_drift.warning_threshold - drift_magnitude,
            message=f"Backend drift: magnitude={drift_magnitude:.4f} ({status.value})",
        )
    
    def _assess_rank_ci_gate(self, transfer: List[Dict],
                              previous: Optional[Dict]) -> Optional[EnhancedGateResult]:
        """Assess ranking correlation with confidence interval."""
        if not transfer:
            return None
        
        # Would compute bootstrap CI in practice
        # For now, use point estimate ± 0.1 as approximation
        ranking_corr = abs(transfer[0].get('promoter_ranking_correlation', 0))
        ci_lower = max(0, ranking_corr - 0.1)
        
        status = self.thresholds.min_rank_stability_ci_lower.evaluate(ci_lower)
        
        return EnhancedGateResult(
            gate_name="rank_stability_ci",
            status=status,
            value=float(ci_lower),
            pass_threshold=self.thresholds.min_rank_stability_ci_lower.pass_threshold,
            warning_threshold=self.thresholds.min_rank_stability_ci_lower.warning_threshold,
            margin_to_pass=ci_lower - self.thresholds.min_rank_stability_ci_lower.pass_threshold,
            margin_to_warning=ci_lower - self.thresholds.min_rank_stability_ci_lower.warning_threshold,
            message=f"Rank stability CI: [{ci_lower:.2f}, {ranking_corr + 0.1:.2f}] ({status.value})",
        )
    
    def _assess_coverage_gate(self, variance: Dict, metadata: Dict,
                               previous: Optional[Dict]) -> Optional[EnhancedGateResult]:
        """Assess cohort coverage."""
        coverage = self._compute_cohort_coverage(variance, metadata)
        
        if not coverage:
            return None
        
        fraction_covered = coverage.fraction_cells_covered
        
        status = self.thresholds.min_cohort_coverage.evaluate(fraction_covered)
        
        return EnhancedGateResult(
            gate_name="cohort_coverage",
            status=status,
            value=float(fraction_covered),
            pass_threshold=self.thresholds.min_cohort_coverage.pass_threshold,
            warning_threshold=self.thresholds.min_cohort_coverage.warning_threshold,
            margin_to_pass=fraction_covered - self.thresholds.min_cohort_coverage.pass_threshold,
            margin_to_warning=fraction_covered - self.thresholds.min_cohort_coverage.warning_threshold,
            message=f"Cohort coverage: {coverage.cells_with_min_replicates}/{coverage.total_cells} cells ({status.value})",
        )
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    def _compute_trend(self, current: float, previous: Optional[float],
                       higher_is_better: bool) -> Optional[str]:
        """Compute trend direction."""
        if previous is None:
            return None
        
        delta = current - previous
        threshold = 0.01 * abs(previous) if previous != 0 else 0.01
        
        if abs(delta) < threshold:
            return "stable"
        elif (delta > 0) == higher_is_better:
            return "improving"
        else:
            return "degrading"
    
    def _compute_cohort_coverage(self, variance: Dict,
                                  metadata: Dict) -> Optional[CohortCoverage]:
        """Compute cohort coverage metrics."""
        summaries = variance.get('promoter_backend_summaries', [])
        
        if not summaries:
            return None
        
        # Count unique promoters and backends
        promoters = set()
        backends = set()
        cells_with_min = 0
        min_replicates = self.thresholds.min_replicates_per_cell.pass_threshold
        
        # Track unique cells (promoter-backend combinations)
        unique_cells = set()
        cells_meeting_threshold = set()
        
        for s in summaries:
            promoter = s.get('promoter', 'unknown')
            backend = s.get('backend', 'unknown')
            promoters.add(promoter)
            backends.add(backend)
            
            cell_key = f"{promoter}_{backend}"
            unique_cells.add(cell_key)
            
            if s.get('replicate_count', 0) >= min_replicates:
                cells_meeting_threshold.add(cell_key)
        
        total_cells = len(unique_cells)
        cells_with_min = len(cells_meeting_threshold)
        
        # Count promoters above S/S threshold
        ss_values = [s.get('signal_to_separation', 0) for s in summaries]
        promoters_above = sum(1 for ss in ss_values if ss >= self.thresholds.min_ss_ratio.pass_threshold)
        
        return CohortCoverage(
            total_promoters=len(promoters),
            promoters_above_ss_threshold=promoters_above,
            fraction_promoters_above_ss=promoters_above / len(promoters) if promoters else 0,
            total_backend_pairs=len(backends) * (len(backends) - 1) // 2 if len(backends) > 1 else 1,
            backend_pairs_tested=len(metadata.get('backend_pairs_tested', [])),
            fraction_backend_pairs_tested=1.0,  # Would need actual data
            total_cells=total_cells,
            cells_with_min_replicates=cells_with_min,
            fraction_cells_covered=cells_with_min / total_cells if total_cells > 0 else 0,
        )
    
    def _compute_backend_drift(self, metadata: Dict) -> Optional[BackendDriftReport]:
        """Compute backend drift detection."""
        drift = metadata.get('backend_drift', {})
        
        if not drift:
            return None
        
        return BackendDriftReport(
            backend_name=drift.get('backend', 'unknown'),
            baseline_date=drift.get('baseline_date', ''),
            current_date=drift.get('current_date', ''),
            drift_magnitude=drift.get('magnitude', 0),
            drift_components=drift.get('components', {}),
            is_significant=drift.get('is_significant', False),
            p_value=drift.get('p_value'),
        )
    
    def _compute_rank_stability_ci(self, transfer: List[Dict]) -> Optional[RankStabilityCI]:
        """Compute ranking correlation confidence interval."""
        if not transfer:
            return None
        
        ranking_corr = abs(transfer[0].get('promoter_ranking_correlation', 0))
        
        # Fisher z-transformation for CI
        # z = 0.5 * ln((1+r)/(1-r))
        # SE = 1/sqrt(n-3)
        # For now, use approximation
        n = transfer[0].get('n_observations', 100)
        
        z = 0.5 * np.log((1 + ranking_corr) / (1 - ranking_corr + 1e-10))
        se = 1.0 / np.sqrt(max(n - 3, 1))
        
        z_lower = z - 1.96 * se
        z_upper = z + 1.96 * se
        
        # Transform back
        ci_lower = (np.exp(2 * z_lower) - 1) / (np.exp(2 * z_lower) + 1)
        ci_upper = (np.exp(2 * z_upper) - 1) / (np.exp(2 * z_upper) + 1)
        
        return RankStabilityCI(
            point_estimate=ranking_corr,
            ci_lower=max(0, ci_lower),
            ci_upper=min(1, ci_upper),
            confidence_level=0.95,
            n_observations=n,
            method="fisher_z",
        )
    
    def _compute_heldout_performance(self, variance: Dict) -> Optional[HeldOutPerformance]:
        """Compute held-out promoter performance."""
        heldout = variance.get('heldout_performance', {})
        
        if not heldout:
            return None
        
        return HeldOutPerformance(
            heldout_promoters=heldout.get('promoters', []),
            correlation_with_observed=heldout.get('correlation', 0),
            mae=heldout.get('mae', 0),
            rmse=heldout.get('rmse', 0),
            coverage=heldout.get('coverage', 0),
        )
    
    def _generate_recommendations(self, gates: List[EnhancedGateResult]) -> List[str]:
        """Generate recommendations based on gate results."""
        recommendations = []
        
        for gate in gates:
            if gate.status == GateStatus.FAIL:
                if gate.gate_name == "replicate_count":
                    recommendations.append(
                        f"Increase replicates to at least {gate.pass_threshold:.0f} per cell"
                    )
                elif gate.gate_name == "residual_spread":
                    recommendations.append(
                        "Investigate residual outliers; consider robust calibration"
                    )
                elif gate.gate_name == "signal_to_separation":
                    recommendations.append(
                        "Increase promoter distinctiveness or reduce measurement noise"
                    )
                elif gate.gate_name == "portability":
                    recommendations.append(
                        "Use backend-conditioned or hierarchical calibration"
                    )
                elif gate.gate_name == "stability":
                    recommendations.append(
                        "Investigate measurement protocol for variance sources"
                    )
                elif gate.gate_name == "model_fit":
                    recommendations.append(
                        "Add covariates (circuit depth, gate counts) to model"
                    )
                elif gate.gate_name == "heldout_performance":
                    recommendations.append(
                        "Evaluate on held-out promoters before promotion"
                    )
                elif gate.gate_name == "backend_drift":
                    recommendations.append(
                        "Recalibrate due to backend drift detected"
                    )
                elif gate.gate_name == "rank_stability_ci":
                    recommendations.append(
                        "Increase sample size for stable ranking estimates"
                    )
                elif gate.gate_name == "cohort_coverage":
                    recommendations.append(
                        "Expand cohort coverage to meet minimum threshold"
                    )
            
            elif gate.status == GateStatus.WARNING:
                recommendations.append(
                    f"Monitor {gate.gate_name}: approaching threshold"
                )
        
        return recommendations


# =============================================================================
# REPORT GENERATOR
# =============================================================================

def generate_lifecycle_report(assessment: LifecycleAssessment, output_path: Path):
    """Generate human-readable lifecycle governance report."""
    
    report_lines = [
        "=" * 70,
        "VCapture Lifecycle Governance Assessment v2.0",
        "=" * 70,
        "",
        f"Assessed at: {assessment.assessed_at}",
        f"Ledger: {assessment.ledger_path}",
        f"Calibration version: {assessment.calibration_version}",
        "",
        "=" * 70,
        "STATE MACHINE STATUS",
        "=" * 70,
        "",
        f"  Current State: {assessment.current_state.upper()}",
        f"  Target State: {assessment.target_state.upper()}",
        f"  Eligible for Promotion: {'YES ✓' if assessment.eligible_for_promotion else 'NO ✗'}",
        f"  Requires Downgrade: {'YES ⚠' if assessment.requires_downgrade else 'NO'}",
        "",
    ]
    
    # State transition diagram
    states = ["development", "candidate", "staging", "production", "retired"]
    current_idx = states.index(assessment.current_state)
    
    report_lines.append("  State Progression:")
    for i, state in enumerate(states):
        if i < current_idx:
            marker = "✓"
        elif i == current_idx:
            marker = "●"
        else:
            marker = "○"
        report_lines.append(f"    {marker} {state.upper()}")
    report_lines.append("")
    
    # Gate results
    report_lines.extend([
        "=" * 70,
        "GATE RESULTS (with Warning Bands)",
        "=" * 70,
        "",
    ])
    
    gates = [
        ("Replicate Count", assessment.replicate_gate),
        ("Residual Spread", assessment.residual_gate),
        ("Signal-to-Separation", assessment.separation_gate),
        ("Portability", assessment.portability_gate),
        ("Stability", assessment.stability_gate),
        ("Model Fit", assessment.model_fit_gate),
    ]
    
    # Add optional gates
    if assessment.heldout_gate:
        gates.append(("Held-Out Performance", assessment.heldout_gate))
    if assessment.drift_gate:
        gates.append(("Backend Drift", assessment.drift_gate))
    if assessment.rank_ci_gate:
        gates.append(("Rank Stability CI", assessment.rank_ci_gate))
    if assessment.coverage_gate:
        gates.append(("Cohort Coverage", assessment.coverage_gate))
    
    for name, gate in gates:
        if gate is None:
            continue
        
        status_icon = {
            GateStatus.PASS: "✓ PASS",
            GateStatus.WARNING: "⚠ WARN",
            GateStatus.FAIL: "✗ FAIL",
        }[gate.status]
        
        trend_str = f" ({gate.trend})" if gate.trend else ""
        
        report_lines.extend([
            f"  {name}:",
            f"    Status: {status_icon}{trend_str}",
            f"    Value: {gate.value:.4f}",
            f"    Pass Threshold: {gate.pass_threshold:.4f}",
            f"    Warning Threshold: {gate.warning_threshold:.4f}",
            f"    Margin to Pass: {gate.margin_to_pass:+.4f}",
            f"    Message: {gate.message}",
            "",
        ])
    
    # Additional metrics
    if assessment.cohort_coverage:
        report_lines.extend([
            "=" * 70,
            "COHORT COVERAGE",
            "=" * 70,
            "",
            f"  Total Promoters: {assessment.cohort_coverage.total_promoters}",
            f"  Promoters Above S/S: {assessment.cohort_coverage.promoters_above_ss_threshold} ({assessment.cohort_coverage.fraction_promoters_above_ss:.1%})",
            f"  Backend Pairs Tested: {assessment.cohort_coverage.backend_pairs_tested}",
            f"  Cells with Min Replicates: {assessment.cohort_coverage.cells_with_min_replicates}/{assessment.cohort_coverage.total_cells} ({assessment.cohort_coverage.fraction_cells_covered:.1%})",
            "",
        ])
    
    if assessment.rank_stability_ci:
        report_lines.extend([
            "=" * 70,
            "RANK STABILITY (with CI)",
            "=" * 70,
            "",
            f"  Point Estimate: {assessment.rank_stability_ci.point_estimate:.4f}",
            f"  95% CI: [{assessment.rank_stability_ci.ci_lower:.4f}, {assessment.rank_stability_ci.ci_upper:.4f}]",
            f"  Method: {assessment.rank_stability_ci.method}",
            f"  N Observations: {assessment.rank_stability_ci.n_observations}",
            "",
        ])
    
    # Blocking issues and warnings
    if assessment.blocking_issues:
        report_lines.extend([
            "=" * 70,
            "BLOCKING ISSUES",
            "=" * 70,
            "",
        ])
        for issue in assessment.blocking_issues:
            report_lines.append(f"  ✗ {issue}")
        report_lines.append("")
    
    if assessment.warnings:
        report_lines.extend([
            "=" * 70,
            "WARNINGS",
            "=" * 70,
            "",
        ])
        for warning in assessment.warnings:
            report_lines.append(f"  ⚠ {warning}")
        report_lines.append("")
    
    if assessment.recommendations:
        report_lines.extend([
            "=" * 70,
            "RECOMMENDATIONS",
            "=" * 70,
            "",
        ])
        for rec in assessment.recommendations:
            report_lines.append(f"  → {rec}")
        report_lines.append("")
    
    # Summary
    report_lines.extend([
        "=" * 70,
        "SUMMARY",
        "=" * 70,
        "",
        f"  Calibration remains in {assessment.current_state.upper()} state.",
    ])
    
    if assessment.eligible_for_promotion:
        report_lines.append("  ✓ Ready for promotion to next state.")
    else:
        report_lines.append("  ✗ Not ready for promotion.")
    
    if assessment.requires_downgrade:
        report_lines.append("  ⚠ CRITICAL: Downgrade recommended due to gate failures.")
    
    report_lines.append("")
    
    report_text = "\n".join(report_lines)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report_text)
    
    return report_text


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="VCapture Lifecycle Governance v2.0")
    parser.add_argument("--ledger", type=str, required=True, help="Path to VCapture ledger JSON")
    parser.add_argument("--output", type=str, default="lifecycle_assessment.json", help="Output assessment JSON")
    parser.add_argument("--report", type=str, default="lifecycle_report.txt", help="Human-readable report")
    parser.add_argument("--current-state", type=str, default="development",
                        choices=["development", "candidate", "staging", "production"],
                        help="Current calibration state")
    parser.add_argument("--target-state", type=str, default="production",
                        choices=["development", "candidate", "staging", "production"],
                        help="Target promotion state")
    parser.add_argument("--previous", type=str, default=None, help="Previous assessment JSON for trend tracking")
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("VCapture Lifecycle Governance v2.0")
    print("=" * 70)
    
    # Initialize governance engine
    current_state = CalibrationState(args.current_state)
    target_state = CalibrationState(args.target_state)
    
    governance = VCaptureLifecycleGovernance(
        current_state=current_state,
        target_state=target_state,
    )
    
    print(f"\nCurrent state: {current_state.value.upper()}")
    print(f"Target state: {target_state.value.upper()}")
    print(f"Assessing ledger: {args.ledger}")
    
    # Load previous assessment if available
    previous = None
    if args.previous:
        with open(args.previous, 'r', encoding='utf-8') as f:
            previous = json.load(f)
    
    # Run assessment
    ledger_path = Path(args.ledger)
    assessment = governance.assess_ledger(ledger_path, previous)
    
    # Save JSON assessment
    output_path = Path(args.output)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(assessment.to_dict(), f, indent=2)
    print(f"\nAssessment saved to: {output_path}")
    
    # Generate human-readable report
    report_path = Path(args.report)
    report_text = generate_lifecycle_report(assessment, report_path)
    print(f"Report saved to: {report_path}")
    
    # Print summary
    print("\n" + "=" * 70)
    print("LIFECYCLE GOVERNANCE SUMMARY")
    print("=" * 70)
    print(f"\n  Current State: {assessment.current_state.upper()}")
    print(f"  Eligible for Promotion: {'YES ✓' if assessment.eligible_for_promotion else 'NO ✗'}")
    print(f"  Requires Downgrade: {'YES ⚠' if assessment.requires_downgrade else 'NO'}")
    
    # Count gate statuses
    gates = [
        assessment.replicate_gate, assessment.residual_gate,
        assessment.separation_gate, assessment.portability_gate,
        assessment.stability_gate, assessment.model_fit_gate,
    ]
    n_pass = sum(1 for g in gates if g.status == GateStatus.PASS)
    n_warn = sum(1 for g in gates if g.status == GateStatus.WARNING)
    n_fail = sum(1 for g in gates if g.status == GateStatus.FAIL)
    
    print(f"\n  Gate Summary: {n_pass} pass, {n_warn} warning, {n_fail} fail")
    
    if assessment.blocking_issues:
        print(f"\n  Blocking Issues: {len(assessment.blocking_issues)}")
        for issue in assessment.blocking_issues[:3]:
            print(f"    • {issue}")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()