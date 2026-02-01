## 2026-01-19 — DL-QMC update

- Added `dl_qmc.py`: lightweight VMC implementation with MLP wavefunction and local energy estimation via autograd.
- Implemented MALA (Metropolis-adjusted Langevin) sampler and added test coverage in `tests/test_dl_qmc_langevin.py`.
- Added demo notebook `notebooks/dl_qmc_langevin_demo.xml` and runner script `scripts/run_dl_qmc_demo.py`.
- Updated `README.md` with DL-QMC usage notes.
