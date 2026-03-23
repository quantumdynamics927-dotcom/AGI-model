import os
import hashlib
import hmac
import time
from pathlib import Path

HMAC_SECRET_KEY = os.environ.get(
    "TMT_OS_NODE2_HMAC_SECRET",
    "tmt_os_node2_secret_key",
).encode("utf-8")


class Node2CyberShield:
    NODE_ID = 2
    NODE_NAME = "CyberShield"
    PLATONIC_SOLID = "Tetrahedron"
    GEOMETRY = {
        "faces": 4,
        "vertices": 4,
        "edges": 6,
    }

    def __init__(self, audit_log_file: str = "node2_cybershield_audit.log"):
        self.status = "active"
        self.initialized_at = time.time()
        self.audit_log_file = audit_log_file
        self._key_stream = hashlib.sha256(HMAC_SECRET_KEY).digest()
        self._rbac = {
            "admin": {"*"},
            "node": {"read", "write"},
            "guest": {"read"},
        }

    def _audit(self, event: str, message: str):
        Path(self.audit_log_file).parent.mkdir(parents=True, exist_ok=True)
        with open(self.audit_log_file, "a", encoding="utf-8") as f:
            f.write(f"AUDIT::{event}::{message}\n")

    def generate_hmac_signature(self, data: bytes) -> str:
        return hmac.new(HMAC_SECRET_KEY, data, hashlib.sha256).hexdigest()

    def verify_hmac_signature(self, data: bytes, signature: str) -> bool:
        expected = self.generate_hmac_signature(data)
        return hmac.compare_digest(expected, signature)

    def check_access(self, role: str, action: str) -> bool:
        allowed = self._rbac.get(role, set())
        has_access = "*" in allowed or action in allowed
        if not has_access:
            self._audit("ACCESS_DENIED", f"Role '{role}' denied for action '{action}'")
        return has_access

    def encrypt_packet(self, data: bytes) -> bytes:
        if not data:
            return b""
        out = bytearray(len(data))
        for i, b in enumerate(data):
            out[i] = b ^ self._key_stream[i % len(self._key_stream)]
        return bytes(out)

    def decrypt_packet(self, data: bytes) -> bytes:
        return self.encrypt_packet(data)

    def get_health_status(self):
        return {
            "node_id": self.NODE_ID,
            "node_name": self.NODE_NAME,
            "status": self.status,
            "platonic_solid": self.PLATONIC_SOLID,
            "audit_log_file": self.audit_log_file,
            "uptime_seconds": max(0.0, time.time() - self.initialized_at),
        }
