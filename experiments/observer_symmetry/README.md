# Observer Symmetry Experiments

## Purpose

Investigate quantum circuit topologies with bilateral measurement structures that exhibit security-relevant properties through observer symmetry.

## Hypothesis

Circuits with symmetric measurement structures across complementary bases produce measurable security properties:
- **Tamper sensitivity**: Measurement disturbance creates detectable deviations
- **Entropy signatures**: Bilateral structures produce verifiable randomness patterns
- **Correlation bounds**: Symmetric constraints create testable Bell-type inequalities

## Experiment Categories

### 1. Bilateral Bell Tests
- CHSH inequality tests with symmetric measurement bases
- Device-independent security bounds

### 2. Entropy Verification
- QRNG circuits with bilateral verification
- Min-entropy estimation under symmetry constraints

### 3. Transport Authentication
- Teleportation-based channel verification
- State transfer fidelity bounds

## Directory Structure

```
observer_symmetry/
├── README.md           # This document
├── results/            # Experiment outputs
│   ├── simulations/    # Simulator results
│   └── hardware/       # Hardware results
├── notebooks/          # Analysis notebooks
└── circuits/           # Circuit definitions
```

## Running Experiments

```python
# Example: Bilateral Bell test
from experiments.observer_symmetry import BilateralBellTest

experiment = BilateralBellTest(
    n_qubits=2,
    n_shots=8192,
    backend="aer_simulator"
)
results = experiment.run()
```

## Status

| Experiment | Status | Last Run |
|------------|--------|----------|
| Bilateral Bell | Not started | - |
| Entropy verification | Not started | - |
| Transport auth | Not started | - |

## Maturity

Current state: **Exploratory**

Next milestone: Validated Research Artifact (requires reproducibility across backends)