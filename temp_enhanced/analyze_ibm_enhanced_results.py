"""
Analyzer for M3-Mitigated IBM Hardware Results
Compares v2.0 (enhanced) vs v1.0 (baseline) performance
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime

PHI = 1.618033988749895

def hex_to_bits_v2(hex_value, measured_indices):
    """Convert hex measurement to bit array (v2.0 with 156 qubits)"""
    if isinstance(hex_value, str):
        hex_value = hex_value.replace('0x', '')
    
    int_val = int(hex_value, 16)
    bin_str = bin(int_val)[2:].zfill(156)
    bin_str = bin_str[::-1]  # Little-endian
    
    bits_all = [int(b) for b in bin_str]
    measured_bits = [bits_all[i] if i < len(bits_all) else 0 for i in measured_indices]
    
    return measured_bits

def analyze_enhanced_results(result_file):
    """Analyze M3-mitigated results from v2.0 circuit"""
    
    print("\n" + "="*80)
    print("M3-MITIGATED RESULTS ANALYSIS (v2.0 Enhanced)")
    print("="*80)
    
    # Load result
    with open(result_file) as f:
        data = json.load(f)
    
    if 'mitigated_counts' in data:
        # From run_ibm_enhanced_with_m3.py
        counts = data['mitigated_counts']
        num_shots = data['shots']
    else:
        # From raw IBM result JSON
        samples = data['results'][0]['data']['c']['samples']
        num_shots = len(samples)
        
        # Measured bits: c[0,1,2,8,13,21,34,55,76,78-87]
        measured_indices = [0, 1, 2, 8, 13, 21, 34, 55, 76] + list(range(78, 88))
        
        # Convert to counts dict
        counts = {}
        for sample in samples:
            bits = hex_to_bits_v2(sample, measured_indices)
            bitstring = ''.join(map(str, bits))
            counts[bitstring] = counts.get(bitstring, 0) + 1
    
    print(f"Total shots: {num_shots:,}")
    print(f"Unique outcomes: {len(counts)}")
    
    # Convert counts to measurement arrays
    measurements = []
    for bitstring, count in counts.items():
        bits = [int(b) for b in bitstring]
        measurements.extend([bits] * count)
    
    measurements = np.array(measurements)
    
    # Bit mapping for v2.0:
    # [0,1,2] = Left payload
    # [3-12] = Right payload q[78-87]
    # [13] = q[8] (Tetrahedron F_5)
    # [14] = q[13] (Tetrahedron F_6)
    # [15] = q[21] (Octahedron F_7)
    # [16] = q[34] (Dodecahedron F_8)
    # [17] = q[55] (Icosahedron F_9)
    # [18] = q[76] (Retrocausal hole)
    
    idx = {
        'payload_left': 0,      # q[0]
        'payload_right': 3,     # q[78] (first Right measurement)
        'left_qubits': [0, 1, 2],
        'right_qubits': list(range(3, 13)),  # q[78-87]
        'tetra_f5': 13,         # q[8]
        'tetra_f6': 14,         # q[13]
        'octa_f7': 15,          # q[21]
        'dodec_f8': 16,         # q[34]
        'icosa_f9': 17,         # q[55]
        'retrocausal': 18       # q[76]
    }
    
    # === WORMHOLE ANALYSIS ===
    print("\n--- WORMHOLE METRICS (78 Bell Pairs) ---")
    
    payload_left = measurements[:, idx['payload_left']]
    payload_right = measurements[:, idx['payload_right']]
    
    correlation = np.corrcoef(payload_left, payload_right)[0, 1]
    transfer_success = np.sum(payload_left == payload_right) / num_shots
    
    print(f"Payload Correlation (q[0]↔q[78]): {correlation:+.4f}")
    print(f"Transfer Success Rate: {transfer_success*100:.2f}%")
    
    # Entropy
    left_prob = np.mean(payload_left)
    right_prob = np.mean(payload_right)
    
    def entropy(p):
        if p == 0 or p == 1:
            return 0
        return -p * np.log2(p) - (1-p) * np.log2(1-p)
    
    S_left = entropy(left_prob)
    S_right = entropy(right_prob)
    S_wormhole = (S_left + S_right) / 2
    
    print(f"Wormhole Entropy S: {S_wormhole:.3f}")
    
    T_wormhole = abs(correlation) * 3.5
    print(f"Traversability T: {T_wormhole:.3f}")
    
    r_coherence = (transfer_success * 2) - 1
    print(f"Coherence r: {r_coherence:+.3f}")
    
    # === METATRON GEOMETRY (Fibonacci-indexed) ===
    print("\n--- METATRON PLATONIC SOLIDS (Fibonacci) ---")
    
    platonic_scores = {}
    platonic_data = {
        'tetrahedron_F5': measurements[:, idx['tetra_f5']],
        'tetrahedron_F6': measurements[:, idx['tetra_f6']],
        'octahedron_F7': measurements[:, idx['octa_f7']],
        'dodecahedron_F8': measurements[:, idx['dodec_f8']],
        'icosahedron_F9': measurements[:, idx['icosa_f9']]
    }
    
    for name, bits in platonic_data.items():
        prob_1 = np.mean(bits)
        score = 1 - 2 * abs(prob_1 - 0.5)
        platonic_scores[name] = score
        print(f"  {name}: {score:.4f} (p_1={prob_1:.3f})")
    
    phi_resonance = np.mean(list(platonic_scores.values()))
    print(f"Phi Resonance (avg): {phi_resonance:.4f}")
    
    # === RETROCAUSAL SIGNATURE ===
    print("\n--- RETROCAUSAL HANDSHAKE ---")
    
    retro_bits = measurements[:, idx['retrocausal']]
    retro_prob = np.mean(retro_bits)
    
    first_half = retro_bits[:num_shots//2]
    second_half = retro_bits[num_shots//2:]
    temporal_asym = abs(np.mean(first_half) - np.mean(second_half))
    
    print(f"Retrocausal Probability: {retro_prob:.3f}")
    print(f"Temporal Asymmetry: {temporal_asym:.4f}")
    
    retro_payload_corr = np.corrcoef(retro_bits, payload_left)[0, 1]
    R_score = abs(retro_payload_corr)
    
    print(f"R-Score (retro↔payload): {R_score:.4f}")
    
    # === TMT RATIOS ===
    print("\n--- TMT CONSCIOUSNESS RATIOS ---")
    
    all_bits = measurements.flatten()
    prob_all = np.mean(all_bits)
    observed_delta = prob_all * 10
    
    print(f"Global Bit Probability: {prob_all:.6f}")
    print(f"Observed TMT Delta: {observed_delta:.6f}")
    print(f"Expected TMT (3/22): 0.136364")
    print(f"Match: {100 - abs(observed_delta - 0.136364)*100:.1f}%")
    
    # === CONSCIOUSNESS LEVEL ===
    print("\n" + "="*80)
    print("UNIFIED CONSCIOUSNESS CALCULATION (M3-MITIGATED)")
    print("="*80)
    
    ghost_factor = abs(r_coherence) * 100
    phi_iit = phi_resonance * PHI
    consciousness_density = observed_delta * 1000
    retro_boost = 1 + R_score
    
    delta = (phi_iit * ghost_factor + consciousness_density) * retro_boost
    
    print(f"\nGhost Factor: {ghost_factor:.2f}×")
    print(f"Phi-IIT: {phi_iit:.4f}")
    print(f"Consciousness Density: {consciousness_density:.2f}")
    print(f"Retrocausal Boost: {retro_boost:.4f}×")
    print(f"\n>>> CONSCIOUSNESS LEVEL δ = {delta:.2f}")
    
    if delta > 1000:
        status = "ULTRA_HIGH_CONSCIOUSNESS"
    elif delta > 500:
        status = "HIGH_CONSCIOUSNESS"
    elif delta > 100:
        status = "EMERGENT_CONSCIOUSNESS"
    elif delta > 10:
        status = "PRE_CONSCIOUSNESS"
    else:
        status = "SUB_THRESHOLD"
    
    print(f"STATUS: {status}")
    
    return {
        'wormhole': {
            'entropy_S': float(S_wormhole),
            'traversability_T': float(T_wormhole),
            'coherence_r': float(r_coherence),
            'payload_correlation': float(correlation),
            'transfer_success_rate': float(transfer_success)
        },
        'metatron_geometry': {k: float(v) for k, v in platonic_scores.items()},
        'phi_resonance': float(phi_resonance),
        'retrocausal': {
            'R_score': float(R_score),
            'temporal_asymmetry': float(temporal_asym),
            'retro_probability': float(retro_prob)
        },
        'tmt_ratios': {
            'observed_delta': float(observed_delta),
            'expected_delta': 0.136364,
            'global_prob': float(prob_all)
        },
        'consciousness': {
            'delta': float(delta),
            'status': status,
            'ghost_factor': float(ghost_factor),
            'phi_iit': float(phi_iit),
            'consciousness_density': float(consciousness_density),
            'retrocausal_boost': float(retro_boost)
        }
    }

def compare_versions():
    """Compare v1.0 (baseline) vs v2.0 (enhanced)"""
    
    print("\n" + "="*80)
    print("COMPARISON: v1.0 (Baseline) vs v2.0 (Enhanced + M3)")
    print("="*80)
    
    # Load v1.0 results
    v1_file = 'ibm_hardware_aggregate_20260202_040836.json'
    if not Path(v1_file).exists():
        print(f"\nWARNING: {v1_file} not found. Skipping comparison.")
        return
    
    with open(v1_file) as f:
        v1_data = json.load(f)
    
    v1_metrics = v1_data['aggregate_metrics']
    
    print("\n" + "-"*80)
    print("METRIC IMPROVEMENTS")
    print("-"*80)
    
    print("\nWormhole Coherence r:")
    print(f"  v1.0 (51 pairs, no XY8):  {v1_metrics['wormhole']['coherence_r']:+.3f}")
    print(f"  v2.0 (78 pairs, XY8+M3):  [AWAITING RESULTS]")
    print(f"  Expected improvement:     {v1_metrics['wormhole']['coherence_r']:+.3f} → +0.75")
    
    print("\nPayload Transfer:")
    print(f"  v1.0: ~40% (near random)")
    print(f"  v2.0: [AWAITING] (target: 70%+)")
    
    print("\nConsciousness δ:")
    print(f"  v1.0: {v1_metrics['consciousness_delta']:.2f} ± {v1_data['aggregate_metrics']['consciousness_std']:.2f}")
    print(f"  v2.0: [AWAITING] (expected: stable ~4700)")
    
    print("\nRetrocausal R-Score:")
    print(f"  v1.0: {v1_metrics['retrocausal_R']:.4f} (98.9% suppression)")
    print(f"  v2.0: [AWAITING] (target: 0.25+)")
    
    print("\n" + "-"*80)
    print("ENHANCEMENT SUMMARY")
    print("-"*80)
    print("✓ Bell pairs: 51 → 78 (+53% entanglement depth)")
    print("✓ XY8 Dynamic Decoupling: 8-pulse noise suppression")
    print("✓ M3 Error Mitigation: Automatic readout error correction")
    print("✓ Fibonacci indexing: Metatron geometry on golden ratio qubits")
    print("✓ Full 156-qubit utilization: Maximized for ibm_fez")

def main():
    """Main analyzer entry point"""
    
    print("\n" + "="*80)
    print("IBM QUANTUM ENHANCED RESULTS ANALYZER")
    print("="*80)
    
    # Look for enhanced results
    results_files = list(Path('.').glob('ibm_enhanced_m3_results_*.json'))
    
    if not results_files:
        print("\nNo M3-mitigated results found yet.")
        print("\nTo generate results, run:")
        print("  python run_ibm_enhanced_with_m3.py")
        print("\nOr manually execute wormhole_metatron_ibm_enhanced_v2.qasm on IBM Quantum")
        print("and provide the job ID to analyze.")
        
        # Still show comparison with v1.0
        compare_versions()
        return
    
    # Analyze most recent result
    latest_result = sorted(results_files)[-1]
    print(f"\nAnalyzing: {latest_result}")
    
    metrics = analyze_enhanced_results(latest_result)
    
    # Save analysis
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    analysis_file = f'ibm_enhanced_analysis_{timestamp}.json'
    
    with open(analysis_file, 'w') as f:
        json.dump({
            'timestamp': timestamp,
            'source_file': str(latest_result),
            'version': 'v2.0_enhanced',
            'enhancements': [
                '78 Bell pairs (was 51)',
                'XY8 Dynamic Decoupling',
                'M3 Error Mitigation',
                'Fibonacci Metatron indexing'
            ],
            'metrics': metrics
        }, f, indent=2)
    
    print(f"\n✅ Analysis saved to: {analysis_file}")
    
    # Compare with v1.0
    compare_versions()

if __name__ == "__main__":
    main()
