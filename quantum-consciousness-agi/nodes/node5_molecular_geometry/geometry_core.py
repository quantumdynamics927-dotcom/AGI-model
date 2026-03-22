"""Core geometry utilities for the Molecular Geometry node.
Provides basic bond-angle calculations, chirality heuristics, NFT metadata serialization,
and integration helpers to archive geometry artifacts into the Metatron DNA registry.
"""
from dataclasses import dataclass, asdict
import json
from pathlib import Path
from typing import List, Tuple
import numpy as np

try:
    from metatron_nervous_system import MetatronNervousSystem
except Exception:
    MetatronNervousSystem = None


@dataclass
class GeometryStructure:
    name: str
    atoms: List[str]
    coords: List[Tuple[float, float, float]]

    def to_dict(self):
        return {"name": self.name, "atoms": self.atoms, "coords": self.coords}


class MolecularGeometryAnalyzer:
    """Lightweight molecular geometry utilities."""

    @staticmethod
    def compute_bond_angle(a: Tuple[float, float, float], b: Tuple[float, float, float], c: Tuple[float, float, float]) -> float:
        """Return angle ABC in degrees (B is the vertex).
        a, b, c: 3D coordinates
        """
        A = np.array(a, dtype=float)
        B = np.array(b, dtype=float)
        C = np.array(c, dtype=float)
        BA = A - B
        BC = C - B
        # guard against zeros
        if np.linalg.norm(BA) == 0 or np.linalg.norm(BC) == 0:
            return 0.0
        cos_theta = np.dot(BA, BC) / (np.linalg.norm(BA) * np.linalg.norm(BC))
        cos_theta = float(np.clip(cos_theta, -1.0, 1.0))
        theta = np.arccos(cos_theta)
        return float(np.degrees(theta))

    @staticmethod
    def center_of_mass(coords: List[Tuple[float, float, float]], masses: List[float] = None) -> Tuple[float, float, float]:
        arr = np.array(coords, dtype=float)
        if masses is None:
            return tuple(np.mean(arr, axis=0))
        m = np.array(masses, dtype=float)
        return tuple((arr.T * m).sum(axis=1) / m.sum())

    @staticmethod
    def is_chiral(coords: List[Tuple[float, float, float]], tol: float = 1e-3) -> bool:
        """Basic chirality heuristic: checks if mirrored coords (over origin) can be mapped by translation+rotation.
        This is a conservative, non-robust check intended for lightweight filtering in tests and pipelines.
        """
        arr = np.array(coords, dtype=float)
        mirrored = -arr
        # Use Procrustes-style alignment: subtract centroids and compare residual norm
        def norm_after_align(X, Y):
            Xc = X - X.mean(axis=0)
            Yc = Y - Y.mean(axis=0)
            # best-fit orthogonal transform via SVD
            U, s, Vt = np.linalg.svd(Xc.T.dot(Yc))
            R = U.dot(Vt)
            Xr = Xc.dot(R)
            return np.linalg.norm(Xr - Yc)
        resid = norm_after_align(arr, mirrored)
        return resid > tol

    @staticmethod
    def to_nft_metadata(struct: GeometryStructure) -> dict:
        # compute some basic geometric descriptors
        coords = struct.coords
        angles = []
        # sample sequential triplets
        for i in range(len(coords) - 2):
            ang = MolecularGeometryAnalyzer.compute_bond_angle(coords[i], coords[i+1], coords[i+2])
            angles.append(ang)
        metadata = {
            'name': struct.name,
            'n_atoms': len(struct.atoms),
            'avg_bond_angle': float(np.mean(angles)) if angles else None,
            'is_chiral': MolecularGeometryAnalyzer.is_chiral(coords) if len(coords) >= 4 else False,
            'angles_sample': angles[:10]
        }
        return metadata

    @staticmethod
    def save_structure(path: Path, struct: GeometryStructure) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(struct.to_dict(), indent=2))
        return path

    @staticmethod
    def archive_with_metatron(struct_path: Path, registry: Path, client: str = 'molecular_geometry', hmac_key: str = None) -> Path:
        """If MetatronNervousSystem is available, create a DNA packet for the structure and archive it."""
        if MetatronNervousSystem is None:
            raise RuntimeError('MetatronNervousSystem is not available in this environment')
        m = MetatronNervousSystem(registry)
        packet = m.create_packet(struct_path, client=client, hmac_key=hmac_key)
        return m.archive_packet(packet)
