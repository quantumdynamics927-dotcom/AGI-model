"""
Pure-python SDF (MOL) file parser for QM9 molecular geometries.

Parses the OEChem SDF format from QM9 (gdb9.sdf), extracting:
  - Atomic positions (num_atoms, 3)
  - Atomic numbers (num_atoms,)
  - Molecular properties from the CSV sidecar

Format reference (V2000):
  - Line 1: molecule name
  - Line 2: comment/OEChem header
  - Line 3: counts line: natoms nbonds ... (V2000)
  - Atom block: natoms lines of X Y Z Element ...
  - Bond block: nbonds lines of a1 a2 type ...
  - M END
  - $$$$ separator
"""

import re
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional, Tuple


ELEMENT_NUMBERS = {
    "H": 1, "He": 2, "Li": 3, "Be": 4, "B": 5, "C": 6, "N": 7, "O": 8,
    "F": 9, "Ne": 10, "Na": 11, "Mg": 12, "Al": 13, "Si": 14, "P": 15,
    "S": 16, "Cl": 17, "Ar": 18, "K": 19, "Ca": 20, "Fe": 26,
}


def parse_counts_line(line: str) -> Tuple[int, int]:
    """Parse the V2000 counts line: natoms nbonds ..."""
    parts = line.split()
    natoms = int(parts[0])
    nbonds = int(parts[1])
    return natoms, nbonds


def parse_sdf_molecule(lines: List[str]) -> Optional[Dict]:
    """
    Parse a single molecule block from SDF.
    Returns dict with positions, atomic_numbers, name, or None on parse failure.
    """
    if not lines:
        return None

    name = lines[0].strip()

    # Skip blank line and header
    idx = 1
    while idx < len(lines) and not lines[idx].strip():
        idx += 1
    if idx >= len(lines):
        return None
    idx += 1  # skip header line

    while idx < len(lines) and not lines[idx].strip():
        idx += 1
    if idx >= len(lines):
        return None

    # Counts line
    try:
        natoms, nbonds = parse_counts_line(lines[idx])
    except (ValueError, IndexError):
        return None
    idx += 1

    # Atom block
    positions = []
    atomic_numbers = []
    for _ in range(natoms):
        if idx >= len(lines):
            return None
        parts = lines[idx].split()
        if len(parts) < 4:
            return None
        try:
            x, y, z = float(parts[0]), float(parts[1]), float(parts[2])
            elem = parts[3]
        except (ValueError, IndexError):
            return None
        positions.append([x, y, z])
        atomic_numbers.append(ELEMENT_NUMBERS.get(elem, 0))
        idx += 1

    # Bond block
    for _ in range(nbonds):
        if idx >= len(lines):
            break
        idx += 1

    return {
        "name": name,
        "positions": np.array(positions, dtype=np.float32),
        "atomic_numbers": np.array(atomic_numbers, dtype=np.int32),
    }


def load_qm9_sdf(sdf_path: str, max_molecules: int = 0) -> List[Dict]:
    """
    Load molecular data from QM9 SDF file.

    Args:
        sdf_path: path to gdb9.sdf
        max_molecules: 0 = all, otherwise limit count

    Returns:
        List of dicts with keys: name, positions (N×3), atomic_numbers (N,)
    """
    with open(sdf_path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    # Split into molecule blocks by $$$$ separator
    raw_blocks = content.split("$$$$")
    molecules = []
    skipped = 0

    for block in raw_blocks:
        lines = block.strip().split("\n")
        if not lines or not lines[0].strip():
            continue

        mol = parse_sdf_molecule(lines)
        if mol is None or mol["atomic_numbers"].sum() == 0:
            skipped += 1
            continue

        molecules.append(mol)
        if max_molecules > 0 and len(molecules) >= max_molecules:
            break

    print(f"[QM9 SDF] Loaded {len(molecules)} molecules, {skipped} skipped")
    return molecules


def load_qm9_csv(csv_path: str, max_rows: int = 0) -> Dict[int, Dict]:
    """
    Load QM9 property CSV (gdb9.sdf.csv).

    Returns dict keyed by 0-based molecule index.
    """
    import csv

    properties = {}
    with open(csv_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if max_rows > 0 and i >= max_rows:
                break
            idx = int(row["#"])
            props = {}
            for key, val in row.items():
                if key == "#":
                    continue
                try:
                    props[key] = float(val)
                except ValueError:
                    props[key] = val
            properties[idx] = props

    return properties


if __name__ == "__main__":
    import sys

    sdf_path = sys.argv[1] if len(sys.argv) > 1 else "qm9_data/raw/gdb9.sdf"
    max_n = int(sys.argv[2]) if len(sys.argv) > 2 else 100

    print(f"Loading from: {sdf_path}")
    mols = load_qm9_sdf(sdf_path, max_molecules=max_n)
    print(f"Loaded {len(mols)} molecules")
    if mols:
        m = mols[0]
        print(f"  First: {m['name']}, {len(m['atomic_numbers'])} atoms")
        print(f"  Elements: {m['atomic_numbers']}")
        print(f"  Positions shape: {m['positions'].shape}")
