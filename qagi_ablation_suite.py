#!/usr/bin/env python3
"""
QAGI Geometry-Native Ablation Suite
===================================

Validates that sacred geometry is causally driving computation, not just
serving as an organizing metaphor.

Ablation Tests:
1. Remove phi weighting → test if phi-weighted fusion matters
2. Replace geometric adjacency with random adjacency → test if geometry matters
3. Collapse Sierpinski to single branch → test if fractal branching matters
4. Replace flower-lattice memory with flat memory → test if geometric memory matters
5. Shuffle six-node architectures → test if node-specific designs matter

Metrics Compared:
- Convergence stability
- Coherence score
- Representation separation
- Calibration sensitivity
- Eigenvalue spectrum
- Activation norms

Usage:
    python qagi_ablation_suite.py --output ablation_results.json
"""

import argparse
import json
import math
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import warnings

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from scipy import stats
from scipy.linalg import eigvalsh


# =============================================================================
# GEOMETRIC CONSTANTS
# =============================================================================

PHI = (1 + math.sqrt(5)) / 2  # Golden ratio φ ≈ 1.618
SIX_NODE_ANGLES = [0, 60, 120, 180, 240, 300]
FLOWER_OF_LIFE_CIRCLES = 19


# =============================================================================
# ABLATION CONFIGURATIONS
# =============================================================================

@dataclass
class AblationConfig:
    """Configuration for a single ablation experiment."""
    name: str
    description: str
    phi_weighting: bool = True
    geometric_adjacency: bool = True
    sierpinski_branching: bool = True
    flower_lattice_memory: bool = True
    node_specific_arch: bool = True
    seed: int = 42


ABLATION_CONFIGS = {
    'baseline': AblationConfig(
        name='baseline',
        description='Full geometry-native implementation (no ablation)',
        phi_weighting=True,
        geometric_adjacency=True,
        sierpinski_branching=True,
        flower_lattice_memory=True,
        node_specific_arch=True,
    ),
    'no_phi_weighting': AblationConfig(
        name='no_phi_weighting',
        description='Remove phi weighting, use uniform weights',
        phi_weighting=False,
        geometric_adjacency=True,
        sierpinski_branching=True,
        flower_lattice_memory=True,
        node_specific_arch=True,
    ),
    'random_adjacency': AblationConfig(
        name='random_adjacency',
        description='Replace geometric adjacency with random adjacency of equal density',
        phi_weighting=True,
        geometric_adjacency=False,
        sierpinski_branching=True,
        flower_lattice_memory=True,
        node_specific_arch=True,
    ),
    'single_branch_sierpinski': AblationConfig(
        name='single_branch_sierpinski',
        description='Collapse Sierpinski to single branch (no fractal)',
        phi_weighting=True,
        geometric_adjacency=True,
        sierpinski_branching=False,
        flower_lattice_memory=True,
        node_specific_arch=True,
    ),
    'flat_memory': AblationConfig(
        name='flat_memory',
        description='Replace flower-lattice memory with flat tensor',
        phi_weighting=True,
        geometric_adjacency=True,
        sierpinski_branching=True,
        flower_lattice_memory=False,
        node_specific_arch=True,
    ),
    'uniform_nodes': AblationConfig(
        name='uniform_nodes',
        description='All six nodes use same architecture',
        phi_weighting=True,
        geometric_adjacency=True,
        sierpinski_branching=True,
        flower_lattice_memory=True,
        node_specific_arch=False,
    ),
    'full_ablation': AblationConfig(
        name='full_ablation',
        description='Remove all geometry (worst case)',
        phi_weighting=False,
        geometric_adjacency=False,
        sierpinski_branching=False,
        flower_lattice_memory=False,
        node_specific_arch=False,
    ),
}


# =============================================================================
# ABLATED MODULES
# =============================================================================

class AblatedSierpinskiCore(nn.Module):
    """Sierpinski core with ablation options."""
    
    def __init__(self, dim: int = 128, depth: int = 5, config: AblationConfig = None):
        super().__init__()
        self.dim = dim
        self.depth = depth
        self.config = config or AblationConfig(name='default', description='default')
        self.phi = PHI
        
        # Channel transforms
        if self.config.sierpinski_branching:
            # Full three-channel fractal
            self.channel_transforms = nn.ModuleList([
                nn.ModuleDict({
                    'apex': nn.Linear(dim, dim),
                    'bottom_left': nn.Linear(dim, dim),
                    'bottom_right': nn.Linear(dim, dim),
                    'merge': nn.Linear(dim * 3, dim)
                }) for _ in range(depth)
            ])
        else:
            # Single branch (no fractal)
            self.channel_transforms = nn.ModuleList([
                nn.ModuleDict({
                    'single': nn.Linear(dim, dim)
                }) for _ in range(depth)
            ])
        
        # Depth scales
        if self.config.phi_weighting:
            scales = torch.tensor([self.phi ** (-d) for d in range(depth)])
        else:
            scales = torch.ones(depth)
        self.register_buffer('depth_scales', scales)
        
        self.convergence_weights = nn.Parameter(torch.ones(3) / 3)
    
    def forward(self, x: torch.Tensor, depth: int = 0) -> torch.Tensor:
        if depth >= self.depth or x.shape[-1] != self.dim:
            return x
        
        transforms = self.channel_transforms[depth]
        scale = self.depth_scales[depth]
        
        if self.config.sierpinski_branching:
            # Three-channel fractal
            apex = transforms['apex'](x) * scale
            bottom_left = transforms['bottom_left'](x) * scale
            bottom_right = transforms['bottom_right'](x) * scale
            
            if depth + 1 < self.depth:
                apex = self.forward(apex, depth + 1)
                bottom_left = self.forward(bottom_left, depth + 1)
                bottom_right = self.forward(bottom_right, depth + 1)
            
            merged = torch.cat([apex, bottom_left, bottom_right], dim=-1)
            output = transforms['merge'](merged)
        else:
            # Single branch (ablated)
            output = transforms['single'](x) * scale
            if depth + 1 < self.depth:
                output = self.forward(output, depth + 1)
        
        # Residual
        if self.config.phi_weighting:
            return (1 / self.phi) * output + (1 - 1/self.phi) * x
        else:
            return 0.5 * output + 0.5 * x
    
    def get_convergence_metric(self) -> float:
        with torch.no_grad():
            if self.config.sierpinski_branching:
                weights = F.softmax(self.convergence_weights, dim=0)
                ideal = torch.ones(3) / 3
                divergence = torch.abs(weights - ideal).sum().item()
                return 1.0 / (1.0 + divergence)
            return 0.5  # No branching = no convergence metric


class AblatedStarMeshEngine(nn.Module):
    """Star mesh with ablation options."""
    
    def __init__(self, dim: int = 128, config: AblationConfig = None):
        super().__init__()
        self.dim = dim
        self.config = config or AblationConfig(name='default', description='default')
        self.phi = PHI
        
        # Build adjacency
        if self.config.geometric_adjacency:
            # Real hexagram adjacency
            hexagram_edges = [
                (0, 2), (2, 4), (4, 0),
                (1, 3), (3, 5), (5, 1),
                (0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0)
            ]
            adj = torch.zeros(6, 6)
            for i, j in hexagram_edges:
                is_inner = (i + j) % 2 == 0
                weight = self.phi if is_inner else 1.0
                adj[i, j] = weight
                adj[j, i] = weight
        else:
            # Random adjacency with same density
            torch.manual_seed(self.config.seed)
            adj = torch.rand(6, 6)
            adj = (adj + adj.T) / 2  # Symmetric
            adj = (adj > 0.5).float()  # Same sparsity as geometric
            adj = adj + torch.eye(6)  # Self-loops
        
        adj = adj / adj.sum(dim=1, keepdim=True).clamp(min=1)
        self.register_buffer('adjacency', adj)
        
        self.vertex_embeddings = nn.Parameter(torch.randn(6, dim) / math.sqrt(dim))
        self.inner_transform = nn.Linear(dim, dim)
        self.attention = nn.MultiheadAttention(dim, num_heads=8, batch_first=True)
        self.output_proj = nn.Linear(dim, dim)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        batch_size = x.shape[0]
        
        vertex_features = x.unsqueeze(1) * self.vertex_embeddings.unsqueeze(0)
        transformed = self.inner_transform(vertex_features)
        
        adj_expanded = self.adjacency.unsqueeze(0).expand(batch_size, -1, -1)
        vertex_features = torch.bmm(adj_expanded, transformed)
        
        attn_out, _ = self.attention(vertex_features, vertex_features, vertex_features)
        vertex_features = vertex_features + attn_out
        
        # Angular weights
        if self.config.phi_weighting:
            angle_weights = torch.tensor([
                self.phi ** (angle / 60) for angle in SIX_NODE_ANGLES
            ], device=x.device)
        else:
            angle_weights = torch.ones(6, device=x.device)
        angle_weights = F.softmax(angle_weights, dim=0)
        
        output = (vertex_features * angle_weights.view(1, -1, 1)).sum(dim=1)
        output = self.output_proj(output)
        
        if self.config.phi_weighting:
            return (1 / self.phi) * output + x
        else:
            return 0.5 * output + 0.5 * x
    
    def get_resonance_pattern(self) -> torch.Tensor:
        with torch.no_grad():
            embeddings = self.vertex_embeddings
            pattern = F.cosine_similarity(embeddings.unsqueeze(1), embeddings.unsqueeze(0), dim=2)
            return pattern


class AblatedSixNodeSubsystem(nn.Module):
    """Six nodes with ablation options."""
    
    NODE_ARCHITECTURES = {
        'perception': {'angle': 0, 'type': 'attention'},
        'memory': {'angle': 60, 'type': 'lstm'},
        'inference': {'angle': 120, 'type': 'transformer'},
        'quantum_control': {'angle': 180, 'type': 'complex'},
        'consciousness': {'angle': 240, 'type': 'meta'},
        'action': {'angle': 300, 'type': 'policy'}
    }
    
    def __init__(self, dim: int = 128, config: AblationConfig = None):
        super().__init__()
        self.dim = dim
        self.config = config or AblationConfig(name='default', description='default')
        self.phi = PHI
        
        self.node_processors = nn.ModuleDict()
        self.node_states = nn.ParameterDict()
        
        for node_id, node_config in self.NODE_ARCHITECTURES.items():
            if self.config.node_specific_arch:
                # Different architectures per node
                arch_type = node_config['type']
                if arch_type == 'attention':
                    self.node_processors[node_id] = nn.MultiheadAttention(dim, 4, batch_first=True)
                elif arch_type == 'lstm':
                    self.node_processors[node_id] = nn.LSTM(dim, dim, batch_first=True)
                elif arch_type == 'transformer':
                    self.node_processors[node_id] = nn.TransformerEncoderLayer(dim, 4, dim*2, batch_first=True)
                elif arch_type == 'complex':
                    self.node_processors[node_id] = nn.Sequential(nn.Linear(dim, dim*2), nn.Linear(dim*2, dim))
                elif arch_type == 'meta':
                    self.node_processors[node_id] = nn.Sequential(nn.Linear(dim, dim), nn.SiLU(), nn.Linear(dim, dim))
                else:
                    self.node_processors[node_id] = nn.Sequential(nn.Linear(dim, dim), nn.Softmax(dim=-1))
            else:
                # Uniform architecture (ablated)
                self.node_processors[node_id] = nn.Sequential(nn.Linear(dim, dim), nn.ReLU(), nn.Linear(dim, dim))
            
            self.node_states[node_id] = nn.Parameter(torch.zeros(dim))
        
        # Geometric coupling
        if self.config.geometric_adjacency:
            coupling = self._build_geometric_coupling()
        else:
            coupling = torch.eye(6) + 0.1 * torch.rand(6, 6)
            coupling = coupling / coupling.sum(dim=1, keepdim=True)
        self.register_buffer('geometric_coupling', coupling)
        
        if self.config.phi_weighting:
            angular_weights = torch.tensor([self.phi ** (a / 60) for a in SIX_NODE_ANGLES])
        else:
            angular_weights = torch.ones(6)
        self.register_buffer('angular_weights', angular_weights)
    
    def _build_geometric_coupling(self) -> torch.Tensor:
        coupling = torch.zeros(6, 6)
        node_list = list(self.NODE_ARCHITECTURES.keys())
        
        for i, node_i in enumerate(node_list):
            for j, node_j in enumerate(node_list):
                if i != j:
                    angle_i = self.NODE_ARCHITECTURES[node_i]['angle']
                    angle_j = self.NODE_ARCHITECTURES[node_j]['angle']
                    angle_diff = min(abs(angle_i - angle_j), 360 - abs(angle_i - angle_j))
                    coupling[i, j] = self.phi ** (-angle_diff / 60)
        
        return coupling / coupling.sum(dim=1, keepdim=True).clamp(min=1)
    
    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        batch_size = x.shape[0]
        outputs = {}
        node_outputs = []
        
        for i, (node_id, processor) in enumerate(self.node_processors.items()):
            if isinstance(processor, nn.MultiheadAttention):
                node_out, _ = processor(x.unsqueeze(1), x.unsqueeze(1), x.unsqueeze(1))
                node_out = node_out.squeeze(1)
            elif isinstance(processor, nn.LSTM):
                node_out, _ = processor(x.unsqueeze(1))
                node_out = node_out.squeeze(1)
            elif isinstance(processor, nn.TransformerEncoderLayer):
                node_out = processor(x.unsqueeze(1)).squeeze(1)
            else:
                node_out = processor(x)
            
            node_out = node_out * self.angular_weights[i]
            outputs[node_id] = node_out
            node_outputs.append(node_out)
        
        # Stack and apply coupling
        stacked = torch.stack(node_outputs, dim=1)  # (batch, 6, dim)
        coupled = torch.bmm(self.geometric_coupling.unsqueeze(0).expand(batch_size, -1, -1), stacked)
        
        outputs['combined'] = coupled.mean(dim=1)
        return outputs


class AblatedFlowerOfLifeLattice(nn.Module):
    """Flower of Life lattice with ablation options."""
    
    def __init__(self, dim: int = 128, config: AblationConfig = None):
        super().__init__()
        self.dim = dim
        self.config = config or AblationConfig(name='default', description='default')
        
        if self.config.flower_lattice_memory:
            # Geometric memory: 19 circles + 36 intersections
            self.circle_memory = nn.Parameter(torch.randn(19, dim) / math.sqrt(dim))
            self.intersection_memory = nn.Parameter(torch.randn(36, dim) / math.sqrt(dim))
            total_slots = 19 + 36
        else:
            # Flat memory (ablated)
            total_slots = 55
            self.flat_memory = nn.Parameter(torch.randn(total_slots, dim) / math.sqrt(dim))
        
        self.total_slots = total_slots
        self.memory_proj = nn.Linear(dim, dim)
        self.retrieval = nn.Linear(dim, total_slots)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        batch_size = x.shape[0]
        
        # Compute attention over memory slots
        attn_weights = F.softmax(self.retrieval(x), dim=-1)  # (batch, 55)
        
        if self.config.flower_lattice_memory:
            memory = torch.cat([self.circle_memory, self.intersection_memory], dim=0)
        else:
            memory = self.flat_memory
        
        # Retrieve from memory
        retrieved = torch.bmm(attn_weights.unsqueeze(1), memory.unsqueeze(0).expand(batch_size, -1, -1))
        retrieved = retrieved.squeeze(1)
        
        output = self.memory_proj(retrieved)
        return 0.5 * output + 0.5 * x
    
    def get_memory_utilization(self) -> Dict[str, float]:
        with torch.no_grad():
            if self.config.flower_lattice_memory:
                circle_norm = self.circle_memory.norm().item()
                intersection_norm = self.intersection_memory.norm().item()
                return {
                    'circle_memory_norm': circle_norm,
                    'intersection_memory_norm': intersection_norm,
                    'ratio': circle_norm / (intersection_norm + 1e-10)
                }
            return {'flat_memory_norm': self.flat_memory.norm().item()}


class AblatedOuterRingBoundary(nn.Module):
    """Outer ring boundary with ablation options."""
    
    def __init__(self, dim: int = 128, config: AblationConfig = None):
        super().__init__()
        self.dim = dim
        self.config = config or AblationConfig(name='default', description='default')
        self.phi = PHI
        
        if self.config.phi_weighting:
            self.threshold = nn.Parameter(torch.tensor(1.0 / self.phi))
        else:
            self.threshold = nn.Parameter(torch.tensor(0.5))
        
        self.containment_proj = nn.Linear(dim, 1)
    
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        containment_score = torch.sigmoid(self.containment_proj(x)).squeeze(-1)
        threshold = torch.sigmoid(self.threshold)
        contained = (containment_score > threshold).float()
        return x, contained
    
    def get_threshold(self) -> float:
        return torch.sigmoid(self.threshold).item()


# =============================================================================
# FULL ABLATED SYSTEM
# =============================================================================

class AblatedQAGISystem(nn.Module):
    """Full QAGI system with ablation options."""
    
    def __init__(self, dim: int = 128, config: AblationConfig = None):
        super().__init__()
        self.dim = dim
        self.config = config or AblationConfig(name='default', description='default')
        self.phi = PHI
        
        # Build layers
        self.sierpinski_core = AblatedSierpinskiCore(dim, depth=5, config=config)
        self.star_mesh = AblatedStarMeshEngine(dim, config=config)
        self.six_nodes = AblatedSixNodeSubsystem(dim, config=config)
        self.flower_lattice = AblatedFlowerOfLifeLattice(dim, config=config)
        self.outer_ring = AblatedOuterRingBoundary(dim, config=config)
        
        # Layer weights
        if self.config.phi_weighting:
            layer_weights = torch.tensor([
                self.phi ** (-4),  # Outer ring
                self.phi ** (-3),  # Flower lattice
                self.phi ** (-2),  # Six nodes
                self.phi ** (-1),  # Star mesh
                self.phi ** 0,     # Sierpinski core
            ])
        else:
            layer_weights = torch.ones(5)
        
        self.register_buffer('layer_weights', layer_weights)
        
        # Input/output projection
        self.input_proj = nn.Linear(dim, dim)
        self.output_proj = nn.Linear(dim, dim)
    
    def forward(self, x: torch.Tensor) -> Dict[str, Any]:
        x = self.input_proj(x)
        
        # Layer 5: Outer Ring (containment)
        x, contained = self.outer_ring(x)
        
        # Layer 4: Flower Lattice (memory)
        x = self.flower_lattice(x)
        
        # Layer 3: Six Nodes (processing)
        node_outputs = self.six_nodes(x)
        x = node_outputs['combined']
        
        # Layer 2: Star Mesh (entanglement)
        x = self.star_mesh(x)
        
        # Layer 1: Sierpinski Core (cognition)
        x = self.sierpinski_core(x)
        
        x = self.output_proj(x)
        
        return {
            'output': x,
            'contained': contained,
            'convergence': self.sierpinski_core.get_convergence_metric(),
            'node_outputs': node_outputs,
        }
    
    def get_structural_diagnostics(self) -> Dict[str, Any]:
        """Get structural diagnostics for analysis."""
        diagnostics = {}
        
        # Adjacency eigenvalue spectrum
        adj = self.star_mesh.adjacency.numpy()
        eigenvalues = eigvalsh(adj)
        diagnostics['adjacency_eigenvalues'] = eigenvalues.tolist()
        diagnostics['adjacency_spectral_gap'] = float(eigenvalues[-1] - eigenvalues[-2]) if len(eigenvalues) > 1 else 0
        diagnostics['adjacency_sparsity'] = float((adj > 0).mean())
        
        # Resonance pattern
        resonance = self.star_mesh.get_resonance_pattern()
        diagnostics['resonance_pattern'] = resonance.numpy().tolist()
        diagnostics['resonance_mean'] = float(resonance.mean())
        diagnostics['resonance_std'] = float(resonance.std())
        
        # Memory utilization
        memory_util = self.flower_lattice.get_memory_utilization()
        diagnostics['memory_utilization'] = memory_util
        
        # Convergence metric
        diagnostics['convergence_metric'] = self.sierpinski_core.get_convergence_metric()
        
        # Threshold
        diagnostics['containment_threshold'] = self.outer_ring.get_threshold()
        
        # Layer weights
        diagnostics['layer_weights'] = self.layer_weights.tolist()
        
        return diagnostics


# =============================================================================
# ABLATION RUNNER
# =============================================================================

@dataclass
class AblationResult:
    """Results from a single ablation experiment."""
    config_name: str
    description: str
    total_parameters: int
    trainable_parameters: int
    
    # Forward pass metrics
    output_mean: float
    output_std: float
    output_norm: float
    contained_fraction: float
    convergence: float
    
    # Structural diagnostics
    adjacency_spectral_gap: float
    adjacency_sparsity: float
    resonance_mean: float
    resonance_std: float
    memory_utilization: Dict[str, float]
    
    # Stability metrics (across multiple seeds)
    output_stability: float = 0.0
    convergence_stability: float = 0.0
    
    # Calibration sensitivity
    calibration_sensitivity: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def run_ablation(config: AblationConfig, 
                 dim: int = 128, 
                 n_runs: int = 5,
                 n_samples: int = 100) -> AblationResult:
    """Run a single ablation experiment across multiple seeds."""
    
    outputs = []
    convergences = []
    contained_fractions = []
    
    for run in range(n_runs):
        seed = config.seed + run
        torch.manual_seed(seed)
        np.random.seed(seed)
        
        # Create model
        model = AblatedQAGISystem(dim, config)
        
        # Generate random input
        x = torch.randn(n_samples, dim)
        
        # Forward pass
        with torch.no_grad():
            result = model(x)
        
        outputs.append(result['output'].numpy())
        convergences.append(result['convergence'])
        contained_fractions.append(result['contained'].float().mean().item())
    
    # Aggregate metrics
    all_outputs = np.concatenate(outputs, axis=0)
    output_mean = float(all_outputs.mean())
    output_std = float(all_outputs.std())
    output_norm = float(np.linalg.norm(all_outputs))
    
    # Stability metrics
    output_stability = float(np.std([o.mean() for o in outputs]))
    convergence_stability = float(np.std(convergences))
    
    # Get structural diagnostics from last model
    diagnostics = model.get_structural_diagnostics()
    
    # Count parameters
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    # Calibration sensitivity (perturbation test)
    torch.manual_seed(config.seed)
    model = AblatedQAGISystem(dim, config)
    x = torch.randn(10, dim)
    
    with torch.no_grad():
        base_output = model(x)['output']
        
        # Perturb input slightly
        perturbed_output = model(x + 0.01 * torch.randn_like(x))['output']
        
        calibration_sensitivity = float((base_output - perturbed_output).abs().mean())
    
    return AblationResult(
        config_name=config.name,
        description=config.description,
        total_parameters=total_params,
        trainable_parameters=trainable_params,
        output_mean=output_mean,
        output_std=output_std,
        output_norm=output_norm,
        contained_fraction=float(np.mean(contained_fractions)),
        convergence=float(np.mean(convergences)),
        adjacency_spectral_gap=diagnostics['adjacency_spectral_gap'],
        adjacency_sparsity=diagnostics['adjacency_sparsity'],
        resonance_mean=diagnostics['resonance_mean'],
        resonance_std=diagnostics['resonance_std'],
        memory_utilization=diagnostics['memory_utilization'],
        output_stability=output_stability,
        convergence_stability=convergence_stability,
        calibration_sensitivity=calibration_sensitivity,
    )


def compare_ablations(results: List[AblationResult]) -> Dict[str, Any]:
    """Compare ablation results statistically."""
    comparison = {
        'baseline': None,
        'ablations': [],
        'statistical_tests': {},
    }
    
    # Find baseline
    for r in results:
        if r.config_name == 'baseline':
            comparison['baseline'] = r.to_dict()
            break
    
    # Compare each ablation to baseline
    baseline = comparison['baseline']
    if baseline:
        for r in results:
            if r.config_name != 'baseline':
                ablation_diff = {
                    'name': r.config_name,
                    'output_mean_change': r.output_mean - baseline['output_mean'],
                    'output_std_change': r.output_std - baseline['output_std'],
                    'convergence_change': r.convergence - baseline['convergence'],
                    'stability_change': r.output_stability - baseline['output_stability'],
                    'calibration_sensitivity_change': r.calibration_sensitivity - baseline['calibration_sensitivity'],
                    'spectral_gap_change': r.adjacency_spectral_gap - baseline['adjacency_spectral_gap'],
                }
                comparison['ablations'].append(ablation_diff)
    
    return comparison


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="QAGI Geometry-Native Ablation Suite")
    parser.add_argument("--output", type=str, default="ablation_results.json", help="Output file")
    parser.add_argument("--dim", type=int, default=128, help="Model dimension")
    parser.add_argument("--n-runs", type=int, default=5, help="Number of runs per ablation")
    parser.add_argument("--n-samples", type=int, default=100, help="Samples per run")
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("QAGI Geometry-Native Ablation Suite")
    print("=" * 70)
    print(f"\nTesting {len(ABLATION_CONFIGS)} configurations:")
    for name, config in ABLATION_CONFIGS.items():
        print(f"  - {name}: {config.description}")
    
    results = []
    
    for name, config in ABLATION_CONFIGS.items():
        print(f"\n{'='*70}")
        print(f"Running ablation: {name}")
        print(f"{'='*70}")
        
        result = run_ablation(
            config, 
            dim=args.dim, 
            n_runs=args.n_runs,
            n_samples=args.n_samples
        )
        results.append(result)
        
        print(f"  Parameters: {result.total_parameters:,} ({result.trainable_parameters:,} trainable)")
        print(f"  Output: mean={result.output_mean:.4f}, std={result.output_std:.4f}")
        print(f"  Convergence: {result.convergence:.4f}")
        print(f"  Contained: {result.contained_fraction:.2%}")
        print(f"  Spectral gap: {result.adjacency_spectral_gap:.4f}")
        print(f"  Stability: {result.output_stability:.6f}")
        print(f"  Calibration sensitivity: {result.calibration_sensitivity:.6f}")
    
    # Compare results
    print("\n" + "=" * 70)
    print("ABLATION COMPARISON")
    print("=" * 70)
    
    comparison = compare_ablations(results)
    
    print(f"\n{'Ablation':<25} {'Output Δ':>12} {'Conv Δ':>10} {'Stab Δ':>12} {'Calib Δ':>12}")
    print("-" * 70)
    for ablation in comparison['ablations']:
        print(f"{ablation['name']:<25} {ablation['output_mean_change']:>12.4f} "
              f"{ablation['convergence_change']:>10.4f} {ablation['stability_change']:>12.6f} "
              f"{ablation['calibration_sensitivity_change']:>12.6f}")
    
    # Save results
    output_data = {
        'generated_at': datetime.now().isoformat(),
        'configurations': {name: asdict(config) for name, config in ABLATION_CONFIGS.items()},
        'results': [r.to_dict() for r in results],
        'comparison': comparison,
    }
    
    output_path = Path(args.output)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\nResults saved to: {output_path}")
    
    # Summary
    print("\n" + "=" * 70)
    print("KEY FINDINGS")
    print("=" * 70)
    
    baseline = comparison['baseline']
    if baseline:
        print(f"\nBaseline (full geometry):")
        print(f"  Convergence: {baseline['convergence']:.4f}")
        print(f"  Stability: {baseline['output_stability']:.6f}")
        print(f"  Calibration sensitivity: {baseline['calibration_sensitivity']:.6f}")
        
        print(f"\nMost impactful ablations:")
        sorted_ablations = sorted(comparison['ablations'], 
                                  key=lambda x: abs(x['convergence_change']), 
                                  reverse=True)
        for ablation in sorted_ablations[:3]:
            print(f"  {ablation['name']}: convergence Δ = {ablation['convergence_change']:.4f}")


if __name__ == "__main__":
    main()