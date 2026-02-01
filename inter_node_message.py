"""Inter-node message format and helpers for TMT-OS Multi-Agent Nodes.

Provides a portable, versioned message dataclass and utilities to:
- serialize/deserialize messages
- attach HMAC-SHA256 signatures
- encode/decode numpy arrays as base64 (optionally compressed)
- apply Phi-based scaling (Phi-Quantization decompression/compression)

This format is intended for passing latent / resonance data from a
smaller node (e.g. 3.8B Wing Node) to a larger node (e.g. 70B Core Node).

Usage example:
    msg = create_message('wing-phi', 'node-w', 'node-core', phase='COGNITION',
                         phi_resonance=1.618, payload=latent_array, payload_type='ndarray',
                         quantized=True, key=b'secret')
    raw = serialize_message(msg)
    msg2 = deserialize_message(raw)
    valid = verify_message_signature(msg2, b'secret')
"""
from __future__ import annotations

import json
import base64
import zlib
import hmac
import hashlib
import time
import uuid
from dataclasses import dataclass, asdict
from io import BytesIO
from typing import Any, Dict, Optional, Tuple

import numpy as np

# Golden ratio constant used for Phi-Quantization operations
PHI = 1.618033988749895


@dataclass
class InterNodeMessage:
    version: str
    msg_id: str
    timestamp: float
    source: str
    target: str
    phase: str
    phi_resonance: float
    payload_type: str  # 'ndarray' | 'json' | 'bytes'
    payload_b64: str
    metadata: Dict[str, Any]
    signature: Optional[str] = None


def _ndarray_to_b64(arr: np.ndarray, compress: bool = True) -> str:
    buf = BytesIO()
    # Use numpy's binary format for exact reconstruction
    np.save(buf, arr, allow_pickle=False)
    raw = buf.getvalue()
    if compress:
        raw = zlib.compress(raw)
    return base64.b64encode(raw).decode('ascii')


def _b64_to_ndarray(b64: str, compressed: bool = True) -> np.ndarray:
    raw = base64.b64decode(b64.encode('ascii'))
    if compressed:
        raw = zlib.decompress(raw)
    buf = BytesIO(raw)
    buf.seek(0)
    return np.load(buf)


def _json_to_b64(obj: Any, compress: bool = True) -> str:
    raw = json.dumps(obj, separators=(',', ':'), sort_keys=True).encode('utf-8')
    if compress:
        raw = zlib.compress(raw)
    return base64.b64encode(raw).decode('ascii')


def _b64_to_json(b64: str, compressed: bool = True) -> Any:
    raw = base64.b64decode(b64.encode('ascii'))
    if compressed:
        raw = zlib.decompress(raw)
    return json.loads(raw.decode('utf-8'))


def phi_decompress_array(arr: np.ndarray, phi: float = PHI) -> np.ndarray:
    """Apply Phi-scaling to expand quantized array into decompressed values.

    This is intentionally a simple multiplicative transform: arr * phi
    (user can replace with more complex decompression mapping).
    """
    return arr.astype(float) * float(phi)


def phi_compress_array(arr: np.ndarray, phi: float = PHI) -> np.ndarray:
    """Apply inverse transform to produce quantized representation.
    """
    return (arr.astype(float) / float(phi)).astype(arr.dtype)


def sign_message(message_dict: Dict[str, Any], key: bytes) -> str:
    """Compute HMAC-SHA256 signature over canonical JSON representation."""
    canon = json.dumps(message_dict, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
    mac = hmac.new(key, canon.encode('utf-8'), hashlib.sha256).hexdigest()
    return mac


def verify_message_signature(msg: InterNodeMessage, key: bytes) -> bool:
    sig = msg.signature
    if not sig:
        return False
    # Recompute signature over message without signature field
    d = asdict(msg).copy()
    d['signature'] = None
    recomputed = sign_message(d, key)
    return hmac.compare_digest(recomputed, sig)


def create_message(
    msg_type: str,
    source: str,
    target: str,
    phase: str,
    phi_resonance: float,
    payload: Any,
    payload_type: str = 'ndarray',
    quantized: bool = False,
    compress: bool = True,
    metadata: Optional[Dict[str, Any]] = None,
    key: Optional[bytes] = None,
) -> InterNodeMessage:
    """Build and optionally sign an InterNodeMessage.

    - If `quantized` and `payload_type=='ndarray'`, apply `phi_compress_array` before encoding.
    - `key` if provided will produce an HMAC signature.
    """
    metadata = metadata or {}
    msg_id = str(uuid.uuid4())
    ts = time.time()

    if payload_type == 'ndarray':
        arr = np.asarray(payload)
        if quantized:
            arr = phi_compress_array(arr)
        payload_b64 = _ndarray_to_b64(arr, compress=compress)
    elif payload_type == 'json':
        payload_b64 = _json_to_b64(payload, compress=compress)
    elif payload_type == 'bytes':
        raw = bytes(payload)
        if compress:
            raw = zlib.compress(raw)
        payload_b64 = base64.b64encode(raw).decode('ascii')
    else:
        raise ValueError('Unsupported payload_type')

    msg = InterNodeMessage(
        version='1.0',
        msg_id=msg_id,
        timestamp=ts,
        source=source,
        target=target,
        phase=phase,
        phi_resonance=float(phi_resonance),
        payload_type=payload_type,
        payload_b64=payload_b64,
        metadata=metadata,
        signature=None,
    )

    if key is not None:
        d = asdict(msg).copy()
        d['signature'] = None
        sig = sign_message(d, key)
        msg.signature = sig

    return msg


def serialize_message(msg: InterNodeMessage) -> str:
    """Serialize message to JSON string for network transport."""
    return json.dumps(asdict(msg), sort_keys=False, separators=(',', ':'), ensure_ascii=False)


def deserialize_message(raw: str) -> InterNodeMessage:
    d = json.loads(raw)
    return InterNodeMessage(**d)


def extract_payload(msg: InterNodeMessage, compressed: bool = True) -> Any:
    """Decode payload according to `payload_type` and return original object.
    If payload was quantized, the caller should run `phi_decompress_array` on the ndarray.
    """
    if msg.payload_type == 'ndarray':
        return _b64_to_ndarray(msg.payload_b64, compressed=compressed)
    elif msg.payload_type == 'json':
        return _b64_to_json(msg.payload_b64, compressed=compressed)
    elif msg.payload_type == 'bytes':
        raw = base64.b64decode(msg.payload_b64.encode('ascii'))
        if compressed:
            raw = zlib.decompress(raw)
        return raw
    else:
        raise ValueError('Unsupported payload_type')


__all__ = [
    'InterNodeMessage',
    'create_message',
    'serialize_message',
    'deserialize_message',
    'sign_message',
    'verify_message_signature',
    'extract_payload',
    'phi_decompress_array',
    'phi_compress_array',
]
