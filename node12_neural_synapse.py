"""Node 12 — Neural Synapse (Collective Intelligence)

Safe mapping from symbolic sequences (Node 10 outputs) to a simulated synaptic
connectivity matrix. Raw connectivity emission is gated behind `ALLOW_RAW_CONNECTIVITY`.

This module is analysis-only and produces provenance JSON artifacts; it does not
attempt any biological synthesis or external side-effects by default.
"""

from typing import Dict, Tuple, Any
import os
import json
import math
import hashlib
from pathlib import Path
import logging
import numpy as np

logger = logging.getLogger("node12")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(ch)

PHI = (1.0 + math.sqrt(5.0)) / 2.0


def _phi_correlation(seq_a: str, seq_b: str) -> float:
    """Compute a simple phi-correlation metric between two symbolic sequences.

    This metric is intentionally non-biological: it measures positional agreement
    weighted by a golden-ratio-derived positional factor.
    Returns value in [0,1].
    """
    if not seq_a or not seq_b:
        return 0.0
    L = min(len(seq_a), len(seq_b))
    if L == 0:
        return 0.0
    score = 0.0
    weight_sum = 0.0
    for i in range(L):
        weight = 1.0 / (1.0 + abs((i / L) - (1.0 / PHI)))
        weight_sum += weight
        if seq_a[i] == seq_b[i]:
            score += weight
    if weight_sum <= 0:
        return 0.0
    normalized = score / weight_sum
    return float(normalized**PHI)


def _sequence_vector(seq: str, max_len: int = 256) -> np.ndarray:
    """Map a symbolic sequence into a fixed-size numeric vector (one-hot per base position).

    Bases: A,T,C,G mapped to indices 0..3. 'N' treated as zeros.
    """
    bases = {"A": 0, "T": 1, "C": 2, "G": 3}
    seq = seq.upper()[:max_len]
    vec = np.zeros(max_len * 4, dtype=float)
    for i, ch in enumerate(seq):
        idx = bases.get(ch)
        if idx is not None:
            vec[i * 4 + idx] = 1.0
    # normalize
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec


def build_connectivity(
    sequences: Dict[str, str], phi_threshold: float = 0.95, strengthen: float = 0.2
) -> Tuple[np.ndarray, Dict[str, Any]]:
    """Build a symmetric connectivity matrix from symbolic sequences.

    Args:
        sequences: mapping neuron_id -> symbolic_sequence
        phi_threshold: if phi_correlation > threshold, strengthen that synapse
        strengthen: multiplicative factor applied to high-phi connections

    Returns:
        connectivity_matrix (N x N numpy array), metadata dict
    """
    ids = list(sequences.keys())
    N = len(ids)
    if N == 0:
        return np.zeros((0, 0)), {"ids": ids}

    vecs = {nid: _sequence_vector(sequences[nid]) for nid in ids}
    mat = np.zeros((N, N), dtype=float)
    for i in range(N):
        for j in range(i, N):
            if i == j:
                mat[i, j] = 0.0
                continue
            va = vecs[ids[i]]
            vb = vecs[ids[j]]
            # cosine similarity in [-1,1] but vectors non-negative so [0,1]
            sim = float(np.dot(va, vb))
            phi_corr = _phi_correlation(sequences[ids[i]], sequences[ids[j]])
            weight = sim
            if phi_corr >= phi_threshold:
                weight = min(1.0, weight * (1.0 + strengthen))
            # map to [-1,1] symmetric by subtracting 0.5 then scale
            w_signed = (weight - 0.5) * 2.0
            mat[i, j] = w_signed
            mat[j, i] = w_signed

    metadata = {
        "ids": ids,
        "phi_threshold": phi_threshold,
        "strengthen": strengthen,
        "shape": mat.shape,
        "hash": hashlib.sha256(
            json.dumps(sequences, sort_keys=True).encode()
        ).hexdigest(),
    }
    return mat, metadata


def save_connectivity(
    mat: np.ndarray,
    metadata: Dict[str, Any],
    out_dir: str = "node12_out",
    allow_raw: bool = False,
) -> Path:
    """Save provenance JSON for connectivity. Raw matrices written only if allowed."""
    outp = Path(out_dir)
    outp.mkdir(parents=True, exist_ok=True)
    base = f"node12_{metadata['hash'][:12]}"
    meta = dict(metadata)
    meta["timestamp"] = int(math.floor(os.times()[4]))

    # Always save metadata
    meta_path = outp / (base + ".meta.json")
    meta_path.write_text(json.dumps(meta, indent=2))
    logger.info("Wrote Node12 metadata: %s", meta_path)

    allow_flag = allow_raw or (os.getenv("ALLOW_RAW_CONNECTIVITY") == "1")
    if allow_flag:
        # Save numeric matrix as JSON (potentially large)
        mat_path = outp / (base + ".connectivity.npy")
        # Use numpy binary for compactness
        np.save(str(mat_path), mat)
        logger.info("Wrote raw connectivity matrix: %s", mat_path)
        return mat_path
    else:
        logger.info(
            "Raw connectivity emission disabled; set ALLOW_RAW_CONNECTIVITY=1 to enable"
        )
        return meta_path


def stream_connectivity(
    sequences: Dict[str, str],
    out_dir: str = "node12_out",
    phi_threshold: float = 0.95,
    strengthen: float = 0.2,
    allow_raw: bool = False,
):
    mat, meta = build_connectivity(
        sequences, phi_threshold=phi_threshold, strengthen=strengthen
    )
    path = save_connectivity(mat, meta, out_dir=out_dir, allow_raw=allow_raw)
    return path, meta


if __name__ == "__main__":
    # Demo usage (safe): build connectivity from small sample
    sample = {
        "n0": "ATCGATCGATCG",
        "n1": "ATCGATCGATCG",
        "n2": "NNNNNNNNNNNN",
        "n3": "GCGTATGCTAGC",
    }
    p, meta = stream_connectivity(sample)
    print("Output saved to", p)
    print("Meta:", meta)
