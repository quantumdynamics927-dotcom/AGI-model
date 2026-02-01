import unittest
import sys
import os
import time
import numpy as np
from unittest.mock import MagicMock, patch

# Add project root to the path for module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock the qiskit library before importing qvae_bridge. This is crucial
# because qiskit is not a guaranteed dependency in the test environment.
class MockQuantumCircuit:
    """A mock of qiskit.QuantumCircuit with just enough functionality for tests to run."""
    def __init__(self, num_qubits, name="mock_qc"):
        self.num_qubits = num_qubits
        self.name = name
        self.instructions = []

    def h(self, i): self.instructions.append(f"h({i})")
    def ry(self, angle, i): self.instructions.append(f"ry({angle}, {i})")
    def barrier(self): self.instructions.append("barrier")

# We apply the mock to sys.modules so that any 'import qiskit' call uses our mock.
sys.modules['qiskit'] = MagicMock()
sys.modules['qiskit'].QuantumCircuit = MockQuantumCircuit
sys.modules['qiskit'].QuantumRegister = MagicMock()

# Now we can safely import the module to be tested
from qvae_bridge import QVAEBridge, get_bridge

class TestQVAEBridge(unittest.TestCase):
    """Unit tests for the enhanced QVAEBridge class."""

    def setUp(self):
        """Get a fresh bridge instance for each test."""
        # The bridge uses a singleton pattern, so we must reset it for test isolation
        qvae_bridge_module = sys.modules['qvae_bridge']
        qvae_bridge_module._BRIDGE_INSTANCE = None
        self.bridge = get_bridge()

    def test_initialization(self):
        """Test that the bridge initializes correctly with all its components."""
        self.assertEqual(self.bridge.node_id, 9)
        self.assertEqual(self.bridge.platonic_solid, 'Merkabah')
        self.assertIsNotNone(self.bridge.mock_backend)
        self.assertIsInstance(self.bridge.jobs, dict)
        print("TestNode9: test_initialization PASSED")

    def test_map_classical_to_quantum(self):
        """Test the mapping from a classical vector to a quantum circuit object."""
        latent_vector = [0.1, -0.5, 0.9, 0.0]
        circuit = self.bridge.map_classical_to_quantum(latent_vector)
        
        self.assertIsInstance(circuit, MockQuantumCircuit)
        self.assertEqual(circuit.num_qubits, 127) # Check against the default
        self.assertGreater(len(circuit.instructions), 127, "Circuit should have instructions applied.")
        print("TestNode9: test_map_classical_to_quantum PASSED")

    @patch('qvae_bridge.QVAEBridge._import_qiskit', return_value=(None, None))
    def test_map_classical_to_quantum_no_qiskit(self, mock_import):
        """Test that the mapping function returns an error when qiskit is not available."""
        latent_vector = [0.1, -0.5]
        # Re-initialize bridge to use the patched import that simulates qiskit's absence
        bridge_no_qiskit = QVAEBridge()
        result = bridge_no_qiskit.map_classical_to_quantum(latent_vector)
        self.assertEqual(result, {"error": "Qiskit not available"})
        print("TestNode9: test_map_classical_to_quantum_no_qiskit PASSED")
        
    def test_job_submission_and_lifecycle(self):
        """Test the full lifecycle of a job: submit -> queued -> running -> completed."""
        latent_vector = np.random.rand(5).tolist()
        circuit = self.bridge.map_classical_to_quantum(latent_vector)
        self.assertIsNotNone(circuit)

        # 1. Submit the job
        job_id = self.bridge.submit_job(circuit)
        self.assertIn(job_id, self.bridge.jobs)
        
        # 2. Check initial status (should be queued)
        initial_status = self.bridge.get_job_status(job_id)
        self.assertEqual(initial_status['status'], 'queued')

        # 3. Poll for completion (with a timeout)
        timeout = 5  # seconds
        start_time = time.time()
        final_status_info = None
        while time.time() - start_time < timeout:
            status_info = self.bridge.get_job_status(job_id)
            if status_info['status'] == 'completed':
                final_status_info = status_info
                break
            time.sleep(0.2)
        
        self.assertIsNotNone(final_status_info, "Job did not complete within the 5-second timeout.")
        self.assertEqual(final_status_info['status'], 'completed')
        self.assertIn('result', final_status_info)
        self.assertIsInstance(final_status_info['result'], dict, "Job result should be a dictionary of counts.")
        self.assertGreater(len(final_status_info['result']), 0, "Job result should contain measurement counts.")
        print("TestNode9: test_job_submission_and_lifecycle PASSED")

    def test_get_job_status_invalid_id(self):
        """Test retrieving the status for a non-existent job ID returns None."""
        status = self.bridge.get_job_status('invalid-job-id')
        self.assertIsNone(status)
        print("TestNode9: test_get_job_status_invalid_id PASSED")

if __name__ == '__main__':
    print("Running tests for Node 9: QVAE Bridge...")
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestQVAEBridge))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if result.failures or result.errors:
        print("Node 9 tests failed.")
        sys.exit(1)
    print("All tests for Node 9 passed successfully.")