"""
Node 3: TMT-OS Labs (Icosahedron)

This module implements the experimental labs for the TMT-OS, mapped to the Icosahedron.
It provides A/B testing frameworks, research tracking, and integration testing utilities.
"""
import json
import logging
import time
import math
from pathlib import Path
from typing import Dict, Any, List, Optional
import random

# Configure logging for the node
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(ch)

# --- Core Constants ---
PHI = (1 + math.sqrt(5)) / 2

class Node3ExperimentalLabs:
    """
    Implements the functionality for Node 3, the TMT-OS Labs, associated
    with the Icosahedron platonic solid.
    """
    NODE_ID = 3
    NODE_NAME = "TMT-OS Labs"
    PLATONIC_SOLID = "Icosahedron"
    GEOMETRY = {
        'faces': 20,
        'vertices': 12,
        'edges': 30
    }

    def __init__(self, experiments_dir: str = "TMT-OS-Labs/experiments"):
        """Initializes the Node 3 instance."""
        self.experiments_dir = Path(experiments_dir)
        self.experiments_dir.mkdir(parents=True, exist_ok=True)
        self.status = "initializing"
        self.initialized_at: float | None = None
        self.phi = PHI
        self.active_experiments: Dict[str, Dict[str, Any]] = {}
        self._initialize_system()

    def _initialize_system(self):
        """Private method to perform system initialization."""
        logger.info(f"Initializing {self.NODE_NAME} (Node {self.NODE_ID}, {self.PLATONIC_SOLID})...")
        # Load existing experiments
        self._load_experiments()
        self.initialized_at = time.time()
        self.status = "active"
        logger.info(f"{self.NODE_NAME} initialized successfully.")

    def _load_experiments(self):
        """Load existing experiments from disk."""
        experiments_file = self.experiments_dir / "experiments.json"
        if experiments_file.exists():
            try:
                with open(experiments_file, 'r') as f:
                    self.active_experiments = json.load(f)
                logger.info(f"Loaded {len(self.active_experiments)} existing experiments")
            except json.JSONDecodeError:
                logger.warning("Failed to load experiments file, starting fresh")

    def _save_experiments(self):
        """Save experiments to disk."""
        experiments_file = self.experiments_dir / "experiments.json"
        try:
            with open(experiments_file, 'w') as f:
                json.dump(self.active_experiments, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save experiments: {e}")

    def create_experiment(self, name: str, description: str, variants: List[str],
                         metrics: List[str], duration_days: int = 7) -> str:
        """
        Create a new A/B testing experiment.

        Args:
            name: Experiment name
            description: Experiment description
            variants: List of variant names (e.g., ['control', 'treatment'])
            metrics: List of metrics to track
            duration_days: How long to run the experiment

        Returns:
            Experiment ID
        """
        experiment_id = f"exp_{int(time.time())}_{name.replace(' ', '_')}"

        experiment = {
            'id': experiment_id,
            'name': name,
            'description': description,
            'variants': variants,
            'metrics': metrics,
            'duration_days': duration_days,
            'created_at': time.time(),
            'status': 'active',
            'results': {variant: {metric: [] for metric in metrics} for variant in variants},
            'phi_weighted_score': 0.0
        }

        self.active_experiments[experiment_id] = experiment
        self._save_experiments()

        logger.info(f"Created experiment: {name} (ID: {experiment_id})")
        return experiment_id

    def record_measurement(self, experiment_id: str, variant: str,
                          metric: str, value: float, metadata: Dict[str, Any] = None) -> bool:
        """
        Record a measurement for an experiment.

        Args:
            experiment_id: The experiment ID
            variant: Which variant this measurement is for
            metric: Which metric is being measured
            value: The measured value
            metadata: Optional metadata about the measurement

        Returns:
            True if recorded successfully, False otherwise
        """
        if experiment_id not in self.active_experiments:
            logger.error(f"Experiment {experiment_id} not found")
            return False

        experiment = self.active_experiments[experiment_id]

        if variant not in experiment['variants']:
            logger.error(f"Variant {variant} not in experiment {experiment_id}")
            return False

        if metric not in experiment['metrics']:
            logger.error(f"Metric {metric} not in experiment {experiment_id}")
            return False

        measurement = {
            'timestamp': time.time(),
            'value': value,
            'metadata': metadata or {}
        }

        experiment['results'][variant][metric].append(measurement)

        # Update phi-weighted score
        experiment['phi_weighted_score'] = self._calculate_phi_score(experiment)

        self._save_experiments()
        logger.debug(f"Recorded measurement for {experiment_id}: {variant}.{metric} = {value}")
        return True

    def _calculate_phi_score(self, experiment: Dict[str, Any]) -> float:
        """Calculate a phi-weighted score for experiment significance."""
        total_measurements = 0
        weighted_sum = 0

        for variant_results in experiment['results'].values():
            for metric_results in variant_results.values():
                for measurement in metric_results:
                    weight = 1 / (PHI ** (time.time() - measurement['timestamp']) / 86400)  # Decay by days
                    weighted_sum += measurement['value'] * weight
                    total_measurements += 1

        return weighted_sum / total_measurements if total_measurements > 0 else 0

    def get_experiment_results(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        """
        Get results for a specific experiment.

        Args:
            experiment_id: The experiment ID

        Returns:
            Experiment results or None if not found
        """
        if experiment_id not in self.active_experiments:
            return None

        experiment = self.active_experiments[experiment_id]

        # Calculate statistics for each variant/metric
        results_summary = {}
        for variant, metrics_data in experiment['results'].items():
            results_summary[variant] = {}
            for metric, measurements in metrics_data.items():
                if measurements:
                    values = [m['value'] for m in measurements]
                    results_summary[variant][metric] = {
                        'count': len(values),
                        'mean': sum(values) / len(values),
                        'min': min(values),
                        'max': max(values),
                        'latest': values[-1]
                    }
                else:
                    results_summary[variant][metric] = {'count': 0}

        return {
            'experiment': experiment,
            'summary': results_summary,
            'is_conclusive': self._is_experiment_conclusive(experiment)
        }

    def _is_experiment_conclusive(self, experiment: Dict[str, Any]) -> bool:
        """Determine if an experiment has enough data to be conclusive."""
        min_measurements = 10  # Minimum measurements per variant per metric
        min_days = 1  # Minimum days of data

        elapsed_days = (time.time() - experiment['created_at']) / 86400

        if elapsed_days < min_days:
            return False

        for variant_results in experiment['results'].values():
            for measurements in variant_results.values():
                if len(measurements) < min_measurements:
                    return False

        return True

    def run_integration_test(self, test_name: str, test_function: callable,
                           *args, **kwargs) -> Dict[str, Any]:
        """
        Run an integration test and record results.

        Args:
            test_name: Name of the test
            test_function: Function to run
            *args, **kwargs: Arguments for the test function

        Returns:
            Test results
        """
        start_time = time.time()
        success = False
        error_message = None
        result_data = None

        try:
            result_data = test_function(*args, **kwargs)
            success = True
            logger.info(f"Integration test '{test_name}' passed")
        except Exception as e:
            error_message = str(e)
            logger.error(f"Integration test '{test_name}' failed: {e}")

        end_time = time.time()
        duration = end_time - start_time

        test_result = {
            'test_name': test_name,
            'timestamp': start_time,
            'duration_seconds': duration,
            'success': success,
            'error_message': error_message,
            'result_data': result_data
        }

        # Save test result
        tests_dir = self.experiments_dir / "integration_tests"
        tests_dir.mkdir(exist_ok=True)
        test_file = tests_dir / f"{test_name}_{int(start_time)}.json"
        with open(test_file, 'w') as f:
            json.dump(test_result, f, indent=2)

        return test_result

    def get_health_status(self) -> Dict[str, Any]:
        """
        Returns the current health, status, and metadata of the node.
        """
        if self.initialized_at is None:
            uptime = 0
            self.status = "failed_initialization"
        else:
            uptime = time.time() - self.initialized_at

        return {
            'node_id': self.NODE_ID,
            'node_name': self.NODE_NAME,
            'status': self.status,
            'platonic_solid': self.PLATONIC_SOLID,
            'geometry': self.GEOMETRY,
            'phi': self.phi,
            'initialized_at': self.initialized_at,
            'uptime_seconds': uptime,
            'active_experiments': len(self.active_experiments),
            'experiments_dir': str(self.experiments_dir)
        }

    def get_geometry_info(self) -> Dict[str, int]:
        """Returns the geometric properties of the node's platonic solid."""
        return self.GEOMETRY


# --- Standalone Execution Example ---
if __name__ == '__main__':
    """
    Demonstrates the basic functionality of the Node3ExperimentalLabs class.
    """
    logger.info("--- Running Node 3 Experimental Labs Standalone Demo ---")

    # Instantiate the node
    node3 = Node3ExperimentalLabs()

    # Get and print health status
    health_status = node3.get_health_status()
    logger.info(f"Current Health Status: {health_status}")

    # Create a sample experiment
    exp_id = node3.create_experiment(
        name="Quantum Consciousness Enhancement",
        description="Testing phi-based consciousness metrics",
        variants=["control", "phi_enhanced"],
        metrics=["consciousness_level", "stability"],
        duration_days=7
    )

    # Record some sample measurements
    for i in range(20):
        # Simulate measurements for both variants
        control_level = 0.7 + random.random() * 0.2
        phi_level = 0.8 + random.random() * 0.3

        node3.record_measurement(exp_id, "control", "consciousness_level", control_level)
        node3.record_measurement(exp_id, "phi_enhanced", "consciousness_level", phi_level)

        control_stability = 0.8 + random.random() * 0.15
        phi_stability = 0.85 + random.random() * 0.2

        node3.record_measurement(exp_id, "control", "stability", control_stability)
        node3.record_measurement(exp_id, "phi_enhanced", "stability", phi_stability)

    # Get experiment results
    results = node3.get_experiment_results(exp_id)
    if results:
        logger.info(f"Experiment Results: {results['summary']}")
        logger.info(f"Is Conclusive: {results['is_conclusive']}")

    # Run a sample integration test
    def sample_test():
        return {"test_metric": 0.95, "status": "passed"}

    test_result = node3.run_integration_test("sample_integration_test", sample_test)
    logger.info(f"Integration Test Result: {test_result}")

    logger.info("--- Node 3 Demo Finished ---")