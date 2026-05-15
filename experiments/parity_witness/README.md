# Parity Witness Experiments

## Purpose

Investigate parity-based tamper detection using ancilla qubits that extract correlation information from data qubits.

## Hypothesis

Intermediate measurements on data qubits produce detectable deviations in parity ancilla distributions, providing a foundation for correlation-based tamper detection.

## Background

This investigation follows the OBS-3Q observer symmetry experiment (falsified 2026-05-15), which demonstrated that single-qubit marginals are insufficient for detecting interception in GHZ-like states. Parity witnesses target multi-qubit correlations instead.

## Directory Structure

```
parity_witness/
├── README.md           # This document
├── results/            # Experiment outputs
├── circuits/           # Circuit definitions
├── run_pw_baseline.py  # Baseline experiment runner
└── analyze_pw_results.py # Statistical analysis
```

## Circuit Families

| Family | Description | Status |
|--------|-------------|--------|
| PW-3Q | Basic parity witness | Ready for testing |
| PW-3Q-E | Entangled data qubits | Ready for testing |
| PW-3Q-C | Coherence-sensitive | Ready for testing |
| PW-4Q | Mirrored bilateral | Ready for testing |

## Running Experiments

```bash
# Basic variant
python run_pw_baseline.py --shots 8192 --seed 42 --variant basic

# Entangled variant
python run_pw_baseline.py --shots 8192 --seed 42 --variant entangled

# Analyze results
python analyze_pw_results.py --input results/pw_baseline_basic_*.json
```

## Metrics

| Metric | Target | Description |
|--------|--------|-------------|
| Parity KL | > 0.05 | KL divergence from baseline |
| Joint KL | > 0.05 | Joint marginal deviation |
| Correlation Drift | > 0.1 bits | Mutual information change |
| Witness Score | > 0.1 | Composite detection metric |

## Status

| Experiment | Status | Last Run |
|------------|--------|----------|
| PW-3Q Basic | Not started | - |
| PW-3Q Entangled | Not started | - |
| PW-3Q Coherence | Not started | - |
| PW-4Q Mirrored | Not started | - |

## Maturity

Current state: **Exploratory**

Next milestone: Validated Research Artifact (requires reproducibility across backends)

## References

- `research/quantum_security/parity_witness_tamper/HYPOTHESIS.md`
- `research/quantum_security/parity_witness_tamper/METRICS.md`
- `research/quantum_security/parity_witness_tamper/CIRCUIT_FAMILIES.md`
- `research/quantum_security/parity_witness_tamper/CLAIM_BOUNDARIES.md`
- OBS-3Q Investigation: `../observer_symmetry/`