import unittest
import os
import sys
import json
import time

# Add project root to the path to allow direct import of 'data_provenance'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from data_provenance.node6_audit_trails import Node6AuditTrails
except ImportError as e:
     raise ImportError(
        "Could not import Node6AuditTrails. "
        "Ensure 'data_provenance/node6_audit_trails.py' exists and the test is run from the project root."
    ) from e

class TestNode6AuditTrails(unittest.TestCase):
    """Unit tests for the Node6AuditTrails class."""

    def setUp(self):
        """Set up a new Node6 instance with a temporary log file for each test."""
        self.test_log_file = 'temp_test_node6_log.jsonl'
        # Ensure the file is clean before each test to guarantee isolation
        if os.path.exists(self.test_log_file):
            os.remove(self.test_log_file)
        self.node = Node6AuditTrails(log_file_path=self.test_log_file)

    def tearDown(self):
        """Clean up the temporary log file after each test."""
        if os.path.exists(self.test_log_file):
            os.remove(self.test_log_file)

    def test_initialization_creates_genesis_entry(self):
        """Test that initializing the node creates a log file with a valid genesis entry."""
        self.assertTrue(os.path.exists(self.test_log_file))
        
        with open(self.test_log_file, 'r') as f:
            lines = f.readlines()
        
        self.assertEqual(len(lines), 1, "Log file should contain exactly one entry (the genesis block).")
        genesis_wrapper = json.loads(lines[0])
        genesis_content = genesis_wrapper['content']

        self.assertEqual(genesis_content['index'], 0)
        self.assertEqual(genesis_content['data'], 'Genesis Entry: Provenance Log Initialized')
        self.assertEqual(genesis_content['previous_hash'], '0' * 64)
        
        # Verify the hash of the genesis entry content is correct
        recalculated_hash = self.node._hash_entry_content(genesis_content)
        self.assertEqual(genesis_wrapper['hash'], recalculated_hash)
        print("TestNode6: test_initialization_creates_genesis_entry PASSED")

    def test_add_log_entry(self):
        """Test adding new, correctly linked entries to the audit log."""
        # The genesis block is already there. Get its hash.
        genesis_entry = self.node.get_last_entry()
        self.assertIsNotNone(genesis_entry)
        previous_hash = genesis_entry['hash']

        # Add a new entry
        new_data_1 = {'event': 'test_event', 'value': 'foo'}
        entry_1_wrapper = self.node.add_log_entry(new_data_1)
        
        self.assertEqual(entry_1_wrapper['content']['index'], 1)
        self.assertEqual(entry_1_wrapper['content']['data'], new_data_1)
        self.assertEqual(entry_1_wrapper['content']['previous_hash'], previous_hash, "New entry must link to previous hash.")
        
        # Add a second entry
        new_data_2 = {'event': 'another_event', 'value': 'bar'}
        entry_2_wrapper = self.node.add_log_entry(new_data_2)
        
        self.assertEqual(entry_2_wrapper['content']['index'], 2)
        self.assertEqual(entry_2_wrapper['content']['data'], new_data_2)
        self.assertEqual(entry_2_wrapper['content']['previous_hash'], entry_1_wrapper['hash'], "Second entry must link to the first.")
        print("TestNode6: test_add_log_entry PASSED")

    def test_verify_valid_chain(self):
        """Test that verify_chain passes on an untampered, multi-entry log."""
        self.node.add_log_entry({'data': 'first addition'})
        self.node.add_log_entry({'data': 'second addition'})
        
        is_valid, message = self.node.verify_chain()
        self.assertTrue(is_valid, f"Verification failed on a valid chain: {message}")
        self.assertEqual(message, "Provenance chain is valid and untampered.")
        print("TestNode6: test_verify_valid_chain PASSED")

    def test_verify_tampered_chain_content_fails(self):
        """Test that verify_chain fails if an entry's content is altered after logging."""
        self.node.add_log_entry({'data': 'first addition'})
        
        # Manually tamper with the log file
        with open(self.test_log_file, 'r+') as f:
            lines = f.readlines()
            # Tamper with the genesis entry's data field
            tampered_wrapper = json.loads(lines[0])
            tampered_wrapper['content']['data'] = 'TAMPERED GENESIS DATA'
            lines[0] = json.dumps(tampered_wrapper) + '\n'
            f.seek(0)
            f.truncate()
            f.writelines(lines)
            
        is_valid, message = self.node.verify_chain()
        self.assertFalse(is_valid, "Verification should fail on a tampered chain.")
        self.assertIn("tampered with", message, "Failure message should indicate tampering.")
        print("TestNode6: test_verify_tampered_chain_content_fails PASSED")

    def test_verify_broken_chain_link_fails(self):
        """Test that verify_chain fails if the hash link between entries is broken."""
        self.node.add_log_entry({'data': 'first addition'})
        
        with open(self.test_log_file, 'r+') as f:
            lines = f.readlines()
            # Break the chain by altering the previous_hash of the second entry
            tampered_wrapper = json.loads(lines[1])
            tampered_wrapper['content']['previous_hash'] = '0' * 64 # Set to an incorrect link
            lines[1] = json.dumps(tampered_wrapper) + '\n'
            f.seek(0)
            f.truncate()
            f.writelines(lines)
            
        is_valid, message = self.node.verify_chain()
        self.assertFalse(is_valid, "Verification should fail on a broken chain.")
        self.assertIn("Chain broken", message, "Failure message should indicate a broken link.")
        print("TestNode6: test_verify_broken_chain_link_fails PASSED")

    def test_health_status_reflects_chain_validity(self):
        """Test that the health status report accurately reflects chain validity."""
        # 1. Test on a valid chain
        self.node.add_log_entry("health check data")
        health = self.node.get_health_status()
        self.assertEqual(health['status'], "active")
        self.assertTrue(health['chain_verification']['is_valid'])

        # 2. Test on a tampered chain
        with open(self.test_log_file, 'r+') as f:
            lines = f.readlines()
            lines[0] = '{"invalid_json_structure": true}\n' # Corrupt the file with invalid content
            f.seek(0)
            f.truncate()
            f.writelines(lines)
            
        tampered_health = self.node.get_health_status()
        self.assertEqual(tampered_health['status'], "error_tampered_log")
        self.assertFalse(tampered_health['chain_verification']['is_valid'])
        print("TestNode6: test_health_status_reflects_chain_validity PASSED")

if __name__ == '__main__':
    print("Running tests for Node 6: Data Provenance...")
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestNode6AuditTrails))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if result.failures or result.errors:
        print("Node 6 tests failed.")
        sys.exit(1)
    print("All tests for Node 6 passed successfully.")
