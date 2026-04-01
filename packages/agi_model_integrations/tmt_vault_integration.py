"""Utilities for using TMT_Quantum_Vault as an external validation backend.

This module keeps the integration opt-in. It locates a sibling Vault checkout,
runs the Vault CLI via ``python -m tmt_quantum_vault``, and returns structured
results that AGI-model can record alongside checkpoints and experiment outputs.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

from ollama_cloud_models import (
    describe_ollama_operation_models,
    get_ollama_cloud_model,
)


DEFAULT_VAULT_REPO_CANDIDATES = (
    "TMT_Quantum_Vault-",
    "TMT_Quantum_Vault",
)
VAULT_REPO_ENV_VARS = (
    "AGI_MODEL_VAULT_REPO",
    "TMT_QUANTUM_VAULT_REPO",
)
VAULT_INTEROP_CONTRACT_VERSION = "1.0"
DEFAULT_VAE_SMOKE_ARTIFACT = "vae_smoke_result.json"
DEFAULT_VAE_INTERPRETATION_ARTIFACT = "vae_loss_interpretation.json"
DEFAULT_PHI_ANALYSIS_ARTIFACT = "phi_artifact_analysis.json"
DEFAULT_CI_AUDIT_ARTIFACT = "ci_audit_result.json"
DEFAULT_EVAL_CASE_GENERATION_ARTIFACT = "eval_case_generation.json"
DEFAULT_RESEARCH_LOOP_ARTIFACT = "research_loop_result.json"
DEFAULT_EVAL_DATASET_PATH = "tmp_vault_eval_dataset.json"


class VaultIntegrationError(RuntimeError):
    """Raised when the external Vault backend cannot be found or invoked."""


@dataclass(frozen=True)
class VaultInteropConfig:
    """Supported AGI ↔ Vault interoperability contract."""

    contract_version: str = VAULT_INTEROP_CONTRACT_VERSION
    repo_env_vars: tuple[str, ...] = VAULT_REPO_ENV_VARS
    repo_candidates: tuple[str, ...] = DEFAULT_VAULT_REPO_CANDIDATES
    validate_module: str = "agi_model.validate_run"
    validate_subcommand: str = "agi-validate"
    smoke_subcommand: str = "agi-eval-smoke"
    default_timeout_seconds: int = 300

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class VaultCommandResult:
    """Structured result for a Vault CLI invocation."""

    command: List[str]
    cwd: str
    returncode: int
    stdout: str
    stderr: str
    parsed_json: Optional[Any] = None

    @property
    def ok(self) -> bool:
        return self.returncode == 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "command": self.command,
            "cwd": self.cwd,
            "returncode": self.returncode,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "parsed_json": self.parsed_json,
            "ok": self.ok,
        }


def vault_interop_contract() -> Dict[str, Any]:
    """Return the stable interoperability contract for AGI-model ↔ Vault."""
    return VaultInteropConfig().to_dict()


def _candidate_repo_paths(anchor: Optional[Path] = None) -> Iterable[Path]:
    base = anchor or Path(__file__).resolve().parents[2]
    for env_name in VAULT_REPO_ENV_VARS:
        env_value = os.environ.get(env_name)
        if env_value:
            yield Path(env_value).expanduser().resolve()

    for name in DEFAULT_VAULT_REPO_CANDIDATES:
        yield (base / name).resolve()
        yield (base.parent / name).resolve()


def resolve_vault_repo_path(repo_path: Optional[str] = None) -> Path:
    """Resolve the local checkout path for TMT_Quantum_Vault."""
    if repo_path:
        resolved = Path(repo_path).expanduser().resolve()
        if not resolved.exists():
            raise VaultIntegrationError(
                f"Vault repo path does not exist: {resolved}"
            )
        return resolved

    for candidate in _candidate_repo_paths():
        if candidate.exists():
            return candidate

    raise VaultIntegrationError(
        "Could not locate TMT_Quantum_Vault. Set AGI_MODEL_VAULT_REPO or "
        "TMT_QUANTUM_VAULT_REPO, or clone the repo beside AGI-model."
    )


def ensure_vault_repo_on_syspath(repo_path: Optional[str] = None) -> Path:
    """Resolve the Vault checkout and prepend it to ``sys.path`` once."""
    resolved = resolve_vault_repo_path(repo_path)
    resolved_str = str(resolved)
    if resolved_str not in sys.path:
        sys.path.insert(0, resolved_str)
    return resolved


def build_vault_command(
    vault_python: Optional[str],
    subcommand: str,
    args: Sequence[str],
) -> List[str]:
    python_executable = (
        vault_python
        or os.environ.get("TMT_QUANTUM_VAULT_PYTHON")
        or sys.executable
    )
    return [python_executable, "-m", "tmt_quantum_vault", subcommand, *args]


def _run_vault_module_with_args_file(
    python_executable: str,
    cwd: Path,
    subcommand: str,
    args: Sequence[str],
    timeout: int,
) -> subprocess.CompletedProcess[str]:
    wrapper = (
        "import json, runpy, sys;"
        "import click.utils;"
        "from pathlib import Path;"
        "argv = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'));"
        "click.utils._expand_args = lambda args, **kwargs: list(args);"
        "sys.argv = ['tmt_quantum_vault', *argv];"
        "runpy.run_module('tmt_quantum_vault', run_name='__main__')"
    )
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        suffix=".json",
        delete=False,
    ) as handle:
        json.dump([subcommand, *args], handle)
        args_file = Path(handle.name)
    try:
        return subprocess.run(
            [python_executable, "-c", wrapper, str(args_file)],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    finally:
        try:
            args_file.unlink(missing_ok=True)
        except OSError:
            pass


def _extract_json_payload(text: str) -> Optional[Any]:
    stripped = text.strip()
    if not stripped:
        return None

    structured_candidates = [stripped]
    structured_candidates.extend(
        line.strip()
        for line in stripped.splitlines()
        if line.strip() and line.strip()[0] in "[{"
    )

    for candidate in reversed(structured_candidates):
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, (dict, list)):
                return parsed
        except json.JSONDecodeError:
            continue

    start_positions = [
        idx for idx, char in enumerate(stripped) if char in "[{"
    ]
    for start in reversed(start_positions):
        candidate = stripped[start:]
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, (dict, list)):
                return parsed
        except json.JSONDecodeError:
            continue

    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        return None


def run_vault_command(
    subcommand: str,
    args: Sequence[str],
    repo_path: Optional[str] = None,
    expect_json: bool = False,
    timeout: int = 300,
    vault_python: Optional[str] = None,
) -> VaultCommandResult:
    """Run a Vault CLI command from the resolved Vault checkout."""
    cwd = resolve_vault_repo_path(repo_path)
    command = build_vault_command(vault_python, subcommand, args)
    python_executable = command[0]
    completed = _run_vault_module_with_args_file(
        python_executable=python_executable,
        cwd=cwd,
        subcommand=subcommand,
        args=args,
        timeout=timeout,
    )

    parsed_json = (
        _extract_json_payload(completed.stdout) if expect_json else None
    )
    result = VaultCommandResult(
        command=command,
        cwd=str(cwd),
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        parsed_json=parsed_json,
    )
    if completed.returncode != 0:
        error_text = completed.stderr.strip() or completed.stdout.strip()
        raise VaultIntegrationError(
            f"Vault command failed ({subcommand}): {error_text}"
        )
    return result


def run_local_contract_command(args: Sequence[str]) -> dict[str, Any]:
    """Run the AGI deterministic contract and return parsed JSON."""
    command = [sys.executable, "-m", "agi_model.validate_run", *args]
    completed = subprocess.run(
        command,
        cwd=str(Path(__file__).resolve().parent),
        capture_output=True,
        text=True,
        check=False,
    )
    parsed_json = _extract_json_payload(completed.stdout)
    if completed.returncode != 0:
        error_text = completed.stderr.strip() or completed.stdout.strip()
        raise VaultIntegrationError(
            f"Local AGI contract failed ({' '.join(args)}): {error_text}"
        )
    if not isinstance(parsed_json, dict):
        raise VaultIntegrationError(
            f"Local AGI contract returned non-JSON output for {' '.join(args)}"
        )
    return parsed_json


def run_agent_task_prompt(
    prompt: str,
    repo_path: Optional[str] = None,
    mode: str = "cloud",
    model: Optional[str] = None,
    operation: str = "vae_checkpoint_validation",
    timeout: int = 300,
    raw_final_only: bool = True,
) -> VaultCommandResult:
    selected_model = get_ollama_cloud_model(operation, override=model)
    args = [prompt, "--mode", mode, "--model", selected_model, "--json"]
    if raw_final_only:
        args.append("--raw-final-only")
    return run_vault_command(
        "agent-task",
        args,
        repo_path=repo_path,
        expect_json=True,
        timeout=timeout,
    )


def summarise_training_metrics(training_summary: Dict[str, Any]) -> str:
    """Create a compact natural-language prompt from a training summary."""
    best = training_summary.get("best_checkpoint", {})
    metrics = best.get("val_losses", {})
    learning_rate = best.get("learning_rate")
    parts = [
        f"epoch={best.get('epoch', 'unknown')}",
        f"total_loss={metrics.get('total', 'n/a')}",
        f"recon={metrics.get('recon', 'n/a')}",
        f"kl={metrics.get('kl', 'n/a')}",
        f"coherence={metrics.get('coherence', 'n/a')}",
        f"fidelity={metrics.get('fidelity', 'n/a')}",
        f"entropy={metrics.get('entropy', 'n/a')}",
    ]
    if learning_rate is not None:
        parts.append(f"lr={learning_rate}")

    consciousness = best.get("consciousness_metrics", {})
    if consciousness:
        parts.append(
            "lz_reconstructed="
            f"{consciousness.get('lz_reconstructed', 'n/a')}"
        )
        parts.append(
            "pci_reconstructed="
            f"{consciousness.get('pci_reconstructed', 'n/a')}"
        )

    return ", ".join(str(part) for part in parts)


def build_training_validation_prompt(
    training_summary: Dict[str, Any],
    checkpoint_path: Optional[str] = None,
    extra_context: Optional[str] = None,
) -> str:
    summary_line = summarise_training_metrics(training_summary)
    checkpoint_part = (
        f"Checkpoint: {checkpoint_path}. " if checkpoint_path else ""
    )
    context_part = (
        f" Additional context: {extra_context}" if extra_context else ""
    )
    return (
        "Analyze this AGI-model Quantum VAE training run and determine "
        "whether the checkpoint "
        "looks healthy enough to promote. "
        f"{checkpoint_part}Metrics: {summary_line}. "
        "Return a concise structured assessment with pass/fail reasoning "
        "for fidelity, stability, "
        f"and reconstruction quality.{context_part}"
    )


def run_agent_task_validation(
    training_summary: Dict[str, Any],
    checkpoint_path: Optional[str] = None,
    repo_path: Optional[str] = None,
    mode: str = "cloud",
    extra_context: Optional[str] = None,
    model: Optional[str] = None,
    timeout: int = 300,
) -> VaultCommandResult:
    prompt = build_training_validation_prompt(
        training_summary,
        checkpoint_path,
        extra_context,
    )
    return run_agent_task_prompt(
        prompt,
        repo_path=repo_path,
        mode=mode,
        model=model,
        operation="vae_checkpoint_validation",
        timeout=timeout,
    )


def build_vae_interpretation_prompt(contract_payload: Dict[str, Any]) -> str:
    return (
        "Given this AGI-model VAE contract output, explain what the KL, "
        "Hamming, and mixed-state loss values suggest about the quantum-DNA "
        "encoding quality, and recommend one training adjustment. Return JSON "
        "with keys: analysis, recommendation, risk_level, supporting_metrics.\n\n"
        f"Contract JSON:\n{json.dumps(contract_payload, indent=2)}"
    )


def load_contract_artifact(artifact_path: str) -> Dict[str, Any]:
    resolved_artifact = Path(artifact_path).resolve()
    payload = json.loads(resolved_artifact.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise VaultIntegrationError(
            f"Expected JSON object in contract artifact: {resolved_artifact}"
        )
    return payload


def load_json_artifact(artifact_path: str) -> Any:
    resolved_artifact = Path(artifact_path).resolve()
    return json.loads(resolved_artifact.read_text(encoding="utf-8"))


def persist_json_artifact(payload: Dict[str, Any], output_path: str) -> Path:
    resolved_output = Path(output_path).resolve()
    resolved_output.write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )
    return resolved_output


def _summarize_dataset_for_prompt(dataset: Dict[str, Any]) -> Dict[str, Any]:
    cases = dataset.get("cases", []) if isinstance(dataset, dict) else []
    sample_cases = []
    for case in cases[:3]:
        if isinstance(case, dict):
            sample_cases.append(
                {
                    "id": case.get("id"),
                    "prompt_preview": str(case.get("prompt", ""))[:180],
                    "expectation": case.get("expectation", {}),
                }
            )
    return {
        "name": dataset.get("name") if isinstance(dataset, dict) else None,
        "description": (
            dataset.get("description") if isinstance(dataset, dict) else None
        ),
        "case_count": len(cases),
        "sample_cases": sample_cases,
    }


def _extract_final_stage_output(payload: Dict[str, Any]) -> Any:
    if not isinstance(payload, dict):
        return payload
    final_output = payload.get("final_output")
    if isinstance(final_output, str):
        try:
            return json.loads(final_output)
        except json.JSONDecodeError:
            return final_output
    return final_output


def _summarize_vae_analysis_for_audit(payload: Dict[str, Any]) -> Dict[str, Any]:
    contract = payload.get("contract", {}) if isinstance(payload, dict) else {}
    metrics = contract.get("metrics", {}) if isinstance(contract, dict) else {}
    analysis = payload.get("analysis", {}) if isinstance(payload, dict) else {}
    return {
        "contract_path": payload.get("contract_path"),
        "total_loss": metrics.get("loss_total") or metrics.get("total_loss"),
        "reconstruction_mae": metrics.get("reconstruction_mae"),
        "loss_kl": metrics.get("loss_kl"),
        "loss_hamming": metrics.get("loss_hamming"),
        "loss_mixed_state": metrics.get("loss_mixed_state"),
        "final_stage_output": _extract_final_stage_output(analysis),
    }


def _summarize_phi_analysis_for_audit(payload: Dict[str, Any]) -> Dict[str, Any]:
    contract = payload.get("contract", {}) if isinstance(payload, dict) else {}
    metrics = contract.get("metrics", {}) if isinstance(contract, dict) else {}
    details = contract.get("details", {}) if isinstance(contract, dict) else {}
    analysis = payload.get("analysis", {}) if isinstance(payload, dict) else {}
    return {
        "artifact_path": payload.get("artifact_path"),
        "artifact_type": details.get("artifact_type"),
        "phi_value": metrics.get("phi_value"),
        "phi_alignment_score": metrics.get("phi_alignment_score"),
        "consciousness_level": metrics.get("consciousness_level"),
        "integrated_information": metrics.get("integrated_information"),
        "ghz_mass_delta_control_to_moderate": metrics.get(
            "ghz_mass_delta_control_to_moderate"
        ),
        "entropy_delta_control_to_moderate": metrics.get(
            "entropy_delta_control_to_moderate"
        ),
        "backend_gap_marrakesh_minus_fez": metrics.get(
            "backend_gap_marrakesh_minus_fez"
        ),
        "final_stage_output": _extract_final_stage_output(analysis),
    }


def _validate_eval_case(case: Any, index: int) -> Dict[str, Any]:
    if not isinstance(case, dict):
        raise VaultIntegrationError(f"Generated case {index} is not an object")
    for field in ("id", "prompt", "expectation"):
        if field not in case:
            raise VaultIntegrationError(
                f"Generated case {index} is missing required field: {field}"
            )
    expectation = case.get("expectation")
    if not isinstance(expectation, dict):
        raise VaultIntegrationError(
            f"Generated case {index} expectation must be an object"
        )
    for field in ("contains_all", "contains_any", "excludes"):
        if field not in expectation:
            raise VaultIntegrationError(
                f"Generated case {index} expectation missing: {field}"
            )
        if not isinstance(expectation[field], list):
            raise VaultIntegrationError(
                f"Generated case {index} expectation field {field} must be a list"
            )
    return case


def merge_eval_cases_into_dataset(
    generated_cases: List[Dict[str, Any]],
    dataset_path: str,
) -> Dict[str, Any]:
    resolved_dataset = Path(dataset_path).resolve()
    if resolved_dataset.exists():
        dataset = load_json_artifact(str(resolved_dataset))
    else:
        dataset = {
            "name": "agi-model-artifacts",
            "description": (
                "AGI-model artifact-derived regression and research "
                "evaluation set."
            ),
            "cases": [],
        }
    if not isinstance(dataset, dict):
        raise VaultIntegrationError("Existing eval dataset must be a JSON object")
    existing_cases = dataset.get("cases", [])
    if not isinstance(existing_cases, list):
        raise VaultIntegrationError("Existing eval dataset cases must be a list")

    merged_cases: Dict[str, Dict[str, Any]] = {}
    for index, case in enumerate(existing_cases):
        validated_case = _validate_eval_case(case, index)
        merged_cases[str(validated_case["id"])] = validated_case
    for index, case in enumerate(generated_cases):
        validated_case = _validate_eval_case(case, index)
        merged_cases[str(validated_case["id"])] = validated_case

    dataset["cases"] = list(merged_cases.values())
    resolved_dataset.write_text(json.dumps(dataset, indent=2), encoding="utf-8")
    return {
        "dataset_path": str(resolved_dataset),
        "total_cases": len(dataset["cases"]),
        "generated_case_ids": [case["id"] for case in generated_cases],
    }


def run_vae_loss_interpreter(
    artifact_path: Optional[str] = None,
    contract_output_path: str = DEFAULT_VAE_SMOKE_ARTIFACT,
    analysis_output_path: str = DEFAULT_VAE_INTERPRETATION_ARTIFACT,
    repo_path: Optional[str] = None,
    mode: str = "cloud",
    model: Optional[str] = None,
    seed: int = 7,
    batch_size: int = 8,
    input_dim: int = 128,
    latent_dim: int = 32,
    include_advanced: bool = False,
    timeout: int = 300,
) -> VaultCommandResult:
    if artifact_path:
        contract_payload = load_contract_artifact(artifact_path)
        persisted_contract_path = Path(artifact_path).resolve()
    else:
        contract_payload = run_local_contract_command(
            [
                "vae-smoke",
                "--seed",
                str(seed),
                "--batch-size",
                str(batch_size),
                "--input-dim",
                str(input_dim),
                "--latent-dim",
                str(latent_dim),
                *(["--include-advanced"] if include_advanced else []),
            ]
        )
        persisted_contract_path = persist_json_artifact(
            contract_payload,
            contract_output_path,
        )
    prompt = build_vae_interpretation_prompt(contract_payload)
    result = run_agent_task_prompt(
        prompt,
        repo_path=repo_path,
        mode=mode,
        model=model,
        operation="vae_loss_interpretation",
        timeout=timeout,
    )
    analysis_payload = {
        "contract_path": str(persisted_contract_path),
        "contract": contract_payload,
        "analysis": result.parsed_json,
    }
    persisted_analysis_path = persist_json_artifact(
        analysis_payload,
        analysis_output_path,
    )
    result.parsed_json = {
        **analysis_payload,
        "analysis_path": str(persisted_analysis_path),
    }
    return result


def build_phi_artifact_prompt(
    artifact_path: Path,
    contract_payload: Dict[str, Any],
) -> str:
    metrics = contract_payload.get("metrics", {})
    details = contract_payload.get("details", {})
    artifact_type = details.get("artifact_type")
    if artifact_type == "ibm-decoherence-analysis":
        return (
            "Given this AGI-model IBM decoherence artifact summary, interpret "
            "the collapse kinetics across control, mild, and moderate pulse "
            "variants. Focus on whether GHZ mass and entropy trends indicate "
            "observable decoherence, whether backend differences dominate the "
            "signal, and what the next experiment should be. Return JSON with "
            "keys: analysis, collapse_kinetics, next_experiment, confidence, "
            "cited_metrics.\n\n"
            f"Artifact: {artifact_path.name}\n"
            f"Summary JSON:\n{json.dumps(contract_payload, indent=2)}\n\n"
            "Primary metrics: "
            f"control_avg_ghz_mass={metrics.get('control_avg_ghz_mass')}, "
            f"moderate_avg_ghz_mass={metrics.get('moderate_avg_ghz_mass')}, "
            "ghz_mass_delta_control_to_moderate="
            f"{metrics.get('ghz_mass_delta_control_to_moderate')}, "
            f"control_avg_entropy={metrics.get('control_avg_entropy')}, "
            f"moderate_avg_entropy={metrics.get('moderate_avg_entropy')}, "
            "entropy_delta_control_to_moderate="
            f"{metrics.get('entropy_delta_control_to_moderate')}, "
            "backend_gap_marrakesh_minus_fez="
            f"{metrics.get('backend_gap_marrakesh_minus_fez')}, "
            f"interpretation={details.get('interpretation')}"
        )
    return (
        "Given this AGI-model phi artifact summary, interpret what the phi "
        "and integrated-information values imply for the IIT consciousness "
        "model, then suggest the next experiment. Return JSON with keys: "
        "analysis, next_experiment, confidence, cited_metrics.\n\n"
        f"Artifact: {artifact_path.name}\n"
        f"Summary JSON:\n{json.dumps(contract_payload, indent=2)}\n\n"
        f"Primary metrics: phi_value={metrics.get('phi_value')}, "
        f"phi_alignment_score={metrics.get('phi_alignment_score')}, "
        f"consciousness_level={metrics.get('consciousness_level')}, "
        f"integrated_information={metrics.get('integrated_information')}, "
        f"is_conscious={details.get('is_conscious')}"
    )


def run_phi_artifact_analyst(
    artifact_path: str,
    analysis_output_path: str = DEFAULT_PHI_ANALYSIS_ARTIFACT,
    repo_path: Optional[str] = None,
    mode: str = "cloud",
    model: Optional[str] = None,
    timeout: int = 300,
) -> VaultCommandResult:
    resolved_artifact = Path(artifact_path).resolve()
    contract_payload = run_local_contract_command(
        ["artifact-summary", "--artifact", str(resolved_artifact)]
    )
    prompt = build_phi_artifact_prompt(resolved_artifact, contract_payload)
    result = run_agent_task_prompt(
        prompt,
        repo_path=repo_path,
        mode=mode,
        model=model,
        operation="phi_artifact_analysis",
        timeout=timeout,
    )
    analysis_payload = {
        "artifact_path": str(resolved_artifact),
        "contract": contract_payload,
        "analysis": result.parsed_json,
    }
    persisted_analysis_path = persist_json_artifact(
        analysis_payload,
        analysis_output_path,
    )
    result.parsed_json = {
        **analysis_payload,
        "analysis_path": str(persisted_analysis_path),
    }
    return result


def build_ci_audit_prompt(
    smoke_payload: Dict[str, Any],
    vae_analysis_payload: Dict[str, Any],
    phi_analysis_payload: Dict[str, Any],
) -> str:
    smoke_metrics = smoke_payload.get("metrics", {})
    smoke_summary = {
        "passed": smoke_payload.get("passed"),
        "total_loss": smoke_metrics.get("loss_total") or smoke_metrics.get("total_loss"),
        "reconstruction_mae": smoke_metrics.get("reconstruction_mae"),
        "loss_kl": smoke_metrics.get("loss_kl"),
        "loss_hamming": smoke_metrics.get("loss_hamming"),
        "loss_mixed_state": smoke_metrics.get("loss_mixed_state"),
        "checks": smoke_payload.get("checks"),
    }
    vae_summary = _summarize_vae_analysis_for_audit(vae_analysis_payload)
    phi_summary = _summarize_phi_analysis_for_audit(phi_analysis_payload)
    return (
        "Act as the AGI-model CI audit oracle. Review the VAE smoke contract, "
        "the VAE loss interpretation, and the phi artifact analysis. Return JSON "
        "with keys: status, notes, blocking_issues, suggested_next_step, "
        "confidence, cited_artifacts. Status must be one of ok, review, fail.\n\n"
        f"VAE smoke summary:\n{json.dumps(smoke_summary, indent=2)}\n\n"
        f"VAE interpretation summary:\n{json.dumps(vae_summary, indent=2)}\n\n"
        f"Phi analysis summary:\n{json.dumps(phi_summary, indent=2)}"
    )


def run_ci_audit_oracle(
    smoke_artifact_path: str = DEFAULT_VAE_SMOKE_ARTIFACT,
    vae_analysis_artifact_path: str = DEFAULT_VAE_INTERPRETATION_ARTIFACT,
    phi_analysis_artifact_path: str = DEFAULT_PHI_ANALYSIS_ARTIFACT,
    analysis_output_path: str = DEFAULT_CI_AUDIT_ARTIFACT,
    repo_path: Optional[str] = None,
    mode: str = "cloud",
    model: Optional[str] = None,
    timeout: int = 300,
) -> VaultCommandResult:
    smoke_payload = load_contract_artifact(smoke_artifact_path)
    vae_analysis_payload = load_contract_artifact(vae_analysis_artifact_path)
    phi_analysis_payload = load_contract_artifact(phi_analysis_artifact_path)
    prompt = build_ci_audit_prompt(
        smoke_payload,
        vae_analysis_payload,
        phi_analysis_payload,
    )
    result = run_agent_task_prompt(
        prompt,
        repo_path=repo_path,
        mode=mode,
        model=model,
        operation="ci_audit_oracle",
        timeout=timeout,
    )
    audit_payload = {
        "smoke_artifact_path": str(Path(smoke_artifact_path).resolve()),
        "vae_analysis_artifact_path": str(
            Path(vae_analysis_artifact_path).resolve()
        ),
        "phi_analysis_artifact_path": str(
            Path(phi_analysis_artifact_path).resolve()
        ),
        "audit": result.parsed_json,
    }
    persisted_audit_path = persist_json_artifact(
        audit_payload,
        analysis_output_path,
    )
    result.parsed_json = {
        **audit_payload,
        "analysis_path": str(persisted_audit_path),
    }
    return result


def build_eval_case_generation_prompt(
    seed_payload: Dict[str, Any],
    dataset_summary: Dict[str, Any],
    count: int,
) -> str:
    return (
        "Generate additional AGI-model Vault eval cases. Return JSON with a "
        "single key `cases`, whose value is a list of exactly "
        f"{count} objects. Each case must follow this schema: "
        "{id, prompt, expectation:{contains_all, contains_any, excludes}}. "
        "Focus on boundary and edge cases such as near-zero phi, degenerate "
        "latent space, mismatched DNA source, unstable integrated information, "
        "and low-coherence quantum outputs. Avoid duplicate ids and avoid code "
        "fences in the expected responses.\n\n"
        f"Seed artifact JSON:\n{json.dumps(seed_payload, indent=2)}\n\n"
        f"Existing dataset summary:\n{json.dumps(dataset_summary, indent=2)}"
    )


def run_eval_case_generation(
    seed_artifact_path: str,
    count: int,
    dataset_path: str = DEFAULT_EVAL_DATASET_PATH,
    analysis_output_path: str = DEFAULT_EVAL_CASE_GENERATION_ARTIFACT,
    repo_path: Optional[str] = None,
    mode: str = "cloud",
    model: Optional[str] = None,
    timeout: int = 300,
) -> VaultCommandResult:
    seed_payload = load_contract_artifact(seed_artifact_path)
    resolved_dataset_path = Path(dataset_path).resolve()
    if resolved_dataset_path.exists():
        dataset_payload = load_contract_artifact(str(resolved_dataset_path))
    else:
        dataset_payload = {
            "name": "agi-model-artifacts",
            "description": (
                "AGI-model artifact-derived regression and research "
                "evaluation set."
            ),
            "cases": [],
        }
    dataset_summary = _summarize_dataset_for_prompt(dataset_payload)
    prompt = build_eval_case_generation_prompt(
        seed_payload,
        dataset_summary,
        count,
    )
    result = run_agent_task_prompt(
        prompt,
        repo_path=repo_path,
        mode=mode,
        model=model,
        operation="eval_case_generation",
        timeout=timeout,
    )
    generated_payload = result.parsed_json
    if not isinstance(generated_payload, dict):
        raise VaultIntegrationError("Generated eval cases payload must be an object")
    generated_cases = generated_payload.get("cases")
    if not isinstance(generated_cases, list):
        raise VaultIntegrationError("Generated eval cases payload must include a cases list")
    if len(generated_cases) != count:
        raise VaultIntegrationError(
            f"Expected {count} generated cases, received {len(generated_cases)}"
        )
    merge_summary = merge_eval_cases_into_dataset(generated_cases, dataset_path)
    generation_payload = {
        "seed_artifact_path": str(Path(seed_artifact_path).resolve()),
        "requested_count": count,
        "generated_cases": generated_cases,
        "merge_summary": merge_summary,
    }
    persisted_generation_path = persist_json_artifact(
        generation_payload,
        analysis_output_path,
    )
    result.parsed_json = {
        **generation_payload,
        "analysis_path": str(persisted_generation_path),
    }
    return result


def run_research_loop(
    phi_artifact_path: str,
    smoke_artifact_path: Optional[str] = None,
    contract_output_path: str = DEFAULT_VAE_SMOKE_ARTIFACT,
    vae_analysis_output_path: str = DEFAULT_VAE_INTERPRETATION_ARTIFACT,
    phi_analysis_output_path: str = DEFAULT_PHI_ANALYSIS_ARTIFACT,
    ci_audit_output_path: str = DEFAULT_CI_AUDIT_ARTIFACT,
    loop_output_path: str = DEFAULT_RESEARCH_LOOP_ARTIFACT,
    repo_path: Optional[str] = None,
    mode: str = "cloud",
    model: Optional[str] = None,
) -> Dict[str, Any]:
    vae_result = run_vae_loss_interpreter(
        artifact_path=smoke_artifact_path,
        contract_output_path=contract_output_path,
        analysis_output_path=vae_analysis_output_path,
        repo_path=repo_path,
        mode=mode,
        model=model,
    )
    vae_payload = (
        vae_result.parsed_json
        if isinstance(vae_result.parsed_json, dict)
        else {}
    )
    phi_result = run_phi_artifact_analyst(
        phi_artifact_path,
        analysis_output_path=phi_analysis_output_path,
        repo_path=repo_path,
        mode=mode,
        model=model,
    )
    audit_result = run_ci_audit_oracle(
        smoke_artifact_path=contract_output_path,
        vae_analysis_artifact_path=vae_analysis_output_path,
        phi_analysis_artifact_path=phi_analysis_output_path,
        analysis_output_path=ci_audit_output_path,
        repo_path=repo_path,
        mode=mode,
        model=model,
    )
    loop_payload = {
        "mode": mode,
        "phi_artifact_path": str(Path(phi_artifact_path).resolve()),
        "vae_contract_artifact": str(
            Path(vae_payload.get("contract_path", contract_output_path)).resolve()
        ),
        "vae_analysis_artifact": str(Path(vae_analysis_output_path).resolve()),
        "phi_analysis_artifact": str(Path(phi_analysis_output_path).resolve()),
        "ci_audit_artifact": str(Path(ci_audit_output_path).resolve()),
        "steps": {
            "vae_interpretation": vae_result.parsed_json,
            "phi_analysis": phi_result.parsed_json,
            "ci_audit": audit_result.parsed_json,
        },
    }
    persisted_loop_path = persist_json_artifact(loop_payload, loop_output_path)
    return {
        **loop_payload,
        "loop_output_path": str(persisted_loop_path),
    }


def run_release_evidence(
    output_dir: str,
    model: Optional[str] = None,
    repo_path: Optional[str] = None,
    timeout: int = 600,
) -> VaultCommandResult:
    selected_model = get_ollama_cloud_model(
        "research_report_generation",
        override=model,
    )
    args = ["--output-dir", output_dir, "--json", "--model", selected_model]
    return run_vault_command(
        "release-evidence",
        args,
        repo_path=repo_path,
        expect_json=True,
        timeout=timeout,
    )


def run_release_gate(
    bundle_dir: str,
    repo_path: Optional[str] = None,
    require_comparison: bool = True,
    timeout: int = 600,
) -> VaultCommandResult:
    args = ["--bundle", bundle_dir, "--json"]
    if require_comparison:
        args.append("--require-comparison")
    return run_vault_command(
        "release-gate",
        args,
        repo_path=repo_path,
        expect_json=True,
        timeout=timeout,
    )


def run_eval_dataset(
    dataset_path: str,
    repo_path: Optional[str] = None,
    mode: str = "cloud",
    timeout: int = 600,
) -> VaultCommandResult:
    return run_vault_command(
        "eval",
        ["--dataset", dataset_path, "--mode", mode, "--json"],
        repo_path=repo_path,
        expect_json=True,
        timeout=timeout,
    )


def run_raw_payload(
    payload_path: str,
    repo_path: Optional[str] = None,
    mode: str = "cloud",
    raw_final_only: bool = True,
    timeout: int = 300,
) -> VaultCommandResult:
    payload = Path(payload_path).read_text(encoding="utf-8")
    args = [payload, "--mode", mode]
    if raw_final_only:
        args.append("--raw-final-only")
    return run_vault_command(
        "run",
        args,
        repo_path=repo_path,
        expect_json=False,
        timeout=timeout,
    )


def _cli() -> int:
    parser = argparse.ArgumentParser(
        description="AGI-model helper for TMT Quantum Vault integration"
    )
    parser.add_argument(
        "action",
        choices=[
            "resolve",
            "models",
            "agent-task",
            "vae-interpret",
            "vae-loss-interpretation",
            "phi-analyst",
            "phi-artifact-analysis",
            "ci-audit-oracle",
            "eval-case-generation",
            "research-loop",
            "eval",
            "run",
            "release-evidence",
            "release-gate",
        ],
    )
    parser.add_argument(
        "--repo",
        help="Explicit path to the TMT_Quantum_Vault checkout",
    )
    parser.add_argument(
        "--summary",
        help="Training summary JSON file for agent-task",
    )
    parser.add_argument(
        "--checkpoint",
        help="Checkpoint path for agent-task context",
    )
    parser.add_argument("--dataset", help="Dataset file for eval")
    parser.add_argument("--payload", help="Raw JSON payload file for run")
    parser.add_argument("--mode", default="cloud", help="Vault execution mode")
    parser.add_argument("--output-dir", help="Evidence output directory")
    parser.add_argument("--bundle", help="Release gate bundle directory")
    parser.add_argument(
        "--model",
        help="Explicit Ollama model override for supported cloud operations",
    )
    parser.add_argument(
        "--artifact",
        help="Artifact path for phi-analyst or local summary workflows",
    )
    parser.add_argument(
        "--seed-artifact",
        help="Seed artifact path for eval-case-generation",
    )
    parser.add_argument(
        "--smoke-artifact",
        default=DEFAULT_VAE_SMOKE_ARTIFACT,
        help="Artifact path for a saved vae-smoke contract",
    )
    parser.add_argument(
        "--vae-analysis-artifact",
        default=DEFAULT_VAE_INTERPRETATION_ARTIFACT,
        help="Artifact path for saved VAE interpretation JSON",
    )
    parser.add_argument(
        "--phi-analysis-artifact",
        default=DEFAULT_PHI_ANALYSIS_ARTIFACT,
        help="Artifact path for saved phi analysis JSON",
    )
    parser.add_argument(
        "--contract-output",
        default=DEFAULT_VAE_SMOKE_ARTIFACT,
        help="Output path for auto-persisted vae-smoke JSON artifacts",
    )
    parser.add_argument(
        "--analysis-output",
        default=None,
        help="Output path for persisted cloud-analysis JSON artifacts",
    )
    parser.add_argument(
        "--loop-output",
        default=DEFAULT_RESEARCH_LOOP_ARTIFACT,
        help="Output path for the one-shot research loop manifest JSON",
    )
    parser.add_argument(
        "--extra-context",
        help="Extra prompt context for agent-task",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="Number of new eval cases to generate",
    )
    parser.add_argument("--seed", type=int, default=7, help="Seed for vae-interpret")
    parser.add_argument(
        "--batch-size",
        type=int,
        default=8,
        help="Batch size for vae-interpret contract generation",
    )
    parser.add_argument(
        "--input-dim",
        type=int,
        default=128,
        help="Input dimension for vae-interpret contract generation",
    )
    parser.add_argument(
        "--latent-dim",
        type=int,
        default=32,
        help="Latent dimension for vae-interpret contract generation",
    )
    parser.add_argument(
        "--include-advanced",
        action="store_true",
        help="Include advanced loss terms when generating vae-smoke input",
    )
    args = parser.parse_args()

    try:
        if args.action == "resolve":
            print(resolve_vault_repo_path(args.repo))
            return 0

        if args.action == "models":
            print(json.dumps(describe_ollama_operation_models(), indent=2))
            return 0

        if args.action == "agent-task":
            if not args.summary:
                raise VaultIntegrationError(
                    "--summary is required for agent-task"
                )
            summary = json.loads(
                Path(args.summary).read_text(encoding="utf-8")
            )
            result = run_agent_task_validation(
                summary,
                checkpoint_path=args.checkpoint,
                repo_path=args.repo,
                mode=args.mode,
                extra_context=args.extra_context,
                model=args.model,
            )
            print(json.dumps(result.to_dict(), indent=2))
            return 0

        if args.action in {"vae-interpret", "vae-loss-interpretation"}:
            result = run_vae_loss_interpreter(
                artifact_path=args.artifact,
                contract_output_path=args.contract_output,
                analysis_output_path=(
                    args.analysis_output
                    or DEFAULT_VAE_INTERPRETATION_ARTIFACT
                ),
                repo_path=args.repo,
                mode=args.mode,
                model=args.model,
                seed=args.seed,
                batch_size=args.batch_size,
                input_dim=args.input_dim,
                latent_dim=args.latent_dim,
                include_advanced=args.include_advanced,
            )
            print(json.dumps(result.to_dict(), indent=2))
            return 0

        if args.action == "ci-audit-oracle":
            result = run_ci_audit_oracle(
                smoke_artifact_path=args.smoke_artifact,
                vae_analysis_artifact_path=args.vae_analysis_artifact,
                phi_analysis_artifact_path=args.phi_analysis_artifact,
                analysis_output_path=(
                    args.analysis_output or DEFAULT_CI_AUDIT_ARTIFACT
                ),
                repo_path=args.repo,
                mode=args.mode,
                model=args.model,
            )
            print(json.dumps(result.to_dict(), indent=2))
            return 0

        if args.action == "eval-case-generation":
            if not args.seed_artifact:
                raise VaultIntegrationError(
                    "--seed-artifact is required for eval-case-generation"
                )
            result = run_eval_case_generation(
                seed_artifact_path=args.seed_artifact,
                count=args.count,
                dataset_path=(args.dataset or DEFAULT_EVAL_DATASET_PATH),
                analysis_output_path=(
                    args.analysis_output
                    or DEFAULT_EVAL_CASE_GENERATION_ARTIFACT
                ),
                repo_path=args.repo,
                mode=args.mode,
                model=args.model,
            )
            print(json.dumps(result.to_dict(), indent=2))
            return 0

        if args.action == "research-loop":
            if not args.artifact:
                raise VaultIntegrationError(
                    "--artifact is required for research-loop"
                )
            loop_result = run_research_loop(
                phi_artifact_path=args.artifact,
                smoke_artifact_path=args.smoke_artifact,
                contract_output_path=args.contract_output,
                vae_analysis_output_path=args.vae_analysis_artifact,
                phi_analysis_output_path=args.phi_analysis_artifact,
                ci_audit_output_path=(
                    args.analysis_output or DEFAULT_CI_AUDIT_ARTIFACT
                ),
                loop_output_path=args.loop_output,
                repo_path=args.repo,
                mode=args.mode,
                model=args.model,
            )
            print(json.dumps(loop_result, indent=2))
            return 0

        if args.action in {"phi-analyst", "phi-artifact-analysis"}:
            if not args.artifact:
                raise VaultIntegrationError(
                    "--artifact is required for phi-artifact-analysis"
                )
            result = run_phi_artifact_analyst(
                args.artifact,
                analysis_output_path=(
                    args.analysis_output
                    or DEFAULT_PHI_ANALYSIS_ARTIFACT
                ),
                repo_path=args.repo,
                mode=args.mode,
                model=args.model,
            )
            print(json.dumps(result.to_dict(), indent=2))
            return 0

        if args.action == "eval":
            if not args.dataset:
                raise VaultIntegrationError("--dataset is required for eval")
            result = run_eval_dataset(
                args.dataset,
                repo_path=args.repo,
                mode=args.mode,
            )
            print(json.dumps(result.to_dict(), indent=2))
            return 0

        if args.action == "run":
            if not args.payload:
                raise VaultIntegrationError("--payload is required for run")
            result = run_raw_payload(
                args.payload,
                repo_path=args.repo,
                mode=args.mode,
            )
            print(result.stdout)
            return 0

        if args.action == "release-evidence":
            if not args.output_dir:
                raise VaultIntegrationError(
                    "--output-dir is required for release-evidence"
                )
            result = run_release_evidence(
                args.output_dir,
                model=args.model,
                repo_path=args.repo,
            )
            print(json.dumps(result.to_dict(), indent=2))
            return 0

        if args.action == "release-gate":
            if not args.bundle:
                raise VaultIntegrationError("--bundle is required for release-gate")
            result = run_release_gate(args.bundle, repo_path=args.repo)
            print(json.dumps(result.to_dict(), indent=2))
            return 0
    except VaultIntegrationError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    return 0


def main() -> int:
    """Public CLI entrypoint for the canonical Vault integration module."""
    return _cli()


if __name__ == "__main__":
    raise SystemExit(main())
