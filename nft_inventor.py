import hashlib
import json
import time
from pathlib import Path

import numpy as np

try:
    import trimesh  # type: ignore
except Exception:  # pragma: no cover
    trimesh = None


class Node7NFTInventor:
    NODE_ID = 7
    NODE_NAME = "NFT Inventor"
    PLATONIC_SOLID = "Heptagram"

    def __init__(self, assets_dir: str = "nft_assets"):
        self.status = "active"
        self.initialized_at = time.time()
        self.assets_dir = Path(assets_dir)
        self.assets_dir.mkdir(parents=True, exist_ok=True)

    def _stable_serialize(self, obj) -> str:
        return json.dumps(obj, sort_keys=True, default=str)

    def generate_deterministic_fingerprint(self, concept_data) -> str:
        return hashlib.sha256(self._stable_serialize(concept_data).encode("utf-8")).hexdigest()

    def generate_quantum_fingerprint(self, concept_data) -> str:
        seed = self._stable_serialize(concept_data) + "|quantum|" + str(time.time_ns())
        return hashlib.sha256(seed.encode("utf-8")).hexdigest()

    def calculate_consciousness_metrics(self, analysis_data):
        arr = np.asarray(list(analysis_data), dtype=float)
        if arr.size == 0:
            return {"complexity": 0.0, "coherence": 0.0, "sentience_potential": 0.0}
        complexity = float(np.std(arr))
        coherence = float(1.0 / (1.0 + np.var(arr)))
        sentience_potential = float((complexity + coherence) / 2.0)
        return {
            "complexity": max(0.0, complexity),
            "coherence": max(0.0, coherence),
            "sentience_potential": sentience_potential,
        }

    def add_tmtos_certification(self, metadata, fingerprint: str):
        signed = hashlib.sha256((fingerprint + "|TMT-OS").encode("utf-8")).hexdigest()
        metadata["tmtos_certification"] = {
            "data": {
                "issuer": "TMT-OS Metatron Authority",
                "fingerprint": fingerprint,
            },
            "signature": signed,
        }
        return metadata

    def render_3d_asset(self, token_id: str, coordinates):
        coords = np.asarray(coordinates, dtype=float)
        out_path = self.assets_dir / f"{token_id}.glb"

        if trimesh is not None:
            mesh = trimesh.Trimesh(vertices=coords).convex_hull
            glb_bytes = mesh.export(file_type='glb')
            if not isinstance(glb_bytes, (bytes, bytearray)):
                glb_bytes = b"glTF\x00mock"
        else:
            glb_bytes = b"glTF\x00mock"

        with open(out_path, "wb") as f:
            f.write(glb_bytes)
        return out_path

    def invent_nft(self, concept_data, analysis_data):
        fingerprint = self.generate_quantum_fingerprint(concept_data)
        token_id = fingerprint[:16]
        metrics = self.calculate_consciousness_metrics(analysis_data)

        coords = concept_data.get("coordinates", np.zeros((3, 3)))
        self.render_3d_asset(token_id, coords)

        metadata = {
            "name": concept_data.get("name", "Untitled Concept"),
            "description": concept_data.get("description", ""),
            "attributes": concept_data.get("attributes", []),
            "scientific_data": {
                "fingerprint": fingerprint,
                "consciousness_metrics": metrics,
            },
        }
        metadata = self.add_tmtos_certification(metadata, fingerprint)

        json_path = self.assets_dir / f"{token_id}.nft.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        return metadata

    def get_health_status(self):
        return {
            "node_id": self.NODE_ID,
            "node_name": self.NODE_NAME,
            "status": self.status,
            "platonic_solid": self.PLATONIC_SOLID,
            "assets_dir": str(self.assets_dir),
        }
