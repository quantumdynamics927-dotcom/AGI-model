#!/usr/bin/env python3
"""
DNA-to-Quantum Circuit \& VQE Integration Examples
===================================================

Comprehensive examples demonstrating:
1. DNA sequence to quantum circuit encoding
2. OpenQASM parsing and import
3. Molecular VQE with qiskit-nature
4. DNA-to-molecule mapping
5. Integrated DNA-VQE calculations

Requirements:
    pip install qiskit qiskit-nature qiskit-algorithms pyscf

Usage:
    python dna_vqe_examples.py

Author: AGI-model Quantum Computing Team
Date: April 9, 2026
"""

import numpy as np
from pathlib import Path
import json


def example_1_dna_encoding():
    """
    Example 1: DNA Sequence to Quantum Circuit
    
    Demonstrates encoding DNA sequences using different schemes:
    - base_to_gate: A→H, T→X, G→RZ, C→RY
    - codon: 3-base codons to rotation angles
    - watson_crick: Complementary base pairing with entanglement
    """
    print("\n" + "="*80)
    print("Example 1: DNA Sequence to Quantum Circuit Encoding")
    print("="*80)
    
    from dna_quantum_circuits import DNAQuantumEncoder
    
    # Example DNA sequence
    dna_sequence = "ATGCATGC"
    print(f"\nDNA Sequence: {dna_sequence}")
    print(f"Length: {len(dna_sequence)} bp\n")
    
    # Try different encoding schemes
    schemes = ['base_to_gate', 'codon', 'watson_crick']
    
    for scheme in schemes:
        print(f"\n--- Encoding Scheme: {scheme.upper()} ---")
        
        encoder = DNAQuantumEncoder(encoding_scheme=scheme)
        circuit = encoder.encode_sequence(dna_sequence)
        analysis = encoder.analyze_dna_circuit(circuit)
        
        print(f"  Qubits: {analysis['circuit_width']}")
        print(f"  Depth: {analysis['circuit_depth']}")
        print(f"  Total Gates: {analysis['total_gates']}")
        print(f"  Entanglement Gates: {analysis['entanglement_gates']}")
        print(f"  Gate Distribution: {analysis['gate_counts']}")
        
        # Export to OpenQASM
        qasm_file = f'dna_{scheme}_circuit.qasm'
        encoder.export_to_qasm(circuit, qasm_file)
        print(f"  Exported to: {qasm_file}")


def example_2_openqasm_parsing():
    """
    Example 2: OpenQASM Import and Parsing
    
    Demonstrates:
    - Importing circuits from OpenQASM strings
    - Loading circuits from .qasm files
    - Parsing QASM to extract gate information
    """
    print("\n" + "="*80)
    print("Example 2: OpenQASM Import and Parsing")
    print("="*80)
    
    from dna_quantum_circuits import DNAQuantumEncoder
    
    # Example OpenQASM 2.0 string
    qasm_string = """
OPENQASM 2.0;
include "qelib1.inc";
qreg q[3];
creg c[3];
h q[0];
cx q[0],q[1];
cx q[1],q[2];
measure q -> c;
"""
    
    print("\nImporting circuit from OpenQASM string...")
    encoder = DNAQuantumEncoder()
    circuit = encoder.import_from_qasm(qasm_string)
    
    print(f"  Imported: {circuit.num_qubits} qubits, {circuit.depth()} depth")
    
    # Parse QASM gates
    print("\nParsing QASM gates...")
    gate_info = encoder.parse_qasm_gates(qasm_string)
    
    print(f"  Total gates: {gate_info['total_gates']}")
    print(f"  Qubits used: {gate_info['num_qubits']}")
    print(f"  Gate types: {gate_info['gate_types']}")
    
    # Show individual gates
    print("\nGate breakdown:")
    for i, gate in enumerate(gate_info['gates'][:5]):  # Show first 5 gates
        print(f"  {i+1}. {gate['gate']} on qubits {gate['qubits']}, params: {gate['params']}")


def example_3_molecular_vqe():
    """
    Example 3: Molecular VQE with qiskit-nature
    
    Demonstrates:
    - Setting up molecules with PySCFDriver
    - Running VQE with different ansatz types
    - Comparing with experimental energies
    """
    print("\n" + "="*80)
    print("Example 3: Molecular VQE with qiskit-nature")
    print("="*80)
    
    from dna_quantum_circuits import MolecularVQE
    
    # Check if qiskit-nature is available
    try:
        from qiskit_nature.second_q.drivers import PySCFDriver
    except ImportError:
        print("\n⚠️  qiskit-nature not available. Install with: pip install qiskit-nature pyscf")
        return
    
    # Setup H₂ molecule
    print("\n--- Hydrogen Molecule (H₂) ---")
    vqe = MolecularVQE('H2')
    
    # Setup molecule with PySCF
    mol_data = vqe.setup_molecule(basis='sto-3g')
    print(f"  Num particles: {mol_data['num_particles']}")
    print(f"  Num spin orbitals: {mol_data['num_spin_orbitals']}")
    
    # Get Hamiltonian
    hamiltonian = vqe.get_hamiltonian(mapper='jordan_wigner')
    print(f"  Hamiltonian terms: {len(hamiltonian)}")
    
    # Run VQE with different ansatz types
    ansatz_types = ['uccsd', 'real_amplitudes']
    
    for ansatz in ansatz_types:
        print(f"\n--- Ansatz: {ansatz.upper()} ---")
        
        try:
            result = vqe.run_vqe(
                ansatz_type=ansatz,
                optimizer='cobyla',
                shots=1024
            )
            
            print(f"  Ground state energy: {result['energy']:.6f} Hartree")
            print(f"  Experimental energy: {result['experimental_energy']:.6f} Hartree")
            print(f"  Absolute error: {result['absolute_error']:.6f} Hartree")
            print(f"  Relative error: {result['relative_error']:.4f}%")
            
        except Exception as e:
            print(f"  Error: {e}")


def example_4_dna_to_molecule():
    """
    Example 4: DNA Sequence to Molecular Mapping
    
    Demonstrates:
    - Mapping DNA bases to molecule types
    - Calculating bond lengths from sequence length
    - Selecting basis sets from GC content
    """
    print("\n" + "="*80)
    print("Example 4: DNA Sequence to Molecular Mapping")
    print("="*80)
    
    from dna_quantum_circuits import MolecularVQE
    
    # Test sequences
    test_sequences = [
        "ATGC",      # AT → H2
        "GCGC",      # GC → LiH
        "AATT",      # AA → H2O
        "GGCC",      # GG → N2
        "ATGCATGC",  # Longer sequence
    ]
    
    vqe_temp = MolecularVQE('H2')
    
    for seq in test_sequences:
        print(f"\n--- Sequence: {seq} ---")
        params = vqe_temp.dna_to_molecule(seq)
        
        print(f"  Molecule: {params['molecule']}")
        print(f"  Bond length: {params['bond_length']:.3f} Å")
        print(f"  Basis set: {params['basis']}")
        print(f"  GC content: {params['gc_content']:.2%}")


def example_5_integrated_dna_vqe():
    """
    Example 5: Integrated DNA-VQE Calculation
    
    Demonstrates:
    - End-to-end DNA sequence to VQE energy
    - Comparing multiple DNA sequences
    - Exporting results to JSON
    """
    print("\n" + "="*80)
    print("Example 5: Integrated DNA-VQE Calculation")
    print("="*80)
    
    from dna_quantum_circuits import DNAVQEIntegrator
    
    # Check dependencies
    try:
        from qiskit_nature.second_q.drivers import PySCFDriver
        from qiskit_algorithms import VQE
    except ImportError:
        print("\n⚠️  Required packages not available.")
        print("Install with: pip install qiskit-nature pyscf qiskit-algorithms")
        return
    
    # Create integrator
    integrator = DNAVQEIntegrator()
    
    # Test sequences
    test_sequences = [
        "ATGC",
        "GCGC",
    ]
    
    print(f"\nProcessing {len(test_sequences)} DNA sequences...\n")
    
    results = []
    for seq in test_sequences:
        print(f"--- Processing: {seq} ---")
        
        try:
            result = integrator.dna_sequence_to_vqe(
                seq,
                optimizer='cobyla',
                shots=512  # Fewer shots for faster demo
            )
            
            results.append({
                'sequence': seq,
                'molecule': result['molecular_params']['molecule'],
                'energy': result['vqe_result']['energy'],
                'bond_length': result['molecular_params']['bond_length'],
            })
            
            print(f"  Molecule: {result['molecular_params']['molecule']}")
            print(f"  Bond length: {result['molecular_params']['bond_length']:.3f} Å")
            print(f"  VQE Energy: {result['vqe_result']['energy']:.6f} Hartree")
            print()
            
        except Exception as e:
            print(f"  Error: {e}")
            print()
    
    # Summary
    if results:
        print("\n" + "="*80)
        print("Summary")
        print("="*80)
        
        for r in results:
            print(f"  {r['sequence']:10s} → {r['molecule']:5s} → {r['energy']:12.6f} Hartree")
        
        # Export results
        integrator.export_results('dna_vqe_example_results.json')
        print("\nResults exported to: dna_vqe_example_results.json")


def example_6_34bp_consciousness():
    """
    Example 6: 34bp DNA Consciousness Analysis
    
    Demonstrates:
    - Creating 102-qubit circuits from 34bp sequences
    - Fibonacci-weighted sequence generation
    - Consciousness peak analysis
    """
    print("\n" + "="*80)
    print("Example 6: 34bp DNA Consciousness Analysis")
    print("="*80)
    
    from dna_quantum_circuits import DNA34bpAnalyzer
    
    analyzer = DNA34bpAnalyzer()
    
    # Generate Fibonacci-weighted sequence
    print("\nGenerating Fibonacci-weighted sequence...")
    fib_sequence = analyzer.generate_fibonacci_sequence()
    print(f"  Sequence: {fib_sequence}")
    print(f"  Length: {len(fib_sequence)} bp")
    
    # Create 102-qubit circuit
    print("\nCreating 102-qubit circuit...")
    circuit = analyzer.create_34bp_circuit(fib_sequence)
    
    print(f"  Qubits: {circuit.num_qubits}")
    print(f"  Depth: {circuit.depth()}")
    
    # Analyze circuit
    analysis = analyzer.encoder.analyze_dna_circuit(circuit)
    print(f"\nCircuit Analysis:")
    print(f"  Total gates: {analysis['total_gates']}")
    print(f"  Entanglement gates: {analysis['entanglement_gates']}")
    print(f"  Entanglement ratio: {analysis['entanglement_ratio']:.3f}")
    
    # Export to QASM
    analyzer.encoder.export_to_qasm(circuit, 'dna_34bp_consciousness.qasm')
    print("\nExported to: dna_34bp_consciousness.qasm")


def main():
    """Run all examples."""
    print("="*80)
    print("DNA-to-Quantum Circuit & VQE Integration Examples")
    print("="*80)
    print("\nThis script demonstrates:")
    print("  1. DNA sequence to quantum circuit encoding")
    print("  2. OpenQASM parsing and import")
    print("  3. Molecular VQE with qiskit-nature")
    print("  4. DNA-to-molecule mapping")
    print("  5. Integrated DNA-VQE calculations")
    print("  6. 34bp DNA consciousness analysis")
    print("\nNote: VQE examples require qiskit-nature and pyscf.")
    print("      Install with: pip install qiskit-nature pyscf qiskit-algorithms\n")
    
    # Run examples
    try:
        example_1_dna_encoding()
        example_2_openqasm_parsing()
        example_3_molecular_vqe()
        example_4_dna_to_molecule()
        example_5_integrated_dna_vqe()
        example_6_34bp_consciousness()
        
        print("\n" + "="*80)
        print("All Examples Complete!")
        print("="*80)
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
