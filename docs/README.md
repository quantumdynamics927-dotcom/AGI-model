# AGI-model Documentation

This directory is the documentation hub for AGI-model. It now supports a repository positioned around hardware-calibrated promoter validation, IBM Quantum execution, audit-grade artifacts, and the broader quantum-inspired modeling stack.

## Start here

If you are new to the project, read these documents in order:

1. [Repository README](../README.md) — current project stage, calibration stance, quick start, and validation commands
2. [Architecture guide](architecture/README.md) — component map and system structure
3. [Development guide](development/README.md) — coding standards, testing, and workflow expectations

## Documentation map

| Document | When to use it |
| --- | --- |
| [Architecture](architecture/README.md) | Understand the high-level system design and component relationships |
| [API reference](api/README.md) | Review available interfaces and integration-facing details |
| [Deployment guide](deployment/README.md) | Run the project in local, staging, or production-style environments |
| [Development guide](development/README.md) | Follow coding, testing, and contribution expectations |
| [Environment contract](development/environment-contract.md) | Configure local, CI, and sibling Vault interoperability variables |
| [Security guide](security/README.md) | Review security controls, assumptions, and operational guidance |
| [Contributing guide](contributing/CONTRIBUTING.md) | Prepare pull requests and collaborate consistently |
| [Code of conduct](contributing/CODE_OF_CONDUCT.md) | Understand community participation expectations |
| [`../CALIBRATION_REPORT_v2.0.md`](../CALIBRATION_REPORT_v2.0.md) | Review the current hardware-calibrated promoter validation report |

## Practical validation workflow

Before making or reviewing changes, validate the local environment with the repository's existing commands:

```bash
make lint
make test
make check
```

If you have not installed the developer toolchain yet, run:

```bash
pip install -r requirements-dev.txt
```

## Common examples

### Train the model

```bash
python train_vae.py
```

### Run the lightweight model check

```bash
python test_model.py
```

### Launch the dashboard

```bash
streamlit run dashboards/quantum_consciousness_dashboard/app.py
```

### Explore downstream analysis

```bash
python quantum_calibration_framework.py
python latent_analysis.py
python quantum_consciousness_link.py
```

## Notes on scope

- The project is experimental and research-oriented.
- The current scientific label is **hardware-calibrated promoter validation v1**.
- The present calibration result is promising but sample-poor; replicate-aware expansion is the next milestone.
- NFT-related workflows are currently paused.
- Some documents describe broader TMT-OS concepts that complement, but do not replace, the practical quick-start guidance in the top-level README.

## Support

For documentation gaps or corrections, open a GitHub issue so the appropriate guide can be updated.
