import hashlib
import itertools
import time
from copy import deepcopy


class _MockIPFSNode:
    def upload_json(self, payload):
        digest = hashlib.sha1(repr(payload).encode("utf-8")).hexdigest()[:40]
        return f"Qm{digest}"


class _MockBlockchain:
    def __init__(self):
        self.ledger = {}
        self.listeners = []

    def add_listener(self, listener):
        self.listeners.append(listener)

    def mint(self, token_id, owner, metadata_cid):
        tx_seed = f"{token_id}:{owner}:{metadata_cid}".encode("utf-8")
        tx_hash = "0x" + hashlib.sha256(tx_seed).hexdigest()
        event = {
            "token_id": token_id,
            "owner": owner,
            "metadata_cid": metadata_cid,
            "tx_hash": tx_hash,
        }
        self.ledger[token_id] = event
        for listener in list(self.listeners):
            cb = getattr(listener, "on_mint_event", None)
            if callable(cb):
                cb(event)
        return tx_hash


class Node4NFTLayer:
    NODE_ID = 4
    NODE_NAME = "NFT Layer"
    PLATONIC_SOLID = "Dodecahedron"
    GEOMETRY = {
        "faces": 12,
        "vertices": 20,
        "edges": 30,
    }

    def __init__(self):
        self.status = "active"
        self.initialized_at = time.time()
        self.ipfs_node = _MockIPFSNode()
        self.blockchain = _MockBlockchain()
        self.asset_registry = {}
        self._token_counter = itertools.count(0)

    def standardize_metadata(self, metadata):
        out = deepcopy(metadata) if metadata else {}
        attrs = out.get("attributes", [])
        if isinstance(attrs, dict):
            out["attributes"] = [{"trait_type": k, "value": v} for k, v in attrs.items()]
        elif not isinstance(attrs, list):
            out["attributes"] = []
        return out

    def create_asset(self, owner, raw_metadata):
        token_id = next(self._token_counter)
        metadata = self.standardize_metadata(raw_metadata)
        metadata_cid = self.ipfs_node.upload_json(metadata)
        metadata["image"] = f"ipfs://{metadata_cid}"
        tx_hash = self.blockchain.mint(token_id, owner, metadata_cid)
        asset = {
            "token_id": token_id,
            "owner": owner,
            "metadata_cid": metadata_cid,
            "tx_hash": tx_hash,
            "metadata": metadata,
        }
        self.asset_registry[token_id] = asset
        return asset

    def get_asset(self, token_id):
        return self.asset_registry.get(token_id)

    def get_health_status(self):
        return {
            "node_id": self.NODE_ID,
            "node_name": self.NODE_NAME,
            "status": self.status,
            "platonic_solid": self.PLATONIC_SOLID,
            "assets_registered": len(self.asset_registry),
            "uptime_seconds": max(0.0, time.time() - self.initialized_at),
        }
