# Deploying AGI-model

This document covers the **currently active** deployment path: pushing
the interactive 13-node control surface to a Hugging Face Space from
GitHub Actions.

> **Out of scope (intentionally):** GitHub Container Registry pushes
> and the GHCR-based deploy pipeline (`deploy.yml`) are disabled. See
> the bottom of this doc for how to re-enable.

## TL;DR

Every push to `main` that touches `space_app.py`, `Dockerfile.space`,
or `requirements.txt` runs `sync-to-huggingface.yml`, which:

1. Runs the milestone 0 test suite (`tests/test_backend_aware_offset.py`).
2. Builds a Space-only bundle in `hf-deploy/`.
3. Pushes the bundle to `${HF_USER}/agi-model` on the Hub.

No manual step is needed once the secrets below are configured.

## Required GitHub repository secrets

| Secret | Purpose |
| --- | --- |
| `HF_TOKEN` | Hugging Face write token for the Space. |
| `HF_USER` | Hugging Face username that owns the Space. |
| `CODECOV_TOKEN` | Codecov upload token (non-blocking). |

Optional secrets:

| Secret | Purpose |
| --- | --- |
| `TMT_VAULT_TOKEN` | Used by the `vault-integration.yml` workflow for sibling-repo contract tests. |
| `OLLAMA_API_KEY` | Used by the manual `vault-agi-eval-smoke` job in `ci.yml`. |

See `SECRETS.md` for the full list and the rotation policy.

## First-time Space setup

1. Create the Space at <https://huggingface.co/new-space>:
   - **Owner:** your `HF_USER`
   - **Name:** `agi-model`
   - **SDK:** `Docker`
   - **Visibility:** public or private per your preference.
2. Add `HF_TOKEN` (write scope) and `HF_USER` to the GitHub repo
   secrets (Settings -> Secrets and variables -> Actions -> New
   repository secret).
3. Push to `main`. The `sync-to-huggingface.yml` workflow will pick
   up the change and deploy. The Space URL will be
   `https://huggingface.co/spaces/${HF_USER}/agi-model`.

## Local end-to-end test (before pushing)

```bash
# Build the Space image locally.
docker build -f Dockerfile.space -t agi-space:local .

# Run it on port 7860 (the default Gradio port).
docker run --rm -p 7860:7860 agi-space:local

# In another terminal, verify the Space responds.
curl -fsS http://localhost:7860/ | head -c 200
```

A successful run boots Gradio and returns the embedded HTML for the
13-node dashboard. The `--rm` flag means the container is removed
when you Ctrl-C it.

## Local backend-aware offset smoke (CI parity)

```bash
PYTHONPATH="$(pwd):$(pwd)/TMT-OS:$(pwd)/tmt-os-labs:$(pwd)/integrations:$(pwd)/agi_scripts:$(pwd)/agi_app:$(pwd)/agi_model:$(pwd)/quantum_observer" \
  python -m pytest tests/test_backend_aware_offset.py -v
```

11 tests should pass. The CLI smoke is:

```bash
python -m backend_aware_offset --report quantum_calibration_report.json
```

It prints a Markdown table with per-backend offsets. See
`docs/QUANTUM_AGI_ROADMAP.md` for what this table means scientifically.

## Local multi-container stack (compose)

The `docker-compose.yml` is **local-dev only**. It is not used for
production deploys. To run it:

```bash
cp .env.example .env  # fill in POSTGRES_PASSWORD at minimum
docker compose up -d

# Sanity-check the API.
curl -fsS http://localhost:8000/api/v1/system/health

# Open the dashboard.
open http://localhost:8501

# Stop everything.
docker compose down -v
```

For a development override that bind-mounts the source tree:

```bash
cp docker-compose.override.yml.example docker-compose.override.yml
docker compose up -d
```

## What gets tested before deploy

`ci.yml` runs on every push and PR to `main`:

- `test` — pytest with coverage on Python 3.10 + 3.11, Codecov upload.
- `backend-aware-offset` — runs only on main pushes; produces a
  Markdown + JSON artifact per batch.

`sync-to-huggingface.yml` runs the milestone 0 tests
(`tests/test_backend_aware_offset.py`) as a `test-before-sync` gate.
The Space is not pushed if that job fails.

## Rollback

The Space's git history on the Hub is the rollback surface. To roll
back to a previous commit:

```bash
# Locally
git clone https://huggingface.co/spaces/${HF_USER}/agi-model /tmp/agi-space
cd /tmp/agi-space
git log --oneline | head  # pick the SHA to roll back to
git revert --no-edit HEAD  # or reset --hard to a chosen SHA
git push
```

Alternatively, push a known-good commit from this repo to `main` and
let `sync-to-huggingface.yml` redeploy.

## Re-enabling the GHCR / docker-image deploy (not currently used)

`deploy.yml` is now a stub that fails on dispatch. To bring back the
GHCR-based pipeline:

1. Rewrite `.github/workflows/deploy.yml` to include the original
   `build-runtime` and `build-dashboard` jobs (the disabled stub has
   the original file's git history if needed).
2. Add a `GITHUB_TOKEN` secret with `packages: write` permission
   (this is automatic, but verify the repo's default token
   permissions include it under Settings -> Actions -> General).
3. Document the GHCR image URL in this file and update
   `docker-compose.yml` to pull from GHCR instead of building
   locally.

Until then, treat `deploy.yml` as a placeholder.

## See also

- `SECRETS.md` — what secrets go where, and which are deprecated.
- `SECURITY_HARDENING.md` — Docker and CI security policy.
- `docs/QUANTUM_AGI_ROADMAP.md` — the research roadmap (P0–P3).
- `README.md` — what the repo is and how to develop against it.
