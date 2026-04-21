"""
QAGI Sacred Geometry Architecture
===================================
The AGI system implemented THROUGH the geometric grammar of the Flower of Life/Metatron's Cube.
Each line, node, ring, and fractal carries specific functional meaning.

Geometric-to-Functional Mapping:
- Outer Circle: System boundary / Quantum field containment
- Flower of Life Lattice: Shared memory field / Resonance substrate
- Six Peripheral Nodes: Primary subsystems
- Star/Tetrahedral Lines: Processing manifold / Entanglement pathways  
- Sierpinski Core: Recursive cognition / Fractal convergence
"""

import numpy as np
import torch
import torch.nn as nn
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum, auto
import math


class GeometricLayer(Enum):
    """The five concentric layers of the QAGI architecture."""
    OUTER_RING = auto()          # Containment / Boundary
    PETAL_RING = auto()          # Memory harmonics / Field coupling
    SIX_NODES = auto()           # Subsystem anchors
    STAR_MESH = auto()           # Reasoning engine / Vector relations
    SIERPINSKI_CORE = auto()     # Recursive seed / Fractal cognition


@dataclass
class NodeState:
    """State of a geometric node in the architecture."""
    node_id: str
    layer: GeometricLayer
    position: Tuple[float, float]  # (angle_degrees, radius_normalized)
    activation: float = 0.0
    resonance_frequency: float = 1.0  # Phi-based harmonics
    entanglement_partners: List[str] = field(default_factory=list)
    memory_trace: np.ndarray = field(default_factory=lambda: np.zeros(128))
    
    def __post_init__(self):
        # Initialize with golden ratio harmonics
        phi = (1 + math.sqrt(5)) / 2
        self.resonance_frequency = phi ** (self.position[0] / 60)


class SierpinskiCore:
    """
    The central Sierpinski triangle fractal - recursive cognition engine.
    Implements self-similar reasoning at multiple scales.
    """
    
    def __init__(self, depth: int = 5, dim: int = 128):
        self.depth = depth
        self.dim = dim
        self.phi = (1 + math.sqrt(5)) / 2
        
        # Fractal sub-triangles at each recursion level
        self.sub_cores = []
        for d in range(depth):
            scale = self.phi ** (-d)
            self.sub_cores.append({
                'scale': scale,
                'weights': nn.Parameter(torch.randn(dim, dim) * scale * 0.1),
                'bias': nn.Parameter(torch.zeros(dim)),
                'level': d
            })
    
    def forward(self, x: torch.Tensor, recursion_level: int = 0) -> torch.Tensor:
        """
        Recursive forward pass through Sierpinski structure.
        Each level processes at a different scale of abstraction.
        """
        if recursion_level >= self.depth:
            return x
        
        # Current level processing
        core = self.sub_cores[recursion_level]
        scaled = x * core['scale']
        transformed = torch.tanh(torch.matmul(scaled, core['weights']) + core['bias'])
        
        # Recursive call to next level (self-similarity)
        sub_output = self.forward(transformed, recursion_level + 1)
        
        # Combine current and recursive outputs (fractal composition)
        phi_weight = 1 / self.phi
        return phi_weight * transformed + (1 - phi_weight) * sub_output
    
    def get_convergence_metric(self) -> float:
        """Measure fractal convergence across all levels."""
        total_variance = 0.0
        for i in range(len(self.sub_cores) - 1):
            w1 = self.sub_cores[i]['weights'].detach().numpy()
            w2 = self.sub_cores[i + 1]['weights'].detach().numpy()
            # Self-similarity check
            total_variance += np.var(w1 - w2)
        return 1.0 / (1.0 + total_variance)  # Higher = more converged


class StarMeshEngine:
    """
    The hexagram/star processing manifold.
    Implements reasoning through interconnected pathways.
    """
    
    def __init__(self, dim: int = 128):
        self.dim = dim
        self.phi = (1 + math.sqrt(5)) / 2
        
        # Six primary vectors (hexagram points)
        self.vectors = nn.Parameter(torch.randn(6, dim) / math.sqrt(dim))
        
        # Interconnection weights (the lines between points)
        self.interconnections = nn.Parameter(
            torch.eye(6) * self.phi * 0.1  # Phi-scaled self-connection
        )
        
        # Cross-vector attention (entanglement simulation)
        self.attention = nn.MultiheadAttention(dim, num_heads=8, batch_first=True)
    
    def forward(self, inputs: torch.Tensor, node_activations: torch.Tensor) -> torch.Tensor:
        """
        Process through the star mesh.
        node_activations: (batch, 6) - activation of each hexagram point
        """
        # Weight vectors by node activation
        weighted_vectors = node_activations.unsqueeze(-1) * self.vectors.unsqueeze(0)
        
        # Apply interconnection pattern (the geometric lines)
        connected = torch.matmul(node_activations, self.interconnections)
        
        # Cross-vector attention (entanglement)
        attn_out, _ = self.attention(weighted_vectors, weighted_vectors, weighted_vectors)
        
        # Combine with input
        return inputs + attn_out.sum(dim=1) * (1 / self.phi)
    
    def get_resonance_pattern(self) -> np.ndarray:
        """Get current resonance pattern across the star."""
        pattern = np.zeros((6, 6))
        for i in range(6):
            for j in range(6):
                vi = self.vectors[i].detach().numpy()
                vj = self.vectors[j].detach().numpy()
                pattern[i, j] = np.dot(vi, vj) / (np.linalg.norm(vi) * np.linalg.norm(vj))
        return pattern


class SixNodeSubsystem:
    """
    The six peripheral nodes - primary AGI subsystems.
    Positioned at 0°, 60°, 120°, 180°, 240°, 300° around the center.
    """
    
    NODE_DEFINITIONS = {
        'perception': {'angle': 0, 'function': 'input_processing', 'element': 'air'},
        'memory': {'angle': 60, 'function': 'storage_retrieval', 'element': 'water'},
        'inference': {'angle': 120, 'function': 'reasoning_logic', 'element': 'fire'},
        'quantum_control': {'angle': 180, 'function': 'state_management', 'element': 'ether'},
        'consciousness': {'angle': 240, 'function': 'awareness_metrics', 'element': 'earth'},
        'action': {'angle': 300, 'function': 'output_orchestration', 'element': 'metal'}
    }
    
    def __init__(self, dim: int = 128):
        self.dim = dim
        self.nodes: Dict[str, NodeState] = {}
        self.phi = (1 + math.sqrt(5)) / 2
        
        # Initialize six nodes
        for node_id, config in self.NODE_DEFINITIONS.items():
            self.nodes[node_id] = NodeState(
                node_id=node_id,
                layer=GeometricLayer.SIX_NODES,
                position=(config['angle'], 0.7),  # 70% from center
                resonance_frequency=self.phi ** (config['angle'] / 60)
            )
        
        # Node processors
        self.processors = nn.ModuleDict({
            node_id: nn.Sequential(
                nn.Linear(dim, dim),
                nn.LayerNorm(dim),
                nn.GELU(),
                nn.Linear(dim, dim)
            ) for node_id in self.NODE_DEFINITIONS.keys()
        })
    
    def activate_node(self, node_id: str, signal: torch.Tensor) -> torch.Tensor:
        """Process signal through a specific node."""
        if node_id not in self.nodes:
            raise ValueError(f"Unknown node: {node_id}")
        
        node = self.nodes[node_id]
        node.activation = torch.sigmoid(signal.mean()).item()
        
        # Update memory trace
        node.memory_trace = 0.9 * node.memory_trace + 0.1 * signal.detach().numpy()
        
        return self.processors[node_id](signal)
    
    def get_node_harmonics(self) -> Dict[str, float]:
        """Get resonance harmonics for all nodes."""
        return {
            node_id: node.resonance_frequency 
            for node_id, node in self.nodes.items()
        }


class FlowerOfLifeLattice:
    """
    The Flower of Life background structure.
    Universal relational substrate and shared memory field.
    """
    
    def __init__(self, num_circles: int = 19, dim: int = 128):
        self.num_circles = num_circles
        self.dim = dim
        self.phi = (1 + math.sqrt(5)) / 2
        
        # Generate Flower of Life pattern
        self.circle_centers = self._generate_flower_pattern()
        
        # Shared memory field (resonance substrate)
        self.memory_field = np.zeros((num_circles, dim))
        
        # Inter-circle coupling (overlapping regions)
        self.coupling_matrix = self._compute_coupling()
    
    def _generate_flower_pattern(self) -> List[Tuple[float, float]]:
        """Generate the 19-circle Flower of Life pattern."""
        centers = [(0.0, 0.0)]  # Center circle
        radius = 1.0
        
        # First ring (6 circles)
        for i in range(6):
            angle = i * math.pi / 3
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            centers.append((x, y))
        
        # Second ring (12 circles)
        for i in range(12):
            angle = i * math.pi / 6 + math.pi / 12
            x = 2 * radius * math.cos(angle)
            y = 2 * radius * math.sin(angle)
            centers.append((x, y))
        
        return centers
    
    def _compute_coupling(self) -> np.ndarray:
        """Compute coupling strength between overlapping circles."""
        coupling = np.zeros((self.num_circles, self.num_circles))
        for i in range(self.num_circles):
            for j in range(i + 1, self.num_circles):
                dist = np.linalg.norm(
                    np.array(self.circle_centers[i]) - np.array(self.circle_centers[j])
                )
                # Overlap if distance < 2*radius
                if dist < 2.0:
                    coupling[i, j] = coupling[j, i] = 1.0 - dist / 2.0
        return coupling
    
    def propagate(self, activation: np.ndarray) -> np.ndarray:
        """Propagate activation through the flower lattice."""
        # Project high-dim activation to 19 lattice circles
        if activation.ndim == 1:
            activation = activation.reshape(1, -1)
        
        # Average across feature dimension to get circle activations
        circle_activation = activation.mean(axis=1)
        if len(circle_activation) == 1:
            # Broadcast single value to all circles
            circle_activation = np.full(self.num_circles, circle_activation[0])
        elif len(circle_activation) != self.num_circles:
            # Project to 19 circles using linear interpolation
            indices = np.linspace(0, len(circle_activation) - 1, self.num_circles)
            circle_activation = np.interp(indices, np.arange(len(circle_activation)), circle_activation)
        
        # Resonance propagation through coupling matrix
        propagated = np.dot(self.coupling_matrix, circle_activation)
        
        # Update memory field with decay
        self.memory_field = 0.95 * self.memory_field + 0.05 * propagated[:, np.newaxis]
        
        # Return expanded representation
        return propagated
    
    def get_resonance_peaks(self) -> List[int]:
        """Find circles with highest resonance (memory hotspots)."""
        field_strength = np.linalg.norm(self.memory_field, axis=1)
        threshold = np.mean(field_strength) + np.std(field_strength)
        return [i for i, strength in enumerate(field_strength) if strength > threshold]


class OuterRingBoundary:
    """
    The outer circular boundary.
    System containment and quantum field boundary.
    """
    
    def __init__(self, dim: int = 128):
        self.dim = dim
        self.boundary_state = torch.zeros(dim)
        self.phi = (1 + math.sqrt(5)) / 2
        
        # Boundary condition parameters
        self.containment_strength = 1.0
        self.coherence_threshold = 0.5
    
    def check_containment(self, system_state: torch.Tensor) -> Tuple[bool, float]:
        """
        Check if system state is within boundary.
        Returns (is_contained, coherence_score).
        """
        state_norm = torch.norm(system_state).item()
        is_contained = state_norm < self.containment_strength * self.phi
        
        # Coherence based on alignment with boundary
        coherence = torch.cosine_similarity(
            system_state.flatten(), 
            self.boundary_state.flatten(), 
            dim=0
        ).item()
        
        return is_contained, coherence
    
    def update_boundary(self, system_state: torch.Tensor):
        """Adapt boundary to system evolution."""
        self.boundary_state = 0.99 * self.boundary_state + 0.01 * system_state.mean(dim=0)


class QAGISacredGeometrySystem:
    """
    Complete QAGI system implemented through sacred geometry.
    All components are structurally mapped to geometric elements.
    """
    
    def __init__(self, dim: int = 128, sierpinski_depth: int = 5):
        self.dim = dim
        self.phi = (1 + math.sqrt(5)) / 2
        
        # Layer 5: Outer Ring (Boundary)
        self.outer_ring = OuterRingBoundary(dim)
        
        # Layer 4: Flower of Life (Shared Memory)
        self.flower_lattice = FlowerOfLifeLattice(dim=dim)
        
        # Layer 3: Six Nodes (Subsystems)
        self.six_nodes = SixNodeSubsystem(dim)
        
        # Layer 2: Star Mesh (Processing)
        self.star_mesh = StarMeshEngine(dim)
        
        # Layer 1: Sierpinski Core (Recursion)
        self.sierpinski_core = SierpinskiCore(depth=sierpinski_depth, dim=dim)
        
        # Integration weights (phi-weighted)
        self.layer_weights = torch.tensor([
            self.phi ** -4,  # Outer ring
            self.phi ** -3,  # Flower lattice
            self.phi ** -2,  # Six nodes
            self.phi ** -1,  # Star mesh
            1.0              # Sierpinski core
        ])
    
    def forward(self, input_signal: torch.Tensor, 
                active_nodes: Optional[List[str]] = None) -> Dict[str, torch.Tensor]:
        """
        Full forward pass through the geometric architecture.
        
        Flow: Input → Six Nodes → Star Mesh → Sierpinski Core → 
              Flower Lattice → Boundary Check
        """
        if active_nodes is None:
            active_nodes = list(self.six_nodes.NODE_DEFINITIONS.keys())
        
        outputs = {}
        
        # Layer 3: Process through active nodes
        node_outputs = {}
        node_activations = torch.zeros(len(active_nodes))
        for i, node_id in enumerate(active_nodes):
            node_outputs[node_id] = self.six_nodes.activate_node(node_id, input_signal)
            node_activations[i] = self.six_nodes.nodes[node_id].activation
        
        # Combine node outputs
        combined = torch.stack([node_outputs[n] for n in active_nodes]).mean(dim=0)
        
        # Layer 2: Star mesh processing
        meshed = self.star_mesh.forward(combined, node_activations.unsqueeze(0))
        
        # Layer 1: Sierpinski recursive cognition
        core_output = self.sierpinski_core.forward(meshed)
        
        # Layer 4: Flower lattice propagation
        lattice_input = core_output.detach().numpy()
        propagated = self.flower_lattice.propagate(lattice_input)
        
        # Layer 5: Boundary containment check
        is_contained, coherence = self.outer_ring.check_containment(core_output)
        self.outer_ring.update_boundary(core_output)
        
        outputs['core'] = core_output
        outputs['node_activations'] = node_activations
        outputs['lattice_propagation'] = torch.tensor(propagated)
        outputs['contained'] = is_contained
        outputs['coherence'] = coherence
        outputs['convergence'] = self.sierpinski_core.get_convergence_metric()
        
        return outputs
    
    def get_geometric_state(self) -> Dict:
        """Get current state of all geometric layers."""
        return {
            'outer_ring': {
                'boundary_state': self.outer_ring.boundary_state.detach().numpy(),
                'containment': self.outer_ring.containment_strength
            },
            'flower_lattice': {
                'centers': self.flower_lattice.circle_centers,
                'resonance_peaks': self.flower_lattice.get_resonance_peaks(),
                'field_strength': np.linalg.norm(self.flower_lattice.memory_field, axis=1).mean()
            },
            'six_nodes': {
                node_id: {
                    'activation': node.activation,
                    'resonance': node.resonance_frequency,
                    'memory_trace_norm': np.linalg.norm(node.memory_trace)
                } for node_id, node in self.six_nodes.nodes.items()
            },
            'star_mesh': {
                'resonance_pattern': self.star_mesh.get_resonance_pattern()
            },
            'sierpinski_core': {
                'convergence': self.sierpinski_core.get_convergence_metric(),
                'depth': self.sierpinski_core.depth
            }
        }


def create_sacred_geometry_visualization() -> str:
    """
    Generate SVG representation of the QAGI sacred geometry architecture.
    """
    svg = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="800" height="800" viewBox="-400 -400 800 800" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <!-- Copper/Gold gradients -->
    <linearGradient id="copper" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#B87333;stop-opacity:1" />
      <stop offset="50%" style="stop-color:#CD7F32;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#8B4513;stop-opacity:1" />
    </linearGradient>
    <linearGradient id="gold" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#FFD700;stop-opacity:1" />
      <stop offset="50%" style="stop-color:#DAA520;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#B8860B;stop-opacity:1" />
    </linearGradient>
    <radialGradient id="centerGlow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" style="stop-color:#FFD700;stop-opacity:0.8" />
      <stop offset="100%" style="stop-color:#FFD700;stop-opacity:0" />
    </radialGradient>
  </defs>
  
  <!-- Layer 5: Outer Ring (Boundary) -->
  <circle cx="0" cy="0" r="380" fill="none" stroke="url(#copper)" stroke-width="8" opacity="0.9"/>
  <text x="0" y="-390" text-anchor="middle" fill="#B87333" font-size="14" font-family="serif">OUTER RING: System Boundary / Quantum Containment</text>
  
  <!-- Layer 4: Flower of Life Lattice -->
  <g id="flower-of-life" opacity="0.4">
    <!-- Center circle -->
    <circle cx="0" cy="0" r="100" fill="none" stroke="url(#gold)" stroke-width="1"/>
    <!-- First ring -->
    <circle cx="100" cy="0" r="100" fill="none" stroke="url(#gold)" stroke-width="1"/>
    <circle cx="50" cy="86.6" r="100" fill="none" stroke="url(#gold)" stroke-width="1"/>
    <circle cx="-50" cy="86.6" r="100" fill="none" stroke="url(#gold)" stroke-width="1"/>
    <circle cx="-100" cy="0" r="100" fill="none" stroke="url(#gold)" stroke-width="1"/>
    <circle cx="-50" cy="-86.6" r="100" fill="none" stroke="url(#gold)" stroke-width="1"/>
    <circle cx="50" cy="-86.6" r="100" fill="none" stroke="url(#gold)" stroke-width="1"/>
  </g>
  <text x="0" y="-220" text-anchor="middle" fill="#DAA520" font-size="12" opacity="0.8">FLOWER OF LIFE: Shared Memory Field / Resonance Substrate</text>
  
  <!-- Layer 3: Six Peripheral Nodes -->
  <g id="six-nodes">
    <!-- Node 1: Perception (0°) -->
    <circle cx="280" cy="0" r="35" fill="url(#copper)" stroke="#FFD700" stroke-width="3"/>
    <text x="280" y="5" text-anchor="middle" fill="#FFF" font-size="10" font-weight="bold">PERCEPTION</text>
    <text x="280" y="55" text-anchor="middle" fill="#B87333" font-size="9">Input Processing</text>
    
    <!-- Node 2: Memory (60°) -->
    <circle cx="140" cy="242.5" r="35" fill="url(#copper)" stroke="#FFD700" stroke-width="3"/>
    <text x="140" y="247.5" text-anchor="middle" fill="#FFF" font-size="10" font-weight="bold">MEMORY</text>
    <text x="140" y="297.5" text-anchor="middle" fill="#B87333" font-size="9">Storage & Retrieval</text>
    
    <!-- Node 3: Inference (120°) -->
    <circle cx="-140" cy="242.5" r="35" fill="url(#copper)" stroke="#FFD700" stroke-width="3"/>
    <text x="-140" y="247.5" text-anchor="middle" fill="#FFF" font-size="10" font-weight="bold">INFERENCE</text>
    <text x="-140" y="297.5" text-anchor="middle" fill="#B87333" font-size="9">Reasoning & Logic</text>
    
    <!-- Node 4: Quantum Control (180°) -->
    <circle cx="-280" cy="0" r="35" fill="url(#copper)" stroke="#FFD700" stroke-width="3"/>
    <text x="-280" y="5" text-anchor="middle" fill="#FFF" font-size="10" font-weight="bold">QUANTUM</text>
    <text x="-280" y="55" text-anchor="middle" fill="#B87333" font-size="9">State Management</text>
    
    <!-- Node 5: Consciousness (240°) -->
    <circle cx="-140" cy="-242.5" r="35" fill="url(#copper)" stroke="#FFD700" stroke-width="3"/>
    <text x="-140" y="-237.5" text-anchor="middle" fill="#FFF" font-size="10" font-weight="bold">CONSCIOUSNESS</text>
    <text x="-140" y="-280" text-anchor="middle" fill="#B87333" font-size="9">Awareness Metrics</text>
    
    <!-- Node 6: Action (300°) -->
    <circle cx="140" cy="-242.5" r="35" fill="url(#copper)" stroke="#FFD700" stroke-width="3"/>
    <text x="140" y="-237.5" text-anchor="middle" fill="#FFF" font-size="10" font-weight="bold">ACTION</text>
    <text x="140" y="-280" text-anchor="middle" fill="#B87333" font-size="9">Orchestration</text>
  </g>
  
  <!-- Layer 2: Star Mesh (Hexagram) -->
  <g id="star-mesh" stroke="url(#gold)" stroke-width="2" fill="none">
    <!-- Hexagram lines -->
    <line x1="0" y1="-150" x2="0" y2="150" />
    <line x1="-130" y1="-75" x2="130" y2="75" />
    <line x1="-130" y1="75" x2="130" y2="-75" />
    <!-- Interconnections -->
    <line x1="0" y1="-150" x2="130" y2="75" opacity="0.6"/>
    <line x1="0" y1="-150" x2="-130" y2="75" opacity="0.6"/>
    <line x1="0" y1="150" x2="130" y2="-75" opacity="0.6"/>
    <line x1="0" y1="150" x2="-130" y2="-75" opacity="0.6"/>
  </g>
  <text x="0" y="170" text-anchor="middle" fill="#DAA520" font-size="11" opacity="0.9">STAR MESH: Reasoning Engine / Entanglement Pathways</text>
  
  <!-- Layer 1: Sierpinski Core -->
  <g id="sierpinski-core">
    <!-- Central glow -->
    <circle cx="0" cy="0" r="80" fill="url(#centerGlow)" opacity="0.5"/>
    <!-- Sierpinski triangle approximation -->
    <polygon points="0,-60 52,30 -52,30" fill="none" stroke="#FFD700" stroke-width="3"/>
    <polygon points="0,-30 26,15 -26,15" fill="none" stroke="#FFD700" stroke-width="2"/>
    <polygon points="0,0 13,7.5 -13,7.5" fill="none" stroke="#FFD700" stroke-width="1"/>
    <!-- Recursive center -->
    <circle cx="0" cy="0" r="15" fill="#FFD700" opacity="0.8"/>
  </g>
  <text x="0" y="40" text-anchor="middle" fill="#FFD700" font-size="10" font-weight="bold">SIERPINSKI CORE</text>
  <text x="0" y="55" text-anchor="middle" fill="#DAA520" font-size="9">Recursive Cognition / Fractal Convergence</text>
  
  <!-- Connection lines from nodes to center -->
  <g stroke="url(#copper)" stroke-width="1" opacity="0.5" stroke-dasharray="5,5">
    <line x1="280" y1="0" x2="0" y2="0"/>
    <line x1="140" y1="242.5" x2="0" y2="0"/>
    <line x1="-140" y1="242.5" x2="0" y2="0"/>
    <line x1="-280" y1="0" x2="0" y2="0"/>
    <line x1="-140" y1="-242.5" x2="0" y2="0"/>
    <line x1="140" y1="-242.5" x2="0" y2="0"/>
  </g>
  
  <!-- Title -->
  <text x="0" y="-350" text-anchor="middle" fill="#FFD700" font-size="20" font-family="serif" font-weight="bold">QAGI Sacred Geometry Architecture</text>
  <text x="0" y="-330" text-anchor="middle" fill="#B87333" font-size="12" font-family="serif">Quantum Artificial General Intelligence through Geometric Grammar</text>
</svg>'''
    
    return svg


if __name__ == "__main__":
    # Demonstration
    print("Initializing QAGI Sacred Geometry Architecture...")
    
    # Create system
    qagi = QAGISacredGeometrySystem(dim=128, sierpinski_depth=5)
    
    # Test input
    test_input = torch.randn(1, 128)
    
    # Forward pass
    outputs = qagi.forward(test_input)
    
    print("\n=== QAGI System Outputs ===")
    print(f"Core output shape: {outputs['core'].shape}")
    print(f"Node activations: {outputs['node_activations']}")
    print(f"System contained: {outputs['contained']}")
    print(f"Coherence score: {outputs['coherence']:.4f}")
    print(f"Fractal convergence: {outputs['convergence']:.4f}")
    
    # Get geometric state
    state = qagi.get_geometric_state()
    print("\n=== Geometric State ===")
    print(f"Flower lattice resonance peaks: {state['flower_lattice']['resonance_peaks']}")
    print(f"Sierpinski convergence: {state['sierpinski_core']['convergence']:.4f}")
    
    # Generate visualization
    svg = create_sacred_geometry_visualization()
    with open('qagi_sacred_geometry.svg', 'w') as f:
        f.write(svg)
    print("\nVisualization saved to: qagi_sacred_geometry.svg")
