# IBM Quantum Teleportation Hardware Validation - Scientific Summary

## What Was Measured

**Corrected computational-basis population fidelity** - NOT full quantum state fidelity.

### Key Distinction

| Metric | What It Measures | What It Misses |
|--------|------------------|-----------------|
| **This work** | Z-basis population agreement after classical corrections | Phase information (RZ(π/7) component) |
| **Full state fidelity** | Complete quantum state overlap (amplitude + phase) | Nothing |

### Why Phase Matters for This State

The target state is:
$$|\psi\rangle = RY(\pi/3) \cdot RZ(\pi/7) |0\rangle$$

- **RY(π/3)** creates amplitude structure: P(0) ≈ 0.75, P(1) ≈ 0.25
- **RZ(π/7)** creates phase structure: relative phase between |0⟩ and |1⟩

**Z-basis measurement alone cannot detect phase errors.** A state with correct populations but wrong phase would score identically high on our metric.

---

## Results Summary (Correctly Framed)

### What We Can Claim

**"Across 6 fresh IBM hardware runs on 3 backends (ibm_fez, ibm_kingston, ibm_marrakesh), the corrected output populations of the teleported qubit matched the target state's computational-basis statistics with Bhattacharyya overlap scores of 0.980–0.990."**

### Detailed Results

| Backend | Job ID | Shots | Z-Basis Overlap | Bell Distribution |
|---------|--------|-------|-----------------|-------------------|
| ibm_fez | d7l8r1i8ui0s73b648q0 | 1024 | 0.9900 | 00:29%, 01:23%, 10:22%, 11:26% |
| ibm_fez | d7l8qri4lglc7380atr0 | 4096 | 0.9820 | 00:27%, 01:22%, 10:23%, 11:28% |
| ibm_kingston | d7l8r028ui0s73b648ng | 1024 | 0.9876 | 00:29%, 01:23%, 10:23%, 11:26% |
| ibm_kingston | d7l8qp24lglc7380atlg | 4096 | 0.9841 | 00:29%, 01:22%, 10:23%, 11:27% |
| ibm_marrakesh | d7l8qtokj84c73ceo7tg | 4096 | 0.9847 | 00:28%, 01:23%, 10:22%, 11:27% |
| ibm_marrakesh | d7l8r38kj84c73ceo860 | 1024 | 0.9802 | 00:29%, 01:21%, 10:23%, 11:27% |

### Statistics

- **Mean Z-Basis Overlap**: 0.9848 ± 0.0033
- **Best Result**: 0.9900 (ibm_fez, 1024 shots)
- **Reproducibility**: 6/6 runs show strong agreement
- **Cross-Backend Consistency**: Narrow range (0.980–0.990) across 3 processors

---

## What This Validates

### ✅ Confirmed

1. **Bell measurement works**: Bell outcomes are approximately uniform (~25% each), consistent with proper Bell-state preparation and measurement
2. **Classical correction logic is sound**: Applying X corrections based on Alice's bits produces expected populations
3. **Population transfer is reproducible**: Z-basis statistics match target across backends and shot counts
4. **Hardware execution is stable**: Results consistent between 1024-shot and 4096-shot runs

### ❌ Not Yet Validated

1. **Phase preservation**: Z-basis measurement cannot verify RZ(π/7) phase was teleported correctly
2. **Full state fidelity**: Would require multi-basis measurements or state tomography
3. **Arbitrary state teleportation**: Single test state is not sufficient to claim general teleportation capability

---

## Methodology Details

### Classical Corrections Applied

For each shot:
1. Extract Alice's Bell measurement: bits c[0] and c[1]
2. Extract Bob's raw measurement: bit c[2]
3. Apply correction:
   - If c[1] = 1: Flip Bob's bit (X correction)
   - If c[0] = 1: Phase correction (Z) - invisible in Z-basis measurement

### Fidelity Metric

$$F_{Z} = \sqrt{P_{\text{target}}(0) \cdot P_{\text{corrected}}(0)} + \sqrt{P_{\text{target}}(1) \cdot P_{\text{corrected}}(1)}$$

This is the **Bhattacharyya coefficient** between target and measured Z-basis distributions.

**Important**: This is NOT the same as quantum state fidelity:
$$F_{\text{quantum}} = \langle\psi_{\text{target}}|\rho_{\text{out}}|\psi_{\text{target}}\rangle$$

---

## Recommended Next Steps for Full Validation

### Option 1: Multi-Basis Measurement

Run the same circuit but measure Bob's qubit in X, Y, and Z bases:

```python
# X-basis measurement (H before measure)
circuit.h(bob_qubit)
circuit.measure(bob_qubit, c[2])

# Y-basis measurement (S† H before measure)  
circuit.sdg(bob_qubit)
circuit.h(bob_qubit)
circuit.measure(bob_qubit, c[2])
```

### Option 2: State Tomography

Use Qiskit's state tomography to reconstruct the output density matrix:

```python
from qiskit_experiments.library import StateTomography
from qiskit.quantum_info import DensityMatrix, state_fidelity

# Reconstruct density matrix
tomography = StateTomography(circuit)
result = tomography.run(backend)
rho_out = result.analysis_results("state")

# Compute true state fidelity
target_state = ...  # RY(pi/3) @ RZ(pi/7) @ |0⟩
fidelity = state_fidelity(target_state, rho_out)
```

### Option 3: Process Fidelity

Test teleportation over multiple input states to compute process fidelity:

```python
# Test states: |0⟩, |1⟩, |+⟩, |-⟩, |+i⟩, |-i⟩
# Compute average fidelity over all inputs
```

---

## Conservative Scientific Statement

**For immediate communication:**

> "We performed hardware validation of quantum teleportation on three IBM Quantum backends (ibm_fez, ibm_kingston, ibm_marrakesh) with 6 total runs. After applying classical corrections conditioned on Bell measurement outcomes, the corrected computational-basis populations of the teleported qubit showed strong agreement with the target state RY(π/3)·RZ(π/7)|0⟩, with Bhattacharyya overlap scores of 0.980–0.990 (mean: 0.9848 ± 0.0033). Bell measurement outcomes were approximately uniformly distributed, consistent with proper protocol execution. Full quantum state fidelity validation would require additional basis measurements to verify phase preservation."

---

## Files Generated

| File | Description |
|------|-------------|
| `corrected_hardware_validation_report.md` | Full report with methodology |
| `corrected_hardware_validation_results.json` | Raw data |
| `SCIENTIFIC_SUMMARY.md` | This document |

---

## References

1. **Teleportation Protocol**: Bennett et al., "Teleporting an unknown quantum state via dual classical and Einstein-Podolsky-Rosen channels" (1993)
2. **Fidelity Definitions**: Nielsen & Chuang, "Quantum Computation and Quantum Information"
3. **State Tomography**: Qiskit Textbook, "Quantum State Tomography"
4. **Process Fidelity**: Bowden & Jones, "Process fidelity of quantum operations"