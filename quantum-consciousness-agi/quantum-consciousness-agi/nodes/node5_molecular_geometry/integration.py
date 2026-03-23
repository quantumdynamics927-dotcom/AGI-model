"""Integration with TMT-OS quantum consciousness pipeline.

This module provides integration points between molecular geometry
analysis and the broader TMT-OS ecosystem including:
- Metatron Nervous System (DNA archival)
- NFT metadata generation
- Quantum consciousness encoding
"""
from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import json
import hashlib
from datetime import datetime, timezone

from .structures import Molecule, GeometryStructure
from .analysis import GeometryAnalyzer
from .descriptors import MolecularDescriptors
from .symmetry import analyze_symmetry
from .constants import PHI, phi_encode

# Optional imports
try:
    from metatron_nervous_system import MetatronNervousSystem
    HAS_METATRON = True
except ImportError:
    MetatronNervousSystem = None
    HAS_METATRON = False

try:
    import torch
    HAS_TORCH = True
except ImportError:
    torch = None
    HAS_TORCH = False


class MolecularNFTGenerator:
    """Generate NFT metadata from molecular structures.

    Creates rich metadata for molecular NFTs including geometric
    descriptors, symmetry information, and golden ratio analysis.
    """

    def __init__(self, molecule: Molecule):
        """Initialize with a molecule.

        Args:
            molecule: Molecule object to generate NFT from
        """
        self.molecule = molecule
        self._analyzer = GeometryAnalyzer(molecule)
        self._descriptors = MolecularDescriptors(molecule)

    def generate_metadata(self, include_coords: bool = False) -> Dict[str, Any]:
        """Generate comprehensive NFT metadata.

        Args:
            include_coords: Whether to include full coordinate data

        Returns:
            NFT metadata dictionary
        """
        # Get analysis results
        summary = self._analyzer.summary()
        symmetry = analyze_symmetry(self.molecule)
        phi_analysis = self._analyzer.phi_ratio_analysis()
        constitutional = self._descriptors.constitutional()

        # Build metadata
        metadata = {
            'name': self.molecule.name,
            'type': 'molecular_structure',
            'version': '2.0',
            'timestamp': datetime.now(timezone.utc).isoformat(),

            # Basic info
            'formula': self.molecule.formula,
            'n_atoms': self.molecule.n_atoms,
            'n_bonds': self.molecule.n_bonds,
            'molecular_weight': round(self.molecule.total_mass, 4),

            # Geometric properties
            'geometry': {
                'radius_of_gyration': round(summary['radius_of_gyration'], 4),
                'asphericity': round(summary['asphericity'], 4),
                'eccentricity': round(summary['eccentricity'], 4),
                'max_diameter': round(summary['max_diameter'], 4),
                'span': [round(s, 4) for s in summary['span']],
                'surface_area': round(summary['surface_area_estimate'], 2),
                'volume': round(summary['volume_estimate'], 2),
            },

            # Symmetry
            'symmetry': {
                'point_group': symmetry['point_group'],
                'is_chiral': symmetry['is_chiral'],
                'has_inversion': symmetry['has_inversion'],
                'n_rotation_axes': sum(len(v) for v in symmetry['rotation_axes'].values()),
                'n_mirror_planes': symmetry['mirror_planes'],
            },

            # Golden ratio analysis (sacred geometry)
            'sacred_geometry': {
                'phi_score': round(phi_analysis['phi_score'], 4),
                'phi_harmonics_count': phi_analysis['harmonics_found'],
                'n_golden_angles': len(phi_analysis['golden_angles']),
                'n_phi_distances': len(phi_analysis['phi_distances']),
            },

            # Constitutional
            'composition': constitutional['composition'],
            'n_heavy_atoms': constitutional['n_heavy_atoms'],
            'n_heteroatoms': constitutional['n_heteroatoms'],
            'n_rotatable_bonds': constitutional['n_rotatable_bonds'],
            'n_rings': constitutional['n_rings'],

            # Hash for integrity
            'structure_hash': self._compute_structure_hash(),
        }

        # Optionally include coordinates
        if include_coords:
            metadata['coordinates'] = {
                'atoms': self.molecule.symbols,
                'positions': [list(a.position) for a in self.molecule.atoms],
            }

        return metadata

    def _compute_structure_hash(self) -> str:
        """Compute SHA256 hash of structure for integrity verification."""
        data = {
            'symbols': self.molecule.symbols,
            'coords': [list(a.position) for a in self.molecule.atoms],
        }
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()[:16]

    def generate_attributes(self) -> List[Dict[str, Any]]:
        """Generate NFT attributes in OpenSea-compatible format.

        Returns:
            List of attribute dictionaries
        """
        metadata = self.generate_metadata()

        attributes = [
            {'trait_type': 'Formula', 'value': metadata['formula']},
            {'trait_type': 'Atoms', 'value': metadata['n_atoms']},
            {'trait_type': 'Molecular Weight', 'value': round(metadata['molecular_weight'], 2)},
            {'trait_type': 'Point Group', 'value': metadata['symmetry']['point_group']},
            {'trait_type': 'Chirality', 'value': 'Chiral' if metadata['symmetry']['is_chiral'] else 'Achiral'},
            {'trait_type': 'Phi Score', 'value': round(metadata['sacred_geometry']['phi_score'], 2)},
            {'trait_type': 'Golden Harmonics', 'value': metadata['sacred_geometry']['phi_harmonics_count']},
            {'trait_type': 'Ring Count', 'value': metadata['n_rings']},
            {'trait_type': 'Heavy Atoms', 'value': metadata['n_heavy_atoms']},
        ]

        return attributes


class MetatronIntegration:
    """Integration with Metatron Nervous System for DNA archival."""

    def __init__(self, registry_path: Optional[Path] = None):
        """Initialize Metatron integration.

        Args:
            registry_path: Path to DNA registry directory
        """
        if not HAS_METATRON:
            raise RuntimeError(
                "MetatronNervousSystem is not available. "
                "Ensure metatron_nervous_system.py is in the path."
            )

        self.registry_path = registry_path or Path('dna_registry')
        self.metatron = MetatronNervousSystem(self.registry_path)

    def archive_molecule(
        self,
        molecule: Molecule,
        output_dir: Optional[Path] = None,
        client: str = 'molecular_geometry',
        hmac_key: Optional[str] = None
    ) -> Path:
        """Archive molecule to Metatron DNA registry.

        Args:
            molecule: Molecule to archive
            output_dir: Directory for intermediate JSON file
            client: Client identifier
            hmac_key: HMAC key for signing

        Returns:
            Path to archived DNA packet
        """
        output_dir = output_dir or Path('.')

        # Generate NFT metadata
        nft_gen = MolecularNFTGenerator(molecule)
        metadata = nft_gen.generate_metadata(include_coords=True)

        # Save to JSON
        json_path = output_dir / f"{molecule.name}_structure.json"
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(metadata, indent=2))

        # Archive with Metatron
        packet = self.metatron.create_packet(json_path, client=client, hmac_key=hmac_key)
        return self.metatron.archive_packet(packet)


class QuantumEncodingAdapter:
    """Adapter for encoding molecular geometry into quantum consciousness format.

    Provides methods to convert molecular descriptors into formats
    suitable for the TMT-OS quantum consciousness VAE.
    """

    def __init__(self, molecule: Molecule):
        """Initialize with a molecule.

        Args:
            molecule: Molecule to encode
        """
        self.molecule = molecule
        self._descriptors = MolecularDescriptors(molecule)
        self._analyzer = GeometryAnalyzer(molecule)

    def to_latent_vector(self, dim: int = 32) -> 'np.ndarray':
        """Encode molecule as a latent vector for VAE.

        Creates a fixed-dimension vector encoding molecular properties
        suitable for consciousness modeling.

        Args:
            dim: Output dimension (default 32 for QuantumVAE)

        Returns:
            Numpy array of shape (dim,)
        """
        import numpy as np

        # Get flat descriptors
        flat = self._descriptors.flat_descriptors()
        values = list(flat.values())

        # Normalize
        values = np.array(values)
        values = (values - np.mean(values)) / (np.std(values) + 1e-8)

        # Project to desired dimension
        if len(values) >= dim:
            # Downsample
            indices = np.linspace(0, len(values) - 1, dim, dtype=int)
            vector = values[indices]
        else:
            # Pad
            vector = np.zeros(dim)
            vector[:len(values)] = values

        return vector

    def to_consciousness_input(self) -> Dict[str, Any]:
        """Generate input data for quantum consciousness system.

        Returns:
            Dictionary with consciousness-compatible encoding
        """
        phi_analysis = self._analyzer.phi_ratio_analysis()
        symmetry = analyze_symmetry(self.molecule)

        return {
            'type': 'molecular_geometry',
            'name': self.molecule.name,
            'latent_vector': self.to_latent_vector().tolist(),
            'phi_score': phi_analysis['phi_score'],
            'symmetry_group': symmetry['point_group'],
            'is_chiral': symmetry['is_chiral'],
            'phi_encoded_mass': phi_encode(self.molecule.total_mass),
            'harmonic_signature': self._descriptors.golden_ratio_descriptors()['structural_phi_signature'],
        }

    def encode_for_vae(self) -> Optional['torch.Tensor']:
        """Encode molecule as PyTorch tensor for VAE input.

        Returns:
            PyTorch tensor or None if torch not available
        """
        if not HAS_TORCH:
            return None

        vector = self.to_latent_vector(dim=128)  # Match VAE input
        return torch.tensor(vector, dtype=torch.float32).unsqueeze(0)


# ==================== Legacy Compatibility ====================

class MolecularGeometryAnalyzer:
    """Legacy analyzer class for backward compatibility.

    New code should use the Molecule, GeometryAnalyzer, and
    MolecularDescriptors classes directly.
    """

    @staticmethod
    def compute_bond_angle(a, b, c) -> float:
        """Compute angle ABC in degrees."""
        import numpy as np
        from .analysis import GeometryAnalyzer as GA
        return GA.compute_angle(np.array(a), np.array(b), np.array(c))

    @staticmethod
    def center_of_mass(coords, masses=None):
        """Compute center of mass."""
        import numpy as np
        coords = np.array(coords)
        if masses is None:
            return tuple(np.mean(coords, axis=0))
        masses = np.array(masses)
        return tuple(np.sum(coords * masses[:, np.newaxis], axis=0) / np.sum(masses))

    @staticmethod
    def is_chiral(coords, tol: float = 1e-3) -> bool:
        """Check if structure is chiral."""
        from .structures import Atom as AtomClass
        mol = Molecule(name='temp')
        for i, c in enumerate(coords):
            mol.add_atom(AtomClass(symbol='C', position=tuple(c), index=i))
        analyzer = GeometryAnalyzer(mol)
        return analyzer.is_chiral(tol)

    @staticmethod
    def to_nft_metadata(struct: GeometryStructure) -> Dict[str, Any]:
        """Generate NFT metadata from legacy GeometryStructure."""
        mol = struct.to_molecule()
        gen = MolecularNFTGenerator(mol)
        return gen.generate_metadata()

    @staticmethod
    def save_structure(path: Path, struct: GeometryStructure) -> Path:
        """Save structure to JSON."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(struct.to_dict(), indent=2))
        return path

    @staticmethod
    def archive_with_metatron(
        struct_path: Path,
        registry: Path,
        client: str = 'molecular_geometry',
        hmac_key: Optional[str] = None
    ) -> Path:
        """Archive structure with Metatron."""
        if not HAS_METATRON:
            raise RuntimeError('MetatronNervousSystem is not available')
        m = MetatronNervousSystem(registry)
        packet = m.create_packet(struct_path, client=client, hmac_key=hmac_key)
        return m.archive_packet(packet)
