"""
Run Parity Witness Baseline Experiment

Execute PW-3Q circuit variants and collect baseline metrics.

Usage:
    python run_pw_baseline.py [--shots SHOTS] [--backend BACKEND]
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
from qiskit import transpile
from qiskit_aer import AerSimulator

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from circuits.security_topologies.parity_witness_3q import (
    CircuitVariant,
    InterceptionMode,
    PW3QConfig,
    create_pw_3q_circuit,
    create_pw_4q_circuit,
    get_circuit_info,
)


def compute_distribution(counts: dict, n_bits: int = 1) -> np.ndarray:
    """Convert counts to probability distribution."""
    total = sum(counts.values())
    n_outcomes = 2**n_bits

    distribution = np.zeros(n_outcomes)
    for bitstring, count in counts.items():
        if isinstance(bitstring, str):
            idx = int(bitstring, 2)
        else:
            idx = bitstring
        distribution[idx] = count / total

    return distribution


def compute_parity_distribution(counts: dict) -> np.ndarray:
    """
    Extract parity ancilla distribution from counts.

    For 3-qubit measurement, the ancilla is the last measured qubit.
    """
    total = sum(counts.values())
    p_parity_0 = 0.0
    p_parity_1 = 0.0

    for bitstring, count in counts.items():
        if isinstance(bitstring, str):
            # For 3 qubits, ancilla is the last bit (highest index)
            bits = bitstring.zfill(3)
            parity_bit = bits[2]  # Ancilla is q[2]
        else:
            parity_bit = "1" if (bitstring >> 2) & 1 else "0"

        if parity_bit == "0":
            p_parity_0 += count / total
        else:
            p_parity_1 += count / total

    return np.array([p_parity_0, p_parity_1])


def compute_joint_distribution(counts: dict) -> np.ndarray:
    """
    Extract joint distribution of data qubits (D0, D1).

    Returns 4-element array for [00, 01, 10, 11].

    Qiskit bitstring convention: for 3 qubits [q0, q1, q2], bitstring is q2q1q0
    - Rightmost bit (index -1 or 2) = q0 = D0
    - Middle bit (index 1) = q1 = D1
    - Leftmost bit (index 0) = q2 = A (ancilla)
    """
    total = sum(counts.values())
    joint = np.zeros(4)

    for bitstring, count in counts.items():
        if isinstance(bitstring, str):
            bits = bitstring.zfill(3)
            # D0 is q[0] (rightmost bit), D1 is q[1] (middle bit)
            d0 = int(bits[2])  # Rightmost bit
            d1 = int(bits[1])  # Middle bit
        else:
            d0 = bitstring & 1
            d1 = (bitstring >> 1) & 1

        idx = d1 * 2 + d0
        joint[idx] += count / total

    return joint


def kl_divergence(p: np.ndarray, q: np.ndarray, epsilon: float = 1e-10) -> float:
    """Compute KL divergence D_KL(p || q)."""
    p = np.clip(p, epsilon, 1.0)
    q = np.clip(q, epsilon, 1.0)
    return float(np.sum(p * np.log(p / q)))


def compute_mutual_information(joint_dist: np.ndarray) -> float:
    """
    Compute mutual information I(D0:D1) from joint distribution.

    I(D0:D1) = H(D0) + H(D1) - H(D0,D1)
    """
    # Marginals
    p_d0 = np.array([joint_dist[0] + joint_dist[2], joint_dist[1] + joint_dist[3]])
    p_d1 = np.array([joint_dist[0] + joint_dist[1], joint_dist[2] + joint_dist[3]])

    # Entropies
    def entropy(p):
        p = p[p > 0]
        return -np.sum(p * np.log2(p))

    h_d0 = entropy(p_d0)
    h_d1 = entropy(p_d1)
    h_joint = entropy(joint_dist)

    return h_d0 + h_d1 - h_joint


def compute_min_entropy(distribution: np.ndarray) -> float:
    """Compute min-entropy of distribution."""
    max_prob = np.max(distribution)
    return -np.log2(max_prob + 1e-10)


def run_experiment(
    shots: int = 8192,
    backend_name: str = "aer_simulator",
    seed: Optional[int] = None,
    variant: CircuitVariant = CircuitVariant.BASIC,
    output_dir: Optional[Path] = None,
) -> dict:
    """
    Run the complete parity witness baseline experiment.

    Args:
        shots: Number of shots per circuit
        backend_name: Simulator backend name
        seed: Random seed for reproducibility
        variant: Circuit variant to test
        output_dir: Directory to save results

    Returns:
        Dictionary with all results
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Initialize backend
    backend = AerSimulator()

    results = {
        "timestamp": timestamp,
        "shots": shots,
        "backend": backend_name,
        "seed": seed,
        "variant": variant.value,
        "modes": {},
    }

    # Run each interception mode
    for mode in InterceptionMode:
        print(f"\nRunning {mode.value} mode...")

        config = PW3QConfig(
            shots=shots,
            variant=variant,
            interception_mode=mode,
            measure_all=(mode != InterceptionMode.NONE),
        )
        circuit = create_pw_3q_circuit(config)

        # Transpile for backend
        transpiled = transpile(circuit, backend)

        # Run circuit
        job = backend.run(transpiled, shots=shots, seed_simulator=seed)
        counts = job.result().get_counts()

        # Compute metrics
        if mode == InterceptionMode.NONE:
            # Ancilla-only measurement
            parity_dist = compute_distribution(counts, n_bits=1)
            joint_dist = None
        else:
            # Full measurement for interception modes
            parity_dist = compute_parity_distribution(counts)
            joint_dist = compute_joint_distribution(counts)

        min_entropy = compute_min_entropy(parity_dist)

        mode_results = {
            "circuit_info": get_circuit_info(circuit),
            "counts": dict(counts),
            "parity_distribution": parity_dist.tolist(),
            "min_entropy": min_entropy,
        }

        if joint_dist is not None:
            mode_results["joint_distribution"] = joint_dist.tolist()
            mode_results["mutual_information"] = compute_mutual_information(joint_dist)

        results["modes"][mode.value] = mode_results

        print(f"  Parity distribution: {parity_dist}")
        print(f"  Min-entropy: {min_entropy:.4f} bits")
        if joint_dist is not None:
            print(
                f"  Mutual information: {mode_results['mutual_information']:.4f} bits"
            )

    # Compute KL divergences between modes
    baseline_parity = np.array(results["modes"]["none"]["parity_distribution"])

    for mode_name in ["d0", "d1", "both"]:
        if mode_name in results["modes"]:
            mode_parity = np.array(results["modes"][mode_name]["parity_distribution"])
            kl = kl_divergence(mode_parity, baseline_parity)
            results["modes"][mode_name]["parity_kl_from_baseline"] = kl
            print(f"  {mode_name} KL from baseline: {kl:.4f}")

    # Save results
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / f"pw_baseline_{variant.value}_{timestamp}.json"
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2, default=str)

        print(f"\nResults saved to: {output_file}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Run parity witness baseline experiment"
    )
    parser.add_argument("--shots", type=int, default=8192, help="Number of shots")
    parser.add_argument(
        "--backend", type=str, default="aer_simulator", help="Backend name"
    )
    parser.add_argument("--seed", type=int, default=None, help="Random seed")
    parser.add_argument(
        "--variant",
        type=str,
        default="basic",
        choices=["basic", "entangled", "coherence"],
        help="Circuit variant",
    )
    parser.add_argument("--output", type=str, default=None, help="Output directory")

    args = parser.parse_args()

    output_dir = Path(args.output) if args.output else Path(__file__).parent / "results"
    variant = CircuitVariant(args.variant)

    results = run_experiment(
        shots=args.shots,
        backend_name=args.backend,
        seed=args.seed,
        variant=variant,
        output_dir=output_dir,
    )

    # Print summary
    print("\n" + "=" * 60)
    print("EXPERIMENT SUMMARY")
    print("=" * 60)

    for mode_name, mode_data in results["modes"].items():
        print(f"\n{mode_name.upper()}:")
        print(f"  Parity Distribution: {mode_data['parity_distribution']}")
        print(f"  Min-Entropy: {mode_data['min_entropy']:.4f} bits")
        if "mutual_information" in mode_data:
            print(f"  Mutual Information: {mode_data['mutual_information']:.4f} bits")
        if "parity_kl_from_baseline" in mode_data:
            print(f"  KL from Baseline: {mode_data['parity_kl_from_baseline']:.4f}")


if __name__ == "__main__":
    main()
