# Development Guide

## Overview

This document captures the practical local-development workflow for AGI-model.

The repository is a mixed research workspace, so contributors should optimize for:

- reproducible Python environments,
- CI-parity test execution,
- targeted changes in the area being modified,
- documentation updates whenever workflows or repo structure change.

## Local environment setup

### Recommended

```bash
make setup
make env
```

### Manual

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip -r requirements.txt -r requirements-dev.txt
cp .env.example .env
```

## CI-parity test execution

The default CI workflow sets:

```bash
PYTHONPATH="$(pwd):$(pwd)/TMT-OS:$(pwd)/tmt-os-labs"
```

Mirror that locally when troubleshooting imports:

```bash
PYTHONPATH="$(pwd):$(pwd)/TMT-OS:$(pwd)/tmt-os-labs" pytest -q
```

## Standard commands

```bash
make lint
make test
make check
make dashboard
```

### What they do

- `make lint` runs `flake8` and `black --check`
- `make test` runs `pytest tests/ -v`
- `make check` chains lint, test, and security-scan targets
- `make dashboard` launches the Streamlit dashboard

## Development expectations

### Scope changes carefully

This repository contains research code, imported modules, and legacy subtrees. Prefer focused changes in the files directly related to the task instead of broad cleanup passes.

### Keep docs in sync

Update the README or docs pages whenever you change:

- setup steps,
- contributor workflows,
- Docker/runtime expectations,
- GitHub Actions behavior,
- repository metadata or supported deployment patterns.

### Validate what you change

Run the smallest existing validation that covers your change:

- docs and metadata changes: spot-check links and referenced commands
- workflow changes: review YAML carefully and validate related commands locally when possible
- Python changes: run the relevant tests plus any nearby smoke checks

## Repository conventions

- Use Python 3.10+.
- Prefer existing tooling already in the repo over adding new automation layers.
- Keep experimental deployment assumptions out of docs unless they are actually supported in-tree.
- Treat the repo as an experimental research platform, not a production service monolith.

## Pull requests

Before opening a PR:

1. run the relevant validation,
2. update documentation when workflows changed,
3. summarize any known unrelated failures separately from your change.
