"""Dataset and file parsers for Molecular Geometry node.
Simple XYZ parser used for tests and lightweight integrations.
"""
from pathlib import Path
from typing import List, Tuple


def parse_xyz(path_or_str) -> dict:
    """Parse a simple XYZ formatted string or file and return a dict with name, atoms, coords"""
    if isinstance(path_or_str, Path):
        s = path_or_str.read_text()
    else:
        s = str(path_or_str)
    lines = [ln.strip() for ln in s.splitlines() if ln.strip()]
    if len(lines) < 3:
        raise ValueError('Invalid XYZ data')
    try:
        n = int(lines[0])
        name = lines[1]
        atom_lines = lines[2:2+n]
    except Exception:
        # fallback: try to parse all lines after header as atoms
        name = lines[0]
        atom_lines = lines[1:]
    atoms = []
    coords = []
    for ln in atom_lines:
        parts = ln.split()
        if len(parts) < 4:
            continue
        atoms.append(parts[0])
        coords.append((float(parts[1]), float(parts[2]), float(parts[3])))
    return {'name': name, 'atoms': atoms, 'coords': coords}
