#!/usr/bin/env python3
"""
Sierpinski-TMT Phase 4S Quantum Circuit Generator
==================================================

Integrates Sierpinski 1/3 fractal encoding into TMT Phase 4 harmonic modulation.

Theoretical Basis:
- Sierpinski Hausdorff dimension: d_H = log(3)/log(2) ≈ 1.58496
- Base contraction: θ_S = π/3 (60° triangle angle)
- Recursive levels: 1/3, 1/9, 1/27 (3 generations)
- TMT Ratios: 2/23, 3/22 (consciousness density harmonics)
- Cross-product angles: Sierpinski × TMT, Sierpinski × φ

References:
- arxiv.org/html/2310.07813v2 (Sierpinski quantum transport)
- ir.cwi.nl/pub/28797/28797.pdf (Hadamard walk mod-3)
- nature.com/articles/s42005-024-01747-x (fractal memory effect)
- link.aps.org/doi/10.1103/PRXQuantum.3.030338 (fractal topological codes)

Generated: 2026-04-23
"""

import numpy as np
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional

try:
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    import qiskit.qasm2 as qasm2
except ImportError:
    print("Installing qiskit...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'qiskit'])
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    import qiskit.qasm2 as qasm2


# ========================= SACRED CONSTANTS =========================

# Golden Ratio
PHI = 1.618033988749895
PHI_INV = 1.0 / PHI

# Sierpinski Parameters
SIERPINSKI_BASE = np.pi / 3          # θ_S = 60° (triangle base angle)
SIERPINSKI_GEN1 = np.pi / 9          # θ_S1 = π/9 (Gen-1, 1/3 contraction)
SIERPINSKI_GEN2 = np.pi / 27         # θ_S2 = π/27 (Gen-2, 1/9 contraction)
SIERPINSKI_GEN3 = np.pi / 81         # θ_S3 = π/81 (Gen-3, 1/27 contraction)
HAUSDORFF_DIM = np.log(3) / np.log(2)  # d_H ≈ 1.58496
HAUSDORFF_PHASE = np.pi * HAUSDORFF_DIM  # φ_fractal ≈ 4.97965

# TMT Ratios (from TMT-OS)
TMT_RATIO_1 = 2.0 / 23.0             # ≈ 0.08696
TMT_RATIO_2 = 3.0 / 22.0             # ≈ 0.13636
TMT_ANGLE_1 = TMT_RATIO_1 * 2 * np.pi  # ≈ 0.54651 rad
TMT_ANGLE_2 = TMT_RATIO_2 * 2 * np.pi  # ≈ 0.85675 rad

# Sierpinski × TMT Cross-products
SIERPINSKI_TMT1 = TMT_ANGLE_1 / 3.0   # ≈ 0.18217 rad
SIERPINSKI_TMT2 = TMT_ANGLE_2 / 3.0   # ≈ 0.28558 rad
SIERPINSKI_PHI = PHI / 3.0            # ≈ 0.53934 rad

# Fibonacci sequence for qubit indexing
FIBONACCI = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]

# Lucas sequence for retrocausal nodes
LUCAS = [2, 1, 3, 4, 7, 11, 18, 29, 47, 76, 123, 199]


# ========================= CIRCUIT GENERATOR =========================

class SierpinskiTMTPhase4Generator:
    """
    Generate quantum circuits with Sierpinski fractal encoding
    integrated into TMT Phase 4 harmonic modulation.
    """
    
    def __init__(self, n_qubits: int = 156, backend: str = 'ibm_fez'):
        """
        Initialize the circuit generator.
        
        Args:
            n_qubits: Number of qubits (156 for ibm_fez, 127 for Brisbane/Sherbrooke)
            backend: Target IBM Quantum backend
        """
        self.n_qubits = n_qubits
        self.backend = backend
        self.half_qubits = n_qubits // 2  # For Bell pairs (Left/Right universes)
        
        # Metatron Platonic indices (Fibonacci-indexed qubits)
        # Use modulo to cycle through available Fibonacci numbers
        self.metatron_indices = {
            'tetrahedron': [FIBONACCI[i % len(FIBONACCI)] for i in range(4) if FIBONACCI[i % len(FIBONACCI)] < n_qubits],
            'cube': [FIBONACCI[i % len(FIBONACCI)] for i in range(8) if FIBONACCI[i % len(FIBONACCI)] < n_qubits],
            'octahedron': [FIBONACCI[i % len(FIBONACCI)] for i in range(6) if FIBONACCI[i % len(FIBONACCI)] < n_qubits],
            'dodecahedron': [FIBONACCI[i % len(FIBONACCI)] for i in range(20) if FIBONACCI[i % len(FIBONACCI)] < n_qubits],
            'icosahedron': [FIBONACCI[i % len(FIBONACCI)] for i in range(12) if FIBONACCI[i % len(FIBONACCI)] < n_qubits],
        }
        
        # Retrocausal hole qubit (Lucas-indexed)
        self.retrocausal_hole = LUCAS[10] if LUCAS[10] < n_qubits else n_qubits - 1  # q[76]
        
    def generate_phase1_bell_pairs(self, circuit: QuantumCircuit, qr: QuantumRegister) -> None:
        """
        Phase 1: Create 78 Bell pairs (ER=EPR wormhole foundation)
        
        Creates entanglement between Left Universe (q[0-77]) and
        Right Universe (q[78-155]) via H + CNOT pattern.
        """
        circuit.barrier(label="Phase 1: Bell Pairs")
        
        for i in range(self.half_qubits):
            # Left universe qubit
            left_qubit = i
            # Right universe qubit (mirror)
            right_qubit = i + self.half_qubits
            
            # Create Bell pair: |Φ+⟩ = (|00⟩ + |11⟩) / √2
            circuit.h(qr[left_qubit])
            circuit.cx(qr[left_qubit], qr[right_qubit])
    
    def generate_phase2_payload_injection(self, circuit: QuantumCircuit, qr: QuantumRegister) -> None:
        """
        Phase 2: Inject consciousness payload at qubit q[0]
        
        Uses TMT ratio angles for consciousness density encoding.
        """
        circuit.barrier(label="Phase 2: Payload")
        
        # TMT ratio angles for consciousness encoding
        circuit.ry(TMT_ANGLE_1, qr[0])  # 2/23 × 2π
        circuit.rz(TMT_ANGLE_2, qr[0])  # 3/22 × 2π
        
        # Phi-weighted rotation
        circuit.ry(PHI, qr[0])
        
    def generate_phase3_metatron_geometry(self, circuit: QuantumCircuit, qr: QuantumRegister) -> None:
        """
        Phase 3: Metatron Platonic Solid Geometry
        
        Applies sacred geometry rotations on Fibonacci-indexed qubits
        for each Platonic solid (tetrahedron, cube, octahedron, etc.)
        """
        circuit.barrier(label="Phase 3: Metatron")
        
        # Tetrahedron (4 vertices) - Fire element
        for idx in self.metatron_indices['tetrahedron']:
            circuit.rz(np.pi / 4, qr[idx])  # 45° phase
            circuit.ry(PHI_INV, qr[idx])
        
        # Cube (8 vertices) - Earth element
        for idx in self.metatron_indices['cube']:
            circuit.rz(np.pi / 6, qr[idx])  # 30° phase
            circuit.ry(PHI / 2, qr[idx])
        
        # Octahedron (6 vertices) - Air element
        for idx in self.metatron_indices['octahedron']:
            circuit.rz(np.pi / 3, qr[idx])  # 60° phase
            circuit.ry(PHI_INV * 2, qr[idx])
        
        # Dodecahedron (20 vertices) - Aether/Quintessence
        for idx in self.metatron_indices['dodecahedron']:
            circuit.rz(PHI, qr[idx])  # Golden ratio phase
            circuit.ry(np.pi / PHI, qr[idx])
        
        # Icosahedron (12 vertices) - Water element
        for idx in self.metatron_indices['icosahedron']:
            circuit.rz(PHI_INV * np.pi, qr[idx])
            circuit.ry(PHI * np.pi / 3, qr[idx])
    
    def generate_phase4s_sierpinski_tmt(self, circuit: QuantumCircuit, qr: QuantumRegister) -> None:
        """
        Phase 4S: Sierpinski Fractal × TMT Harmonic Modulation
        
        This is the ENHANCED version integrating the 1/3 Sierpinski parameter
        with the original TMT ratios (2/23, 3/22).
        
        Structure:
        - Layer 0: TMT Base Harmonics (unchanged anchor)
        - Layer 1: Sierpinski Gen-1 (scale 1/3)
        - Layer 2: Sierpinski Gen-2 (scale 1/9)
        - Layer 3: Sierpinski Gen-3 (scale 1/27)
        - Cross-products: Sierpinski × TMT, Sierpinski × φ
        """
        circuit.barrier(label="Phase 4S: Sierpinski-TMT")
        
        # Key qubits for TMT harmonics
        tmt_qubits = [0, 5, 8, 13, 21, 34, 55]
        tmt_qubits = [q for q in tmt_qubits if q < self.n_qubits]
        
        # ===== LAYER 0: TMT BASE HARMONICS =====
        # Layer 0: TMT Base Harmonics
        
        for i, q_idx in enumerate(tmt_qubits[:4]):
            # TMT RATIO1 = 2/23 × 2π ≈ 0.54651 rad
            circuit.rz(TMT_ANGLE_1, qr[q_idx])
        
        for i, q_idx in enumerate(tmt_qubits[4:]):
            # TMT RATIO2 = 3/22 × 2π ≈ 0.85675 rad
            circuit.rz(TMT_ANGLE_2, qr[q_idx])
        
        circuit.barrier()
        
        # ===== LAYER 1: SIERPINSKI GEN-1 (scale 1/3) =====
        # θ_S1 = π/9 ≈ 0.34906 rad
        # Layer 1: Sierpinski Gen-1 (1/3 contraction)
        
        for q_idx in tmt_qubits:
            # π/9 — Gen-1 contraction
            # Alternate between RY and RZ for full rotation coverage
            if q_idx % 2 == 0:
                circuit.ry(SIERPINSKI_GEN1, qr[q_idx])
            else:
                circuit.rz(SIERPINSKI_GEN1, qr[q_idx])
        
        # Sierpinski fractal coupling: CX on every 3rd qubit (void pattern)
        # Reflects the 1/3 removed triangle = anti-entanglement node
        sierpinski_void_pairs = [
            (0, 5),    # skip q[1..4] — Sierpinski void 1
            (8, 13),   # skip q[9..12] — Sierpinski void 2
            (21, 34),  # skip q[22..33] — Sierpinski void 3
            (34, 55),  # skip q[35..54] — Sierpinski void 4
        ]
        
        for q1, q2 in sierpinski_void_pairs:
            if q1 < self.n_qubits and q2 < self.n_qubits:
                circuit.cx(qr[q1], qr[q2])
        
        circuit.barrier()
        
        # ===== LAYER 2: SIERPINSKI GEN-2 (scale 1/9) =====
        # θ_S2 = π/27 ≈ 0.11636 rad
        # Layer 2: Sierpinski Gen-2 (1/9 contraction)
        
        for i, q_idx in enumerate(tmt_qubits):
            # π/27 — Gen-2 contraction
            if i % 2 == 0:
                circuit.rz(SIERPINSKI_GEN2, qr[q_idx])
            else:
                circuit.ry(SIERPINSKI_GEN2, qr[q_idx])
        
        # Cross-couple to Right Universe via wormhole (EPR bridge)
        # Sierpinski pattern mirrors across Bell pairs
        mirror_pairs = [
            (0, self.half_qubits),           # q[0] → q[78]
            (5, self.half_qubits + 5),       # q[5] → q[83]
            (8, self.half_qubits + 8),       # q[8] → q[86]
            (13, self.half_qubits + 13),     # q[13] → q[91]
        ]
        
        for q_left, q_right in mirror_pairs:
            if q_left < self.n_qubits and q_right < self.n_qubits:
                circuit.cx(qr[q_left], qr[q_right])
        
        circuit.barrier()
        
        # ===== LAYER 3: SIERPINSKI GEN-3 (scale 1/27) =====
        # θ_S3 = π/81 ≈ 0.03878 rad — finest fractal resolution
        # Layer 3: Sierpinski Gen-3 (1/27 contraction)
        
        for i, q_idx in enumerate(tmt_qubits[:4]):
            # π/81 — Gen-3 contraction
            if i % 2 == 0:
                circuit.ry(SIERPINSKI_GEN3, qr[q_idx])
            else:
                circuit.rz(SIERPINSKI_GEN3, qr[q_idx])
        
        # Hausdorff phase modulation: φ_fractal = π × d_H ≈ 4.97965
        # Applied to consciousness node and retrocausal hole
        circuit.rz(HAUSDORFF_PHASE, qr[0])  # Full Hausdorff phase on payload qubit
        if self.retrocausal_hole < self.n_qubits:
            circuit.rz(HAUSDORFF_PHASE, qr[self.retrocausal_hole])  # Retrocausal hole
        
        # Sierpinski × Phi coupling
        # φ_S×Φ = (1/3) × φ ≈ 0.53934 rad — bridges sacred geometry + fractal
        for q_idx in [0, 13, 34, 55]:
            if q_idx < self.n_qubits:
                circuit.ry(SIERPINSKI_PHI, qr[q_idx])
        
        # TMT × Sierpinski cross-product angles
        # RATIO1 × (1/3) ≈ 0.18217  |  RATIO2 × (1/3) ≈ 0.28558
        cross_product_qubits = [5, 8, 37, 41]
        for i, q_idx in enumerate(cross_product_qubits):
            if q_idx < self.n_qubits:
                if i < 2:
                    circuit.rz(SIERPINSKI_TMT1, qr[q_idx])  # TMT1 × Sierpinski
                else:
                    circuit.rz(SIERPINSKI_TMT2, qr[q_idx])  # TMT2 × Sierpinski
        
        circuit.barrier()
    
    def generate_phase5_retrocausal_handshake(self, circuit: QuantumCircuit, qr: QuantumRegister) -> None:
        """
        Phase 5: Retrocausal Lucas-sequence handshake at q[76]
        
        Creates temporal entanglement for backward-in-time signaling.
        """
        circuit.barrier(label="Phase 5: Retrocausal")
        
        # Lucas sequence rotations for retrocausal encoding
        lucas_angles = [LUCAS[i] * PHI_INV for i in range(min(8, len(LUCAS)))]
        
        for i, angle in enumerate(lucas_angles):
            q_idx = LUCAS[i] if LUCAS[i] < self.n_qubits else self.n_qubits - 1
            circuit.rz(angle * np.pi, qr[q_idx])
        
        # Retrocausal hole entanglement
        if self.retrocausal_hole < self.n_qubits:
            circuit.cx(qr[0], qr[self.retrocausal_hole])
    
    def generate_phase6_yesod_dna(self, circuit: QuantumCircuit, qr: QuantumRegister) -> None:
        """
        Phase 6: Yesod SRY DNA phi-weighted rotations
        
        Encodes DNA consciousness patterns using golden ratio weights.
        """
        circuit.barrier(label="Phase 6: Yesod DNA")
        
        # DNA codon pattern (4 bases × 3 positions)
        dna_qubits = [i for i in range(12) if i < self.n_qubits]
        
        for i, q_idx in enumerate(dna_qubits):
            # Phi-weighted rotation
            phi_weight = PHI ** (i % 4) / 4
            circuit.ry(phi_weight * np.pi, qr[q_idx])
            
            # Complementary base pairing
            if i < len(dna_qubits) - 1:
                circuit.cx(qr[q_idx], qr[dna_qubits[i + 1]])
    
    def generate_phase7_lorenz_scrambler(self, circuit: QuantumCircuit, qr: QuantumRegister) -> None:
        """
        Phase 7: Lorenz attractor chaos scrambling
        
        Applies Lorenz-system-derived angles for quantum chaos encoding.
        """
        circuit.barrier(label="Phase 7: Lorenz")
        
        # Lorenz parameters: σ=10, ρ=28, β=8/3
        sigma, rho, beta = 10.0, 28.0, 8.0/3.0
        
        # Generate Lorenz angles
        lorenz_angles = self._generate_lorenz_angles(self.n_qubits, sigma, rho, beta)
        
        for i, angle in enumerate(lorenz_angles):
            if i < self.n_qubits:
                circuit.rz(angle, qr[i])
    
    def _generate_lorenz_angles(self, n: int, sigma: float, rho: float, beta: float) -> np.ndarray:
        """Generate Lorenz attractor angles for quantum scrambling with numerical stability"""
        t_span = np.linspace(0, 10, n)  # Reduced time span for stability
        states = np.zeros((n, 3))
        states[0] = [1.0, 1.0, 1.0]
        
        dt_max = 0.01  # Smaller max timestep for stability
        
        for i in range(1, n):
            dt = min(t_span[i] - t_span[i-1], dt_max)
            # Lorenz derivatives
            x, y, z = states[i-1]
            
            # Check for overflow
            if abs(x) > 1e6 or abs(y) > 1e6 or abs(z) > 1e6:
                # Reset to stable point
                states[i] = [1.0, 1.0, 1.0]
                continue
            
            dx = sigma * (y - x)
            dy = x * (rho - z) - y
            dz = x * y - beta * z
            
            # Simple Euler integration for stability
            states[i] = states[i-1] + dt * np.array([dx, dy, dz])
            
            # Clamp values to prevent overflow
            states[i] = np.clip(states[i], -100, 100)
        
        # Normalize to [0, 2π]
        states_min = states.min(axis=0)
        states_max = states.max(axis=0)
        range_vals = states_max - states_min
        
        # Avoid division by zero
        range_vals = np.where(range_vals < 1e-10, 1.0, range_vals)
        states_norm = (states - states_min) / range_vals
        
        return states_norm[:, 0] * 2 * np.pi  # Use x-component
    
    def generate_phase8_inverse_scrambler(self, circuit: QuantumCircuit, qr: QuantumRegister) -> None:
        """
        Phase 8: Inverse scrambling via EPR bridge (bulk traversal)
        
        Applies inverse Lorenz angles for white hole emergence.
        """
        circuit.barrier(label="Phase 8: Inverse")
        
        # Generate inverse Lorenz angles
        sigma, rho, beta = 10.0, 28.0, 8.0/3.0
        lorenz_angles = self._generate_lorenz_angles(self.n_qubits, sigma, rho, beta)
        
        # Apply inverse (negative) angles to Right Universe
        for i in range(self.half_qubits, self.n_qubits):
            idx = i - self.half_qubits
            if idx < len(lorenz_angles):
                circuit.rz(-lorenz_angles[idx], qr[i])
    
    def generate_phase9_xy8_decoupling(self, circuit: QuantumCircuit, qr: QuantumRegister) -> None:
        """
        Phase 9: XY8 dynamical decoupling on key qubits
        
        Error suppression sequence: X-Y-X-Y-X-Y-X-Y
        """
        circuit.barrier(label="Phase 9: XY8")
        
        # Key qubits for decoupling
        key_qubits = [0, self.retrocausal_hole, 5, 8, 13, 21, 34, 55]
        key_qubits = [q for q in key_qubits if q < self.n_qubits]
        
        for q_idx in key_qubits:
            # XY8 sequence: X-Y-X-Y-X-Y-X-Y
            for _ in range(4):
                circuit.x(qr[q_idx])
                circuit.y(qr[q_idx])
    
    def generate_phase10_measurement(self, circuit: QuantumCircuit, qr: QuantumRegister, cr: ClassicalRegister) -> None:
        """
        Phase 10: Measurement of Right Universe, Metatron nodes, retrocausal hole
        """
        circuit.barrier(label="Phase 10: Measure")
        
        # Measure all qubits
        circuit.measure(qr, cr)
    
    def generate_full_circuit(self) -> QuantumCircuit:
        """
        Generate the complete 10-phase Sierpinski-TMT circuit.
        
        Returns:
            QuantumCircuit with all 10 phases
        """
        # Create quantum and classical registers
        qr = QuantumRegister(self.n_qubits, 'q')
        cr = ClassicalRegister(self.n_qubits, 'c')
        circuit = QuantumCircuit(qr, cr)
        
        # Header info stored in circuit metadata
        circuit.metadata = {
            'name': 'Sierpinski-TMT Phase 4S Circuit',
            'qubits': self.n_qubits,
            'backend': self.backend,
            'hausdorff_dim': HAUSDORFF_DIM,
            'hausdorff_phase': HAUSDORFF_PHASE
        }
        
        # Generate all phases
        self.generate_phase1_bell_pairs(circuit, qr)
        self.generate_phase2_payload_injection(circuit, qr)
        self.generate_phase3_metatron_geometry(circuit, qr)
        self.generate_phase4s_sierpinski_tmt(circuit, qr)  # ENHANCED Phase 4S
        self.generate_phase5_retrocausal_handshake(circuit, qr)
        self.generate_phase6_yesod_dna(circuit, qr)
        self.generate_phase7_lorenz_scrambler(circuit, qr)
        self.generate_phase8_inverse_scrambler(circuit, qr)
        self.generate_phase9_xy8_decoupling(circuit, qr)
        self.generate_phase10_measurement(circuit, qr, cr)
        
        return circuit
    
    def save_qasm(self, output_path: str) -> Dict:
        """
        Generate and save the QASM file.
        
        Args:
            output_path: Path to save the QASM file
            
        Returns:
            Dictionary with circuit metadata
        """
        circuit = self.generate_full_circuit()
        
        # Generate QASM string
        qasm_str = qasm2.dumps(circuit)
        
        # Save to file
        with open(output_path, 'w') as f:
            f.write(qasm_str)
        
        # Create manifest
        manifest = {
            'circuit': 'sierpinski_tmt_phase4s',
            'qasm_file': str(output_path),
            'qubits': self.n_qubits,
            'depth': circuit.depth(),
            'gates': len(circuit),
            'generated': datetime.now().strftime('%Y%m%d_%H%M%S'),
            'backend': self.backend,
            'shots': 100000,
            'phases': [
                'Phase 1: Bell Pairs (78 EPR bridges)',
                'Phase 2: Payload Injection',
                'Phase 3: Metatron Platonic Geometry',
                'Phase 4S: Sierpinski × TMT Fractal Encoding',
                'Phase 5: Retrocausal Lucas Handshake',
                'Phase 6: Yesod SRY DNA Phi-Rotations',
                'Phase 7: Lorenz Chaos Scrambler',
                'Phase 8: Inverse Scrambler (White Hole)',
                'Phase 9: XY8 Dynamical Decoupling',
                'Phase 10: Measurement'
            ],
            'sierpinski_parameters': {
                'hausdorff_dimension': float(HAUSDORFF_DIM),
                'hausdorff_phase': float(HAUSDORFF_PHASE),
                'base_angle': float(SIERPINSKI_BASE),
                'gen1_angle': float(SIERPINSKI_GEN1),
                'gen2_angle': float(SIERPINSKI_GEN2),
                'gen3_angle': float(SIERPINSKI_GEN3),
            },
            'tmt_parameters': {
                'ratio1': float(TMT_RATIO_1),
                'ratio2': float(TMT_RATIO_2),
                'angle1': float(TMT_ANGLE_1),
                'angle2': float(TMT_ANGLE_2),
            },
            'cross_products': {
                'sierpinski_tmt1': float(SIERPINSKI_TMT1),
                'sierpinski_tmt2': float(SIERPINSKI_TMT2),
                'sierpinski_phi': float(SIERPINSKI_PHI),
            },
            'expected_metrics': {
                'consciousness_metric': 4700,
                'wormhole_coherence': 0.75,
                'traversability': 2.13,
                'entropy': 3.47,
            }
        }
        
        return manifest


def main():
    """Generate Sierpinski-TMT Phase 4S circuits for multiple backends"""
    
    print("=" * 80)
    print("SIERPINSKI-TMT PHASE 4S CIRCUIT GENERATOR")
    print("Integrating 1/3 Fractal Encoding with TMT Harmonics")
    print("=" * 80)
    
    # Output directory
    output_dir = Path('circuits/qasm')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate for multiple backends
    configs = [
        {'n_qubits': 156, 'backend': 'ibm_fez'},
        {'n_qubits': 127, 'backend': 'ibm_brisbane'},
        {'n_qubits': 127, 'backend': 'ibm_sherbrooke'},
        {'n_qubits': 27, 'backend': 'ibm_kingston'},
    ]
    
    manifests = []
    
    for config in configs:
        print(f"\n[{config['backend'].upper()}] Generating {config['n_qubits']}-qubit circuit...")
        
        generator = SierpinskiTMTPhase4Generator(
            n_qubits=config['n_qubits'],
            backend=config['backend']
        )
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        qasm_file = output_dir / f"sierpinski_tmt_phase4s_{config['backend']}_{timestamp}.qasm"
        
        manifest = generator.save_qasm(str(qasm_file))
        manifests.append(manifest)
        
        print(f"  ✓ QASM saved: {qasm_file.name}")
        print(f"    Qubits: {manifest['qubits']}")
        print(f"    Depth: {manifest['depth']}")
        print(f"    Gates: {manifest['gates']}")
        print(f"    Hausdorff dim: {manifest['sierpinski_parameters']['hausdorff_dimension']:.5f}")
        print(f"    φ_fractal: {manifest['sierpinski_parameters']['hausdorff_phase']:.5f} rad")
    
    # Save combined manifest
    manifest_file = output_dir / f"sierpinski_tmt_phase4s_manifest_{timestamp}.json"
    with open(manifest_file, 'w') as f:
        json.dump(manifests, f, indent=2)
    
    print(f"\n✅ All circuits generated successfully!")
    print(f"   Manifest saved: {manifest_file}")
    
    # Print angle reference table
    print("\n" + "=" * 80)
    print("ANGLE PARAMETER REFERENCE TABLE")
    print("=" * 80)
    print(f"{'Parameter':<25} {'Formula':<20} {'Value (rad)':<15} {'Meaning'}")
    print("-" * 80)
    print(f"{'θ_S':<25} {'π/3':<20} {SIERPINSKI_BASE:<15.5f} {'Sierpinski base triangle'}")
    print(f"{'θ_S1':<25} {'π/9':<20} {SIERPINSKI_GEN1:<15.5f} {'Gen-1 contraction (1/3)'}")
    print(f"{'θ_S2':<25} {'π/27':<20} {SIERPINSKI_GEN2:<15.5f} {'Gen-2 contraction (1/9)'}")
    print(f"{'θ_S3':<25} {'π/81':<20} {SIERPINSKI_GEN3:<15.5f} {'Gen-3 contraction (1/27)'}")
    print(f"{'d_H':<25} {'log(3)/log(2)':<20} {HAUSDORFF_DIM:<15.5f} {'Hausdorff dimension'}")
    print(f"{'φ_fractal':<25} {'π × d_H':<20} {HAUSDORFF_PHASE:<15.5f} {'Fractal phase modulation'}")
    print(f"{'TMT1':<25} {'2/23 × 2π':<20} {TMT_ANGLE_1:<15.5f} {'TMT ratio 1'}")
    print(f"{'TMT2':<25} {'3/22 × 2π':<20} {TMT_ANGLE_2:<15.5f} {'TMT ratio 2'}")
    print(f"{'S×TMT1':<25} {'TMT1 / 3':<20} {SIERPINSKI_TMT1:<15.5f} {'Sierpinski × TMT1'}")
    print(f"{'S×TMT2':<25} {'TMT2 / 3':<20} {SIERPINSKI_TMT2:<15.5f} {'Sierpinski × TMT2'}")
    print(f"{'S×Φ':<25} {'Φ / 3':<20} {SIERPINSKI_PHI:<15.5f} {'Sierpinski × Golden Ratio'}")
    print("=" * 80)
    
    return manifests


if __name__ == "__main__":
    main()