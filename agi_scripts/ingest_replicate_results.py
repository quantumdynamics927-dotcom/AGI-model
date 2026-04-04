#!/usr/bin/env python3
"""
Replicate Result Ingestion
==========================

Fetches completed IBM Runtime jobs referenced by a promoter replicate schedule,
computes measured phi using the existing calibration framework, writes raw
hardware result artifacts, and updates the schedule manifest in-place.

Usage:
    python agi_scripts/ingest_replicate_results.py \
      --schedule raw_hardware/promoter_replicate_schedule_manifest.json

Requires IBM_QUANTUM_API_KEY or --api-key.
"""

import argparse
import importlib
import json
import os
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    save_schedule_csv = importlib.import_module(
        "agi_scripts.schedule_promoter_replicates"
    ).save_schedule_csv
except ModuleNotFoundError:
    save_schedule_csv = importlib.import_module(
        "schedule_promoter_replicates"
    ).save_schedule_csv

from quantum_calibration_framework import calculate_phi_resonance

try:
    from qiskit_ibm_runtime import QiskitRuntimeService
except ImportError:
    QiskitRuntimeService = None

try:
    from qiskit_ibm_runtime.utils import RuntimeDecoder
except ImportError:
    RuntimeDecoder = None


IBM_CLOUD_INSTANCE = (
    "crn:v1:bluemix:public:quantum-computing:us-east:"
    "a/03b6dbec24d04cb4971615d1db2b636a:"
    "950af0f7-51c2-48ac-b1e4-4c4faa584df4::"
)


def load_manifest(path: Path) -> Dict:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def save_manifest(path: Path, manifest: Dict) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, ensure_ascii=False)


def initialize_service(api_key: str):
    if QiskitRuntimeService is None:
        raise RuntimeError("qiskit-ibm-runtime is required for ingestion")
    return QiskitRuntimeService(
        channel="ibm_cloud",
        token=api_key,
        instance=IBM_CLOUD_INSTANCE,
    )


def coerce_status(raw_status) -> str:
    if isinstance(raw_status, str):
        status = raw_status
    else:
        status = getattr(raw_status, "name", str(raw_status))

    normalized = str(status).upper()
    if normalized in {"DONE", "COMPLETED"}:
        return "DONE"
    return normalized


def extract_counts_from_result_payload(payload: Dict) -> Dict[str, int]:
    if RuntimeDecoder is None:
        raise RuntimeError(
            "qiskit-ibm-runtime is required to decode archived payloads"
        )
    primitive_result = json.loads(
        json.dumps(payload),
        cls=RuntimeDecoder,
    )
    return dict(primitive_result[0].data.meas.get_counts())


def load_archived_payloads(
    results_dir: Path,
    job_id: str,
) -> Tuple[Optional[Dict], Optional[Dict]]:
    info_path = results_dir / f"job-{job_id}-info.json"
    result_path = results_dir / f"job-{job_id}-result.json"

    info_payload = None
    result_payload = None
    if info_path.exists():
        with open(info_path, "r", encoding="utf-8") as handle:
            info_payload = json.load(handle)
    if result_path.exists():
        with open(result_path, "r", encoding="utf-8") as handle:
            result_payload = json.load(handle)
    return info_payload, result_payload


def counts_to_bitstrings(counts: Dict[str, int]) -> List[str]:
    bitstrings: List[str] = []
    for bitstring, count in counts.items():
        bitstrings.extend([bitstring] * int(count))
    return bitstrings


def compute_measured_phi(counts: Dict[str, int]) -> Optional[float]:
    if not counts:
        return None
    first_key = next(iter(counts))
    num_bits = len(first_key)
    bitstrings = counts_to_bitstrings(counts)
    measured_phi, _stats = calculate_phi_resonance(bitstrings, num_bits)
    return float(measured_phi)


def build_raw_artifact(
    run: Dict,
    status: str,
    counts: Dict[str, int],
    measured_phi: Optional[float],
) -> Dict:
    execution = run.get("execution", {})
    planned = run.get("planned_metrics", {})
    now = datetime.now().isoformat()
    shots = int(sum(counts.values())) if counts else int(run.get("shots", 0))
    return {
        "promoter_id": run.get("promoter_id"),
        "run_id": run.get("run_id"),
        "backend": run.get("backend"),
        "backend_role": run.get("backend_role"),
        "replicate_index": run.get("replicate_index"),
        "job_id": execution.get("job_id"),
        "status": status,
        "shots": shots,
        "transpiled_depth": execution.get("transpiled_depth"),
        "qubit_layout": execution.get("qubit_layout", []),
        "predicted_phi": planned.get("predicted_phi"),
        "measured_phi": measured_phi,
        "unique_states": len(counts),
        "counts": counts,
        "artifact_metadata": {
            "evidence_class": "primary",
            "artifact_type": "raw_hardware",
            "artifact_id": f"{run.get('run_id')}_{execution.get('job_id')}",
            "generation_timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "provenance": {
                "vendor": "IBM Quantum",
                "vendor_job_id": execution.get("job_id"),
                "submitted_at": execution.get("submitted_at"),
                "retrieved_at": now,
            },
            "audit_note": (
                "Raw IBM Runtime counts captured from replicate ingestion"
            ),
            "validation_status": status.lower(),
        },
    }


def ingest_run_from_service(service, run: Dict, output_dir: Path) -> Dict:
    execution = run.get("execution", {})
    job_id = execution.get("job_id")
    if not job_id:
        return {"run_id": run.get("run_id"), "status": "MISSING_JOB_ID"}

    job = service.job(job_id)
    status = coerce_status(job.status())
    execution["status"] = status

    if status != "DONE":
        return {"run_id": run.get("run_id"), "status": status}

    result = job.result()
    pub = result[0]
    counts = dict(pub.data.meas.get_counts())
    measured_phi = compute_measured_phi(counts)
    predicted_phi = run.get("planned_metrics", {}).get("predicted_phi")

    observed = run.setdefault("observed_metrics", {})
    observed["measured_phi"] = measured_phi
    observed["calibrated_phi"] = measured_phi
    observed["residual"] = (
        float(measured_phi) - float(predicted_phi)
        if measured_phi is not None and predicted_phi is not None
        else None
    )
    observed["timestamp"] = datetime.now().isoformat()

    raw_artifact = build_raw_artifact(run, status, counts, measured_phi)
    output_path = output_dir / f"promoter_{run.get('run_id')}_{job_id}.json"
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(raw_artifact, handle, indent=2, ensure_ascii=False)

    return {
        "run_id": run.get("run_id"),
        "status": status,
        "job_id": job_id,
        "output_path": str(output_path),
        "measured_phi": measured_phi,
        "unique_states": len(counts),
    }


def ingest_run_from_archive(
    run: Dict,
    output_dir: Path,
    results_dir: Path,
) -> Dict:
    execution = run.get("execution", {})
    job_id = execution.get("job_id")
    if not job_id:
        return {"run_id": run.get("run_id"), "status": "MISSING_JOB_ID"}

    info_payload, result_payload = load_archived_payloads(results_dir, job_id)
    if result_payload is None:
        return {
            "run_id": run.get("run_id"),
            "status": "MISSING_RESULT_FILE",
            "job_id": job_id,
        }

    status = "DONE"
    if info_payload is not None:
        status = coerce_status(
            info_payload.get("state", {}).get("status", status)
        )
    execution["status"] = status

    counts = extract_counts_from_result_payload(result_payload)
    measured_phi = compute_measured_phi(counts)
    predicted_phi = run.get("planned_metrics", {}).get("predicted_phi")

    observed = run.setdefault("observed_metrics", {})
    observed["measured_phi"] = measured_phi
    observed["calibrated_phi"] = measured_phi
    observed["residual"] = (
        float(measured_phi) - float(predicted_phi)
        if measured_phi is not None and predicted_phi is not None
        else None
    )
    observed["timestamp"] = datetime.now().isoformat()

    raw_artifact = build_raw_artifact(run, status, counts, measured_phi)
    provenance = raw_artifact["artifact_metadata"]["provenance"]
    provenance["archived_result_file"] = str(
        results_dir / f"job-{job_id}-result.json"
    )
    provenance["archived_info_file"] = str(
        results_dir / f"job-{job_id}-info.json"
    )

    output_path = output_dir / f"promoter_{run.get('run_id')}_{job_id}.json"
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(raw_artifact, handle, indent=2, ensure_ascii=False)

    return {
        "run_id": run.get("run_id"),
        "status": status,
        "job_id": job_id,
        "output_path": str(output_path),
        "measured_phi": measured_phi,
        "unique_states": len(counts),
    }


def build_summary(results: List[Dict]) -> Dict:
    counter = Counter(result["status"] for result in results)
    completed = [result for result in results if result["status"] == "DONE"]
    return {
        "generated_at": datetime.now().isoformat(),
        "runs_total": len(results),
        "status_counts": dict(counter),
        "completed_runs": len(completed),
        "run_summaries": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Ingest completed replicate results"
    )
    parser.add_argument(
        "--schedule",
        default="raw_hardware/promoter_replicate_schedule_manifest.json",
        help="Replicate schedule manifest to update",
    )
    parser.add_argument(
        "--api-key",
        default=os.environ.get("IBM_QUANTUM_API_KEY"),
        help="IBM Quantum API key; defaults to IBM_QUANTUM_API_KEY",
    )
    parser.add_argument(
        "--results-dir",
        help=(
            "Optional directory of archived job-*-info/result JSON "
            "files for offline ingestion"
        ),
    )
    parser.add_argument(
        "--output-dir",
        default="raw_hardware",
        help="Directory for per-run raw hardware artifacts",
    )
    parser.add_argument(
        "--summary-output",
        default="raw_hardware/replicate_ingestion_summary.json",
        help="Output path for ingestion summary",
    )
    args = parser.parse_args()

    schedule_path = Path(args.schedule)
    if not schedule_path.exists():
        print(f"Error: schedule manifest not found: {schedule_path}")
        return 1

    manifest = load_manifest(schedule_path)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    results_dir = Path(args.results_dir) if args.results_dir else None

    if results_dir is None and not args.api_key:
        print(
            "Error: IBM_QUANTUM_API_KEY or --api-key is required "
            "unless --results-dir is provided"
        )
        return 1

    service = initialize_service(args.api_key) if results_dir is None else None

    results: List[Dict] = []
    for run in manifest.get("scheduled_runs", []):
        if results_dir is not None:
            results.append(
                ingest_run_from_archive(run, output_dir, results_dir)
            )
        else:
            results.append(ingest_run_from_service(service, run, output_dir))

    save_manifest(schedule_path, manifest)

    csv_path = schedule_path.with_name(
        "promoter_replicate_schedule_matrix.csv"
    )
    if csv_path.exists():
        save_schedule_csv(manifest, csv_path)

    summary = build_summary(results)
    summary_path = Path(args.summary_output)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_path, "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, ensure_ascii=False)

    print("\n" + "=" * 80)
    print("REPLICATE RESULT INGESTION")
    print("=" * 80)
    print(f"Schedule: {schedule_path}")
    print(f"Runs processed: {summary['runs_total']}")
    print(f"Completed runs: {summary['completed_runs']}")
    for status, count in sorted(summary["status_counts"].items()):
        print(f"  - {status}: {count}")
    print(f"Updated manifest: {schedule_path}")
    print(f"Updated CSV: {csv_path}")
    print(f"Summary: {summary_path}")
    print("=" * 80 + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
