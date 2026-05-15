# Parity Witness Tamper Detection Hypothesis

## Background

The OBS-3Q observer symmetry investigation (2026-05-15) demonstrated that single-qubit marginal distributions are insufficient for detecting intermediate measurements in GHZ-like entangled states. The center qubit marginal remained statistically indistinguishable (KL ~0.0003, p=0.98) across all interception conditions.

**Key Insight**: In GHZ-like states, local marginals can remain unchanged while joint correlations carry the entanglement information. Detection must target multi-qubit structure, not single-qubit marginals.

## Core Hypothesis

**H1**: In a parity-witness circuit, an ancilla qubit measuring ZZ or XX parity across data qubits will exhibit detectable deviation when an unauthorized intermediate measurement occurs on the data qubits.

**H2**: The magnitude of witness deviation correlates with the information gained by the interceptor, creating a measurable detection-utility trade-off.

**H3**: Parity oscillation methods (phase-sensitive parity extraction) provide enhanced detection sensitivity compared to static parity measurements.

## Formal Statement

For a 3-qubit parity-witness circuit with data qubits (D0, D1) and ancilla (A):

```
P_baseline = P(A | D0 ⊕ D1)     # Authorized parity readout
P_intercept = P(A | D0 ⊕ D1)    # After unauthorized measurement on D0 or D1
```

**Claim**: |P_baseline - P_intercept| > ε where ε exceeds shot noise and simulator variance.

## Topology Definition

### Basic Parity Witness (PW-3Q)

```
D0 ────■────
       │
D1 ────■────
       │
A  ────X──── H ──── M (parity readout)
```

Ancilla A extracts parity of D0 and D1 via CNOT cascade, then Hadamard for measurement.

### Expected Behavior

| Condition | Parity Distribution | Detection Signal |
|-----------|---------------------|------------------|
| Baseline | Balanced parity (0/1) | Reference |
| Intercept D0 | Parity bias | Correlation disturbance |
| Intercept D1 | Parity bias | Correlation disturbance |
| Intercept both | Maximum disturbance | Strongest signal |

## Falsification Criteria

This hypothesis is falsified if:

1. **No witness deviation**: Parity ancilla distribution remains statistically indistinguishable (p > 0.05) across all interception conditions

2. **Noise-dominated**: Witness deviation is within shot noise bounds for all practical shot counts (up to 32768)

3. **No correlation**: Witness deviation magnitude is uncorrelated with interceptor information gain

## Test Protocol

### Experiment A: Basic Parity Witness

1. Prepare D0, D1 in entangled state (Bell pair or GHZ-like)
2. Extract parity via ancilla A
3. Compare baseline vs. interception on D0, D1, or both
4. Measure: parity distribution, KL divergence, correlation drift

### Experiment B: Mirrored Parity Witness (PW-4Q)

1. Two data pairs: (D0, D1) left, (D2, D3) right
2. Two ancillas: A_L for left pair, A_R for right pair
3. Compare bilateral symmetry under asymmetric interception
4. Measure: cross-parity correlation, symmetry score

### Experiment C: Coherence-Sensitive Parity

1. Insert phase rotation Rz(θ) before parity extraction
2. Measure parity oscillation as function of θ
3. Compare oscillation amplitude/frequency under interception
4. Measure: coherence proxy, oscillation degradation

## Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| Parity KL Divergence | KL(P_parity_intercept || P_parity_baseline) | > 0.05 |
| Correlation Drift | Δ I(D0:D1) | > 0.1 bits |
| Witness Score | Composite detection metric | > 0.1 threshold |
| Parity Oscillation Amplitude | Coherence proxy | Detectable change |
| Chi-square p-value | Statistical significance | < 0.01 |

## Success Criteria

- [ ] Detectable parity deviation in at least one interception scenario (p < 0.01)
- [ ] Detection rate > 80% for single-qubit interception
- [ ] Positive correlation between interceptor utility and witness deviation
- [ ] Reproducible across multiple simulator seeds
- [ ] Validated on noise-aware simulator

## Failure Criteria

- [ ] No statistically significant deviation in any scenario
- [ ] Detection rate < 50% for all scenarios
- [ ] No correlation between utility and detection
- [ ] Non-reproducible results

## Relationship to OBS-3Q

| Aspect | OBS-3Q (Falsified) | PW-3Q (This Investigation) |
|--------|-------------------|---------------------------|
| Detection target | Single-qubit marginal | Multi-qubit correlation |
| Observer type | Center qubit | Parity ancilla |
| Information carrier | Local state | Joint parity |
| Expected signal | Marginal shift | Correlation disturbance |

## Timeline

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Circuit design | 1 day | `parity_witness_3q.py` |
| Simulation | 2 days | Baseline and interception results |
| Analysis | 1 day | Statistical report |
| Noise-aware validation | 2 days | AerSimulator with noise model |
| Hardware validation | 3 days | IBM Quantum results (if simulation succeeds) |

## References

- OBS-3Q Investigation: `research/quantum_security/observer_symmetry/`
- GHZ State Properties: arXiv:2604.27824v1
- Parity Measurement Methods: thp.uni-koeln.de/trebst/Lectures/QuantCompPhys-2024
- Entanglement Witnesses: PMC7083610