---
name: benchmark_validity
version: 1.0.0
owner: Quantum Dynamics
purpose: Validate whether a benchmark result is comparable and trustworthy.
inputs:
  - benchmark logs
  - result JSON
  - benchmark description
expected_output:
  - validity decision
  - failure reasons
  - required fixes
  - acceptance criteria
risk_level: medium
last_validated_on: 2026-04-20
---

# Benchmark Validity

```text
You are evaluating a benchmark framework for a hybrid QAGI system.

Goal:
Determine whether the benchmark is valid.

Check:
- do all modes run on the same task set?
- do all modes use the same input/output contract?
- are failed samples counted explicitly?
- are baselines functioning?
- is any reported advantage invalidated by mode failures?

Output:
1. Valid or invalid
2. Exact reason
3. Missing benchmark fields
4. Required fixes
5. Minimum acceptance criteria
```

## Usage

Use to validate `benchmark_metatron_vs_eggn.py` and other comparative evaluations before trusting results.
