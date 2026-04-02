"""
Node 4: Quantum Result Archive Layer

Replaces the NFT/blockchain layer with a scientific research archival system.
Provides cryptographic verification and provenance tracking for quantum experiments.

This module provides:
- Quantum result registry with cryptographic hashes
- Experiment provenance tracking
- Research data archival integration
- Reproducibility verification
"""

import hashlib
import itertools
import time
from copy import deepcopy
from typing import Dict, Any, List, Optional
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


class _MockArchiveStorage:
    """Mock storage for quantum experiment results (replaces IPFS)."""
    
    def __init__(self, storage_path: str = "archive"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._cache: Dict[str, Dict] = {}
    
    def upload_result(self, payload: Dict[str, Any]) -> str:
        """Upload result and return archive CID."""
        content = json.dumps(payload, sort_keys=True)
        digest = hashlib.sha3_256(content.encode("utf-8")).hexdigest()
        cid = f"QRA-{digest[:40]}"
        self._cache[cid] = payload
        
        # Save to disk
        file_path = self.storage_path / f"{cid}.json"
        try:
            with open(file_path, 'w') as f:
                json.dump(payload, f, indent=2)
        except Exception as e:
            logger.warning(f"Failed to save archive file: {e}")
        
        return cid
    
    def retrieve_result(self, cid: str) -> Optional[Dict[str, Any]]:
        """Retrieve result by CID."""
        if cid in self._cache:
            return self._cache[cid]
        
        file_path = self.storage_path / f"{cid}.json"
        if file_path.exists():
            try:
                with open(file_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load archive file: {e}")
        
        return None


class _MockProvenanceChain:
    """
    Mock provenance chain for experiment verification (replaces blockchain).
    
    Provides cryptographic verification and lineage tracking without
    the overhead and complexity of blockchain.
    """
    
    def __init__(self):
        self.ledger: Dict[str, Dict] = {}
        self.listeners: List = []
    
    def add_listener(self, listener):
        """Add a listener for archive events."""
        self.listeners.append(listener)

    @staticmethod
    def _compat_mint_event(event: Dict[str, Any]) -> Dict[str, Any]:
        """Build a legacy mint event payload from an archive event."""
        archive_id = event.get("archive_id")
        token_id = None
        if isinstance(archive_id, int):
            token_id = archive_id
        elif isinstance(archive_id, str):
            parts = archive_id.rsplit("-", 1)
            if len(parts) == 2 and parts[1].isdigit():
                token_id = int(parts[1])
            elif archive_id.isdigit():
                token_id = int(archive_id)
        compat_event = deepcopy(event)
        compat_event["token_id"] = token_id
        return compat_event
    
    def archive_result(
        self,
        archive_id: str,
        owner: str,
        metadata_cid: str,
        experiment_type: str = "quantum_experiment"
    ) -> str:
        """
        Archive a quantum experiment result.
        
        Args:
            archive_id: Unique identifier for the result
            owner: Owner/creator of the result
            metadata_cid: Content ID of the metadata
            experiment_type: Type of quantum experiment
            
        Returns:
            Transaction hash (verification hash)
        """
        # Create verification hash
        tx_seed = f"{archive_id}:{owner}:{metadata_cid}:{experiment_type}".encode("utf-8")
        tx_hash = "0x" + hashlib.sha3_256(tx_seed).hexdigest()
        
        event = {
            "archive_id": archive_id,
            "owner": owner,
            "metadata_cid": metadata_cid,
            "experiment_type": experiment_type,
            "tx_hash": tx_hash,
            "timestamp": time.time(),
            "verification_count": 0
        }
        
        self.ledger[archive_id] = event
        
        # Notify listeners
        for listener in list(self.listeners):
            cb = getattr(listener, "on_archive_event", None)
            if callable(cb):
                cb(event)
            else:
                legacy_cb = getattr(listener, "on_mint_event", None)
                if callable(legacy_cb):
                    legacy_cb(self._compat_mint_event(event))
        
        return tx_hash
    
    def verify_result(self, archive_id: str) -> bool:
        """Verify an archived result exists and is valid."""
        if archive_id not in self.ledger:
            return False
        
        self.ledger[archive_id]["verification_count"] += 1
        return True


class Node4QuantumArchive:
    """
    Node 4: Quantum Result Archive Layer
    
    Replaces the NFT Layer with a scientific research archival system.
    Provides cryptographic verification and provenance tracking for quantum experiments.
    
    Features:
    - Quantum result registry with SHA3-256 hashes
    - Experiment provenance tracking
    - Research data archival integration
    - Reproducibility verification
    """
    
    NODE_ID = 4
    NODE_NAME = "Quantum Archive Layer"
    PLATONIC_SOLID = "Dodecahedron"
    GEOMETRY = {
        "faces": 12,
        "vertices": 20,
        "edges": 30,
    }
    
    # Map old NFT names to new archive names for backward compatibility
    _COMPAT_NAMES = {
        "NFT Layer": "Quantum Archive Layer",
        "token_id": "archive_id",
        "NFTMetadata": "QuantumResultMetadata"
    }

    def __init__(self, storage_path: str = "archive"):
        self.status = "active"
        self.initialized_at = time.time()
        self.archive_storage = _MockArchiveStorage(storage_path)
        self.provenance_chain = _MockProvenanceChain()
        self.asset_registry: Dict[str, Dict] = {}
        self._archive_counter = itertools.count(0)
    
    def standardize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standardize metadata format for archival.
        
        Args:
            metadata: Raw metadata dictionary
            
        Returns:
            Standardized metadata with required fields
        """
        out = deepcopy(metadata) if metadata else {}
        
        # Ensure attributes are in correct format
        attrs = out.get("attributes", [])
        if isinstance(attrs, dict):
            out["attributes"] = [{"trait_type": k, "value": v} for k, v in attrs.items()]
        elif not isinstance(attrs, list):
            out["attributes"] = []
        
        # Add quantum-specific fields
        if "experiment_type" not in out:
            out["experiment_type"] = "quantum_vae"
        if "fingerprint" not in out:
            out["fingerprint"] = {
                "sha3_256": hashlib.sha3_256(str(out).encode()).hexdigest(),
                "timestamp": time.time()
            }
        
        return out
    
    def create_asset(
        self,
        owner: str,
        raw_metadata: Dict[str, Any],
        experiment_type: str = "quantum_experiment"
    ) -> Dict[str, Any]:
        """
        Create and archive a quantum experiment result.
        
        Args:
            owner: Owner/creator of the result
            raw_metadata: Metadata describing the experiment
            experiment_type: Type of quantum experiment
            
        Returns:
            Archived asset with verification hash
        """
        archive_id = f"QRA-{next(self._archive_counter):06d}"
        
        # Standardize metadata
        metadata = self.standardize_metadata(raw_metadata)
        metadata["experiment_type"] = experiment_type
        
        # Upload to archive storage
        metadata_cid = self.archive_storage.upload_result(metadata)
        metadata["archive_cid"] = f"archive://{metadata_cid}"
        
        # Archive in provenance chain
        tx_hash = self.provenance_chain.archive_result(
            archive_id=archive_id,
            owner=owner,
            metadata_cid=metadata_cid,
            experiment_type=experiment_type
        )
        
        # Create asset record
        asset = {
            "archive_id": archive_id,
            "owner": owner,
            "metadata_cid": metadata_cid,
            "tx_hash": tx_hash,
            "metadata": metadata,
            "experiment_type": experiment_type,
            "created_at": time.time()
        }
        
        self.asset_registry[archive_id] = asset
        
        logger.info(f"Archived quantum result {archive_id} with hash {tx_hash[:16]}...")
        return asset
    
    def get_asset(self, archive_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve an archived quantum result.
        
        Args:
            archive_id: ID of the archived result
            
        Returns:
            Asset dictionary or None if not found
        """
        return self.asset_registry.get(archive_id)
    
    def verify_asset(self, archive_id: str) -> bool:
        """
        Verify the integrity of an archived result.
        
        Args:
            archive_id: ID of the archived result
            
        Returns:
            True if verification succeeds
        """
        if archive_id not in self.asset_registry:
            return False
        
        # Verify in provenance chain
        is_valid = self.provenance_chain.verify_result(archive_id)
        
        if is_valid:
            # Retrieve and verify metadata
            asset = self.asset_registry[archive_id]
            stored_metadata = self.archive_storage.retrieve_result(asset["metadata_cid"])
            
            if stored_metadata:
                # Verify fingerprint
                expected_hash = asset["metadata"].get("fingerprint", {}).get("sha3_256", "")
                actual_hash = hashlib.sha3_256(str(stored_metadata).encode()).hexdigest()
                
                if expected_hash and expected_hash != actual_hash:
                    logger.warning(f"Hash mismatch for {archive_id}")
                    return False
        
        return is_valid
    
    def get_lineage(self, archive_id: str) -> Dict[str, Any]:
        """
        Get the lineage/ancestry of an archived result.
        
        Args:
            archive_id: ID of the archived result
            
        Returns:
            Dictionary with lineage information
        """
        if archive_id not in self.asset_registry:
            return {"error": f"Archive ID {archive_id} not found"}
        
        asset = self.asset_registry[archive_id]
        
        return {
            "archive_id": archive_id,
            "experiment_type": asset.get("experiment_type"),
            "owner": asset.get("owner"),
            "created_at": asset.get("created_at"),
            "verification_count": self.provenance_chain.ledger.get(archive_id, {}).get("verification_count", 0)
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get health status of the archive layer.
        
        Returns:
            Health status dictionary
        """
        return {
            "node_id": self.NODE_ID,
            "node_name": self.NODE_NAME,
            "status": self.status,
            "platonic_solid": self.PLATONIC_SOLID,
            "assets_archived": len(self.asset_registry),
            "uptime_seconds": max(0.0, time.time() - self.initialized_at),
            "storage_type": "quantum_archive",
            "verification_enabled": True
        }
    
    # Backward compatibility aliases
    def mint(self, owner: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Alias for create_asset (backward compatibility)."""
        return self.create_asset(owner, metadata)
    
    @property
    def blockchain(self):
        """Alias for provenance_chain (backward compatibility)."""
        return self.provenance_chain


# Backward compatibility alias
Node4NFTLayer = Node4QuantumArchive


if __name__ == "__main__":
    # Example usage
    archive = Node4QuantumArchive()
    
    # Create a quantum experiment result
    result = archive.create_asset(
        owner="researcher@example.com",
        raw_metadata={
            "experiment_type": "vae_training",
            "fidelity": 0.9876,
            "coherence": 0.9543,
            "kl_divergence": 0.0234,
            "attributes": {
                "model": "QuantumVAE",
                "latent_dim": 32
            }
        }
    )
    
    print(f"Archived: {result['archive_id']}")
    print(f"Verification hash: {result['tx_hash']}")
    
    # Verify the result
    is_valid = archive.verify_asset(result["archive_id"])
    print(f"Verification: {'PASSED' if is_valid else 'FAILED'}")
    
    # Get health status
    health = archive.get_health_status()
    print(f"Archive status: {health}")
