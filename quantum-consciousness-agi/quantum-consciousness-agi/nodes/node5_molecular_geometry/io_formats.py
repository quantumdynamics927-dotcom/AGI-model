"""File format readers and writers for molecular structures.

Supports multiple common molecular file formats:
- XYZ: Simple Cartesian coordinates
- PDB: Protein Data Bank format
- MOL2: Tripos MOL2 format
- SDF/MOL: MDL Structure Data Format
"""
from __future__ import annotations
from pathlib import Path
from typing import Union, List, Optional, Dict, Any, TextIO
import re
import json

from .structures import Molecule, Atom, Bond, BondOrder
from .constants import ATOMIC_NUMBERS, ELEMENT_SYMBOLS


class MoleculeIO:
    """Unified molecular file I/O handler."""

    # Format detection patterns
    FORMAT_PATTERNS = {
        'xyz': r'^\s*\d+\s*$',  # First line is atom count
        'pdb': r'^(ATOM|HETATM|HEADER|CRYST)',
        'mol2': r'@<TRIPOS>',
        'sdf': r'^\s*\n.*\n.*\n.*V[23]000',
    }

    @classmethod
    def read(cls, path: Union[str, Path], format: Optional[str] = None) -> Molecule:
        """Read molecule from file.

        Args:
            path: File path
            format: Format hint ('xyz', 'pdb', 'mol2', 'sdf', 'json')
                   If None, auto-detected from extension or content

        Returns:
            Molecule object
        """
        path = Path(path)
        content = path.read_text()

        if format is None:
            format = cls._detect_format(path, content)

        readers = {
            'xyz': cls.read_xyz,
            'pdb': cls.read_pdb,
            'mol2': cls.read_mol2,
            'sdf': cls.read_sdf,
            'mol': cls.read_sdf,
            'json': cls.read_json,
        }

        reader = readers.get(format.lower())
        if reader is None:
            raise ValueError(f"Unsupported format: {format}")

        return reader(content, name=path.stem)

    @classmethod
    def write(cls, molecule: Molecule, path: Union[str, Path],
              format: Optional[str] = None) -> Path:
        """Write molecule to file.

        Args:
            molecule: Molecule to write
            path: Output file path
            format: Format ('xyz', 'pdb', 'mol2', 'sdf', 'json')
                   If None, detected from extension

        Returns:
            Path to written file
        """
        path = Path(path)

        if format is None:
            format = path.suffix.lstrip('.').lower()
            if not format:
                format = 'xyz'

        writers = {
            'xyz': cls.write_xyz,
            'pdb': cls.write_pdb,
            'json': cls.write_json,
        }

        writer = writers.get(format.lower())
        if writer is None:
            raise ValueError(f"Unsupported write format: {format}")

        content = writer(molecule)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return path

    @classmethod
    def _detect_format(cls, path: Path, content: str) -> str:
        """Auto-detect file format."""
        # Try extension first
        ext = path.suffix.lstrip('.').lower()
        if ext in ['xyz', 'pdb', 'mol2', 'sdf', 'mol', 'json']:
            return ext

        # Try content patterns
        lines = content.split('\n')
        first_lines = '\n'.join(lines[:10])

        if re.search(cls.FORMAT_PATTERNS['pdb'], first_lines, re.MULTILINE):
            return 'pdb'
        if re.search(cls.FORMAT_PATTERNS['mol2'], content):
            return 'mol2'
        if re.search(cls.FORMAT_PATTERNS['sdf'], content, re.MULTILINE):
            return 'sdf'

        # Default to XYZ
        try:
            int(lines[0].strip())
            return 'xyz'
        except ValueError:
            pass

        return 'xyz'

    # ==================== XYZ Format ====================

    @classmethod
    def read_xyz(cls, content: str, name: str = 'molecule') -> Molecule:
        """Parse XYZ format.

        Format:
            <n_atoms>
            <comment/name>
            <element> <x> <y> <z>
            ...
        """
        lines = [ln.strip() for ln in content.splitlines() if ln.strip()]

        if len(lines) < 3:
            raise ValueError("Invalid XYZ format: too few lines")

        try:
            n_atoms = int(lines[0])
            mol_name = lines[1] if lines[1] else name
            atom_lines = lines[2:2 + n_atoms]
        except ValueError:
            # Fallback: no header
            mol_name = name
            atom_lines = lines

        mol = Molecule(name=mol_name)

        for i, line in enumerate(atom_lines):
            parts = line.split()
            if len(parts) < 4:
                continue

            symbol = parts[0]
            try:
                x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
            except ValueError:
                continue

            mol.add_atom(Atom(symbol=symbol, position=(x, y, z), index=i))

        return mol

    @classmethod
    def write_xyz(cls, molecule: Molecule) -> str:
        """Write XYZ format."""
        lines = [
            str(molecule.n_atoms),
            molecule.name or 'molecule',
        ]

        for atom in molecule.atoms:
            lines.append(f"{atom.symbol:2s} {atom.x:15.8f} {atom.y:15.8f} {atom.z:15.8f}")

        return '\n'.join(lines) + '\n'

    # ==================== PDB Format ====================

    @classmethod
    def read_pdb(cls, content: str, name: str = 'molecule') -> Molecule:
        """Parse PDB format.

        Reads ATOM and HETATM records.
        """
        mol = Molecule(name=name)
        idx = 0

        for line in content.splitlines():
            record = line[:6].strip()

            if record in ('ATOM', 'HETATM'):
                try:
                    # PDB format columns (1-indexed in spec, 0-indexed here)
                    # atom_num = int(line[6:11])
                    # atom_name = line[12:16].strip()
                    # alt_loc = line[16]
                    residue = line[17:20].strip()
                    chain = line[21]
                    # res_num = int(line[22:26])
                    x = float(line[30:38])
                    y = float(line[38:46])
                    z = float(line[46:54])

                    # Element is in columns 77-78, or parse from atom name
                    if len(line) >= 78:
                        symbol = line[76:78].strip()
                    else:
                        # Extract from atom name
                        atom_name = line[12:16].strip()
                        symbol = ''.join(c for c in atom_name if c.isalpha())[:2]

                    if not symbol:
                        symbol = 'C'

                    mol.add_atom(Atom(
                        symbol=symbol,
                        position=(x, y, z),
                        index=idx,
                        residue=residue if residue else None,
                        chain=chain if chain.strip() else None,
                    ))
                    idx += 1

                except (ValueError, IndexError):
                    continue

            elif record == 'TITLE':
                mol.name = line[10:].strip() or name

        return mol

    @classmethod
    def write_pdb(cls, molecule: Molecule) -> str:
        """Write PDB format."""
        lines = [f"TITLE     {molecule.name}"]

        for i, atom in enumerate(molecule.atoms):
            # Format: ATOM serial name resName chainID resSeq x y z occupancy tempFactor element
            atom_name = atom.symbol.ljust(4)
            residue = (atom.residue or 'UNK')[:3].ljust(3)
            chain = atom.chain or ' '

            line = (
                f"HETATM{i+1:5d} {atom_name:4s} {residue:3s} {chain:1s}"
                f"{1:4d}    {atom.x:8.3f}{atom.y:8.3f}{atom.z:8.3f}"
                f"  1.00  0.00          {atom.symbol:>2s}"
            )
            lines.append(line)

        lines.append("END")
        return '\n'.join(lines) + '\n'

    # ==================== MOL2 Format ====================

    @classmethod
    def read_mol2(cls, content: str, name: str = 'molecule') -> Molecule:
        """Parse Tripos MOL2 format."""
        mol = Molecule(name=name)

        # Split into sections
        sections = {}
        current_section = None
        current_lines = []

        for line in content.splitlines():
            if line.startswith('@<TRIPOS>'):
                if current_section:
                    sections[current_section] = current_lines
                current_section = line.replace('@<TRIPOS>', '').strip()
                current_lines = []
            elif current_section:
                current_lines.append(line)

        if current_section:
            sections[current_section] = current_lines

        # Parse MOLECULE section
        if 'MOLECULE' in sections:
            mol_lines = sections['MOLECULE']
            if mol_lines:
                mol.name = mol_lines[0].strip() or name

        # Parse ATOM section
        if 'ATOM' in sections:
            for i, line in enumerate(sections['ATOM']):
                parts = line.split()
                if len(parts) < 6:
                    continue
                try:
                    # atom_id = int(parts[0])
                    # atom_name = parts[1]
                    x = float(parts[2])
                    y = float(parts[3])
                    z = float(parts[4])
                    atom_type = parts[5]

                    # Extract element from atom type (e.g., "C.3" -> "C")
                    symbol = atom_type.split('.')[0]

                    charge = float(parts[8]) if len(parts) > 8 else 0.0

                    mol.add_atom(Atom(
                        symbol=symbol,
                        position=(x, y, z),
                        index=i,
                        charge=charge,
                    ))
                except (ValueError, IndexError):
                    continue

        # Parse BOND section
        if 'BOND' in sections:
            for line in sections['BOND']:
                parts = line.split()
                if len(parts) < 4:
                    continue
                try:
                    # bond_id = int(parts[0])
                    atom1 = int(parts[1]) - 1  # MOL2 is 1-indexed
                    atom2 = int(parts[2]) - 1
                    bond_type = parts[3]

                    order_map = {
                        '1': BondOrder.SINGLE,
                        '2': BondOrder.DOUBLE,
                        '3': BondOrder.TRIPLE,
                        'ar': BondOrder.AROMATIC,
                        'am': BondOrder.PARTIAL,
                    }
                    order = order_map.get(bond_type.lower(), BondOrder.SINGLE)

                    mol.add_bond(atom1, atom2, order)
                except (ValueError, IndexError):
                    continue

        return mol

    # ==================== SDF/MOL Format ====================

    @classmethod
    def read_sdf(cls, content: str, name: str = 'molecule') -> Molecule:
        """Parse MDL SDF/MOL format."""
        lines = content.splitlines()

        if len(lines) < 4:
            raise ValueError("Invalid SDF format: too few lines")

        # Header
        mol_name = lines[0].strip() or name
        # lines[1] is program/timestamp
        # lines[2] is comment

        mol = Molecule(name=mol_name)

        # Counts line
        counts = lines[3].split()
        try:
            n_atoms = int(counts[0])
            n_bonds = int(counts[1])
        except (ValueError, IndexError):
            raise ValueError("Invalid SDF counts line")

        # Atom block
        for i in range(n_atoms):
            line = lines[4 + i]
            parts = line.split()
            if len(parts) < 4:
                continue
            try:
                x = float(parts[0])
                y = float(parts[1])
                z = float(parts[2])
                symbol = parts[3]

                charge = 0.0
                if len(parts) > 4:
                    charge_code = int(parts[4]) if parts[4].isdigit() else 0
                    if charge_code > 0:
                        charge = 4 - charge_code  # SDF charge encoding

                mol.add_atom(Atom(symbol=symbol, position=(x, y, z), index=i, charge=charge))
            except (ValueError, IndexError):
                continue

        # Bond block
        bond_start = 4 + n_atoms
        for i in range(n_bonds):
            if bond_start + i >= len(lines):
                break
            line = lines[bond_start + i]
            parts = line.split()
            if len(parts) < 3:
                continue
            try:
                atom1 = int(parts[0]) - 1  # SDF is 1-indexed
                atom2 = int(parts[1]) - 1
                bond_type = int(parts[2])

                order_map = {
                    1: BondOrder.SINGLE,
                    2: BondOrder.DOUBLE,
                    3: BondOrder.TRIPLE,
                    4: BondOrder.AROMATIC,
                }
                order = order_map.get(bond_type, BondOrder.SINGLE)

                mol.add_bond(atom1, atom2, order)
            except (ValueError, IndexError):
                continue

        return mol

    # ==================== JSON Format ====================

    @classmethod
    def read_json(cls, content: str, name: str = 'molecule') -> Molecule:
        """Read JSON format."""
        data = json.loads(content)
        mol = Molecule.from_dict(data)
        if not mol.name:
            mol.name = name
        return mol

    @classmethod
    def write_json(cls, molecule: Molecule) -> str:
        """Write JSON format."""
        return molecule.to_json(indent=2)


# Convenience functions
def read_molecule(path: Union[str, Path], format: Optional[str] = None) -> Molecule:
    """Read molecule from file."""
    return MoleculeIO.read(path, format)


def write_molecule(molecule: Molecule, path: Union[str, Path],
                   format: Optional[str] = None) -> Path:
    """Write molecule to file."""
    return MoleculeIO.write(molecule, path, format)


def parse_xyz(path_or_str: Union[str, Path]) -> Dict[str, Any]:
    """Parse XYZ format (legacy compatibility function).

    Args:
        path_or_str: File path or XYZ content string

    Returns:
        Dictionary with 'name', 'atoms', 'coords' keys
    """
    if isinstance(path_or_str, Path):
        content = path_or_str.read_text()
    elif Path(path_or_str).exists():
        content = Path(path_or_str).read_text()
    else:
        content = str(path_or_str)

    mol = MoleculeIO.read_xyz(content)
    return {
        'name': mol.name,
        'atoms': mol.symbols,
        'coords': [tuple(a.position) for a in mol.atoms],
    }
