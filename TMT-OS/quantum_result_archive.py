"""
Quantum Result Archive System

Replaces NFT/blockchain functionality with a scientific research archival system.
Provides cryptographic verification and provenance tracking for quantum experiments.

Features:
- Quantum result registry with cryptographic hashes
- Experiment provenance tracking
- Research data archival integration
- Reproducibility verification
"""

import hashlib
import json
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ArchiveStatus(Enum):
    """Status of archived quantum results."""
    PENDING = "pending"
    VERIFIED = "verified"
    PUBLISHED = "published"
    RETRACTED = "retracted"


@dataclass
class QuantumFingerprint:
    """Cryptographic fingerprint of a quantum experiment result."""
    experiment_id: str
    timestamp: str
    sha3_256: str
    blake2b: str
    experiment_type: str
    parameters_hash: str
    results_hash: str
    
    def to_dict(self) -> Dict[str, str]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'QuantumFingerprint':
        return cls(**data)


@dataclass
class ExperimentProvenance:
    """Provenance tracking for quantum experiments."""
    experiment_id: str
    parent_ids: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    modified_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    authors: List[str] = field(default_factory=list)
    institution: str = ""
    project: str = "TMT-OS Quantum Consciousness"
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExperimentProvenance':
        return cls(**data)


@dataclass
class ArchivedResult:
    """Archived quantum experiment result with full metadata."""
    archive_id: str
    fingerprint: QuantumFingerprint
    provenance: ExperimentProvenance
    status: ArchiveStatus
    metadata: Dict[str, Any]
    result_data: Dict[str, Any]
    verification_count: int = 0
    last_verified: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'archive_id': self.archive_id,
            'fingerprint': self.fingerprint.to_dict(),
            'provenance': self.provenance.to_dict(),
            'status': self.status.value,
            'metadata': self.metadata,
            'result_data': self.result_data,
            'verification_count': self.verification_count,
            'last_verified': self.last_verified
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ArchivedResult':
        return cls(
            archive_id=data['archive_id'],
            fingerprint=QuantumFingerprint.from_dict(data['fingerprint']),
            provenance=ExperimentProvenance.from_dict(data['provenance']),
            status=ArchiveStatus(data['status']),
            metadata=data['metadata'],
            result_data=data['result_data'],
            verification_count=data.get('verification_count', 0),
            last_verified=data.get('last_verified')
        )


class QuantumResultArchive:
    """
    Archive system for quantum experiment results.
    
    Replaces the NFT/blockchain system with a scientific research archival approach
    that provides:
    - Cryptographic verification via SHA3-256 and BLAKE2b hashes
    - Provenance tracking for reproducibility
    - Integration with scientific repositories (Zenodo, Figshare)
    - Local and cloud storage options
    """
    
    def __init__(self, storage_path: str = "archive"):
        """
        Initialize the quantum result archive.
        
        Args:
            storage_path: Path to store archived results
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._archive_registry: Dict[str, ArchivedResult] = {}
        self._load_registry()
    
    def _load_registry(self) -> None:
        """Load the archive registry from disk."""
        registry_path = self.storage_path / "registry.json"
        if registry_path.exists():
            try:
                with open(registry_path, 'r') as f:
                    data = json.load(f)
                    self._archive_registry = {
                        k: ArchivedResult.from_dict(v) for k, v in data.items()
                    }
                logger.info(f"Loaded {len(self._archive_registry)} archived results")
            except Exception as e:
                logger.warning(f"Failed to load registry: {e}")
                self._archive_registry = {}
    
    def _save_registry(self) -> None:
        """Save the archive registry to disk."""
        registry_path = self.storage_path / "registry.json"
        try:
            with open(registry_path, 'w') as f:
                json.dump(
                    {k: v.to_dict() for k, v in self._archive_registry.items()},
                    f,
                    indent=2
                )
        except Exception as e:
            logger.error(f"Failed to save registry: {e}")
    
    def _compute_hash(self, data: Union[str, bytes, Dict]) -> str:
        """Compute SHA3-256 hash of data."""
        if isinstance(data, dict):
            data = json.dumps(data, sort_keys=True)
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.sha3_256(data).hexdigest()
    
    def _compute_blake2b(self, data: Union[str, bytes, Dict]) -> str:
        """Compute BLAKE2b hash of data."""
        if isinstance(data, dict):
            data = json.dumps(data, sort_keys=True)
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.blake2b(data, digest_size=32).hexdigest()
    
    def generate_archive_id(self, experiment_type: str) -> str:
        """Generate a unique archive ID."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        random_suffix = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
        return f"QRA-{experiment_type[:3].upper()}-{timestamp}-{random_suffix}"
    
    def archive_result(
        self,
        experiment_type: str,
        result_data: Dict[str, Any],
        parameters: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        parent_ids: Optional[List[str]] = None,
        authors: Optional[List[str]] = None,
        tags: Optional[List[str]] = None
    ) -> ArchivedResult:
        """
        Archive a quantum experiment result.
        
        Args:
            experiment_type: Type of quantum experiment (e.g., 'vae_training', 'quantum_teleportation')
            result_data: The experimental results to archive
            parameters: Parameters used in the experiment
            metadata: Additional metadata
            parent_ids: IDs of parent experiments (for lineage tracking)
            authors: List of authors/contributors
            tags: Tags for categorization
            
        Returns:
            ArchivedResult with cryptographic fingerprint
        """
        # Generate archive ID
        archive_id = self.generate_archive_id(experiment_type)
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Compute cryptographic hashes
        result_hash = self._compute_hash(result_data)
        params_hash = self._compute_hash(parameters)
        combined_hash = self._compute_hash({
            'result': result_data,
            'parameters': parameters,
            'timestamp': timestamp
        })
        
        # Create fingerprint
        fingerprint = QuantumFingerprint(
            experiment_id=archive_id,
            timestamp=timestamp,
            sha3_256=combined_hash,
            blake2b=self._compute_blake2b(combined_hash),
            experiment_type=experiment_type,
            parameters_hash=params_hash,
            results_hash=result_hash
        )
        
        # Create provenance
        provenance = ExperimentProvenance(
            experiment_id=archive_id,
            parent_ids=parent_ids or [],
            authors=authors or [],
            tags=tags or [experiment_type]
        )
        
        # Create archived result
        archived = ArchivedResult(
            archive_id=archive_id,
            fingerprint=fingerprint,
            provenance=provenance,
            status=ArchiveStatus.PENDING,
            metadata=metadata or {},
            result_data=result_data
        )
        
        # Save to registry
        self._archive_registry[archive_id] = archived
        self._save_registry()
        
        # Save individual result file
        self._save_result_file(archived)
        
        logger.info(f"Archived result {archive_id} with fingerprint {fingerprint.sha3_256[:16]}...")
        return archived
    
    def _save_result_file(self, archived: ArchivedResult) -> None:
        """Save individual result file to disk."""
        result_path = self.storage_path / f"{archived.archive_id}.json"
        try:
            with open(result_path, 'w') as f:
                json.dump(archived.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save result file: {e}")
    
    def verify_result(self, archive_id: str) -> bool:
        """
        Verify the integrity of an archived result.
        
        Args:
            archive_id: ID of the archived result
            
        Returns:
            True if verification succeeds, False otherwise
        """
        if archive_id not in self._archive_registry:
            logger.warning(f"Archive ID {archive_id} not found")
            return False
        
        archived = self._archive_registry[archive_id]
        
        # Recompute hashes
        result_hash = self._compute_hash(archived.result_data)
        params_hash = self._compute_hash(archived.metadata.get('parameters', {}))
        
        # Verify hashes match
        if result_hash != archived.fingerprint.results_hash:
            logger.error(f"Result hash mismatch for {archive_id}")
            return False
        
        if params_hash != archived.fingerprint.parameters_hash:
            logger.error(f"Parameters hash mismatch for {archive_id}")
            return False
        
        # Update verification count
        archived.verification_count += 1
        archived.last_verified = datetime.now(timezone.utc).isoformat()
        archived.status = ArchiveStatus.VERIFIED
        self._save_registry()
        
        logger.info(f"Verified {archive_id} (count: {archived.verification_count})")
        return True
    
    def get_result(self, archive_id: str) -> Optional[ArchivedResult]:
        """Retrieve an archived result by ID."""
        return self._archive_registry.get(archive_id)
    
    def search_by_type(self, experiment_type: str) -> List[ArchivedResult]:
        """Search archived results by experiment type."""
        return [
            r for r in self._archive_registry.values()
            if r.fingerprint.experiment_type == experiment_type
        ]
    
    def search_by_tag(self, tag: str) -> List[ArchivedResult]:
        """Search archived results by tag."""
        return [
            r for r in self._archive_registry.values()
            if tag in r.provenance.tags
        ]
    
    def get_lineage(self, archive_id: str) -> Dict[str, Any]:
        """
        Get the lineage/ancestry of an archived result.
        
        Args:
            archive_id: ID of the archived result
            
        Returns:
            Dictionary with lineage information
        """
        if archive_id not in self._archive_registry:
            return {'error': f'Archive ID {archive_id} not found'}
        
        lineage = {
            'archive_id': archive_id,
            'parents': [],
            'children': [],
            'depth': 0
        }
        
        # Get parents
        archived = self._archive_registry[archive_id]
        for parent_id in archived.provenance.parent_ids:
            if parent_id in self._archive_registry:
                lineage['parents'].append({
                    'id': parent_id,
                    'type': self._archive_registry[parent_id].fingerprint.experiment_type
                })
        
        # Get children
        for aid, result in self._archive_registry.items():
            if archive_id in result.provenance.parent_ids:
                lineage['children'].append({
                    'id': aid,
                    'type': result.fingerprint.experiment_type
                })
        
        return lineage
    
    def export_for_repository(
        self,
        archive_id: str,
        format: str = 'zenodo'
    ) -> Dict[str, Any]:
        """
        Export archived result for submission to a scientific repository.
        
        Args:
            archive_id: ID of the archived result
            format: Repository format ('zenodo', 'figshare', 'generic')
            
        Returns:
            Formatted metadata for repository submission
        """
        if archive_id not in self._archive_registry:
            return {'error': f'Archive ID {archive_id} not found'}
        
        archived = self._archive_registry[archive_id]
        
        if format == 'zenodo':
            return {
                'title': f"Quantum Experiment: {archived.fingerprint.experiment_type}",
                'description': f"Archived quantum experiment result from TMT-OS Quantum Consciousness system.",
                'creators': [{'name': author} for author in archived.provenance.authors],
                'keywords': archived.provenance.tags + ['quantum', 'consciousness', 'tmt-os'],
                'related_identifiers': [
                    {
                        'identifier': f"sha3-256:{archived.fingerprint.sha3_256}",
                        'relation': 'isIdenticalTo'
                    }
                ],
                'upload_type': 'dataset',
                'license': 'mit',
                'metadata': {
                    'experiment_type': archived.fingerprint.experiment_type,
                    'timestamp': archived.fingerprint.timestamp,
                    'verification_count': archived.verification_count
                }
            }
        elif format == 'figshare':
            return {
                'title': f"Quantum Experiment: {archived.fingerprint.experiment_type}",
                'description': f"Archived quantum experiment result from TMT-OS Quantum Consciousness system.",
                'authors': archived.provenance.authors,
                'tags': archived.provenance.tags + ['quantum', 'consciousness', 'tmt-os'],
                'categories': [100],  # Science category
                'license': 8,  # MIT license
                'fingerprint': archived.fingerprint.to_dict()
            }
        else:
            return {
                'archive_id': archive_id,
                'fingerprint': archived.fingerprint.to_dict(),
                'provenance': archived.provenance.to_dict(),
                'metadata': archived.metadata
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the archive."""
        if not self._archive_registry:
            return {
                'total_results': 0,
                'experiment_types': {},
                'verified_count': 0,
                'total_verifications': 0
            }
        
        experiment_types = {}
        verified_count = 0
        total_verifications = 0
        
        for result in self._archive_registry.values():
            exp_type = result.fingerprint.experiment_type
            experiment_types[exp_type] = experiment_types.get(exp_type, 0) + 1
            if result.status == ArchiveStatus.VERIFIED:
                verified_count += 1
            total_verifications += result.verification_count
        
        return {
            'total_results': len(self._archive_registry),
            'experiment_types': experiment_types,
            'verified_count': verified_count,
            'total_verifications': total_verifications
        }


# Convenience function for backward compatibility
def create_quantum_archive(storage_path: str = "archive") -> QuantumResultArchive:
    """Create a quantum result archive instance."""
    return QuantumResultArchive(storage_path)


# Example usage
if __name__ == "__main__":
    # Create archive
    archive = QuantumResultArchive("quantum_archive")
    
    # Archive a quantum experiment result
    result = archive.archive_result(
        experiment_type="vae_training",
        result_data={
            "fidelity": 0.9876,
            "coherence": 0.9543,
            "kl_divergence": 0.0234,
            "latent_dim": 32
        },
        parameters={
            "epochs": 200,
            "batch_size": 64,
            "learning_rate": 0.001
        },
        metadata={
            "model_version": "v2.1",
            "dataset": "sacred_geometry"
        },
        authors=["TMT-OS System"],
        tags=["vae", "quantum", "consciousness"]
    )
    
    print(f"Archived: {result.archive_id}")
    print(f"Fingerprint: {result.fingerprint.sha3_256[:32]}...")
    
    # Verify the result
    is_valid = archive.verify_result(result.archive_id)
    print(f"Verification: {'PASSED' if is_valid else 'FAILED'}")
    
    # Get statistics
    stats = archive.get_statistics()
    print(f"Archive statistics: {stats}")