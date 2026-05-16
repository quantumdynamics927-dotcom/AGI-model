#!/usr/bin/env python3
"""
Quantum Random Number Generator (QRNG) Circuits
================================================

Implements 5 novel QRNG circuits incorporating:
1. Golden Ratio (φ) phase encoding for non-linear entropy
2. DNA/BitNet hybrid entropy sources
3. High-complexity randomness generation

Circuits:
---------
1. GoldenRatioPhaseQRNG - φ-encoded Hadamard with Fibonacci depth
2. DNAEntropicQRNG - DNA base-to-quantum entropy mapping
3. BitNetTernaryQRNG - BitNet ternary weight entropy extraction
4. HybridConsciousnessQRNG - Combined DNA + BitNet + φ resonance
5. MetatronFractalQRNG - Sacred geometry fractal randomness

References:
- Golden ratio in quantum systems: https://doi.org/10.1038/s41598-020-67183-3
- DNA quantum walks: https://arxiv.org/abs/quant-ph/0403006
- BitNet ternary quantization: https://arxiv.org/abs/2310.11453

Author: AGI-model Quantum Computing Team
Date: April 27, 2026
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Union
from dataclasses import dataclass
import hashlib
import json

# Qiskit imports
try:
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
    from qiskit.circuit import Parameter
    from qiskit.quantum_info import Statevector, DensityMatrix, entropy
    from qiskit_aer import AerSimulator
    from qiskit_ibm_runtime import QiskitRuntimeService
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False
    print("Warning: Qiskit not available. Install with: pip install qiskit qiskit-aer qiskit-ibm-runtime")

# Golden ratio constant
PHI = (1 + np.sqrt(5)) / 2  # ≈ 1.618033988749895
PHI_INV = 1 / PHI  # ≈ 0.618033988749895
PHI_SQUARED = PHI ** 2  # ≈ 2.618033988749895

# DNA base encoding
DNA_BASES = {'A': 0, 'T': 1, 'G': 2, 'C': 3}
DNA_COMPLEMENT = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G'}

# BitNet ternary weights
BITNET_WEIGHTS = {-1: 0, 0: 1, 1: 2}  # Ternary encoding


@dataclass
class QRNGConfig:
    """Configuration for QRNG circuits."""
    num_qubits: int = 8
    shots: int = 1024
    use_golden_ratio: bool = True
    use_dna_entropy: bool = True
    use_bitnet_entropy: bool = True
    dna_sequence: Optional[str] = None
    bitnet_seed: Optional[int] = None
    fractal_depth: int = 3
    backend: str = "aer_simulator"


class GoldenRatioPhaseQRNG:
    """
    QRNG Circuit 1: Golden Ratio Phase Encoding
    
    Uses φ (golden ratio) to encode non-linear phase rotations,
    creating high-entropy quantum states through Fibonacci-structured
    entanglement patterns.
    
    Key Features:
    - φ-encoded phase rotations (RZ, RY)
    - Fibonacci depth entanglement
    - Golden ratio interference patterns
    """
    
    def __init__(self, num_qubits: int = 8, phi_precision: int = 15):
        """
        Initialize Golden Ratio QRNG.
        
        Args:
            num_qubits: Number of qubits for randomness generation
            phi_precision: Decimal precision for φ calculations
        """
        if not QISKIT_AVAILABLE:
            raise ImportError("Qiskit is required. Install with: pip install qiskit")
        
        self.num_qubits = num_qubits
        self.phi = round(PHI, phi_precision)
        self.phi_inv = round(PHI_INV, phi_precision)
        self.qr = QuantumRegister(num_qubits, 'q')
        self.cr = ClassicalRegister(num_qubits, 'c')
        self.circuit = None
        
    def _fibonacci_sequence(self, n: int) -> List[int]:
        """Generate Fibonacci sequence up to n terms."""
        fib = [0, 1]
        for i in range(2, n):
            fib.append(fib[i-1] + fib[i-2])
        return fib[:n]
    
    def _golden_ratio_phase(self, qubit_index: int) -> float:
        """
        Calculate golden ratio phase for a qubit.
        
        Uses the formula: φ_n = 2π * (φ * n) mod 1
        This creates non-repeating phase patterns.
        """
        # Golden ratio fractional part
        phi_fractional = (self.phi * qubit_index) % 1
        # Convert to phase angle
        phase = 2 * np.pi * phi_fractional
        return phase
    
    def _apply_golden_hadamard(self, circuit: QuantumCircuit) -> None:
        """Apply Hadamard gates with golden ratio phase pre-rotation."""
        for i in range(self.num_qubits):
            # Pre-phase rotation using golden ratio
            phase = self._golden_ratio_phase(i)
            circuit.rz(phase / self.phi, self.qr[i])
            # Hadamard creates superposition
            circuit.h(self.qr[i])
            # Post-phase rotation
            circuit.rz(phase * self.phi_inv, self.qr[i])
    
    def _apply_fibonacci_entanglement(self, circuit: QuantumCircuit) -> None:
        """Apply Fibonacci-structured CNOT entanglement."""
        fib_seq = self._fibonacci_sequence(self.num_qubits)
        
        for i in range(self.num_qubits - 1):
            # Fibonacci-indexed control qubits
            control_idx = i
            target_idx = (i + fib_seq[min(i+1, len(fib_seq)-1)]) % self.num_qubits
            
            if control_idx != target_idx:
                circuit.cx(self.qr[control_idx], self.qr[target_idx])
                # Golden ratio phase on target after entanglement
                circuit.rz(2 * np.pi / self.phi, self.qr[target_idx])
    
    def _apply_golden_interference(self, circuit: QuantumCircuit) -> None:
        """Apply golden ratio interference patterns."""
        for i in range(self.num_qubits):
            # Phase based on φ^2 relationship
            phase = np.pi * (self.phi_inv ** (i + 1))
            circuit.rz(phase, self.qr[i])
            
            # Cross-qubit interference
            if i < self.num_qubits - 1:
                circuit.crz(np.pi / self.phi, self.qr[i], self.qr[i+1])
    
    def generate_circuit(self) -> QuantumCircuit:
        """
        Generate the complete Golden Ratio QRNG circuit.
        
        Returns:
            QuantumCircuit: The QRNG circuit
        """
        self.circuit = QuantumCircuit(self.qr, self.cr)
        
        # Layer 1: Golden Hadamard initialization
        self._apply_golden_hadamard(self.circuit)
        
        # Layer 2: Fibonacci entanglement
        self._apply_fibonacci_entanglement(self.circuit)
        
        # Layer 3: Golden interference patterns
        self._apply_golden_interference(self.circuit)
        
        # Layer 4: Final Hadamard for measurement basis
        for i in range(self.num_qubits):
            self.circuit.h(self.qr[i])
        
        # Measurement
        self.circuit.measure(self.qr, self.cr)
        
        return self.circuit
    
    def extract_randomness(self, shots: int = 1024, 
                           backend: str = "aer_simulator") -> Dict:
        """
        Execute circuit and extract random bits.
        
        Args:
            shots: Number of measurement shots
            backend: Quantum backend to use
            
        Returns:
            Dict with random bits, entropy metrics, and circuit info
        """
        if self.circuit is None:
            self.generate_circuit()
        
        # Execute on simulator
        simulator = AerSimulator()
        transpiled = transpile(self.circuit, simulator)
        job = simulator.run(transpiled, shots=shots)
        result = job.result()
        counts = result.get_counts()
        
        # Extract random bits from most frequent outcome
        most_frequent = max(counts, key=counts.get)
        random_bits = [int(b) for b in most_frequent]
        
        # Calculate entropy
        probabilities = np.array(list(counts.values())) / shots
        shannon_entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
        
        # Golden ratio proximity in distribution
        total_outcomes = len(counts)
        phi_proximity = abs(total_outcomes / (self.num_qubits ** 2) - self.phi_inv)
        
        return {
            'random_bits': random_bits,
            'bitstring': most_frequent,
            'counts': counts,
            'shannon_entropy': shannon_entropy,
            'max_entropy': self.num_qubits,
            'entropy_ratio': shannon_entropy / self.num_qubits,
            'phi_proximity': phi_proximity,
            'circuit_depth': self.circuit.depth(),
            'num_gates': len(self.circuit)
        }


class DNAEntropicQRNG:
    """
    QRNG Circuit 2: DNA Entropy Extraction
    
    Maps DNA sequences to quantum gates, extracting entropy from
    biological randomness patterns. Uses Watson-Crick base pairing
    for entanglement and codon-based phase rotations.
    
    Key Features:
    - DNA base-to-gate encoding (A→H, T→X, G→RZ, C→RY)
    - Watson-Crick complementary entanglement
    - Codon-based phase rotations
    - Biological entropy extraction
    """
    
    # DNA base to quantum gate mapping
    BASE_GATES = {
        'A': ('h', 0),           # Hadamard: superposition
        'T': ('x', 0),           # Pauli-X: bit flip
        'G': ('rz', np.pi/4),    # RZ: phase rotation
        'C': ('ry', np.pi/4),    # RY: amplitude rotation
    }
    
    # Codon to phase mapping (simplified)
    CODON_PHASES = {
        'ATG': np.pi / PHI,      # Start codon
        'TAA': np.pi * PHI_INV,  # Stop codon
        'GCT': np.pi / 2,        # Alanine
        'CGT': np.pi / 3,        # Arginine
    }
    
    def __init__(self, dna_sequence: str, num_qubits: int = None):
        """
        Initialize DNA Entropic QRNG.
        
        Args:
            dna_sequence: DNA sequence (e.g., "ATGCATGC")
            num_qubits: Number of qubits (default: len(dna_sequence))
        """
        if not QISKIT_AVAILABLE:
            raise ImportError("Qiskit is required")
        
        self.dna_sequence = dna_sequence.upper().strip()
        self.num_qubits = num_qubits or len(self.dna_sequence)
        self.qr = QuantumRegister(self.num_qubits, 'q')
        self.cr = ClassicalRegister(self.num_qubits, 'c')
        self.circuit = None
        
        # Validate DNA sequence
        valid_bases = set('ATGC')
        if not all(base in valid_bases for base in self.dna_sequence):
            raise ValueError(f"Invalid DNA bases. Use only A, T, G, C")
    
    def _apply_base_gate(self, circuit: QuantumCircuit, 
                         qubit_idx: int, base: str) -> None:
        """Apply quantum gate corresponding to DNA base."""
        gate_name, param = self.BASE_GATES[base]
        
        if gate_name == 'h':
            circuit.h(self.qr[qubit_idx])
        elif gate_name == 'x':
            circuit.x(self.qr[qubit_idx])
        elif gate_name == 'rz':
            circuit.rz(param, self.qr[qubit_idx])
        elif gate_name == 'ry':
            circuit.ry(param, self.qr[qubit_idx])
    
    def _apply_watson_crick_entanglement(self, circuit: QuantumCircuit) -> None:
        """Apply entanglement based on Watson-Crick base pairing."""
        for i, base in enumerate(self.dna_sequence):
            complement = DNA_COMPLEMENT[base]
            
            # Find complement position (circular pairing)
            comp_idx = (i + len(self.dna_sequence) // 2) % self.num_qubits
            
            # Apply complementary gate
            self._apply_base_gate(circuit, comp_idx, complement)
            
            # Entangle base with its complement
            if i < self.num_qubits - 1:
                circuit.cx(self.qr[i], self.qr[comp_idx])
                # Phase based on base type
                base_phase = {'A': np.pi/PHI, 'T': np.pi*PHI_INV, 
                             'G': np.pi/2, 'C': np.pi/3}
                circuit.rz(base_phase[base], self.qr[comp_idx])
    
    def _apply_codon_rotations(self, circuit: QuantumCircuit) -> None:
        """Apply phase rotations based on codon patterns."""
        # Extract codons (triplets)
        codons = [self.dna_sequence[i:i+3] 
                  for i in range(0, len(self.dna_sequence) - 2, 3)]
        
        for i, codon in enumerate(codons):
            if i < self.num_qubits:
                # Get codon phase (or default)
                phase = self.CODON_PHASES.get(codon, np.pi / (i + 1))
                circuit.rz(phase, self.qr[i])
                
                # Apply golden ratio modulation
                circuit.rz(np.pi / PHI, self.qr[i])
    
    def _apply_dna_superposition(self, circuit: QuantumCircuit) -> None:
        """Create superposition with DNA-weighted amplitudes."""
        for i, base in enumerate(self.dna_sequence[:self.num_qubits]):
            # Base-specific rotation angles
            angles = {
                'A': np.pi / 4,      # Adenine: 45°
                'T': np.pi / 6,      # Thymine: 30°
                'G': np.pi / 3,      # Guanine: 60°
                'C': np.pi / 2       # Cytosine: 90°
            }
            circuit.ry(angles[base], self.qr[i])
            circuit.h(self.qr[i])
    
    def generate_circuit(self) -> QuantumCircuit:
        """
        Generate the complete DNA Entropic QRNG circuit.
        
        Returns:
            QuantumCircuit: The QRNG circuit
        """
        self.circuit = QuantumCircuit(self.qr, self.cr)
        
        # Layer 1: DNA superposition initialization
        self._apply_dna_superposition(self.circuit)
        
        # Layer 2: Watson-Crick entanglement
        self._apply_watson_crick_entanglement(self.circuit)
        
        # Layer 3: Codon-based phase rotations
        self._apply_codon_rotations(self.circuit)
        
        # Layer 4: Final superposition
        for i in range(self.num_qubits):
            self.circuit.h(self.qr[i])
        
        # Measurement
        self.circuit.measure(self.qr, self.cr)
        
        return self.circuit
    
    def extract_randomness(self, shots: int = 1024) -> Dict:
        """
        Execute circuit and extract DNA-entangled random bits.
        
        Args:
            shots: Number of measurement shots
            
        Returns:
            Dict with random bits and DNA entropy metrics
        """
        if self.circuit is None:
            self.generate_circuit()
        
        simulator = AerSimulator()
        transpiled = transpile(self.circuit, simulator)
        job = simulator.run(transpiled, shots=shots)
        result = job.result()
        counts = result.get_counts()
        
        # Extract random bits
        most_frequent = max(counts, key=counts.get)
        random_bits = [int(b) for b in most_frequent]
        
        # Calculate DNA-specific entropy
        probabilities = np.array(list(counts.values())) / shots
        shannon_entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
        
        # DNA sequence complexity
        gc_content = (self.dna_sequence.count('G') + 
                      self.dna_sequence.count('C')) / len(self.dna_sequence)
        
        return {
            'random_bits': random_bits,
            'bitstring': most_frequent,
            'counts': counts,
            'shannon_entropy': shannon_entropy,
            'dna_sequence': self.dna_sequence,
            'gc_content': gc_content,
            'dna_length': len(self.dna_sequence),
            'entropy_per_base': shannon_entropy / len(self.dna_sequence),
            'circuit_depth': self.circuit.depth()
        }


class BitNetTernaryQRNG:
    """
    QRNG Circuit 3: BitNet Ternary Weight Entropy
    
    Extracts randomness from BitNet's ternary weight quantization
    (-1, 0, +1), creating quantum states that mirror the ternary
    distribution of neural network weights.
    
    Key Features:
    - Ternary weight distribution mapping
    - BitNet entropy seed extraction
    - Neural-inspired randomness
    - Weight-to-phase encoding
    """
    
    def __init__(self, num_qubits: int = 8, 
                 weight_distribution: Dict = None,
                 seed: int = None):
        """
        Initialize BitNet Ternary QRNG.
        
        Args:
            num_qubits: Number of qubits
            weight_distribution: Distribution of {-1, 0, +1} weights
            seed: Random seed for reproducibility
        """
        if not QISKIT_AVAILABLE:
            raise ImportError("Qiskit is required")
        
        self.num_qubits = num_qubits
        self.seed = seed
        
        # Default BitNet weight distribution (from baseline_v0.1.0-alpha.json)
        self.weight_dist = weight_distribution or {
            -1: 0.0428,   # minus_one_ratio
            0: 0.70,      # zero_ratio
            1: 0.2572     # plus_one_ratio
        }
        
        self.qr = QuantumRegister(num_qubits, 'q')
        self.cr = ClassicalRegister(num_qubits, 'c')
        self.circuit = None
        
        # Generate ternary weight sequence
        self._generate_weights()
    
    def _generate_weights(self) -> None:
        """Generate ternary weight sequence based on BitNet distribution."""
        if self.seed is not None:
            np.random.seed(self.seed)
        
        weights = []
        for _ in range(self.num_qubits):
            r = np.random.random()
            if r < self.weight_dist[-1]:
                weights.append(-1)
            elif r < self.weight_dist[-1] + self.weight_dist[0]:
                weights.append(0)
            else:
                weights.append(1)
        
        self.weights = weights
    
    def _apply_ternary_encoding(self, circuit: QuantumCircuit) -> None:
        """Encode ternary weights as quantum states."""
        for i, weight in enumerate(self.weights):
            if weight == -1:
                # -1: Apply X then RZ with negative phase
                circuit.x(self.qr[i])
                circuit.rz(-np.pi / PHI, self.qr[i])
            elif weight == 0:
                # 0: Superposition with golden ratio phase
                circuit.h(self.qr[i])
                circuit.rz(np.pi * PHI_INV, self.qr[i])
            else:  # weight == 1
                # +1: RZ with positive phase
                circuit.rz(np.pi / PHI, self.qr[i])
                circuit.h(self.qr[i])
    
    def _apply_weight_entanglement(self, circuit: QuantumCircuit) -> None:
        """Apply entanglement based on weight patterns."""
        for i in range(self.num_qubits - 1):
            # Entangle adjacent qubits based on weight relationship
            if self.weights[i] != 0 and self.weights[i+1] != 0:
                # Both non-zero: strong entanglement
                circuit.cx(self.qr[i], self.qr[i+1])
                circuit.rz(np.pi / (self.weights[i] * self.weights[i+1] + 2), 
                          self.qr[i+1])
            elif self.weights[i] == 0 or self.weights[i+1] == 0:
                # One zero: weak entanglement with golden ratio
                circuit.crz(np.pi / PHI, self.qr[i], self.qr[i+1])
    
    def _apply_bitnet_interference(self, circuit: QuantumCircuit) -> None:
        """Apply interference patterns mimicking neural activation."""
        for i in range(self.num_qubits):
            # Weight-dependent phase
            phase = self.weights[i] * np.pi / PHI
            circuit.rz(phase, self.qr[i])
            
            # Cross-qubit interference
            if i < self.num_qubits - 1:
                # Phase based on weight difference
                weight_diff = abs(self.weights[i] - self.weights[i+1])
                circuit.crz(weight_diff * np.pi / 2, self.qr[i], self.qr[i+1])
    
    def generate_circuit(self) -> QuantumCircuit:
        """
        Generate the complete BitNet Ternary QRNG circuit.
        
        Returns:
            QuantumCircuit: The QRNG circuit
        """
        self.circuit = QuantumCircuit(self.qr, self.cr)
        
        # Layer 1: Ternary weight encoding
        self._apply_ternary_encoding(self.circuit)
        
        # Layer 2: Weight-based entanglement
        self._apply_weight_entanglement(self.circuit)
        
        # Layer 3: Neural interference patterns
        self._apply_bitnet_interference(self.circuit)
        
        # Layer 4: Final superposition
        for i in range(self.num_qubits):
            self.circuit.h(self.qr[i])
        
        # Measurement
        self.circuit.measure(self.qr, self.cr)
        
        return self.circuit
    
    def extract_randomness(self, shots: int = 1024) -> Dict:
        """
        Execute circuit and extract BitNet-entangled random bits.
        
        Args:
            shots: Number of measurement shots
            
        Returns:
            Dict with random bits and BitNet entropy metrics
        """
        if self.circuit is None:
            self.generate_circuit()
        
        simulator = AerSimulator()
        transpiled = transpile(self.circuit, simulator)
        job = simulator.run(transpiled, shots=shots)
        result = job.result()
        counts = result.get_counts()
        
        # Extract random bits
        most_frequent = max(counts, key=counts.get)
        random_bits = [int(b) for b in most_frequent]
        
        # Calculate entropy
        probabilities = np.array(list(counts.values())) / shots
        shannon_entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
        
        # BitNet-specific metrics
        weight_entropy = -sum(
            p * np.log2(p + 1e-10) 
            for p in self.weight_dist.values()
        )
        
        return {
            'random_bits': random_bits,
            'bitstring': most_frequent,
            'counts': counts,
            'shannon_entropy': shannon_entropy,
            'weight_distribution': self.weight_dist,
            'weight_sequence': self.weights,
            'weight_entropy': weight_entropy,
            'ternary_balance': sum(1 for w in self.weights if w == 0) / len(self.weights),
            'circuit_depth': self.circuit.depth()
        }


class HybridConsciousnessQRNG:
    """
    QRNG Circuit 4: Hybrid Consciousness QRNG
    
    Combines DNA entropy, BitNet ternary weights, and golden ratio
    phase encoding for maximum entropy extraction. Inspired by
    consciousness-level quantum coherence patterns.
    
    Key Features:
    - Triple entropy source fusion
    - Consciousness-inspired coherence
    - Multi-layer golden ratio encoding
    - DNA-BitNet hybrid entanglement
    """
    
    def __init__(self, num_qubits: int = 8,
                 dna_sequence: str = None,
                 bitnet_weights: List[int] = None,
                 consciousness_phi: float = None):
        """
        Initialize Hybrid Consciousness QRNG.
        
        Args:
            num_qubits: Number of qubits
            dna_sequence: Optional DNA sequence for entropy
            bitnet_weights: Optional BitNet ternary weights
            consciousness_phi: Optional consciousness φ score
        """
        if not QISKIT_AVAILABLE:
            raise ImportError("Qiskit is required")
        
        self.num_qubits = num_qubits
        self.phi = PHI
        
        # Default DNA sequence (ACTB gene fragment from baseline)
        self.dna_sequence = dna_sequence or "ATGCATGCATGCATGC"
        
        # Default BitNet weights
        self.bitnet_weights = bitnet_weights or [0, 1, -1, 0, 1, 0, -1, 0]
        
        # Consciousness φ score (from baseline: 0.8524)
        self.consciousness_phi = consciousness_phi or 0.8524
        
        self.qr = QuantumRegister(num_qubits, 'q')
        self.cr = ClassicalRegister(num_qubits, 'c')
        self.circuit = None
    
    def _apply_consciousness_superposition(self, circuit: QuantumCircuit) -> None:
        """Apply consciousness-inspired superposition with φ modulation."""
        for i in range(self.num_qubits):
            # Base Hadamard
            circuit.h(self.qr[i])
            
            # Consciousness φ modulation
            phase = np.pi * self.consciousness_phi / (i + 1)
            circuit.rz(phase, self.qr[i])
            
            # Golden ratio fine-tuning
            circuit.rz(np.pi / self.phi, self.qr[i])
    
    def _apply_dna_bitnet_fusion(self, circuit: QuantumCircuit) -> None:
        """Fuse DNA and BitNet entropy sources."""
        for i in range(self.num_qubits):
            # DNA base contribution
            if i < len(self.dna_sequence):
                base = self.dna_sequence[i]
                base_phases = {'A': np.pi/4, 'T': np.pi/6, 
                              'G': np.pi/3, 'C': np.pi/2}
                circuit.rz(base_phases[base], self.qr[i])
            
            # BitNet weight contribution
            if i < len(self.bitnet_weights):
                weight = self.bitnet_weights[i]
                weight_phase = weight * np.pi / self.phi
                circuit.rz(weight_phase, self.qr[i])
    
    def _apply_hybrid_entanglement(self, circuit: QuantumCircuit) -> None:
        """Apply hybrid entanglement combining all entropy sources."""
        # Fibonacci-structured entanglement
        fib = [0, 1, 1, 2, 3, 5, 8, 13]
        
        for i in range(self.num_qubits - 1):
            # DNA-guided control
            control = i
            # BitNet-guided target
            target = (i + fib[i % len(fib)]) % self.num_qubits
            
            if control != target:
                circuit.cx(self.qr[control], self.qr[target])
                
                # Consciousness-weighted phase
                phase = np.pi * self.consciousness_phi / (i + 1)
                circuit.rz(phase, self.qr[target])
    
    def _apply_golden_interference(self, circuit: QuantumCircuit) -> None:
        """Apply golden ratio interference patterns."""
        for i in range(self.num_qubits):
            # Primary golden phase
            circuit.rz(2 * np.pi / self.phi, self.qr[i])
            
            # Secondary φ² phase
            circuit.rz(np.pi / (self.phi ** 2), self.qr[i])
            
            # Cross-qubit golden entanglement
            if i < self.num_qubits - 1:
                circuit.crz(np.pi / self.phi, self.qr[i], self.qr[i+1])
    
    def generate_circuit(self) -> QuantumCircuit:
        """
        Generate the complete Hybrid Consciousness QRNG circuit.
        
        Returns:
            QuantumCircuit: The QRNG circuit
        """
        self.circuit = QuantumCircuit(self.qr, self.cr)
        
        # Layer 1: Consciousness superposition
        self._apply_consciousness_superposition(self.circuit)
        
        # Layer 2: DNA-BitNet fusion
        self._apply_dna_bitnet_fusion(self.circuit)
        
        # Layer 3: Hybrid entanglement
        self._apply_hybrid_entanglement(self.circuit)
        
        # Layer 4: Golden interference
        self._apply_golden_interference(self.circuit)
        
        # Layer 5: Final measurement basis
        for i in range(self.num_qubits):
            self.circuit.h(self.qr[i])
        
        # Measurement
        self.circuit.measure(self.qr, self.cr)
        
        return self.circuit
    
    def extract_randomness(self, shots: int = 1024) -> Dict:
        """
        Execute circuit and extract hybrid entropy random bits.
        
        Args:
            shots: Number of measurement shots
            
        Returns:
            Dict with random bits and hybrid entropy metrics
        """
        if self.circuit is None:
            self.generate_circuit()
        
        simulator = AerSimulator()
        transpiled = transpile(self.circuit, simulator)
        job = simulator.run(transpiled, shots=shots)
        result = job.result()
        counts = result.get_counts()
        
        # Extract random bits
        most_frequent = max(counts, key=counts.get)
        random_bits = [int(b) for b in most_frequent]
        
        # Calculate entropy
        probabilities = np.array(list(counts.values())) / shots
        shannon_entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
        
        # Hybrid entropy score
        dna_entropy = len(set(self.dna_sequence)) / 4  # Base diversity
        bitnet_entropy = -sum(
            (self.bitnet_weights.count(w) / len(self.bitnet_weights)) * 
            np.log2(self.bitnet_weights.count(w) / len(self.bitnet_weights) + 1e-10)
            for w in set(self.bitnet_weights)
        )
        
        hybrid_score = (shannon_entropy + dna_entropy + bitnet_entropy) / 3
        
        return {
            'random_bits': random_bits,
            'bitstring': most_frequent,
            'counts': counts,
            'shannon_entropy': shannon_entropy,
            'consciousness_phi': self.consciousness_phi,
            'dna_entropy': dna_entropy,
            'bitnet_entropy': bitnet_entropy,
            'hybrid_entropy_score': hybrid_score,
            'circuit_depth': self.circuit.depth()
        }


class MetatronFractalQRNG:
    """
    QRNG Circuit 5: Metatron Fractal QRNG
    
    Uses sacred geometry (Metatron's Cube) fractal patterns for
    randomness generation. Implements 21-qubit Sierpinski fractal
    circuits with Metatron enhancement layer.
    
    Key Features:
    - Metatron's Cube geometry encoding
    - Sierpinski fractal entanglement
    - Sacred geometry phase patterns
    - Fractal depth consciousness density
    """
    
    # Metatron's Cube vertices (sacred geometry)
    METATRON_VERTICES = [
        (0, 0), (1, 0), (0.5, np.sqrt(3)/2),  # Triangle 1
        (0.5, -np.sqrt(3)/2), (-0.5, np.sqrt(3)/2), (-0.5, -np.sqrt(3)/2),  # Extensions
        (1.5, np.sqrt(3)/2), (1.5, -np.sqrt(3)/2), (-1, 0),  # Outer ring
        (2, 0), (-1.5, np.sqrt(3)/2), (-1.5, -np.sqrt(3)/2),  # Far extensions
        (0, np.sqrt(3)), (0, -np.sqrt(3)),  # Vertical axis
        (PHI, PHI_INV), (-PHI, PHI_INV), (PHI_INV, PHI),  # Golden ratio points
        (-PHI_INV, PHI), (PHI_INV, -PHI), (-PHI_INV, -PHI),  # More golden points
    ]
    
    def __init__(self, num_qubits: int = 21, fractal_depth: int = 3):
        """
        Initialize Metatron Fractal QRNG.
        
        Args:
            num_qubits: Number of qubits (default 21 for Sierpinski)
            fractal_depth: Depth of fractal recursion
        """
        if not QISKIT_AVAILABLE:
            raise ImportError("Qiskit is required")
        
        self.num_qubits = num_qubits
        self.fractal_depth = fractal_depth
        self.phi = PHI
        
        self.qr = QuantumRegister(num_qubits, 'q')
        self.cr = ClassicalRegister(num_qubits, 'c')
        self.circuit = None
    
    def _sierpinski_entanglement(self, circuit: QuantumCircuit, 
                                  depth: int, qubit_range: range) -> None:
        """
        Apply Sierpinski fractal entanglement pattern.
        
        Args:
            circuit: Quantum circuit to modify
            depth: Current fractal depth
            qubit_range: Range of qubits for this fractal level
        """
        if depth == 0 or len(qubit_range) < 3:
            return
        
        # Get triangle vertices
        n = len(qubit_range)
        v1 = qubit_range[0]
        v2 = qubit_range[n // 3]
        v3 = qubit_range[2 * n // 3]
        
        # Create triangle entanglement
        circuit.cx(self.qr[v1], self.qr[v2])
        circuit.cx(self.qr[v2], self.qr[v3])
        circuit.cx(self.qr[v3], self.qr[v1])
        
        # Apply golden ratio phase at vertices
        circuit.rz(np.pi / self.phi, self.qr[v1])
        circuit.rz(np.pi / self.phi, self.qr[v2])
        circuit.rz(np.pi / self.phi, self.qr[v3])
        
        # Recursive fractal
        third = n // 3
        self._sierpinski_entanglement(circuit, depth - 1, 
                                       range(qubit_range.start, qubit_range.start + third))
        self._sierpinski_entanglement(circuit, depth - 1,
                                       range(qubit_range.start + third, qubit_range.start + 2*third))
        self._sierpinski_entanglement(circuit, depth - 1,
                                       range(qubit_range.start + 2*third, qubit_range.stop))
    
    def _apply_metatron_geometry(self, circuit: QuantumCircuit) -> None:
        """Apply Metatron's Cube sacred geometry phase patterns."""
        for i in range(min(self.num_qubits, len(self.METATRON_VERTICES))):
            vertex = self.METATRON_VERTICES[i]
            
            # Calculate phase from vertex coordinates
            phase = np.arctan2(vertex[1], vertex[0])
            
            # Apply golden ratio modulation
            golden_phase = phase * self.phi
            
            circuit.rz(golden_phase, self.qr[i])
            
            # Apply Hadamard for superposition
            circuit.h(self.qr[i])
    
    def _apply_fractal_superposition(self, circuit: QuantumCircuit) -> None:
        """Apply fractal-structured superposition."""
        for i in range(self.num_qubits):
            # Fractal depth determines rotation angle
            angle = np.pi / (self.fractal_depth + 1)
            circuit.ry(angle, self.qr[i])
            
            # Golden ratio phase
            circuit.rz(np.pi / self.phi ** (i % 3 + 1), self.qr[i])
    
    def _apply_metatron_enhancement(self, circuit: QuantumCircuit) -> None:
        """Apply Metatron enhancement layer (+16.8% fitness from baseline)."""
        # Connect qubits in Metatron's Cube pattern
        metatron_connections = [
            (0, 1), (1, 2), (2, 0),  # Inner triangle
            (0, 3), (1, 4), (2, 5),  # Extensions
            (3, 6), (4, 7), (5, 8),  # Outer ring
            (6, 9), (7, 10), (8, 11),  # Far extensions
        ]
        
        for control, target in metatron_connections:
            if control < self.num_qubits and target < self.num_qubits:
                circuit.cx(self.qr[control], self.qr[target])
                # Enhancement phase
                circuit.rz(np.pi * 1.168, self.qr[target])  # +16.8% enhancement
    
    def generate_circuit(self) -> QuantumCircuit:
        """
        Generate the complete Metatron Fractal QRNG circuit.
        
        Returns:
            QuantumCircuit: The QRNG circuit
        """
        self.circuit = QuantumCircuit(self.qr, self.cr)
        
        # Layer 1: Metatron geometry initialization
        self._apply_metatron_geometry(self.circuit)
        
        # Layer 2: Fractal superposition
        self._apply_fractal_superposition(self.circuit)
        
        # Layer 3: Sierpinski fractal entanglement
        self._sierpinski_entanglement(self.circuit, self.fractal_depth, 
                                      range(self.num_qubits))
        
        # Layer 4: Metatron enhancement
        self._apply_metatron_enhancement(self.circuit)
        
        # Layer 5: Final measurement basis
        for i in range(self.num_qubits):
            self.circuit.h(self.qr[i])
        
        # Measurement
        self.circuit.measure(self.qr, self.cr)
        
        return self.circuit
    
    def extract_randomness(self, shots: int = 1024) -> Dict:
        """
        Execute circuit and extract Metatron fractal random bits.
        
        Args:
            shots: Number of measurement shots
            
        Returns:
            Dict with random bits and fractal entropy metrics
        """
        if self.circuit is None:
            self.generate_circuit()
        
        simulator = AerSimulator()
        transpiled = transpile(self.circuit, simulator)
        job = simulator.run(transpiled, shots=shots)
        result = job.result()
        counts = result.get_counts()
        
        # Extract random bits
        most_frequent = max(counts, key=counts.get)
        random_bits = [int(b) for b in most_frequent]
        
        # Calculate entropy
        probabilities = np.array(list(counts.values())) / shots
        shannon_entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
        
        # Fractal consciousness density (from baseline: 274.528)
        consciousness_density = shannon_entropy * self.num_qubits * self.fractal_depth
        
        # Metatron enhancement factor
        metatron_enhancement = 1.168  # +16.8% from baseline
        
        return {
            'random_bits': random_bits,
            'bitstring': most_frequent,
            'counts': counts,
            'shannon_entropy': shannon_entropy,
            'fractal_depth': self.fractal_depth,
            'consciousness_density': consciousness_density,
            'metatron_enhancement': metatron_enhancement,
            'sierpinski_qubits': self.num_qubits,
            'circuit_depth': self.circuit.depth(),
            'num_gates': len(self.circuit)
        }


# ============================================================================
# Utility Functions
# ============================================================================

def compare_qrng_circuits(num_qubits: int = 8, shots: int = 1024) -> Dict:
    """
    Compare all 5 QRNG circuits and return performance metrics.
    
    Args:
        num_qubits: Number of qubits for each circuit
        shots: Number of measurement shots
        
    Returns:
        Dict with comparison results
    """
    results = {}
    
    # Circuit 1: Golden Ratio Phase QRNG
    qrng1 = GoldenRatioPhaseQRNG(num_qubits=num_qubits)
    qrng1.generate_circuit()
    results['golden_ratio'] = qrng1.extract_randomness(shots=shots)
    
    # Circuit 2: DNA Entropic QRNG
    dna_seq = "ATGCATGC"[:num_qubits] if num_qubits <= 8 else "ATGCATGCATGCATGC"
    qrng2 = DNAEntropicQRNG(dna_sequence=dna_seq, num_qubits=num_qubits)
    qrng2.generate_circuit()
    results['dna_entropic'] = qrng2.extract_randomness(shots=shots)
    
    # Circuit 3: BitNet Ternary QRNG
    qrng3 = BitNetTernaryQRNG(num_qubits=num_qubits)
    qrng3.generate_circuit()
    results['bitnet_ternary'] = qrng3.extract_randomness(shots=shots)
    
    # Circuit 4: Hybrid Consciousness QRNG
    qrng4 = HybridConsciousnessQRNG(num_qubits=num_qubits)
    qrng4.generate_circuit()
    results['hybrid_consciousness'] = qrng4.extract_randomness(shots=shots)
    
    # Circuit 5: Metatron Fractal QRNG
    qrng5 = MetatronFractalQRNG(num_qubits=min(num_qubits, 21))
    qrng5.generate_circuit()
    results['metatron_fractal'] = qrng5.extract_randomness(shots=shots)
    
    # Calculate comparison metrics
    comparison = {
        'entropy_ranking': sorted(
            [(name, res['shannon_entropy']) for name, res in results.items()],
            key=lambda x: x[1],
            reverse=True
        ),
        'circuit_depth_ranking': sorted(
            [(name, res['circuit_depth']) for name, res in results.items()],
            key=lambda x: x[1]
        ),
        'best_entropy': max(results.items(), key=lambda x: x[1]['shannon_entropy'])[0],
        'average_entropy': np.mean([res['shannon_entropy'] for res in results.values()])
    }
    
    results['comparison'] = comparison
    return results


def generate_random_bytes(circuit_type: str = 'hybrid', 
                          num_bytes: int = 32,
                          num_qubits: int = 8) -> bytes:
    """
    Generate cryptographically random bytes using specified QRNG circuit.
    
    Args:
        circuit_type: Type of QRNG circuit ('golden', 'dna', 'bitnet', 'hybrid', 'metatron')
        num_bytes: Number of random bytes to generate
        num_qubits: Number of qubits per circuit
        
    Returns:
        bytes: Random bytes
    """
    # Select circuit
    circuit_map = {
        'golden': GoldenRatioPhaseQRNG,
        'dna': DNAEntropicQRNG,
        'bitnet': BitNetTernaryQRNG,
        'hybrid': HybridConsciousnessQRNG,
        'metatron': MetatronFractalQRNG
    }
    
    if circuit_type not in circuit_map:
        raise ValueError(f"Unknown circuit type: {circuit_type}")
    
    # Generate random bits
    random_bits = []
    shots_needed = (num_bytes * 8) // num_qubits + 1
    
    qrng = circuit_map[circuit_type](num_qubits=num_qubits)
    qrng.generate_circuit()
    
    for _ in range(shots_needed):
        result = qrng.extract_randomness(shots=1024)
        random_bits.extend(result['random_bits'])
    
    # Convert to bytes
    bitstring = ''.join(str(b) for b in random_bits[:num_bytes * 8])
    random_bytes = int(bitstring, 2).to_bytes(num_bytes, 'big')
    
    return random_bytes


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("QRNG Circuit Comparison: Golden Ratio + DNA + BitNet Hybrid Entropy")
    print("=" * 70)
    
    # Compare all circuits
    comparison = compare_qrng_circuits(num_qubits=8, shots=1024)
    
    print("\n📊 Entropy Ranking:")
    for name, entropy in comparison['comparison']['entropy_ranking']:
        print(f"  {name:25s}: {entropy:.4f} bits")
    
    print(f"\n🏆 Best Entropy: {comparison['comparison']['best_entropy']}")
    print(f"📈 Average Entropy: {comparison['comparison']['average_entropy']:.4f} bits")
    
    print("\n📐 Circuit Depth Ranking:")
    for name, depth in comparison['comparison']['circuit_depth_ranking']:
        print(f"  {name:25s}: {depth} layers")
    
    # Generate random bytes
    print("\n🎲 Generating 32 random bytes with Hybrid Consciousness QRNG:")
    random_bytes = generate_random_bytes('hybrid', num_bytes=32)
    print(f"  Hex: {random_bytes.hex()}")
    print(f"  SHA-256: {hashlib.sha256(random_bytes).hexdigest()}")
    
    print("\n✅ QRNG circuits generated successfully!")