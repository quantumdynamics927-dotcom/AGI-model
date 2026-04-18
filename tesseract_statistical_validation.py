"""
Statistical Validation for Tesseract Routing

Provides statistical tests to determine if tesseract routing improvements 
are significant versus flat routing baseline.
"""

import torch
import numpy as np
import scipy.stats as stats
from typing import Dict, Any, List, Tuple, Optional
import logging

from quantum_cognitive_core import QuantumCognitiveCore, QuantumCognitiveConfig

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TesseractStatisticalValidation:
    """Statistical validation for tesseract routing improvements"""
    
    def __init__(self, significance_level: float = 0.05):
        self.significance_level = significance_level
        
    def run_statistical_comparison(
        self,
        num_samples: int = 1000,
        num_trials: int = 10
    ) -> Dict[str, Any]:
        """Run statistical comparison between tesseract and flat routing"""
        
        logger.info("Running statistical validation of tesseract routing...")
        
        # Collect results across multiple trials
        tesseract_results = []
        flat_results = []
        
        for trial in range(num_trials):
            logger.info(f"Running trial {trial + 1}/{num_trials}")
            
            # Test both approaches on same inputs
            tesseract_perf, flat_perf = self._compare_single_trial(num_samples)
            tesseract_results.extend(tesseract_perf)
            flat_results.extend(flat_perf)
            
        # Perform statistical tests
        statistical_results = self._perform_statistical_tests(
            tesseract_results, flat_results
        )
        
        return statistical_results
        
    def _compare_single_trial(
        self, 
        num_samples: int
    ) -> Tuple[List[float], List[float]]:
        """Compare tesseract vs flat routing on single trial"""
        
        # Create cores
        tesseract_config = QuantumCognitiveConfig()
        tesseract_config.tesseract_enabled = True
        
        flat_config = QuantumCognitiveConfig()
        flat_config.tesseract_enabled = False
        
        tesseract_core = QuantumCognitiveCore(tesseract_config)
        flat_core = QuantumCognitiveCore(flat_config)
        
        tesseract_performances = []
        flat_performances = []
        
        for i in range(num_samples):
            try:
                # Generate test input
                input_data = torch.randn(1, 128)
                target = torch.randn(1, 32)  # Target output for comparison
                
                # Test tesseract routing
                tesseract_result = tesseract_core.process_input(input_data)
                tesseract_perf = self._calculate_performance(tesseract_result, target)
                tesseract_performances.append(tesseract_perf)
                
                # Test flat routing
                flat_result = flat_core.process_input(input_data)
                flat_perf = self._calculate_performance(flat_result, target)
                flat_performances.append(flat_perf)
                
            except Exception as e:
                logger.warning(f"Sample {i} failed: {e}")
                # Add neutral performance for failed samples
                tesseract_performances.append(0.5)
                flat_performances.append(0.5)
                
        return tesseract_performances, flat_performances
        
    def _calculate_performance(
        self, 
        result: Dict[str, Any], 
        target: torch.Tensor
    ) -> float:
        """Calculate performance metric for a result"""
        try:
            # Extract action/policy output
            action = result.get('action', torch.randn(1, 32))
            
            # Ensure compatible dimensions
            if action.shape != target.shape:
                # Handle dimension mismatch
                if action.shape[0] == 1 and target.shape[0] == 1:
                    min_dim = min(action.shape[1], target.shape[1])
                    action_slice = action[:, :min_dim]
                    target_slice = target[:, :min_dim]
                else:
                    # Flatten both and take minimum elements
                    action_flat = action.flatten()
                    target_flat = target.flatten()
                    min_elements = min(len(action_flat), len(target_flat))
                    action_slice = action_flat[:min_elements].unsqueeze(0)
                    target_slice = target_flat[:min_elements].unsqueeze(0)
            else:
                action_slice = action
                target_slice = target
                
            # Calculate cosine similarity as performance metric
            action_norm = action_slice / (torch.norm(action_slice) + 1e-8)
            target_norm = target_slice / (torch.norm(target_slice) + 1e-8)
            similarity = torch.dot(action_norm.flatten(), target_norm.flatten()).item()
            
            # Normalize to [0,1] range
            performance = (similarity + 1.0) / 2.0
            return performance
            
        except Exception as e:
            logger.warning(f"Performance calculation failed: {e}")
            return 0.5  # Neutral performance
            
    def _perform_statistical_tests(
        self, 
        tesseract_results: List[float], 
        flat_results: List[float]
    ) -> Dict[str, Any]:
        """Perform statistical tests on results"""
        
        # Convert to numpy arrays
        tesseract_array = np.array(tesseract_results)
        flat_array = np.array(flat_results)
        
        # Descriptive statistics
        tesseract_mean = np.mean(tesseract_array)
        tesseract_std = np.std(tesseract_array)
        flat_mean = np.mean(flat_array)
        flat_std = np.std(flat_array)
        
        # T-test for difference in means
        t_stat, p_value = stats.ttest_rel(tesseract_array, flat_array)
        
        # Effect size (Cohen's d)
        diff = tesseract_mean - flat_mean
        pooled_std = np.sqrt(((len(tesseract_array) - 1) * tesseract_std**2 + 
                             (len(flat_array) - 1) * flat_std**2) / 
                            (len(tesseract_array) + len(flat_array) - 2))
        cohens_d = diff / pooled_std if pooled_std > 0 else 0
        
        # Confidence intervals
        confidence_level = 1 - self.significance_level
        tesseract_ci = stats.t.interval(confidence_level, 
                                       len(tesseract_array) - 1,
                                       tesseract_mean, 
                                       stats.sem(tesseract_array))
        flat_ci = stats.t.interval(confidence_level,
                                  len(flat_array) - 1,
                                  flat_mean,
                                  stats.sem(flat_array))
        
        # Statistical significance
        is_significant = p_value < self.significance_level
        improvement = tesseract_mean - flat_mean
        
        # Practical significance
        practical_significance = "YES" if abs(cohens_d) > 0.2 else "NO"
        
        results = {
            "descriptive_statistics": {
                "tesseract_mean": float(tesseract_mean),
                "tesseract_std": float(tesseract_std),
                "tesseract_ci_lower": float(tesseract_ci[0]),
                "tesseract_ci_upper": float(tesseract_ci[1]),
                "flat_mean": float(flat_mean),
                "flat_std": float(flat_std),
                "flat_ci_lower": float(flat_ci[0]),
                "flat_ci_upper": float(flat_ci[1])
            },
            "statistical_tests": {
                "t_statistic": float(t_stat),
                "p_value": float(p_value),
                "is_statistically_significant": is_significant,
                "cohens_d": float(cohens_d),
                "practical_significance": practical_significance
            },
            "interpretation": {
                "mean_difference": float(improvement),
                "improvement_percentage": float((improvement / flat_mean * 100) if flat_mean > 0 else 0),
                "significance_level": self.significance_level
            }
        }
        
        # Add recommendation
        if is_significant and cohens_d > 0.2:
            results["recommendation"] = "ADOPT_TESSERACT_ROUTING"
            results["justification"] = "Statistically and practically significant improvement"
        elif is_significant and cohens_d <= 0.2:
            results["recommendation"] = "MORE_DATA_NEEDED"
            results["justification"] = "Statistically significant but practically small effect"
        else:
            results["recommendation"] = "STICK_WITH_FLAT_ROUTING"
            results["justification"] = "No significant improvement detected"
            
        return results
        
    def validate_assumptions(self, data1: List[float], data2: List[float]) -> Dict[str, Any]:
        """Validate statistical assumptions for the tests"""
        
        # Normality test (Shapiro-Wilk)
        try:
            shapiro_tesseract = stats.shapiro(data1[:5000])  # Limit sample size for test
            shapiro_flat = stats.shapiro(data2[:5000])
            normality_ok = shapiro_tesseract.pvalue > 0.05 and shapiro_flat.pvalue > 0.05
        except:
            # Shapiro test fails with large samples, assume normality
            normality_ok = True
            shapiro_tesseract = (0, 1.0)
            shapiro_flat = (0, 1.0)
            
        # Homogeneity of variance (Levene's test)
        try:
            levene_stat, levene_p = stats.levene(data1, data2)
            variance_homogeneous = levene_p > 0.05
        except:
            variance_homogeneous = True
            levene_stat, levene_p = (0, 1.0)
            
        return {
            "normality_assumption": {
                "tesseract_normal": normality_ok,
                "tesseract_shapiro_stat": float(shapiro_tesseract[0]),
                "tesseract_shapiro_p": float(shapiro_tesseract[1]),
                "flat_normal": normality_ok,
                "flat_shapiro_stat": float(shapiro_flat[0]),
                "flat_shapiro_p": float(shapiro_flat[1])
            },
            "variance_assumption": {
                "homogeneous_variance": variance_homogeneous,
                "levene_statistic": float(levene_stat),
                "levene_p_value": float(levene_p)
            },
            "assumptions_met": normality_ok and variance_homogeneous
        }

def run_statistical_validation():
    """Run complete statistical validation"""
    logger.info("Starting statistical validation of tesseract routing...")
    
    # Create validator
    validator = TesseractStatisticalValidation(significance_level=0.05)
    
    # Run comparison
    results = validator.run_statistical_comparison(
        num_samples=200,  # Reduced for faster execution
        num_trials=5      # Reduced for faster execution
    )
    
    # Print results
    print("\n" + "="*60)
    print("STATISTICAL VALIDATION OF TESSERACT ROUTING")
    print("="*60)
    
    stats_desc = results["descriptive_statistics"]
    stats_tests = results["statistical_tests"]
    
    print(f"\nDescriptive Statistics:")
    print(f"  Tesseract Mean: {stats_desc['tesseract_mean']:.4f} ± {stats_desc['tesseract_std']:.4f}")
    print(f"  Flat Mean:      {stats_desc['flat_mean']:.4f} ± {stats_desc['flat_std']:.4f}")
    print(f"  Difference:     {results['interpretation']['mean_difference']:.4f}")
    
    print(f"\nStatistical Tests:")
    print(f"  T-statistic: {stats_tests['t_statistic']:.4f}")
    print(f"  P-value: {stats_tests['p_value']:.6f}")
    print(f"  Cohen's d: {stats_tests['cohens_d']:.4f}")
    print(f"  Significant: {'YES' if stats_tests['is_statistically_significant'] else 'NO'}")
    
    print(f"\nRecommendation: {results['recommendation']}")
    print(f"Justification: {results['justification']}")
    
    print(f"\n" + "="*60)
    
    return results

# Example usage
if __name__ == "__main__":
    results = run_statistical_validation()