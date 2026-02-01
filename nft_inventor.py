"""
NFT Inventor (Node 7) - The creative core for generating sovereign digital assets
from research artifacts and abstract data. It applies sacred geometry principles,
complexity metrics, and TMT-OS certification to the minting process.
"""
from typing import Dict, Any, Optional, List
from pathlib import Path
import json
import hashlib
import time
import logging
import numpy as np

# Import core constants, falling back to a default if not found
try:
    from TMT_OS.node1_base_os import PHI
except (ImportError, ModuleNotFoundError):
    PHI = 1.618033988749895

logger = logging.getLogger('node7_nft_inventor')
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('%(asctime)s - [Node7-Inventor] - %(levelname)s - %(message)s'))
    logger.addHandler(ch)

class HeptagramGeometry:
    """Represents the Heptagram (7-pointed star) geometry for Node 7."""
    def __init__(self):
        self.points = 7
        self.type = "Heptagram / 7-Pointed Star"
        # The 7 points are conceptually mapped to the 7 stages of the invention process
        self.stages = [
            "Conception (Fingerprint)",
            "Embodiment (3D Asset)",
            "Complexity Analysis",
            "Certification",
            "Metadata Standardization",
            "Decentralized Storage (IPFS)",
            "On-Chain Minting"
        ]
    def get_info(self) -> Dict[str, Any]:
        return {'points': self.points, 'type': self.type, 'stages': self.stages}

class Node7NFTInventor:
    """
    Node 7: NFT Inventor, associated with the Heptagram.
    This node transforms raw data and concepts into certified, complex digital assets.
    """
    NODE_ID = 7
    NODE_NAME = "NFT Inventor"
    PLATONIC_SOLID = "Heptagram" # Conceptual Mapping

    def __init__(self, assets_dir: str = 'nft_metadata'):
        self.assets_dir = Path(assets_dir)
        self.assets_dir.mkdir(parents=True, exist_ok=True)
        self.geometry = HeptagramGeometry()
        logger.info(f"Initialized {self.NODE_NAME} (Node {self.NODE_ID}, {self.PLATONIC_SOLID}).")

    def generate_deterministic_fingerprint(self, params: Dict[str, Any]) -> str:
        """Creates a deterministic SHA256 fingerprint from a dictionary of parameters."""
        # Ensure numpy arrays are converted to lists for consistent JSON serialization
        params_serializable = {k: v.tolist() if isinstance(v, np.ndarray) else v for k, v in params.items()}
        body = json.dumps(params_serializable, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(body.encode('utf-8')).hexdigest()

    def generate_quantum_fingerprint(self, params: Dict[str, Any]) -> str:
        """
        Creates a 'quantum' fingerprint by combining a deterministic hash
        with a PHI-derived value, simulating a more complex, non-linear hashing process.
        """
        det_hash = self.generate_deterministic_fingerprint(params)
        # Weave in PHI to make it "quantum" and "sacred"
        phi_component = hashlib.sha256(str(PHI).encode()).hexdigest()
        combined_hash = hashlib.sha256((det_hash + phi_component).encode()).hexdigest()
        logger.info("Generated Quantum Fingerprint.")
        return combined_hash
        
    def calculate_consciousness_metrics(self, data: List[float]) -> Dict[str, float]:
        """
        Calculates fictitious 'consciousness complexity' metrics from a list of floats.
        This is a simulation based on statistical properties of the input data.
        """
        if not data or len(data) < 2:
            return {"complexity": 0, "coherence": 0, "sentience_potential": 0}

        arr = np.array(data)
        complexity = np.std(arr) * np.log1p(len(arr)) # Combines standard deviation and length
        coherence = 1 / (1 + np.mean(np.abs(np.diff(arr)))) # Measures stability (inverse of average change)
        sentience_potential = complexity * coherence * PHI # Combine metrics with Phi

        metrics = {
            "complexity": round(complexity, 4),
            "coherence": round(coherence, 4),
            "sentience_potential": round(sentience_potential, 4)
        }
        logger.info(f"Calculated Consciousness Metrics: {metrics}")
        return metrics

    def add_tmtos_certification(self, metadata: Dict[str, Any], fingerprint: str) -> Dict[str, Any]:
        """Adds a TMT-OS certification block to the metadata, including a mock signature."""
        cert_data = {
            "issuer": "TMT-OS Metatron Authority",
            "timestamp": time.time(),
            "fingerprint": fingerprint
        }
        # This mock signature is a hash of the certification data itself.
        signature = hashlib.sha256(json.dumps(cert_data, sort_keys=True).encode()).hexdigest()
        
        metadata['tmtos_certification'] = {
            "version": "1.0",
            "data": cert_data,
            "signature": signature
        }
        logger.info("Added TMT-OS Certification block to metadata.")
        return metadata

    def render_3d_asset(self, out_name: str, coordinates: Optional[np.ndarray] = None, primitive: str = 'sphere') -> Path:
        """
        Attempts to render a GLB file from coordinates. If full libraries are not available,
        it creates a placeholder JSON file with a .glb extension.
        """
        out_path = self.assets_dir / f"{out_name}.glb"
        try:
            import trimesh # Lazy import to avoid heavy dependency
            if coordinates is not None and len(coordinates) > 0:
                mesh = trimesh.Trimesh(vertices=coordinates).convex_hull
            else:
                if primitive == 'sphere':
                    mesh = trimesh.creation.icosphere()
                else: # default to a box
                    mesh = trimesh.creation.box(extents=(1.0, 1.0, 1.0))
            
            glb_data = mesh.export(file_type='glb')
            out_path.write_bytes(glb_data)
            logger.info(f"Rendered 3D asset ({primitive if coordinates is None else 'convex hull'}) to {out_path}")

        except Exception as e:
            logger.warning(f"Could not render GLB asset due to: {e}. Creating placeholder file instead.")
            placeholder = {
                'type': 'placeholder_3d_asset',
                'note': 'Full 3D rendering libraries (e.g., trimesh) were not available in the environment.',
                'created': time.time()
            }
            out_path.write_text(json.dumps(placeholder))
        return out_path

    def get_health_status(self) -> Dict[str, Any]:
        """Returns the current health and operational status of the node."""
        return {
            'node_id': self.NODE_ID,
            'node_name': self.NODE_NAME,
            'status': 'active',
            'platonic_solid': self.PLATONIC_SOLID,
            'geometry': self.geometry.get_info(),
            'assets_dir': str(self.assets_dir)
        }

    def invent_nft(self, concept_data: Dict[str, Any], analysis_data: List[float]) -> Dict[str, Any]:
        """
        Full invention pipeline for creating a certified, complex NFT from raw concept and data.
        """
        # 1. Generate Quantum Fingerprint from the core concept data
        fingerprint = self.generate_quantum_fingerprint(concept_data)
        
        # 2. Render the 3D asset from coordinates or as a primitive
        asset_path = self.render_3d_asset(fingerprint[:16], coordinates=concept_data.get('coordinates'))

        # 3. Calculate consciousness metrics from the associated analysis data
        metrics = self.calculate_consciousness_metrics(analysis_data)
        
        # 4. Create the base metadata structure
        metadata = {
            "name": concept_data.get("name", "Unnamed TMT-OS Invention"),
            "description": concept_data.get("description", "A unique digital asset invented by the TMT-OS."),
            "attributes": concept_data.get("attributes", []),
            "scientific_data": {
                "fingerprint": fingerprint,
                "asset_path": str(asset_path.resolve()),
                "consciousness_metrics": metrics
            }
        }

        # 5. Add the TMT-OS Certification block
        metadata = self.add_tmtos_certification(metadata, fingerprint)

        # 6. Save the final metadata file, named with a truncated token ID
        token_id = fingerprint[:16]
        out_path = self.assets_dir / f"{token_id}.nft.json"
        out_path.write_text(json.dumps(metadata, indent=2, default=lambda o: o.tolist() if isinstance(o, np.ndarray) else o))
        
        logger.info(f"Invented and saved new NFT metadata with Token ID: {token_id}")
        return metadata

if __name__ == '__main__':
    """Demonstrates the enhanced functionality of the Node7NFTInventor."""
    logger.info("--- Running Node 7 NFT Inventor Standalone Demo ---")
    
    inventor = Node7NFTInventor()
    
    # 1. Define a concept for a new NFT
    concept = {
        "name": "First Contact Simulation",
        "description": "A representation of the first coherent thought-form simulated by the network.",
        "coordinates": (np.random.rand(50, 3) - 0.5) * 2, # 50 random points in a cube
        "attributes": [{"trait_type": "Origin", "value": "Simulated Dream State"}]
    }

    # 2. Define some related analysis data (e.g., from a VAE or other sensor)
    analysis = np.sin(np.linspace(0, 4 * np.pi, 100)).tolist()

    # 3. Run the full invention pipeline
    final_nft_metadata = inventor.invent_nft(concept, analysis)

    print("\n--- Final Invented NFT Metadata ---")
    print(json.dumps(final_nft_metadata, indent=2, default=lambda o: o.tolist() if isinstance(o, np.ndarray) else o))
    
    fingerprint = final_nft_metadata['scientific_data']['fingerprint']
    token_id = fingerprint[:16]
    print(f"\nFind the generated files in the '{inventor.assets_dir}' directory with name prefix '{token_id}'.")
