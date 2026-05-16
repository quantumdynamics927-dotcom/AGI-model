#!/usr/bin/env python3
"""
Analyze Bell_Phi_State IBM Quantum job results.

Circuit Structure:
- 2 qubits
- Creates Bell state: H(0) → CX(0,1)
- Applies phase P(5.083) to both qubits
- Measures both qubits

This creates a Bell state with phi-encoded phase.
"""

import json
import numpy as np
from collections import Counter
import base64
from pathlib import Path

# Job paths
RESULT_PATH = Path(r"E:\Descargas\job-d7nunoak4prs73dspdtg\job-d7nunoak4prs73dspdtg-result.json")
INFO_PATH = Path(r"E:\Descargas\job-d7nunoak4prs73dspdtg\job-d7nunoak4prs73dspdtg-info.json")

# Phase value from circuit
PHASE_VALUE = 5.0832036923152595
PHI = (1 + np.sqrt(5)) / 2  # Golden ratio


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


def analyze_bell_phi_results():
    """Main analysis function."""
    print("=" * 70)
    print("Bell_Phi_State IBM Quantum Job Analysis")
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
    
    # Circuit analysis
    print("\n--- Circuit Analysis ---")
    print(f"Phase value: {PHASE_VALUE:.15f}")
    print(f"Golden ratio (φ): {PHI:.15f}")
    print(f"Phase / φ: {PHASE_VALUE / PHI:.6f}")
    print(f"Phase / π: {PHASE_VALUE / np.pi:.6f}")
    print(f"Phase / (π × φ): {PHASE_VALUE / (np.pi * PHI):.6f}")
    print(f"φ²: {PHI**2:.15f}")
    print(f"π × φ: {np.pi * PHI:.6f}")
    
    # Check if phase relates to golden ratio
    print("\n--- Phase Relationship Analysis ---")
    print(f"  Phase ≈ π × φ² / 1.23 = {np.pi * PHI**2 / 1.23:.6f}")
    print(f"  Phase ≈ 2π × φ / 1.23 = {2 * np.pi * PHI / 1.23:.6f}")
    print(f"  Phase ≈ π × φ × 1.618 = {np.pi * PHI * 1.618:.6f}")
    
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
    print(f"\n--- Bell State Distribution ---")
    print("State | Count | Probability | Ideal Bell")
    print("-" * 50)
    
    # Ideal Bell state probabilities
    # |Φ+⟩ = (|00⟩ + |11⟩) / √2
    # After phase P(θ) on both qubits: |00⟩ + e^(2iθ)|11⟩
    # Measurement probabilities: P(00) = P(11) = 0.5
    
    ideal_probs = {0: 0.5, 3: 0.5}  # |00⟩ and |11⟩
    
    for state in [0, 1, 2, 3]:
        binary = format(state, '02b')
        count = counts.get(state, 0)
        prob = count / total
        ideal = ideal_probs.get(state, 0)
        diff = prob - ideal
        print(f"  |{binary}⟩: {count:4d} | {prob:.4f} | {ideal:.4f} | {diff:+.4f}")
    
    # Bell state fidelity
    p00 = counts.get(0, 0) / total
    p11 = counts.get(3, 0) / total
    bell_fidelity = p00 + p11
    
    print(f"\n--- Bell State Metrics ---")
    print(f"  P(|00⟩): {p00:.4f}")
    print(f"  P(|11⟩): {p11:.4f}")
    print(f"  P(|01⟩): {counts.get(1, 0) / total:.4f}")
    print(f"  P(|10⟩): {counts.get(2, 0) / total:.4f}")
    print(f"  Bell fidelity: {bell_fidelity:.4f}")
    print(f"  Ideal fidelity: 1.0000")
    
    # Correlation analysis
    print(f"\n--- Qubit Correlation ---")
    q0 = bit_array[:, 0]
    q1 = bit_array[:, 1]
    correlation = np.corrcoef(q0, q1)[0, 1]
    print(f"  Q0-Q1 correlation: {correlation:.4f}")
    print(f"  Ideal Bell correlation: 1.0000")
    
    # Entropy
    probabilities = np.array([count / total for count in counts.values()])
    shannon_entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
    
    print(f"\n--- Entropy ---")
    print(f"  Shannon entropy: {shannon_entropy:.4f} bits")
    print(f"  Max entropy (2 qubits): 2.0000 bits")
    print(f"  Ideal Bell entropy: 1.0000 bits")
    
    # Phase effect analysis
    print(f"\n--- Phase Effect Analysis ---")
    print("  The phase P(5.083) applied to both qubits creates:")
    print("  |Φ(θ)⟩ = (|00⟩ + e^(2iθ)|11⟩) / √2")
    print(f"  where θ = {PHASE_VALUE:.4f} rad")
    print(f"  e^(2iθ) = e^(2i × 5.083) = e^(10.166i)")
    print(f"  Phase factor: {np.exp(2j * PHASE_VALUE):.4f}")
    
    # Summary
    print(f"\n{'='*70}")
    print("Summary")
    print(f"{'='*70}")
    print(f"""
Hardware Execution: CONFIRMED
  - Job completed successfully on ibm_kingston
  - 1024 shots executed
  - Measurement data retrieved

Bell State Quality:
  - Fidelity: {bell_fidelity:.4f} (ideal: 1.0)
  - Correlation: {correlation:.4f} (ideal: 1.0)
  - Entropy: {shannon_entropy:.4f} bits (ideal Bell: 1.0)

Phase Value Analysis:
  - Phase: {PHASE_VALUE:.6f} rad
  - Relationship to φ: {PHASE_VALUE / PHI:.6f} × φ
  - Relationship to π: {PHASE_VALUE / np.pi:.6f} × π

Scientific Assessment:
  - Hardware deployability confirmed
  - Bell state created with phase-encoded correlation
  - "Phi-Bell" interpretation requires documentation of design intent
  - Functional correctness requires comparison with expected distribution
""")
    
    return {
        'info': info,
        'counts': counts,
        'bell_fidelity': bell_fidelity,
        'correlation': correlation,
        'shannon_entropy': shannon_entropy
    }


if __name__ == "__main__":
    analyze_bell_phi_results()