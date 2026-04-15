"""
Null Models for Metric Validation
=================================

Provides null model generators for testing whether metrics
are significantly different from random/shuffled baselines.

Date: April 15, 2026
"""

import numpy as np
from typing import Callable, Dict, List, Tuple, Optional
from scipy import stats


class NullModelGenerator:
    """Generates null model data for metric validation."""
    
    def __init__(self, seed: int = 42):
        np.random.seed(seed)
        self.phi = (1 + np.sqrt(5)) / 2
    
    # =========================================================================
    # GEOMETRIC NULL MODELS
    # =========================================================================
    
    def random_positions(self, n_atoms: int, scale: float = 1.0) -> np.ndarray:
        """Generate random 3D positions (null for molecular geometry)."""
        return np.random.randn(n_atoms, 3) * scale
    
    def random_geometric_ratios(self, n_ratios: int = 10) -> np.ndarray:
        """Generate random geometric ratios (null for phi-ratio analysis)."""
        distances = np.sort(np.random.exponential(1.0, n_ratios + 1))
        ratios = distances[1:] / distances[:-1]
        return ratios
    
    def shuffled_positions(self, positions: np.ndarray) -> np.ndarray:
        """Shuffle atomic positions (null for structure-property relationships)."""
        shuffled = positions.copy()
        np.random.shuffle(shuffled)
        return shuffled
    
    # =========================================================================
    # QUANTUM NULL MODELS
    # =========================================================================
    
    def random_quantum_state(self, dim: int) -> np.ndarray:
        """Generate random quantum state vector (null for quantum metrics)."""
        state = np.random.randn(dim) + 1j * np.random.randn(dim)
        return state / np.linalg.norm(state)
    
    def random_amplitudes(self, n_atoms: int, latent_dim: int) -> np.ndarray:
        """Generate random quantum amplitudes (null for molecular encoding)."""
        amplitudes = np.random.randn(n_atoms, latent_dim)
        norms = np.linalg.norm(amplitudes, axis=1, keepdims=True)
        return amplitudes / (norms + 1e-10)
    
    def random_phases(self, n_atoms: int, latent_dim: int) -> np.ndarray:
        """Generate random quantum phases (null for coherence analysis)."""
        return np.random.uniform(0, 2 * np.pi, (n_atoms, latent_dim))
    
    def random_density_matrix(self, dim: int) -> np.ndarray:
        """Generate random valid density matrix (null for entropy analysis)."""
        # Generate random Hermitian matrix
        H = np.random.randn(dim, dim) + 1j * np.random.randn(dim, dim)
        rho = H @ H.conj().T
        # Normalize to trace 1
        return rho / np.trace(rho)
    
    # =========================================================================
    # NEURAL NULL MODELS
    # =========================================================================
    
    def random_network(self, n_nodes: int, edge_prob: float = 0.1) -> np.ndarray:
        """Generate random network adjacency matrix (null for network metrics)."""
        adj = np.random.rand(n_nodes, n_nodes) < edge_prob
        adj = adj.astype(float)
        adj = (adj + adj.T) / 2  # Symmetric
        np.fill_diagonal(adj, 0)  # No self-loops
        return adj
    
    def random_activations(self, n_neurons: int, n_samples: int) -> np.ndarray:
        """Generate random neural activations (null for neural metrics)."""
        return np.random.randn(n_samples, n_neurons)
    
    # =========================================================================
    # SEQUENCE NULL MODELS
    # =========================================================================
    
    def random_sequence(self, length: int, alphabet_size: int = 4) -> np.ndarray:
        """Generate random sequence (null for sequence metrics)."""
        return np.random.randint(0, alphabet_size, length)
    
    def shuffled_sequence(self, sequence: np.ndarray) -> np.ndarray:
        """Shuffle a sequence (null for order-dependent metrics)."""
        shuffled = sequence.copy()
        np.random.shuffle(shuffled)
        return shuffled
    
    # =========================================================================
    # TEXT NULL MODELS
    # =========================================================================
    
    def random_text_length(self, min_len: int = 10, max_len: int = 1000) -> int:
        """Generate random text length (null for phi-coherence)."""
        return np.random.randint(min_len, max_len)


class NullModelTester:
    """Tests metrics against null models."""
    
    def __init__(self, n_trials: int = 1000, seed: int = 42):
        self.n_trials = n_trials
        self.generator = NullModelGenerator(seed)
    
    def test_phi_resonance_null(self, 
                                 metric_fn: Callable,
                                 n_ratios: int = 10) -> Dict:
        """
        Test phi resonance against random geometric ratios.
        
        Args:
            metric_fn: Function that computes phi resonance from ratios
            n_ratios: Number of ratios to generate
            
        Returns:
            Dictionary with null distribution and p-value
        """
        null_values = []
        
        for _ in range(self.n_trials):
            ratios = self.generator.random_geometric_ratios(n_ratios)
            value = metric_fn(ratios)
            null_values.append(value)
        
        null_values = np.array(null_values)
        
        return {
            "null_mean": float(np.mean(null_values)),
            "null_std": float(np.std(null_values)),
            "null_median": float(np.median(null_values)),
            "null_q05": float(np.percentile(null_values, 5)),
            "null_q95": float(np.percentile(null_values, 95)),
            "null_distribution": null_values.tolist()
        }
    
    def test_entanglement_entropy_null(self,
                                        metric_fn: Callable,
                                        n_atoms: int = 5,
                                        latent_dim: int = 32) -> Dict:
        """
        Test entanglement entropy against random quantum states.
        
        Args:
            metric_fn: Function that computes entropy from amplitudes
            n_atoms: Number of atoms
            latent_dim: Latent dimension
        """
        null_values = []
        
        for _ in range(self.n_trials):
            amplitudes = self.generator.random_amplitudes(n_atoms, latent_dim)
            value = metric_fn(amplitudes)
            null_values.append(value)
        
        null_values = np.array(null_values)
        
        return {
            "null_mean": float(np.mean(null_values)),
            "null_std": float(np.std(null_values)),
            "null_median": float(np.median(null_values)),
            "null_q05": float(np.percentile(null_values, 5)),
            "null_q95": float(np.percentile(null_values, 95)),
        }
    
    def test_platonic_alignment_null(self,
                                     metric_fn: Callable,
                                     n_atoms: int = 5) -> Dict:
        """
        Test Platonic alignment against random point clouds.
        """
        null_values = []
        
        for _ in range(self.n_trials):
            positions = self.generator.random_positions(n_atoms)
            value = metric_fn(positions)
            null_values.append(value)
        
        null_values = np.array(null_values)
        
        return {
            "null_mean": float(np.mean(null_values)),
            "null_std": float(np.std(null_values)),
            "null_median": float(np.median(null_values)),
        }
    
    def test_biomimetic_resonance_null(self,
                                        metric_fn: Callable,
                                        feature_dim: int = 100) -> Dict:
        """
        Test biomimetic resonance against random feature vectors.
        """
        null_values = []
        
        for _ in range(self.n_trials):
            X_system = self.generator.random_activations(1, feature_dim).flatten()
            X_bio = self.generator.random_activations(1, feature_dim).flatten()
            value = metric_fn(X_system, X_bio)
            null_values.append(value)
        
        null_values = np.array(null_values)
        
        return {
            "null_mean": float(np.mean(null_values)),
            "null_std": float(np.std(null_values)),
            "null_median": float(np.median(null_values)),
        }
    
    def compute_p_value(self, 
                        observed_value: float, 
                        null_distribution: np.ndarray,
                        alternative: str = "two-sided") -> float:
        """
        Compute p-value for observed value against null distribution.
        
        Args:
            observed_value: The observed metric value
            null_distribution: Array of null model values
            alternative: 'two-sided', 'greater', or 'less'
            
        Returns:
            p-value
        """
        null_mean = np.mean(null_distribution)
        null_std = np.std(null_distribution) + 1e-10
        
        if alternative == "two-sided":
            # Two-sided: probability of being this far from mean
            z = abs(observed_value - null_mean) / null_std
            p = 2 * (1 - stats.norm.cdf(z))
        elif alternative == "greater":
            # One-sided: probability of being this large or larger
            z = (observed_value - null_mean) / null_std
            p = 1 - stats.norm.cdf(z)
        elif alternative == "less":
            # One-sided: probability of being this small or smaller
            z = (observed_value - null_mean) / null_std
            p = stats.norm.cdf(z)
        else:
            raise ValueError(f"Unknown alternative: {alternative}")
        
        return float(p)
    
    def is_significant(self,
                       observed_value: float,
                       null_distribution: np.ndarray,
                       alpha: float = 0.05,
                       alternative: str = "two-sided") -> Tuple[bool, float]:
        """
        Test if observed value is significantly different from null.
        
        Returns:
            (is_significant, p_value)
        """
        p_value = self.compute_p_value(observed_value, null_distribution, alternative)
        return p_value < alpha, p_value


# =============================================================================
# SPECIFIC NULL MODEL IMPLEMENTATIONS
# =============================================================================

def null_phi_resonance(n_trials: int = 1000) -> Dict:
    """
    Compute null distribution for phi resonance.
    
    For random geometric ratios, the expected phi resonance is ~0.6
    because random ratios are uniformly distributed and the minimum
    deviation from phi is typically around 0.4.
    """
    phi = (1 + np.sqrt(5)) / 2
    null_values = []
    
    for _ in range(n_trials):
        # Random ratios from exponential distances
        distances = np.sort(np.random.exponential(1.0, 11))
        ratios = distances[1:] / distances[:-1]
        
        # Phi resonance formula
        min_dev = np.min(np.abs(ratios - phi))
        resonance = np.exp(-min_dev)
        null_values.append(resonance)
    
    return {
        "null_mean": float(np.mean(null_values)),
        "null_std": float(np.std(null_values)),
        "expected_range": (0.4, 0.8),
        "n_trials": n_trials
    }


def null_entanglement_entropy(n_atoms: int = 5, 
                               latent_dim: int = 32,
                               n_trials: int = 1000) -> Dict:
    """
    Compute null distribution for entanglement entropy.
    
    For random quantum states, the expected entropy is close to
    the maximum log(d_A) where d_A is the subsystem dimension.
    """
    null_values = []
    
    for _ in range(n_trials):
        # Random normalized amplitudes
        amps = np.random.randn(n_atoms, latent_dim)
        amps = amps / np.linalg.norm(amps, axis=1, keepdims=True)
        
        # Flatten and reshape for bipartite
        psi = amps.flatten()
        n_total = len(psi)
        d_A = int(np.sqrt(n_total))
        while n_total % d_A != 0 and d_A > 1:
            d_A -= 1
        d_B = n_total // d_A
        
        # Compute reduced density matrix
        psi_matrix = psi.reshape(d_A, d_B)
        rho_A = psi_matrix @ psi_matrix.conj().T
        
        # Compute entropy
        eigenvalues = np.linalg.eigvalsh(rho_A)
        eigenvalues = np.maximum(eigenvalues, 1e-10)
        entropy = -np.sum(eigenvalues * np.log(eigenvalues))
        null_values.append(entropy)
    
    return {
        "null_mean": float(np.mean(null_values)),
        "null_std": float(np.std(null_values)),
        "theoretical_max": float(np.log(d_A)),
        "n_trials": n_trials
    }


def null_platonic_alignment(n_atoms: int = 5, n_trials: int = 1000) -> Dict:
    """
    Compute null distribution for Platonic alignment scores.
    
    For random point clouds, the expected alignment is ~0.6
    because random points in a unit sphere have average distance
    of about 0.5 from any template vertex.
    """
    null_values = []
    
    for _ in range(n_trials):
        # Random positions in unit sphere
        positions = np.random.randn(n_atoms, 3)
        positions = positions / np.linalg.norm(positions, axis=1, keepdims=True)
        
        # Simple alignment score (distance to origin)
        mean_dist = np.mean(np.linalg.norm(positions, axis=1))
        alignment = np.exp(-mean_dist)
        null_values.append(alignment)
    
    return {
        "null_mean": float(np.mean(null_values)),
        "null_std": float(np.std(null_values)),
        "n_trials": n_trials
    }


if __name__ == "__main__":
    print("="*60)
    print("NULL MODEL DISTRIBUTIONS")
    print("="*60)
    
    print("\nPhi Resonance Null Model:")
    phi_null = null_phi_resonance(1000)
    print(f"  Mean: {phi_null['null_mean']:.4f}")
    print(f"  Std:  {phi_null['null_std']:.4f}")
    print(f"  Expected range: {phi_null['expected_range']}")
    
    print("\nEntanglement Entropy Null Model:")
    entropy_null = null_entanglement_entropy(5, 32, 1000)
    print(f"  Mean: {entropy_null['null_mean']:.4f}")
    print(f"  Std:  {entropy_null['null_std']:.4f}")
    print(f"  Theoretical max: {entropy_null['theoretical_max']:.4f}")
    
    print("\nPlatonic Alignment Null Model:")
    platonic_null = null_platonic_alignment(5, 1000)
    print(f"  Mean: {platonic_null['null_mean']:.4f}")
    print(f"  Std:  {platonic_null['null_std']:.4f}")