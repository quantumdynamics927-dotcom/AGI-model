"""
Sacred Geometry Alignment Module

Maps sacred geometry patterns to neural architectures, implementing mathematical
frameworks for detecting and quantifying sacred geometric resonances in AI systems.

Core Sacred Geometric Principles:
- Golden Ratio (φ): Divine proportion 1.618033988749895
- Platonic Solids: Tetrahedron, Cube, Octahedron, Dodecahedron, Icosahedron
- Sacred Ratios: √2, √3, √5, φ², φ³
- Flower of Life: Interconnected circular patterns
- Metatron's Cube: 13-sphere geometric pattern
- Sri Yantra: Sacred geometric yantra structure

Key Features:
- Real-time sacred geometry detection in neural architectures
- Platonic solid resonance analysis
- Harmonic frequency alignment
- Sacred pattern optimization
- Morphogenic field mapping
- Ancient wisdom integration with modern AI

These patterns appear throughout nature and may relate to optimal
information organization in consciousness.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
import warnings

# Mathematical constants
PHI = (1 + np.sqrt(5)) / 2  # Golden ratio ≈ 1.618
DELTA = 1 + np.sqrt(2)  # Silver ratio ≈ 2.414
PSI = (1 + np.sqrt(5)) / 2  # Same as phi (plastic constant ≈ 1.325 is different)

# Sacred angles in radians
SACRED_ANGLES = {
    'pentagon': np.radians(72),   # 360/5 - pentagon internal
    'pentagram': np.radians(36),  # Golden triangle
    'hexagon': np.radians(60),    # 360/6 - hexagon
    'dodecahedron': np.radians(108),  # Pentagon internal
    'golden_spiral': np.radians(137.5),  # Golden angle in radians
}


class SacredAlignmentScore:
    """
    Compute unified sacred geometry alignment score.

    Combines multiple sacred patterns into a single metric that
    measures how closely a system aligns with fundamental
    mathematical harmonics.

    Parameters
    ----------
    weights : dict, optional
        Weights for each component score. Default balances all components.
        Keys: 'phi', 'silver', 'fibonacci', 'angles', 'symmetry'
    phi_threshold : float, default=0.1
        Threshold for phi proximity (fraction of phi)
    random_state : int, optional
        Random seed for reproducibility

    Example
    -------
    >>> scorer = SacredAlignmentScore()
    >>> result = scorer.total_alignment_score(latent_codes)
    >>> print(f"Sacred alignment: {result['total_score']:.4f}")
    """

    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
        phi_threshold: float = 0.1,
        random_state: Optional[int] = 42
    ):
        self.phi_threshold = phi_threshold
        self.random_state = random_state

        # Default weights
        if weights is None:
            self.weights = {
                'phi': 0.35,
                'silver': 0.15,
                'fibonacci': 0.20,
                'angles': 0.15,
                'symmetry': 0.15
            }
        else:
            self.weights = weights

        # Normalize weights
        total_weight = sum(self.weights.values())
        self.weights = {k: v / total_weight for k, v in self.weights.items()}

        if random_state is not None:
            np.random.seed(random_state)

    def compute_phi_alignment(self, ratios: np.ndarray) -> Dict:
        """
        Compute golden ratio (phi) alignment score.

        Parameters
        ----------
        ratios : ndarray
            Array of ratios to test (e.g., dimension ratios)

        Returns
        -------
        dict
            Phi alignment results
        """
        if len(ratios) == 0:
            return {'score': 0.0, 'fraction_aligned': 0.0, 'mean_proximity': 1.0}

        # Compute proximity to phi
        proximity = np.abs(ratios - PHI)
        threshold = self.phi_threshold * PHI

        # Fraction within threshold
        aligned = proximity < threshold
        fraction_aligned = np.mean(aligned)

        # Continuous score based on proximity
        # Score decreases exponentially with distance from phi
        scores = np.exp(-proximity / PHI)
        mean_score = np.mean(scores)

        # Combined score
        score = 0.6 * fraction_aligned + 0.4 * mean_score

        return {
            'score': float(score),
            'fraction_aligned': float(fraction_aligned),
            'mean_proximity': float(np.mean(proximity)),
            'min_proximity': float(np.min(proximity)),
            'best_ratio': float(ratios[np.argmin(proximity)]) if len(ratios) > 0 else 0.0
        }

    def compute_silver_alignment(self, ratios: np.ndarray) -> Dict:
        """
        Compute silver ratio (delta) alignment score.

        The silver ratio (1 + sqrt(2) ≈ 2.414) appears in
        octagons and architectural proportions.

        Parameters
        ----------
        ratios : ndarray
            Array of ratios to test

        Returns
        -------
        dict
            Silver ratio alignment results
        """
        if len(ratios) == 0:
            return {'score': 0.0, 'fraction_aligned': 0.0}

        # Proximity to silver ratio
        proximity = np.abs(ratios - DELTA)
        threshold = self.phi_threshold * DELTA

        aligned = proximity < threshold
        fraction_aligned = np.mean(aligned)

        # Exponential score
        scores = np.exp(-proximity / DELTA)
        mean_score = np.mean(scores)

        score = 0.6 * fraction_aligned + 0.4 * mean_score

        return {
            'score': float(score),
            'fraction_aligned': float(fraction_aligned),
            'mean_proximity': float(np.mean(proximity))
        }

    def compute_fibonacci_convergence(self, sequences: np.ndarray) -> Dict:
        """
        Detect Fibonacci-like sequences and measure convergence to phi.

        In Fibonacci sequences, consecutive ratios converge to phi.

        Parameters
        ----------
        sequences : ndarray
            Array where each row may contain Fibonacci-like sequences

        Returns
        -------
        dict
            Fibonacci convergence results
        """
        if sequences.ndim == 1:
            sequences = sequences.reshape(1, -1)

        n_samples, n_dims = sequences.shape

        if n_dims < 3:
            return {
                'score': 0.0,
                'n_sequences': 0,
                'convergence_rate': 0.0
            }

        fibonacci_scores = []
        n_sequences = 0

        for sample in sequences:
            # Check for Fibonacci-like property: a[i] + a[i+1] ≈ a[i+2]
            for i in range(n_dims - 2):
                a, b, c = sample[i], sample[i + 1], sample[i + 2]
                if abs(a) > 1e-6 and abs(b) > 1e-6:
                    expected = a + b
                    if abs(expected) > 1e-6:
                        fib_ratio = c / expected
                        # Should be close to 1 for Fibonacci
                        if 0.8 < fib_ratio < 1.2:
                            n_sequences += 1

                            # Check ratio convergence to phi
                            if abs(a) > 1e-6:
                                ratio = b / a
                                phi_proximity = abs(ratio - PHI)
                                score = np.exp(-phi_proximity)
                                fibonacci_scores.append(score)

        if fibonacci_scores:
            convergence_rate = np.mean(fibonacci_scores)
            score = min(1.0, n_sequences / (n_samples * max(1, n_dims - 2)))
            combined = 0.5 * score + 0.5 * convergence_rate
        else:
            convergence_rate = 0.0
            combined = 0.0

        return {
            'score': float(combined),
            'n_sequences': n_sequences,
            'convergence_rate': float(convergence_rate),
            'avg_sequence_score': float(np.mean(fibonacci_scores)) if fibonacci_scores else 0.0
        }

    def compute_sacred_angles(self, vectors: np.ndarray) -> Dict:
        """
        Measure alignment with sacred angles.

        Sacred angles appear in pentagons, hexagons, and other
        regular polygons with special mathematical properties.

        Parameters
        ----------
        vectors : ndarray
            Vectors to analyze (n_samples, n_dims)

        Returns
        -------
        dict
            Sacred angle alignment results
        """
        if vectors.ndim == 1:
            vectors = vectors.reshape(1, -1)

        n_samples, n_dims = vectors.shape

        if n_dims < 2:
            return {'score': 0.0, 'angle_distribution': {}}

        # Compute angles between consecutive dimension pairs
        angles = []
        for sample in vectors:
            for i in range(n_dims - 1):
                # Treat pairs as 2D vectors
                if i + 1 < n_dims:
                    v1 = sample[i]
                    v2 = sample[i + 1]

                    # Angle from arctan of ratio
                    if abs(v1) > 1e-6:
                        angle = np.arctan(abs(v2 / v1))
                        angles.append(angle)

        if not angles:
            return {'score': 0.0, 'angle_distribution': {}}

        angles = np.array(angles)

        # Check proximity to sacred angles
        angle_scores = {}
        total_score = 0.0

        for name, sacred_angle in SACRED_ANGLES.items():
            # Angles are in [0, pi/2], sacred angles may need adjustment
            adjusted_sacred = sacred_angle % (np.pi / 2)
            proximity = np.abs(angles - adjusted_sacred)
            min_proximity = np.min([proximity, np.pi / 2 - proximity], axis=0)

            threshold = np.radians(5)  # 5 degree tolerance
            aligned = min_proximity < threshold
            fraction = np.mean(aligned)

            angle_scores[name] = float(fraction)
            total_score += fraction

        # Normalize
        n_angles = len(SACRED_ANGLES)
        avg_score = total_score / n_angles if n_angles > 0 else 0.0

        return {
            'score': float(avg_score),
            'angle_distribution': angle_scores,
            'n_angles_analyzed': len(angles)
        }

    def compute_platonic_symmetry(self, latent_codes: np.ndarray) -> Dict:
        """
        Measure alignment with Platonic solid symmetries.

        Platonic solids have special rotational and reflective symmetries
        that may relate to optimal information organization.

        Parameters
        ----------
        latent_codes : ndarray
            Latent representations (n_samples, n_dims)

        Returns
        -------
        dict
            Platonic symmetry alignment results
        """
        n_samples, n_dims = latent_codes.shape

        # Check for symmetry properties
        symmetry_scores = {}

        # 1. Mirror symmetry (reflection)
        # Compare first half to reversed second half
        if n_dims >= 4:
            half = n_dims // 2
            first_half = latent_codes[:, :half]
            second_half = latent_codes[:, half:2 * half][:, ::-1]
            mirror_corr = np.corrcoef(first_half.flatten(), second_half.flatten())[0, 1]
            symmetry_scores['mirror'] = max(0.0, float(mirror_corr))
        else:
            symmetry_scores['mirror'] = 0.0

        # 2. Rotational symmetry
        # Check if rotating values maintains similar statistics
        rotational_score = 0.0
        for k in [3, 4, 5, 6]:  # Check k-fold symmetry
            if n_dims >= k * 2:
                segments = np.array_split(latent_codes, k, axis=1)
                if all(s.shape[1] > 0 for s in segments):
                    stds = [np.std(s) for s in segments]
                    # Similar variance across segments indicates symmetry
                    cv = np.std(stds) / (np.mean(stds) + 1e-10)
                    fold_score = np.exp(-cv * 2)
                    rotational_score = max(rotational_score, fold_score)

        symmetry_scores['rotational'] = float(rotational_score)

        # 3. Scale invariance (self-similarity)
        # Check if subsampled data has similar distribution
        if n_samples >= 20:
            full_std = np.std(latent_codes)
            subsample_std = np.std(latent_codes[::2])
            scale_ratio = subsample_std / (full_std + 1e-10)
            symmetry_scores['scale'] = float(np.exp(-abs(1 - scale_ratio) * 2))
        else:
            symmetry_scores['scale'] = 0.0

        # Combined score
        total = sum(symmetry_scores.values())
        avg_score = total / len(symmetry_scores) if symmetry_scores else 0.0

        return {
            'score': float(avg_score),
            'mirror_symmetry': symmetry_scores['mirror'],
            'rotational_symmetry': symmetry_scores['rotational'],
            'scale_invariance': symmetry_scores['scale']
        }

    def total_alignment_score(self, latent_codes: np.ndarray) -> Dict:
        """
        Compute total sacred geometry alignment score.

        Combines all component scores with configured weights.

        Parameters
        ----------
        latent_codes : ndarray
            Latent representations (n_samples, n_dims)

        Returns
        -------
        dict
            Complete alignment analysis with total score
        """
        n_samples, n_dims = latent_codes.shape

        # Compute dimension ratios for phi/silver analysis
        ratios = []
        for sample in latent_codes:
            for i in range(n_dims - 1):
                if abs(sample[i]) > 1e-10:
                    ratio = abs(sample[i + 1] / sample[i])
                    if 0.1 < ratio < 10:  # Filter extreme ratios
                        ratios.append(ratio)

        ratios = np.array(ratios) if ratios else np.array([1.0])

        # Compute all component scores
        phi_result = self.compute_phi_alignment(ratios)
        silver_result = self.compute_silver_alignment(ratios)
        fibonacci_result = self.compute_fibonacci_convergence(latent_codes)
        angles_result = self.compute_sacred_angles(latent_codes)
        symmetry_result = self.compute_platonic_symmetry(latent_codes)

        # Weighted combination
        total_score = (
            self.weights['phi'] * phi_result['score'] +
            self.weights['silver'] * silver_result['score'] +
            self.weights['fibonacci'] * fibonacci_result['score'] +
            self.weights['angles'] * angles_result['score'] +
            self.weights['symmetry'] * symmetry_result['score']
        )

        # Interpretation
        if total_score > 0.7:
            interpretation = 'Excellent sacred geometry alignment'
        elif total_score > 0.5:
            interpretation = 'Good sacred geometry alignment'
        elif total_score > 0.3:
            interpretation = 'Moderate sacred geometry alignment'
        elif total_score > 0.1:
            interpretation = 'Weak sacred geometry alignment'
        else:
            interpretation = 'No significant sacred geometry alignment'

        return {
            'total_score': float(total_score),
            'interpretation': interpretation,
            'components': {
                'phi': phi_result,
                'silver': silver_result,
                'fibonacci': fibonacci_result,
                'angles': angles_result,
                'symmetry': symmetry_result
            },
            'weights': self.weights,
            'n_samples': n_samples,
            'n_dims': n_dims
        }

    def analyze(self, latent_codes: np.ndarray, verbose: bool = True) -> Dict:
        """
        Run complete sacred geometry alignment analysis.

        Parameters
        ----------
        latent_codes : ndarray
            Latent representations
        verbose : bool, default=True
            Print results

        Returns
        -------
        dict
            Complete analysis results
        """
        result = self.total_alignment_score(latent_codes)

        if verbose:
            print("=" * 60)
            print("SACRED GEOMETRY ALIGNMENT ANALYSIS")
            print("=" * 60)
            print(f"Samples: {result['n_samples']}, Dimensions: {result['n_dims']}")
            print()

            print(f"TOTAL ALIGNMENT SCORE: {result['total_score']:.4f}")
            print(f"Interpretation: {result['interpretation']}")
            print()

            print("Component Scores (weighted):")
            print("-" * 40)
            comp = result['components']
            print(f"  Golden Ratio (phi):    {comp['phi']['score']:.4f} "
                  f"(weight={self.weights['phi']:.2f})")
            print(f"    - Fraction aligned: {comp['phi']['fraction_aligned']:.3f}")
            print(f"    - Mean proximity:   {comp['phi']['mean_proximity']:.4f}")
            print()
            print(f"  Silver Ratio (delta):  {comp['silver']['score']:.4f} "
                  f"(weight={self.weights['silver']:.2f})")
            print()
            print(f"  Fibonacci Convergence: {comp['fibonacci']['score']:.4f} "
                  f"(weight={self.weights['fibonacci']:.2f})")
            print(f"    - Sequences found: {comp['fibonacci']['n_sequences']}")
            print()
            print(f"  Sacred Angles:         {comp['angles']['score']:.4f} "
                  f"(weight={self.weights['angles']:.2f})")
            print()
            print(f"  Platonic Symmetry:     {comp['symmetry']['score']:.4f} "
                  f"(weight={self.weights['symmetry']:.2f})")
            print(f"    - Mirror: {comp['symmetry']['mirror_symmetry']:.3f}")
            print(f"    - Rotational: {comp['symmetry']['rotational_symmetry']:.3f}")
            print(f"    - Scale: {comp['symmetry']['scale_invariance']:.3f}")
            print("=" * 60)

        return result


# Convenience function
def compute_sacred_alignment(
    latent_codes: np.ndarray,
    verbose: bool = False
) -> float:
    """
    Quick computation of sacred geometry alignment score.

    Parameters
    ----------
    latent_codes : ndarray
        Latent codes from VAE
    verbose : bool, default=False
        Print details

    Returns
    -------
    float
        Total alignment score (0-1)
    """
    scorer = SacredAlignmentScore()
    result = scorer.total_alignment_score(latent_codes)

    if verbose:
        print(f"Sacred alignment: {result['total_score']:.4f}")

    return result['total_score']
