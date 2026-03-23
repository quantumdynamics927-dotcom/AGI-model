"""Molecular structure data classes and core representations.

This module provides the fundamental data structures for representing
molecules, atoms, bonds, and related geometric entities.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Any, Iterator, Union
from enum import Enum, auto
import json
from pathlib import Path
import numpy as np
import sys
import os

# Add current directory to path for direct execution
sys.path.insert(0, os.path.dirname(__file__))

from constants import (
    ATOMIC_MASSES, COVALENT_RADII, VDW_RADII, ATOMIC_NUMBERS,
    get_mass, get_covalent_radius, get_vdw_radius, PHI
)


class BondOrder(Enum):
    """Chemical bond order enumeration."""
    SINGLE = 1
    DOUBLE = 2
    TRIPLE = 3
    AROMATIC = 1.5
    PARTIAL = 0.5
    UNKNOWN = 0


@dataclass
class Atom:
    """Represents a single atom in 3D space.

    Attributes:
        symbol: Element symbol (e.g., 'C', 'N', 'O')
        position: 3D coordinates as (x, y, z) tuple
        index: Atom index within the molecule
        charge: Formal charge
        mass: Atomic mass (auto-populated if not provided)
        residue: Residue name (for biomolecules)
        chain: Chain identifier (for biomolecules)
        properties: Additional custom properties
    """
    symbol: str
    position: Tuple[float, float, float]
    index: int = 0
    charge: float = 0.0
    mass: Optional[float] = None
    residue: Optional[str] = None
    chain: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        # Normalize symbol
        self.symbol = self.symbol.strip()
        if len(self.symbol) > 1:
            self.symbol = self.symbol[0].upper() + self.symbol[1:].lower()
        else:
            self.symbol = self.symbol.upper()

        # Auto-populate mass if not provided
        if self.mass is None:
            self.mass = get_mass(self.symbol)

    @property
    def x(self) -> float:
        return self.position[0]

    @property
    def y(self) -> float:
        return self.position[1]

    @property
    def z(self) -> float:
        return self.position[2]

    @property
    def coords(self) -> np.ndarray:
        """Return position as numpy array."""
        return np.array(self.position, dtype=np.float64)

    @property
    def atomic_number(self) -> int:
        """Get atomic number."""
        return ATOMIC_NUMBERS.get(self.symbol, 0)

    @property
    def covalent_radius(self) -> float:
        """Get covalent radius in Angstroms."""
        return get_covalent_radius(self.symbol)

    @property
    def vdw_radius(self) -> float:
        """Get van der Waals radius in Angstroms."""
        return get_vdw_radius(self.symbol)

    def distance_to(self, other: Atom) -> float:
        """Calculate distance to another atom."""
        return float(np.linalg.norm(self.coords - other.coords))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'symbol': self.symbol,
            'position': list(self.position),
            'index': self.index,
            'charge': self.charge,
            'mass': self.mass,
            'residue': self.residue,
            'chain': self.chain,
            'properties': self.properties,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Atom:
        """Create Atom from dictionary."""
        return cls(
            symbol=data['symbol'],
            position=tuple(data['position']),
            index=data.get('index', 0),
            charge=data.get('charge', 0.0),
            mass=data.get('mass'),
            residue=data.get('residue'),
            chain=data.get('chain'),
            properties=data.get('properties', {}),
        )


@dataclass
class Bond:
    """Represents a chemical bond between two atoms.

    Attributes:
        atom1_idx: Index of first atom
        atom2_idx: Index of second atom
        order: Bond order (single, double, triple, aromatic)
        length: Bond length in Angstroms (computed or specified)
        properties: Additional custom properties
    """
    atom1_idx: int
    atom2_idx: int
    order: BondOrder = BondOrder.SINGLE
    length: Optional[float] = None
    properties: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'atom1_idx': self.atom1_idx,
            'atom2_idx': self.atom2_idx,
            'order': self.order.value,
            'length': self.length,
            'properties': self.properties,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Bond:
        """Create Bond from dictionary."""
        order_val = data.get('order', 1)
        if isinstance(order_val, (int, float)):
            order = BondOrder(order_val) if order_val in [b.value for b in BondOrder] else BondOrder.UNKNOWN
        else:
            order = BondOrder.UNKNOWN
        return cls(
            atom1_idx=data['atom1_idx'],
            atom2_idx=data['atom2_idx'],
            order=order,
            length=data.get('length'),
            properties=data.get('properties', {}),
        )


@dataclass
class Molecule:
    """Represents a complete molecular structure.

    This is the primary data structure for molecular geometry analysis.
    Supports atoms, bonds, and various molecular properties.

    Attributes:
        name: Molecule name/identifier
        atoms: List of Atom objects
        bonds: List of Bond objects
        charge: Total molecular charge
        multiplicity: Spin multiplicity
        properties: Additional custom properties
    """
    name: str
    atoms: List[Atom] = field(default_factory=list)
    bonds: List[Bond] = field(default_factory=list)
    charge: int = 0
    multiplicity: int = 1
    properties: Dict[str, Any] = field(default_factory=dict)

    def __len__(self) -> int:
        return len(self.atoms)

    def __iter__(self) -> Iterator[Atom]:
        return iter(self.atoms)

    def __getitem__(self, idx: int) -> Atom:
        return self.atoms[idx]

    @property
    def n_atoms(self) -> int:
        """Number of atoms."""
        return len(self.atoms)

    @property
    def n_bonds(self) -> int:
        """Number of bonds."""
        return len(self.bonds)

    @property
    def symbols(self) -> List[str]:
        """List of element symbols."""
        return [atom.symbol for atom in self.atoms]

    @property
    def coordinates(self) -> np.ndarray:
        """All atomic coordinates as Nx3 numpy array."""
        if not self.atoms:
            return np.empty((0, 3), dtype=np.float64)
        return np.array([atom.position for atom in self.atoms], dtype=np.float64)

    @coordinates.setter
    def coordinates(self, coords: np.ndarray):
        """Set coordinates from Nx3 array."""
        coords = np.asarray(coords, dtype=np.float64)
        if coords.shape[0] != len(self.atoms):
            raise ValueError(f"Coordinate array has {coords.shape[0]} rows but molecule has {len(self.atoms)} atoms")
        for i, atom in enumerate(self.atoms):
            atom.position = tuple(coords[i])

    @property
    def masses(self) -> np.ndarray:
        """Array of atomic masses."""
        return np.array([atom.mass for atom in self.atoms], dtype=np.float64)

    @property
    def total_mass(self) -> float:
        """Total molecular mass."""
        return float(np.sum(self.masses))

    @property
    def formula(self) -> str:
        """Molecular formula (Hill notation)."""
        from collections import Counter
        counts = Counter(self.symbols)

        # Hill notation: C first, then H, then alphabetical
        formula_parts = []
        for elem in ['C', 'H']:
            if elem in counts:
                count = counts.pop(elem)
                formula_parts.append(f"{elem}{count if count > 1 else ''}")

        for elem in sorted(counts.keys()):
            count = counts[elem]
            formula_parts.append(f"{elem}{count if count > 1 else ''}")

        return ''.join(formula_parts)

    @property
    def center_of_mass(self) -> np.ndarray:
        """Center of mass coordinates."""
        if not self.atoms:
            return np.zeros(3)
        coords = self.coordinates
        masses = self.masses
        return np.sum(coords * masses[:, np.newaxis], axis=0) / np.sum(masses)

    @property
    def centroid(self) -> np.ndarray:
        """Geometric centroid (unweighted center)."""
        if not self.atoms:
            return np.zeros(3)
        return np.mean(self.coordinates, axis=0)

    def add_atom(self, atom: Atom) -> int:
        """Add an atom to the molecule. Returns the atom index."""
        atom.index = len(self.atoms)
        self.atoms.append(atom)
        return atom.index

    def add_bond(self, atom1_idx: int, atom2_idx: int,
                 order: BondOrder = BondOrder.SINGLE) -> Bond:
        """Add a bond between two atoms."""
        if atom1_idx >= len(self.atoms) or atom2_idx >= len(self.atoms):
            raise ValueError("Atom index out of range")
        length = self.atoms[atom1_idx].distance_to(self.atoms[atom2_idx])
        bond = Bond(atom1_idx, atom2_idx, order, length)
        self.bonds.append(bond)
        return bond

    def get_atom(self, idx: int) -> Atom:
        """Get atom by index."""
        return self.atoms[idx]

    def get_bonds_for_atom(self, atom_idx: int) -> List[Bond]:
        """Get all bonds involving a specific atom."""
        return [b for b in self.bonds if b.atom1_idx == atom_idx or b.atom2_idx == atom_idx]

    def get_neighbors(self, atom_idx: int) -> List[int]:
        """Get indices of atoms bonded to the specified atom."""
        neighbors = []
        for bond in self.get_bonds_for_atom(atom_idx):
            if bond.atom1_idx == atom_idx:
                neighbors.append(bond.atom2_idx)
            else:
                neighbors.append(bond.atom1_idx)
        return neighbors

    def translate(self, vector: np.ndarray) -> Molecule:
        """Translate molecule by a vector. Returns self for chaining."""
        vector = np.asarray(vector, dtype=np.float64)
        for atom in self.atoms:
            new_pos = np.array(atom.position) + vector
            atom.position = tuple(new_pos)
        return self

    def center(self) -> Molecule:
        """Center molecule at origin (using center of mass). Returns self."""
        return self.translate(-self.center_of_mass)

    def rotate(self, rotation_matrix: np.ndarray) -> Molecule:
        """Apply rotation matrix to all coordinates. Returns self."""
        rotation_matrix = np.asarray(rotation_matrix, dtype=np.float64)
        coords = self.coordinates @ rotation_matrix.T
        self.coordinates = coords
        return self

    def copy(self) -> Molecule:
        """Create a deep copy of the molecule."""
        new_mol = Molecule(
            name=self.name,
            charge=self.charge,
            multiplicity=self.multiplicity,
            properties=dict(self.properties),
        )
        for atom in self.atoms:
            new_mol.atoms.append(Atom(
                symbol=atom.symbol,
                position=atom.position,
                index=atom.index,
                charge=atom.charge,
                mass=atom.mass,
                residue=atom.residue,
                chain=atom.chain,
                properties=dict(atom.properties),
            ))
        for bond in self.bonds:
            new_mol.bonds.append(Bond(
                atom1_idx=bond.atom1_idx,
                atom2_idx=bond.atom2_idx,
                order=bond.order,
                length=bond.length,
                properties=dict(bond.properties),
            ))
        return new_mol

    def to_dict(self) -> Dict[str, Any]:
        """Convert molecule to dictionary representation."""
        return {
            'name': self.name,
            'atoms': [a.to_dict() for a in self.atoms],
            'bonds': [b.to_dict() for b in self.bonds],
            'charge': self.charge,
            'multiplicity': self.multiplicity,
            'properties': self.properties,
            'formula': self.formula,
            'n_atoms': self.n_atoms,
            'total_mass': self.total_mass,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Molecule:
        """Create Molecule from dictionary."""
        mol = cls(
            name=data['name'],
            charge=data.get('charge', 0),
            multiplicity=data.get('multiplicity', 1),
            properties=data.get('properties', {}),
        )
        for atom_data in data.get('atoms', []):
            mol.atoms.append(Atom.from_dict(atom_data))
        for bond_data in data.get('bonds', []):
            mol.bonds.append(Bond.from_dict(bond_data))
        return mol

    def to_json(self, path: Optional[Path] = None, indent: int = 2) -> str:
        """Serialize to JSON. Optionally write to file."""
        json_str = json.dumps(self.to_dict(), indent=indent)
        if path:
            Path(path).write_text(json_str)
        return json_str

    @classmethod
    def from_json(cls, path_or_str: Union[str, Path]) -> Molecule:
        """Load molecule from JSON file or string."""
        if isinstance(path_or_str, Path) or (isinstance(path_or_str, str) and Path(path_or_str).exists()):
            data = json.loads(Path(path_or_str).read_text())
        else:
            data = json.loads(path_or_str)
        return cls.from_dict(data)


# Legacy compatibility alias
@dataclass
class GeometryStructure:
    """Legacy structure for backward compatibility.

    Prefer using Molecule for new code.
    """
    name: str
    atoms: List[str]
    coords: List[Tuple[float, float, float]]

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "atoms": self.atoms, "coords": self.coords}

    def to_molecule(self) -> Molecule:
        """Convert to Molecule object."""
        mol = Molecule(name=self.name)
        for i, (symbol, coord) in enumerate(zip(self.atoms, self.coords)):
            mol.add_atom(Atom(symbol=symbol, position=coord, index=i))
        return mol

    @classmethod
    def from_molecule(cls, mol: Molecule) -> GeometryStructure:
        """Create from Molecule object."""
        return cls(
            name=mol.name,
            atoms=mol.symbols,
            coords=[tuple(a.position) for a in mol.atoms],
        )
