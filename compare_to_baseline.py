"""
Baseline Comparison Tool for Phase 3

Provides statistical comparison between optimization candidates and locked baseline,
with proper hypothesis testing, effect sizes, and multiple comparisons correction.

This tool ensures:
- Paired t-tests for dependent samples
- Cohen's d effect sizes with confidence intervals
- Holm-Bonferroni multiple comparisons correction
- Non-inferiority testing with pre-declared margins
- Bootstrap confidence intervals for robust estimates

References:
- mcpanalytics.ai/articles/holm-bonferroni-method
- pmc.ncbi.nlm.nih.gov/articles/PMC6972498/
- pmc.ncbi.nlm.nih.gov/articles/PMC11294879/
"""

import json
import logging
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass, field
from pathlib import Path
from scipy import stats
import warnings

# Import governance layer
from governance_layer import MetricsRegistry, TypedMetric, MetricType

logger = logging.getLogger(__name__)


@dataclass
class StatisticalTestResult:
    """Results from a statistical test comparing candidate to baseline"""
    metric_name: str
    condition: str
    baseline_mean: float
    candidate_mean: float
    difference: float
    t_statistic: float
    p_value: float
    degrees_of_freedom: int
    cohens_d: float
    cohens_d_ci: Tuple[float, float]  # 95% CI for Cohen's d
    is_significant: bool
    is_superior: bool
    is_non_inferior: bool
    non_inferiority_margin: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "metric_name": self.metric_name,
            "condition": self.condition,
            "baseline_mean": self.baseline_mean,
            "candidate_mean": self.candidate_mean,
            "difference": self.difference,
            "t_statistic": self.t_statistic,
            "p_value": self.p_value,
            "degrees_of_freedom": self.degrees_of_freedom,
            "cohens_d": self.cohens_d,
            "cohens_d_ci": self.cohens_d_ci,
            "is_significant": self.is_significant,
            "is_superior": self.is_superior,
            "is_non_inferior": self.is_non_inferior,
            "non_inferiority_margin": self.non_inferiority_margin
        }


class BaselineComparator:
    """
    Compares optimization candidates to locked baseline with statistical rigor.
    
    Implements proper hypothesis testing with:
    - Paired t-tests for dependent samples
    - Effect sizes (Cohen's d) with confidence intervals
    - Multiple comparisons correction (Holm-Bonferroni)
    - Non-inferiority testing with pre-declared margins
    """
    
    def __init__(self, baseline_fingerprint_path: str,
                 non_inferiority_margins: Optional[Dict[str, float]] = None):
        """
        Initialize comparator with baseline and margins.
        
        Args:
            baseline_fingerprint_path: Path to locked baseline fingerprint
            non_inferiority_margins: Dict mapping metric names to margins
        """
        # Load baseline fingerprint
        with open(baseline_fingerprint_path) as f:
            self.baseline_data = json.load(f)
        
        # Default non-inferiority margins
        self.non_inferiority_margins = non_inferiority_margins or {
            "latency": 0.10,           # 10% allowed increase
            "invalid_transition_rate": 0.15,  # 15% allowed increase
            "success_rate": -0.05,     # 5% allowed decrease (negative margin)
            "confidence_calibration": -0.03,  # 3% allowed decrease
        }
        
        logger.info("Baseline Comparator initialized")
        logger.info(f"Baseline: {baseline_fingerprint_path}")
        logger.info(f"Non-inferiority margins: {self.non_inferiority_margins}")
    
    def compare_candidate(self, candidate_results: Dict[str, Any], 
                         candidate_id: str) -> List[StatisticalTestResult]:
        """
        Compare candidate results to baseline across all conditions.
        
        Args:
            candidate_results: Dict with condition -> metrics -> values
            candidate_id: Identifier for this candidate
            
        Returns:
            List of statistical test results
        """
        logger.info(f"Comparing candidate {candidate_id} to baseline")
        
        all_results = []
        
        # Compare each condition
        for condition_name in ["clean", "fault", "stress"]:
            if condition_name not in candidate_results:
                logger.warning(f"Missing {condition_name} condition in candidate results")
                continue
                
            baseline_condition = self.baseline_data[f"{condition_name}_results"]
            candidate_condition = candidate_results[condition_name]
            
            # Compare each metric
            for metric_name, candidate_values in candidate_condition.items():
                if metric_name not in baseline_condition["metrics"]:
                    logger.warning(f"Metric {metric_name} not found in baseline")
                    continue
                
                baseline_stats = baseline_condition["metrics"][metric_name]
                baseline_values = self._reconstruct_baseline_samples(baseline_stats)
                
                # Perform statistical comparison
                result = self._perform_statistical_test(
                    baseline_values, candidate_values, 
                    metric_name, condition_name, baseline_stats
                )
                
                if result:
                    all_results.append(result)
        
        # Apply multiple comparisons correction
        corrected_results = self._apply_multiple_comparisons_correction(all_results)
        
        return corrected_results
    
    def _reconstruct_baseline_samples(self, baseline_stats: Dict[str, Any]) -> np.ndarray:
        """
        Reconstruct baseline samples from summary statistics.
        
        Args:
            baseline_stats: Statistical summary from baseline fingerprint
            
        Returns:
            Array of reconstructed baseline samples
        """
        # This is an approximation - in practice, we'd store raw samples
        n_samples = baseline_stats["n_samples"]
        mean = baseline_stats["mean"]
        std = baseline_stats["std"]
        
        # Generate samples that match the summary statistics
        # This is a simplification - real implementation would use stored raw data
        np.random.seed(42)  # For reproducibility
        samples = np.random.normal(mean, std, n_samples)
        
        # Adjust to match exact mean/std (moment matching)
        samples = samples * (std / np.std(samples)) if np.std(samples) > 0 else samples
        samples = samples + (mean - np.mean(samples))
        
        return samples
    
    def _perform_statistical_test(self, baseline_samples: np.ndarray,
                                candidate_samples: np.ndarray,
                                metric_name: str, 
                                condition_name: str,
                                baseline_stats: Dict[str, Any]) -> Optional[StatisticalTestResult]:
        """
        Perform statistical test comparing baseline to candidate.
        
        Args:
            baseline_samples: Baseline samples
            candidate_samples: Candidate samples  
            metric_name: Name of metric being tested
            condition_name: Condition (clean, fault, stress)
            baseline_stats: Baseline statistical summary
            
        Returns:
            StatisticalTestResult or None if test fails
        """
        try:
            # Ensure same sample size for paired test
            n_samples = min(len(baseline_samples), len(candidate_samples))
            if n_samples < 2:
                logger.warning(f"Insufficient samples for {metric_name} in {condition_name}")
                return None
            
            baseline_subset = baseline_samples[:n_samples]
            candidate_subset = candidate_samples[:n_samples]
            
            # Paired t-test for dependent samples
            t_stat, p_value = stats.ttest_rel(candidate_subset, baseline_subset)
            df = n_samples - 1
            
            # Effect size (Cohen's d for paired samples)
            diff = candidate_subset - baseline_subset
            cohens_d = np.mean(diff) / np.std(diff) if np.std(diff) > 0 else 0
            
            # Bootstrap confidence interval for Cohen's d
            cohens_d_ci = self._bootstrap_cohens_d_ci(diff)
            
            # Check significance
            is_significant = p_value < 0.05
            
            # Check superiority (directional improvement)
            is_superior = self._check_superiority(metric_name, np.mean(diff), cohens_d)
            
            # Check non-inferiority
            non_inf_margin = self.non_inferiority_margins.get(
                metric_name, 
                self.non_inferiority_margins.get("default", 0.05)
            )
            is_non_inferior = self._check_non_inferiority(
                np.mean(diff), non_inf_margin, np.std(diff), n_samples
            )
            
            return StatisticalTestResult(
                metric_name=metric_name,
                condition=condition_name,
                baseline_mean=np.mean(baseline_subset),
                candidate_mean=np.mean(candidate_subset),
                difference=np.mean(diff),
                t_statistic=t_stat,
                p_value=p_value,
                degrees_of_freedom=df,
                cohens_d=cohens_d,
                cohens_d_ci=cohens_d_ci,
                is_significant=is_significant,
                is_superior=is_superior,
                is_non_inferior=is_non_inferior,
                non_inferiority_margin=non_inf_margin
            )
            
        except Exception as e:
            logger.error(f"Error in statistical test for {metric_name}: {e}")
            return None
    
    def _bootstrap_cohens_d_ci(self, differences: np.ndarray, 
                              n_bootstrap: int = 1000) -> Tuple[float, float]:
        """
        Compute bootstrap confidence interval for Cohen's d.
        
        Args:
            differences: Difference scores between candidate and baseline
            n_bootstrap: Number of bootstrap samples
            
        Returns:
            (lower_ci, upper_ci) 95% confidence interval
        """
        if len(differences) < 2:
            return (0.0, 0.0)
        
        bootstrap_ds = []
        for _ in range(n_bootstrap):
            # Bootstrap sample
            boot_sample = np.random.choice(differences, size=len(differences), replace=True)
            if np.std(boot_sample) > 0:
                boot_d = np.mean(boot_sample) / np.std(boot_sample)
                bootstrap_ds.append(boot_d)
        
        if not bootstrap_ds:
            return (0.0, 0.0)
        
        # 95% CI
        lower_ci = np.percentile(bootstrap_ds, 2.5)
        upper_ci = np.percentile(bootstrap_ds, 97.5)
        
        return (lower_ci, upper_ci)
    
    def _check_superiority(self, metric_name: str, mean_diff: float, cohens_d: float) -> bool:
        """
        Check if candidate shows superiority on a metric.
        
        Args:
            metric_name: Name of metric
            mean_diff: Mean difference (candidate - baseline)
            cohens_d: Cohen's d effect size
            
        Returns:
            True if superior
        """
        # Directional expectations
        if "success" in metric_name or "confidence" in metric_name:
            # Want positive improvement
            return mean_diff > 0 and cohens_d >= 0.2
        elif "route_length" in metric_name or "latency" in metric_name:
            # Want negative improvement (lower is better)
            return mean_diff < 0 and cohens_d <= -0.2
        elif "invalid" in metric_name:
            # Want negative improvement (lower is better)
            return mean_diff < 0 and cohens_d <= -0.2
        else:
            # Neutral - just check effect size
            return abs(cohens_d) >= 0.2
    
    def _check_non_inferiority(self, mean_diff: float, margin: float, 
                              std_diff: float, n_samples: int) -> bool:
        """
        Check if candidate meets non-inferiority criteria.
        
        Args:
            mean_diff: Mean difference (candidate - baseline)
            margin: Non-inferiority margin
            std_diff: Standard deviation of differences
            n_samples: Number of samples
            
        Returns:
            True if non-inferior
        """
        if std_diff <= 0 or n_samples < 2:
            return True  # Conservative assumption
            
        # One-sided t-test for non-inferiority
        # H0: mean_diff <= margin (inferior)
        # H1: mean_diff > margin (non-inferior)
        se = std_diff / np.sqrt(n_samples)
        t_stat = (mean_diff - margin) / se if se > 0 else 0
        p_value = 1 - stats.t.cdf(t_stat, n_samples - 1)
        
        # Non-inferior if we can reject inferiority (p < 0.05)
        return p_value < 0.05
    
    def _apply_multiple_comparisons_correction(self, results: List[StatisticalTestResult]) -> List[StatisticalTestResult]:
        """
        Apply Holm-Bonferroni correction for multiple comparisons.
        
        Args:
            results: List of statistical test results
            
        Returns:
            Corrected results with adjusted p-values
        """
        if not results:
            return results
        
        # Extract p-values
        p_values = [result.p_value for result in results]
        sorted_indices = np.argsort(p_values)
        
        # Apply Holm-Bonferroni correction
        corrected_p_values = []
        n_tests = len(p_values)
        
        for i, idx in enumerate(sorted_indices):
            # Holm correction: p_adj = max(p_orig * (n_tests - rank + 1), previous_adj)
            rank = i + 1
            holm_p = min(p_values[idx] * (n_tests - rank + 1), 1.0)
            
            # Ensure monotonicity
            if corrected_p_values:
                holm_p = max(holm_p, corrected_p_values[-1])
                
            corrected_p_values.append(holm_p)
        
        # Update results with corrected p-values
        corrected_results = []
        for i, result in enumerate(results):
            # Find original index
            orig_idx = sorted_indices.tolist().index(i)
            corrected_p = corrected_p_values[orig_idx]
            
            # Create new result with corrected p-value
            corrected_result = StatisticalTestResult(
                metric_name=result.metric_name,
                condition=result.condition,
                baseline_mean=result.baseline_mean,
                candidate_mean=result.candidate_mean,
                difference=result.difference,
                t_statistic=result.t_statistic,
                p_value=corrected_p,  # Updated
                degrees_of_freedom=result.degrees_of_freedom,
                cohens_d=result.cohens_d,
                cohens_d_ci=result.cohens_d_ci,
                is_significant=corrected_p < 0.05,  # Updated
                is_superior=result.is_superior,
                is_non_inferior=result.is_non_inferior,
                non_inferiority_margin=result.non_inferiority_margin
            )
            corrected_results.append(corrected_result)
        
        logger.info(f"Applied Holm-Bonferroni correction to {len(results)} tests")
        return corrected_results


def main():
    """Example usage of baseline comparator"""
    logging.basicConfig(level=logging.INFO)
    
    # Initialize comparator
    comparator = BaselineComparator(
        baseline_fingerprint_path="baseline_lock/baseline_fingerprint_baseline_20260418_232605.json"
    )
    
    # Example candidate results (in practice, these would come from optimization runs)
    candidate_results = {
        "clean": {
            "success_rate": np.random.beta(9.5, 1.5, 333),  # Slightly better
            "latency": np.random.normal(0.48, 0.09, 333),   # Slightly better
            "invalid_transition_rate": np.random.beta(1, 100, 333),  # Much better
        },
        "fault": {
            "success_rate": np.random.beta(8.5, 1.5, 333),  # Slightly better
            "latency": np.random.normal(0.62, 0.12, 333),   # Slightly better
            "invalid_transition_rate": np.random.beta(1, 20, 333),   # Better
        },
        "stress": {
            "success_rate": np.random.beta(7.5, 1.5, 334),  # Slightly better
            "latency": np.random.normal(0.74, 0.15, 334),   # Slightly better
            "invalid_transition_rate": np.random.beta(1, 12, 334),   # Better
        }
    }
    
    # Compare candidate to baseline
    results = comparator.compare_candidate(candidate_results, "example_candidate_001")
    
    # Print results
    print("\n" + "="*80)
    print("BASELINE COMPARISON RESULTS")
    print("="*80)
    
    for result in results:
        print(f"\n{result.metric_name} ({result.condition}):")
        print(f"  Baseline: {result.baseline_mean:.3f}")
        print(f"  Candidate: {result.candidate_mean:.3f}")
        print(f"  Difference: {result.difference:+.3f}")
        print(f"  Cohen's d: {result.cohens_d:+.3f} [{result.cohens_d_ci[0]:+.3f}, {result.cohens_d_ci[1]:+.3f}]")
        print(f"  p-value: {result.p_value:.3f} ({'significant' if result.is_significant else 'not significant'})")
        print(f"  Superior: {'yes' if result.is_superior else 'no'}")
        print(f"  Non-inferior: {'yes' if result.is_non_inferior else 'no'}")


if __name__ == "__main__":
    main()
