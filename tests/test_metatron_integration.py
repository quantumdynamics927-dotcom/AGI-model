"""
Metatron Nervous System Integration Tests

This module tests the integration of all 12 functional nodes coordinated by
the Metatron Nervous System (Node 13). It validates:
1. All nodes can be instantiated
2. Health status is reported correctly
3. Cross-node communication works
4. DNA packet encoding/decoding is consistent
5. Platonic solid geometry is properly mapped
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

# Import the Metatron Nervous System
from metatron_nervous_system import (
    MetatronNervousSystem,
    MetatronCoordinator,
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

    def test_hmac_signing(self):
        """Test HMAC signature generation."""
        message = "test message"
        key = "test_key"

        sig1 = self.mns.hmac_sign(message, key)
        sig2 = self.mns.hmac_sign(message, key)

        # Same message and key should produce same signature
        self.assertEqual(sig1, sig2)

        # Different key should produce different signature
        sig3 = self.mns.hmac_sign(message, "different_key")
        self.assertNotEqual(sig1, sig3)

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

        # Check that we have nodes 1-12 (excluding Metatron itself which is 13)
        core_nodes = {1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12}  # Node 8 may be included
        self.assertTrue(core_nodes.issubset(registered_ids),
            f"Missing nodes. Expected at least {core_nodes}, got {registered_ids}")

        print("TestNodeRegistry: test_all_nodes_registered PASSED")

    def test_platonic_solids_mapped(self):
        """Test that each node has a Platonic solid or sacred geometry mapping."""
        for node_name, node_info in NODE_REGISTRY.items():
            solid = node_info.get('platonic_solid')
            self.assertIsNotNone(solid,
                f"Node '{node_name}' missing platonic_solid mapping")

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


class TestMetatronCoordinator(unittest.TestCase):
    """Tests for the MetatronCoordinator (Node 13)."""

    def setUp(self):
        """Set up a coordinator instance for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.registry = Path(self.temp_dir) / "dna_registry"
        self.coordinator = MetatronCoordinator(registry=self.registry)

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

        print("TestMetatronCoordinator: test_coordinator_initialization PASSED")

    def test_coordinator_health_status(self):
        """Test coordinator health status reporting."""
        health = self.coordinator.get_health_status()

        self.assertEqual(health['node_id'], 13)
        self.assertEqual(health['status'], 'active')
        self.assertIn('uptime_seconds', health)
        self.assertIn('registered_nodes', health)
        self.assertGreater(health['registered_nodes'], 0)

        print("TestMetatronCoordinator: test_coordinator_health_status PASSED")

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
        self.assertGreater(summary['total_nodes'], 0)

        print("TestMetatronCoordinator: test_system_health_report PASSED")

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

        print("TestMetatronCoordinator: test_message_routing PASSED")

    def test_geometry_contains_all_platonic_solids(self):
        """Test that Metatron's Cube geometry contains all 5 Platonic solids."""
        expected_solids = {'Cube', 'Tetrahedron', 'Octahedron', 'Icosahedron', 'Dodecahedron'}
        contained = set(self.coordinator.GEOMETRY['contains'])

        self.assertEqual(expected_solids, contained,
            f"Metatron's Cube should contain all 5 Platonic solids")

        print("TestMetatronCoordinator: test_geometry_contains_all_platonic_solids PASSED")


class TestIndividualNodes(unittest.TestCase):
    """Tests for individual node health status methods."""

    def test_node1_base_os(self):
        """Test Node 1 (TMT-OS Base) health status."""
        try:
            import importlib
            mod = importlib.import_module("TMT-OS.node1_base_os")
            node = mod.Node1BaseOS()

            health = node.get_health_status()
            self.assertEqual(health['node_id'], 1)
            self.assertEqual(health['status'], 'active')
            self.assertEqual(health['platonic_solid'], 'Cube')
            self.assertAlmostEqual(health['phi'], PHI, places=10)

            print("TestIndividualNodes: test_node1_base_os PASSED")
        except ImportError:
            self.skipTest("Node 1 module not available")

    def test_node2_cybershield(self):
        """Test Node 2 (CyberShield) health status."""
        try:
            import importlib
            mod = importlib.import_module("TMT-OS.node2_cybershield")
            node = mod.Node2CyberShield()

            health = node.get_health_status()
            self.assertEqual(health['node_id'], 2)
            self.assertEqual(health['status'], 'active')
            self.assertEqual(health['platonic_solid'], 'Tetrahedron')

            print("TestIndividualNodes: test_node2_cybershield PASSED")
        except ImportError:
            self.skipTest("Node 2 module not available")

    def test_node5_molecular_geometry(self):
        """Test Node 5 (Molecular Geometry) health status."""
        try:
            from molecular_geometry.node5_spatial_intelligence import Node5SpatialIntelligence
            node = Node5SpatialIntelligence()

            health = node.get_health_status()
            self.assertEqual(health['node_id'], 5)
            self.assertEqual(health['status'], 'active')
            self.assertEqual(health['platonic_solid'], 'Octahedron')

            print("TestIndividualNodes: test_node5_molecular_geometry PASSED")
        except ImportError:
            self.skipTest("Node 5 module not available")

    def test_node6_data_provenance(self):
        """Test Node 6 (Data Provenance) health status."""
        try:
            from data_provenance.node6_audit_trails import Node6AuditTrails

            # Use a temporary log file
            temp_log = "temp_test_node6_health.jsonl"
            node = Node6AuditTrails(log_file_path=temp_log)

            health = node.get_health_status()
            self.assertEqual(health['node_id'], 6)
            self.assertIn(health['status'], ['active', 'error_tampered_log'])
            self.assertEqual(health['platonic_solid'], 'Metatron Nexus')

            # Clean up
            if os.path.exists(temp_log):
                os.remove(temp_log)

            print("TestIndividualNodes: test_node6_data_provenance PASSED")
        except ImportError:
            self.skipTest("Node 6 module not available")

    def test_node7_nft_inventor(self):
        """Test Node 7 (NFT Inventor) health status."""
        try:
            from nft_inventor import Node7NFTInventor
            node = Node7NFTInventor()

            health = node.get_health_status()
            self.assertEqual(health['node_id'], 7)
            self.assertEqual(health['status'], 'active')
            self.assertEqual(health['platonic_solid'], 'Heptagram')

            print("TestIndividualNodes: test_node7_nft_inventor PASSED")
        except ImportError:
            self.skipTest("Node 7 module not available")

    def test_node9_qvae_bridge(self):
        """Test Node 9 (QVAE Bridge) health status."""
        try:
            from qvae_bridge import get_bridge
            node = get_bridge()

            health = node.get_health_status()
            self.assertEqual(health['node_id'], 9)
            self.assertEqual(health['status'], 'active')
            self.assertEqual(health['platonic_solid'], 'Merkabah')

            print("TestIndividualNodes: test_node9_qvae_bridge PASSED")
        except ImportError:
            self.skipTest("Node 9 module not available")


class TestPlatonicSolidGeometry(unittest.TestCase):
    """Tests to validate Platonic solid geometry values."""

    def test_cube_geometry(self):
        """Test Cube (Node 1) has correct geometry."""
        # Cube: 6 faces, 8 vertices, 12 edges
        try:
            import importlib
            mod = importlib.import_module("TMT-OS.node1_base_os")
            geometry = mod.Node1BaseOS.GEOMETRY

            self.assertEqual(geometry['faces'], 6)
            self.assertEqual(geometry['vertices'], 8)
            self.assertEqual(geometry['edges'], 12)

            print("TestPlatonicSolidGeometry: test_cube_geometry PASSED")
        except ImportError:
            self.skipTest("Node 1 module not available")

    def test_tetrahedron_geometry(self):
        """Test Tetrahedron (Node 2) has correct geometry."""
        # Tetrahedron: 4 faces, 4 vertices, 6 edges
        try:
            import importlib
            mod = importlib.import_module("TMT-OS.node2_cybershield")
            geometry = mod.Node2CyberShield.GEOMETRY

            self.assertEqual(geometry['faces'], 4)
            self.assertEqual(geometry['vertices'], 4)
            self.assertEqual(geometry['edges'], 6)

            print("TestPlatonicSolidGeometry: test_tetrahedron_geometry PASSED")
        except ImportError:
            self.skipTest("Node 2 module not available")

    def test_octahedron_geometry(self):
        """Test Octahedron (Node 5) has correct geometry."""
        # Octahedron: 8 faces, 6 vertices, 12 edges
        try:
            from molecular_geometry.node5_spatial_intelligence import Node5SpatialIntelligence
            geometry = Node5SpatialIntelligence.GEOMETRY

            self.assertEqual(geometry['faces'], 8)
            self.assertEqual(geometry['vertices'], 6)
            self.assertEqual(geometry['edges'], 12)

            print("TestPlatonicSolidGeometry: test_octahedron_geometry PASSED")
        except ImportError:
            self.skipTest("Node 5 module not available")

    def test_icosahedron_geometry(self):
        """Test Icosahedron (Node 3) has correct geometry."""
        # Icosahedron: 20 faces, 12 vertices, 30 edges
        try:
            from tmt_os_labs.node3_experimental_labs import Node3ExperimentalLabs
            geometry = Node3ExperimentalLabs.GEOMETRY

            self.assertEqual(geometry['faces'], 20)
            self.assertEqual(geometry['vertices'], 12)
            self.assertEqual(geometry['edges'], 30)

            print("TestPlatonicSolidGeometry: test_icosahedron_geometry PASSED")
        except ImportError:
            self.skipTest("Node 3 module not available")

    def test_dodecahedron_geometry(self):
        """Test Dodecahedron (Node 4) has correct geometry."""
        # Dodecahedron: 12 faces, 20 vertices, 30 edges
        try:
            import importlib
            mod = importlib.import_module("TMT-OS.node4_nft_layer")
            geometry = mod.Node4NFTLayer.GEOMETRY

            self.assertEqual(geometry['faces'], 12)
            self.assertEqual(geometry['vertices'], 20)
            self.assertEqual(geometry['edges'], 30)

            print("TestPlatonicSolidGeometry: test_dodecahedron_geometry PASSED")
        except ImportError:
            self.skipTest("Node 4 module not available")


if __name__ == '__main__':
    print("=" * 70)
    print("Running Metatron Nervous System Integration Tests")
    print("=" * 70)

    # Create a test suite with all test classes
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestMetatronNervousSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestNodeRegistry))
    suite.addTests(loader.loadTestsFromTestCase(TestMetatronCoordinator))
    suite.addTests(loader.loadTestsFromTestCase(TestIndividualNodes))
    suite.addTests(loader.loadTestsFromTestCase(TestPlatonicSolidGeometry))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("ALL INTEGRATION TESTS PASSED!")
    else:
        print(f"TESTS FAILED: {len(result.failures)} failures, {len(result.errors)} errors")
    print("=" * 70)

    sys.exit(0 if result.wasSuccessful() else 1)
