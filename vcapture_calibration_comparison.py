#!/usr/bin/env python3
"""
VCapture Calibration Comparison Framework
==========================================

Compares calibration models under the same governance gates to determine
if a new model improves residual spread, increases S/S, and preserves
ranking portability enough to move from development to candidate.

This implements the key scientific question:
    "Does hierarchical calibration improve over offset-only baseline
    under the same governance thresholds?"

Usage:
    python vcapture_calibration_comparison.py \
        --baseline raw_hardware/vcapture_ledger_report.json \
        --hierarchical raw_hardware/hierarchical_ledger_report.json \
        --output raw_hardware/calibration_comparison.json
"""

import argparse
import json
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import numpy as np
from scipy import stats


# =============================================================================
# COMPARISON METRICS
# =============================================================================

@dataclass
class MetricComparison:
    """Comparison of a single metric between two calibration models."""
    metric_name: str
    baseline_value: float
    hierarchical_value: float
    delta: float  # hierarchical - baseline
    percent_improvement: float  # (delta / baseline) * 100
    effect_size: float  # Cohen's d
    p_value: float
    is_significant: bool  # p < 0.05
    is_improvement: bool  # delta in desired direction
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class GateComparison:
    """Comparison of gate status between two models."""
    gate_name: str
    baseline_status: str  # pass, warning, fail
    hierarchical_status: str
    baseline_value: float
    hierarchical_value: float
    status_change: str  # "improved", "degraded", "unchanged"
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CalibrationComparison:
    """Complete comparison between baseline and hierarchical calibration."""
    # Overall assessment
    baseline_state: str
    hierarchical_state: str
    baseline_eligible: bool
    hierarchical_eligible: bool
    promotion_recommendation: str  # "promote", "hold", "reject"
    
    # Metric comparisons
    residual_comparison: MetricComparison
    ss_comparison: MetricComparison
    portability_comparison: MetricComparison
    stability_comparison: MetricComparison
    r2_comparison: MetricComparison
    
    # Gate comparisons
    gate_comparisons: List[GateComparison]
    
    # Summary statistics
    n_metrics_improved: int
    n_metrics_degraded: int
    n_metrics_unchanged: int
    n_gates_improved: int
    n_gates_degraded: int
    
    # Statistical summary
    mean_effect_size: float
    significant_improvements: int
    significant_degradations: int
    
    # Recommendations
    blocking_issues: List[str]
    recommendations: List[str]
    
    # Metadata
    compared_at: str
    baseline_path: str
    hierarchical_path: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "baseline_state": self.baseline_state,
            "hierarchical_state": self.hierarchical_state,
            "baseline_eligible": self.baseline_eligible,
            "hierarchical_eligible": self.hierarchical_eligible,
            "promotion_recommendation": self.promotion_recommendation,
            "metrics": {
                "residual": self.residual_comparison.to_dict(),
                "signal_to_separation": self.ss_comparison.to_dict(),
                "portability": self.portability_comparison.to_dict(),
                "stability": self.stability_comparison.to_dict(),
                "r_squared": self.r2_comparison.to_dict(),
            },
            "gates": [g.to_dict() for g in self.gate_comparisons],
            "summary": {
                "n_metrics_improved": self.n_metrics_improved,
                "n_metrics_degraded": self.n_metrics_degraded,
                "n_metrics_unchanged": self.n_metrics_unchanged,
                "n_gates_improved": self.n_gates_improved,
                "n_gates_degraded": self.n_gates_degraded,
                "mean_effect_size": self.mean_effect_size,
                "significant_improvements": self.significant_improvements,
                "significant_degradations": self.significant_degradations,
            },
            "blocking_issues": self.blocking_issues,
            "recommendations": self.recommendations,
            "compared_at": self.compared_at,
            "baseline_path": self.baseline_path,
            "hierarchical_path": self.hierarchical_path,
        }


# =============================================================================
# COMPARISON ENGINE
# =============================================================================

class CalibrationComparisonEngine:
    """
    Compare calibration models under the same governance gates.
    
    This answers the key scientific question:
        "Does the new model improve residual spread, increase S/S,
        and preserve ranking portability enough to move from
        development to candidate?"
    """
    
    def __init__(self, alpha: float = 0.05):
        self.alpha = alpha
    
    def compare_calibrations(self,
                              baseline_path: Path,
                              hierarchical_path: Path) -> CalibrationComparison:
        """
        Compare baseline and hierarchical calibration under same gates.
        
        Args:
            baseline_path: Path to baseline VCapture ledger
            hierarchical_path: Path to hierarchical VCapture ledger
            
        Returns:
            CalibrationComparison with full analysis
        """
        # Load ledgers
        with open(baseline_path, 'r', encoding='utf-8') as f:
            baseline = json.load(f)
        
        with open(hierarchical_path, 'r', encoding='utf-8') as f:
            hierarchical = json.load(f)
        
        # Extract metrics
        baseline_metrics = self._extract_metrics(baseline)
        hierarchical_metrics = self._extract_metrics(hierarchical)
        
        # Compare metrics
        residual_comp = self._compare_metric(
            "residual_std",
            baseline_metrics['residual_std'],
            hierarchical_metrics['residual_std'],
            lower_is_better=True,
            baseline_samples=baseline_metrics.get('residual_samples', []),
            hierarchical_samples=hierarchical_metrics.get('residual_samples', []),
        )
        
        ss_comp = self._compare_metric(
            "signal_to_separation",
            baseline_metrics['ss_ratio'],
            hierarchical_metrics['ss_ratio'],
            lower_is_better=False,
            baseline_samples=baseline_metrics.get('ss_samples', []),
            hierarchical_samples=hierarchical_metrics.get('ss_samples', []),
        )
        
        portability_comp = self._compare_metric(
            "portability_score",
            baseline_metrics['portability_score'],
            hierarchical_metrics['portability_score'],
            lower_is_better=False,
            baseline_samples=baseline_metrics.get('portability_samples', []),
            hierarchical_samples=hierarchical_metrics.get('portability_samples', []),
        )
        
        stability_comp = self._compare_metric(
            "stability",
            baseline_metrics['stability'],
            hierarchical_metrics['stability'],
            lower_is_better=True,
            baseline_samples=baseline_metrics.get('stability_samples', []),
            hierarchical_samples=hierarchical_metrics.get('stability_samples', []),
        )
        
        r2_comp = self._compare_metric(
            "r_squared",
            baseline_metrics['r_squared'],
            hierarchical_metrics['r_squared'],
            lower_is_better=False,
            baseline_samples=baseline_metrics.get('r2_samples', []),
            hierarchical_samples=hierarchical_metrics.get('r2_samples', []),
        )
        
        # Compare gates
        gate_comparisons = self._compare_gates(baseline, hierarchical)
        
        # Determine states
        baseline_state, baseline_eligible = self._determine_state(baseline)
        hierarchical_state, hierarchical_eligible = self._determine_state(hierarchical)
        
        # Count improvements/degradations
        metric_comps = [residual_comp, ss_comp, portability_comp, stability_comp, r2_comp]
        
        n_improved = sum(1 for m in metric_comps if m.is_improvement)
        n_degraded = sum(1 for m in metric_comps if not m.is_improvement and abs(m.delta) > 0.001)
        n_unchanged = len(metric_comps) - n_improved - n_degraded
        
        n_gates_improved = sum(1 for g in gate_comparisons if g.status_change == "improved")
        n_gates_degraded = sum(1 for g in gate_comparisons if g.status_change == "degraded")
        
        # Statistical summary
        effect_sizes = [m.effect_size for m in metric_comps if abs(m.effect_size) < 10]
        mean_effect_size = float(np.mean(effect_sizes)) if effect_sizes else 0.0
        
        sig_improvements = sum(1 for m in metric_comps if m.is_significant and m.is_improvement)
        sig_degradations = sum(1 for m in metric_comps if m.is_significant and not m.is_improvement)
        
        # Determine promotion recommendation
        promotion_rec = self._determine_promotion(
            n_improved, n_degraded, n_gates_improved, n_gates_degraded,
            sig_improvements, sig_degradations, hierarchical_eligible
        )
        
        # Generate blocking issues and recommendations
        blocking_issues = self._identify_blocking_issues(
            gate_comparisons, metric_comps
        )
        recommendations = self._generate_recommendations(
            metric_comps, gate_comparisons, promotion_rec
        )
        
        return CalibrationComparison(
            baseline_state=baseline_state,
            hierarchical_state=hierarchical_state,
            baseline_eligible=baseline_eligible,
            hierarchical_eligible=hierarchical_eligible,
            promotion_recommendation=promotion_rec,
            residual_comparison=residual_comp,
            ss_comparison=ss_comp,
            portability_comparison=portability_comp,
            stability_comparison=stability_comp,
            r2_comparison=r2_comp,
            gate_comparisons=gate_comparisons,
            n_metrics_improved=n_improved,
            n_metrics_degraded=n_degraded,
            n_metrics_unchanged=n_unchanged,
            n_gates_improved=n_gates_improved,
            n_gates_degraded=n_gates_degraded,
            mean_effect_size=mean_effect_size,
            significant_improvements=sig_improvements,
            significant_degradations=sig_degradations,
            blocking_issues=blocking_issues,
            recommendations=recommendations,
            compared_at=datetime.now().isoformat(),
            baseline_path=str(baseline_path),
            hierarchical_path=str(hierarchical_path),
        )
    
    def _extract_metrics(self, ledger: Dict) -> Dict[str, float]:
        """Extract key metrics from ledger."""
        variance = ledger.get('variance_structure', {})
        transfer = ledger.get('transferability', [])
        mixed = ledger.get('mixed_effects', {})
        
        # Residual
        residual_std = variance.get('residual_std', 1.0)
        
        # Signal-to-separation
        summaries = variance.get('promoter_backend_summaries', [])
        ss_values = [s.get('signal_to_separation', 0) for s in summaries]
        ss_ratio = float(np.mean(ss_values)) if ss_values else 0.0
        
        # Portability
        if transfer:
            portability_score = transfer[0].get('portability_score', 0)
        else:
            portability_score = 0.0
        
        # Stability
        within_var = variance.get('within_promoter_variance', {})
        within_stds = [np.sqrt(v) for v in within_var.values() if v > 0]
        stability = float(np.mean(within_stds)) if within_stds else 1.0
        
        # R-squared
        model_stats = mixed.get('model_statistics', {})
        r_squared = model_stats.get('r_squared', 0)
        
        return {
            'residual_std': residual_std,
            'ss_ratio': ss_ratio,
            'portability_score': portability_score,
            'stability': stability,
            'r_squared': r_squared,
        }
    
    def _compare_metric(self,
                        name: str,
                        baseline_value: float,
                        hierarchical_value: float,
                        lower_is_better: bool,
                        baseline_samples: List[float] = None,
                        hierarchical_samples: List[float] = None) -> MetricComparison:
        """Compare a single metric between models."""
        
        delta = hierarchical_value - baseline_value
        
        # Determine if improvement
        if lower_is_better:
            is_improvement = delta < 0
        else:
            is_improvement = delta > 0
        
        # Percent improvement
        if abs(baseline_value) > 1e-10:
            percent_improvement = (delta / abs(baseline_value)) * 100
            if lower_is_better:
                percent_improvement = -percent_improvement  # Flip for lower-is-better
        else:
            percent_improvement = 0.0
        
        # Effect size and significance
        if baseline_samples and hierarchical_samples:
            # Use actual samples for statistical test
            pooled_std = np.sqrt(
                (np.var(baseline_samples) + np.var(hierarchical_samples)) / 2
            )
            effect_size = delta / pooled_std if pooled_std > 1e-10 else 0.0
            
            # t-test
            t_stat, p_value = stats.ttest_ind(baseline_samples, hierarchical_samples)
            is_significant = p_value < self.alpha
        else:
            # Use approximate effect size
            effect_size = delta / max(abs(baseline_value), 0.01)
            p_value = 1.0  # No significance without samples
            is_significant = False
        
        return MetricComparison(
            metric_name=name,
            baseline_value=baseline_value,
            hierarchical_value=hierarchical_value,
            delta=delta,
            percent_improvement=percent_improvement,
            effect_size=effect_size,
            p_value=p_value,
            is_significant=is_significant,
            is_improvement=is_improvement,
        )
    
    def _compare_gates(self, baseline: Dict, hierarchical: Dict) -> List[GateComparison]:
        """Compare gate statuses between models."""
        comparisons = []
        
        # Extract gate values
        baseline_variance = baseline.get('variance_structure', {})
        hierarchical_variance = hierarchical.get('variance_structure', {})
        
        baseline_transfer = baseline.get('transferability', [])
        hierarchical_transfer = hierarchical.get('transferability', [])
        
        baseline_mixed = baseline.get('mixed_effects', {})
        hierarchical_mixed = hierarchical.get('mixed_effects', {})
        
        # Define gates to compare
        gates_to_compare = [
            ("residual_spread", 
             baseline_variance.get('residual_std', 1.0),
             hierarchical_variance.get('residual_std', 1.0),
             0.10, 0.15, False),  # pass, warning, lower_is_better
            ("signal_to_separation",
             np.mean([s.get('signal_to_separation', 0) for s in baseline_variance.get('promoter_backend_summaries', [])]) if baseline_variance.get('promoter_backend_summaries') else 0,
             np.mean([s.get('signal_to_separation', 0) for s in hierarchical_variance.get('promoter_backend_summaries', [])]) if hierarchical_variance.get('promoter_backend_summaries') else 0,
             2.0, 1.5, True),  # pass, warning, higher_is_better
            ("portability",
             baseline_transfer[0].get('portability_score', 0) if baseline_transfer else 0,
             hierarchical_transfer[0].get('portability_score', 0) if hierarchical_transfer else 0,
             0.85, 0.75, True),
            ("stability",
             np.mean([np.sqrt(v) for v in baseline_variance.get('within_promoter_variance', {}).values() if v > 0]) if baseline_variance.get('within_promoter_variance') else 1.0,
             np.mean([np.sqrt(v) for v in hierarchical_variance.get('within_promoter_variance', {}).values() if v > 0]) if hierarchical_variance.get('within_promoter_variance') else 1.0,
             0.01, 0.02, False),
            ("model_fit",
             baseline_mixed.get('model_statistics', {}).get('r_squared', 0),
             hierarchical_mixed.get('model_statistics', {}).get('r_squared', 0),
             0.70, 0.60, True),
        ]
        
        for gate_name, baseline_val, hierarchical_val, pass_thresh, warn_thresh, higher_is_better in gates_to_compare:
            # Determine status for each
            baseline_status = self._get_gate_status(baseline_val, pass_thresh, warn_thresh, higher_is_better)
            hierarchical_status = self._get_gate_status(hierarchical_val, pass_thresh, warn_thresh, higher_is_better)
            
            # Determine change
            status_order = {"fail": 0, "warning": 1, "pass": 2}
            if status_order[hierarchical_status] > status_order[baseline_status]:
                status_change = "improved"
            elif status_order[hierarchical_status] < status_order[baseline_status]:
                status_change = "degraded"
            else:
                status_change = "unchanged"
            
            comparisons.append(GateComparison(
                gate_name=gate_name,
                baseline_status=baseline_status,
                hierarchical_status=hierarchical_status,
                baseline_value=baseline_val,
                hierarchical_value=hierarchical_val,
                status_change=status_change,
            ))
        
        return comparisons
    
    def _get_gate_status(self, value: float, pass_thresh: float, 
                         warn_thresh: float, higher_is_better: bool) -> str:
        """Determine gate status from value."""
        if higher_is_better:
            if value >= pass_thresh:
                return "pass"
            elif value >= warn_thresh:
                return "warning"
            else:
                return "fail"
        else:
            if value <= pass_thresh:
                return "pass"
            elif value <= warn_thresh:
                return "warning"
            else:
                return "fail"
    
    def _determine_state(self, ledger: Dict) -> Tuple[str, bool]:
        """Determine calibration state from ledger."""
        # Simplified state determination
        # In practice, would use full lifecycle governance
        variance = ledger.get('variance_structure', {})
        transfer = ledger.get('transferability', [])
        mixed = ledger.get('mixed_effects', {})
        
        # Check key metrics
        residual_std = variance.get('residual_std', 1.0)
        
        summaries = variance.get('promoter_backend_summaries', [])
        ss_values = [s.get('signal_to_separation', 0) for s in summaries]
        mean_ss = float(np.mean(ss_values)) if ss_values else 0
        
        if transfer:
            portability = transfer[0].get('portability_score', 0)
        else:
            portability = 0
        
        r_squared = mixed.get('model_statistics', {}).get('r_squared', 0)
        
        # Determine state
        if (residual_std <= 0.10 and mean_ss >= 2.0 and 
            portability >= 0.85 and r_squared >= 0.70):
            return "production", True
        elif (residual_std <= 0.15 and mean_ss >= 1.5 and 
              portability >= 0.75 and r_squared >= 0.60):
            return "staging", True
        elif (residual_std <= 0.20 and mean_ss >= 1.0 and 
              portability >= 0.60 and r_squared >= 0.50):
            return "candidate", True
        else:
            return "development", False
    
    def _determine_promotion(self, n_improved: int, n_degraded: int,
                             n_gates_improved: int, n_gates_degraded: int,
                             sig_improvements: int, sig_degradations: int,
                             eligible: bool) -> str:
        """Determine promotion recommendation."""
        
        # Strong promotion: significant improvements, no degradations
        if sig_improvements >= 2 and sig_degradations == 0 and eligible:
            return "promote"
        
        # Conditional promotion: more improvements than degradations
        if n_improved > n_degraded and n_gates_improved >= n_gates_degraded and eligible:
            return "promote"
        
        # Hold: mixed results
        if n_improved > 0 and n_degraded > 0:
            return "hold"
        
        # Reject: more degradations than improvements
        if n_degraded > n_improved or n_gates_degraded > n_gates_improved:
            return "reject"
        
        # Default: hold
        return "hold"
    
    def _identify_blocking_issues(self, gate_comps: List[GateComparison],
                                   metric_comps: List[MetricComparison]) -> List[str]:
        """Identify blocking issues from comparison."""
        issues = []
        
        # Check for degraded gates
        for gate in gate_comps:
            if gate.status_change == "degraded":
                issues.append(
                    f"{gate.gate_name} degraded: {gate.baseline_status} → {gate.hierarchical_status}"
                )
        
        # Check for significant degradations
        for metric in metric_comps:
            if metric.is_significant and not metric.is_improvement:
                issues.append(
                    f"{metric.metric_name} significantly degraded (p={metric.p_value:.4f})"
                )
        
        return issues
    
    def _generate_recommendations(self, metric_comps: List[MetricComparison],
                                    gate_comps: List[GateComparison],
                                    promotion: str) -> List[str]:
        """Generate recommendations based on comparison."""
        recommendations = []
        
        if promotion == "promote":
            recommendations.append(
                "Hierarchical calibration shows improvement over baseline"
            )
            recommendations.append(
                "Proceed with promotion to next state"
            )
        
        elif promotion == "hold":
            recommendations.append(
                "Mixed results: some metrics improved, others degraded"
            )
            recommendations.append(
                "Investigate specific degradations before promotion"
            )
            
            # Specific recommendations
            for metric in metric_comps:
                if not metric.is_improvement and abs(metric.delta) > 0.01:
                    recommendations.append(
                        f"Address {metric.metric_name}: delta={metric.delta:.4f}"
                    )
        
        elif promotion == "reject":
            recommendations.append(
                "Hierarchical calibration shows degradation from baseline"
            )
            recommendations.append(
                "Do not promote; investigate root causes"
            )
        
        # Add improvement highlights
        for metric in metric_comps:
            if metric.is_improvement and abs(metric.percent_improvement) > 5:
                recommendations.append(
                    f"✓ {metric.metric_name} improved by {abs(metric.percent_improvement):.1f}%"
                )
        
        return recommendations


# =============================================================================
# REPORT GENERATOR
# =============================================================================

def generate_comparison_report(comparison: CalibrationComparison, output_path: Path):
    """Generate human-readable comparison report."""
    
    report_lines = [
        "=" * 70,
        "VCapture Calibration Comparison Report",
        "=" * 70,
        "",
        f"Compared at: {comparison.compared_at}",
        f"Baseline: {comparison.baseline_path}",
        f"Hierarchical: {comparison.hierarchical_path}",
        "",
        "=" * 70,
        "STATE COMPARISON",
        "=" * 70,
        "",
        f"  Baseline State: {comparison.baseline_state.upper()}",
        f"  Hierarchical State: {comparison.hierarchical_state.upper()}",
        f"  Baseline Eligible: {'YES' if comparison.baseline_eligible else 'NO'}",
        f"  Hierarchical Eligible: {'YES' if comparison.hierarchical_eligible else 'NO'}",
        "",
        f"  PROMOTION RECOMMENDATION: {comparison.promotion_recommendation.upper()}",
        "",
        "=" * 70,
        "METRIC COMPARISONS",
        "=" * 70,
        "",
    ]
    
    metrics = [
        ("Residual Spread", comparison.residual_comparison, False),
        ("Signal-to-Separation", comparison.ss_comparison, True),
        ("Portability", comparison.portability_comparison, True),
        ("Stability", comparison.stability_comparison, False),
        ("R-Squared", comparison.r2_comparison, True),
    ]
    
    for name, comp, higher_is_better in metrics:
        direction = "↑" if (comp.delta > 0) == higher_is_better else "↓"
        sig_marker = "*" if comp.is_significant else ""
        
        report_lines.extend([
            f"  {name}:",
            f"    Baseline: {comp.baseline_value:.4f}",
            f"    Hierarchical: {comp.hierarchical_value:.4f}",
            f"    Delta: {comp.delta:+.4f} {direction}{sig_marker}",
            f"    Improvement: {comp.percent_improvement:+.1f}%",
            f"    Effect Size: {comp.effect_size:.4f}",
            f"    p-value: {comp.p_value:.4f}",
            "",
        ])
    
    # Gate comparisons
    report_lines.extend([
        "=" * 70,
        "GATE STATUS CHANGES",
        "=" * 70,
        "",
    ])
    
    for gate in comparison.gate_comparisons:
        change_icon = {
            "improved": "↑",
            "degraded": "↓",
            "unchanged": "→",
        }[gate.status_change]
        
        report_lines.extend([
            f"  {gate.gate_name}:",
            f"    Baseline: {gate.baseline_status.upper()}",
            f"    Hierarchical: {gate.hierarchical_status.upper()}",
            f"    Change: {change_icon} {gate.status_change.upper()}",
            "",
        ])
    
    # Summary
    report_lines.extend([
        "=" * 70,
        "SUMMARY",
        "=" * 70,
        "",
        f"  Metrics Improved: {comparison.n_metrics_improved}",
        f"  Metrics Degraded: {comparison.n_metrics_degraded}",
        f"  Metrics Unchanged: {comparison.n_metrics_unchanged}",
        "",
        f"  Gates Improved: {comparison.n_gates_improved}",
        f"  Gates Degraded: {comparison.n_gates_degraded}",
        "",
        f"  Mean Effect Size: {comparison.mean_effect_size:.4f}",
        f"  Significant Improvements: {comparison.significant_improvements}",
        f"  Significant Degradations: {comparison.significant_degradations}",
        "",
    ])
    
    if comparison.blocking_issues:
        report_lines.extend([
            "=" * 70,
            "BLOCKING ISSUES",
            "=" * 70,
            "",
        ])
        for issue in comparison.blocking_issues:
            report_lines.append(f"  ✗ {issue}")
        report_lines.append("")
    
    if comparison.recommendations:
        report_lines.extend([
            "=" * 70,
            "RECOMMENDATIONS",
            "=" * 70,
            "",
        ])
        for rec in comparison.recommendations:
            report_lines.append(f"  → {rec}")
        report_lines.append("")
    
    report_text = "\n".join(report_lines)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report_text)
    
    return report_text


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="VCapture Calibration Comparison")
    parser.add_argument("--baseline", type=str, required=True, help="Path to baseline ledger JSON")
    parser.add_argument("--hierarchical", type=str, required=True, help="Path to hierarchical ledger JSON")
    parser.add_argument("--output", type=str, default="calibration_comparison.json", help="Output comparison JSON")
    parser.add_argument("--report", type=str, default="calibration_comparison_report.txt", help="Human-readable report")
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("VCapture Calibration Comparison")
    print("=" * 70)
    
    print(f"\nBaseline: {args.baseline}")
    print(f"Hierarchical: {args.hierarchical}")
    
    # Initialize comparison engine
    engine = CalibrationComparisonEngine()
    
    # Run comparison
    baseline_path = Path(args.baseline)
    hierarchical_path = Path(args.hierarchical)
    
    comparison = engine.compare_calibrations(baseline_path, hierarchical_path)
    
    # Save JSON comparison
    output_path = Path(args.output)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(comparison.to_dict(), f, indent=2)
    print(f"\nComparison saved to: {output_path}")
    
    # Generate human-readable report
    report_path = Path(args.report)
    report_text = generate_comparison_report(comparison, report_path)
    print(f"Report saved to: {report_path}")
    
    # Print summary
    print("\n" + "=" * 70)
    print("COMPARISON SUMMARY")
    print("=" * 70)
    print(f"\n  Baseline State: {comparison.baseline_state.upper()}")
    print(f"  Hierarchical State: {comparison.hierarchical_state.upper()}")
    print(f"\n  Promotion Recommendation: {comparison.promotion_recommendation.upper()}")
    print(f"\n  Metrics: {comparison.n_metrics_improved} improved, {comparison.n_metrics_degraded} degraded")
    print(f"  Gates: {comparison.n_gates_improved} improved, {comparison.n_gates_degraded} degraded")
    print(f"  Significant Improvements: {comparison.significant_improvements}")
    
    if comparison.blocking_issues:
        print(f"\n  Blocking Issues: {len(comparison.blocking_issues)}")
        for issue in comparison.blocking_issues[:3]:
            print(f"    • {issue}")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()