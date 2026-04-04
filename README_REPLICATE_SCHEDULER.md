# Promoter Replicate Scheduler

This scheduler expands the IBM Quantum promoter workflow from single-pass submission to a controlled replicate matrix.

## Purpose

The scheduler preserves `ibm_fez` as the continuity backend and pairs it with `ibm_kingston` for comparison runs before any default backend switch is made.

It creates a manifest with one row per:

- promoter
- backend
- replicate index

Each scheduled run records:

- promoter ID
- replicate index
- backend
- shots
- cohort-selection tags
- predicted phi when available
- transpiled depth and qubit layout placeholders
- measured phi, calibrated phi, and residual placeholders

## Usage

Dry-run schedule generation:

```powershell
python agi_scripts/schedule_promoter_replicates.py
```

Five replicates across Fez and Kingston:

```powershell
python agi_scripts/schedule_promoter_replicates.py --replicates 5 --backends ibm_fez,ibm_kingston
```

Schedule all promoters:

```powershell
python agi_scripts/schedule_promoter_replicates.py --all-promoters
```

Build and submit immediately:

```powershell
python agi_scripts/schedule_promoter_replicates.py --submit --api-key <TOKEN>
```

## Outputs

Default outputs:

- `raw_hardware/promoter_replicate_schedule_manifest.json`
- `raw_hardware/promoter_replicate_schedule_matrix.csv`

The JSON manifest is the authoritative artifact for later backend-aware calibration.

## Scientific sequencing

Recommended order:

1. Build the replicate matrix
2. Run Fez and Kingston replicates
3. Fit backend-aware calibration on replicate-aware observations
4. Only then consider changing the default submission backend

This keeps the current Fez phi baseline intact while expanding evidence quality.
