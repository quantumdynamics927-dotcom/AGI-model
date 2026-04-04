#!/usr/bin/env python3
"""
Promoter Replicate Scheduler
===========================

Builds a replicate-aware execution matrix for multi-backend IBM Quantum runs
while preserving ibm_fez as the continuity backend and ibm_kingston as the
comparison backend.

The scheduler supports two modes:
1. Dry-run schedule generation (default)
2. Live submission to IBM Quantum (`--submit`)

Usage:
    python agi_scripts/schedule_promoter_replicates.py
    python agi_scripts/schedule_promoter_replicates.py \
        --replicates 5 --backends ibm_fez,ibm_kingston
    python agi_scripts/schedule_promoter_replicates.py \
        --submit --api-key <TOKEN>
"""

import argparse
import csv
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List

try:
    from agi_scripts.submit_to_ibm_quantum import (
        AVAILABLE_BACKENDS,
        QISKIT_AVAILABLE,
        create_promoter_circuit,
        load_comparison_report,
        select_hardware_candidates,
    )
except ModuleNotFoundError:
    from submit_to_ibm_quantum import (
        AVAILABLE_BACKENDS,
        QISKIT_AVAILABLE,
        create_promoter_circuit,
        load_comparison_report,
        select_hardware_candidates,
    )

try:
    from qiskit import transpile
    from qiskit_ibm_runtime import QiskitRuntimeService, Sampler
except ImportError:
    transpile = None
    QiskitRuntimeService = None
    Sampler = None

EXPECTED_RESONANCE = {
    "OXT": 0.786,
    "FOXG1": 0.742,
    "SRY": 0.698,
    "TP53": 0.901,
    "DCTN1": 0.655,
}


DEFAULT_BACKEND_MATRIX = ["ibm_fez", "ibm_kingston"]
DEFAULT_REPLICATES = 3
DEFAULT_SHOTS = 8192


def parse_backend_list(raw_backends: str) -> List[str]:
    """Parse and validate requested backends."""
    backends = [
        item.strip() for item in raw_backends.split(',') if item.strip()
    ]
    invalid = [
        backend for backend in backends if backend not in AVAILABLE_BACKENDS
    ]
    if invalid:
        raise ValueError(f"Unsupported backends: {', '.join(invalid)}")
    if not backends:
        raise ValueError("At least one backend is required")
    return backends


def build_selection_tags(comparison: Dict) -> Dict[str, List[str]]:
    """Map scheduled promoters back to cohort-selection logic."""
    candidates = comparison.get("hardware_selection", {}).get("candidates", [])
    by_phi = comparison.get("rankings", {}).get("by_phi_alignment", [])
    by_entropy = comparison.get("rankings", {}).get("by_entropy", [])

    top_phi = {entry["promoter_id"] for entry in by_phi[:2]}
    high_entropy = {entry["promoter_id"] for entry in by_entropy[:2]}

    selection_tags: Dict[str, List[str]] = {}
    for promoter_id in candidates:
        tags: List[str] = []
        if promoter_id in top_phi:
            tags.append("top_phi_aligned")
        if promoter_id in high_entropy:
            tags.append("high_entropy")
        if not tags:
            tags.append("structural_outlier")
        selection_tags[promoter_id] = tags

    return selection_tags


def get_promoter_records(
    comparison: Dict,
    promoter_ids: List[str],
) -> Dict[str, Dict]:
    """Index promoter rows by ID for fast lookup."""
    promoter_index = {
        promoter["promoter_id"]: promoter
        for promoter in comparison.get("promoters", [])
    }
    return {
        promoter_id: promoter_index[promoter_id]
        for promoter_id in promoter_ids
        if promoter_id in promoter_index
    }


def extract_qubit_layout(transpiled_circuit) -> List[int]:
    """Extract qubit layout in a Qiskit-version-tolerant way."""
    layout = getattr(transpiled_circuit, "layout", None)
    if layout is None:
        return []

    for attr_name in ("final_index_layout", "initial_index_layout"):
        attr = getattr(layout, attr_name, None)
        if callable(attr):
            try:
                indices = attr()
                if indices is not None:
                    return [
                        int(index) for index in indices if index is not None
                    ]
            except (AttributeError, TypeError, ValueError):
                pass

    physical_bits = getattr(layout, "get_physical_bits", None)
    if callable(physical_bits):
        try:
            mapping = physical_bits()
            return sorted(int(index) for index in mapping.keys())
        except (AttributeError, TypeError, ValueError):
            pass

    return []


def make_run_record(
    promoter: Dict,
    backend: str,
    replicate_index: int,
    shots: int,
    selection_tags: List[str],
) -> Dict:
    """Create a single scheduled run record."""
    promoter_id = promoter["promoter_id"]
    predicted_phi = EXPECTED_RESONANCE.get(promoter_id)
    backend_role = (
        "reference_backend"
        if backend == "ibm_fez"
        else "comparison_backend"
    )
    run_id = f"{promoter_id}_{backend}_r{replicate_index:02d}"

    return {
        "run_id": run_id,
        "promoter_id": promoter_id,
        "sephirot_label": promoter.get("sephirot_label"),
        "backend": backend,
        "backend_role": backend_role,
        "replicate_index": replicate_index,
        "shots": shots,
        "selection_tags": selection_tags,
        "cohort_logic_label": ",".join(selection_tags),
        "planned_metrics": {
            "sequence_length": promoter.get("sequence_length"),
            "qubit_count": promoter.get("qubit_count"),
            "predicted_phi": predicted_phi,
            "phi_alignment_score": promoter.get("phi_alignment_score"),
            "entropy_shannon": promoter.get("entropy_shannon"),
            "artifact_id": promoter.get("artifact_id"),
        },
        "execution": {
            "status": "SCHEDULED",
            "job_id": None,
            "submitted_at": None,
            "transpiled_depth": None,
            "qubit_layout": [],
            "backend_timestamp": None,
        },
        "observed_metrics": {
            "measured_phi": None,
            "calibrated_phi": None,
            "residual": None,
            "timestamp": None,
        },
    }


def build_schedule_manifest(
    comparison: Dict,
    promoters: List[str],
    backends: List[str],
    replicates: int,
    shots: int,
) -> Dict:
    """Build the full replicate matrix manifest."""
    promoter_records = get_promoter_records(comparison, promoters)
    selection_tags = build_selection_tags(comparison)

    scheduled_runs: List[Dict] = []
    for promoter_id in promoters:
        promoter = promoter_records[promoter_id]
        tags = selection_tags.get(promoter_id, ["explicit_selection"])
        for backend in backends:
            for replicate_index in range(1, replicates + 1):
                scheduled_runs.append(
                    make_run_record(
                        promoter=promoter,
                        backend=backend,
                        replicate_index=replicate_index,
                        shots=shots,
                        selection_tags=tags,
                    )
                )

    return {
        "manifest_type": "promoter_replicate_schedule",
        "generated_at": datetime.now().isoformat(),
        "reference_backend": "ibm_fez",
        "comparison_backends": [
            backend for backend in backends if backend != "ibm_fez"
        ],
        "replicates_per_backend": replicates,
        "shots_per_run": shots,
        "comparison_report": comparison.get("report_type", "unknown"),
        "comparison_generated_at": comparison.get("generated_at"),
        "selected_promoters": promoters,
        "matrix_dimensions": {
            "promoters": len(promoters),
            "backends": len(backends),
            "replicates": replicates,
            "total_runs": len(scheduled_runs),
        },
        "artifact_metadata": {
            "evidence_class": "secondary",
            "artifact_type": "derived_metrics",
            "artifact_id": (
                "replicate_schedule_"
                f"{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            ),
            "audit_note": (
                "Replicate-aware backend scheduling matrix preserving "
                "ibm_fez continuity baseline"
            ),
            "parent_artifacts": [
                "tmt_os_panel_results/promoter_panel_comparison.json",
            ],
            "data_lineage": {
                "derived_from_prior_runs": True,
                "transform_chain": [
                    "load_comparison_report",
                    "select_promoters",
                    "assign_selection_tags",
                    "expand_backend_replicate_matrix",
                ],
            },
        },
        "scheduled_runs": scheduled_runs,
    }


def initialize_ibm_service(api_key: str):
    """Create IBM Runtime service using the existing project instance."""
    if not QISKIT_AVAILABLE or QiskitRuntimeService is None:
        raise RuntimeError(
            "qiskit and qiskit-ibm-runtime are required for live submission"
        )

    return QiskitRuntimeService(
        channel="ibm_cloud",
        token=api_key,
        instance=(
            "crn:v1:bluemix:public:quantum-computing:us-east:"
            "a/03b6dbec24d04cb4971615d1db2b636a:"
            "950af0f7-51c2-48ac-b1e4-4c4faa584df4::"
        ),
    )


def submit_schedule_runs(
    manifest: Dict,
    comparison: Dict,
    api_key: str,
) -> Dict:
    """Submit all scheduled runs and update the manifest in-place."""
    service = initialize_ibm_service(api_key)
    promoter_lookup = get_promoter_records(
        comparison,
        manifest["selected_promoters"],
    )
    backend_cache = {}

    for run in manifest["scheduled_runs"]:
        backend_name = run["backend"]
        promoter_id = run["promoter_id"]
        promoter_data = promoter_lookup[promoter_id]

        if backend_name not in backend_cache:
            backend_cache[backend_name] = service.backend(backend_name)
        backend = backend_cache[backend_name]

        circuit = create_promoter_circuit(promoter_data)
        transpiled_circuit = transpile(circuit, backend, optimization_level=3)
        sampler = Sampler(backend)
        job = sampler.run([transpiled_circuit], shots=run["shots"])

        run["execution"].update({
            "status": "SUBMITTED",
            "job_id": job.job_id(),
            "submitted_at": datetime.now().isoformat(),
            "transpiled_depth": transpiled_circuit.depth(),
            "qubit_layout": extract_qubit_layout(transpiled_circuit),
            "backend_timestamp": datetime.now().isoformat(),
        })

    return manifest


def save_manifest(manifest: Dict, output_path: Path):
    """Write JSON schedule manifest."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as handle:
        json.dump(manifest, handle, indent=2, ensure_ascii=False)


def save_schedule_csv(manifest: Dict, csv_path: Path):
    """Write a flat CSV for quick inspection."""
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "run_id",
        "promoter_id",
        "sephirot_label",
        "backend",
        "backend_role",
        "replicate_index",
        "shots",
        "cohort_logic_label",
        "predicted_phi",
        "transpiled_depth",
        "qubit_layout",
        "measured_phi",
        "calibrated_phi",
        "residual",
        "job_id",
        "submitted_at",
    ]

    with open(csv_path, 'w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for run in manifest["scheduled_runs"]:
            writer.writerow({
                "run_id": run["run_id"],
                "promoter_id": run["promoter_id"],
                "sephirot_label": run["sephirot_label"],
                "backend": run["backend"],
                "backend_role": run["backend_role"],
                "replicate_index": run["replicate_index"],
                "shots": run["shots"],
                "cohort_logic_label": run["cohort_logic_label"],
                "predicted_phi": run["planned_metrics"].get("predicted_phi"),
                "transpiled_depth": run["execution"].get("transpiled_depth"),
                "qubit_layout": ";".join(
                    str(item)
                    for item in run["execution"].get("qubit_layout", [])
                ),
                "measured_phi": run["observed_metrics"].get("measured_phi"),
                "calibrated_phi": run["observed_metrics"].get(
                    "calibrated_phi"
                ),
                "residual": run["observed_metrics"].get("residual"),
                "job_id": run["execution"].get("job_id"),
                "submitted_at": run["execution"].get("submitted_at"),
            })


def choose_promoters(args, comparison: Dict) -> List[str]:
    """Resolve promoter selection from CLI arguments."""
    if args.promoters:
        return [
            item.strip() for item in args.promoters.split(',') if item.strip()
        ]
    if args.all_promoters:
        return [
            promoter["promoter_id"]
            for promoter in comparison.get("promoters", [])
        ]
    return select_hardware_candidates(comparison)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Schedule replicate-aware multi-backend promoter runs"
    )
    parser.add_argument(
        "--comparison-report",
        default="tmt_os_panel_results/promoter_panel_comparison.json",
        help="Path to promoter comparison report",
    )
    parser.add_argument(
        "--promoters",
        help="Comma-separated promoter IDs; defaults to hardware candidates",
    )
    parser.add_argument(
        "--all-promoters",
        action="store_true",
        help="Schedule all promoters in the comparison report",
    )
    parser.add_argument(
        "--backends",
        default=",".join(DEFAULT_BACKEND_MATRIX),
        help=(
            "Comma-separated backend matrix; default keeps ibm_fez as "
            "reference and ibm_kingston as comparison"
        ),
    )
    parser.add_argument(
        "--replicates",
        type=int,
        default=DEFAULT_REPLICATES,
        help="Replicates per promoter per backend",
    )
    parser.add_argument(
        "--shots",
        type=int,
        default=DEFAULT_SHOTS,
        help="Shots per scheduled run",
    )
    parser.add_argument(
        "--output-json",
        default="raw_hardware/promoter_replicate_schedule_manifest.json",
        help="Output JSON manifest path",
    )
    parser.add_argument(
        "--output-csv",
        default="raw_hardware/promoter_replicate_schedule_matrix.csv",
        help="Output CSV matrix path",
    )
    parser.add_argument(
        "--submit",
        action="store_true",
        help="Submit scheduled runs immediately after building the manifest",
    )
    parser.add_argument(
        "--api-key",
        default=os.environ.get("IBM_QUANTUM_API_KEY"),
        help="IBM Quantum API key; required only with --submit",
    )

    args = parser.parse_args()

    report_path = Path(args.comparison_report)
    if not report_path.exists():
        print(f"Error: comparison report not found: {report_path}")
        return 1

    if args.replicates < 1:
        print("Error: replicates must be >= 1")
        return 1

    try:
        backends = parse_backend_list(args.backends)
    except ValueError as exc:
        print(f"Error: {exc}")
        return 1

    comparison = load_comparison_report(report_path)
    promoters = choose_promoters(args, comparison)
    manifest = build_schedule_manifest(
        comparison=comparison,
        promoters=promoters,
        backends=backends,
        replicates=args.replicates,
        shots=args.shots,
    )

    print("\n" + "=" * 80)
    print("PROMOTER REPLICATE SCHEDULE")
    print("=" * 80)
    print(f"Promoters: {len(promoters)}")
    print(f"Backends: {', '.join(backends)}")
    print(f"Replicates per backend: {args.replicates}")
    print(f"Total runs: {manifest['matrix_dimensions']['total_runs']}")
    print(f"Reference backend: {manifest['reference_backend']}")

    if args.submit:
        if not args.api_key:
            print("Error: --submit requires IBM_QUANTUM_API_KEY or --api-key")
            return 1
        manifest = submit_schedule_runs(manifest, comparison, args.api_key)
        print(
            "Live submission complete; manifest updated with job IDs "
            "and transpiled metadata."
        )
    else:
        print(
            "Dry-run mode: manifest contains scheduled runs with "
            "execution placeholders."
        )

    json_path = Path(args.output_json)
    csv_path = Path(args.output_csv)
    save_manifest(manifest, json_path)
    save_schedule_csv(manifest, csv_path)

    print(f"JSON manifest: {json_path}")
    print(f"CSV matrix: {csv_path}")
    print("=" * 80 + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
