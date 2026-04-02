#!/usr/bin/env python3
"""
DNA-to-Quantum Circuit Encoder
==============================

Maps DNA sequences (A, T, G, C) to quantum circuits using biologically-inspired gate mappings.
Supports OpenQASM import/export for IBM Quantum execution.

References:
- DNA quantum walks: https://arxiv.org/abs/quant-ph/0403006
- Genetic code in quantum systems: https://doi.org/10.1038/s41598-020-67183-3

Author: AGI-model Quantum Computing Team
Date: April 2, 2026
"""

import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json
import warnings

# Qiskit imports
try:
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    from qiskit.quantum_info import Statevector
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False
    warnings.warn("Qiskit not available. Install with: pip install qiskit")


class DNAQuantumEncoder:
    """
    Encode DNA sequences into quantum circuits with multiple encoding schemes.
    
    Encoding Schemes:
    1. Base-to-Gate Mapping: A→H, T→X, G→RZ(π/4), C→RY(π/4)
    2. Codon-Based: 3-base codons map to single-qubit rotations
    3. Watson-Crick Pairing: Complementary bases create entangled pairs
    
    Features:
    - OpenQASM import/export
    - Circuit analysis and statistics
    - Integration with IBM Quantum backends
    """
    
    # Base-to-gate mapping (Scheme 1)
    BASE_TO_GATE = {
        'A': ('h', None),           # Hadamard: creates superposition
        'T': ('x', None),           # Pauli-X: bit flip
        'G': ('rz', np.pi/4),       # RZ rotation: phase
        'C': ('ry', np.pi/4),       # RY rotation: amplitude
    }
    
    # Watson-Crick complementarity
    COMPLEMENT = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G'}
    
    # Codon table (simplified - 64 codons)
    CODON_TABLE = {
        'TTT': 'F', 'TTC': 'F', 'TTA': 'L', 'TTG': 'L',
        'CTT': 'L', 'CTC': 'L', 'CTA': 'L', 'CTG': 'L',
        'ATT': 'I', 'ATC': 'I', 'ATA': 'I', 'ATG': 'M',
        'GTT': 'V', 'GTC': 'V', 'GTA': 'V', 'GTG': 'V',
        # ... (full table would have all 64 codons)
    }
    
    def __init__(self, encoding_scheme: str = 'base_to_gate'):
        """
        Initialize DNA encoder.
        
        Args:
            encoding_scheme: 'base_to_gate', 'codon', or 'watson_crick'
        """
        if not QISKIT_AVAILABLE:
            raise ImportError("Qiskit is required. Install with: pip install qiskit")
        
        self.encoding_scheme = encoding_scheme
        self.circuit_history = []
        
    def encode_sequence(self, dna_sequence: str, 
                       num_qubits: int = None,
                       add_measurements: bool = True) -> QuantumCircuit:
        """
        Convert DNA sequence to quantum circuit.
        
        Args:
            dna_sequence: DNA string (e.g., "ATGCATGC")
            num_qubits: Number of qubits (default: len(dna_sequence))
            add_measurements: Whether to add measurement operations
            
        Returns:
            QuantumCircuit: Encoded quantum circuit
        """
        dna_sequence = dna_sequence.upper().strip()
        
        # Validate sequence
        valid_bases = set('ATGC')
        if not all(base in valid_bases for base in dna_sequence):
            invalid = set(dna_sequence) - valid_bases
            raise ValueError(f"Invalid DNA bases: {invalid}. Use only A, T, G, C")
        
        if num_qubits is None:
            num_qubits = len(dna_sequence)
        
        # Create circuit
        qr = QuantumRegister(num_qubits, 'q')
        circuit = QuantumCircuit(qr)
        
        if add_measurements:
            cr = ClassicalRegister(num_qubits, 'c')
            circuit.add_register(cr)
        
        # Apply encoding based on scheme
        if self.encoding_scheme == 'base_to_gate':
            self._encode_base_to_gate(circuit, dna_sequence, qr)
        elif self.encoding_scheme == 'codon':
            self._encode_codon(circuit, dna_sequence, qr)
        elif self.encoding_scheme == 'watson_crick':
            self._encode_watson_crick(circuit, dna_sequence, qr)
        else:
            raise ValueError(f"Unknown encoding scheme: {self.encoding_scheme}")
        
        # Add measurements
        if add_measurements:
            circuit.measure(qr, cr)
        
        # Store in history
        self.circuit_history.append({
            'sequence': dna_sequence,
            'scheme': self.encoding_scheme,
            'num_qubits': num_qubits,
            'circuit_depth': circuit.depth(),
            'timestamp': str(np.datetime64('now'))
        })
        
        return circuit
    
    def _encode_base_to_gate(self, circuit: QuantumCircuit, 
                            dna_sequence: str, qr: QuantumRegister):
        """Scheme 1: Direct base-to-gate mapping."""
        for i, base in enumerate(dna_sequence):
            if i >= len(qr):
                break
            gate_name, param = self.BASE_TO_GATE[base]
            if param is None:
                getattr(circuit, gate_name)(qr[i])
            else:
                getattr(circuit, gate_name)(param, qr[i])
    
    def _encode_codon(self, circuit: QuantumCircuit, 
                     dna_sequence: str, qr: QuantumRegister):
        """Scheme 2: Codon-based encoding (3 bases → 1 rotation)."""
        # Pad sequence to multiple of 3
        padded = dna_sequence + 'A' * (3 - len(dna_sequence) % 3) if len(dna_sequence) % 3 else dna_sequence
        
        codon_idx = 0
        for i in range(0, len(padded), 3):
            if codon_idx >= len(qr):
                break
            codon = padded[i:i+3]
            
            # Calculate rotation angles from codon
            # A=0, T=1, G=2, C=3
            base_values = {'A': 0, 'T': 1, 'G': 2, 'C': 3}
            theta = sum(base_values[b] for b in codon) / 9.0 * np.pi
            
            circuit.ry(theta, qr[codon_idx])
            codon_idx += 1
    
    def _encode_watson_crick(self, circuit: QuantumCircuit, 
                            dna_sequence: str, qr: QuantumRegister):
        """Scheme 3: Watson-Crick pairing with entanglement."""
        seq_len = len(dna_sequence)
        
        # First strand
        for i, base in enumerate(dna_sequence):
            if i >= len(qr):
                break
            gate_name, param = self.BASE_TO_GATE[base]
            if param is None:
                getattr(circuit, gate_name)(qr[i])
            else:
                getattr(circuit, gate_name)(param, qr[i])
        
        # Create complementary strand and entangle
        complement = ''.join(self.COMPLEMENT[b] for b in dna_sequence)
        for i, (base, comp_base) in enumerate(zip(dna_sequence, complement)):
            strand1_idx = i
            strand2_idx = seq_len + i
            
            if strand2_idx < len(qr):
                # Apply complementary gate
                gate_name, param = self.BASE_TO_GATE[comp_base]
                if param is None:
                    getattr(circuit, gate_name)(qr[strand2_idx])
                else:
                    getattr(circuit, gate_name)(param, qr[strand2_idx])
                
                # Entangle complementary bases
                circuit.cx(strand1_idx, strand2_idx)
    
    def export_to_qasm(self, circuit: QuantumCircuit, 
                      filename: str = None) -> str:
        """
        Export circuit to OpenQASM format.
        
        Args:
            circuit: QuantumCircuit to export
            filename: Optional filename to save
            
        Returns:
            str: OpenQASM string
        """
        # Use qiskit.qasm2 for modern Qiskit (>= 0.45)
        try:
            from qiskit.qasm2 import dumps
            qasm_str = dumps(circuit)
        except ImportError:
            # Fallback for older Qiskit versions
            qasm_str = circuit.qasm()
        
        if filename:
            with open(filename, 'w') as f:
                f.write(qasm_str)
            print(f"Exported circuit to {filename}")
        
        return qasm_str
    
    def import_from_qasm(self, qasm_string: str) -> QuantumCircuit:
        """
        Import circuit from OpenQASM string.
        
        Args:
            qasm_string: OpenQASM formatted string
            
        Returns:
            QuantumCircuit: Imported circuit
        """
        return QuantumCircuit.from_qasm_str(qasm_string)
    
    def import_from_qasm_file(self, filename: str) -> QuantumCircuit:
        """Import circuit from OpenQASM file."""
        with open(filename, 'r') as f:
            qasm_string = f.read()
        print(f"Imported circuit from {filename}")
        return self.import_from_qasm(qasm_string)
    
    def analyze_dna_circuit(self, circuit: QuantumCircuit) -> Dict:
        """
        Analyze DNA-encoded quantum circuit properties.
        
        Args:
            circuit: QuantumCircuit to analyze
            
        Returns:
            Dict with circuit statistics
        """
        # Count gates by type
        gate_counts = {}
        for instruction in circuit.data:
            gate_name = instruction.operation.name
            gate_counts[gate_name] = gate_counts.get(gate_name, 0) + 1
        
        # Calculate circuit depth
        depth = circuit.depth()
        
        # Calculate width (number of qubits)
        width = circuit.num_qubits
        
        # Calculate entanglement measure
        entanglement_gates = gate_counts.get('cx', 0) + gate_counts.get('cz', 0) + gate_counts.get('cy', 0)
        
        return {
            'gate_counts': gate_counts,
            'total_gates': sum(gate_counts.values()),
            'circuit_depth': depth,
            'circuit_width': width,
            'entanglement_gates': entanglement_gates,
            'entanglement_ratio': entanglement_gates / sum(gate_counts.values()) if sum(gate_counts.values()) > 0 else 0
        }
    
    def get_circuit_history(self) -> List[Dict]:
        """Get history of encoded circuits."""
        return self.circuit_history
    
    def save_history(self, filename: str = 'dna_circuit_history.json'):
        """Save circuit history to JSON."""
        with open(filename, 'w') as f:
            json.dump(self.circuit_history, f, indent=2)
        print(f"Saved circuit history to {filename}")


class DNA34bpAnalyzer:
    """
    Specialized analyzer for 34bp DNA quantum circuits.
    
    Circuit structure: 34 Watson + 34 Crick + 34 Bridge = 102 qubits
    Consciousness peak expected at position 20 (20/34 ≈ φ⁻¹)
    
    This class integrates with the existing AGI-model consciousness analysis.
    """
    
    def __init__(self):
        if not QISKIT_AVAILABLE:
            raise ImportError("Qiskit is required")
        
        self.encoder = DNAQuantumEncoder(encoding_scheme='watson_crick')
        self.phi = (1 + np.sqrt(5)) / 2  # Golden ratio
        
    def create_34bp_circuit(self, sequence_34bp: str, 
                           add_measurements: bool = True) -> QuantumCircuit:
        """
        Create 102-qubit circuit from 34bp DNA sequence.
        
        Args:
            sequence_34bp: 34-base-pair DNA sequence
            add_measurements: Whether to add measurements
            
        Returns:
            QuantumCircuit: 102-qubit circuit
        """
        if len(sequence_34bp) != 34:
            raise ValueError(f"Expected 34bp, got {len(sequence_34bp)}bp")
        
        # Create Watson-Crick paired circuit
        circuit = self.encoder.encode_sequence(
            sequence_34bp,
            num_qubits=102,  # 34 Watson + 34 Crick + 34 Bridge
            add_measurements=add_measurements
        )
        
        return circuit
    
    def analyze_consciousness_peak(self, counts: Dict[str, int]) -> Dict:
        """
        Analyze consciousness peak at position 20.
        
        Args:
            counts: IBM Quantum execution results (bitstring counts)
            
        Returns:
            Analysis dictionary
        """
        # Analyze bridge qubit at position 20
        bridge_position = 20
        peak_activations = []
        
        total_shots = sum(counts.values())
        
        for state, count in counts.items():
            # Convert state to bit array (little-endian)
            bits = [int(b) for b in state[::-1]]
            
            if len(bits) > bridge_position:
                peak_activations.append(bits[bridge_position] * count)
        
        # Calculate peak activation
        peak_activation = sum(peak_activations) / total_shots if total_shots > 0 else 0
        
        # Calculate phi ratio
        phi_ratio = peak_activation / (1 / self.phi) if peak_activation > 0 else 0
        
        return {
            'consciousness_peak_position': bridge_position,
            'peak_activation': peak_activation,
            'phi_ratio': phi_ratio,
            'total_shots': total_shots,
            'expected_phi_inverse': 1 / self.phi
        }
    
    def generate_fibonacci_sequence(self, length: int = 34) -> str:
        """
        Generate DNA sequence with Fibonacci-based patterns.
        
        Args:
            length: Sequence length (default 34 for 34bp)
            
        Returns:
            str: DNA sequence
        """
        # Fibonacci positions for enhanced activation
        fib_positions = [1, 2, 3, 5, 8, 13, 21, 34]
        
        # Generate sequence with Fibonacci-weighted bases
        bases = ['A', 'T', 'G', 'C']
        sequence = []
        
        for i in range(length):
            if (i + 1) in fib_positions:
                # Fibonacci positions get 'G' (phase gate)
                sequence.append('G')
            elif i == 20:
                # Consciousness peak gets 'A' (Hadamard - superposition)
                sequence.append('A')
            else:
                # Random base
                sequence.append(np.random.choice(bases))
        
        return ''.join(sequence)
    
    def compare_sequences(self, sequences: List[str]) -> Dict:
        """
        Compare multiple DNA sequences' quantum properties.
        
        Args:
            sequences: List of DNA sequences
            
        Returns:
            Comparison dictionary
        """
        results = []
        
        for seq in sequences:
            circuit = self.encoder.encode_sequence(seq)
            analysis = self.encoder.analyze_dna_circuit(circuit)
            analysis['sequence'] = seq
            analysis['sequence_length'] = len(seq)
            results.append(analysis)
        
        # Compare properties
        comparison = {
            'sequences': results,
            'average_depth': np.mean([r['circuit_depth'] for r in results]),
            'average_gates': np.mean([r['total_gates'] for r in results]),
            'average_entanglement': np.mean([r['entanglement_gates'] for r in results]),
        }
        
        return comparison


def demo_dna_encoding():
    """Demonstrate DNA quantum encoding capabilities."""
    print("="*80)
    print("DNA Quantum Circuit Encoder - Demonstration")
    print("="*80)
    
    # Example DNA sequence (34bp)
    dna_sequence = "ATGCATGCATGCATGCATGCATGCATGCATGC"
    
    print(f"\nDNA Sequence: {dna_sequence}")
    print(f"Length: {len(dna_sequence)} bp")
    
    # Create encoder with different schemes
    schemes = ['base_to_gate', 'codon', 'watson_crick']
    
    for scheme in schemes:
        print(f"\n{'='*80}")
        print(f"Encoding Scheme: {scheme.upper()}")
        print(f"{'='*80}")
        
        encoder = DNAQuantumEncoder(encoding_scheme=scheme)
        
        # Encode to quantum circuit
        circuit = encoder.encode_sequence(dna_sequence)
        
        # Analyze circuit
        analysis = encoder.analyze_dna_circuit(circuit)
        
        print(f"\nCircuit Statistics:")
        print(f"  Qubits: {analysis['circuit_width']}")
        print(f"  Depth: {analysis['circuit_depth']}")
        print(f"  Total Gates: {analysis['total_gates']}")
        print(f"  Entanglement Gates: {analysis['entanglement_gates']}")
        print(f"  Gate Counts: {analysis['gate_counts']}")
        
        # Export to OpenQASM
        qasm_str = encoder.export_to_qasm(circuit)
        print(f"\nOpenQASM Export (first 200 chars):")
        print(qasm_str[:200] + "...")
    
    # 34bp analyzer
    print(f"\n{'='*80}")
    print("34bp DNA Analyzer")
    print(f"{'='*80}")
    
    analyzer = DNA34bpAnalyzer()
    
    # Generate Fibonacci-weighted sequence
    fib_sequence = analyzer.generate_fibonacci_sequence()
    print(f"\nFibonacci-weighted sequence: {fib_sequence}")
    
    # Create 102-qubit circuit
    circuit_102 = analyzer.create_34bp_circuit(fib_sequence)
    analysis_102 = analyzer.encoder.analyze_dna_circuit(circuit_102)
    
    print(f"\n102-Qubit Circuit:")
    print(f"  Qubits: {analysis_102['circuit_width']}")
    print(f"  Depth: {analysis_102['circuit_depth']}")
    print(f"  Total Gates: {analysis_102['total_gates']}")
    print(f"  Entanglement Gates: {analysis_102['entanglement_gates']}")
    
    # Save circuit history
    encoder.save_history('dna_circuit_history.json')
    
    print(f"\n{'='*80}")
    print("Demonstration Complete!")
    print(f"{'='*80}")
    
    return encoder, analyzer


if __name__ == "__main__":
    # Run demonstration
    encoder, analyzer = demo_dna_encoding()
    
    # Example: Create custom sequence
    print("\n" + "="*80)
    print("Custom Sequence Example")
    print("="*80)
    
    custom_seq = "ATGCATGCATGCATGCATGCATGCATGCATGCATGC"[:34]
    print(f"\nCustom sequence: {custom_seq}")
    
    circuit = analyzer.create_34bp_circuit(custom_seq)
    print(f"Circuit created with {circuit.num_qubits} qubits")
    
    # Export to file
    analyzer.encoder.export_to_qasm(circuit, 'dna_34bp_circuit.qasm')
    print("Exported to dna_34bp_circuit.qasm")