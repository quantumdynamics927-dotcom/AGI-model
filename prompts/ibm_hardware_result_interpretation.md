---
name: ibm_hardware_result_interpretation
version: 1.0.0
owner: Quantum Dynamics
purpose: Hardware-provenance-first analysis of IBM Quantum job results.
inputs:
  - IBM job results
  - raw counts
  - calibration data
expected_output:
  - what is strongly supported
  - what is weakly supported
  - what is overstated
  - missing metadata
  - next repeat run
risk_level: high
last_validated_on: 2026-04-20
---

# IBM Hardware Result Interpretation

```text
Interpret these IBM Quantum job results as an internal hardware analysis.

For each reported metric, determine:
- Was it computed directly from raw counts, quasi-probabilities, or post-processed features?
- What calibration or mitigation assumptions were applied?
- What is the likely shot-noise floor at the reported number of shots?
- Could the effect be explained by readout bias, backend drift, or transpilation artifacts?

Classify each result as:
- directly measured
- calibration-dependent
- mitigation-dependent
- post-processing artifact
- potentially meaningful signal

Then return:
1. What is strongly supported
2. What is weakly supported
3. What is overstated
4. What metadata is missing
5. What repeat run should be done next
```

## Usage

Use for all `analyze_ibm_*.py` outputs, backend comparison results, and hardware-limited claims. Prefer reasoning from hardware provenance outward, not interpretation inward.
