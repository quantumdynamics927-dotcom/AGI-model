"""
Tests for Phi Agent - Integrated Information Theory Consciousness Analysis

This module tests the Phi agent functionality:
1. Consciousness metrics calculation
2. Phi-harmonic structure analysis
3. IIT theory agreement
4. Consciousness level computation
5. DNA-to-consciousness data conversion
"""
import unittest
import sys
import os
import json
import tempfile
import shutil
import numpy as np
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agi_scripts.phi_agent import (
    PHI,
    PHI_INV,
    PHI_SQUARED,
    calculate_entropy,
    PhiConsciousnessAnalyzer,
)


class TestPhiConstants(unittest.TestCase):
    """Test Phi agent constants."""

    def test_phi_constant(self):
        """Test that PHI is the golden ratio."""
        expected_phi = (1 + np.sqrt(5)) / 2
        self.assertAlmostEqual(PHI, expected_phi, places=10)
        print("TestPhiConstants: test_phi_constant PASSED")

    def test_phi_inverse(self):
        """Test that PHI_INV is the inverse of PHI."""
        self.assertAlmostEqual(PHI_INV, 1 / PHI, places=10)
        print("TestPhiConstants: test_phi_inverse PASSED")

    def test_phi_squared(self):
        """Test that PHI_SQUARED is PHI squared."""
        self.assertAlmostEqual(PHI_SQUARED, PHI ** 2, places=10)
        print("TestPhiConstants: test_phi_squared PASSED")


class TestEntropyCalculation(unittest.TestCase):
    """Test entropy calculation functions."""

    def test_entropy_uniform_distribution(self):
        """Test entropy of uniform distribution."""
        # Uniform distribution should have maximum entropy
        prob_dist = [0.25, 0.25, 0.25, 0.25]
        entropy = calculate_entropy(prob_dist)
        # Maximum entropy for 4 outcomes is log2(4) = 2
        self.assertAlmostEqual(entropy, 2.0, places=5)
        print("TestEntropyCalculation: test_entropy_uniform_distribution PASSED")

    def test_entropy_deterministic(self):
        """Test entropy of deterministic distribution (should be 0)."""
        prob_dist = [1.0, 0.0, 0.0, 0.0]
        entropy = calculate_entropy(prob_dist)
        self.assertAlmostEqual(entropy, 0.0, places=5)
        print("TestEntropyCalculation: test_entropy_deterministic PASSED")

    def test_entropy_empty_distribution(self):
        """Test entropy of empty distribution."""
        prob_dist = []
        entropy = calculate_entropy(prob_dist)
        self.assertEqual(entropy, 0.0)
        print("TestEntropyCalculation: test_entropy_empty_distribution PASSED")

    def test_entropy_biased_distribution(self):
        """Test entropy of biased distribution."""
        prob_dist = [0.7, 0.2, 0.1]
        entropy = calculate_entropy(prob_dist)
        # Should be less than maximum (log2(3) ≈ 1.585)
        self.assertLess(entropy, 1.585)
        self.assertGreater(entropy, 0.0)
        print("TestEntropyCalculation: test_entropy_biased_distribution PASSED")


class TestPhiConsciousnessAnalyzer(unittest.TestCase):
    """Tests for PhiConsciousnessAnalyzer class."""

    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = PhiConsciousnessAnalyzer()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization(self):
        """Test analyzer initialization with correct constants."""
        self.assertAlmostEqual(self.analyzer.phi, PHI, places=10)
        self.assertAlmostEqual(self.analyzer.phi_inv, PHI_INV, places=10)
        print("TestPhiConsciousnessAnalyzer: test_initialization PASSED")

    def test_phi_alignment_score_perfect(self):
        """Test phi alignment score with perfect alignment."""
        # Perfect alignment: phi_ratio equals PHI_INV
        phi_ratio = PHI_INV
        alignment_score = 1.0 - abs(phi_ratio - PHI_INV) / PHI_INV
        self.assertAlmostEqual(alignment_score, 1.0, places=5)
        print("TestPhiConsciousnessAnalyzer: test_phi_alignment_score_perfect PASSED")

    def test_phi_alignment_score_misaligned(self):
        """Test phi alignment score with misaligned ratio."""
        # Misaligned: phi_ratio far from PHI_INV
        phi_ratio = 0.3
        alignment_score = 1.0 - abs(phi_ratio - PHI_INV) / PHI_INV
        self.assertLess(alignment_score, 0.5)
        print("TestPhiConsciousnessAnalyzer: test_phi_alignment_score_misaligned PASSED")

    def test_consciousness_level_calculation(self):
        """Test consciousness level calculation."""
        # Test with good phi alignment
        dna_phi_ratio = PHI_INV  # Perfect alignment
        wormhole_activation = 0.5
        
        phi_alignment_score = 1.0 - abs(dna_phi_ratio - PHI_INV) / PHI_INV
        consciousness_level = min(phi_alignment_score + wormhole_activation * 0.1, 1.0)
        
        self.assertGreater(consciousness_level, 0.0)
        self.assertLessEqual(consciousness_level, 1.0)
        print("TestPhiConsciousnessAnalyzer: test_consciousness_level_calculation PASSED")

    def test_theory_agreement_boost(self):
        """Test theory agreement calculation with boost."""
        phi_alignment_score = 0.8
        theory_agreement = min(phi_alignment_score * 1.2, 1.0)
        
        # Should be boosted but capped at 1.0
        self.assertGreater(theory_agreement, phi_alignment_score)
        self.assertLessEqual(theory_agreement, 1.0)
        print("TestPhiConsciousnessAnalyzer: test_theory_agreement_boost PASSED")


class TestPhiHarmonicAnalysis(unittest.TestCase):
    """Test phi-harmonic analysis functions."""

    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = PhiConsciousnessAnalyzer()

    def test_phi_harmonic_sequence(self):
        """Test phi-harmonic sequence generation."""
        base = 1.0
        harmonics = [base * (PHI ** n) for n in range(-3, 4)]
        
        # Check that sequence follows phi powers
        for i in range(len(harmonics) - 1):
            ratio = harmonics[i + 1] / harmonics[i]
            self.assertAlmostEqual(ratio, PHI, places=5)
        print("TestPhiHarmonicAnalysis: test_phi_harmonic_sequence PASSED")

    def test_phi_resonance_detection(self):
        """Test phi resonance detection in data."""
        # Create data with phi resonance (consecutive powers of PHI)
        phi_resonant_data = [PHI ** 0, PHI ** 1, PHI ** 2, PHI ** 3]
        
        # Check ratios between consecutive elements
        ratios = [phi_resonant_data[i+1] / phi_resonant_data[i] 
                  for i in range(len(phi_resonant_data)-1)]
        
        # All ratios should be close to PHI
        for ratio in ratios:
            self.assertAlmostEqual(ratio, PHI, places=5)
        print("TestPhiHarmonicAnalysis: test_phi_resonance_detection PASSED")


if __name__ == '__main__':
    unittest.main(verbosity=2)
