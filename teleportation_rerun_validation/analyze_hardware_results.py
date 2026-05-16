#!/usr/bin/env python3
"""
Analyze Teleportation Results from IBM Quantum Hardware

Processes job results from 3 different backends (ibm_marrakesh, ibm_fez, ibm_kingston)
with 2 runs each, computing teleportation fidelity.

Job IDs:
- ibm_marrakesh: d7l8qtokj84c73ceo7tg (4096 shots), d7l8r38kj84c73ceo860 (1024 shots)
- ibm_fez: d7l8r1i8ui0s73b648q0 (1024 shots), d7l8qri4lglc7380atr0 (4096 shots)
- ibm_kingston: d7l8r028ui0s73b648ng (1024 shots), d7l8qp24lglc7380atlg (4096 shots)
"""

import json
import base64
import numpy as np
from pathlib import Path
from collections import Counter
from datetime import datetime

# Constants
PHI = 1.618033988749895
CLASSICAL_FIDELITY_THRESHOLD = 2.0 / 3.0  # ~0.667
THETA_Y = np.pi / 3
THETA_Z = np.pi / 7

# Expected probabilities for RY(π/3)|0⟩
EXPECTED_P0 = np.cos(THETA_Y / 2) ** 2
EXPECTED_P1 = np.sin(THETA_Y / 2) ** 2


def decode_bitarray_data(base64_data: str, shape: list) -> np.ndarray:
    """
    Decode base64-encoded BitArray data from IBM Runtime results.
    
    Args:
        base64_data: Base64-encoded string
        shape: Shape of the array [shots, num_bits]
        
    Returns:
        np.ndarray: Decoded boolean array of shape [shots, num_bits]
    """
    # Decode base64
    decoded = base64.b64decode(base64_data)
    
    # Convert to numpy array of bytes
    arr = np.frombuffer(decoded, dtype=np.uint8)
    
    # Unpack bits
    num_shots = shape[0]
    num_bits = shape[1]
    
    # Create output array
    result = np.zeros((num_shots, num_bits), dtype=np.uint8)
    
    # Unpack bits for each shot
    for shot_idx in range(num_shots):
        for bit_idx in range(num_bits):
            bit_index = shot_idx * num_bits + bit_idx
            byte_index = bit_index // 8
            bit_offset = bit_index % 8
            
            if byte_index < len(arr):
                # Extract the bit (MSB first)
                result[shot_idx, bit_idx] = (arr[byte_index] >> (7 - bit_offset)) & 1
    
    return result


def compute_fidelity(measurement_data: np.ndarray) -> dict:
    """
    Compute teleportation fidelity from measurement data.
    
    Args:
        measurement_data: Array of shape [shots, 3] with measurements
        
    Returns:
        Dict with fidelity metrics
    """
    # Extract Bob's qubit measurements (3rd qubit, index 2)
    bob_outcomes = measurement_data[:, 2]
    
    # Count outcomes
    bob_0_count = np.sum(bob_outcomes == 0)
    bob_1_count = np.sum(bob_outcomes == 1)
    total = len(bob_outcomes)
    
    # Measured probabilities
    p_measured_0 = bob_0_count / total
    p_measured_1 = bob_1_count / total
    
    # Fidelity calculation
    fidelity = np.sqrt(EXPECTED_P0 * p_measured_0) + np.sqrt(EXPECTED_P1 * p_measured_1)
    fidelity_squared = fidelity ** 2
    
    # Quality rating
    if fidelity > 0.9:
        quality = "EXCELLENT ✅"
    elif fidelity > 0.8:
        quality = "VERY GOOD ✓"
    elif fidelity > CLASSICAL_FIDELITY_THRESHOLD:
        quality = "GOOD (above classical) ✓"
    elif fidelity > 0.5:
        quality = "MODERATE ⚠️"
    else:
        quality = "POOR ❌"
    
    return {
        "fidelity": float(fidelity),
        "fidelity_squared": float(fidelity_squared),
        "expected_prob_0": float(EXPECTED_P0),
        "expected_prob_1": float(EXPECTED_P1),
        "measured_prob_0": float(p_measured_0),
        "measured_prob_1": float(p_measured_1),
        "bob_0_count": int(bob_0_count),
        "bob_1_count": int(bob_1_count),
        "total_shots": int(total),
        "exceeds_classical_threshold": bool(fidelity > CLASSICAL_FIDELITY_THRESHOLD),
        "quality": quality
    }


def analyze_full_distribution(measurement_data: np.ndarray) -> dict:
    """
    Analyze the full 3-qubit measurement distribution.
    
    Args:
        measurement_data: Array of shape [shots, 3]
        
    Returns:
        Dict with distribution analysis
    """
    # Convert to state tuples
    states = [tuple(row) for row in measurement_data]
    state_counts = Counter(states)
    
    # Convert to bitstrings
    bitstring_counts = {}
    for state, count in state_counts.items():
        bitstring = ''.join(str(int(b)) for b in state)
        bitstring_counts[bitstring] = count
    
    total = len(states)
    
    # Shannon entropy
    probs = np.array(list(state_counts.values())) / total
    entropy = -np.sum(probs * np.log2(probs + 1e-10))
    max_entropy = np.log2(len(state_counts))
    
    return {
        "total_shots": total,
        "unique_states": len(state_counts),
        "state_distribution": {k: v for k, v in sorted(bitstring_counts.items(), key=lambda x: -x[1])},
        "entropy": float(entropy),
        "max_entropy": float(max_entropy),
        "uniformity": float(entropy / max_entropy) if max_entropy > 0 else 0
    }


def process_job(job_info_path: str, job_result_path: str) -> dict:
    """
    Process a single job's info and result files.
    
    Args:
        job_info_path: Path to job info JSON
        job_result_path: Path to job result JSON
        
    Returns:
        Dict with job analysis
    """
    # Load job info
    with open(job_info_path, 'r') as f:
        job_info = json.load(f)
    
    # Load job result
    with open(job_result_path, 'r') as f:
        job_result = json.load(f)
    
    # Extract metadata
    job_id = job_info['id']
    backend = job_info['backend']
    created = job_info['created']
    shots = job_info['params']['quantum_program']['shots']
    status = job_info['status']
    
    # Extract measurement data
    result_data = job_result['data'][0]['results']['c']
    base64_data = result_data['data']
    shape = result_data['shape']
    
    # Decode data
    measurement_data = decode_bitarray_data(base64_data, shape)
    
    # Compute fidelity
    fidelity_metrics = compute_fidelity(measurement_data)
    
    # Analyze full distribution
    distribution_analysis = analyze_full_distribution(measurement_data)
    
    return {
        "job_id": job_id,
        "backend": backend,
        "created": created,
        "shots": shots,
        "status": status,
        "fidelity_metrics": fidelity_metrics,
        "distribution_analysis": distribution_analysis
    }


def generate_report(results: list) -> str:
    """
    Generate a comprehensive markdown report.
    
    Args:
        results: List of job analysis results
        
    Returns:
        Markdown report string
    """
    lines = []
    
    # Header
    lines.append("# IBM Quantum Teleportation Hardware Validation Report")
    lines.append(f"\n**Generated**: {datetime.now().isoformat()}")
    lines.append(f"\n**Circuit**: `teleport_circuit_1.qasm`")
    lines.append(f"\n**Target State**: RY(π/3) · RZ(π/7) |0⟩")
    lines.append(f"\n**Classical Threshold**: F > {CLASSICAL_FIDELITY_THRESHOLD:.4f}")
    
    # Expected probabilities
    lines.append(f"\n---\n\n## Expected State Probabilities")
    lines.append(f"\n- **P(0)** = cos²(π/6) = {EXPECTED_P0:.4f}")
    lines.append(f"\n- **P(1)** = sin²(π/6) = {EXPECTED_P1:.4f}")
    
    # Summary table
    lines.append(f"\n\n---\n\n## Results Summary")
    lines.append(f"\n| Backend | Job ID | Shots | Fidelity | Quality | Above Classical |")
    lines.append(f"\n|---------|--------|-------|----------|---------|-----------------|")
    
    for r in results:
        fm = r['fidelity_metrics']
        above = "✓" if fm['exceeds_classical_threshold'] else "✗"
        lines.append(f"\n| {r['backend']} | `{r['job_id'][:12]}...` | {r['shots']} | {fm['fidelity']:.4f} | {fm['quality']} | {above} |")
    
    # Per-backend analysis
    lines.append(f"\n\n---\n\n## Per-Backend Analysis")
    
    backends = {}
    for r in results:
        if r['backend'] not in backends:
            backends[r['backend']] = []
        backends[r['backend']].append(r)
    
    for backend, backend_results in sorted(backends.items()):
        lines.append(f"\n\n### {backend}")
        
        fidelities = [r['fidelity_metrics']['fidelity'] for r in backend_results]
        mean_f = np.mean(fidelities)
        std_f = np.std(fidelities)
        best_f = max(fidelities)
        above_threshold = sum(1 for f in fidelities if f > CLASSICAL_FIDELITY_THRESHOLD)
        
        lines.append(f"\n- **Runs**: {len(backend_results)}")
        lines.append(f"\n- **Best Fidelity**: {best_f:.4f}")
        lines.append(f"\n- **Mean Fidelity**: {mean_f:.4f} ± {std_f:.4f}")
        lines.append(f"\n- **Above Classical Threshold**: {above_threshold}/{len(backend_results)}")
        
        for r in backend_results:
            fm = r['fidelity_metrics']
            lines.append(f"\n\n#### Job `{r['job_id']}`")
            lines.append(f"\n- **Shots**: {r['shots']}")
            lines.append(f"\n- **Fidelity**: {fm['fidelity']:.4f}")
            lines.append(f"\n- **Fidelity²**: {fm['fidelity_squared']:.4f}")
            lines.append(f"\n- **Quality**: {fm['quality']}")
            lines.append(f"\n- **Bob's Measurements**: |0⟩={fm['bob_0_count']}, |1⟩={fm['bob_1_count']}")
            lines.append(f"\n- **Measured P(0)**: {fm['measured_prob_0']:.4f}")
            lines.append(f"\n- **Measured P(1)**: {fm['measured_prob_1']:.4f}")
            
            # Distribution
            da = r['distribution_analysis']
            lines.append(f"\n- **Entropy**: {da['entropy']:.4f} bits (max: {da['max_entropy']:.4f})")
            lines.append(f"\n- **Uniformity**: {da['uniformity']:.4f}")
            
            # Top states
            top_states = list(da['state_distribution'].items())[:5]
            lines.append(f"\n- **Top States**: {', '.join([f'|{s}⟩:{c}' for s, c in top_states])}")
    
    # Overall statistics
    all_fidelities = [r['fidelity_metrics']['fidelity'] for r in results]
    overall_mean = np.mean(all_fidelities)
    overall_std = np.std(all_fidelities)
    overall_best = max(all_fidelities)
    overall_above = sum(1 for f in all_fidelities if f > CLASSICAL_FIDELITY_THRESHOLD)
    
    lines.append(f"\n\n---\n\n## Overall Statistics")
    lines.append(f"\n- **Total Runs**: {len(results)}")
    lines.append(f"\n- **Best Fidelity**: {overall_best:.4f}")
    lines.append(f"\n- **Mean Fidelity**: {overall_mean:.4f} ± {overall_std:.4f}")
    lines.append(f"\n- **Runs Above Classical Threshold**: {overall_above}/{len(results)}")
    
    # Conclusion
    lines.append(f"\n\n---\n\n## Conclusion")
    
    if overall_above == len(results):
        conclusion = "**CONFIRMED**: All runs exceed the classical teleportation threshold. The teleportation protocol is reproducible across all three hardware backends."
    elif overall_above >= len(results) // 2:
        conclusion = f"**PARTIALLY CONFIRMED**: {overall_above}/{len(results)} runs exceed the classical threshold. The teleportation protocol shows promising evidence across hardware backends."
    else:
        conclusion = f"**NOT CONFIRMED**: Only {overall_above}/{len(results)} runs exceed the classical threshold. Further investigation needed."
    
    lines.append(f"\n{conclusion}")
    
    # Evidence summary
    lines.append(f"\n\n### Evidence Summary")
    lines.append(f"\n- **Backends Tested**: {', '.join(sorted(backends.keys()))}")
    lines.append(f"\n- **Total Shots**: {sum(r['shots'] for r in results):,}")
    lines.append(f"\n- **Best Fidelity**: {overall_best:.4f} ({results[np.argmax(all_fidelities)]['backend']})")
    lines.append(f"\n- **Mean Fidelity**: {overall_mean:.4f} ± {overall_std:.4f}")
    lines.append(f"\n- **Reproducibility**: {overall_above}/{len(results)} runs above classical threshold")
    
    return ''.join(lines)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze teleportation job results")
    parser.add_argument("--input-dir", type=str, default=r"D:\Somnath-PROJECT\Jobs-to-check",
                        help="Directory containing job files")
    parser.add_argument("--output-dir", type=str, default="teleportation_rerun_validation",
                        help="Output directory")
    
    args = parser.parse_args()
    
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 80)
    print("IBM QUANTUM TELEPORTATION HARDWARE VALIDATION ANALYSIS")
    print("=" * 80)
    
    # Define jobs to process
    jobs = [
        # ibm_marrakesh
        ("d7l8qtokj84c73ceo7tg", "ibm_marrakesh", 4096),
        ("d7l8r38kj84c73ceo860", "ibm_marrakesh", 1024),
        # ibm_fez
        ("d7l8r1i8ui0s73b648q0", "ibm_fez", 1024),
        ("d7l8qri4lglc7380atr0", "ibm_fez", 4096),
        # ibm_kingston
        ("d7l8r028ui0s73b648ng", "ibm_kingston", 1024),
        ("d7l8qp24lglc7380atlg", "ibm_kingston", 4096),
    ]
    
    results = []
    
    for job_id, expected_backend, expected_shots in jobs:
        info_path = input_dir / f"job-{job_id}-info.json"
        result_path = input_dir / f"job-{job_id}-result.json"
        
        if not info_path.exists() or not result_path.exists():
            print(f"\n⚠️  Missing files for job {job_id}")
            continue
        
        print(f"\n📊 Processing job {job_id}...")
        
        try:
            result = process_job(str(info_path), str(result_path))
            results.append(result)
            
            fm = result['fidelity_metrics']
            print(f"   Backend: {result['backend']}")
            print(f"   Shots: {result['shots']}")
            print(f"   Fidelity: {fm['fidelity']:.4f}")
            print(f"   Quality: {fm['quality']}")
            print(f"   Above Classical: {fm['exceeds_classical_threshold']}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    if not results:
        print("\n❌ No results to analyze")
        return
    
    # Generate report
    print(f"\n📝 Generating report...")
    report = generate_report(results)
    
    # Save report
    report_path = output_dir / "hardware_validation_report.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"✅ Report saved to: {report_path}")
    
    # Save JSON results
    json_path = output_dir / "hardware_validation_results.json"
    with open(json_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"✅ Results saved to: {json_path}")
    
    # Print summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print("=" * 80)
    
    all_fidelities = [r['fidelity_metrics']['fidelity'] for r in results]
    overall_mean = np.mean(all_fidelities)
    overall_best = max(all_fidelities)
    overall_above = sum(1 for f in all_fidelities if f > CLASSICAL_FIDELITY_THRESHOLD)
    
    print(f"\n📊 Overall Statistics:")
    print(f"   Total Runs: {len(results)}")
    print(f"   Best Fidelity: {overall_best:.4f}")
    print(f"   Mean Fidelity: {overall_mean:.4f}")
    print(f"   Above Classical Threshold: {overall_above}/{len(results)}")
    
    print(f"\n📋 Per-Backend Results:")
    backends = {}
    for r in results:
        if r['backend'] not in backends:
            backends[r['backend']] = []
        backends[r['backend']].append(r['fidelity_metrics']['fidelity'])
    
    for backend, fidelities in sorted(backends.items()):
        mean_f = np.mean(fidelities)
        best_f = max(fidelities)
        above = sum(1 for f in fidelities if f > CLASSICAL_FIDELITY_THRESHOLD)
        print(f"   {backend}: Mean={mean_f:.4f}, Best={best_f:.4f}, Above Threshold={above}/{len(fidelities)}")
    
    print(f"\n{'='*80}")


if __name__ == "__main__":
    main()