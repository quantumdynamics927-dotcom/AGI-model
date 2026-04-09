#!/usr/bin/env python3
"""
Autonomous Data Lineage Connector
=================================

Connects imported autonomous_data IBM jobs and QASM assets to the existing
lineage validation and hardware-analysis pipeline in AGI-model.

Usage:
    python agi_scripts/connect_autonomous_lineage.py \
        --inventory data/external_imports/autonomous_data_20260405/autonomous_data_inventory.json \
        --output-dir raw_hardware/autonomous_imports
"""

import argparse
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


# Artifact type constants (from validate_artifact_lineage.py)
ARTIFACT_TYPE_RAW_HARDWARE = "raw_hardware"
ARTIFACT_TYPE_DERIVED_METRICS = "derived_metrics"
ARTIFACT_TYPE_RECONSTRUCTED = "reconstructed"

# Evidence class constants
EVIDENCE_CLASS_PRIMARY = "primary"
EVIDENCE_CLASS_SECONDARY = "secondary"


def create_raw_hardware_artifact(
    job_record: Dict[str, Any],
    source_file: str,
    import_provenance: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Create a raw_hardware artifact from an imported IBM job record.
    Compatible with validate_artifact_lineage.py expectations.
    """
    job_id = job_record.get("job_id", "unknown")
    circuit = job_record.get("circuit", "unknown")
    processor = job_record.get("processor", "unknown")
    execution_date = job_record.get("execution_date", datetime.now().isoformat())

    artifact_id = f"autonomous_{circuit}_{job_id}"

    return {
        "artifact_metadata": {
            "artifact_type": ARTIFACT_TYPE_RAW_HARDWARE,
            "evidence_class": EVIDENCE_CLASS_PRIMARY,
            "artifact_id": artifact_id,
            "created_at": datetime.now().isoformat(),
            "parent_artifacts": [source_file],
            "provenance": {
                "vendor": "IBM Quantum",
                "vendor_job_id": job_id,
                "backend": processor,
                "execution_date": execution_date,
                "circuit_name": circuit,
                "qubits_used": job_record.get("qubits"),
                "circuit_depth": job_record.get("depth"),
                "gate_count": job_record.get("gates"),
                "structural_entropy": job_record.get("structural_entropy"),
                "provenance_verified": job_record.get("provenance_verified", False),
            },
            "data_lineage": {
                "sources": [import_provenance.get("import_root", "unknown")],
                "imported_at": import_provenance.get("imported_at"),
                "original_source": import_provenance.get("original_source"),
            },
            "audit_note": (
                f"Imported from autonomous_data. "
                f"Original execution: {execution_date}. "
                f"Processor: {processor}."
            ),
        },
        "hardware_results": {
            "job_id": job_id,
            "circuit": circuit,
            "processor": processor,
            "metrics": {
                "qubits": job_record.get("qubits"),
                "depth": job_record.get("depth"),
                "gates": job_record.get("gates"),
                "structural_entropy": job_record.get("structural_entropy"),
            },
        },
    }


def create_derived_metrics_artifact(
    discovery_entry: Dict[str, Any],
    source_file: str,
    import_provenance: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """
    Create a derived_metrics artifact from discovery data.
    Only creates if the discovery has meaningful metrics.
    """
    session_id = discovery_entry.get("session_id", "unknown")
    timestamp = discovery_entry.get("timestamp", datetime.now().isoformat())

    # Skip empty discoveries
    if discovery_entry.get("total_discoveries", 0) == 0:
        return None

    artifact_id = f"autonomous_discoveries_{session_id}"

    return {
        "artifact_metadata": {
            "artifact_type": ARTIFACT_TYPE_DERIVED_METRICS,
            "evidence_class": EVIDENCE_CLASS_SECONDARY,
            "artifact_id": artifact_id,
            "created_at": datetime.now().isoformat(),
            "parent_artifacts": [source_file],
            "data_lineage": {
                "sources": [import_provenance.get("import_root", "unknown")],
                "transform_chain": ["parse_discovery_json", "extract_metrics"],
                "imported_at": import_provenance.get("imported_at"),
            },
            "audit_note": (
                f"Derived from autonomous discovery session {session_id}. "
                f"Total discoveries: {discovery_entry.get('total_discoveries', 0)}. "
                f"Domains: {', '.join(discovery_entry.get('domain_distribution', {}).keys())}."
            ),
        },
        "derived_metrics": {
            "session_id": session_id,
            "timestamp": timestamp,
            "total_discoveries": discovery_entry.get("total_discoveries", 0),
            "domain_distribution": discovery_entry.get("domain_distribution", {}),
            "phi_alignment_range": discovery_entry.get("phi_alignment_range"),
            "has_consciousness_signatures": discovery_entry.get(
                "has_consciousness_signatures", False
            ),
            "has_wormhole_metrics": discovery_entry.get("has_wormhole_metrics", False),
        },
    }


def create_qasm_lineage_record(
    qasm_entry: Dict[str, Any],
    source_file: str,
    import_provenance: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Create a lineage record for a QASM circuit.
    QASM files are treated as reconstructed artifacts (source code).
    """
    file_name = qasm_entry.get("file_name", "unknown")
    base_name = Path(file_name).stem

    return {
        "artifact_metadata": {
            "artifact_type": ARTIFACT_TYPE_RECONSTRUCTED,
            "evidence_class": EVIDENCE_CLASS_SECONDARY,
            "artifact_id": f"autonomous_qasm_{base_name}",
            "created_at": datetime.now().isoformat(),
            "parent_artifacts": [source_file],
            "data_lineage": {
                "sources": [import_provenance.get("import_root", "unknown")],
                "transform_chain": ["import_qasm", "parse_metadata"],
                "derived_from_prior_runs": False,
                "imported_at": import_provenance.get("imported_at"),
            },
            "audit_note": (
                f"Imported QASM circuit: {file_name}. "
                f"Qubits: {qasm_entry.get('total_qubits', 'unknown')}. "
                f"Gates: {qasm_entry.get('gate_count', 'unknown')}."
            ),
        },
        "circuit_metadata": {
            "file_name": file_name,
            "total_qubits": qasm_entry.get("total_qubits"),
            "total_cbits": qasm_entry.get("total_cbits"),
            "gate_count": qasm_entry.get("gate_count"),
            "qreg_count": qasm_entry.get("qreg_count"),
            "creg_count": qasm_entry.get("creg_count"),
        },
    }


def link_to_hardware_analysis(
    job_records: List[Dict[str, Any]],
    output_path: Path,
) -> None:
    """
    Create a hardware analysis input file compatible with analyze_ibm_hardware_jobs.py.
    """
    analysis_input = {
        "generated_at": datetime.now().isoformat(),
        "source": "autonomous_data_import",
        "jobs": [],
    }

    for job in job_records:
        analysis_input["jobs"].append(
            {
                "job_id": job.get("job_id"),
                "processor": job.get("processor"),
                "circuit": job.get("circuit"),
                "qubits": job.get("qubits"),
                "depth": job.get("depth"),
                "gates": job.get("gates"),
                "execution_date": job.get("execution_date"),
                "structural_entropy": job.get("structural_entropy"),
            }
        )

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(analysis_input, f, indent=2, ensure_ascii=False)


def build_lineage_manifest(
    inventory_path: Path,
    output_dir: Path,
) -> Dict[str, Any]:
    """
    Build a complete lineage manifest connecting autonomous data to AGI-model pipeline.
    """
    with open(inventory_path, "r", encoding="utf-8") as f:
        inventory = json.load(f)

    import_root = inventory.get("import_root", str(inventory_path.parent))
    import_provenance = {
        "import_root": import_root,
        "imported_at": inventory.get("generated_at", datetime.now().isoformat()),
        "original_source": "E:\\tmt-os\\autonomous_data",
    }

    manifest = {
        "manifest_type": "autonomous_data_lineage",
        "generated_at": datetime.now().isoformat(),
        "import_provenance": import_provenance,
        "artifacts": {
            "raw_hardware": [],
            "derived_metrics": [],
            "reconstructed": [],
        },
        "hardware_analysis_input": None,
        "validation_summary": {
            "total_raw_hardware": 0,
            "total_derived_metrics": 0,
            "total_reconstructed": 0,
        },
    }

    # Create output directories
    raw_hardware_dir = output_dir / "raw_hardware"
    derived_metrics_dir = output_dir / "derived_metrics"
    reconstructed_dir = output_dir / "reconstructed"

    raw_hardware_dir.mkdir(parents=True, exist_ok=True)
    derived_metrics_dir.mkdir(parents=True, exist_ok=True)
    reconstructed_dir.mkdir(parents=True, exist_ok=True)

    # Process IBM jobs -> raw_hardware artifacts
    ibm_jobs = inventory.get("artifacts", {}).get("ibm_jobs")
    if ibm_jobs and ibm_jobs.get("jobs"):
        source_file = ibm_jobs.get("file_name", "ibm_jobs.json")

        for job in ibm_jobs["jobs"]:
            artifact = create_raw_hardware_artifact(
                job, source_file, import_provenance
            )
            artifact_id = artifact["artifact_metadata"]["artifact_id"]

            # Write artifact
            artifact_path = raw_hardware_dir / f"{artifact_id}.json"
            with open(artifact_path, "w", encoding="utf-8") as f:
                json.dump(artifact, f, indent=2, ensure_ascii=False)

            manifest["artifacts"]["raw_hardware"].append(
                {
                    "artifact_id": artifact_id,
                    "path": str(artifact_path.relative_to(output_dir)),
                    "job_id": job.get("job_id"),
                    "circuit": job.get("circuit"),
                }
            )

        # Create hardware analysis input
        analysis_input_path = output_dir / "autonomous_hardware_analysis_input.json"
        link_to_hardware_analysis(ibm_jobs["jobs"], analysis_input_path)
        manifest["hardware_analysis_input"] = str(
            analysis_input_path.relative_to(output_dir)
        )

    # Process discoveries -> derived_metrics artifacts
    discoveries = inventory.get("artifacts", {}).get("discoveries", [])
    for discovery in discoveries:
        source_file = discovery.get("file_name", "unknown")
        artifact = create_derived_metrics_artifact(
            discovery, source_file, import_provenance
        )

        if artifact:
            artifact_id = artifact["artifact_metadata"]["artifact_id"]

            # Write artifact
            artifact_path = derived_metrics_dir / f"{artifact_id}.json"
            with open(artifact_path, "w", encoding="utf-8") as f:
                json.dump(artifact, f, indent=2, ensure_ascii=False)

            manifest["artifacts"]["derived_metrics"].append(
                {
                    "artifact_id": artifact_id,
                    "path": str(artifact_path.relative_to(output_dir)),
                    "session_id": discovery.get("session_id"),
                    "total_discoveries": discovery.get("total_discoveries", 0),
                }
            )

    # Process QASM circuits -> reconstructed artifacts
    qasm_circuits = inventory.get("artifacts", {}).get("qasm_circuits", [])
    for qasm in qasm_circuits:
        source_file = qasm.get("file_name", "unknown")
        record = create_qasm_lineage_record(qasm, source_file, import_provenance)
        artifact_id = record["artifact_metadata"]["artifact_id"]

        # Write lineage record
        record_path = reconstructed_dir / f"{artifact_id}.json"
        with open(record_path, "w", encoding="utf-8") as f:
            json.dump(record, f, indent=2, ensure_ascii=False)

        manifest["artifacts"]["reconstructed"].append(
            {
                "artifact_id": artifact_id,
                "path": str(record_path.relative_to(output_dir)),
                "file_name": qasm.get("file_name"),
                "total_qubits": qasm.get("total_qubits"),
            }
        )

    # Update validation summary
    manifest["validation_summary"]["total_raw_hardware"] = len(
        manifest["artifacts"]["raw_hardware"]
    )
    manifest["validation_summary"]["total_derived_metrics"] = len(
        manifest["artifacts"]["derived_metrics"]
    )
    manifest["validation_summary"]["total_reconstructed"] = len(
        manifest["artifacts"]["reconstructed"]
    )

    return manifest


def main():
    parser = argparse.ArgumentParser(
        description="Connect imported autonomous data to AGI-model lineage pipeline"
    )
    parser.add_argument(
        "--inventory",
        type=str,
        required=True,
        help="Path to autonomous_data_inventory.json",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="raw_hardware/autonomous_imports",
        help="Output directory for lineage artifacts",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Run lineage validation after creating artifacts",
    )

    args = parser.parse_args()

    inventory_path = Path(args.inventory)
    output_dir = Path(args.output_dir)

    if not inventory_path.exists():
        print(f"Error: Inventory not found: {inventory_path}")
        return 1

    print(f"Loading inventory: {inventory_path}")
    print(f"Output directory: {output_dir}")

    # Build lineage manifest
    manifest = build_lineage_manifest(inventory_path, output_dir)

    # Write manifest
    manifest_path = output_dir / "autonomous_lineage_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"\nLineage manifest: {manifest_path}")
    print(f"  Raw hardware artifacts: {manifest['validation_summary']['total_raw_hardware']}")
    print(f"  Derived metrics artifacts: {manifest['validation_summary']['total_derived_metrics']}")
    print(f"  Reconstructed artifacts: {manifest['validation_summary']['total_reconstructed']}")

    if manifest["hardware_analysis_input"]:
        print(f"  Hardware analysis input: {manifest['hardware_analysis_input']}")

    # Optionally run validation
    if args.validate:
        print("\nRunning lineage validation...")
        try:
            import subprocess

            result = subprocess.run(
                [
                    "python",
                    "agi_scripts/validate_artifact_lineage.py",
                    "--dir",
                    str(output_dir),
                ],
                capture_output=True,
                text=True,
            )
            print(result.stdout)
            if result.returncode != 0:
                print("Validation completed with warnings/errors")
        except Exception as e:
            print(f"Validation failed: {e}")

    print("\nTo validate artifacts manually:")
    print(f"  python agi_scripts/validate_artifact_lineage.py --dir {output_dir}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
