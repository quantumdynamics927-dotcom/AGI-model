"""
Governance Layer - Typed Metrics Registry

Provides immutable typed metrics, bounded experiments, and reproducible registration
for all QAGI precursor stack experiments.

This module ensures scientific rigor by:
1. Typing all metrics (structural, task-facing, robustness, quantum, governance)
2. Bounding all experiments with pre-declared criteria
3. Registering full provenance for reproducibility
"""

import json
import hashlib
import time
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, Callable, List, Tuple
from enum import Enum
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Classification of metric types for the QAGI precursor stack"""
    STRUCTURAL = "structural"      # Route efficiency, density, diameter
    TASK_FACING = "task_facing"    # Accuracy, latency, calibration
    ROBUSTNESS = "robustness"      # Lesion performance, recovery
    QUANTUM = "quantum"            # Circuit depth, fidelity, utility
    GOVERNANCE = "governance"      # Reproducibility, traceability
    BIOMIMETIC = "biomimetic"      # Plasticity, resilience, emergence


class ExperimentStatus(Enum):
    """Status of an experiment in the governance lifecycle"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    REJECTED = "rejected"  # Did not meet acceptance criteria


@dataclass(frozen=True)
class TypedMetric:
    """
    Immutable typed metric with bounds and confidence.
    
    All metrics in the QAGI precursor stack must be typed, bounded,
    and carry confidence intervals for scientific validity.
    """
    name: str
    metric_type: MetricType
    value: float
    bounds: Tuple[float, float]  # (min, max) acceptable values
    confidence: float            # 0-1 confidence interval
    timestamp: str
    experiment_id: str
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        # Validate confidence is in valid range
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be in [0, 1], got {self.confidence}")
    
    def is_valid(self) -> bool:
        """Check if metric value is within acceptable bounds"""
        return self.bounds[0] <= self.value <= self.bounds[1]
    
    def is_significant(self, threshold: float = 0.05) -> bool:
        """Check if metric meets significance threshold"""
        return self.confidence >= (1 - threshold)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "name": self.name,
            "metric_type": self.metric_type.value,
            "value": self.value,
            "bounds": self.bounds,
            "confidence": self.confidence,
            "timestamp": self.timestamp,
            "experiment_id": self.experiment_id,
            "metadata": self.metadata or {},
            "is_valid": self.is_valid()
        }


@dataclass
class ExperimentRegistration:
    """
    Pre-registration of experiment parameters for reproducibility.
    
    Once registered, experiment parameters cannot be modified.
    This prevents p-hacking and ensures scientific validity.
    """
    experiment_id: str
    hypothesis: str
    success_criteria: Dict[str, Callable[[float], bool]]
    failure_criteria: Dict[str, Callable[[float], bool]]
    max_iterations: int
    timeout_seconds: float
    timestamp: str
    parameters_hash: str  # Hash of frozen parameters
    status: ExperimentStatus
    
    def __post_init__(self):
        # Compute hash of criteria for immutability verification
        criteria_str = json.dumps({
            "success": list(self.success_criteria.keys()),
            "failure": list(self.failure_criteria.keys()),
            "max_iter": self.max_iterations,
            "timeout": self.timeout_seconds
        }, sort_keys=True)
        object.__setattr__(self, 'parameters_hash', 
                          hashlib.sha256(criteria_str.encode()).hexdigest()[:16])
    
    def verify_integrity(self) -> bool:
        """Verify that parameters haven't been tampered with"""
        criteria_str = json.dumps({
            "success": list(self.success_criteria.keys()),
            "failure": list(self.failure_criteria.keys()),
            "max_iter": self.max_iterations,
            "timeout": self.timeout_seconds
        }, sort_keys=True)
        current_hash = hashlib.sha256(criteria_str.encode()).hexdigest()[:16]
        return current_hash == self.parameters_hash


class MetricsRegistry:
    """
    Central registry for all typed metrics in the QAGI precursor stack.
    
    Provides:
    - Metric registration and storage
    - Query and filtering capabilities
    - Export to various formats
    - Reproducibility verification
    """
    
    def __init__(self, registry_dir: str = "governance_registry"):
        self.registry_dir = Path(registry_dir)
        self.registry_dir.mkdir(exist_ok=True)
        self.metrics: Dict[str, List[TypedMetric]] = {}
        self.experiments: Dict[str, ExperimentRegistration] = {}
        self._load_existing_registry()
    
    def _load_existing_registry(self):
        """Load existing metrics from registry directory"""
        metrics_file = self.registry_dir / "metrics_registry.json"
        if metrics_file.exists():
            try:
                with open(metrics_file, 'r') as f:
                    data = json.load(f)
                    for exp_id, metrics_list in data.items():
                        self.metrics[exp_id] = [
                            TypedMetric(
                                name=m["name"],
                                metric_type=MetricType(m["metric_type"]),
                                value=m["value"],
                                bounds=tuple(m["bounds"]),
                                confidence=m["confidence"],
                                timestamp=m["timestamp"],
                                experiment_id=m["experiment_id"],
                                metadata=m.get("metadata", {})
                            )
                            for m in metrics_list
                        ]
                logger.info(f"Loaded {len(self.metrics)} experiments from registry")
            except Exception as e:
                logger.error(f"Failed to load registry: {e}")
    
    def register_experiment(self, 
                           hypothesis: str,
                           success_criteria: Dict[str, Callable[[float], bool]],
                           failure_criteria: Dict[str, Callable[[float], bool]],
                           max_iterations: int = 100,
                           timeout_seconds: float = 3600.0) -> str:
        """
        Pre-register an experiment with frozen parameters.
        
        Args:
            hypothesis: The hypothesis being tested
            success_criteria: Dict of metric_name -> predicate function
            failure_criteria: Dict of metric_name -> predicate function
            max_iterations: Maximum iterations allowed
            timeout_seconds: Timeout for experiment
            
        Returns:
            experiment_id: Unique identifier for this experiment
        """
        experiment_id = self._generate_experiment_id()
        timestamp = datetime.now().isoformat()
        
        registration = ExperimentRegistration(
            experiment_id=experiment_id,
            hypothesis=hypothesis,
            success_criteria=success_criteria,
            failure_criteria=failure_criteria,
            max_iterations=max_iterations,
            timeout_seconds=timeout_seconds,
            timestamp=timestamp,
            parameters_hash="",  # Will be computed in __post_init__
            status=ExperimentStatus.PENDING
        )
        
        self.experiments[experiment_id] = registration
        self.metrics[experiment_id] = []
        
        logger.info(f"Registered experiment {experiment_id}: {hypothesis}")
        return experiment_id
    
    def record_metric(self, metric: TypedMetric) -> bool:
        """
        Record a typed metric to the registry.
        
        Args:
            metric: The TypedMetric to record
            
        Returns:
            bool: True if metric was recorded successfully
        """
        if metric.experiment_id not in self.experiments:
            logger.error(f"Experiment {metric.experiment_id} not registered")
            return False
        
        if metric.experiment_id not in self.metrics:
            self.metrics[metric.experiment_id] = []
        
        self.metrics[metric.experiment_id].append(metric)
        
        if not metric.is_valid():
            logger.warning(f"Metric {metric.name} is out of bounds: "
                          f"{metric.value} not in {metric.bounds}")
        
        return True
    
    def evaluate_experiment(self, experiment_id: str) -> Dict[str, Any]:
        """
        Evaluate an experiment against its pre-registered criteria.
        
        Args:
            experiment_id: The experiment to evaluate
            
        Returns:
            Dict with evaluation results
        """
        if experiment_id not in self.experiments:
            return {"error": "Experiment not found"}
        
        registration = self.experiments[experiment_id]
        metrics = self.metrics.get(experiment_id, [])
        
        # Check integrity
        if not registration.verify_integrity():
            return {"error": "Experiment parameters have been tampered with"}
        
        # Evaluate success criteria
        success_results = {}
        for criterion_name, predicate in registration.success_criteria.items():
            # Find matching metric
            matching_metrics = [m for m in metrics if m.name == criterion_name]
            if matching_metrics:
                latest_value = matching_metrics[-1].value
                success_results[criterion_name] = {
                    "met": predicate(latest_value),
                    "value": latest_value
                }
            else:
                success_results[criterion_name] = {"met": False, "value": None}
        
        # Evaluate failure criteria
        failure_results = {}
        for criterion_name, predicate in registration.failure_criteria.items():
            matching_metrics = [m for m in metrics if m.name == criterion_name]
            if matching_metrics:
                latest_value = matching_metrics[-1].value
                failure_results[criterion_name] = {
                    "triggered": predicate(latest_value),
                    "value": latest_value
                }
            else:
                failure_results[criterion_name] = {"triggered": False, "value": None}
        
        # Overall assessment
        success_count = sum(1 for r in success_results.values() if r["met"])
        total_success = len(registration.success_criteria)
        failure_triggered = any(r["triggered"] for r in failure_results.values())
        
        if failure_triggered:
            status = ExperimentStatus.FAILED
            verdict = "FAILED"
        elif success_count == total_success:
            status = ExperimentStatus.COMPLETED
            verdict = "SUCCESS"
        elif success_count > 0:
            status = ExperimentStatus.COMPLETED
            verdict = "PARTIAL_SUCCESS"
        else:
            status = ExperimentStatus.REJECTED
            verdict = "REJECTED"
        
        return {
            "experiment_id": experiment_id,
            "hypothesis": registration.hypothesis,
            "status": status.value,
            "verdict": verdict,
            "success_criteria_met": f"{success_count}/{total_success}",
            "failure_criteria_triggered": failure_triggered,
            "success_details": success_results,
            "failure_details": failure_results,
            "metrics_count": len(metrics),
            "timestamp": datetime.now().isoformat()
        }
    
    def query_metrics(self, 
                     experiment_id: Optional[str] = None,
                     metric_type: Optional[MetricType] = None,
                     valid_only: bool = False) -> List[TypedMetric]:
        """
        Query metrics from the registry.
        
        Args:
            experiment_id: Filter by experiment (None = all)
            metric_type: Filter by metric type (None = all)
            valid_only: Only return metrics within bounds
            
        Returns:
            List of matching TypedMetric objects
        """
        results = []
        
        experiments_to_search = [experiment_id] if experiment_id else self.metrics.keys()
        
        for exp_id in experiments_to_search:
            if exp_id not in self.metrics:
                continue
            
            for metric in self.metrics[exp_id]:
                if metric_type and metric.metric_type != metric_type:
                    continue
                if valid_only and not metric.is_valid():
                    continue
                results.append(metric)
        
        return results
    
    def export_registry(self, output_path: Optional[str] = None) -> str:
        """
        Export the full registry to JSON.
        
        Args:
            output_path: Path for export (None = use default)
            
        Returns:
            Path to exported file
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.registry_dir / f"registry_export_{timestamp}.json"
        
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "experiments": {
                exp_id: {
                    "hypothesis": reg.hypothesis,
                    "status": reg.status.value,
                    "timestamp": reg.timestamp,
                    "parameters_hash": reg.parameters_hash
                }
                for exp_id, reg in self.experiments.items()
            },
            "metrics": {
                exp_id: [m.to_dict() for m in metrics]
                for exp_id, metrics in self.metrics.items()
            }
        }
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"Exported registry to {output_path}")
        return str(output_path)
    
    def save_registry(self):
        """Save registry to disk"""
        metrics_file = self.registry_dir / "metrics_registry.json"
        
        data = {
            exp_id: [m.to_dict() for m in metrics]
            for exp_id, metrics in self.metrics.items()
        }
        
        with open(metrics_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Saved registry with {len(self.metrics)} experiments")
    
    def _generate_experiment_id(self) -> str:
        """Generate unique experiment ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = hashlib.sha256(str(time.time()).encode()).hexdigest()[:8]
        return f"exp_{timestamp}_{random_suffix}"
    
    def get_experiment_summary(self, experiment_id: str) -> Dict[str, Any]:
        """Get summary of an experiment"""
        if experiment_id not in self.experiments:
            return {"error": "Experiment not found"}
        
        registration = self.experiments[experiment_id]
        metrics = self.metrics.get(experiment_id, [])
        
        # Group metrics by type
        metrics_by_type = {}
        for metric in metrics:
            if metric.metric_type.value not in metrics_by_type:
                metrics_by_type[metric.metric_type.value] = []
            metrics_by_type[metric.metric_type.value].append(metric.name)
        
        return {
            "experiment_id": experiment_id,
            "hypothesis": registration.hypothesis,
            "status": registration.status.value,
            "timestamp": registration.timestamp,
            "total_metrics": len(metrics),
            "metrics_by_type": metrics_by_type,
            "integrity_verified": registration.verify_integrity()
        }


# Pre-defined acceptance criteria for common experiments
class AcceptanceCriteria:
    """Pre-defined acceptance criteria for QAGI precursor experiments"""
    
    @staticmethod
    def tesseract_routing_success() -> Dict[str, Callable[[float], bool]]:
        """Success criteria for tesseract routing promotion"""
        return {
            "efficiency_improvement": lambda x: x > 0.10,  # > 10%
            "robustness_improvement": lambda x: x > 0.05,  # > 5%
            "accuracy_degradation": lambda x: x < 0.02,    # < 2%
            "calibration_stability": lambda x: x < 0.05,   # < 5%
            "statistical_significance": lambda x: x < 0.05 # p < 0.05
        }
    
    @staticmethod
    def tesseract_routing_failure() -> Dict[str, Callable[[float], bool]]:
        """Failure criteria for tesseract routing"""
        return {
            "accuracy_degradation": lambda x: x > 0.10,    # > 10% degradation
            "robustness_regression": lambda x: x < -0.05,  # > 5% regression
            "instability": lambda x: x > 0.20              # > 20% variance
        }
    
    @staticmethod
    def quantum_utility_success() -> Dict[str, Callable[[float], bool]]:
        """Success criteria for quantum utility demonstration"""
        return {
            "utility_score": lambda x: x > 1.0,           # Benefit > cost
            "task_speedup": lambda x: x > 0.05,           # > 5% speedup
            "fidelity_threshold": lambda x: x > 0.7       # > 70% fidelity
        }
    
    @staticmethod
    def biomimetic_emergence_success() -> Dict[str, Callable[[float], bool]]:
        """Success criteria for biomimetic emergence"""
        return {
            "emergence_index": lambda x: x > 0.5,           # Emergence > 0.5
            "resilience_score": lambda x: x > 0.6,         # Resilience > 0.6
            "plasticity_in_range": lambda x: 0.2 <= x <= 0.8,  # Plasticity in range
            "integration_score": lambda x: x > 0.4          # Integration > 0.4
        }


# Convenience functions for common operations
def create_metric(name: str,
                 metric_type: MetricType,
                 value: float,
                 bounds: Tuple[float, float],
                 experiment_id: str,
                 confidence: float = 0.95,
                 metadata: Optional[Dict[str, Any]] = None) -> TypedMetric:
    """
    Convenience function to create a TypedMetric.
    
    Args:
        name: Metric name
        metric_type: Type of metric
        value: Measured value
        bounds: (min, max) acceptable values
        experiment_id: Associated experiment
        confidence: Confidence level (0-1)
        metadata: Additional metadata
        
    Returns:
        TypedMetric instance
    """
    return TypedMetric(
        name=name,
        metric_type=metric_type,
        value=value,
        bounds=bounds,
        confidence=confidence,
        timestamp=datetime.now().isoformat(),
        experiment_id=experiment_id,
        metadata=metadata
    )


# Example usage and testing
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Create registry
    registry = MetricsRegistry()
    
    # Register an experiment
    exp_id = registry.register_experiment(
        hypothesis="Tesseract routing improves efficiency by >10%",
        success_criteria=AcceptanceCriteria.tesseract_routing_success(),
        failure_criteria=AcceptanceCriteria.tesseract_routing_failure(),
        max_iterations=200,
        timeout_seconds=3600.0
    )
    
    print(f"Registered experiment: {exp_id}")
    
    # Record some metrics
    registry.record_metric(create_metric(
        name="efficiency_improvement",
        metric_type=MetricType.STRUCTURAL,
        value=0.12,  # 12% improvement
        bounds=(0.0, 1.0),
        experiment_id=exp_id,
        confidence=0.95
    ))
    
    registry.record_metric(create_metric(
        name="robustness_improvement",
        metric_type=MetricType.ROBUSTNESS,
        value=0.08,  # 8% improvement
        bounds=(0.0, 1.0),
        experiment_id=exp_id,
        confidence=0.90
    ))
    
    # Evaluate experiment
    result = registry.evaluate_experiment(exp_id)
    print(f"\nEvaluation result:")
    print(json.dumps(result, indent=2))
    
    # Query metrics
    structural_metrics = registry.query_metrics(
        metric_type=MetricType.STRUCTURAL
    )
    print(f"\nStructural metrics: {len(structural_metrics)}")
    
    # Export registry
    export_path = registry.export_registry()
    print(f"\nExported registry to: {export_path}")
    
    # Save registry
    registry.save_registry()
    print("\nRegistry saved successfully")
