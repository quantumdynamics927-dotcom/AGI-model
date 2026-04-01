# Environment contract

This repository now treats environment configuration as part of the supported
interop contract between local development, CI, and the sibling
`TMT_Quantum_Vault-` checkout.

## Supported environments

- local developer shell
- GitHub Actions CI
- optional sibling-repo integration with `TMT_Quantum_Vault-`
- optional container runtime

## Core variables

| Variable | Required | Purpose |
| --- | --- | --- |
| `PYTHONPATH` | CI/local parity | Include the repo root plus `TMT-OS`, `tmt-os-labs`, `integrations`, `agi_scripts`, `agi_app`, `agi_model`, and `quantum_observer` when running tests |
| `TMT_OS_ENV` | optional | Runtime mode such as `development`, `testing`, or `production` |
| `LOG_LEVEL` | optional | Logging verbosity override |

## Vault interoperability variables

| Variable | Required | Purpose |
| --- | --- | --- |
| `AGI_MODEL_VAULT_REPO` | preferred when using Vault | Absolute path to a sibling `TMT_Quantum_Vault-` checkout |
| `TMT_QUANTUM_VAULT_REPO` | supported alias | Backward-compatible Vault checkout path override |
| `TMT_QUANTUM_VAULT_PYTHON` | optional | Python interpreter to use when invoking the Vault CLI |
| `OLLAMA_API_KEY` | optional/secret | Required by cloud-mode Vault flows |

## Resolution order for the Vault repo

1. explicit function argument or CLI flag
2. `AGI_MODEL_VAULT_REPO`
3. `TMT_QUANTUM_VAULT_REPO`
4. sibling checkout discovery for `TMT_Quantum_Vault-` and `TMT_Quantum_Vault`

## Contracted commands

```bash
python -m agi_model.validate_run vae-smoke
python tmt_vault_integration.py resolve
python -m tmt_quantum_vault agi-validate --root "$AGI_MODEL_VAULT_REPO" --agi-root "$(pwd)" --operation vae-smoke --json
```
