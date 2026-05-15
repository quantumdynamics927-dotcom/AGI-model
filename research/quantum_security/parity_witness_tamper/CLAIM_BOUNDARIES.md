# Parity Witness Claim Boundaries

## What We Claim

### C1: Parity Distribution Disturbance
**Claim**: Intermediate measurements on data qubits produce statistically distinguishable deviations in parity ancilla distributions.

**Evidence Required**:
- KL divergence > 0.05 between intercepted and baseline parity distributions
- p < 0.01 for chi-square test comparing distributions
- Reproducible across ≥ 3 independent runs

**Scope**: Limited to the specific circuit families defined in CIRCUIT_FAMILIES.md. Does not generalize to arbitrary quantum circuits without additional validation.

### C2: Correlation-Based Detection
**Claim**: Joint correlation metrics (mutual information, joint marginals) provide stronger detection signals than single-qubit marginals.

**Evidence Required**:
- Joint marginal KL divergence > single-qubit marginal KL divergence
- Correlation drift > 0.1 bits under interception
- Statistical significance p < 0.01

**Scope**: Based on OBS-3Q falsification showing single-qubit marginals are insufficient for GHZ-like states.

### C3: Detection-Utility Trade-off
**Claim**: The magnitude of witness deviation correlates with the information gained by an interceptor.

**Evidence Required**:
- Positive correlation (r > 0.5) between interceptor mutual information and witness score
- Statistical significance p < 0.05 for correlation test

**Scope**: Limited to single-interceptor scenarios. Does not address coordinated multi-party attacks.

### C4: Coherence Sensitivity (Conditional)
**Claim**: Phase-sensitive parity extraction provides enhanced detection capability compared to static parity measurement.

**Evidence Required**:
- Oscillation amplitude reduction > 20% under interception
- Detection rate improvement over static parity

**Scope**: Only claimed if PW-3Q-C experiments succeed.

---

## What We Do NOT Claim

### NC1: Universal Tamper Detection
We do NOT claim that this approach detects all forms of quantum interception. Specific limitations:
- Does not detect coherent attacks that preserve quantum states
- Does not detect attacks that occur before parity extraction
- Does not claim detection of classical side-channel attacks

### NC2: Information-Theoretic Security
We do NOT claim information-theoretic security guarantees. This is:
- A detection mechanism, not a prevention mechanism
- Subject to false positive and false negative rates
- Dependent on statistical thresholds that may not suit all applications

### NC3: Hardware-Independent Results
We do NOT claim that results on one hardware platform generalize to others. Specific exclusions:
- Ion trap systems (different noise model)
- Photonic systems (different measurement paradigm)
- Superconducting systems from other vendors (different calibration)

### NC4: Real-Time Detection
We do NOT claim real-time tamper detection capability. Current limitations:
- Requires statistical analysis over multiple shots
- Detection latency depends on shot count and backend
- Not suitable for single-shot security decisions

### NC5: Cryptographic Security
We do NOT claim that this provides cryptographic security on its own. This is:
- A primitive that may contribute to security protocols
- Not a replacement for established cryptographic methods
- Not validated against adversarial cryptanalysis

---

## Claim Evolution Protocol

Claims may be strengthened, weakened, or retracted based on evidence:

### Strengthening Criteria
A claim may be strengthened (scope expanded) when:
- Evidence exceeds original requirements by > 2x
- Independent replication by external party
- Hardware validation confirms simulator predictions

### Weakening Criteria
A claim must be weakened (scope narrowed) when:
- Evidence meets minimum but not target thresholds
- Reproducibility issues discovered
- Hardware results diverge significantly from simulation

### Retraction Criteria
A claim must be retracted when:
- Falsification criteria met
- Fundamental error in methodology discovered
- Results cannot be reproduced after reasonable attempts

---

## Current Claim Status

| Claim | Status | Evidence Level | Last Updated |
|-------|--------|----------------|--------------|
| C1 | **SUPPORTED** | Preliminary | 2026-05-15 |
| C2 | **SUPPORTED** | Preliminary | 2026-05-15 |
| C3 | **SUPPORTED** | Preliminary | 2026-05-15 |
| C4 | Unvalidated | None | 2026-05-15 |

### Evidence Levels
- **None**: No experimental data collected
- **Preliminary**: Initial simulation results, not peer-reviewed
- **Validated**: Reproducible across multiple backends
- **Hardware-confirmed**: Validated on quantum hardware
- **External-replicated**: Independently replicated by external party
- **Falsified**: Hypothesis contradicted by experimental evidence

### Key Evidence (2026-05-15)

**PW-3Q-E Entangled Parity Witness**:
- Baseline: Parity distribution [1.0, 0.0] (deterministic)
- Intercepted: Parity distribution [0.5, 0.5] (random)
- KL Divergence: 10.85 (massive signal)
- Chi-square p-value: 0.0000 (highly significant)
- Detection rate: 100%

---

## Relationship to OBS-3Q

| Aspect | OBS-3Q (Falsified) | PW-3Q (This Investigation) |
|--------|-------------------|---------------------------|
| Detection target | Single-qubit marginal | Multi-qubit correlation |
| Observer type | Center qubit | Parity ancilla |
| Information carrier | Local state | Joint parity |
| Expected signal | Marginal shift | Correlation disturbance |
| Claim C1 | FALSIFIED | Unvalidated |
| Claim C2 | N/A | Unvalidated |

---

## Promotion Requirements

For any claim to be promoted to QSG:

1. **Evidence Level**: Must reach at least "Hardware-confirmed"
2. **Scope Clarity**: Claim boundaries must be explicitly documented
3. **Limitations**: All NC (non-claim) items must be addressed
4. **Use Case**: Clear application within QSG architecture
5. **Review**: Independent review by at least one other researcher

---

## Revision History

| Date | Claim | Change | Rationale |
|------|-------|--------|-----------|
| 2026-05-15 | All | Initial definition | Investigation 2 started |