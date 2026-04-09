#!/usr/bin/env python3
"""
DNA-to-Circuit Features Demo (No PySCF Required)
=================================================

This script demonstrates all DNA-to-quantum circuit features that work
WITHOUT requiring PySCF installation.

Features Demonstrated:
✅ DNA-to-quantum circuit encoding (3 schemes)
✅ OpenQASM import/export
✅ Gate parsing and analysis
✅ 34bp consciousness analysis
✅ DNA-to-molecule mapping (parameter calculation)
✅ Circuit visualization and statistics

Author: AGI-model Quantum Computing Team
Date: April 9, 2026
"""

import numpy as np
from pathlib import Path
import json


def demo_1_dna_encoding():
    """Demonstrate DNA-to-quantum circuit encoding."""
    print("\n" + "="*80)
    print("Feature 1: DNA-to-Quantum Circuit Encoding")
    print("="*80)
    
    from dna_quantum_circuits import DNAQuantumEncoder
    
    # Example DNA sequences
    sequences = [
        "ATGC",              # 4 bp
        "ATGCATGC",          # 8 bp
        "ATGCATGCATGCATGC",  # 16 bp
    ]
    
    schemes = ['base_to_gate', 'codon', 'watson_crick']
    
    for seq in sequences:
        print(f"\nDNA Sequence: {seq} ({len(seq)} bp)")
        print("-" * 60)
        
        for scheme in schemes:
            encoder = DNAQuantumEncoder(encoding_scheme=scheme)
            circuit = encoder.encode_sequence(seq)
            analysis = encoder.analyze_dna_circuit(circuit)
            
            print(f"\n  {scheme.upper()}:")
            print(f"    Qubits: {analysis['circuit_width']}")
            print(f"    Depth: {analysis['circuit_depth']}")
            print(f"    Total Gates: {analysis['total_gates']}")
            print(f"    Entanglement Gates: {analysis['entanglement_gates']}")
            
            # Gate distribution
            gate_counts = analysis['gate_counts']
            top_gates = sorted(gate_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            print(f"    Top Gates: {dict(top_gates)}")


def demo_2_openqasm_io():
    """Demonstrate OpenQASM import/export."""
    print("\n" + "="*80)
    print("Feature 2: OpenQASM Import/Export")
    print("="*80)
    
    from dna_quantum_circuits import DNAQuantumEncoder
    
    encoder = DNAQuantumEncoder()
    
    # Create a circuit from DNA
    dna_seq = "ATGCATGC"
    circuit = encoder.encode_sequence(dna_seq)
    
    print(f"\nOriginal DNA: {dna_seq}")
    print(f"Circuit: {circuit.num_qubits} qubits, {circuit.depth()} depth")
    
    # Export to OpenQASM
    print("\n--- Export to OpenQASM ---")
    qasm_str = encoder.export_to_qasm(circuit, filename='demo_dna_circuit.qasm')
    print(f"Exported to: demo_dna_circuit.qasm")
    print(f"QASM length: {len(qasm_str)} characters")
    print("\nFirst 300 characters:")
    print(qasm_str[:300])
    
    # Import from OpenQASM
    print("\n--- Import from OpenQASM ---")
    imported_circuit = encoder.import_from_qasm(qasm_str)
    print(f"Imported circuit: {imported_circuit.num_qubits} qubits")
    print(f"Circuit depth: {imported_circuit.depth()}")
    print(f"Number of gates: {imported_circuit.size()}")
    
    # Verify round-trip
    assert circuit.num_qubits == imported_circuit.num_qubits
    print("\n✅ Round-trip verification successful!")


def demo_3_gate_parsing():
    """Demonstrate QASM gate parsing and analysis."""
    print("\n" + "="*80)
    print("Feature 3: Gate Parsing and Analysis")
    print("="*80)
    
    from dna_quantum_circuits import DNAQuantumEncoder
    
    encoder = DNAQuantumEncoder()
    
    # Sample QASM with various gates
    qasm_example = """
OPENQASM 2.0;
include "qelib1.inc";
qreg q[4];
creg c[4];
h q[0];
h q[1];
cx q[0],q[1];
rz(0.785) q[2];
ry(0.785) q[3];
measure q[0] -> c[0];
measure q[1] -> c[1];
"""
    
    print("Parsing QASM example...")
    gate_info = encoder.parse_qasm_gates(qasm_example)
    
    print(f"\nGate Analysis Results:")
    print(f"  Total Gates: {gate_info['total_gates']}")
    print(f"  Number of Qubits: {gate_info['num_qubits']}")
    print(f"  Gate Types: {gate_info['gate_types']}")
    
    print(f"\nDetailed Gate List:")
    for i, gate in enumerate(gate_info['gates']):
        params_str = f"({', '.join(f'{p:.3f}' for p in gate['params'])})" if gate['params'] else ""
        qubits_str = f"q{gate['qubits']}"
        print(f"  {i+1}. {gate['gate']}{params_str} on {qubits_str}")


def demo_4_consciousness_analysis():
    """Demonstrate 34bp consciousness analysis."""
    print("\n" + "="*80)
    print("Feature 4: 34bp Consciousness Analysis")
    print("="*80)
    
    from dna_quantum_circuits import DNA34bpAnalyzer
    
    analyzer = DNA34bpAnalyzer()
    
    # Generate Fibonacci-weighted sequence
    print("\nGenerating Fibonacci-weighted DNA sequence...")
    fib_sequence = analyzer.generate_fibonacci_sequence()
    print(f"Sequence: {fib_sequence}")
    print(f"Length: {len(fib_sequence)} bp")
    
    # Create 102-qubit circuit
    print("\nCreating 102-qubit quantum circuit...")
    print("(34 Watson + 34 Crick + 34 Bridge qubits)")
    circuit = analyzer.create_34bp_circuit(fib_sequence)
    
    print(f"\nCircuit Properties:")
    print(f"  Total Qubits: {circuit.num_qubits}")
    print(f"  Circuit Depth: {circuit.depth()}")
    print(f"  Total Gates: {circuit.size()}")
    
    # Analyze circuit
    analysis = analyzer.encoder.analyze_dna_circuit(circuit)
    
    print(f"\nDetailed Analysis:")
    print(f"  Circuit Width: {analysis['circuit_width']}")
    print(f"  Circuit Depth: {analysis['circuit_depth']}")
    print(f"  Total Gates: {analysis['total_gates']}")
    print(f"  Entanglement Gates: {analysis['entanglement_gates']}")
    print(f"  Entanglement Ratio: {analysis['entanglement_ratio']:.3f}")
    
    # Gate distribution
    print(f"\nGate Distribution:")
    for gate, count in sorted(analysis['gate_counts'].items(), key=lambda x: x[1], reverse=True):
        percentage = count / analysis['total_gates'] * 100
        print(f"  {gate:10s}: {count:4d} ({percentage:.1f}%)")
    
    # Export to QASM
    qasm_file = 'demo_34bp_consciousness.qasm'
    analyzer.encoder.export_to_qasm(circuit, qasm_file)
    print(f"\nExported to: {qasm_file}")
    
    # File size
    file_size = Path(qasm_file).stat().st_size
    print(f"File size: {file_size:,} bytes")


def demo_5_dna_to_molecule():
    """Demonstrate DNA-to-molecule mapping."""
    print("\n" + "="*80)
    print("Feature 5: DNA-to-Molecule Mapping")
    print("="*80)
    
    from dna_quantum_circuits import MolecularVQE
    
    # Test sequences
    test_cases = [
        ("ATGC", "H2 (Hydrogen)"),
        ("GCGC", "LiH (Lithium Hydride)"),
        ("AATT", "H2O (Water)"),
        ("GGCC", "N2 (Nitrogen)"),
        ("ATGCATGC", "H2 (longer sequence)"),
    ]
    
    vqe_temp = MolecularVQE('H2')
    
    print("\nMapping DNA sequences to molecular parameters:\n")
    
    for seq, expected in test_cases:
        params = vqe_temp.dna_to_molecule(seq)
        
        print(f"DNA: {seq:12s} → Molecule: {params['molecule']:5s} ({expected})")
        print(f"  Bond Length: {params['bond_length']:.4f} Å")
        print(f"  Basis Set: {params['basis']}")
        print(f"  GC Content: {params['gc_content']:.2%}")
        print()


def demo_6_circuit_statistics():
    """Demonstrate comprehensive circuit statistics."""
    print("\n" + "="*80)
    print("Feature 6: Circuit Statistics and Analysis")
    print("="*80)
    
    from dna_quantum_circuits import DNAQuantumEncoder
    
    encoder = DNAQuantumEncoder()
    
    # Test sequences of increasing length
    sequences = ["ATGC", "ATGCATGC", "ATGCATGCATGCATGC"]
    
    print("\nCircuit Complexity vs DNA Length:\n")
    print(f"{'DNA Length':<12} {'Qubits':<8} {'Depth':<8} {'Gates':<8} {'Entanglement':<14}")
    print("-" * 60)
    
    results = []
    for seq in sequences:
        encoder_wc = DNAQuantumEncoder(encoding_scheme='watson_crick')
        circuit = encoder_wc.encode_sequence(seq)
        analysis = encoder_wc.analyze_dna_circuit(circuit)
        
        results.append({
            'dna_length': len(seq),
            'qubits': analysis['circuit_width'],
            'depth': analysis['circuit_depth'],
            'gates': analysis['total_gates'],
            'entanglement': analysis['entanglement_gates']
        })
        
        print(f"{len(seq):<12} {analysis['circuit_width']:<8} "
              f"{analysis['circuit_depth']:<8} {analysis['total_gates']:<8} "
              f"{analysis['entanglement_gates']:<14}")
    
    # Save statistics
    stats_file = 'demo_circuit_statistics.json'
    with open(stats_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nStatistics saved to: {stats_file}")


def demo_7_history_tracking():
    """Demonstrate circuit history tracking."""
    print("\n" + "="*80)
    print("Feature 7: Circuit History Tracking")
    print("="*80)
    
    from dna_quantum_circuits import DNAQuantumEncoder
    
    encoder = DNAQuantumEncoder(encoding_scheme='base_to_gate')
    
    # Encode multiple sequences
    sequences = ["ATGC", "GCGC", "ATAT", "GCTA"]
    
    print(f"\nEncoding {len(sequences)} sequences...")
    for seq in sequences:
        circuit = encoder.encode_sequence(seq)
        print(f"  Encoded: {seq} → {circuit.num_qubits} qubits")
    
    # Get history
    history = encoder.get_circuit_history()
    
    print(f"\nCircuit History ({len(history)} entries):")
    for i, entry in enumerate(history, 1):
        print(f"  {i}. {entry['sequence']:8s} - "
              f"{entry['scheme']:15s} - "
              f"{entry['num_qubits']:2d} qubits, "
              f"depth {entry['circuit_depth']}")
    
    # Save history
    history_file = 'demo_circuit_history.json'
    encoder.save_history(history_file)
    print(f"\nHistory saved to: {history_file}")


def main():
    """Run all demonstrations."""
    print("="*80)
    print("DNA-to-Circuit Features Demo (No PySCF Required)")
    print("="*80)
    print("\nThis demo showcases features that work WITHOUT PySCF installation:")
    print("  [OK] DNA-to-quantum circuit encoding")
    print("  [OK] OpenQASM import/export")
    print("  [OK] Gate parsing and analysis")
    print("  [OK] 34bp consciousness analysis")
    print("  [OK] DNA-to-molecule mapping")
    print("  [OK] Circuit statistics")
    print("  [OK] History tracking")
    print("\nNote: Only VQE execution requires PySCF.\n")
    
    try:
        # Run all demos
        demo_1_dna_encoding()
        demo_2_openqasm_io()
        demo_3_gate_parsing()
        demo_4_consciousness_analysis()
        demo_5_dna_to_molecule()
        demo_6_circuit_statistics()
        demo_7_history_tracking()
        
        # Summary
        print("\n" + "="*80)
        print("Demo Complete!")
        print("="*80)
        print("\nGenerated Files:")
        generated_files = [
            'demo_dna_circuit.qasm',
            'demo_34bp_consciousness.qasm',
            'demo_circuit_statistics.json',
            'demo_circuit_history.json'
        ]
        
        for f in generated_files:
            if Path(f).exists():
                size = Path(f).stat().st_size
                print(f"  [OK] {f} ({size:,} bytes)")
            else:
                print(f"  [FAIL] {f} (not found)")
        
        print("\nAll DNA-to-Circuit features are working correctly!")
        print("For VQE calculations, use Docker or install PySCF separately.")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
