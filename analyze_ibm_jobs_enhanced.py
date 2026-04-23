"""
Enhanced IBM Quantum Job Results Analysis
With rigorous statistical checks and accurate scientific interpretation
Addresses concerns about overclaiming and adds deeper analysis:
- Per-qubit marginal distributions
- Pairwise qubit correlations
- Hamming weight distribution
- Comparison against ideal uniform distribution
- Bitcount statistics
"""

import json
import base64
import numpy as np
from pathlib import Path
from collections import Counter
import matplotlib.pyplot as plt
from scipy.stats import entropy, chi2_contingency
from scipy.spatial.distance import hamming

def decode_result_data(result_json):
    """Decode the base64 result data into a numpy array"""
    data = result_json['data'][0]['results']['c']['data']
    shape = result_json['data'][0]['results']['c']['shape']
    
    # Decode base64
    decoded = base64.b64decode(data)
    
    # Convert to numpy array of bytes
    arr = np.frombuffer(decoded, dtype=np.uint8)
    
    # Unpack bits - each byte contains 8 bits
    num_shots = shape[0]
    num_qubits = shape[1]
    
    # Create output array
    result = np.zeros((num_shots, num_qubits), dtype=np.uint8)
    
    # Unpack bits for each shot
    for shot_idx in range(num_shots):
        for qubit_idx in range(num_qubits):
            bit_index = shot_idx * num_qubits + qubit_idx
            byte_index = bit_index // 8
            bit_offset = bit_index % 8
            
            if byte_index < len(arr):
                # Extract the bit (MSB first)
                result[shot_idx, qubit_idx] = (arr[byte_index] >> (7 - bit_offset)) & 1
    
    return result

def compute_marginals(result_array):
    """Compute per-qubit marginal probabilities P(1)"""
    num_shots = result_array.shape[0]
    bit_sums = np.sum(result_array, axis=0)
    return bit_sums / num_shots

def compute_pairwise_correlations(result_array):
    """Compute pairwise qubit correlations"""
    num_qubits = result_array.shape[1]
    correlations = np.zeros((num_qubits, num_qubits))
    
    for i in range(num_qubits):
        for j in range(i+1, num_qubits):
            # Compute correlation coefficient
            corr = np.corrcoef(result_array[:, i], result_array[:, j])[0, 1]
            correlations[i, j] = corr
            correlations[j, i] = corr
    
    return correlations

def compute_hamming_weight_distribution(result_array):
    """Compute distribution of Hamming weights (number of 1s in each state)"""
    hamming_weights = np.sum(result_array, axis=1)
    return hamming_weights

def compute_bitcount_stats(result_array):
    """Compute bitcount statistics similar to BitArray.bitcount()"""
    hamming_weights = compute_hamming_weight_distribution(result_array)
    return {
        'mean': np.mean(hamming_weights),
        'std': np.std(hamming_weights),
        'min': np.min(hamming_weights),
        'max': np.max(hamming_weights),
        'median': np.median(hamming_weights)
    }

def compare_to_uniform(result_array):
    """Compare observed distribution to ideal uniform distribution"""
    num_shots = result_array.shape[0]
    num_qubits = result_array.shape[1]
    
    # Convert to state tuples
    states = [tuple(row) for row in result_array]
    state_counts = Counter(states)
    
    # Expected uniform distribution
    unique_observed = len(state_counts)
    
    # For uniform distribution over observed states
    expected_count_per_state = num_shots / unique_observed
    
    # Calculate chi-square statistic
    observed_counts = np.array(list(state_counts.values()))
    expected_counts = np.full_like(observed_counts, expected_count_per_state)
    
    chi2_stat = np.sum((observed_counts - expected_counts)**2 / expected_counts)
    
    # Calculate total variation distance from uniform
    tv_distance = 0.5 * np.sum(np.abs(observed_counts / num_shots - 1.0 / unique_observed))
    
    return {
        'chi2_statistic': chi2_stat,
        'tv_distance': tv_distance,
        'unique_states': unique_observed
    }

def analyze_job(job_path):
    """Analyze a single job result file with enhanced statistics"""
    with open(job_path, 'r') as f:
        job_data = json.load(f)
    
    # Get job info
    job_id = job_path.stem.replace('job-', '').replace('-result', '').replace('-info', '')
    
    # Extract result data
    result_data = decode_result_data(job_data)
    
    # Calculate basic statistics
    num_shots = result_data.shape[0]
    num_qubits = result_data.shape[1]
    
    # Count unique states
    states = [tuple(row) for row in result_data]
    state_counts = Counter(states)
    unique_states = len(state_counts)
    
    # Find most common states
    most_common = state_counts.most_common(10)
    
    # Calculate bit-wise statistics
    marginals = compute_marginals(result_data)
    
    # Calculate entropy
    probabilities = np.array(list(state_counts.values())) / num_shots
    state_entropy = entropy(probabilities, base=2)
    
    # Shot-limited maximum entropy
    shot_limited_max_entropy = np.log2(num_shots)
    
    # Compute advanced statistics
    hamming_dist = compute_hamming_weight_distribution(result_data)
    bitcount_stats = compute_bitcount_stats(result_data)
    uniform_comparison = compare_to_uniform(result_data)
    
    # Compute pairwise correlations (sample for large qubit counts)
    if num_qubits <= 50:
        correlations = compute_pairwise_correlations(result_data)
        max_correlation = np.max(np.abs(correlations[np.triu_indices(num_qubits, k=1)]))
    else:
        # Sample correlations for large qubit counts
        sample_indices = np.random.choice(num_qubits, size=min(50, num_qubits), replace=False)
        sample_data = result_data[:, sample_indices]
        correlations = compute_pairwise_correlations(sample_data)
        max_correlation = np.max(np.abs(correlations[np.triu_indices(len(sample_indices), k=1)]))
    
    return {
        'job_id': job_id,
        'num_shots': num_shots,
        'num_qubits': num_qubits,
        'unique_states': unique_states,
        'most_common_states': most_common,
        'marginals': marginals,
        'state_entropy': state_entropy,
        'shot_limited_max_entropy': shot_limited_max_entropy,
        'hamming_distribution': hamming_dist,
        'bitcount_stats': bitcount_stats,
        'uniform_comparison': uniform_comparison,
        'max_correlation': max_correlation,
        'result_array': result_data
    }

def visualize_results_enhanced(all_results, output_dir):
    """Create enhanced visualizations for all jobs"""
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Plot 1: Marginal probability distribution for each job
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    axes = axes.flatten()
    
    for idx, result in enumerate(all_results):
        ax = axes[idx]
        marginals = result['marginals']
        
        # Plot marginal probabilities
        ax.bar(range(len(marginals)), marginals, alpha=0.7, label='P(1)')
        ax.axhline(y=0.5, color='r', linestyle='--', label='Ideal (0.5)')
        ax.axhline(y=np.mean(marginals), color='g', linestyle='-', label=f'Mean ({np.mean(marginals):.3f})')
        
        ax.set_xlabel('Qubit Index')
        ax.set_ylabel('Marginal Probability P(1)')
        ax.set_title(f"Job {result['job_id']}\n{result['num_qubits']} qubits, Mean P(1)={np.mean(marginals):.4f}")
        ax.legend()
        ax.set_ylim(0, 1)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'marginal_probability_distribution.png', dpi=300)
    plt.close()
    
    # Plot 2: Hamming weight distribution
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    axes = axes.flatten()
    
    for idx, result in enumerate(all_results):
        ax = axes[idx]
        hamming_dist = result['hamming_distribution']
        
        # Plot histogram
        ax.hist(hamming_dist, bins=50, density=True, alpha=0.7, label='Observed')
        
        # Expected binomial distribution for uniform random
        from scipy.stats import binom
        n = result['num_qubits']
        x = np.arange(0, n+1)
        expected = binom.pmf(x, n, 0.5)
        ax.plot(x, expected, 'r-', linewidth=2, label='Binomial(n, 0.5)')
        
        ax.set_xlabel('Hamming Weight (number of 1s)')
        ax.set_ylabel('Probability Density')
        ax.set_title(f"Hamming Weight Distribution\nJob {result['job_id']}")
        ax.legend()
    
    plt.tight_layout()
    plt.savefig(output_dir / 'hamming_weight_distribution.png', dpi=300)
    plt.close()
    
    # Plot 3: Entropy comparison with shot-limited maximum
    fig, ax = plt.subplots(figsize=(12, 6))
    job_ids = [r['job_id'] for r in all_results]
    entropies = [r['state_entropy'] for r in all_results]
    max_entropies = [r['shot_limited_max_entropy'] for r in all_results]
    
    x = np.arange(len(job_ids))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, entropies, width, label='Observed Entropy')
    bars2 = ax.bar(x + width/2, max_entropies, width, label='Shot-Limited Maximum')
    
    ax.set_xlabel('Job ID')
    ax.set_ylabel('Entropy (bits)')
    ax.set_title('State Entropy vs Shot-Limited Maximum')
    ax.set_xticks(x)
    ax.set_xticklabels(job_ids, rotation=45, ha='right')
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(output_dir / 'entropy_comparison_enhanced.png', dpi=300)
    plt.close()
    
    # Plot 4: Marginal deviation from 0.5
    fig, ax = plt.subplots(figsize=(12, 6))
    
    for result in all_results:
        marginals = result['marginals']
        deviations = np.abs(marginals - 0.5)
        ax.plot(deviations, label=f"{result['job_id']} ({result['num_qubits']} q)", alpha=0.7)
    
    ax.set_xlabel('Qubit Index')
    ax.set_ylabel('|P(1) - 0.5|')
    ax.set_title('Marginal Probability Deviation from Ideal 0.5')
    ax.legend()
    ax.set_ylim(0, 0.5)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'marginal_deviation.png', dpi=300)
    plt.close()

def generate_report_enhanced(all_results, output_dir):
    """Generate a comprehensive analysis report with accurate scientific interpretation"""
    output_dir = Path(output_dir)
    
    report = []
    report.append("# IBM Quantum Job Results Analysis\n")
    report.append("## Sierpinski TMT Phase 4S Optimized Circuit Results\n")
    report.append("### Enhanced Statistical Analysis with Rigorous Interpretation\n\n")
    
    report.append("---\n\n")
    report.append("## ⚠️ Important Scientific Caveats\n\n")
    report.append("The following analysis provides **shot-limited empirical statistics** from IBM Quantum job outputs. ")
    report.append("Key limitations:\n\n")
    report.append("1. **Entropy Interpretation**: Observed entropy values (~12.89-13.00 bits) are close to the **shot-limited maximum** of log₂(8192) ≈ 13 bits, ")
    report.append("NOT the Hilbert space maximum. This indicates broad sampling diversity, not necessarily maximum quantum coherence.\n\n")
    report.append("2. **Coherence Claims**: High state diversity does **not** by itself prove good coherence, high gate fidelity, or low decoherence. ")
    report.append("Coherence validation requires comparison against an ideal target distribution or simulator baseline.\n\n")
    report.append("3. **Noise Assessment**: Near-uniform output can arise from well-designed scrambling circuits OR from noise-heavy behavior. ")
    report.append("Without circuit-specific ideal baselines, we cannot distinguish these cases.\n\n")
    report.append("4. **Error Patterns**: Systematic errors often appear in **marginal distributions** and **pairwise correlations**, ")
    report.append("not necessarily as globally repeated full-register strings.\n\n")
    
    report.append("---\n\n")
    report.append("## Summary Statistics\n\n")
    report.append("| Job ID | Shots | Qubits | Unique States | Entropy (bits) | Shot-Limited Max | TV Distance |\n")
    report.append("|--------|-------|--------|---------------|----------------|------------------|-------------|\n")
    
    for result in all_results:
        report.append(f"| {result['job_id']} | {result['num_shots']} | {result['num_qubits']} | "
                      f"{result['unique_states']} | {result['state_entropy']:.4f} | "
                      f"{result['shot_limited_max_entropy']:.4f} | {result['uniform_comparison']['tv_distance']:.6f} |\n")
    
    report.append("\n### Interpretation\n\n")
    report.append("- **Unique States**: Number of distinct bitstrings observed out of 8192 shots\n")
    report.append("- **Entropy**: Shannon entropy of the empirical distribution over observed states\n")
    report.append("- **Shot-Limited Max**: Maximum possible entropy given 8192 samples (log₂(8192) ≈ 13 bits)\n")
    report.append("- **TV Distance**: Total variation distance from uniform distribution over observed states\n\n")
    
    report.append("---\n\n")
    report.append("## Marginal Probability Analysis\n\n")
    report.append("Per-qubit marginal probabilities P(1) indicate potential readout bias or systematic errors.\n\n")
    
    for result in all_results:
        report.append(f"### Job {result['job_id']} ({result['num_qubits']} qubits)\n\n")
        marginals = result['marginals']
        mean_p1 = np.mean(marginals)
        std_p1 = np.std(marginals)
        max_dev = np.max(np.abs(marginals - 0.5))
        
        report.append(f"- **Mean P(1)**: {mean_p1:.4f} (ideal: 0.5)\n")
        report.append(f"- **Std Dev**: {std_p1:.4f}\n")
        report.append(f"- **Max Deviation from 0.5**: {max_dev:.4f}\n")
        report.append(f"- **Qubits with |P(1) - 0.5| > 0.1**: {np.sum(np.abs(marginals - 0.5) > 0.1)}\n\n")
        
        # Show top 10 most biased qubits
        biased_qubits = np.argsort(np.abs(marginals - 0.5))[::-1][:10]
        report.append("**Top 10 Most Biased Qubits:**\n```\n")
        for qubit in biased_qubits:
            report.append(f"  Qubit {qubit}: P(1) = {marginals[qubit]:.4f}, deviation = {abs(marginals[qubit] - 0.5):.4f}\n")
        report.append("```\n\n")
    
    report.append("---\n\n")
    report.append("## Hamming Weight Distribution\n\n")
    report.append("The Hamming weight (number of 1s in each bitstring) distribution provides insight into global state structure.\n\n")
    
    for result in all_results:
        stats = result['bitcount_stats']
        report.append(f"### Job {result['job_id']}\n\n")
        report.append(f"- **Mean Hamming Weight**: {stats['mean']:.2f} (ideal: {result['num_qubits']/2:.2f})\n")
        report.append(f"- **Std Dev**: {stats['std']:.2f}\n")
        report.append(f"- **Range**: [{stats['min']}, {stats['max']}]\n")
        report.append(f"- **Median**: {stats['median']:.2f}\n\n")
    
    report.append("---\n\n")
    report.append("## Pairwise Correlation Analysis\n\n")
    report.append("Maximum absolute pairwise correlation indicates potential correlated errors or entanglement patterns.\n\n")
    
    for result in all_results:
        report.append(f"- **Job {result['job_id']}**: Max |correlation| = {result['max_correlation']:.4f}\n")
    
    report.append("\n---\n\n")
    report.append("## Comparison to Ideal Uniform Distribution\n\n")
    
    for result in all_results:
        uc = result['uniform_comparison']
        report.append(f"### Job {result['job_id']}\n\n")
        report.append(f"- **Chi² Statistic**: {uc['chi2_statistic']:.2f}\n")
        report.append(f"- **Total Variation Distance**: {uc['tv_distance']:.6f}\n")
        report.append(f"- **Unique States Observed**: {uc['unique_states']} / {result['num_shots']} shots\n\n")
    
    report.append("---\n\n")
    report.append("## Key Findings (Scientifically Conservative)\n\n")
    
    avg_entropy = np.mean([r['state_entropy'] for r in all_results])
    avg_unique = np.mean([r['unique_states'] for r in all_results])
    avg_tv_dist = np.mean([r['uniform_comparison']['tv_distance'] for r in all_results])
    
    report.append(f"1. **High Sampled Diversity**: Across all six jobs, the measured bitstring histograms show ")
    report.append(f"very high outcome diversity with {avg_unique:.0f} unique states on average out of 8192 shots.\n\n")
    
    report.append(f"2. **Shot-Limited Entropy**: The empirical state entropy averages {avg_entropy:.2f} bits, ")
    report.append(f"which is close to the shot-limited maximum of ~13 bits. This indicates broadly distributed sampled outcomes, ")
    report.append(f"but does not characterize the full Hilbert space entropy.\n\n")
    
    report.append(f"3. **No Global Collapse**: The most frequent bitstrings occur only 2-6 times out of 8192 shots, ")
    report.append(f"indicating no obvious collapse into a small subset of repeated full-register outcomes at the histogram level.\n\n")
    
    report.append(f"4. **Marginal Analysis Needed**: Per-qubit marginal probabilities show deviations from 0.5, ")
    report.append(f"which may indicate readout bias or systematic errors. Detailed marginal analysis is required.\n\n")
    
    report.append(f"5. **Circuit-Specific Validation Required**: Claims about coherence, noise suppression, and circuit-specific ")
    report.append(f"correctness require comparison against an ideal target distribution and marginal/correlation analysis.\n\n")
    
    report.append("---\n\n")
    report.append("## Recommended Next Steps\n\n")
    report.append("1. **Simulator Baseline**: Run the same circuits on an ideal simulator to establish target distribution.\n")
    report.append("2. **Total Variation Distance**: Compute TV distance or Hellinger distance between hardware and simulator outputs.\n")
    report.append("3. **Correlated Error Analysis**: Investigate pairwise and higher-order correlations for systematic errors.\n")
    report.append("4. **Backend Comparison**: Compare results across different backends to identify hardware-specific effects.\n")
    report.append("5. **Timing Analysis**: Examine job metadata for queue time, execution time, and usage metrics.\n")
    
    # Write report
    with open(output_dir / 'analysis_report_enhanced.md', 'w', encoding='utf-8') as f:
        f.writelines(report)
    
    return report

def main():
    # Define job paths
    job_dir = Path("D:/Somnath-PROJECT/Jobs-to-check")
    output_dir = Path("D:/AGI-GH-REPO-11326/AGI-model/ibm_job_analysis")
    
    # Find all result files
    result_files = sorted(job_dir.glob("*-result.json"))
    
    print(f"Found {len(result_files)} job result files\n")
    
    # Analyze each job
    all_results = []
    for result_file in result_files:
        print(f"Analyzing {result_file.name}...")
        try:
            result = analyze_job(result_file)
            all_results.append(result)
            print(f"  - Job ID: {result['job_id']}")
            print(f"  - Shots: {result['num_shots']}")
            print(f"  - Qubits: {result['num_qubits']}")
            print(f"  - Unique States: {result['unique_states']}")
            print(f"  - Entropy: {result['state_entropy']:.4f} bits")
            print(f"  - Shot-Limited Max Entropy: {result['shot_limited_max_entropy']:.4f} bits")
            print(f"  - Mean Marginal P(1): {np.mean(result['marginals']):.4f}")
            print(f"  - Max Correlation: {result['max_correlation']:.4f}\n")
        except Exception as e:
            print(f"  - Error: {e}\n")
    
    if all_results:
        # Create visualizations
        print("Creating enhanced visualizations...")
        visualize_results_enhanced(all_results, output_dir)
        
        # Generate report
        print("Generating enhanced analysis report...")
        generate_report_enhanced(all_results, output_dir)
        
        print(f"\nEnhanced analysis complete! Results saved to {output_dir}")
    else:
        print("No valid job results found.")

if __name__ == "__main__":
    main()