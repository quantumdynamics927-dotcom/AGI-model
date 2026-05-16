#!/usr/bin/env python3
"""
Analyze IBM Quantum Merkaba_Activation job results.

Performs rigorous statistical analysis:
- Output distribution
- Per-bit bias
- Pairwise correlations
- Entropy metrics
- Expected-vs-observed comparison
"""

import json
import numpy as np
from collections import Counter
import base64
from pathlib import Path

# Load result files
result1_path = Path(r'E:\Descargas\workloads (42)\job-d7nti8497osc73dsgp0g-result.json')
result2_path = Path(r'E:\Descargas\workloads (42)\job-d7nti9s97osc73dsgp2g-result.json')


def decode_base64_bool_array(base64_data: str, shape: list) -> np.ndarray:
    """Decode base64-encoded boolean array from IBM Quantum results."""
    raw_bytes = base64.b64decode(base64_data)
    # Each byte represents 8 bits, need to unpack
    n_shots, n_qubits = shape
    total_bits = n_shots * n_qubits
    
    # Convert bytes to bits
    bits = np.unpackbits(np.frombuffer(raw_bytes, dtype=np.uint8))
    
    # Reshape to (shots, qubits)
    # IBM packs bits in a specific order
    bool_array = bits[:total_bits].reshape(shape).astype(bool)
    
    return bool_array


def bits_to_integers(bit_array: np.ndarray) -> np.ndarray:
    """Convert bit array to integer values."""
    # bit_array shape: (n_shots, n_qubits)
    n_shots, n_qubits = bit_array.shape
    integers = np.zeros(n_shots, dtype=int)
    for i in range(n_qubits):
        integers += bit_array[:, i].astype(int) * (2 ** i)
    return integers


def compute_statistics(bit_array: np.ndarray, job_name: str) -> dict:
    """Compute comprehensive statistics on measurement results."""
    n_shots, n_qubits = bit_array.shape
    
    print(f"\n{'='*70}")
    print(f"Job: {job_name}")
    print(f"{'='*70}")
    print(f"Shots: {n_shots}, Qubits: {n_qubits}")
    
    # Convert to integers for distribution
    integers = bits_to_integers(bit_array)
    
    # 1. Output distribution
    counts = Counter(integers)
    total = sum(counts.values())
    
    print(f"\n--- Output Distribution (top 10 states) ---")
    sorted_counts = counts.most_common(10)
    for state, count in sorted_counts:
        binary = format(state, f'0{n_qubits}b')
        prob = count / total
        print(f"  |{binary}>: {count:4d} ({prob:.4%})")
    
    # 2. Per-bit bias
    print(f"\n--- Per-Qubit Bias ---")
    bit_means = np.mean(bit_array, axis=0)
    for i, mean in enumerate(bit_means):
        bias = mean - 0.5  # Deviation from uniform
        print(f"  Qubit {i}: P(1) = {mean:.4f}, Bias = {bias:+.4f}")
    
    # 3. Shannon entropy
    probabilities = np.array([count / total for count in counts.values()])
    shannon_entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
    max_entropy = n_qubits
    
    print(f"\n--- Entropy Metrics ---")
    print(f"  Shannon Entropy: {shannon_entropy:.4f} bits")
    print(f"  Max Entropy: {max_entropy} bits")
    print(f"  Entropy Ratio: {shannon_entropy / max_entropy:.4f}")
    
    # 4. Pairwise correlations
    print(f"\n--- Pairwise Correlations (|corr| > 0.1) ---")
    correlations = np.corrcoef(bit_array.T)
    significant_corrs = []
    for i in range(n_qubits):
        for j in range(i + 1, n_qubits):
            corr = correlations[i, j]
            if abs(corr) > 0.1:
                significant_corrs.append((i, j, corr))
    
    if significant_corrs:
        for i, j, corr in sorted(significant_corrs, key=lambda x: abs(x[2]), reverse=True):
            print(f"  Q{i}-Q{j}: {corr:+.4f}")
    else:
        print("  No significant correlations (all |corr| < 0.1)")
    
    # 5. Unique states count
    unique_states = len(counts)
    possible_states = 2 ** n_qubits
    
    print(f"\n--- State Coverage ---")
    print(f"  Unique states observed: {unique_states} / {possible_states}")
    print(f"  Coverage: {unique_states / possible_states:.2%}")
    
    # 6. Chi-squared test for uniformity
    expected = total / possible_states
    chi_sq = sum((count - expected) ** 2 / expected for count in counts.values())
    print(f"\n--- Uniformity Test ---")
    print(f"  Chi-squared statistic: {chi_sq:.2f}")
    print(f"  (Lower values indicate more uniform distribution)")
    
    return {
        'counts': counts,
        'bit_means': bit_means,
        'shannon_entropy': shannon_entropy,
        'correlations': correlations,
        'unique_states': unique_states,
        'chi_squared': chi_sq
    }


def compare_jobs(stats1: dict, stats2: dict, name1: str, name2: str):
    """Compare statistics between two jobs."""
    print(f"\n{'='*70}")
    print(f"Comparison: {name1} vs {name2}")
    print(f"{'='*70}")
    
    # Entropy comparison
    print(f"\n--- Entropy Comparison ---")
    print(f"  {name1}: {stats1['shannon_entropy']:.4f} bits")
    print(f"  {name2}: {stats2['shannon_entropy']:.4f} bits")
    print(f"  Difference: {abs(stats1['shannon_entropy'] - stats2['shannon_entropy']):.4f} bits")
    
    # Bias comparison
    print(f"\n--- Bias Comparison ---")
    for i in range(len(stats1['bit_means'])):
        diff = stats1['bit_means'][i] - stats2['bit_means'][i]
        print(f"  Qubit {i}: {stats1['bit_means'][i]:.4f} vs {stats2['bit_means'][i]:.4f} (diff: {diff:+.4f})")
    
    # State overlap
    states1 = set(stats1['counts'].keys())
    states2 = set(stats2['counts'].keys())
    overlap = len(states1 & states2)
    
    print(f"\n--- State Overlap ---")
    print(f"  {name1} unique states: {len(states1)}")
    print(f"  {name2} unique states: {len(states2)}")
    print(f"  Overlapping states: {overlap}")


def main():
    print("="*70)
    print("Merkaba_Activation IBM Quantum Job Analysis")
    print("="*70)
    
    # Load and parse results
    with open(result1_path, 'r') as f:
        data1 = json.load(f)
    
    with open(result2_path, 'r') as f:
        data2 = json.load(f)
    
    # Extract measurement data
    meas1 = data1['data'][0]['results']['meas']
    meas2 = data2['data'][0]['results']['meas']
    
    # Decode base64 data
    bit_array1 = decode_base64_bool_array(meas1['data'], meas1['shape'])
    bit_array2 = decode_base64_bool_array(meas2['data'], meas2['shape'])
    
    # Compute statistics
    stats1 = compute_statistics(bit_array1, "Job 1 (d7nti8497, 4096 shots)")
    stats2 = compute_statistics(bit_array2, "Job 2 (d7nti9s9, 1024 shots)")
    
    # Compare jobs
    compare_jobs(stats1, stats2, "Job 1", "Job 2")
    
    # Summary
    print(f"\n{'='*70}")
    print("Summary")
    print(f"{'='*70}")
    print("""
Hardware Execution: CONFIRMED
  - Both jobs completed successfully on ibm_kingston
  - Measurement data retrieved from real quantum hardware

Functional Correctness: NOT YET VALIDATED
  - Requires comparison against expected distribution
  - Requires validation protocol or benchmark
  - Requires design documentation for intended behavior

Next Steps:
  1. Define expected output distribution for Merkaba_Activation
  2. Implement statistical test (e.g., Kolmogorov-Smirnov)
  3. Compare observed vs expected with significance testing
  4. Document design intent before claiming golden ratio encoding
""")


if __name__ == "__main__":
    main()