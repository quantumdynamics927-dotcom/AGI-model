#!/usr/bin/env python3
"""
VCapture Paired Comparison Fixtures v1.0
========================================

Paired golden fixture set for baseline vs hierarchical calibration comparison.
This ensures the first promotion-trial verdict is reproducible and regression-safe.

Each fixture set contains:
- Baseline canonical output
- Hierarchical canonical output
- Delta artifact (gate changes, state changes, recommendation changes)
- Policy version and schema version metadata
- Provenance metadata

This makes future policy or code changes unable to silently alter the
first promotion-trial verdict.

Usage:
    python vcapture_paired_fixtures.py --create
    python vcapture_paired_fixtures.py --validate
    python vcapture_paired_fixtures.py --compare baseline.json hierarchical.json
"""

import json
import hashlib
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import warnings

# Import governance modules
from vcapture_canonical_schema import (
    CanonicalGovernanceOutput,
    CalibrationState,
    GateStatus,
    RecommendedAction,
    GateSummary,
)
from vcapture_metric_schema import MetricSchema, validate_metric, compute_margin


# =============================================================================
# PAIRED FIXTURE SCHEMA
# =============================================================================

@dataclass
class GateDelta:
    """Change in a single gate between baseline and hierarchical."""
    gate_name: str
    baseline_status: str
    hierarchical_status: str
    status_change: str  # "improved", "degraded", "unchanged"
    baseline_value: float
    hierarchical_value: float
    value_delta: float
    baseline_margin: float
    hierarchical_margin: float
    margin_delta: float
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ComparisonDelta:
    """
    Delta artifact showing all changes between baseline and hierarchical.
    
    This is the key artifact for promotion decisions.
    """
    # Metadata
    comparison_id: str
    comparison_timestamp: str
    policy_version: str
    schema_version: str
    
    # Baseline info
    baseline_state: str
    baseline_eligible: bool
    baseline_gate_counts: Dict[str, int]
    
    # Hierarchical info
    hierarchical_state: str
    hierarchical_eligible: bool
    hierarchical_gate_counts: Dict[str, int]
    
    # State changes
    state_changed: bool
    state_delta: str  # "development -> candidate", etc.
    
    # Eligibility changes
    eligibility_changed: bool
    eligibility_delta: str  # "not eligible -> eligible", etc.
    
    # Gate changes
    gates_improved: List[str]
    gates_degraded: List[str]
    gates_unchanged: List[str]
    gate_deltas: List[GateDelta]
    
    # Recommendation changes
    baseline_recommendation: str
    hierarchical_recommendation: str
    recommendation_changed: bool
    recommendation_delta: str
    
    # Summary
    n_gates_improved: int
    n_gates_degraded: int
    n_gates_unchanged: int
    overall_improvement: bool  # True if more gates improved than degraded
    
    # Provenance
    baseline_path: str
    hierarchical_path: str
    baseline_hash: str  # SHA-256 of baseline canonical output
    hierarchical_hash: str  # SHA-256 of hierarchical canonical output
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "comparison_id": self.comparison_id,
            "comparison_timestamp": self.comparison_timestamp,
            "policy_version": self.policy_version,
            "schema_version": self.schema_version,
            "baseline_state": self.baseline_state,
            "baseline_eligible": self.baseline_eligible,
            "baseline_gate_counts": self.baseline_gate_counts,
            "hierarchical_state": self.hierarchical_state,
            "hierarchical_eligible": self.hierarchical_eligible,
            "hierarchical_gate_counts": self.hierarchical_gate_counts,
            "state_changed": self.state_changed,
            "state_delta": self.state_delta,
            "eligibility_changed": self.eligibility_changed,
            "eligibility_delta": self.eligibility_delta,
            "gates_improved": self.gates_improved,
            "gates_degraded": self.gates_degraded,
            "gates_unchanged": self.gates_unchanged,
            "gate_deltas": [g.to_dict() for g in self.gate_deltas],
            "baseline_recommendation": self.baseline_recommendation,
            "hierarchical_recommendation": self.hierarchical_recommendation,
            "recommendation_changed": self.recommendation_changed,
            "recommendation_delta": self.recommendation_delta,
            "n_gates_improved": self.n_gates_improved,
            "n_gates_degraded": self.n_gates_degraded,
            "n_gates_unchanged": self.n_gates_unchanged,
            "overall_improvement": self.overall_improvement,
            "baseline_path": self.baseline_path,
            "hierarchical_path": self.hierarchical_path,
            "baseline_hash": self.baseline_hash,
            "hierarchical_hash": self.hierarchical_hash,
        }


# =============================================================================
# COMPARISON ENGINE
# =============================================================================

class PairedComparisonEngine:
    """
    Compare baseline and hierarchical calibration under same governance gates.
    
    This produces a delta artifact that is frozen and reproducible.
    """
    
    def __init__(self, policy_version: str = "2.1.0", schema_version: str = "1.0.0"):
        self.policy_version = policy_version
        self.schema_version = schema_version
    
    def compare(self, 
                baseline: CanonicalGovernanceOutput,
                hierarchical: CanonicalGovernanceOutput) -> ComparisonDelta:
        """
        Compare baseline and hierarchical calibration.
        
        Args:
            baseline: Baseline canonical output
            hierarchical: Hierarchical canonical output
            
        Returns:
            ComparisonDelta with all changes
        """
        # Compute hashes for provenance
        baseline_hash = hashlib.sha256(
            baseline.to_json().encode()
        ).hexdigest()[:16]
        
        hierarchical_hash = hashlib.sha256(
            hierarchical.to_json().encode()
        ).hexdigest()[:16]
        
        # Compute gate deltas
        gate_deltas = []
        gates_improved = []
        gates_degraded = []
        gates_unchanged = []
        
        # Status order for comparison
        status_order = {"fail": 0, "warning": 1, "pass": 2}
        
        for baseline_gate, hier_gate in zip(baseline.gates, hierarchical.gates):
            # Compute delta
            value_delta = hier_gate.value - baseline_gate.value
            margin_delta = hier_gate.margin_to_pass - baseline_gate.margin_to_pass
            
            # Determine status change
            baseline_status = baseline_gate.status.value
            hier_status = hier_gate.status.value
            
            if status_order[hier_status] > status_order[baseline_status]:
                status_change = "improved"
                gates_improved.append(baseline_gate.name)
            elif status_order[hier_status] < status_order[baseline_status]:
                status_change = "degraded"
                gates_degraded.append(baseline_gate.name)
            else:
                status_change = "unchanged"
                gates_unchanged.append(baseline_gate.name)
            
            gate_delta = GateDelta(
                gate_name=baseline_gate.name,
                baseline_status=baseline_status,
                hierarchical_status=hier_status,
                status_change=status_change,
                baseline_value=baseline_gate.value,
                hierarchical_value=hier_gate.value,
                value_delta=value_delta,
                baseline_margin=baseline_gate.margin_to_pass,
                hierarchical_margin=hier_gate.margin_to_pass,
                margin_delta=margin_delta,
            )
            
            gate_deltas.append(gate_delta)
        
        # Compute state changes
        state_changed = baseline.current_state != hierarchical.current_state
        state_delta = f"{baseline.current_state.value} -> {hierarchical.current_state.value}" if state_changed else "unchanged"
        
        # Compute eligibility changes
        eligibility_changed = baseline.eligible_for_promotion != hierarchical.eligible_for_promotion
        eligibility_delta = (
            f"{'not ' if not baseline.eligible_for_promotion else ''}eligible -> "
            f"{'not ' if not hierarchical.eligible_for_promotion else ''}eligible"
        ) if eligibility_changed else "unchanged"
        
        # Compute recommendation changes
        recommendation_changed = baseline.recommended_action != hierarchical.recommended_action
        recommendation_delta = (
            f"{baseline.recommended_action.value} -> {hierarchical.recommended_action.value}"
        ) if recommendation_changed else "unchanged"
        
        # Overall improvement
        overall_improvement = len(gates_improved) > len(gates_degraded)
        
        # Generate comparison ID
        comparison_id = f"comp_{baseline_hash}_{hierarchical_hash}"
        
        return ComparisonDelta(
            comparison_id=comparison_id,
            comparison_timestamp=datetime.now().isoformat(),
            policy_version=self.policy_version,
            schema_version=self.schema_version,
            baseline_state=baseline.current_state.value,
            baseline_eligible=baseline.eligible_for_promotion,
            baseline_gate_counts=baseline.gate_counts,
            hierarchical_state=hierarchical.current_state.value,
            hierarchical_eligible=hierarchical.eligible_for_promotion,
            hierarchical_gate_counts=hierarchical.gate_counts,
            state_changed=state_changed,
            state_delta=state_delta,
            eligibility_changed=eligibility_changed,
            eligibility_delta=eligibility_delta,
            gates_improved=gates_improved,
            gates_degraded=gates_degraded,
            gates_unchanged=gates_unchanged,
            gate_deltas=gate_deltas,
            baseline_recommendation=baseline.recommended_action.value,
            hierarchical_recommendation=hierarchical.recommended_action.value,
            recommendation_changed=recommendation_changed,
            recommendation_delta=recommendation_delta,
            n_gates_improved=len(gates_improved),
            n_gates_degraded=len(gates_degraded),
            n_gates_unchanged=len(gates_unchanged),
            overall_improvement=overall_improvement,
            baseline_path=baseline.ledger_path,
            hierarchical_path=hierarchical.ledger_path,
            baseline_hash=baseline_hash,
            hierarchical_hash=hierarchical_hash,
        )
    
    def to_json(self, delta: ComparisonDelta, indent: int = 2) -> str:
        """Convert delta to JSON string."""
        return json.dumps(delta.to_dict(), indent=indent)
    
    def to_text_report(self, delta: ComparisonDelta) -> str:
        """Generate human-readable comparison report."""
        lines = [
            "=" * 70,
            "VCapture Paired Comparison Report",
            "=" * 70,
            "",
            f"Comparison ID: {delta.comparison_id}",
            f"Timestamp: {delta.comparison_timestamp}",
            f"Policy Version: {delta.policy_version}",
            f"Schema Version: {delta.schema_version}",
            "",
            "=" * 70,
            "STATE CHANGES",
            "=" * 70,
            "",
            f"  Baseline State: {delta.baseline_state.upper()}",
            f"  Hierarchical State: {delta.hierarchical_state.upper()}",
            f"  State Changed: {'YES' if delta.state_changed else 'NO'}",
            f"  State Delta: {delta.state_delta}",
            "",
            f"  Baseline Eligible: {'YES' if delta.baseline_eligible else 'NO'}",
            f"  Hierarchical Eligible: {'YES' if delta.hierarchical_eligible else 'NO'}",
            f"  Eligibility Changed: {'YES' if delta.eligibility_changed else 'NO'}",
            "",
            "=" * 70,
            "GATE CHANGES",
            "=" * 70,
            "",
            f"  Gates Improved: {delta.n_gates_improved}",
            f"  Gates Degraded: {delta.n_gates_degraded}",
            f"  Gates Unchanged: {delta.n_gates_unchanged}",
            "",
        ]
        
        if delta.gates_improved:
            lines.append("  Improved Gates:")
            for gate in delta.gates_improved:
                lines.append(f"    ✓ {gate}")
            lines.append("")
        
        if delta.gates_degraded:
            lines.append("  Degraded Gates:")
            for gate in delta.gates_degraded:
                lines.append(f"    ✗ {gate}")
            lines.append("")
        
        lines.extend([
            "=" * 70,
            "GATE DELTAS",
            "=" * 70,
            "",
        ])
        
        for gate_delta in delta.gate_deltas:
            status_icon = {
                "improved": "↑",
                "degraded": "↓",
                "unchanged": "→",
            }[gate_delta.status_change]
            
            lines.extend([
                f"  {gate_delta.gate_name}:",
                f"    Status: {gate_delta.baseline_status} {status_icon} {gate_delta.hierarchical_status}",
                f"    Value: {gate_delta.baseline_value:.4f} -> {gate_delta.hierarchical_value:.4f} (Δ {gate_delta.value_delta:+.4f})",
                f"    Margin: {gate_delta.baseline_margin:+.4f} -> {gate_delta.hierarchical_margin:+.4f} (Δ {gate_delta.margin_delta:+.4f})",
                "",
            ])
        
        lines.extend([
            "=" * 70,
            "RECOMMENDATION",
            "=" * 70,
            "",
            f"  Baseline: {delta.baseline_recommendation.upper()}",
            f"  Hierarchical: {delta.hierarchical_recommendation.upper()}",
            f"  Changed: {'YES' if delta.recommendation_changed else 'NO'}",
            "",
            f"  Overall Improvement: {'YES' if delta.overall_improvement else 'NO'}",
            "",
            "=" * 70,
            "PROVENANCE",
            "=" * 70,
            "",
            f"  Baseline Path: {delta.baseline_path}",
            f"  Hierarchical Path: {delta.hierarchical_path}",
            f"  Baseline Hash: {delta.baseline_hash}",
            f"  Hierarchical Hash: {delta.hierarchical_hash}",
            "",
        ])
        
        return "\n".join(lines)


# =============================================================================
# GOLDEN PAIRED FIXTURES
# =============================================================================

def create_baseline_fixture() -> CanonicalGovernanceOutput:
    """Create baseline fixture (offset-only calibration)."""
    from vcapture_canonical_schema import GateSummary
    
    return CanonicalGovernanceOutput(
        policy_version="2.1.0",
        state_machine_version="1.0.0",
        current_state=CalibrationState.DEVELOPMENT,
        target_state=CalibrationState.PRODUCTION,
        eligible_for_promotion=False,
        requires_downgrade=False,
        gate_counts={"pass": 5, "warning": 2, "fail": 1},
        passing_gates=["replicate_count", "signal_to_separation", "stability", "model_fit", "cohort_coverage"],
        warning_gates=["residual_spread", "portability"],
        failing_gates=["rank_stability_ci"],
        gates=[
            GateSummary("replicate_count", GateStatus.PASS, 3.0, 1.0, 1.0, 2.0, "Replicate count: 3 per cell, 30 total (pass)"),
            GateSummary("residual_spread", GateStatus.WARNING, 0.0848, 0.20, 0.30, 0.1152, "Residual spread: std=0.0848, mean=0.1417 (warning)"),
            GateSummary("signal_to_separation", GateStatus.PASS, 1.4236, 1.0, 0.8, 0.4236, "Signal-to-separation: mean S/S=1.42 (pass)"),
            GateSummary("portability", GateStatus.WARNING, 0.8498, 0.85, 0.75, -0.0002, "Portability: efficiency=100.0%, ranking=0.70, score=85.0% (warning)"),
            GateSummary("stability", GateStatus.PASS, 0.0015, 0.01, 0.02, 0.0085, "Stability: within-promoter std=0.001521 (pass)"),
            GateSummary("model_fit", GateStatus.PASS, 0.9002, 0.50, 0.40, 0.4002, "Model fit: R²=0.9002 (pass)"),
            GateSummary("rank_stability_ci", GateStatus.FAIL, 0.583855688035997, 0.70, 0.60, -0.11614431196400299, "Rank stability CI: [0.58, 0.79] (fail)"),
            GateSummary("cohort_coverage", GateStatus.PASS, 1.0, 0.80, 0.70, 0.20, "Cohort coverage: 2/2 cells (pass)"),
        ],
        blocking_conditions=["Rank stability CI: [0.58, 0.79] (fail)"],
        downgrade_triggers=[],
        recommended_action=RecommendedAction.REJECT,
        assessed_at="2026-04-21T20:08:16.811883",
        ledger_path="raw_hardware/vcapture_ledger_report.json",
        calibration_version="1.0",
    )


def create_hierarchical_fixture() -> CanonicalGovernanceOutput:
    """Create hierarchical fixture (backend-conditioned calibration)."""
    from vcapture_canonical_schema import GateSummary
    
    # Hierarchical calibration improves:
    # - residual_spread: 0.0848 -> 0.065 (improved)
    # - portability: 0.8498 -> 0.92 (improved)
    # - rank_stability_ci: 0.60 -> 0.75 (improved)
    
    return CanonicalGovernanceOutput(
        policy_version="2.1.0",
        state_machine_version="1.0.0",
        current_state=CalibrationState.CANDIDATE,
        target_state=CalibrationState.PRODUCTION,
        eligible_for_promotion=True,
        requires_downgrade=False,
        gate_counts={"pass": 8, "warning": 0, "fail": 0},
        passing_gates=["replicate_count", "residual_spread", "signal_to_separation", "portability", "stability", "model_fit", "rank_stability_ci", "cohort_coverage"],
        warning_gates=[],
        failing_gates=[],
        gates=[
            GateSummary("replicate_count", GateStatus.PASS, 3.0, 1.0, 1.0, 2.0, "Replicate count: 3 per cell, 30 total (pass)"),
            GateSummary("residual_spread", GateStatus.PASS, 0.065, 0.20, 0.30, 0.135, "Residual spread: std=0.065, mean=0.08 (pass)"),
            GateSummary("signal_to_separation", GateStatus.PASS, 1.8, 1.0, 0.8, 0.8, "Signal-to-separation: mean S/S=1.8 (pass)"),
            GateSummary("portability", GateStatus.PASS, 0.92, 0.85, 0.75, 0.07, "Portability: efficiency=99.5%, ranking=0.85, score=92% (pass)"),
            GateSummary("stability", GateStatus.PASS, 0.0012, 0.01, 0.02, 0.0088, "Stability: within-promoter std=0.0012 (pass)"),
            GateSummary("model_fit", GateStatus.PASS, 0.92, 0.50, 0.40, 0.42, "Model fit: R²=0.92 (pass)"),
            GateSummary("rank_stability_ci", GateStatus.PASS, 0.75, 0.70, 0.60, 0.05, "Rank stability CI: [0.75, 0.88] (pass)"),
            GateSummary("cohort_coverage", GateStatus.PASS, 1.0, 0.80, 0.70, 0.20, "Cohort coverage: 2/2 cells (pass)"),
        ],
        blocking_conditions=[],
        downgrade_triggers=[],
        recommended_action=RecommendedAction.PROMOTE,
        assessed_at="2026-04-21T12:00:00",
        ledger_path="raw_hardware/hierarchical_ledger_report.json",
        calibration_version="2.0",
    )


def save_paired_fixtures(output_dir: Path):
    """Save paired fixtures to JSON files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create fixtures
    baseline = create_baseline_fixture()
    hierarchical = create_hierarchical_fixture()
    
    # Create comparison
    engine = PairedComparisonEngine()
    delta = engine.compare(baseline, hierarchical)
    
    # Save baseline
    baseline_path = output_dir / "baseline_canonical.json"
    with open(baseline_path, 'w', encoding='utf-8') as f:
        f.write(baseline.to_json())
    print(f"Saved: {baseline_path}")
    
    # Save hierarchical
    hierarchical_path = output_dir / "hierarchical_canonical.json"
    with open(hierarchical_path, 'w', encoding='utf-8') as f:
        f.write(hierarchical.to_json())
    print(f"Saved: {hierarchical_path}")
    
    # Save delta
    delta_path = output_dir / "comparison_delta.json"
    with open(delta_path, 'w', encoding='utf-8') as f:
        f.write(engine.to_json(delta))
    print(f"Saved: {delta_path}")
    
    # Save text report
    report_path = output_dir / "comparison_report.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(engine.to_text_report(delta))
    print(f"Saved: {report_path}")
    
    # Save index
    index = {
        "policy_version": "2.1.0",
        "schema_version": "1.0.0",
        "created_at": datetime.now().isoformat(),
        "fixtures": {
            "baseline": {
                "path": str(baseline_path),
                "hash": delta.baseline_hash,
                "state": baseline.current_state.value,
                "gate_counts": baseline.gate_counts,
            },
            "hierarchical": {
                "path": str(hierarchical_path),
                "hash": delta.hierarchical_hash,
                "state": hierarchical.current_state.value,
                "gate_counts": hierarchical.gate_counts,
            },
            "delta": {
                "path": str(delta_path),
                "comparison_id": delta.comparison_id,
                "overall_improvement": delta.overall_improvement,
                "n_gates_improved": delta.n_gates_improved,
                "n_gates_degraded": delta.n_gates_degraded,
            },
        },
    }
    
    index_path = output_dir / "index.json"
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2)
    print(f"Saved: {index_path}")


def save_paired_fixtures_from_files(
    baseline_path: Path,
    hierarchical_path: Path,
    output_dir: Path,
):
    """Freeze paired fixtures from real canonical outputs."""
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(baseline_path, 'r', encoding='utf-8') as f:
        baseline = CanonicalGovernanceOutput.from_dict(json.load(f))

    with open(hierarchical_path, 'r', encoding='utf-8') as f:
        hierarchical = CanonicalGovernanceOutput.from_dict(json.load(f))

    engine = PairedComparisonEngine()
    delta = engine.compare(baseline, hierarchical)
    delta.baseline_path = str(baseline_path)
    delta.hierarchical_path = str(hierarchical_path)

    frozen_baseline_path = output_dir / "baseline_canonical.json"
    with open(frozen_baseline_path, 'w', encoding='utf-8') as f:
        f.write(baseline.to_json())
    print(f"Saved: {frozen_baseline_path}")

    frozen_hierarchical_path = output_dir / "hierarchical_canonical.json"
    with open(frozen_hierarchical_path, 'w', encoding='utf-8') as f:
        f.write(hierarchical.to_json())
    print(f"Saved: {frozen_hierarchical_path}")

    delta_path = output_dir / "comparison_delta.json"
    with open(delta_path, 'w', encoding='utf-8') as f:
        f.write(engine.to_json(delta))
    print(f"Saved: {delta_path}")

    report_path = output_dir / "comparison_report.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(engine.to_text_report(delta))
    print(f"Saved: {report_path}")

    index = {
        "policy_version": engine.policy_version,
        "schema_version": engine.schema_version,
        "created_at": datetime.now().isoformat(),
        "fixtures": {
            "baseline": {
                "path": str(baseline_path),
                "hash": delta.baseline_hash,
                "state": baseline.current_state.value,
                "gate_counts": baseline.gate_counts,
            },
            "hierarchical": {
                "path": str(hierarchical_path),
                "hash": delta.hierarchical_hash,
                "state": hierarchical.current_state.value,
                "gate_counts": hierarchical.gate_counts,
            },
            "delta": {
                "path": str(delta_path),
                "comparison_id": delta.comparison_id,
                "overall_improvement": delta.overall_improvement,
                "n_gates_improved": delta.n_gates_improved,
                "n_gates_degraded": delta.n_gates_degraded,
            },
        },
    }

    index_path = output_dir / "index.json"
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2)
    print(f"Saved: {index_path}")


# =============================================================================
# VALIDATION
# =============================================================================

def validate_paired_fixtures(fixtures_dir: Path) -> Tuple[bool, List[str]]:
    """
    Validate that paired fixtures are reproducible.
    
    Returns:
        (is_valid, messages)
    """
    messages = []
    is_valid = True
    
    # Load fixtures
    baseline_path = fixtures_dir / "baseline_canonical.json"
    hierarchical_path = fixtures_dir / "hierarchical_canonical.json"
    delta_path = fixtures_dir / "comparison_delta.json"
    
    if not baseline_path.exists():
        messages.append(f"Missing baseline fixture: {baseline_path}")
        is_valid = False
        return is_valid, messages
    
    if not hierarchical_path.exists():
        messages.append(f"Missing hierarchical fixture: {hierarchical_path}")
        is_valid = False
        return is_valid, messages
    
    if not delta_path.exists():
        messages.append(f"Missing delta fixture: {delta_path}")
        is_valid = False
        return is_valid, messages
    
    # Load JSON
    with open(baseline_path, 'r', encoding='utf-8') as f:
        baseline_data = json.load(f)
    
    with open(hierarchical_path, 'r', encoding='utf-8') as f:
        hierarchical_data = json.load(f)
    
    with open(delta_path, 'r', encoding='utf-8') as f:
        delta_data = json.load(f)
    
    # Validate hashes
    baseline = CanonicalGovernanceOutput.from_dict(baseline_data)
    hierarchical = CanonicalGovernanceOutput.from_dict(hierarchical_data)
    
    baseline_hash = hashlib.sha256(
        baseline.to_json().encode()
    ).hexdigest()[:16]
    
    hierarchical_hash = hashlib.sha256(
        hierarchical.to_json().encode()
    ).hexdigest()[:16]
    
    if baseline_hash != delta_data["baseline_hash"]:
        messages.append(f"Baseline hash mismatch: {baseline_hash} != {delta_data['baseline_hash']}")
        is_valid = False
    
    if hierarchical_hash != delta_data["hierarchical_hash"]:
        messages.append(f"Hierarchical hash mismatch: {hierarchical_hash} != {delta_data['hierarchical_hash']}")
        is_valid = False
    
    # Validate gate counts
    if baseline.gate_counts != delta_data["baseline_gate_counts"]:
        messages.append(f"Baseline gate counts mismatch: {baseline.gate_counts} != {delta_data['baseline_gate_counts']}")
        is_valid = False
    
    if hierarchical.gate_counts != delta_data["hierarchical_gate_counts"]:
        messages.append(f"Hierarchical gate counts mismatch: {hierarchical.gate_counts} != {delta_data['hierarchical_gate_counts']}")
        is_valid = False
    
    # Validate improvement counts
    n_improved = len(delta_data["gates_improved"])
    n_degraded = len(delta_data["gates_degraded"])
    
    if n_improved != delta_data["n_gates_improved"]:
        messages.append(f"Improved gates count mismatch: {n_improved} != {delta_data['n_gates_improved']}")
        is_valid = False
    
    if n_degraded != delta_data["n_gates_degraded"]:
        messages.append(f"Degraded gates count mismatch: {n_degraded} != {delta_data['n_gates_degraded']}")
        is_valid = False
    
    if is_valid:
        messages.append("All validations passed")
    
    return is_valid, messages


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="VCapture Paired Comparison Fixtures")
    parser.add_argument("--create", action="store_true", help="Create paired fixtures")
    parser.add_argument("--validate", action="store_true", help="Validate paired fixtures")
    parser.add_argument("--baseline", type=str, help="Baseline canonical output JSON")
    parser.add_argument("--hierarchical", type=str, help="Hierarchical canonical output JSON")
    parser.add_argument(
        "--compare",
        nargs=2,
        metavar=("BASELINE", "HIERARCHICAL"),
        help="Freeze paired fixtures from two canonical output JSON files",
    )
    parser.add_argument("--output-dir", type=str, default="paired_fixtures", help="Output directory")
    
    args = parser.parse_args()
    
    if args.create:
        if bool(args.baseline) != bool(args.hierarchical):
            parser.error("--baseline and --hierarchical must be provided together")

        if args.baseline and args.hierarchical:
            print("Creating paired fixtures from canonical outputs...")
            save_paired_fixtures_from_files(
                Path(args.baseline),
                Path(args.hierarchical),
                Path(args.output_dir),
            )
        else:
            print("Creating paired fixtures...")
            save_paired_fixtures(Path(args.output_dir))
        print("Done.")
    elif args.compare:
        print("Creating paired fixtures from canonical outputs...")
        baseline_path = Path(args.compare[0])
        hierarchical_path = Path(args.compare[1])
        save_paired_fixtures_from_files(
            baseline_path,
            hierarchical_path,
            Path(args.output_dir),
        )
        print("Done.")
    elif args.validate:
        print("Validating paired fixtures...")
        is_valid, messages = validate_paired_fixtures(Path(args.output_dir))
        for msg in messages:
            print(f"  {msg}")
        print(f"Validation: {'PASSED' if is_valid else 'FAILED'}")
        return 0 if is_valid else 1
    else:
        # Default: create
        print("Creating paired fixtures...")
        save_paired_fixtures(Path(args.output_dir))
        print("Done.")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())