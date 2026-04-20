---
name: interpret_results_conservatively
version: 1.0.0
owner: Quantum Dynamics
purpose: Conservative classification of metrics before claiming significance.
inputs:
  - JSON results
  - tables
  - logs
expected_output:
  - what is actually supported
  - what is only suggested
  - what should not be claimed
  - next validating experiment
risk_level: high
last_validated_on: 2026-04-20
---

# Interpret Results Conservatively

```text
Interpret these results conservatively.

For each metric, classify it as:
- directly measured
- derived but well-defined
- custom heuristic
- currently unreliable

Then answer:
1. What is actually supported?
2. What is only suggested?
3. What should not be claimed?
4. What is the next validating experiment?

Input:
[PASTE JSON / TABLE / LOGS]
```

## Usage

Use for all golden ratio proximity metrics, coherence calculations, and consciousness-related outputs before logging as indicators.
