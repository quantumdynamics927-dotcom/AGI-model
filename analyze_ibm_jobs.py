"""
IBM Quantum Job Results Analysis
Analyzes 6 IBM Quantum jobs for Sierpinski TMT Phase 4S optimized circuits
"""

import json
import base64
import numpy as np
from pathlib import Path
from collections import Counter
import matplotlib.pyplot as plt

def decode_result_data(result_json):
    """Decode the base64 result data into a numpy array"""
    data = result_json['data'][0]['results']['c']['data']
    shape = result_json['data'][0]['results']['c']['shape']
    
    # Decode base64
    decoded = base64.b64decode(data)
    
    # Convert to numpy array of bytes
    arr = np.frombuffer(decoded, dtype=np.uint8)
    
    # Unpack bits - each byte contains 8 bits
    # The data is stored as packed bits, need to unpack
    num_shots = shape[0]
    num_qubits = shape[1]
    
    # Calculate expected size in bits
    total_bits = num_shots * num_qubits
    expected_bytes = (total_bits + 7) // 8  # Round up to nearest byte
    
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

def analyze_job(job_path):
    """Analyze a single job result file"""
    with open(job_path, 'r') as f:
        job_data = json.load(f)
    
    # Get job info
    job_id = job_path.stem.replace('job-', '').replace('-result', '').replace('-info', '')
    
    # Extract result data
    result_data = decode_result_data(job_data)
    
    # Calculate statistics
    num_shots = result_data.shape[0]
    num_qubits = result_data.shape[1]
    
    # Count unique states
    # Convert each row to a tuple for hashing
    states = [tuple(row) for row in result_data]
    state_counts = Counter(states)
    unique_states = len(state_counts)
    
    # Find most common states
    most_common = state_counts.most_common(10)
    
    # Calculate bit-wise statistics
    bit_sums = np.sum(result_data, axis=0)
    bit_probs = bit_sums / num_shots
    
    # Calculate entropy
    from scipy.stats import entropy
    probabilities = np.array(list(state_counts.values())) / num_shots
    state_entropy = entropy(probabilities, base=2)
    
    return {
        'job_id': job_id,
        'num_shots': num_shots,
        'num_qubits': num_qubits,
        'unique_states': unique_states,
        'most_common_states': most_common,
        'bit_probabilities': bit_probs,
        'state_entropy': state_entropy,
        'result_array': result_data
    }

def visualize_results(all_results, output_dir):
    """Create visualizations for all jobs"""
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Plot 1: Bit probability distribution for each job
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    axes = axes.flatten()
    
    for idx, result in enumerate(all_results):
        ax = axes[idx]
        ax.bar(range(result['num_qubits']), result['bit_probabilities'])
        ax.set_xlabel('Qubit Index')
        ax.set_ylabel('Probability of |1⟩')
        ax.set_title(f"Job {result['job_id']}\nShots: {result['num_shots']}, Unique States: {result['unique_states']}")
        ax.set_ylim(0, 1)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'bit_probability_distribution.png', dpi=300)
    plt.close()
    
    # Plot 2: State count comparison
    fig, ax = plt.subplots(figsize=(12, 6))
    job_ids = [r['job_id'] for r in all_results]
    unique_counts = [r['unique_states'] for r in all_results]
    
    bars = ax.bar(job_ids, unique_counts)
    ax.set_xlabel('Job ID')
    ax.set_ylabel('Number of Unique States')
    ax.set_title('Unique Quantum States per Job')
    ax.tick_params(axis='x', rotation=45)
    
    # Add value labels on bars
    for bar, count in zip(bars, unique_counts):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50, 
                str(count), ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'unique_states_comparison.png', dpi=300)
    plt.close()
    
    # Plot 3: Entropy comparison
    fig, ax = plt.subplots(figsize=(12, 6))
    entropies = [r['state_entropy'] for r in all_results]
    
    bars = ax.bar(job_ids, entropies)
    ax.set_xlabel('Job ID')
    ax.set_ylabel('State Entropy (bits)')
    ax.set_title('Quantum State Entropy per Job')
    ax.tick_params(axis='x', rotation=45)
    
    for bar, ent in zip(bars, entropies):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                f'{ent:.2f}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'entropy_comparison.png', dpi=300)
    plt.close()
    
    # Plot 4: Heatmap of most common states
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    axes = axes.flatten()
    
    for idx, result in enumerate(all_results):
        ax = axes[idx]
        
        # Get top 20 most common states
        top_states = result['most_common_states'][:20]
        if top_states:
            state_arrays = np.array([list(state) for state, count in top_states])
            counts = np.array([count for state, count in top_states])
            
            # Create heatmap
            im = ax.imshow(state_arrays, cmap='binary', aspect='auto')
            ax.set_xlabel('Qubit Index')
            ax.set_ylabel('State Rank')
            ax.set_title(f"Job {result['job_id']}\nTop 20 States")
            
            # Add count annotations
            for i, count in enumerate(counts):
                ax.text(-2, i, f'{count}', va='center', ha='right', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'top_states_heatmap.png', dpi=300)
    plt.close()

def generate_report(all_results, output_dir):
    """Generate a comprehensive analysis report"""
    output_dir = Path(output_dir)
    
    report = []
    report.append("# IBM Quantum Job Results Analysis\n")
    report.append("## Sierpinski TMT Phase 4S Optimized Circuit Results\n\n")
    
    report.append("### Summary Statistics\n\n")
    report.append("| Job ID | Shots | Qubits | Unique States | Entropy (bits) |\n")
    report.append("|--------|-------|--------|----------------|----------------|\n")
    
    for result in all_results:
        report.append(f"| {result['job_id']} | {result['num_shots']} | {result['num_qubits']} | "
                      f"{result['unique_states']} | {result['state_entropy']:.4f} |\n")
    
    report.append("\n### Detailed Analysis\n\n")
    
    for result in all_results:
        report.append(f"#### Job {result['job_id']}\n\n")
        report.append(f"- **Total Shots**: {result['num_shots']}\n")
        report.append(f"- **Number of Qubits**: {result['num_qubits']}\n")
        report.append(f"- **Unique States Observed**: {result['unique_states']}\n")
        report.append(f"- **State Entropy**: {result['state_entropy']:.4f} bits\n")
        report.append(f"- **Maximum Possible States**: {2**result['num_qubits']}\n")
        report.append(f"- **State Space Coverage**: {result['unique_states'] / 2**result['num_qubits'] * 100:.6f}%\n\n")
        
        report.append("**Top 10 Most Frequent States:**\n```\n")
        for i, (state, count) in enumerate(result['most_common_states'][:10], 1):
            state_str = ''.join(map(str, state))
            prob = count / result['num_shots']
            report.append(f"{i}. State: {state_str[:50]}{'...' if len(state_str) > 50 else ''}\n")
            report.append(f"   Count: {count}, Probability: {prob:.6f}\n")
        report.append("```\n\n")
    
    # Calculate aggregate statistics
    report.append("### Aggregate Statistics\n\n")
    
    avg_entropy = np.mean([r['state_entropy'] for r in all_results])
    std_entropy = np.std([r['state_entropy'] for r in all_results])
    avg_unique = np.mean([r['unique_states'] for r in all_results])
    
    report.append(f"- **Average State Entropy**: {avg_entropy:.4f} ± {std_entropy:.4f} bits\n")
    report.append(f"- **Average Unique States**: {avg_unique:.0f}\n")
    
    # Compare bit probabilities across jobs
    report.append("\n### Bit Probability Analysis\n\n")
    
    # Group jobs by qubit count
    qubit_groups = {}
    for result in all_results:
        n_qubits = result['num_qubits']
        if n_qubits not in qubit_groups:
            qubit_groups[n_qubits] = []
        qubit_groups[n_qubits].append(result)
    
    for num_qubits, group_results in qubit_groups.items():
        report.append(f"\n#### {num_qubits} Qubit Jobs\n\n")
        
        # Find qubits with high variance across jobs in this group
        all_bit_probs = np.array([r['bit_probabilities'] for r in group_results])
        bit_prob_variance = np.var(all_bit_probs, axis=0)
        high_variance_qubits = np.where(bit_prob_variance > 0.01)[0]
        
        if len(high_variance_qubits) > 0:
            report.append(f"**Qubits with High Variance:** {high_variance_qubits.tolist()[:20]}\n\n")
            for qubit in high_variance_qubits[:10]:  # Limit to top 10
                probs = [r['bit_probabilities'][qubit] for r in group_results]
                report.append(f"- Qubit {qubit}: min={min(probs):.4f}, max={max(probs):.4f}, "
                             f"mean={np.mean(probs):.4f}, std={np.std(probs):.4f}\n")
    
    # Write report
    with open(output_dir / 'analysis_report.md', 'w') as f:
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
            print(f"  - Entropy: {result['state_entropy']:.4f} bits\n")
        except Exception as e:
            print(f"  - Error: {e}\n")
    
    if all_results:
        # Create visualizations
        print("Creating visualizations...")
        visualize_results(all_results, output_dir)
        
        # Generate report
        print("Generating analysis report...")
        generate_report(all_results, output_dir)
        
        print(f"\nAnalysis complete! Results saved to {output_dir}")
    else:
        print("No valid job results found.")

if __name__ == "__main__":
    main()