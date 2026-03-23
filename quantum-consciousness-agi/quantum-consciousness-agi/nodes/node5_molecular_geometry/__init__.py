"""Molecular Geometry Node - Professional Molecular Structure Analysis

This module provides comprehensive molecular geometry analysis capabilities
for the TMT-OS quantum consciousness ecosystem.

Core Components:
    - Molecule, Atom, Bond: Molecular data structures
    - GeometryAnalyzer: Advanced geometric calculations
    - MolecularDescriptors: Comprehensive molecular descriptors
    - SymmetryAnalyzer: Point group and symmetry detection
    - MoleculeIO: Multi-format file I/O

Integration:
    - MolecularNFTGenerator: NFT metadata generation
    - MetatronIntegration: DNA registry archival
    - QuantumEncodingAdapter: Quantum consciousness encoding

Example Usage:
    >>> from molecular_geometry import Molecule, read_molecule, GeometryAnalyzer
    >>> mol = read_molecule("water.xyz")
    >>> analyzer = GeometryAnalyzer(mol)
    >>> print(analyzer.summary())

    >>> from molecular_geometry import MolecularDescriptors
    >>> desc = MolecularDescriptors(mol)
    >>> print(desc.all_descriptors())

Golden Ratio Integration:
    This module includes phi-based (φ = 1.618...) analysis throughout,
    aligning molecular geometry with sacred geometry principles used
    in the TMT-OS quantum consciousness architecture.
"""
__version__ = '2.0.0'
__author__ = 'TMT-OS'

# Core structures
from .structures import (
    Molecule,
    Atom,
    Bond,
    BondOrder,
    GeometryStructure,  # Legacy compatibility
)

# Analysis
from .analysis import (
    GeometryAnalyzer,
    compute_distance,
    compute_angle,
    compute_dihedral,
)

# Descriptors
from .descriptors import (
    MolecularDescriptors,
    calculate_descriptors,
    molecular_similarity,
)

# Symmetry
from .symmetry import (
    SymmetryAnalyzer,
    SymmetryElement,
    PointGroup,
    analyze_symmetry,
    get_point_group,
)

# File I/O
from .io_formats import (
    MoleculeIO,
    read_molecule,
    write_molecule,
    parse_xyz,  # Legacy compatibility
)

# Constants
from .constants import (
    PHI,
    GOLDEN_ANGLE,
    ATOMIC_MASSES,
    COVALENT_RADII,
    VDW_RADII,
    ATOMIC_NUMBERS,
    get_mass,
    get_covalent_radius,
    get_vdw_radius,
    is_phi_harmonic,
    phi_encode,
    phi_decode,
)

# Integration (lazy imports to avoid heavy dependencies)
def get_nft_generator(molecule):
    """Get MolecularNFTGenerator for a molecule."""
    from .integration import MolecularNFTGenerator
    return MolecularNFTGenerator(molecule)


def get_metatron_integration(registry_path=None):
    """Get MetatronIntegration instance."""
    from .integration import MetatronIntegration
    return MetatronIntegration(registry_path)


def get_quantum_encoder(molecule):
    """Get QuantumEncodingAdapter for a molecule."""
    from .integration import QuantumEncodingAdapter
    return QuantumEncodingAdapter(molecule)


# Legacy compatibility - import the old analyzer
from .integration import MolecularGeometryAnalyzer

__all__ = [
    # Version
    '__version__',

    # Core structures
    'Molecule',
    'Atom',
    'Bond',
    'BondOrder',
    'GeometryStructure',

    # Analysis
    'GeometryAnalyzer',
    'compute_distance',
    'compute_angle',
    'compute_dihedral',

    # Descriptors
    'MolecularDescriptors',
    'calculate_descriptors',
    'molecular_similarity',

    # Symmetry
    'SymmetryAnalyzer',
    'SymmetryElement',
    'PointGroup',
    'analyze_symmetry',
    'get_point_group',

    # File I/O
    'MoleculeIO',
    'read_molecule',
    'write_molecule',
    'parse_xyz',

    # Constants
    'PHI',
    'GOLDEN_ANGLE',
    'ATOMIC_MASSES',
    'COVALENT_RADII',
    'VDW_RADII',
    'ATOMIC_NUMBERS',
    'get_mass',
    'get_covalent_radius',
    'get_vdw_radius',
    'is_phi_harmonic',
    'phi_encode',
    'phi_decode',

    # Integration helpers
    'get_nft_generator',
    'get_metatron_integration',
    'get_quantum_encoder',

    # Legacy compatibility
    'MolecularGeometryAnalyzer',
]
