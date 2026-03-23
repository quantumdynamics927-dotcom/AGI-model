"""
Node 5: Molecular Geometry (Octahedron)

This module provides spatial intelligence capabilities for analyzing molecular
structures. It is mapped to the Octahedron, representing complex structure and
higher-order organization.
"""

import numpy as np
import matplotlib.pyplot as plt
import logging
import os
import json
from typing import Dict, Any, List

# Configure logging for the node
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(ch)

# A simple dictionary of atomic masses for analysis.
# A real-world application should use a comprehensive library like mendeleev or periodictable.
ATOMIC_MASSES = {
    "H": 1.008,
    "C": 12.011,
    "N": 14.007,
    "O": 15.999,
    "F": 18.998,
    "P": 30.974,
    "S": 32.06,
    "Cl": 35.45,
    "DEFAULT": 1.0,  # Default mass for unknown elements
}


def _truncate(values: np.ndarray, decimals: int = 3) -> np.ndarray:
    factor = 10**decimals
    return np.trunc(values * factor) / factor


class Node5SpatialIntelligence:
    """
    Implements the functionality for Node 5, providing spatial analysis and
    visualization of molecular data, associated with the Octahedron.
    """

    NODE_ID = 5
    NODE_NAME = "Molecular Geometry"
    PLATONIC_SOLID = "Octahedron"
    GEOMETRY = {"faces": 8, "vertices": 6, "edges": 12}

    def __init__(self):
        """Initializes the Node 5 instance."""
        self.status = "active"
        logger.info(
            f"Initialized {self.NODE_NAME} (Node {self.NODE_ID}, {self.PLATONIC_SOLID})."
        )

    def analyze_structure(
        self, symbols: List[str], coords: np.ndarray
    ) -> Dict[str, Any]:
        """
        Performs a basic geometric and mass-based analysis of the molecular structure.

        Args:
            symbols: A list of atomic symbols (e.g., ['C', 'H', 'H', 'H', 'H']).
            coords: A NumPy array of atomic coordinates (shape: [N, 3]).

        Returns:
            A dictionary containing analysis results like center of mass and radius of gyration.
        """
        if (
            not isinstance(coords, np.ndarray)
            or coords.ndim != 2
            or coords.shape[1] != 3
        ):
            raise ValueError("Coordinates must be a NumPy array of shape [N, 3].")
        if len(symbols) != coords.shape[0]:
            raise ValueError(
                "Length of symbols list must match the number of coordinates."
            )

        masses = np.array(
            [ATOMIC_MASSES.get(s.upper(), ATOMIC_MASSES["DEFAULT"]) for s in symbols]
        )
        total_mass = np.sum(masses)

        # Center of Mass Calculation
        center_of_mass = np.sum(coords * masses[:, np.newaxis], axis=0) / total_mass

        # Geometric spread summary around the centroid.
        centroid = np.mean(coords, axis=0)
        centered_coords = coords - centroid
        radius_of_gyration = np.mean(np.linalg.norm(centered_coords, axis=1))

        analysis = {
            "num_atoms": len(symbols),
            "total_mass": float(total_mass),
            "center_of_mass": _truncate(center_of_mass, 3).tolist(),
            "radius_of_gyration": float(radius_of_gyration),
        }
        logger.info(
            f"Analyzed structure with {analysis['num_atoms']} atoms. RoG: {radius_of_gyration:.3f} Å."
        )
        return analysis

    def recognize_patterns(
        self, coords: np.ndarray, tolerance: float = 0.1
    ) -> Dict[str, bool]:
        """
        Recognizes simple spatial patterns (linearity, planarity) in the molecular structure.

        Args:
            coords: A NumPy array of atomic coordinates.
            tolerance: The numerical tolerance for checking alignment to a line or plane.

        Returns:
            A dictionary indicating detected patterns (e.g., 'is_linear', 'is_planar').
        """
        if coords.shape[0] < 3:
            return {"is_linear": True, "is_planar": True}

        # Check for linearity
        p1, p2 = coords[0], coords[1]
        line_vec = p2 - p1
        norm = np.linalg.norm(line_vec)
        if norm == 0:
            return {"is_linear": False, "is_planar": False}
        line_vec /= norm

        distances_from_line = [
            np.linalg.norm(np.cross(line_vec, p - p1)) for p in coords
        ]
        is_linear = all(d < tolerance for d in distances_from_line)

        # Check for planarity using Singular Value Decomposition (SVD)
        centered_coords = coords - np.mean(coords, axis=0)
        _, s, _ = np.linalg.svd(centered_coords)
        # The smallest singular value indicates the deviation from the best-fit plane.
        is_planar = s[2] < tolerance if len(s) > 2 else True

        patterns = {
            "is_linear": bool(is_linear),
            "is_planar": bool(is_planar and not is_linear),
        }
        logger.info(f"Pattern recognition results: {patterns}")
        return patterns

    def generate_3d_visualization(
        self,
        symbols: List[str],
        coords: np.ndarray,
        output_path: str,
        interactive: bool = False,
    ) -> str:
        """
        Generates and saves a 3D scatter plot of the molecule, with optional bond visualization.

        Args:
            symbols: A list of atomic symbols for coloring.
            coords: A NumPy array of atomic coordinates.
            output_path: The file path to save the visualization (e.g., 'molecule.png').
            interactive: If True, display interactive plot instead of saving.

        Returns:
            The absolute path to the saved image file (or empty string if interactive).
        """
        if interactive:
            try:
                import plotly.graph_objects as go

                fig = go.Figure()
                # Color-code atoms
                color_map = {"C": "black", "H": "lightgray", "O": "red", "N": "blue"}
                colors = [color_map.get(s.upper(), "purple") for s in symbols]
                sizes = [ATOMIC_MASSES.get(s.upper(), 1.0) * 10 for s in symbols]

                # Add atoms
                fig.add_trace(
                    go.Scatter3d(
                        x=coords[:, 0],
                        y=coords[:, 1],
                        z=coords[:, 2],
                        mode="markers",
                        marker=dict(size=sizes, color=colors, opacity=0.8),
                        name="Atoms",
                    )
                )

                # Add bonds
                bond_threshold = 1.2  # Å
                for i in range(len(coords)):
                    for j in range(i + 1, len(coords)):
                        dist = np.linalg.norm(coords[i] - coords[j])
                        if dist < bond_threshold:
                            fig.add_trace(
                                go.Scatter3d(
                                    x=[coords[i, 0], coords[j, 0]],
                                    y=[coords[i, 1], coords[j, 1]],
                                    z=[coords[i, 2], coords[j, 2]],
                                    mode="lines",
                                    line=dict(color="gray", width=5),
                                    showlegend=False,
                                )
                            )

                fig.update_layout(
                    scene=dict(
                        xaxis_title="X (Å)", yaxis_title="Y (Å)", zaxis_title="Z (Å)"
                    ),
                    title=f"Molecular Structure ({len(symbols)} atoms)",
                )
                fig.show()
                logger.info("Displayed interactive 3D visualization")
                return ""
            except ImportError:
                logger.warning("Plotly not available, falling back to matplotlib")
                interactive = False

        # Matplotlib version
        fig = plt.figure(figsize=(8, 8))
        ax = fig.add_subplot(111, projection="3d")

        # Color-code atoms for better visualization
        color_map = {"C": "black", "H": "lightgray", "O": "red", "N": "blue"}
        colors = [color_map.get(s.upper(), "purple") for s in symbols]
        sizes = [ATOMIC_MASSES.get(s.upper(), 1.0) * 10 for s in symbols]

        ax.scatter(
            coords[:, 0],
            coords[:, 1],
            coords[:, 2],
            c=colors,
            s=sizes,
            edgecolors="k",
            alpha=0.8,
        )

        # Draw bonds
        bond_threshold = 1.2  # Å
        for i in range(len(coords)):
            for j in range(i + 1, len(coords)):
                dist = np.linalg.norm(coords[i] - coords[j])
                if dist < bond_threshold:
                    ax.plot(
                        [coords[i, 0], coords[j, 0]],
                        [coords[i, 1], coords[j, 1]],
                        [coords[i, 2], coords[j, 2]],
                        color="gray",
                        linewidth=2,
                    )

        ax.set_xlabel("X (Å)")
        ax.set_ylabel("Y (Å)")
        ax.set_zlabel("Z (Å)")
        ax.set_title(f"Molecular Structure ({len(symbols)} atoms)")

        if not interactive:
            try:
                plt.savefig(output_path, dpi=150, bbox_inches="tight")
            finally:
                plt.close(fig)  # Ensure figure is closed to free memory

            abs_path = os.path.abspath(output_path)
            logger.info(f"Generated 3D visualization at '{abs_path}'")
            return abs_path
        else:
            plt.show()
            plt.close(fig)
            logger.info("Displayed interactive matplotlib visualization")
            return ""

    def get_health_status(self) -> Dict[str, Any]:
        """Returns the health status of the node."""
        return {
            "node_id": self.NODE_ID,
            "node_name": self.NODE_NAME,
            "status": self.status,
            "platonic_solid": self.PLATONIC_SOLID,
        }


if __name__ == "__main__":
    """Demonstrates the functionality of the Node5SpatialIntelligence class."""
    logger.info("--- Running Node 5 Spatial Intelligence Standalone Demo ---")

    # Example 1: Methane (CH4) - a tetrahedral molecule
    methane_symbols = ["C", "H", "H", "H", "H"]
    methane_coords = np.array(
        [
            [0.000, 0.000, 0.000],  # C
            [0.629, 0.629, 0.629],  # H1
            [-0.629, -0.629, 0.629],  # H2
            [-0.629, 0.629, -0.629],  # H3
            [0.629, -0.629, -0.629],  # H4
        ]
    )

    node5 = Node5SpatialIntelligence()

    # 1. Analyze the structure
    analysis = node5.analyze_structure(methane_symbols, methane_coords)
    print(f"\nAnalysis of Methane:\n{json.dumps(analysis, indent=2)}")

    # 2. Recognize patterns
    patterns = node5.recognize_patterns(methane_coords)
    print(f"\nPattern Recognition for Methane:\n{json.dumps(patterns, indent=2)}")
    assert not patterns["is_linear"] and not patterns["is_planar"]

    # 3. Generate visualization
    viz_path = "methane_visualization.png"
    if os.path.exists(viz_path):
        os.remove(viz_path)
    saved_path = node5.generate_3d_visualization(
        methane_symbols, methane_coords, viz_path
    )
    print(f"\nVisualization saved to: {saved_path}")
    assert os.path.exists(saved_path)

    # Example 2: Water (H2O) - a planar molecule
    water_symbols = ["O", "H", "H"]
    water_coords = np.array(
        [[0.0, 0.0, 0.0], [0.757, 0.586, 0.0], [-0.757, 0.586, 0.0]]
    )
    water_patterns = node5.recognize_patterns(water_coords)
    print(f"\nPattern Recognition for Water:\n{json.dumps(water_patterns, indent=2)}")
    assert water_patterns["is_planar"]

    logger.info("--- Node 5 Demo Finished ---")
