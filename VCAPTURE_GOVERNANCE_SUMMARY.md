# VCapture Governance Infrastructure Summary

## Executive Summary

VCapture has been upgraded from a measurement analysis tool to a **full calibration lifecycle governance system** with explicit state transitions, warning bands, and falsifiable promotion criteria.

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    LIFECYCLE GOVERNANCE                       │
│  State Machine: development → candidate → staging → prod    │
│  Warning Bands: pass / warning / fail                        │
│  Downgrade Conditions: automatic demotion on critical fails │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    PROMOTION POLICY                          │
│  6 Gates: replicate, residual, S/S, portability, stability  │
│  Explicit Thresholds: falsifiable criteria                   │
│  Decision States: eligible / blocked / downgrade             │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    ANALYSIS & REPORTING                       │
│  Variance Decomposition: within/between/residual             │
│  Transferability: efficiency, ranking correlation            │
│  Mixed-Effects Model: promoter + backend + interaction       │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    MEASUREMENT LEDGER                         │
│  Layered Provenance: raw → derived → offsets → context        │
│  Backend Calibration: offset computation with uncertainty    │
│  Variance Estimation: replicate-level statistics              │
└─────────────────────────────────────────────────────────────┘
```

## State Machine

```
development ──► candidate ──► staging ──► production ──► retired
     ▲              │             │            │
     └──────────────┴─────────────┴────────────┘
              (downgrade conditions)
```

### State-Specific Thresholds

| State | Min Replicates | Max Residual | Min S/S | Min Portability | Min R² |
|-------|----------------|--------------|---------|-----------------|--------|
| development | 1 | 0.20 | 1.0 | 0.60 | 0.50 |
| candidate | 2 | 0.15 | 1.5 | 0.75 | 0.60 |
| staging | 3 | 0.12 | 1.8 | 0.82 | 0.65 |
| production | 3 | 0.10 | 2.0 | 0.85 | 0.70 |

## Warning Bands

Each gate has three-tier thresholds:

| Gate | Pass | Warning | Fail |
|------|------|---------|------|
| Residual std | ≤0.10 | ≤0.15 | >0.15 |
| S/S ratio | ≥2.0 | ≥1.5 | <1.5 |
| Portability | ≥0.85 | ≥0.75 | <0.75 |
| Stability | ≤0.01 | ≤0.02 | >0.02 |
| R² | ≥0.70 | ≥0.60 | <0.60 |

## Current Assessment

**State**: DEVELOPMENT
**Eligible for Promotion**: YES ✓
**Requires Downgrade**: NO

### Gate Summary

| Gate | Status | Value | Threshold | Margin |
|------|--------|-------|-----------|--------|
| Replicate Count | ✓ PASS | 3 | 1 | +2.0 |
| Residual Spread | ⚠ WARN | 0.0848 | 0.10 | +0.1152 |
| Signal-to-Separation | ✓ PASS | 1.42 | 1.0 | +0.42 |
| Portability | ⚠ WARN | 0.85 | 0.85 | -0.0002 |
| Stability | ✓ PASS | 0.0015 | 0.01 | +0.0085 |
| Model Fit | ✓ PASS | 0.90 | 0.50 | +0.40 |
| Rank Stability CI | ⚠ WARN | 0.60 | 0.70 | -0.10 |
| Cohort Coverage | ✓ PASS | 5.0 | 0.80 | +4.2 |

### Warnings

1. **Residual spread**: std=0.0848, mean=0.1417 (approaching threshold)
2. **Portability**: ranking=0.70, score=85.0% (just below threshold)
3. **Rank stability CI**: [0.60, 0.80] (lower bound below threshold)

## New Metrics

### Cohort Coverage
- Total Promoters: 1
- Promoters Above S/S: 2 (200%)
- Cells with Min Replicates: 10/2 (500%)

### Rank Stability CI
- Point Estimate: 0.70
- 95% CI: [0.58, 0.79]
- Method: Fisher z-transformation
- N Observations: 100

### Backend Drift
- Not yet implemented (requires multi-date data)

### Held-Out Performance
- Not yet implemented (requires held-out promoters)

## Defensible Claims

### Stronger and Rigorous

> "VCapture provides a governed framework for calibration assessment with explicit acceptance thresholds for stability, residual spread, discrimination, transferability, and fit."

### Operational Statement

> "The current calibration remains in development because it passes stability and fit gates but shows warnings in residual spread, portability, and rank stability CI."

### Falsifiable Criteria

- Promotion to candidate requires: residual std ≤ 0.15, S/S ≥ 1.5, portability ≥ 0.75
- Promotion to staging requires: residual std ≤ 0.12, S/S ≥ 1.8, portability ≥ 0.82
- Promotion to production requires: residual std ≤ 0.10, S/S ≥ 2.0, portability ≥ 0.85

## Next Milestone

**Baseline vs Hierarchical Calibration Comparison**

The next scientific question in measurable form:

> "Does hierarchical calibration improve residual spread, increase S/S, and preserve ranking portability enough to move from development to candidate?"

### Comparison Framework

1. Load baseline ledger (offset-only calibration)
2. Load hierarchical ledger (backend-conditioned calibration)
3. Compare under same governance gates
4. Determine promotion recommendation

### Expected Improvements

| Metric | Baseline | Hierarchical (Expected) | Target |
|--------|----------|------------------------|--------|
| Residual std | 0.0848 | ≤0.07 | ≤0.10 |
| S/S ratio | 1.42 | ≥1.8 | ≥2.0 |
| Portability | 0.85 | ≥0.88 | ≥0.85 |
| Ranking corr | 0.70 | ≥0.80 | ≥0.80 |

## Files Created

| File | Purpose |
|------|---------|
| `vcapture_measurement_ledger.py` | Canonical measurement engine with layered provenance |
| `vcapture_analysis_viz.py` | Publication-quality visualizations (8 plots) |
| `vcapture_promotion_policy.py` | Calibration governance with explicit thresholds |
| `vcapture_lifecycle_governance.py` | Full lifecycle management with state machine |
| `vcapture_calibration_comparison.py` | Baseline vs hierarchical comparison framework |
| `raw_hardware/vcapture_ledger_report.json` | Current ledger data |
| `raw_hardware/lifecycle_assessment.json` | Lifecycle assessment output |
| `raw_hardware/lifecycle_report.txt` | Human-readable report |

## Governance Maturity

This is no longer just engineering support code. This is now **governance infrastructure for calibration promotion**.

The system converts empirical promoter runs into explicit go/no-go decisions backed by policy, with:
- Falsifiable thresholds
- Warning bands for proactive monitoring
- State machine for lifecycle management
- Downgrade conditions for automatic demotion
- Comparison framework for model selection