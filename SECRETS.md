# Secrets and environment variables for AGI-model.
#
# This repo deploys to a Hugging Face Space and a (currently disabled)
# GitHub Container Registry pipeline. It also runs as a local multi-
# container stack via `docker-compose.yml`. Each surface has its own
# secret set; this file is the canonical list.
#
# NEVER commit a real `.env`. Use `.env.example` as a template and keep
# real values in:
#   - GitHub repository secrets (Settings -> Secrets and variables -> Actions)
#   - Hugging Face Space secrets (Space settings -> Variables and secrets)
#   - A local `.env` that is gitignored

## GitHub repository secrets (required for CI + deploy)

| Secret | Required by | Purpose |
| --- | --- | --- |
| `HF_TOKEN` | `sync-to-huggingface.yml` | Hugging Face write token used to push the Space. Must have `write` scope on the Space repo. |
| `HF_USER` | `sync-to-huggingface.yml` | Hugging Face username that owns the Space. The default Space name is `${HF_USER}/agi-model`. |
| `CODECOV_TOKEN` | `ci.yml` | Codecov upload token. Failing uploads are non-blocking (`fail_ci_if_error: false`). |
| `GITHUB_TOKEN` | (automatic) | Used for GHCR login in `deploy.yml.disabled`. Provided by Actions; no action needed. |
| `QISKIT_IBM_TOKEN` | `tests.yml` (legacy, off by default) | Optional. Only needed if you re-enable the IBM hardware integration tests. |

## Hugging Face Space secrets

Set in the Space's "Variables and secrets" tab.

| Secret | Required | Purpose |
| --- | --- | --- |
| `IBM_BACKEND` | optional | Default IBM Quantum backend (e.g. `ibm_fez`). Falls back to `ibmq_qasm_simulator` in `space_app.py`. |
| `QISKIT_IBM_TOKEN` | optional | If set, the Space can submit real hardware jobs. If unset, the Space runs against `qiskit_aer` only. |

## Local `.env` (compose / scripts)

`docker-compose.yml` reads these from the host environment; copy
`.env.example` to `.env` and fill in:

| Variable | Default | Purpose |
| --- | --- | --- |
| `POSTGRES_PASSWORD` | (required) | Postgres password for the `tmtos` user. |
| `JWT_SECRET` | (required for prod) | Secret used to sign API JWTs. |
| `GRAFANA_PASSWORD` | (required for prod) | Admin password for the local Grafana UI. |
| `QISKIT_IBM_TOKEN` | (optional) | Only needed for IBM Quantum jobs. |

## DEPRECATED — do not set

The following were used by the NFT / IPFS publishing pipeline, which has
been disabled (see `SECURITY_HARDENING.md` and the deletion of the
`ipfs_publish` job in `ci.yml`). Do **not** populate these on GitHub, on
the HF Space, or in `.env`:

- `PINATA_JWT`
- `PINATA_API_KEY`
- `PINATA_API_SECRET`
- `NFT_CONTRACT_ADDRESS`
- `SMTP_PASSWORD`
- `SLACK_WEBHOOK_URL`

## Rotation policy

- Rotate `HF_TOKEN` every 90 days or whenever a contributor with write
  access leaves the project.
- Rotate `POSTGRES_PASSWORD` on any local-data restore from backup.
- Never echo secrets in CI logs; all workflows use `${{ secrets.* }}`
  interpolation, never inline strings.

## Audit

To list every place a secret is referenced in this repo, run:

    rg -n 'secrets\.[A-Z_]+' .github/ docker-compose.yml Dockerfile*