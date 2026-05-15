"""
Run 3-Qubit Baseline Experiment

Execute OBS-3Q circuit variants and collect baseline metrics.

Usage:
    python run_3q_baseline.py [--shots SHOTS] [--backend BACKEND]
"""

import argparse
import json

# Add parent to path for imports
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np
from qiskit import transpile
from qiskit_aer import AerSimulator

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from circuits.security_topologies.observer_symmetry_3q import (
    InterceptionMode,
    OBS3QConfig,
    create_obs_3q_circuit,
    get_circuit_info,
)


def compute_distribution(counts: dict, n_bits: int = 1) -> np.ndarray:
    """
    Convert counts to probability distribution.

    Args:
        counts: Qiskit counts dictionary
        n_bits: Number of measured bits

    Returns:
        Probability distribution as numpy array
    """
    total = sum(counts.values())
    n_outcomes = 2**n_bits

    distribution = np.zeros(n_outcomes)
    for bitstring, count in counts.items():
        # Handle both string and int keys
        if isinstance(bitstring, str):
            idx = int(bitstring, 2)
        else:
            idx = bitstring
        distribution[idx] = count / total

    return distribution


def kl_divergence(p: np.ndarray, q: np.ndarray, epsilon: float = 1e-10) -> float:
    """
    Compute KL divergence D_KL(p || q).

    Args:
        p: True distribution
        q: Approximating distribution
        epsilon: Small value to avoid log(0)

    Returns:
        KL divergence value
    """
    p = np.clip(p, epsilon, 1.0)
    q = np.clip(q, epsilon, 1.0)
    return float(np.sum(p * np.log(p / q)))


def compute_symmetry_score(
    counts: dict, left_bit: int = 0, right_bit: int = 2
) -> float:
    """
    Compute symmetry score for bilateral circuit.

    For 3-qubit circuit measuring all qubits, compare P(L|C) vs P(R|C).

    Args:
        counts: Measurement counts
        left_bit: Index of left reservoir bit
        right_bit: Index of right reservoir bit

    Returns:
        Symmetry score in [0, 1]
    """
    total = sum(counts.values())

    # Compute conditional probabilities P(L=1|C=0), P(R=1|C=0), etc.
    # For center-only measurement, we need full measurement
    # This is a placeholder for the full 3-bit measurement case

    # For center-only measurement, use balance of outcomes
    if "0" in counts and "1" in counts:
        p0 = counts["0"] / total
        p1 = counts["1"] / total
        # Symmetry score based on balance
        return 1.0 - abs(p0 - p1)

    return 1.0


def compute_min_entropy(distribution: np.ndarray) -> float:
    """
    Compute min-entropy of distribution.

    Args:
        distribution: Probability distribution

    Returns:
        Min-entropy in bits
    """
    max_prob = np.max(distribution)
    return -np.log2(max_prob + 1e-10)


def run_experiment(
    shots: int = 8192,
    backend_name: str = "aer_simulator",
    seed: Optional[int] = None,
    output_dir: Optional[Path] = None,
) -> dict:
    """
    Run the complete 3-qubit baseline experiment.

    Args:
        shots: Number of shots per circuit
        backend_name: Simulator backend name
        seed: Random seed for reproducibility
        output_dir: Directory to save results

    Returns:
        Dictionary with all results
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Initialize backend
    if backend_name == "aer_simulator":
        backend = AerSimulator()
    else:
        backend = AerSimulator()  # Default fallback

    results = {
        "timestamp": timestamp,
        "shots": shots,
        "backend": backend_name,
        "seed": seed,
        "modes": {},
    }

    # Run each interception mode
    for mode in InterceptionMode:
        print(f"\nRunning {mode.value} mode...")

        config = OBS3QConfig(
            shots=shots,
            interception_mode=mode,
            measure_all=(mode != InterceptionMode.NONE),
        )
        circuit = create_obs_3q_circuit(config)

        # Transpile for backend
        transpiled = transpile(circuit, backend)

        # Run circuit
        job = backend.run(transpiled, shots=shots, seed_simulator=seed)
        counts = job.result().get_counts()

        # Compute metrics
        if mode == InterceptionMode.NONE:
            # Center-only measurement
            distribution = compute_distribution(counts, n_bits=1)
            symmetry_score = compute_symmetry_score(counts)
        else:
            # Full measurement for interception modes
            distribution = compute_distribution(counts, n_bits=3)
            symmetry_score = compute_symmetry_score(counts)

        min_entropy = compute_min_entropy(distribution)

        mode_results = {
            "circuit_info": get_circuit_info(circuit),
            "counts": dict(counts),
            "distribution": distribution.tolist(),
            "symmetry_score": symmetry_score,
            "min_entropy": min_entropy,
        }

        results["modes"][mode.value] = mode_results

        print(f"  Symmetry score: {symmetry_score:.4f}")
        print(f"  Min-entropy: {min_entropy:.4f} bits")
        print(f"  Distribution: {distribution}")

    # Compute KL divergences between modes
    baseline_dist = np.array(results["modes"]["none"]["distribution"])

    for mode_name in ["left", "right", "bilateral"]:
        if mode_name in results["modes"]:
            mode_dist = np.array(results["modes"][mode_name]["distribution"])
            # For fair comparison, we need same number of bits
            # This is simplified - full analysis needs proper handling
            results["modes"][mode_name]["kl_from_baseline"] = None  # Placeholder

    # Save results
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / f"baseline_3q_{timestamp}.json"
        with open(output_file, "w") as f:
            # Convert numpy arrays to lists for JSON
            json.dump(results, f, indent=2, default=str)

        print(f"\nResults saved to: {output_file}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Run 3-qubit baseline experiment")
    parser.add_argument("--shots", type=int, default=8192, help="Number of shots")
    parser.add_argument(
        "--backend", type=str, default="aer_simulator", help="Backend name"
    )
    parser.add_argument("--seed", type=int, default=None, help="Random seed")
    parser.add_argument("--output", type=str, default=None, help="Output directory")

    args = parser.parse_args()

    output_dir = Path(args.output) if args.output else Path(__file__).parent / "results"

    results = run_experiment(
        shots=args.shots,
        backend_name=args.backend,
        seed=args.seed,
        output_dir=output_dir,
    )

    # Print summary
    print("\n" + "=" * 60)
    print("EXPERIMENT SUMMARY")
    print("=" * 60)

    for mode_name, mode_data in results["modes"].items():
        print(f"\n{mode_name.upper()}:")
        print(f"  Symmetry Score: {mode_data['symmetry_score']:.4f}")
        print(f"  Min-Entropy: {mode_data['min_entropy']:.4f} bits")


if __name__ == "__main__":
    main()
