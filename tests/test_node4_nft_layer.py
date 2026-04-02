import unittest
import sys
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "TMT-OS" / "node4_nft_layer.py"

if not MODULE_PATH.exists():
    pytest.skip(
        "TMT-OS/node4_nft_layer.py not present in this repo", allow_module_level=True
    )

spec = importlib.util.spec_from_file_location("node4_nft_layer", MODULE_PATH)
node4_module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(node4_module)
# Support both old and new class names (backward compatibility)
Node4NFTLayer = getattr(node4_module, 'Node4NFTLayer', None) or node4_module.Node4QuantumArchive


class TestNode4NFTLayer(unittest.TestCase):
    """Unit tests for the Node4QuantumArchive class (formerly NFT Layer)."""

    def setUp(self):
        """Set up a new Node4 instance and common test data before each test."""
        self.node4 = Node4NFTLayer()
        self.owner_address = "researcher@example.com"
        self.raw_metadata = {
            "name": "Test Quantum Result",
            "description": "A test quantum experiment result for Node 4.",
            "experiment_type": "vae_training",
            "attributes": {"Fidelity": 0.98, "Coherence": 0.95},
        }

    def test_initialization(self):
        """Test that the node initializes correctly with its default state."""
        self.assertEqual(self.node4.NODE_ID, 4)
        # Support both old and new naming
        self.assertIn(self.node4.NODE_NAME, ["Quantum Archive Layer", "NFT Layer"])
        self.assertEqual(self.node4.PLATONIC_SOLID, "Dodecahedron")
        self.assertEqual(self.node4.status, "active")
        self.assertIsNotNone(self.node4.archive_storage)
        self.assertIsNotNone(self.node4.provenance_chain)
        print("TestNode4: test_initialization PASSED")

    def test_standardize_metadata(self):
        """Test the metadata standardization process for archive compatibility."""
        standardized = self.node4.standardize_metadata(self.raw_metadata)

        self.assertEqual(standardized["name"], self.raw_metadata["name"])
        self.assertEqual(standardized["description"], self.raw_metadata["description"])

        # Check that dictionary attributes are converted to the correct list format
        expected_attributes = [
            {"trait_type": "Fidelity", "value": 0.98},
            {"trait_type": "Coherence", "value": 0.95},
        ]
        # Use assertCountEqual to compare lists of dicts regardless of order
        self.assertCountEqual(standardized["attributes"], expected_attributes)
        print("TestNode4: test_standardize_metadata PASSED")

    def test_create_asset_pipeline(self):
        """Test the end-to-end asset creation pipeline, including all mock interactions."""
        final_asset = self.node4.create_asset(self.owner_address, self.raw_metadata)

        # 1. Check the structure of the final asset object returned to the user
        # Support both old (token_id) and new (archive_id) naming
        self.assertTrue("archive_id" in final_asset or "token_id" in final_asset)
        self.assertEqual(final_asset["owner"], self.owner_address)
        self.assertIn("metadata_cid", final_asset)
        self.assertTrue(final_asset["metadata_cid"].startswith("QRA") or final_asset["metadata_cid"].startswith("Qm"))
        self.assertIn("tx_hash", final_asset)
        self.assertTrue(final_asset["tx_hash"].startswith("0x"))

        # 2. Check that the metadata's archive_cid field was correctly updated
        if "archive_cid" in final_asset.get("metadata", {}):
            self.assertTrue(final_asset["metadata"]["archive_cid"].startswith("archive://"))

        # 3. Check the internal state of the mock services and registry
        # Support both old (token_id) and new (archive_id) naming
        asset_id = final_asset.get("archive_id") or final_asset.get("token_id")
        self.assertIn(
            asset_id,
            self.node4.asset_registry,
            "Asset should be in the local registry.",
        )
        self.assertIn(
            asset_id,
            self.node4.provenance_chain.ledger,
            "Asset should be in the provenance chain.",
        )
        self.assertEqual(
            self.node4.provenance_chain.ledger[asset_id]["owner"], self.owner_address
        )
        print("TestNode4: test_create_asset_pipeline PASSED")

    def test_get_asset(self):
        """Test retrieving a successfully created asset from the registry."""
        created_asset = self.node4.create_asset(self.owner_address, self.raw_metadata)
        asset_id = created_asset.get("archive_id") or created_asset.get("token_id")

        retrieved_asset = self.node4.get_asset(asset_id)

        self.assertIsNotNone(retrieved_asset, "Should retrieve the created asset.")
        self.assertEqual(
            created_asset,
            retrieved_asset,
            "Retrieved asset should match the created one.",
        )
        print("TestNode4: test_get_asset PASSED")

    def test_get_asset_invalid_id(self):
        """Test that retrieving a non-existent asset returns None."""
        retrieved_asset = self.node4.get_asset("QRA-999999")  # An ID that shouldn't exist yet
        self.assertIsNone(
            retrieved_asset, "Should return None for an invalid archive ID."
        )
        print("TestNode4: test_get_asset_invalid_id PASSED")

    def test_health_status_updates(self):
        """Test that the health status payload correctly reflects the number of registered assets."""
        initial_health = self.node4.get_health_status()
        # Support both old and new naming
        assets_key = "assets_archived" if "assets_archived" in initial_health else "assets_registered"
        self.assertEqual(initial_health[assets_key], 0)

        # Create one asset
        self.node4.create_asset(self.owner_address, self.raw_metadata)

        health_after_one = self.node4.get_health_status()
        self.assertEqual(health_after_one[assets_key], 1)

        # Create another asset
        self.node4.create_asset(self.owner_address, {"name": "Asset 2"})

        health_after_two = self.node4.get_health_status()
        self.assertEqual(health_after_two[assets_key], 2)
        print("TestNode4: test_health_status_updates PASSED")

    def test_compat_mint_event_conversion(self):
        """Test legacy mint event payload conversion for archive events."""
        convert = self.node4.provenance_chain._compat_mint_event

        self.assertEqual(convert({"archive_id": 7})["token_id"], 7)
        self.assertEqual(convert({"archive_id": "QRA-000123"})["token_id"], 123)
        self.assertEqual(convert({"archive_id": "456"})["token_id"], 456)
        self.assertIsNone(convert({"archive_id": None})["token_id"])
        self.assertIsNone(convert({"archive_id": "not-a-token"})["token_id"])

    def test_listener_backward_compatibility(self):
        """Test that archive listeners and legacy mint listeners are notified compatibly."""
        legacy_events = []
        archive_events = []
        dual_events = []

        class LegacyListener:
            def on_mint_event(self, event):
                legacy_events.append(event)

        class ArchiveListener:
            def on_archive_event(self, event):
                archive_events.append(event)

        class DualListener:
            def on_mint_event(self, event):
                dual_events.append(("mint", event))

            def on_archive_event(self, event):
                dual_events.append(("archive", event))

        self.node4.blockchain.add_listener(LegacyListener())
        self.node4.blockchain.add_listener(ArchiveListener())
        self.node4.blockchain.add_listener(DualListener())

        asset = self.node4.create_asset(self.owner_address, self.raw_metadata)

        self.assertEqual(len(legacy_events), 1)
        self.assertEqual(legacy_events[0]["token_id"], 0)
        self.assertEqual(legacy_events[0]["archive_id"], asset["archive_id"])

        self.assertEqual(len(archive_events), 1)
        self.assertEqual(archive_events[0]["archive_id"], asset["archive_id"])

        self.assertEqual(dual_events, [("archive", archive_events[0])])


if __name__ == "__main__":
    print("Running tests for Node 4: Quantum Archive Layer...")
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestNode4NFTLayer))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if result.failures or result.errors:
        print("Node 4 tests failed.")
        sys.exit(1)
    print("All tests for Node 4 passed successfully.")
