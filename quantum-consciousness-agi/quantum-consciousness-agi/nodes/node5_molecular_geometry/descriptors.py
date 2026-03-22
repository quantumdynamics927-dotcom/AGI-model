"""Molecular descriptors and fingerprints.

This module provides various molecular descriptors for characterizing
molecular structures, useful for machine learning and similarity analysis.
"""
from __future__ import annotations
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter
import numpy as np
from scipy.spatial.distance import pdist

from .structures import Molecule, Atom, Bond, BondOrder
from .constants import (
    ATOMIC_MASSES, ATOMIC_NUMBERS, ELECTRONEGATIVITY, VDW_RADII,
    PHI, GOLDEN_ANGLE, is_phi_harmonic
)
from .analysis import GeometryAnalyzer


class MolecularDescriptors:
    """Calculate various molecular descriptors.

    Provides constitutional, topological, geometric, and
    electronic descriptors for molecular characterization.
    """

    def __init__(self, molecule: Molecule):
        """Initialize with a molecule.

        Args:
            molecule: Molecule object with atoms and optionally bonds
        """
        self.molecule = molecule
        self._analyzer: Optional[GeometryAnalyzer] = None

    @property
    def analyzer(self) -> GeometryAnalyzer:
        """Lazy-loaded geometry analyzer."""
        if self._analyzer is None:
            self._analyzer = GeometryAnalyzer(self.molecule)
        return self._analyzer

    # ==================== Constitutional Descriptors ====================

    def constitutional(self) -> Dict[str, Any]:
        """Calculate constitutional (composition-based) descriptors.

        Returns:
            Dictionary of constitutional descriptors
        """
        symbols = self.molecule.symbols
        counts = Counter(symbols)

        return {
            'n_atoms': self.molecule.n_atoms,
            'n_bonds': self.molecule.n_bonds,
            'n_heavy_atoms': sum(1 for s in symbols if s != 'H'),
            'n_heteroatoms': sum(1 for s in symbols if s not in ['C', 'H']),
            'molecular_weight': self.molecule.total_mass,
            'formula': self.molecule.formula,
            'composition': dict(counts),
            'n_carbons': counts.get('C', 0),
            'n_nitrogens': counts.get('N', 0),
            'n_oxygens': counts.get('O', 0),
            'n_sulfurs': counts.get('S', 0),
            'n_halogens': sum(counts.get(x, 0) for x in ['F', 'Cl', 'Br', 'I']),
            'n_rotatable_bonds': self._count_rotatable_bonds(),
            'n_rings': self._estimate_ring_count(),
        }

    def _count_rotatable_bonds(self) -> int:
        """Estimate number of rotatable bonds."""
        count = 0
        for bond in self.molecule.bonds:
            if bond.order != BondOrder.SINGLE:
                continue
            # Skip terminal atoms
            atom1 = self.molecule.atoms[bond.atom1_idx]
            atom2 = self.molecule.atoms[bond.atom2_idx]
            n1 = len(self.molecule.get_neighbors(bond.atom1_idx))
            n2 = len(self.molecule.get_neighbors(bond.atom2_idx))
            if n1 > 1 and n2 > 1:
                # Skip bonds to hydrogens
                if atom1.symbol != 'H' and atom2.symbol != 'H':
                    count += 1
        return count

    def _estimate_ring_count(self) -> int:
        """Estimate number of rings using Euler formula: R = E - V + 1."""
        # This counts independent cycles in the molecular graph
        n_atoms = self.molecule.n_atoms
        n_bonds = self.molecule.n_bonds
        if n_bonds >= n_atoms:
            return n_bonds - n_atoms + 1
        return 0

    # ==================== Topological Descriptors ====================

    def topological(self) -> Dict[str, Any]:
        """Calculate topological (graph-based) descriptors.

        Returns:
            Dictionary of topological descriptors
        """
        adj_matrix = self._adjacency_matrix()
        dist_matrix = self._topological_distance_matrix(adj_matrix)

        wiener = self._wiener_index(dist_matrix)
        zagreb1, zagreb2 = self._zagreb_indices(adj_matrix)

        return {
            'wiener_index': wiener,
            'zagreb_m1': zagreb1,
            'zagreb_m2': zagreb2,
            'balaban_j': self._balaban_j(dist_matrix),
            'average_connectivity': self._average_connectivity(adj_matrix),
            'molecular_connectivity_chi': self._molecular_connectivity(adj_matrix),
            'eccentric_connectivity': self._eccentric_connectivity(dist_matrix, adj_matrix),
        }

    def _adjacency_matrix(self) -> np.ndarray:
        """Build adjacency matrix from bonds."""
        n = self.molecule.n_atoms
        adj = np.zeros((n, n), dtype=np.int32)
        for bond in self.molecule.bonds:
            adj[bond.atom1_idx, bond.atom2_idx] = 1
            adj[bond.atom2_idx, bond.atom1_idx] = 1
        return adj

    def _topological_distance_matrix(self, adj: np.ndarray) -> np.ndarray:
        """Calculate topological (shortest path) distance matrix."""
        n = adj.shape[0]
        dist = np.full((n, n), np.inf)
        np.fill_diagonal(dist, 0)

        # Floyd-Warshall
        dist[adj > 0] = 1
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if dist[i, k] + dist[k, j] < dist[i, j]:
                        dist[i, j] = dist[i, k] + dist[k, j]

        return dist

    def _wiener_index(self, dist: np.ndarray) -> float:
        """Calculate Wiener index (sum of all shortest paths)."""
        finite = dist[np.isfinite(dist)]
        return float(np.sum(finite) / 2)

    def _zagreb_indices(self, adj: np.ndarray) -> Tuple[float, float]:
        """Calculate Zagreb M1 and M2 indices."""
        degrees = np.sum(adj, axis=1)
        m1 = float(np.sum(degrees ** 2))

        m2 = 0.0
        for bond in self.molecule.bonds:
            d1 = degrees[bond.atom1_idx]
            d2 = degrees[bond.atom2_idx]
            m2 += d1 * d2

        return m1, m2

    def _balaban_j(self, dist: np.ndarray) -> float:
        """Calculate Balaban J index."""
        n = dist.shape[0]
        m = self.molecule.n_bonds

        if m == 0:
            return 0.0

        # Row sums (distance sums)
        row_sums = np.sum(dist, axis=1)
        row_sums[row_sums == 0] = 1  # Avoid division by zero

        # Calculate J
        j_sum = 0.0
        for bond in self.molecule.bonds:
            i, j = bond.atom1_idx, bond.atom2_idx
            j_sum += 1.0 / np.sqrt(row_sums[i] * row_sums[j])

        cyclic = m - n + 1  # Number of rings
        return float((m / (cyclic + 1)) * j_sum)

    def _average_connectivity(self, adj: np.ndarray) -> float:
        """Calculate average vertex connectivity."""
        degrees = np.sum(adj, axis=1)
        return float(np.mean(degrees))

    def _molecular_connectivity(self, adj: np.ndarray) -> float:
        """Calculate Randic molecular connectivity index (chi)."""
        degrees = np.sum(adj, axis=1).astype(float)
        degrees[degrees == 0] = 1

        chi = 0.0
        for bond in self.molecule.bonds:
            i, j = bond.atom1_idx, bond.atom2_idx
            chi += 1.0 / np.sqrt(degrees[i] * degrees[j])

        return float(chi)

    def _eccentric_connectivity(self, dist: np.ndarray, adj: np.ndarray) -> float:
        """Calculate eccentric connectivity index."""
        degrees = np.sum(adj, axis=1)
        eccentricities = np.max(dist, axis=1)
        eccentricities[~np.isfinite(eccentricities)] = 0
        return float(np.sum(degrees * eccentricities))

    # ==================== Geometric Descriptors ====================

    def geometric(self) -> Dict[str, Any]:
        """Calculate geometric (3D-based) descriptors.

        Returns:
            Dictionary of geometric descriptors
        """
        summary = self.analyzer.summary()

        # Distance-based
        dm = self.analyzer.distance_matrix
        distances = dm[np.triu_indices_from(dm, k=1)]

        return {
            'radius_of_gyration': summary['radius_of_gyration'],
            'asphericity': summary['asphericity'],
            'eccentricity': summary['eccentricity'],
            'max_diameter': summary['max_diameter'],
            'span_x': summary['span'][0],
            'span_y': summary['span'][1],
            'span_z': summary['span'][2],
            'surface_area': summary['surface_area_estimate'],
            'volume': summary['volume_estimate'],
            'mean_distance': float(np.mean(distances)) if len(distances) > 0 else 0.0,
            'std_distance': float(np.std(distances)) if len(distances) > 0 else 0.0,
            'moments_of_inertia': summary['moments_of_inertia'],
            'gravitational_index': self._gravitational_index(),
        }

    def _gravitational_index(self) -> float:
        """Calculate gravitational index (mass-weighted distance sum)."""
        coords = self.molecule.coordinates
        masses = self.molecule.masses

        g_index = 0.0
        for i in range(len(masses)):
            for j in range(i + 1, len(masses)):
                dist = np.linalg.norm(coords[i] - coords[j])
                if dist > 0.01:
                    g_index += (masses[i] * masses[j]) / (dist ** 2)

        return float(g_index)

    # ==================== Electronic Descriptors ====================

    def electronic(self) -> Dict[str, Any]:
        """Calculate electronic property descriptors.

        Returns:
            Dictionary of electronic descriptors
        """
        electronegativities = []
        atomic_nums = []

        for atom in self.molecule.atoms:
            en = ELECTRONEGATIVITY.get(atom.symbol, 2.5)
            electronegativities.append(en)
            atomic_nums.append(atom.atomic_number)

        en_arr = np.array(electronegativities)

        # Calculate electronegativity-based descriptors
        total_charge = sum(a.charge for a in self.molecule.atoms)

        return {
            'mean_electronegativity': float(np.mean(en_arr)),
            'max_electronegativity': float(np.max(en_arr)),
            'min_electronegativity': float(np.min(en_arr)),
            'electronegativity_range': float(np.max(en_arr) - np.min(en_arr)),
            'total_atomic_number': sum(atomic_nums),
            'mean_atomic_number': float(np.mean(atomic_nums)),
            'total_formal_charge': float(total_charge),
            'dipole_moment_estimate': self._estimate_dipole(),
        }

    def _estimate_dipole(self) -> float:
        """Estimate dipole moment from partial charges and positions."""
        coords = self.molecule.coordinates
        charges = np.array([a.charge for a in self.molecule.atoms])

        if np.all(charges == 0):
            # Use electronegativity difference for simple estimate
            return 0.0

        # Dipole = sum(q_i * r_i)
        dipole_vector = np.sum(charges[:, np.newaxis] * coords, axis=0)
        return float(np.linalg.norm(dipole_vector))

    # ==================== Golden Ratio Descriptors ====================

    def golden_ratio_descriptors(self) -> Dict[str, Any]:
        """Calculate golden ratio and sacred geometry descriptors.

        These descriptors capture harmonic relationships based on
        the golden ratio (phi = 1.618...) for TMT-OS integration.

        Returns:
            Dictionary of golden ratio descriptors
        """
        phi_analysis = self.analyzer.phi_ratio_analysis()

        # Angle analysis
        angles = [a[3] for a in self.analyzer.all_bond_angles()]
        golden_angle_proximity = []
        for angle in angles:
            # Distance to golden angle or its complement
            diff1 = abs(angle - GOLDEN_ANGLE)
            diff2 = abs(angle - (360 - GOLDEN_ANGLE))
            diff3 = abs(angle - 180 / PHI)  # ~111.25 degrees
            golden_angle_proximity.append(min(diff1, diff2, diff3))

        # Distance analysis
        dm = self.analyzer.distance_matrix
        distances = dm[np.triu_indices_from(dm, k=1)]
        phi_distances = []
        for d in distances:
            if d > 0:
                ratio = d / PHI
                if is_phi_harmonic(d, tolerance=0.1):
                    phi_distances.append(d)

        return {
            'phi_score': phi_analysis['phi_score'],
            'n_phi_harmonic_distances': len(phi_analysis['phi_distances']),
            'n_golden_angles': len(phi_analysis['golden_angles']),
            'mean_golden_angle_deviation': float(np.mean(golden_angle_proximity)) if golden_angle_proximity else 0.0,
            'phi_distance_fraction': len(phi_distances) / len(distances) if len(distances) > 0 else 0.0,
            'structural_phi_signature': self._phi_signature(),
        }

    def _phi_signature(self) -> List[float]:
        """Generate a phi-based structural fingerprint.

        Returns a vector encoding phi-harmonic relationships.
        """
        signature = []

        # Encode phi relationships in distances
        dm = self.analyzer.distance_matrix
        distances = dm[np.triu_indices_from(dm, k=1)]

        # Binned phi ratio distribution
        bins = [0, PHI/2, PHI, PHI*1.5, PHI**2, PHI**2*1.5, PHI**3, np.inf]
        hist, _ = np.histogram(distances, bins=bins)
        signature.extend((hist / max(1, len(distances))).tolist())

        # Angle-based phi signature
        angles = [a[3] for a in self.analyzer.all_bond_angles()]
        if angles:
            golden_bins = [0, GOLDEN_ANGLE/2, GOLDEN_ANGLE, 180, 360-GOLDEN_ANGLE, 360]
            angle_hist, _ = np.histogram(angles, bins=golden_bins)
            signature.extend((angle_hist / max(1, len(angles))).tolist())
        else:
            signature.extend([0.0] * 5)

        return signature

    # ==================== All Descriptors ====================

    def all_descriptors(self) -> Dict[str, Any]:
        """Calculate all available descriptors.

        Returns:
            Dictionary containing all descriptor categories
        """
        return {
            'constitutional': self.constitutional(),
            'topological': self.topological(),
            'geometric': self.geometric(),
            'electronic': self.electronic(),
            'golden_ratio': self.golden_ratio_descriptors(),
        }

    def flat_descriptors(self) -> Dict[str, float]:
        """Get all numerical descriptors as a flat dictionary.

        Useful for machine learning applications.

        Returns:
            Dictionary with descriptor names as keys and numerical values
        """
        all_desc = self.all_descriptors()
        flat = {}

        def flatten(d: Dict[str, Any], prefix: str = ''):
            for key, value in d.items():
                full_key = f"{prefix}_{key}" if prefix else key
                if isinstance(value, dict):
                    flatten(value, full_key)
                elif isinstance(value, (int, float, np.number)):
                    flat[full_key] = float(value)
                elif isinstance(value, (list, tuple, np.ndarray)):
                    arr = np.array(value)
                    if arr.dtype.kind in 'iufc':  # numeric types
                        for i, v in enumerate(arr.flat):
                            flat[f"{full_key}_{i}"] = float(v)

        flatten(all_desc)
        return flat

    def descriptor_vector(self) -> np.ndarray:
        """Get descriptors as a fixed-length numpy vector.

        Returns:
            Numpy array of descriptor values
        """
        flat = self.flat_descriptors()
        # Sort keys for consistent ordering
        sorted_keys = sorted(flat.keys())
        return np.array([flat[k] for k in sorted_keys])


def calculate_descriptors(molecule: Molecule) -> Dict[str, Any]:
    """Convenience function to calculate all descriptors.

    Args:
        molecule: Molecule to analyze

    Returns:
        Dictionary of all descriptors
    """
    return MolecularDescriptors(molecule).all_descriptors()


def molecular_similarity(mol1: Molecule, mol2: Molecule,
                         method: str = 'descriptor') -> float:
    """Calculate similarity between two molecules.

    Args:
        mol1, mol2: Molecules to compare
        method: Similarity method ('descriptor', 'rmsd')

    Returns:
        Similarity score [0, 1] where 1 is identical
    """
    if method == 'rmsd':
        # RMSD-based similarity (requires same number of atoms)
        if mol1.n_atoms != mol2.n_atoms:
            return 0.0
        analyzer = GeometryAnalyzer(mol1)
        rmsd = analyzer.rmsd(mol2, align=True)
        # Convert RMSD to similarity (exponential decay)
        return float(np.exp(-rmsd / 2.0))

    elif method == 'descriptor':
        # Descriptor-based similarity (Tanimoto-like)
        desc1 = MolecularDescriptors(mol1).descriptor_vector()
        desc2 = MolecularDescriptors(mol2).descriptor_vector()

        # Normalize and compute cosine similarity
        norm1 = np.linalg.norm(desc1)
        norm2 = np.linalg.norm(desc2)

        if norm1 < 1e-10 or norm2 < 1e-10:
            return 0.0

        similarity = np.dot(desc1, desc2) / (norm1 * norm2)
        return float((similarity + 1) / 2)  # Map [-1,1] to [0,1]

    else:
        raise ValueError(f"Unknown similarity method: {method}")
