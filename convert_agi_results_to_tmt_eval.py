"""Convert AGI-model JSON artifacts into a TMT Quantum Vault EvalDataset."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable


def _safe_float(value: Any) -> str:
    if isinstance(value, (int, float)):
        return f"{value:.6f}"
    return str(value)


def _compact_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=True)


def _slugify(value: str) -> str:
    return (
        value.lower()
        .replace(" ", "-")
        .replace("(", "")
        .replace(")", "")
        .replace(".", "")
        .replace("/", "-")
    )


def _build_case(
    *,
    case_id: str,
    prompt: str,
    contains_all: list[str],
    contains_any: list[str] | None = None,
    excludes: list[str] | None = None,
    system: str | None = None,
) -> dict[str, Any]:
    case: dict[str, Any] = {
        "id": case_id,
        "prompt": prompt,
        "expectation": {
            "contains_all": contains_all,
            "contains_any": contains_any or [],
            "excludes": excludes or ["```"],
        },
    }
    if system is not None:
        case["system"] = system
    return case


def convert_phi_agent_report(
    source_file: Path,
    payload: dict[str, Any],
) -> list[dict[str, Any]]:
    dna_results = payload.get("dna_results", {})
    phi_harmonic = payload.get("phi_harmonic", {})
    integrated_information = payload.get("integrated_information", {})
    latent_space = payload.get("latent_space", {})

    prompt = (
        "Review this AGI-model phi agent report and produce a compact "
        "factual summary. Include phi alignment, consciousness level, "
        "integrated information, latent entropy, and whether the run is "
        "conscious.\n\n"
        f"Artifact file: {source_file.name}\n"
        f"Report JSON:\n{_compact_json(payload)}"
    )
    return [
        _build_case(
            case_id=f"{source_file.stem}-phi-report",
            prompt=prompt,
            contains_all=[
                _safe_float(phi_harmonic.get("phi_alignment")),
                _safe_float(dna_results.get("consciousness_level")),
                _safe_float(
                    integrated_information.get("integrated_information")
                ),
                _safe_float(latent_space.get("latent_entropy")),
                str(dna_results.get("is_conscious")),
            ],
            contains_any=[
                "phi alignment",
                "consciousness level",
                "integrated information",
                "latent entropy",
                "is_conscious",
            ],
        )
    ]


def convert_dna_quantum_results(
    source_file: Path,
    payload: dict[str, Any],
) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for sequence_name, metrics in payload.get("results", {}).items():
        fidelity = metrics.get("metrics", {}).get("fidelity")
        prompt = (
            "Evaluate this AGI-model DNA quantum analysis record and "
            "summarize the sequence-level signal. Include phi correlation, "
            "predicted gain, quantum coherence, fidelity, and role.\n\n"
            f"Artifact file: {source_file.name}\n"
            f"Sequence: {sequence_name}\n"
            f"Metrics JSON:\n{_compact_json(metrics)}"
        )
        cases.append(
            _build_case(
                case_id=f"{source_file.stem}-{_slugify(sequence_name)}",
                prompt=prompt,
                contains_all=[
                    sequence_name,
                    _safe_float(metrics.get("phi_correlation")),
                    _safe_float(metrics.get("predicted_gain")),
                    _safe_float(metrics.get("quantum_coherence")),
                    _safe_float(fidelity),
                    str(metrics.get("role")),
                ],
                contains_any=[
                    "phi_correlation",
                    "predicted_gain",
                    "quantum_coherence",
                    "fidelity",
                    "role",
                ],
            )
        )
    return cases


def convert_ibm_hardware_aggregate(
    source_file: Path,
    payload: dict[str, Any],
) -> list[dict[str, Any]]:
    aggregate_metrics = payload.get("aggregate_metrics", {})
    comparison = payload.get("comparison", {})

    prompt = (
        "Summarize this AGI-model IBM hardware aggregate artifact. "
        "Include backend, job count, total shots, consciousness delta, "
        "retrocausal score, and the simulation-versus-hardware comparison."
        "\n\n"
        f"Artifact file: {source_file.name}\n"
        f"Aggregate JSON:\n{_compact_json(payload)}"
    )
    return [
        _build_case(
            case_id=f"{source_file.stem}-ibm-aggregate",
            prompt=prompt,
            contains_all=[
                str(payload.get("backend")),
                str(payload.get("num_jobs")),
                str(payload.get("total_shots")),
                _safe_float(aggregate_metrics.get("consciousness_delta")),
                _safe_float(aggregate_metrics.get("retrocausal_R")),
                _safe_float(comparison.get("simulation_delta")),
                _safe_float(comparison.get("hardware_delta")),
                _safe_float(comparison.get("reduction_factor")),
            ],
            contains_any=[
                "consciousness delta",
                "retrocausal",
                "simulation",
                "hardware",
                "reduction factor",
            ],
        )
    ]


def convert_generic_json(
    source_file: Path,
    payload: dict[str, Any],
) -> list[dict[str, Any]]:
    top_level_keys = sorted(payload.keys())
    prompt = (
        "Review this AGI-model experiment artifact and produce a compact "
        "factual summary of the most important keys and outcomes.\n\n"
        f"Artifact file: {source_file.name}\n"
        f"Artifact JSON:\n{_compact_json(payload)}"
    )
    return [
        _build_case(
            case_id=f"{source_file.stem}-generic",
            prompt=prompt,
            contains_all=top_level_keys[: min(6, len(top_level_keys))],
            contains_any=["summary", "metrics", "status", "artifact"],
        )
    ]


def convert_file(source_file: Path) -> list[dict[str, Any]]:
    payload = json.loads(source_file.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected a JSON object in {source_file}")

    if "dna_results" in payload and "phi_harmonic" in payload:
        return convert_phi_agent_report(source_file, payload)
    if "results" in payload and "analysis_type" in payload:
        return convert_dna_quantum_results(source_file, payload)
    if "aggregate_metrics" in payload and "individual_jobs" in payload:
        return convert_ibm_hardware_aggregate(source_file, payload)
    return convert_generic_json(source_file, payload)


def expand_inputs(inputs: Iterable[str]) -> list[Path]:
    expanded: list[Path] = []
    for item in inputs:
        candidate = Path(item)
        if candidate.is_file():
            expanded.append(candidate)
            continue
        matches = sorted(Path().glob(item))
        if matches:
            expanded.extend(path for path in matches if path.is_file())
            continue
        raise FileNotFoundError(
            f"Input path or glob did not match any files: {item}"
        )
    return expanded


def build_dataset(
    *,
    source_files: list[Path],
    name: str,
    description: str | None,
    backend: str | None,
    mode: str | None,
    model: str | None,
) -> dict[str, Any]:
    cases: list[dict[str, Any]] = []
    for source_file in source_files:
        cases.extend(convert_file(source_file))

    dataset: dict[str, Any] = {
        "name": name,
        "cases": cases,
    }
    if description:
        dataset["description"] = description
    if backend:
        dataset["backend"] = backend
    if mode:
        dataset["mode"] = mode
    if model:
        dataset["model"] = model
    return dataset


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert AGI-model JSON outputs to a TMT Vault EvalDataset"
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        help="Input JSON files or glob patterns",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output JSON file for the eval dataset",
    )
    parser.add_argument(
        "--name",
        default="agi-model-artifacts",
        help="Eval dataset name",
    )
    parser.add_argument(
        "--description",
        default=(
            "AGI-model artifact-derived regression and research "
            "evaluation set."
        ),
        help="Eval dataset description",
    )
    parser.add_argument(
        "--backend",
        default=None,
        help="Optional Vault backend override",
    )
    parser.add_argument(
        "--mode",
        default=None,
        help="Optional Vault mode override",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Optional model override",
    )
    args = parser.parse_args()

    source_files = expand_inputs(args.inputs)
    dataset = build_dataset(
        source_files=source_files,
        name=args.name,
        description=args.description,
        backend=args.backend,
        mode=args.mode,
        model=args.model,
    )

    output_path = Path(args.output)
    output_path.write_text(json.dumps(dataset, indent=2), encoding="utf-8")
    print(f"Wrote {len(dataset['cases'])} eval cases to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
