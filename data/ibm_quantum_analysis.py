"""
IBM Quantum Hardware Integration for Consciousness Analysis

Uses real quantum circuit execution results from IBM Quantum hardware
(ibm_fez, ibm_torino, ibm_marrakesh, ibm_kingston) to provide
ground-truth measurement distributions for the quantum consciousness pipeline.

Each job result contains:
  - BitArray measurement outcomes (50,128 shots per job)
  - Circuit metadata (depth, num_qubits, backend)
  - Outcome distribution across all possible bitstrings

These real distributions can validate whether phi-resonant VAE latent
structures show non-trivial quantum-like correlations vs random baselines.
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field

# IBM backends
IBM_BACKENDS = {
    "ibm_fez": "IBM Fez (127 qubits, Heron r3)",
    "ibm_marrakesh": "IBM Marrakesh (127 qubits, Eagle r3)",
    "ibm_torino": "IBM Torino (133 qubits, photonic)",
    "ibm_kyiv": "IBM Kyiv (127 qubits, Eagle r3)",
    "ibm_brisbane": "IBM Brisbane (127 qubits, Eagle r3)",
    "ibm_osaka": "IBM Osaka (127 qubits, Eagle r3)",
    "ibm_nairobi": "IBM Nairobi (127 qubits, Eagle r3)",
    "ibm_casablanca": "IBM Casablanca (127 qubits, Eagle r3)",
    "ibm_kingston": "IBM Kingston (127 qubits, Eagle r3)",
}


# ── Dataclasses ─────────────────────────────────────────────────────────────

@dataclass
class IBMJobResult:
    job_id: str
    backend: str
    status: str
    created: str
    completed: Optional[str]
    cost: int
    usage_ns: int
    num_qubits: int
    circuit_depth: int
    num_shots: int
    outcome_counts: Dict[str, int]
    total_shots: int
    raw_result: Dict


@dataclass
class WorkloadDataset:
    jobs: List[IBMJobResult]
    backend_counts: Dict[str, int]
    date_range: Tuple[str, str]
    total_shots: int


# ── Analysis ─────────────────────────────────────────────────────────────────

def compute_shannon_entropy(outcome_counts: Dict[str, int]) -> float:
    """Compute Shannon entropy H of an outcome distribution in bits."""
    total = sum(outcome_counts.values())
    if total == 0:
        return 0.0
    probs = [count / total for count in outcome_counts.values() if count > 0]
    return -sum(p * np.log2(p) for p in probs if p > 0)


def compute_max_entropy(num_bits: int) -> float:
    """Maximum possible entropy for num_bits (uniform distribution)."""
    return float(num_bits)


def compute_ibm_quantum_score(job: IBMJobResult) -> Dict:
    """
    Compute quantum signature metrics from IBM job results.

    Metrics:
    - shannon_entropy: H of outcome distribution
    - max_entropy: H_max = num_qubits (if num_qubits > 0)
    - entropy_ratio: H / H_max (0 = deterministic, 1 = uniform)
    - success_rate: fraction of shots in top-10 outcomes
    - gini_like: spread of distribution (0 = uniform, 1 = deterministic)
    """
    total = job.total_shots
    if total == 0 or not job.outcome_counts:
        return {"shannon_entropy": 0.0, "entropy_ratio": 0.0, "gini_like": 0.0}

    entropy = compute_shannon_entropy(job.outcome_counts)

    # Estimate num_bits from number of possible outcomes
    num_outcomes = len(job.outcome_counts)
    num_bits = int(np.round(np.log2(num_outcomes))) if num_outcomes > 1 else 1

    max_entropy = compute_max_entropy(num_bits)
    entropy_ratio = entropy / max_entropy if max_entropy > 0 else 0.0

    # Gini-like coefficient of distribution spread
    counts = np.array(list(job.outcome_counts.values()), dtype=float)
    counts_sorted = np.sort(counts)
    n = len(counts_sorted)
    cumsum = np.cumsum(counts_sorted)
    gini = (2.0 * np.sum((np.arange(1, n + 1) * counts_sorted))) / (n * np.sum(counts_sorted)) - (n + 1) / n
    gini = max(0.0, min(1.0, gini))

    # Success rate: fraction in top-10 outcomes
    sorted_outcomes = sorted(job.outcome_counts.items(), key=lambda x: -x[1])
    top10_shots = sum(count for _, count in sorted_outcomes[:10])
    success_rate = top10_shots / total

    return {
        "shannon_entropy": float(entropy),
        "max_entropy": float(max_entropy),
        "entropy_ratio": float(entropy_ratio),
        "gini_like": float(gini),
        "top10_fraction": float(success_rate),
        "num_outcomes": num_outcomes,
        "num_bits_estimated": num_bits,
    }


def analyze_backend_performance(dataset: WorkloadDataset) -> Dict:
    """Per-backend statistics."""
    from collections import defaultdict

    by_backend = defaultdict(list)
    for job in dataset.jobs:
        by_backend[job.backend].append(job)

    stats = {}
    for backend, jobs in by_backend.items():
        jobs_with_entropy = [j for j in jobs if j.outcome_counts]
        usage_s = [j.usage_ns / 1e9 for j in jobs if j.usage_ns > 0]
        entropies = [compute_shannon_entropy(j.outcome_counts) for j in jobs_with_entropy]
        scores = [compute_ibm_quantum_score(j) for j in jobs_with_entropy]

        # Circuit size analysis
        sizes = [j.circuit_size_bytes for j in jobs if j.circuit_size_bytes > 0]

        # Stratify by entropy (proxy for circuit family)
        high_entropy_jobs = [j for j in jobs_with_entropy
                            if len(j.outcome_counts) >= 200]
        low_entropy_jobs = [j for j in jobs_with_entropy
                           if len(j.outcome_counts) < 200]

        stats[backend] = {
            "n_jobs": len(jobs),
            "n_jobs_with_entropy": len(jobs_with_entropy),
            "total_shots": sum(j.total_shots for j in jobs),
            "success_rate": sum(1 for j in jobs if j.status == "Completed") / max(len(jobs), 1),
            "mean_entropy": float(np.mean(entropies)) if entropies else 0.0,
            "std_entropy": float(np.std(entropies)) if entropies else 0.0,
            "mean_entropy_ratio": float(np.mean([s["entropy_ratio"] for s in scores])) if scores else 0.0,
            "mean_gini": float(np.mean([s["gini_like"] for s in scores])) if scores else 0.0,
            "n_high_entropy": len(high_entropy_jobs),
            "n_low_entropy": len(low_entropy_jobs),
            "mean_circuit_size_bytes": float(np.mean(sizes)) if sizes else 0.0,
            "median_circuit_size_bytes": float(np.median(sizes)) if sizes else 0.0,
        }

    return stats


def compare_phi_vae_to_ibm(
    vae_phi_alignment: float,
    ibm_jobs: List[IBMJobResult],
) -> Dict:
    """
    Compare phi-VAE latent phi-alignment against real quantum hardware distributions.

    Phi-alignment is a structured prior injected by regularization.
    IBM outcomes are genuine quantum hardware distributions.

    This comparison asks: does the phi-regularized latent space
    show entropy/complexity patterns consistent with quantum hardware?

    Returns a comparison dict with z-scores vs IBM distribution.
    """
    if not ibm_jobs:
        return {}

    # Compute entropy for each IBM job
    ibm_entropies = [compute_shannon_entropy(j.outcome_counts) for j in ibm_jobs if j.outcome_counts]
    ibm_entropy_ratios = [compute_ibm_quantum_score(j)["entropy_ratio"] for j in ibm_jobs if j.outcome_counts]

    if not ibm_entropies:
        return {}

    mean_ibm_entropy = float(np.mean(ibm_entropies))
    std_ibm_entropy = float(np.std(ibm_entropies)) + 1e-12

    mean_ibm_ratio = float(np.mean(ibm_entropy_ratios))
    std_ibm_ratio = float(np.std(ibm_entropy_ratios)) + 1e-12

    # Z-score: where does phi-alignment fall in IBM distribution?
    z_entropy = (vae_phi_alignment - mean_ibm_entropy) / std_ibm_entropy

    return {
        "ibm_mean_entropy": mean_ibm_entropy,
        "ibm_std_entropy": std_ibm_entropy,
        "ibm_mean_entropy_ratio": mean_ibm_ratio,
        "ibm_std_entropy_ratio": std_ibm_ratio,
        "vae_phi_alignment": vae_phi_alignment,
        "z_score_vs_ibm": z_entropy,
        "interpretation": (
            "HIGHLY UNLIKELY" if abs(z_entropy) > 3
            else "UNLIKELY" if abs(z_entropy) > 2
            else "WITHIN_IBM_RANGE" if abs(z_entropy) <= 2
            else "UNKNOWN"
        ),
    }


def filter_jobs_by_backend(
    jobs: List[IBMJobResult],
    backend: str,
    min_shots: int = 1000,
) -> List[IBMJobResult]:
    """Filter IBM jobs by backend and minimum shot count."""
    return [
        j for j in jobs
        if j.backend == backend
        and j.total_shots >= min_shots
        and j.status == "Completed"
        and j.outcome_counts
    ]


def get_global_outcome_distribution(
    jobs: List[IBMJobResult],
) -> Dict[str, float]:
    """Aggregate outcome distribution across all jobs (normalized to probabilities)."""
    total_counts: Dict[str, int] = {}
    total_shots = 0
    for job in jobs:
        for outcome, count in job.outcome_counts.items():
            total_counts[outcome] = total_counts.get(outcome, 0) + count
            total_shots += count

    if total_shots == 0:
        return {}
    return {k: v / total_shots for k, v in total_counts.items()}


def chi_square_test_vs_uniform(
    job: IBMJobResult,
) -> Tuple[float, float]:
    """
    Chi-square test: does the outcome distribution deviate from uniform?

    Returns (chi2_statistic, p_value).
    """
    from scipy import stats as scipy_stats

    n_outcomes = len(job.outcome_counts)
    expected = job.total_shots / n_outcomes
    observed = np.array([job.outcome_counts.get(str(i), 0) for i in range(n_outcomes)], dtype=float)

    # Chi-square
    chi2 = np.sum((observed - expected) ** 2 / expected)
    # Degrees of freedom = n_outcomes - 1
    p_value = 1.0 - scipy_stats.chi2.cdf(chi2, df=max(n_outcomes - 1, 1))

    return float(chi2), float(p_value)


# ── CLI ───────────────────────────────────────────────────────────────────

def main():
    import argparse
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    import ibm_quantum_workloads as iqw

    parser = argparse.ArgumentParser(description="IBM Quantum consciousness analysis")
    parser.add_argument("--dir", default="E:/Descargas", help="Downloads directory")
    parser.add_argument("--backend", default=None, help="Filter by backend (e.g. ibm_fez)")
    parser.add_argument("--chi2", action="store_true", help="Run chi-square vs uniform test")
    parser.add_argument("--entropy", action="store_true", help="Show entropy distribution")
    args = parser.parse_args()

    print("=" * 60)
    print("IBM QUANTUM HARDWARE ANALYSIS")
    print("=" * 60)

    dataset = iqw.load_all_workloads(downloads_dir=args.dir)

    jobs = dataset.jobs
    if args.backend:
        jobs = filter_jobs_by_backend(jobs, args.backend)
        print(f"\nFiltered to {args.backend}: {len(jobs)} jobs")

    # Global distribution
    print(f"\nTotal: {len(dataset.jobs)} jobs, {dataset.total_shots:,} shots")
    print(f"Date range: {dataset.date_range[0]} to {dataset.date_range[1]}")
    print(f"Backends: {dataset.backend_counts}")

    # Per-backend performance
    print("\nBackend performance:")
    stats = analyze_backend_performance(dataset)
    for backend, s in sorted(stats.items()):
        print(f"  {backend}: jobs={s['n_jobs']}, shots={s['total_shots']:,}, "
              f"mean_H={s['mean_entropy']:.3f} bits, "
              f"entropy_ratio={s['mean_entropy_ratio']:.3f}, "
              f"gini={s['mean_gini']:.3f}")

    # Entropy distribution
    if args.entropy:
        all_entropies = [compute_shannon_entropy(j.outcome_counts) for j in jobs if j.outcome_counts]
        all_ratios = [compute_ibm_quantum_score(j)["entropy_ratio"] for j in jobs if j.outcome_counts]
        print(f"\nEntropy distribution ({len(all_entropies)} jobs):")
        print(f"  H: mean={np.mean(all_entropies):.3f}, std={np.std(all_entropies):.3f}, "
              f"min={np.min(all_entropies):.3f}, max={np.max(all_entropies):.3f}")
        print(f"  H_ratio: mean={np.mean(all_ratios):.3f}, std={np.std(all_ratios):.3f}")

    # Chi-square tests
    if args.chi2:
        print("\nChi-square vs uniform (first 10 jobs):")
        for job in jobs[:10]:
            if job.outcome_counts:
                chi2, p = chi_square_test_vs_uniform(job)
                sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
                print(f"  {job.job_id} [{job.backend}]: chi2={chi2:.1f}, p={p:.4f} {sig}")

    # Save full analysis
    analysis = {
        "n_jobs": len(dataset.jobs),
        "date_range": list(dataset.date_range),
        "total_shots": dataset.total_shots,
        "backend_counts": dataset.backend_counts,
        "per_backend": stats,
        "global_outcome_dist": get_global_outcome_distribution(dataset.jobs),
    }
    with open("ibm_quantum_analysis.json", "w") as f:
        json.dump(analysis, f, indent=2)
    print(f"\n[OK] Analysis saved to: ibm_quantum_analysis.json")


if __name__ == "__main__":
    main()
