# Quantum Consciousness VAE Documentation

This directory contains the supporting documentation for the Quantum Consciousness VAE repository. Use it as the navigation hub for architecture details, development workflows, deployment instructions, security guidance, and contribution standards.

## Start here

If you are new to the project, read these documents in order:

1. [Repository README](../README.md) — overview, quick start, examples, and validation commands
2. [Architecture guide](architecture/README.md) — component map and system structure
3. [Development guide](development/README.md) — coding standards, testing, and workflow expectations

## Documentation map

| Document | When to use it |
| --- | --- |
| [Architecture](architecture/README.md) | Understand the high-level system design and component relationships |
| [API reference](api/README.md) | Review available interfaces and integration-facing details |
| [Deployment guide](deployment/README.md) | Run the project in local, staging, or production-style environments |
| [Development guide](development/README.md) | Follow coding, testing, and contribution expectations |
| [Security guide](security/README.md) | Review security controls, assumptions, and operational guidance |
| [Contributing guide](contributing/CONTRIBUTING.md) | Prepare pull requests and collaborate consistently |
| [Code of conduct](contributing/CODE_OF_CONDUCT.md) | Understand community participation expectations |

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
python latent_analysis.py
python quantum_consciousness_link.py
```

## Notes on scope

- The project is experimental and research-oriented.
- NFT-related workflows are currently paused.
- Some documents describe broader TMT-OS concepts that complement, but do not replace, the practical quick-start guidance in the top-level README.

## License

This project is licensed under the MIT License. See the [LICENSE](../LICENSE) file for details.
