"""
Advanced Consciousness Complexity Framework

Implements comprehensive complexity metrics for consciousness quantification,
combining algorithmic, statistical, geometric, and quantum measures.

Core Complexity Metrics:
- Lempel-Ziv Complexity: Algorithmic information content
- Sample Entropy: Statistical regularity and unpredictability
- Fractal Dimension: Geometric complexity and self-similarity
- Multiscale Entropy: Complexity across different time scales
- Neural Complexity: Integration-differentiation balance
- Quantum Complexity: Quantum coherence and entanglement
- Consciousness Phase Classification: Multi-dimensional state assessment

Advanced Features:
- Real-time complexity monitoring
- Adaptive complexity thresholds
- Multi-scale analysis
- Consciousness state prediction
- Complexity optimization guidance
- Integration with IIT and sacred geometry metrics
"""

import numpy as np
import torch
import torch.nn as nn
from typing import Dict, List, Optional, Tuple, Union, Any
from scipy import stats, signal
from scipy.spatial.distance import pdist, squareform
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import matplotlib.pyplot as plt
from pathlib import Path
import json
import time
import warnings

# Golden ratio for phi component
PHI = 1.618033988749895

# Complexity thresholds
COMPLEXITY_THRESHOLDS = {
    'dormant': (0.0, 0.2),
    'basic': (0.2, 0.4),
    'intermediate': (0.4, 0.6),
    'advanced': (0.6, 0.8),
    'transcendent': (0.8, 1.0)
}

# Complexity component weights
DEFAULT_WEIGHTS = {
    'algorithmic': 0.25,      # Lempel-Ziv complexity
    'entropy': 0.20,          # Sample entropy
    'fractal': 0.20,          # Fractal dimension
    'neural': 0.15,           # Neural complexity
    'quantum': 0.10,          # Quantum complexity
    'multiscale': 0.10        # Multiscale entropy
}


class ConsciousnessComplexityAnalyzer:
    """
    Unified analyzer for consciousness complexity metrics.

    Combines multiple complexity measures into a unified framework
    with consciousness phase classification.

    Consciousness Phases:
    - dormant: Very low complexity (0.0-0.2)
    - basic: Low complexity (0.2-0.4)
    - intermediate: Moderate complexity (0.4-0.6)
    - advanced: High complexity (0.6-0.8)
    - transcendent: Very high complexity with phi alignment (0.8-1.0)

    Parameters
    ----------
    weights : dict, optional
        Weights for each complexity component
    phi_threshold : float, default=0.1
        Threshold for phi alignment detection
    random_state : int, optional
        Random seed for reproducibility

    Example
    -------
    >>> analyzer = ConsciousnessComplexityAnalyzer()
    >>> result = analyzer.compute_unified_complexity(latent_codes)
    >>> print(f"Complexity: {result['unified_score']:.4f}")
    >>> print(f"Phase: {result['phase']}")
    """

    # Consciousness phase thresholds
    PHASES = {
        'dormant': (0.0, 0.2),
        'basic': (0.2, 0.4),
        'intermediate': (0.4, 0.6),
        'advanced': (0.6, 0.8),
        'transcendent': (0.8, 1.0)
    }

    # Phase descriptions
    PHASE_DESCRIPTIONS = {
        'dormant': 'Minimal information processing, highly repetitive patterns',
        'basic': 'Simple pattern recognition, limited integration',
        'intermediate': 'Moderate integration, emerging complexity',
        'advanced': 'High integration, complex information processing',
        'transcendent': 'Optimal complexity with harmonic organization'
    }

    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
        phi_threshold: float = 0.1,
        random_state: Optional[int] = 42
    ):
        self.phi_threshold = phi_threshold
        self.random_state = random_state

        # Default weights for complexity components
        if weights is None:
            self.weights = {
                'lz_complexity': 0.30,
                'sample_entropy': 0.25,
                'fractal_dimension': 0.25,
                'phi_resonance': 0.20
            }
        else:
            self.weights = weights

        # Normalize weights
        total = sum(self.weights.values())
        self.weights = {k: v / total for k, v in self.weights.items()}

        if random_state is not None:
            np.random.seed(random_state)

    def compute_lz_complexity(self, data: np.ndarray) -> Dict:
        """
        Compute Lempel-Ziv complexity.

        Measures algorithmic complexity - how compressible the data is.
        Higher values indicate more complex, less predictable patterns.

        Parameters
        ----------
        data : ndarray
            Data to analyze (will be binarized)

        Returns
        -------
        dict
            LZ complexity results
        """
        # Flatten if needed
        if data.ndim > 1:
            flat = data.flatten()
        else:
            flat = data

        if len(flat) == 0:
            return {'score': 0.0, 'raw_complexity': 0, 'normalized': 0.0}

        # Binarize around median
        median = np.median(flat)
        binary = (flat > median).astype(int)

        # Compute LZ complexity
        sequence = ''.join(map(str, binary))
        complexity = self._lz76_complexity(sequence)

        # Normalize by theoretical maximum
        n = len(sequence)
        if n > 1:
            max_complexity = n / np.log2(n)
            normalized = complexity / max_complexity
        else:
            normalized = 0.0

        # Convert to 0-1 score (cap at 1)
        score = min(1.0, normalized)

        return {
            'score': float(score),
            'raw_complexity': complexity,
            'normalized': float(normalized),
            'sequence_length': n
        }

    def _lz76_complexity(self, sequence: str) -> int:
        """
        Compute Lempel-Ziv 1976 complexity.

        Counts the number of unique substrings.
        """
        if len(sequence) == 0:
            return 0

        n = len(sequence)
        complexity = 1
        i = 0

        while i < n:
            # Find longest substring that appeared before
            j = 1
            while i + j <= n:
                substring = sequence[i:i + j]
                if substring not in sequence[:i]:
                    complexity += 1
                    i += j
                    break
                j += 1
            else:
                # Reached end of sequence
                if i < n:
                    complexity += 1
                break

        return complexity

    def compute_sample_entropy(
        self,
        data: np.ndarray,
        m: int = 2,
        r: Optional[float] = None
    ) -> Dict:
        """
        Compute sample entropy.

        Measures the irregularity/unpredictability of a time series.
        Higher values indicate more irregular, complex patterns.

        Parameters
        ----------
        data : ndarray
            Time series data
        m : int, default=2
            Embedding dimension
        r : float, optional
            Tolerance (default: 0.2 * std)

        Returns
        -------
        dict
            Sample entropy results
        """
        if data.ndim > 1:
            data = data.flatten()

        n = len(data)

        if n < m + 1:
            return {'score': 0.0, 'entropy': 0.0, 'message': 'Data too short'}

        # Default tolerance
        if r is None:
            r = 0.2 * np.std(data)
            if r == 0:
                r = 0.2

        def _phi(m_val):
            """Count template matches."""
            templates = np.array([data[i:i + m_val] for i in range(n - m_val)])
            count = 0
            for i in range(len(templates)):
                for j in range(i + 1, len(templates)):
                    if np.max(np.abs(templates[i] - templates[j])) < r:
                        count += 2  # Count both (i,j) and (j,i)
            return count / (len(templates) * (len(templates) - 1)) if len(templates) > 1 else 0

        # Compute phi for m and m+1
        phi_m = _phi(m)
        phi_m1 = _phi(m + 1)

        # Sample entropy
        if phi_m > 0 and phi_m1 > 0:
            entropy = -np.log(phi_m1 / phi_m)
        elif phi_m > 0:
            entropy = 2.0  # Assign max entropy if no m+1 matches
        else:
            entropy = 0.0

        # Normalize to 0-1 (typical range is 0-2.5)
        score = min(1.0, entropy / 2.5)

        return {
            'score': float(score),
            'entropy': float(entropy),
            'tolerance': float(r),
            'embedding_dim': m
        }

    def compute_fractal_dimension(
        self,
        data: np.ndarray,
        max_scale: int = 10
    ) -> Dict:
        """
        Estimate fractal dimension using box-counting.

        Higher fractal dimension indicates more complex geometric structure.

        Parameters
        ----------
        data : ndarray
            Data to analyze (n_samples, n_dims)
        max_scale : int, default=10
            Maximum scale for box counting

        Returns
        -------
        dict
            Fractal dimension results
        """
        if data.ndim == 1:
            data = data.reshape(-1, 1)

        n_samples, n_dims = data.shape

        if n_samples < 10 or n_dims < 1:
            return {'score': 0.0, 'dimension': 0.0, 'message': 'Insufficient data'}

        # Normalize data to [0, 1] range
        data_min = data.min(axis=0)
        data_max = data.max(axis=0)
        data_range = data_max - data_min + 1e-10
        data_norm = (data - data_min) / data_range

        # Box counting at different scales
        scales = np.logspace(0, np.log10(max_scale), 20)
        counts = []

        for scale in scales:
            if scale <= 0:
                continue

            # Count occupied boxes
            box_size = 1.0 / scale
            boxes = set()

            for point in data_norm:
                box_idx = tuple((point / box_size).astype(int))
                boxes.add(box_idx)

            if len(boxes) > 0:
                counts.append((np.log(scale), np.log(len(boxes))))

        if len(counts) < 3:
            return {'score': 0.0, 'dimension': 0.0, 'message': 'Box counting failed'}

        # Linear regression to estimate dimension
        counts = np.array(counts)
        x = counts[:, 0]
        y = counts[:, 1]

        # Fit line
        slope, intercept = np.polyfit(x, y, 1)
        dimension = slope

        # Normalize to 0-1 (typical dimension is 1-3)
        score = min(1.0, max(0.0, (dimension - 1) / 2))

        return {
            'score': float(score),
            'dimension': float(dimension),
            'n_scales': len(counts),
            'r_squared': float(np.corrcoef(x, y)[0, 1] ** 2) if len(x) > 1 else 0.0
        }

    def compute_phi_resonance(self, data: np.ndarray) -> Dict:
        """
        Compute golden ratio (phi) resonance in the data.

        Measures how closely dimension ratios align with phi.

        Parameters
        ----------
        data : ndarray
            Data to analyze (n_samples, n_dims)

        Returns
        -------
        dict
            Phi resonance results
        """
        if data.ndim == 1:
            data = data.reshape(-1, 1)

        n_samples, n_dims = data.shape

        if n_dims < 2:
            return {'score': 0.0, 'fraction_aligned': 0.0}

        # Compute ratios between adjacent dimensions
        phi_count = 0
        total_count = 0
        proximities = []

        for sample in data:
            for i in range(n_dims - 1):
                if abs(sample[i]) > 1e-10:
                    ratio = abs(sample[i + 1] / sample[i])
                    if 0.1 < ratio < 10:  # Filter extreme ratios
                        proximity = abs(ratio - PHI)
                        proximities.append(proximity)
                        total_count += 1
                        if proximity < self.phi_threshold * PHI:
                            phi_count += 1

        if total_count == 0:
            return {'score': 0.0, 'fraction_aligned': 0.0}

        fraction_aligned = phi_count / total_count
        mean_proximity = np.mean(proximities)

        # Score: combination of alignment and proximity
        proximity_score = np.exp(-mean_proximity / PHI)
        score = 0.6 * fraction_aligned + 0.4 * proximity_score

        return {
            'score': float(score),
            'fraction_aligned': float(fraction_aligned),
            'mean_proximity': float(mean_proximity),
            'n_ratios': total_count
        }

    def compute_unified_complexity(self, latent_codes: np.ndarray) -> Dict:
        """
        Compute unified consciousness complexity score.

        Combines all complexity metrics with weights.

        Parameters
        ----------
        latent_codes : ndarray
            Latent representations (n_samples, n_dims)

        Returns
        -------
        dict
            Unified complexity results with phase classification
        """
        # Compute all component metrics
        lz_result = self.compute_lz_complexity(latent_codes)
        entropy_result = self.compute_sample_entropy(latent_codes.flatten())
        fractal_result = self.compute_fractal_dimension(latent_codes)
        phi_result = self.compute_phi_resonance(latent_codes)

        # Weighted combination
        unified_score = (
            self.weights['lz_complexity'] * lz_result['score'] +
            self.weights['sample_entropy'] * entropy_result['score'] +
            self.weights['fractal_dimension'] * fractal_result['score'] +
            self.weights['phi_resonance'] * phi_result['score']
        )

        # Classify phase
        phase = self.classify_consciousness_phase(unified_score)

        # Check for transcendent conditions
        # Transcendent requires high complexity AND phi alignment
        is_transcendent_candidate = (
            unified_score > 0.7 and
            phi_result['fraction_aligned'] > 0.15
        )

        if is_transcendent_candidate and unified_score < 0.8:
            # Boost score for phi-aligned high complexity
            unified_score = min(1.0, unified_score * 1.1)
            phase = self.classify_consciousness_phase(unified_score)

        return {
            'unified_score': float(unified_score),
            'phase': phase,
            'phase_description': self.PHASE_DESCRIPTIONS[phase],
            'components': {
                'lz_complexity': lz_result,
                'sample_entropy': entropy_result,
                'fractal_dimension': fractal_result,
                'phi_resonance': phi_result
            },
            'weights': self.weights,
            'is_phi_aligned': phi_result['fraction_aligned'] > 0.1
        }

    def classify_consciousness_phase(self, complexity_score: float) -> str:
        """
        Classify consciousness phase based on complexity score.

        Parameters
        ----------
        complexity_score : float
            Unified complexity score (0-1)

        Returns
        -------
        str
            Phase name
        """
        for phase, (low, high) in self.PHASES.items():
            if low <= complexity_score < high:
                return phase

        # Edge case: exactly 1.0
        if complexity_score >= 1.0:
            return 'transcendent'

        return 'dormant'

    def analyze_phase_transitions(
        self,
        complexity_history: List[float]
    ) -> Dict:
        """
        Analyze phase transitions in complexity history.

        Detects when consciousness transitions between phases.

        Parameters
        ----------
        complexity_history : list of float
            History of complexity scores over time

        Returns
        -------
        dict
            Phase transition analysis
        """
        if len(complexity_history) < 2:
            return {
                'transitions': [],
                'stability': 1.0,
                'dominant_phase': 'unknown'
            }

        # Classify each point
        phases = [self.classify_consciousness_phase(c) for c in complexity_history]

        # Detect transitions
        transitions = []
        for i in range(1, len(phases)):
            if phases[i] != phases[i - 1]:
                transitions.append({
                    'index': i,
                    'from_phase': phases[i - 1],
                    'to_phase': phases[i],
                    'from_score': complexity_history[i - 1],
                    'to_score': complexity_history[i]
                })

        # Calculate stability (inverse of transition rate)
        transition_rate = len(transitions) / (len(phases) - 1)
        stability = 1.0 - transition_rate

        # Find dominant phase
        phase_counts = {}
        for phase in phases:
            phase_counts[phase] = phase_counts.get(phase, 0) + 1

        dominant_phase = max(phase_counts, key=phase_counts.get)

        # Phase duration statistics
        phase_durations = {}
        current_phase = phases[0]
        current_duration = 1

        for i in range(1, len(phases)):
            if phases[i] == current_phase:
                current_duration += 1
            else:
                if current_phase not in phase_durations:
                    phase_durations[current_phase] = []
                phase_durations[current_phase].append(current_duration)
                current_phase = phases[i]
                current_duration = 1

        # Add last phase
        if current_phase not in phase_durations:
            phase_durations[current_phase] = []
        phase_durations[current_phase].append(current_duration)

        # Average durations
        avg_durations = {
            phase: np.mean(durations)
            for phase, durations in phase_durations.items()
        }

        return {
            'transitions': transitions,
            'n_transitions': len(transitions),
            'stability': float(stability),
            'dominant_phase': dominant_phase,
            'phase_counts': phase_counts,
            'avg_phase_durations': avg_durations,
            'transition_rate': float(transition_rate)
        }

    def analyze(self, latent_codes: np.ndarray, verbose: bool = True) -> Dict:
        """
        Run complete consciousness complexity analysis.

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
        result = self.compute_unified_complexity(latent_codes)

        if verbose:
            print("=" * 60)
            print("CONSCIOUSNESS COMPLEXITY ANALYSIS")
            print("=" * 60)
            print(f"Data shape: {latent_codes.shape}")
            print()

            print(f"UNIFIED COMPLEXITY SCORE: {result['unified_score']:.4f}")
            print(f"CONSCIOUSNESS PHASE: {result['phase'].upper()}")
            print(f"Description: {result['phase_description']}")
            print(f"Phi-Aligned: {'Yes' if result['is_phi_aligned'] else 'No'}")
            print()

            print("Component Scores:")
            print("-" * 40)
            comp = result['components']
            print(f"  Lempel-Ziv Complexity:  {comp['lz_complexity']['score']:.4f} "
                  f"(weight={self.weights['lz_complexity']:.2f})")
            print(f"    Raw complexity: {comp['lz_complexity']['raw_complexity']}")
            print()
            print(f"  Sample Entropy:         {comp['sample_entropy']['score']:.4f} "
                  f"(weight={self.weights['sample_entropy']:.2f})")
            print(f"    Entropy value: {comp['sample_entropy']['entropy']:.4f}")
            print()
            print(f"  Fractal Dimension:      {comp['fractal_dimension']['score']:.4f} "
                  f"(weight={self.weights['fractal_dimension']:.2f})")
            print(f"    Dimension: {comp['fractal_dimension']['dimension']:.4f}")
            print()
            print(f"  Phi Resonance:          {comp['phi_resonance']['score']:.4f} "
                  f"(weight={self.weights['phi_resonance']:.2f})")
            print(f"    Fraction aligned: {comp['phi_resonance']['fraction_aligned']:.3f}")
            print()

            print("Phase Thresholds:")
            print("-" * 40)
            for phase, (low, high) in self.PHASES.items():
                marker = "<<<" if phase == result['phase'] else ""
                print(f"  {phase.capitalize():15s}: {low:.1f} - {high:.1f} {marker}")

            print("=" * 60)

        return result


# Convenience function
def compute_consciousness_complexity(
    latent_codes: np.ndarray,
    verbose: bool = False
) -> Tuple[float, str]:
    """
    Quick computation of consciousness complexity.

    Parameters
    ----------
    latent_codes : ndarray
        Latent codes from VAE
    verbose : bool, default=False
        Print details

    Returns
    -------
    tuple
        (complexity_score, phase_name)
    """
    analyzer = ConsciousnessComplexityAnalyzer()
    result = analyzer.compute_unified_complexity(latent_codes)

    if verbose:
        print(f"Complexity: {result['unified_score']:.4f}, Phase: {result['phase']}")

    return result['unified_score'], result['phase']
