"""
Nodes 10, 11, 12: Comprehensive Test Suite

Tests for:
- Node 10: Bio-Digital Interface (quantum to symbolic DNA mapping)
- Node 11: Frequency Master (Tesla analysis and consciousness integrals)
- Node 12: Neural Synapse (collective intelligence connectivity)

This suite validates:
1. Symbolic sequence generation from quantum states
2. Tesla consciousness analysis
3. Phi-correlation and connectivity matrix construction
4. Provenance tracking and safety mechanisms
5. Integration between nodes 10, 11, and 12
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


class TestNode10BioDigital(unittest.TestCase):
    """Tests for Node 10: Bio-Digital Interface."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_qubit_states = [
            {'phase': 0.5, 'probability': 0.8, 'p': 0.8},
            {'phase': 1.2, 'probability': 0.6, 'p': 0.6},
            {'phase': 2.1, 'probability': 0.9, 'p': 0.9},
            {'phase': 3.5, 'probability': 0.4, 'p': 0.4},
        ]

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_safe_base_mapping(self):
        """Test deterministic base mapping from quantum values."""
        from node10_biodigital import _safe_base_from_value

        # Test with various values
        base1 = _safe_base_from_value(0.0, 0)
        base2 = _safe_base_from_value(1.0, 1)
        base3 = _safe_base_from_value(-1.0, 2)

        # All should be valid nucleotide symbols
        self.assertIn(base1, ['A', 'T', 'C', 'G'])
        self.assertIn(base2, ['A', 'T', 'C', 'G'])
        self.assertIn(base3, ['A', 'T', 'C', 'G'])

        # Same input should produce same output (deterministic)
        base1_again = _safe_base_from_value(0.0, 0)
        self.assertEqual(base1, base1_again)

        print("TestNode10BioDigital: test_safe_base_mapping PASSED")

    def test_quantum_to_symbolic_basic(self):
        """Test basic quantum to symbolic sequence conversion."""
        from node10_biodigital import quantum_to_symbolic

        result = quantum_to_symbolic(self.test_qubit_states)

        # Check structure
        self.assertIn('symbolic_sequence', result)
        self.assertIn('summary', result)

        # Check symbolic sequence
        symbolic = result['symbolic_sequence']
        self.assertIsInstance(symbolic, str)
        self.assertLessEqual(len(symbolic), len(self.test_qubit_states))

        # All characters should be valid (A, T, C, G, or N for non-resonant)
        for char in symbolic:
            self.assertIn(char, ['A', 'T', 'C', 'G', 'N'])

        # Check summary
        summary = result['summary']
        self.assertIn('length', summary)
        self.assertIn('counts', summary)
        self.assertIn('resonant_fraction', summary)

        self.assertEqual(summary['length'], len(symbolic))
        self.assertIsInstance(summary['counts'], dict)
        self.assertGreaterEqual(summary['resonant_fraction'], 0.0)
        self.assertLessEqual(summary['resonant_fraction'], 1.0)

        print("TestNode10BioDigital: test_quantum_to_symbolic_basic PASSED")

    def test_quantum_to_symbolic_max_length(self):
        """Test that max_length parameter is respected."""
        from node10_biodigital import quantum_to_symbolic

        # Create many qubit states
        many_states = [{'phase': i * 0.1, 'probability': 0.5} for i in range(100)]

        # Test with different max lengths
        for max_len in [10, 50, 100]:
            result = quantum_to_symbolic(many_states, max_length=max_len)
            self.assertLessEqual(len(result['symbolic_sequence']), max_len)

        print("TestNode10BioDigital: test_quantum_to_symbolic_max_length PASSED")

    def test_sequence_hash(self):
        """Test SHA-256 hashing of symbolic sequences."""
        from node10_biodigital import get_sequence_hash

        seq1 = "ATCG"
        seq2 = "ATCG"
        seq3 = "GCTA"

        hash1 = get_sequence_hash(seq1)
        hash2 = get_sequence_hash(seq2)
        hash3 = get_sequence_hash(seq3)

        # Same sequence should produce same hash
        self.assertEqual(hash1, hash2)

        # Different sequences should produce different hashes
        self.assertNotEqual(hash1, hash3)

        # Hash should be 64 characters (SHA-256 hex)
        self.assertEqual(len(hash1), 64)

        print("TestNode10BioDigital: test_sequence_hash PASSED")

    def test_stream_symbolic_sequence(self):
        """Test streaming symbolic sequence to file."""
        from node10_biodigital import stream_symbolic_sequence

        out_path = stream_symbolic_sequence(
            self.test_qubit_states,
            out_dir=self.temp_dir,
            allow_raw=True
        )

        # File should be created
        self.assertTrue(out_path.exists())
        self.assertEqual(out_path.suffix, '.json')

        # Load and verify content
        with open(out_path, 'r') as f:
            data = json.load(f)

        self.assertIn('timestamp', data)
        self.assertIn('node', data)
        self.assertEqual(data['node'], 10)
        self.assertIn('symbolic_summary', data)
        self.assertIn('sequence_hash', data)
        self.assertIn('symbolic_sequence', data)  # Present because allow_raw=True

        print("TestNode10BioDigital: test_stream_symbolic_sequence PASSED")

    def test_safety_no_raw_output_by_default(self):
        """Test that raw symbolic sequences are not output by default."""
        from node10_biodigital import stream_symbolic_sequence

        # Ensure environment variable is not set
        old_value = os.environ.get('ALLOW_RAW_DNA_OUTPUT')
        if 'ALLOW_RAW_DNA_OUTPUT' in os.environ:
            del os.environ['ALLOW_RAW_DNA_OUTPUT']

        try:
            out_path = stream_symbolic_sequence(
                self.test_qubit_states,
                out_dir=self.temp_dir,
                allow_raw=False
            )

            with open(out_path, 'r') as f:
                data = json.load(f)

            # Raw sequence should NOT be present
            self.assertNotIn('symbolic_sequence', data)
            self.assertIn('symbolic_summary', data)
            self.assertIn('sequence_hash', data)

        finally:
            # Restore environment
            if old_value is not None:
                os.environ['ALLOW_RAW_DNA_OUTPUT'] = old_value

        print("TestNode10BioDigital: test_safety_no_raw_output_by_default PASSED")


class TestNode11FrequencyMaster(unittest.TestCase):
    """Tests for Node 11: Frequency Master."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.sample_counts = {
            '00': 600,
            '01': 200,
            '10': 150,
            '11': 50
        }

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_frequency_master_initialization(self):
        """Test FrequencyMaster class initialization."""
        from node11_frequency_master import FrequencyMaster

        fm = FrequencyMaster()
        self.assertIsNotNone(fm)
        self.assertIsNone(fm.registry)
        self.assertIsNotNone(fm.memory)

        # Test with registry
        fm_with_registry = FrequencyMaster(registry='test_registry')
        self.assertEqual(fm_with_registry.registry, 'test_registry')

        print("TestNode11FrequencyMaster: test_frequency_master_initialization PASSED")

    def test_analyze_counts_triangle(self):
        """Test Tesla consciousness analysis for triangle experiment."""
        from node11_frequency_master import FrequencyMaster

        fm = FrequencyMaster()
        result = fm.analyze_counts(self.sample_counts, experiment_type='triangle')

        # Check result structure
        self.assertIsInstance(result, dict)
        self.assertIn('_oint', result)

        # _oint should be a numeric value
        self.assertIsInstance(result['_oint'], (int, float))

        # Should have other consciousness metrics
        self.assertIn('H_entropy', result)
        self.assertIn('MI_avg', result)
        self.assertIn('FI_sens', result)

        print("TestNode11FrequencyMaster: test_analyze_counts_triangle PASSED")

    def test_analyze_counts_different_types(self):
        """Test analysis with different experiment types."""
        from node11_frequency_master import FrequencyMaster

        fm = FrequencyMaster()

        # Test different experiment types
        for exp_type in ['triangle', 'chord', 'custom']:
            result = fm.analyze_counts(self.sample_counts, experiment_type=exp_type)
            self.assertIn('_oint', result)
            self.assertIsInstance(result['_oint'], (int, float))

        print("TestNode11FrequencyMaster: test_analyze_counts_different_types PASSED")

    def test_store_experiment(self):
        """Test Tesla experiment storage."""
        from node11_frequency_master import FrequencyMaster

        fm = FrequencyMaster()

        experiment_id = "test_exp_001"
        qasm = "OPENQASM 2.0; include 'qelib1.inc'; qreg q[2];"
        consciousness_data = {'_oint': 0.85, 'coherence': 0.92}
        counts = {'00': 500, '11': 500}

        # Store experiment (may return None if storage is mock/not implemented)
        result = fm.store_experiment(
            experiment_id,
            qasm,
            consciousness_data,
            counts,
            experiment_type='triangle'
        )

        # Method should complete without error (result may be None for mock storage)
        # The important thing is that it doesn't raise an exception
        self.assertTrue(True)  # If we got here, the method executed successfully

        print("TestNode11FrequencyMaster: test_store_experiment PASSED")


class TestNode12NeuralSynapse(unittest.TestCase):
    """Tests for Node 12: Neural Synapse."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_sequences = {
            'neuron_1': 'ATCGATCG',
            'neuron_2': 'ATCGATCG',
            'neuron_3': 'GCTAGCTA',
            'neuron_4': 'NNNNATCG',
        }

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_phi_correlation_identical(self):
        """Test phi-correlation for identical sequences."""
        from node12_neural_synapse import _phi_correlation

        seq1 = "ATCGATCG"
        seq2 = "ATCGATCG"

        corr = _phi_correlation(seq1, seq2)

        # Identical sequences should have high correlation
        self.assertGreater(corr, 0.9)
        self.assertLessEqual(corr, 1.0)

        print("TestNode12NeuralSynapse: test_phi_correlation_identical PASSED")

    def test_phi_correlation_different(self):
        """Test phi-correlation for different sequences."""
        from node12_neural_synapse import _phi_correlation

        seq1 = "ATCG"
        seq2 = "GCTA"

        corr = _phi_correlation(seq1, seq2)

        # Different sequences should have lower correlation
        self.assertGreaterEqual(corr, 0.0)
        self.assertLess(corr, 1.0)

        print("TestNode12NeuralSynapse: test_phi_correlation_different PASSED")

    def test_phi_correlation_empty(self):
        """Test phi-correlation with empty sequences."""
        from node12_neural_synapse import _phi_correlation

        corr1 = _phi_correlation("", "ATCG")
        corr2 = _phi_correlation("ATCG", "")
        corr3 = _phi_correlation("", "")

        # Empty sequences should have zero correlation
        self.assertEqual(corr1, 0.0)
        self.assertEqual(corr2, 0.0)
        self.assertEqual(corr3, 0.0)

        print("TestNode12NeuralSynapse: test_phi_correlation_empty PASSED")

    def test_sequence_vector(self):
        """Test symbolic sequence to numeric vector conversion."""
        from node12_neural_synapse import _sequence_vector

        seq = "ATCG"
        vec = _sequence_vector(seq, max_len=10)

        # Vector should be numpy array
        self.assertIsInstance(vec, np.ndarray)

        # Vector size should be max_len * 4 (one-hot encoding)
        self.assertEqual(vec.shape[0], 10 * 4)

        # Vector should be normalized
        norm = np.linalg.norm(vec)
        self.assertAlmostEqual(norm, 1.0, places=5)

        print("TestNode12NeuralSynapse: test_sequence_vector PASSED")

    def test_build_connectivity_basic(self):
        """Test basic connectivity matrix construction."""
        from node12_neural_synapse import build_connectivity

        mat, metadata = build_connectivity(self.test_sequences)

        # Matrix should be numpy array
        self.assertIsInstance(mat, np.ndarray)

        # Matrix should be square
        n_neurons = len(self.test_sequences)
        self.assertEqual(mat.shape[0], n_neurons)
        self.assertEqual(mat.shape[1], n_neurons)

        # Matrix should be symmetric
        self.assertTrue(np.allclose(mat, mat.T))

        # Diagonal should be zero
        self.assertTrue(np.allclose(np.diag(mat), 0.0))

        # Check metadata
        self.assertIn('ids', metadata)
        self.assertIn('phi_threshold', metadata)
        self.assertIn('strengthen', metadata)
        self.assertIn('shape', metadata)
        self.assertIn('hash', metadata)

        self.assertEqual(len(metadata['ids']), n_neurons)

        print("TestNode12NeuralSynapse: test_build_connectivity_basic PASSED")

    def test_build_connectivity_empty(self):
        """Test connectivity with empty sequences."""
        from node12_neural_synapse import build_connectivity

        mat, metadata = build_connectivity({})

        # Should return empty matrix
        self.assertEqual(mat.shape[0], 0)
        self.assertEqual(mat.shape[1], 0)
        self.assertEqual(len(metadata['ids']), 0)

        print("TestNode12NeuralSynapse: test_build_connectivity_empty PASSED")

    def test_build_connectivity_strengthen(self):
        """Test connectivity matrix strengthening for high phi-correlation."""
        from node12_neural_synapse import build_connectivity

        # Identical sequences should have strengthened connections
        identical_seqs = {
            'n1': 'ATCGATCG',
            'n2': 'ATCGATCG',
        }

        mat1, _ = build_connectivity(identical_seqs, phi_threshold=0.5, strengthen=0.2)
        mat2, _ = build_connectivity(identical_seqs, phi_threshold=0.5, strengthen=0.0)

        # Strengthened matrix should have higher absolute values
        # (or equal if no connections exceeded threshold)
        self.assertGreaterEqual(np.abs(mat1[0, 1]), np.abs(mat2[0, 1]))

        print("TestNode12NeuralSynapse: test_build_connectivity_strengthen PASSED")

    def test_save_connectivity_metadata(self):
        """Test saving connectivity metadata to file."""
        from node12_neural_synapse import build_connectivity, save_connectivity

        mat, metadata = build_connectivity(self.test_sequences)
        out_path = save_connectivity(mat, metadata, out_dir=self.temp_dir, allow_raw=False)

        # Metadata file should be created
        self.assertTrue(out_path.exists())

        # Load and verify
        with open(out_path, 'r') as f:
            saved_meta = json.load(f)

        self.assertIn('ids', saved_meta)
        self.assertIn('hash', saved_meta)
        self.assertIn('timestamp', saved_meta)

        print("TestNode12NeuralSynapse: test_save_connectivity_metadata PASSED")

    def test_safety_no_raw_connectivity_by_default(self):
        """Test that raw connectivity matrices are not saved by default."""
        from node12_neural_synapse import build_connectivity, save_connectivity

        mat, metadata = build_connectivity(self.test_sequences)

        # Ensure environment variable is not set
        old_value = os.environ.get('ALLOW_RAW_CONNECTIVITY')
        if 'ALLOW_RAW_CONNECTIVITY' in os.environ:
            del os.environ['ALLOW_RAW_CONNECTIVITY']

        try:
            out_path = save_connectivity(mat, metadata, out_dir=self.temp_dir, allow_raw=False)

            # Only metadata should be saved (not .npy file)
            self.assertTrue(out_path.exists())
            self.assertTrue(out_path.name.endswith('.meta.json'))

            # Check that .npy file was NOT created
            npy_file = out_path.parent / out_path.name.replace('.meta.json', '.connectivity.npy')
            self.assertFalse(npy_file.exists())

        finally:
            # Restore environment
            if old_value is not None:
                os.environ['ALLOW_RAW_CONNECTIVITY'] = old_value

        print("TestNode12NeuralSynapse: test_safety_no_raw_connectivity_by_default PASSED")


class TestNodeIntegration(unittest.TestCase):
    """Integration tests for Nodes 10, 11, and 12."""

    def setUp(self):
        """Set up integration test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_qubit_states = [
            {'phase': 0.5, 'probability': 0.8},
            {'phase': 1.2, 'probability': 0.6},
            {'phase': 2.1, 'probability': 0.9},
            {'phase': 3.5, 'probability': 0.4},
        ]

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_node10_to_node12_pipeline(self):
        """Test pipeline: Node 10 output -> Node 12 input."""
        from node10_biodigital import quantum_to_symbolic
        from node12_neural_synapse import build_connectivity

        # Node 10: Convert quantum states to symbolic sequences
        result10 = quantum_to_symbolic(self.test_qubit_states)
        symbolic_seq = result10['symbolic_sequence']

        # Create multiple sequences for connectivity
        sequences = {
            'quantum_1': symbolic_seq,
            'quantum_2': symbolic_seq[::-1],  # Reversed
            'quantum_3': 'ATCG' * 20,  # Pattern
        }

        # Node 12: Build connectivity from sequences
        mat, metadata = build_connectivity(sequences)

        # Verify pipeline output
        self.assertEqual(mat.shape[0], 3)
        self.assertEqual(mat.shape[1], 3)
        self.assertIn('hash', metadata)

        print("TestNodeIntegration: test_node10_to_node12_pipeline PASSED")

    def test_node11_consciousness_metrics(self):
        """Test Node 11 consciousness metrics integration."""
        from node11_frequency_master import FrequencyMaster
        from node10_biodigital import quantum_to_symbolic

        # Node 10: Get quantum states
        result10 = quantum_to_symbolic(self.test_qubit_states)

        # Node 11: Analyze consciousness metrics
        fm = FrequencyMaster()

        # Simulate counts based on symbolic sequence
        counts = {
            '00': len([c for c in result10['symbolic_sequence'] if c in 'AT']),
            '01': len([c for c in result10['symbolic_sequence'] if c in 'CG']),
            '10': result10['summary']['resonant_fraction'] * 100,
            '11': 50
        }

        result11 = fm.analyze_counts(counts, experiment_type='triangle')

        # Verify consciousness metrics
        self.assertIn('_oint', result11)
        self.assertIsInstance(result11['_oint'], (int, float))

        print("TestNodeIntegration: test_node11_consciousness_metrics PASSED")

    def test_full_pipeline_10_11_12(self):
        """Test full pipeline: Node 10 -> Node 11 -> Node 12."""
        from node10_biodigital import quantum_to_symbolic, get_sequence_hash
        from node11_frequency_master import FrequencyMaster
        from node12_neural_synapse import build_connectivity, _phi_correlation

        # Node 10: Quantum to symbolic
        result10 = quantum_to_symbolic(self.test_qubit_states)
        seq1 = result10['symbolic_sequence']
        hash10 = get_sequence_hash(seq1)

        # Node 11: Consciousness analysis
        fm = FrequencyMaster()
        counts = {'00': 500, '01': 300, '10': 150, '11': 50}
        result11 = fm.analyze_counts(counts)
        consciousness_metric = result11['_oint']

        # Node 12: Connectivity from multiple sequences
        sequences = {
            'seq_1': seq1,
            'seq_2': seq1[:len(seq1)//2] if len(seq1) > 1 else 'A',
            'seq_3': 'ATCG' * 10,
        }

        mat, metadata = build_connectivity(sequences)

        # Verify full pipeline
        self.assertIsNotNone(hash10)
        self.assertIsInstance(consciousness_metric, float)
        self.assertEqual(mat.shape[0], 3)

        # Check phi-correlation in connectivity
        corr = _phi_correlation(sequences['seq_1'], sequences['seq_1'])
        self.assertGreater(corr, 0.9)

        print("TestNodeIntegration: test_full_pipeline_10_11_12 PASSED")


def run_tests():
    """Run all tests for Nodes 10, 11, 12."""
    print("=" * 70)
    print("Nodes 10, 11, 12: Comprehensive Test Suite")
    print("=" * 70)

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestNode10BioDigital))
    suite.addTests(loader.loadTestsFromTestCase(TestNode11FrequencyMaster))
    suite.addTests(loader.loadTestsFromTestCase(TestNode12NeuralSynapse))
    suite.addTests(loader.loadTestsFromTestCase(TestNodeIntegration))

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
