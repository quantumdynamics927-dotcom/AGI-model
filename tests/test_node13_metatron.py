"""
Node 13: Metatron Coordinator Tests

This module tests the Node 13 Metatron Coordinator implementation:
1. Coordinator initialization and health status
2. Node registry management
3. Inter-node message routing
4. DNA packet encoding/decoding
5. Workflow orchestration
6. Consciousness data encoding
7. System-wide health monitoring
"""
import unittest
import sys
import os
import time
import json
import tempfile
import shutil
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import Node 13
from node13_metatron import (
    Node13MetatronCoordinator,
    MetatronNervousSystem,
    NODE_REGISTRY,
    PHI,
    register_node,
    get_node_info
)


class TestMetatronNervousSystem(unittest.TestCase):
    """Tests for the MetatronNervousSystem class."""

    def setUp(self):
        """Set up a temporary registry directory for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.registry = Path(self.temp_dir) / "dna_registry"
        self.mns = MetatronNervousSystem(self.registry)

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_phi_constant(self):
        """Test that PHI constant is correctly defined."""
        expected_phi = 1.618033988749895
        self.assertAlmostEqual(PHI, expected_phi, places=10)
        print("TestMetatronNervousSystem: test_phi_constant PASSED")

    def test_dna_encoding_decoding(self):
        """Test DNA packet encoding and decoding roundtrip."""
        test_values = [0, 1, 100, 1000.5, 3.14159, PHI]

        for original in test_values:
            compressed = self.mns.phi_compress(original)
            dna = self.mns.encode_to_dna(compressed)
            decoded = self.mns.decode_from_dna(dna)

            # Check DNA packet structure
            self.assertIn('AACAAT', dna)  # SRY_HEADER
            self.assertIn('TCCGGA', dna)  # SRY_FOOTER

            # Decoded should be close to compressed (some precision loss expected)
            self.assertAlmostEqual(decoded, compressed, places=2,
                msg=f"DNA roundtrip failed for {original}")

        print("TestMetatronNervousSystem: test_dna_encoding_decoding PASSED")

    def test_phi_compress_expand(self):
        """Test phi compression and expansion roundtrip."""
        test_values = [1.0, 10.0, 100.0, PHI, 1000.5]

        for original in test_values:
            compressed = self.mns.phi_compress(original)
            expanded = self.mns.phi_expand(compressed)
            self.assertAlmostEqual(original, expanded, places=10)

        print("TestMetatronNervousSystem: test_phi_compress_expand PASSED")

    def test_hmac_signing(self):
        """Test HMAC signature generation and verification."""
        message = "test message"
        key = "test_key"

        sig = self.mns.hmac_sign(message, key)
        self.assertTrue(self.mns.verify_signature(message, key, sig))
        
        # Wrong key should fail
        self.assertFalse(self.mns.verify_signature(message, "wrong_key", sig))

        print("TestMetatronNervousSystem: test_hmac_signing PASSED")

    def test_registry_creation(self):
        """Test that the registry directory is created."""
        self.assertTrue(self.registry.exists())
        print("TestMetatronNervousSystem: test_registry_creation PASSED")


class TestNodeRegistry(unittest.TestCase):
    """Tests for the Node Registry."""

    def test_all_nodes_registered(self):
        """Test that all 12 functional nodes are registered."""
        expected_node_ids = set(range(1, 13))  # Nodes 1-12

        registered_ids = set()
        for node_info in NODE_REGISTRY.values():
            registered_ids.add(node_info['node_id'])

        # Check that we have nodes 1-12
        self.assertEqual(expected_node_ids, registered_ids,
            f"Missing nodes. Expected {expected_node_ids}, got {registered_ids}")

        print("TestNodeRegistry: test_all_nodes_registered PASSED")

    def test_platonic_solids_mapped(self):
        """Test that each node has a Platonic solid or sacred geometry mapping."""
        expected_solids = {
            'Cube', 'Tetrahedron', 'Icosahedron', 'Dodecahedron',
            'Octahedron', 'Metatron Nexus', 'Heptagram', 'Octave',
            'Merkabah', 'Merkaba-Bio', 'Tesla Triangle', 'Omega Point'
        }
        
        registered_solids = set()
        for node_info in NODE_REGISTRY.values():
            solid = node_info.get('platonic_solid')
            self.assertIsNotNone(solid,
                f"Node '{node_info['node_id']}' missing platonic_solid mapping")
            registered_solids.add(solid)

        self.assertEqual(len(registered_solids), 12,
            "All nodes should have unique platonic solids")

        print("TestNodeRegistry: test_platonic_solids_mapped PASSED")

    def test_register_node_function(self):
        """Test dynamic node registration."""
        test_node_name = "test_node_xyz"

        register_node(
            name=test_node_name,
            node_id=99,
            role="Test node for unit testing",
            path="tests/test_node.py",
            platonic_solid="TestSolid",
            contact="metatron"
        )

        retrieved = get_node_info(test_node_name)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved['node_id'], 99)
        self.assertEqual(retrieved['platonic_solid'], "TestSolid")

        # Clean up
        if test_node_name in NODE_REGISTRY:
            del NODE_REGISTRY[test_node_name]

        print("TestNodeRegistry: test_register_node_function PASSED")

    def test_node_registry_structure(self):
        """Test that all registry entries have required fields."""
        required_fields = {'node_id', 'role', 'platonic_solid', 'path', 'contact'}

        for node_name, node_info in NODE_REGISTRY.items():
            self.assertEqual(set(node_info.keys()), required_fields,
                f"Node '{node_name}' missing required fields")
            self.assertIsInstance(node_info['node_id'], int)
            self.assertIsInstance(node_info['role'], str)
            self.assertIsInstance(node_info['platonic_solid'], str)
            self.assertIsInstance(node_info['path'], str)
            self.assertIsInstance(node_info['contact'], str)

        print("TestNodeRegistry: test_node_registry_structure PASSED")


class TestNode13MetatronCoordinator(unittest.TestCase):
    """Tests for the Node13MetatronCoordinator class."""

    def setUp(self):
        """Set up a coordinator instance for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.registry = Path(self.temp_dir) / "dna_registry"
        self.coordinator = Node13MetatronCoordinator(registry=self.registry)

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_coordinator_initialization(self):
        """Test that the coordinator initializes correctly."""
        self.assertEqual(self.coordinator.NODE_ID, 13)
        self.assertEqual(self.coordinator.NODE_NAME, "Metatron Coordinator")
        self.assertEqual(self.coordinator.PLATONIC_SOLID, "Metatron's Cube")
        self.assertEqual(self.coordinator.status, "active")
        self.assertIsNotNone(self.coordinator.initialized_at)

        print("TestNode13MetatronCoordinator: test_coordinator_initialization PASSED")

    def test_coordinator_health_status(self):
        """Test coordinator health status reporting."""
        health = self.coordinator.get_health_status()

        self.assertEqual(health['node_id'], 13)
        self.assertEqual(health['status'], 'active')
        self.assertIn('uptime_seconds', health)
        self.assertIn('registered_nodes', health)
        self.assertGreater(health['registered_nodes'], 0)
        self.assertIn('message_count', health)

        print("TestNode13MetatronCoordinator: test_coordinator_health_status PASSED")

    def test_system_health_report(self):
        """Test system-wide health reporting."""
        system_health = self.coordinator.get_system_health()

        self.assertIn('coordinator', system_health)
        self.assertIn('nodes', system_health)
        self.assertIn('summary', system_health)

        # Check summary counts
        summary = system_health['summary']
        self.assertIn('total_nodes', summary)
        self.assertIn('active', summary)
        self.assertIn('not_loaded', summary)
        self.assertIn('error', summary)
        self.assertGreater(summary['total_nodes'], 0)

        print("TestNode13MetatronCoordinator: test_system_health_report PASSED")

    def test_message_routing(self):
        """Test cross-node message routing."""
        message = self.coordinator.send_message(
            from_node="node1_base_os",
            to_node="node2_cybershield",
            message_type="health_check",
            payload={"request": "status"}
        )

        self.assertEqual(message['from'], "node1_base_os")
        self.assertEqual(message['to'], "node2_cybershield")
        self.assertEqual(message['type'], "health_check")
        self.assertIn('timestamp', message)
        self.assertIn('dna_packet', message)
        self.assertEqual(message['routed_by'], "Metatron Coordinator")

        # Verify message was logged
        self.assertEqual(len(self.coordinator.message_log), 1)

        print("TestNode13MetatronCoordinator: test_message_routing PASSED")

    def test_geometry_contains_all_platonic_solids(self):
        """Test that Metatron's Cube geometry contains all 5 Platonic solids."""
        expected_solids = {'Cube', 'Tetrahedron', 'Octahedron', 'Icosahedron', 'Dodecahedron'}
        contained = set(self.coordinator.GEOMETRY['contains'])

        self.assertEqual(expected_solids, contained,
            f"Metatron's Cube should contain all 5 Platonic solids")

        print("TestNode13MetatronCoordinator: test_geometry_contains_all_platonic_solids PASSED")

    def test_consciousness_data_encoding(self):
        """Test consciousness data encoding to DNA packets."""
        consciousness_data = {
            'phi_ratio': PHI,
            'coherence': 0.85,
            'entanglement': 0.92,
            'fidelity': 0.88
        }

        encoded = self.coordinator.encode_consciousness_data(consciousness_data)

        self.assertIn('original_data', encoded)
        self.assertIn('dna_packets', encoded)
        self.assertEqual(len(encoded['dna_packets']), 4)

        # Check each encoded value
        for key in consciousness_data.keys():
            self.assertIn(key, encoded['dna_packets'])
            packet = encoded['dna_packets'][key]
            self.assertIn('original', packet)
            self.assertIn('compressed', packet)
            self.assertIn('dna', packet)
            self.assertIn('AACAAT', packet['dna'])  # Header

        print("TestNode13MetatronCoordinator: test_consciousness_data_encoding PASSED")

    def test_consciousness_data_decoding(self):
        """Test DNA packet decoding back to consciousness data."""
        original_data = {
            'phi_ratio': PHI,
            'coherence': 0.85,
            'entanglement': 0.92
        }

        encoded = self.coordinator.encode_consciousness_data(original_data)
        decoded = self.coordinator.decode_consciousness_data(encoded)

        # Check decoded values are close to original (some precision loss expected)
        for key in original_data.keys():
            self.assertIn(key, decoded)
            self.assertAlmostEqual(decoded[key], original_data[key], places=1,
                msg=f"Decoding failed for {key}")

        print("TestNode13MetatronCoordinator: test_consciousness_data_decoding PASSED")

    def test_workflow_execution(self):
        """Test multi-node workflow execution."""
        # Create a simple workflow with available nodes
        workflow_result = self.coordinator.execute_workflow(
            workflow_name="test_workflow",
            nodes=["node1_base_os"],
            input_data={"test": "data"}
        )

        self.assertEqual(workflow_result['workflow_name'], "test_workflow")
        self.assertIn('start_time', workflow_result)
        self.assertIn('end_time', workflow_result)
        self.assertIn('duration_seconds', workflow_result)
        self.assertIn('nodes_executed', workflow_result)
        self.assertIn('results', workflow_result)

        print("TestNode13MetatronCoordinator: test_workflow_execution PASSED")

    def test_uptime_tracking(self):
        """Test that uptime is tracked correctly."""
        health1 = self.coordinator.get_health_status()
        time.sleep(0.1)
        health2 = self.coordinator.get_health_status()

        # Uptime should increase
        self.assertGreater(health2['uptime_seconds'], health1['uptime_seconds'])

        print("TestNode13MetatronCoordinator: test_uptime_tracking PASSED")


class TestNode13Integration(unittest.TestCase):
    """Integration tests for Node 13 with other nodes."""

    def setUp(self):
        """Set up coordinator for integration tests."""
        self.temp_dir = tempfile.mkdtemp()
        self.registry = Path(self.temp_dir) / "dna_registry"
        self.coordinator = Node13MetatronCoordinator(registry=self.registry)

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_node1_health_check(self):
        """Test health check for Node 1 (Base OS)."""
        health = self.coordinator.get_node_health("node1_base_os")
        
        self.assertIn('node_name', health)
        self.assertIn('status', health)
        # Node 1 should be loadable
        self.assertIn(health['status'], ['active', 'not_loaded', 'error'])

        print("TestNode13Integration: test_node1_health_check PASSED")

    def test_node2_health_check(self):
        """Test health check for Node 2 (CyberShield)."""
        health = self.coordinator.get_node_health("node2_cybershield")
        
        self.assertIn('node_name', health)
        self.assertIn('status', health)

        print("TestNode13Integration: test_node2_health_check PASSED")

    def test_node5_health_check(self):
        """Test health check for Node 5 (Molecular Geometry)."""
        health = self.coordinator.get_node_health("node5_spatial_intelligence")
        
        self.assertIn('node_name', health)
        self.assertIn('status', health)

        print("TestNode13Integration: test_node5_health_check PASSED")


def run_tests():
    """Run all Node 13 tests."""
    print("=" * 70)
    print("Node 13: Metatron Coordinator - Test Suite")
    print("=" * 70)
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestMetatronNervousSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestNodeRegistry))
    suite.addTests(loader.loadTestsFromTestCase(TestNode13MetatronCoordinator))
    suite.addTests(loader.loadTestsFromTestCase(TestNode13Integration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "=" * 70)
    if result.failures or result.errors:
        print(f"Tests completed with {len(result.failures)} failures and {len(result.errors)} errors")
        return False
    else:
        print(f"All {result.testsRun} tests passed successfully!")
        return True


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
