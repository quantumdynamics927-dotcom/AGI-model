# Observer Symmetry Circuit Families

## Family 1: 3-Qubit Bilateral Observer (OBS-3Q)

### Purpose
Minimal bilateral topology for testing symmetry-breaking detection.

### Structure
```
Q0 (Left) ────■────
              │
Q1 (Center) ──X──── H ──── M
              │
Q2 (Right) ───■────
```

### Operations
1. Initialize all qubits to |0⟩
2. Apply Hadamard to Q0 and Q2
3. CNOT Q0 → Q1 (control: Q0, target: Q1)
4. CNOT Q2 → Q1 (control: Q2, target: Q1)
5. Hadamard on Q1
6. Measure Q1 (center observer)

### Expected Behavior
- Undisturbed: Q1 measurement shows balanced superposition
- Left interception (measure Q0 before step 5): Biases Q1 outcome
- Right interception (measure Q2 before step 5): Biases Q1 outcome

### Parameters
| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| shots | 8192 | 1024-32768 | Number of circuit executions |
| interception_point | None | 0-5 | Gate index for interception |

### QASM Representation
```qasm
OPENQASM 2.0;
include "qelib1.inc";
qreg q[3];
creg c[1];

// Initialize bilateral structure
h q[0];
h q[2];

// Entangle with center
cx q[0], q[1];
cx q[2], q[1];

// Observer measurement
h q[1];
measure q[1] -> c[0];
```

---

## Family 2: 5-Qubit Mirrored Topology (OBS-5Q)

### Purpose
Extended bilateral structure with mirrored reservoirs for enhanced detection.

### Structure
```
Q0 (Left-1) ────■────
               │
Q1 (Left-2) ───■─────■────
                     │
Q2 (Center) ─────────X──── H ──── M
                     │
Q3 (Right-2) ──■─────■────
               │
Q4 (Right-1) ──■────
```

### Operations
1. Initialize all qubits to |0⟩
2. Apply Hadamard to Q0, Q1, Q3, Q4
3. CNOT Q0 → Q2, CNOT Q1 → Q2
4. CNOT Q3 → Q2, CNOT Q4 → Q2
5. Hadamard on Q2
6. Measure Q2 (center observer)

### Expected Behavior
- More robust symmetry due to multiple entanglement paths
- Interception on any single reservoir qubit produces smaller but still detectable deviation
- Bilateral interception (both sides) produces maximum disturbance

### Parameters
| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| shots | 8192 | 1024-32768 | Number of circuit executions |
| mirror_depth | 2 | 1-4 | Number of qubits per side |

---

## Family 3: Entropy Generation Mode (OBS-ENT)

### Purpose
Use bilateral topology for QRNG with built-in tamper detection.

### Structure
Same as OBS-3Q, but measure all three qubits for entropy extraction.

### Operations
1. Run OBS-3Q circuit
2. Measure Q0, Q1, Q2
3. Extract 3 bits of entropy
4. Compute symmetry metrics on-the-fly
5. Flag outputs with suspicious symmetry deviation

### Expected Behavior
- Normal operation: Balanced 3-bit output distribution
- Interception: Biased distribution + detectable symmetry loss
- Output: (bits, symmetry_score, tamper_flag)

### Parameters
| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| shots | 8192 | 1024-32768 | Number of circuit executions |
| symmetry_threshold | 0.95 | 0.9-0.99 | Minimum symmetry for valid output |
| entropy_bits | 3 | 1-3 | Number of bits to extract |

---

## Family 4: Teleportation-Based Verification (OBS-TEL)

### Purpose
Use bilateral structure for quantum teleportation with verification.

### Structure
```
Q0 (Source) ────■──── H ──── M
               │
Q1 (Channel) ──X──── M
               │
Q2 (Receiver) ─■──── X ──── M (if Q1=1)
```

### Operations
1. Prepare entangled pair Q1-Q2
2. Entangle Q0 with Q1
3. Measure Q0, Q1 in Bell basis
4. Apply correction to Q2 based on measurement
5. Verify Q2 state matches original Q0 state

### Expected Behavior
- Undisturbed: Q2 state matches Q0 with high fidelity
- Channel interception: Fidelity loss + detectable correlation shift

### Parameters
| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| shots | 8192 | 1024-32768 | Number of circuit executions |
| fidelity_threshold | 0.95 | 0.9-0.99 | Minimum fidelity for valid teleport |

---

## Circuit Selection Guide

| Use Case | Recommended Family | Rationale |
|----------|-------------------|-----------|
| Initial testing | OBS-3Q | Minimal complexity, clear signal |
| Enhanced detection | OBS-5Q | More robust, multiple interception points |
| QRNG application | OBS-ENT | Built-in entropy + tamper detection |
| Transport security | OBS-TEL | Teleportation-based verification |

## Implementation Priority

1. **OBS-3Q**: Implement first, validate hypothesis
2. **OBS-ENT**: If OBS-3Q succeeds, extend to entropy mode
3. **OBS-5Q**: If OBS-3Q succeeds, test enhanced detection
4. **OBS-TEL**: If OBS-ENT succeeds, extend to transport