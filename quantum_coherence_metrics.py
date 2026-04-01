"""
Quantum Coherence Metrics Module
================================

Implements advanced quantum coherence metrics for VAE latent space analysis.
Based on quantum information theory and consciousness research.

References:
- Cooney (2019) - Quantum coherence measures
- Girolami (2014) - Quantum discord and correlations
- Zurek (2003) - Decoherence and einselection
"""

import torch
import numpy as np
from typing import Dict, Tuple, Optional, Union
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class CoherenceMetrics:
    """Container for quantum coherence metrics."""
    l1_coherence: float
    relative_entropy_coherence: float
    geometric_coherence: float
    robustness_coherence: float
    frobenius_norm: float
    trace_distance: float
    purity: float
    von_neumann_entropy: float
    participation_ratio: float
    effective_dimension: float


class QuantumCoherenceAnalyzer:
    """
    Analyzes quantum coherence properties of VAE latent representations.
    
    Implements multiple coherence measures:
    - L1-norm coherence (Baumgratz et al., 2014)
    - Relative entropy coherence (Streltsov et al., 2016)
    - Geometric coherence (Chitambar & Goh, 2017)
    - Robustness of coherence (Napoli et al., 2016)
    """
    
    def __init__(
        self,
        latent_dim: int = 32,
        device: str = 'cpu',
        epsilon: float = 1e-10
    ):
        """
        Initialize the coherence analyzer.
        
        Args:
            latent_dim: Dimension of the latent space
            device: Device for computations ('cpu' or 'cuda')
            epsilon: Small value for numerical stability
        """
        self.latent_dim = latent_dim
        self.device = device
        self.epsilon = epsilon
    
    def compute_density_matrix(
        self,
        latent_codes: torch.Tensor,
        normalize: bool = True
    ) -> torch.Tensor:
        """
        Compute the density matrix from latent codes.
        
        Args:
            latent_codes: Batch of latent vectors [batch_size, latent_dim]
            normalize: Whether to normalize the density matrix
            
        Returns:
            Density matrix [latent_dim, latent_dim]
        """
        # Ensure 2D
        if latent_codes.dim() == 1:
            latent_codes = latent_codes.unsqueeze(0)
        
        batch_size = latent_codes.shape[0]
        
        # Compute outer products and average
        # ρ = (1/N) Σ |z_i⟩⟨z_i|
        density_matrix = torch.zeros(
            self.latent_dim, self.latent_dim,
            device=self.device, dtype=latent_codes.dtype
        )
        
        for i in range(batch_size):
            z = latent_codes[i].unsqueeze(1)  # [latent_dim, 1]
            density_matrix += z @ z.T  # Outer product
        
        density_matrix /= batch_size
        
        if normalize:
            # Ensure trace = 1
            trace = torch.trace(density_matrix)
            if trace > self.epsilon:
                density_matrix /= trace
        
        return density_matrix
    
    def l1_coherence(self, density_matrix: torch.Tensor) -> float:
        """
        Compute L1-norm coherence.
        
        C_l1(ρ) = Σ_{i≠j} |ρ_ij|
        
        Args:
            density_matrix: Quantum state density matrix
            
        Returns:
            L1 coherence value
        """
        # Off-diagonal elements
        off_diagonal = density_matrix - torch.diag(torch.diag(density_matrix))
        coherence = torch.sum(torch.abs(off_diagonal)).item()
        
        # Normalize by dimension
        normalized = coherence / (self.latent_dim - 1) if self.latent_dim > 1 else coherence
        
        return normalized
    
    def relative_entropy_coherence(
        self,
        density_matrix: torch.Tensor,
        max_iter: int = 100
    ) -> float:
        """
        Compute relative entropy coherence.
        
        C_re(ρ) = S(ρ_diag) - S(ρ)
        
        where S is von Neumann entropy and ρ_diag is diagonal part.
        
        Args:
            density_matrix: Quantum state density matrix
            max_iter: Maximum iterations for numerical stability
            
        Returns:
            Relative entropy coherence
        """
        # Diagonal part (incoherent state)
        diag = torch.diag(torch.diag(density_matrix))
        
        # Von Neumann entropy of diagonal
        diag_eigenvalues = torch.diag(diag)
        diag_eigenvalues = torch.clamp(diag_eigenvalues, min=self.epsilon)
        s_diag = -torch.sum(diag_eigenvalues * torch.log2(diag_eigenvalues + self.epsilon))
        
        # Von Neumann entropy of full state
        eigenvalues = torch.linalg.eigvalsh(density_matrix)
        eigenvalues = torch.clamp(eigenvalues, min=self.epsilon)
        s_rho = -torch.sum(eigenvalues * torch.log2(eigenvalues + self.epsilon))
        
        # Relative entropy coherence
        coherence = (s_diag - s_rho).item()
        
        return max(0.0, coherence)  # Ensure non-negative
    
    def geometric_coherence(self, density_matrix: torch.Tensor) -> float:
        """
        Compute geometric coherence.
        
        C_g(ρ) = min_{δ∈I} ||ρ - δ||_2
        
        where I is the set of incoherent states.
        
        Args:
            density_matrix: Quantum state density matrix
            
        Returns:
            Geometric coherence value
        """
        # Distance to nearest incoherent state (diagonal)
        incoherent = torch.diag(torch.diag(density_matrix))
        
        # Frobenius norm distance
        distance = torch.norm(density_matrix - incoherent, p='fro').item()
        
        # Normalize
        normalized = distance / np.sqrt(2 * (self.latent_dim - 1)) if self.latent_dim > 1 else distance
        
        return normalized
    
    def robustness_coherence(
        self,
        density_matrix: torch.Tensor,
        tolerance: float = 1e-6
    ) -> float:
        """
        Compute robustness of coherence.
        
        C_R(ρ) = min { s ≥ 0 : (ρ + sδ)/(1+s) ∈ I }
        
        Simplified implementation using geometric approximation.
        
        Args:
            density_matrix: Quantum state density matrix
            tolerance: Numerical tolerance
            
        Returns:
            Robustness coherence value
        """
        # Simplified: use geometric coherence as approximation
        # Full SDP solution would be more accurate but computationally expensive
        geometric = self.geometric_coherence(density_matrix)
        
        # Approximate robustness
        robustness = geometric * (1 + geometric) / (1 + self.epsilon)
        
        return robustness
    
    def compute_purity(self, density_matrix: torch.Tensor) -> float:
        """
        Compute purity of the quantum state.
        
        P(ρ) = Tr(ρ²)
        
        Args:
            density_matrix: Quantum state density matrix
            
        Returns:
            Purity value (1 for pure states, < 1 for mixed)
        """
        purity = torch.trace(density_matrix @ density_matrix).item()
        return purity
    
    def compute_von_neumann_entropy(self, density_matrix: torch.Tensor) -> float:
        """
        Compute von Neumann entropy.
        
        S(ρ) = -Tr(ρ log₂ ρ)
        
        Args:
            density_matrix: Quantum state density matrix
            
        Returns:
            Von Neumann entropy in bits
        """
        eigenvalues = torch.linalg.eigvalsh(density_matrix)
        eigenvalues = torch.clamp(eigenvalues, min=self.epsilon)
        
        entropy = -torch.sum(eigenvalues * torch.log2(eigenvalues + self.epsilon)).item()
        
        return entropy
    
    def compute_participation_ratio(self, density_matrix: torch.Tensor) -> float:
        """
        Compute participation ratio (effective number of states).
        
        PR = 1 / Σ_i λ_i²
        
        Args:
            density_matrix: Quantum state density matrix
            
        Returns:
            Participation ratio
        """
        eigenvalues = torch.linalg.eigvalsh(density_matrix)
        eigenvalues = torch.clamp(eigenvalues, min=self.epsilon)
        
        # Inverse of purity
        purity = torch.sum(eigenvalues ** 2).item()
        
        if purity > self.epsilon:
            return 1.0 / purity
        return 1.0
    
    def compute_effective_dimension(
        self,
        latent_codes: torch.Tensor,
        threshold: float = 0.95
    ) -> int:
        """
        Compute effective dimensionality of latent space.
        
        Number of dimensions needed to explain threshold variance.
        
        Args:
            latent_codes: Batch of latent vectors
            threshold: Variance threshold (default 95%)
            
        Returns:
            Effective dimension
        """
        # Compute covariance
        if latent_codes.dim() == 1:
            latent_codes = latent_codes.unsqueeze(0)
        
        # Center the data
        centered = latent_codes - latent_codes.mean(dim=0)
        
        # Compute covariance matrix
        cov = torch.cov(centered.T)
        
        # Eigenvalue decomposition
        eigenvalues = torch.linalg.eigvalsh(cov)
        eigenvalues = torch.sort(eigenvalues, descending=True)[0]
        
        # Cumulative variance
        total_var = eigenvalues.sum()
        cumsum = torch.cumsum(eigenvalues, dim=0)
        
        # Find threshold
        effective_dim = torch.sum(cumsum < threshold * total_var).item() + 1
        
        return min(effective_dim, self.latent_dim)
    
    def analyze(
        self,
        latent_codes: torch.Tensor,
        compute_all: bool = True
    ) -> CoherenceMetrics:
        """
        Perform comprehensive coherence analysis.
        
        Args:
            latent_codes: Batch of latent vectors
            compute_all: Whether to compute all metrics
            
        Returns:
            CoherenceMetrics with all computed values
        """
        # Move to device
        latent_codes = latent_codes.to(self.device)
        
        # Compute density matrix
        density_matrix = self.compute_density_matrix(latent_codes)
        
        # Compute all metrics
        metrics = CoherenceMetrics(
            l1_coherence=self.l1_coherence(density_matrix),
            relative_entropy_coherence=self.relative_entropy_coherence(density_matrix),
            geometric_coherence=self.geometric_coherence(density_matrix),
            robustness_coherence=self.robustness_coherence(density_matrix),
            frobenius_norm=torch.norm(density_matrix, p='fro').item(),
            trace_distance=self._compute_trace_distance(density_matrix),
            purity=self.compute_purity(density_matrix),
            von_neumann_entropy=self.compute_von_neumann_entropy(density_matrix),
            participation_ratio=self.compute_participation_ratio(density_matrix),
            effective_dimension=self.compute_effective_dimension(latent_codes)
        )
        
        return metrics
    
    def _compute_trace_distance(self, density_matrix: torch.Tensor) -> float:
        """Compute trace distance from maximally mixed state."""
        maximally_mixed = torch.eye(self.latent_dim, device=self.device) / self.latent_dim
        difference = density_matrix - maximally_mixed
        trace_distance = 0.5 * torch.trace(torch.sqrt(difference @ difference.T)).item()
        return trace_distance
    
    def to_dict(self, metrics: CoherenceMetrics) -> Dict[str, float]:
        """Convert metrics to dictionary."""
        return {
            'l1_coherence': metrics.l1_coherence,
            'relative_entropy_coherence': metrics.relative_entropy_coherence,
            'geometric_coherence': metrics.geometric_coherence,
            'robustness_coherence': metrics.robustness_coherence,
            'frobenius_norm': metrics.frobenius_norm,
            'trace_distance': metrics.trace_distance,
            'purity': metrics.purity,
            'von_neumann_entropy': metrics.von_neumann_entropy,
            'participation_ratio': metrics.participation_ratio,
            'effective_dimension': metrics.effective_dimension
        }


class GoldenRatioLoss(torch.nn.Module):
    """
    Loss function for golden ratio optimization in latent space.
    
    Encourages latent dimensions to exhibit golden ratio (φ ≈ 1.618)
    relationships, which are associated with optimal packing and
    consciousness-related patterns.
    """
    
    def __init__(
        self,
        phi: float = 1.618033988749895,
        weight: float = 0.1,
        method: str = 'ratio'
    ):
        """
        Initialize golden ratio loss.
        
        Args:
            phi: Golden ratio value (default: precise value)
            weight: Loss weight coefficient
            method: Loss method ('ratio', 'difference', 'fibonacci')
        """
        super().__init__()
        self.phi = phi
        self.weight = weight
        self.method = method
    
    def forward(self, latent_codes: torch.Tensor) -> torch.Tensor:
        """
        Compute golden ratio loss.
        
        Args:
            latent_codes: Batch of latent vectors [batch_size, latent_dim]
            
        Returns:
            Golden ratio loss value
        """
        if latent_codes.dim() == 1:
            latent_codes = latent_codes.unsqueeze(0)
        
        if self.method == 'ratio':
            return self._ratio_loss(latent_codes)
        elif self.method == 'difference':
            return self._difference_loss(latent_codes)
        elif self.method == 'fibonacci':
            return self._fibonacci_loss(latent_codes)
        else:
            return self._ratio_loss(latent_codes)
    
    def _ratio_loss(self, latent_codes: torch.Tensor) -> torch.Tensor:
        """
        Compute ratio-based golden ratio loss.
        
        Encourages consecutive dimension ratios to approach φ.
        """
        # Sort latent dimensions by magnitude
        sorted_latent, _ = torch.sort(torch.abs(latent_codes), dim=1, descending=True)
        
        # Compute consecutive ratios
        ratios = sorted_latent[:, 1:] / (sorted_latent[:, :-1] + 1e-10)
        
        # Distance from golden ratio
        phi_distance = torch.abs(ratios - self.phi)
        
        # Mean distance
        loss = torch.mean(phi_distance)
        
        return self.weight * loss
    
    def _difference_loss(self, latent_codes: torch.Tensor) -> torch.Tensor:
        """
        Compute difference-based golden ratio loss.
        
        Encourages φ relationships in dimension differences.
        """
        # Compute pairwise differences
        diff_matrix = latent_codes.unsqueeze(2) - latent_codes.unsqueeze(1)
        
        # Flatten and compute ratio to golden ratio
        diffs = diff_matrix.view(latent_codes.shape[0], -1)
        
        # Encourage differences to be multiples of φ
        normalized = diffs / self.phi
        fractional = normalized - torch.round(normalized)
        
        loss = torch.mean(torch.abs(fractional))
        
        return self.weight * loss
    
    def _fibonacci_loss(self, latent_codes: torch.Tensor) -> torch.Tensor:
        """
        Compute Fibonacci-based golden ratio loss.
        
        Uses Fibonacci sequence relationships to encourage φ patterns.
        """
        # Generate Fibonacci-like weights
        batch_size, latent_dim = latent_codes.shape
        
        # Create Fibonacci sequence
        fib = [1, 1]
        for i in range(2, latent_dim):
            fib.append(fib[-1] + fib[-2])
        
        fib_tensor = torch.tensor(fib, device=latent_codes.device, dtype=latent_codes.dtype)
        
        # Normalize
        fib_weights = fib_tensor / fib_tensor.sum()
        
        # Weighted latent codes
        weighted = latent_codes * fib_weights.unsqueeze(0)
        
        # Encourage weighted sum to follow Fibonacci pattern
        expected_ratio = torch.tensor(self.phi, device=latent_codes.device)
        
        # Compute ratio of consecutive weighted sums
        weighted_sorted, _ = torch.sort(torch.abs(weighted), dim=1, descending=True)
        ratios = weighted_sorted[:, 1:] / (weighted_sorted[:, :-1] + 1e-10)
        
        # Distance from golden ratio
        loss = torch.mean(torch.abs(ratios - expected_ratio))
        
        return self.weight * loss


class MixedStateRegularizer(torch.nn.Module):
    """
    Regularizer for mixed-state quantum representations.
    
    Encourages the latent space to maintain quantum-like mixed-state
    properties including:
    - Positive semi-definiteness
    - Unit trace
    - Proper eigenvalue distribution
    """
    
    def __init__(
        self,
        latent_dim: int = 32,
        entropy_weight: float = 0.05,
        purity_weight: float = 0.05,
        trace_weight: float = 0.01
    ):
        """
        Initialize mixed state regularizer.
        
        Args:
            latent_dim: Dimension of latent space
            entropy_weight: Weight for entropy regularization
            purity_weight: Weight for purity regularization
            trace_weight: Weight for trace regularization
        """
        super().__init__()
        self.latent_dim = latent_dim
        self.entropy_weight = entropy_weight
        self.purity_weight = purity_weight
        self.trace_weight = trace_weight
    
    def forward(self, latent_codes: torch.Tensor) -> Dict[str, torch.Tensor]:
        """
        Compute mixed state regularization losses.
        
        Args:
            latent_codes: Batch of latent vectors
            
        Returns:
            Dictionary of loss components
        """
        # Compute density matrix
        density_matrix = self._compute_density_matrix(latent_codes)
        
        # Entropy regularization (encourage mixed states)
        entropy_loss = self._entropy_regularization(density_matrix)
        
        # Purity regularization (balance pure/mixed)
        purity_loss = self._purity_regularization(density_matrix)
        
        # Trace regularization (ensure unit trace)
        trace_loss = self._trace_regularization(density_matrix)
        
        # Total loss
        total_loss = (
            self.entropy_weight * entropy_loss +
            self.purity_weight * purity_loss +
            self.trace_weight * trace_loss
        )
        
        return {
            'total': total_loss,
            'entropy': entropy_loss,
            'purity': purity_loss,
            'trace': trace_loss
        }
    
    def _compute_density_matrix(self, latent_codes: torch.Tensor) -> torch.Tensor:
        """Compute density matrix from latent codes."""
        batch_size = latent_codes.shape[0]
        
        # Outer products
        density = torch.zeros(
            self.latent_dim, self.latent_dim,
            device=latent_codes.device, dtype=latent_codes.dtype
        )
        
        for i in range(batch_size):
            z = latent_codes[i].unsqueeze(1)
            density += z @ z.T
        
        density /= batch_size
        
        return density
    
    def _entropy_regularization(self, density_matrix: torch.Tensor) -> torch.Tensor:
        """Regularize entropy to encourage mixed states."""
        eigenvalues = torch.linalg.eigvalsh(density_matrix)
        eigenvalues = torch.clamp(eigenvalues, min=1e-10)
        
        # Von Neumann entropy
        entropy = -torch.sum(eigenvalues * torch.log2(eigenvalues + 1e-10))
        
        # Target: maximum entropy (fully mixed state)
        max_entropy = np.log2(self.latent_dim)
        
        # Loss: distance from maximum entropy
        loss = torch.abs(entropy - max_entropy)
        
        return loss
    
    def _purity_regularization(self, density_matrix: torch.Tensor) -> torch.Tensor:
        """Regularize purity to balance pure/mixed states."""
        purity = torch.trace(density_matrix @ density_matrix)
        
        # Target: intermediate purity (not too pure, not too mixed)
        target_purity = 0.5  # Balance point
        
        loss = torch.abs(purity - target_purity)
        
        return loss
    
    def _trace_regularization(self, density_matrix: torch.Tensor) -> torch.Tensor:
        """Regularize trace to ensure unit trace."""
        trace = torch.trace(density_matrix)
        
        # Target: trace = 1
        loss = torch.abs(trace - 1.0)
        
        return loss


# Convenience functions
def compute_coherence_metrics(
    latent_codes: Union[torch.Tensor, np.ndarray],
    device: str = 'cpu'
) -> Dict[str, float]:
    """
    Convenience function to compute all coherence metrics.
    
    Args:
        latent_codes: Batch of latent vectors
        device: Device for computation
        
    Returns:
        Dictionary of metric names and values
    """
    if isinstance(latent_codes, np.ndarray):
        latent_codes = torch.from_numpy(latent_codes)
    
    latent_dim = latent_codes.shape[-1]
    analyzer = QuantumCoherenceAnalyzer(latent_dim=latent_dim, device=device)
    metrics = analyzer.analyze(latent_codes)
    
    return analyzer.to_dict(metrics)


if __name__ == "__main__":
    # Example usage
    print("Quantum Coherence Metrics Module")
    print("=" * 50)
    
    # Create sample latent codes
    batch_size = 64
    latent_dim = 32
    
    latent_codes = torch.randn(batch_size, latent_dim)
    
    # Initialize analyzer
    analyzer = QuantumCoherenceAnalyzer(latent_dim=latent_dim)
    
    # Compute metrics
    metrics = analyzer.analyze(latent_codes)
    
    print(f"L1 Coherence: {metrics.l1_coherence:.4f}")
    print(f"Relative Entropy Coherence: {metrics.relative_entropy_coherence:.4f}")
    print(f"Geometric Coherence: {metrics.geometric_coherence:.4f}")
    print(f"Purity: {metrics.purity:.4f}")
    print(f"Von Neumann Entropy: {metrics.von_neumann_entropy:.4f}")
    print(f"Participation Ratio: {metrics.participation_ratio:.4f}")
    print(f"Effective Dimension: {metrics.effective_dimension}")
    
    # Test golden ratio loss
    gr_loss = GoldenRatioLoss()
    loss = gr_loss(latent_codes)
    print(f"\nGolden Ratio Loss: {loss.item():.4f}")
    
    # Test mixed state regularizer
    ms_reg = MixedStateRegularizer(latent_dim=latent_dim)
    reg_losses = ms_reg(latent_codes)
    print(f"\nMixed State Regularization:")
    for key, value in reg_losses.items():
        print(f"  {key}: {value.item():.4f}")