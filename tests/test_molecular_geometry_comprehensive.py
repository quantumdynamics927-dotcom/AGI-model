"""
Comprehensive tests for molecular_geometry module.
"""

import pytest
import numpy as np
from pathlib import Path
import tempfile
import json

from molecular_geometry.geometry_core import (
    MolecularGeometryAnalyzer,
    GeometryStructure,
)
from molecular_geometry.structures import (
    Atom,
    Molecule,
    BondOrder,
)
from molecular_geometry.descriptors import (
    MolecularDescriptors,
)
from molecular_geometry.io_formats import (
    parse_xyz,
)
from molecular_geometry.constants import (
    ATOMIC_MASSES,
    COVALENT_RADII,
    VDW_RADII,
    ATOMIC_NUMBERS,
    get_mass,
    get_covalent_radius,
    get_vdw_radius,
    PHI,
)


class TestGeometryStructure:
    """Tests for GeometryStructure dataclass."""

    def test_geometry_structure_creation(self):
        struct = GeometryStructure(
            name="water",
            atoms=["O", "H", "H"],
            coords=[(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)],
        )
        assert struct.name == "water"
        assert len(struct.atoms) == 3

    def test_to_dict(self):
        struct = GeometryStructure(
            name="methane",
            atoms=["C", "H", "H", "H", "H"],
            coords=[(0.0, 0.0, 0.0), (1.0, 1.0, 1.0), (-1.0, -1.0, 1.0), (-1.0, 1.0, -1.0), (1.0, -1.0, -1.0)],
        )
        d = struct.to_dict()
        assert d["name"] == "methane"
        assert len(d["atoms"]) == 5


class TestMolecularGeometryAnalyzer:
    """Tests for MolecularGeometryAnalyzer class."""

    def test_compute_bond_angle_linear(self):
        a, b, c = (-1.0, 0.0, 0.0), (0.0, 0.0, 0.0), (1.0, 0.0, 0.0)
        angle = MolecularGeometryAnalyzer.compute_bond_angle(a, b, c)
        assert abs(angle - 180.0) < 1e-6

    def test_compute_bond_angle_right_angle(self):
        a, b, c = (1.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 1.0, 0.0)
        angle = MolecularGeometryAnalyzer.compute_bond_angle(a, b, c)
        assert abs(angle - 90.0) < 1e-6

    def test_compute_bond_angle_zero_distance(self):
        a, b, c = (0.0, 0.0, 0.0), (0.0, 0.0, 0.0), (1.0, 0.0, 0.0)
        angle = MolecularGeometryAnalyzer.compute_bond_angle(a, b, c)
        assert angle == 0.0

    def test_center_of_mass_uniform(self):
        coords = [(0.0, 0.0, 0.0), (2.0, 0.0, 0.0), (0.0, 2.0, 0.0), (0.0, 0.0, 2.0)]
        com = MolecularGeometryAnalyzer.center_of_mass(coords)
        assert abs(com[0] - 0.5) < 1e-6

    def test_center_of_mass_weighted(self):
        coords = [(0.0, 0.0, 0.0), (2.0, 0.0, 0.0)]
        masses = [1.0, 3.0]
        com = MolecularGeometryAnalyzer.center_of_mass(coords, masses)
        assert abs(com[0] - 1.5) < 1e-6

    def test_is_chiral_insufficient_atoms(self):
        coords = [(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)]
        is_chiral = MolecularGeometryAnalyzer.is_chiral(coords)
        assert is_chiral in [True, False, np.True_, np.False_]

    def test_to_nft_metadata(self):
        struct = GeometryStructure(name="water", atoms=["O", "H", "H"], coords=[(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)])
        metadata = MolecularGeometryAnalyzer.to_nft_metadata(struct)
        assert metadata["n_atoms"] == 3
        assert "avg_bond_angle" in metadata

    def test_save_structure(self, tmp_path):
        struct = GeometryStructure(name="test", atoms=["C", "C"], coords=[(0.0, 0.0, 0.0), (1.5, 0.0, 0.0)])
        filepath = tmp_path / "test_structure.json"
        result_path = MolecularGeometryAnalyzer.save_structure(filepath, struct)
        assert result_path.exists()
        data = json.loads(filepath.read_text())
        assert data["name"] == "test"

    def test_save_structure_creates_directories(self, tmp_path):
        struct = GeometryStructure(name="test", atoms=["C"], coords=[(0.0, 0.0, 0.0)])
        filepath = tmp_path / "subdir1" / "subdir2" / "test.json"
        result_path = MolecularGeometryAnalyzer.save_structure(filepath, struct)
        assert result_path.exists()


class TestAtom:
    """Tests for Atom class."""

    def test_atom_creation_basic(self):
        atom = Atom(symbol="C", position=(0.0, 0.0, 0.0), index=0)
        assert atom.symbol == "C"
        assert atom.mass is not None

    def test_atom_symbol_normalization(self):
        atom1 = Atom(symbol="c", position=(0.0, 0.0, 0.0))
        atom2 = Atom(symbol="CA", position=(0.0, 0.0, 0.0))
        assert atom1.symbol == "C"
        assert atom2.symbol == "Ca"

    def test_atom_auto_mass(self):
        carbon = Atom(symbol="C", position=(0.0, 0.0, 0.0))
        oxygen = Atom(symbol="O", position=(0.0, 0.0, 0.0))
        assert carbon.mass == get_mass("C")
        assert oxygen.mass != carbon.mass

    def test_atom_properties(self):
        atom = Atom(symbol="C", position=(1.0, 2.0, 3.0))
        assert atom.x == 1.0
        assert isinstance(atom.coords, np.ndarray)

    def test_atom_atomic_number(self):
        assert Atom(symbol="C", position=(0,0,0)).atomic_number == 6
        assert Atom(symbol="O", position=(0,0,0)).atomic_number == 8

    def test_atom_radii(self):
        carbon = Atom(symbol="C", position=(0.0, 0.0, 0.0))
        assert carbon.covalent_radius == get_covalent_radius("C")
        assert carbon.covalent_radius < carbon.vdw_radius


class TestMolecule:
    """Tests for Molecule class."""

    def test_molecule_creation_empty(self):
        mol = Molecule(name="empty")
        assert mol.name == "empty"
        assert len(mol.atoms) == 0

    def test_molecule_creation_with_atoms(self):
        atoms = [Atom(symbol="O", position=(0.0, 0.0, 0.0), index=0)]
        mol = Molecule(name="water", atoms=atoms)
        assert len(mol.atoms) == 1

    def test_molecule_add_atom(self):
        mol = Molecule(name="test")
        atom = Atom(symbol="C", position=(0.0, 0.0, 0.0), index=0)
        mol.add_atom(atom)
        assert len(mol.atoms) == 1

    def test_molecule_to_dict(self):
        mol = Molecule(name="test", atoms=[Atom(symbol="C", position=(0,0,0), index=0)])
        d = mol.to_dict()
        assert d["name"] == "test"


class TestDescriptors:
    """Tests for molecular descriptor classes."""

    def test_molecular_descriptors_init(self):
        atoms = [Atom(symbol="C", position=(0.0, 0.0, 0.0), index=0)]
        mol = Molecule(name="test", atoms=atoms)
        descriptor_calc = MolecularDescriptors(mol)
        assert descriptor_calc.molecule == mol

    def test_constitutional_descriptors(self):
        atoms = [Atom(symbol="C", position=(0.0, 0.0, 0.0), index=0), Atom(symbol="O", position=(1.2, 0.0, 0.0), index=1)]
        mol = Molecule(name="test", atoms=atoms)
        descriptor_calc = MolecularDescriptors(mol)
        descriptors = descriptor_calc.constitutional()
        assert isinstance(descriptors, dict)


class TestIOFormats:
    """Tests for file I/O functions."""

    def test_parse_xyz(self):
        xyz_content = "3\nWater molecule\nO 0.0 0.0 0.0\nH 1.0 0.0 0.0\nH 0.0 1.0 0.0\n"
        result = parse_xyz(xyz_content)
        assert result["name"] == "Water molecule"
        assert len(result["atoms"]) == 3


class TestConstants:
    """Tests for molecular constants."""

    def test_atomic_masses(self):
        assert ATOMIC_MASSES["H"] > 0
        assert ATOMIC_MASSES["C"] > ATOMIC_MASSES["H"]

    def test_get_mass(self):
        assert get_mass("H") == ATOMIC_MASSES["H"]
        assert get_mass("C") == ATOMIC_MASSES["C"]
        assert get_mass("unknown") > 0

    def test_covalent_radii(self):
        assert COVALENT_RADII["H"] > 0
        assert COVALENT_RADII["C"] > COVALENT_RADII["H"]

    def test_get_covalent_radius(self):
        assert get_covalent_radius("C") == COVALENT_RADII["C"]
        assert get_covalent_radius("unknown") > 0

    def test_vdw_radii(self):
        assert VDW_RADII["H"] > 0

    def test_get_vdw_radius(self):
        assert get_vdw_radius("C") == VDW_RADII["C"]
        assert get_vdw_radius("unknown") > 0

    def test_atomic_numbers(self):
        assert ATOMIC_NUMBERS["H"] == 1
        assert ATOMIC_NUMBERS["C"] == 6

    def test_phi_constant(self):
        expected_phi = (1 + np.sqrt(5)) / 2
        assert abs(PHI - expected_phi) < 1e-10
        assert abs(PHI**2 - PHI - 1) < 1e-10


class TestIntegration:
    """Integration tests."""

    def test_full_workflow_water(self, tmp_path):
        struct = GeometryStructure(name="water", atoms=["O", "H", "H"], coords=[(0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (-1.0, 0.0, 0.0)])
        metadata = MolecularGeometryAnalyzer.to_nft_metadata(struct)
        assert metadata["n_atoms"] == 3
        filepath = tmp_path / "water.json"
        MolecularGeometryAnalyzer.save_structure(filepath, struct)
        assert filepath.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
