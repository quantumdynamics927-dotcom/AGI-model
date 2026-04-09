#!/usr/bin/env python3
"""
Autonomous Data Inventory Generator
====================================

Analyzes and inventories imported autonomous_data JSON and CSV artifacts,
creating a normalized project-local index for downstream lineage tracking.

Usage:
    python agi_scripts/inventory_autonomous_data.py \
        --import-root data/external_imports/autonomous_data_20260405
"""

import argparse
import csv
import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


# Patterns for parsing filenames
DISCOVERY_PATTERN = re.compile(
    r"discoveries_(?P<date>\d{8})_(?P<time>\d{6})\.json"
)
SUMMARY_PATTERN = re.compile(r"summary_(?P<date>\d{8})_(?P<time>\d{6})\.txt")
PHI_SWEEP_PATTERN = re.compile(
    r"phi_string_sweep_(?P<date>\d{8})_(?P<time>\d{6})\.csv"
)
PHI_UNIVERSALITY_PATTERN = re.compile(
    r"phi_universality_(?P<date>\d{8})_(?P<time>\d{6})\.csv"
)
CONSCIOUSNESS_PATTERN = re.compile(
    r"consciousness_(?P<date>\d{8})_(?P<time>\d{6})\.csv"
)
BIOMOLECULAR_PATTERN = re.compile(
    r"biomolecular_(?P<date>\d{8})_(?P<time>\d{6})\.csv"
)
DNA_QUANTUM_PATTERN = re.compile(
    r"dna_quantum_(?P<date>\d{8})_(?P<time>\d{6})\.csv"
)


def parse_discovery_json(path: Path) -> Dict[str, Any]:
    """Parse a discoveries JSON file and extract metadata."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    match = DISCOVERY_PATTERN.match(path.name)
    session_id = data.get("session_id", "")
    timestamp = data.get("timestamp", "")
    total_discoveries = data.get("total_discoveries", 0)
    discoveries = data.get("discoveries", [])

    # Extract domain distribution
    domain_counts = defaultdict(int)
    for d in discoveries:
        domain = d.get("domain", "unknown")
        domain_counts[domain] += 1

    # Extract phi alignment range if available
    phi_alignments = [
        d.get("phi_alignment")
        for d in discoveries
        if d.get("phi_alignment") is not None
    ]
    phi_range = None
    if phi_alignments:
        phi_range = {
            "min": min(phi_alignments),
            "max": max(phi_alignments),
            "mean": sum(phi_alignments) / len(phi_alignments),
        }

    return {
        "file_path": str(path),
        "file_name": path.name,
        "session_id": session_id,
        "timestamp": timestamp,
        "total_discoveries": total_discoveries,
        "domain_distribution": dict(domain_counts),
        "phi_alignment_range": phi_range,
        "has_consciousness_signatures": any(
            d.get("consciousness_signature") is not None for d in discoveries
        ),
        "has_wormhole_metrics": any(
            d.get("wormhole_entanglement") is not None for d in discoveries
        ),
    }


def parse_csv_artifact(path: Path) -> Dict[str, Any]:
    """Parse a CSV artifact and extract metadata."""
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Extract column names
    columns = list(rows[0].keys()) if rows else []

    # Try to infer data type from filename
    data_type = "unknown"
    if "phi_string" in path.name:
        data_type = "phi_string_sweep"
    elif "phi_universality" in path.name:
        data_type = "phi_universality"
    elif "consciousness" in path.name:
        data_type = "consciousness"
    elif "biomolecular" in path.name:
        data_type = "biomolecular"
    elif "dna_quantum" in path.name:
        data_type = "dna_quantum"

    # Extract numeric ranges for key columns
    numeric_stats = {}
    for col in columns:
        values = []
        for row in rows:
            try:
                val = float(row[col])
                values.append(val)
            except (ValueError, TypeError):
                continue
        if values:
            numeric_stats[col] = {
                "min": min(values),
                "max": max(values),
                "mean": sum(values) / len(values),
            }

    return {
        "file_path": str(path),
        "file_name": path.name,
        "data_type": data_type,
        "row_count": len(rows),
        "columns": columns,
        "numeric_stats": numeric_stats,
    }


def parse_ibm_jobs_json(path: Path) -> Dict[str, Any]:
    """Parse the ibm_jobs.json file and extract job metadata."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    jobs = data.get("jobs", [])
    job_records = []

    for job in jobs:
        job_records.append(
            {
                "job_id": job.get("job_id"),
                "processor": job.get("processor"),
                "circuit": job.get("circuit"),
                "qubits": job.get("qubits"),
                "depth": job.get("depth"),
                "gates": job.get("gates"),
                "execution_date": job.get("execution_date"),
                "structural_entropy": job.get("structural_entropy"),
                "provenance_verified": job.get("provenance_verified", False),
            }
        )

    return {
        "file_path": str(path),
        "file_name": path.name,
        "total_jobs": len(jobs),
        "jobs": job_records,
        "processors": list(set(j.get("processor") for j in jobs if j.get("processor"))),
        "circuits": list(set(j.get("circuit") for j in jobs if j.get("circuit"))),
    }


def parse_qasm_file(path: Path) -> Dict[str, Any]:
    """Parse a QASM file and extract circuit metadata."""
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Count qubits from qreg declarations
    qreg_pattern = re.compile(r"qreg\s+(\w+)\[(\d+)\]")
    creg_pattern = re.compile(r"creg\s+(\w+)\[(\d+)\]")

    qregs = qreg_pattern.findall(content)
    cregs = creg_pattern.findall(content)

    total_qubits = sum(int(n) for _, n in qregs)
    total_cbits = sum(int(n) for _, n in cregs)

    # Count gates
    gate_lines = [
        line for line in content.split("\n") if line.strip() and not line.strip().startswith("//")
    ]
    gate_count = len(gate_lines)

    return {
        "file_path": str(path),
        "file_name": path.name,
        "qreg_count": len(qregs),
        "total_qubits": total_qubits,
        "creg_count": len(cregs),
        "total_cbits": total_cbits,
        "gate_count": gate_count,
        "content_preview": content[:500] if content else "",
    }


def parse_toroidal_wormhole_json(path: Path) -> Dict[str, Any]:
    """Parse toroidal wormhole results JSON."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return {
        "file_path": str(path),
        "file_name": path.name,
        "experiment": data.get("experiment"),
        "timestamp": data.get("timestamp"),
        "n_qubits": data.get("parameters", {}).get("n_qubits"),
        "consciousness_detected": data.get("consciousness_detected"),
        "metrics": data.get("metrics", {}),
        "parameters": data.get("parameters", {}),
    }


def parse_phi_locked_resonance_json(path: Path) -> Dict[str, Any]:
    """Parse phi locked resonance JSON."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return {
        "file_path": str(path),
        "file_name": path.name,
        "timestamp": data.get("timestamp"),
        "phi_locked": data.get("phi_locked", False),
        "resonance_strength": data.get("resonance_strength"),
        "metrics": data.get("metrics", {}),
    }


def parse_portfolio_json(path: Path) -> Dict[str, Any]:
    """Parse portfolio JSON."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return {
        "file_path": str(path),
        "file_name": path.name,
        "portfolio_items": len(data) if isinstance(data, list) else 0,
        "keys": list(data.keys()) if isinstance(data, dict) else [],
    }


def parse_nfts_json(path: Path) -> Dict[str, Any]:
    """Parse NFTs JSON."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    nfts = data.get("nfts", []) if isinstance(data, dict) else data
    return {
        "file_path": str(path),
        "file_name": path.name,
        "nft_count": len(nfts) if isinstance(nfts, list) else 0,
    }


def build_inventory(import_root: Path) -> Dict[str, Any]:
    """Build a complete inventory of autonomous data artifacts."""
    data_dir = import_root / "autonomous_data"

    inventory = {
        "import_root": str(import_root),
        "generated_at": datetime.now().isoformat(),
        "artifacts": {
            "discoveries": [],
            "csv_series": [],
            "ibm_jobs": None,
            "qasm_circuits": [],
            "toroidal_wormhole": None,
            "phi_locked_resonance": None,
            "portfolio": None,
            "nfts": None,
            "summaries": [],
        },
        "summary": {
            "total_discoveries": 0,
            "total_csv_rows": 0,
            "total_ibm_jobs": 0,
            "total_qasm_circuits": 0,
            "domains_found": set(),
        },
    }

    if not data_dir.exists():
        return inventory

    # Scan all files
    for file_path in data_dir.iterdir():
        if not file_path.is_file():
            continue

        try:
            if DISCOVERY_PATTERN.match(file_path.name):
                entry = parse_discovery_json(file_path)
                inventory["artifacts"]["discoveries"].append(entry)
                inventory["summary"]["total_discoveries"] += entry.get(
                    "total_discoveries", 0
                )
                inventory["summary"]["domains_found"].update(
                    entry.get("domain_distribution", {}).keys()
                )

            elif file_path.name == "ibm_jobs.json":
                entry = parse_ibm_jobs_json(file_path)
                inventory["artifacts"]["ibm_jobs"] = entry
                inventory["summary"]["total_ibm_jobs"] = entry.get("total_jobs", 0)

            elif file_path.name == "toroidal_wormhole_results.json":
                entry = parse_toroidal_wormhole_json(file_path)
                inventory["artifacts"]["toroidal_wormhole"] = entry

            elif file_path.name == "phi_locked_resonance_20260101_231552.json":
                entry = parse_phi_locked_resonance_json(file_path)
                inventory["artifacts"]["phi_locked_resonance"] = entry

            elif file_path.name == "portfolio.json":
                entry = parse_portfolio_json(file_path)
                inventory["artifacts"]["portfolio"] = entry

            elif file_path.name == "nfts.json":
                entry = parse_nfts_json(file_path)
                inventory["artifacts"]["nfts"] = entry

            elif file_path.suffix == ".csv":
                entry = parse_csv_artifact(file_path)
                inventory["artifacts"]["csv_series"].append(entry)
                inventory["summary"]["total_csv_rows"] += entry.get("row_count", 0)

            elif file_path.suffix == ".qasm":
                entry = parse_qasm_file(file_path)
                inventory["artifacts"]["qasm_circuits"].append(entry)
                inventory["summary"]["total_qasm_circuits"] += 1

            elif file_path.suffix == ".txt" and SUMMARY_PATTERN.match(file_path.name):
                inventory["artifacts"]["summaries"].append(
                    {"file_path": str(file_path), "file_name": file_path.name}
                )

        except Exception as e:
            print(f"Warning: Failed to parse {file_path.name}: {e}")

    # Convert set to list for JSON serialization
    inventory["summary"]["domains_found"] = sorted(inventory["summary"]["domains_found"])

    return inventory


def resolve_default_import_root() -> Optional[Path]:
    """Resolve the default import root based on project structure."""
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent

    # Look for the most recent autonomous_data import
    imports_dir = project_root / "data" / "external_imports"
    if not imports_dir.exists():
        return None

    candidates = sorted(
        [d for d in imports_dir.iterdir() if d.is_dir() and "autonomous" in d.name],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    return candidates[0] if candidates else None


def main():
    parser = argparse.ArgumentParser(
        description="Inventory imported autonomous data artifacts"
    )
    parser.add_argument(
        "--import-root",
        type=str,
        default=None,
        help=(
            "Project-local import root containing autonomous_data folder "
            "(defaults to most recent)"
        ),
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help=(
            "Output inventory path; defaults to "
            "<import-root>/autonomous_data_inventory.json"
        ),
    )

    args = parser.parse_args()

    import_root = (
        Path(args.import_root) if args.import_root else resolve_default_import_root()
    )
    if not import_root:
        print("Error: Could not resolve import root. Use --import-root.")
        return 1

    print(f"Scanning: {import_root}")
    inventory = build_inventory(import_root)

    output_path = (
        Path(args.output)
        if args.output
        else import_root / "autonomous_data_inventory.json"
    )

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(inventory, f, indent=2, ensure_ascii=False)

    print(f"\nInventory saved: {output_path}")
    print(f"  Discoveries: {inventory['summary']['total_discoveries']}")
    print(f"  IBM Jobs: {inventory['summary']['total_ibm_jobs']}")
    print(f"  QASM Circuits: {inventory['summary']['total_qasm_circuits']}")
    print(f"  CSV Rows: {inventory['summary']['total_csv_rows']}")
    print(f"  Domains: {', '.join(inventory['summary']['domains_found'])}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
