# Observer Symmetry Claim Boundaries

## What We Claim

### C1: Detectable Symmetry Breaking
**Claim**: Intermediate measurements on bilateral quantum circuits produce statistically distinguishable deviations in output distributions.

**Evidence Required**:
- KL divergence > 0.05 between intercepted and baseline distributions
- p < 0.01 for chi-square test comparing distributions
- Reproducible across ≥ 3 independent runs

**Scope**: Limited to the specific circuit families defined in CIRCUIT_FAMILIES.md. Does not generalize to arbitrary quantum circuits without additional validation.

### C2: Detection-Utility Trade-off
**Claim**: The magnitude of detectable deviation correlates with the information gained by an interceptor.

**Evidence Required**:
- Positive correlation (r > 0.5) between interceptor mutual information and detection score
- Statistical significance p < 0.05 for correlation test

**Scope**: Limited to single-interceptor scenarios. Does not address coordinated multi-party attacks.

### C3: Reproducibility
**Claim**: Results are reproducible across simulator backends and (if validated) hardware.

**Evidence Required**:
- Same circuit produces consistent results on Aer simulator with different seeds
- If hardware validated: results within 2σ of simulator predictions

**Scope**: Limited to IBM Quantum backends. Does not claim reproducibility on other hardware platforms without additional testing.

---

## What We Do NOT Claim

### NC1: Universal Tamper Detection
We do NOT claim that this approach detects all forms of quantum interception. Specific limitations:
- Does not detect coherent attacks that preserve quantum states
- Does not detect attacks that occur before entanglement creation
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
- Falsification criteria met (see HYPOTHESIS.md)
- Fundamental error in methodology discovered
- Results cannot be reproduced after reasonable attempts

---

## Current Claim Status

| Claim | Status | Evidence Level | Last Updated |
|-------|--------|----------------|--------------|
| C1 | Unvalidated | None | 2026-05-15 |
| C2 | Unvalidated | None | 2026-05-15 |
| C3 | Unvalidated | None | 2026-05-15 |

### Evidence Levels
- **None**: No experimental data collected
- **Preliminary**: Initial simulation results, not peer-reviewed
- **Validated**: Reproducible across multiple backends
- **Hardware-confirmed**: Validated on quantum hardware
- **External-replicated**: Independently replicated by external party

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
| 2026-05-15 | All | Initial definition | Research charter established |