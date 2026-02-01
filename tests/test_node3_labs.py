"""
Tests for Node 3: TMT-OS Labs (Icosahedron)

This module contains unit tests for the experimental labs functionality.
"""
import unittest
import tempfile
import shutil
import json
import time
import math
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import the node module
import sys
sys.path.append('TMT-OS-Labs')
from node3_experimental_labs import Node3ExperimentalLabs

class TestNode3ExperimentalLabs(unittest.TestCase):
    """Test cases for Node 3 Experimental Labs functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.node = Node3ExperimentalLabs(experiments_dir=self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_initialization(self):
        """Test node initialization."""
        self.assertEqual(self.node.NODE_ID, 3)
        self.assertEqual(self.node.NODE_NAME, "TMT-OS Labs")
        self.assertEqual(self.node.PLATONIC_SOLID, "Icosahedron")
        self.assertEqual(self.node.GEOMETRY['faces'], 20)
        self.assertEqual(self.node.GEOMETRY['vertices'], 12)
        self.assertEqual(self.node.GEOMETRY['edges'], 30)
        self.assertEqual(self.node.status, "active")
        self.assertIsNotNone(self.node.initialized_at)
        self.assertAlmostEqual(self.node.phi, (1 + math.sqrt(5)) / 2, places=5)

    def test_geometry_info(self):
        """Test geometry information retrieval."""
        geometry = self.node.get_geometry_info()
        self.assertEqual(geometry['faces'], 20)
        self.assertEqual(geometry['vertices'], 12)
        self.assertEqual(geometry['edges'], 30)

    def test_health_status(self):
        """Test health status reporting."""
        status = self.node.get_health_status()
        self.assertEqual(status['node_id'], 3)
        self.assertEqual(status['node_name'], "TMT-OS Labs")
        self.assertEqual(status['status'], "active")
        self.assertEqual(status['platonic_solid'], "Icosahedron")
        self.assertIn('geometry', status)
        self.assertIn('phi', status)
        self.assertIn('initialized_at', status)
        self.assertIn('uptime_seconds', status)
        self.assertGreater(status['uptime_seconds'], 0)

    def test_create_experiment(self):
        """Test experiment creation."""
        exp_id = self.node.create_experiment(
            name="Test Experiment",
            description="A test experiment",
            variants=["A", "B"],
            metrics=["metric1", "metric2"],
            duration_days=5
        )

        self.assertIn(exp_id, self.node.active_experiments)
        experiment = self.node.active_experiments[exp_id]
        self.assertEqual(experiment['name'], "Test Experiment")
        self.assertEqual(experiment['description'], "A test experiment")
        self.assertEqual(experiment['variants'], ["A", "B"])
        self.assertEqual(experiment['metrics'], ["metric1", "metric2"])
        self.assertEqual(experiment['duration_days'], 5)
        self.assertEqual(experiment['status'], 'active')
        self.assertIn('created_at', experiment)

    def test_record_measurement(self):
        """Test recording measurements."""
        exp_id = self.node.create_experiment(
            name="Measurement Test",
            description="Test measurements",
            variants=["control", "test"],
            metrics=["accuracy"]
        )

        # Record a measurement
        success = self.node.record_measurement(exp_id, "control", "accuracy", 0.85)
        self.assertTrue(success)

        # Check the measurement was recorded
        experiment = self.node.active_experiments[exp_id]
        measurements = experiment['results']['control']['accuracy']
        self.assertEqual(len(measurements), 1)
        self.assertEqual(measurements[0]['value'], 0.85)
        self.assertIn('timestamp', measurements[0])

    def test_record_measurement_invalid_experiment(self):
        """Test recording measurement for invalid experiment."""
        success = self.node.record_measurement("invalid_exp", "control", "accuracy", 0.85)
        self.assertFalse(success)

    def test_record_measurement_invalid_variant(self):
        """Test recording measurement for invalid variant."""
        exp_id = self.node.create_experiment(
            name="Test",
            description="Test",
            variants=["A", "B"],
            metrics=["accuracy"]
        )

        success = self.node.record_measurement(exp_id, "invalid_variant", "accuracy", 0.85)
        self.assertFalse(success)

    def test_record_measurement_invalid_metric(self):
        """Test recording measurement for invalid metric."""
        exp_id = self.node.create_experiment(
            name="Test",
            description="Test",
            variants=["A", "B"],
            metrics=["accuracy"]
        )

        success = self.node.record_measurement(exp_id, "A", "invalid_metric", 0.85)
        self.assertFalse(success)

    def test_get_experiment_results(self):
        """Test getting experiment results."""
        exp_id = self.node.create_experiment(
            name="Results Test",
            description="Test results",
            variants=["A", "B"],
            metrics=["score"]
        )

        # Record some measurements
        self.node.record_measurement(exp_id, "A", "score", 0.8)
        self.node.record_measurement(exp_id, "A", "score", 0.9)
        self.node.record_measurement(exp_id, "B", "score", 0.7)
        self.node.record_measurement(exp_id, "B", "score", 0.85)

        results = self.node.get_experiment_results(exp_id)
        self.assertIsNotNone(results)
        self.assertIn('experiment', results)
        self.assertIn('summary', results)

        summary = results['summary']
        self.assertIn('A', summary)
        self.assertIn('B', summary)
        self.assertIn('score', summary['A'])
        self.assertIn('score', summary['B'])

        # Check statistics
        a_stats = summary['A']['score']
        self.assertEqual(a_stats['count'], 2)
        self.assertAlmostEqual(a_stats['mean'], 0.85, places=2)
        self.assertEqual(a_stats['min'], 0.8)
        self.assertEqual(a_stats['max'], 0.9)

    def test_get_experiment_results_invalid(self):
        """Test getting results for invalid experiment."""
        results = self.node.get_experiment_results("invalid_exp")
        self.assertIsNone(results)

    def test_run_integration_test_success(self):
        """Test running a successful integration test."""
        def test_func():
            return {"result": "success"}

        result = self.node.run_integration_test("test_success", test_func)

        self.assertEqual(result['test_name'], "test_success")
        self.assertTrue(result['success'])
        self.assertIsNone(result['error_message'])
        self.assertEqual(result['result_data'], {"result": "success"})
        self.assertIn('timestamp', result)
        self.assertIn('duration_seconds', result)

    def test_run_integration_test_failure(self):
        """Test running a failing integration test."""
        def failing_test():
            raise ValueError("Test failed")

        result = self.node.run_integration_test("test_failure", failing_test)

        self.assertEqual(result['test_name'], "test_failure")
        self.assertFalse(result['success'])
        self.assertEqual(result['error_message'], "Test failed")
        self.assertIn('timestamp', result)
        self.assertIn('duration_seconds', result)

    def test_experiment_persistence(self):
        """Test that experiments are persisted and loaded correctly."""
        # Create experiment in one instance
        exp_id = self.node.create_experiment(
            name="Persistence Test",
            description="Test persistence",
            variants=["X", "Y"],
            metrics=["value"]
        )

        # Create new instance with same directory
        node2 = Node3ExperimentalLabs(experiments_dir=self.temp_dir)

        # Check that experiment was loaded
        self.assertIn(exp_id, node2.active_experiments)
        experiment = node2.active_experiments[exp_id]
        self.assertEqual(experiment['name'], "Persistence Test")

    def test_phi_weighted_score(self):
        """Test phi-weighted scoring calculation."""
        exp_id = self.node.create_experiment(
            name="Phi Test",
            description="Test phi scoring",
            variants=["test"],
            metrics=["value"]
        )

        # Record a measurement
        self.node.record_measurement(exp_id, "test", "value", 1.0)

        experiment = self.node.active_experiments[exp_id]
        self.assertGreater(experiment['phi_weighted_score'], 0)


if __name__ == '__main__':
    unittest.main()