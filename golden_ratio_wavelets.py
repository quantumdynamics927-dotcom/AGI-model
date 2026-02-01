"""
Golden Ratio Wavelet Analysis Module

Multi-scale wavelet analysis for detecting golden ratio patterns at
different frequency bands in the VAE latent space.

Features:
- Daubechies wavelet decomposition of dimension ratios
- Per-level phi pattern detection
- Multi-scale evidence aggregation
- Visualization of wavelet coefficients
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
import warnings

# Try to import PyWavelets
try:
    import pywt
    PYWT_AVAILABLE = True
except ImportError:
    PYWT_AVAILABLE = False
    warnings.warn(
        "PyWavelets not available - wavelet analysis disabled. "
        "Install with: pip install PyWavelets"
    )

# Golden ratio constant
PHI = 1.618033988749895


class WaveletPhiDetector:
    """
    Multi-scale wavelet analysis for golden ratio detection.

    Uses wavelet decomposition to analyze dimension ratios at different
    scales (frequency bands), enabling detection of phi patterns that
    may only be visible at certain resolutions.

    Parameters
    ----------
    latent_codes : ndarray, shape (n_samples, n_dimensions)
        Latent representations from VAE
    wavelet : str, default='db4'
        Wavelet family to use. Options: 'db4' (Daubechies), 'haar', 'sym4', etc.
    max_level : int, optional
        Maximum decomposition level. If None, computed automatically.
    random_state : int, optional
        Random seed for reproducibility

    Attributes
    ----------
    phi : float
        Golden ratio constant (1.618...)
    ratios : ndarray
        Computed dimension ratios
    coefficients : dict
        Wavelet coefficients at each level
    """

    def __init__(
        self,
        latent_codes: np.ndarray,
        wavelet: str = 'db4',
        max_level: Optional[int] = None,
        random_state: Optional[int] = 42
    ):
        if not PYWT_AVAILABLE:
            raise ImportError(
                "PyWavelets is required for wavelet analysis. "
                "Install with: pip install PyWavelets"
            )

        self.latent_codes = latent_codes
        self.wavelet = wavelet
        self.phi = PHI
        self.random_state = random_state
        self.n_samples, self.n_dims = latent_codes.shape

        # Compute maximum decomposition level if not specified
        if max_level is None:
            # Rule of thumb: log2(n) levels for signal of length n
            self.max_level = min(
                pywt.dwt_max_level(self.n_samples, wavelet),
                6  # Cap at 6 levels to avoid over-decomposition
            )
        else:
            self.max_level = max_level

        # Compute ratios and wavelet decomposition
        self.ratios = self._compute_ratios()
        self.coefficients = None
        self._decomposed = False

    def _compute_ratios(self) -> np.ndarray:
        """
        Compute all pairwise dimension ratios.

        Returns mean ratio across samples for each dimension pair.
        """
        ratios = []
        for i in range(self.n_dims - 1):
            # Adjacent dimension ratios
            ratio = np.abs(self.latent_codes[:, i + 1]) / (
                np.abs(self.latent_codes[:, i]) + 1e-10
            )
            ratios.append(np.mean(ratio))

        return np.array(ratios)

    def decompose_multiscale(self, levels: Optional[int] = None) -> Dict:
        """
        Perform wavelet decomposition of dimension ratios.

        Parameters
        ----------
        levels : int, optional
            Number of decomposition levels. Uses max_level if not specified.

        Returns
        -------
        dict
            Dictionary containing:
            - approximation : ndarray
                Final approximation coefficients (low-frequency)
            - details : list of ndarray
                Detail coefficients at each level (high-frequency)
            - levels : int
                Number of decomposition levels
            - wavelet : str
                Wavelet used
        """
        if levels is None:
            levels = self.max_level

        # Ensure we have enough data for decomposition
        if len(self.ratios) < 4:
            warnings.warn("Not enough dimension pairs for wavelet decomposition")
            return {
                'approximation': self.ratios,
                'details': [],
                'levels': 0,
                'wavelet': self.wavelet
            }

        # Adjust levels if signal is too short
        max_possible = pywt.dwt_max_level(len(self.ratios), self.wavelet)
        levels = min(levels, max_possible)

        if levels < 1:
            return {
                'approximation': self.ratios,
                'details': [],
                'levels': 0,
                'wavelet': self.wavelet
            }

        # Perform multi-level decomposition
        coeffs = pywt.wavedec(self.ratios, self.wavelet, level=levels)

        # coeffs[0] is approximation, coeffs[1:] are details (coarse to fine)
        self.coefficients = {
            'approximation': coeffs[0],
            'details': coeffs[1:],
            'levels': levels,
            'wavelet': self.wavelet
        }
        self._decomposed = True

        return self.coefficients

    def detect_phi_per_level(
        self,
        threshold: float = 0.1
    ) -> Dict:
        """
        Detect golden ratio patterns at each wavelet level.

        Parameters
        ----------
        threshold : float, default=0.1
            Maximum distance from phi to count as golden ratio

        Returns
        -------
        dict
            Dictionary with detection results per level:
            - level_results : list of dict
                Results for each decomposition level
            - overall_score : float
                Aggregate phi resonance score (0-1)
            - best_level : int
                Level with strongest phi detection
        """
        if not self._decomposed:
            self.decompose_multiscale()

        if self.coefficients is None or self.coefficients['levels'] == 0:
            return {
                'level_results': [],
                'overall_score': 0.0,
                'best_level': -1,
                'message': 'Decomposition not available'
            }

        level_results = []

        # Analyze approximation (coarsest scale)
        approx = self.coefficients['approximation']
        approx_phi_fraction = self._compute_phi_fraction(approx, threshold)
        level_results.append({
            'level': 'approximation',
            'coefficients': approx,
            'phi_fraction': approx_phi_fraction,
            'mean_proximity': np.mean(np.abs(approx - self.phi)),
            'n_coeffs': len(approx)
        })

        # Analyze each detail level
        for i, detail in enumerate(self.coefficients['details']):
            if len(detail) > 0:
                phi_fraction = self._compute_phi_fraction(detail, threshold)
                mean_prox = np.mean(np.abs(detail - self.phi))
            else:
                phi_fraction = 0.0
                mean_prox = float('inf')

            level_results.append({
                'level': f'detail_{i + 1}',
                'coefficients': detail,
                'phi_fraction': phi_fraction,
                'mean_proximity': mean_prox,
                'n_coeffs': len(detail)
            })

        # Find best level
        phi_fractions = [r['phi_fraction'] for r in level_results]
        best_idx = np.argmax(phi_fractions)
        best_level = level_results[best_idx]['level']

        # Compute overall score (weighted average)
        # Weight by number of coefficients at each level
        total_coeffs = sum(r['n_coeffs'] for r in level_results)
        if total_coeffs > 0:
            overall_score = sum(
                r['phi_fraction'] * r['n_coeffs'] for r in level_results
            ) / total_coeffs
        else:
            overall_score = 0.0

        return {
            'level_results': level_results,
            'overall_score': overall_score,
            'best_level': best_level,
            'best_phi_fraction': phi_fractions[best_idx]
        }

    def _compute_phi_fraction(
        self,
        coefficients: np.ndarray,
        threshold: float
    ) -> float:
        """Compute fraction of coefficients within threshold of phi."""
        if len(coefficients) == 0:
            return 0.0
        proximity = np.abs(np.abs(coefficients) - self.phi)
        return np.mean(proximity < threshold)

    def aggregate_multiscale_evidence(
        self,
        threshold: float = 0.1,
        weights: Optional[List[float]] = None
    ) -> Dict:
        """
        Aggregate evidence across all wavelet scales.

        Combines phi detection results from all levels into a unified
        evidence score with optional custom weighting.

        Parameters
        ----------
        threshold : float, default=0.1
            Threshold for phi proximity
        weights : list of float, optional
            Custom weights for each level. If None, uses inverse-variance weighting.

        Returns
        -------
        dict
            Dictionary containing:
            - aggregate_score : float
                Combined evidence score (0-1)
            - weighted_phi_fraction : float
                Weighted average phi fraction
            - significance : str
                Interpretation ('strong', 'moderate', 'weak', 'none')
            - level_contributions : list
                Contribution from each level
            - recommendation : str
                Suggested interpretation
        """
        detection = self.detect_phi_per_level(threshold)

        if not detection['level_results']:
            return {
                'aggregate_score': 0.0,
                'weighted_phi_fraction': 0.0,
                'significance': 'none',
                'level_contributions': [],
                'recommendation': 'Insufficient data for analysis'
            }

        level_results = detection['level_results']
        n_levels = len(level_results)

        # Default weights: favor finer scales (detail levels)
        if weights is None:
            # Approximation gets weight 0.5, details share the remaining
            weights = [0.5] + [0.5 / max(1, n_levels - 1)] * (n_levels - 1)

        # Normalize weights
        weights = np.array(weights[:n_levels])
        weights = weights / weights.sum()

        # Compute weighted evidence
        phi_fractions = [r['phi_fraction'] for r in level_results]
        weighted_phi_fraction = np.sum(weights * phi_fractions)

        # Compute level contributions
        level_contributions = []
        for i, (result, w) in enumerate(zip(level_results, weights)):
            level_contributions.append({
                'level': result['level'],
                'weight': w,
                'contribution': w * result['phi_fraction'],
                'phi_fraction': result['phi_fraction']
            })

        # Compute aggregate score (combine phi fraction with consistency)
        # Higher score if phi is detected consistently across levels
        consistency = 1.0 - np.std(phi_fractions) if len(phi_fractions) > 1 else 1.0
        aggregate_score = weighted_phi_fraction * (0.7 + 0.3 * consistency)

        # Interpret significance
        if aggregate_score > 0.3:
            significance = 'strong'
            recommendation = (
                'Strong multi-scale phi patterns detected. '
                'Golden ratio organization present at multiple frequency bands.'
            )
        elif aggregate_score > 0.15:
            significance = 'moderate'
            recommendation = (
                'Moderate phi patterns detected at some scales. '
                'Partial golden ratio organization in latent space.'
            )
        elif aggregate_score > 0.05:
            significance = 'weak'
            recommendation = (
                'Weak phi patterns detected. '
                'May be noise or localized to specific frequency bands.'
            )
        else:
            significance = 'none'
            recommendation = (
                'No significant phi patterns detected at any scale. '
                'Latent space does not exhibit golden ratio organization.'
            )

        return {
            'aggregate_score': aggregate_score,
            'weighted_phi_fraction': weighted_phi_fraction,
            'significance': significance,
            'level_contributions': level_contributions,
            'consistency': consistency,
            'recommendation': recommendation
        }

    def reconstruct_phi_enhanced(
        self,
        enhance_level: Optional[str] = None,
        enhancement_factor: float = 1.5
    ) -> np.ndarray:
        """
        Reconstruct ratios with enhanced phi components.

        Amplifies wavelet coefficients near phi at specified level(s)
        to see effect of phi enhancement.

        Parameters
        ----------
        enhance_level : str, optional
            Level to enhance ('approximation', 'detail_1', etc.).
            If None, enhances the best level automatically.
        enhancement_factor : float, default=1.5
            Factor to multiply phi-proximate coefficients

        Returns
        -------
        ndarray
            Reconstructed ratios with enhanced phi components
        """
        if not self._decomposed:
            self.decompose_multiscale()

        if self.coefficients is None or self.coefficients['levels'] == 0:
            return self.ratios.copy()

        # Determine which level to enhance
        if enhance_level is None:
            detection = self.detect_phi_per_level()
            enhance_level = detection['best_level']

        # Create modified coefficients
        approx = self.coefficients['approximation'].copy()
        details = [d.copy() for d in self.coefficients['details']]

        threshold = 0.2  # Wider threshold for enhancement

        if enhance_level == 'approximation':
            mask = np.abs(np.abs(approx) - self.phi) < threshold
            approx[mask] *= enhancement_factor
        elif enhance_level.startswith('detail_'):
            level_idx = int(enhance_level.split('_')[1]) - 1
            if level_idx < len(details):
                mask = np.abs(np.abs(details[level_idx]) - self.phi) < threshold
                details[level_idx][mask] *= enhancement_factor

        # Reconstruct
        coeffs = [approx] + details
        reconstructed = pywt.waverec(coeffs, self.wavelet)

        # Trim to original length if needed
        return reconstructed[:len(self.ratios)]

    def analyze(self, threshold: float = 0.1, verbose: bool = True) -> Dict:
        """
        Run complete wavelet-based golden ratio analysis.

        Parameters
        ----------
        threshold : float, default=0.1
            Threshold for phi proximity detection
        verbose : bool, default=True
            Print results to console

        Returns
        -------
        dict
            Complete analysis results
        """
        # Decompose
        decomp = self.decompose_multiscale()

        # Detect per level
        detection = self.detect_phi_per_level(threshold)

        # Aggregate evidence
        aggregate = self.aggregate_multiscale_evidence(threshold)

        if verbose:
            print("=" * 60)
            print("WAVELET-BASED GOLDEN RATIO ANALYSIS")
            print("=" * 60)
            print(f"Wavelet: {self.wavelet}")
            print(f"Decomposition levels: {decomp['levels']}")
            print(f"Threshold: {threshold}")
            print()

            print("Per-Level Results:")
            print("-" * 40)
            for result in detection['level_results']:
                level = result['level']
                phi_frac = result['phi_fraction']
                mean_prox = result['mean_proximity']
                print(f"  {level}: phi_fraction={phi_frac:.3f}, "
                      f"mean_proximity={mean_prox:.4f}")

            print()
            print(f"Best level: {detection['best_level']}")
            print(f"Overall score: {detection['overall_score']:.3f}")
            print()

            print("Aggregate Evidence:")
            print("-" * 40)
            print(f"  Aggregate score: {aggregate['aggregate_score']:.3f}")
            print(f"  Significance: {aggregate['significance'].upper()}")
            print(f"  Consistency: {aggregate['consistency']:.3f}")
            print()
            print(f"Recommendation: {aggregate['recommendation']}")
            print("=" * 60)

        return {
            'decomposition': decomp,
            'detection': detection,
            'aggregate': aggregate,
            'ratios': self.ratios,
            'wavelet': self.wavelet,
            'threshold': threshold
        }


# Convenience function
def wavelet_phi_analysis(
    latent_codes: np.ndarray,
    wavelet: str = 'db4',
    threshold: float = 0.1,
    verbose: bool = True
) -> Dict:
    """
    Quick wavelet-based golden ratio analysis.

    Parameters
    ----------
    latent_codes : ndarray
        Latent codes from VAE (n_samples, n_dimensions)
    wavelet : str, default='db4'
        Wavelet family to use
    threshold : float, default=0.1
        Threshold for phi detection
    verbose : bool, default=True
        Print results

    Returns
    -------
    dict
        Analysis results
    """
    detector = WaveletPhiDetector(latent_codes, wavelet=wavelet)
    return detector.analyze(threshold=threshold, verbose=verbose)
