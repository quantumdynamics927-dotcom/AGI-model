"""
Test New Golden Ratio Modules (Standalone)

This script tests the new modules without requiring torch or trained models.
"""

import numpy as np

def main():
    print("="*80)
    print("TESTING NEW GOLDEN RATIO MODULES")
    print("="*80)
    print()

    # Test 1: Import modules
    print("[1/6] Testing module imports...")
    try:
        from golden_ratio_statistics import GoldenRatioStatistics
        print("  ✓ golden_ratio_statistics imported")
    except ImportError as e:
        print(f"  ✗ Failed to import golden_ratio_statistics: {e}")

    try:
        from golden_ratio_detectors import MultiMethodDetector
        print("  ✓ golden_ratio_detectors imported")
    except ImportError as e:
        print(f"  ✗ Failed to import golden_ratio_detectors: {e}")

    try:
        from golden_ratio_visualization import GoldenRatioVisualizer
        print("  ✓ golden_ratio_visualization imported (note: requires matplotlib)")
    except ImportError as e:
        print(f"  ✗ Failed to import golden_ratio_visualization: {e}")

    try:
        from golden_ratio_analysis_v2 import ComprehensiveGoldenRatioAnalyzer
        print("  ✓ golden_ratio_analysis_v2 imported")
    except ImportError as e:
        print(f"  ✗ Failed to import golden_ratio_analysis_v2: {e}")

    print()

    # Test 2: Create synthetic data
    print("[2/6] Creating synthetic test data...")
    np.random.seed(42)
    phi = (1 + np.sqrt(5)) / 2

    # Generate synthetic latent codes with embedded golden ratio
    n_samples, n_dims = 500, 32
    latent_codes = np.random.randn(n_samples, n_dims)

    # Embed golden ratio in some dimensions
    for i in range(0, 10, 2):
        latent_codes[:, i+1] = phi * latent_codes[:, i] + 0.1 * np.random.randn(n_samples)

    print(f"  Generated {n_samples} samples × {n_dims} dimensions")
    print(f"  Embedded golden ratio in 5 dimension pairs")
    print()

    # Test 3: Statistical analysis
    print("[3/6] Testing GoldenRatioStatistics...")
    try:
        from golden_ratio_statistics import GoldenRatioStatistics

        stats = GoldenRatioStatistics(latent_codes, random_state=42)

        # Bootstrap (reduced iterations for testing)
        print("  Running bootstrap threshold estimation (2000 iterations)...")
        bootstrap_result = stats.bootstrap_threshold(n_bootstrap=2000)
        print(f"    Threshold: {bootstrap_result['threshold']:.4f}")
        print(f"    95% CI: [{bootstrap_result['ci_lower']:.4f}, {bootstrap_result['ci_upper']:.4f}]")

        # Permutation test (reduced iterations for testing)
        print("  Running permutation test (1000 permutations)...")
        perm_result = stats.permutation_test(n_permutations=1000, threshold=bootstrap_result['threshold'])
        print(f"    p-value: {perm_result['p_value']:.4f}")
        print(f"    Significant: {perm_result['is_significant']}")

        # Effect sizes
        print("  Calculating effect sizes...")
        effect_result = stats.calculate_effect_sizes(threshold=bootstrap_result['threshold'])
        print(f"    Cohen's d: {effect_result['cohens_d']:.3f}")
        print(f"    Odds ratio: {effect_result['odds_ratio']:.2f}")

        print("  ✓ Statistical analysis complete")
    except Exception as e:
        print(f"  ✗ Error in statistical analysis: {e}")
        import traceback
        traceback.print_exc()

    print()

    # Test 4: Multi-method detection
    print("[4/6] Testing MultiMethodDetector...")
    try:
        from golden_ratio_detectors import MultiMethodDetector

        detector = MultiMethodDetector(latent_codes)
        detection_results = detector.detect_all(threshold=0.15)

        print(f"  Enhanced ratio: {detection_results['enhanced_ratio']['n_golden_pairs']} pairs")
        print(f"  Fibonacci: {detection_results['fibonacci']['n_patterns']} patterns")
        print(f"  Continued fraction: {detection_results['continued_fraction']['n_detections']} detections")
        print(f"  Spiral: {'golden' if detection_results['spiral']['is_golden_spiral'] else 'not golden'}")
        print(f"  Ensemble votes: {detection_results['ensemble_votes']}/4")
        print(f"  Consensus: {detection_results['consensus']}")

        print("  ✓ Multi-method detection complete")
    except Exception as e:
        print(f"  ✗ Error in detection: {e}")
        import traceback
        traceback.print_exc()

    print()

    # Test 5: Visualization (if matplotlib available)
    print("[5/6] Testing visualization...")
    try:
        from golden_ratio_visualization import plot_quick_summary

        # Prepare results
        statistical_results = {
            'bootstrap': bootstrap_result,
            'permutation': perm_result,
            'effect_sizes': effect_result,
            'recommended_threshold': bootstrap_result['threshold'],
            'conclusion': 'significant' if perm_result['is_significant'] else 'not_significant'
        }

        print("  Creating quick summary plot...")
        plot_quick_summary(latent_codes, statistical_results, save_path='test_golden_ratio_quick.png')
        print("  ✓ Visualization complete (saved to test_golden_ratio_quick.png)")
    except ImportError as e:
        print(f"  ⚠ Skipping visualization (missing dependencies): {e}")
    except Exception as e:
        print(f"  ✗ Error in visualization: {e}")
        import traceback
        traceback.print_exc()

    print()

    # Test 6: Comprehensive analyzer
    print("[6/6] Testing ComprehensiveGoldenRatioAnalyzer...")
    try:
        from golden_ratio_analysis_v2 import ComprehensiveGoldenRatioAnalyzer

        analyzer = ComprehensiveGoldenRatioAnalyzer(latent_codes, random_state=42)

        print("  Running quick analysis (reduced iterations)...")
        results = analyzer.run_quick_analysis(output_dir='.')

        print(f"\n  Summary:")
        print(f"    Conclusion: {results['summary']['conclusion']}")
        print(f"    p-value: {results['summary']['key_metrics']['p_value']:.4f}")
        print(f"    Cohen's d: {results['summary']['key_metrics']['cohens_d']:.3f}")

        if results['visualizations_created']:
            print(f"    Visualizations: {len(results['visualizations_created'])} files created")

        print("  ✓ Comprehensive analysis complete")
    except Exception as e:
        print(f"  ✗ Error in comprehensive analysis: {e}")
        import traceback
        traceback.print_exc()

    print()
    print("="*80)


if __name__ == "__main__":
    main()

