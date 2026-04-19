# Phase 3 Optimization Report

**Generated:** 2026-04-19T17:38:26  
**Baseline:** baseline_20260418_232605  
**Candidates Tested:** 4

## Summary

| Candidate | Primary Superiority | Non-inferiority | Decision |
|-----------|-------------------|-----------------|----------|
| tess_001 | 9 metrics | ✓ | reject |
| tess_002 | 10 metrics | ✗ | reject |
| tess_003 | 10 metrics | ✗ | reject |
| tess_004 | 10 metrics | ✗ | reject |

## Detailed Results

### tess_001: REJECT
**Reasoning:** Non-inferiority violated on 3 metrics

| Condition | Metric | Baseline | Candidate | Diff | p-value | Cohen's d |
|-----------|--------|----------|-----------|------|---------|-----------|
| clean | latency | 0.497 | 0.496 | -0.001 | 0.872 | -0.012 |
| clean | route_length | 10.025 | 10.151 | +0.125 | 0.416 | +0.089 |
| clean | success_rate | 0.899 | 0.932 | +0.034 | 0.000 | +0.361 |
| clean | invalid_transition_rate | 0.010 | 0.010 | +0.000 | 0.868 | +0.002 |
| clean | confidence_calibration | 0.805 | 0.825 | +0.020 | 0.031 | +0.183 |
| clean | seed | 208.000 | 210.600 | +2.600 | 0.728 | +0.038 |
| fault | latency | 0.641 | 0.607 | -0.034 | 0.001 | -0.294 |
| fault | route_length | 11.984 | 11.527 | -0.457 | 0.012 | -0.277 |
| fault | success_rate | 0.812 | 0.801 | -0.012 | 0.043 | -0.133 |
| fault | invalid_transition_rate | 0.050 | 0.048 | -0.002 | 0.606 | -0.024 |
| fault | confidence_calibration | 0.675 | 0.657 | -0.018 | 0.034 | -0.171 |
| fault | seed | 10208.000 | 9818.820 | -389.180 | 0.000 | -5.717 |
| stress | latency | 0.763 | 0.685 | -0.078 | 0.000 | -0.593 |
| stress | route_length | 14.364 | 13.089 | -1.275 | 0.000 | -0.665 |
| stress | success_rate | 0.715 | 0.667 | -0.047 | 0.000 | -0.538 |
| stress | invalid_transition_rate | 0.083 | 0.075 | -0.007 | 0.292 | -0.077 |
| stress | confidence_calibration | 0.600 | 0.553 | -0.046 | 0.000 | -0.490 |
| stress | seed | 20208.000 | 18414.540 | -1793.460 | 0.000 | -26.345 |

### tess_002: REJECT
**Reasoning:** Critical violations: 1 - success_rate(stress): -0.067 < -0.05

| Condition | Metric | Baseline | Candidate | Diff | p-value | Cohen's d |
|-----------|--------|----------|-----------|------|---------|-----------|
| clean | latency | 0.497 | 0.497 | -0.000 | 0.974 | -0.002 |
| clean | route_length | 10.025 | 10.050 | +0.025 | 0.871 | +0.018 |
| clean | success_rate | 0.899 | 0.905 | +0.007 | 0.314 | +0.072 |
| clean | invalid_transition_rate | 0.010 | 0.010 | +0.000 | 0.973 | +0.000 |
| clean | confidence_calibration | 0.805 | 0.809 | +0.004 | 0.664 | +0.037 |
| clean | seed | 208.000 | 208.520 | +0.520 | 0.944 | +0.008 |
| fault | latency | 0.641 | 0.608 | -0.032 | 0.001 | -0.283 |
| fault | route_length | 11.984 | 11.413 | -0.571 | 0.002 | -0.347 |
| fault | success_rate | 0.812 | 0.777 | -0.035 | 0.000 | -0.395 |
| fault | invalid_transition_rate | 0.050 | 0.048 | -0.002 | 0.519 | -0.031 |
| fault | confidence_calibration | 0.675 | 0.644 | -0.031 | 0.000 | -0.295 |
| fault | seed | 10208.000 | 9721.844 | -486.156 | 0.000 | -7.141 |
| stress | latency | 0.763 | 0.686 | -0.077 | 0.000 | -0.583 |
| stress | route_length | 14.364 | 12.960 | -1.404 | 0.000 | -0.733 |
| stress | success_rate | 0.715 | 0.648 | -0.067 | 0.000 | -0.758 |
| stress | invalid_transition_rate | 0.083 | 0.074 | -0.008 | 0.246 | -0.085 |
| stress | confidence_calibration | 0.600 | 0.542 | -0.057 | 0.000 | -0.603 |
| stress | seed | 20208.000 | 18232.668 | -1975.332 | 0.000 | -29.017 |

### tess_003: REJECT
**Reasoning:** Critical violations: 1 - success_rate(stress): -0.077 < -0.05

| Condition | Metric | Baseline | Candidate | Diff | p-value | Cohen's d |
|-----------|--------|----------|-----------|------|---------|-----------|
| clean | latency | 0.497 | 0.497 | -0.000 | 0.969 | -0.003 |
| clean | route_length | 10.025 | 9.995 | -0.030 | 0.845 | -0.021 |
| clean | success_rate | 0.899 | 0.891 | -0.008 | 0.227 | -0.087 |
| clean | invalid_transition_rate | 0.010 | 0.010 | -0.000 | 0.968 | -0.000 |
| clean | confidence_calibration | 0.805 | 0.800 | -0.005 | 0.603 | -0.044 |
| clean | seed | 208.000 | 207.376 | -0.624 | 0.933 | -0.009 |
| fault | latency | 0.641 | 0.608 | -0.032 | 0.001 | -0.284 |
| fault | route_length | 11.984 | 11.351 | -0.633 | 0.001 | -0.385 |
| fault | success_rate | 0.812 | 0.765 | -0.048 | 0.000 | -0.540 |
| fault | invalid_transition_rate | 0.050 | 0.048 | -0.003 | 0.474 | -0.034 |
| fault | confidence_calibration | 0.675 | 0.637 | -0.038 | 0.000 | -0.363 |
| fault | seed | 10208.000 | 9668.507 | -539.493 | 0.000 | -7.925 |
| stress | latency | 0.763 | 0.686 | -0.077 | 0.000 | -0.583 |
| stress | route_length | 14.364 | 12.889 | -1.475 | 0.000 | -0.770 |
| stress | success_rate | 0.715 | 0.638 | -0.077 | 0.000 | -0.879 |
| stress | invalid_transition_rate | 0.083 | 0.074 | -0.008 | 0.223 | -0.089 |
| stress | confidence_calibration | 0.600 | 0.537 | -0.063 | 0.000 | -0.666 |
| stress | seed | 20208.000 | 18132.638 | -2075.362 | 0.000 | -30.486 |

### tess_004: REJECT
**Reasoning:** Critical violations: 1 - success_rate(stress): -0.061 < -0.05

| Condition | Metric | Baseline | Candidate | Diff | p-value | Cohen's d |
|-----------|--------|----------|-----------|------|---------|-----------|
| clean | latency | 0.497 | 0.497 | -0.001 | 0.944 | -0.005 |
| clean | route_length | 10.025 | 10.080 | +0.055 | 0.720 | +0.039 |
| clean | success_rate | 0.899 | 0.913 | +0.015 | 0.027 | +0.159 |
| clean | invalid_transition_rate | 0.010 | 0.010 | +0.000 | 0.942 | +0.001 |
| clean | confidence_calibration | 0.805 | 0.814 | +0.009 | 0.340 | +0.080 |
| clean | seed | 208.000 | 209.144 | +1.144 | 0.878 | +0.017 |
| fault | latency | 0.641 | 0.608 | -0.033 | 0.001 | -0.286 |
| fault | route_length | 11.984 | 11.447 | -0.537 | 0.003 | -0.326 |
| fault | success_rate | 0.812 | 0.784 | -0.028 | 0.000 | -0.317 |
| fault | invalid_transition_rate | 0.050 | 0.048 | -0.002 | 0.544 | -0.029 |
| fault | confidence_calibration | 0.675 | 0.648 | -0.027 | 0.001 | -0.257 |
| fault | seed | 10208.000 | 9750.937 | -457.063 | 0.000 | -6.714 |
| stress | latency | 0.763 | 0.686 | -0.077 | 0.000 | -0.586 |
| stress | route_length | 14.364 | 12.998 | -1.365 | 0.000 | -0.713 |
| stress | success_rate | 0.715 | 0.654 | -0.061 | 0.000 | -0.692 |
| stress | invalid_transition_rate | 0.083 | 0.075 | -0.008 | 0.259 | -0.083 |
| stress | confidence_calibration | 0.600 | 0.546 | -0.054 | 0.000 | -0.569 |
| stress | seed | 20208.000 | 18287.230 | -1920.770 | 0.000 | -28.215 |


## Recommendations

1. **Promoted Candidates:** Implement and integrate into main routing
2. **Rejected Candidates:** Analyze failure modes for future iterations  
3. **Iterate Candidates:** Refine parameters and re-test

## Next Steps

- If any tesseract candidates promoted, proceed to Phase 3B (biomimetic addition)
- If no tesseract candidates promoted, consider:
  - Additional parameter tuning
  - Alternative routing topologies  
  - Shift focus to biomimetic adaptation
  - Memory-policy improvements

---

*Generated by Phase 3 Optimization Campaign*  
*QAGI Precursor Stack - Scientific Governance*
