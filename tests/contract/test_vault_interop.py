from __future__ import annotations

import sys
from pathlib import Path

from agi_model.validate_run import run_vae_smoke
from packages.agi_model_integrations import (
    VAULT_INTEROP_CONTRACT_VERSION,
    ensure_vault_repo_on_syspath,
    resolve_vault_repo_path,
    vault_interop_contract,
)


def test_vault_repo_resolution_prefers_supported_env_var(
    monkeypatch, tmp_path: Path
) -> None:
    vault_repo = tmp_path / "TMT_Quantum_Vault-"
    vault_repo.mkdir()
    monkeypatch.setenv("AGI_MODEL_VAULT_REPO", str(vault_repo))
    monkeypatch.delenv("TMT_QUANTUM_VAULT_REPO", raising=False)

    assert resolve_vault_repo_path() == vault_repo.resolve()


def test_ensure_vault_repo_on_syspath_adds_repo_once(
    monkeypatch, tmp_path: Path
) -> None:
    vault_repo = tmp_path / "TMT_Quantum_Vault-"
    vault_repo.mkdir()
    monkeypatch.setenv("AGI_MODEL_VAULT_REPO", str(vault_repo))
    monkeypatch.delenv("TMT_QUANTUM_VAULT_REPO", raising=False)

    resolved = ensure_vault_repo_on_syspath()

    assert resolved == vault_repo.resolve()
    assert sys.path.count(str(resolved)) == 1


def test_vault_interop_contract_is_versioned() -> None:
    contract = vault_interop_contract()

    assert contract["contract_version"] == VAULT_INTEROP_CONTRACT_VERSION
    assert "AGI_MODEL_VAULT_REPO" in contract["repo_env_vars"]
    assert contract["validate_module"] == "agi_model.validate_run"


def test_vae_smoke_contract_payload_is_structured() -> None:
    payload = run_vae_smoke(
        seed=7,
        batch_size=2,
        input_dim=128,
        latent_dim=32,
        include_advanced=False,
    )

    assert payload["operation"] == "vae-smoke"
    assert payload["contract_version"] == "1.0"
    assert isinstance(payload["metrics"]["total_loss"], float)
    assert payload["checks"]
