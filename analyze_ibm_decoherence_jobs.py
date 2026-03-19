"""Analyze IBM Quantum decoherence job pairs for the phi-phased GHZ probe.

This script ingests the JSON job info/result pairs produced by IBM Runtime
sampler execution, classifies each circuit into a decoherence sweep variant,
and computes compact comparison metrics across backends.
"""

from __future__ import annotations

import argparse
import base64
import io
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np
from qiskit import qpy
from qiskit.primitives.containers import BitArray


PHI = 1.618033988749895
DEFAULT_JOBS_DIR = Path(r"E:\FILES-TO-USE")
DEFAULT_OUTPUT = Path("artifacts/ibm_decoherence_job_analysis.json")


def load_circuit_from_info(info: dict[str, Any]):
    item = info["params"]["quantum_program"]["items"][0]
    encoded = item["circuit"]["circuit_b64"]
    return qpy.load(io.BytesIO(base64.b64decode(encoded)))[0]


def classify_variant(circuit) -> str:
    rz_params: list[float] = []
    for instruction in circuit.data:
        operation = instruction.operation
        if operation.name == "rz":
            try:
                rz_params.append(float(operation.params[0]))
            except (TypeError, ValueError):
                continue

    if rz_params and all(
        abs(value - math.pi / 2) < 1e-6
        for value in rz_params
    ):
        return "control"
    if any(abs(value - 0.050563) < 1e-4 for value in rz_params):
        return "mild"
    if any(abs(value - 0.202254) < 1e-4 for value in rz_params):
        return "moderate"
    if any(abs(value - PHI / 8.0) < 1e-4 for value in rz_params):
        return "strong"
    return "unknown"


def extract_counts(result_payload: dict[str, Any]) -> dict[str, int]:
    c_field = result_payload["data"][0]["results"]["c"]
    raw = base64.b64decode(c_field["data"])
    array = np.frombuffer(raw, dtype=np.uint8).reshape(c_field["shape"][0], -1)
    bit_array = BitArray(array, c_field["shape"][1])
    return bit_array.get_counts()


def summarize_counts(counts: dict[str, int]) -> dict[str, float | str | int]:
    shots = sum(counts.values())
    if shots <= 0:
        return {
            "shots": 0,
            "ghz_mass": 0.0,
            "parity_expectation": 0.0,
            "distribution_entropy": 0.0,
            "dominant_bitstring": "",
            "dominant_count": 0,
            "dominant_probability": 0.0,
        }

    probabilities = {
        bitstring: count / shots
        for bitstring, count in counts.items()
    }
    ghz_mass = (
        probabilities.get("00000000", 0.0)
        + probabilities.get("11111111", 0.0)
    )
    entropy = -sum(
        probability * math.log2(probability)
        for probability in probabilities.values()
        if probability > 0
    )

    even = 0
    odd = 0
    for bitstring, count in counts.items():
        if bitstring.count("1") % 2 == 0:
            even += count
        else:
            odd += count

    dominant_bitstring, dominant_count = max(
        counts.items(),
        key=lambda item: item[1],
    )
    return {
        "shots": shots,
        "ghz_mass": round(ghz_mass, 6),
        "parity_expectation": round((even - odd) / shots, 6),
        "distribution_entropy": round(entropy, 6),
        "dominant_bitstring": dominant_bitstring,
        "dominant_count": dominant_count,
        "dominant_probability": round(dominant_count / shots, 6),
    }


def top_counts(
    counts: dict[str, int],
    limit: int = 6,
) -> list[dict[str, int | str]]:
    return [
        {"bitstring": bitstring, "count": count}
        for bitstring, count in sorted(
            counts.items(),
            key=lambda item: item[1],
            reverse=True,
        )[:limit]
    ]


def analyze_job_pair(info_path: Path) -> dict[str, Any]:
    result_path = info_path.with_name(
        info_path.name.replace("-info.json", "-result.json")
    )
    info = json.loads(info_path.read_text(encoding="utf-8"))
    result = json.loads(result_path.read_text(encoding="utf-8"))

    circuit = load_circuit_from_info(info)
    counts = extract_counts(result)
    metrics = summarize_counts(counts)

    gate_counts: dict[str, int] = defaultdict(int)
    for instruction in circuit.data:
        gate_counts[instruction.operation.name] += 1

    return {
        "job_id": info["id"],
        "backend": info["backend"],
        "created": info.get("created"),
        "status": info.get("status") or info.get("state", {}).get("status"),
        "variant": classify_variant(circuit),
        "shots": info["params"]["quantum_program"]["shots"],
        "gate_counts": dict(gate_counts),
        "metrics": metrics,
        "top_counts": top_counts(counts),
    }


def aggregate_jobs(job_results: list[dict[str, Any]]) -> dict[str, Any]:
    by_variant: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_backend: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for result in job_results:
        by_variant[result["variant"]].append(result)
        by_backend[result["backend"]].append(result)

    variant_summary: dict[str, Any] = {}
    for variant, entries in by_variant.items():
        ghz_values = [entry["metrics"]["ghz_mass"] for entry in entries]
        entropy_values = [
            entry["metrics"]["distribution_entropy"]
            for entry in entries
        ]
        parity_values = [
            entry["metrics"]["parity_expectation"]
            for entry in entries
        ]
        variant_summary[variant] = {
            "num_jobs": len(entries),
            "backends": sorted({entry["backend"] for entry in entries}),
            "avg_ghz_mass": round(sum(ghz_values) / len(ghz_values), 6),
            "avg_entropy": round(sum(entropy_values) / len(entropy_values), 6),
            "avg_parity": round(sum(parity_values) / len(parity_values), 6),
        }

    backend_summary: dict[str, Any] = {}
    for backend, entries in by_backend.items():
        backend_summary[backend] = {
            "num_jobs": len(entries),
            "variants": sorted({entry["variant"] for entry in entries}),
            "avg_ghz_mass": round(
                sum(entry["metrics"]["ghz_mass"] for entry in entries)
                / len(entries),
                6,
            ),
            "avg_entropy": round(
                sum(
                    entry["metrics"]["distribution_entropy"]
                    for entry in entries
                ) / len(entries),
                6,
            ),
        }

    interpretation = (
        "Z-basis measurements remain dominated by 00000000 and "
        "11111111 across variants, so these jobs act primarily "
        "as population controls. Phase-only kicks do not produce "
        "a strong decoherence signature without an X-basis coherence readout."
    )

    return {
        "num_jobs": len(job_results),
        "variants": variant_summary,
        "backends": backend_summary,
        "interpretation": interpretation,
    }


def write_output(report: dict[str, Any], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Analyze IBM decoherence job pairs"
    )
    parser.add_argument(
        "jobs_dir",
        nargs="?",
        default=str(DEFAULT_JOBS_DIR),
        help="Directory containing job-*-info/result JSON pairs",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help="Path to write the analysis JSON",
    )
    args = parser.parse_args()

    jobs_dir = Path(args.jobs_dir)
    info_files = sorted(jobs_dir.glob("job-*-info.json"))
    if not info_files:
        raise FileNotFoundError(f"No job info files found in {jobs_dir}")

    job_results = [analyze_job_pair(info_path) for info_path in info_files]
    report = {
        "jobs_dir": str(jobs_dir),
        "job_results": job_results,
        "aggregate": aggregate_jobs(job_results),
    }
    output_path = write_output(report, Path(args.output))
    print(f"Analyzed {len(job_results)} decoherence jobs")
    print(f"Saved report to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
