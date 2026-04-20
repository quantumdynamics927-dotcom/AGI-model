"""
Statistical Analysis for Response Path Audit

Implements proper significance testing for the controlled ablation study.
Uses scipy.stats for t-tests, ANOVA, and effect size calculations.
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

# Statistical analysis requires scipy
try:
    from scipy import stats
    from scipy.stats import mannwhitneyu, wilcoxon, friedmanchisquare
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    logger.warning("scipy not available, statistical tests will be limited")


@dataclass
class StatisticalResult:
    """Result of a statistical test"""
    test_name: str
    statistic: float
    p_value: float
    effect_size: float
    confidence_interval: Tuple[float, float]
    interpretation: str
    significant: bool


class ResponseAuditStatistics:
    """Statistical analysis for response path audit results"""
    
    def __init__(self, results_dir: str = "response_audit_results"):
        """
        Initialize statistics analyzer.
        
        Args:
            results_dir: Directory containing audit results
        """
        self.results_dir = Path(results_dir)
        self.results = self._load_results()
        self.traces = self._load_traces()
        
    def _load_results(self) -> Dict[str, List[Dict]]:
        """Load audit results from file"""
        results_file = self.results_dir / "response_audit_results.json"
        
        if not results_file.exists():
            raise FileNotFoundError(f"Results file not found: {results_file}")
            
        with open(results_file) as f:
            return json.load(f)
            
    def _load_traces(self) -> Dict[str, List[Dict]]:
        """Load route traces from file"""
        traces_file = self.results_dir / "response_traces.json"
        
        if not traces_file.exists():
            raise FileNotFoundError(f"Traces file not found: {traces_file}")
            
        with open(traces_file) as f:
            return json.load(f)
            
    def extract_metric(self, metric_name: str, config_id: str) -> List[float]:
        """
        Extract a specific metric for a configuration.
        
        Args:
            metric_name: Name of the metric (e.g., 'judge_score')
            config_id: Configuration ID (C0, C1, C2)
            
        Returns:
            List of metric values
        """
        if config_id not in self.results:
            raise ValueError(f"Config {config_id} not found in results")
            
        values = []
        for result in self.results[config_id]:
            if metric_name in result['evaluation_metrics']:
                value = result['evaluation_metrics'][metric_name]
                if value is not None:
                    # Convert boolean to float for statistical tests
                    if isinstance(value, bool):
                        value = float(value)
                    values.append(value)
                    
        return values
        
    def paired_t_test(self, metric_name: str, config1: str, config2: str) -> StatisticalResult:
        """
        Perform paired t-test between two configurations.
        
        This is appropriate when the same prompts are tested under both conditions.
        
        Args:
            metric_name: Name of the metric to compare
            config1: First configuration ID
            config2: Second configuration ID
            
        Returns:
            StatisticalResult with test results
        """
        if not SCIPY_AVAILABLE:
            return self._fallback_comparison(metric_name, config1, config2)
            
        # Get paired samples
        values1 = self.extract_metric(metric_name, config1)
        values2 = self.extract_metric(metric_name, config2)
        
        # Ensure same length (paired samples)
        min_len = min(len(values1), len(values2))
        values1 = values1[:min_len]
        values2 = values2[:min_len]
        
        if min_len < 2:
            return StatisticalResult(
                test_name="paired_t_test",
                statistic=0.0,
                p_value=1.0,
                effect_size=0.0,
                confidence_interval=(0.0, 0.0),
                interpretation="Insufficient data for test",
                significant=False
            )
            
        # Perform paired t-test
        t_stat, p_value = stats.ttest_rel(values1, values2)
        
        # Calculate effect size (Cohen's d)
        mean_diff = np.mean(values1) - np.mean(values2)
        pooled_std = np.sqrt((np.var(values1) + np.var(values2)) / 2)
        cohens_d = mean_diff / pooled_std if pooled_std > 0 else 0
        
        # Calculate confidence interval
        diff = np.array(values1) - np.array(values2)
        se = stats.sem(diff)
        ci = stats.t.interval(0.95, len(diff) - 1, loc=np.mean(diff), scale=se)
        
        # Interpret result
        if p_value < 0.05:
            if cohens_d > 0.8:
                interpretation = f"Large significant difference (d={cohens_d:.2f})"
            elif cohens_d > 0.5:
                interpretation = f"Medium significant difference (d={cohens_d:.2f})"
            else:
                interpretation = f"Small significant difference (d={cohens_d:.2f})"
        else:
            interpretation = f"No significant difference (p={p_value:.4f})"
            
        return StatisticalResult(
            test_name="paired_t_test",
            statistic=t_stat,
            p_value=p_value,
            effect_size=cohens_d,
            confidence_interval=ci,
            interpretation=interpretation,
            significant=p_value < 0.05
        )
        
    def wilcoxon_test(self, metric_name: str, config1: str, config2: str) -> StatisticalResult:
        """
        Perform Wilcoxon signed-rank test (non-parametric alternative to paired t-test).
        
        Args:
            metric_name: Name of the metric to compare
            config1: First configuration ID
            config2: Second configuration ID
            
        Returns:
            StatisticalResult with test results
        """
        if not SCIPY_AVAILABLE:
            return self._fallback_comparison(metric_name, config1, config2)
            
        values1 = self.extract_metric(metric_name, config1)
        values2 = self.extract_metric(metric_name, config2)
        
        min_len = min(len(values1), len(values2))
        values1 = values1[:min_len]
        values2 = values2[:min_len]
        
        if min_len < 2:
            return StatisticalResult(
                test_name="wilcoxon",
                statistic=0.0,
                p_value=1.0,
                effect_size=0.0,
                confidence_interval=(0.0, 0.0),
                interpretation="Insufficient data for test",
                significant=False
            )
            
        # Perform Wilcoxon test
        stat, p_value = wilcoxon(values1, values2)
        
        # Calculate effect size (rank-biserial correlation)
        n = len(values1)
        effect_size = stat / (n * (n + 1) / 2) if n > 0 else 0
        
        interpretation = f"Wilcoxon statistic: {stat:.2f}, p={p_value:.4f}"
        
        return StatisticalResult(
            test_name="wilcoxon",
            statistic=stat,
            p_value=p_value,
            effect_size=effect_size,
            confidence_interval=(0.0, 0.0),
            interpretation=interpretation,
            significant=p_value < 0.05
        )
        
    def anova_test(self, metric_name: str) -> StatisticalResult:
        """
        Perform one-way ANOVA across all three configurations.
        
        Args:
            metric_name: Name of the metric to compare
            
        Returns:
            StatisticalResult with test results
        """
        if not SCIPY_AVAILABLE:
            return StatisticalResult(
                test_name="anova",
                statistic=0.0,
                p_value=1.0,
                effect_size=0.0,
                confidence_interval=(0.0, 0.0),
                interpretation="scipy not available",
                significant=False
            )
            
        values_c0 = self.extract_metric(metric_name, 'C0')
        values_c1 = self.extract_metric(metric_name, 'C1')
        values_c2 = self.extract_metric(metric_name, 'C2')
        
        if min(len(values_c0), len(values_c1), len(values_c2)) < 2:
            return StatisticalResult(
                test_name="anova",
                statistic=0.0,
                p_value=1.0,
                effect_size=0.0,
                confidence_interval=(0.0, 0.0),
                interpretation="Insufficient data for test",
                significant=False
            )
            
        # Perform ANOVA
        f_stat, p_value = stats.f_oneway(values_c0, values_c1, values_c2)
        
        # Calculate effect size (eta-squared)
        all_values = values_c0 + values_c1 + values_c2
        grand_mean = np.mean(all_values)
        
        ss_between = (len(values_c0) * (np.mean(values_c0) - grand_mean)**2 +
                     len(values_c1) * (np.mean(values_c1) - grand_mean)**2 +
                     len(values_c2) * (np.mean(values_c2) - grand_mean)**2)
        
        ss_total = sum((v - grand_mean)**2 for v in all_values)
        
        eta_squared = ss_between / ss_total if ss_total > 0 else 0
        
        interpretation = f"F={f_stat:.2f}, p={p_value:.4f}, eta_sq={eta_squared:.3f}"
        
        return StatisticalResult(
            test_name="anova",
            statistic=f_stat,
            p_value=p_value,
            effect_size=eta_squared,
            confidence_interval=(0.0, 0.0),
            interpretation=interpretation,
            significant=p_value < 0.05
        )
        
    def friedman_test(self, metric_name: str) -> StatisticalResult:
        """
        Perform Friedman test (non-parametric alternative to ANOVA for repeated measures).
        
        Args:
            metric_name: Name of the metric to compare
            
        Returns:
            StatisticalResult with test results
        """
        if not SCIPY_AVAILABLE:
            return StatisticalResult(
                test_name="friedman",
                statistic=0.0,
                p_value=1.0,
                effect_size=0.0,
                confidence_interval=(0.0, 0.0),
                interpretation="scipy not available",
                significant=False
            )
            
        values_c0 = self.extract_metric(metric_name, 'C0')
        values_c1 = self.extract_metric(metric_name, 'C1')
        values_c2 = self.extract_metric(metric_name, 'C2')
        
        min_len = min(len(values_c0), len(values_c1), len(values_c2))
        
        if min_len < 2:
            return StatisticalResult(
                test_name="friedman",
                statistic=0.0,
                p_value=1.0,
                effect_size=0.0,
                confidence_interval=(0.0, 0.0),
                interpretation="Insufficient data for test",
                significant=False
            )
            
        # Perform Friedman test
        stat, p_value = friedmanchisquare(
            values_c0[:min_len],
            values_c1[:min_len],
            values_c2[:min_len]
        )
        
        # Calculate effect size (Kendall's W)
        n = min_len
        k = 3
        effect_size = stat / (n * (k - 1))
        
        interpretation = f"Friedman χ²={stat:.2f}, p={p_value:.4f}, W={effect_size:.3f}"
        
        return StatisticalResult(
            test_name="friedman",
            statistic=stat,
            p_value=p_value,
            effect_size=effect_size,
            confidence_interval=(0.0, 0.0),
            interpretation=interpretation,
            significant=p_value < 0.05
        )
        
    def _fallback_comparison(self, metric_name: str, config1: str, config2: str) -> StatisticalResult:
        """Fallback comparison when scipy is not available"""
        values1 = self.extract_metric(metric_name, config1)
        values2 = self.extract_metric(metric_name, config2)
        
        mean1 = np.mean(values1) if values1 else 0
        mean2 = np.mean(values2) if values2 else 0
        
        diff = mean1 - mean2
        
        return StatisticalResult(
            test_name="mean_comparison",
            statistic=diff,
            p_value=1.0,
            effect_size=abs(diff),
            confidence_interval=(diff - 0.1, diff + 0.1),
            interpretation=f"Mean difference: {diff:.4f} (scipy not available for significance test)",
            significant=False
        )
        
    def analyze_by_prompt_class(self, metric_name: str) -> Dict[str, Dict[str, Any]]:
        """
        Analyze metric differences by prompt class.
        
        Args:
            metric_name: Name of the metric to analyze
            
        Returns:
            Dictionary with analysis results by prompt class
        """
        results = {}
        
        # Load prompts to get class information
        prompts_file = Path("response_audit_prompts.json")
        if not prompts_file.exists():
            return results
            
        with open(prompts_file) as f:
            prompts_data = json.load(f)
            
        prompt_classes = {}
        for p in prompts_data['prompts']:
            prompt_classes[p['prompt_id']] = p['prompt_class']
            
        # Group results by class
        for config_id in ['C0', 'C1', 'C2']:
            if config_id not in self.results:
                continue
                
            results[config_id] = {}
            
            for result in self.results[config_id]:
                prompt_id = result['prompt_id']
                if prompt_id not in prompt_classes:
                    continue
                    
                pclass = prompt_classes[prompt_id]
                if pclass not in results[config_id]:
                    results[config_id][pclass] = []
                    
                if metric_name in result['evaluation_metrics']:
                    value = result['evaluation_metrics'][metric_name]
                    if value is not None:
                        results[config_id][pclass].append(value)
                        
        # Calculate statistics by class
        analysis = {}
        for pclass in ['ambiguous', 'tool_use', 'fault_tolerance', 'memory_governance', 'factual_control']:
            analysis[pclass] = {}
            
            for config_id in ['C0', 'C1', 'C2']:
                if config_id in results and pclass in results[config_id]:
                    values = results[config_id][pclass]
                    if values:
                        analysis[pclass][config_id] = {
                            'mean': np.mean(values),
                            'std': np.std(values),
                            'count': len(values)
                        }
                        
        return analysis
        
    def generate_statistical_report(self) -> str:
        """
        Generate comprehensive statistical report.
        
        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 80)
        report.append("STATISTICAL ANALYSIS REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Primary metrics
        primary_metrics = ['judge_score', 'task_success', 'confidence_alignment']
        
        for metric in primary_metrics:
            report.append(f"\n{metric.upper()}")
            report.append("-" * 40)
            
            # ANOVA
            anova_result = self.anova_test(metric)
            report.append(f"\nANOVA: {anova_result.interpretation}")
            report.append(f"  Significant: {anova_result.significant}")
            
            # Paired comparisons
            report.append("\nPaired Comparisons:")
            
            # C1 vs C0
            result = self.paired_t_test(metric, 'C1', 'C0')
            report.append(f"  C1 vs C0: {result.interpretation}")
            report.append(f"    Effect size (Cohen's d): {result.effect_size:.3f}")
            report.append(f"    95% CI: [{result.confidence_interval[0]:.4f}, {result.confidence_interval[1]:.4f}]")
            
            # C2 vs C1
            result = self.paired_t_test(metric, 'C2', 'C1')
            report.append(f"  C2 vs C1: {result.interpretation}")
            report.append(f"    Effect size (Cohen's d): {result.effect_size:.3f}")
            report.append(f"    95% CI: [{result.confidence_interval[0]:.4f}, {result.confidence_interval[1]:.4f}]")
            
            # C2 vs C0
            result = self.paired_t_test(metric, 'C2', 'C0')
            report.append(f"  C2 vs C0: {result.interpretation}")
            report.append(f"    Effect size (Cohen's d): {result.effect_size:.3f}")
            report.append(f"    95% CI: [{result.confidence_interval[0]:.4f}, {result.confidence_interval[1]:.4f}]")
            
        # Analysis by prompt class
        report.append("\n\nANALYSIS BY PROMPT CLASS")
        report.append("-" * 40)
        
        class_analysis = self.analyze_by_prompt_class('judge_score')
        
        for pclass in ['ambiguous', 'tool_use', 'fault_tolerance', 'memory_governance', 'factual_control']:
            if pclass in class_analysis:
                report.append(f"\n{pclass.upper()}:")
                for config_id in ['C0', 'C1', 'C2']:
                    if config_id in class_analysis[pclass]:
                        stats = class_analysis[pclass][config_id]
                        report.append(f"  {config_id}: {stats['mean']:.4f} ± {stats['std']:.4f} (n={stats['count']})")
                        
        # Conclusions
        report.append("\n\nCONCLUSIONS")
        report.append("-" * 40)
        
        # Check for quantum benefit
        c2_vs_c1 = self.paired_t_test('judge_score', 'C2', 'C1')
        c1_vs_c0 = self.paired_t_test('judge_score', 'C1', 'C0')
        
        if c2_vs_c1.significant and c2_vs_c1.effect_size > 0:
            report.append("\n[PASS] QUANTUM-ASSISTED ROUTING BENEFIT DETECTED")
            report.append(f"  C2 shows significant improvement over C1 (p={c2_vs_c1.p_value:.4f}, d={c2_vs_c1.effect_size:.2f})")
        else:
            report.append("\n[FAIL] NO QUANTUM-ASSISTED ROUTING BENEFIT DETECTED")
            report.append(f"  C2 does not significantly outperform C1 (p={c2_vs_c1.p_value:.4f})")
            
        if c1_vs_c0.significant and c1_vs_c0.effect_size > 0:
            report.append("\n[PASS] TESSERACT TOPOLOGY BENEFIT DETECTED")
            report.append(f"  C1 shows significant improvement over C0 (p={c1_vs_c0.p_value:.4f}, d={c1_vs_c0.effect_size:.2f})")
        else:
            report.append("\n[FAIL] NO TESSERACT TOPOLOGY BENEFIT DETECTED")
            report.append(f"  C1 does not significantly outperform C0 (p={c1_vs_c0.p_value:.4f})")
            
        report.append("\n" + "=" * 80)
        
        return "\n".join(report)


def main():
    """Run statistical analysis"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Statistical Analysis for Response Path Audit")
    parser.add_argument('--results-dir', type=str, default='response_audit_results',
                       help='Directory containing audit results')
    parser.add_argument('--output', type=str, default='statistical_report.txt',
                       help='Output file for statistical report')
    
    args = parser.parse_args()
    
    # Create analyzer
    analyzer = ResponseAuditStatistics(results_dir=args.results_dir)
    
    # Generate report
    report = analyzer.generate_statistical_report()
    
    # Print report
    print(report)
    
    # Save report
    output_file = Path(args.results_dir) / args.output
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
        
    print(f"\nReport saved to {output_file}")


if __name__ == "__main__":
    main()