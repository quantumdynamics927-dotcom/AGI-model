"""Molecular symmetry analysis and point group detection.

This module provides symmetry element detection and point group
classification for molecular structures.
"""
from __future__ import annotations
from typing import List, Tuple, Optional, Dict, Any, Set
from enum import Enum
import numpy as np

from .structures import Molecule
from .constants import PHI


class SymmetryElement(Enum):
    """Types of symmetry elements."""
    IDENTITY = "E"           # Identity
    ROTATION = "Cn"          # n-fold rotation axis
    REFLECTION = "σ"         # Mirror plane
    INVERSION = "i"          # Inversion center
    IMPROPER = "Sn"          # Improper rotation (rotation + reflection)


class PointGroup(Enum):
    """Common molecular point groups."""
    C1 = "C1"       # No symmetry
    Cs = "Cs"       # Single mirror plane
    Ci = "Ci"       # Inversion center only
    C2 = "C2"       # 2-fold rotation
    C3 = "C3"       # 3-fold rotation
    C4 = "C4"       # 4-fold rotation
    C5 = "C5"       # 5-fold rotation
    C6 = "C6"       # 6-fold rotation
    C2v = "C2v"     # C2 + 2 vertical mirror planes
    C3v = "C3v"     # C3 + 3 vertical mirror planes
    C4v = "C4v"     # C4 + 4 vertical mirror planes
    C2h = "C2h"     # C2 + horizontal mirror plane
    D2 = "D2"       # 3 perpendicular C2 axes
    D3 = "D3"       # C3 + 3 perpendicular C2 axes
    D2h = "D2h"     # D2 + inversion
    D3h = "D3h"     # D3 + horizontal mirror
    D4h = "D4h"     # D4 + horizontal mirror
    D5h = "D5h"     # D5 + horizontal mirror (pentagonal)
    D6h = "D6h"     # D6 + horizontal mirror (benzene)
    Td = "Td"       # Tetrahedral
    Oh = "Oh"       # Octahedral
    Ih = "Ih"       # Icosahedral
    Cinfv = "C∞v"   # Linear with no inversion (HCl)
    Dinfh = "D∞h"   # Linear with inversion (CO2)
    UNKNOWN = "?"


class SymmetryAnalyzer:
    """Molecular symmetry analysis.

    Detects symmetry elements and determines point group
    for molecular structures.
    """

    def __init__(self, molecule: Molecule, tolerance: float = 0.1):
        """Initialize symmetry analyzer.

        Args:
            molecule: Molecule to analyze
            tolerance: Distance tolerance in Angstroms for symmetry detection
        """
        self.molecule = molecule
        self.tolerance = tolerance
        self._centered_coords: Optional[np.ndarray] = None
        self._elements: List[Tuple[SymmetryElement, Any]] = []

    @property
    def coords(self) -> np.ndarray:
        """Centered molecular coordinates."""
        if self._centered_coords is None:
            self._centered_coords = self.molecule.coordinates - self.molecule.centroid
        return self._centered_coords

    @property
    def symbols(self) -> List[str]:
        """Element symbols."""
        return self.molecule.symbols

    def analyze(self) -> Dict[str, Any]:
        """Perform complete symmetry analysis.

        Returns:
            Dictionary with symmetry elements and point group
        """
        self._elements = []

        # Always has identity
        self._elements.append((SymmetryElement.IDENTITY, None))

        # Check for inversion center
        has_inversion = self._check_inversion()
        if has_inversion:
            self._elements.append((SymmetryElement.INVERSION, None))

        # Check for rotation axes
        rotation_orders = self._find_rotation_axes()

        # Check for mirror planes
        mirror_planes = self._find_mirror_planes()

        # Determine point group
        point_group = self._determine_point_group(
            has_inversion, rotation_orders, mirror_planes
        )

        return {
            'point_group': point_group.value,
            'symmetry_elements': [
                (elem.value, data) for elem, data in self._elements
            ],
            'has_inversion': has_inversion,
            'rotation_axes': rotation_orders,
            'mirror_planes': len(mirror_planes),
            'is_chiral': not has_inversion and len(mirror_planes) == 0,
        }

    def _check_inversion(self) -> bool:
        """Check for inversion center at origin."""
        coords = self.coords
        symbols = self.symbols

        for i, (coord, sym) in enumerate(zip(coords, symbols)):
            # Find inverted position
            inverted = -coord

            # Check if equivalent atom exists at inverted position
            found = False
            for j, (other_coord, other_sym) in enumerate(zip(coords, symbols)):
                if i == j:
                    continue
                if other_sym != sym:
                    continue
                if np.linalg.norm(inverted - other_coord) < self.tolerance:
                    found = True
                    break

            if not found:
                # Check if atom is at origin (self-inverting)
                if np.linalg.norm(coord) > self.tolerance:
                    return False

        return True

    def _find_rotation_axes(self) -> Dict[int, List[np.ndarray]]:
        """Find rotation axes.

        Returns:
            Dictionary mapping rotation order to list of axis vectors
        """
        axes = {2: [], 3: [], 4: [], 5: [], 6: []}

        # Test common axis candidates
        axis_candidates = self._generate_axis_candidates()

        for axis in axis_candidates:
            for order in [6, 5, 4, 3, 2]:
                if self._is_rotation_axis(axis, order):
                    axes[order].append(axis)
                    self._elements.append((
                        SymmetryElement.ROTATION,
                        {'order': order, 'axis': axis.tolist()}
                    ))
                    break  # Don't double-count (C6 implies C3, C2)

        return axes

    def _generate_axis_candidates(self) -> List[np.ndarray]:
        """Generate candidate rotation axes."""
        candidates = []

        # Principal axes
        candidates.append(np.array([1, 0, 0]))
        candidates.append(np.array([0, 1, 0]))
        candidates.append(np.array([0, 0, 1]))

        # Axes through pairs of equivalent atoms
        coords = self.coords
        symbols = self.symbols

        for i in range(len(coords)):
            for j in range(i + 1, len(coords)):
                if symbols[i] == symbols[j]:
                    # Axis through midpoint
                    midpoint = (coords[i] + coords[j]) / 2
                    if np.linalg.norm(midpoint) > 0.01:
                        candidates.append(midpoint / np.linalg.norm(midpoint))

                    # Axis perpendicular to pair
                    diff = coords[j] - coords[i]
                    if np.linalg.norm(diff) > 0.01:
                        candidates.append(diff / np.linalg.norm(diff))

        # Axes through single atoms
        for coord in coords:
            if np.linalg.norm(coord) > 0.01:
                candidates.append(coord / np.linalg.norm(coord))

        return candidates

    def _is_rotation_axis(self, axis: np.ndarray, order: int) -> bool:
        """Check if axis is a Cn rotation axis."""
        angle = 2 * np.pi / order
        rotation_matrix = self._rotation_matrix(axis, angle)

        rotated = self.coords @ rotation_matrix.T

        # Check if all atoms map to equivalent atoms
        for i, (coord, sym) in enumerate(zip(rotated, self.symbols)):
            found = False
            for j, (orig_coord, orig_sym) in enumerate(zip(self.coords, self.symbols)):
                if orig_sym != sym:
                    continue
                if np.linalg.norm(coord - orig_coord) < self.tolerance:
                    found = True
                    break
            if not found:
                return False

        return True

    def _rotation_matrix(self, axis: np.ndarray, angle: float) -> np.ndarray:
        """Generate 3x3 rotation matrix for rotation around axis."""
        axis = axis / np.linalg.norm(axis)
        cos_a = np.cos(angle)
        sin_a = np.sin(angle)

        K = np.array([
            [0, -axis[2], axis[1]],
            [axis[2], 0, -axis[0]],
            [-axis[1], axis[0], 0]
        ])

        return np.eye(3) + sin_a * K + (1 - cos_a) * (K @ K)

    def _find_mirror_planes(self) -> List[np.ndarray]:
        """Find mirror planes.

        Returns:
            List of plane normal vectors
        """
        planes = []

        # Test coordinate planes
        plane_candidates = [
            np.array([1, 0, 0]),
            np.array([0, 1, 0]),
            np.array([0, 0, 1]),
        ]

        # Add planes through pairs of atoms
        coords = self.coords
        for i in range(len(coords)):
            for j in range(i + 1, len(coords)):
                # Plane perpendicular to line between atoms
                diff = coords[j] - coords[i]
                if np.linalg.norm(diff) > 0.01:
                    plane_candidates.append(diff / np.linalg.norm(diff))

        for normal in plane_candidates:
            if self._is_mirror_plane(normal):
                # Check if we already have this plane
                is_duplicate = False
                for existing in planes:
                    if abs(abs(np.dot(normal, existing)) - 1) < 0.01:
                        is_duplicate = True
                        break
                if not is_duplicate:
                    planes.append(normal)
                    self._elements.append((
                        SymmetryElement.REFLECTION,
                        {'normal': normal.tolist()}
                    ))

        return planes

    def _is_mirror_plane(self, normal: np.ndarray) -> bool:
        """Check if plane (through origin) with given normal is a mirror plane."""
        normal = normal / np.linalg.norm(normal)

        # Reflection matrix
        R = np.eye(3) - 2 * np.outer(normal, normal)

        reflected = self.coords @ R.T

        for i, (coord, sym) in enumerate(zip(reflected, self.symbols)):
            found = False
            for j, (orig_coord, orig_sym) in enumerate(zip(self.coords, self.symbols)):
                if orig_sym != sym:
                    continue
                if np.linalg.norm(coord - orig_coord) < self.tolerance:
                    found = True
                    break
            if not found:
                return False

        return True

    def _determine_point_group(
        self,
        has_inversion: bool,
        rotation_axes: Dict[int, List[np.ndarray]],
        mirror_planes: List[np.ndarray]
    ) -> PointGroup:
        """Determine point group from symmetry elements."""

        n_mirrors = len(mirror_planes)
        max_rotation = max(
            (order for order, axes in rotation_axes.items() if axes),
            default=1
        )
        n_c2 = len(rotation_axes.get(2, []))

        # Check for high symmetry first
        if len(rotation_axes.get(5, [])) >= 6:
            return PointGroup.Ih
        if len(rotation_axes.get(4, [])) >= 3:
            return PointGroup.Oh
        if len(rotation_axes.get(3, [])) >= 4:
            return PointGroup.Td

        # Linear molecules
        if self._is_linear():
            if has_inversion:
                return PointGroup.Dinfh
            return PointGroup.Cinfv

        # Dnh groups
        if max_rotation >= 2 and n_c2 >= max_rotation:
            if has_inversion or n_mirrors > max_rotation:
                group_map = {
                    2: PointGroup.D2h,
                    3: PointGroup.D3h,
                    4: PointGroup.D4h,
                    5: PointGroup.D5h,
                    6: PointGroup.D6h,
                }
                return group_map.get(max_rotation, PointGroup.UNKNOWN)
            else:
                group_map = {2: PointGroup.D2, 3: PointGroup.D3}
                return group_map.get(max_rotation, PointGroup.UNKNOWN)

        # Cnv groups
        if max_rotation >= 2 and n_mirrors >= max_rotation:
            group_map = {
                2: PointGroup.C2v,
                3: PointGroup.C3v,
                4: PointGroup.C4v,
            }
            return group_map.get(max_rotation, PointGroup.UNKNOWN)

        # Cnh groups
        if max_rotation >= 2 and n_mirrors == 1 and has_inversion:
            return PointGroup.C2h

        # Pure rotation groups
        if max_rotation >= 2:
            group_map = {
                2: PointGroup.C2,
                3: PointGroup.C3,
                4: PointGroup.C4,
                5: PointGroup.C5,
                6: PointGroup.C6,
            }
            return group_map.get(max_rotation, PointGroup.UNKNOWN)

        # Low symmetry
        if n_mirrors == 1:
            return PointGroup.Cs
        if has_inversion:
            return PointGroup.Ci

        return PointGroup.C1

    def _is_linear(self) -> bool:
        """Check if molecule is linear."""
        if len(self.molecule.atoms) < 2:
            return True
        if len(self.molecule.atoms) == 2:
            return True

        coords = self.coords

        # Check if all atoms are collinear
        # Use first two atoms to define line
        if len(coords) < 3:
            return True

        v1 = coords[1] - coords[0]
        n1 = np.linalg.norm(v1)
        if n1 < 1e-10:
            return False
        v1 = v1 / n1

        for i in range(2, len(coords)):
            v2 = coords[i] - coords[0]
            n2 = np.linalg.norm(v2)
            if n2 < 1e-10:
                continue
            v2 = v2 / n2

            # Check if parallel (cross product near zero)
            cross = np.cross(v1, v2)
            if np.linalg.norm(cross) > self.tolerance:
                return False

        return True


def analyze_symmetry(molecule: Molecule, tolerance: float = 0.1) -> Dict[str, Any]:
    """Convenience function for symmetry analysis.

    Args:
        molecule: Molecule to analyze
        tolerance: Distance tolerance in Angstroms

    Returns:
        Symmetry analysis results
    """
    analyzer = SymmetryAnalyzer(molecule, tolerance)
    return analyzer.analyze()


def get_point_group(molecule: Molecule, tolerance: float = 0.1) -> str:
    """Get point group symbol for a molecule.

    Args:
        molecule: Molecule to analyze
        tolerance: Distance tolerance in Angstroms

    Returns:
        Point group symbol string
    """
    result = analyze_symmetry(molecule, tolerance)
    return result['point_group']
