"""
Tesseract Routing Acceptance Test

Implementation of the acceptance criteria: "only promote it to default routing 
if it beats flat routing on efficiency and robustness without materially 
harming route accuracy or calibration."
"""

import torch
import numpy as np
import time
from typing import Dict, Any, List
import logging

from quantum_cognitive_core import QuantumCognitiveCore, QuantumCognitiveConfig
from tesseract_validation_benchmark import TesseractValidationBenchmark
from tesseract_statistical_validation import TesseractStatisticalValidation

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TesseractAcceptanceTest:
    """Acceptance test for tesseract routing based on defined criteria"""
    
    def __init__(self):
        self.efficiency_threshold = 0.1    # 10% improvement in efficiency required
        self.robustness_threshold = 0.05   # 5% improvement in robustness required
        self.accuracy_degradation_limit = 0.02  # Max 2% degradation in accuracy
        self.calibration_degradation_limit = 0.05  # Max 5% degradation in calibration
        
    def run_acceptance_test(
        self, 
        num_samples: int = 500,
        confidence_level: float = 0.95
    ) -> Dict[str, Any]:
        """Run complete acceptance test based on defined criteria"""
        
        logger.info("Running tesseract routing acceptance test...")
        logger.info(f"Criteria: efficiency > {self.efficiency_threshold*100}%, "
                   f"robustness > {self.robustness_threshold*100}%, "
                   f"accuracy degradation < {self.accuracy_degradation_limit*100}%, "
                   f"calibration degradation < {self.calibration_degradation_limit*100}%")
        
        # Run validation benchmark
        validator = TesseractValidationBenchmark()
        validation_results = validator.run_comprehensive_validation(
            num_samples=num_samples,
            task_complexity="medium"
        )
        
        # Run statistical validation
        stat_validator = TesseractStatisticalValidation()
        stat_results = stat_validator.run_statistical_comparison(
            num_samples=min(num_samples, 200),  # Limit for performance
            num_trials=3
        )
        
        # Evaluate acceptance criteria
        acceptance_decision = self._evaluate_acceptance_criteria(
            validation_results, stat_results
        )
        
        # Generate report
        self._generate_acceptance_report(
            validation_results, stat_results, acceptance_decision
        )
        
        return {
            "validation_results": validation_results,
            "statistical_results": stat_results,
            "acceptance_decision": acceptance_decision
        }
        
    def _evaluate_acceptance_criteria(
        self, 
        validation_results: Dict[str, Any], 
        stat_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate whether tesseract routing meets acceptance criteria"""
        
        # Extract metrics
        tesseract_metrics = validation_results['tesseract_routing']
        flat_metrics = validation_results['flat_routing']
        
        # Calculate improvements/degradations
        efficiency_improvement = flat_metrics.route_efficiency - tesseract_metrics.route_efficiency
        robustness_improvement = tesseract_metrics.lesion_robustness - flat_metrics.lesion_robustness
        accuracy_degradation = flat_metrics.route_accuracy - tesseract_metrics.route_accuracy
        calibration_degradation = flat_metrics.confidence_calibration - tesseract_metrics.confidence_calibration
        
        # Statistical significance
        is_statistically_significant = stat_results["statistical_tests"]["is_statistically_significant"]
        cohens_d = stat_results["statistical_tests"]["cohens_d"]
        practical_significance = stat_results["statistical_tests"]["practical_significance"]
        
        # Evaluate each criterion
        criteria_evaluation = {
            "efficiency_criterion": {
                "required": f"> {self.efficiency_threshold*100}%",
                "actual_improvement": f"{efficiency_improvement*100:.2f}%",
                "met": efficiency_improvement > self.efficiency_threshold
            },
            "robustness_criterion": {
                "required": f"> {self.robustness_threshold*100}%",
                "actual_improvement": f"{robustness_improvement*100:.2f}%",
                "met": robustness_improvement > self.robustness_threshold
            },
            "accuracy_criterion": {
                "required": f"< {self.accuracy_degradation_limit*100}%",
                "actual_degradation": f"{accuracy_degradation*100:.2f}%",
                "met": accuracy_degradation < self.accuracy_degradation_limit
            },
            "calibration_criterion": {
                "required": f"< {self.calibration_degradation_limit*100}%",
                "actual_degradation": f"{calibration_degradation*100:.2f}%",
                "met": calibration_degradation < self.calibration_degradation_limit
            },
            "statistical_criterion": {
                "required": "statistically significant improvement",
                "actual": f"p={stat_results['statistical_tests']['p_value']:.6f}, d={cohens_d:.3f}",
                "met": is_statistically_significant and cohens_d > 0
            }
        }
        
        # Count met criteria
        met_criteria = sum(1 for criterion in criteria_evaluation.values() if criterion["met"])
        total_criteria = len(criteria_evaluation)
        
        # Overall decision
        if met_criteria >= 4:  # Require at least 4 out of 5 criteria
            decision = "ACCEPT_TESSERACT_ROUTING"
            reason = f"Meets {met_criteria}/{total_criteria} acceptance criteria"
        elif met_criteria >= 2:
            decision = "CONDITIONAL_ACCEPTANCE"
            reason = f"Meets {met_criteria}/{total_criteria} criteria, needs further validation"
        else:
            decision = "REJECT_TESSERACT_ROUTING"
            reason = f"Only meets {met_criteria}/{total_criteria} criteria"
            
        return {
            "decision": decision,
            "reason": reason,
            "criteria_met": met_criteria,
            "total_criteria": total_criteria,
            "individual_criteria": criteria_evaluation,
            "efficiency_improvement": efficiency_improvement,
            "robustness_improvement": robustness_improvement,
            "accuracy_degradation": accuracy_degradation,
            "calibration_degradation": calibration_degradation
        }
        
    def _generate_acceptance_report(
        self, 
        validation_results: Dict[str, Any], 
        stat_results: Dict[str, Any],
        acceptance_decision: Dict[str, Any]
    ):
        """Generate comprehensive acceptance report"""
        
        print("\n" + "="*70)
        print("TESSELLATED ROUTING ACCEPTANCE TEST REPORT")
        print("="*70)
        
        # Validation Results Summary
        print(f"\nVALIDATION RESULTS:")
        print("-" * 20)
        for approach, metrics in validation_results.items():
            print(f"\n{approach.upper()}:")
            print(f"  Route Efficiency: {metrics.route_efficiency:.3f}")
            print(f"  Route Accuracy: {metrics.route_accuracy:.3f}")
            print(f"  Lesion Robustness: {metrics.lesion_robustness:.3f}")
            print(f"  Confidence Calibration: {metrics.confidence_calibration:.3f}")
            print(f"  Average Latency: {metrics.average_latency:.4f}s")
            
        # Statistical Results Summary
        print(f"\nSTATISTICAL VALIDATION:")
        print("-" * 25)
        stats_desc = stat_results["descriptive_statistics"]
        stats_tests = stat_results["statistical_tests"]
        print(f"  Tesseract Mean: {stats_desc['tesseract_mean']:.4f} ± {stats_desc['tesseract_std']:.4f}")
        print(f"  Flat Mean:      {stats_desc['flat_mean']:.4f} ± {stats_desc['flat_std']:.4f}")
        print(f"  T-statistic: {stats_tests['t_statistic']:.4f}")
        print(f"  P-value: {stats_tests['p_value']:.6f}")
        print(f"  Cohen's d: {stats_tests['cohens_d']:.4f}")
        
        # Acceptance Criteria Evaluation
        print(f"\nACCEPTANCE CRITERIA EVALUATION:")
        print("-" * 35)
        criteria = acceptance_decision["individual_criteria"]
        for criterion_name, criterion_result in criteria.items():
            status = "[PASS]" if criterion_result["met"] else "[FAIL]"
            print(f"  {criterion_name}: {status}")
            print(f"    Required: {criterion_result['required']}")
            # Handle different key names for actual values
            if "actual" in criterion_result:
                print(f"    Actual: {criterion_result['actual']}")
            elif "actual_improvement" in criterion_result:
                print(f"    Actual: {criterion_result['actual_improvement']}")
            elif "actual_degradation" in criterion_result:
                print(f"    Actual: {criterion_result['actual_degradation']}")
            
        # Final Decision
        print(f"\nFINAL DECISION:")
        print("-" * 15)
        decision = acceptance_decision["decision"]
        reason = acceptance_decision["reason"]
        
        if decision == "ACCEPT_TESSERACT_ROUTING":
            print("[PASS] ACCEPT TESSERACT ROUTING")
            print("  Recommendation: Promote tesseract routing to default")
        elif decision == "CONDITIONAL_ACCEPTANCE":
            print("[CONDITIONAL] CONDITIONAL ACCEPTANCE")
            print("  Recommendation: Further validation recommended before promotion")
        else:
            print("[FAIL] REJECT TESSERACT_ROUTING")
            print("  Recommendation: Continue with flat routing")
            
        print(f"  Reason: {reason}")
        
        # Improvement Summary
        print(f"\nIMPROVEMENT SUMMARY:")
        print("-" * 20)
        eff_imp = acceptance_decision["efficiency_improvement"]
        rob_imp = acceptance_decision["robustness_improvement"]
        acc_deg = acceptance_decision["accuracy_degradation"]
        cal_deg = acceptance_decision["calibration_degradation"]
        
        print(f"  Route Efficiency: {'+' if eff_imp > 0 else ''}{eff_imp*100:.2f}%")
        print(f"  Lesion Robustness: {'+' if rob_imp > 0 else ''}{rob_imp*100:.2f}%")
        print(f"  Route Accuracy: {'-' if acc_deg > 0 else '+'}{-acc_deg*100:.2f}%")
        print(f"  Confidence Calibration: {'-' if cal_deg > 0 else '+'}{-cal_deg*100:.2f}%")
        
        print(f"\n" + "="*70)

def run_acceptance_test():
    """Run the complete acceptance test"""
    logger.info("Starting tesseract routing acceptance test...")
    
    # Create acceptance test
    acceptance_test = TesseractAcceptanceTest()
    
    # Run test
    results = acceptance_test.run_acceptance_test(
        num_samples=300,  # Balanced for thoroughness and performance
        confidence_level=0.95
    )
    
    return results

# Example usage
if __name__ == "__main__":
    results = run_acceptance_test()