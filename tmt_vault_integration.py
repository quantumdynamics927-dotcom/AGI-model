"""Backward-compatible wrapper for the canonical Vault integration module."""

from packages.agi_model_integrations.tmt_vault_integration import *  # noqa: F401,F403


def _wrapper_main() -> int:
    from packages.agi_model_integrations.tmt_vault_integration import main

    return main()


if __name__ == "__main__":
    raise SystemExit(_wrapper_main())
