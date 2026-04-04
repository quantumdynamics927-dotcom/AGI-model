## 2026-04-04 — IBM promoter replicate batch

- Ingested the completed 30-run promoter replicate set across `ibm_fez` and `ibm_kingston` for `SRY`, `FOXG1`, `DCTN1`, `TP53`, and `OXT`, with 3 replicates per promoter-backend pair and 30 of 30 jobs reaching completion.
- Generated archive-backed raw hardware artifacts in `raw_hardware/`, refreshed the replicate manifest and matrix, and confirmed lineage validity for all 30 new per-run artifacts after fixing a Windows console encoding issue in `agi_scripts/validate_artifact_lineage.py`.
- Observed mean measured phi of `0.615994` on `ibm_fez` and `0.613398` on `ibm_kingston`, with backend-aware calibration offsets of `-0.140406` and `-0.143002`, respectively.
- Promoter-specific backend interaction remained low, with backend spread between `0.002263` and `0.002795` across all five promoters, and backend RMSE remained effectively matched (`0.084773` for `ibm_fez`, `0.084847` for `ibm_kingston`).
- Result: the replicate evidence supports keeping `ibm_fez` as the reference calibration backend while treating `ibm_kingston` as a throughput-capable backend under the current replicate-aware correction model.

## 2026-01-19 — DL-QMC update

- Added `dl_qmc.py`: lightweight VMC implementation with MLP wavefunction and local energy estimation via autograd.
- Implemented MALA (Metropolis-adjusted Langevin) sampler and added test coverage in `tests/test_dl_qmc_langevin.py`.
- Added demo notebook `notebooks/dl_qmc_langevin_demo.xml` and runner script `scripts/run_dl_qmc_demo.py`.
- Updated `README.md` with DL-QMC usage notes.
