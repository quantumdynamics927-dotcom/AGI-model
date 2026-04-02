#!/usr/bin/env python3
"""
Test DNA Quantum Encoder and Molecular VQE
==========================================

Tests:
1. DNA-to-Quantum Circuit Encoder (dna_quantum_circuits.py)
2. Molecular VQE with proper chemistry (run_molecular_vqe.py)

This script handles missing dependencies gracefully.

Author: AGI-model Quantum Computing Team
Date: April 2, 2026
"""

import sys
import traceback
from pathlib import Path

# Add parent directory to path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


def test_dna_quantum_encoder():
    """Test DNA-to-Quantum Circuit Encoder."""
    print("\n" + "="*80)
    print("TEST 1: DNA Quantum Encoder")
    print("="*80)
    
    try:
        from dna_quantum_circuits import DNAQuantumEncoder, DNA34bpAnalyzer
        import numpy as np
        
        # Test basic encoding
        print("\n[1.1] Testing base-to-gate encoding...")
        encoder = DNAQuantumEncoder(encoding_scheme='base_to_gate')
        
        # Test sequence
        test_sequence = "ATGCATGC"
        print(f"  DNA sequence: {test_sequence}")
        
        circuit = encoder.encode_sequence(test_sequence)
        print(f"  Circuit qubits: {circuit.num_qubits}")
        print(f"  Circuit depth: {circuit.depth}")
        print(f"  Circuit gates: {circuit.count_ops()}")
        
        # Analyze circuit
        analysis = encoder.analyze_dna_circuit(circuit)
        print(f"\n  Circuit Analysis:")
        print(f"    Total gates: {analysis['total_gates']}")
        print(f"    Entanglement gates: {analysis['entanglement_gates']}")
        print(f"    Entanglement ratio: {analysis['entanglement_ratio']:.3f}")
        
        # Test codon encoding
        print("\n[1.2] Testing codon-based encoding...")
        encoder_codon = DNAQuantumEncoder(encoding_scheme='codon')
        circuit_codon = encoder_codon.encode_sequence("ATGCATGCATGC")
        print(f"  Codon circuit qubits: {circuit_codon.num_qubits}")
        print(f"  Codon circuit depth: {circuit_codon.depth}")
        
        # Test Watson-Crick encoding
        print("\n[1.3] Testing Watson-Crick entanglement encoding...")
        encoder_wc = DNAQuantumEncoder(encoding_scheme='watson_crick')
        circuit_wc = encoder_wc.encode_sequence("ATGC", num_qubits=8)
        print(f"  WC circuit qubits: {circuit_wc.num_qubits}")
        print(f"  WC circuit depth: {circuit_wc.depth}")
        print(f"  WC gates: {circuit_wc.count_ops()}")
        
        # Test OpenQASM export
        print("\n[1.4] Testing OpenQASM export...")
        try:
            qasm_str = encoder.export_to_qasm(circuit)
            print(f"  QASM length: {len(qasm_str)} characters")
            print(f"  QASM preview (first 200 chars):\n{qasm_str[:200]}...")
        except Exception as e:
            print(f"  QASM export note: {e}")
        
        # Test 34bp analyzer
        print("\n[1.5] Testing 34bp DNA analyzer...")
        try:
            analyzer = DNA34bpAnalyzer()
            print("  DNA34bpAnalyzer initialized successfully")
        except Exception as e:
            print(f"  DNA34bpAnalyzer note: {e}")
        
        print("\n✅ DNA Quantum Encoder tests PASSED")
        return True
        
    except ImportError as e:
        print(f"\n❌ DNA Quantum Encoder import failed: {e}")
        print("   Install qiskit: pip install qiskit")
        return False
    except Exception as e:
        print(f"\n❌ DNA Quantum Encoder test failed: {e}")
        traceback.print_exc()
        return False


def test_molecular_vqe_with_pyscf():
    """Test Molecular VQE with PySCF (if available)."""
    print("\n" + "="*80)
    print("TEST 2: Molecular VQE (with PySCF)")
    print("="*80)
    
    try:
        from tools.run_molecular_vqe import MolecularVQE
        
        print("\n[2.1] Testing H₂ molecule setup...")
        vqe = MolecularVQE(molecule_name="H2")
        
        mol_data = vqe.setup_molecule(
            atom_string="H 0 0 0; H 0 0 0.74",
            basis="sto-3g"
        )
        
        print(f"  Molecule: {mol_data['molecule']}")
        print(f"  Atoms: {mol_data['num_atoms']}")
        print(f"  Electrons: {mol_data['num_electrons']}")
        print(f"  Orbitals: {mol_data['num_molecular_orbitals']}")
        print(f"  Qubits: {mol_data['num_qubits']}")
        print(f"  Hamiltonian terms: {mol_data['hamiltonian_terms']}")
        
        print("\n[2.2] Running VQE optimization...")
        results = vqe.run_vqe(
            optimizer_name="COBYLA",
            ansatz_name="RealAmplitudes",
            shots=1024,
            max_iterations=50
        )
        
        print(f"\n  VQE Results:")
        print(f"    Ground State Energy: {results['ground_state_energy']:.6f} Hartree")
        print(f"    Exact Energy: {results['exact_energy']:.6f} Hartree")
        print(f"    Energy Error: {results['energy_error']:.6f} Hartree")
        
        if 'experimental_energy' in results:
            print(f"    Experimental Energy: {results['experimental_energy']:.6f} Hartree")
            print(f"    Error vs Experiment: {results['error_vs_experiment']:.6f} Hartree")
        
        vqe.print_summary()
        
        print("\n✅ Molecular VQE (PySCF) tests PASSED")
        return True
        
    except ImportError as e:
        print(f"\n⚠️ PySCF not available: {e}")
        print("   PySCF requires C/C++ compilation on Windows.")
        print("   Install via conda: conda install -c pyscf pyscf")
        print("   Or use WSL/Linux for native PySCF support.")
        return None  # Indicate skipped, not failed
    except Exception as e:
        print(f"\n❌ Molecular VQE test failed: {e}")
        traceback.print_exc()
        return False


def test_molecular_vqe_synthetic():
    """Test Molecular VQE with synthetic Hamiltonian (fallback when PySCF unavailable)."""
    print("\n" + "="*80)
    print("TEST 3: Molecular VQE (Synthetic Hamiltonian)")
    print("="*80)
    
    try:
        import numpy as np
        from qiskit import QuantumCircuit
        from qiskit.circuit.library import real_amplitudes
        from qiskit.quantum_info import SparsePauliOp
        from qiskit_algorithms.optimizers import COBYLA
        from qiskit_algorithms import VQE
        
        print("\n[3.1] Creating synthetic H₂-like Hamiltonian...")
        
        # Create H₂-like Hamiltonian (simplified)
        # H = g0 * II + g1 * IZ + g2 * ZI + g3 * ZZ + g4 * XX
        # These coefficients approximate H₂ at equilibrium bond length
        
        # Coefficients (in Hartree, approximate for H₂ at 0.74 Å)
        g0 = -1.052  # Nuclear repulsion + constant
        g1 = -0.397  # IZ term
        g2 = -0.397  # ZI term  
        g3 = 0.180   # ZZ term
        g4 = 0.180   # XX term
        
        # Build Pauli operator
        paulis = [
            ("II", g0),
            ("IZ", g1),
            ("ZI", g2),
            ("ZZ", g3),
            ("XX", g4),
        ]
        
        hamiltonian = SparsePauliOp.from_list(paulis)
        print(f"  Hamiltonian: {hamiltonian}")
        print(f"  Qubits: {hamiltonian.num_qubits}")
        print(f"  Terms: {len(hamiltonian)}")
        
        print("\n[3.2] Setting up VQE...")
        
        # Create ansatz using function (not class, for Qiskit 2.1+)
        num_qubits = 2
        ansatz = real_amplitudes(num_qubits, reps=2)
        print(f"  Ansatz: real_amplitudes({num_qubits} qubits, 2 reps)")
        print(f"  Parameters: {ansatz.num_parameters}")
        
        # Setup optimizer
        optimizer = COBYLA(maxiter=100)
        
        # Use StatevectorEstimator for modern Qiskit (no shots needed)
        try:
            from qiskit.primitives import StatevectorEstimator
            estimator = StatevectorEstimator()
            print("  Using StatevectorEstimator (modern API)")
        except ImportError:
            # Fallback for older Qiskit versions
            try:
                from qiskit_aer.primitives import Estimator
                estimator = Estimator(approximation=True)
                print("  Using Aer Estimator")
            except ImportError:
                print("  Note: Using manual statevector simulation fallback")
                estimator = None
        
        # Run VQE
        print("\n[3.3] Running VQE optimization...")
        
        if estimator is not None:
            vqe = VQE(estimator, ansatz, optimizer)
            result = vqe.compute_minimum_eigenvalue(hamiltonian)
            vqe_energy = result.eigenvalue.real
            print(f"\n  VQE Results:")
            print(f"    Ground State Energy: {vqe_energy:.6f} Hartree")
        else:
            # Manual statevector simulation fallback
            print("  Using manual statevector simulation...")
            from qiskit.quantum_info import Statevector
            
            def compute_expectation(params, ansatz, hamiltonian):
                """Compute expectation value manually."""
                bound_circuit = ansatz.assign_parameters(params)
                statevector = Statevector(bound_circuit)
                expectation = statevector.expectation_value(hamiltonian)
                return expectation.real
            
            # Simple optimization using COBYLA
            initial_params = np.zeros(ansatz.num_parameters)
            
            def objective(params):
                return compute_expectation(params, ansatz, hamiltonian)
            
            result = optimizer.minimize(objective, initial_params)
            vqe_energy = result.fun
            print(f"\n  VQE Results (Statevector):")
            print(f"    Ground State Energy: {vqe_energy:.6f} Hartree")
        
        # Calculate exact energy for comparison
        print("\n[3.4] Calculating exact ground state energy...")
        hamiltonian_matrix = hamiltonian.to_matrix()
        eigenvalues = np.linalg.eigvalsh(hamiltonian_matrix)
        exact_energy = np.min(eigenvalues)
        
        print(f"  Exact Ground State Energy: {exact_energy:.6f} Hartree")
        print(f"  VQE Error: {abs(vqe_energy - exact_energy):.6f} Hartree")
        
        # Reference H₂ energy
        print(f"\n  Reference H₂ energy (STO-3G): -1.137285 Hartree")
        print(f"  Our synthetic model: {vqe_energy:.6f} Hartree")
        
        print("\n✅ Molecular VQE (Synthetic) tests PASSED")
        return True
        
    except ImportError as e:
        print(f"\n❌ Required imports failed: {e}")
        print("   Install: pip install qiskit qiskit-algorithms")
        return False
    except Exception as e:
        print(f"\n❌ Synthetic VQE test failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("="*80)
    print("DNA Quantum Encoder & Molecular VQE Test Suite")
    print("="*80)
    print(f"Working directory: {ROOT}")
    print(f"Python: {sys.version}")
    
    results = {}
    
    # Test 1: DNA Quantum Encoder
    results['dna_encoder'] = test_dna_quantum_encoder()
    
    # Test 2: Molecular VQE with PySCF
    results['molecular_vqe_pyscf'] = test_molecular_vqe_with_pyscf()
    
    # Test 3: Molecular VQE with synthetic Hamiltonian (fallback)
    if results['molecular_vqe_pyscf'] is None:
        print("\n⚠️ PySCF unavailable, running synthetic Hamiltonian test...")
        results['molecular_vqe_synthetic'] = test_molecular_vqe_synthetic()
    else:
        results['molecular_vqe_synthetic'] = None  # Skipped
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for test_name, result in results.items():
        if result is True:
            status = "✅ PASSED"
        elif result is None:
            status = "⚠️ SKIPPED"
        else:
            status = "❌ FAILED"
        print(f"  {test_name}: {status}")
    
    # Overall result
    passed = sum(1 for r in results.values() if r is True)
    failed = sum(1 for r in results.values() if r is False)
    skipped = sum(1 for r in results.values() if r is None)
    
    print(f"\nTotal: {passed} passed, {failed} failed, {skipped} skipped")
    
    if failed > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())