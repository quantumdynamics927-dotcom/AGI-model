from __future__ import annotations

import argparse
import importlib
import json
import math
import sys
import time
from pathlib import Path
from typing import Any

import torch

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

_vae_model = importlib.import_module("vae_model")
QuantumVAE = _vae_model.QuantumVAE
total_loss = _vae_model.total_loss


CONTRACT_VERSION = "1.0"
DEFAULT_ARTIFACT_PATTERNS = (
    "phi_agent_report_*.json",
    "ibm_hardware_aggregate_*.json",
    "dna_quantum_analysis_results.json",
    "artifacts/ibm_decoherence_job_analysis.json",
)


def _round(value: float, digits: int = 6) -> float:
    return round(float(value), digits)


def _is_finite(value: Any) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _density_trace_mean(density_matrix: torch.Tensor) -> float:
    if density_matrix.ndim < 2:
        return 0.0
    diagonal = torch.diagonal(density_matrix, dim1=-2, dim2=-1)
    return float(diagonal.sum(dim=-1).mean().item())


def _resolve_artifact_path(repo_root: Path, artifact: str | None) -> Path:
    if artifact:
        candidate = Path(artifact)
        if not candidate.is_absolute():
            candidate = repo_root / candidate
        return candidate.resolve()

    matches: list[Path] = []
    for pattern in DEFAULT_ARTIFACT_PATTERNS:
        matches.extend(repo_root.glob(pattern))
    if not matches:
        raise FileNotFoundError(
            "No artifact file found. Pass --artifact or create one of the "
            f"expected files: {', '.join(DEFAULT_ARTIFACT_PATTERNS)}"
        )
    return max(matches, key=lambda path: path.stat().st_mtime).resolve()


def _build_payload(
    *,
    operation: str,
    passed: bool,
    metrics: dict[str, Any],
    checks: list[dict[str, Any]],
    details: dict[str, Any],
) -> dict[str, Any]:
    return {
        "contract_version": CONTRACT_VERSION,
        "operation": operation,
        "passed": passed,
        "metrics": metrics,
        "checks": checks,
        "details": details,
        "generated_at_epoch_s": time.time(),
        "repo_root": str(ROOT),
    }


def run_vae_smoke(
    seed: int,
    batch_size: int,
    input_dim: int,
    latent_dim: int,
    include_advanced: bool,
    checkpoint_path: str | None = None,
) -> dict[str, Any]:
    torch.manual_seed(seed)
    model = QuantumVAE(input_dim=input_dim, latent_dim=latent_dim)
    resolved_checkpoint_path: Path | None = None
    if checkpoint_path:
        resolved_checkpoint_path = Path(checkpoint_path)
        if not resolved_checkpoint_path.is_absolute():
            resolved_checkpoint_path = (
                ROOT / resolved_checkpoint_path
            ).resolve()
        if not resolved_checkpoint_path.exists():
            raise FileNotFoundError(
                f"Checkpoint path does not exist: {resolved_checkpoint_path}"
            )
        state_dict = torch.load(resolved_checkpoint_path, map_location="cpu")
        model.load_state_dict(state_dict)
    model.eval()

    with torch.no_grad():
        inputs = torch.rand(batch_size, input_dim)
        recon_x, mu, log_var, density_matrix = model(inputs, return_density=True)
        total_tensor, losses = total_loss(
            recon_x,
            inputs,
            mu,
            log_var,
            density_matrix,
            include_advanced=include_advanced,
        )

    metrics = {
        "batch_size": batch_size,
        "input_dim": input_dim,
        "latent_dim": latent_dim,
        "total_loss": _round(total_tensor.item()),
        "reconstruction_mae": _round(
            torch.mean(torch.abs(recon_x - inputs)).item()
        ),
        "mu_mean": _round(mu.mean().item()),
        "mu_std": _round(mu.std().item()),
        "log_var_mean": _round(log_var.mean().item()),
        "density_trace_mean": _round(_density_trace_mean(density_matrix)),
    }
    for key, value in losses.items():
        metrics[f"loss_{key}"] = _round(value)

    checks = [
        {
            "name": "reconstruction_shape",
            "passed": list(recon_x.shape) == [batch_size, input_dim],
            "detail": f"got {list(recon_x.shape)}",
        },
        {
            "name": "mu_shape",
            "passed": list(mu.shape) == [batch_size, latent_dim],
            "detail": f"got {list(mu.shape)}",
        },
        {
            "name": "log_var_shape",
            "passed": list(log_var.shape) == [batch_size, latent_dim],
            "detail": f"got {list(log_var.shape)}",
        },
        {
            "name": "finite_losses",
            "passed": all(_is_finite(value) for value in losses.values()),
            "detail": "all reported loss components must be finite",
        },
        {
            "name": "finite_metrics",
            "passed": all(
                _is_finite(value)
                for key, value in metrics.items()
                if key not in {"batch_size", "input_dim", "latent_dim"}
            ),
            "detail": "core metrics must be finite",
        },
    ]
    passed = all(check["passed"] for check in checks)

    return _build_payload(
        operation="vae-smoke",
        passed=passed,
        metrics=metrics,
        checks=checks,
        details={
            "seed": seed,
            "include_advanced": include_advanced,
            "device": str(next(model.parameters()).device),
            "checkpoint_path": (
                str(resolved_checkpoint_path)
                if resolved_checkpoint_path is not None
                else None
            ),
        },
    )


def _summarize_phi_agent_report(
    payload: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    dna_results = payload.get("dna_results", {})
    phi_harmonic = payload.get("phi_harmonic", {})
    latent_space = payload.get("latent_space", {})
    integrated_information = payload.get("integrated_information", {})
    metrics = {
        "phi_value": _round(dna_results.get("phi_value", 0.0)),
        "phi_alignment_score": _round(
            dna_results.get("phi_alignment_score", 0.0)
        ),
        "consciousness_level": _round(
            dna_results.get("consciousness_level", 0.0)
        ),
        "phi_harmonic_score": _round(
            phi_harmonic.get("phi_harmonic_score", 0.0)
        ),
        "latent_entropy": _round(latent_space.get("latent_entropy", 0.0)),
        "integrated_information": _round(
            integrated_information.get("integrated_information", 0.0)
        ),
    }
    checks = [
        {
            "name": "has_dna_results",
            "passed": bool(dna_results),
            "detail": "phi report should contain dna_results",
        },
        {
            "name": "finite_metrics",
            "passed": all(_is_finite(value) for value in metrics.values()),
            "detail": "all summary metrics must be finite",
        },
    ]
    details = {
        "artifact_type": "phi-agent-report",
        "timestamp": payload.get("timestamp") or dna_results.get("timestamp"),
        "is_conscious": bool(dna_results.get("is_conscious", False)),
        "dna_source": dna_results.get("dna_source"),
    }
    return metrics, checks, details


def _summarize_ibm_aggregate(
    payload: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    aggregate_metrics = payload.get("aggregate_metrics", {})
    individual_jobs = payload.get("individual_jobs", [])
    phi_resonances = [job.get("phi_resonance", 0.0) for job in individual_jobs]
    consciousness_states = [
        job.get("consciousness", {}).get("status", "unknown")
        for job in individual_jobs
    ]
    metrics = {
        "num_jobs": int(payload.get("num_jobs", len(individual_jobs))),
        "total_shots": int(payload.get("total_shots", 0)),
        "mean_phi_resonance": _round(
            sum(phi_resonances) / len(phi_resonances)
        ) if phi_resonances else 0.0,
        "consciousness_delta": _round(
            aggregate_metrics.get("consciousness_delta", 0.0)
        ),
        "consciousness_std": _round(
            aggregate_metrics.get("consciousness_std", 0.0)
        ),
        "retrocausal_R": _round(aggregate_metrics.get("retrocausal_R", 0.0)),
    }
    checks = [
        {
            "name": "has_jobs",
            "passed": len(individual_jobs) > 0,
            "detail": f"found {len(individual_jobs)} jobs",
        },
        {
            "name": "finite_metrics",
            "passed": all(_is_finite(value) for value in metrics.values()),
            "detail": "all summary metrics must be finite",
        },
    ]
    details = {
        "artifact_type": "ibm-hardware-aggregate",
        "timestamp": payload.get("timestamp"),
        "backend": payload.get("backend"),
        "consciousness_statuses": sorted(set(consciousness_states)),
    }
    return metrics, checks, details


def _summarize_dna_quantum_analysis(
    payload: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    results = payload.get("results", {})
    sequences = list(results.values())
    phi_correlations = [item.get("phi_correlation", 0.0) for item in sequences]
    gains = [item.get("predicted_gain", 0.0) for item in sequences]
    coherence = [item.get("quantum_coherence", 0.0) for item in sequences]
    metrics = {
        "sequences_analyzed": int(
            payload.get("sequences_analyzed", len(sequences))
        ),
        "mean_phi_correlation": _round(
            sum(phi_correlations) / len(phi_correlations)
        ) if phi_correlations else 0.0,
        "max_phi_correlation": (
            _round(max(phi_correlations)) if phi_correlations else 0.0
        ),
        "mean_predicted_gain": (
            _round(sum(gains) / len(gains)) if gains else 0.0
        ),
        "mean_quantum_coherence": _round(
            sum(coherence) / len(coherence)
        ) if coherence else 0.0,
    }
    checks = [
        {
            "name": "has_sequences",
            "passed": len(sequences) > 0,
            "detail": f"found {len(sequences)} sequence results",
        },
        {
            "name": "finite_metrics",
            "passed": all(_is_finite(value) for value in metrics.values()),
            "detail": "all summary metrics must be finite",
        },
    ]
    details = {
        "artifact_type": "dna-quantum-analysis",
        "analysis_type": payload.get("analysis_type"),
        "timestamp": payload.get("timestamp"),
    }
    return metrics, checks, details


def _summarize_ibm_decoherence_analysis(
    payload: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    aggregate = payload.get("aggregate", {})
    variants = (
        aggregate.get("variants", {})
        if isinstance(aggregate, dict)
        else {}
    )
    backends = (
        aggregate.get("backends", {})
        if isinstance(aggregate, dict)
        else {}
    )

    control = variants.get("control", {})
    mild = variants.get("mild", {})
    moderate = variants.get("moderate", {})
    fez = backends.get("ibm_fez", {})
    marrakesh = backends.get("ibm_marrakesh", {})

    control_ghz = _round(control.get("avg_ghz_mass", 0.0))
    mild_ghz = _round(mild.get("avg_ghz_mass", 0.0))
    moderate_ghz = _round(moderate.get("avg_ghz_mass", 0.0))
    control_entropy = _round(control.get("avg_entropy", 0.0))
    mild_entropy = _round(mild.get("avg_entropy", 0.0))
    moderate_entropy = _round(moderate.get("avg_entropy", 0.0))
    fez_ghz = _round(fez.get("avg_ghz_mass", 0.0))
    marrakesh_ghz = _round(marrakesh.get("avg_ghz_mass", 0.0))

    metrics = {
        "num_jobs": int(
            aggregate.get("num_jobs", len(payload.get("job_results", [])))
        ),
        "num_variants": int(len(variants)),
        "control_avg_ghz_mass": control_ghz,
        "mild_avg_ghz_mass": mild_ghz,
        "moderate_avg_ghz_mass": moderate_ghz,
        "control_avg_entropy": control_entropy,
        "mild_avg_entropy": mild_entropy,
        "moderate_avg_entropy": moderate_entropy,
        "ghz_mass_delta_control_to_moderate": _round(
            moderate_ghz - control_ghz
        ),
        "entropy_delta_control_to_moderate": _round(
            moderate_entropy - control_entropy
        ),
        "backend_gap_marrakesh_minus_fez": _round(marrakesh_ghz - fez_ghz),
    }
    checks = [
        {
            "name": "has_jobs",
            "passed": metrics["num_jobs"] > 0,
            "detail": f"found {metrics['num_jobs']} decoherence jobs",
        },
        {
            "name": "has_variants",
            "passed": len(variants) > 0,
            "detail": f"found variants: {sorted(variants.keys())}",
        },
        {
            "name": "finite_metrics",
            "passed": all(_is_finite(value) for value in metrics.values()),
            "detail": "all summary metrics must be finite",
        },
    ]
    details = {
        "artifact_type": "ibm-decoherence-analysis",
        "jobs_dir": payload.get("jobs_dir"),
        "variants_present": sorted(variants.keys()),
        "backends_present": sorted(backends.keys()),
        "interpretation": aggregate.get("interpretation"),
    }
    return metrics, checks, details


def run_artifact_summary(artifact: str | None) -> dict[str, Any]:
    artifact_path = _resolve_artifact_path(ROOT, artifact)
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))

    if isinstance(payload, dict) and "dna_results" in payload:
        metrics, checks, details = _summarize_phi_agent_report(payload)
    elif (
        isinstance(payload, dict)
        and "aggregate_metrics" in payload
        and "individual_jobs" in payload
    ):
        metrics, checks, details = _summarize_ibm_aggregate(payload)
    elif (
        isinstance(payload, dict)
        and "analysis_type" in payload
        and "results" in payload
    ):
        metrics, checks, details = _summarize_dna_quantum_analysis(payload)
    elif (
        isinstance(payload, dict)
        and "aggregate" in payload
        and "job_results" in payload
    ):
        metrics, checks, details = _summarize_ibm_decoherence_analysis(payload)
    else:
        raise ValueError(
            f"Unsupported artifact format in {artifact_path.name}."
        )

    passed = all(check["passed"] for check in checks)
    details["artifact_path"] = str(artifact_path)
    details["artifact_name"] = artifact_path.name

    return _build_payload(
        operation="artifact-summary",
        passed=passed,
        metrics=metrics,
        checks=checks,
        details=details,
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Emit deterministic AGI-model validation JSON for external gates."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    vae_parser = subparsers.add_parser(
        "vae-smoke",
        help="Run a seeded QuantumVAE forward/loss smoke test.",
    )
    vae_parser.add_argument("--seed", type=int, default=7)
    vae_parser.add_argument("--batch-size", type=int, default=8)
    vae_parser.add_argument("--input-dim", type=int, default=128)
    vae_parser.add_argument("--latent-dim", type=int, default=32)
    vae_parser.add_argument(
        "--include-advanced",
        action="store_true",
        help="Include advanced fidelity and entropy loss terms.",
    )
    vae_parser.add_argument(
        "--checkpoint",
        type=str,
        default=None,
        help="Optional checkpoint path to load before the smoke pass.",
    )

    artifact_parser = subparsers.add_parser(
        "artifact-summary",
        help="Normalize a supported AGI-model artifact into contract JSON.",
    )
    artifact_parser.add_argument(
        "--artifact",
        type=str,
        default=None,
        help=(
            "Artifact path. Defaults to the newest supported artifact in the "
            "repo root."
        ),
    )

    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    try:
        if args.command == "vae-smoke":
            payload = run_vae_smoke(
                seed=args.seed,
                batch_size=args.batch_size,
                input_dim=args.input_dim,
                latent_dim=args.latent_dim,
                include_advanced=args.include_advanced,
                checkpoint_path=args.checkpoint,
            )
        elif args.command == "artifact-summary":
            payload = run_artifact_summary(args.artifact)
        else:
            raise ValueError(f"Unsupported command: {args.command}")
    except (
        FileNotFoundError,
        ValueError,
        json.JSONDecodeError,
        RuntimeError,
    ) as exc:
        error_payload = {
            "contract_version": CONTRACT_VERSION,
            "operation": args.command,
            "passed": False,
            "error": str(exc),
            "repo_root": str(ROOT),
        }
        json.dump(error_payload, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 1

    json.dump(payload, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
