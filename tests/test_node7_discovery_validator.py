"""
Node 7: Scientific Discovery Validator - Test Suite

Tests for the transformed Node 7 functionality:
- Discovery validation with cryptographic fingerprints
- TMT-OS certification generation
- Consciousness metrics calculation
- Reproducibility package generation
- Certificate creation and verification
- Provenance tracking

This suite validates the transformation from NFT Inventor to
Scientific Discovery Validator.
"""
import unittest
import sys
import os
import tempfile
import shutil
import json
import numpy as np
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import Node 7
from node7_discovery_validator import (
    Node7DiscoveryValidator,
    DiscoveryCertificate,
    asdict
)


class TestNode7DiscoveryValidator(unittest.TestCase):
    """Tests for Node 7: Scientific Discovery Validator."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.validator = Node7DiscoveryValidator(validation_dir=self.temp_dir)
        
        self.sample_discovery = {
            'title': 'Test Discovery',
            'description': 'A test scientific discovery',
            'data': {
                'measurements': [1.0, 2.0, 3.0, 4.0],
                'observations': ['obs1', 'obs2']
            },
            'results': {
                'significance': 0.95,
                'confidence': 0.99
            },
            'analysis': {
                'complexity': 2.5,
                'coherence': 0.85,
                'phi_score': 0.92
            },
            'methods': {
                'protocol': 'test_protocol_v1',
                'instrument': 'test_instrument'
            }
        }

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_validator_initialization(self):
        """Test Discovery Validator initialization."""
        self.assertEqual(self.validator.NODE_ID, 7)
        self.assertEqual(self.validator.NODE_NAME, "Scientific Discovery Validator")
        self.assertEqual(self.validator.PLATONIC_SOLID, "Heptagram")
        self.assertEqual(self.validator.status, "active")
        self.assertTrue(self.validator.validation_dir.exists())
        self.assertEqual(self.validator.validation_count, 0)

        print("TestNode7DiscoveryValidator: test_validator_initialization PASSED")

    def test_stable_serialize(self):
        """Test stable serialization for reproducibility."""
        obj1 = {'z': 1, 'a': 2, 'b': [3, 4]}
        obj2 = {'a': 2, 'b': [3, 4], 'z': 1}
        
        # Same object, different order should produce same serialization
        ser1 = self.validator._stable_serialize(obj1)
        ser2 = self.validator._stable_serialize(obj2)
        
        self.assertEqual(ser1, ser2)
        self.assertIsInstance(ser1, str)

        print("TestNode7DiscoveryValidator: test_stable_serialize PASSED")

    def test_discovery_fingerprint(self):
        """Test deterministic fingerprint generation."""
        fingerprint1 = self.validator.generate_discovery_fingerprint(self.sample_discovery)
        fingerprint2 = self.validator.generate_discovery_fingerprint(self.sample_discovery)
        
        # Same data should produce same fingerprint
        self.assertEqual(fingerprint1, fingerprint2)
        self.assertEqual(len(fingerprint1), 64)  # SHA-256 hex length
        
        # Different data should produce different fingerprint
        modified = self.sample_discovery.copy()
        modified['title'] = 'Different Title'
        fingerprint3 = self.validator.generate_discovery_fingerprint(modified)
        self.assertNotEqual(fingerprint1, fingerprint3)

        print("TestNode7DiscoveryValidator: test_discovery_fingerprint PASSED")

    def test_quantum_fingerprint(self):
        """Test quantum-enhanced fingerprint generation."""
        fp1 = self.validator.generate_quantum_fingerprint(self.sample_discovery)
        fp2 = self.validator.generate_quantum_fingerprint(self.sample_discovery)
        
        # Quantum fingerprints should differ due to timestamp
        self.assertNotEqual(fp1, fp2)
        self.assertEqual(len(fp1), 64)

        print("TestNode7DiscoveryValidator: test_quantum_fingerprint PASSED")

    def test_consciousness_metrics(self):
        """Test consciousness metrics calculation."""
        analysis = {
            'value1': 1.0,
            'value2': 2.0,
            'value3': 3.0,
            'value4': 4.0
        }
        
        metrics = self.validator.calculate_consciousness_metrics(analysis)
        
        # Check structure
        self.assertIn('complexity', metrics)
        self.assertIn('coherence', metrics)
        self.assertIn('sentience_potential', metrics)
        self.assertIn('phi_resonance', metrics)
        
        # Check ranges
        self.assertGreaterEqual(metrics['complexity'], 0.0)
        self.assertGreaterEqual(metrics['coherence'], 0.0)
        self.assertGreaterEqual(metrics['sentience_potential'], 0.0)
        self.assertGreaterEqual(metrics['phi_resonance'], 0.0)
        self.assertLessEqual(metrics['coherence'], 1.0)
        self.assertLessEqual(metrics['phi_resonance'], 1.0)

        print("TestNode7DiscoveryValidator: test_consciousness_metrics PASSED")

    def test_consciousness_metrics_empty(self):
        """Test consciousness metrics with empty data."""
        metrics = self.validator.calculate_consciousness_metrics({})
        
        self.assertEqual(metrics['complexity'], 0.0)
        self.assertEqual(metrics['coherence'], 0.0)
        self.assertEqual(metrics['sentience_potential'], 0.0)
        self.assertEqual(metrics['phi_resonance'], 0.0)

        print("TestNode7DiscoveryValidator: test_consciousness_metrics_empty PASSED")

    def test_validate_discovery(self):
        """Test discovery validation."""
        validation = self.validator.validate_discovery(self.sample_discovery)
        
        # Check structure
        self.assertIn('is_valid', validation)
        self.assertIn('checks', validation)
        self.assertIn('warnings', validation)
        self.assertIn('metrics', validation)
        
        # Should be valid
        self.assertTrue(validation['is_valid'])
        self.assertGreater(len(validation['checks']), 0)
        
        # Should have fingerprint
        self.assertIn('fingerprint', validation)
        self.assertEqual(len(validation['fingerprint']), 64)

        print("TestNode7DiscoveryValidator: test_validate_discovery PASSED")

    def test_validate_discovery_missing_fields(self):
        """Test validation with missing required fields."""
        incomplete = {'description': 'Missing title'}
        
        validation = self.validator.validate_discovery(incomplete)
        
        # Should have warnings
        self.assertGreater(len(validation['warnings']), 0)
        self.assertTrue(any('title' in w for w in validation['warnings']))

        print("TestNode7DiscoveryValidator: test_validate_discovery_missing_fields PASSED")

    def test_tmtos_certification(self):
        """Test TMT-OS certification generation."""
        certificate = {
            'discovery_id': 'test123',
            'title': 'Test',
            'fingerprint': 'abc123'
        }
        
        certified = self.validator.add_tmtos_certification(certificate, 'test_fingerprint')
        
        # Check certification block
        self.assertIn('tmtos_certification', certified)
        cert_block = certified['tmtos_certification']
        
        self.assertEqual(cert_block['issuer'], 'TMT-OS Metatron Authority')
        self.assertEqual(cert_block['validator_node'], 7)
        self.assertEqual(cert_block['validator_name'], 'Scientific Discovery Validator')
        self.assertIn('signature', cert_block)
        self.assertEqual(len(cert_block['signature']), 64)
        self.assertIn('certification_timestamp', cert_block)
        self.assertEqual(cert_block['certification_standard'], 'TMT-OS-Scientific-v1.0')

        print("TestNode7DiscoveryValidator: test_tmtos_certification PASSED")

    def test_reproducibility_package(self):
        """Test reproducibility package generation."""
        package = self.validator.generate_reproducibility_package(self.sample_discovery)
        
        # Check structure
        self.assertIn('metadata', package)
        self.assertIn('data_hash', package)
        self.assertIn('code_hash', package)
        self.assertIn('results_hash', package)
        self.assertIn('complete_hash', package)
        self.assertIn('reproducibility_score', package)
        
        # Hashes should be present
        self.assertIsNotNone(package['data_hash'])
        self.assertIsNotNone(package['results_hash'])
        self.assertIsNotNone(package['complete_hash'])
        
        # Reproducibility score should be reasonable
        self.assertGreaterEqual(package['reproducibility_score'], 0.0)
        self.assertLessEqual(package['reproducibility_score'], 1.0)

        print("TestNode7DiscoveryValidator: test_reproducibility_package PASSED")

    def test_create_certificate(self):
        """Test complete certificate creation."""
        certificate = self.validator.create_certificate(self.sample_discovery)
        
        # Check it's a DiscoveryCertificate
        self.assertIsInstance(certificate, DiscoveryCertificate)
        
        # Check required fields
        self.assertIsNotNone(certificate.discovery_id)
        self.assertEqual(len(certificate.discovery_id), 16)
        self.assertEqual(certificate.title, 'Test Discovery')
        self.assertEqual(certificate.description, 'A test scientific discovery')
        self.assertEqual(len(certificate.fingerprint), 64)
        self.assertIsNotNone(certificate.timestamp)
        self.assertIsNotNone(certificate.validator_signature)
        self.assertIsNotNone(certificate.tmtos_certification)
        self.assertIsNotNone(certificate.consciousness_metrics)
        self.assertIn(certificate.validation_status, ['valid', 'invalid'])
        self.assertIsNotNone(certificate.reproducibility_hash)

        print("TestNode7DiscoveryValidator: test_create_certificate PASSED")

    def test_save_certificate(self):
        """Test saving certificate to file."""
        certificate = self.validator.create_certificate(self.sample_discovery)
        filepath = self.validator.save_certificate(certificate)
        
        # File should exist
        self.assertTrue(filepath.exists())
        self.assertEqual(filepath.suffix, '.json')
        
        # Load and verify
        with open(filepath, 'r') as f:
            saved_data = json.load(f)
        
        self.assertEqual(saved_data['discovery_id'], certificate.discovery_id)
        self.assertEqual(saved_data['title'], certificate.title)
        self.assertIn('tmtos_certification', saved_data)

        print("TestNode7DiscoveryValidator: test_save_certificate PASSED")

    def test_validate_and_certify(self):
        """Test complete validation and certification workflow."""
        result = self.validator.validate_and_certify(self.sample_discovery, save=True)
        
        # Check result structure
        self.assertIsInstance(result, dict)
        self.assertIn('discovery_id', result)
        self.assertIn('title', result)
        self.assertIn('fingerprint', result)
        self.assertIn('tmtos_certification', result)
        self.assertIn('consciousness_metrics', result)
        self.assertIn('reproducibility_hash', result)
        
        # Validator count should increase
        self.assertEqual(self.validator.validation_count, 1)
        
        # Certificate should be registered
        self.assertIn(result['discovery_id'], self.validator.discovery_registry)

        print("TestNode7DiscoveryValidator: test_validate_and_certify PASSED")

    def test_get_certificate(self):
        """Test retrieving certificate by ID."""
        certificate = self.validator.create_certificate(self.sample_discovery)
        retrieved = self.validator.get_certificate(certificate.discovery_id)
        
        # Should retrieve same certificate
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.discovery_id, certificate.discovery_id)
        self.assertEqual(retrieved.fingerprint, certificate.fingerprint)

        print("TestNode7DiscoveryValidator: test_get_certificate PASSED")

    def test_verify_certificate(self):
        """Test certificate verification."""
        certificate = self.validator.validate_and_certify(self.sample_discovery, save=False)
        
        # Verify with original data
        is_valid = self.validator.verify_certificate(
            certificate['discovery_id'],
            self.sample_discovery
        )
        self.assertTrue(is_valid)
        
        # Verify with modified data should fail
        modified = self.sample_discovery.copy()
        modified['title'] = 'Modified Title'
        is_invalid = self.validator.verify_certificate(
            certificate['discovery_id'],
            modified
        )
        self.assertFalse(is_invalid)

        print("TestNode7DiscoveryValidator: test_verify_certificate PASSED")

    def test_health_status(self):
        """Test health status reporting."""
        # Create a few certificates
        for i in range(3):
            discovery = self.sample_discovery.copy()
            discovery['title'] = f'Test Discovery {i}'
            self.validator.validate_and_certify(discovery, save=False)
        
        health = self.validator.get_health_status()
        
        # Check structure
        self.assertEqual(health['node_id'], 7)
        self.assertEqual(health['node_name'], 'Scientific Discovery Validator')
        self.assertEqual(health['status'], 'active')
        self.assertEqual(health['platonic_solid'], 'Heptagram')
        
        # Check counts
        self.assertEqual(health['validations_performed'], 3)
        self.assertEqual(health['registered_discoveries'], 3)
        self.assertGreater(health['uptime_seconds'], 0.0)
        self.assertIn('validation_directory', health)

        print("TestNode7DiscoveryValidator: test_health_status PASSED")


class TestNode7Integration(unittest.TestCase):
    """Integration tests for Node 7 with other system components."""

    def setUp(self):
        """Set up integration test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.validator = Node7DiscoveryValidator(validation_dir=self.temp_dir)

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_vae_output_validation(self):
        """Test validation of VAE model outputs."""
        # Simulate VAE output
        vae_discovery = {
            'title': 'VAE Latent Space Discovery',
            'description': 'Novel pattern in VAE latent space',
            'data': {
                'latent_vectors': np.random.rand(10, 32).tolist(),
                'reconstruction_error': 0.05
            },
            'results': {
                'kl_divergence': 0.02,
                'fidelity': 0.95
            },
            'analysis': {
                'complexity': 3.2,
                'coherence': 0.88,
                'phi_score': 0.91
            }
        }
        
        certificate = self.validator.validate_and_certify(vae_discovery)
        
        self.assertEqual(certificate['validation_status'], 'valid')
        self.assertIn('phi_resonance', certificate['consciousness_metrics'])
        self.assertGreater(certificate['consciousness_metrics']['phi_resonance'], 0.0)

        print("TestNode7Integration: test_vae_output_validation PASSED")

    def test_quantum_result_validation(self):
        """Test validation of quantum experiment results."""
        quantum_discovery = {
            'title': 'Quantum Entanglement Measurement',
            'description': 'Bell state fidelity measurement',
            'data': {
                'shots': 8192,
                'counts': {'00': 4096, '11': 4096}
            },
            'results': {
                'fidelity': 0.98,
                'entanglement_witness': 0.95
            },
            'analysis': {
                'complexity': 1.5,
                'coherence': 0.92
            }
        }
        
        certificate = self.validator.validate_and_certify(quantum_discovery)
        
        self.assertEqual(certificate['validation_status'], 'valid')
        self.assertGreater(certificate['consciousness_metrics']['coherence'], 0.9)

        print("TestNode7Integration: test_quantum_result_validation PASSED")

    def test_consciousness_analysis_validation(self):
        """Test validation of consciousness analysis results."""
        consciousness_discovery = {
            'title': 'Consciousness Pattern Detection',
            'description': 'Phi resonance in consciousness metrics',
            'data': {
                'eeg_channels': 64,
                'duration_seconds': 300
            },
            'results': {
                'phi_resonance_strength': 0.94,
                'global_coherence': 0.89
            },
            'analysis': {
                'complexity': 4.5,
                'coherence': 0.89,
                'phi_score': 0.94,
                'lzc_complexity': 0.85
            }
        }
        
        certificate = self.validator.validate_and_certify(consciousness_discovery)
        
        self.assertEqual(certificate['validation_status'], 'valid')
        # Phi resonance should be positive (exact value depends on data distribution)
        self.assertGreater(certificate['consciousness_metrics']['phi_resonance'], 0.0)

        print("TestNode7Integration: test_consciousness_analysis_validation PASSED")


def run_tests():
    """Run all Node 7 tests."""
    print("=" * 70)
    print("Node 7: Scientific Discovery Validator - Test Suite")
    print("=" * 70)

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestNode7DiscoveryValidator))
    suite.addTests(loader.loadTestsFromTestCase(TestNode7Integration))

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
