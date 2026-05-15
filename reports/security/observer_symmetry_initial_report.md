# Observer Symmetry Initial Report

**Status**: Hypothesis Not Supported  
**Date**: 2026-05-15  
**Researcher**: AGI-model Lab

## Objective

Test the hypothesis that bilateral quantum circuits exhibit detectable symmetry-breaking when subjected to unauthorized intermediate measurements.

## Methodology

### Circuit Family
- **OBS-3Q**: 3-qubit bilateral observer topology
- Left reservoir (Q0), Center observer (Q1), Right reservoir (Q2)

### Test Conditions
| Condition | Description |
|-----------|-------------|
| Baseline | No intermediate measurement |
| Left intercept | Measure Q0 before center measurement |
| Right intercept | Measure Q2 before center measurement |
| Bilateral intercept | Measure both Q0 and Q2 before center |

### Metrics
- Symmetry Score (S)
- KL Divergence from baseline (D_KL)
- Min-Entropy (H_min)
- Chi-square test p-value
- Detection Score (composite)

## Results

### Experiment Execution

```bash
cd D:\AGI-GH-REPO-11326\AGI-model
python experiments/observer_symmetry/run_3q_baseline.py --shots 8192 --seed 42
python experiments/observer_symmetry/analyze_symmetry_breaking.py --input experiments/observer_symmetry/results/baseline_3q_20260515_014900.json
```

### Key Findings

| Metric | Baseline | Left | Right | Bilateral |
|--------|----------|------|-------|-----------|
| Center marginal [0] | 0.495 | 0.498 | 0.498 | 0.498 |
| Center marginal [1] | 0.505 | 0.502 | 0.502 | 0.502 |
| KL Divergence | - | 0.0003 | 0.0003 | 0.0003 |
| Chi-square p-value | - | 0.98 | 0.98 | 0.98 |

### Critical Observation

**The center qubit marginal distribution is statistically indistinguishable across all conditions.**

- KL divergence ~0.0003 (essentially zero)
- Chi-square p-value ~0.98 (no significant difference)
- All center marginals are approximately uniform [0.5, 0.5]

This means **intermediate measurements on the reservoir qubits do NOT create detectable disturbance in the center observer qubit**.

### Why Detection Score Was High

The detection score (0.586) was driven by:
1. **Entropy difference**: Intercepted circuits measure 3 qubits vs 1 qubit baseline
2. **Not actual disturbance**: The center qubit distribution is unchanged

This is a **false positive** in the detection metric, not evidence of tamper detection.

## Hypothesis Status

**H1: NOT SUPPORTED**

The hypothesis stated:
> "An intermediate measurement on either reservoir qubit produces a statistically distinguishable deviation in the final measurement distribution compared to the undisturbed case."

**Falsification**: The center qubit marginal is statistically indistinguishable (p=0.98) between baseline and all interception modes.

## Root Cause Analysis

The OBS-3Q circuit structure:
```
Q0 --H--■--
        │
Q1 -----X--H--M
        │
Q2 --H--■--
```

After entanglement and Hadamard on Q1:
- Q1 is in a superposition that is **uncorrelated** with Q0 and Q2 individually
- Measuring Q0 or Q2 does NOT collapse Q1's state
- The bilateral entanglement creates a GHZ-like state where Q1 is maximally mixed

This is a **fundamental property** of the circuit topology, not a measurement error.

## Claim Status

| Claim | Status | Evidence |
|-------|--------|----------|
| C1: Detectable symmetry breaking | **FALSIFIED** | KL=0.0003, p=0.98 |
| C2: Detection-utility trade-off | **NOT TESTABLE** | No detection to measure |
| C3: Reproducibility | Validated | Consistent across modes |

## Lessons Learned

1. **Circuit topology matters**: Not all bilateral structures create observable disturbance
2. **Marginal analysis is critical**: Full distribution comparison can mask marginal invariance
3. **Detection metrics must be validated**: High scores can be false positives

## Next Steps

### Option A: Modify Circuit Topology
- Add phase gates to create interference-sensitive structure
- Use different entanglement pattern (e.g., CNOT chain vs star)
- Introduce conditional operations based on reservoir states

### Option B: Different Detection Strategy
- Monitor reservoir qubits directly (requires trusted measurement)
- Use entanglement witnesses instead of marginal distributions
- Implement decoy states for detection

### Option C: Pivot Research Direction
- Focus on entropy verification (QRNG mode)
- Investigate transport security instead
- Explore different security primitives

## References

- `research/quantum_security/observer_symmetry/HYPOTHESIS.md`
- `research/quantum_security/observer_symmetry/METRICS.md`
- `research/quantum_security/observer_symmetry/CIRCUIT_FAMILIES.md`
- `research/quantum_security/observer_symmetry/CLAIM_BOUNDARIES.md`
- `experiments/observer_symmetry/results/baseline_3q_20260515_014900.json`