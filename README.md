> **Note:** NFT-related workflows are currently on hold. NFT generation, deployment, and contract verification remain disabled in CI/CD until that workstream resumes.

# Quantum Consciousness VAE

Quantum Consciousness VAE is an experimental research repository for training, analyzing, and operationalizing a quantum-inspired variational autoencoder alongside TMT-OS integrations, latent-space analysis utilities, and validation workflows.

## About this repository

This repository combines three main areas of work:

1. **Core modeling** — a variational autoencoder that compresses 128-dimensional inputs into a 32-dimensional latent space while tracking quantum-inspired metrics such as coherence, fidelity, entropy, and mixed-state regularization.
2. **Analysis and experimentation** — scripts for golden ratio studies, latent-space visualization, EEG/fMRI-oriented exploration, IBM Quantum job analysis, and additional research experiments.
3. **Operational tooling** — developer workflows, tests, dashboards, Docker assets, documentation, and TMT-OS integration modules for broader system orchestration.

**Project status:** experimental, research-oriented, and actively evolving. The repository contains production-style tooling, but the model and surrounding theory should still be treated as an exploratory platform rather than a finished product.

## Why this repository exists

The project is designed to make it easier to:

- train and inspect a quantum-inspired VAE without rebuilding the training pipeline from scratch;
- compare practical outputs such as saved checkpoints, training curves, dashboards, and analysis reports;
- validate changes using repeatable local commands before shipping new experiments;
- navigate the larger TMT-OS ecosystem without guessing where major components live.

## Core capabilities

| Area | What it provides | Primary entry points |
| --- | --- | --- |
| Model training | Quantum-inspired VAE training, checkpointing, training curves, console metrics | `train_vae.py`, `vae_model.py` |
| Model validation | Smoke tests and local verification helpers | `test_model.py`, `tests/`, `make test` |
| Analysis | Golden ratio, latent-space, consciousness, and IBM Quantum result analysis | `latent_analysis.py`, `golden_ratio_*.py`, `quantum_consciousness_link.py` |
| Visualization | Interactive dashboard for monitoring and exploration | `dashboards/quantum_consciousness_dashboard/app.py`, `make dashboard` |
| Integrations | TMT-OS modules, provenance, molecular geometry, observer and vault-adjacent components | `TMT-OS/`, `integrations/`, `molecular_geometry/` |

## Quick start

### Prerequisites

- Python 3.10 or newer
- `pip` and `venv`
- Optional: Docker and Docker Compose for container workflows
- Optional: IBM Quantum credentials if you plan to run hardware-facing experiments

### Recommended setup

```bash
git clone https://github.com/quantumdynamics927-dotcom/AGI-model.git
cd AGI-model

# Recommended developer setup
make setup

# Create local environment configuration
make env
```

### Manual setup

```bash
python -m venv .venv
source .venv/bin/activate  # Linux / macOS
# .venv\Scripts\activate   # Windows PowerShell

pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt
cp .env.example .env
```

## Validate your environment

Use the existing Make targets to confirm that your local environment is ready:

```bash
# Run code style checks
make lint

# Run the Python test suite
make test

# Run the combined quality gate
make check
```

What each command does:

- `make lint` runs `flake8` and `black --check`
- `make test` runs `pytest tests/ -v`
- `make check` runs linting, tests, and security scanning in sequence

If `make lint` or `make test` fail immediately with messages such as `No module named flake8` or `No module named pytest`, install the developer dependencies first:

```bash
pip install -r requirements-dev.txt
```

## Common workflows with examples

### 1. Train the model

```bash
make train
# or
python train_vae.py
```

Typical outcomes from a successful training run:

- a best checkpoint such as `best_model.pt`
- generated figures such as `training_curves.png`
- console output showing reconstruction, KL, hamming, coherence, fidelity, and entropy-related metrics

Example training output:

```text
🚀 Starting Quantum VAE Training
Training on device: cpu
Target epochs: 200, Early stopping patience: 30

Epoch 80/200 - Quantum VAE Training
Reconstruction: 0.0170
KL Divergence: 4.1700
Quantum Fidelity: 0.9900
Entanglement Entropy: 1.0400
```

### 2. Run a quick local model check

```bash
python test_model.py
```

Use this when you want a lightweight confirmation that the saved model can be loaded and exercised without launching a full training cycle.

### 3. Start the dashboard

```bash
make dashboard
# or
streamlit run dashboards/quantum_consciousness_dashboard/app.py
```

Use the dashboard to review metrics, inspect outputs, and demonstrate the system interactively.

### 4. Run analysis scripts

```bash
python quantum_consciousness_link.py
python latent_analysis.py
python golden_ratio_analysis.py
```

These scripts are useful when you want to:

- inspect latent-space structure,
- study golden ratio proximity and resonance patterns,
- compare training artifacts with downstream analysis outputs.

### 5. Use containerized workflows

```bash
make dev
make build
make build-dashboard
```

This path is appropriate when you want a more reproducible local environment or you are preparing deployment-oriented validation.

## Repository layout

| Path | Purpose |
| --- | --- |
| `vae_model.py` | Core VAE architecture and quantum-oriented loss helpers |
| `train_vae.py` | Main training orchestration entry point |
| `test_model.py` | Lightweight local validation script |
| `tests/` | Automated regression and integration test coverage |
| `docs/` | Documentation hub for architecture, API, deployment, development, and security |
| `dashboards/quantum_consciousness_dashboard/` | Streamlit application for interactive exploration |
| `integrations/` | External system adapters and observer-style integrations |
| `molecular_geometry/` | Molecular and spatial analysis modules |
| `TMT-OS/` | TMT-OS integration assets and system-level components |

## Architecture summary

See [`docs/architecture/README.md`](docs/architecture/README.md) for the longer form architecture guide.

At a high level, the repository centers on:

- **Encoder / decoder pipeline** for 128 → 32 → 128 dimensional compression and reconstruction
- **Latent-space regularization** for KL divergence, mixed-state learning, and quantum-inspired metrics
- **Analysis layers** for sacred geometry, golden ratio, consciousness-oriented, and hardware-oriented studies
- **TMT-OS coordination** for broader orchestration across supporting modules and experiments

## Documentation map

Start with the documents most relevant to your goal:

- [Documentation hub](docs/README.md)
- [Architecture guide](docs/architecture/README.md)
- [API reference](docs/api/README.md)
- [Deployment guide](docs/deployment/README.md)
- [Development guide](docs/development/README.md)
- [Security guide](docs/security/README.md)
- [Contributing guide](docs/contributing/CONTRIBUTING.md)

## Quality and security

The repository includes:

- automated tests under `tests/`
- developer quality commands in the `Makefile`
- security-oriented documentation in `docs/security/README.md`
- CI workflows under `.github/workflows/`

For a broader local verification pass, use:

```bash
make test-coverage
make security-scan
```

## Contributing

Contributions are welcome. Before opening a pull request:

1. review [`docs/contributing/CONTRIBUTING.md`](docs/contributing/CONTRIBUTING.md),
2. confirm your environment with the validation commands above,
3. update documentation when behavior or workflows change.

## Support

- Open an issue on GitHub for bugs or documentation gaps
- Review the docs in `docs/` before starting a large change
- Contact the maintainers if you need clarification on repository direction or integrations
