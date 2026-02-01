"""Advanced molecular geometry analysis functions.

This module provides comprehensive geometric analysis capabilities including
distances, angles, dihedrals, RMSD, superposition, and structural comparisons.
"""
from __future__ import annotations
from typing import List, Tuple, Optional, Dict, Any, Union
import numpy as np
from scipy.spatial.distance import pdist, squareform
from scipy.spatial import ConvexHull
import sys
import os

# Add current directory to path for direct execution
sys.path.insert(0, os.path.dirname(__file__))

from structures import Molecule, Atom, Bond, BondOrder
from constants import (
    COVALENT_RADII, get_covalent_radius, PHI, GOLDEN_ANGLE,
    is_phi_harmonic
)


class GeometryAnalyzer:
    """Advanced molecular geometry analyzer.

    Provides methods for computing distances, angles, dihedrals, RMSD,
    and various molecular descriptors with golden ratio analysis integration.
    """

    def __init__(self, molecule: Molecule):
        """Initialize analyzer with a molecule.

        Args:
            molecule: Molecule object to analyze
        """
        self.molecule = molecule
        self._distance_matrix: Optional[np.ndarray] = None

    @property
    def coords(self) -> np.ndarray:
        """Atomic coordinates as Nx3 array."""
        return self.molecule.coordinates

    @property
    def distance_matrix(self) -> np.ndarray:
        """Compute and cache the pairwise distance matrix."""
        if self._distance_matrix is None:
            self._distance_matrix = squareform(pdist(self.coords))
        return self._distance_matrix

    def invalidate_cache(self):
        """Clear cached computations (call after modifying coordinates)."""
        self._distance_matrix = None

    # ==================== Distance Calculations ====================

    def distance(self, idx1: int, idx2: int) -> float:
        """Calculate distance between two atoms by index."""
        return float(self.distance_matrix[idx1, idx2])

    def all_distances(self) -> np.ndarray:
        """Return full distance matrix."""
        return self.distance_matrix

    def closest_atoms(self, n: int = 10) -> List[Tuple[int, int, float]]:
        """Find n closest atom pairs.

        Returns:
            List of (atom1_idx, atom2_idx, distance) tuples sorted by distance
        """
        dm = self.distance_matrix.copy()
        np.fill_diagonal(dm, np.inf)  # Exclude self-distances
        results = []
        for _ in range(n):
            if np.all(np.isinf(dm)):
                break
            idx = np.unravel_index(np.argmin(dm), dm.shape)
            results.append((int(idx[0]), int(idx[1]), float(dm[idx])))
            dm[idx] = np.inf
            dm[idx[1], idx[0]] = np.inf
        return results

    # ==================== Angle Calculations ====================

    @staticmethod
    def compute_angle(p1: np.ndarray, p2: np.ndarray, p3: np.ndarray) -> float:
        """Compute angle P1-P2-P3 in degrees (P2 is vertex).

        Args:
            p1, p2, p3: 3D coordinate arrays

        Returns:
            Angle in degrees [0, 180]
        """
        v1 = p1 - p2
        v2 = p3 - p2

        n1 = np.linalg.norm(v1)
        n2 = np.linalg.norm(v2)

        if n1 < 1e-10 or n2 < 1e-10:
            return 0.0

        cos_angle = np.dot(v1, v2) / (n1 * n2)
        cos_angle = np.clip(cos_angle, -1.0, 1.0)
        return float(np.degrees(np.arccos(cos_angle)))

    def angle(self, idx1: int, idx2: int, idx3: int) -> float:
        """Calculate angle formed by three atoms (idx2 is vertex)."""
        coords = self.coords
        return self.compute_angle(coords[idx1], coords[idx2], coords[idx3])

    def all_bond_angles(self) -> List[Tuple[int, int, int, float]]:
        """Compute all bond angles in the molecule.

        Returns:
            List of (atom1, vertex, atom3, angle_degrees) tuples
        """
        angles = []
        for i, atom in enumerate(self.molecule.atoms):
            neighbors = self.molecule.get_neighbors(i)
            if len(neighbors) >= 2:
                # Compute angle for each pair of neighbors
                for j in range(len(neighbors)):
                    for k in range(j + 1, len(neighbors)):
                        ang = self.angle(neighbors[j], i, neighbors[k])
                        angles.append((neighbors[j], i, neighbors[k], ang))
        return angles

    # ==================== Dihedral Calculations ====================

    @staticmethod
    def compute_dihedral(p1: np.ndarray, p2: np.ndarray,
                         p3: np.ndarray, p4: np.ndarray) -> float:
        """Compute dihedral angle P1-P2-P3-P4 in degrees.

        The dihedral is the angle between planes (P1,P2,P3) and (P2,P3,P4).

        Args:
            p1, p2, p3, p4: 3D coordinate arrays

        Returns:
            Dihedral angle in degrees [-180, 180]
        """
        b1 = p2 - p1
        b2 = p3 - p2
        b3 = p4 - p3

        # Normalize b2
        b2_norm = b2 / np.linalg.norm(b2)

        # Compute normal vectors to planes
        n1 = np.cross(b1, b2)
        n2 = np.cross(b2, b3)

        # Normalize
        n1_norm = np.linalg.norm(n1)
        n2_norm = np.linalg.norm(n2)

        if n1_norm < 1e-10 or n2_norm < 1e-10:
            return 0.0

        n1 = n1 / n1_norm
        n2 = n2 / n2_norm

        # Compute angle
        m1 = np.cross(n1, b2_norm)
        x = np.dot(n1, n2)
        y = np.dot(m1, n2)

        return float(np.degrees(np.arctan2(y, x)))

    def dihedral(self, idx1: int, idx2: int, idx3: int, idx4: int) -> float:
        """Calculate dihedral angle for four atoms."""
        coords = self.coords
        return self.compute_dihedral(
            coords[idx1], coords[idx2], coords[idx3], coords[idx4]
        )

    def all_dihedrals(self) -> List[Tuple[int, int, int, int, float]]:
        """Compute all torsion angles along connected bonds.

        Returns:
            List of (atom1, atom2, atom3, atom4, dihedral_degrees) tuples
        """
        dihedrals = []
        # Find all connected quadruplets
        for bond in self.molecule.bonds:
            i, j = bond.atom1_idx, bond.atom2_idx
            neighbors_i = [n for n in self.molecule.get_neighbors(i) if n != j]
            neighbors_j = [n for n in self.molecule.get_neighbors(j) if n != i]

            for ni in neighbors_i:
                for nj in neighbors_j:
                    dih = self.dihedral(ni, i, j, nj)
                    dihedrals.append((ni, i, j, nj, dih))

        return dihedrals

    # ==================== RMSD and Superposition ====================

    def rmsd(self, other: Union[Molecule, GeometryAnalyzer, np.ndarray],
             align: bool = False) -> float:
        """Calculate RMSD between this molecule and another structure.

        Args:
            other: Another Molecule, GeometryAnalyzer, or Nx3 coordinate array
            align: If True, perform optimal superposition first

        Returns:
            RMSD value in Angstroms
        """
        if isinstance(other, GeometryAnalyzer):
            other_coords = other.coords
        elif isinstance(other, Molecule):
            other_coords = other.coordinates
        else:
            other_coords = np.asarray(other)

        if self.coords.shape != other_coords.shape:
            raise ValueError("Coordinate arrays must have same shape")

        if align:
            _, other_coords = self.kabsch_align(other_coords)

        diff = self.coords - other_coords
        return float(np.sqrt(np.mean(np.sum(diff ** 2, axis=1))))

    def kabsch_align(self, target_coords: np.ndarray
                     ) -> Tuple[np.ndarray, np.ndarray]:
        """Compute optimal rotation to align target to this molecule.

        Uses the Kabsch algorithm for optimal superposition.

        Args:
            target_coords: Nx3 array of coordinates to align

        Returns:
            (rotation_matrix, aligned_coords) tuple
        """
        # Center both structures
        p = self.coords - self.coords.mean(axis=0)
        q = target_coords - target_coords.mean(axis=0)

        # Compute covariance matrix
        H = p.T @ q

        # SVD
        U, S, Vt = np.linalg.svd(H)

        # Compute rotation matrix
        d = np.linalg.det(Vt.T @ U.T)
        D = np.diag([1, 1, d])
        R = Vt.T @ D @ U.T

        # Apply rotation
        aligned = q @ R

        return R, aligned

    # ==================== Bond Detection ====================

    def detect_bonds(self, tolerance: float = 0.4) -> List[Bond]:
        """Automatically detect bonds based on covalent radii.

        Args:
            tolerance: Additional distance tolerance in Angstroms

        Returns:
            List of detected Bond objects
        """
        bonds = []
        n = len(self.molecule.atoms)

        for i in range(n):
            for j in range(i + 1, n):
                atom_i = self.molecule.atoms[i]
                atom_j = self.molecule.atoms[j]

                # Get covalent radii
                r_i = get_covalent_radius(atom_i.symbol)
                r_j = get_covalent_radius(atom_j.symbol)

                # Maximum bond distance
                max_dist = r_i + r_j + tolerance

                dist = self.distance(i, j)
                if dist <= max_dist:
                    # Estimate bond order from distance
                    order = self._estimate_bond_order(atom_i.symbol, atom_j.symbol, dist)
                    bonds.append(Bond(i, j, order, dist))

        return bonds

    def _estimate_bond_order(self, elem1: str, elem2: str, distance: float) -> BondOrder:
        """Estimate bond order from distance."""
        r1 = get_covalent_radius(elem1)
        r2 = get_covalent_radius(elem2)
        expected_single = r1 + r2

        ratio = distance / expected_single
        if ratio < 0.78:
            return BondOrder.TRIPLE
        elif ratio < 0.87:
            return BondOrder.DOUBLE
        else:
            return BondOrder.SINGLE

    # ==================== Molecular Descriptors ====================

    def radius_of_gyration(self) -> float:
        """Calculate radius of gyration.

        Returns:
            Rg in Angstroms
        """
        coords = self.coords
        masses = self.molecule.masses
        com = self.molecule.center_of_mass

        # Distance from center of mass
        diff = coords - com
        sq_dist = np.sum(diff ** 2, axis=1)

        return float(np.sqrt(np.sum(masses * sq_dist) / np.sum(masses)))

    def moments_of_inertia(self) -> Tuple[np.ndarray, np.ndarray]:
        """Calculate principal moments of inertia.

        Returns:
            (eigenvalues, eigenvectors) - moments and principal axes
        """
        coords = self.coords
        masses = self.molecule.masses
        com = self.molecule.center_of_mass

        # Translate to center of mass
        r = coords - com

        # Build inertia tensor
        I = np.zeros((3, 3))
        for i, (ri, mi) in enumerate(zip(r, masses)):
            I[0, 0] += mi * (ri[1]**2 + ri[2]**2)
            I[1, 1] += mi * (ri[0]**2 + ri[2]**2)
            I[2, 2] += mi * (ri[0]**2 + ri[1]**2)
            I[0, 1] -= mi * ri[0] * ri[1]
            I[0, 2] -= mi * ri[0] * ri[2]
            I[1, 2] -= mi * ri[1] * ri[2]

        I[1, 0] = I[0, 1]
        I[2, 0] = I[0, 2]
        I[2, 1] = I[1, 2]

        eigenvalues, eigenvectors = np.linalg.eigh(I)
        return eigenvalues, eigenvectors

    def asphericity(self) -> float:
        """Calculate asphericity parameter.

        A measure of deviation from spherical shape.
        0 = perfectly spherical, higher = more elongated

        Returns:
            Asphericity value
        """
        I, _ = self.moments_of_inertia()
        I_sorted = np.sort(I)
        return float(I_sorted[2] - 0.5 * (I_sorted[0] + I_sorted[1]))

    def eccentricity(self) -> float:
        """Calculate molecular eccentricity.

        Returns:
            Eccentricity value [0, 1] where 0 is spherical
        """
        I, _ = self.moments_of_inertia()
        I_sorted = np.sort(I)
        if I_sorted[2] < 1e-10:
            return 0.0
        return float(1.0 - I_sorted[0] / I_sorted[2])

    def surface_area_estimate(self) -> float:
        """Estimate molecular surface area using convex hull.

        This is a rough approximation. For accurate SASA, use
        specialized tools like FreeSASA.

        Returns:
            Estimated surface area in Angstroms^2
        """
        if len(self.molecule.atoms) < 4:
            return 0.0

        try:
            # Expand points by VDW radii
            expanded = []
            for atom in self.molecule.atoms:
                r = atom.vdw_radius
                # Add points on sphere surface
                for theta in np.linspace(0, np.pi, 8):
                    for phi in np.linspace(0, 2*np.pi, 8):
                        x = atom.x + r * np.sin(theta) * np.cos(phi)
                        y = atom.y + r * np.sin(theta) * np.sin(phi)
                        z = atom.z + r * np.cos(theta)
                        expanded.append([x, y, z])

            hull = ConvexHull(np.array(expanded))
            return float(hull.area)
        except Exception:
            return 0.0

    def volume_estimate(self) -> float:
        """Estimate molecular volume using convex hull.

        Returns:
            Estimated volume in Angstroms^3
        """
        if len(self.molecule.atoms) < 4:
            return 0.0

        try:
            expanded = []
            for atom in self.molecule.atoms:
                r = atom.vdw_radius
                for theta in np.linspace(0, np.pi, 6):
                    for phi in np.linspace(0, 2*np.pi, 6):
                        x = atom.x + r * np.sin(theta) * np.cos(phi)
                        y = atom.y + r * np.sin(theta) * np.sin(phi)
                        z = atom.z + r * np.cos(theta)
                        expanded.append([x, y, z])

            hull = ConvexHull(np.array(expanded))
            return float(hull.volume)
        except Exception:
            return 0.0

    def span(self) -> Tuple[float, float, float]:
        """Calculate molecular span in each dimension.

        Returns:
            (x_span, y_span, z_span) in Angstroms
        """
        coords = self.coords
        return (
            float(coords[:, 0].max() - coords[:, 0].min()),
            float(coords[:, 1].max() - coords[:, 1].min()),
            float(coords[:, 2].max() - coords[:, 2].min()),
        )

    def max_diameter(self) -> float:
        """Calculate maximum molecular diameter."""
        dm = self.distance_matrix
        return float(dm.max())

    # ==================== Golden Ratio Analysis ====================

    def phi_ratio_analysis(self) -> Dict[str, Any]:
        """Analyze golden ratio relationships in molecular geometry.

        Searches for phi-harmonic distances, angles, and structural patterns.

        Returns:
            Dictionary containing phi-analysis results
        """
        results = {
            'phi_distances': [],
            'golden_angles': [],
            'phi_score': 0.0,
            'harmonics_found': 0,
        }

        # Analyze distances
        dm = self.distance_matrix
        n = len(self.molecule.atoms)
        phi_distances = []

        for i in range(n):
            for j in range(i + 1, n):
                dist = dm[i, j]
                if is_phi_harmonic(dist, tolerance=0.05):
                    phi_distances.append({
                        'atoms': (i, j),
                        'distance': float(dist),
                        'ratio_to_phi': float(dist / PHI),
                    })

        results['phi_distances'] = phi_distances
        results['harmonics_found'] += len(phi_distances)

        # Analyze angles for golden angle proximity
        golden_angles = []
        for angle_data in self.all_bond_angles():
            idx1, vertex, idx3, angle = angle_data
            # Check proximity to golden angle (~137.5°) or its complement
            if abs(angle - GOLDEN_ANGLE) < 5.0:
                golden_angles.append({
                    'atoms': (idx1, vertex, idx3),
                    'angle': angle,
                    'deviation_from_golden': float(abs(angle - GOLDEN_ANGLE)),
                })
            elif abs(angle - (360 - GOLDEN_ANGLE)) < 5.0:
                golden_angles.append({
                    'atoms': (idx1, vertex, idx3),
                    'angle': angle,
                    'deviation_from_golden_complement': float(abs(angle - (360 - GOLDEN_ANGLE))),
                })

        results['golden_angles'] = golden_angles
        results['harmonics_found'] += len(golden_angles)

        # Compute overall phi score
        total_pairs = n * (n - 1) // 2
        total_angles = len(self.all_bond_angles())
        if total_pairs + total_angles > 0:
            results['phi_score'] = float(
                results['harmonics_found'] / (total_pairs + total_angles) * 100
            )

        return results

    # ==================== Chirality Analysis ====================

    def is_chiral(self, tolerance: float = 1e-3) -> bool:
        """Determine if the molecule is chiral.

        Uses Procrustes analysis to check if the mirror image
        can be superimposed on the original.

        Args:
            tolerance: RMSD tolerance for considering structures identical

        Returns:
            True if molecule is chiral
        """
        coords = self.coords
        # Mirror through origin
        mirrored = -coords

        # Optimal alignment
        _, aligned = self.kabsch_align(mirrored)
        rmsd = np.sqrt(np.mean(np.sum((coords - aligned) ** 2, axis=1)))

        return rmsd > tolerance

    def find_chiral_centers(self) -> List[int]:
        """Find potential chiral centers (sp3 carbons with 4 different substituents).

        This is a simplified detection that identifies carbons with 4 bonds
        to different atom types or groups.

        Returns:
            List of atom indices that are potential chiral centers
        """
        chiral_centers = []

        for i, atom in enumerate(self.molecule.atoms):
            if atom.symbol != 'C':
                continue

            neighbors = self.molecule.get_neighbors(i)
            if len(neighbors) != 4:
                continue

            # Get neighbor symbols
            neighbor_symbols = [self.molecule.atoms[n].symbol for n in neighbors]

            # Simple check: all 4 neighbors different
            if len(set(neighbor_symbols)) == 4:
                chiral_centers.append(i)
            elif len(set(neighbor_symbols)) >= 2:
                # More sophisticated: check if substituents are different
                # This would require recursive group comparison
                # For now, mark as potential
                chiral_centers.append(i)

        return chiral_centers

    # ==================== Summary Statistics ====================

    def summary(self) -> Dict[str, Any]:
        """Generate comprehensive molecular geometry summary.

        Returns:
            Dictionary with all computed descriptors
        """
        phi_analysis = self.phi_ratio_analysis()

        return {
            'name': self.molecule.name,
            'formula': self.molecule.formula,
            'n_atoms': self.molecule.n_atoms,
            'n_bonds': self.molecule.n_bonds,
            'total_mass': self.molecule.total_mass,
            'center_of_mass': self.molecule.center_of_mass.tolist(),
            'centroid': self.molecule.centroid.tolist(),
            'radius_of_gyration': self.radius_of_gyration(),
            'asphericity': self.asphericity(),
            'eccentricity': self.eccentricity(),
            'max_diameter': self.max_diameter(),
            'span': self.span(),
            'surface_area_estimate': self.surface_area_estimate(),
            'volume_estimate': self.volume_estimate(),
            'is_chiral': self.is_chiral(),
            'chiral_centers': self.find_chiral_centers(),
            'phi_score': phi_analysis['phi_score'],
            'phi_harmonics_count': phi_analysis['harmonics_found'],
            'moments_of_inertia': self.moments_of_inertia()[0].tolist(),
        }


# Convenience functions for direct coordinate analysis
def compute_distance(p1: np.ndarray, p2: np.ndarray) -> float:
    """Compute distance between two 3D points."""
    return float(np.linalg.norm(np.asarray(p1) - np.asarray(p2)))


def compute_angle(p1: np.ndarray, p2: np.ndarray, p3: np.ndarray) -> float:
    """Compute angle P1-P2-P3 (P2 is vertex) in degrees."""
    return GeometryAnalyzer.compute_angle(
        np.asarray(p1), np.asarray(p2), np.asarray(p3)
    )


def compute_dihedral(p1: np.ndarray, p2: np.ndarray,
                     p3: np.ndarray, p4: np.ndarray) -> float:
    """Compute dihedral angle in degrees."""
    return GeometryAnalyzer.compute_dihedral(
        np.asarray(p1), np.asarray(p2), np.asarray(p3), np.asarray(p4)
    )
