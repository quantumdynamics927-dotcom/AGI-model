# DNA-to-Quantum Circuit Module Documentation

## Overview

The `dna_quantum_circuits.py` module provides a comprehensive framework for encoding DNA sequences into quantum circuits and integrating with molecular VQE (Variational Quantum Eigensolver) calculations using qiskit-nature.

## Features

### 1. DNA-to-Quantum Circuit Encoding

**Three Encoding Schemes:**

- **Base-to-Gate Mapping**: Direct mapping of DNA bases to quantum gates
  - A → Hadamard (H) - creates superposition
  - T → Pauli-X (X) - bit flip
  - G → RZ(π/4) - phase rotation
  - C → RY(π/4) - amplitude rotation

- **Codon-Based Encoding**: Groups of 3 bases (codons) map to rotation angles
  - Each codon → single-qubit rotation
  - Angle calculated from base composition

- **Watson-Crick Pairing**: Biological base pairing with quantum entanglement
  - Complementary bases (A↔T, G↔C) on separate qubits
  - CNOT gates create entanglement between pairs

### 2. OpenQASM Integration

**Import/Export Capabilities:**

```python
from dna_quantum_circuits import DNAQuantumEncoder

encoder = DNAQuantumEncoder()

# Encode DNA to circuit
circuit = encoder.encode_sequence("ATGCATGC")

# Export to OpenQASM
qasm_str = encoder.export_to_qasm(circuit)
encoder.export_to_qasm(circuit, 'my_circuit.qasm')

# Import from OpenQASM
circuit = encoder.import_from_qasm(qasm_str)
circuit = encoder.import_from_qasm_file('my_circuit.qasm')

# Parse QASM gates
gate_info = encoder.parse_qasm_gates(qasm_str)
```

**Supported Formats:**
- OpenQASM 2.0
- OpenQASM 3.0
- Automatic version detection

### 3. Molecular VQE with qiskit-nature

**Real Quantum Chemistry Integration:**

```python
from dna_quantum_circuits import MolecularVQE

# Setup molecule
vqe = MolecularVQE('H2')
mol_data = vqe.setup_molecule(basis='sto-3g')

# Get Hamiltonian
hamiltonian = vqe.get_hamiltonian(mapper='jordan_wigner')

# Run VQE
result = vqe.run_vqe(
    ansatz_type='uccsd',
    optimizer='cobyla',
    shots=1024
)

print(f"Ground state energy: {result['energy']:.6f} Hartree")
```

**Supported Molecules:**
- H₂ (Hydrogen)
- LiH (Lithium Hydride)
- H₂O (Water)
- N₂ (Nitrogen)

**Ansatz Types:**
- UCCSD (Unitary Coupled Cluster) - chemistry-inspired
- RealAmplitudes - hardware-efficient
- TwoLocal - general purpose

**Optimizers:**
- SPSA - noisy optimization
- COBYLA - constrained optimization
- L-BFGS-B - gradient-based
- ADAM - adaptive learning rate

### 4. DNA-to-Molecule Mapping

**Biomolecular Parameter Extraction:**

```python
from dna_quantum_circuits import MolecularVQE

vqe = MolecularVQE('H2')
params = vqe.dna_to_molecule("ATGCATGC")

print(f"Molecule: {params['molecule']}")
print(f"Bond length: {params['bond_length']:.3f} Å")
print(f"Basis set: {params['basis']}")
print(f"GC content: {params['gc_content']:.2%}")
```

**Mapping Rules:**
- First 2 bases → molecule type
  - AT/TA → H₂
  - GC/CG → LiH
  - AA/TT → H₂O
  - GG/CC → N₂
- Sequence length → bond length scaling
- GC content → basis set selection

### 5. Integrated DNA-VQE

**End-to-End Workflow:**

```python
from dna_quantum_circuits import DNAVQEIntegrator

integrator = DNAVQEIntegrator()

# Single sequence
result = integrator.dna_sequence_to_vqe("ATGC")

# Multiple sequences
comparison = integrator.compare_dna_molecules(["ATGC", "GCGC", "ATAT"])

# Export results
integrator.export_results('dna_vqe_results.json')
```

### 6. 34bp Consciousness Analysis

**Specialized Analysis for 34bp Sequences:**

```python
from dna_quantum_circuits import DNA34bpAnalyzer

analyzer = DNA34bpAnalyzer()

# Generate Fibonacci-weighted sequence
fib_seq = analyzer.generate_fibonacci_sequence()

# Create 102-qubit circuit (34 Watson + 34 Crick + 34 Bridge)
circuit = analyzer.create_34bp_circuit(fib_seq)

# Analyze consciousness peak at position 20
analysis = analyzer.analyze_consciousness_peak(counts)
```

## Installation

### Requirements

```bash
pip install qiskit>=1.0.0
pip install qiskit-nature>=0.6.0
pip install qiskit-algorithms>=0.2.0
pip install pyscf>=2.4.0
```

### Full Installation

```bash
# From requirements.txt
pip install -r requirements.txt

# Or individually
pip install qiskit qiskit-nature qiskit-algorithms pyscf numpy matplotlib
```

## Usage Examples

### Basic DNA Encoding

```python
from dna_quantum_circuits import DNAQuantumEncoder

# Create encoder
encoder = DNAQuantumEncoder(encoding_scheme='base_to_gate')

# Encode DNA sequence
dna_sequence = "ATGCATGCATGC"
circuit = encoder.encode_sequence(dna_sequence)

# Analyze circuit
analysis = encoder.analyze_dna_circuit(circuit)
print(f"Qubits: {analysis['circuit_width']}")
print(f"Depth: {analysis['circuit_depth']}")
print(f"Gates: {analysis['total_gates']}")

# Export to file
encoder.export_to_qasm(circuit, 'dna_circuit.qasm')
```

### Molecular VQE

```python
from dna_quantum_circuits import MolecularVQE

# Setup H2 molecule
vqe = MolecularVQE('H2')
vqe.setup_molecule(basis='sto-3g')

# Run VQE with UCCSD ansatz
result = vqe.run_vqe(
    ansatz_type='uccsd',
    optimizer='cobyla',
    shots=1024
)

print(f"Energy: {result['energy']:.6f} Hartree")
print(f"Error: {result['absolute_error']:.6f} Hartree")
```

### DNA-to-VQE Integration

```python
from dna_quantum_circuits import DNAVQEIntegrator

integrator = DNAVQEIntegrator()

# Process DNA sequence
result = integrator.dna_sequence_to_vqe("ATGC")

print(f"DNA: {result['dna_sequence']}")
print(f"Molecule: {result['molecular_params']['molecule']}")
print(f"VQE Energy: {result['vqe_result']['energy']:.6f} Hartree")
```

### OpenQASM Parsing

```python
from dna_quantum_circuits import DNAQuantumEncoder

encoder = DNAQuantumEncoder()

# Import from file
circuit = encoder.import_from_qasm_file('circuit.qasm')

# Parse gate information
gate_info = encoder.parse_qasm_gates(qasm_string)

print(f"Total gates: {gate_info['total_gates']}")
print(f"Gate types: {gate_info['gate_types']}")
```

## API Reference

### DNAQuantumEncoder

**Constructor:**
```python
DNAQuantumEncoder(encoding_scheme: str = 'base_to_gate')
```

**Methods:**
- `encode_sequence(dna_sequence, num_qubits=None, add_measurements=True)` → QuantumCircuit
- `export_to_qasm(circuit, filename=None)` → str
- `import_from_qasm(qasm_string)` → QuantumCircuit
- `import_from_qasm_file(filename)` → QuantumCircuit
- `parse_qasm_gates(qasm_string)` → Dict
- `analyze_dna_circuit(circuit)` → Dict
- `get_circuit_history()` → List[Dict]
- `save_history(filename)` → None

### MolecularVQE

**Constructor:**
```python
MolecularVQE(molecule_name: str = 'H2')
```

**Methods:**
- `setup_molecule(atom_string=None, basis='sto-3g', charge=0, spin=0)` → Dict
- `get_hamiltonian(mapper='jordan_wigner')` → SparsePauliOp
- `create_ansatz(ansatz_type='uccsd', reps=1)` → QuantumCircuit
- `run_vqe(ansatz_type='uccsd', optimizer='spsa', mapper='jordan_wigner', shots=1024)` → Dict
- `dna_to_molecule(dna_sequence)` → Dict

### DNAVQEIntegrator

**Constructor:**
```python
DNAVQEIntegrator()
```

**Methods:**
- `dna_sequence_to_vqe(dna_sequence, optimizer='spsa', shots=1024)` → Dict
- `compare_dna_molecules(dna_sequences)` → Dict
- `export_results(filename='dna_vqe_results.json')` → None

### DNA34bpAnalyzer

**Constructor:**
```python
DNA34bpAnalyzer()
```

**Methods:**
- `create_34bp_circuit(sequence_34bp, add_measurements=True)` → QuantumCircuit
- `analyze_consciousness_peak(counts)` → Dict
- `generate_fibonacci_sequence(length=34)` → str
- `compare_sequences(sequences)` → Dict

## File Formats

### OpenQASM Export

```qasm
OPENQASM 2.0;
include "qelib1.inc";
qreg q[8];
creg c[8];
h q[0];
x q[1];
rz(0.7853981633974483) q[2];
ry(0.7853981633974483) q[3];
measure q[0] -> c[0];
measure q[1] -> c[1];
measure q[2] -> c[2];
measure q[3] -> c[3];
```

### Results JSON

```json
{
  "dna_sequence": "ATGC",
  "dna_analysis": {
    "gate_counts": {"h": 1, "x": 1, "rz": 1, "ry": 1},
    "total_gates": 4,
    "circuit_depth": 1,
    "circuit_width": 4
  },
  "molecular_params": {
    "molecule": "H2",
    "bond_length": 0.74,
    "basis": "sto-3g",
    "gc_content": 0.5
  },
  "vqe_result": {
    "energy": -1.137285,
    "optimizer": "cobyla",
    "ansatz": "uccsd",
    "absolute_error": 0.000123,
    "relative_error": 0.0108
  }
}
```

## Performance Considerations

### VQE Calculations

- **Small basis sets** (sto-3g) for quick testing
- **Fewer shots** (512-1024) for demonstration
- **COBYLA optimizer** for noise-free simulation
- **UCCSD ansatz** for chemistry accuracy

### Circuit Complexity

- **Base-to-gate**: O(n) gates for n-base sequence
- **Codon encoding**: O(n/3) gates
- **Watson-Crick**: O(2n) gates with entanglement

### Memory Usage

- 34bp sequences → 102-qubit circuits
- Full statevector simulation: 2^102 complex amplitudes (infeasible)
- Use shot-based simulation or real hardware for large circuits

## Troubleshooting

### Import Errors

```bash
# qiskit-nature not found
pip install qiskit-nature pyscf

# qiskit-algorithms not found
pip install qiskit-algorithms
```

### VQE Convergence Issues

- Try different optimizers (SPSA for noisy, COBYLA for noise-free)
- Increase maxiter: `COBYLA(maxiter=2000)`
- Use better initial parameters
- Reduce basis set size

### Memory Errors

- Use smaller sequences
- Reduce number of qubits
- Use shot-based simulation instead of statevector

## References

1. DNA quantum walks: https://arxiv.org/abs/quant-ph/0403006
2. Genetic code in quantum systems: https://doi.org/10.1038/s41598-020-67183-3
3. Qiskit Nature documentation: https://qiskit.org/ecosystem/nature/
4. VQE algorithm: https://arxiv.org/abs/1304.3061

## License

AGI-model Quantum Computing Team - April 2026
