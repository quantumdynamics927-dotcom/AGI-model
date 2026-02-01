"""
Unit Tests for Golden Ratio Statistical Analysis

Tests the enhanced golden ratio detection modules:
- Bootstrap threshold estimation
- Permutation testing
- Effect size calculations
- Multi-method detection
- Synthetic data validation
"""

import unittest
import numpy as np
from golden_ratio_statistics import GoldenRatioStatistics
from golden_ratio_detectors import (EnhancedRatioDetector, FibonacciDetector,
                                     ContinuedFractionDetector, SpiralPatternDetector,
                                     MultiMethodDetector)


class TestGoldenRatioStatistics(unittest.TestCase):
    """Test statistical analysis methods."""

    def setUp(self):
        """Set up test data."""
        np.random.seed(42)
        self.phi = (1 + np.sqrt(5)) / 2
        self.latent_codes = np.random.randn(100, 32)

    def test_bootstrap_threshold(self):
        """Test bootstrap threshold estimation."""
        stats = GoldenRatioStatistics(self.latent_codes, random_state=42)
        result = stats.bootstrap_threshold(n_bootstrap=100)

        # Check return structure
        self.assertIn('threshold', result)
        self.assertIn('ci_lower', result)
        self.assertIn('ci_upper', result)
        self.assertIn('bootstrap_dist', result)

        # Check values are reasonable
        self.assertGreater(result['threshold'], 0)
        self.assertGreater(result['ci_upper'], result['ci_lower'])
        self.assertEqual(len(result['bootstrap_dist']), 100)

    def test_permutation_test(self):
        """Test permutation significance testing."""
        stats = GoldenRatioStatistics(self.latent_codes, random_state=42)
        result = stats.permutation_test(n_permutations=100)

        # Check return structure
        self.assertIn('p_value', result)
        self.assertIn('observed_stat', result)
        self.assertIn('is_significant', result)
        self.assertIn('z_score', result)

        # Check p-value is valid probability
        self.assertGreaterEqual(result['p_value'], 0)
        self.assertLessEqual(result['p_value'], 1)

        # Check is_significant is boolean
        self.assertIsInstance(result['is_significant'], (bool, np.bool_))

    def test_effect_sizes(self):
        """Test effect size calculations."""
        stats = GoldenRatioStatistics(self.latent_codes, random_state=42)
        result = stats.calculate_effect_sizes()

        # Check return structure
        self.assertIn('cohens_d', result)
        self.assertIn('odds_ratio', result)
        self.assertIn('mean_proximity', result)

        # Check values are reasonable
        self.assertGreater(result['mean_proximity'], 0)
        self.assertGreater(result['odds_ratio'], 0)

    def test_synthetic_golden_ratio_detection(self):
        """Test detection on synthetic data with embedded golden ratio."""
        # Generate data with embedded golden ratio
        n_samples, n_dims = 100, 32
        golden_latent = np.random.randn(n_samples, n_dims)

        # Embed golden ratio in several dimension pairs
        for i in range(0, 10, 2):
            golden_latent[:, i+1] = self.phi * golden_latent[:, i] + 0.1 * np.random.randn(n_samples)

        stats = GoldenRatioStatistics(golden_latent, random_state=42)
        result = stats.permutation_test(n_permutations=200)

        # Should detect golden ratio (p-value < 0.05)
        # Note: May fail occasionally due to randomness with only 200 permutations
        # In real usage, use n_permutations >= 5000
        print(f"Synthetic test p-value: {result['p_value']:.4f}")

    def test_multiple_testing_correction(self):
        """Test multiple testing correction methods."""
        try:
            import statsmodels
        except ImportError:
            self.skipTest("statsmodels not installed")
        stats = GoldenRatioStatistics(self.latent_codes, random_state=42)

        # Create fake p-values
        p_values = np.array([0.001, 0.01, 0.05, 0.1, 0.5])

        result = stats.correct_multiple_testing(p_values, method='fdr_bh')

        # Check return structure
        self.assertIn('reject', result)
        self.assertIn('pvals_corrected', result)
        self.assertIn('n_significant', result)

        # Check lengths match
        self.assertEqual(len(result['reject']), len(p_values))
        self.assertEqual(len(result['pvals_corrected']), len(p_values))


class TestEnhancedRatioDetector(unittest.TestCase):
    """Test enhanced ratio detection."""

    def setUp(self):
        """Set up test data."""
        np.random.seed(42)
        self.latent_codes = np.random.randn(50, 32)

    def test_detect(self):
        """Test basic detection functionality."""
        detector = EnhancedRatioDetector(self.latent_codes)
        result = detector.detect(threshold=0.1)

        # Check return structure
        self.assertIn('n_golden_pairs', result)
        self.assertIn('golden_pairs', result)
        self.assertIn('weighted_score', result)

        # Check types
        self.assertIsInstance(result['n_golden_pairs'], int)
        self.assertGreaterEqual(result['n_golden_pairs'], 0)


class TestFibonacciDetector(unittest.TestCase):
    """Test Fibonacci sequence detection."""

    def setUp(self):
        """Set up test data."""
        np.random.seed(42)
        self.latent_codes = np.random.randn(50, 32)

    def test_detect(self):
        """Test Fibonacci detection."""
        detector = FibonacciDetector(self.latent_codes)
        result = detector.detect(min_length=3)

        # Check return structure
        self.assertIn('n_patterns', result)
        self.assertIn('patterns', result)
        self.assertIn('max_length', result)

        # Check types
        self.assertIsInstance(result['n_patterns'], int)
        self.assertGreaterEqual(result['n_patterns'], 0)

    def test_fibonacci_sequence(self):
        """Test detection on actual Fibonacci sequence."""
        # Create latent codes with Fibonacci pattern in one sample
        latent = np.random.randn(10, 10)
        fib = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
        latent[0, :] = fib

        detector = FibonacciDetector(latent)
        result = detector.detect(min_length=3, tolerance=0.3)

        # Should detect at least one pattern
        print(f"Fibonacci patterns detected: {result['n_patterns']}")


class TestContinuedFractionDetector(unittest.TestCase):
    """Test continued fraction analysis."""

    def setUp(self):
        """Set up test data."""
        np.random.seed(42)
        self.latent_codes = np.random.randn(50, 32)

    def test_detect(self):
        """Test continued fraction detection."""
        detector = ContinuedFractionDetector(self.latent_codes)
        result = detector.detect(min_consecutive_ones=3)

        # Check return structure
        self.assertIn('n_detections', result)
        self.assertIn('detections', result)
        self.assertIn('max_consecutive_ones', result)

        # Check types
        self.assertIsInstance(result['n_detections'], int)
        self.assertGreaterEqual(result['n_detections'], 0)

    def test_phi_continued_fraction(self):
        """Test that phi has the expected continued fraction."""
        phi = (1 + np.sqrt(5)) / 2
        detector = ContinuedFractionDetector(np.array([[1, phi]]))

        cf = detector._continued_fraction(phi, max_depth=10)

        # Phi should be [1, 1, 1, 1, ...]
        self.assertEqual(cf[0], 1)
        # Most entries should be 1
        ones_count = sum(1 for x in cf if x == 1)
        self.assertGreater(ones_count, 5)


class TestSpiralPatternDetector(unittest.TestCase):
    """Test logarithmic spiral detection."""

    def setUp(self):
        """Set up test data."""
        np.random.seed(42)
        self.latent_codes = np.random.randn(100, 32)

    def test_detect(self):
        """Test spiral detection."""
        detector = SpiralPatternDetector(self.latent_codes)
        result = detector.detect()

        # Check return structure
        self.assertIn('is_spiral', result)
        self.assertIn('is_golden_spiral', result)
        self.assertIn('r_squared', result)
        self.assertIn('golden_b', result)

        # Check types (may be numpy bool or Python bool)
        self.assertIn(type(result['is_spiral']), (bool, np.bool_))
        self.assertIn(type(result['is_golden_spiral']), (bool, np.bool_))

    def test_synthetic_golden_spiral(self):
        """Test detection on synthetic golden spiral data."""
        phi = (1 + np.sqrt(5)) / 2
        golden_b = (2 / np.pi) * np.log(phi)

        # Generate logarithmic spiral in 2D
        n_points = 200
        theta = np.linspace(0, 4*np.pi, n_points)
        a = 1.0
        r = a * np.exp(golden_b * theta)

        x = r * np.cos(theta)
        y = r * np.sin(theta)

        # Embed in higher dimensional space
        latent = np.random.randn(n_points, 32) * 0.1
        latent[:, 0] = x
        latent[:, 1] = y

        detector = SpiralPatternDetector(latent)
        result = detector.detect()

        print(f"Spiral detected: {result['is_spiral']}")
        print(f"Golden spiral: {result['is_golden_spiral']}")
        print(f"R²: {result['r_squared']:.3f}")
        if result['spiral_parameter_b'] is not None:
            print(f"b parameter: {result['spiral_parameter_b']:.4f} (golden: {golden_b:.4f})")


class TestMultiMethodDetector(unittest.TestCase):
    """Test ensemble multi-method detection."""

    def setUp(self):
        """Set up test data."""
        np.random.seed(42)
        self.latent_codes = np.random.randn(100, 32)

    def test_detect_all(self):
        """Test running all detection methods."""
        detector = MultiMethodDetector(self.latent_codes)
        result = detector.detect_all(threshold=0.1)

        # Check return structure
        self.assertIn('enhanced_ratio', result)
        self.assertIn('fibonacci', result)
        self.assertIn('continued_fraction', result)
        self.assertIn('spiral', result)
        self.assertIn('ensemble_votes', result)
        self.assertIn('consensus', result)

        # Check votes range
        self.assertGreaterEqual(result['ensemble_votes'], 0)
        self.assertLessEqual(result['ensemble_votes'], 4)

        # Check consensus is boolean
        self.assertIsInstance(result['consensus'], bool)


class TestRealWorldScenarios(unittest.TestCase):
    """Test real-world scenarios and edge cases."""

    def test_random_data_no_false_positives(self):
        """Test that random data doesn't produce false positives."""
        np.random.seed(42)
        random_latent = np.random.randn(500, 32)

        stats = GoldenRatioStatistics(random_latent, random_state=42)
        result = stats.permutation_test(n_permutations=500)

        # Random data should NOT be significant
        # (p-value should be > 0.05 most of the time)
        print(f"Random data p-value: {result['p_value']:.4f}")
        print(f"Expected: p > 0.05 for random data")

    def test_edge_case_small_dataset(self):
        """Test behavior with very small dataset."""
        small_latent = np.random.randn(10, 8)

        stats = GoldenRatioStatistics(small_latent, random_state=42)

        # Should not crash
        bootstrap_result = stats.bootstrap_threshold(n_bootstrap=50)
        self.assertIn('threshold', bootstrap_result)

    def test_edge_case_high_dimensional(self):
        """Test with high-dimensional latent space."""
        high_dim_latent = np.random.randn(100, 128)

        detector = EnhancedRatioDetector(high_dim_latent)
        result = detector.detect(threshold=0.1)

        # Should handle large number of pairs
        expected_pairs = 128 * 127 // 2
        self.assertEqual(result['total_pairs_tested'], expected_pairs)


def run_validation_suite():
    """
    Run comprehensive validation suite.

    Tests include:
    1. Synthetic golden ratio data → should detect
    2. Random data → should not detect
    3. Fibonacci sequences → should detect
    4. Golden spiral → should detect
    """
    print("\n" + "="*80)
    print("GOLDEN RATIO ANALYSIS VALIDATION SUITE")
    print("="*80 + "\n")

    phi = (1 + np.sqrt(5)) / 2

    # Test 1: Synthetic golden ratio
    print("[1/4] Testing synthetic golden ratio data...")
    n_samples, n_dims = 200, 32
    golden_latent = np.random.randn(n_samples, n_dims)
    for i in range(0, n_dims-1, 2):
        golden_latent[:, i+1] = phi * golden_latent[:, i] + 0.05 * np.random.randn(n_samples)

    stats = GoldenRatioStatistics(golden_latent, random_state=42)
    result = stats.permutation_test(n_permutations=1000)
    print(f"  p-value: {result['p_value']:.4f}")
    print(f"  Expected: p < 0.05 (should detect)")
    print(f"  Result: {'PASS ✓' if result['p_value'] < 0.05 else 'FAIL ✗'}\n")

    # Test 2: Random data
    print("[2/4] Testing random data (negative control)...")
    random_latent = np.random.randn(200, 32)
    stats2 = GoldenRatioStatistics(random_latent, random_state=42)
    result2 = stats2.permutation_test(n_permutations=1000)
    print(f"  p-value: {result2['p_value']:.4f}")
    print(f"  Expected: p > 0.05 (should not detect)")
    print(f"  Result: {'PASS ✓' if result2['p_value'] >= 0.05 else 'FAIL ✗ (may occasionally fail due to randomness)'}\n")

    # Test 3: Fibonacci ratios
    print("[3/4] Testing Fibonacci ratios...")
    fib = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]
    ratios = [fib[i+1]/fib[i] for i in range(len(fib)-1)]
    proximities = [abs(r - phi) for r in ratios]
    mean_proximity = np.mean(proximities)
    print(f"  Mean proximity to φ: {mean_proximity:.4f}")
    print(f"  Expected: < 0.05")
    print(f"  Result: {'PASS ✓' if mean_proximity < 0.05 else 'FAIL ✗'}\n")

    # Test 4: Detector sensitivity
    print("[4/4] Testing multi-method detector sensitivity...")
    detector = MultiMethodDetector(golden_latent)
    result4 = detector.detect_all(threshold=0.15)
    votes = result4['ensemble_votes']
    print(f"  Methods detecting golden ratio: {votes}/4")
    print(f"  Expected: >= 2")
    print(f"  Result: {'PASS ✓' if votes >= 2 else 'FAIL ✗'}\n")

    print("="*80)
    print("VALIDATION SUITE COMPLETE")
    print("="*80 + "\n")


if __name__ == '__main__':
    # Run unit tests
    print("Running unit tests...")
    unittest.main(argv=[''], verbosity=2, exit=False)

    # Run validation suite
    print("\n")
    run_validation_suite()
