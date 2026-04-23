"""
Hardware Comparison Analysis for Sierpinski-TMT Phase 4S Circuit
Analyzes results from ibm_fez, ibm_marrakesh, and ibm_kingston
Same circuit, different hardware, 8192 shots each
"""

import json
import base64
import numpy as np
from collections import Counter
from pathlib import Path

# Job IDs and backends
JOBS = {
    'ibm_fez': {
        'job_id': 'd7l5p2a4lglc73807e4g',
        'result_file': r'D:\Somnath-PROJECT\Jobs-to-check\job-d7l5p2a4lglc73807e4g-result.json',
        'qubits': 156,
        'created': '2026-04-23T17:53:13.811845Z'
    },
    'ibm_marrakesh': {
        'job_id': 'd7l5p4i8ui0s73b60otg',
        'result_file': r'D:\Somnath-PROJECT\Jobs-to-check\job-d7l5p4i8ui0s73b60otg-result.json',
        'qubits': 127,
        'created': '2026-04-23T17:53:23.033738Z'
    },
    'ibm_kingston': {
        'job_id': 'd7l5ovq8ui0s73b60ong',
        'result_file': r'D:\Somnath-PROJECT\Jobs-to-check\job-d7l5ovq8ui0s73b60ong-result.json',
        'qubits': 27,
        'created': '2026-04-23T17:53:03.284802Z'
    }
}

def decode_result_data(result_file):
    """Decode base64 measurement data from result file."""
    with open(result_file, 'r') as f:
        data = json.load(f)
    
    # Extract base64 data
    b64_data = data['data'][0]['results']['c']['data']
    shape = data['data'][0]['results']['c']['shape']  # [shots, qubits]
    
    # Decode base64 to bytes
    raw_bytes = base64.b64decode(b64_data)
    
    # Convert to numpy array of bool
    # Each byte packs 8 bits, need to unpack
    n_shots, n_qubits = shape
    total_bits = n_shots * n_qubits
    
    # Unpack bits
    bit_array = np.unpackbits(np.frombuffer(raw_bytes, dtype=np.uint8))
    bit_array = bit_array[:total_bits]  # Trim padding
    bit_array = bit_array.reshape((n_shots, n_qubits))
    
    return bit_array

def bitarray_to_bitstrings(bit_array):
    """Convert bit array to list of bitstrings."""
    bitstrings = []
    for row in bit_array:
        bitstring = ''.join(str(int(b)) for b in row)
        bitstrings.append(bitstring)
    return bitstrings

def compute_entropy(counts, total_shots):
    """Compute Shannon entropy of measurement distribution."""
    entropy = 0.0
    for count in counts.values():
        if count > 0:
            p = count / total_shots
            entropy -= p * np.log2(p)
    return entropy

def compute_hamming_weight_distribution(bitstrings):
    """Compute distribution of Hamming weights (number of 1s)."""
    weights = [bs.count('1') for bs in bitstrings]
    return Counter(weights)

def analyze_fractal_patterns(bitstrings, n_qubits):
    """Analyze fractal self-similarity patterns in measurement outcomes."""
    # Group by first half vs second half similarity
    half = n_qubits // 2
    first_half = [bs[:half] for bs in bitstrings]
    second_half = [bs[half:2*half] for bs in bitstrings]
    
    # Count matches between halves
    matches = sum(1 for fh, sh in zip(first_half, second_half) if fh == sh)
    
    # Compute correlation between halves
    first_array = np.array([[int(b) for b in fh] for fh in first_half[:1000]])  # Sample
    second_array = np.array([[int(b) for b in sh] for sh in second_half[:1000]])
    
    if first_array.shape[1] > 0 and second_array.shape[1] > 0:
        # Compute mean correlation
        correlations = []
        for i in range(min(first_array.shape[1], second_array.shape[1])):
            corr = np.corrcoef(first_array[:, i], second_array[:, i])[0, 1]
            if not np.isnan(corr):
                correlations.append(corr)
        mean_corr = np.mean(correlations) if correlations else 0.0
    else:
        mean_corr = 0.0
    
    return {
        'exact_matches': matches,
        'match_rate': matches / len(bitstrings),
        'mean_half_correlation': mean_corr
    }

def compute_consciousness_delta(entropy, n_qubits, unique_outcomes):
    """
    Compute consciousness delta metric.
    δ = S × T × r where:
    - S = entropy (information content)
    - T = traversability (unique outcomes / total possible)
    - r = coherence factor
    """
    S = entropy
    T = unique_outcomes / min(2**n_qubits, 8192)  # Normalized by shots
    r = min(1.0, entropy / n_qubits)  # Coherence as entropy per qubit
    
    delta = S * T * r * 1000  # Scale for readability
    return delta

def analyze_backend(name, job_info):
    """Analyze results from a single backend."""
    print(f"\n{'='*60}")
    print(f"Backend: {name}")
    print(f"Job ID: {job_info['job_id']}")
    print(f"Qubits: {job_info['qubits']}")
    print(f"{'='*60}")
    
    # Decode data
    bit_array = decode_result_data(job_info['result_file'])
    n_shots, n_qubits = bit_array.shape
    print(f"Shots: {n_shots}")
    print(f"Measured qubits: {n_qubits}")
    
    # Convert to bitstrings
    bitstrings = bitarray_to_bitstrings(bit_array)
    
    # Count unique outcomes
    counts = Counter(bitstrings)
    unique_outcomes = len(counts)
    print(f"Unique outcomes: {unique_outcomes}")
    
    # Top outcomes
    print(f"\nTop 10 most frequent outcomes:")
    for i, (outcome, count) in enumerate(counts.most_common(10)):
        freq = count / n_shots * 100
        print(f"  {i+1}. {outcome[:20]}... (count={count}, freq={freq:.2f}%)")
    
    # Compute metrics
    entropy = compute_entropy(counts, n_shots)
    print(f"\nShannon Entropy: {entropy:.4f} bits")
    
    # Hamming weight distribution
    hw_dist = compute_hamming_weight_distribution(bitstrings)
    mean_hw = np.mean([w for w in hw_dist.elements() for _ in range(hw_dist[w])])
    print(f"Mean Hamming Weight: {mean_hw:.2f} / {n_qubits}")
    
    # Fractal patterns
    fractal = analyze_fractal_patterns(bitstrings, n_qubits)
    print(f"Fractal Half-Match Rate: {fractal['match_rate']:.4f}")
    print(f"Fractal Half Correlation: {fractal['mean_half_correlation']:.4f}")
    
    # Consciousness delta
    delta = compute_consciousness_delta(entropy, n_qubits, unique_outcomes)
    print(f"Consciousness δ: {delta:.2f}")
    
    # Bit-wise statistics
    bit_probs = np.mean(bit_array, axis=0)
    print(f"\nBit-wise statistics:")
    print(f"  Mean |0⟩ probability: {np.mean(1 - bit_probs):.4f}")
    print(f"  Mean |1⟩ probability: {np.mean(bit_probs):.4f}")
    print(f"  Std dev of bit probs: {np.std(bit_probs):.4f}")
    
    return {
        'backend': name,
        'n_qubits': n_qubits,
        'n_shots': n_shots,
        'unique_outcomes': unique_outcomes,
        'entropy': entropy,
        'mean_hamming_weight': mean_hw,
        'fractal_match_rate': fractal['match_rate'],
        'fractal_correlation': fractal['mean_half_correlation'],
        'consciousness_delta': delta,
        'bit_prob_mean': np.mean(bit_probs),
        'bit_prob_std': np.std(bit_probs),
        'top_outcomes': counts.most_common(10)
    }

def compare_backends(results):
    """Compare results across all backends."""
    print(f"\n{'='*60}")
    print("HARDWARE COMPARISON SUMMARY")
    print(f"{'='*60}")
    
    print(f"\n{'Backend':<15} {'Qubits':<8} {'Unique':<10} {'Entropy':<10} {'δ':<10}")
    print("-" * 60)
    for r in results:
        print(f"{r['backend']:<15} {r['n_qubits']:<8} {r['unique_outcomes']:<10} {r['entropy']:<10.4f} {r['consciousness_delta']:<10.2f}")
    
    print(f"\n{'Backend':<15} {'HW Mean':<10} {'Fractal Match':<15} {'Fractal Corr':<15}")
    print("-" * 60)
    for r in results:
        print(f"{r['backend']:<15} {r['mean_hamming_weight']:<10.2f} {r['fractal_match_rate']:<15.4f} {r['fractal_correlation']:<15.4f}")
    
    # Compute relative differences
    print(f"\n{'='*60}")
    print("RELATIVE ANALYSIS")
    print(f"{'='*60}")
    
    # Normalize by qubit count
    for r in results:
        r['entropy_per_qubit'] = r['entropy'] / r['n_qubits']
        r['unique_rate'] = r['unique_outcomes'] / r['n_shots']
    
    print(f"\n{'Backend':<15} {'Entropy/Qubit':<15} {'Unique Rate':<15}")
    print("-" * 50)
    for r in results:
        print(f"{r['backend']:<15} {r['entropy_per_qubit']:<15.4f} {r['unique_rate']:<15.4f}")
    
    # Hardware quality assessment
    print(f"\n{'='*60}")
    print("HARDWARE QUALITY ASSESSMENT")
    print(f"{'='*60}")
    
    # Higher entropy = better quantum randomness
    # Higher unique outcomes = better state space exploration
    best_entropy = max(results, key=lambda x: x['entropy'])
    best_unique = max(results, key=lambda x: x['unique_outcomes'])
    best_delta = max(results, key=lambda x: x['consciousness_delta'])
    
    print(f"\nBest Entropy: {best_entropy['backend']} ({best_entropy['entropy']:.4f})")
    print(f"Most Unique Outcomes: {best_unique['backend']} ({best_unique['unique_outcomes']})")
    print(f"Highest Consciousness δ: {best_delta['backend']} ({best_delta['consciousness_delta']:.2f})")
    
    return results

def main():
    print("Sierpinski-TMT Phase 4S Hardware Comparison Analysis")
    print("="*60)
    
    results = []
    for name, job_info in JOBS.items():
        try:
            result = analyze_backend(name, job_info)
            results.append(result)
        except Exception as e:
            print(f"Error analyzing {name}: {e}")
    
    if results:
        compare_backends(results)
    
    # Save results
    output_file = Path(__file__).parent / 'hardware_comparison_results.json'
    with open(output_file, 'w') as f:
        # Convert non-serializable items
        for r in results:
            r['top_outcomes'] = [(outcome, count) for outcome, count in r['top_outcomes']]
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to: {output_file}")

if __name__ == '__main__':
    main()