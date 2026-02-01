import unittest
import sys
import os
import importlib
import json

# Add project root to path to allow finding the 'TMT-OS' directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Dynamically import the module due to the hyphen in the 'TMT-OS' directory name
try:
    node4_module = importlib.import_module("TMT-OS.node4_nft_layer")
    Node4NFTLayer = node4_module.Node4NFTLayer
except ImportError as e:
    raise ImportError(
        "Could not import Node4NFTLayer. "
        "Ensure 'TMT-OS/node4_nft_layer.py' exists and the test is run from the project root."
    ) from e

class TestNode4NFTLayer(unittest.TestCase):
    """Unit tests for the Node4NFTLayer class, which handles asset creation."""

    def setUp(self):
        """Set up a new Node4 instance and common test data before each test."""
        self.node4 = Node4NFTLayer()
        self.owner_address = "0x1234567890123456789012345678901234567890"
        self.raw_metadata = {
            "name": "Test Asset",
            "description": "A test asset for Node 4.",
            "attributes": {
                "Level": 5,
                "Rarity": "Common"
            }
        }

    def test_initialization(self):
        """Test that the node initializes correctly with its default state."""
        self.assertEqual(self.node4.NODE_ID, 4)
        self.assertEqual(self.node4.NODE_NAME, "NFT Layer")
        self.assertEqual(self.node4.PLATONIC_SOLID, "Dodecahedron")
        self.assertEqual(self.node4.status, "active")
        self.assertIsNotNone(self.node4.ipfs_node)
        self.assertIsNotNone(self.node4.blockchain)
        print("TestNode4: test_initialization PASSED")

    def test_standardize_metadata(self):
        """Test the metadata standardization process for OpenSea compatibility."""
        standardized = self.node4.standardize_metadata(self.raw_metadata)
        
        self.assertEqual(standardized['name'], self.raw_metadata['name'])
        self.assertEqual(standardized['description'], self.raw_metadata['description'])
        
        # Check that dictionary attributes are converted to the correct list format
        expected_attributes = [
            {"trait_type": "Level", "value": 5},
            {"trait_type": "Rarity", "value": "Common"}
        ]
        # Use assertCountEqual to compare lists of dicts regardless of order
        self.assertCountEqual(standardized['attributes'], expected_attributes)
        print("TestNode4: test_standardize_metadata PASSED")

    def test_create_asset_pipeline(self):
        """Test the end-to-end asset creation pipeline, including all mock interactions."""
        final_asset = self.node4.create_asset(self.owner_address, self.raw_metadata)

        # 1. Check the structure of the final asset object returned to the user
        self.assertIn("token_id", final_asset)
        self.assertEqual(final_asset['owner'], self.owner_address)
        self.assertIn("metadata_cid", final_asset)
        self.assertTrue(final_asset['metadata_cid'].startswith("Qm"))
        self.assertIn("tx_hash", final_asset)
        self.assertTrue(final_asset['tx_hash'].startswith("0x"))

        # 2. Check that the metadata's image field was correctly updated with the IPFS CID
        self.assertEqual(final_asset['metadata']['image'], f"ipfs://{final_asset['metadata_cid']}")
        
        # 3. Check the internal state of the mock services and registry
        token_id = final_asset['token_id']
        self.assertIn(token_id, self.node4.asset_registry, "Asset should be in the local registry.")
        self.assertIn(token_id, self.node4.blockchain.ledger, "Asset should be on the mock blockchain ledger.")
        self.assertEqual(self.node4.blockchain.ledger[token_id]['owner'], self.owner_address)
        print("TestNode4: test_create_asset_pipeline PASSED")
        
    def test_get_asset(self):
        """Test retrieving a successfully created asset from the registry."""
        created_asset = self.node4.create_asset(self.owner_address, self.raw_metadata)
        token_id = created_asset['token_id']
        
        retrieved_asset = self.node4.get_asset(token_id)
        
        self.assertIsNotNone(retrieved_asset, "Should retrieve the created asset.")
        self.assertEqual(created_asset, retrieved_asset, "Retrieved asset should match the created one.")
        print("TestNode4: test_get_asset PASSED")

    def test_get_asset_invalid_id(self):
        """Test that retrieving a non-existent asset returns None."""
        retrieved_asset = self.node4.get_asset(9999) # An ID that shouldn't exist yet
        self.assertIsNone(retrieved_asset, "Should return None for an invalid token ID.")
        print("TestNode4: test_get_asset_invalid_id PASSED")
        
    def test_health_status_updates(self):
        """Test that the health status payload correctly reflects the number of registered assets."""
        initial_health = self.node4.get_health_status()
        self.assertEqual(initial_health['assets_registered'], 0)
        
        # Create one asset
        self.node4.create_asset(self.owner_address, self.raw_metadata)
        
        health_after_one = self.node4.get_health_status()
        self.assertEqual(health_after_one['assets_registered'], 1)

        # Create another asset
        self.node4.create_asset(self.owner_address, {"name": "Asset 2"})
        
        health_after_two = self.node4.get_health_status()
        self.assertEqual(health_after_two['assets_registered'], 2)
        print("TestNode4: test_health_status_updates PASSED")

if __name__ == '__main__':
    print("Running tests for Node 4: NFT Layer...")
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestNode4NFTLayer))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if result.failures or result.errors:
        print("Node 4 tests failed.")
        sys.exit(1)
    print("All tests for Node 4 passed successfully.")
