"""tools/vault_ledger.py

Local Vault Ledger for provenance (local-only, no network).
Records SHA-256 file hashes with timestamps and optional signatures.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
    from cryptography.hazmat.primitives import serialization
    HAS_CRYPTO = True
except Exception:
    HAS_CRYPTO = False


@dataclass
class LedgerEntry:
    timestamp: float
    operation: str
    file_path: str
    file_hash: str
    metadata: dict
    prev_hash: Optional[str] = None
    signature: Optional[str] = None


def vault_root() -> Path:
    return Path(os.environ.get("AGI_VAULT_DIR", "vault"))


def vault_path(*parts: str) -> Path:
    return vault_root().joinpath(*parts)


class VaultLedger:
    def __init__(
        self,
        ledger_path: str | Path | None = None,
        key_dir: str | Path | None = None,
    ):
        self.ledger_path = Path(ledger_path) if ledger_path is not None else vault_path("ledger.json")
        self.key_dir = Path(key_dir) if key_dir is not None else vault_path("keys")
        self.history: list[LedgerEntry] = []
        self._load()

    def _load(self):
        if self.ledger_path.exists():
            try:
                data = json.loads(self.ledger_path.read_text())
                for d in data:
                    self.history.append(LedgerEntry(**d))
            except Exception:
                # Corrupt ledger - start fresh in memory
                self.history = []

    def save_ledger(self):
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        with self.ledger_path.open("w", encoding="utf-8") as f:
            json.dump([asdict(e) for e in self.history], f, indent=2, sort_keys=True)

    def generate_hash(self, file_path: str) -> str:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def _sign(self, message: bytes) -> Optional[str]:
        if not HAS_CRYPTO:
            return None
        priv = self._load_private_key()
        if priv is None:
            return None
        sig = priv.sign(message)
        return sig.hex()

    def _load_private_key(self) -> Optional[Ed25519PrivateKey]:
        if not HAS_CRYPTO:
            return None
        key_file = self.key_dir / "private.key"
        if not key_file.exists():
            return None
        data = key_file.read_bytes()
        try:
            return Ed25519PrivateKey.from_private_bytes(data)
        except Exception:
            # try PEM
            try:
                priv = serialization.load_pem_private_key(data, password=None)
                return priv
            except Exception:
                return None

    def _load_public_key(self) -> Optional[Ed25519PublicKey]:
        if not HAS_CRYPTO:
            return None
        key_file = self.key_dir / "public.key"
        if not key_file.exists():
            return None
        data = key_file.read_bytes()
        try:
            return Ed25519PublicKey.from_public_bytes(data)
        except Exception:
            try:
                pub = serialization.load_pem_public_key(data)
                return pub
            except Exception:
                return None

    def generate_or_get_keys(self):
        if not HAS_CRYPTO:
            raise RuntimeError("cryptography library not found; cannot create keys")
        self.key_dir.mkdir(parents=True, exist_ok=True)
        priv_file = self.key_dir / "private.key"
        pub_file = self.key_dir / "public.key"
        if priv_file.exists() and pub_file.exists():
            return
        priv = Ed25519PrivateKey.generate()
        raw_priv = priv.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption(),
        )
        raw_pub = priv.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
        priv_file.write_bytes(raw_priv)
        pub_file.write_bytes(raw_pub)

    def record_operation(self, op_name: str, file_path: str, metadata: Optional[dict] = None):
        metadata = metadata or {}
        file_hash = self.generate_hash(file_path)
        prev_hash = self.history[-1].file_hash if self.history else None
        entry = LedgerEntry(timestamp=time.time(), operation=op_name, file_path=str(file_path), file_hash=file_hash, metadata=metadata, prev_hash=prev_hash)
        # sign entry body for provenance
        body = json.dumps({"operation": entry.operation, "file_hash": entry.file_hash, "timestamp": entry.timestamp}, sort_keys=True).encode("utf-8")
        try:
            entry.signature = self._sign(body)
        except Exception:
            entry.signature = None
        self.history.append(entry)
        self.save_ledger()
        print(f"🔒 Recorded {op_name}: {file_path} -> {file_hash}")
        return entry

    def verify_entry(self, entry: LedgerEntry) -> bool:
        # verify hash matches file
        current_hash = self.generate_hash(entry.file_path)
        if current_hash != entry.file_hash:
            return False
        # optionally verify signature
        if entry.signature and HAS_CRYPTO:
            pub = self._load_public_key()
            if pub is None:
                return False
            body = json.dumps({"operation": entry.operation, "file_hash": entry.file_hash, "timestamp": entry.timestamp}, sort_keys=True).encode("utf-8")
            try:
                pub.verify(bytes.fromhex(entry.signature), body)
            except Exception:
                return False
        return True


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--init-keys", action="store_true", help="Generate ed25519 keypair for signing ledger entries (requires cryptography)")
    p.add_argument("--ledger", default=str(vault_path("ledger.json")))
    args = p.parse_args()
    ledger = VaultLedger(ledger_path=args.ledger)
    if args.init_keys:
        if not HAS_CRYPTO:
            print("cryptography not available; install it to use key generation")
        else:
            ledger.generate_or_get_keys()
            print("Generated local keypair in vault/keys/")
    else:
        print(f"Ledger path: {ledger.ledger_path}")
        print(f"Entries: {len(ledger.history)}")
