> **Status:** Experimental research repository. NFT deployment and contract-verification workflows remain paused while that workstream is on hold.

# AGI-model

AGI-model is a research platform for exploring a quantum-inspired variational autoencoder (VAE), consciousness-oriented analysis workflows, and TMT-OS integrations in one repository.

## 🚀 Advanced Quantum Consciousness Features

This repository has been significantly enhanced with cutting-edge quantum consciousness capabilities:

### Novel Quantum Circuit Architectures
Five biologically-inspired quantum circuits for consciousness processing:
- Hierarchical Fractal Neural Networks
- Biomimetic Spiking Quantum Circuits
- Epigenetic Quantum Circuits
- Neurotransmitter-Inspired Quantum Channels
- Consciousness-Level Adaptive Circuits

📁 Implementation: `novel_quantum_circuits.py`
📚 Documentation: `ADVANCED_QUANTUM_CONSCIOUSNESS_FEATURES.md` (Section 1)

### Quantum Teleportation for Consciousness Transfer
Specialized protocols for secure consciousness state migration:
- Consciousness Teleportation Protocol
- Inter-Agent Consciousness Transfer
- Consciousness Teleportation Manager

📁 Implementation: `consciousness_teleportation.py`
📚 Documentation: `ADVANCED_QUANTUM_CONSCIOUSNESS_FEATURES.md` (Section 2)

### Ensemble Quantum Agents
Collaborative intelligence models combining specialized quantum agents:
- Quantum Agent Framework with specialized roles
- Consciousness Fusion Engine
- Adaptive Agent Coordinator

📁 Implementation: `ensemble_quantum_agents.py`
📚 Documentation: `ADVANCED_QUANTUM_CONSCIOUSNESS_FEATURES.md` (Section 3)

### Integrated Consciousness System
Unified framework demonstrating all advanced features working together:

📁 Implementation: `integrated_consciousness_system.py`
📊 Summary: `QUANTUM_CONSCIOUSNESS_ADVANCEMENT_SUMMARY.md`

## 🚀 Enhanced Professional Features

It combines model training, latent-space analysis, quantum experiment utilities, dashboards, and validation tooling for researchers and contributors working across machine learning, scientific computing, and experimental system integration.

Benchmark note: This benchmark reports integrated workflow throughput and a derived token-equivalent processing rate; it does not measure literal LLM text-generation tokens/sec.

## Table of contents

- [Overview](#overview)
- [Key capabilities](#key-capabilities)
- [Technology stack](#technology-stack)
- [Getting started](#getting-started)
- [Common workflows](#common-workflows)
- [Repository structure](#repository-structure)
- [Documentation](#documentation)
- [Roadmap](#roadmap)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Overview

This repository brings together three complementary areas of work:

1. **Quantum-inspired modeling** — a VAE pipeline centered on 128-dimensional inputs, 32-dimensional latent representations, and quantum-oriented metrics such as coherence, fidelity, entropy, and mixed-state regularization.
2. **Analysis and experimentation** — scripts for golden ratio pattern analysis, latent-space visualization, EEG/fMRI-oriented exploration, sacred geometry experiments, and IBM Quantum job inspection.
3. **Operational tooling** — tests, Docker assets, dashboards, developer workflows, documentation, and TMT-OS integration modules to support repeatable experimentation.

The project should be treated as an actively evolving research codebase rather than a finished production product.

## Key capabilities

| Area | Description | Primary entry points |
| --- | --- | --- |
| Model training | Train the core quantum-inspired VAE and persist checkpoints and plots | `train_vae.py`, `vae_model.py` |
| Validation | Run automated tests and local smoke checks | `tests/`, `test_model.py`, `.github/workflows/ci.yml` |
| Analysis | Explore latent space, golden ratio proximity, consciousness metrics, and IBM experiment outputs | `latent_analysis.py`, `golden_ratio_*.py`, `quantum_consciousness_link.py` |
| Visualization | Launch an interactive Streamlit dashboard | `dashboards/quantum_consciousness_dashboard/app.py` |
| Integration | Work across TMT-OS, provenance, geometry, and observer-related modules | `TMT-OS/`, `integrations/`, `molecular_geometry/`, `quantum_observer/` |

## Technology stack

- **Language/runtime:** Python 3.10+
- **Core ML/scientific libraries:** PyTorch, NumPy, SciPy, Matplotlib
- **Developer tooling:** pytest, flake8, Black, pre-commit, Bandit, Safety
- **App and ops tooling:** Streamlit, Docker, Docker Compose, GitHub Actions
- **Adjacent integrations:** TMT-OS modules, IBM Quantum-oriented scripts, data provenance and dashboard assets

## Getting started

### Prerequisites

- Python 3.10 or newer
- `pip` and `venv`
- Optional: Docker and Docker Compose for containerized workflows
- Optional: IBM Quantum credentials for hardware-facing experiments

### Recommended setup

```bash
git clone https://github.com/quantumdynamics927-dotcom/AGI-model.git
cd AGI-model
make setup
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

## Common workflows

### Validate the local environment

```bash
make lint
make test
make check
```

What these commands do:

- `make lint` runs `flake8` and `black --check`
- `make test` runs the test suite under `tests/`
- `make check` runs linting, tests, and security scanning in sequence

### Train the model

```bash
make train
# or
python train_vae.py
```

Expected outputs typically include:

- a trained checkpoint such as `best_model.pt`
- generated plots such as training curves
- console metrics covering reconstruction, KL divergence, coherence, fidelity, and entropy-related terms

### Run a quick model smoke test

```bash
python test_model.py
```

Use this when you want a lightweight verification that the saved model can be loaded and exercised locally.

### Launch the dashboard

```bash
make dashboard
# or
streamlit run dashboards/quantum_consciousness_dashboard/app.py
```

### Run analysis workflows

```bash
python quantum_consciousness_link.py
python latent_analysis.py
python golden_ratio_analysis.py
```

These scripts support exploratory analysis of latent structure, resonance patterns, and downstream artifacts.

### Use container workflows

```bash
make dev
make build
make build-dashboard
```

## Repository structure

| Path | Purpose |
| --- | --- |
| `vae_model.py` | Core VAE architecture and quantum-oriented loss logic |
| `train_vae.py` | Main training entry point |
| `test_model.py` | Lightweight local model validation |
| `tests/` | Automated regression and integration coverage |
| `docs/` | Central documentation hub |
| `dashboards/quantum_consciousness_dashboard/` | Streamlit dashboard |
| `integrations/` | External and system integration modules |
| `molecular_geometry/` | Molecular and spatial analysis components |
| `TMT-OS/` | TMT-OS integration assets |
| `real_data/` and `sacred_datasets/` | Input datasets used by research workflows |

## Documentation

Key documentation entry points:

- [Documentation hub](docs/README.md)
- [Architecture guide](docs/architecture/README.md)
- [API reference](docs/api/README.md)
- [Deployment guide](docs/deployment/README.md)
- [Development guide](docs/development/README.md)
- [Security guide](docs/security/README.md)
- [Contributing guide](docs/contributing/CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)

## Roadmap

Current priorities for improving repository quality and maintainability include:

- consolidating root-level experimental scripts into clearer domains
- tightening the onboarding experience for training, testing, and dashboard workflows
- improving documentation for deployment, hardware prerequisites, and data expectations
- continuing to stabilize the research pipeline around repeatable validation and provenance

## Troubleshooting

### Missing development tools

If `make lint` or `make test` fails because `flake8`, `pytest`, or other tools are unavailable, install the development dependencies:

```bash
pip install -r requirements-dev.txt
```

### CI import-path mismatches

The CI workflow sets `PYTHONPATH` to include the repository root, `TMT-OS`, and `tmt-os-labs`. If local imports behave differently from CI, mirror that environment before running tests.

### Hardware-facing experiments

IBM Quantum and other external-integration scripts may require credentials or services that are not present in a default local environment. Start with the Python-only workflows first, then enable external credentials deliberately.

## Contributing

Contributions are welcome. Before opening a pull request:

1. review [the contributing guide](docs/contributing/CONTRIBUTING.md),
2. validate your environment with the commands above,
3. update relevant documentation when workflows or behavior change.

## License

This repository is licensed under the [MIT License](LICENSE).
