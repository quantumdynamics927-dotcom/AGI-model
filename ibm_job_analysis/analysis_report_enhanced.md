# IBM Quantum Job Results Analysis
## Sierpinski TMT Phase 4S Optimized Circuit Results
### Enhanced Statistical Analysis with Rigorous Interpretation

---

## ⚠️ Important Scientific Caveats

The following analysis provides **shot-limited empirical statistics** from IBM Quantum job outputs. Key limitations:

1. **Entropy Interpretation**: Observed entropy values (~12.89-13.00 bits) are close to the **shot-limited maximum** of log₂(8192) ≈ 13 bits, NOT the Hilbert space maximum. This indicates broad sampling diversity, not necessarily maximum quantum coherence.

2. **Coherence Claims**: High state diversity does **not** by itself prove good coherence, high gate fidelity, or low decoherence. Coherence validation requires comparison against an ideal target distribution or simulator baseline.

3. **Noise Assessment**: Near-uniform output can arise from well-designed scrambling circuits OR from noise-heavy behavior. Without circuit-specific ideal baselines, we cannot distinguish these cases.

4. **Error Patterns**: Systematic errors often appear in **marginal distributions** and **pairwise correlations**, not necessarily as globally repeated full-register strings.

---

## Summary Statistics

| Job ID | Shots | Qubits | Unique States | Entropy (bits) | Shot-Limited Max | TV Distance |
|--------|-------|--------|---------------|----------------|------------------|-------------|
| d7l6i60e7usc73f5jm0g | 8192 | 127 | 8111 | 12.9790 | 13.0000 | 0.009800 |
| d7l6i8oe7usc73f5jm50 | 8192 | 127 | 8183 | 12.9978 | 13.0000 | 0.001097 |
| d7l6ib0kj84c73celivg | 8192 | 127 | 8173 | 12.9954 | 13.0000 | 0.002314 |
| d7l6ij0kj84c73celj9g | 8192 | 156 | 7797 | 12.8888 | 13.0000 | 0.046585 |
| d7l6il8e7usc73f5jmig | 8192 | 156 | 8144 | 12.9877 | 13.0000 | 0.005829 |
| d7l6inoe7usc73f5jmm0 | 8192 | 156 | 8075 | 12.9696 | 13.0000 | 0.014109 |

### Interpretation

- **Unique States**: Number of distinct bitstrings observed out of 8192 shots
- **Entropy**: Shannon entropy of the empirical distribution over observed states
- **Shot-Limited Max**: Maximum possible entropy given 8192 samples (log₂(8192) ≈ 13 bits)
- **TV Distance**: Total variation distance from uniform distribution over observed states

---

## Marginal Probability Analysis

Per-qubit marginal probabilities P(1) indicate potential readout bias or systematic errors.

### Job d7l6i60e7usc73f5jm0g (127 qubits)

- **Mean P(1)**: 0.0799 (ideal: 0.5)
- **Std Dev**: 0.0786
- **Max Deviation from 0.5**: 0.4979
- **Qubits with |P(1) - 0.5| > 0.1**: 127

**Top 10 Most Biased Qubits:**
```
  Qubit 88: P(1) = 0.0021, deviation = 0.4979
  Qubit 90: P(1) = 0.0033, deviation = 0.4967
  Qubit 107: P(1) = 0.0034, deviation = 0.4966
  Qubit 86: P(1) = 0.0035, deviation = 0.4965
  Qubit 17: P(1) = 0.0038, deviation = 0.4962
  Qubit 94: P(1) = 0.0039, deviation = 0.4961
  Qubit 84: P(1) = 0.0042, deviation = 0.4958
  Qubit 96: P(1) = 0.0048, deviation = 0.4952
  Qubit 111: P(1) = 0.0049, deviation = 0.4951
  Qubit 105: P(1) = 0.0049, deviation = 0.4951
```

### Job d7l6i8oe7usc73f5jm50 (127 qubits)

- **Mean P(1)**: 0.0775 (ideal: 0.5)
- **Std Dev**: 0.0719
- **Max Deviation from 0.5**: 0.4937
- **Qubits with |P(1) - 0.5| > 0.1**: 127

**Top 10 Most Biased Qubits:**
```
  Qubit 46: P(1) = 0.0063, deviation = 0.4937
  Qubit 114: P(1) = 0.0070, deviation = 0.4930
  Qubit 50: P(1) = 0.0074, deviation = 0.4926
  Qubit 37: P(1) = 0.0077, deviation = 0.4923
  Qubit 48: P(1) = 0.0078, deviation = 0.4922
  Qubit 118: P(1) = 0.0078, deviation = 0.4922
  Qubit 90: P(1) = 0.0084, deviation = 0.4916
  Qubit 41: P(1) = 0.0085, deviation = 0.4915
  Qubit 39: P(1) = 0.0090, deviation = 0.4910
  Qubit 52: P(1) = 0.0090, deviation = 0.4910
```

### Job d7l6ib0kj84c73celivg (127 qubits)

- **Mean P(1)**: 0.0771 (ideal: 0.5)
- **Std Dev**: 0.0733
- **Max Deviation from 0.5**: 0.4965
- **Qubits with |P(1) - 0.5| > 0.1**: 127

**Top 10 Most Biased Qubits:**
```
  Qubit 25: P(1) = 0.0035, deviation = 0.4965
  Qubit 23: P(1) = 0.0040, deviation = 0.4960
  Qubit 103: P(1) = 0.0043, deviation = 0.4957
  Qubit 29: P(1) = 0.0045, deviation = 0.4955
  Qubit 21: P(1) = 0.0049, deviation = 0.4951
  Qubit 27: P(1) = 0.0051, deviation = 0.4949
  Qubit 105: P(1) = 0.0052, deviation = 0.4948
  Qubit 19: P(1) = 0.0052, deviation = 0.4948
  Qubit 31: P(1) = 0.0052, deviation = 0.4948
  Qubit 17: P(1) = 0.0060, deviation = 0.4940
```

### Job d7l6ij0kj84c73celj9g (156 qubits)

- **Mean P(1)**: 0.0708 (ideal: 0.5)
- **Std Dev**: 0.1395
- **Max Deviation from 0.5**: 0.4998
- **Qubits with |P(1) - 0.5| > 0.1**: 149

**Top 10 Most Biased Qubits:**
```
  Qubit 133: P(1) = 0.0002, deviation = 0.4998
  Qubit 95: P(1) = 0.0002, deviation = 0.4998
  Qubit 9: P(1) = 0.0002, deviation = 0.4998
  Qubit 83: P(1) = 0.0004, deviation = 0.4996
  Qubit 116: P(1) = 0.0004, deviation = 0.4996
  Qubit 46: P(1) = 0.0004, deviation = 0.4996
  Qubit 55: P(1) = 0.0005, deviation = 0.4995
  Qubit 141: P(1) = 0.0005, deviation = 0.4995
  Qubit 108: P(1) = 0.0007, deviation = 0.4993
  Qubit 57: P(1) = 0.0007, deviation = 0.4993
```

### Job d7l6il8e7usc73f5jmig (156 qubits)

- **Mean P(1)**: 0.0676 (ideal: 0.5)
- **Std Dev**: 0.1120
- **Max Deviation from 0.5**: 0.4983
- **Qubits with |P(1) - 0.5| > 0.1**: 151

**Top 10 Most Biased Qubits:**
```
  Qubit 55: P(1) = 0.0017, deviation = 0.4983
  Qubit 63: P(1) = 0.0024, deviation = 0.4976
  Qubit 102: P(1) = 0.0026, deviation = 0.4974
  Qubit 51: P(1) = 0.0027, deviation = 0.4973
  Qubit 108: P(1) = 0.0028, deviation = 0.4972
  Qubit 12: P(1) = 0.0028, deviation = 0.4972
  Qubit 24: P(1) = 0.0028, deviation = 0.4972
  Qubit 98: P(1) = 0.0029, deviation = 0.4971
  Qubit 22: P(1) = 0.0033, deviation = 0.4967
  Qubit 94: P(1) = 0.0034, deviation = 0.4966
```

### Job d7l6inoe7usc73f5jmm0 (156 qubits)

- **Mean P(1)**: 0.0659 (ideal: 0.5)
- **Std Dev**: 0.1148
- **Max Deviation from 0.5**: 0.4993
- **Qubits with |P(1) - 0.5| > 0.1**: 151

**Top 10 Most Biased Qubits:**
```
  Qubit 141: P(1) = 0.0007, deviation = 0.4993
  Qubit 52: P(1) = 0.0010, deviation = 0.4990
  Qubit 97: P(1) = 0.0012, deviation = 0.4988
  Qubit 90: P(1) = 0.0012, deviation = 0.4988
  Qubit 119: P(1) = 0.0016, deviation = 0.4984
  Qubit 105: P(1) = 0.0017, deviation = 0.4983
  Qubit 27: P(1) = 0.0017, deviation = 0.4983
  Qubit 25: P(1) = 0.0017, deviation = 0.4983
  Qubit 83: P(1) = 0.0018, deviation = 0.4982
  Qubit 117: P(1) = 0.0018, deviation = 0.4982
```

---

## Hamming Weight Distribution

The Hamming weight (number of 1s in each bitstring) distribution provides insight into global state structure.

### Job d7l6i60e7usc73f5jm0g

- **Mean Hamming Weight**: 10.15 (ideal: 63.50)
- **Std Dev**: 2.70
- **Range**: [2, 21]
- **Median**: 10.00

### Job d7l6i8oe7usc73f5jm50

- **Mean Hamming Weight**: 9.84 (ideal: 63.50)
- **Std Dev**: 2.81
- **Range**: [1, 20]
- **Median**: 10.00

### Job d7l6ib0kj84c73celivg

- **Mean Hamming Weight**: 9.79 (ideal: 63.50)
- **Std Dev**: 2.74
- **Range**: [1, 20]
- **Median**: 10.00

### Job d7l6ij0kj84c73celj9g

- **Mean Hamming Weight**: 11.04 (ideal: 78.00)
- **Std Dev**: 3.34
- **Range**: [2, 24]
- **Median**: 11.00

### Job d7l6il8e7usc73f5jmig

- **Mean Hamming Weight**: 10.55 (ideal: 78.00)
- **Std Dev**: 3.41
- **Range**: [1, 22]
- **Median**: 10.00

### Job d7l6inoe7usc73f5jmm0

- **Mean Hamming Weight**: 10.28 (ideal: 78.00)
- **Std Dev**: 3.40
- **Range**: [0, 24]
- **Median**: 10.00

---

## Pairwise Correlation Analysis

Maximum absolute pairwise correlation indicates potential correlated errors or entanglement patterns.

- **Job d7l6i60e7usc73f5jm0g**: Max |correlation| = 0.6501
- **Job d7l6i8oe7usc73f5jm50**: Max |correlation| = 0.7292
- **Job d7l6ib0kj84c73celivg**: Max |correlation| = 0.7803
- **Job d7l6ij0kj84c73celj9g**: Max |correlation| = 0.6164
- **Job d7l6il8e7usc73f5jmig**: Max |correlation| = 0.3417
- **Job d7l6inoe7usc73f5jmm0**: Max |correlation| = 0.3515

---

## Comparison to Ideal Uniform Distribution

### Job d7l6i60e7usc73f5jm0g

- **Chi² Statistic**: 113.00
- **Total Variation Distance**: 0.009800
- **Unique States Observed**: 8111 / 8192 shots

### Job d7l6i8oe7usc73f5jm50

- **Chi² Statistic**: 9.00
- **Total Variation Distance**: 0.001097
- **Unique States Observed**: 8183 / 8192 shots

### Job d7l6ib0kj84c73celivg

- **Chi² Statistic**: 19.00
- **Total Variation Distance**: 0.002314
- **Unique States Observed**: 8173 / 8192 shots

### Job d7l6ij0kj84c73celj9g

- **Chi² Statistic**: 753.00
- **Total Variation Distance**: 0.046585
- **Unique States Observed**: 7797 / 8192 shots

### Job d7l6il8e7usc73f5jmig

- **Chi² Statistic**: 60.00
- **Total Variation Distance**: 0.005829
- **Unique States Observed**: 8144 / 8192 shots

### Job d7l6inoe7usc73f5jmm0

- **Chi² Statistic**: 157.00
- **Total Variation Distance**: 0.014109
- **Unique States Observed**: 8075 / 8192 shots

---

## Key Findings (Scientifically Conservative)

1. **High Sampled Diversity**: Across all six jobs, the measured bitstring histograms show very high outcome diversity with 8080 unique states on average out of 8192 shots.

2. **Shot-Limited Entropy**: The empirical state entropy averages 12.97 bits, which is close to the shot-limited maximum of ~13 bits. This indicates broadly distributed sampled outcomes, but does not characterize the full Hilbert space entropy.

3. **No Global Collapse**: The most frequent bitstrings occur only 2-6 times out of 8192 shots, indicating no obvious collapse into a small subset of repeated full-register outcomes at the histogram level.

4. **Marginal Analysis Needed**: Per-qubit marginal probabilities show deviations from 0.5, which may indicate readout bias or systematic errors. Detailed marginal analysis is required.

5. **Circuit-Specific Validation Required**: Claims about coherence, noise suppression, and circuit-specific correctness require comparison against an ideal target distribution and marginal/correlation analysis.

---

## Recommended Next Steps

1. **Simulator Baseline**: Run the same circuits on an ideal simulator to establish target distribution.
2. **Total Variation Distance**: Compute TV distance or Hellinger distance between hardware and simulator outputs.
3. **Correlated Error Analysis**: Investigate pairwise and higher-order correlations for systematic errors.
4. **Backend Comparison**: Compare results across different backends to identify hardware-specific effects.
5. **Timing Analysis**: Examine job metadata for queue time, execution time, and usage metrics.
