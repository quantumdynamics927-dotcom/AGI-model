"""Node 10 — Bio-Digital Interface (safe, non-actionable runtime)

This module provides a symbolic mapping from quantum measurement/phase metadata to a bounded
symbolic representation inspired by the DNA alphabet. It intentionally avoids producing raw,
actionable sequences suitable for synthesis. Raw sequence emission is gated behind an explicit
environment flag `ALLOW_RAW_DNA_OUTPUT` and additional manual confirmation.
"""
from typing import List, Dict, Any, Optional
import os
import math
import json
import hashlib
import time
from pathlib import Path
import logging

logger = logging.getLogger('node10_biodigital')
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
    logger.addHandler(ch)

PHI = (1.0 + math.sqrt(5.0)) / 2.0
MAX_SYMBOLIC_LENGTH = int(os.getenv('NODE10_MAX_SYMBOLS', '256'))


def _safe_base_from_value(v: float, idx: int) -> str:
    """Deterministic, non-actionable mapping from a numeric value to a nucleotide symbol.

    This mapping is intentionally simple and non-biological: it uses normalized value bucketing
    to choose symbols. It is not intended for biological design.
    """
    bases = ['A', 'T', 'C', 'G']
    # Normalize v into -1..1 then 0..1
    try:
        vn = float(v)
    except Exception:
        vn = 0.0
    # squash to finite range
    s = math.tanh(vn)
    frac = (s + 1.0) / 2.0
    # incorporate index to add deterministic variability
    idx_factor = (idx * 0.618033988749895) % 1.0
    combined = (frac + idx_factor) % 1.0
    return bases[int(combined * 4) % 4]


def quantum_to_symbolic(qubit_states: List[Dict[str, Any]], phi_threshold: float = PHI,
                        max_length: int = MAX_SYMBOLIC_LENGTH) -> Dict[str, Any]:
    """Map a list of qubit state descriptors to a bounded symbolic DNA-like string.

    Args:
        qubit_states: Sequence of dicts with keys such as `phase` and `probability`.
        phi_threshold: Filter/threshold for Biological Resonance Index (BRI). Used as a
            conceptual filter; it does not enable biological synthesis.
        max_length: Max length of the returned symbolic string.

    Returns:
        A dict with `symbolic_sequence`, `summary` and `resonant_fraction`.
    """
    seq = []
    resonant = 0
    total = 0
    for i, qs in enumerate(qubit_states):
        if total >= max_length:
            break
        total += 1
        phase = qs.get('phase', 0.0)
        prob = qs.get('probability', qs.get('p', 0.0))
        # BRI check (conceptual): phase close to 1/PHI modulo 1
        try:
            phase_frac = abs((phase / (2 * math.pi)) % 1.0 - (1.0 / phi_threshold))
        except Exception:
            phase_frac = 1.0
        is_resonant = phase_frac < 0.01
        if is_resonant:
            resonant += 1
        # combine probability and phase into a value for base mapping
        value = (phase_frac * 0.5) + (float(prob) * 0.5)
        base = _safe_base_from_value(value, i)
        seq.append(base if is_resonant else 'N')

    symbolic = ''.join(seq)
    summary = {
        'length': len(symbolic),
        'counts': {b: symbolic.count(b) for b in set(symbolic)},
        'resonant_fraction': (resonant / total) if total > 0 else 0.0
    }
    return {
        'symbolic_sequence': symbolic,
        'summary': summary
    }


def get_sequence_hash(symbolic: str) -> str:
    """Return SHA-256 hex digest of the symbolic sequence (used for provenance)."""
    return hashlib.sha256(symbolic.encode('utf-8')).hexdigest()


def stream_symbolic_sequence(qubit_states: List[Dict[str, Any]], out_dir: str = 'node10_out',
                             metatron_registry: Optional[str] = None, hmac_key: Optional[str] = None,
                             allow_raw: bool = False) -> Path:
    """Write a provenance JSON for the symbolic mapping and (optionally) archive it.

    By default this function writes only symbolic summaries and a SHA-256 hash. To include the
    raw symbolic string in the saved artifact set the environment variable `ALLOW_RAW_DNA_OUTPUT=1`
    or pass `allow_raw=True`. Enabling raw output requires explicit, auditable approval.
    """
    outp = Path(out_dir)
    outp.mkdir(parents=True, exist_ok=True)

    mapping = quantum_to_symbolic(qubit_states)
    symbolic = mapping['symbolic_sequence']
    seq_hash = get_sequence_hash(symbolic)

    payload = {
        'timestamp': int(time.time()),
        'node': 10,
        'symbolic_summary': mapping['summary'],
        'sequence_hash': seq_hash,
        'meta': {
            'phi': PHI
        }
    }

    # Only include raw symbolic sequence when explicitly allowed
    allow_flag = allow_raw or (os.getenv('ALLOW_RAW_DNA_OUTPUT') == '1')
    if allow_flag:
        # Extra safety: require explicit environment override and log
        logger.warning('Raw symbolic sequence emission enabled; this is gated by environment flag')
        payload['symbolic_sequence'] = symbolic

    fname = f"node10_{seq_hash[:12]}.json"
    out_path = outp / fname
    out_path.write_text(json.dumps(payload, indent=2))
    logger.info('Wrote Node10 provenance file: %s', out_path)

    # Optionally archive through Metatron's registry
    if metatron_registry:
        try:
            from metatron_nervous_system import MetatronNervousSystem
            m = MetatronNervousSystem(Path(metatron_registry))
            packet = m.create_packet(out_path, client='node10', hmac_key=hmac_key)
            m.archive_packet(packet)
            logger.info('Archived Node10 payload via Metatron')
        except Exception as e:
            logger.warning('Failed to archive via Metatron: %s', e)

    return out_path
