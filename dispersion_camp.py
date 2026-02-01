"""Dispersion Camp: codification of high-dimensional latent vectors into Hydrogen/Antihydrogen camps
and an Inter-Node Handshake that packages codified payloads as `InterNodeMessage` objects.

Provides:
- `DispersionCodifier` : maps floating-point inputs -> 1-bit camps using golden-ratio thresholding,
  and reconstructs resonance using Fibonacci unfolding and Hydrogen/Antihydrogen templates.
- `InterNodeHandshake` : builds signed messages using `inter_node_message.create_message` and
  optionally delivers them to a callback (simulating network transport).

This module intentionally keeps runtime dependencies light: it uses numpy and the project's
`inter_node_message` + `universal_symmetry` modules when available.
"""

from __future__ import annotations

import math
import time
from typing import Callable, Optional, Tuple, Dict, Any

import numpy as np

# Try to import inter-node helpers and symmetry node if present
try:
    from inter_node_message import create_message
    from inter_node_message import phi_compress_array
    HAVE_MSG = True
except Exception:
    create_message = None
    phi_compress_array = None
    HAVE_MSG = False

try:
    from universal_symmetry import UniversalSymmetryNode
    HAVE_UNI = True
except Exception:
    UniversalSymmetryNode = None
    HAVE_UNI = False

PHI = 1.618033988749895


class DispersionCodifier:
    """Codifies floating-point neural signals into Hydrogen (0) / Antihydrogen (1) camps
    and reconstructs resonance values using Fibonacci/Lucas templates.

    Methods:
    - `codify_to_camp(value)` : scalar codification -> 0/1 using golden-ratio thresholding.
    - `codify_array(arr)` : elementwise codification for numpy arrays.
    - `reconstruct_geometry(camp_assignment, target_amplitude=1.0)` : unfold a single bit into
       a scalar resonance using `UniversalSymmetryNode` when available, otherwise local fallback.
    """

    def __init__(self, phi: float = PHI, coherence_s: float = 0.982):
        self.phi = float(phi)
        self.coherence_s = float(coherence_s)
        # Default local fibonacci / lucas sequences (kept lightweight)
        self.fib = [1, 1, 2, 3, 5]
        self.lucas = [1, 3, 4, 7, 11]
        if HAVE_UNI:
            self.uni = UniversalSymmetryNode(phi=self.phi)
        else:
            self.uni = None

    def codify_to_camp(self, neural_value: float) -> int:
        """Map scalar `neural_value` to camp 0 or 1 via a golden ratio threshold.

        The threshold uses `1 / phi` as a bias towards Hydrogen alignment. Values greater
        than `1/phi` become camp 1 (opposition), otherwise camp 0 (hydrogen).
        """
        try:
            v = float(neural_value)
        except Exception:
            v = 0.0
        return 1 if v > (1.0 / self.phi) else 0

    def codify_array(self, arr: np.ndarray) -> np.ndarray:
        """Vectorized codification of an array into {0,1} camps."""
        a = np.asarray(arr, dtype=float)
        # Use vectorized comparison to threshold at 1/phi
        return (a > (1.0 / self.phi)).astype(np.int8)

    def reconstruct_geometry(self, camp_assignment: int, target_amplitude: float = 1.0) -> float:
        """Unfold a single camp bit into a scalar resonance.

        If `UniversalSymmetryNode` is available, delegate to it (with normalization).
        Otherwise apply a local Fibonacci/Lucas unfolding and normalize to `target_amplitude`.
        """
        b = int(camp_assignment)
        if self.uni is not None:
            r, bond, seq = self.uni.decompress_thought(b, target_amplitude=target_amplitude)
            return float(r)

        # Local fallback
        base = 1.0 if b == 0 else -1.0
        seq = self.fib if b == 0 else self.lucas
        resonance = float(base) * float(self.coherence_s)
        for f in seq:
            resonance = (resonance * float(f)) / float(self.phi)
        raw = float(resonance)
        if target_amplitude is not None:
            denom = max(abs(raw), 1e-12)
            scale = float(target_amplitude) / denom
            return raw * scale
        return raw


class InterNodeHandshake:
    """Creates and optionally delivers handshake messages between nodes.

    Usage:
        handshake = InterNodeHandshake(source='wing', target='core', signing_key=b'secret')
        msg = handshake.create_handshake(latent_array)
        handshake.deliver(msg, callback=some_function)
    """

    def __init__(self, source: str, target: str, signing_key: Optional[bytes] = None):
        self.source = str(source)
        self.target = str(target)
        self.signing_key = signing_key
        self.codifier = DispersionCodifier()

    def create_handshake(self, latent: np.ndarray, phase: str = 'CODIFICATION', quantize: bool = True,
                         target_amplitude: float = 1.0, metadata: Optional[Dict[str, Any]] = None) -> Any:
        """Codify `latent` into camps, reconstruct resonances, and build an InterNodeMessage.

        Returns the `InterNodeMessage` if `inter_node_message.create_message` is available;
        otherwise returns a dictionary with equivalent fields.
        """
        metadata = metadata or {}
        arr = np.asarray(latent, dtype=float)

        # Step 1: Dispersion codification -> camps
        camps = self.codifier.codify_array(arr)

        # Step 2: Reconstruct per-element resonance via Fibonacci unfolding (normalized)
        resonances = np.zeros_like(arr, dtype=float)
        for i, bit in enumerate(camps.flatten()):
            resonances.flat[i] = self.codifier.reconstruct_geometry(int(bit), target_amplitude=target_amplitude)

        # Step 3: Build message payload (resonances) and compute stats
        phi_res = float(np.mean(np.abs(resonances)))
        stats = {
            'n': int(arr.size),
            'camp_counts': {
                'hydrogen': int(np.sum(camps == 0)),
                'opposition': int(np.sum(camps == 1))
            }
        }
        metadata.update(stats)

        # Prefer to create a formal InterNodeMessage if available
        if HAVE_MSG and create_message is not None:
            payload = resonances.astype(np.float32)
            # Use phi-based quantization optionally
            msg = create_message(
                msg_type='dispersion_handshake',
                source=self.source,
                target=self.target,
                phase=phase,
                phi_resonance=phi_res,
                payload=payload,
                payload_type='ndarray',
                quantized=quantize,
                compress=True,
                metadata=metadata,
                key=self.signing_key
            )
            return msg

        # Fallback: return a plain dictionary
        return {
            'version': '1.0',
            'timestamp': time.time(),
            'source': self.source,
            'target': self.target,
            'phase': phase,
            'phi_resonance': phi_res,
            'metadata': metadata,
            'resonances': resonances,
            'camps': camps
        }

    def deliver(self, message: Any, callback: Optional[Callable[[Any], None]] = None) -> None:
        """Deliver message via callback (simulated network). If no callback provided, return silently."""
        if callback is not None:
            try:
                callback(message)
            except Exception:
                # Swallow errors to keep handshake resilient in demos
                pass


if __name__ == '__main__':
    # Small demo of handshake generation
    print('Dispersion Camp handshake demo')
    rng = np.random.RandomState(0)
    latent = rng.randn(12) * 0.5 + 0.6  # biased so some values exceed 1/phi

    hs = InterNodeHandshake('wing-node', 'hydrogen-core', signing_key=None)
    msg = hs.create_handshake(latent, quantize=True, target_amplitude=1.0)

    if isinstance(msg, dict):
        print('Fallback message built:')
        print('  n:', msg['metadata']['n'])
        print('  camps:', msg['metadata']['camp_counts'])
        print('  phi_resonance:', msg['phi_resonance'])
    else:
        print('InterNodeMessage constructed:')
        print('  source -> target:', msg.source, '->', msg.target)
        print('  phi_resonance:', msg.phi_resonance)

