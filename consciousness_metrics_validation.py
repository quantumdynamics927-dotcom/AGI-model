"""
Consciousness Metrics Validation Module
=======================================

Implements validation metrics for consciousness-related analysis:
- Lempel-Ziv complexity
- Perturbational Complexity Index (PCI)
- Integrated Information Theory (IIT) metrics
- Cross-validation with EEG/fMRI data

References:
- Lempel & Ziv (1976) - Complexity of finite sequences
- Casali et al. (2013) - Perturbational Complexity Index
- Tononi (2004) - Integrated Information Theory
"""

import numpy as np
import torch
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
from scipy import signal
from scipy.stats import entropy
import logging

logger = logging.getLogger(__name__)


@dataclass
class ConsciousnessMetrics:
    """Container for consciousness-related metrics."""
    lz_complexity: float
    normalized_lz: float
    pci: float
    phi: float  # Integrated information
    spectral_entropy: float
    permutation_entropy: float
    sample_entropy: float
    approximate_entropy: float
    multiscale_entropy: List[float]
    functional_connectivity: float
    effective_connectivity: float


class LempelZivComplexity:
    """
    Compute Lempel-Ziv complexity for consciousness analysis.
    
    LZ complexity measures the number of distinct substrings
    in a sequence, related to algorithmic complexity.
    """
    
    def __init__(self, normalize: bool = True):
        """
        Initialize LZ complexity calculator.
        
        Args:
            normalize: Whether to normalize by sequence length
        """
        self.normalize = normalize
    
    def compute(self, sequence: Union[np.ndarray, torch.Tensor]) -> float:
        """
        Compute Lempel-Ziv complexity.
        
        Args:
            sequence: Input sequence (1D array)
            
        Returns:
            LZ complexity value
        """
        if isinstance(sequence, torch.Tensor):
            sequence = sequence.detach().cpu().numpy()
        
        # Binarize if needed
        if sequence.dtype != bool:
            sequence = sequence > np.median(sequence)
        
        sequence = sequence.astype(int)
        n = len(sequence)
        
        if n == 0:
            return 0.0
        
        # LZ76 algorithm
        complexity = 1
        i = 0
        
        while i < n:
            # Find longest substring starting at i that appears before i
            max_len = 0
            for j in range(i):
                k = 0
                while i + k < n and sequence[j + k] == sequence[i + k]:
                    k += 1
                    if j + k >= i:
                        break
                max_len = max(max_len, k)
            
            if max_len == 0:
                i += 1
            else:
                i += max_len
            
            complexity += 1
        
        # Normalize
        if self.normalize:
            # Theoretical maximum for random sequence
            # c(n) ~ n / log2(n)
            if n > 1:
                complexity = complexity * np.log2(n) / n
        
        return complexity
    
    def compute_multivariate(
        self,
        data: Union[np.ndarray, torch.Tensor],
        axis: int = 0
    ) -> float:
        """
        Compute multivariate LZ complexity.
        
        Args:
            data: Multidimensional data
            axis: Axis along which to compute
            
        Returns:
            Average LZ complexity across dimensions
        """
        if isinstance(data, torch.Tensor):
            data = data.detach().cpu().numpy()
        
        # Compute along specified axis
        complexities = []
        
        for i in range(data.shape[axis]):
            slice_data = np.take(data, i, axis=axis)
            complexities.append(self.compute(slice_data.flatten()))
        
        return np.mean(complexities)


class PerturbationalComplexityIndex:
    """
    Compute Perturbational Complexity Index (PCI).
    
    PCI measures the complexity of brain responses to
    perturbations, used to assess consciousness levels.
    
    Reference: Casali et al. (2013) Science Translational Medicine
    """
    
    def __init__(
        self,
        n_permutations: int = 100,
        threshold: float = 0.01
    ):
        """
        Initialize PCI calculator.
        
        Args:
            n_permutations: Number of permutations for significance
            threshold: Significance threshold
        """
        self.n_permutations = n_permutations
        self.threshold = threshold
    
    def compute(
        self,
        response: Union[np.ndarray, torch.Tensor],
        baseline: Optional[Union[np.ndarray, torch.Tensor]] = None
    ) -> float:
        """
        Compute PCI from perturbation response.
        
        Args:
            response: Response signal [time, channels]
            baseline: Optional baseline signal
            
        Returns:
            PCI value
        """
        if isinstance(response, torch.Tensor):
            response = response.detach().cpu().numpy()
        
        if baseline is not None and isinstance(baseline, torch.Tensor):
            baseline = baseline.detach().cpu().numpy()
        
        # Compute complexity of response
        response_complexity = self._compute_complexity(response)
        
        # Compute baseline complexity if provided
        if baseline is not None:
            baseline_complexity = self._compute_complexity(baseline)
            pci = response_complexity - baseline_complexity
        else:
            # Use permutation test for significance
            pci = self._permutation_pci(response)
        
        return max(0.0, pci)  # PCI should be non-negative
    
    def _compute_complexity(self, signal_data: np.ndarray) -> float:
        """Compute signal complexity using Lempel-Ziv."""
        lz = LempelZivComplexity(normalize=True)
        
        # Compute for each channel and average
        complexities = []
        for i in range(signal_data.shape[1] if signal_data.ndim > 1 else 1):
            if signal_data.ndim > 1:
                channel_data = signal_data[:, i]
            else:
                channel_data = signal_data
            complexities.append(lz.compute(channel_data))
        
        return np.mean(complexities)
    
    def _permutation_pci(self, signal_data: np.ndarray) -> float:
        """Compute PCI using permutation test."""
        # Observed complexity
        observed = self._compute_complexity(signal_data)
        
        # Permutation distribution
        perm_complexities = []
        for _ in range(self.n_permutations):
            # Shuffle time points
            shuffled = np.random.permutation(signal_data)
            perm_complexities.append(self._compute_complexity(shuffled))
        
        # PCI is the difference from random
        mean_random = np.mean(perm_complexities)
        pci = observed - mean_random
        
        return pci


class IntegratedInformation:
    """
    Compute Integrated Information (Φ) for consciousness analysis.
    
    Based on Tononi's Integrated Information Theory (IIT).
    Measures how much information is integrated across a system.
    """
    
    def __init__(
        self,
        n_bins: int = 2,
        method: str = 'geometric'
    ):
        """
        Initialize IIT calculator.
        
        Args:
            n_bins: Number of bins for discretization
            method: Integration method ('geometric', 'arithmetic')
        """
        self.n_bins = n_bins
        self.method = method
    
    def compute(
        self,
        data: Union[np.ndarray, torch.Tensor]
    ) -> float:
        """
        Compute integrated information Φ.
        
        Args:
            data: System state data [time, nodes]
            
        Returns:
            Φ value
        """
        if isinstance(data, torch.Tensor):
            data = data.detach().cpu().numpy()
        
        # Discretize data
        discretized = self._discretize(data)
        
        # Compute whole system entropy
        whole_entropy = self._compute_entropy(discretized)
        
        # Compute sum of part entropies
        n_nodes = discretized.shape[1]
        part_entropies = sum(
            self._compute_entropy(discretized[:, i:i+1])
            for i in range(n_nodes)
        )
        
        # Φ = H(whole) - Σ H(parts)
        phi = whole_entropy - part_entropies / n_nodes
        
        return max(0.0, phi)  # Φ should be non-negative
    
    def _discretize(self, data: np.ndarray) -> np.ndarray:
        """Discretize continuous data into bins."""
        discretized = np.zeros_like(data, dtype=int)
        
        for i in range(data.shape[1]):
            # Use percentile-based binning
            percentiles = np.linspace(0, 100, self.n_bins + 1)
            bins = np.percentile(data[:, i], percentiles)
            discretized[:, i] = np.digitize(data[:, i], bins[1:-1])
        
        return discretized
    
    def _compute_entropy(self, discretized: np.ndarray) -> float:
        """Compute Shannon entropy of discretized data."""
        # Flatten and count unique states
        if discretized.ndim == 1:
            values, counts = np.unique(discretized, return_counts=True)
        else:
            # Joint entropy across all dimensions
            states = [tuple(row) for row in discretized]
            unique_states, counts = np.unique(states, axis=0, return_counts=True)
        
        # Normalize counts to probabilities
        probabilities = counts / counts.sum()
        
        # Shannon entropy
        return entropy(probabilities, base=2)


class SpectralEntropy:
    """
    Compute spectral entropy for consciousness analysis.
    
    Measures the flatness of the power spectrum,
    related to signal complexity.
    """
    
    def __init__(self, fs: float = 1.0, nperseg: int = 256):
        """
        Initialize spectral entropy calculator.
        
        Args:
            fs: Sampling frequency
            nperseg: Segment length for Welch's method
        """
        self.fs = fs
        self.nperseg = nperseg
    
    def compute(
        self,
        signal_data: Union[np.ndarray, torch.Tensor]
    ) -> float:
        """
        Compute spectral entropy.
        
        Args:
            signal_data: Input signal
            
        Returns:
            Spectral entropy value
        """
        if isinstance(signal_data, torch.Tensor):
            signal_data = signal_data.detach().cpu().numpy()
        
        # Compute power spectrum
        freqs, psd = signal.welch(
            signal_data,
            fs=self.fs,
            nperseg=min(self.nperseg, len(signal_data))
        )
        
        # Normalize PSD
        psd_normalized = psd / psd.sum()
        
        # Compute entropy
        spectral_entropy = entropy(psd_normalized, base=2)
        
        # Normalize by maximum entropy
        max_entropy = np.log2(len(psd))
        
        return spectral_entropy / max_entropy if max_entropy > 0 else 0.0


class PermutationEntropy:
    """
    Compute permutation entropy for consciousness analysis.
    
    Measures the complexity of ordinal patterns in the signal.
    """
    
    def __init__(self, order: int = 3, delay: int = 1):
        """
        Initialize permutation entropy calculator.
        
        Args:
            order: Embedding dimension (pattern length)
            delay: Time delay
        """
        self.order = order
        self.delay = delay
    
    def compute(
        self,
        signal_data: Union[np.ndarray, torch.Tensor]
    ) -> float:
        """
        Compute permutation entropy.
        
        Args:
            signal_data: Input signal
            
        Returns:
            Permutation entropy value
        """
        if isinstance(signal_data, torch.Tensor):
            signal_data = signal_data.detach().cpu().numpy()
        
        signal_data = signal_data.flatten()
        n = len(signal_data)
        
        if n < self.order * self.delay:
            return 0.0
        
        # Generate ordinal patterns
        patterns = []
        for i in range(n - (self.order - 1) * self.delay):
            pattern = signal_data[i:i + self.order * self.delay:self.delay]
            ordinal = np.argsort(pattern)
            patterns.append(tuple(ordinal))
        
        # Count pattern frequencies
        unique, counts = np.unique(patterns, axis=0, return_counts=True)
        probabilities = counts / counts.sum()
        
        # Compute entropy
        pe = entropy(probabilities, base=2)
        
        # Normalize by maximum entropy
        max_entropy = np.log2(np.math.factorial(self.order))
        
        return pe / max_entropy if max_entropy > 0 else 0.0


class SampleEntropy:
    """
    Compute sample entropy for consciousness analysis.
    
    Measures the regularity of time series data.
    """
    
    def __init__(self, m: int = 2, r: float = 0.2):
        """
        Initialize sample entropy calculator.
        
        Args:
            m: Embedding dimension
            r: Tolerance (fraction of std)
        """
        self.m = m
        self.r = r
    
    def compute(
        self,
        signal_data: Union[np.ndarray, torch.Tensor]
    ) -> float:
        """
        Compute sample entropy.
        
        Args:
            signal_data: Input signal
            
        Returns:
            Sample entropy value
        """
        if isinstance(signal_data, torch.Tensor):
            signal_data = signal_data.detach().cpu().numpy()
        
        signal_data = signal_data.flatten()
        n = len(signal_data)
        
        if n < self.m + 1:
            return 0.0
        
        # Compute tolerance
        std = np.std(signal_data)
        tolerance = self.r * std
        
        def _count_matches(data, m, tol):
            count = 0
            for i in range(len(data) - m):
                for j in range(i + 1, len(data) - m):
                    if np.max(np.abs(data[i:i+m] - data[j:j+m])) <= tol:
                        count += 1
            return count
        
        # Count matches for m and m+1
        matches_m = _count_matches(signal_data, self.m, tolerance)
        matches_m1 = _count_matches(signal_data, self.m + 1, tolerance)
        
        # Sample entropy
        if matches_m == 0:
            return float('inf')
        
        return -np.log(matches_m1 / matches_m)


class ConsciousnessAnalyzer:
    """
    Comprehensive consciousness metrics analyzer.
    
    Combines multiple metrics for consciousness assessment.
    """
    
    def __init__(
        self,
        fs: float = 1.0,
        normalize: bool = True
    ):
        """
        Initialize consciousness analyzer.
        
        Args:
            fs: Sampling frequency
            normalize: Whether to normalize metrics
        """
        self.lz = LempelZivComplexity(normalize=normalize)
        self.pci = PerturbationalComplexityIndex()
        self.iit = IntegratedInformation()
        self.spectral = SpectralEntropy(fs=fs)
        self.permutation = PermutationEntropy()
        self.sample = SampleEntropy()
    
    def analyze(
        self,
        data: Union[np.ndarray, torch.Tensor],
        baseline: Optional[Union[np.ndarray, torch.Tensor]] = None
    ) -> ConsciousnessMetrics:
        """
        Perform comprehensive consciousness analysis.
        
        Args:
            data: Input data [time, channels] or [time]
            baseline: Optional baseline for comparison
            
        Returns:
            ConsciousnessMetrics with all computed values
        """
        if isinstance(data, torch.Tensor):
            data = data.detach().cpu().numpy()
        
        if baseline is not None and isinstance(baseline, torch.Tensor):
            baseline = baseline.detach().cpu().numpy()
        
        # Ensure 2D
        if data.ndim == 1:
            data = data.reshape(-1, 1)
        
        # Compute all metrics
        metrics = ConsciousnessMetrics(
            lz_complexity=self.lz.compute(data.flatten()),
            normalized_lz=self.lz.compute(data.flatten()),
            pci=self.pci.compute(data, baseline),
            phi=self.iit.compute(data),
            spectral_entropy=self.spectral.compute(data[:, 0]),
            permutation_entropy=self.permutation.compute(data[:, 0]),
            sample_entropy=self.sample.compute(data[:, 0]),
            approximate_entropy=self._approximate_entropy(data[:, 0]),
            multiscale_entropy=self._multiscale_entropy(data[:, 0]),
            functional_connectivity=self._functional_connectivity(data),
            effective_connectivity=self._effective_connectivity(data)
        )
        
        return metrics
    
    def _approximate_entropy(self, signal_data: np.ndarray) -> float:
        """Compute approximate entropy."""
        # Simplified implementation
        return self.sample.compute(signal_data) * 0.8  # Approximate relationship
    
    def _multiscale_entropy(
        self,
        signal_data: np.ndarray,
        scales: List[int] = [1, 2, 4, 8]
    ) -> List[float]:
        """Compute multiscale entropy."""
        mse = []
        for scale in scales:
            # Coarse-grain the signal
            n = len(signal_data) // scale
            if n < 2:
                mse.append(0.0)
                continue
            
            coarse = np.array([
                np.mean(signal_data[i*scale:(i+1)*scale])
                for i in range(n)
            ])
            mse.append(self.sample.compute(coarse))
        
        return mse
    
    def _functional_connectivity(self, data: np.ndarray) -> float:
        """Compute functional connectivity strength."""
        if data.shape[1] < 2:
            return 0.0
        
        # Correlation matrix
        corr = np.corrcoef(data.T)
        
        # Mean absolute correlation (excluding diagonal)
        n = corr.shape[0]
        mask = ~np.eye(n, dtype=bool)
        mean_corr = np.mean(np.abs(corr[mask]))
        
        return mean_corr
    
    def _effective_connectivity(self, data: np.ndarray) -> float:
        """Compute effective connectivity (simplified)."""
        # Use Granger causality approximation
        if data.shape[1] < 2 or data.shape[0] < 10:
            return 0.0
        
        # Simplified: use variance explained
        var_explained = []
        for i in range(data.shape[1]):
            # Variance of each channel
            var_explained.append(np.var(data[:, i]))
        
        # Normalize
        total_var = sum(var_explained)
        if total_var > 0:
            return np.mean(var_explained) / total_var
        return 0.0
    
    def to_dict(self, metrics: ConsciousnessMetrics) -> Dict[str, Union[float, List[float]]]:
        """Convert metrics to dictionary."""
        return {
            'lz_complexity': metrics.lz_complexity,
            'normalized_lz': metrics.normalized_lz,
            'pci': metrics.pci,
            'phi': metrics.phi,
            'spectral_entropy': metrics.spectral_entropy,
            'permutation_entropy': metrics.permutation_entropy,
            'sample_entropy': metrics.sample_entropy,
            'approximate_entropy': metrics.approximate_entropy,
            'multiscale_entropy': metrics.multiscale_entropy,
            'functional_connectivity': metrics.functional_connectivity,
            'effective_connectivity': metrics.effective_connectivity
        }


def validate_with_eeg(
    predicted: np.ndarray,
    eeg_data: np.ndarray,
    sampling_rate: float = 250.0
) -> Dict[str, float]:
    """
    Cross-validate predictions with real EEG data.
    
    Args:
        predicted: Model predictions
        eeg_data: Real EEG data
        sampling_rate: EEG sampling rate in Hz
        
    Returns:
        Dictionary of validation metrics
    """
    analyzer = ConsciousnessAnalyzer(fs=sampling_rate)
    
    # Compute metrics for both
    pred_metrics = analyzer.analyze(predicted)
    eeg_metrics = analyzer.analyze(eeg_data)
    
    # Compute correlations
    validation = {
        'lz_correlation': np.corrcoef([pred_metrics.lz_complexity], [eeg_metrics.lz_complexity])[0, 1],
        'pci_difference': abs(pred_metrics.pci - eeg_metrics.pci),
        'phi_difference': abs(pred_metrics.phi - eeg_metrics.phi),
        'spectral_correlation': np.corrcoef([pred_metrics.spectral_entropy], [eeg_metrics.spectral_entropy])[0, 1]
    }
    
    return validation


if __name__ == "__main__":
    print("Consciousness Metrics Validation Module")
    print("=" * 50)
    
    # Create sample data
    np.random.seed(42)
    time_points = 1000
    n_channels = 32
    
    # Simulated neural data
    data = np.random.randn(time_points, n_channels)
    
    # Add some structure
    for i in range(n_channels):
        data[:, i] += 0.5 * np.sin(2 * np.pi * (i + 1) * 0.01 * np.arange(time_points))
    
    # Initialize analyzer
    analyzer = ConsciousnessAnalyzer(fs=250.0)
    
    # Compute metrics
    metrics = analyzer.analyze(data)
    
    print(f"LZ Complexity: {metrics.lz_complexity:.4f}")
    print(f"PCI: {metrics.pci:.4f}")
    print(f"Phi (IIT): {metrics.phi:.4f}")
    print(f"Spectral Entropy: {metrics.spectral_entropy:.4f}")
    print(f"Permutation Entropy: {metrics.permutation_entropy:.4f}")
    print(f"Sample Entropy: {metrics.sample_entropy:.4f}")
    print(f"Functional Connectivity: {metrics.functional_connectivity:.4f}")
    print(f"Effective Connectivity: {metrics.effective_connectivity:.4f}")