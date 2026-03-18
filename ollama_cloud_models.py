"""Central Ollama Cloud model selection for AGI-model operations.

The repo currently validates `qwen3-coder-next:cloud` in CI. This module
keeps operation-to-model selection explicit and overrideable so model routing
is consistent across training hooks, local helpers, and future CI steps.
"""

from __future__ import annotations

import os
from dataclasses import asdict, dataclass
from typing import Dict


VALIDATED_DEFAULT_CLOUD_MODEL = "qwen3-coder-next:cloud"


@dataclass(frozen=True)
class OllamaOperationModel:
    operation: str
    model: str
    purpose: str
    rationale: str
    env_var: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


_OPERATION_MODELS: Dict[str, OllamaOperationModel] = {
    "vae_checkpoint_validation": OllamaOperationModel(
        operation="vae_checkpoint_validation",
        model=VALIDATED_DEFAULT_CLOUD_MODEL,
        purpose="Judge post-training checkpoint health from summary metrics.",
        rationale=(
            "Requires structured JSON output, metric-grounded reasoning, and "
            "stable behavior for CI and release decisions."
        ),
        env_var="AGI_OLLAMA_MODEL_VAE_CHECKPOINT_VALIDATION",
    ),
    "vae_loss_interpretation": OllamaOperationModel(
        operation="vae_loss_interpretation",
        model=VALIDATED_DEFAULT_CLOUD_MODEL,
        purpose=(
            "Interpret VAE smoke-test loss components and recommend one "
            "training adjustment."
        ),
        rationale=(
            "Needs numerical fidelity, concise explanation, and dependable "
            "schema-following for analysis and recommendation JSON."
        ),
        env_var="AGI_OLLAMA_MODEL_VAE_LOSS_INTERPRETATION",
    ),
    "phi_artifact_analysis": OllamaOperationModel(
        operation="phi_artifact_analysis",
        model=VALIDATED_DEFAULT_CLOUD_MODEL,
        purpose=(
            "Interpret phi and IIT-oriented artifacts and propose the next "
            "experiment."
        ),
        rationale=(
            "The repo's phi artifacts mix dense JSON metrics with research "
            "questions, so the most reliable validated cloud model is the "
            "best default until additional tags are proven in this repo."
        ),
        env_var="AGI_OLLAMA_MODEL_PHI_ARTIFACT_ANALYSIS",
    ),
    "eval_case_generation": OllamaOperationModel(
        operation="eval_case_generation",
        model=VALIDATED_DEFAULT_CLOUD_MODEL,
        purpose=(
            "Generate schema-valid regression and edge-case prompts for Vault "
            "eval datasets."
        ),
        rationale=(
            "This is effectively code generation against a JSON schema and "
            "benefits from the repo's validated coder model."
        ),
        env_var="AGI_OLLAMA_MODEL_EVAL_CASE_GENERATION",
    ),
    "ci_audit_oracle": OllamaOperationModel(
        operation="ci_audit_oracle",
        model=VALIDATED_DEFAULT_CLOUD_MODEL,
        purpose=(
            "Render short structured audit verdicts from smoke, contract, and "
            "artifact summaries in CI."
        ),
        rationale=(
            "Audit outputs need short, stable JSON verdicts more than "
            "open-ended "
            "creative language."
        ),
        env_var="AGI_OLLAMA_MODEL_CI_AUDIT_ORACLE",
    ),
    "research_report_generation": OllamaOperationModel(
        operation="research_report_generation",
        model=VALIDATED_DEFAULT_CLOUD_MODEL,
        purpose=(
            "Turn validated AGI and IBM artifacts into concise technical "
            "research summaries."
        ),
        rationale=(
            "This repo currently proves only one cloud tag end-to-end, so the "
            "best operational choice is to standardize on that tag while "
            "keeping per-operation overrides available."
        ),
        env_var="AGI_OLLAMA_MODEL_RESEARCH_REPORT_GENERATION",
    ),
}


def get_ollama_cloud_model(
    operation: str,
    override: str | None = None,
) -> str:
    if override:
        return override
    selection = _OPERATION_MODELS.get(operation)
    if selection is None:
        return os.environ.get(
            "AGI_OLLAMA_MODEL_DEFAULT",
            VALIDATED_DEFAULT_CLOUD_MODEL,
        )
    return os.environ.get(selection.env_var, selection.model)


def describe_ollama_operation_models() -> dict[str, dict[str, str]]:
    return {
        name: selection.to_dict()
        for name, selection in _OPERATION_MODELS.items()
    }
