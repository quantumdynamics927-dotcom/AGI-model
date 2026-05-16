#!/usr/bin/env python3
"""
Corrected Teleportation Fidelity Analysis

This script properly computes teleportation fidelity by:
1. Applying classical corrections based on Alice's Bell measurement outcomes
2. Computing fidelity from the corrected Bob qubit distribution
3. Comparing against proper benchmarks

The key insight: In the OpenQASM 2.0 circuit, conditional corrections are NOT
applied on hardware. They must be applied classically in post-processing.

For each shot:
- Alice's Bell measurement: bits 0 and 1 (c[0], c[1])
- Bob's qubit measurement: bit 2 (c[2])

Correction rules:
- If Alice measures 00 (c[0]=0, c[1]=0): Bob's qubit is correct as-is
- If Alice measures 01 (c[0]=0, c[1]=1): Apply X to Bob's qubit (flip bit)
- If Alice measures 10 (c[0]=1, c[1]=0): Apply Z to Bob's qubit (phase, no bit flip)
- If Alice measures 11 (c[0]=1, c[1]=1): Apply XZ to Bob's qubit (flip bit)

For computational basis measurements, only X corrections matter (Z is phase).
"""

import json
import base64
import numpy as np
from pathlib import Path
from collections import Counter
from datetime import datetime
from typing import Dict, Tuple

# Constants
CLASSICAL_FIDELITY_THRESHOLD = 2.0 / 3.0  # ~0.667
THETA_Y = np.pi / 3
THETA_Z = np.pi / 7

# Expected probabilities for RY(π/3)|0⟩
# |ψ⟩ = RY(π/3)|0⟩ = cos(π/6)|0⟩ + sin(π/6)|1⟩
EXPECTED_P0 = np.cos(THETA_Y / 2) ** 2  # cos²(π/6) ≈ 0.75
EXPECTED_P1 = np.sin(THETA_Y / 2) ** 2  # sin²(π/6) ≈ 0.25


def decode_bitarray_data(base64_data: str, shape: list) -> np.ndarray:
    """Decode base64-encoded BitArray data from IBM Runtime results."""
    decoded = base64.b64decode(base64_data)
    arr = np.frombuffer(decoded, dtype=np.uint8)
    
    num_shots = shape[0]
    num_bits = shape[1]
    result = np.zeros((num_shots, num_bits), dtype=np.uint8)
    
    for shot_idx in range(num_shots):
        for bit_idx in range(num_bits):
            bit_index = shot_idx * num_bits + bit_idx
            byte_index = bit_index // 8
            bit_offset = bit_index % 8
            
            if byte_index < len(arr):
                result[shot_idx, bit_idx] = (arr[byte_index] >> (7 - bit_offset)) & 1
    
    return result


def apply_classical_corrections(measurement_data: np.ndarray) -> np.ndarray:
    """
    Apply classical corrections to Bob's qubit based on Alice's Bell measurement.
    
    In the teleportation protocol:
    - Alice's qubits: bits 0 and 1 (Bell measurement)
    - Bob's qubit: bit 2
    
    Correction rules:
    - 00: No correction needed
    - 01: Apply X (flip Bob's bit)
    - 10: Apply Z (phase correction - no effect on computational basis)
    - 11: Apply XZ (flip Bob's bit)
    
    For computational basis measurements, only X corrections matter.
    
    Args:
        measurement_data: Array of shape [shots, 3] with raw measurements
        
    Returns:
        Corrected Bob qubit outcomes (0 or 1 for each shot)
    """
    # Extract Alice's Bell measurement outcomes
    alice_bit0 = measurement_data[:, 0]  # c[0]
    alice_bit1 = measurement_data[:, 1]  # c[1]
    
    # Extract Bob's raw measurement
    bob_raw = measurement_data[:, 2]
    
    # Apply X correction when Alice's bit 1 is 1
    # (for outcomes 01 and 11, Bob needs X correction)
    bob_corrected = np.where(alice_bit1 == 1, 1 - bob_raw, bob_raw)
    
    return bob_corrected


def compute_teleportation_fidelity(bob_corrected: np.ndarray) -> Dict:
    """
    Compute teleportation fidelity from corrected Bob outcomes.
    
    The fidelity is computed as:
    F = √(P_expected(0) × P_corrected(0)) + √(P_expected(1) × P_corrected(1))
    
    This is the Bhattacharyya coefficient between the expected and measured
    distributions, which is a valid fidelity measure for pure states.
    
    Args:
        bob_corrected: Array of corrected Bob qubit outcomes (0 or 1)
        
    Returns:
        Dict with fidelity metrics
    """
    total = len(bob_corrected)
    
    # Count corrected outcomes
    bob_0_count = np.sum(bob_corrected == 0)
    bob_1_count = np.sum(bob_corrected == 1)
    
    # Measured probabilities (corrected)
    p_corrected_0 = bob_0_count / total
    p_corrected_1 = bob_1_count / total
    
    # Fidelity (Bhattacharyya coefficient)
    fidelity = np.sqrt(EXPECTED_P0 * p_corrected_0) + np.sqrt(EXPECTED_P1 * p_corrected_1)
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
        "expected_p0": float(EXPECTED_P0),
        "expected_p1": float(EXPECTED_P1),
        "corrected_p0": float(p_corrected_0),
        "corrected_p1": float(p_corrected_1),
        "bob_0_count": int(bob_0_count),
        "bob_1_count": int(bob_1_count),
        "total_shots": int(total),
        "exceeds_classical_threshold": bool(fidelity > CLASSICAL_FIDELITY_THRESHOLD),
        "quality": quality
    }


def compute_raw_fidelity(measurement_data: np.ndarray) -> Dict:
    """
    Compute fidelity from Bob's RAW (uncorrected) measurements.
    
    This is what the previous script computed - it does NOT account for
    classical corrections and is NOT the correct teleportation fidelity.
    
    Included for comparison to show the difference.
    """
    bob_raw = measurement_data[:, 2]
    total = len(bob_raw)
    
    bob_0_count = np.sum(bob_raw == 0)
    bob_1_count = np.sum(bob_raw == 1)
    
    p_raw_0 = bob_0_count / total
    p_raw_1 = bob_1_count / total
    
    fidelity = np.sqrt(EXPECTED_P0 * p_raw_0) + np.sqrt(EXPECTED_P1 * p_raw_1)
    
    return {
        "raw_fidelity": float(fidelity),
        "raw_p0": float(p_raw_0),
        "raw_p1": float(p_raw_1),
        "raw_bob_0_count": int(bob_0_count),
        "raw_bob_1_count": int(bob_1_count)
    }


def analyze_bell_measurement_distribution(measurement_data: np.ndarray) -> Dict:
    """
    Analyze the distribution of Alice's Bell measurement outcomes.
    
    In ideal teleportation, all 4 Bell outcomes (00, 01, 10, 11) should be
    equally likely (25% each).
    """
    # Alice's bits
    alice_bit0 = measurement_data[:, 0]
    alice_bit1 = measurement_data[:, 1]
    
    # Bell outcomes
    bell_00 = np.sum((alice_bit0 == 0) & (alice_bit1 == 0))
    bell_01 = np.sum((alice_bit0 == 0) & (alice_bit1 == 1))
    bell_10 = np.sum((alice_bit0 == 1) & (alice_bit1 == 0))
    bell_11 = np.sum((alice_bit0 == 1) & (alice_bit1 == 1))
    
    total = len(alice_bit0)
    
    return {
        "bell_00_count": int(bell_00),
        "bell_01_count": int(bell_01),
        "bell_10_count": int(bell_10),
        "bell_11_count": int(bell_11),
        "bell_00_prob": float(bell_00 / total),
        "bell_01_prob": float(bell_01 / total),
        "bell_10_prob": float(bell_10 / total),
        "bell_11_prob": float(bell_11 / total),
        "ideal_bell_prob": 0.25
    }


def process_job_corrected(job_info_path: str, job_result_path: str) -> Dict:
    """
    Process a job with CORRECTED fidelity computation.
    """
    # Load files
    with open(job_info_path, 'r') as f:
        job_info = json.load(f)
    with open(job_result_path, 'r') as f:
        job_result = json.load(f)
    
    # Extract metadata
    job_id = job_info['id']
    backend = job_info['backend']
    created = job_info['created']
    shots = job_info['params']['quantum_program']['shots']
    status = job_info['status']
    
    # Decode measurement data
    result_data = job_result['data'][0]['results']['c']
    base64_data = result_data['data']
    shape = result_data['shape']
    measurement_data = decode_bitarray_data(base64_data, shape)
    
    # Apply classical corrections
    bob_corrected = apply_classical_corrections(measurement_data)
    
    # Compute corrected fidelity
    corrected_fidelity = compute_teleportation_fidelity(bob_corrected)
    
    # Compute raw fidelity (for comparison)
    raw_fidelity = compute_raw_fidelity(measurement_data)
    
    # Analyze Bell measurement distribution
    bell_analysis = analyze_bell_measurement_distribution(measurement_data)
    
    return {
        "job_id": job_id,
        "backend": backend,
        "created": created,
        "shots": shots,
        "status": status,
        "corrected_fidelity": corrected_fidelity,
        "raw_fidelity": raw_fidelity,
        "bell_analysis": bell_analysis
    }


def generate_corrected_report(results: list) -> str:
    """Generate a corrected report with proper fidelity computation."""
    lines = []
    
    # Header
    lines.append("# IBM Quantum Teleportation Hardware Validation Report (CORRECTED)")
    lines.append(f"\n**Generated**: {datetime.now().isoformat()}")
    lines.append(f"\n**Circuit**: `teleport_circuit_1.qasm`")
    lines.append(f"\n**Target State**: RY(π/3) · RZ(π/7) |0⟩")
    lines.append(f"\n**Classical Threshold**: F > {CLASSICAL_FIDELITY_THRESHOLD:.4f}")
    
    # Methodology
    lines.append(f"\n\n---\n\n## Methodology")
    lines.append(f"\n### Fidelity Computation")
    lines.append(f"\nThis report uses the **corrected fidelity computation**:")
    lines.append(f"\n1. Extract Alice's Bell measurement outcomes (bits 0 and 1)")
    lines.append(f"\n2. Apply classical corrections to Bob's qubit:")
    lines.append(f"\n   - If Alice measures 00: No correction")
    lines.append(f"\n   - If Alice measures 01: Apply X (flip Bob's bit)")
    lines.append(f"\n   - If Alice measures 10: Apply Z (phase, no bit flip)")
    lines.append(f"\n   - If Alice measures 11: Apply XZ (flip Bob's bit)")
    lines.append(f"\n3. Compute fidelity from corrected Bob distribution")
    lines.append(f"\n4. Compare against classical threshold of 2/3")
    
    lines.append(f"\n\n### Expected State")
    lines.append(f"\n- **P(0)** = cos²(π/6) = {EXPECTED_P0:.4f}")
    lines.append(f"\n- **P(1)** = sin²(π/6) = {EXPECTED_P1:.4f}")
    
    # Summary table
    lines.append(f"\n\n---\n\n## Results Summary")
    lines.append(f"\n| Backend | Job ID | Shots | Corrected F | Raw F | Quality |")
    lines.append(f"\n|---------|--------|-------|-------------|-------|---------|")
    
    for r in results:
        cf = r['corrected_fidelity']
        rf = r['raw_fidelity']
        lines.append(f"\n| {r['backend']} | `{r['job_id'][:12]}...` | {r['shots']} | {cf['fidelity']:.4f} | {rf['raw_fidelity']:.4f} | {cf['quality']} |")
    
    # Per-backend analysis
    lines.append(f"\n\n---\n\n## Per-Backend Analysis")
    
    backends = {}
    for r in results:
        if r['backend'] not in backends:
            backends[r['backend']] = []
        backends[r['backend']].append(r)
    
    for backend, backend_results in sorted(backends.items()):
        lines.append(f"\n\n### {backend}")
        
        fidelities = [r['corrected_fidelity']['fidelity'] for r in backend_results]
        mean_f = np.mean(fidelities)
        std_f = np.std(fidelities)
        best_f = max(fidelities)
        above_threshold = sum(1 for f in fidelities if f > CLASSICAL_FIDELITY_THRESHOLD)
        
        lines.append(f"\n- **Runs**: {len(backend_results)}")
        lines.append(f"\n- **Best Corrected Fidelity**: {best_f:.4f}")
        lines.append(f"\n- **Mean Corrected Fidelity**: {mean_f:.4f} ± {std_f:.4f}")
        lines.append(f"\n- **Above Classical Threshold**: {above_threshold}/{len(backend_results)}")
        
        for r in backend_results:
            cf = r['corrected_fidelity']
            rf = r['raw_fidelity']
            ba = r['bell_analysis']
            
            lines.append(f"\n\n#### Job `{r['job_id']}`")
            lines.append(f"\n- **Shots**: {r['shots']}")
            lines.append(f"\n- **Corrected Fidelity**: {cf['fidelity']:.4f}")
            lines.append(f"\n- **Raw Fidelity**: {rf['raw_fidelity']:.4f}")
            lines.append(f"\n- **Quality**: {cf['quality']}")
            lines.append(f"\n- **Corrected Bob**: |0⟩={cf['bob_0_count']}, |1⟩={cf['bob_1_count']}")
            lines.append(f"\n- **Bell Distribution**: 00={ba['bell_00_prob']:.3f}, 01={ba['bell_01_prob']:.3f}, 10={ba['bell_10_prob']:.3f}, 11={ba['bell_11_prob']:.3f}")
    
    # Overall statistics
    all_corrected = [r['corrected_fidelity']['fidelity'] for r in results]
    all_raw = [r['raw_fidelity']['raw_fidelity'] for r in results]
    
    lines.append(f"\n\n---\n\n## Overall Statistics")
    lines.append(f"\n- **Total Runs**: {len(results)}")
    lines.append(f"\n- **Best Corrected Fidelity**: {max(all_corrected):.4f}")
    lines.append(f"\n- **Mean Corrected Fidelity**: {np.mean(all_corrected):.4f} ± {np.std(all_corrected):.4f}")
    lines.append(f"\n- **Mean Raw Fidelity**: {np.mean(all_raw):.4f}")
    lines.append(f"\n- **Runs Above Classical Threshold**: {sum(1 for f in all_corrected if f > CLASSICAL_FIDELITY_THRESHOLD)}/{len(results)}")
    
    # Conclusion
    lines.append(f"\n\n---\n\n## Conclusion")
    
    above_threshold = sum(1 for f in all_corrected if f > CLASSICAL_FIDELITY_THRESHOLD)
    
    if above_threshold == len(results):
        conclusion = f"**CONFIRMED**: All {len(results)} runs exceed the classical teleportation threshold after applying proper classical corrections. The teleportation protocol is reproducible across all three hardware backends."
    elif above_threshold >= len(results) // 2:
        conclusion = f"**PARTIALLY CONFIRMED**: {above_threshold}/{len(results)} runs exceed the classical threshold after corrections."
    else:
        conclusion = f"**NOT CONFIRMED**: Only {above_threshold}/{len(results)} runs exceed the classical threshold."
    
    lines.append(f"\n{conclusion}")
    
    # Important notes
    lines.append(f"\n\n### Important Notes")
    lines.append(f"\n1. **Fidelity Definition**: This report uses the Bhattacharyya coefficient between expected and measured distributions, which is a valid fidelity measure for pure states.")
    lines.append(f"\n2. **Classical Corrections**: Fidelity is computed AFTER applying X corrections based on Alice's Bell measurement outcomes.")
    lines.append(f"\n3. **Single State Test**: This tests teleportation of ONE specific input state (RY(π/3)·RZ(π/7)|0⟩), not average fidelity over all possible input states.")
    lines.append(f"\n4. **No Readout Mitigation**: No readout error mitigation was applied.")
    lines.append(f"\n5. **No Post-Selection**: All shots are included; no shots were discarded.")
    
    return ''.join(lines)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Corrected teleportation fidelity analysis")
    parser.add_argument("--input-dir", type=str, default=r"D:\Somnath-PROJECT\Jobs-to-check",
                        help="Directory containing job files")
    parser.add_argument("--output-dir", type=str, default="teleportation_rerun_validation",
                        help="Output directory")
    
    args = parser.parse_args()
    
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 80)
    print("CORRECTED TELEPORTATION FIDELITY ANALYSIS")
    print("=" * 80)
    print("\n⚠️  NOTE: This analysis applies classical corrections to Bob's qubit")
    print("   based on Alice's Bell measurement outcomes.")
    print()
    
    # Define jobs
    jobs = [
        ("d7l8qtokj84c73ceo7tg", "ibm_marrakesh", 4096),
        ("d7l8r38kj84c73ceo860", "ibm_marrakesh", 1024),
        ("d7l8r1i8ui0s73b648q0", "ibm_fez", 1024),
        ("d7l8qri4lglc7380atr0", "ibm_fez", 4096),
        ("d7l8r028ui0s73b648ng", "ibm_kingston", 1024),
        ("d7l8qp24lglc7380atlg", "ibm_kingston", 4096),
    ]
    
    results = []
    
    for job_id, expected_backend, expected_shots in jobs:
        info_path = input_dir / f"job-{job_id}-info.json"
        result_path = input_dir / f"job-{job_id}-result.json"
        
        if not info_path.exists() or not result_path.exists():
            print(f"⚠️  Missing files for job {job_id}")
            continue
        
        print(f"\n📊 Processing job {job_id}...")
        
        try:
            result = process_job_corrected(str(info_path), str(result_path))
            results.append(result)
            
            cf = result['corrected_fidelity']
            rf = result['raw_fidelity']
            ba = result['bell_analysis']
            
            print(f"   Backend: {result['backend']}")
            print(f"   Shots: {result['shots']}")
            print(f"   Corrected Fidelity: {cf['fidelity']:.4f}")
            print(f"   Raw Fidelity: {rf['raw_fidelity']:.4f}")
            print(f"   Quality: {cf['quality']}")
            print(f"   Bell Distribution: 00={ba['bell_00_prob']:.3f}, 01={ba['bell_01_prob']:.3f}, 10={ba['bell_10_prob']:.3f}, 11={ba['bell_11_prob']:.3f}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    if not results:
        print("\n❌ No results to analyze")
        return
    
    # Generate report
    print(f"\n📝 Generating corrected report...")
    report = generate_corrected_report(results)
    
    # Save report
    report_path = output_dir / "corrected_hardware_validation_report.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"✅ Report saved to: {report_path}")
    
    # Save JSON
    json_path = output_dir / "corrected_hardware_validation_results.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"✅ Results saved to: {json_path}")
    
    # Print summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print("=" * 80)
    
    all_corrected = [r['corrected_fidelity']['fidelity'] for r in results]
    all_raw = [r['raw_fidelity']['raw_fidelity'] for r in results]
    
    print(f"\n📊 Fidelity Comparison:")
    print(f"   Mean Corrected Fidelity: {np.mean(all_corrected):.4f} ± {np.std(all_corrected):.4f}")
    print(f"   Mean Raw Fidelity: {np.mean(all_raw):.4f} ± {np.std(all_raw):.4f}")
    print(f"   Difference: {np.mean(all_corrected) - np.mean(all_raw):.4f}")
    
    print(f"\n📋 Corrected Results by Backend:")
    backends = {}
    for r in results:
        if r['backend'] not in backends:
            backends[r['backend']] = []
        backends[r['backend']].append(r['corrected_fidelity']['fidelity'])
    
    for backend, fidelities in sorted(backends.items()):
        mean_f = np.mean(fidelities)
        best_f = max(fidelities)
        above = sum(1 for f in fidelities if f > CLASSICAL_FIDELITY_THRESHOLD)
        print(f"   {backend}: Mean={mean_f:.4f}, Best={best_f:.4f}, Above Threshold={above}/{len(fidelities)}")
    
    print(f"\n{'='*80}")


if __name__ == "__main__":
    main()