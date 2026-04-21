#!/usr/bin/env python3
"""
VCapture Promotion Policy Engine v1.0
====================================

Turns the measurement ledger into a calibration governance system with
explicit thresholds for promotion decisions.

Promotion Gates:
1. Replicate Count Gate: Minimum replicates per promoter-backend cell
2. Residual Spread Gate: Maximum residual std after calibration
3. Signal-to-Separation Gate: Minimum S/S ratio for promoter identity
4. Portability Gate: Minimum transfer efficiency and ranking correlation
5. Stability Gate: Maximum variance across seeds/runs

Promotion Levels:
- DEVELOPMENT: Not ready for production use
- STAGING: Ready for cross-validation testing
- PRODUCTION: Ready for deployment
- DEPRECATED: Should be replaced

Usage:
    python vcapture_promotion_policy.py --ledger raw_hardware/vcapture_ledger_report.json
"""

import argparse
import json
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import warnings

import numpy as np


# =============================================================================
# PROMOTION LEVELS
# =============================================================================

class PromotionLevel(str, Enum):
    """Calibration model promotion levels."""
    DEVELOPMENT = "development"  # Not ready for production
    STAGING = "staging"          # Ready for cross-validation
    PRODUCTION = "production"    # Ready for deployment
    DEPRECATED = "deprecated"    # Should be replaced


# =============================================================================
# GATE THRESHOLDS
# =============================================================================

@dataclass
class GateThresholds:
    """
    Thresholds for each promotion gate.
    
    These are the explicit decision boundaries that determine whether
    a calibration model passes or fails each quality gate.
    """
    # Replicate Count Gate
    min_replicates_per_cell: int = 3          # Minimum replicates per promoter-backend
    min_total_records: int = 20               # Minimum total records in ledger
    
    # Residual Spread Gate
    max_residual_std: float = 0.10            # Maximum residual std after calibration
    max_residual_mean_abs: float = 0.05      # Maximum |mean residual|
    max_residual_mad: float = 0.08            # Maximum median absolute deviation
    
    # Signal-to-Separation Gate
    min_ss_ratio: float = 2.0                 # Minimum S/S for promoter identity
    min_promoters_above_threshold: float = 0.5  # Fraction of promoters that must pass S/S
    
    # Portability Gate
    min_transfer_efficiency: float = 0.90     # Minimum transfer efficiency
    min_ranking_correlation: float = 0.80    # Minimum ranking correlation
    min_portability_score: float = 0.85      # Minimum overall portability score
    
    # Stability Gate
    max_output_stability: float = 0.01       # Maximum output variance across seeds
    max_convergence_stability: float = 0.1   # Maximum convergence variance
    
    # Mixed-Effects Gate
    min_r_squared: float = 0.70              # Minimum model fit
    max_interaction_variance_ratio: float = 0.1  # Interaction / total variance
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# Default thresholds for different promotion levels
DEFAULT_THRESHOLDS = {
    PromotionLevel.DEVELOPMENT: GateThresholds(
        min_replicates_per_cell=1,
        min_total_records=5,
        max_residual_std=0.20,
        max_residual_mean_abs=0.10,
        max_residual_mad=0.15,
        min_ss_ratio=1.0,
        min_promoters_above_threshold=0.2,
        min_transfer_efficiency=0.70,
        min_ranking_correlation=0.50,
        min_portability_score=0.60,
        max_output_stability=0.05,
        max_convergence_stability=0.3,
        min_r_squared=0.50,
        max_interaction_variance_ratio=0.3,
    ),
    PromotionLevel.STAGING: GateThresholds(
        min_replicates_per_cell=2,
        min_total_records=15,
        max_residual_std=0.15,
        max_residual_mean_abs=0.08,
        max_residual_mad=0.12,
        min_ss_ratio=1.5,
        min_promoters_above_threshold=0.4,
        min_transfer_efficiency=0.85,
        min_ranking_correlation=0.70,
        min_portability_score=0.75,
        max_output_stability=0.02,
        max_convergence_stability=0.2,
        min_r_squared=0.60,
        max_interaction_variance_ratio=0.2,
    ),
    PromotionLevel.PRODUCTION: GateThresholds(
        min_replicates_per_cell=3,
        min_total_records=20,
        max_residual_std=0.10,
        max_residual_mean_abs=0.05,
        max_residual_mad=0.08,
        min_ss_ratio=2.0,
        min_promoters_above_threshold=0.5,
        min_transfer_efficiency=0.90,
        min_ranking_correlation=0.80,
        min_portability_score=0.85,
        max_output_stability=0.01,
        max_convergence_stability=0.1,
        min_r_squared=0.70,
        max_interaction_variance_ratio=0.1,
    ),
}


# =============================================================================
# GATE RESULTS
# =============================================================================

@dataclass
class GateResult:
    """Result of a single promotion gate."""
    gate_name: str
    passed: bool
    value: float
    threshold: float
    margin: float  # value - threshold (positive = passed with margin)
    message: str
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PromotionAssessment:
    """Complete promotion assessment for a calibration model."""
    # Overall result
    promotion_level: str
    eligible_for_promotion: bool
    overall_score: float
    
    # Gate results
    replicate_gate: GateResult
    residual_gate: GateResult
    separation_gate: GateResult
    portability_gate: GateResult
    stability_gate: GateResult
    model_fit_gate: GateResult
    
    # Recommendations
    blocking_issues: List[str]
    warnings: List[str]
    recommendations: List[str]
    
    # Metadata
    assessed_at: str
    ledger_path: str
    calibration_version: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "promotion_level": self.promotion_level,
            "eligible_for_promotion": self.eligible_for_promotion,
            "overall_score": self.overall_score,
            "gates": {
                "replicate": self.replicate_gate.to_dict(),
                "residual": self.residual_gate.to_dict(),
                "separation": self.separation_gate.to_dict(),
                "portability": self.portability_gate.to_dict(),
                "stability": self.stability_gate.to_dict(),
                "model_fit": self.model_fit_gate.to_dict(),
            },
            "blocking_issues": self.blocking_issues,
            "warnings": self.warnings,
            "recommendations": self.recommendations,
            "assessed_at": self.assessed_at,
            "ledger_path": self.ledger_path,
            "calibration_version": self.calibration_version,
        }


# =============================================================================
# PROMOTION POLICY ENGINE
# =============================================================================

class VCapturePromotionPolicy:
    """
    Promotion policy engine for calibration governance.
    
    Evaluates calibration models against explicit thresholds to determine
    whether they are ready for promotion to the next level.
    """
    
    def __init__(self, 
                 target_level: PromotionLevel = PromotionLevel.PRODUCTION,
                 thresholds: Optional[GateThresholds] = None):
        self.target_level = target_level
        self.thresholds = thresholds or DEFAULT_THRESHOLDS[target_level]
    
    def assess_ledger(self, ledger_path: Path) -> PromotionAssessment:
        """
        Assess a VCapture ledger against promotion policy.
        
        Args:
            ledger_path: Path to VCapture ledger JSON
            
        Returns:
            PromotionAssessment with gate results and recommendations
        """
        with open(ledger_path, 'r', encoding='utf-8') as f:
            ledger = json.load(f)
        
        # Extract metrics from ledger
        metadata = ledger.get('metadata', {})
        variance = ledger.get('variance_structure', {})
        transfer = ledger.get('transferability', [])
        mixed = ledger.get('mixed_effects', {})
        
        # Run each gate
        replicate_gate = self._assess_replicate_gate(metadata, variance)
        residual_gate = self._assess_residual_gate(variance)
        separation_gate = self._assess_separation_gate(variance)
        portability_gate = self._assess_portability_gate(transfer)
        stability_gate = self._assess_stability_gate(variance)
        model_fit_gate = self._assess_model_fit_gate(mixed)
        
        # Collect results
        gates = [
            replicate_gate, residual_gate, separation_gate,
            portability_gate, stability_gate, model_fit_gate
        ]
        
        # Determine promotion level
        all_passed = all(g.passed for g in gates)
        passed_count = sum(1 for g in gates if g.passed)
        
        if all_passed:
            promotion_level = self.target_level.value
            eligible = True
        elif passed_count >= 4:
            promotion_level = PromotionLevel.STAGING.value
            eligible = False
        elif passed_count >= 2:
            promotion_level = PromotionLevel.DEVELOPMENT.value
            eligible = False
        else:
            promotion_level = PromotionLevel.DEPRECATED.value
            eligible = False
        
        # Calculate overall score
        margins = [g.margin for g in gates if g.margin is not None]
        overall_score = float(np.mean(margins)) if margins else 0.0
        
        # Generate recommendations
        blocking_issues = [g.message for g in gates if not g.passed]
        warnings = []
        recommendations = self._generate_recommendations(gates)
        
        return PromotionAssessment(
            promotion_level=promotion_level,
            eligible_for_promotion=eligible,
            overall_score=overall_score,
            replicate_gate=replicate_gate,
            residual_gate=residual_gate,
            separation_gate=separation_gate,
            portability_gate=portability_gate,
            stability_gate=stability_gate,
            model_fit_gate=model_fit_gate,
            blocking_issues=blocking_issues,
            warnings=warnings,
            recommendations=recommendations,
            assessed_at=datetime.now().isoformat(),
            ledger_path=str(ledger_path),
            calibration_version=metadata.get('calibration_version', 'unknown'),
        )
    
    def _assess_replicate_gate(self, metadata: Dict, variance: Dict) -> GateResult:
        """Assess replicate count gate."""
        total_records = metadata.get('total_records', 0)
        summaries = variance.get('promoter_backend_summaries', [])
        
        if summaries:
            min_replicates = min(s.get('replicate_count', 0) for s in summaries)
        else:
            min_replicates = 0
        
        # Check both conditions
        passed = (
            min_replicates >= self.thresholds.min_replicates_per_cell and
            total_records >= self.thresholds.min_total_records
        )
        
        # Use the worse metric for value
        value = min(min_replicates, total_records / 10)  # Normalize total records
        
        if passed:
            message = f"Replicate count sufficient: {min_replicates} per cell, {total_records} total"
        else:
            message = f"Insufficient replicates: {min_replicates} per cell (need {self.thresholds.min_replicates_per_cell}), {total_records} total (need {self.thresholds.min_total_records})"
        
        return GateResult(
            gate_name="replicate_count",
            passed=passed,
            value=float(min_replicates),
            threshold=float(self.thresholds.min_replicates_per_cell),
            margin=float(min_replicates - self.thresholds.min_replicates_per_cell),
            message=message,
        )
    
    def _assess_residual_gate(self, variance: Dict) -> GateResult:
        """Assess residual spread gate."""
        residual_mean = abs(variance.get('residual_mean', 1.0))
        residual_std = variance.get('residual_std', 1.0)
        
        # Check both conditions
        passed = (
            residual_std <= self.thresholds.max_residual_std and
            residual_mean <= self.thresholds.max_residual_mean_abs
        )
        
        # Use the worse metric for value
        value = max(residual_std, residual_mean)
        
        if passed:
            message = f"Residual spread acceptable: std={residual_std:.4f}, mean={residual_mean:.4f}"
        else:
            message = f"Residual spread too high: std={residual_std:.4f} (max {self.thresholds.max_residual_std}), mean={residual_mean:.4f} (max {self.thresholds.max_residual_mean_abs})"
        
        return GateResult(
            gate_name="residual_spread",
            passed=passed,
            value=float(residual_std),
            threshold=float(self.thresholds.max_residual_std),
            margin=float(self.thresholds.max_residual_std - residual_std),
            message=message,
        )
    
    def _assess_separation_gate(self, variance: Dict) -> GateResult:
        """Assess signal-to-separation gate."""
        summaries = variance.get('promoter_backend_summaries', [])
        
        if not summaries:
            return GateResult(
                gate_name="signal_to_separation",
                passed=False,
                value=0.0,
                threshold=self.thresholds.min_ss_ratio,
                margin=-self.thresholds.min_ss_ratio,
                message="No promoter-backend summaries available",
            )
        
        # Count promoters above threshold
        ss_values = [s.get('signal_to_separation', 0) for s in summaries]
        promoters_above = sum(1 for ss in ss_values if ss >= self.thresholds.min_ss_ratio)
        fraction_above = promoters_above / len(ss_values) if ss_values else 0
        
        # Also check mean S/S
        mean_ss = np.mean(ss_values) if ss_values else 0
        
        passed = (
            fraction_above >= self.thresholds.min_promoters_above_threshold and
            mean_ss >= self.thresholds.min_ss_ratio * 0.5  # Relaxed mean requirement
        )
        
        value = float(mean_ss)
        
        if passed:
            message = f"Promoter separation sufficient: {promoters_above}/{len(ss_values)} promoters above threshold, mean S/S={mean_ss:.2f}"
        else:
            message = f"Promoter separation insufficient: {promoters_above}/{len(ss_values)} promoters above threshold (need {self.thresholds.min_promoters_above_threshold:.0%}), mean S/S={mean_ss:.2f}"
        
        return GateResult(
            gate_name="signal_to_separation",
            passed=passed,
            value=value,
            threshold=self.thresholds.min_ss_ratio,
            margin=value - self.thresholds.min_ss_ratio,
            message=message,
        )
    
    def _assess_portability_gate(self, transfer: List[Dict]) -> GateResult:
        """Assess portability gate."""
        if not transfer:
            return GateResult(
                gate_name="portability",
                passed=False,
                value=0.0,
                threshold=self.thresholds.min_portability_score,
                margin=-self.thresholds.min_portability_score,
                message="No transferability data available",
            )
        
        # Get first transfer report (primary cross-backend test)
        tr = transfer[0]
        
        transfer_efficiency = tr.get('transfer_efficiency', 0)
        ranking_corr = abs(tr.get('promoter_ranking_correlation', 0))
        portability_score = tr.get('portability_score', 0)
        
        passed = (
            transfer_efficiency >= self.thresholds.min_transfer_efficiency and
            ranking_corr >= self.thresholds.min_ranking_correlation and
            portability_score >= self.thresholds.min_portability_score
        )
        
        value = float(portability_score)
        
        if passed:
            message = f"Calibration portable: efficiency={transfer_efficiency:.1%}, ranking={ranking_corr:.2f}, score={portability_score:.1%}"
        else:
            message = f"Calibration not portable: efficiency={transfer_efficiency:.1%} (need {self.thresholds.min_transfer_efficiency:.0%}), ranking={ranking_corr:.2f} (need {self.thresholds.min_ranking_correlation:.0%}), score={portability_score:.1%}"
        
        return GateResult(
            gate_name="portability",
            passed=passed,
            value=value,
            threshold=self.thresholds.min_portability_score,
            margin=value - self.thresholds.min_portability_score,
            message=message,
        )
    
    def _assess_stability_gate(self, variance: Dict) -> GateResult:
        """Assess stability gate."""
        # Use within-promoter variance as stability proxy
        within_var = variance.get('within_promoter_variance', {})
        
        if not within_var:
            return GateResult(
                gate_name="stability",
                passed=False,
                value=1.0,
                threshold=self.thresholds.max_output_stability,
                margin=self.thresholds.max_output_stability - 1.0,
                message="No within-promoter variance data available",
            )
        
        # Convert variance to std
        within_stds = [np.sqrt(v) for v in within_var.values() if v > 0]
        mean_stability = float(np.mean(within_stds)) if within_stds else 1.0
        
        passed = mean_stability <= self.thresholds.max_output_stability
        
        if passed:
            message = f"Measurement stability sufficient: within-promoter std={mean_stability:.6f}"
        else:
            message = f"Measurement stability insufficient: within-promoter std={mean_stability:.6f} (max {self.thresholds.max_output_stability})"
        
        return GateResult(
            gate_name="stability",
            passed=passed,
            value=mean_stability,
            threshold=self.thresholds.max_output_stability,
            margin=self.thresholds.max_output_stability - mean_stability,
            message=message,
        )
    
    def _assess_model_fit_gate(self, mixed: Dict) -> GateResult:
        """Assess model fit gate."""
        if not mixed:
            return GateResult(
                gate_name="model_fit",
                passed=False,
                value=0.0,
                threshold=self.thresholds.min_r_squared,
                margin=-self.thresholds.min_r_squared,
                message="No mixed-effects model data available",
            )
        
        model_stats = mixed.get('model_statistics', {})
        var_components = mixed.get('variance_components', {})
        
        r_squared = model_stats.get('r_squared', 0)
        
        # Check interaction variance ratio
        total_var = sum(var_components.values()) if var_components else 1
        interaction_var = var_components.get('interaction', 0)
        interaction_ratio = interaction_var / total_var if total_var > 0 else 0
        
        passed = (
            r_squared >= self.thresholds.min_r_squared and
            interaction_ratio <= self.thresholds.max_interaction_variance_ratio
        )
        
        if passed:
            message = f"Model fit sufficient: R²={r_squared:.4f}, interaction ratio={interaction_ratio:.4f}"
        else:
            message = f"Model fit insufficient: R²={r_squared:.4f} (need {self.thresholds.min_r_squared}), interaction ratio={interaction_ratio:.4f}"
        
        return GateResult(
            gate_name="model_fit",
            passed=passed,
            value=float(r_squared),
            threshold=self.thresholds.min_r_squared,
            margin=float(r_squared - self.thresholds.min_r_squared),
            message=message,
        )
    
    def _generate_recommendations(self, gates: List[GateResult]) -> List[str]:
        """Generate recommendations based on gate results."""
        recommendations = []
        
        for gate in gates:
            if not gate.passed:
                if gate.gate_name == "replicate_count":
                    recommendations.append(
                        f"Increase replicates per promoter-backend cell to at least {self.thresholds.min_replicates_per_cell}"
                    )
                elif gate.gate_name == "residual_spread":
                    recommendations.append(
                        "Investigate residual outliers; consider robust calibration methods"
                    )
                elif gate.gate_name == "signal_to_separation":
                    recommendations.append(
                        "Increase promoter distinctiveness or reduce measurement noise"
                    )
                elif gate.gate_name == "portability":
                    recommendations.append(
                        "Use backend-conditioned or hierarchical calibration instead of universal offset"
                    )
                elif gate.gate_name == "stability":
                    recommendations.append(
                        "Investigate measurement protocol for sources of variance"
                    )
                elif gate.gate_name == "model_fit":
                    recommendations.append(
                        "Add covariates (circuit depth, gate counts, backend calibration) to model"
                    )
        
        # Add general recommendations
        if not any(g.passed for g in gates):
            recommendations.append(
                "Consider fundamental redesign of calibration protocol"
            )
        
        return recommendations


# =============================================================================
# PROMOTION REPORT GENERATOR
# =============================================================================

def generate_promotion_report(assessment: PromotionAssessment, output_path: Path):
    """Generate human-readable promotion report."""
    
    report_lines = [
        "=" * 70,
        "VCapture Calibration Promotion Assessment",
        "=" * 70,
        "",
        f"Assessed at: {assessment.assessed_at}",
        f"Ledger: {assessment.ledger_path}",
        f"Calibration version: {assessment.calibration_version}",
        "",
        "=" * 70,
        "PROMOTION DECISION",
        "=" * 70,
        "",
        f"  Promotion Level: {assessment.promotion_level.upper()}",
        f"  Eligible for Promotion: {'YES ✓' if assessment.eligible_for_promotion else 'NO ✗'}",
        f"  Overall Score: {assessment.overall_score:+.4f}",
        "",
        "=" * 70,
        "GATE RESULTS",
        "=" * 70,
        "",
    ]
    
    gates = [
        ("Replicate Count", assessment.replicate_gate),
        ("Residual Spread", assessment.residual_gate),
        ("Signal-to-Separation", assessment.separation_gate),
        ("Portability", assessment.portability_gate),
        ("Stability", assessment.stability_gate),
        ("Model Fit", assessment.model_fit_gate),
    ]
    
    for name, gate in gates:
        status = "✓ PASS" if gate.passed else "✗ FAIL"
        report_lines.append(f"  {name}:")
        report_lines.append(f"    Status: {status}")
        report_lines.append(f"    Value: {gate.value:.4f}")
        report_lines.append(f"    Threshold: {gate.threshold:.4f}")
        report_lines.append(f"    Margin: {gate.margin:+.4f}")
        report_lines.append(f"    Message: {gate.message}")
        report_lines.append("")
    
    if assessment.blocking_issues:
        report_lines.append("=" * 70)
        report_lines.append("BLOCKING ISSUES")
        report_lines.append("=" * 70)
        report_lines.append("")
        for issue in assessment.blocking_issues:
            report_lines.append(f"  • {issue}")
        report_lines.append("")
    
    if assessment.recommendations:
        report_lines.append("=" * 70)
        report_lines.append("RECOMMENDATIONS")
        report_lines.append("=" * 70)
        report_lines.append("")
        for rec in assessment.recommendations:
            report_lines.append(f"  → {rec}")
        report_lines.append("")
    
    report_lines.append("=" * 70)
    report_lines.append("PROMOTION CRITERIA REFERENCE")
    report_lines.append("=" * 70)
    report_lines.append("")
    report_lines.append("  PRODUCTION thresholds:")
    report_lines.append(f"    • Min replicates per cell: {DEFAULT_THRESHOLDS[PromotionLevel.PRODUCTION].min_replicates_per_cell}")
    report_lines.append(f"    • Max residual std: {DEFAULT_THRESHOLDS[PromotionLevel.PRODUCTION].max_residual_std}")
    report_lines.append(f"    • Min S/S ratio: {DEFAULT_THRESHOLDS[PromotionLevel.PRODUCTION].min_ss_ratio}")
    report_lines.append(f"    • Min transfer efficiency: {DEFAULT_THRESHOLDS[PromotionLevel.PRODUCTION].min_transfer_efficiency:.0%}")
    report_lines.append(f"    • Min ranking correlation: {DEFAULT_THRESHOLDS[PromotionLevel.PRODUCTION].min_ranking_correlation:.0%}")
    report_lines.append(f"    • Min R²: {DEFAULT_THRESHOLDS[PromotionLevel.PRODUCTION].min_r_squared}")
    report_lines.append("")
    
    report_text = "\n".join(report_lines)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report_text)
    
    return report_text


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="VCapture Promotion Policy Engine")
    parser.add_argument("--ledger", type=str, required=True, help="Path to VCapture ledger JSON")
    parser.add_argument("--output", type=str, default="promotion_assessment.json", help="Output assessment JSON")
    parser.add_argument("--report", type=str, default="promotion_report.txt", help="Human-readable report")
    parser.add_argument("--target-level", type=str, default="production", 
                        choices=["development", "staging", "production"],
                        help="Target promotion level")
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("VCapture Promotion Policy Engine")
    print("=" * 70)
    
    # Initialize policy engine
    target_level = PromotionLevel(args.target_level)
    policy = VCapturePromotionPolicy(target_level=target_level)
    
    print(f"\nTarget promotion level: {target_level.value.upper()}")
    print(f"Assessing ledger: {args.ledger}")
    
    # Run assessment
    ledger_path = Path(args.ledger)
    assessment = policy.assess_ledger(ledger_path)
    
    # Save JSON assessment
    output_path = Path(args.output)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(assessment.to_dict(), f, indent=2)
    print(f"\nAssessment saved to: {output_path}")
    
    # Generate human-readable report
    report_path = Path(args.report)
    report_text = generate_promotion_report(assessment, report_path)
    print(f"Report saved to: {report_path}")
    
    # Print summary
    print("\n" + "=" * 70)
    print("PROMOTION DECISION SUMMARY")
    print("=" * 70)
    print(f"\n  Level: {assessment.promotion_level.upper()}")
    print(f"  Eligible: {'YES ✓' if assessment.eligible_for_promotion else 'NO ✗'}")
    print(f"  Score: {assessment.overall_score:+.4f}")
    print(f"\n  Gates passed: {sum(1 for g in [assessment.replicate_gate, assessment.residual_gate, assessment.separation_gate, assessment.portability_gate, assessment.stability_gate, assessment.model_fit_gate] if g.passed)}/6")
    
    if assessment.blocking_issues:
        print(f"\n  Blocking issues: {len(assessment.blocking_issues)}")
        for issue in assessment.blocking_issues[:3]:
            print(f"    • {issue[:60]}...")
    
    print("\n" + report_text)


if __name__ == "__main__":
    main()