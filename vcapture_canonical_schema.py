#!/usr/bin/env python3
"""
VCapture Canonical Output Schema v2.2
=====================================

Ensures all governance outputs derive from ONE canonical decision object.
This prevents summary mismatches and ensures consistency across:
- JSON assessment
- Text report
- Markdown summary
- CLI display

The canonical schema contains:
- policy_version: Version of governance policy
- state_machine_version: Version of state machine
- current_state: Current calibration state
- target_state: Target promotion state
- eligible_for_promotion: Boolean eligibility
- gate_counts: {pass, warning, fail}
- passing_gates: List of passing gate names
- warning_gates: List of warning gate names
- failing_gates: List of failing gate names
- blocking_conditions: List of blocking issues
- downgrade_triggers: List of downgrade triggers
- recommended_action: promote/hold/reject/downgrade

All metrics are validated against vcapture_metric_schema to ensure
semantic consistency (units, ranges, comparison directions).

Usage:
    from vcapture_canonical_schema import CanonicalGovernanceOutput
    
    # Create from assessment
    canonical = CanonicalGovernanceOutput.from_assessment(assessment)
    
    # Generate all outputs
    canonical.to_json()
    canonical.to_text_report()
    canonical.to_markdown_summary()
    canonical.to_cli_display()
"""

from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
import json

# Import metric schema for validation
try:
    from vcapture_metric_schema import MetricSchema, validate_metric, compute_margin
    HAS_METRIC_SCHEMA = True
except ImportError:
    HAS_METRIC_SCHEMA = False


# =============================================================================
# ENUMS
# =============================================================================

class CalibrationState(str, Enum):
    """Calibration model lifecycle states."""
    DEVELOPMENT = "development"
    CANDIDATE = "candidate"
    STAGING = "staging"
    PRODUCTION = "production"
    RETIRED = "retired"


class GateStatus(str, Enum):
    """Gate evaluation status with warning bands."""
    PASS = "pass"
    WARNING = "warning"
    FAIL = "fail"


class RecommendedAction(str, Enum):
    """Recommended action from governance assessment."""
    PROMOTE = "promote"
    HOLD = "hold"
    REJECT = "reject"
    DOWNGRADE = "downgrade"


# =============================================================================
# CANONICAL OUTPUT SCHEMA
# =============================================================================

@dataclass
class GateSummary:
    """Summary of a single gate."""
    name: str
    status: GateStatus
    value: float
    pass_threshold: float
    warning_threshold: float
    margin_to_pass: float
    message: str
    
    # Metric metadata (from vcapture_metric_schema)
    unit: str = ""
    comparison_direction: str = ""
    
    def __post_init__(self):
        """Validate metric against schema."""
        if HAS_METRIC_SCHEMA:
            is_valid, msg = validate_metric(self.name, self.value)
            if not is_valid:
                # Log warning but don't fail
                import warnings
                warnings.warn(f"Metric validation: {msg}")
                
                # Try to get schema for metadata
                schema = MetricSchema.get(self.name)
                if schema:
                    self.unit = schema.unit
                    self.comparison_direction = schema.comparison_direction.value
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status.value,
            "value": self.value,
            "pass_threshold": self.pass_threshold,
            "warning_threshold": self.warning_threshold,
            "margin_to_pass": self.margin_to_pass,
            "message": self.message,
            "unit": self.unit,
            "comparison_direction": self.comparison_direction,
        }


@dataclass
class CanonicalGovernanceOutput:
    """
    Canonical governance output schema.
    
    ALL outputs (JSON, text, markdown, CLI) MUST derive from this object.
    This prevents summary mismatches and ensures consistency.
    """
    # Version metadata
    policy_version: str = "2.1.0"
    state_machine_version: str = "1.0.0"
    
    # State information
    current_state: CalibrationState = CalibrationState.DEVELOPMENT
    target_state: CalibrationState = CalibrationState.PRODUCTION
    eligible_for_promotion: bool = False
    requires_downgrade: bool = False
    
    # Gate counts (MUST be consistent)
    gate_counts: Dict[str, int] = field(default_factory=lambda: {"pass": 0, "warning": 0, "fail": 0})
    
    # Gate lists (MUST match counts)
    passing_gates: List[str] = field(default_factory=list)
    warning_gates: List[str] = field(default_factory=list)
    failing_gates: List[str] = field(default_factory=list)
    
    # Detailed gate results
    gates: List[GateSummary] = field(default_factory=list)
    
    # Core gates (always present)
    core_gates: List[str] = field(default_factory=lambda: [
        "replicate_count", "residual_spread", "signal_to_separation",
        "portability", "stability", "model_fit"
    ])
    
    # Optional gates (may be None)
    optional_gates: List[str] = field(default_factory=lambda: [
        "heldout_performance", "backend_drift", "rank_stability_ci", "cohort_coverage"
    ])
    
    # Blocking and downgrade
    blocking_conditions: List[str] = field(default_factory=list)
    downgrade_triggers: List[str] = field(default_factory=list)
    recommended_action: RecommendedAction = RecommendedAction.HOLD
    
    # Additional context
    cohort_coverage: Optional[Dict[str, Any]] = None
    rank_stability_ci: Optional[Dict[str, Any]] = None
    
    # Metadata
    assessed_at: str = ""
    ledger_path: str = ""
    calibration_version: str = ""
    
    def __post_init__(self):
        """Validate consistency after initialization."""
        self._validate_consistency()
    
    def _validate_consistency(self):
        """Ensure gate counts match gate lists."""
        # Count from lists
        n_pass = len(self.passing_gates)
        n_warning = len(self.warning_gates)
        n_fail = len(self.failing_gates)
        
        # Check against gate_counts
        assert self.gate_counts["pass"] == n_pass, \
            f"Gate count mismatch: gate_counts['pass']={self.gate_counts['pass']} but passing_gates has {n_pass} items"
        assert self.gate_counts["warning"] == n_warning, \
            f"Gate count mismatch: gate_counts['warning']={self.gate_counts['warning']} but warning_gates has {n_warning} items"
        assert self.gate_counts["fail"] == n_fail, \
            f"Gate count mismatch: gate_counts['fail']={self.gate_counts['fail']} but failing_gates has {n_fail} items"
        
        # Check that all gates are accounted for
        total_gates = n_pass + n_warning + n_fail
        assert total_gates == len(self.gates), \
            f"Gate count mismatch: {total_gates} gates in lists but {len(self.gates)} gate summaries"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "policy_version": self.policy_version,
            "state_machine_version": self.state_machine_version,
            "current_state": self.current_state.value,
            "target_state": self.target_state.value,
            "eligible_for_promotion": self.eligible_for_promotion,
            "requires_downgrade": self.requires_downgrade,
            "gate_counts": self.gate_counts,
            "passing_gates": self.passing_gates,
            "warning_gates": self.warning_gates,
            "failing_gates": self.failing_gates,
            "gates": [g.to_dict() for g in self.gates],
            "core_gates": self.core_gates,
            "optional_gates": self.optional_gates,
            "blocking_conditions": self.blocking_conditions,
            "downgrade_triggers": self.downgrade_triggers,
            "recommended_action": self.recommended_action.value,
            "cohort_coverage": self.cohort_coverage,
            "rank_stability_ci": self.rank_stability_ci,
            "assessed_at": self.assessed_at,
            "ledger_path": self.ledger_path,
            "calibration_version": self.calibration_version,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CanonicalGovernanceOutput":
        """Create CanonicalGovernanceOutput from dictionary (deserialized JSON)."""
        # Parse gates from list of dicts
        gates = []
        for gate_data in data.get("gates", []):
            gate_summary = GateSummary(
                name=gate_data["name"],
                status=GateStatus(gate_data["status"]),
                value=gate_data["value"],
                pass_threshold=gate_data["pass_threshold"],
                warning_threshold=gate_data["warning_threshold"],
                margin_to_pass=gate_data["margin_to_pass"],
                message=gate_data["message"],
            )
            gates.append(gate_summary)
        
        return cls(
            policy_version=data.get("policy_version", "2.1.0"),
            state_machine_version=data.get("state_machine_version", "1.0.0"),
            current_state=CalibrationState(data.get("current_state", "development")),
            target_state=CalibrationState(data.get("target_state", "production")),
            eligible_for_promotion=data.get("eligible_for_promotion", False),
            requires_downgrade=data.get("requires_downgrade", False),
            gate_counts=data.get("gate_counts", {"pass": 0, "warning": 0, "fail": 0}),
            passing_gates=data.get("passing_gates", []),
            warning_gates=data.get("warning_gates", []),
            failing_gates=data.get("failing_gates", []),
            gates=gates,
            core_gates=data.get("core_gates", [
                "replicate_count", "residual_spread", "signal_to_separation",
                "portability", "stability", "model_fit"
            ]),
            optional_gates=data.get("optional_gates", [
                "heldout_performance", "backend_drift", "rank_stability_ci", "cohort_coverage"
            ]),
            blocking_conditions=data.get("blocking_conditions", []),
            downgrade_triggers=data.get("downgrade_triggers", []),
            recommended_action=RecommendedAction(data.get("recommended_action", "hold")),
            cohort_coverage=data.get("cohort_coverage"),
            rank_stability_ci=data.get("rank_stability_ci"),
            assessed_at=data.get("assessed_at", ""),
            ledger_path=data.get("ledger_path", ""),
            calibration_version=data.get("calibration_version", ""),
        )
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)
    
    def to_text_report(self) -> str:
        """Generate human-readable text report."""
        lines = [
            "=" * 70,
            "VCapture Lifecycle Governance Assessment v2.1",
            "=" * 70,
            "",
            f"Policy Version: {self.policy_version}",
            f"State Machine Version: {self.state_machine_version}",
            f"Assessed at: {self.assessed_at}",
            f"Ledger: {self.ledger_path}",
            f"Calibration version: {self.calibration_version}",
            "",
            "=" * 70,
            "STATE MACHINE STATUS",
            "=" * 70,
            "",
            f"  Current State: {self.current_state.value.upper()}",
            f"  Target State: {self.target_state.value.upper()}",
            f"  Eligible for Promotion: {'YES ✓' if self.eligible_for_promotion else 'NO ✗'}",
            f"  Requires Downgrade: {'YES ⚠' if self.requires_downgrade else 'NO'}",
            "",
            "  State Progression:",
        ]
        
        # State progression diagram
        states = ["development", "candidate", "staging", "production", "retired"]
        current_idx = states.index(self.current_state.value)
        
        for i, state in enumerate(states):
            if i < current_idx:
                marker = "✓"
            elif i == current_idx:
                marker = "●"
            else:
                marker = "○"
            lines.append(f"    {marker} {state.upper()}")
        lines.append("")
        
        # Gate summary (CANONICAL)
        lines.extend([
            "=" * 70,
            "GATE SUMMARY (CANONICAL)",
            "=" * 70,
            "",
            f"  Total Gates: {len(self.gates)}",
            f"  Core Gates: {len(self.core_gates)}",
            f"  Optional Gates: {len([g for g in self.optional_gates if any(gate.name == g for gate in self.gates)])}",
            "",
            f"  PASS: {self.gate_counts['pass']}",
            f"  WARNING: {self.gate_counts['warning']}",
            f"  FAIL: {self.gate_counts['fail']}",
            "",
        ])
        
        # Passing gates
        if self.passing_gates:
            lines.append("  Passing Gates:")
            for gate_name in self.passing_gates:
                lines.append(f"    ✓ {gate_name}")
            lines.append("")
        
        # Warning gates
        if self.warning_gates:
            lines.append("  Warning Gates:")
            for gate_name in self.warning_gates:
                lines.append(f"    ⚠ {gate_name}")
            lines.append("")
        
        # Failing gates
        if self.failing_gates:
            lines.append("  Failing Gates:")
            for gate_name in self.failing_gates:
                lines.append(f"    ✗ {gate_name}")
            lines.append("")
        
        # Detailed gate results
        lines.extend([
            "=" * 70,
            "GATE DETAILS",
            "=" * 70,
            "",
        ])
        
        for gate in self.gates:
            status_icon = {
                GateStatus.PASS: "✓ PASS",
                GateStatus.WARNING: "⚠ WARN",
                GateStatus.FAIL: "✗ FAIL",
            }[gate.status]
            
            lines.extend([
                f"  {gate.name}:",
                f"    Status: {status_icon}",
                f"    Value: {gate.value:.4f}",
                f"    Pass Threshold: {gate.pass_threshold:.4f}",
                f"    Warning Threshold: {gate.warning_threshold:.4f}",
                f"    Margin to Pass: {gate.margin_to_pass:+.4f}",
                f"    Message: {gate.message}",
                "",
            ])
        
        # Blocking conditions
        if self.blocking_conditions:
            lines.extend([
                "=" * 70,
                "BLOCKING CONDITIONS",
                "=" * 70,
                "",
            ])
            for condition in self.blocking_conditions:
                lines.append(f"  ✗ {condition}")
            lines.append("")
        
        # Downgrade triggers
        if self.downgrade_triggers:
            lines.extend([
                "=" * 70,
                "DOWNGRADE TRIGGERS",
                "=" * 70,
                "",
            ])
            for trigger in self.downgrade_triggers:
                lines.append(f"  ⚠ {trigger}")
            lines.append("")
        
        # Recommended action
        lines.extend([
            "=" * 70,
            "RECOMMENDED ACTION",
            "=" * 70,
            "",
            f"  {self.recommended_action.value.upper()}",
            "",
        ])
        
        # Additional context
        if self.cohort_coverage:
            lines.extend([
                "=" * 70,
                "COHORT COVERAGE",
                "=" * 70,
                "",
                f"  Total Promoters: {self.cohort_coverage.get('total_promoters', 'N/A')}",
                f"  Promoters Above S/S: {self.cohort_coverage.get('promoters_above_ss', 'N/A')}",
                f"  Cells with Min Replicates: {self.cohort_coverage.get('cells_with_min_replicates', 'N/A')}/{self.cohort_coverage.get('total_cells', 'N/A')}",
                "",
            ])
        
        if self.rank_stability_ci:
            lines.extend([
                "=" * 70,
                "RANK STABILITY CI",
                "=" * 70,
                "",
                f"  Point Estimate: {self.rank_stability_ci.get('point_estimate', 'N/A'):.4f}",
                f"  95% CI: [{self.rank_stability_ci.get('ci_lower', 'N/A'):.4f}, {self.rank_stability_ci.get('ci_upper', 'N/A'):.4f}]",
                "",
            ])
        
        return "\n".join(lines)
    
    def to_markdown_summary(self) -> str:
        """Generate markdown summary."""
        lines = [
            "# VCapture Governance Assessment",
            "",
            f"**Policy Version**: {self.policy_version}",
            f"**State Machine Version**: {self.state_machine_version}",
            "",
            "## State Machine Status",
            "",
            f"- **Current State**: `{self.current_state.value.upper()}`",
            f"- **Target State**: `{self.target_state.value.upper()}`",
            f"- **Eligible for Promotion**: {'✓ YES' if self.eligible_for_promotion else '✗ NO'}",
            f"- **Requires Downgrade**: {'⚠ YES' if self.requires_downgrade else 'NO'}",
            "",
            "## Gate Summary",
            "",
            f"- **PASS**: {self.gate_counts['pass']}",
            f"- **WARNING**: {self.gate_counts['warning']}",
            f"- **FAIL**: {self.gate_counts['fail']}",
            "",
        ]
        
        if self.passing_gates:
            lines.append("### Passing Gates")
            lines.append("")
            for gate_name in self.passing_gates:
                lines.append(f"- ✓ {gate_name}")
            lines.append("")
        
        if self.warning_gates:
            lines.append("### Warning Gates")
            lines.append("")
            for gate_name in self.warning_gates:
                lines.append(f"- ⚠ {gate_name}")
            lines.append("")
        
        if self.failing_gates:
            lines.append("### Failing Gates")
            lines.append("")
            for gate_name in self.failing_gates:
                lines.append(f"- ✗ {gate_name}")
            lines.append("")
        
        lines.extend([
            "## Recommended Action",
            "",
            f"**{self.recommended_action.value.upper()}**",
            "",
        ])
        
        if self.blocking_conditions:
            lines.extend([
                "## Blocking Conditions",
                "",
            ])
            for condition in self.blocking_conditions:
                lines.append(f"- ✗ {condition}")
            lines.append("")
        
        return "\n".join(lines)
    
    def to_cli_display(self) -> str:
        """Generate CLI display string."""
        lines = [
            "=" * 70,
            "LIFECYCLE GOVERNANCE SUMMARY",
            "=" * 70,
            "",
            f"  Current State: {self.current_state.value.upper()}",
            f"  Eligible for Promotion: {'YES ✓' if self.eligible_for_promotion else 'NO ✗'}",
            f"  Requires Downgrade: {'YES ⚠' if self.requires_downgrade else 'NO'}",
            "",
            f"  Gate Summary: {self.gate_counts['pass']} pass, {self.gate_counts['warning']} warning, {self.gate_counts['fail']} fail",
            "",
        ]
        
        if self.warning_gates:
            lines.append("  Warnings:")
            for gate_name in self.warning_gates:
                lines.append(f"    • {gate_name}")
            lines.append("")
        
        if self.failing_gates:
            lines.append("  Failures:")
            for gate_name in self.failing_gates:
                lines.append(f"    • {gate_name}")
            lines.append("")
        
        lines.append(f"  Recommended Action: {self.recommended_action.value.upper()}")
        lines.append("")
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    @classmethod
    def from_assessment(cls, assessment: Dict[str, Any]) -> 'CanonicalGovernanceOutput':
        """
        Create canonical output from lifecycle assessment.
        
        This is the ONLY way to create CanonicalGovernanceOutput from an assessment.
        It ensures consistency between gate counts and gate lists.
        """
        # Extract gates
        gates_data = assessment.get('gates', {})
        
        # Core gates (always present)
        core_gate_names = [
            "replicate_count", "residual_spread", "signal_to_separation",
            "portability", "stability", "model_fit"
        ]
        
        # Optional gates (may be None)
        optional_gate_names = [
            "heldout_performance", "backend_drift", "rank_stability_ci", "cohort_coverage"
        ]
        
        # Build gate summaries
        gates = []
        passing_gates = []
        warning_gates = []
        failing_gates = []
        
        # Process core gates
        for gate_name in core_gate_names:
            # Map gate names to assessment keys
            gate_key = gate_name.replace("signal_to_separation", "separation")
            gate_key = gate_key.replace("replicate_count", "replicate")
            gate_key = gate_key.replace("residual_spread", "residual")
            gate_key = gate_key.replace("model_fit", "model_fit")
            gate_data = gates_data.get(gate_key, {})
            
            if gate_data:
                status_str = gate_data.get('status', 'fail')
                status = GateStatus(status_str)
                
                gate_summary = GateSummary(
                    name=gate_name,
                    status=status,
                    value=gate_data.get('value', 0.0),
                    pass_threshold=gate_data.get('pass_threshold', 0.0),
                    warning_threshold=gate_data.get('warning_threshold', 0.0),
                    margin_to_pass=gate_data.get('margin_to_pass', 0.0),
                    message=gate_data.get('message', ''),
                )
                
                gates.append(gate_summary)
                
                if status == GateStatus.PASS:
                    passing_gates.append(gate_name)
                elif status == GateStatus.WARNING:
                    warning_gates.append(gate_name)
                else:
                    failing_gates.append(gate_name)
        
        # Process optional gates
        for gate_name in optional_gate_names:
            gate_key = gate_name.replace("heldout_performance", "heldout")
            gate_key = gate_key.replace("backend_drift", "drift")
            gate_key = gate_key.replace("rank_stability_ci", "rank_ci")
            gate_key = gate_key.replace("cohort_coverage", "coverage")
            
            gate_data = gates_data.get(gate_key)
            
            if gate_data:
                status_str = gate_data.get('status', 'fail')
                status = GateStatus(status_str)
                
                gate_summary = GateSummary(
                    name=gate_name,
                    status=status,
                    value=gate_data.get('value', 0.0),
                    pass_threshold=gate_data.get('pass_threshold', 0.0),
                    warning_threshold=gate_data.get('warning_threshold', 0.0),
                    margin_to_pass=gate_data.get('margin_to_pass', 0.0),
                    message=gate_data.get('message', ''),
                )
                
                gates.append(gate_summary)
                
                if status == GateStatus.PASS:
                    passing_gates.append(gate_name)
                elif status == GateStatus.WARNING:
                    warning_gates.append(gate_name)
                else:
                    failing_gates.append(gate_name)
        
        # Calculate gate counts (MUST match lists)
        gate_counts = {
            "pass": len(passing_gates),
            "warning": len(warning_gates),
            "fail": len(failing_gates),
        }
        
        # Determine recommended action
        current_state = CalibrationState(assessment.get('current_state', 'development'))
        eligible = assessment.get('eligible_for_promotion', False)
        requires_downgrade = assessment.get('requires_downgrade', False)
        
        if requires_downgrade:
            recommended_action = RecommendedAction.DOWNGRADE
        elif eligible and gate_counts['fail'] == 0:
            recommended_action = RecommendedAction.PROMOTE
        elif gate_counts['fail'] > 0:
            recommended_action = RecommendedAction.REJECT
        else:
            recommended_action = RecommendedAction.HOLD
        
        # Extract additional context
        cohort_coverage = assessment.get('cohort_coverage')
        rank_stability_ci = assessment.get('rank_stability_ci')
        
        return cls(
            policy_version="2.1.0",
            state_machine_version="1.0.0",
            current_state=current_state,
            target_state=CalibrationState(assessment.get('target_state', 'production')),
            eligible_for_promotion=eligible,
            requires_downgrade=requires_downgrade,
            gate_counts=gate_counts,
            passing_gates=passing_gates,
            warning_gates=warning_gates,
            failing_gates=failing_gates,
            gates=gates,
            core_gates=core_gate_names,
            optional_gates=optional_gate_names,
            blocking_conditions=assessment.get('blocking_issues', []),
            downgrade_triggers=[],  # Would need to extract from assessment
            recommended_action=recommended_action,
            cohort_coverage=cohort_coverage,
            rank_stability_ci=rank_stability_ci,
            assessed_at=assessment.get('assessed_at', ''),
            ledger_path=assessment.get('ledger_path', ''),
            calibration_version=assessment.get('calibration_version', ''),
        )


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Test canonical output schema."""
    import argparse
    from pathlib import Path
    
    parser = argparse.ArgumentParser(description="VCapture Canonical Output Schema")
    parser.add_argument("--assessment", type=str, help="Path to lifecycle assessment JSON")
    parser.add_argument("--output-json", type=str, default="canonical_output.json", help="Output JSON path")
    parser.add_argument("--output-text", type=str, default="canonical_report.txt", help="Output text report path")
    parser.add_argument("--output-markdown", type=str, default="canonical_summary.md", help="Output markdown path")
    
    args = parser.parse_args()
    
    if args.assessment:
        # Load assessment
        with open(args.assessment, 'r', encoding='utf-8') as f:
            assessment = json.load(f)
        
        # Create canonical output
        canonical = CanonicalGovernanceOutput.from_assessment(assessment)
        
        # Save all outputs
        with open(args.output_json, 'w', encoding='utf-8') as f:
            f.write(canonical.to_json())
        
        with open(args.output_text, 'w', encoding='utf-8') as f:
            f.write(canonical.to_text_report())
        
        with open(args.output_markdown, 'w', encoding='utf-8') as f:
            f.write(canonical.to_markdown_summary())
        
        # Print CLI display
        print(canonical.to_cli_display())
        
        print(f"\nJSON saved to: {args.output_json}")
        print(f"Text report saved to: {args.output_text}")
        print(f"Markdown saved to: {args.output_markdown}")
    else:
        # Create example canonical output
        example = CanonicalGovernanceOutput(
            current_state=CalibrationState.DEVELOPMENT,
            target_state=CalibrationState.PRODUCTION,
            eligible_for_promotion=True,
            requires_downgrade=False,
            gate_counts={"pass": 4, "warning": 3, "fail": 0},
            passing_gates=["replicate_count", "signal_to_separation", "stability", "model_fit"],
            warning_gates=["residual_spread", "portability", "rank_stability_ci"],
            failing_gates=[],
            gates=[
                GateSummary("replicate_count", GateStatus.PASS, 3.0, 1.0, 1.0, 2.0, "Replicate count: 3 per cell, 30 total (pass)"),
                GateSummary("residual_spread", GateStatus.WARNING, 0.0848, 0.10, 0.15, 0.0152, "Residual spread: std=0.0848, mean=0.1417 (warning)"),
                GateSummary("signal_to_separation", GateStatus.PASS, 1.42, 1.0, 0.8, 0.42, "Signal-to-separation: mean S/S=1.42 (pass)"),
                GateSummary("portability", GateStatus.WARNING, 0.85, 0.85, 0.75, 0.0, "Portability: efficiency=100.0%, ranking=0.70, score=85.0% (warning)"),
                GateSummary("stability", GateStatus.PASS, 0.0015, 0.01, 0.02, 0.0085, "Stability: within-promoter std=0.0015 (pass)"),
                GateSummary("model_fit", GateStatus.PASS, 0.90, 0.50, 0.40, 0.40, "Model fit: R²=0.90 (pass)"),
                GateSummary("rank_stability_ci", GateStatus.WARNING, 0.60, 0.70, 0.60, -0.10, "Rank stability CI: [0.60, 0.80] (warning)"),
            ],
            blocking_conditions=[],
            downgrade_triggers=[],
            recommended_action=RecommendedAction.HOLD,
            assessed_at=datetime.now().isoformat(),
            ledger_path="raw_hardware/vcapture_ledger_report.json",
            calibration_version="1.0",
        )
        
        print(example.to_cli_display())


if __name__ == "__main__":
    main()