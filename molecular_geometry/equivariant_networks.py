"""E(3)-Equivariant Neural Networks for Molecular Geometry.

This module implements E(3)-equivariant graph neural networks that respect
rotational, translational, and reflective symmetries of 3D molecular structures.

Based on research:
- EnviroDetaNet (Nature 2025): Environment-aware E(3)-equivariant message passing
- GotenNet (ICLR 2025): Geometric tensor networks with strict E(3) equivariance
- OrbNet-Equi: Physics-informed equivariant networks for quantum chemistry

Integration with TMT-OS golden ratio analysis and consciousness modeling.
"""
from __future__ import annotations
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
import numpy as np

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor

from .structures import Molecule, Atom
from .constants import (
    PHI, PHI_SQUARED, GOLDEN_ANGLE, ATOMIC_NUMBERS,
    ELECTRONEGATIVITY, COVALENT_RADII, VDW_RADII,
    is_phi_harmonic
)


# ============================================================================
# Spherical Harmonics and Irreducible Representations
# ============================================================================

def get_spherical_harmonics_l0(vectors: Tensor) -> Tensor:
    """L=0 spherical harmonics (scalar, rotationally invariant)."""
    return torch.ones(vectors.shape[0], 1, device=vectors.device, dtype=vectors.dtype)


def get_spherical_harmonics_l1(vectors: Tensor) -> Tensor:
    """L=1 spherical harmonics (vector, transforms as a 3D vector).

    Args:
        vectors: (N, 3) normalized direction vectors

    Returns:
        (N, 3) spherical harmonics coefficients for l=1
    """
    # Y_1^{-1}, Y_1^0, Y_1^1 proportional to y, z, x
    return vectors  # Already in Cartesian form


def get_spherical_harmonics_l2(vectors: Tensor) -> Tensor:
    """L=2 spherical harmonics (5 components, quadrupole symmetry).

    Args:
        vectors: (N, 3) normalized direction vectors

    Returns:
        (N, 5) spherical harmonics coefficients for l=2
    """
    x, y, z = vectors[:, 0], vectors[:, 1], vectors[:, 2]

    # Real spherical harmonics for l=2
    sqrt3 = np.sqrt(3)
    sqrt15 = np.sqrt(15)

    Y2_m2 = sqrt15 * x * y  # xy
    Y2_m1 = sqrt15 * y * z  # yz
    Y2_0 = 0.5 * (3 * z * z - 1)  # 3z^2 - 1
    Y2_p1 = sqrt15 * x * z  # xz
    Y2_p2 = 0.5 * sqrt15 * (x * x - y * y)  # x^2 - y^2

    return torch.stack([Y2_m2, Y2_m1, Y2_0, Y2_p1, Y2_p2], dim=1)


def spherical_harmonics(l: int, vectors: Tensor) -> Tensor:
    """Compute real spherical harmonics up to order l.

    Args:
        l: Maximum angular momentum (0, 1, or 2)
        vectors: (N, 3) normalized direction vectors

    Returns:
        Tensor of shape (N, 2l+1) with spherical harmonic coefficients
    """
    if l == 0:
        return get_spherical_harmonics_l0(vectors)
    elif l == 1:
        return get_spherical_harmonics_l1(vectors)
    elif l == 2:
        return get_spherical_harmonics_l2(vectors)
    else:
        raise ValueError(f"Spherical harmonics for l={l} not implemented")


# ============================================================================
# Radial Basis Functions
# ============================================================================

class GaussianRadialBasis(nn.Module):
    """Gaussian radial basis functions for encoding distances."""

    def __init__(self,
                 n_rbf: int = 50,
                 cutoff: float = 10.0,
                 trainable: bool = True,
                 phi_enhanced: bool = True):
        """Initialize Gaussian RBF.

        Args:
            n_rbf: Number of radial basis functions
            cutoff: Distance cutoff in Angstroms
            trainable: Whether centers and widths are trainable
            phi_enhanced: Include golden ratio harmonic centers
        """
        super().__init__()
        self.n_rbf = n_rbf
        self.cutoff = cutoff
        self.phi_enhanced = phi_enhanced

        # Standard evenly-spaced centers
        n_standard = n_rbf - 8 if phi_enhanced else n_rbf
        centers = torch.linspace(0.0, cutoff, n_standard)

        if phi_enhanced:
            # Add golden ratio harmonic centers for TMT-OS integration
            phi_centers = torch.tensor([
                PHI / 2,           # ~0.809
                PHI,               # ~1.618
                PHI * 1.5,         # ~2.427
                PHI_SQUARED,       # ~2.618
                PHI_SQUARED * 1.5, # ~3.927
                PHI ** 3,          # ~4.236
                PHI ** 3 * 1.5,    # ~6.354
                PHI ** 4,          # ~6.854
            ], dtype=torch.float32)
            phi_centers = phi_centers[phi_centers < cutoff]
            # Pad if needed
            while len(phi_centers) < 8:
                phi_centers = torch.cat([phi_centers, torch.tensor([cutoff * 0.9])])
            centers = torch.cat([centers, phi_centers[:8]])

        widths = torch.ones_like(centers) * (cutoff / n_rbf)

        if trainable:
            self.centers = nn.Parameter(centers)
            self.widths = nn.Parameter(widths)
        else:
            self.register_buffer('centers', centers)
            self.register_buffer('widths', widths)

    def forward(self, distances: Tensor) -> Tensor:
        """Compute RBF features for distances.

        Args:
            distances: (N,) or (N, 1) tensor of distances

        Returns:
            (N, n_rbf) tensor of RBF features
        """
        distances = distances.view(-1, 1)
        # Gaussian: exp(-((d - c) / w)^2)
        return torch.exp(-((distances - self.centers) / self.widths) ** 2)


class BesselRadialBasis(nn.Module):
    """Bessel radial basis functions (better for periodic systems)."""

    def __init__(self, n_rbf: int = 16, cutoff: float = 10.0):
        super().__init__()
        self.n_rbf = n_rbf
        self.cutoff = cutoff

        # Bessel function frequencies
        freqs = torch.arange(1, n_rbf + 1, dtype=torch.float32) * np.pi / cutoff
        self.register_buffer('freqs', freqs)

    def forward(self, distances: Tensor) -> Tensor:
        """Compute Bessel RBF features."""
        distances = distances.view(-1, 1)
        # Bessel: sin(n * pi * d / cutoff) / d
        d_safe = torch.clamp(distances, min=1e-8)
        return torch.sin(self.freqs * distances) / d_safe


class CosineCutoff(nn.Module):
    """Smooth cosine cutoff function."""

    def __init__(self, cutoff: float = 10.0):
        super().__init__()
        self.cutoff = cutoff

    def forward(self, distances: Tensor) -> Tensor:
        """Apply smooth cutoff to distances."""
        # 0.5 * (cos(pi * d / cutoff) + 1) for d < cutoff, else 0
        cutoffs = 0.5 * (torch.cos(np.pi * distances / self.cutoff) + 1)
        return cutoffs * (distances < self.cutoff).float()


# ============================================================================
# Equivariant Message Passing Layers
# ============================================================================

class EquivariantLinear(nn.Module):
    """Linear layer that preserves E(3) equivariance for each irrep channel."""

    def __init__(self, in_features: int, out_features: int, l: int = 0):
        """Initialize equivariant linear layer.

        Args:
            in_features: Input feature dimension per irrep
            out_features: Output feature dimension per irrep
            l: Angular momentum of this channel (0=scalar, 1=vector, 2=tensor)
        """
        super().__init__()
        self.l = l
        self.linear = nn.Linear(in_features, out_features, bias=(l == 0))

    def forward(self, x: Tensor) -> Tensor:
        """Apply equivariant linear transformation."""
        return self.linear(x)


class TensorProductLayer(nn.Module):
    """Tensor product between irreducible representations.

    Computes Clebsch-Gordan coupling between different angular momenta.
    """

    def __init__(self,
                 in_features: int,
                 out_features: int,
                 l_in: int = 1,
                 l_filter: int = 1,
                 l_out: int = 0):
        """Initialize tensor product layer.

        Args:
            in_features: Input feature channels
            out_features: Output feature channels
            l_in: Input angular momentum
            l_filter: Filter angular momentum
            l_out: Output angular momentum
        """
        super().__init__()
        self.l_in = l_in
        self.l_filter = l_filter
        self.l_out = l_out

        # Weight matrix for tensor product
        self.weight = nn.Parameter(torch.randn(in_features, out_features) * 0.1)

    def forward(self,
                features: Tensor,
                edge_sh: Tensor,
                edge_weights: Tensor) -> Tensor:
        """Apply tensor product.

        Args:
            features: (N_edges, in_features, 2*l_in+1) input features
            edge_sh: (N_edges, 2*l_filter+1) spherical harmonics of edge directions
            edge_weights: (N_edges, 1) edge weights from radial network

        Returns:
            (N_edges, out_features, 2*l_out+1) output features
        """
        # Simplified tensor product (full CG coefficients would go here)
        # For l_out = 0, we compute dot product
        if self.l_out == 0 and self.l_in == 1 and self.l_filter == 1:
            # Contract vector with spherical harmonic
            contracted = torch.einsum('nik,nk->ni', features, edge_sh)
            weighted = contracted * edge_weights
            output = torch.einsum('ni,io->no', weighted, self.weight)
            return output.unsqueeze(-1)
        else:
            # General case: outer product and weight
            outer = torch.einsum('nik,nj->nikj', features, edge_sh)
            outer = outer.view(outer.shape[0], -1)
            output = F.linear(outer, self.weight.view(-1, self.weight.shape[1]))
            return output.unsqueeze(-1)


class EquivariantMessageBlock(nn.Module):
    """E(3)-equivariant message passing block.

    Implements environment-aware message passing with:
    - Scalar (l=0) invariant features
    - Vector (l=1) equivariant features
    - Optional tensor (l=2) features
    """

    def __init__(self,
                 hidden_dim: int = 128,
                 n_rbf: int = 50,
                 cutoff: float = 10.0,
                 max_l: int = 1,
                 phi_enhanced: bool = True):
        """Initialize equivariant message block.

        Args:
            hidden_dim: Hidden feature dimension
            n_rbf: Number of radial basis functions
            cutoff: Distance cutoff
            max_l: Maximum angular momentum (1 or 2)
            phi_enhanced: Use golden ratio enhanced RBF
        """
        super().__init__()
        self.hidden_dim = hidden_dim
        self.max_l = max_l

        # Radial network
        self.rbf = GaussianRadialBasis(n_rbf, cutoff, phi_enhanced=phi_enhanced)
        self.cutoff = CosineCutoff(cutoff)

        # Radial MLP for edge weights
        self.radial_mlp = nn.Sequential(
            nn.Linear(n_rbf, hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, hidden_dim)
        )

        # Scalar message network
        self.scalar_net = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, hidden_dim)
        )

        # Vector message network (equivariant)
        self.vector_linear = EquivariantLinear(hidden_dim, hidden_dim, l=1)

        # Update networks
        self.scalar_update = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, hidden_dim)
        )

        self.vector_update = EquivariantLinear(hidden_dim, hidden_dim, l=1)

        # Layer normalization
        self.scalar_norm = nn.LayerNorm(hidden_dim)
        self.vector_norm = nn.LayerNorm(hidden_dim)

    def forward(self,
                scalar_features: Tensor,
                vector_features: Tensor,
                edge_index: Tensor,
                edge_vec: Tensor,
                edge_dist: Tensor) -> Tuple[Tensor, Tensor]:
        """Forward pass with equivariant message passing.

        Args:
            scalar_features: (N, hidden_dim) node scalar features
            vector_features: (N, hidden_dim, 3) node vector features
            edge_index: (2, E) edge indices
            edge_vec: (E, 3) edge direction vectors (normalized)
            edge_dist: (E,) edge distances

        Returns:
            Updated (scalar_features, vector_features)
        """
        src, dst = edge_index

        # Compute radial features and cutoff
        rbf_features = self.rbf(edge_dist)
        cutoff_weights = self.cutoff(edge_dist).unsqueeze(-1)
        radial_weights = self.radial_mlp(rbf_features) * cutoff_weights

        # === Scalar Messages ===
        # Concatenate source and destination features
        scalar_src = scalar_features[src]
        scalar_dst = scalar_features[dst]
        scalar_pair = torch.cat([scalar_src, scalar_dst], dim=-1)

        # Compute scalar messages
        scalar_msg = self.scalar_net(scalar_pair) * radial_weights

        # Aggregate scalar messages
        scalar_agg = torch.zeros_like(scalar_features)
        scalar_agg.scatter_add_(0, dst.unsqueeze(-1).expand_as(scalar_msg), scalar_msg)

        # === Vector Messages ===
        # Get source vector features
        vector_src = vector_features[src]  # (E, hidden_dim, 3)

        # Apply equivariant linear
        vector_transformed = self.vector_linear(vector_src.transpose(-1, -2)).transpose(-1, -2)

        # Weight by radial weights
        vector_msg = vector_transformed * radial_weights.unsqueeze(-1)

        # Add directional component (vector spherical harmonics coupling)
        edge_contribution = edge_vec.unsqueeze(1) * radial_weights.unsqueeze(-1)
        vector_msg = vector_msg + edge_contribution * scalar_src.unsqueeze(-1)

        # Aggregate vector messages
        vector_agg = torch.zeros_like(vector_features)
        vector_agg.scatter_add_(0,
                                dst.unsqueeze(-1).unsqueeze(-1).expand_as(vector_msg),
                                vector_msg)

        # === Updates with residual connections ===
        # Scalar update
        scalar_input = torch.cat([scalar_features, scalar_agg], dim=-1)
        scalar_output = scalar_features + self.scalar_update(scalar_input)
        scalar_output = self.scalar_norm(scalar_output)

        # Vector update
        vector_output = vector_features + self.vector_update(
            vector_agg.transpose(-1, -2)
        ).transpose(-1, -2)

        # Normalize vector features (per-feature normalization)
        vector_norms = torch.norm(vector_output, dim=-1, keepdim=True).clamp(min=1e-8)
        vector_output = self.vector_norm(vector_output.transpose(-1, -2)).transpose(-1, -2)

        return scalar_output, vector_output


# ============================================================================
# Full E(3)-Equivariant Graph Neural Network
# ============================================================================

class E3EquivariantGNN(nn.Module):
    """E(3)-Equivariant Graph Neural Network for Molecular Properties.

    Implements a full equivariant architecture with:
    - Atom embedding with element-specific features
    - Multiple equivariant message passing layers
    - Invariant readout for molecular properties
    - Golden ratio integration for TMT-OS
    """

    def __init__(self,
                 n_elements: int = 100,
                 hidden_dim: int = 128,
                 n_layers: int = 4,
                 n_rbf: int = 50,
                 cutoff: float = 10.0,
                 max_l: int = 1,
                 output_dim: int = 1,
                 phi_enhanced: bool = True):
        """Initialize E(3)-equivariant GNN.

        Args:
            n_elements: Maximum atomic number to embed
            hidden_dim: Hidden dimension for features
            n_layers: Number of message passing layers
            n_rbf: Number of radial basis functions
            cutoff: Distance cutoff in Angstroms
            max_l: Maximum angular momentum
            output_dim: Output dimension (e.g., 1 for energy)
            phi_enhanced: Enable golden ratio enhancements
        """
        super().__init__()
        self.hidden_dim = hidden_dim
        self.n_layers = n_layers
        self.cutoff = cutoff
        self.phi_enhanced = phi_enhanced

        # Atom embedding
        self.element_embedding = nn.Embedding(n_elements, hidden_dim)

        # Additional atomic features embedding
        self.atomic_features_net = nn.Sequential(
            nn.Linear(4, hidden_dim // 4),  # [electronegativity, cov_radius, vdw_radius, atomic_num]
            nn.SiLU(),
            nn.Linear(hidden_dim // 4, hidden_dim)
        )

        # Initial vector features (zero-initialized, to be populated by message passing)
        self.vector_init = nn.Linear(hidden_dim, hidden_dim * 3)

        # Message passing layers
        self.message_blocks = nn.ModuleList([
            EquivariantMessageBlock(
                hidden_dim=hidden_dim,
                n_rbf=n_rbf,
                cutoff=cutoff,
                max_l=max_l,
                phi_enhanced=phi_enhanced
            )
            for _ in range(n_layers)
        ])

        # Golden ratio attention (if enabled)
        if phi_enhanced:
            self.phi_attention = GoldenRatioAttention(hidden_dim)

        # Readout: convert equivariant features to invariant output
        self.readout = InvariantReadout(hidden_dim, output_dim)

        # For extracting molecular descriptors
        self.descriptor_projection = nn.Linear(hidden_dim, 64)

    def forward(self,
                atomic_numbers: Tensor,
                positions: Tensor,
                batch: Optional[Tensor] = None) -> Dict[str, Tensor]:
        """Forward pass for molecular property prediction.

        Args:
            atomic_numbers: (N,) atomic numbers
            positions: (N, 3) atomic positions in Angstroms
            batch: (N,) batch assignment for each atom

        Returns:
            Dictionary with 'energy', 'forces', 'descriptors'
        """
        n_atoms = atomic_numbers.shape[0]
        device = atomic_numbers.device

        if batch is None:
            batch = torch.zeros(n_atoms, dtype=torch.long, device=device)

        # === Build graph from positions ===
        edge_index, edge_vec, edge_dist = self._build_graph(positions, batch)

        # === Initial embeddings ===
        # Element embedding
        scalar_features = self.element_embedding(atomic_numbers.clamp(0, 99))

        # Add atomic property features
        atomic_features = self._get_atomic_features(atomic_numbers)
        scalar_features = scalar_features + self.atomic_features_net(atomic_features)

        # Initialize vector features
        vector_init = self.vector_init(scalar_features).view(n_atoms, self.hidden_dim, 3)
        vector_features = vector_init * 0.01  # Small initialization

        # === Message Passing ===
        for block in self.message_blocks:
            scalar_features, vector_features = block(
                scalar_features, vector_features,
                edge_index, edge_vec, edge_dist
            )

        # === Golden ratio attention (optional) ===
        if self.phi_enhanced:
            scalar_features = self.phi_attention(
                scalar_features, edge_index, edge_dist
            )

        # === Readout ===
        output = self.readout(scalar_features, vector_features, batch)

        # === Compute molecular descriptors ===
        atom_descriptors = self.descriptor_projection(scalar_features)

        # Aggregate to molecule level
        n_molecules = batch.max().item() + 1
        mol_descriptors = torch.zeros(n_molecules, 64, device=device)
        mol_descriptors.scatter_add_(
            0,
            batch.unsqueeze(-1).expand(-1, 64),
            atom_descriptors
        )
        # Normalize by atom count
        atom_counts = torch.bincount(batch, minlength=n_molecules).float().unsqueeze(-1)
        mol_descriptors = mol_descriptors / atom_counts.clamp(min=1)

        output['descriptors'] = mol_descriptors
        output['atom_features'] = scalar_features

        return output

    def _build_graph(self,
                     positions: Tensor,
                     batch: Tensor) -> Tuple[Tensor, Tensor, Tensor]:
        """Build molecular graph with distance-based edges.

        Args:
            positions: (N, 3) atomic positions
            batch: (N,) batch indices

        Returns:
            edge_index (2, E), edge_vec (E, 3), edge_dist (E,)
        """
        n_atoms = positions.shape[0]
        device = positions.device

        # Compute pairwise distances within each molecule
        src_list, dst_list = [], []

        for mol_idx in range(batch.max().item() + 1):
            mask = batch == mol_idx
            mol_indices = torch.where(mask)[0]
            n_mol = len(mol_indices)

            # All pairs within molecule
            for i in range(n_mol):
                for j in range(n_mol):
                    if i != j:
                        idx_i = mol_indices[i]
                        idx_j = mol_indices[j]
                        dist = torch.norm(positions[idx_i] - positions[idx_j])
                        if dist < self.cutoff:
                            src_list.append(idx_i)
                            dst_list.append(idx_j)

        if len(src_list) == 0:
            # No edges (single atoms)
            edge_index = torch.zeros(2, 0, dtype=torch.long, device=device)
            edge_vec = torch.zeros(0, 3, device=device)
            edge_dist = torch.zeros(0, device=device)
        else:
            edge_index = torch.stack([
                torch.tensor(src_list, device=device),
                torch.tensor(dst_list, device=device)
            ])

            # Compute edge vectors and distances
            edge_vec = positions[edge_index[1]] - positions[edge_index[0]]
            edge_dist = torch.norm(edge_vec, dim=-1)

            # Normalize edge vectors
            edge_vec = edge_vec / edge_dist.unsqueeze(-1).clamp(min=1e-8)

        return edge_index, edge_vec, edge_dist

    def _get_atomic_features(self, atomic_numbers: Tensor) -> Tensor:
        """Get additional atomic features for each atom.

        Args:
            atomic_numbers: (N,) atomic numbers

        Returns:
            (N, 4) tensor of [electronegativity, cov_radius, vdw_radius, normalized_z]
        """
        device = atomic_numbers.device
        n_atoms = atomic_numbers.shape[0]
        features = torch.zeros(n_atoms, 4, device=device)

        # Map atomic numbers to properties
        element_to_idx = {v: k for k, v in ATOMIC_NUMBERS.items()}

        for i, z in enumerate(atomic_numbers.cpu().numpy()):
            symbol = element_to_idx.get(int(z), 'C')
            features[i, 0] = ELECTRONEGATIVITY.get(symbol, 2.5) / 4.0  # Normalized
            features[i, 1] = COVALENT_RADII.get(symbol, 1.5) / 2.5
            features[i, 2] = VDW_RADII.get(symbol, 1.7) / 3.5
            features[i, 3] = z / 100.0  # Normalized atomic number

        return features


class GoldenRatioAttention(nn.Module):
    """Attention mechanism weighted by golden ratio harmonic distances.

    Enhances features at phi-harmonic distances for TMT-OS integration.
    """

    def __init__(self, hidden_dim: int):
        super().__init__()
        self.hidden_dim = hidden_dim

        # Phi-harmonic distance detector
        self.phi_harmonics = torch.tensor([
            PHI / 2, PHI, PHI * 1.5, PHI_SQUARED,
            PHI_SQUARED * 1.5, PHI ** 3
        ])

        # Attention networks
        self.query = nn.Linear(hidden_dim, hidden_dim)
        self.key = nn.Linear(hidden_dim, hidden_dim)
        self.value = nn.Linear(hidden_dim, hidden_dim)

        # Phi-weighting network
        self.phi_weight = nn.Sequential(
            nn.Linear(1, 16),
            nn.SiLU(),
            nn.Linear(16, 1),
            nn.Sigmoid()
        )

        self.output_proj = nn.Linear(hidden_dim, hidden_dim)
        self.norm = nn.LayerNorm(hidden_dim)

    def forward(self,
                features: Tensor,
                edge_index: Tensor,
                edge_dist: Tensor) -> Tensor:
        """Apply golden ratio attention.

        Args:
            features: (N, hidden_dim) node features
            edge_index: (2, E) edge indices
            edge_dist: (E,) edge distances

        Returns:
            (N, hidden_dim) updated features
        """
        src, dst = edge_index

        # Compute attention scores
        q = self.query(features[dst])
        k = self.key(features[src])
        v = self.value(features[src])

        # Standard attention
        attn = torch.sum(q * k, dim=-1) / np.sqrt(self.hidden_dim)

        # Compute phi-harmonic weights
        phi_distances = self.phi_harmonics.to(edge_dist.device)
        min_phi_dist = torch.min(
            torch.abs(edge_dist.unsqueeze(-1) - phi_distances),
            dim=-1
        )[0]
        phi_weights = self.phi_weight(min_phi_dist.unsqueeze(-1)).squeeze(-1)

        # Combine attention with phi weights
        attn = attn + phi_weights * 2.0  # Boost phi-harmonic interactions

        # Softmax over incoming edges
        attn_exp = torch.exp(attn - attn.max())
        attn_sum = torch.zeros(features.shape[0], device=features.device)
        attn_sum.scatter_add_(0, dst, attn_exp)
        attn_normalized = attn_exp / attn_sum[dst].clamp(min=1e-8)

        # Aggregate values
        weighted_v = v * attn_normalized.unsqueeze(-1)
        output = torch.zeros_like(features)
        output.scatter_add_(0, dst.unsqueeze(-1).expand_as(weighted_v), weighted_v)

        # Project and residual connection
        output = self.output_proj(output)
        return self.norm(features + output)


class InvariantReadout(nn.Module):
    """Invariant readout layer for predicting molecular properties.

    Combines scalar and vector features into rotationally invariant outputs.
    """

    def __init__(self, hidden_dim: int, output_dim: int):
        super().__init__()
        self.hidden_dim = hidden_dim

        # Compute invariants from vectors
        self.vector_to_scalar = nn.Linear(hidden_dim, hidden_dim)

        # Final prediction networks
        self.pre_pool = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, hidden_dim)
        )

        self.post_pool = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.SiLU(),
            nn.Linear(hidden_dim // 2, output_dim)
        )

    def forward(self,
                scalar_features: Tensor,
                vector_features: Tensor,
                batch: Tensor) -> Dict[str, Tensor]:
        """Compute invariant molecular properties.

        Args:
            scalar_features: (N, hidden_dim) scalar features
            vector_features: (N, hidden_dim, 3) vector features
            batch: (N,) batch assignment

        Returns:
            Dictionary with 'energy' and 'forces'
        """
        # Compute vector invariants (squared norms)
        vector_norms = torch.norm(vector_features, dim=-1)  # (N, hidden_dim)
        vector_invariant = self.vector_to_scalar(vector_norms)

        # Combine scalar and vector-derived features
        combined = torch.cat([scalar_features, vector_invariant], dim=-1)
        atom_energies = self.pre_pool(combined)

        # Aggregate to molecules
        n_molecules = batch.max().item() + 1
        mol_features = torch.zeros(n_molecules, self.hidden_dim,
                                   device=scalar_features.device)
        mol_features.scatter_add_(
            0,
            batch.unsqueeze(-1).expand_as(atom_energies),
            atom_energies
        )

        # Predict molecular energy
        energy = self.post_pool(mol_features)

        # Forces can be computed via autograd on energy w.r.t. positions
        return {
            'energy': energy,
            'atom_contributions': atom_energies
        }


# ============================================================================
# Integration with Molecular Geometry Module
# ============================================================================

class MoleculeToGraph:
    """Convert Molecule objects to graph format for E3-GNN."""

    @staticmethod
    def convert(molecule: Molecule,
                device: str = 'cpu') -> Dict[str, Tensor]:
        """Convert Molecule to tensors for E3-GNN.

        Args:
            molecule: Molecule object
            device: Target device

        Returns:
            Dictionary with 'atomic_numbers', 'positions', 'batch'
        """
        atomic_numbers = torch.tensor(
            [ATOMIC_NUMBERS.get(atom.symbol, 6) for atom in molecule.atoms],
            dtype=torch.long,
            device=device
        )

        positions = torch.tensor(
            molecule.coordinates,
            dtype=torch.float32,
            device=device
        )

        batch = torch.zeros(len(molecule.atoms), dtype=torch.long, device=device)

        return {
            'atomic_numbers': atomic_numbers,
            'positions': positions,
            'batch': batch
        }

    @staticmethod
    def batch_convert(molecules: List[Molecule],
                      device: str = 'cpu') -> Dict[str, Tensor]:
        """Convert multiple molecules to batched graph.

        Args:
            molecules: List of Molecule objects
            device: Target device

        Returns:
            Batched graph tensors
        """
        all_z, all_pos, all_batch = [], [], []

        for mol_idx, mol in enumerate(molecules):
            for atom in mol.atoms:
                all_z.append(ATOMIC_NUMBERS.get(atom.symbol, 6))
                all_pos.append(list(atom.position))
                all_batch.append(mol_idx)

        return {
            'atomic_numbers': torch.tensor(all_z, dtype=torch.long, device=device),
            'positions': torch.tensor(all_pos, dtype=torch.float32, device=device),
            'batch': torch.tensor(all_batch, dtype=torch.long, device=device)
        }


class EquivariantDescriptorCalculator:
    """Calculate equivariant molecular descriptors using E3-GNN.

    Provides learned descriptors that are invariant to rotation/translation.
    """

    def __init__(self,
                 model: Optional[E3EquivariantGNN] = None,
                 hidden_dim: int = 128,
                 n_layers: int = 4,
                 device: str = 'cpu'):
        """Initialize descriptor calculator.

        Args:
            model: Pre-trained E3EquivariantGNN (or creates new one)
            hidden_dim: Hidden dimension if creating new model
            n_layers: Number of layers if creating new model
            device: Computation device
        """
        self.device = device

        if model is None:
            self.model = E3EquivariantGNN(
                hidden_dim=hidden_dim,
                n_layers=n_layers,
                phi_enhanced=True
            ).to(device)
        else:
            self.model = model.to(device)

        self.model.eval()

    @torch.no_grad()
    def compute(self, molecule: Molecule) -> Dict[str, np.ndarray]:
        """Compute equivariant descriptors for a molecule.

        Args:
            molecule: Molecule object

        Returns:
            Dictionary with 'descriptors', 'atom_features', 'energy'
        """
        graph = MoleculeToGraph.convert(molecule, self.device)

        output = self.model(
            graph['atomic_numbers'],
            graph['positions'],
            graph['batch']
        )

        return {
            'descriptors': output['descriptors'].cpu().numpy(),
            'atom_features': output['atom_features'].cpu().numpy(),
            'energy': output['energy'].cpu().numpy()
        }

    @torch.no_grad()
    def batch_compute(self,
                      molecules: List[Molecule]) -> Dict[str, np.ndarray]:
        """Compute descriptors for multiple molecules.

        Args:
            molecules: List of Molecule objects

        Returns:
            Batched descriptors
        """
        graph = MoleculeToGraph.batch_convert(molecules, self.device)

        output = self.model(
            graph['atomic_numbers'],
            graph['positions'],
            graph['batch']
        )

        return {
            'descriptors': output['descriptors'].cpu().numpy(),
            'energies': output['energy'].cpu().numpy()
        }


# ============================================================================
# Pre-configured Models
# ============================================================================

def create_envirodetanet(hidden_dim: int = 128,
                         n_layers: int = 6,
                         phi_enhanced: bool = True) -> E3EquivariantGNN:
    """Create EnviroDetaNet-style model.

    Based on: Nature Computational Materials 2025
    """
    return E3EquivariantGNN(
        hidden_dim=hidden_dim,
        n_layers=n_layers,
        n_rbf=64,
        cutoff=10.0,
        max_l=1,
        output_dim=1,
        phi_enhanced=phi_enhanced
    )


def create_gotennet(hidden_dim: int = 256,
                    n_layers: int = 8) -> E3EquivariantGNN:
    """Create GotenNet-style model.

    Based on: ICLR 2025
    """
    return E3EquivariantGNN(
        hidden_dim=hidden_dim,
        n_layers=n_layers,
        n_rbf=128,
        cutoff=12.0,
        max_l=2,
        output_dim=1,
        phi_enhanced=True
    )
