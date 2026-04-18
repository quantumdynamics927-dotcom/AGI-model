"""
Tesseract Routing Experimental Runner

Executes comprehensive experiments to validate tesseract routing vs flat routing
across multiple conditions: clean, lesioned, classical vs quantum scoring.
"""

import torch
import numpy as np
import time
import json
from typing import Dict, Any, List, Tuple
from pathlib import Path
import logging
from dataclasses import dataclass, asdict

from quantum_cognitive_core import QuantumCognitiveCore, QuantumCognitiveConfig
from tesseract_validation_benchmark import TesseractValidationBenchmark
from tesseract_statistical_validation import TesseractStatisticalValidation
from tesseract_acceptance_test import TesseractAcceptanceTest

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ExperimentalResults:
    """Container for experimental results"""
    experiment_name: str
    timestamp: str
    flat_metrics: Dict[str, float]
    tesseract_metrics: Dict[str, float]
    comparison: Dict[str, float]
    statistical_significance: Dict[str, Any]
    recommendation: str

class TesseractExperimentalRunner:
    """Runner for comprehensive tesseract routing experiments"""
    
    def __init__(self, output_dir: str = "experimental_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.results = []
        
    def _convert_to_serializable(self, obj):
        """Convert NumPy types to native Python types for JSON serialization"""
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: self._convert_to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_to_serializable(item) for item in obj]
        return obj
        
    def run_experiment_suite(self):
        """Run complete experimental suite"""
        logger.info("Starting comprehensive tesseract routing experiment suite...")
        
        # Experiment 1: Clean condition comparison
        logger.info("\n=== Experiment 1: Clean Condition Comparison ===")
        clean_results = self._run_clean_condition_experiment()
        self.results.append(clean_results)
        
        # Experiment 2: Lesioned condition comparison
        logger.info("\n=== Experiment 2: Lesioned Condition Comparison ===")
        lesioned_results = self._run_lesioned_condition_experiment()
        self.results.append(lesioned_results)
        
        # Experiment 3: Classical vs Quantum edge scoring
        logger.info("\n=== Experiment 3: Classical vs Quantum Edge Scoring ===")
        scoring_results = self._run_edge_scoring_experiment()
        self.results.append(scoring_results)
        
        # Experiment 4: Acceptance test
        logger.info("\n=== Experiment 4: Acceptance Criteria Evaluation ===")
        acceptance_results = self._run_acceptance_experiment()
        self.results.append(acceptance_results)
        
        # Generate comprehensive report
        self._generate_comprehensive_report()
        
        logger.info("\n=== Experiment Suite Complete ===")
        logger.info(f"Results saved to: {self.output_dir}")
        
    def _run_clean_condition_experiment(self) -> ExperimentalResults:
        """Run experiment under clean (non-lesioned) conditions"""
        
        # Create validation benchmark
        validator = TesseractValidationBenchmark()
        
        # Run validation with clean conditions
        validation_results = validator.run_comprehensive_validation(
            num_samples=200,
            task_complexity="medium"
        )
        
        # Extract metrics
        flat_metrics = validation_results['flat_routing']
        tesseract_metrics = validation_results['tesseract_routing']
        
        # Calculate comparison
        comparison = {
            'efficiency_improvement': flat_metrics.route_efficiency - tesseract_metrics.route_efficiency,
            'accuracy_change': tesseract_metrics.route_accuracy - flat_metrics.route_accuracy,
            'robustness_improvement': tesseract_metrics.lesion_robustness - flat_metrics.lesion_robustness,
            'latency_change': tesseract_metrics.average_latency - flat_metrics.average_latency,
            'calibration_improvement': tesseract_metrics.confidence_calibration - flat_metrics.confidence_calibration
        }
        
        # Statistical significance
        stat_validator = TesseractStatisticalValidation()
        stat_results = stat_validator.run_statistical_comparison(num_samples=100, num_trials=3)
        
        # Recommendation
        if comparison['efficiency_improvement'] > 0.1 and comparison['robustness_improvement'] > 0.05:
            recommendation = "TESSELLACT_ROUTING_ADVANTAGE_CLEAN"
        elif comparison['efficiency_improvement'] < -0.05:
            recommendation = "FLAT_ROUTING_ADVANTAGE_CLEAN"
        else:
            recommendation = "EQUIVALENT_PERFORMANCE_CLEAN"
            
        return ExperimentalResults(
            experiment_name="clean_condition",
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            flat_metrics={
                'route_efficiency': flat_metrics.route_efficiency,
                'route_accuracy': flat_metrics.route_accuracy,
                'lesion_robustness': flat_metrics.lesion_robustness,
                'average_latency': flat_metrics.average_latency,
                'confidence_calibration': flat_metrics.confidence_calibration
            },
            tesseract_metrics={
                'route_efficiency': tesseract_metrics.route_efficiency,
                'route_accuracy': tesseract_metrics.route_accuracy,
                'lesion_robustness': tesseract_metrics.lesion_robustness,
                'average_latency': tesseract_metrics.average_latency,
                'confidence_calibration': tesseract_metrics.confidence_calibration
            },
            comparison=comparison,
            statistical_significance=stat_results,
            recommendation=recommendation
        )
        
    def _run_lesioned_condition_experiment(self) -> ExperimentalResults:
        """Run experiment under lesioned conditions"""
        
        # Create cores with lesion testing
        flat_config = QuantumCognitiveConfig()
        flat_config.tesseract_enabled = False
        
        tesseract_config = QuantumCognitiveConfig()
        tesseract_config.tesseract_enabled = True
        
        flat_core = QuantumCognitiveCore(flat_config)
        tesseract_core = QuantumCognitiveCore(tesseract_config)
        
        # Test under various lesion levels
        lesion_levels = [0.0, 0.1, 0.25, 0.5]
        flat_performances = []
        tesseract_performances = []
        
        for lesion_rate in lesion_levels:
            # Apply lesions to tesseract core
            if tesseract_core.tesseract_router:
                num_degraded = int(16 * lesion_rate)
                degraded_vertices = list(range(num_degraded))
                tesseract_core.tesseract_router.update_fault_mask(degraded_vertices)
            
            # Test both cores
            flat_perf = self._test_core_performance(flat_core, num_samples=50)
            tesseract_perf = self._test_core_performance(tesseract_core, num_samples=50)
            
            flat_performances.append(flat_perf)
            tesseract_performances.append(tesseract_perf)
        
        # Calculate lesion robustness
        flat_robustness = np.mean(flat_performances)
        tesseract_robustness = np.mean(tesseract_performances)
        
        # Calculate degradation slopes
        if len(lesion_levels) > 1:
            flat_slope = np.polyfit(lesion_levels, flat_performances, 1)[0]
            tesseract_slope = np.polyfit(lesion_levels, tesseract_performances, 1)[0]
        else:
            flat_slope = 0
            tesseract_slope = 0
        
        comparison = {
            'robustness_improvement': tesseract_robustness - flat_robustness,
            'degradation_slope_improvement': abs(flat_slope) - abs(tesseract_slope),
            'lesion_resilience': tesseract_robustness / flat_robustness if flat_robustness > 0 else 1.0
        }
        
        if comparison['robustness_improvement'] > 0.05:
            recommendation = "TESSELLACT_ROUTING_SUPERIOR_LESIONED"
        elif comparison['robustness_improvement'] < -0.05:
            recommendation = "FLAT_ROUTING_SUPERIOR_LESIONED"
        else:
            recommendation = "EQUIVALENT_LESION_PERFORMANCE"
            
        return ExperimentalResults(
            experiment_name="lesioned_condition",
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            flat_metrics={
                'lesion_robustness': flat_robustness,
                'degradation_slope': flat_slope,
                'final_performance': flat_performances[-1] if flat_performances else 0.5
            },
            tesseract_metrics={
                'lesion_robustness': tesseract_robustness,
                'degradation_slope': tesseract_slope,
                'final_performance': tesseract_performances[-1] if tesseract_performances else 0.5
            },
            comparison=comparison,
            statistical_significance={},
            recommendation=recommendation
        )
        
    def _test_core_performance(self, core: QuantumCognitiveCore, num_samples: int) -> float:
        """Test core performance on sample inputs"""
        performances = []
        
        for i in range(num_samples):
            try:
                input_data = torch.randn(1, core.config.encoder_input_dim)
                result = core.process_input(input_data)
                
                # Simple performance metric based on action quality
                action = result['action']
                target = torch.randn_like(action)
                
                # Cosine similarity
                action_norm = action / (torch.norm(action) + 1e-8)
                target_norm = target / (torch.norm(target) + 1e-8)
                similarity = torch.dot(action_norm.flatten(), target_norm.flatten()).item()
                performance = (similarity + 1.0) / 2.0
                
                performances.append(performance)
            except Exception as e:
                logger.warning(f"Sample failed: {e}")
                performances.append(0.5)
                
        return np.mean(performances) if performances else 0.5
        
    def _run_edge_scoring_experiment(self) -> ExperimentalResults:
        """Compare classical vs quantum edge scoring within tesseract"""
        
        # Create tesseract core
        config = QuantumCognitiveConfig()
        config.tesseract_enabled = True
        core = QuantumCognitiveCore(config)
        
        # Test classical scoring (disable quantum backend)
        if core.quantum_edge_scorer:
            original_backend = core.quantum_edge_scorer.backend
            core.quantum_edge_scorer.backend = None
            
        classical_performances = []
        for i in range(100):
            try:
                input_data = torch.randn(1, core.config.encoder_input_dim)
                result = core.process_input(input_data)
                classical_performances.append(result.get('phi_score', 0.0))
            except:
                classical_performances.append(0.0)
        
        # Test quantum scoring (restore quantum backend)
        if core.quantum_edge_scorer:
            core.quantum_edge_scorer.backend = original_backend
            
        quantum_performances = []
        for i in range(100):
            try:
                input_data = torch.randn(1, core.config.encoder_input_dim)
                result = core.process_input(input_data)
                quantum_performances.append(result.get('phi_score', 0.0))
            except:
                quantum_performances.append(0.0)
        
        classical_mean = np.mean(classical_performances)
        quantum_mean = np.mean(quantum_performances)
        
        comparison = {
            'quantum_advantage': quantum_mean - classical_mean,
            'relative_improvement': (quantum_mean - classical_mean) / classical_mean if classical_mean > 0 else 0
        }
        
        if comparison['quantum_advantage'] > 0.01:
            recommendation = "QUANTUM_SCORING_ADVANTAGE"
        elif comparison['quantum_advantage'] < -0.01:
            recommendation = "CLASSICAL_SCORING_ADVANTAGE"
        else:
            recommendation = "EQUIVALENT_SCORING"
            
        return ExperimentalResults(
            experiment_name="edge_scoring_comparison",
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            flat_metrics={
                'classical_scoring_performance': classical_mean,
                'samples_tested': 100
            },
            tesseract_metrics={
                'quantum_scoring_performance': quantum_mean,
                'samples_tested': 100
            },
            comparison=comparison,
            statistical_significance={},
            recommendation=recommendation
        )
        
    def _run_acceptance_experiment(self) -> ExperimentalResults:
        """Run full acceptance criteria evaluation"""
        
        acceptance_test = TesseractAcceptanceTest()
        results = acceptance_test.run_acceptance_test(
            num_samples=300,
            confidence_level=0.95
        )
        
        acceptance_decision = results['acceptance_decision']
        
        return ExperimentalResults(
            experiment_name="acceptance_criteria",
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            flat_metrics={
                'baseline_performance': 0.5,  # Placeholder
                'meets_criteria': acceptance_decision['criteria_met']
            },
            tesseract_metrics={
                'tested_performance': acceptance_decision['criteria_met'],
                'total_criteria': acceptance_decision['total_criteria']
            },
            comparison={
                'criteria_met': acceptance_decision['criteria_met'],
                'total_criteria': acceptance_decision['total_criteria']
            },
            statistical_significance=results['statistical_results'],
            recommendation=acceptance_decision['decision']
        )
        
    def _generate_comprehensive_report(self):
        """Generate comprehensive experimental report"""
        
        report = {
            "experimental_suite_summary": {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_experiments": len(self.results),
                "experiments": []
            },
            "individual_results": [],
            "overall_assessment": {}
        }
        
        # Process each experiment
        tesseract_advantages = 0
        flat_advantages = 0
        equivalents = 0
        
        for result in self.results:
            exp_summary = {
                "name": result.experiment_name,
                "recommendation": result.recommendation,
                "timestamp": result.timestamp
            }
            report["experimental_suite_summary"]["experiments"].append(exp_summary)
            report["individual_results"].append(asdict(result))
            
            # Count advantages
            if "TESSELLACT" in result.recommendation:
                tesseract_advantages += 1
            elif "FLAT" in result.recommendation:
                flat_advantages += 1
            else:
                equivalents += 1
        
        # Overall assessment
        total_experiments = len(self.results)
        if total_experiments > 0:
            tesseract_win_rate = tesseract_advantages / total_experiments
            
            if tesseract_win_rate >= 0.6:
                overall_recommendation = "STRONG_TESSERACT_ADVANTAGE"
            elif tesseract_win_rate >= 0.4:
                overall_recommendation = "CONDITIONAL_TESSERACT_SUPPORT"
            elif tesseract_win_rate >= 0.2:
                overall_recommendation = "WEAK_TESSERACT_SUPPORT"
            else:
                overall_recommendation = "STICK_WITH_FLAT_ROUTING"
        else:
            overall_recommendation = "INSUFFICIENT_DATA"
            
        report["overall_assessment"] = {
            "tesseract_advantages": tesseract_advantages,
            "flat_advantages": flat_advantages,
            "equivalents": equivalents,
            "tesseract_win_rate": tesseract_advantages / total_experiments if total_experiments > 0 else 0,
            "overall_recommendation": overall_recommendation
        }
        
        # Save report
        report_file = self.output_dir / f"experimental_suite_report_{int(time.time())}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self._convert_to_serializable(report), f, indent=2)
            
        # Print summary
        self._print_experimental_summary(report)
        
    def _print_experimental_summary(self, report: Dict):
        """Print experimental summary to console"""
        
        print("\n" + "="*70)
        print("TESSELLATED ROUTING EXPERIMENTAL SUITE RESULTS")
        print("="*70)
        
        print(f"\nExperiments Conducted: {report['experimental_suite_summary']['total_experiments']}")
        print("-" * 50)
        
        for exp in report['individual_results']:
            print(f"\n{exp['experiment_name'].upper()}:")
            print(f"  Recommendation: {exp['recommendation']}")
            if 'comparison' in exp:
                for metric, value in exp['comparison'].items():
                    if isinstance(value, float):
                        print(f"  {metric}: {value:.4f}")
                        
        assessment = report['overall_assessment']
        print(f"\n{'='*70}")
        print("OVERALL ASSESSMENT")
        print("="*70)
        print(f"Tesseract Advantages: {assessment['tesseract_advantages']}")
        print(f"Flat Advantages: {assessment['flat_advantages']}")
        print(f"Equivalents: {assessment['equivalents']}")
        print(f"Tesseract Win Rate: {assessment['tesseract_win_rate']*100:.1f}%")
        print(f"\nOverall Recommendation: {assessment['overall_recommendation']}")
        
        if assessment['overall_recommendation'] == "STRONG_TESSERACT_ADVANTAGE":
            print("\n✓ TESSERACT ROUTING SHOULD BE PROMOTED TO DEFAULT")
            print("  Strong evidence of superiority across multiple conditions")
        elif assessment['overall_recommendation'] == "CONDITIONAL_TESSERACT_SUPPORT":
            print("\n~ CONDITIONAL TESSERACT SUPPORT")
            print("  Moderate evidence, consider gradual adoption")
        elif assessment['overall_recommendation'] == "WEAK_TESSERACT_SUPPORT":
            print("\n? WEAK TESSERACT SUPPORT")
            print("  Limited evidence, more testing recommended")
        else:
            print("\n✗ STICK WITH FLAT ROUTING")
            print("  Insufficient evidence for tesseract advantage")
            
        print(f"\n{'='*70}")

def main():
    """Main experimental runner"""
    logger.info("Initializing Tesseract Routing Experimental Suite...")
    
    runner = TesseractExperimentalRunner()
    runner.run_experiment_suite()
    
    logger.info("Experimental suite complete!")

if __name__ == "__main__":
    main()