# Teleportation Circuits Directory

This directory contains OpenQASM circuits for manual execution on IBM Quantum hardware.

## Files

### OpenQASM 2.0 Circuits (Standard)

| File | Description | Reference Job |
|------|-------------|---------------|
| `teleport_circuit_1.qasm` | Standard teleportation | d6kvddgfh9oc73emadvg |
| `teleport_circuit_2.qasm` | Standard teleportation | d6kvdfs3pels739umfg0 |
| `teleport_circuit_3.qasm` | Standard teleportation | d6kvdjgfh9oc73emae50 |
| `teleport_circuit_4.qasm` | Standard teleportation | d6kvdm43pels739umfog |

### OpenQASM 3 Circuits (Dynamic)

| File | Description | Reference Job |
|------|-------------|---------------|
| `teleport_circuit_dynamic_1.qasm` | Dynamic circuit with conditional corrections | d6kvddgfh9oc73emadvg |
| `teleport_circuit_dynamic_2.qasm` | Dynamic circuit with conditional corrections | d6kvdfs3pels739umfg0 |
| `teleport_circuit_dynamic_3.qasm` | Dynamic circuit with conditional corrections | d6kvdjgfh9oc73emae50 |
| `teleport_circuit_dynamic_4.qasm` | Dynamic circuit with conditional corrections | d6kvdm43pels739umfog |

## Circuit Description

All circuits implement the same quantum teleportation protocol:

**Target State**: RY(π/3) · RZ(π/7) |0⟩

**Protocol**:
1. Prepare state |ψ⟩ = RY(π/3) · RZ(π/7) |0⟩ on Alice's qubit (q[0])
2. Create EPR pair |Φ+⟩ between Alice (q[1]) and Bob (q[2])
3. Alice performs Bell measurement on q[0] and q[1]
4. Bob applies corrections based on Alice's measurements
5. Measure Bob's qubit (q[2])

**Qubit Allocation**:
- q[0]: Alice's qubit (state to teleport)
- q[1]: EPR pair qubit 1 (Alice's half)
- q[2]: EPR pair qubit 2 (Bob's qubit - receives teleported state)

## OpenQASM 2.0 vs OpenQASM 3

### OpenQASM 2.0 (Standard)
- Uses `measure q[i] -> c[i]` syntax
- Conditional corrections applied in post-processing
- Compatible with all IBM Quantum backends

### OpenQASM 3 (Dynamic)
- Uses `c[i] = measure q[i]` syntax
- Includes `if` statements for conditional corrections
- Requires dynamic circuit support on backend

## Manual Execution

### Using IBM Quantum Lab

1. Go to [IBM Quantum Lab](https://quantum.cloud.ibm.com/)
2. Create a new notebook
3. Upload the QASM file or copy the circuit code
4. Run using:

```python
from qiskit import QuantumCircuit
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

# Load circuit
circuit = QuantumCircuit.from_qasm_file("teleport_circuit_1.qasm")

# Connect to IBM Quantum
service = QiskitRuntimeService()
backend = service.backend("ibm_fez")  # or your preferred backend

# Transpile and run
from qiskit.transpiler.preset_pass_managers import generate_preset_pass_manager
pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
transpiled = pm.run(circuit)

sampler = SamplerV2(backend)
job = sampler.run([transpiled], shots=1024)
print(f"Job ID: {job.job_id()}")
```

### Using Python Script

```bash
# Run single circuit
python run_circuits_manually.py --circuit circuits/teleport_circuit_1.qasm --shots 1024

# Run all 4 circuits
python run_circuits_manually.py --all --shots 1024 --backend ibm_fez

# Run and wait for results
python run_circuits_manually.py --all --shots 1024 --wait
```

## Fidelity Calculation

After execution, compute fidelity:

$$F = \sqrt{P_{\text{expected}}(0) \times P_{\text{measured}}(0)} + \sqrt{P_{\text{expected}}(1) \times P_{\text{measured}}(1)}$$

Where:
- $P_{\text{expected}}(0) = \cos^2(\pi/6) \approx 0.75$
- $P_{\text{expected}}(1) = \sin^2(\pi/6) \approx 0.25$

**Classical Threshold**: F > 2/3 ≈ 0.667

## Notes

- All circuits use 3 qubits minimum
- Recommended shots: 1024 or higher
- For dynamic circuits, ensure backend supports dynamic circuits
- Corrections in OpenQASM 2.0 version must be applied classically in post-processing