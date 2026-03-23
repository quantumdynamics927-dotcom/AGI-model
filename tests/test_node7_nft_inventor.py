import unittest
import sys
import os
import numpy as np
from unittest.mock import patch, MagicMock

import pytest

# Add project root to path to allow importing 'nft_inventor'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Mock the trimesh library before importing the node module. This allows tests
# to run even if this heavy optional dependency is not installed.
sys.modules["trimesh"] = MagicMock()

Node7NFTInventor = pytest.importorskip("nft_inventor").Node7NFTInventor


class TestNode7NFTInventor(unittest.TestCase):
    """Unit tests for the enhanced Node7NFTInventor class."""

    def setUp(self):
        """Set up a new Node7 instance and test data before each test."""
        self.test_assets_dir = "test_nft_assets"
        self.inventor = Node7NFTInventor(assets_dir=self.test_assets_dir)
        self.concept_data = {
            "name": "Test Concept",
            "description": "A concept for testing the enhanced functionality of Node 7.",
            "coordinates": (np.random.rand(10, 3) - 0.5),
            "attributes": [{"trait_type": "Origin", "value": "Test Suite"}],
        }
        self.analysis_data = list(np.random.randn(100))

    def tearDown(self):
        """Clean up any created asset files and directories after each test."""
        if os.path.exists(self.inventor.assets_dir):
            for f in os.listdir(self.inventor.assets_dir):
                os.remove(os.path.join(self.inventor.assets_dir, f))
            os.rmdir(self.inventor.assets_dir)

    def test_fingerprints_are_distinct(self):
        """Test that quantum and deterministic fingerprints are generated and are different."""
        det_fp = self.inventor.generate_deterministic_fingerprint(self.concept_data)
        q_fp = self.inventor.generate_quantum_fingerprint(self.concept_data)

        self.assertIsInstance(det_fp, str)
        self.assertIsInstance(q_fp, str)
        self.assertEqual(len(det_fp), 64, "Fingerprint should be a SHA256 hash.")
        self.assertEqual(len(q_fp), 64)
        self.assertNotEqual(
            det_fp,
            q_fp,
            "Quantum fingerprint should differ from the deterministic one.",
        )
        print("TestNode7: test_fingerprints_are_distinct PASSED")

    def test_consciousness_metrics_calculation(self):
        """Test the calculation of consciousness metrics returns a valid structure."""
        metrics = self.inventor.calculate_consciousness_metrics(self.analysis_data)

        self.assertIn("complexity", metrics)
        self.assertIn("coherence", metrics)
        self.assertIn("sentience_potential", metrics)
        self.assertGreaterEqual(metrics["complexity"], 0)
        self.assertGreaterEqual(metrics["coherence"], 0)
        self.assertIsInstance(metrics["sentience_potential"], float)
        print("TestNode7: test_consciousness_metrics_calculation PASSED")

    def test_tmtos_certification_block(self):
        """Test the addition of the TMT-OS certification block to metadata."""
        metadata = {}
        fingerprint = "test_fingerprint_123"
        certified_metadata = self.inventor.add_tmtos_certification(
            metadata, fingerprint
        )

        self.assertIn("tmtos_certification", certified_metadata)
        cert_block = certified_metadata["tmtos_certification"]
        self.assertEqual(cert_block["data"]["issuer"], "TMT-OS Metatron Authority")
        self.assertEqual(cert_block["data"]["fingerprint"], fingerprint)
        self.assertIn("signature", cert_block)
        self.assertEqual(len(cert_block["signature"]), 64)
        print("TestNode7: test_tmtos_certification_block PASSED")

    @patch("nft_inventor.trimesh")
    def test_render_3d_asset_with_mock_trimesh(self, mock_trimesh):
        """Test that the 3D asset rendering function is called correctly, using a mock."""
        # Configure the mock to simulate the export method returning bytes
        mock_mesh = MagicMock()
        mock_trimesh.Trimesh.return_value.convex_hull = mock_mesh
        mock_mesh.export.return_value = b"mock_glb_binary_data"

        asset_path = self.inventor.render_3d_asset(
            "test_asset_render", coordinates=self.concept_data["coordinates"]
        )

        mock_trimesh.Trimesh.assert_called_once()
        mock_mesh.export.assert_called_once_with(file_type="glb")
        self.assertTrue(os.path.exists(asset_path))
        with open(asset_path, "rb") as f:
            self.assertEqual(f.read(), b"mock_glb_binary_data")
        print("TestNode7: test_render_3d_asset_with_mock_trimesh PASSED")

    def test_full_invent_nft_pipeline(self):
        """Test the full invent_nft pipeline to ensure all pieces are integrated."""
        final_metadata = self.inventor.invent_nft(self.concept_data, self.analysis_data)

        # 1. Check for quantum fingerprint in the scientific data
        self.assertIn("fingerprint", final_metadata["scientific_data"])

        # 2. Check for consciousness metrics
        self.assertIn("consciousness_metrics", final_metadata["scientific_data"])
        self.assertIn(
            "complexity", final_metadata["scientific_data"]["consciousness_metrics"]
        )

        # 3. Check for TMT-OS certification block
        self.assertIn("tmtos_certification", final_metadata)

        # 4. Check that the corresponding asset files were created on disk
        fingerprint = final_metadata["scientific_data"]["fingerprint"]
        token_id = fingerprint[:16]
        json_path = self.inventor.assets_dir / f"{token_id}.nft.json"
        glb_path = self.inventor.assets_dir / f"{token_id}.glb"

        self.assertTrue(
            os.path.exists(json_path), "Metadata JSON file should be created."
        )
        self.assertTrue(os.path.exists(glb_path), "GLB asset file should be created.")
        print("TestNode7: test_full_invent_nft_pipeline PASSED")


if __name__ == "__main__":
    print("Running tests for Node 7: NFT Inventor...")
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestNode7NFTInventor))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if result.failures or result.errors:
        print("Node 7 tests failed.")
        sys.exit(1)
    print("All tests for Node 7 passed successfully.")
