import unittest
import time
import math
import sys
import os
import importlib

# Add the project root to the path to allow imports from other directories
# This allows finding the 'TMT-OS' directory.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Dynamically import the module from the 'TMT-OS' directory.
# Standard import syntax (from TMT-OS.node1_base_os) fails because of the hyphen.
try:
    node1_base_os_module = importlib.import_module("TMT-OS.node1_base_os")
    Node1BaseOS = node1_base_os_module.Node1BaseOS
    PHI = node1_base_os_module.PHI
except ImportError as e:
    # Provide a helpful error message if the module can't be found.
    raise ImportError(
        "Could not import Node1BaseOS. "
        "Ensure 'TMT-OS/node1_base_os.py' exists and the test is run from the project root."
    ) from e


class TestNode1BaseOS(unittest.TestCase):
    """Unit tests for the Node1BaseOS class."""

    def setUp(self):
        """Set up a new Node1BaseOS instance for each test."""
        self.node = Node1BaseOS()

    def test_initialization(self):
        """Test that the node initializes with correct default values."""
        self.assertEqual(self.node.NODE_ID, 1)
        self.assertEqual(self.node.NODE_NAME, "TMT-OS Base")
        self.assertEqual(self.node.PLATONIC_SOLID, "Cube")
        self.assertEqual(self.node.status, "active")
        self.assertIsNotNone(self.node.initialized_at)
        print("TestNode1BaseOS: test_initialization PASSED")

    def test_phi_constant(self):
        """Test that the phi constant is correct."""
        self.assertEqual(self.node.get_phi(), PHI)
        self.assertEqual(self.node.phi, (1 + math.sqrt(5)) / 2)
        print("TestNode1BaseOS: test_phi_constant PASSED")

    def test_geometry_info(self):
        """Test the geometry information of the cube."""
        geometry = self.node.get_geometry_info()
        self.assertEqual(geometry['faces'], 6)
        self.assertEqual(geometry['vertices'], 8)
        self.assertEqual(geometry['edges'], 12)
        self.assertEqual(self.node.GEOMETRY, geometry)
        print("TestNode1BaseOS: test_geometry_info PASSED")

    def test_health_status(self):
        """Test the health status reporting."""
        status = self.node.get_health_status()
        self.assertEqual(status['node_id'], 1)
        self.assertEqual(status['status'], 'active')
        self.assertEqual(status['platonic_solid'], 'Cube')
        self.assertGreater(status['uptime_seconds'], 0)
        self.assertEqual(status['phi'], PHI)
        print("TestNode1BaseOS: test_health_status PASSED")

    def test_uptime_calculation(self):
        """Test that uptime increases over time."""
        initial_status = self.node.get_health_status()
        time.sleep(0.1)
        next_status = self.node.get_health_status()
        self.assertGreater(next_status['uptime_seconds'], initial_status['uptime_seconds'])
        # Loosen the delta to account for system load variability
        self.assertAlmostEqual(next_status['uptime_seconds'] - initial_status['uptime_seconds'], 0.1, delta=0.08)
        print("TestNode1BaseOS: test_uptime_calculation PASSED")

if __name__ == '__main__':
    # This allows running the test script directly.
    print("Running tests for Node 1: TMT-OS Base OS...")
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestNode1BaseOS))
    runner = unittest.TextTestRunner()
    result = runner.run(suite)
    # Exit with a non-zero code if tests failed, for CI/CD purposes
    if result.failures or result.errors:
        sys.exit(1)
    print("All tests for Node 1 passed successfully.")
