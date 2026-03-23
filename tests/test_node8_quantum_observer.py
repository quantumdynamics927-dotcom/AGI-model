import unittest
import importlib
import sys
import os
import importlib.util
from pathlib import Path

import pytest

# Add project root to path to allow importing node modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Mock heavy dependencies (qiskit) before importing other modules
from unittest.mock import MagicMock

sys.modules["qiskit"] = MagicMock()

MODULE_PATH = Path(__file__).resolve().parents[1] / "TMT-OS" / "node4_nft_layer.py"
if not MODULE_PATH.exists():
    pytest.skip(
        "TMT-OS/node4_nft_layer.py not present in this repo", allow_module_level=True
    )

Node8QuantumObserver = importlib.import_module(
    "quantum_observer.node8_chain_monitor"
).Node8QuantumObserver

spec = importlib.util.spec_from_file_location("node4_nft_layer", MODULE_PATH)
node4_module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(node4_module)
Node4NFTLayer = node4_module.Node4NFTLayer
get_bridge = importlib.import_module("qvae_bridge").get_bridge


class TestNode8QuantumObserver(unittest.TestCase):
    """Unit tests for the Node8QuantumObserver, testing its monitoring capabilities."""

    def setUp(self):
        """Set up instances of the observer and the nodes it depends on for each test."""
        # The QVAE bridge uses a singleton, so it must be reset for test isolation
        if "qvae_bridge" in sys.modules:
            sys.modules["qvae_bridge"]._BRIDGE_INSTANCE = None

        self.node4 = Node4NFTLayer()
        self.node9 = get_bridge()
        self.observer = Node8QuantumObserver(
            nft_layer_node=self.node4, qvae_bridge_node=self.node9
        )

    def test_initialization_and_listener_registration(self):
        """Test that the observer initializes correctly and registers itself as a listener to the blockchain."""
        self.assertEqual(self.observer.NODE_ID, 8)
        self.assertEqual(self.observer.NODE_NAME, "Quantum Observer")
        # Check that the observer instance was successfully added to the blockchain's list of listeners
        self.assertIn(self.observer, self.node4.blockchain.listeners)
        print("TestNode8: test_initialization_and_listener_registration PASSED")

    def test_on_mint_event_triggers_notification(self):
        """Test that a mint event on Node 4 correctly triggers the on_mint_event callback and sends a notification."""
        initial_notification_count = len(self.observer.notifications)

        # Trigger a mint event by having Node 4 create a new asset
        self.node4.create_asset("0xTestOwner123", {"name": "Observable Mint Event"})

        # Check that the observer's notification count has increased by one
        self.assertEqual(
            len(self.observer.notifications), initial_notification_count + 1
        )
        last_notification = self.observer.notifications[-1]
        self.assertIn("MINT_CONFIRMATION", last_notification)
        self.assertIn("Token ID 0", last_notification)
        self.assertIn("0xTestOwner123", last_notification)
        print("TestNode8: test_on_mint_event_triggers_notification PASSED")

    def test_detect_quantum_collapse_logic(self):
        """Test the quantum collapse detection logic with both collapsed and superpositioned states."""
        # 1. Test a "collapsed" state where one outcome is highly probable
        collapsed_job_id = "job_collapsed_state"
        self.node9.jobs[collapsed_job_id] = {
            "status": "completed",
            "result": {"10101": 950, "01010": 50},
        }

        # The observer should detect a collapse
        self.assertTrue(
            self.observer.detect_quantum_collapse(
                collapsed_job_id, collapse_threshold=0.9
            )
        )
        # A notification for the collapse should have been sent
        self.assertIn("QUANTUM_COLLAPSE", self.observer.notifications[-1])
        self.assertIn("State '10101'", self.observer.notifications[-1])

        # 2. Test a "superposition" state where outcomes are balanced
        superposed_job_id = "job_superposed_state"
        self.node9.jobs[superposed_job_id] = {
            "status": "completed",
            "result": {"10101": 505, "01010": 495},
        }

        # The observer should NOT detect a collapse here
        self.assertFalse(
            self.observer.detect_quantum_collapse(
                superposed_job_id, collapse_threshold=0.9
            )
        )
        print("TestNode8: test_detect_quantum_collapse_logic PASSED")

    def test_detect_collapse_on_incomplete_job(self):
        """Test that collapse detection correctly returns False for jobs that are not yet complete."""
        incomplete_job_id = "job_still_running"
        self.node9.jobs[incomplete_job_id] = {"status": "running"}

        self.assertFalse(self.observer.detect_quantum_collapse(incomplete_job_id))
        print("TestNode8: test_detect_collapse_on_incomplete_job PASSED")

    def test_health_status_payload(self):
        """Test that the health status payload is accurate and updates correctly."""
        health = self.observer.get_health_status()
        self.assertEqual(health["node_id"], 8)
        self.assertEqual(health["status"], "active")
        self.assertEqual(health["notifications_sent"], 0)

        # Trigger an event that sends a notification
        self.node4.create_asset("0xHealthCheckOwner", {"name": "Health Check Asset"})

        # The health status should now reflect the new notification
        next_health = self.observer.get_health_status()
        self.assertEqual(next_health["notifications_sent"], 1)
        print("TestNode8: test_health_status_payload PASSED")


if __name__ == "__main__":
    print("Running tests for Node 8: Quantum Observer...")
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestNode8QuantumObserver))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if result.failures or result.errors:
        print("Node 8 tests failed.")
        sys.exit(1)
    print("All tests for Node 8 passed successfully.")
