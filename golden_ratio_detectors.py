"""
Golden Ratio Multi-Method Detection Module

Implements 4 complementary detection algorithms:
1. EnhancedRatioDetector - All pairwise ratio analysis
2. FibonacciDetector - Fibonacci sequence detection
3. ContinuedFractionDetector - Continued fraction analysis
4. SpiralPatternDetector - Logarithmic spiral detection
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from sklearn.decomposition import PCA
from scipy.optimize import curve_fit
from scipy.stats import gaussian_kde


class EnhancedRatioDetector:
    """
    Enhanced dimension ratio analysis.

    Analyzes all pairwise ratios (not just adjacent dimensions),
    weights by variance, checks symmetry, and tracks stability.

    Parameters
    ----------
    latent_codes : ndarray, shape (n_samples, n_dimensions)
        Latent representations
    """

    def __init__(self, latent_codes: np.ndarray):
        self.latent_codes = latent_codes
        self.phi = (1 + np.sqrt(5)) / 2
        self.n_samples, self.n_dims = latent_codes.shape

    def detect(self, threshold: float = 0.1) -> Dict:
        """
        Detect golden ratio patterns in all pairwise dimension ratios.

        Parameters
        ----------
        threshold : float, default=0.1
            Proximity threshold for golden ratio classification

        Returns
        -------
        dict
            Detection results including:
            - n_golden_pairs : int
                Number of dimension pairs with golden ratio
            - golden_pairs : list of tuples
                (dim_i, dim_j, proximity, confidence)
            - all_proximities : ndarray
                All proximity values
            - weighted_score : float
                Variance-weighted detection score
        """
        golden_pairs = []
        all_proximities = []
        dimension_variances = np.var(self.latent_codes, axis=0)

        # Analyze all pairwise combinations
        for i in range(self.n_dims):
            for j in range(i + 1, self.n_dims):
                # Forward ratio: dim_i / dim_j
                ratio_forward = np.abs(self.latent_codes[:, i]) / (np.abs(self.latent_codes[:, j]) + 1e-10)
                proximity_forward = np.abs(ratio_forward - self.phi)
                mean_prox_forward = np.mean(proximity_forward)

                # Backward ratio: dim_j / dim_i
                ratio_backward = np.abs(self.latent_codes[:, j]) / (np.abs(self.latent_codes[:, i]) + 1e-10)
                proximity_backward = np.abs(ratio_backward - self.phi)
                mean_prox_backward = np.mean(proximity_backward)

                # Take minimum (best match)
                mean_proximity = min(mean_prox_forward, mean_prox_backward)
                all_proximities.append(mean_proximity)

                # Variance weighting (higher variance = more reliable)
                weight = (dimension_variances[i] + dimension_variances[j]) / 2
                confidence = weight * (1 - mean_proximity)  # Higher is better

                if mean_proximity < threshold:
                    golden_pairs.append((i, j, mean_proximity, confidence))

        all_proximities = np.array(all_proximities)

        # Weighted score: average confidence of detected pairs
        weighted_score = np.mean([conf for _, _, _, conf in golden_pairs]) if golden_pairs else 0.0

        return {
            'n_golden_pairs': len(golden_pairs),
            'golden_pairs': sorted(golden_pairs, key=lambda x: x[2]),  # Sort by proximity
            'all_proximities': all_proximities,
            'weighted_score': weighted_score,
            'total_pairs_tested': len(all_proximities)
        }


class FibonacciDetector:
    """
    Fibonacci sequence pattern detection.

    Detects sequences where consecutive values follow Fibonacci-like growth,
    with ratios converging to phi.

    Parameters
    ----------
    latent_codes : ndarray
        Latent representations
    """

    def __init__(self, latent_codes: np.ndarray):
        self.latent_codes = latent_codes
        self.phi = (1 + np.sqrt(5)) / 2
        self.n_samples, self.n_dims = latent_codes.shape

    def detect(self, min_length: int = 3, tolerance: float = 0.2) -> Dict:
        """
        Detect Fibonacci-like sequences in latent dimensions.

        A Fibonacci-like sequence satisfies: d[i] + d[i+1] ≈ d[i+2]
        And ratios d[i+1]/d[i] should converge to phi.

        Parameters
        ----------
        min_length : int, default=3
            Minimum sequence length to consider
        tolerance : float, default=0.2
            Relative tolerance for Fibonacci relation

        Returns
        -------
        dict
            Detection results
        """
        patterns = []

        for sample_idx in range(self.n_samples):
            sample = self.latent_codes[sample_idx, :]

            # Find Fibonacci-like sequences using dynamic programming
            # dp[(i,j)] = length of sequence ending at positions i, j
            dp = {}

            for i in range(self.n_dims - 2):
                for j in range(i + 1, self.n_dims - 1):
                    for k in range(j + 1, self.n_dims):
                        # Check Fibonacci relation: sample[i] + sample[j] ≈ sample[k]
                        expected = sample[i] + sample[j]
                        actual = sample[k]

                        if abs(expected) > 1e-10:
                            relative_error = abs(actual - expected) / abs(expected)
                            if relative_error < tolerance:
                                # Extend sequence
                                prev_length = dp.get((i, j), 2)
                                dp[(j, k)] = prev_length + 1

            # Analyze found sequences
            if dp:
                for (i, j), length in dp.items():
                    if length >= min_length:
                        # Check ratio convergence to phi
                        ratio = abs(sample[j]) / (abs(sample[i]) + 1e-10)
                        phi_proximity = abs(ratio - self.phi)

                        patterns.append({
                            'sample_idx': sample_idx,
                            'length': length,
                            'end_dimensions': (i, j),
                            'ratio': ratio,
                            'phi_proximity': phi_proximity,
                            'quality_score': length / (phi_proximity + 0.1)  # Avoid div by zero
                        })

        # Summary statistics
        if patterns:
            max_length = max(p['length'] for p in patterns)
            mean_quality = np.mean([p['quality_score'] for p in patterns])
            n_converging = sum(1 for p in patterns if p['phi_proximity'] < 0.1)
        else:
            max_length = 0
            mean_quality = 0.0
            n_converging = 0

        return {
            'n_patterns': len(patterns),
            'patterns': sorted(patterns, key=lambda x: -x['quality_score']),
            'max_length': max_length,
            'mean_quality_score': mean_quality,
            'n_converging_to_phi': n_converging,
            'fraction_converging': n_converging / len(patterns) if patterns else 0.0
        }


class ContinuedFractionDetector:
    """
    Continued fraction analysis for golden ratio detection.

    The golden ratio has the simplest continued fraction: [1; 1, 1, 1, ...]
    Ratios with many consecutive 1's are phi-like.

    Parameters
    ----------
    latent_codes : ndarray
        Latent representations
    """

    def __init__(self, latent_codes: np.ndarray):
        self.latent_codes = latent_codes
        self.phi = (1 + np.sqrt(5)) / 2
        self.n_samples, self.n_dims = latent_codes.shape

    def _continued_fraction(self, x: float, max_depth: int = 10) -> List[int]:
        """
        Compute continued fraction expansion of a number.

        Parameters
        ----------
        x : float
            Number to expand
        max_depth : int
            Maximum depth of expansion

        Returns
        -------
        list of int
            Continued fraction coefficients
        """
        cf = []
        x = abs(x)

        for _ in range(max_depth):
            if x < 1e-10:
                break
            floor_val = int(x)
            cf.append(floor_val)
            x = x - floor_val
            if x < 1e-10:
                break
            x = 1 / x

        return cf

    def _count_consecutive_ones(self, cf: List[int]) -> int:
        """Count maximum consecutive 1's in continued fraction."""
        max_ones = 0
        current_ones = 0

        for val in cf:
            if val == 1:
                current_ones += 1
                max_ones = max(max_ones, current_ones)
            else:
                current_ones = 0

        return max_ones

    def detect(self, min_consecutive_ones: int = 3) -> Dict:
        """
        Detect golden ratio via continued fraction analysis.

        Parameters
        ----------
        min_consecutive_ones : int, default=3
            Minimum consecutive 1's to consider phi-like

        Returns
        -------
        dict
            Detection results
        """
        results = []

        for i in range(self.n_dims - 1):
            for j in range(i + 1, self.n_dims):
                # Compute ratios across all samples
                ratios = np.abs(self.latent_codes[:, i]) / (np.abs(self.latent_codes[:, j]) + 1e-10)

                for sample_idx, ratio in enumerate(ratios):
                    cf = self._continued_fraction(ratio)
                    consecutive_ones = self._count_consecutive_ones(cf)
                    starts_with_one = len(cf) > 0 and cf[0] == 1

                    if consecutive_ones >= min_consecutive_ones and starts_with_one:
                        phi_proximity = abs(ratio - self.phi)
                        results.append({
                            'dimensions': (i, j),
                            'sample_idx': sample_idx,
                            'ratio': ratio,
                            'continued_fraction': cf,
                            'consecutive_ones': consecutive_ones,
                            'phi_proximity': phi_proximity,
                            'score': consecutive_ones / (phi_proximity + 0.01)
                        })

        # Summary
        if results:
            mean_consecutive = np.mean([r['consecutive_ones'] for r in results])
            max_consecutive = max(r['consecutive_ones'] for r in results)
            mean_score = np.mean([r['score'] for r in results])
        else:
            mean_consecutive = 0
            max_consecutive = 0
            mean_score = 0.0

        return {
            'n_detections': len(results),
            'detections': sorted(results, key=lambda x: -x['score']),
            'mean_consecutive_ones': mean_consecutive,
            'max_consecutive_ones': max_consecutive,
            'mean_score': mean_score
        }


class SpiralPatternDetector:
    """
    Logarithmic spiral pattern detection.

    Projects latent space to 2D and fits logarithmic spiral.
    Golden spirals have growth parameter b = (2/π) * ln(φ) ≈ 0.306.

    Parameters
    ----------
    latent_codes : ndarray
        Latent representations
    """

    def __init__(self, latent_codes: np.ndarray):
        self.latent_codes = latent_codes
        self.phi = (1 + np.sqrt(5)) / 2
        self.golden_b = (2 / np.pi) * np.log(self.phi)  # ≈ 0.306
        self.n_samples, self.n_dims = latent_codes.shape

    def detect(self) -> Dict:
        """
        Detect golden spiral patterns in latent space.

        Returns
        -------
        dict
            Detection results including:
            - is_spiral : bool
                Whether data forms a spiral pattern
            - is_golden_spiral : bool
                Whether spiral has golden ratio parameter
            - spiral_parameter_b : float
                Fitted growth parameter
            - r_squared : float
                Goodness of fit
            - deviation_from_golden : float
                Relative deviation from golden b parameter
        """
        # Project to 2D using PCA
        pca = PCA(n_components=2)
        latent_2d = pca.fit_transform(self.latent_codes)

        # Convert to polar coordinates
        x, y = latent_2d[:, 0], latent_2d[:, 1]
        r = np.sqrt(x**2 + y**2)
        theta = np.arctan2(y, x)

        # Sort by angle for continuous spiral
        sort_idx = np.argsort(theta)
        theta_sorted = theta[sort_idx]
        r_sorted = r[sort_idx]

        # Remove points too close to origin (unstable)
        valid_mask = r_sorted > 0.1 * np.median(r_sorted)
        theta_valid = theta_sorted[valid_mask]
        r_valid = r_sorted[valid_mask]

        if len(r_valid) < 10:
            # Not enough points
            return {
                'is_spiral': False,
                'is_golden_spiral': False,
                'spiral_parameter_b': None,
                'golden_b': self.golden_b,
                'deviation_from_golden': np.inf,
                'r_squared': 0.0,
                'pca_explained_variance': pca.explained_variance_ratio_.tolist()
            }

        # Fit logarithmic spiral: r = a * exp(b * theta)
        def log_spiral(theta, a, b):
            return a * np.exp(b * theta)

        try:
            # Initial guess
            a_init = np.median(r_valid)
            b_init = 0.3

            params, _ = curve_fit(
                log_spiral, theta_valid, r_valid,
                p0=[a_init, b_init],
                maxfev=10000,
                bounds=([0, -2], [np.inf, 2])  # Reasonable bounds
            )

            a, b = params

            # Calculate goodness of fit
            r_pred = log_spiral(theta_valid, a, b)
            ss_res = np.sum((r_valid - r_pred)**2)
            ss_tot = np.sum((r_valid - np.mean(r_valid))**2)
            r_squared = 1 - (ss_res / (ss_tot + 1e-10))

            # Check if spiral
            is_spiral = r_squared > 0.5

            # Check if golden spiral
            deviation_from_golden = abs(b - self.golden_b) / abs(self.golden_b)
            is_golden_spiral = is_spiral and (deviation_from_golden < 0.15)

            return {
                'is_spiral': is_spiral,
                'is_golden_spiral': is_golden_spiral,
                'spiral_parameter_b': b,
                'spiral_parameter_a': a,
                'golden_b': self.golden_b,
                'deviation_from_golden': deviation_from_golden,
                'r_squared': r_squared,
                'pca_explained_variance': pca.explained_variance_ratio_.tolist(),
                'n_points_fitted': len(r_valid)
            }

        except Exception as e:
            # Fit failed
            return {
                'is_spiral': False,
                'is_golden_spiral': False,
                'spiral_parameter_b': None,
                'golden_b': self.golden_b,
                'deviation_from_golden': np.inf,
                'r_squared': 0.0,
                'pca_explained_variance': pca.explained_variance_ratio_.tolist(),
                'error': str(e)
            }


class MultiMethodDetector:
    """
    Ensemble detector combining all 4 methods.

    Parameters
    ----------
    latent_codes : ndarray
        Latent representations
    """

    def __init__(self, latent_codes: np.ndarray):
        self.latent_codes = latent_codes
        self.phi = (1 + np.sqrt(5)) / 2

        # Initialize all detectors
        self.enhanced_ratio = EnhancedRatioDetector(latent_codes)
        self.fibonacci = FibonacciDetector(latent_codes)
        self.continued_fraction = ContinuedFractionDetector(latent_codes)
        self.spiral = SpiralPatternDetector(latent_codes)

    def detect_all(self, threshold: float = 0.1) -> Dict:
        """
        Run all detection methods and combine results.

        Parameters
        ----------
        threshold : float, default=0.1
            Detection threshold for ratio-based methods

        Returns
        -------
        dict
            Combined results from all detectors
        """
        print("Running multi-method golden ratio detection...")
        print("="*70)

        # 1. Enhanced ratio detection
        print("[1/4] Enhanced Ratio Detection")
        ratio_results = self.enhanced_ratio.detect(threshold)
        print(f"  Detected {ratio_results['n_golden_pairs']} golden pairs out of {ratio_results['total_pairs_tested']}")
        print()

        # 2. Fibonacci detection
        print("[2/4] Fibonacci Sequence Detection")
        fib_results = self.fibonacci.detect()
        print(f"  Found {fib_results['n_patterns']} Fibonacci patterns")
        print(f"  Max sequence length: {fib_results['max_length']}")
        print(f"  Converging to phi: {fib_results['n_converging_to_phi']} ({fib_results['fraction_converging']*100:.1f}%)")
        print()

        # 3. Continued fraction detection
        print("[3/4] Continued Fraction Analysis")
        cf_results = self.continued_fraction.detect()
        print(f"  Detected {cf_results['n_detections']} phi-like continued fractions")
        print(f"  Mean consecutive 1's: {cf_results['mean_consecutive_ones']:.2f}")
        print()

        # 4. Spiral pattern detection
        print("[4/4] Logarithmic Spiral Detection")
        spiral_results = self.spiral.detect()
        if spiral_results['is_spiral']:
            print(f"  Spiral detected: YES (R² = {spiral_results['r_squared']:.3f})")
            print(f"  Spiral parameter b: {spiral_results['spiral_parameter_b']:.4f} (golden: {spiral_results['golden_b']:.4f})")
            print(f"  Golden spiral: {'YES' if spiral_results['is_golden_spiral'] else 'NO'} " +
                  f"(deviation: {spiral_results['deviation_from_golden']*100:.1f}%)")
        else:
            print(f"  Spiral detected: NO (R² = {spiral_results['r_squared']:.3f})")
        print()

        # Ensemble voting
        print("="*70)
        print("ENSEMBLE RESULTS")
        print("="*70)

        votes = 0
        votes += 1 if ratio_results['n_golden_pairs'] > 0 else 0
        votes += 1 if fib_results['fraction_converging'] > 0.1 else 0
        votes += 1 if cf_results['n_detections'] > 0 else 0
        votes += 1 if spiral_results['is_golden_spiral'] else 0

        consensus = votes >= 3  # Majority voting

        print(f"Methods detecting golden ratio: {votes}/4")
        print(f"Consensus: {'YES - Strong evidence for golden ratio' if consensus else 'NO - Weak or no evidence'}")
        print("="*70)

        return {
            'enhanced_ratio': ratio_results,
            'fibonacci': fib_results,
            'continued_fraction': cf_results,
            'spiral': spiral_results,
            'ensemble_votes': votes,
            'consensus': consensus,
            'threshold_used': threshold
        }
