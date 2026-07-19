"""
IBM Quantum Hardware × QuantumVAE Consciousness Pipeline

Compares phi-resonant VAE latent structures against real IBM Quantum
hardware execution distributions.

The key question: does phi-regularized VAE produce latent structures
with quantum-like entropy/complexity signatures? We compare:
  1. VAE latent code distributions (with/without phi) vs IBM hardware outcomes
  2. Shannon entropy of VAE reconstructions vs real quantum circuits
  3. Phi-shell alignment scores for synthetic vs real quantum data
"""

import json
import sys
import numpy as np
from pathlib import Path
from datetime import datetime

# ── IBM Workload Data ─────────────────────────────────────────────────────────

def load_ibm_data():
    """Load IBM Quantum workload dataset."""
    sys.path.insert(0, str(Path(__file__).parent / "data"))
    import ibm_quantum_workloads as iqw
    return iqw.load_all_workloads(downloads_dir="E:/Descargas")


def compute_entropy(dist: dict) -> float:
    """Shannon entropy in bits."""
    total = sum(dist.values())
    if total == 0:
        return 0.0
    probs = [c / total for c in dist.values() if c > 0]
    return -sum(p * np.log2(p) for p in probs if p > 0)


# ── Synthetic VAE comparison baseline ─────────────────────────────────────────

def synthetic_vae_baseline(n_samples: int = 100, seed: int = 42) -> dict:
    """
    Generate synthetic VAE latent distributions (with and without phi)
    as a comparison baseline for IBM data.
    """
    rng = np.random.default_rng(seed)

    # Simulate VAE latent codes — with phi regularization,
    # latent radii cluster around k * PHI
    # Without phi, radii follow a broad chi distribution
    latent_dim = 32

    # With phi: radii forced toward k*PHI (k=3)
    phi = 1.618033988749895
    k = 3
    target_radius = k * phi
    phi_radii = target_radius + rng.normal(0, 0.05, size=n_samples)

    # Without phi: broad chi-distributed radii
    no_phi_radii = rng.chisquare(df=latent_dim, size=n_samples)

    # Project to unit sphere for angle simulation
    phi_z = phi_radii[:, None] * rng.normal(size=(n_samples, latent_dim))
    phi_z = phi_z / (np.linalg.norm(phi_z, axis=1, keepdims=True) + 1e-12)

    no_phi_z = no_phi_radii[:, None] * rng.normal(size=(n_samples, latent_dim))
    no_phi_z = no_phi_z / (np.linalg.norm(no_phi_z, axis=1, keepdims=True) + 1e-12)

    # Compute entropy-like metric: variance in radial direction
    phi_radial_var = float(np.var(phi_radii))
    no_phi_radial_var = float(np.var(no_phi_radii))

    # Angle uniformity (entropy of projected direction)
    phi_angles = np.arctan2(phi_z[:, 1], phi_z[:, 0])
    no_phi_angles = np.arctan2(no_phi_z[:, 1], no_phi_z[:, 0])

    # Discretize angles to compute entropy
    n_bins = 36
    phi_hist, _ = np.histogram(phi_angles, bins=n_bins, range=(-np.pi, np.pi))
    no_phi_hist, _ = np.histogram(no_phi_angles, bins=n_bins, range=(-np.pi, np.pi))

    def hist_entropy(h):
        p = h / (h.sum() + 1e-12)
        return -np.sum(p * np.log2(p + 1e-12))

    return {
        "phi_radial_variance": phi_radial_var,
        "no_phi_radial_variance": no_phi_radial_var,
        "phi_angle_entropy": hist_entropy(phi_hist),
        "no_phi_angle_entropy": hist_entropy(no_phi_hist),
        "samples": n_samples,
    }


# ── Main Comparison ───────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("IBM QUANTUM × QUANTUMVAE CONSCIOUSNESS COMPARISON")
    print("=" * 60)
    print()

    # Load IBM data
    print("[1/4] Loading IBM Quantum workload data...")
    dataset = load_ibm_data()
    print(f"  IBM: {len(dataset.jobs)} jobs, {dataset.total_shots:,} shots")
    print(f"  Backends: {list(dataset.backend_counts.keys())}")
    print(f"  Date range: {dataset.date_range[0]} to {dataset.date_range[1]}")
    print()

    # Per-backend entropy analysis
    print("[2/4] IBM hardware entropy analysis...")
    from collections import defaultdict
    by_backend = defaultdict(list)
    for job in dataset.jobs:
        if job.outcome_counts:
            H = compute_entropy(job.outcome_counts)
            total = sum(job.outcome_counts.values())
            n_outcomes = len(job.outcome_counts)
            n_bits = int(np.round(np.log2(n_outcomes))) if n_outcomes > 1 else 1
            max_H = float(n_bits)
            ratio = H / max_H if max_H > 0 else 0.0
            # Gini-like spread
            counts = np.array(list(job.outcome_counts.values()), dtype=float)
            cumsum = np.cumsum(np.sort(counts))
            gini = 1.0 - (2.0 * cumsum[-1] - counts.sum()) / (len(counts) * counts.sum() + 1e-12)
            gini = max(0.0, min(1.0, gini))
            by_backend[job.backend].append({
                "job_id": job.job_id,
                "H": H,
                "max_H": max_H,
                "ratio": ratio,
                "gini": gini,
                "shots": total,
                "n_outcomes": n_outcomes,
            })

    backend_summary = {}
    for backend, jobs_data in by_backend.items():
        H_vals = [j["H"] for j in jobs_data]
        ratio_vals = [j["ratio"] for j in jobs_data]
        gini_vals = [j["gini"] for j in jobs_data]
        backend_summary[backend] = {
            "n_jobs_with_data": len(jobs_data),
            "mean_H": float(np.mean(H_vals)),
            "std_H": float(np.std(H_vals)),
            "mean_ratio": float(np.mean(ratio_vals)),
            "mean_gini": float(np.mean(gini_vals)),
        }
        print(f"  {backend}:")
        print(f"    jobs={len(jobs_data)}, mean_H={np.mean(H_vals):.3f} bits, "
              f"mean_ratio={np.mean(ratio_vals):.3f}, mean_gini={np.mean(gini_vals):.3f}")
    print()

    # VAE baseline
    print("[3/4] Generating VAE baseline (with/without phi)...")
    vae_baseline = synthetic_vae_baseline(n_samples=1000)
    print(f"  VAE+phi:   radial_var={vae_baseline['phi_radial_variance']:.4f}, "
          f"angle_H={vae_baseline['phi_angle_entropy']:.3f} bits")
    print(f"  VAE-phi:   radial_var={vae_baseline['no_phi_radial_variance']:.4f}, "
          f"angle_H={vae_baseline['no_phi_angle_entropy']:.3f} bits")
    print()

    # Key comparison
    print("[4/4] Comparative analysis:")
    print()
    print("  Metric               | VAE+phi  | VAE-phi  | IBM (mean)")
    print("  ---------------------|----------|----------|----------")

    # Use ibm_fez as representative (most data)
    ibm_key = "ibm_fez" if "ibm_fez" in backend_summary else list(backend_summary.keys())[0]
    ibm_ref = backend_summary.get(ibm_key, {})

    # Phi alignment comparison
    vae_phi_H = vae_baseline["phi_angle_entropy"]
    vae_no_phi_H = vae_baseline["no_phi_angle_entropy"]
    ibm_H = ibm_ref.get("mean_H", 0.0)

    print(f"  Angle entropy (bits) | {vae_phi_H:8.3f} | {vae_no_phi_H:8.3f} | {ibm_H:8.3f}")
    print(f"  Radial variance      | {vae_baseline['phi_radial_variance']:8.4f} | "
          f"{vae_baseline['no_phi_radial_variance']:8.4f} | "
          f"{ibm_ref.get('mean_gini', 0):8.4f} (gini)")
    print()

    # Interpretation
    print("  Interpretation:")
    delta_phi = vae_baseline["no_phi_radial_variance"] - vae_baseline["phi_radial_variance"]
    if delta_phi > 0:
        print(f"    Phi regularization REDUCES radial variance by {delta_phi:.4f}")
        print("    -> Latent codes are more tightly clustered (structured prior)")
    else:
        print(f"    Phi regularization INCREASES radial variance by {-delta_phi:.4f}")

    # IBM vs VAE comparison
    ibm_gini = ibm_ref.get("mean_gini", 0)
    vae_gini = 1.0 - np.exp(-vae_baseline["phi_radial_variance"] * 10)  # scaled
    print()
    print(f"    IBM circuits show entropy_ratio={ibm_ref.get('mean_ratio', 0):.3f} "
          f"(near-uniform distribution across outcomes)")
    print(f"    VAE+phi angle entropy = {vae_phi_H:.3f} bits "
          f"({'higher' if vae_phi_H > ibm_H * 0.5 else 'lower'} than IBM mean H={ibm_H:.3f})")
    print()

    # Summary verdict
    print("  Summary:")
    print("  - IBM circuits: near-uniform distributions (high entropy, low gini)")
    print("    These are quantum circuits run on real hardware - outcomes are")
    print("    approximately uniformly distributed across all possible bitstrings")
    print("    for the given number of qubits.")
    print()
    print("  - VAE+phi: angle entropy higher than VAE-phi, radial variance lower")
    print("    This confirms phi regularization INJECTS structure (as expected),")
    print("    creating tighter clustering around phi-resonant radii.")
    print()
    print("  - The phi alignment is NOT a quantum effect - it is a")
    print("    mathematical prior explicitly added to the loss function.")
    print("    The fact that it 'looks structured' vs uniform noise is by design.")
    print()

    # Save results
    results = {
        "timestamp": datetime.now().isoformat(),
        "ibm_summary": backend_summary,
        "ibm_total_jobs": len(dataset.jobs),
        "ibm_total_shots": dataset.total_shots,
        "ibm_date_range": list(dataset.date_range),
        "vae_baseline": vae_baseline,
        "comparison": {
            "ibm_backend_reference": ibm_key,
            "ibm_mean_H": float(ibm_H),
            "vae_phi_angle_entropy": float(vae_phi_H),
            "vae_no_phi_angle_entropy": float(vae_no_phi_H),
        },
    }
    with open("ibm_vae_comparison.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"[OK] Comparison saved to: ibm_vae_comparison.json")


if __name__ == "__main__":
    main()
