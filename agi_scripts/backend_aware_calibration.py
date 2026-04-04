#!/usr/bin/env python3
"""
Backend-Aware Calibration Fitter
================================

Fits backend-specific calibration offsets and variance diagnostics from
replicate-aware schedule manifests.

Usage:
    python agi_scripts/backend_aware_calibration.py \
      --schedule raw_hardware/test_replicate_schedule_manifest.json

Optional: provide multiple manifests with --schedule repeated.
"""

import argparse
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np


def load_manifest(path: Path) -> Dict:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def collect_rows(manifests: List[Dict]) -> List[Dict]:
    rows: List[Dict] = []
    for manifest in manifests:
        for run in manifest.get("scheduled_runs", []):
            planned = run.get("planned_metrics", {})
            observed = run.get("observed_metrics", {})
            execution = run.get("execution", {})
            rows.append(
                {
                    "run_id": run.get("run_id"),
                    "promoter_id": run.get("promoter_id"),
                    "backend": run.get("backend"),
                    "replicate_index": run.get("replicate_index"),
                    "predicted_phi": planned.get("predicted_phi"),
                    "measured_phi": observed.get("measured_phi"),
                    "calibrated_phi": observed.get("calibrated_phi"),
                    "residual": observed.get("residual"),
                    "shots": run.get("shots"),
                    "transpiled_depth": execution.get("transpiled_depth"),
                    "qubit_layout": execution.get("qubit_layout", []),
                    "status": execution.get("status"),
                    "timestamp": observed.get("timestamp") or execution.get("submitted_at"),
                }
            )
    return rows


def has_observations(rows: List[Dict]) -> bool:
    for row in rows:
        if row["measured_phi"] is not None:
            return True
    return False


def fit_backend_offsets(rows: List[Dict], fallback_baseline: Optional[float] = 0.6183) -> Dict[str, float]:
    grouped_deltas: Dict[str, List[float]] = defaultdict(list)

    for row in rows:
        backend = row["backend"]
        predicted = row["predicted_phi"]
        measured = row["measured_phi"]
        if predicted is not None and measured is not None:
            grouped_deltas[backend].append(float(measured) - float(predicted))

    offsets: Dict[str, float] = {}
    if grouped_deltas:
        for backend, deltas in grouped_deltas.items():
            offsets[backend] = float(np.mean(deltas))
        return offsets

    # No observed measurements yet; define zero-knowledge placeholders.
    for backend in sorted({row["backend"] for row in rows}):
        offsets[backend] = 0.0

    # Keep Fez continuity baseline visible for downstream users.
    if fallback_baseline is not None and "ibm_fez" in offsets:
        offsets["ibm_fez_baseline_phi"] = float(fallback_baseline)

    return offsets


def promoter_backend_interaction(rows: List[Dict]) -> Dict[str, Dict[str, float]]:
    interaction: Dict[str, Dict[str, float]] = {}
    grouped: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))

    for row in rows:
        measured = row["measured_phi"]
        predicted = row["predicted_phi"]
        if measured is None or predicted is None:
            continue
        grouped[row["promoter_id"]][row["backend"]].append(float(measured) - float(predicted))

    for promoter_id, by_backend in grouped.items():
        interaction[promoter_id] = {}
        backend_means: Dict[str, float] = {}
        for backend, deltas in by_backend.items():
            backend_means[backend] = float(np.mean(deltas))
            interaction[promoter_id][f"offset_{backend}"] = backend_means[backend]
        if len(backend_means) >= 2:
            values = list(backend_means.values())
            interaction[promoter_id]["backend_spread"] = float(np.max(values) - np.min(values))

    return interaction


def variance_report(rows: List[Dict]) -> Dict:
    within_promoter: Dict[str, float] = {}
    between_promoter_by_backend: Dict[str, float] = {}

    # Within-promoter variance across replicate measurements.
    by_promoter_measurements: Dict[str, List[float]] = defaultdict(list)
    for row in rows:
        measured = row["measured_phi"]
        if measured is not None:
            by_promoter_measurements[row["promoter_id"]].append(float(measured))

    for promoter_id, values in by_promoter_measurements.items():
        if len(values) >= 2:
            within_promoter[promoter_id] = float(np.var(values, ddof=1))
        else:
            within_promoter[promoter_id] = 0.0

    # Between-promoter variance for each backend.
    backend_promoter_means: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        measured = row["measured_phi"]
        if measured is not None:
            backend_promoter_means[row["backend"]][row["promoter_id"]].append(float(measured))

    for backend, promoter_values in backend_promoter_means.items():
        means = [np.mean(values) for values in promoter_values.values() if values]
        if len(means) >= 2:
            between_promoter_by_backend[backend] = float(np.var(means, ddof=1))
        else:
            between_promoter_by_backend[backend] = 0.0

    return {
        "within_promoter_variance": within_promoter,
        "between_promoter_variance_by_backend": between_promoter_by_backend,
    }


def transferability(rows: List[Dict], reference_backend: str = "ibm_fez") -> Dict:
    """Estimate how well reference-backend offset transfers to others."""
    residuals_by_backend: Dict[str, List[float]] = defaultdict(list)

    # Fit reference offset if possible.
    reference_deltas: List[float] = []
    for row in rows:
        if (
            row["backend"] == reference_backend
            and row["measured_phi"] is not None
            and row["predicted_phi"] is not None
        ):
            reference_deltas.append(float(row["measured_phi"]) - float(row["predicted_phi"]))

    if not reference_deltas:
        return {
            "reference_backend": reference_backend,
            "reference_offset": None,
            "status": "insufficient_observations",
        }

    reference_offset = float(np.mean(reference_deltas))

    for row in rows:
        measured = row["measured_phi"]
        predicted = row["predicted_phi"]
        if measured is None or predicted is None:
            continue
        calibrated_prediction = float(predicted) + reference_offset
        residual = float(measured) - calibrated_prediction
        residuals_by_backend[row["backend"]].append(residual)

    backend_rmse: Dict[str, float] = {}
    for backend, residuals in residuals_by_backend.items():
        if residuals:
            backend_rmse[backend] = float(np.sqrt(np.mean(np.square(residuals))))

    return {
        "reference_backend": reference_backend,
        "reference_offset": reference_offset,
        "backend_rmse": backend_rmse,
        "status": "ok",
    }


def summarize_schedule_coverage(rows: List[Dict]) -> Dict:
    coverage: Dict[tuple, int] = defaultdict(int)
    by_backend: Dict[str, int] = defaultdict(int)
    by_promoter: Dict[str, int] = defaultdict(int)

    for row in rows:
        coverage[(row["promoter_id"], row["backend"])] += 1
        by_backend[row["backend"]] += 1
        by_promoter[row["promoter_id"]] += 1

    return {
        "runs_total": len(rows),
        "runs_by_backend": dict(by_backend),
        "runs_by_promoter": dict(by_promoter),
        "replicates_by_promoter_backend": {
            f"{promoter}:{backend}": count
            for (promoter, backend), count in sorted(coverage.items())
        },
    }


def build_calibration_report(manifests: List[Dict], rows: List[Dict]) -> Dict:
    offsets = fit_backend_offsets(rows)
    interaction = promoter_backend_interaction(rows)
    variance = variance_report(rows)
    transfer = transferability(rows)

    return {
        "report_type": "backend_aware_calibration",
        "generated_at": datetime.now().isoformat(),
        "input_manifests": [
            manifest.get("artifact_metadata", {}).get("artifact_id")
            for manifest in manifests
        ],
        "coverage": summarize_schedule_coverage(rows),
        "observations_present": has_observations(rows),
        "backend_offsets": offsets,
        "promoter_backend_interaction": interaction,
        "variance": variance,
        "transferability": transfer,
        "recommendation": {
            "keep_reference_backend": "ibm_fez",
            "primary_throughput_backend": "ibm_kingston",
            "policy_gate": (
                "Switch default backend only after replicate-aware calibration "
                "shows stable RMSE and low backend interaction spread."
            ),
        },
    }


def save_report(report: Dict, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)


def main() -> int:
    parser = argparse.ArgumentParser(description="Fit backend-aware calibration")
    parser.add_argument(
        "--schedule",
        action="append",
        required=True,
        help="Path to replicate schedule manifest JSON (repeatable)",
    )
    parser.add_argument(
        "--output",
        default="raw_hardware/backend_aware_calibration_report.json",
        help="Output report path",
    )

    args = parser.parse_args()

    schedule_paths = [Path(item) for item in args.schedule]
    missing = [str(path) for path in schedule_paths if not path.exists()]
    if missing:
        print("Missing schedule manifests:")
        for path in missing:
            print(f"  - {path}")
        return 1

    manifests = [load_manifest(path) for path in schedule_paths]
    rows = collect_rows(manifests)
    report = build_calibration_report(manifests, rows)
    save_report(report, Path(args.output))

    print("\n" + "=" * 80)
    print("BACKEND-AWARE CALIBRATION")
    print("=" * 80)
    print(f"Input manifests: {len(manifests)}")
    print(f"Total scheduled runs: {report['coverage']['runs_total']}")
    print(f"Observations present: {report['observations_present']}")
    print("Backend offsets:")
    for backend, offset in report["backend_offsets"].items():
        print(f"  - {backend}: {offset}")
    print(f"Output report: {args.output}")
    print("=" * 80 + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
