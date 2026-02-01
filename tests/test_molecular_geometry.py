"""Legacy tests for molecular_geometry module backward compatibility.

These tests verify the old API still works with the new v2.0 implementation.
"""
from pathlib import Path
import tempfile
import json

from molecular_geometry import MolecularGeometryAnalyzer, parse_xyz, GeometryStructure


def test_compute_bond_angle_right_angle():
    a = (1.0, 0.0, 0.0)
    b = (0.0, 0.0, 0.0)
    c = (0.0, 1.0, 0.0)
    ang = MolecularGeometryAnalyzer.compute_bond_angle(a, b, c)
    assert abs(ang - 90.0) < 1e-6


def test_parse_xyz_and_metadata(tmp_path):
    xyz = """
    3
    water
    O 0.0 0.0 0.0
    H 1.0 0.0 0.0
    H 0.0 1.0 0.0
    """
    parsed = parse_xyz(xyz)
    assert parsed['name'].strip() == 'water'
    assert len(parsed['atoms']) == 3
    struct = GeometryStructure(name=parsed['name'], atoms=parsed['atoms'], coords=parsed['coords'])
    # Use new integration API for NFT metadata
    from molecular_geometry import get_nft_generator
    mol = struct.to_molecule()
    nft = get_nft_generator(mol)
    metadata = nft.generate_metadata()
    assert 'n_atoms' in metadata and metadata['n_atoms'] == 3


def test_save_structure_and_archive(tmp_path, monkeypatch):
    struct = GeometryStructure(name='demo', atoms=['C','C','C'], coords=[(0,0,0),(1,0,0),(0,1,0)])
    p = tmp_path / 'demo.json'
    MolecularGeometryAnalyzer.save_structure(p, struct)
    assert p.exists()
    txt = json.loads(p.read_text())
    assert txt['name'] == 'demo'
    # archiving requires Metatron; ensure clear failure mode when not available
    # Patch the integration module's MetatronNervousSystem
    import molecular_geometry.integration as integ
    monkeypatch.setattr(integ, 'MetatronNervousSystem', None)
    monkeypatch.setattr(integ, 'HAS_METATRON', False)
    # calling archive_with_metatron without Metatron should raise
    try:
        MolecularGeometryAnalyzer.archive_with_metatron(p, tmp_path)
    except RuntimeError:
        pass
    else:
        raise AssertionError('archive_with_metatron should have failed without Metatron')
