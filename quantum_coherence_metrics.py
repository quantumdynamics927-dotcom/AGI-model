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
    # Enhanced metrics
    quantum_fisher_information: float = 0.0
    coherence_of_formation: float = 0.0
    skew_information: float = 0.0
    superposition_degree: float = 0.0
    entanglement_entropy: float = 0.0
    golden_ratio_alignment: float = 0.0
    phase_coherence: float = 0.0
    decoherence_rate: float = 0.0


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
            effective_dimension=self.compute_effective_dimension(latent_codes),
            # Enhanced metrics
            quantum_fisher_information=self.compute_quantum_fisher_information(density_matrix),
            coherence_of_formation=self.compute_coherence_of_formation(density_matrix),
            skew_information=self.compute_skew_information(density_matrix),
            superposition_degree=self.compute_superposition_degree(density_matrix),
            entanglement_entropy=self.compute_entanglement_entropy(density_matrix),
            golden_ratio_alignment=self.compute_golden_ratio_alignment(latent_codes),
            phase_coherence=self.compute_phase_coherence(latent_codes),
            decoherence_rate=self.compute_decoherence_rate(density_matrix)
        )
        
        return metrics
    
    def _compute_trace_distance(self, density_matrix: torch.Tensor) -> float:
        """Compute trace distance from maximally mixed state."""
        maximally_mixed = torch.eye(self.latent_dim, device=self.device) / self.latent_dim
        difference = density_matrix - maximally_mixed
        trace_distance = 0.5 * torch.trace(torch.sqrt(difference @ difference.T)).item()
        return trace_distance
    
    def compute_quantum_fisher_information(
        self,
        density_matrix: torch.Tensor,
        parameter: str = 'phase'
    ) -> float:
        """
        Compute quantum Fisher information.
        
        F_Q[ρ] = Tr(ρ L²)
        
        where L is the symmetric logarithmic derivative.
        
        Args:
            density_matrix: Quantum state density matrix
            parameter: Parameter type ('phase', 'amplitude')
            
        Returns:
            Quantum Fisher information
        """
        eigenvalues = torch.linalg.eigvalsh(density_matrix)
        eigenvalues = torch.clamp(eigenvalues, min=self.epsilon)
        
        # Compute Fisher information for phase estimation
        # F_Q ≈ 4 * Var(H) for Hamiltonian H
        # Simplified: use eigenvalue variance
        mean_eigenvalue = torch.mean(eigenvalues)
        variance = torch.mean((eigenvalues - mean_eigenvalue) ** 2)
        
        # Quantum Fisher information
        qfi = 4 * variance.item()
        
        return qfi
    
    def compute_coherence_of_formation(
        self,
        density_matrix: torch.Tensor
    ) -> float:
        """
        Compute coherence of formation.
        
        C_F(ρ) = min_{p_k, |ψ_k⟩} Σ_k p_k C(|ψ_k⟩)
        
        Approximated using entanglement of formation.
        
        Args:
            density_matrix: Quantum state density matrix
            
        Returns:
            Coherence of formation
        """
        # Use L1 coherence as lower bound
        l1 = self.l1_coherence(density_matrix)
        
        # Compute eigenvalues for upper bound
        eigenvalues = torch.linalg.eigvalsh(density_matrix)
        eigenvalues = torch.clamp(eigenvalues, min=self.epsilon)
        
        # Entropy-based upper bound
        entropy = -torch.sum(eigenvalues * torch.log2(eigenvalues + self.epsilon))
        
        # Approximate coherence of formation
        cof = (l1 + entropy.item() / np.log2(self.latent_dim)) / 2
        
        return cof
    
    def compute_skew_information(
        self,
        density_matrix: torch.Tensor
    ) -> float:
        """
        Compute skew information (Wigner-Yanase skew information).
        
        I(ρ, H) = -1/2 Tr([√ρ, H]²)
        
        Measures quantum uncertainty of observable H.
        
        Args:
            density_matrix: Quantum state density matrix
            
        Returns:
            Skew information
        """
        # Use identity operator as observable
        # Simplified: measure deviation from diagonal
        diag = torch.diag(torch.diag(density_matrix))
        
        # Compute sqrt of density matrix (approximate)
        eigenvalues, eigenvectors = torch.linalg.eigh(density_matrix)
        eigenvalues = torch.clamp(eigenvalues, min=self.epsilon)
        sqrt_eigenvalues = torch.sqrt(eigenvalues)
        sqrt_density = eigenvectors @ torch.diag(sqrt_eigenvalues) @ eigenvectors.T
        
        # Skew information approximation
        # I(ρ, H) ≈ Tr(ρ H²) - Tr(√ρ H √ρ H)
        # For identity: I ≈ Tr(ρ) - Tr(√ρ √ρ) = 0
        # Use off-diagonal contribution instead
        off_diag = density_matrix - diag
        skew = 0.5 * torch.trace(sqrt_density @ off_diag @ sqrt_density @ off_diag.T).item()
        
        return abs(skew)
    
    def compute_superposition_degree(
        self,
        density_matrix: torch.Tensor
    ) -> float:
        """
        Compute degree of superposition in the quantum state.
        
        Measures how much the state is in superposition vs. classical mixture.
        
        Args:
            density_matrix: Quantum state density matrix
            
        Returns:
            Superposition degree [0, 1]
        """
        # Off-diagonal elements indicate superposition
        off_diag = density_matrix - torch.diag(torch.diag(density_matrix))
        
        # Sum of absolute off-diagonal values
        superposition = torch.sum(torch.abs(off_diag)).item()
        
        # Normalize by maximum possible (n² - n for n×n matrix)
        max_superposition = self.latent_dim ** 2 - self.latent_dim
        
        if max_superposition > 0:
            return superposition / max_superposition
        return 0.0
    
    def compute_entanglement_entropy(
        self,
        density_matrix: torch.Tensor,
        subsystem_size: Optional[int] = None
    ) -> float:
        """
        Compute entanglement entropy for bipartition.
        
        S_A = -Tr(ρ_A log₂ ρ_A)
        
        Args:
            density_matrix: Quantum state density matrix
            subsystem_size: Size of subsystem A (default: half)
            
        Returns:
            Entanglement entropy
        """
        if subsystem_size is None:
            subsystem_size = self.latent_dim // 2
        
        # Partial trace over subsystem B
        # Simplified: use eigenvalue-based approximation
        eigenvalues = torch.linalg.eigvalsh(density_matrix)
        eigenvalues = torch.clamp(eigenvalues, min=self.epsilon)
        
        # Von Neumann entropy as entanglement proxy
        entropy = -torch.sum(eigenvalues * torch.log2(eigenvalues + self.epsilon))
        
        # Normalize by maximum possible entanglement
        max_entropy = np.log2(min(subsystem_size, self.latent_dim - subsystem_size))
        
        if max_entropy > 0:
            return entropy.item() / max_entropy
        return 0.0
    
    def compute_golden_ratio_alignment(
        self,
        latent_codes: torch.Tensor
    ) -> float:
        """
        Compute alignment with golden ratio patterns.
        
        Measures how well latent dimensions follow φ relationships.
        
        Args:
            latent_codes: Batch of latent vectors
            
        Returns:
            Golden ratio alignment score [0, 1]
        """
        phi = 1.618033988749895
        
        # Sort by magnitude
        sorted_latent, _ = torch.sort(torch.abs(latent_codes), dim=1, descending=True)
        
        # Compute consecutive ratios
        ratios = sorted_latent[:, 1:] / (sorted_latent[:, :-1] + 1e-10)
        
        # Distance from golden ratio
        phi_distance = torch.abs(ratios - phi)
        
        # Convert to alignment score (inverse distance)
        alignment = 1.0 / (1.0 + torch.mean(phi_distance).item())
        
        return alignment
    
    def compute_phase_coherence(
        self,
        latent_codes: torch.Tensor
    ) -> float:
        """
        Compute phase coherence in latent space.
        
        Measures coherence of phase relationships across dimensions.
        
        Args:
            latent_codes: Batch of latent vectors
            
        Returns:
            Phase coherence [0, 1]
        """
        # Compute phase from latent codes
        phases = torch.angle(torch.complex(latent_codes, torch.zeros_like(latent_codes)))
        
        # Phase variance
        phase_mean = torch.mean(phases, dim=0)
        phase_variance = torch.mean((phases - phase_mean) ** 2)
        
        # Coherence is inverse of variance
        coherence = 1.0 / (1.0 + phase_variance.item())
        
        return coherence
    
    def compute_decoherence_rate(
        self,
        density_matrix: torch.Tensor
    ) -> float:
        """
        Compute estimated decoherence rate.
        
        Based on off-diagonal decay in density matrix.
        
        Args:
            density_matrix: Quantum state density matrix
            
        Returns:
            Decoherence rate estimate
        """
        # Off-diagonal elements decay under decoherence
        diag = torch.diag(torch.diag(density_matrix))
        off_diag = density_matrix - diag
        
        # Measure off-diagonal magnitude
        off_diag_norm = torch.norm(off_diag, p='fro').item()
        diag_norm = torch.norm(diag, p='fro').item()
        
        # Decoherence rate approximation
        if diag_norm > 0:
            return 1.0 - (off_diag_norm / diag_norm)
        return 1.0
    
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
            'effective_dimension': metrics.effective_dimension,
            'quantum_fisher_information': metrics.quantum_fisher_information,
            'coherence_of_formation': metrics.coherence_of_formation,
            'skew_information': metrics.skew_information,
            'superposition_degree': metrics.superposition_degree,
            'entanglement_entropy': metrics.entanglement_entropy,
            'golden_ratio_alignment': metrics.golden_ratio_alignment,
            'phase_coherence': metrics.phase_coherence,
            'decoherence_rate': metrics.decoherence_rate
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
    
    def _positivity_regularization(self, density_matrix: torch.Tensor) -> torch.Tensor:
        """Ensure density matrix is positive semi-definite."""
        eigenvalues = torch.linalg.eigvalsh(density_matrix)
        negative_eigenvalues = torch.clamp(eigenvalues, max=0)
        loss = torch.sum(torch.abs(negative_eigenvalues))
        return loss
    
    def _hermiticity_regularization(self, density_matrix: torch.Tensor) -> torch.Tensor:
        """Ensure density matrix is Hermitian."""
        # For real matrices, Hermitian = symmetric
        diff = density_matrix - density_matrix.T
        loss = torch.norm(diff, p='fro')
        return loss
    
    def forward_enhanced(
        self,
        latent_codes: torch.Tensor,
        include_positivity: bool = True,
        include_hermiticity: bool = True
    ) -> Dict[str, torch.Tensor]:
        """
        Compute enhanced mixed state regularization losses.
        
        Args:
            latent_codes: Batch of latent vectors
            include_positivity: Include positivity constraint
            include_hermiticity: Include Hermiticity constraint
            
        Returns:
            Dictionary of loss components
        """
        # Compute density matrix
        density_matrix = self._compute_density_matrix(latent_codes)
        
        # Standard losses
        entropy_loss = self._entropy_regularization(density_matrix)
        purity_loss = self._purity_regularization(density_matrix)
        trace_loss = self._trace_regularization(density_matrix)
        
        # Enhanced losses
        losses = {
            'entropy': entropy_loss,
            'purity': purity_loss,
            'trace': trace_loss
        }
        
        if include_positivity:
            losses['positivity'] = self._positivity_regularization(density_matrix)
        
        if include_hermiticity:
            losses['hermiticity'] = self._hermiticity_regularization(density_matrix)
        
        # Total loss
        total_loss = (
            self.entropy_weight * entropy_loss +
            self.purity_weight * purity_loss +
            self.trace_weight * trace_loss
        )
        
        if include_positivity:
            total_loss = total_loss + 0.01 * losses['positivity']
        
        if include_hermiticity:
            total_loss = total_loss + 0.01 * losses['hermiticity']
        
        losses['total'] = total_loss
        
        return losses


class EnhancedGoldenRatioLoss(torch.nn.Module):
    """
    Enhanced golden ratio loss with multiple optimization strategies.
    
    Implements:
    - Ratio-based loss (consecutive dimension ratios)
    - Fibonacci-weighted loss
    - Spectral golden ratio loss
    - Phase alignment loss
    - Logarithmic golden ratio loss
    """
    
    def __init__(
        self,
        phi: float = 1.618033988749895,
        weight: float = 0.1,
        method: str = 'combined',
        adaptive_weight: bool = True
    ):
        """
        Initialize enhanced golden ratio loss.
        
        Args:
            phi: Golden ratio value
            weight: Base loss weight
            method: Loss method ('ratio', 'fibonacci', 'spectral', 'phase', 'combined')
            adaptive_weight: Whether to use adaptive weighting
        """
        super().__init__()
        self.phi = phi
        self.weight = weight
        self.method = method
        self.adaptive_weight = adaptive_weight
        
        # Fibonacci sequence for weighting
        self.register_buffer('fibonacci', self._generate_fibonacci(32))
    
    def _generate_fibonacci(self, n: int) -> torch.Tensor:
        """Generate Fibonacci sequence."""
        fib = [1, 1]
        for i in range(2, n):
            fib.append(fib[-1] + fib[-2])
        return torch.tensor(fib, dtype=torch.float32)
    
    def forward(self, latent_codes: torch.Tensor) -> torch.Tensor:
        """
        Compute enhanced golden ratio loss.
        
        Args:
            latent_codes: Batch of latent vectors [batch_size, latent_dim]
            
        Returns:
            Golden ratio loss value
        """
        if latent_codes.dim() == 1:
            latent_codes = latent_codes.unsqueeze(0)
        
        if self.method == 'ratio':
            loss = self._ratio_loss(latent_codes)
        elif self.method == 'fibonacci':
            loss = self._fibonacci_loss(latent_codes)
        elif self.method == 'spectral':
            loss = self._spectral_loss(latent_codes)
        elif self.method == 'phase':
            loss = self._phase_loss(latent_codes)
        elif self.method == 'combined':
            loss = self._combined_loss(latent_codes)
        else:
            loss = self._ratio_loss(latent_codes)
        
        # Adaptive weighting based on current alignment
        if self.adaptive_weight:
            alignment = self._compute_alignment(latent_codes)
            adaptive_weight = self.weight * (1.0 + (1.0 - alignment))
            return adaptive_weight * loss
        
        return self.weight * loss
    
    def _compute_alignment(self, latent_codes: torch.Tensor) -> float:
        """Compute current golden ratio alignment."""
        sorted_latent, _ = torch.sort(torch.abs(latent_codes), dim=1, descending=True)
        ratios = sorted_latent[:, 1:] / (sorted_latent[:, :-1] + 1e-10)
        phi_distance = torch.abs(ratios - self.phi)
        alignment = 1.0 / (1.0 + torch.mean(phi_distance).item())
        return alignment
    
    def _ratio_loss(self, latent_codes: torch.Tensor) -> torch.Tensor:
        """Ratio-based golden ratio loss."""
        sorted_latent, _ = torch.sort(torch.abs(latent_codes), dim=1, descending=True)
        ratios = sorted_latent[:, 1:] / (sorted_latent[:, :-1] + 1e-10)
        phi_distance = torch.abs(ratios - self.phi)
        return torch.mean(phi_distance)
    
    def _fibonacci_loss(self, latent_codes: torch.Tensor) -> torch.Tensor:
        """Fibonacci-weighted golden ratio loss."""
        batch_size, latent_dim = latent_codes.shape
        
        # Get Fibonacci weights
        fib = self.fibonacci[:latent_dim].to(latent_codes.device)
        fib_weights = fib / fib.sum()
        
        # Weighted latent codes
        weighted = latent_codes * fib_weights.unsqueeze(0)
        
        # Sort and compute ratios
        weighted_sorted, _ = torch.sort(torch.abs(weighted), dim=1, descending=True)
        ratios = weighted_sorted[:, 1:] / (weighted_sorted[:, :-1] + 1e-10)
        
        # Distance from golden ratio
        return torch.mean(torch.abs(ratios - self.phi))
    
    def _spectral_loss(self, latent_codes: torch.Tensor) -> torch.Tensor:
        """Spectral golden ratio loss based on eigenvalue distribution."""
        # Compute covariance matrix
        cov = torch.cov(latent_codes.T)
        
        # Get eigenvalues
        eigenvalues = torch.linalg.eigvalsh(cov)
        eigenvalues = torch.sort(eigenvalues, descending=True)[0]
        
        # Compute eigenvalue ratios
        ratios = eigenvalues[1:] / (eigenvalues[:-1] + 1e-10)
        
        # Distance from golden ratio
        return torch.mean(torch.abs(ratios - self.phi))
    
    def _phase_loss(self, latent_codes: torch.Tensor) -> torch.Tensor:
        """Phase-based golden ratio loss."""
        # Compute phase angles
        phases = torch.angle(torch.complex(latent_codes, torch.zeros_like(latent_codes)))
        
        # Sort phases
        sorted_phases, _ = torch.sort(phases, dim=1)
        
        # Compute phase differences
        phase_diffs = sorted_phases[:, 1:] - sorted_phases[:, :-1]
        
        # Target: golden ratio of 2π
        target_diff = 2 * np.pi / self.phi
        
        # Distance from target
        return torch.mean(torch.abs(phase_diffs - target_diff))
    
    def _combined_loss(self, latent_codes: torch.Tensor) -> torch.Tensor:
        """Combined golden ratio loss."""
        ratio_loss = self._ratio_loss(latent_codes)
        fib_loss = self._fibonacci_loss(latent_codes)
        spectral_loss = self._spectral_loss(latent_codes)
        
        # Weighted combination
        return 0.4 * ratio_loss + 0.3 * fib_loss + 0.3 * spectral_loss


class QuantumFidelityLoss(torch.nn.Module):
    """
    Loss function for quantum fidelity optimization.
    
    Encourages high fidelity between latent representations
    and target quantum states.
    """
    
    def __init__(
        self,
        target_fidelity: float = 0.95,
        weight: float = 0.1
    ):
        """
        Initialize quantum fidelity loss.
        
        Args:
            target_fidelity: Target fidelity value
            weight: Loss weight
        """
        super().__init__()
        self.target_fidelity = target_fidelity
        self.weight = weight
    
    def forward(
        self,
        latent_codes: torch.Tensor,
        target_codes: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """
        Compute quantum fidelity loss.
        
        Args:
            latent_codes: Batch of latent vectors
            target_codes: Optional target codes (uses identity if None)
            
        Returns:
            Fidelity loss value
        """
        if target_codes is None:
            # Use maximally entangled state as target
            target_codes = torch.ones_like(latent_codes) / np.sqrt(latent_codes.shape[-1])
        
        # Compute density matrices
        batch_size = latent_codes.shape[0]
        latent_dim = latent_codes.shape[-1]
        
        # Density matrix for latent codes
        rho = torch.zeros(latent_dim, latent_dim, device=latent_codes.device)
        for i in range(batch_size):
            z = latent_codes[i].unsqueeze(1)
            rho += z @ z.T
        rho /= batch_size
        
        # Density matrix for target
        sigma = torch.zeros(latent_dim, latent_dim, device=target_codes.device)
        for i in range(batch_size):
            t = target_codes[i].unsqueeze(1)
            sigma += t @ t.T
        sigma /= batch_size
        
        # Fidelity: F(ρ, σ) = (Tr(√(√ρ σ √ρ)))²
        # Simplified: F ≈ Tr(ρ σ) for pure states
        fidelity = torch.trace(rho @ sigma).clamp(min=0, max=1)
        
        # Loss: distance from target fidelity
        loss = torch.abs(fidelity - self.target_fidelity)
        
        return self.weight * loss


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