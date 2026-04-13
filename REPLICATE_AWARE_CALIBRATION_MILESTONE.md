# Replicate-Aware Promoter Calibration Milestone

**Date:** April 13, 2026  
**Status:** ✅ Complete

## Overview

This milestone transitions from job-level calibration to **replicate-aware promoter calibration**, enabling robust variance estimation and cross-backend transferability testing.

## Implementation

### New Module: `replicate_aware_promoter_calibration.py`

A comprehensive calibration system that addresses three key requirements:

### 1. Rich Metadata Capture

Each calibration record captures:

| Field | Description |
|-------|-------------|
| `record_id` | Unique identifier (promoter_backend_replicate) |
| `promoter_id` | Gene promoter identifier (e.g., SRY, FOXG1, TP53) |
| `replicate_index` | Replicate number (1, 2, 3, ...) |
| `backend` | Quantum backend (ibm_fez, ibm_kingston) |
| `shots` | Number of measurement shots |
| `transpiled_depth` | Circuit depth after transpilation |
| `qubit_layout` | Physical qubit mapping |
| `predicted_phi` | Model-predicted phi value |
| `measured_phi` | Hardware-measured phi value |
| `calibrated_phi` | Calibrated phi (predicted + offset) |
| `residual` | measured - calibrated |
| `calibration_offset_applied` | Offset used for calibration |
| `calibration_source` | none/backend_default/promoter_specific |
| `timestamp` | Measurement timestamp |
| `job_id` | IBM Quantum job identifier |
| `entropy` | Shannon entropy of measurement |
| `fidelity` | Phi alignment score |

### 2. Variance Structure Estimation

The system computes:

- **Within-promoter variance**: Replicate variability for each promoter
- **Between-promoter variance**: Separation between promoters (per backend)
- **Residual distribution**: Full statistics (mean, std, min, max, median, quartiles)
- **Backend variance components**: ANOVA-style decomposition

**Results from current data:**
```
Within-promoter mean variance: 2.33e-06
Between-promoter mean variance: 6.32e-07
Residual std: 0.0848
```

### 3. Transferability Testing

Tests whether calibration from a reference backend transfers to other backends:

| Metric | Value |
|--------|-------|
| Reference backend | ibm_fez |
| Reference offset | -0.1404 |
| Portability score | **99.95%** |
| Is portable | ✅ True |

**Transfer metrics for ibm_kingston:**
- RMSE with reference offset: 0.0848
- RMSE with native offset: 0.0848
- Transfer efficiency: 99.95%
- Offset difference: 0.0026

## Calibration Results

### Backend Offsets

| Backend | Offset |
|---------|--------|
| ibm_fez | -0.1404 |
| ibm_kingston | -0.1430 |

### Promoter-Backend Offsets

| Promoter | ibm_fez | ibm_kingston | Spread |
|----------|---------|--------------|--------|
| SRY | -0.0808 | -0.0830 | 0.0023 |
| FOXG1 | -0.1263 | -0.1288 | 0.0025 |
| DCTN1 | -0.0392 | -0.0420 | 0.0028 |
| TP53 | -0.2855 | -0.2881 | 0.0026 |
| OXT | -0.1702 | -0.1730 | 0.0028 |

## Recommendations

### Calibration Strategy
**Use unified calibration across backends.** Reference backend ibm_fez offset is portable (99.95% transfer efficiency).

### Backend Selection
**Preferred: ibm_fez** (offset magnitude: 0.1404)

### Replicate Policy
**2 replicates per promoter-backend combination** for stable calibration.

### Quality Gates
1. Residual |z-score| < 2.0 (95% CI)
2. Within-promoter variance < 0.000005
3. Transfer efficiency > 90% for portable calibration

## Usage

```bash
# Run calibration analysis
python replicate_aware_promoter_calibration.py \
  --manifest raw_hardware/promoter_replicate_schedule_manifest.json \
  --output raw_hardware/replicate_aware_calibration_report.json

# With custom parameters
python replicate_aware_promoter_calibration.py \
  --manifest manifest1.json --manifest manifest2.json \
  --tolerance 0.15 \
  --min-replicates 2 \
  --reference-backend ibm_fez
```

## Output Files

- `raw_hardware/replicate_aware_calibration_report.json` - Full calibration database with:
  - All 30 calibration records with rich metadata
  - Backend and promoter-specific offsets
  - Variance structure analysis
  - Transferability assessment
  - Actionable recommendations

## Key Findings

1. **Calibration is PORTABLE**: The ibm_fez offset transfers effectively to ibm_kingston with 99.95% efficiency.

2. **Low within-promoter variance** (~2.3e-06) indicates stable replicate measurements.

3. **Small backend spread** (0.002-0.003) suggests consistent behavior across backends.

4. **Promoter-specific offsets vary significantly** (range: -0.04 to -0.29), justifying promoter-aware calibration.

## Integration Points

- **Input**: Schedule manifests from `promoter_replicate_schedule_manifest.json`
- **Output**: Calibration database for downstream validation
- **Compatible with**: `backend_aware_calibration.py` (legacy), `quantum_calibration_framework.py`

## Next Steps

1. Extend to additional backends (ibm_brisbane, ibm_nazca)
2. Implement time-series calibration drift tracking
3. Add promoter-specific calibration models
4. Integrate with automated job submission pipeline