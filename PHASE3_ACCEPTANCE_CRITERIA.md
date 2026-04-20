# Phase 3 Acceptance Criteria

**Date:** April 19, 2026  
**Version:** 1.0.0

This document defines the acceptance criteria for promoting tesseract/biomimetic optimizations in Phase 3 of the QAGI precursor stack development.

## Promotion Rule

Each candidate optimization must pass a three-part gate against the locked baseline (`baseline_20260418_232605`):

1. **Superiority** on at least one primary metric
2. **Non-inferiority** on latency and robustness
3. **Meaningful effect size** with confidence intervals

Statistical significance (p < 0.05) alone is insufficient for promotion.

## Primary Metrics for Promotion

### Success Rate
- **Target:** Increase by ≥3% absolute gain over baseline
- **Baseline:** 0.899 (clean), 0.812 (fault), 0.715 (stress)
- **Non-inferiority Margin:** -2% allowed decrease

### Confidence Calibration
- **Target:** Increase by ≥5% over baseline
- **Baseline:** 0.805 (clean), 0.675 (fault), 0.600 (stress)
- **Non-inferiority Margin:** -3% allowed decrease

### Route Efficiency
- **Target:** Reduce route length by ≥5% over baseline
- **Baseline:** 10.025 (clean), 11.984 (fault), 14.364 (stress)
- **Non-inferiority Margin:** +3% allowed increase

## Secondary Metrics

### Latency
- **Non-inferiority Margin:** +10% allowed increase
- **Baseline:** 0.497s (clean), 0.641s (fault), 0.763s (stress)

### Invalid Transition Rate
- **Target:** Reduce by ≥25% over baseline
- **Baseline:** 0.010 (clean), 0.050 (fault), 0.083 (stress)
- **Non-inferiority Margin:** +15% allowed increase

### Fault Degradation Slope
- **Target:** Flatten by ≥10% over baseline
- **Calculation:** (Fault_Success - Clean_Success) / (Stress_Success - Clean_Success)
- **Baseline:** ~0.77 (fault/stress degradation ratio)

### Recovery Consistency
- **Target:** Increase by ≥5% over baseline
- **Definition:** Fraction of perturbed runs returning to baseline performance
- **Baseline:** Variable by perturbation type

## Statistical Hygiene

### Multiple Comparisons Correction
- **Method:** Holm-Bonferroni correction for family-wise error control
- **Hypothesis Family:** Pre-declared primary metrics only
- **Alpha Level:** 0.05 (corrected)

### Effect Size Requirements
- **Primary Metrics:** Cohen's d ≥ 0.2 (small but meaningful)
- **Secondary Metrics:** Cohen's d ≥ 0.1 (indicative)
- **Confidence Intervals:** 95% CI reported for all effects

### Non-Inferiority Margins
- **Declaration:** Fixed before experiment run
- **Latency:** +10% margin
- **Robustness:** -5% margin on success rate under fault
- **Invalid Transitions:** +15% margin

## Candidate Structure

### Tesseract-Only Optimization (Phase 3A)
1. **Parameters to Tune:**
   - Phi prior strength (0.5-2.0)
   - Routing confidence threshold (0.7-0.95)
   - Fault-mask penalty (0.1-1.0)
   - Edge-score weighting (0.5-1.5)

2. **Constraints:**
   - Biomimetic adaptation OFF
   - Same task suite as baseline
   - Same condition classes (clean, fault, stress)

### Biomimetic Addition (Phase 3B)
1. **Activation Criteria:**
   - Tesseract alone shows ≥1 primary metric improvement
   - No degradation beyond non-inferiority margins
   - Effect size ≥ 0.1 on any metric

2. **Biomimetic Parameters:**
   - Plasticity rate (0.001-0.05)
   - Resilience threshold (0.5-0.9)
   - Emergence detection window (5-50 steps)

## Governance Requirements

### Experiment Registration
- All candidates must be pre-registered via `governance_layer.py`
- Hypotheses declared before execution
- Success/failure criteria frozen

### Metric Tracking
- All primary and secondary metrics recorded via `MetricsRegistry`
- Raw data preserved in JSONL format
- Confidence intervals computed for all comparisons

### Reproducibility
- Software hash verified
- Configuration locked with hash
- Seeds stratified by condition

## Practical Targets

### Minimum Defensible Win
1. **Success Rate:** +3% absolute gain under fault/stress
2. **Latency:** Within +10% non-inferiority margin
3. **Invalid Transitions:** No worsening beyond +15% margin

### Evidence Value
Even negative results are valuable:
- If tesseract cannot win, shift to biomimetic adaptation
- If biomimetic cannot win, shift to memory-policy improvements
- Document all findings for strategic pivots

## Decision Process

### Promote
- Passes all three-part gate
- Meets effect size requirements
- Maintains governance compliance

### Reject
- Fails superiority on any primary metric
- Exceeds non-inferiority margins
- Shows degradation without compensating gains

### Iterate
- Shows promising trends but needs refinement
- Requires additional parameter tuning
- Needs larger sample size for significance

---

*This criteria set is LOCKED as of 2026-04-19.*  
*Any changes require version bump and re-approval.*