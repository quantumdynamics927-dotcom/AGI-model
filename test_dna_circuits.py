#!/usr/bin/env python3
"""
DNA-to-Circuit Module - Quick Test Suite
=========================================

Tests the core functionality of the enhanced dna_quantum_circuits module.

Run: python test_dna_circuits.py
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))


def test_imports():
    """Test that all classes can be imported."""
    print("\n" + "="*80)
    print("Test 1: Module Imports")
    print("="*80)
    
    try:
        from dna_quantum_circuits import (
            DNAQuantumEncoder,
            MolecularVQE,
            DNAVQEIntegrator,
            DNA34bpAnalyzer
        )
        print("✅ All classes imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_dna_encoding():
    """Test DNA sequence encoding."""
    print("\n" + "="*80)
    print("Test 2: DNA Encoding")
    print("="*80)
    
    try:
        from dna_quantum_circuits import DNAQuantumEncoder
        
        # Test all encoding schemes
        schemes = ['base_to_gate', 'codon', 'watson_crick']
        dna_sequence = "ATGCATGC"
        
        for scheme in schemes:
            encoder = DNAQuantumEncoder(encoding_scheme=scheme)
            circuit = encoder.encode_sequence(dna_sequence)
            
            assert circuit.num_qubits == len(dna_sequence), f"Qubit count mismatch for {scheme}"
            print(f"  ✅ {scheme}: {circuit.num_qubits} qubits, {circuit.depth()} depth")
        
        return True
    except Exception as e:
        print(f"❌ DNA encoding failed: {e}")
        return False


def test_openqasm_export():
    """Test OpenQASM export functionality."""
    print("\n" + "="*80)
    print("Test 3: OpenQASM Export")
    print("="*80)
    
    try:
        from dna_quantum_circuits import DNAQuantumEncoder
        
        encoder = DNAQuantumEncoder()
        circuit = encoder.encode_sequence("ATGC")
        
        # Export to string
        qasm_str = encoder.export_to_qasm(circuit)
        assert 'OPENQASM' in qasm_str, "Invalid QASM format"
        assert 'qreg' in qasm_str, "Missing qubit register"
        print(f"  ✅ QASM export: {len(qasm_str)} characters")
        
        # Export to file
        qasm_file = 'test_dna_circuit.qasm'
        encoder.export_to_qasm(circuit, qasm_file)
        assert Path(qasm_file).exists(), "QASM file not created"
        print(f"  ✅ QASM file created: {qasm_file}")
        
        # Cleanup
        Path(qasm_file).unlink()
        
        return True
    except Exception as e:
        print(f"❌ QASM export failed: {e}")
        return False


def test_openqasm_import():
    """Test OpenQASM import functionality."""
    print("\n" + "="*80)
    print("Test 4: OpenQASM Import")
    print("="*80)
    
    try:
        from dna_quantum_circuits import DNAQuantumEncoder
        
        # Sample QASM string
        qasm_string = """
OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];
h q[0];
cx q[0],q[1];
measure q -> c;
"""
        
        encoder = DNAQuantumEncoder()
        circuit = encoder.import_from_qasm(qasm_string)
        
        assert circuit.num_qubits == 2, "Qubit count mismatch"
        assert circuit.depth() > 0, "Circuit depth should be > 0"
        print(f"  ✅ QASM import: {circuit.num_qubits} qubits, {circuit.depth()} depth")
        
        # Test gate parsing
        gate_info = encoder.parse_qasm_gates(qasm_string)
        assert gate_info['total_gates'] > 0, "No gates parsed"
        assert 'h' in gate_info['gate_types'], "Hadamard gate not found"
        assert 'cx' in gate_info['gate_types'], "CNOT gate not found"
        print(f"  ✅ Gate parsing: {gate_info['total_gates']} gates, types: {gate_info['gate_types']}")
        
        return True
    except Exception as e:
        print(f"❌ QASM import failed: {e}")
        return False


def test_molecular_vqe_setup():
    """Test molecular VQE setup (without running VQE)."""
    print("\n" + "="*80)
    print("Test 5: Molecular VQE Setup")
    print("="*80)
    
    try:
        from dna_quantum_circuits import MolecularVQE
        
        # Check if qiskit-nature is available
        try:
            from qiskit_nature.second_q.drivers import PySCFDriver
            print("  ✅ qiskit-nature available")
        except ImportError:
            print("  ⚠️  qiskit-nature not available - skipping VQE tests")
            return True
        
        # Test molecule setup
        vqe = MolecularVQE('H2')
        mol_data = vqe.setup_molecule(basis='sto-3g')
        
        assert 'num_particles' in mol_data, "Missing particle count"
        assert 'num_spin_orbitals' in mol_data, "Missing orbital count"
        print(f"  ✅ Molecule setup: {mol_data['num_particles']} particles, "
              f"{mol_data['num_spin_orbitals']} spin orbitals")
        
        # Test Hamiltonian
        hamiltonian = vqe.get_hamiltonian(mapper='jordan_wigner')
        assert hamiltonian is not None, "Hamiltonian is None"
        print(f"  ✅ Hamiltonian: {len(hamiltonian)} Pauli terms")
        
        # Test ansatz creation
        ansatz = vqe.create_ansatz(ansatz_type='real_amplitudes')
        assert ansatz.num_qubits > 0, "Ansatz qubit count invalid"
        print(f"  ✅ Ansatz: {ansatz.num_qubits} qubits, {ansatz.size()} gates")
        
        return True
    except Exception as e:
        print(f"❌ VQE setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dna_to_molecule():
    """Test DNA-to-molecule mapping."""
    print("\n" + "="*80)
    print("Test 6: DNA-to-Molecule Mapping")
    print("="*80)
    
    try:
        from dna_quantum_circuits import MolecularVQE
        
        # Test sequences
        test_cases = [
            ("ATGC", "H2"),
            ("GCGC", "LiH"),
            ("AATT", "H2O"),
            ("GGCC", "N2"),
        ]
        
        vqe_temp = MolecularVQE('H2')
        
        for seq, expected_mol in test_cases:
            params = vqe_temp.dna_to_molecule(seq)
            assert params['molecule'] == expected_mol, \
                f"Expected {expected_mol} for {seq}, got {params['molecule']}"
            print(f"  ✅ {seq} → {params['molecule']} (bond: {params['bond_length']:.3f} Å, "
                  f"GC: {params['gc_content']:.2%})")
        
        return True
    except Exception as e:
        print(f"❌ DNA-to-molecule mapping failed: {e}")
        return False


def test_34bp_analyzer():
    """Test 34bp consciousness analyzer."""
    print("\n" + "="*80)
    print("Test 7: 34bp Consciousness Analyzer")
    print("="*80)
    
    try:
        from dna_quantum_circuits import DNA34bpAnalyzer
        
        analyzer = DNA34bpAnalyzer()
        
        # Generate Fibonacci sequence
        fib_seq = analyzer.generate_fibonacci_sequence()
        assert len(fib_seq) == 34, f"Expected 34bp, got {len(fib_seq)}bp"
        print(f"  ✅ Fibonacci sequence: {fib_seq}")
        
        # Create 102-qubit circuit
        circuit = analyzer.create_34bp_circuit(fib_seq)
        assert circuit.num_qubits == 102, f"Expected 102 qubits, got {circuit.num_qubits}"
        print(f"  ✅ 102-qubit circuit: {circuit.num_qubits} qubits, "
              f"{circuit.depth()} depth, {circuit.size()} gates")
        
        return True
    except Exception as e:
        print(f"❌ 34bp analyzer failed: {e}")
        return False


def test_circuit_analysis():
    """Test circuit analysis functionality."""
    print("\n" + "="*80)
    print("Test 8: Circuit Analysis")
    print("="*80)
    
    try:
        from dna_quantum_circuits import DNAQuantumEncoder
        
        encoder = DNAQuantumEncoder()
        circuit = encoder.encode_sequence("ATGCATGC")
        
        # Analyze circuit
        analysis = encoder.analyze_dna_circuit(circuit)
        
        assert 'gate_counts' in analysis, "Missing gate counts"
        assert 'total_gates' in analysis, "Missing total gates"
        assert 'circuit_depth' in analysis, "Missing circuit depth"
        assert 'circuit_width' in analysis, "Missing circuit width"
        
        print(f"  ✅ Analysis: {analysis['total_gates']} gates, "
              f"depth {analysis['circuit_depth']}, "
              f"width {analysis['circuit_width']}")
        print(f"  ✅ Gate distribution: {analysis['gate_counts']}")
        
        return True
    except Exception as e:
        print(f"❌ Circuit analysis failed: {e}")
        return False


def main():
    """Run all tests."""
    print("="*80)
    print("DNA-to-Circuit Module - Quick Test Suite")
    print("="*80)
    
    tests = [
        ("Imports", test_imports),
        ("DNA Encoding", test_dna_encoding),
        ("OpenQASM Export", test_openqasm_export),
        ("OpenQASM Import", test_openqasm_import),
        ("Molecular VQE Setup", test_molecular_vqe_setup),
        ("DNA-to-Molecule", test_dna_to_molecule),
        ("34bp Analyzer", test_34bp_analyzer),
        ("Circuit Analysis", test_circuit_analysis),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test {name} crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*80)
    print("Test Summary")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
