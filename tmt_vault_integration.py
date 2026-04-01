"""Backward-compatible wrapper for the canonical Vault integration module."""

from packages.agi_model_integrations.tmt_vault_integration import *  # noqa: F401,F403


if __name__ == "__main__":
    from packages.agi_model_integrations.tmt_vault_integration import main

    raise SystemExit(main())
