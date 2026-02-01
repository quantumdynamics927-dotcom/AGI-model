import unittest
import os
import sys
import importlib
import hmac
import hashlib

# Add project root to the path to allow finding the 'TMT-OS' directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Dynamically import the module due to the hyphen in the 'TMT-OS' directory name
try:
    node2_module = importlib.import_module("TMT-OS.node2_cybershield")
    Node2CyberShield = node2_module.Node2CyberShield
    HMAC_SECRET_KEY = node2_module.HMAC_SECRET_KEY
except ImportError as e:
    raise ImportError(
        "Could not import Node2CyberShield. "
        "Ensure 'TMT-OS/node2_cybershield.py' exists and the test is run from the project root."
    ) from e

class TestNode2CyberShield(unittest.TestCase):
    """Unit tests for the Node2CyberShield class."""

    @classmethod
    def setUpClass(cls):
        """Set up for all tests. Create a shield instance."""
        cls.shield = Node2CyberShield()
        cls.audit_log_path = 'node2_cybershield_audit.log'
        # Ensure the log file is clean before starting tests
        if os.path.exists(cls.audit_log_path):
            os.remove(cls.audit_log_path)

    def test_initialization(self):
        """Test that the node initializes with correct default values."""
        self.assertEqual(self.shield.NODE_ID, 2)
        self.assertEqual(self.shield.NODE_NAME, "CyberShield")
        self.assertEqual(self.shield.PLATONIC_SOLID, "Tetrahedron")
        self.assertEqual(self.shield.status, "active")
        print("TestNode2CyberShield: test_initialization PASSED")

    def test_hmac_signature(self):
        """Test HMAC-SHA256 signature generation and verification."""
        data = b"test payload for hmac"
        signature = self.shield.generate_hmac_signature(data)
        
        # Test 1: A correct signature should verify successfully.
        self.assertTrue(self.shield.verify_hmac_signature(data, signature))
        
        # Test 2: An incorrect signature should fail verification.
        self.assertFalse(self.shield.verify_hmac_signature(data, "incorrect_signature_string" * 3))
        
        # Test 3: Tampered data with a valid signature should fail.
        self.assertFalse(self.shield.verify_hmac_signature(b"tampered payload data", signature))
        print("TestNode2CyberShield: test_hmac_signature PASSED")

    def test_access_control_logic(self):
        """Test the simple Role-Based Access Control (RBAC) system."""
        # Admin role should have wildcard access
        self.assertTrue(self.shield.check_access('admin', 'read'))
        self.assertTrue(self.shield.check_access('admin', 'write'))
        self.assertTrue(self.shield.check_access('admin', 'any_other_action'))

        # Node role should have specific access
        self.assertTrue(self.shield.check_access('node', 'read'))
        self.assertTrue(self.shield.check_access('node', 'write'))
        self.assertFalse(self.shield.check_access('node', 'delete_everything')) # An action not in its list

        # Guest role should have the most limited access
        self.assertTrue(self.shield.check_access('guest', 'read'))
        self.assertFalse(self.shield.check_access('guest', 'write'))
        self.assertFalse(self.shield.check_access('guest', 'execute'))

        # An unknown role should have no access at all
        self.assertFalse(self.shield.check_access('unknown_role', 'read'))
        print("TestNode2CyberShield: test_access_control_logic PASSED")

    def test_encryption_decryption_symmetry(self):
        """Test that decryption is the perfect inverse of the encryption operation."""
        original_data = b"This is a highly confidential message that must be protected."
        encrypted_data = self.shield.encrypt_packet(original_data)
        decrypted_data = self.shield.decrypt_packet(encrypted_data)
        
        # Encrypted data should be different from the original
        self.assertNotEqual(original_data, encrypted_data)
        # Decrypted data must match the original data exactly
        self.assertEqual(original_data, decrypted_data)
        print("TestNode2CyberShield: test_encryption_decryption_symmetry PASSED")

    def test_audit_log_creation_and_content(self):
        """Test that security events are correctly written to the audit log file."""
        # Perform an action that should be audited (e.g., a failed access attempt)
        self.shield.check_access('guest', 'write')
        
        self.assertTrue(os.path.exists(self.audit_log_path), "Audit log file should be created.")
        
        with open(self.audit_log_path, 'r') as f:
            log_content = f.read()
        
        # Check that the log contains the expected audit trail
        self.assertIn("AUDIT::ACCESS_DENIED", log_content)
        self.assertIn("Role 'guest' denied for action 'write'", log_content)
        print("TestNode2CyberShield: test_audit_log_creation_and_content PASSED")

    def test_health_status_payload(self):
        """Test that the health status payload is accurate."""
        status = self.shield.get_health_status()
        self.assertEqual(status['node_id'], 2)
        self.assertEqual(status['status'], 'active')
        self.assertEqual(status['platonic_solid'], 'Tetrahedron')
        self.assertEqual(status['audit_log_file'], self.audit_log_path)
        print("TestNode2CyberShield: test_health_status_payload PASSED")

    @classmethod
    def tearDownClass(cls):
        """Clean up the audit log file after all tests are complete."""
        if os.path.exists(cls.audit_log_path):
            try:
                os.remove(cls.audit_log_path)
            except OSError as e:
                print(f"Error removing audit log file: {e}")

if __name__ == '__main__':
    print("Running tests for Node 2: CyberShield...")
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestNode2CyberShield))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    # Provide a clear exit status for automation
    if result.failures or result.errors:
        print("Node 2 tests failed.")
        sys.exit(1)
    print("All tests for Node 2 passed successfully.")
