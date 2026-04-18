"""
Bounded Experiment Framework

Provides pre-registered, immutable experiments with declared success/failure criteria.
Prevents p-hacking and ensures scientific validity of all QAGI precursor experiments.
"""

import time
import threading
import logging
from typing import Dict, Any, Callable, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
from pathlib import Path

from governance_layer import (
    MetricsRegistry, 
    TypedMetric, 
    MetricType, 
    ExperimentStatus,
    AcceptanceCriteria,
    create_metric
)

logger = logging.getLogger(__name__)


class ExperimentOutcome(Enum):
    """Possible outcomes of a bounded experiment"""
    SUCCESS = "success"           # Met all success criteria
    PARTIAL_SUCCESS = "partial"   # Met some success criteria
    FAILURE = "failure"           # Triggered failure criteria
    TIMEOUT = "timeout"          # Exceeded time limit
    ERROR = "error"              # Exception during execution
    REJECTED = "rejected"        # Did not meet criteria


@dataclass
class ExperimentResult:
    """Result of a bounded experiment"""
    experiment_id: str
    outcome: ExperimentOutcome
    hypothesis: str
    metrics: List[TypedMetric] = field(default_factory=list)
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duration_seconds: float = 0.0
    iterations_completed: int = 0
    error_message: Optional[str] = None
    evaluation_summary: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "experiment_id": self.experiment_id,
            "outcome": self.outcome.value,
            "hypothesis": self.hypothesis,
            "metrics": [m.to_dict() for m in self.metrics],
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_seconds": self.duration_seconds,
            "iterations_completed": self.iterations_completed,
            "error_message": self.error_message,
            "evaluation_summary": self.evaluation_summary
        }


class BoundedExperiment:
    """
    A bounded experiment with pre-declared success/failure criteria.
    
    Once instantiated, experiment parameters cannot be modified.
    This ensures scientific rigor and prevents p-hacking.
    
    Example:
        experiment = BoundedExperiment(
            name="Tesseract Efficiency Test",
            hypothesis="Tesseract routing improves efficiency by >10%",
            success_criteria={"efficiency": lambda x: x > 0.10},
            failure_criteria={"accuracy": lambda x: x < 0.90},
            max_iterations=100,
            timeout_seconds=3600.0
        )
        
        result = experiment.run(experiment_logic)
    """
    
    def __init__(self,
                 name: str,
                 hypothesis: str,
                 success_criteria: Dict[str, Callable[[float], bool]],
                 failure_criteria: Dict[str, Callable[[float], bool]],
                 max_iterations: int = 100,
                 timeout_seconds: float = 3600.0,
                 registry: Optional[MetricsRegistry] = None):
        """
        Initialize a bounded experiment.
        
        Args:
            name: Human-readable experiment name
            hypothesis: The hypothesis being tested
            success_criteria: Dict of metric_name -> predicate
            failure_criteria: Dict of metric_name -> predicate
            max_iterations: Maximum iterations allowed
            timeout_seconds: Maximum time allowed
            registry: MetricsRegistry for recording results
        """
        self.name = name
        self.hypothesis = hypothesis
        self.success_criteria = success_criteria
        self.failure_criteria = failure_criteria
        self.max_iterations = max_iterations
        self.timeout_seconds = timeout_seconds
        self.registry = registry or MetricsRegistry()
        
        # Register with governance layer
        self.experiment_id = self.registry.register_experiment(
            hypothesis=hypothesis,
            success_criteria=success_criteria,
            failure_criteria=failure_criteria,
            max_iterations=max_iterations,
            timeout_seconds=timeout_seconds
        )
        
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self._interrupted = False
        
        logger.info(f"Created bounded experiment: {name} ({self.experiment_id})")
    
    def run(self, 
            experiment_logic: Callable[[int, 'BoundedExperiment'], Dict[str, Any]],
            callback: Optional[Callable[[int, Dict[str, Any]], None]] = None) -> ExperimentResult:
        """
        Run the bounded experiment.
        
        Args:
            experiment_logic: Function(iteration, experiment) -> metrics_dict
            callback: Optional callback(iteration, metrics) for progress updates
            
        Returns:
            ExperimentResult with full outcome
        """
        self.start_time = datetime.now()
        metrics_collected: List[TypedMetric] = []
        
        # Setup timeout using threading (cross-platform compatible)
        timeout_event = threading.Event()
        timeout_occurred = [False]  # Use list to allow mutation in nested function
        
        def timeout_worker():
            time.sleep(self.timeout_seconds)
            timeout_occurred[0] = True
            timeout_event.set()
        
        timeout_thread = threading.Thread(target=timeout_worker, daemon=True)
        timeout_thread.start()
        
        try:
            logger.info(f"Starting experiment: {self.name}")
            
            for iteration in range(self.max_iterations):
                # Check for timeout
                if timeout_occurred[0]:
                    raise TimeoutError(f"Experiment exceeded {self.timeout_seconds} seconds")
                
                if self._interrupted:
                    logger.warning("Experiment interrupted by user")
                    break
                
                # Run one iteration
                try:
                    metrics_dict = experiment_logic(iteration, self)
                    
                    # Convert to TypedMetrics and record
                    for metric_name, metric_value in metrics_dict.items():
                        if isinstance(metric_value, dict):
                            # Complex metric with metadata
                            metric = create_metric(
                                name=metric_name,
                                metric_type=metric_value.get('type', MetricType.TASK_FACING),
                                value=metric_value['value'],
                                bounds=metric_value.get('bounds', (0.0, 1.0)),
                                experiment_id=self.experiment_id,
                                confidence=metric_value.get('confidence', 0.95),
                                metadata=metric_value.get('metadata', {})
                            )
                        else:
                            # Simple numeric metric
                            metric = create_metric(
                                name=metric_name,
                                metric_type=MetricType.TASK_FACING,
                                value=float(metric_value),
                                bounds=(0.0, 1.0),
                                experiment_id=self.experiment_id
                            )
                        
                        self.registry.record_metric(metric)
                        metrics_collected.append(metric)
                    
                    # Callback for progress updates
                    if callback:
                        callback(iteration, metrics_dict)
                    
                    # Check for early termination conditions
                    if self._check_failure_criteria(metrics_collected):
                        logger.warning("Failure criteria triggered - stopping early")
                        break
                    
                    if self._check_success_criteria(metrics_collected):
                        logger.info("Success criteria met - stopping early")
                        break
                        
                except Exception as e:
                    logger.error(f"Error in iteration {iteration}: {e}")
                    return self._create_result(
                        ExperimentOutcome.ERROR,
                        metrics_collected,
                        error_message=str(e),
                        iterations_completed=iteration
                    )
            
            # Evaluate final result
            evaluation = self.registry.evaluate_experiment(self.experiment_id)
            
            # Determine outcome
            if evaluation.get("verdict") == "SUCCESS":
                outcome = ExperimentOutcome.SUCCESS
            elif evaluation.get("verdict") == "PARTIAL_SUCCESS":
                outcome = ExperimentOutcome.PARTIAL_SUCCESS
            elif evaluation.get("verdict") == "FAILED":
                outcome = ExperimentOutcome.FAILURE
            else:
                outcome = ExperimentOutcome.REJECTED
            
            return self._create_result(
                outcome,
                metrics_collected,
                evaluation_summary=evaluation,
                iterations_completed=len(metrics_collected)
            )
            
        except TimeoutError as e:
            logger.error(f"Experiment timed out: {e}")
            return self._create_result(
                ExperimentOutcome.TIMEOUT,
                metrics_collected,
                error_message=str(e)
            )
            
        finally:
            timeout_event.set()  # Signal timeout thread to stop
            self.end_time = datetime.now()
            self.registry.save_registry()
    
    def _check_success_criteria(self, metrics: List[TypedMetric]) -> bool:
        """Check if all success criteria are met"""
        if not self.success_criteria:
            return False
        
        for criterion_name, predicate in self.success_criteria.items():
            # Find latest metric with this name
            matching = [m for m in metrics if m.name == criterion_name]
            if not matching:
                return False  # Criteria not yet measured
            
            latest_value = matching[-1].value
            if not predicate(latest_value):
                return False  # Criteria not met
        
        return True  # All criteria met
    
    def _check_failure_criteria(self, metrics: List[TypedMetric]) -> bool:
        """Check if any failure criteria are triggered"""
        for criterion_name, predicate in self.failure_criteria.items():
            matching = [m for m in metrics if m.name == criterion_name]
            if matching:
                latest_value = matching[-1].value
                if predicate(latest_value):
                    return True  # Failure triggered
        
        return False
    
    def _create_result(self,
                      outcome: ExperimentOutcome,
                      metrics: List[TypedMetric],
                      error_message: Optional[str] = None,
                      iterations_completed: int = 0,
                      evaluation_summary: Optional[Dict[str, Any]] = None) -> ExperimentResult:
        """Create an ExperimentResult"""
        duration = 0.0
        if self.start_time and self.end_time:
            duration = (self.end_time - self.start_time).total_seconds()
        elif self.start_time:
            duration = (datetime.now() - self.start_time).total_seconds()
        
        return ExperimentResult(
            experiment_id=self.experiment_id,
            outcome=outcome,
            hypothesis=self.hypothesis,
            metrics=metrics,
            start_time=self.start_time.isoformat() if self.start_time else None,
            end_time=self.end_time.isoformat() if self.end_time else None,
            duration_seconds=duration,
            iterations_completed=iterations_completed,
            error_message=error_message,
            evaluation_summary=evaluation_summary
        )
    
    def interrupt(self):
        """Signal the experiment to stop after current iteration"""
        self._interrupted = True
        logger.info("Experiment interrupt signal received")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of experiment configuration"""
        return {
            "experiment_id": self.experiment_id,
            "name": self.name,
            "hypothesis": self.hypothesis,
            "success_criteria": list(self.success_criteria.keys()),
            "failure_criteria": list(self.failure_criteria.keys()),
            "max_iterations": self.max_iterations,
            "timeout_seconds": self.timeout_seconds,
            "status": "running" if self.start_time and not self.end_time else "pending"
        }


class ExperimentSuite:
    """
    A suite of bounded experiments that run sequentially or in parallel.
    
    Provides comprehensive benchmarking across multiple conditions.
    """
    
    def __init__(self, name: str, registry: Optional[MetricsRegistry] = None):
        """
        Initialize an experiment suite.
        
        Args:
            name: Suite name
            registry: Shared metrics registry
        """
        self.name = name
        self.registry = registry or MetricsRegistry()
        self.experiments: List[BoundedExperiment] = []
        self.results: List[ExperimentResult] = []
        
        logger.info(f"Created experiment suite: {name}")
    
    def add_experiment(self, experiment: BoundedExperiment):
        """Add an experiment to the suite"""
        self.experiments.append(experiment)
        logger.info(f"Added experiment {experiment.name} to suite {self.name}")
    
    def run_sequential(self, 
                      experiment_logic_map: Dict[str, Callable],
                      stop_on_failure: bool = True) -> List[ExperimentResult]:
        """
        Run all experiments sequentially.
        
        Args:
            experiment_logic_map: Map of experiment_name -> logic function
            stop_on_failure: Stop suite if any experiment fails
            
        Returns:
            List of ExperimentResults
        """
        logger.info(f"Running suite {self.name} sequentially ({len(self.experiments)} experiments)")
        
        self.results = []
        for experiment in self.experiments:
            if experiment.name not in experiment_logic_map:
                logger.error(f"No logic provided for experiment {experiment.name}")
                continue
            
            logic = experiment_logic_map[experiment.name]
            result = experiment.run(logic)
            self.results.append(result)
            
            logger.info(f"Experiment {experiment.name}: {result.outcome.value}")
            
            if stop_on_failure and result.outcome in [ExperimentOutcome.FAILURE, 
                                                       ExperimentOutcome.ERROR,
                                                       ExperimentOutcome.TIMEOUT]:
                logger.warning(f"Stopping suite due to failure in {experiment.name}")
                break
        
        return self.results
    
    def get_suite_summary(self) -> Dict[str, Any]:
        """Get summary of all experiment results"""
        if not self.results:
            return {"status": "not_run", "experiments": len(self.experiments)}
        
        outcomes = {}
        for result in self.results:
            outcome = result.outcome.value
            outcomes[outcome] = outcomes.get(outcome, 0) + 1
        
        total_duration = sum(r.duration_seconds for r in self.results)
        total_metrics = sum(len(r.metrics) for r in self.results)
        
        return {
            "suite_name": self.name,
            "total_experiments": len(self.experiments),
            "completed": len(self.results),
            "outcomes": outcomes,
            "total_duration_seconds": total_duration,
            "total_metrics_collected": total_metrics,
            "success_rate": outcomes.get("success", 0) / len(self.results) if self.results else 0
        }
    
    def export_results(self, output_path: Optional[str] = None) -> str:
        """Export all results to JSON"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"{self.name}_results_{timestamp}.json"
        
        data = {
            "suite_name": self.name,
            "export_timestamp": datetime.now().isoformat(),
            "summary": self.get_suite_summary(),
            "results": [r.to_dict() for r in self.results]
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Exported suite results to {output_path}")
        return output_path


# Pre-defined experiment templates
class ExperimentTemplates:
    """Templates for common QAGI precursor experiments"""
    
    @staticmethod
    def tesseract_efficiency_test(registry: Optional[MetricsRegistry] = None) -> BoundedExperiment:
        """Template for tesseract routing efficiency test"""
        return BoundedExperiment(
            name="Tesseract Efficiency Test",
            hypothesis="Tesseract routing improves route efficiency by >10% over flat routing",
            success_criteria=AcceptanceCriteria.tesseract_routing_success(),
            failure_criteria=AcceptanceCriteria.tesseract_routing_failure(),
            max_iterations=200,
            timeout_seconds=3600.0,
            registry=registry
        )
    
    @staticmethod
    def quantum_utility_test(registry: Optional[MetricsRegistry] = None) -> BoundedExperiment:
        """Template for quantum utility demonstration"""
        return BoundedExperiment(
            name="Quantum Utility Test",
            hypothesis="Quantum edge scoring provides measurable utility (>1.0) on routing tasks",
            success_criteria=AcceptanceCriteria.quantum_utility_success(),
            failure_criteria={
                "negative_utility": lambda x: x < 0.5,
                "high_overhead": lambda x: x > 10.0  # >10x overhead
            },
            max_iterations=100,
            timeout_seconds=1800.0,
            registry=registry
        )
    
    @staticmethod
    def biomimetic_emergence_test(registry: Optional[MetricsRegistry] = None) -> BoundedExperiment:
        """Template for biomimetic emergence demonstration"""
        return BoundedExperiment(
            name="Biomimetic Emergence Test",
            hypothesis="Biomimetic calibration demonstrates emergence (index > 0.5)",
            success_criteria=AcceptanceCriteria.biomimetic_emergence_success(),
            failure_criteria={
                "no_plasticity": lambda x: x < 0.1,
                "no_resilience": lambda x: x < 0.3,
                "collapse": lambda x: x < 0.0
            },
            max_iterations=50,
            timeout_seconds=3600.0,
            registry=registry
        )


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create a simple test experiment
    def dummy_experiment_logic(iteration: int, experiment: BoundedExperiment) -> Dict[str, Any]:
        """Dummy logic for testing"""
        import random
        return {
            "efficiency_improvement": {
                "value": 0.12 + random.gauss(0, 0.02),  # 12% improvement
                "type": MetricType.STRUCTURAL,
                "bounds": (0.0, 1.0),
                "confidence": 0.95
            },
            "robustness_improvement": {
                "value": 0.08 + random.gauss(0, 0.01),
                "type": MetricType.ROBUSTNESS,
                "bounds": (0.0, 1.0),
                "confidence": 0.90
            }
        }
    
    # Create and run experiment
    experiment = ExperimentTemplates.tesseract_efficiency_test()
    result = experiment.run(dummy_experiment_logic)
    
    print(f"\nExperiment Result:")
    print(f"Outcome: {result.outcome.value}")
    print(f"Duration: {result.duration_seconds:.2f}s")
    print(f"Iterations: {result.iterations_completed}")
    print(f"Metrics collected: {len(result.metrics)}")
    
    if result.evaluation_summary:
        print(f"\nEvaluation:")
        print(json.dumps(result.evaluation_summary, indent=2))
