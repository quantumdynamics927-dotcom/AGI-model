#!/usr/bin/env python3
"""
Imported Promoter Asset Inventory
================================

Analyzes imported promoter FASTA and QASM assets copied into the project and
emits a normalized inventory JSON that downstream pipeline stages can consume.

Usage:
    python agi_scripts/inventory_imported_promoter_assets.py
    python agi_scripts/inventory_imported_promoter_assets.py \
        --import-root data/external_imports/tmt_os_20260405
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


FASTA_HEADER_RE = re.compile(
    r"^>(?P<gene>[^|]+)\|(?P<label>[^|]+)\|(?P<ensembl>[^|]+)\|"
    r"(?P<assembly>[^|]+)\|(?P<coords>[^|]+)$"
)
QREG_RE = re.compile(r"^qreg\s+\w+\[(\d+)\];$")
CREG_RE = re.compile(r"^creg\s+\w+\[(\d+)\];$")


def parse_fasta(path: Path) -> Dict:
    lines = path.read_text(encoding="utf-8").splitlines()
    header = lines[0].strip() if lines else ""
    sequence = "".join(line.strip() for line in lines[1:] if line.strip())
    match = FASTA_HEADER_RE.match(header)

    header_data = {
        "raw_header": header,
        "assembly": None,
        "coordinates": None,
        "ensembl_gene_id": None,
        "header_gene": None,
        "header_label": None,
    }
    if match:
        header_data.update({
            "assembly": match.group("assembly"),
            "coordinates": match.group("coords"),
            "ensembl_gene_id": match.group("ensembl"),
            "header_gene": match.group("gene"),
            "header_label": match.group("label"),
        })

    gc_count = sequence.upper().count("G") + sequence.upper().count("C")
    stem_parts = path.stem.split("_")
    gene_name = stem_parts[0] if stem_parts else path.stem
    sephirot_label = stem_parts[1] if len(stem_parts) > 1 else None

    return {
        "gene_name": gene_name,
        "sephirot_label": sephirot_label,
        "file_path": str(path),
        "file_name": path.name,
        "sequence_length": len(sequence),
        "gc_content": (gc_count / len(sequence)) if sequence else 0.0,
        "sequence_preview": sequence[:20],
        "header": header_data,
    }


def parse_qasm(path: Path) -> Dict:
    lines = path.read_text(encoding="utf-8").splitlines()
    qreg_size: Optional[int] = None
    creg_sizes: List[int] = []

    for line in lines:
        stripped = line.strip()
        qreg_match = QREG_RE.match(stripped)
        if qreg_match:
            qreg_size = int(qreg_match.group(1))
        creg_match = CREG_RE.match(stripped)
        if creg_match:
            creg_sizes.append(int(creg_match.group(1)))

    stem_parts = path.stem.split("_")
    gene_name = stem_parts[0] if stem_parts else path.stem
    sephirot_label = stem_parts[1] if len(stem_parts) > 1 else None

    return {
        "gene_name": gene_name,
        "sephirot_label": sephirot_label,
        "file_path": str(path),
        "file_name": path.name,
        "declared_qubits": qreg_size,
        "declared_classical_registers": creg_sizes,
        "line_count": len(lines),
    }


def load_promoter_manifest_csv(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def build_inventory(import_root: Path) -> Dict:
    fasta_31_dir = import_root / "promoters_fasta_31bp"
    fasta_81_dir = import_root / "promoters_fasta_81bp"
    qasm_dir = import_root / "promoter_qasm"

    fasta_31_entries = [
        parse_fasta(path)
        for path in sorted(fasta_31_dir.glob("*_promoter.fa"))
    ]
    fasta_81_entries = [
        parse_fasta(path)
        for path in sorted(fasta_81_dir.glob("*_promoter.fa"))
    ]
    qasm_entries = [
        parse_qasm(path)
        for path in sorted(qasm_dir.glob("*.qasm"))
    ]

    promoter_index: Dict[str, Dict] = {}
    for entry in fasta_31_entries:
        promoter_index.setdefault(entry["gene_name"], {})["fasta_31bp"] = entry
    for entry in fasta_81_entries:
        promoter_index.setdefault(entry["gene_name"], {})["fasta_81bp"] = entry
    for entry in qasm_entries:
        promoter_index.setdefault(
            entry["gene_name"], {}
        )["promoter_qasm"] = entry

    for promoter_id, assets in promoter_index.items():
        lengths = []
        for key in ("fasta_31bp", "fasta_81bp"):
            if key in assets:
                lengths.append(assets[key]["sequence_length"])
        qasm_qubits = None
        if "promoter_qasm" in assets:
            qasm_qubits = assets["promoter_qasm"].get("declared_qubits")
        assets["consistency"] = {
            "has_fasta_31bp": "fasta_31bp" in assets,
            "has_fasta_81bp": "fasta_81bp" in assets,
            "has_promoter_qasm": "promoter_qasm" in assets,
            "fasta_lengths": lengths,
            "qasm_declared_qubits": qasm_qubits,
            "qasm_matches_31bp": qasm_qubits == 31,
            "shared_sephirot_label": next(
                (
                    assets[name]["sephirot_label"]
                    for name in ("fasta_31bp", "fasta_81bp", "promoter_qasm")
                    if name in assets and assets[name].get("sephirot_label")
                ),
                None,
            ),
        }

    manifest_rows = {
        "31bp": load_promoter_manifest_csv(
            fasta_31_dir / "promoters_manifest.csv"
        ),
        "81bp": load_promoter_manifest_csv(
            fasta_81_dir / "promoters_manifest.csv"
        ),
    }

    promoters = []
    for promoter_id in sorted(promoter_index):
        assets = promoter_index[promoter_id]
        promoters.append({
            "promoter_id": promoter_id,
            **assets,
        })

    return {
        "inventory_type": "imported_promoter_assets",
        "generated_at": datetime.now().isoformat(),
        "import_root": str(import_root),
        "asset_sets": {
            "promoters_fasta_31bp": {
                "path": str(fasta_31_dir),
                "count": len(fasta_31_entries),
                "manifest_rows": manifest_rows["31bp"],
            },
            "promoters_fasta_81bp": {
                "path": str(fasta_81_dir),
                "count": len(fasta_81_entries),
                "manifest_rows": manifest_rows["81bp"],
            },
            "promoter_qasm": {
                "path": str(qasm_dir),
                "count": len(qasm_entries),
            },
        },
        "summary": {
            "promoters_with_all_assets": sum(
                1
                for promoter in promoters
                if promoter["consistency"]["has_fasta_31bp"]
                and promoter["consistency"]["has_fasta_81bp"]
                and promoter["consistency"]["has_promoter_qasm"]
            ),
            "total_promoters": len(promoters),
            "fasta_31bp_count": len(fasta_31_entries),
            "fasta_81bp_count": len(fasta_81_entries),
            "promoter_qasm_count": len(qasm_entries),
        },
        "promoters": promoters,
    }


def resolve_default_import_root() -> Optional[Path]:
    base = Path("data/external_imports")
    if not base.exists():
        return None
    candidates = sorted(path for path in base.iterdir() if path.is_dir())
    return candidates[-1] if candidates else None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inventory imported promoter FASTA and QASM assets"
    )
    parser.add_argument(
        "--import-root",
        help=(
            "Project-local import root containing promoter FASTA and "
            "QASM folders"
        ),
    )
    parser.add_argument(
        "--output",
        help=(
            "Output inventory path; defaults to "
            "<import-root>/promoter_asset_inventory.json"
        ),
    )
    args = parser.parse_args()

    import_root = (
        Path(args.import_root)
        if args.import_root
        else resolve_default_import_root()
    )
    if import_root is None or not import_root.exists():
        print("Error: import root not found")
        return 1

    inventory = build_inventory(import_root)
    output_path = (
        Path(args.output)
        if args.output
        else import_root / "promoter_asset_inventory.json"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(inventory, handle, indent=2, ensure_ascii=False)

    print(f"Inventory saved: {output_path}")
    print(f"Promoters inventoried: {inventory['summary']['total_promoters']}")
    print(
        "Promoters with 31bp FASTA, 81bp FASTA, and promoter QASM: "
        f"{inventory['summary']['promoters_with_all_assets']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
