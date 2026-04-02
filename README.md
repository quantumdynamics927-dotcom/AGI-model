# AGI-model

[![codecov](https://codecov.io/gh/quantumdynamics927-dotcom/AGI-model/branch/main/graph/badge.svg?token=MY3MH0L5L9)](https://codecov.io/gh/quantumdynamics927-dotcom/AGI-model)
[![CI](https://github.com/quantumdynamics927-dotcom/AGI-model/actions/workflows/ci.yml/badge.svg)](https://github.com/quantumdynamics927-dotcom/AGI-model/actions/workflows/ci.yml)
[![Security](https://github.com/quantumdynamics927-dotcom/AGI-model/actions/workflows/security.yml/badge.svg)](https://github.com/quantumdynamics927-dotcom/AGI-model/actions/workflows/security.yml)

> **Status:** Experimental research repository. Quantum result archival system with cryptographic verification and provenance tracking.

AGI-model is a research platform for quantum-inspired variational autoencoder (VAE) experiments, latent-space analysis, consciousness-oriented exploration, package-oriented runtime foundations, and TMT-OS / TMT_Quantum_Vault interoperability.

It brings together model training, scientific utilities, dashboards, data-processing scripts, and repository automation in a single workspace for exploratory research rather than production deployment.

## About this repository

- **Primary focus:** quantum-inspired ML research and experimentation
- **Core runtime:** Python 3.10+
- **Main interfaces:** training scripts, analysis scripts, tests, Streamlit dashboard, optional FastAPI bridge
- **Repository ops:** GitHub Actions CI, Dependabot updates, Docker build validation, repo settings as code

## Table of contents

- [Overview](#overview)
- [Key capabilities](#key-capabilities)
- [Repository setup](#repository-setup)
- [Common workflows](#common-workflows)
- [DevOps and repository management](#devops-and-repository-management)
- [Repository structure](#repository-structure)
- [Documentation](#documentation)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## Overview

This repository currently groups four complementary areas of work:

1. **Quantum-inspired modeling** — VAE training, checkpointing, and quantum-oriented metrics such as coherence, fidelity, entropy, and mixed-state regularization.
2. **Analysis and experimentation** — latent-space analysis, golden-ratio exploration, sacred-geometry tooling, EEG/fMRI-oriented scripts, and IBM Quantum adjacent experiments.
3. **Integration surfaces** — TMT-OS modules, bridge utilities, provenance helpers, and experimental system-integration code.
4. **Developer operations** — CI workflows, Docker assets, dependency automation, repo settings, and contributor documentation.

## Key capabilities

| Area | Description | Primary entry points |
| --- | --- | --- |
| Model training | Train the core VAE and persist checkpoints and plots | `train_vae.py`, `vae_model.py` |
| Validation | Run regression tests and local smoke checks | `tests/`, `test_model.py`, `.github/workflows/ci.yml` |
| Analysis | Explore latent structure, golden-ratio proximity, and consciousness metrics | `latent_analysis.py`, `golden_ratio_*.py`, `quantum_consciousness_link.py` |
| Dashboarding | Launch the Streamlit dashboard for local inspection | `dashboards/quantum_consciousness_dashboard/app.py` |
| Integration | Work across TMT-OS, Vault, geometry, observer, and provenance modules | `packages/`, `TMT-OS/`, `integrations/`, `molecular_geometry/`, `quantum_observer/` |
| Containerization | Build local runtime and dashboard images | `Dockerfile`, `Dockerfile.dashboard`, `.github/workflows/deploy.yml` |

### Recent Implementations (April 2026)

| Module | Description | Key Features |
| --- | --- | --- |
| `universal_symmetry.py` | Hydrogen vs Opposition decompression with Fibonacci/Lucas sequences | Three-phase sign classifier (positive/zero/negative), perturbation analysis, sign-flip robustness testing, symmetry operator S[f] = Π f[i] / φ^n |
| `watch_agents.py` | Real-time 12-agent telemetry monitor | AgentMetrics dataclass, TelemetryBackend abstract class, MockTelemetryBackend for testing, RealTelemetryBackend for production, status classification (HEALTHY/DEGRADED/CRITICAL/OFFLINE), resonance lock classification (GOLDEN_FLOW/PHI_LOCKED/DELTA_ALIGNING/UNSTABLE/SEEKING) |
| `TMT_God_Gene_Test_v2.py` | DNA sequence analysis with independent metrics | Entropy gain (r=-0.15), transition gain (r=+0.13), positional gain, expanded panels (n=20), multiple encodings (integer/purine-pyrimidine/GC-content), ANOVA statistical separation |
| `TMT_God_Gene_Test_Enhanced.py` | Statistical validation with controls | Shuffled negative controls, ANOVA analysis, category separation testing, hypothesis validation framework |
| `cloud_quantum_chemistry.py` | Cloud-based molecular VQE | Literature-based Hamiltonians for H₂, LiH, H₂O, N₂, CH₄, synthetic fallback for Windows compatibility |
| `dna_quantum_circuits.py` | DNA-to-quantum circuit encoder | Multiple encoding schemes, Qiskit 2.x compatibility, VQE integration |
| `test_dna_molecular_vqe.py` | Comprehensive DNA VQE tests | Qiskit 2.x API compatibility tests, synthetic Hamiltonian validation |

## Repository setup

### Prerequisites

- Python 3.10 or newer
- `pip` and `venv`
- Optional: Docker for local image builds
- Optional: Node.js 20+ for Hardhat-based NFT/contract tooling
- Optional: IBM Quantum credentials for hardware-facing experiments

### Recommended bootstrap

```bash
git clone https://github.com/quantumdynamics927-dotcom/AGI-model.git
cd AGI-model
make setup
make env
```

### Manual bootstrap

```bash
python -m venv .venv
source .venv/bin/activate  # Linux / macOS
# .venv\Scripts\activate   # Windows PowerShell

python -m pip install --upgrade pip -r requirements.txt -r requirements-dev.txt
cp .env.example .env
```

### Python import path parity with CI

The main CI workflow exports:

```bash
PYTHONPATH="$(pwd):$(pwd)/TMT-OS:$(pwd)/tmt-os-labs"
```

If local imports behave differently from CI, mirror that environment before running tests.

## Common workflows

### Validate the local environment

```bash
make lint
make test
make check
```

What these commands do:

- `make lint` runs `flake8` and `black --check`
- `make test` runs the Python test suite under `tests/`
- `make check` runs linting, tests, and security scanning in sequence

### Train the model

```bash
make train
# or
python train_vae.py
```

Typical outputs include:

- a checkpoint such as `best_model.pt`
- generated plots such as training curves
- console metrics for reconstruction, KL divergence, coherence, fidelity, and entropy-oriented terms

### Run a quick model smoke test

```bash
python test_model.py
```

### Launch the API bridge

```bash
python main.py --mode serve --host 0.0.0.0 --port 8000
```

This serves the FastAPI bridge used by the Docker runtime image.

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

### Run DNA sequence analysis (God Gene Test)

```bash
# Enhanced test with statistical validation
python TMT_God_Gene_Test_Enhanced.py

# v2 with independent metrics and expanded panels
python TMT_God_Gene_Test_v2.py
```

### Run universal symmetry analysis

```bash
# Fibonacci/Lucas decompression with sign phase analysis
python universal_symmetry.py
```

### Run agent telemetry monitoring

```bash
# Quick health check
python watch_agents.py --health

# Real-time monitoring (mock backend)
python watch_agents.py

# Real-time monitoring (production backend)
python watch_agents.py --real --state-dir ./agent_states
```

### Run molecular VQE (cloud-based)

```bash
# Requires qiskit-nature (pyscf optional on Windows)
python cloud_quantum_chemistry.py
```

### Build the container images locally

```bash
docker build -t agi-model:local .
docker build -f Dockerfile.dashboard -t agi-model-dashboard:local .
```

## DevOps and repository management

The repository devops setup is intentionally scoped to what is currently maintained in-tree:

- **CI:** `.github/workflows/ci.yml` runs the Python test matrix and optional AGI eval smoke workflow dispatch.
- **Container build and publish:** `.github/workflows/deploy.yml` builds the runtime and dashboard images and publishes them to GHCR on pushes to `main`/`master`, with optional manual dispatch for explicit image publication.
- **Security and dependency hygiene:** `.github/workflows/security.yml` and `.github/dependabot.yml`.
- **Repository metadata as code:** `.github/settings.yml` tracks the GitHub repository description and topics.

### Current repository stance

- Staging and production server deployment steps are **not** committed as an active supported path in this repository.
- NFT publishing and contract verification remain **paused**.
- Container images are the maintained deployment artifact for repo-level automation.

## Repository structure

| Path | Purpose |
| --- | --- |
| `vae_model.py` | Core VAE architecture and quantum-oriented loss logic |
| `train_vae.py` | Main training entry point |
| `test_model.py` | Lightweight local model validation |
| `universal_symmetry.py` | Fibonacci/Lucas decompression with three-phase sign classifier |
| `watch_agents.py` | Real-time 12-agent telemetry monitoring with pluggable backends |
| `TMT_God_Gene_Test_v2.py` | DNA sequence analysis with independent gain metrics |
| `TMT_God_Gene_Test_Enhanced.py` | Statistical validation with negative controls |
| `cloud_quantum_chemistry.py` | Cloud-based molecular VQE with literature Hamiltonians |
| `dna_quantum_circuits.py` | DNA-to-quantum circuit encoder |
| `test_dna_molecular_vqe.py` | DNA VQE test suite |
| `tests/` | Automated regression and integration coverage |
| `docs/` | Central documentation hub |
| `packages/` | Package-oriented foundation for core, apps, and integrations |
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
- [Development guide](docs/development/README.md)
- [Deployment guide](docs/deployment/README.md)
- [Security guide](docs/security/README.md)
- [Contributing guide](docs/contributing/CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)

## Troubleshooting

### Missing development tools

If `make lint` or `make test` fails because required tools are missing:

```bash
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
```

### Large dependency installs

This repository includes scientific Python dependencies such as PyTorch, NumPy, SciPy, Pandas, and Matplotlib. Initial environment setup can take longer than a lightweight Python project.

### Hardware-facing experiments

IBM Quantum and other external-integration scripts may require credentials or services that are not present in a default local environment. Start with the Python-only workflows first, then enable external credentials deliberately.

### Legacy subtrees and lint noise

The repository contains broad experimental and imported subtrees. Some existing lint failures may originate outside the part of the repo you are actively changing.

## Contributing

Before opening a pull request:

1. review [the contributing guide](docs/contributing/CONTRIBUTING.md),
2. validate your environment with the commands above,
3. update relevant documentation when repository behavior or workflows change.

## License

This repository is licensed under the [GNU Affero General Public License v3.0](LICENSE).
