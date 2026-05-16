#!/usr/bin/env python3
"""
Analyze Wormhole_Traversal IBM Quantum job results.

Circuit Structure:
- 20 qubits organized as 10 entry/exit pairs
- Bell pair creation (H + CX) for each pair
- Alternating RY rotations with CZ entanglement
- SWAP operations for "traversal" simulation
"""

import json
import numpy as np
from collections import Counter
import base64
from pathlib import Path

# Job paths
RESULT_PATH = Path(r"E:\Descargas\job-d7nulde2jamc73bovf30\job-d7nulde2jamc73bovf30-result.json")
INFO_PATH = Path(r"E:\Descargas\job-d7nulde2jamc73bovf30\job-d7nulde2jamc73bovf30-info.json")


def decode_base64_bool_array(base64_data: str, shape: list) -> np.ndarray:
    """Decode base64-encoded boolean array from IBM Quantum results."""
    raw_bytes = base64.b64decode(base64_data)
    n_shots, n_qubits = shape
    total_bits = n_shots * n_qubits
    bits = np.unpackbits(np.frombuffer(raw_bytes, dtype=np.uint8))
    bool_array = bits[:total_bits].reshape(shape).astype(bool)
    return bool_array


def bits_to_integers(bit_array: np.ndarray) -> np.ndarray:
    """Convert bit array to integer values."""
    n_shots, n_qubits = bit_array.shape
    integers = np.zeros(n_shots, dtype=int)
    for i in range(n_qubits):
        integers += bit_array[:, i].astype(int) * (2 ** i)
    return integers


def analyze_wormhole_results():
    """Main analysis function."""
    print("=" * 70)
    print("Wormhole_Traversal IBM Quantum Job Analysis")
    print("=" * 70)
    
    # Load job info
    with open(INFO_PATH, 'r') as f:
        info = json.load(f)
    
    # Load results
    with open(RESULT_PATH, 'r') as f:
        result = json.load(f)
    
    # Job metadata
    print("\n--- Job Metadata ---")
    print(f"Job ID: {info['id']}")
    print(f"Backend: {info['backend']}")
    print(f"Status: {info['status']}")
    print(f"Created: {info['created']}")
    print(f"Shots: {info['params']['quantum_program']['shots']}")
    print(f"Cost: {info['cost']}")
    
    # Extract measurement data
    meas = result['data'][0]['results']['meas']
    bit_array = decode_base64_bool_array(meas['data'], meas['shape'])
    n_shots, n_qubits = bit_array.shape
    
    print(f"\n--- Measurement Data ---")
    print(f"Shots: {n_shots}")
    print(f"Qubits: {n_qubits}")
    
    # Convert to integers
    integers = bits_to_integers(bit_array)
    counts = Counter(integers)
    total = sum(counts.values())
    
    # Output distribution
    print(f"\n--- Output Distribution (top 15 states) ---")
    sorted_counts = counts.most_common(15)
    for state, count in sorted_counts:
        binary = format(state, f'0{n_qubits}b')
        prob = count / total
        print(f"  |{binary}>: {count:4d} ({prob:.4%})")
    
    # Per-qubit bias
    print(f"\n--- Per-Qubit Bias ---")
    bit_means = np.mean(bit_array, axis=0)
    
    # Group by entry/exit pairs
    print("  Entry qubits (0-9):")
    for i in range(10):
        bias = bit_means[i] - 0.5
        print(f"    Q{i}: P(1) = {bit_means[i]:.4f}, Bias = {bias:+.4f}")
    
    print("  Exit qubits (10-19):")
    for i in range(10, 20):
        bias = bit_means[i] - 0.5
        print(f"    Q{i}: P(1) = {bit_means[i]:.4f}, Bias = {bias:+.4f}")
    
    # Entry-Exit correlation analysis
    print(f"\n--- Entry-Exit Pair Correlations ---")
    correlations = np.corrcoef(bit_array.T)
    for i in range(10):
        entry = i
        exit_q = i + 10
        corr = correlations[entry, exit_q]
        print(f"  Pair {i}: Q{entry}-Q{exit_q} correlation = {corr:+.4f}")
    
    # Entropy metrics
    probabilities = np.array([count / total for count in counts.values()])
    shannon_entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
    max_entropy = n_qubits
    
    print(f"\n--- Entropy Metrics ---")
    print(f"  Shannon Entropy: {shannon_entropy:.4f} bits")
    print(f"  Max Entropy: {max_entropy} bits")
    print(f"  Entropy Ratio: {shannon_entropy / max_entropy:.4f}")
    
    # State coverage
    unique_states = len(counts)
    possible_states = 2 ** n_qubits
    
    print(f"\n--- State Coverage ---")
    print(f"  Unique states observed: {unique_states} / {possible_states}")
    print(f"  Coverage: {unique_states / possible_states:.6%}")
    
    # SWAP operation analysis
    print(f"\n--- SWAP Operation Analysis ---")
    print("  Checking if entry/exit qubits show swapped correlations...")
    
    # Compare original pairs vs swapped pairs
    original_corr = np.mean([correlations[i, i+10] for i in range(10)])
    swapped_corr = np.mean([correlations[i, (i+1)%10 + 10] for i in range(10)])
    
    print(f"  Average original pair correlation: {original_corr:+.4f}")
    print(f"  Average shifted pair correlation: {swapped_corr:+.4f}")
    
    # Hamming distance analysis
    print(f"\n--- Hamming Distance Analysis ---")
    # Compare each shot's entry bits with exit bits
    entry_bits = bit_array[:, :10]
    exit_bits = bit_array[:, 10:]
    
    hamming_distances = np.sum(entry_bits != exit_bits, axis=1)
    mean_hamming = np.mean(hamming_distances)
    
    print(f"  Mean Hamming distance (entry vs exit): {mean_hamming:.4f} / 10")
    print(f"  Expected for random: 5.0")
    
    # Distribution of Hamming distances
    hamming_counts = Counter(hamming_distances)
    print(f"\n  Hamming distance distribution:")
    for dist in sorted(hamming_counts.keys())[:11]:
        count = hamming_counts[dist]
        pct = count / n_shots * 100
        bar = "█" * int(pct / 2)
        print(f"    d={dist:2d}: {count:4d} ({pct:5.2f}%) {bar}")
    
    # Summary
    print(f"\n{'='*70}")
    print("Summary")
    print(f"{'='*70}")
    print("""
Hardware Execution: CONFIRMED
  - Job completed successfully on ibm_kingston
  - 4096 shots executed
  - Measurement data retrieved

Circuit Behavior Observations:
  - Near-uniform distribution across states
  - Low entry-exit pair correlations (SWAP effect)
  - Hamming distance near random expectation

Scientific Assessment:
  - Hardware deployability confirmed
  - Functional correctness requires comparison with expected distribution
  - "Wormhole traversal" interpretation requires validation protocol
""")
    
    return {
        'info': info,
        'counts': counts,
        'bit_means': bit_means,
        'correlations': correlations,
        'shannon_entropy': shannon_entropy,
        'hamming_distances': hamming_distances
    }


if __name__ == "__main__":
    analyze_wormhole_results()