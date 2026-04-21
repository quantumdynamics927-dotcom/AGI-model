# VCapture Promotion Policy

## Overview

The VCapture Promotion Policy Engine turns the measurement ledger into a calibration governance system with explicit thresholds for promotion decisions.

## Promotion Levels

| Level | Description | Requirements |
|-------|-------------|--------------|
| **DEVELOPMENT** | Not ready for production | Basic functionality, minimal data |
| **STAGING** | Ready for cross-validation | Intermediate thresholds passed |
| **PRODUCTION** | Ready for deployment | All gates passed |
| **DEPRECATED** | Should be replaced | Multiple gates failed |

## Promotion Gates

### 1. Replicate Count Gate
- **Purpose**: Ensure sufficient data for statistical inference
- **Thresholds**:
  - Min replicates per cell: 3
  - Min total records: 20
- **Current Status**: ✓ PASS (3 per cell, 30 total)

### 2. Residual Spread Gate
- **Purpose**: Ensure calibration removes systematic bias
- **Thresholds**:
  - Max residual std: 0.10
  - Max |mean residual|: 0.05
- **Current Status**: ✗ FAIL (std=0.0848, mean=0.1417)

### 3. Signal-to-Separation Gate
- **Purpose**: Ensure promoter identity is recoverable above noise
- **Thresholds**:
  - Min S/S ratio: 2.0
  - Min promoters above threshold: 50%
- **Current Status**: ✗ FAIL (mean S/S=1.42, 20% above threshold)

### 4. Portability Gate
- **Purpose**: Ensure calibration transfers across backends
- **Thresholds**:
  - Min transfer efficiency: 90%
  - Min ranking correlation: 80%
  - Min portability score: 85%
- **Current Status**: ✗ FAIL (efficiency=100%, ranking=0.70, score=85.0%)

### 5. Stability Gate
- **Purpose**: Ensure measurement reproducibility
- **Thresholds**:
  - Max within-promoter std: 0.01
- **Current Status**: ✓ PASS (std=0.0015)

### 6. Model Fit Gate
- **Purpose**: Ensure variance decomposition is meaningful
- **Thresholds**:
  - Min R²: 0.70
  - Max interaction variance ratio: 0.1
- **Current Status**: ✓ PASS (R²=0.9002, interaction=0.0)

## Current Assessment

**Promotion Level**: DEVELOPMENT
**Eligible for PRODUCTION**: NO ✗
**Gates Passed**: 3/6
**Overall Score**: -0.0588

### Blocking Issues

1. **Residual spread too high**: Mean residual 0.1417 exceeds threshold 0.05
2. **Promoter separation insufficient**: Only 2/10 promoters above S/S threshold
3. **Calibration not portable**: Ranking correlation 0.70 below threshold 0.80

### Recommendations

1. Investigate residual outliers; consider robust calibration methods
2. Increase promoter distinctiveness or reduce measurement noise
3. Use backend-conditioned or hierarchical calibration instead of universal offset

## Threshold Reference

### PRODUCTION Thresholds
| Gate | Threshold | Current | Status |
|------|-----------|---------|--------|
| Replicates per cell | ≥ 3 | 3 | ✓ |
| Total records | ≥ 20 | 30 | ✓ |
| Residual std | ≤ 0.10 | 0.0848 | ✓ |
| Residual mean | ≤ 0.05 | 0.1417 | ✗ |
| S/S ratio | ≥ 2.0 | 1.42 | ✗ |
| Promoters above S/S | ≥ 50% | 20% | ✗ |
| Transfer efficiency | ≥ 90% | 100% | ✓ |
| Ranking correlation | ≥ 80% | 70% | ✗ |
| Portability score | ≥ 85% | 85.0% | ✗ |
| Within-promoter std | ≤ 0.01 | 0.0015 | ✓ |
| R² | ≥ 0.70 | 0.9002 | ✓ |
| Interaction ratio | ≤ 0.1 | 0.0 | ✓ |

### STAGING Thresholds (for reference)
| Gate | Threshold |
|------|-----------|
| Replicates per cell | ≥ 2 |
| Residual std | ≤ 0.15 |
| S/S ratio | ≥ 1.5 |
| Transfer efficiency | ≥ 85% |
| Ranking correlation | ≥ 70% |
| R² | ≥ 0.60 |

## Usage

```bash
# Assess calibration for production promotion
python vcapture_promotion_policy.py \
    --ledger raw_hardware/vcapture_ledger_report.json \
    --target-level production

# Assess for staging promotion
python vcapture_promotion_policy.py \
    --ledger raw_hardware/vcapture_ledger_report.json \
    --target-level staging
```

## Integration with Calibration Workflow

1. **Run calibration** → Generate VCapture ledger
2. **Assess promotion** → Run promotion policy engine
3. **Review gates** → Identify blocking issues
4. **Address issues** → Increase replicates, improve calibration, etc.
5. **Re-assess** → Iterate until promotion level achieved
6. **Promote** → Deploy calibration model to next environment

## Key Insight

The most valuable thing VCapture now provides is **evidence-based governance**:

- **Stable**: Measurement stability confirmed (low within-promoter variance)
- **Discriminative**: Identity separation needs improvement (S/S too low)
- **Transferable**: RMSE transfers well, but ranking does not
- **Promotion-worthy**: Currently at DEVELOPMENT level, needs work for PRODUCTION

This is exactly the infrastructure needed to move from empirical runs to governed, falsifiable calibration decisions.