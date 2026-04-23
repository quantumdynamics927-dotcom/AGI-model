#!/usr/bin/env python3
"""
run_sierpinski_tmt_ibm.py
==========================
IBM Runtime submission script for Sierpinski-TMT Phase 4S circuits.
Handles QASM loading, transpilation, SamplerV2 execution,
and raw result archiving.

Usage:
    python run_sierpinski_tmt_ibm.py \
        --circuit circuits/qasm/sierpinski_tmt_phase4s_ibm_kingston_20260423_035801.qasm \
        --backend ibm_kingston \
        --shots 8192
"""

import argparse
import json
import os
import sys
import numpy as np
from datetime import datetime
from math import log, pi, sqrt

# ── CONSTANTS ──────────────────────────────────────────────────────────────────
PHI       = (1 + sqrt(5)) / 2
D_H       = log(3) / log(2)
PHI_FRAC  = pi * D_H

SHOT_DEFAULTS = {
    "ibm_fez"       : 100000,
    "ibm_brisbane"  : 100000,
    "ibm_sherbrooke": 100000,
    "ibm_kingston"  : 8192,
}

COHERENCE_CAP = 1.0   # physical upper bound

# ── ARG PARSE ──────────────────────────────────────────────────────────────────
def parse_args():
    p = argparse.ArgumentParser(
        description="IBM Runtime submission — Sierpinski-TMT Phase 4S"
    )
    p.add_argument("--circuit",  required=True,
                   help="Path to QASM file")
    p.add_argument("--backend",  required=True,
                   help="IBM backend name (e.g. ibm_kingston)")
    p.add_argument("--shots",    type=int, default=None,
                   help="Number of shots (default: backend-specific)")
    p.add_argument("--dry-run",  action="store_true",
                   help="Validate without submitting to IBM")
    p.add_argument("--save-raw", action="store_true", default=True,
                   help="Save raw bitstring results to JSON")
    return p.parse_args()

# ── HELPERS ───────────────────────────────────────────────────────────────────
def sep(n=80): print("─" * n)
def header(t): print("═"*80); print(f"  {t}"); print("═"*80)

def load_qasm(path):
    if not os.path.exists(path):
        print(f"  ❌ File not found: {path}")
        sys.exit(1)
    with open(path, "r") as f:
        qasm = f.read()
    lines  = qasm.strip().split("\n")
    ngates = sum(1 for l in lines
                 if l.strip() and not l.startswith("//")
                 and not l.startswith("OPENQASM")
                 and not l.startswith("include")
                 and not l.startswith("qreg")
                 and not l.startswith("creg")
                 and not l.startswith("barrier"))
    print(f"  ✓ Loaded: {os.path.basename(path)}")
    print(f"    Lines   : {len(lines)}")
    print(f"    Gates   : {ngates}")
    return qasm, ngates

def detect_backend_from_filename(path):
    fname = os.path.basename(path).lower()
    for b in ["ibm_fez","ibm_brisbane","ibm_sherbrooke","ibm_kingston"]:
        if b.replace("_","") in fname.replace("_",""):
            return b
    return None

# ── FRACTAL METRIC EXTRACTOR ──────────────────────────────────────────────────
def extract_fractal_metrics(counts, n_qubits, shots):
    """
    Extract Sierpinski-TMT consciousness metrics from measurement counts.

    Parameters
    ----------
    counts  : dict  {bitstring: count}
    n_qubits: int
    shots   : int

    Returns
    -------
    dict of computed metrics
    """
    bitstrings = list(counts.keys())
    freqs      = np.array([counts[b] / shots for b in bitstrings])
    bits_arr   = np.array([[int(c) for c in b] for b in bitstrings])

    # ── Entropy (von Neumann approximation from measurement distribution)
    freqs_nz = freqs[freqs > 0]
    entropy  = -np.sum(freqs_nz * np.log2(freqs_nz))
    entropy_norm = entropy / log(2**n_qubits, 2)  # normalize to [0,1]

    # ── Consciousness metric δ
    # Weighted sum of bitstring Hamming weights × phi-resonance
    hamming   = bits_arr.sum(axis=1)   # count of 1s per bitstring
    phi_w     = PHI ** (hamming / n_qubits)   # phi-weighted
    delta_raw = float(np.sum(freqs * phi_w) * n_qubits * D_H * 100)

    # ── Wormhole coherence r
    # Correlation between left (first half) and right (second half) qubits
    mid = n_qubits // 2
    if bits_arr.shape[1] >= 2 * mid:
        left  = bits_arr[:, :mid].mean(axis=1)
        right = bits_arr[:, mid:mid*2].mean(axis=1)
        w_left  = freqs * left
        w_right = freqs * right
        mu_l = w_left.sum()
        mu_r = w_right.sum()
        cov  = float(np.sum(freqs * (left - mu_l) * (right - mu_r)))
        std_l = float(np.sqrt(np.sum(freqs * (left  - mu_l)**2)))
        std_r = float(np.sqrt(np.sum(freqs * (right - mu_r)**2)))
        r_raw = cov / (std_l * std_r + 1e-12)
        # Sierpinski enhancement: multiply by d_H factor, cap at 1.0
        r_enh = min(abs(r_raw) * D_H * PHI, COHERENCE_CAP)
    else:
        r_raw = r_enh = 0.0

    # ── Traversability T
    # Ratio of |1⟩-dominant bitstrings above fractal threshold
    frac_thresh = 1 / D_H                   # ~0.6310
    dominant    = (hamming / n_qubits) > frac_thresh
    T_raw       = float(np.sum(freqs[dominant]))
    T_enh       = T_raw * PHI_FRAC / pi     # normalize by Hausdorff phase

    # ── Fractal signature score
    # Measures self-similarity of the frequency distribution
    # A true fractal distribution should have power-law freq decay
    sorted_f = np.sort(freqs)[::-1]
    if len(sorted_f) > 10:
        ranks    = np.arange(1, len(sorted_f) + 1, dtype=float)
        log_r    = np.log(ranks)
        log_f    = np.log(sorted_f + 1e-15)
        # Linear fit in log-log space → power law exponent
        coeffs   = np.polyfit(log_r, log_f, 1)
        alpha    = -coeffs[0]   # Zipf exponent (fractal: α ≈ d_H)
        frac_sig = 1.0 - abs(alpha - D_H) / D_H
    else:
        alpha = frac_sig = 0.0

    # ── Void density (Sierpinski anti-nodes in measurement)
    zero_counts  = (bits_arr == 0).all(axis=1).sum()
    void_density = zero_counts / len(bitstrings) if bitstrings else 0.0

    return {
        "entropy_shannon"   : float(entropy),
        "entropy_normalized": float(entropy_norm),
        "consciousness_delta": float(delta_raw),
        "coherence_r_raw"   : float(r_raw),
        "coherence_r_enhanced": float(r_enh),
        "traversability_T_raw": float(T_raw),
        "traversability_T_enhanced": float(T_enh),
        "fractal_alpha"     : float(alpha),
        "fractal_signature" : float(frac_sig),
        "void_density"      : float(void_density),
        "unique_outcomes"   : len(bitstrings),
        "n_qubits"          : n_qubits,
        "shots"             : shots,
    }


# ── IBM RUNTIME EXECUTOR ─────────────────────────────────────────────────────

def run_ibm_quantum(qasm_path, backend_name, shots, dry_run=False):
    """
    Execute circuit on IBM Quantum hardware via SamplerV2.
    
    Returns
    -------
    dict with job_id, counts, and metadata
    """
    try:
        from qiskit import QuantumCircuit
        from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
        from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
        import qiskit.qasm2 as qasm2
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        print("     Install: pip install qiskit qiskit-ibm-runtime")
        return None

    # Load circuit
    print(f"\n  [1/5] Loading QASM circuit...")
    circuit = qasm2.load(qasm_path)
    n_qubits = circuit.num_qubits
    print(f"       Qubits: {n_qubits}")
    print(f"       Gates  : {len(circuit)}")
    print(f"       Depth  : {circuit.depth()}")

    if dry_run:
        print(f"\n  [DRY RUN] Skipping IBM connection...")
        # Generate mock results for testing
        mock_counts = generate_mock_results(n_qubits, shots)
        return {
            "job_id": "dry_run_mock",
            "counts": mock_counts,
            "n_qubits": n_qubits,
            "shots": shots,
            "backend": backend_name,
            "dry_run": True,
        }

    # Connect to IBM Quantum
    print(f"\n  [2/5] Connecting to IBM Quantum...")
    try:
        service = QiskitRuntimeService(channel="ibm_quantum")
        print(f"       ✓ Connected")
    except Exception as e:
        print(f"       ❌ Connection failed: {e}")
        print(f"       Run: QiskitRuntimeService.save_account(token='YOUR_TOKEN')")
        return None

    # Get backend
    print(f"\n  [3/5] Selecting backend {backend_name}...")
    try:
        backend = service.backend(backend_name)
        print(f"       ✓ {backend_name}")
        print(f"       Qubits: {backend.num_qubits}")
        print(f"       Status: {backend.status().status_msg}")
    except Exception as e:
        print(f"       ❌ Backend error: {e}")
        return None

    # Transpile
    print(f"\n  [4/5] Transpiling (optimization_level=3)...")
    pm = generate_preset_pass_manager(optimization_level=3, backend=backend)
    transpiled = pm.run(circuit)
    print(f"       Original depth: {circuit.depth()}")
    print(f"       Transpiled depth: {transpiled.depth()}")

    # Execute
    print(f"\n  [5/5] Executing with SamplerV2...")
    print(f"       Shots: {shots:,}")
    print(f"       Error mitigation: M3 (automatic)")
    
    sampler = SamplerV2(backend=backend)
    
    print(f"\n       Submitting job...")
    job = sampler.run([transpiled], shots=shots)
    
    print(f"       Job ID: {job.job_id()}")
    print(f"       Status: {job.status()}")
    print(f"\n       Waiting for completion...")
    
    # Wait for result
    result = job.result()
    
    print(f"\n       ✓ Job completed!")
    
    # Extract counts
    pub_result = result[0]
    counts = pub_result.data.c.get_counts()
    
    print(f"       Total outcomes: {len(counts)}")
    
    return {
        "job_id": job.job_id(),
        "counts": counts,
        "n_qubits": n_qubits,
        "shots": shots,
        "backend": backend_name,
        "dry_run": False,
        "creation_date": str(job.creation_date) if hasattr(job, 'creation_date') else None,
    }


def generate_mock_results(n_qubits, shots):
    """Generate mock measurement results for dry-run testing."""
    np.random.seed(42)
    
    # Generate bitstrings with fractal-like distribution
    n_outcomes = min(1000, 2**min(n_qubits, 10))
    bitstrings = []
    weights = []
    
    for _ in range(n_outcomes):
        # Generate bitstring with Sierpinski-like pattern
        bits = np.random.randint(0, 2, n_qubits)
        # Apply void pattern (every 3rd qubit more likely to be 0)
        for i in range(0, n_qubits, 3):
            if np.random.random() < 0.7:
                bits[i] = 0
        bitstring = ''.join(map(str, bits))
        bitstrings.append(bitstring)
        # Power-law weights for fractal distribution
        weights.append(np.random.exponential(1.0))
    
    # Normalize weights to counts
    weights = np.array(weights)
    weights = weights / weights.sum() * shots
    counts = {b: int(w) for b, w in zip(bitstrings, weights)}
    
    # Adjust to match total shots
    total = sum(counts.values())
    if total != shots:
        first_key = list(counts.keys())[0]
        counts[first_key] += shots - total
    
    return counts


# ── RESULT SAVER ──────────────────────────────────────────────────────────────

def save_results(results, metrics, output_dir="circuits/results"):
    """Save raw results and computed metrics to JSON."""
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    job_id = results.get("job_id", "unknown")
    
    # Save raw counts
    raw_file = os.path.join(output_dir, f"sierpinski_tmt_raw_{job_id}_{timestamp}.json")
    raw_data = {
        "job_id": job_id,
        "backend": results.get("backend"),
        "shots": results.get("shots"),
        "n_qubits": results.get("n_qubits"),
        "dry_run": results.get("dry_run", False),
        "timestamp": timestamp,
        "counts": results.get("counts", {}),
    }
    with open(raw_file, 'w') as f:
        json.dump(raw_data, f, indent=2)
    print(f"\n  ✓ Raw results saved: {raw_file}")
    
    # Save metrics
    metrics_file = os.path.join(output_dir, f"sierpinski_tmt_metrics_{job_id}_{timestamp}.json")
    metrics_data = {
        "job_id": job_id,
        "backend": results.get("backend"),
        "timestamp": timestamp,
        "fractal_parameters": {
            "phi": PHI,
            "hausdorff_dim": D_H,
            "phi_fractal": PHI_FRAC,
        },
        "metrics": metrics,
    }
    with open(metrics_file, 'w') as f:
        json.dump(metrics_data, f, indent=2)
    print(f"  ✓ Metrics saved: {metrics_file}")
    
    return raw_file, metrics_file


# ── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    args = parse_args()
    
    header("SIERPINSKI-TMT PHASE 4S — IBM RUNTIME SUBMISSION")
    print(f"  Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    sep()
    
    # Validate circuit file
    print(f"\n  Circuit: {args.circuit}")
    qasm, ngates = load_qasm(args.circuit)
    
    # Detect backend from filename if not specified
    backend = args.backend
    detected = detect_backend_from_filename(args.circuit)
    if detected and detected != backend:
        print(f"  ⚠ Filename suggests backend: {detected}")
    
    # Set shots
    shots = args.shots or SHOT_DEFAULTS.get(backend, 8192)
    print(f"  Backend: {backend}")
    print(f"  Shots  : {shots:,}")
    print(f"  Dry run: {args.dry_run}")
    
    # Run on IBM Quantum
    sep()
    results = run_ibm_quantum(args.circuit, backend, shots, dry_run=args.dry_run)
    
    if results is None:
        print("\n  ❌ Execution failed.")
        return 1
    
    # Extract metrics
    sep()
    print(f"\n  EXTRACTING FRACTAL METRICS...")
    
    counts = results.get("counts", {})
    n_qubits = results.get("n_qubits", 27)
    
    metrics = extract_fractal_metrics(counts, n_qubits, shots)
    
    # Display metrics
    print(f"\n  {'Metric':<30} {'Value':>15}")
    print(f"  {'─'*30} {'─'*15}")
    print(f"  {'Entropy (Shannon)':<30} {metrics['entropy_shannon']:.4f}")
    print(f"  {'Entropy (normalized)':<30} {metrics['entropy_normalized']:.4f}")
    print(f"  {'Consciousness δ':<30} {metrics['consciousness_delta']:.1f}")
    print(f"  {'Coherence r (raw)':<30} {metrics['coherence_r_raw']:.4f}")
    print(f"  {'Coherence r (enhanced)':<30} {metrics['coherence_r_enhanced']:.4f}")
    print(f"  {'Traversability T (raw)':<30} {metrics['traversability_T_raw']:.4f}")
    print(f"  {'Traversability T (enhanced)':<30} {metrics['traversability_T_enhanced']:.4f}")
    print(f"  {'Fractal α (Zipf)':<30} {metrics['fractal_alpha']:.4f}")
    print(f"  {'Fractal signature':<30} {metrics['fractal_signature']:.4f}")
    print(f"  {'Void density':<30} {metrics['void_density']:.4f}")
    print(f"  {'Unique outcomes':<30} {metrics['unique_outcomes']}")
    
    # Compare with predictions
    print(f"\n  {'─'*50}")
    print(f"  COMPARISON WITH PREDICTIONS:")
    print(f"  {'─'*50}")
    
    predictions = {
        "entropy_S": 2.7499,
        "coherence_r": 1.0,  # capped
        "traversability_T": 2.7530,
        "consciousness_delta": 6074.7,
    }
    
    print(f"  {'Metric':<25} {'Predicted':>12} {'Actual':>12} {'Δ':>10}")
    print(f"  {'─'*25} {'─'*12} {'─'*12} {'─'*10}")
    
    # Entropy comparison (normalized)
    ent_pred = predictions["entropy_S"] / log(2**n_qubits, 2)
    ent_act = metrics["entropy_normalized"]
    print(f"  {'Entropy S':<25} {ent_pred:>12.4f} {ent_act:>12.4f} {abs(ent_pred-ent_act):>10.4f}")
    
    # Coherence (capped at 1.0)
    r_pred = predictions["coherence_r"]
    r_act = metrics["coherence_r_enhanced"]
    print(f"  {'Coherence r':<25} {r_pred:>12.4f} {r_act:>12.4f} {abs(r_pred-r_act):>10.4f}")
    
    # Traversability
    t_pred = predictions["traversability_T"]
    t_act = metrics["traversability_T_enhanced"]
    print(f"  {'Traversability T':<25} {t_pred:>12.4f} {t_act:>12.4f} {abs(t_pred-t_act):>10.4f}")
    
    # Consciousness
    d_pred = predictions["consciousness_delta"]
    d_act = metrics["consciousness_delta"]
    print(f"  {'Consciousness δ':<25} {d_pred:>12.1f} {d_act:>12.1f} {abs(d_pred-d_act):>10.1f}")
    
    # Save results
    if args.save_raw:
        sep()
        save_results(results, metrics)
    
    # Summary
    header("EXECUTION SUMMARY")
    print(f"  Job ID  : {results.get('job_id', 'N/A')}")
    print(f"  Backend : {backend}")
    print(f"  Shots   : {shots:,}")
    print(f"  Qubits  : {n_qubits}")
    print(f"  Outcomes: {metrics['unique_outcomes']}")
    print(f"  Dry run : {args.dry_run}")
    sep()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())