# Parity Witness Circuit Families

## Family 1: Basic Parity Witness (PW-3Q)

### Purpose
Minimal parity extraction circuit for testing correlation-based tamper detection.

### Structure
```
D0 ────H────■────
            │
D1 ────H────■────
            │
A  ────────X──── H ──── M
```

### Operations
1. Initialize D0, D1 to |0⟩, A to |0⟩
2. Apply Hadamard to D0, D1 (create superposition)
3. CNOT D0 → A (parity bit 1)
4. CNOT D1 → A (parity bit 2)
5. Hadamard on A
6. Measure A (parity readout)

### Expected Behavior
- Baseline: Balanced parity distribution
- Intercept D0: Parity bias due to correlation disturbance
- Intercept D1: Parity bias due to correlation disturbance
- Intercept both: Maximum disturbance

### Parameters
| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| shots | 8192 | 1024-32768 | Number of circuit executions |
| interception_qubit | None | 0, 1 | Data qubit to intercept |

### QASM Representation
```qasm
OPENQASM 2.0;
include "qelib1.inc";
qreg q[3];
creg c[1];

// Data qubits: q[0], q[1]
// Ancilla: q[2]

// Create superposition on data qubits
h q[0];
h q[1];

// Extract parity to ancilla
cx q[0], q[2];
cx q[1], q[2];

// Parity measurement
h q[2];
measure q[2] -> c[0];
```

---

## Family 2: Entangled Parity Witness (PW-3Q-E)

### Purpose
Parity witness with entangled data qubits for enhanced correlation sensitivity.

### Structure
```
D0 ────H────■────■────
            │    │
D1 ─────────X────■────
                 │
A  ─────────────X──── H ──── M
```

### Operations
1. Create Bell pair between D0 and D1
2. Extract parity via ancilla A
3. Measure A for parity readout

### Expected Behavior
- Stronger correlation between D0 and D1
- More sensitive to interception disturbance
- Higher baseline correlation = larger detection signal

---

## Family 3: Mirrored Parity Witness (PW-4Q)

### Purpose
Bilateral parity structure for asymmetric interception detection.

### Structure
```
D0 ────■────
       │
D1 ────■────
       │
A_L ───X──── H ──── M_L

D2 ────■────
       │
D3 ────■────
       │
A_R ───X──── H ──── M_R
```

### Operations
1. Two independent parity circuits (left and right)
2. Compare parity distributions and cross-correlation
3. Detect asymmetric interception

### Expected Behavior
| Condition | Left Parity | Right Parity | Cross-Corr |
|-----------|-------------|--------------|------------|
| Baseline | Balanced | Balanced | Reference |
| Intercept left | Disturbed | Balanced | Changed |
| Intercept right | Balanced | Disturbed | Changed |
| Intercept both | Disturbed | Disturbed | Maximum change |

### Parameters
| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| shots | 8192 | 1024-32768 | Number of circuit executions |
| interception_side | None | left, right, both | Which side to intercept |

---

## Family 4: Coherence-Sensitive Parity (PW-3Q-C)

### Purpose
Phase-sensitive parity extraction for coherence-based detection.

### Structure
```
D0 ────H────■──── Rz(θ) ────
            │
D1 ────H────■──── Rz(θ) ────
            │
A  ────────X──── H ──── M
```

### Operations
1. Prepare data qubits in superposition
2. Extract parity to ancilla
3. Apply phase rotation Rz(θ) to data qubits
4. Measure ancilla
5. Repeat for multiple θ values

### Expected Behavior
- Parity oscillates with phase angle θ
- Oscillation amplitude indicates coherence
- Interception reduces amplitude (decoherence effect)

### Parameters
| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| shots | 8192 | 1024-32768 | Number of circuit executions |
| phase_angles | [0, π/4, π/2, 3π/4, π] | Any | Phase angles to test |
| interception_qubit | None | 0, 1 | Data qubit to intercept |

### Oscillation Analysis
```python
def analyze_oscillation(parity_probs: List[float], phases: List[float]) -> dict:
    """
    Analyze parity oscillation.
    
    Returns:
        amplitude: Oscillation amplitude
        frequency: Oscillation frequency
        coherence: Coherence proxy
    """
    # Fit sinusoidal model
    # P(parity=1) = A * cos(ωθ + φ) + B
    
    from scipy.optimize import curve_fit
    
    def model(theta, A, omega, phi, B):
        return A * np.cos(omega * theta + phi) + B
    
    popt, _ = curve_fit(model, phases, parity_probs)
    amplitude, frequency, phase, offset = popt
    
    return {
        'amplitude': amplitude,
        'frequency': frequency,
        'phase': phase,
        'offset': offset,
        'coherence': amplitude / (1 - offset) if offset < 1 else 0
    }
```

---

## Family 5: Multi-Ancilla Witness (PW-5Q)

### Purpose
Multiple ancilla measurements for comprehensive correlation mapping.

### Structure
```
D0 ────■────■────
       │    │
D1 ────■────┼────
       │    │
A_Z ───X────┼──── H ──── M_Z (ZZ parity)
            │
A_X ────────X──── H ──── M_X (XX parity)
```

### Operations
1. Extract ZZ parity via A_Z
2. Extract XX parity via A_X
3. Compare both parity channels under interception

### Expected Behavior
- Different interception types may affect ZZ and XX differently
- Multi-channel detection provides richer signature
- Cross-correlation between channels as additional metric

---

## Circuit Selection Guide

| Use Case | Recommended Family | Rationale |
|----------|-------------------|-----------|
| Initial testing | PW-3Q | Minimal complexity, clear signal |
| Enhanced sensitivity | PW-3Q-E | Entangled data qubits |
| Asymmetric detection | PW-4Q | Bilateral comparison |
| Coherence detection | PW-3Q-C | Phase-sensitive |
| Comprehensive mapping | PW-5Q | Multi-channel |

## Implementation Priority

1. **PW-3Q**: Implement first, validate hypothesis
2. **PW-3Q-E**: If PW-3Q shows signal, test enhanced version
3. **PW-3Q-C**: If PW-3Q succeeds, test coherence sensitivity
4. **PW-4Q**: If PW-3Q succeeds, test mirrored topology
5. **PW-5Q**: If multi-channel needed for application