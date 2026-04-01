"""Integration-layer package namespace."""

from .tmt_vault_integration import (
    DEFAULT_VAULT_REPO_CANDIDATES,
    VAULT_INTEROP_CONTRACT_VERSION,
    VAULT_REPO_ENV_VARS,
    VaultCommandResult,
    VaultIntegrationError,
    VaultInteropConfig,
    ensure_vault_repo_on_syspath,
    resolve_vault_repo_path,
    resolve_vault_repo_path_or_fallback,
    vault_interop_contract,
)

__all__ = [
    "DEFAULT_VAULT_REPO_CANDIDATES",
    "VAULT_INTEROP_CONTRACT_VERSION",
    "VAULT_REPO_ENV_VARS",
    "VaultCommandResult",
    "VaultIntegrationError",
    "VaultInteropConfig",
    "ensure_vault_repo_on_syspath",
    "resolve_vault_repo_path",
    "resolve_vault_repo_path_or_fallback",
    "vault_interop_contract",
]
