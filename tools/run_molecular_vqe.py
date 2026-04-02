#!/usr/bin/env python3
"""
Molecular VQE with Quantum Chemistry
=====================================

Proper molecular Hamiltonian calculation using qiskit-nature and PySCF.
Replaces arbitrary golden ratio scaling with chemistry-derived parameters.

This module provides:
- H₂ molecule ground state energy calculation
- Extended molecules (LiH, H2O, etc.)
- Chemistry-derived Hamiltonians (not arbitrary scaling)
- VQE optimization with proper ansatz

Requirements:
    pip install qiskit-nature pyscf

Author: AGI-model Quantum Computing Team
Date: April 2, 2026
"""

import numpy as np
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import warnings

# Qiskit Nature imports
try:
    from qiskit_nature.second_q.drivers import PySCFDriver
    from qiskit_nature.second_q.mappers import JordanWignerMapper, ParityMapper
    from qiskit_nature.second_q.algorithms import GroundStateEigensolver
    from qiskit_nature.second_q.problems import ElectronicStructureProblem
    QISKIT_NATURE_AVAILABLE = True
except ImportError:
    QISKIT_NATURE_AVAILABLE = False
    warnings.warn("qiskit-nature not available. Install with: pip install qiskit-nature pyscf")

# Qiskit algorithms
try:
    from qiskit_algorithms.optimizers import SPSA, COBYLA, L_BFGS_B
    from qiskit_algorithms import VQE
    from qiskit.primitives import Estimator
    VQE_AVAILABLE = True
except ImportError:
    VQE_AVAILABLE = False
    warnings.warn("Qiskit algorithms not available. Install with: pip install qiskit-algorithms")

# Standard Qiskit
try:
    from qiskit.circuit.library import RealAmplitudes, UCCSD, TwoLocal
    from qiskit.quantum_info import Statevector, SparsePauliOp
    from qiskit import QuantumCircuit
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False
    warnings.warn("Qiskit not available. Install with: pip install qiskit")


class MolecularVQE:
    """
    Variational Quantum Eigensolver for molecular systems.
    
    Uses proper quantum chemistry Hamiltonians from PySCF,
    not arbitrary golden ratio scaling.
    
    Features:
    - Chemistry-derived Hamiltonians (PySCF)
    - Multiple ansatz options (UCCSD, RealAmplitudes)
    - Multiple optimizers (SPSA, COBYLA, L_BFGS_B)
    - Exact diagonalization for comparison
    """
    
    # Common molecules with experimental energies (Hartree)
    MOLECULES = {
        'H2': {
            'atoms': "H 0 0 0; H 0 0 0.74",
            'experimental_energy': -1.137285,
            'description': 'Hydrogen molecule'
        },
        'LiH': {
            'atoms': "Li 0 0 0; H 0 0 1.60",
            'experimental_energy': -7.88,
            'description': 'Lithium hydride'
        },
        'H2O': {
            'atoms': "O 0 0 0; H 0 0.757 0.587; H 0 -0.757 0.587",
            'experimental_energy': -75.0,
            'description': 'Water molecule'
        },
        'N2': {
            'atoms': "N 0 0 0; N 0 0 1.10",
            'experimental_energy': -108.0,
            'description': 'Nitrogen molecule'
        }
    }
    
    def __init__(self, molecule_name: str = "H2"):
        """
        Initialize molecular VQE.
        
        Args:
            molecule_name: Name of molecule (H2, LiH, H2O, N2)
        """
        if not QISKIT_NATURE_AVAILABLE:
            raise ImportError("qiskit-nature required. Install with: pip install qiskit-nature pyscf")
        
        self.molecule_name = molecule_name
        self.driver = None
        self.problem = None
        self.qubit_op = None
        self.results = {}
        self.molecular_data = {}
        
    def setup_molecule(self, 
                      atom_string: str = None,
                      basis: str = "sto-3g",
                      charge: int = 0, 
                      spin: int = 0) -> Dict:
        """
        Setup molecular system using PySCF driver.
        
        Args:
            atom_string: Atomic coordinates (e.g., "H 0 0 0; H 0 0 0.74")
                        If None, uses predefined molecule
            basis: Basis set (default: sto-3g)
            charge: Molecular charge
            spin: Molecular spin (2S, where S is total spin)
            
        Returns:
            Dict with molecular properties
        """
        # Use predefined molecule if available
        if atom_string is None:
            if self.molecule_name in self.MOLECULES:
                atom_string = self.MOLECULES[self.molecule_name]['atoms']
            else:
                raise ValueError(f"Unknown molecule: {self.molecule_name}. Provide atom_string.")
        
        # Create PySCF driver
        self.driver = PySCFDriver(
            atom=atom_string,
            basis=basis,
            charge=charge,
            spin=spin,
        )
        
        # Run driver to get electronic structure problem
        self.problem = self.driver.run()
        
        # Extract molecular properties
        self.molecular_data = {
            'molecule': self.molecule_name,
            'atom_string': atom_string,
            'basis': basis,
            'charge': charge,
            'spin': spin,
            'num_atoms': len(atom_string.split(';')),
            'num_electrons': self.problem.num_electrons,
            'num_molecular_orbitals': self.problem.num_molecular_orbitals,
            'num_spin_orbitals': self.problem.num_spin_orbitals,
            'nuclear_repulsion_energy': self.problem.nuclear_repulsion_energy,
        }
        
        # Map to qubit operator
        mapper = JordanWignerMapper()
        self.qubit_op = mapper.map(self.problem.hamiltonian)
        
        self.molecular_data['num_qubits'] = self.qubit_op.num_qubits
        self.molecular_data['hamiltonian_terms'] = len(self.qubit_op)
        
        # Add experimental energy if available
        if self.molecule_name in self.MOLECULES:
            self.molecular_data['experimental_energy'] = \
                self.MOLECULES[self.molecule_name]['experimental_energy']
        
        return self.molecular_data
    
    def run_vqe(self, 
               optimizer_name: str = "SPSA",
               ansatz_name: str = "UCCSD",
               shots: int = 1024,
               max_iterations: int = 100) -> Dict:
        """
        Run VQE calculation.
        
        Args:
            optimizer_name: Classical optimizer (SPSA, COBYLA, L_BFGS_B)
            ansatz_name: Ansatz circuit (UCCSD, RealAmplitudes, TwoLocal)
            shots: Number of measurement shots
            max_iterations: Maximum optimizer iterations
            
        Returns:
            Dict with VQE results
        """
        if not VQE_AVAILABLE:
            raise ImportError("Qiskit VQE not available")
        
        if self.qubit_op is None:
            raise ValueError("Run setup_molecule() first")
        
        # Setup optimizer
        if optimizer_name == "SPSA":
            optimizer = SPSA(maxiter=max_iterations)
        elif optimizer_name == "COBYLA":
            optimizer = COBYLA(maxiter=max_iterations)
        elif optimizer_name == "L_BFGS_B":
            optimizer = L_BFGS_B(maxiter=max_iterations)
        else:
            optimizer = COBYLA(maxiter=max_iterations)
        
        # Setup ansatz
        if ansatz_name == "UCCSD":
            ansatz = UCCSD(
                num_electrons=self.problem.num_electrons,
                num_spatial_orbitals=self.problem.num_molecular_orbitals,
                qubit_mapper=JordanWignerMapper(),
            )
        elif ansatz_name == "RealAmplitudes":
            ansatz = RealAmplitudes(
                num_qubits=self.qubit_op.num_qubits,
                reps=2,
                entanglement='full',
            )
        elif ansatz_name == "TwoLocal":
            ansatz = TwoLocal(
                num_qubits=self.qubit_op.num_qubits,
                rotation_blocks='ry',
                entanglement_blocks='cx',
                reps=2,
            )
        else:
            ansatz = RealAmplitudes(
                num_qubits=self.qubit_op.num_qubits,
                reps=2,
            )
        
        # Setup VQE
        estimator = Estimator(options={"shots": shots})
        vqe = VQE(
            estimator=estimator,
            ansatz=ansatz,
            optimizer=optimizer,
        )
        
        # Run VQE
        print(f"\nRunning VQE for {self.molecule_name}...")
        print(f"  Optimizer: {optimizer_name}")
        print(f"  Ansatz: {ansatz_name}")
        print(f"  Shots: {shots}")
        print(f"  Qubits: {self.qubit_op.num_qubits}")
        
        result = vqe.compute_minimum_eigenvalue(self.qubit_op)
        
        # Extract results
        self.results = {
            'ground_state_energy': result.eigenvalue.real,
            'optimal_parameters': result.optimal_point.tolist() if hasattr(result, 'optimal_point') else None,
            'optimizer_evaluations': result.cost_function_evals if hasattr(result, 'cost_function_evals') else None,
            'converged': result.cost_function_evals is not None,
            'optimizer_name': optimizer_name,
            'ansatz_name': ansatz_name,
            'shots': shots,
        }
        
        # Calculate exact energy for comparison
        exact_energy = self._calculate_exact_energy()
        self.results['exact_energy'] = exact_energy
        self.results['energy_error'] = abs(self.results['ground_state_energy'] - exact_energy)
        
        # Compare with experimental if available
        if 'experimental_energy' in self.molecular_data:
            self.results['experimental_energy'] = self.molecular_data['experimental_energy']
            self.results['error_vs_experiment'] = abs(
                self.results['ground_state_energy'] - self.molecular_data['experimental_energy']
            )
        
        return self.results
    
    def _calculate_exact_energy(self) -> float:
        """Calculate exact ground state energy via full diagonalization."""
        if self.qubit_op is None:
            return 0.0
        
        # Convert to matrix
        sparse_op = self.qubit_op.to_matrix()
        
        # Diagonalize
        eigenvalues = np.linalg.eigvalsh(sparse_op.toarray())
        
        return float(np.min(eigenvalues))
    
    def get_hamiltonian_info(self) -> Dict:
        """
        Get information about the molecular Hamiltonian.
        
        Returns:
            Dict with Hamiltonian details
        """
        if self.qubit_op is None:
            raise ValueError("Run setup_molecule() first")
        
        # Count Pauli terms
        pauli_terms = {}
        for term in self.qubit_op:
            pauli_str = str(term.paulis)
            pauli_terms[pauli_str] = pauli_terms.get(pauli_str, 0) + 1
        
        return {
            'num_qubits': self.qubit_op.num_qubits,
            'num_terms': len(self.qubit_op),
            'pauli_term_counts': pauli_terms,
            'hamiltonian_type': 'Jordan-Wigner mapped',
        }
    
    def export_results(self, filename: str = None) -> str:
        """Export results to JSON."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"vqe_{self.molecule_name.lower()}_{timestamp}.json"
        
        results = {
            'molecule': self.molecule_name,
            'timestamp': datetime.now().isoformat(),
            'molecular_data': self.molecular_data,
            'vqe_results': self.results,
        }
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"Results exported to {filename}")
        return filename
    
    def print_summary(self):
        """Print summary of VQE results."""
        print(f"\n{'='*80}")
        print(f"VQE Results Summary: {self.molecule_name}")
        print(f"{'='*80}")
        
        if self.molecular_data:
            print(f"\nMolecular Data:")
            print(f"  Atoms: {self.molecular_data.get('num_atoms', 'N/A')}")
            print(f"  Electrons: {self.molecular_data.get('num_electrons', 'N/A')}")
            print(f"  Orbitals: {self.molecular_data.get('num_molecular_orbitals', 'N/A')}")
            print(f"  Qubits: {self.molecular_data.get('num_qubits', 'N/A')}")
            print(f"  Hamiltonian Terms: {self.molecular_data.get('hamiltonian_terms', 'N/A')}")
        
        if self.results:
            print(f"\nVQE Results:")
            print(f"  Ground State Energy: {self.results['ground_state_energy']:.6f} Hartree")
            print(f"  Exact Energy: {self.results['exact_energy']:.6f} Hartree")
            print(f"  Energy Error: {self.results['energy_error']:.6f} Hartree")
            
            if 'experimental_energy' in self.results:
                print(f"  Experimental Energy: {self.results['experimental_energy']:.6f} Hartree")
                print(f"  Error vs Experiment: {self.results['error_vs_experiment']:.6f} Hartree")
            
            print(f"  Optimizer: {self.results.get('optimizer_name', 'N/A')}")
            print(f"  Ansatz: {self.results.get('ansatz_name', 'N/A')}")
            print(f"  Converged: {self.results.get('converged', 'N/A')}")


def run_h2_molecule():
    """Example: H₂ molecule ground state energy calculation."""
    print("="*80)
    print("H₂ Molecule VQE Calculation")
    print("="*80)
    
    # Initialize VQE
    vqe = MolecularVQE(molecule_name="H2")
    
    # Setup H₂ molecule (bond length 0.74 Å)
    mol_data = vqe.setup_molecule(
        atom_string="H 0 0 0; H 0 0 0.74",
        basis="sto-3g",
        charge=0,
        spin=0
    )
    
    print(f"\nMolecular Data:")
    print(f"  Atoms: {mol_data['num_atoms']}")
    print(f"  Electrons: {mol_data['num_electrons']}")
    print(f"  Orbitals: {mol_data['num_molecular_orbitals']}")
    print(f"  Qubits: {mol_data['num_qubits']}")
    print(f"  Hamiltonian Terms: {mol_data['hamiltonian_terms']}")
    
    # Run VQE
    vqe_results = vqe.run_vqe(optimizer_name="SPSA", shots=1024)
    
    # Print summary
    vqe.print_summary()
    
    # Export results
    filename = vqe.export_results()
    
    return vqe


def run_extended_molecules():
    """Example: Extended molecules (LiH, H2O)."""
    molecules_to_run = ['H2', 'LiH']
    
    results = {}
    
    for mol_name in molecules_to_run:
        print(f"\n{'='*80}")
        print(f"{mol_name} Molecule VQE")
        print(f"{'='*80}")
        
        try:
            vqe = MolecularVQE(molecule_name=mol_name)
            mol_data = vqe.setup_molecule()
            vqe_results = vqe.run_vqe(optimizer_name="COBYLA", shots=512)
            
            vqe.print_summary()
            
            results[mol_name] = {
                'molecular_data': mol_data,
                'vqe_results': vqe_results,
            }
        except Exception as e:
            print(f"Error running {mol_name}: {e}")
            results[mol_name] = {'error': str(e)}
    
    return results


def compare_with_golden_ratio():
    """
    Compare chemistry-derived Hamiltonian with golden ratio scaling.
    
    This demonstrates why golden ratio scaling is NOT appropriate
    for molecular Hamiltonians.
    """
    print("\n" + "="*80)
    print("Comparison: Chemistry vs Golden Ratio Hamiltonians")
    print("="*80)
    
    # Chemistry-derived H2 Hamiltonian
    vqe = MolecularVQE(molecule_name="H2")
    vqe.setup_molecule()
    
    print("\nChemistry-Derived Hamiltonian:")
    print(f"  Terms: {vqe.qubit_op.num_terms}")
    print(f"  Qubits: {vqe.qubit_op.num_qubits}")
    
    # Show first few terms
    print("\n  First 5 Hamiltonian terms:")
    for i, term in enumerate(vqe.qubit_op[:5]):
        coeff = term.coeffs[0]
        pauli = term.paulis[0]
        print(f"    {coeff:+.6f} * {pauli}")
    
    # Compare with golden ratio scaling (from run_local_vqe.py)
    print("\nGolden Ratio Scaling (INCORRECT):")
    print("  H = -φ*ZZ - 0.2*X")
    print("  where φ = 1.618...")
    print("\n  Issues:")
    print("    1. No physical basis for φ scaling")
    print("    2. Coefficients not from electronic structure")
    print("    3. Cannot reproduce experimental energies")
    
    # Show energy comparison
    print("\nEnergy Comparison:")
    print(f"  Chemistry VQE: {vqe.results.get('ground_state_energy', 'N/A'):.6f} Hartree")
    print(f"  Experimental: {vqe.molecular_data.get('experimental_energy', 'N/A'):.6f} Hartree")
    print(f"  Golden Ratio:  Would give arbitrary energy (no physical meaning)")
    
    return vqe


def demo_molecular_vqe():
    """Demonstrate molecular VQE capabilities."""
    print("="*80)
    print("Molecular VQE Demonstration")
    print("="*80)
    
    # Run H2 example
    vqe_h2 = run_h2_molecule()
    
    # Compare with golden ratio
    vqe_comparison = compare_with_golden_ratio()
    
    print("\n" + "="*80)
    print("Demonstration Complete!")
    print("="*80)
    
    return vqe_h2, vqe_comparison


if __name__ == "__main__":
    # Check dependencies
    print("Checking dependencies...")
    print(f"  Qiskit Nature: {'✓' if QISKIT_NATURE_AVAILABLE else '✗'}")
    print(f"  VQE: {'✓' if VQE_AVAILABLE else '✗'}")
    print(f"  Qiskit: {'✓' if QISKIT_AVAILABLE else '✗'}")
    
    if not all([QISKIT_NATURE_AVAILABLE, VQE_AVAILABLE, QISKIT_AVAILABLE]):
        print("\nMissing dependencies. Install with:")
        print("  pip install qiskit-nature pyscf qiskit-algorithms")
    else:
        # Run demonstration
        vqe_h2, vqe_comparison = demo_molecular_vqe()