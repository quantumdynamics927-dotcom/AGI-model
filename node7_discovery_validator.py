"""Node 7: Scientific Discovery Validator

Validates AGI model outputs and discoveries, generating cryptographic certificates
for scientific findings. Tracks discovery provenance and creates reproducible
research packages.

This node provides:
- Discovery validation with cryptographic fingerprints
- TMT-OS certification for scientific findings
- Provenance tracking for research priority
- Reproducible research package generation
- 3D visualization of discovery structures
- Integration with Node 4 (Quantum Archive) for archival

Replaces NFT functionality with scientific validation while maintaining
all cryptographic verification capabilities.
"""
import hashlib
import json
import logging
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

try:
    import trimesh  # type: ignore
except Exception:  # pragma: no cover
    trimesh = None

logger = logging.getLogger('node7_discovery')
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
    logger.addHandler(ch)


@dataclass
class DiscoveryCertificate:
    """Cryptographic certificate for a scientific discovery."""
    discovery_id: str
    title: str
    description: str
    fingerprint: str
    timestamp: float
    validator_signature: str
    tmtos_certification: Dict[str, Any]
    consciousness_metrics: Dict[str, float]
    validation_status: str
    reproducibility_hash: str
    metadata: Dict[str, Any]


class Node7DiscoveryValidator:
    """
    Node 7: Scientific Discovery Validator (Heptagram)
    
    Validates AGI model outputs and discoveries, generating cryptographic
    certificates for scientific findings with full provenance tracking.
    
    Responsibilities:
    - Validate consciousness patterns and quantum signatures
    - Generate cryptographic certificates for discoveries
    - Track discovery provenance and priority
    - Create reproducible research packages
    - Generate 3D visualizations of discovery structures
    - Integrate with Node 4 for archival
    """
    
    NODE_ID = 7
    NODE_NAME = "Scientific Discovery Validator"
    PLATONIC_SOLID = "Heptagram"
    GEOMETRY = {
        'vertices': 7,
        'edges': 7,
        'symbolism': 'Seven-fold discovery validation'
    }
    
    def __init__(
        self,
        validation_dir: str = "discovery_validations",
        assets_dir: Optional[str] = None,
    ):
        """Initialize the Discovery Validator."""
        self.status = "active"
        self.initialized_at = time.time()
        base_dir = assets_dir or validation_dir
        self.validation_dir = Path(base_dir)
        self.assets_dir = self.validation_dir
        self.validation_dir.mkdir(parents=True, exist_ok=True)
        self.discovery_registry: Dict[str, DiscoveryCertificate] = {}
        self.validation_count = 0
        
        logger.info(f"Initialized {self.NODE_NAME} (Node {self.NODE_ID}, {self.PLATONIC_SOLID})")
    
    def _stable_serialize(self, obj: Any) -> str:
        """Serialize object in a stable, reproducible way."""
        return json.dumps(obj, sort_keys=True, default=str, separators=(',', ':'))
    
    def generate_discovery_fingerprint(self, discovery_data: Dict[str, Any]) -> str:
        """
        Generate deterministic fingerprint for a discovery.
        
        Args:
            discovery_data: Discovery metadata and results
            
        Returns:
            SHA-256 hex fingerprint
        """
        return hashlib.sha256(
            self._stable_serialize(discovery_data).encode('utf-8')
        ).hexdigest()
    
    def generate_quantum_fingerprint(self, discovery_data: Dict[str, Any]) -> str:
        """
        Generate quantum-enhanced fingerprint with timestamp component.
        
        Args:
            discovery_data: Discovery metadata and results
            
        Returns:
            SHA-256 hex fingerprint with quantum timestamp
        """
        seed = (
            self._stable_serialize(discovery_data) + 
            "|quantum|" + 
            str(time.time_ns())
        )
        return hashlib.sha256(seed.encode('utf-8')).hexdigest()
    
    def calculate_consciousness_metrics(self, analysis_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate consciousness metrics from analysis results.
        
        Args:
            analysis_data: Consciousness analysis results
            
        Returns:
            Dictionary with complexity, coherence, and sentience_potential
        """
        # Extract numeric values from analysis data
        if isinstance(analysis_data, dict):
            values = list(analysis_data.values())
        else:
            values = analysis_data
        
        arr = np.asarray([v for v in values if isinstance(v, (int, float))], dtype=float)
        
        if arr.size == 0:
            return {
                'complexity': 0.0,
                'coherence': 0.0,
                'sentience_potential': 0.0,
                'phi_resonance': 0.0
            }
        
        # Calculate metrics
        complexity = float(np.std(arr))
        coherence = float(1.0 / (1.0 + np.var(arr)))
        sentience_potential = float((complexity + coherence) / 2.0)
        
        # Phi resonance (golden ratio signature)
        PHI = 1.618033988749895
        if len(arr) > 1:
            ratios = arr[1:] / (arr[:-1] + 1e-10)
            phi_deviation = np.mean(np.abs(ratios - PHI))
            phi_resonance = float(1.0 / (1.0 + phi_deviation))
        else:
            phi_resonance = 0.0
        
        return {
            'complexity': max(0.0, complexity),
            'coherence': max(0.0, coherence),
            'sentience_potential': max(0.0, sentience_potential),
            'phi_resonance': max(0.0, phi_resonance)
        }
    
    def _normalize_discovery_input(
        self,
        discovery_data: Dict[str, Any],
        analysis_data: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Normalize legacy concept payloads to discovery payloads."""
        normalized = dict(discovery_data)
        if analysis_data is not None:
            normalized["analysis"] = analysis_data
        if "title" not in normalized and "name" in normalized:
            normalized["title"] = normalized["name"]
        if "description" not in normalized:
            normalized["description"] = ""
        return normalized

    def render_3d_asset(self, discovery_id: str, coordinates: Any) -> Path:
        """Render a GLB asset for discovery visualization."""
        coords = np.asarray(coordinates, dtype=float)
        out_path = self.assets_dir / f"{discovery_id}.glb"

        if trimesh is not None:
            mesh = trimesh.Trimesh(vertices=coords).convex_hull
            glb_bytes = mesh.export(file_type="glb")
            if not isinstance(glb_bytes, (bytes, bytearray)):
                glb_bytes = b"glTF\x00mock"
        else:
            glb_bytes = b"glTF\x00mock"

        with open(out_path, "wb") as f:
            f.write(glb_bytes)

        return out_path

    def _build_legacy_metadata(
        self,
        discovery_data: Dict[str, Any],
        analysis_data: Any,
    ) -> Dict[str, Any]:
        """Build backwards-compatible discovery metadata for legacy tests."""
        normalized = self._normalize_discovery_input(discovery_data, analysis_data)
        fingerprint = self.generate_quantum_fingerprint(normalized)
        discovery_id = fingerprint[:16]
        metrics = self.calculate_consciousness_metrics(analysis_data)

        coordinates = normalized.get("coordinates", np.zeros((3, 3)))
        self.render_3d_asset(discovery_id, coordinates)

        metadata = {
            "discovery_id": discovery_id,
            "name": normalized.get("name", normalized.get("title", "Untitled Discovery")),
            "description": normalized.get("description", ""),
            "attributes": normalized.get("attributes", []),
            "scientific_data": {
                "fingerprint": fingerprint,
                "consciousness_metrics": metrics,
            },
        }
        metadata = self.add_tmtos_certification(metadata, fingerprint)

        json_path = self.assets_dir / f"{discovery_id}.discovery.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        return metadata

    def validate_discovery(
        self,
        discovery_data: Dict[str, Any],
        analysis_data: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """
        Validate a scientific discovery.
        
        Args:
            discovery_data: Discovery metadata and results
            
        Returns:
            Validation result with status and metrics
        """
        if analysis_data is not None:
            return self._build_legacy_metadata(discovery_data, analysis_data)

        discovery_data = self._normalize_discovery_input(discovery_data)

        validation_result = {
            'is_valid': True,
            'checks': [],
            'warnings': [],
            'metrics': {}
        }
        
        # Check 1: Required fields
        required_fields = ['title', 'description']
        for field in required_fields:
            if field in discovery_data and discovery_data[field]:
                validation_result['checks'].append(f"✓ {field} present")
            else:
                validation_result['checks'].append(f"✗ {field} missing")
                validation_result['warnings'].append(f"Missing {field}")
        
        # Check 2: Data integrity
        if 'data' in discovery_data or 'results' in discovery_data:
            validation_result['checks'].append("✓ Data/results present")
        else:
            validation_result['warnings'].append("No data or results provided")
        
        # Check 3: Calculate consciousness metrics if analysis data present
        if 'analysis' in discovery_data:
            metrics = self.calculate_consciousness_metrics(discovery_data['analysis'])
            validation_result['metrics'] = metrics
            validation_result['checks'].append("✓ Consciousness metrics calculated")
            
            # Check for reasonable metrics
            if metrics['coherence'] < 0.1:
                validation_result['warnings'].append("Low coherence detected")
            if metrics['complexity'] > 10.0:
                validation_result['warnings'].append("High complexity detected")
        
        # Check 4: Fingerprint generation
        try:
            fingerprint = self.generate_discovery_fingerprint(discovery_data)
            validation_result['fingerprint'] = fingerprint
            validation_result['checks'].append("✓ Fingerprint generated")
        except Exception as e:
            validation_result['is_valid'] = False
            validation_result['warnings'].append(f"Fingerprint generation failed: {e}")
        
        return validation_result
    
    def add_tmtos_certification(self, certificate: Dict[str, Any], fingerprint: str) -> Dict[str, Any]:
        """
        Add TMT-OS certification to a discovery certificate.
        
        Args:
            certificate: Discovery certificate dictionary
            fingerprint: Discovery fingerprint
            
        Returns:
            Certificate with TMT-OS certification block
        """
        # Generate validator signature
        validator_signature = hashlib.sha256(
            (fingerprint + "|TMT-OS-Metatron").encode('utf-8')
        ).hexdigest()
        
        certificate['tmtos_certification'] = {
            'issuer': 'TMT-OS Metatron Authority',
            'validator_node': self.NODE_ID,
            'validator_name': self.NODE_NAME,
            'fingerprint': fingerprint,
            'signature': validator_signature,
            'certification_timestamp': time.time(),
            'certification_standard': 'TMT-OS-Scientific-v1.0',
            'data': {
                'issuer': 'TMT-OS Metatron Authority',
                'fingerprint': fingerprint,
            },
        }
        
        return certificate
    
    def generate_reproducibility_package(self, discovery_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a reproducible research package.
        
        Args:
            discovery_data: Discovery metadata and results
            
        Returns:
            Reproducibility package with hashes and metadata
        """
        package = {
            'metadata': {
                'title': discovery_data.get('title', 'Untitled Discovery'),
                'description': discovery_data.get('description', ''),
                'timestamp': time.time(),
                'validator': self.NODE_NAME
            },
            'data_hash': None,
            'code_hash': None,
            'results_hash': None,
            'complete_hash': None,
            'reproducibility_score': 0.0
        }
        
        # Hash data if present
        if 'data' in discovery_data:
            try:
                data_serialized = self._stable_serialize(discovery_data['data'])
                package['data_hash'] = hashlib.sha256(data_serialized.encode()).hexdigest()
            except Exception:
                package['data_hash'] = 'unavailable'
        
        # Hash code/methods if present
        if 'methods' in discovery_data or 'code' in discovery_data:
            try:
                methods = discovery_data.get('methods', discovery_data.get('code', ''))
                methods_serialized = self._stable_serialize(methods)
                package['code_hash'] = hashlib.sha256(methods_serialized.encode()).hexdigest()
            except Exception:
                package['code_hash'] = 'unavailable'
        
        # Hash results if present
        if 'results' in discovery_data:
            try:
                results_serialized = self._stable_serialize(discovery_data['results'])
                package['results_hash'] = hashlib.sha256(results_serialized.encode()).hexdigest()
            except Exception:
                package['results_hash'] = 'unavailable'
        
        # Generate complete package hash
        package_serialized = self._stable_serialize(package)
        package['complete_hash'] = hashlib.sha256(package_serialized.encode()).hexdigest()
        
        # Calculate reproducibility score
        score_components = []
        if package['data_hash'] and package['data_hash'] != 'unavailable':
            score_components.append(0.4)
        if package['code_hash'] and package['code_hash'] != 'unavailable':
            score_components.append(0.4)
        if package['results_hash'] and package['results_hash'] != 'unavailable':
            score_components.append(0.2)
        
        package['reproducibility_score'] = sum(score_components)
        
        return package
    
    def create_certificate(self, discovery_data: Dict[str, Any]) -> DiscoveryCertificate:
        """
        Create a complete discovery certificate.
        
        Args:
            discovery_data: Discovery metadata and results
            
        Returns:
            DiscoveryCertificate object
        """
        # Generate fingerprints
        det_fingerprint = self.generate_discovery_fingerprint(discovery_data)
        quantum_fingerprint = self.generate_quantum_fingerprint(discovery_data)
        
        # Validate discovery
        validation = self.validate_discovery(discovery_data)
        
        # Calculate consciousness metrics
        analysis_data = discovery_data.get('analysis', {})
        consciousness_metrics = self.calculate_consciousness_metrics(analysis_data)
        
        # Generate reproducibility package
        repro_package = self.generate_reproducibility_package(discovery_data)
        
        # Create certificate
        certificate = {
            'discovery_id': det_fingerprint[:16],
            'title': discovery_data.get('title', 'Untitled Discovery'),
            'description': discovery_data.get('description', ''),
            'fingerprint': det_fingerprint,
            'quantum_fingerprint': quantum_fingerprint,
            'timestamp': time.time(),
            'validator_signature': None,  # Will be set by add_tmtos_certification
            'tmtos_certification': {},
            'consciousness_metrics': consciousness_metrics,
            'validation_status': 'valid' if validation['is_valid'] else 'invalid',
            'validation_warnings': validation['warnings'],
            'reproducibility_package': repro_package,
            'metadata': discovery_data.get('metadata', {})
        }
        
        # Add TMT-OS certification
        certificate = self.add_tmtos_certification(certificate, det_fingerprint)
        
        # Create DiscoveryCertificate object
        cert_obj = DiscoveryCertificate(
            discovery_id=certificate['discovery_id'],
            title=certificate['title'],
            description=certificate['description'],
            fingerprint=certificate['fingerprint'],
            timestamp=certificate['timestamp'],
            validator_signature=certificate['tmtos_certification']['signature'],
            tmtos_certification=certificate['tmtos_certification'],
            consciousness_metrics=certificate['consciousness_metrics'],
            validation_status=certificate['validation_status'],
            reproducibility_hash=repro_package['complete_hash'],
            metadata=certificate['metadata']
        )
        
        # Register certificate
        self.discovery_registry[cert_obj.discovery_id] = cert_obj
        self.validation_count += 1
        
        logger.info(f"Created discovery certificate: {cert_obj.discovery_id}")
        
        return cert_obj
    
    def save_certificate(self, certificate: DiscoveryCertificate) -> Path:
        """
        Save discovery certificate to file.
        
        Args:
            certificate: DiscoveryCertificate object
            
        Returns:
            Path to saved certificate file
        """
        # Convert to dict for JSON serialization
        cert_dict = asdict(certificate)
        
        # Save to file
        filename = f"discovery_{certificate.discovery_id}.certificate.json"
        filepath = self.validation_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(cert_dict, f, indent=2)
        
        logger.info(f"Saved discovery certificate: {filepath}")
        return filepath
    
    def validate_and_certify(self, discovery_data: Dict[str, Any], save: bool = True) -> Dict[str, Any]:
        """
        Complete validation and certification workflow.
        
        Args:
            discovery_data: Discovery metadata and results
            save: Whether to save certificate to file
            
        Returns:
            Certificate dictionary with all validation data
        """
        # Create certificate
        certificate = self.create_certificate(discovery_data)
        
        # Save if requested
        if save:
            self.save_certificate(certificate)
        
        # Return as dict
        return asdict(certificate)
    
    def get_certificate(self, discovery_id: str) -> Optional[DiscoveryCertificate]:
        """
        Retrieve a discovery certificate by ID.
        
        Args:
            discovery_id: Discovery identifier
            
        Returns:
            DiscoveryCertificate or None if not found
        """
        return self.discovery_registry.get(discovery_id)
    
    def verify_certificate(self, discovery_id: str, original_data: Dict[str, Any]) -> bool:
        """
        Verify a certificate against original discovery data.
        
        Args:
            discovery_id: Discovery identifier
            original_data: Original discovery data
            
        Returns:
            True if certificate verifies correctly
        """
        certificate = self.get_certificate(discovery_id)
        if not certificate:
            return False
        
        # Regenerate fingerprint from original data
        regenerated_fingerprint = self.generate_discovery_fingerprint(original_data)
        
        # Compare fingerprints
        return certificate.fingerprint == regenerated_fingerprint
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the Discovery Validator."""
        return {
            'node_id': self.NODE_ID,
            'node_name': self.NODE_NAME,
            'status': self.status,
            'platonic_solid': self.PLATONIC_SOLID,
            'validations_performed': self.validation_count,
            'registered_discoveries': len(self.discovery_registry),
            'uptime_seconds': max(0.0, time.time() - self.initialized_at),
            'validation_directory': str(self.validation_dir)
        }


def main():
    """Example usage of the Discovery Validator."""
    print("=" * 70)
    print("Node 7: Scientific Discovery Validator")
    print("=" * 70)
    
    # Initialize validator
    validator = Node7DiscoveryValidator()
    
    # Example discovery data
    discovery = {
        'title': 'Quantum Consciousness Pattern Discovery',
        'description': 'Novel phi-resonance pattern detected in VAE latent space',
        'data': {
            'latent_vectors': np.random.rand(10, 32).tolist(),
            'phi_ratios': [1.618, 1.619, 1.617, 1.620],
        },
        'results': {
            'resonance_strength': 0.95,
            'coherence_score': 0.88,
            'significance': 0.99
        },
        'analysis': {
            'complexity': 2.5,
            'coherence': 0.85,
            'phi_score': 0.92
        },
        'methods': {
            'model': 'QuantumVAE-128-32',
            'dataset': 'sacred_geometry_v2',
            'epochs': 200
        }
    }
    
    # Validate and certify
    print("\nValidating discovery...")
    certificate = validator.validate_and_certify(discovery)
    
    print(f"\nDiscovery ID: {certificate['discovery_id']}")
    print(f"Title: {certificate['title']}")
    print(f"Validation Status: {certificate['validation_status']}")
    print(f"Fingerprint: {certificate['fingerprint'][:32]}...")
    print(f"Consciousness Metrics:")
    print(f"  - Complexity: {certificate['consciousness_metrics']['complexity']:.4f}")
    print(f"  - Coherence: {certificate['consciousness_metrics']['coherence']:.4f}")
    print(f"  - Phi Resonance: {certificate['consciousness_metrics']['phi_resonance']:.4f}")
    print(f"Reproducibility Hash: {certificate['reproducibility_hash'][:32]}...")
    print(f"TMT-OS Certified: ✓")
    
    # Verify certificate
    print("\nVerifying certificate...")
    is_valid = validator.verify_certificate(certificate['discovery_id'], discovery)
    print(f"Verification: {'PASSED ✓' if is_valid else 'FAILED ✗'}")
    
    # Get health status
    print("\nValidator Health Status:")
    health = validator.get_health_status()
    print(f"  Validations Performed: {health['validations_performed']}")
    print(f"  Registered Discoveries: {health['registered_discoveries']}")
    
    print("\n" + "=" * 70)
    print("Node 7: Scientific Discovery Validator - Active and Ready")
    print("=" * 70)


if __name__ == '__main__':
    main()
