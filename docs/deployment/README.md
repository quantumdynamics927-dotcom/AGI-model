# Deployment Guide

## Overview

This repository currently supports two maintained deployment-oriented paths:

1. **local Python execution** for training, testing, analysis, and API serving
2. **container image builds** for the runtime app and Streamlit dashboard

Infrastructure-specific staging and production rollout logic is intentionally not documented here unless it exists in this repository and is actively maintained.

## Supported deployment artifacts

### Runtime image

- **Definition:** `/Dockerfile`
- **Purpose:** run the main Python application in API serve mode
- **Default port:** `8000`

### Dashboard image

- **Definition:** `/Dockerfile.dashboard`
- **Purpose:** run the Streamlit dashboard
- **Default port:** `8501`

## Local runtime workflow

Use the Python environment directly when you want the most transparent local setup:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip -r requirements.txt -r requirements-dev.txt
python main.py --mode serve --host 0.0.0.0 --port 8000
```

## Local container workflow

### Build the images

```bash
docker build -t agi-model:local .
docker build -f Dockerfile.dashboard -t agi-model-dashboard:local .
```

### Run the images

```bash
docker run --rm -p 8000:8000 agi-model:local
docker run --rm -p 8501:8501 agi-model-dashboard:local
```

## GitHub Actions deployment automation

The repository's container workflow lives in:

- `.github/workflows/deploy.yml`

It is responsible for:

- validating that both Docker images build successfully,
- generating OCI metadata,
- publishing images to GitHub Container Registry on pushes to the main branches and when manually triggered via the workflow.

## Environment and secrets

### Local environment file

Create a local `.env` from the checked-in example:

```bash
cp .env.example .env
```

### Optional credentials

Some scripts may require credentials that are not needed for basic repo operation:

- IBM Quantum tokens
- blockchain/NFT deployment secrets
- external service API keys

Enable those only for the workflows that actually need them.

## Non-goals in this repository

The following are currently out of scope for the committed deployment docs:

- server SSH rollout instructions
- production blue/green cutover steps
- undocumented external hostnames
- infrastructure configs that are not present in-tree

If those capabilities become actively maintained here later, they should be documented alongside the actual IaC or runtime files that support them.
