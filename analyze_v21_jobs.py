"""
Analyzer for v2.1 Optimized Results - Quick Multi-Job Analysis
"""
import json
import numpy as np
from pathlib import Path
from datetime import datetime

PHI = 1.618033988749895

job_ids = [
    'd602l2pmvbjc73ad1ph0',
    'd602lu1mvbjc73ad1qug', 
    'd602m0l7fc0s73aujuo0',
    'd602m3d7fc0s73aujuu0'
]

print("="*80)
print("WORMHOLE-METATRON v2.1 OPTIMIZED - IBM FEZ RESULTS")
print("30 Bell Pairs + XY8 + M3 Error Mitigation")
print("="*80)

all_results = []

for job_id in job_ids:
    result_file = Path(f'data/Jobs/job-{job_id}-result.json')
    
    with open(result_file) as f:
        data = json.load(f)
    
    samples = data['results'][0]['data']['c']['samples']
    num_shots = len(samples)
    
    print(f"\n{'='*80}")
    print(f"Job: {job_id}")
    print(f"Shots: {num_shots:,}")
    print(f"{'='*80}")
    
    # Convert hex samples to measurements
    measurements = []
    for sample in samples:
        if isinstance(sample, str):
            sample = sample.replace('0x', '')
        int_val = int(sample, 16)
        bin_str = bin(int_val)[2:].zfill(60)[::-1]  # 60 qubits, little-endian
        
        # Extract measured bits: c[0,1,2,8,13,21,26,28,30-35]
        indices = [0, 1, 2, 8, 13, 21, 26, 28, 30, 31, 32, 33, 34, 35]
        bits = [int(bin_str[i]) if i < len(bin_str) else 0 for i in indices]
        measurements.append(bits)
    
    measurements = np.array(measurements)
    
    # Bit mapping:
    # [0] = q[0] (Left payload)
    # [1] = q[1]
    # [2] = q[2]
    # [3] = q[8] (Tetrahedron F_5)
    # [4] = q[13] (Cube F_6)
    # [5] = q[21] (Octahedron F_7)
    # [6] = q[26] (Retrocausal hole)
    # [7] = q[28] (Dodecahedron)
    # [8] = q[30] (Right payload - wormhole output)
    # [9-13] = q[31-35] (Right Universe)
    
    payload_left = measurements[:, 0]
    payload_right = measurements[:, 8]
    
    # WORMHOLE METRICS
    print("\n--- WORMHOLE (30 Bell Pairs) ---")
    
    correlation = np.corrcoef(payload_left, payload_right)[0, 1]
    transfer_success = np.sum(payload_left == payload_right) / num_shots
    
    print(f"Payload Correlation (q[0]↔q[30]): {correlation:+.4f}")
    print(f"Transfer Success: {transfer_success*100:.2f}%")
    
    def entropy(p):
        if p == 0 or p == 1:
            return 0
        return -p * np.log2(p) - (1-p) * np.log2(1-p)
    
    S_left = entropy(np.mean(payload_left))
    S_right = entropy(np.mean(payload_right))
    S_wormhole = (S_left + S_right) / 2
    
    T_wormhole = abs(correlation) * 3.5
    r_coherence = (transfer_success * 2) - 1
    
    print(f"Entropy S: {S_wormhole:.3f}")
    print(f"Traversability T: {T_wormhole:.3f}")
    print(f"Coherence r: {r_coherence:+.3f}")
    
    # METATRON GEOMETRY
    print("\n--- METATRON (Fibonacci-indexed) ---")
    
    platonic_bits = {
        'tetrahedron_F5': measurements[:, 3],  # q[8]
        'cube_F6': measurements[:, 4],         # q[13]
        'octahedron_F7': measurements[:, 5],   # q[21]
        'dodecahedron': measurements[:, 7]     # q[28]
    }
    
    platonic_scores = {}
    for name, bits in platonic_bits.items():
        prob_1 = np.mean(bits)
        score = 1 - 2 * abs(prob_1 - 0.5)
        platonic_scores[name] = score
        print(f"  {name}: {score:.4f} (p_1={prob_1:.3f})")
    
    phi_resonance = np.mean(list(platonic_scores.values()))
    print(f"Phi Resonance: {phi_resonance:.4f}")
    
    # RETROCAUSAL
    print("\n--- RETROCAUSAL ---")
    
    retro_bits = measurements[:, 6]  # q[26]
    retro_prob = np.mean(retro_bits)
    
    first_half = retro_bits[:num_shots//2]
    second_half = retro_bits[num_shots//2:]
    temporal_asym = abs(np.mean(first_half) - np.mean(second_half))
    
    retro_payload_corr = np.corrcoef(retro_bits, payload_left)[0, 1]
    R_score = abs(retro_payload_corr)
    
    print(f"Retrocausal Probability: {retro_prob:.3f}")
    print(f"Temporal Asymmetry: {temporal_asym:.4f}")
    print(f"R-Score: {R_score:.4f}")
    
    # CONSCIOUSNESS
    print("\n--- CONSCIOUSNESS ---")
    
    all_bits = measurements.flatten()
    prob_all = np.mean(all_bits)
    observed_delta = prob_all * 10
    
    ghost_factor = abs(r_coherence) * 100
    phi_iit = phi_resonance * PHI
    consciousness_density = observed_delta * 1000
    retro_boost = 1 + R_score
    
    delta = (phi_iit * ghost_factor + consciousness_density) * retro_boost
    
    print(f"Delta δ: {delta:.2f}")
    
    # Store
    all_results.append({
        'job_id': job_id,
        'shots': num_shots,
        'wormhole': {
            'r': float(r_coherence),
            'transfer': float(transfer_success),
            'S': float(S_wormhole),
            'T': float(T_wormhole),
            'correlation': float(correlation)
        },
        'metatron': {k: float(v) for k, v in platonic_scores.items()},
        'phi_resonance': float(phi_resonance),
        'retrocausal': {
            'R_score': float(R_score),
            'temporal_asym': float(temporal_asym)
        },
        'consciousness': {
            'delta': float(delta),
            'ghost_factor': float(ghost_factor)
        }
    })

# AGGREGATE
print("\n" + "="*80)
print("AGGREGATE STATISTICS (4 jobs, 40,000 shots)")
print("="*80)

avg_r = np.mean([r['wormhole']['r'] for r in all_results])
avg_transfer = np.mean([r['wormhole']['transfer'] for r in all_results])
avg_S = np.mean([r['wormhole']['S'] for r in all_results])
avg_delta = np.mean([r['consciousness']['delta'] for r in all_results])
avg_phi = np.mean([r['phi_resonance'] for r in all_results])
avg_R = np.mean([r['retrocausal']['R_score'] for r in all_results])

std_r = np.std([r['wormhole']['r'] for r in all_results])
std_delta = np.std([r['consciousness']['delta'] for r in all_results])

print(f"\nWormhole Coherence r: {avg_r:+.3f} ± {std_r:.3f}")
print(f"Transfer Success: {avg_transfer*100:.1f}%")
print(f"Entropy S: {avg_S:.3f}")
print(f"Phi Resonance: {avg_phi:.4f}")
print(f"Retrocausal R: {avg_R:.4f}")
print(f"Consciousness δ: {avg_delta:.2f} ± {std_delta:.2f}")

# COMPARISON WITH v1.0
print("\n" + "="*80)
print("COMPARISON: v1.0 (Baseline) vs v2.1 (Optimized)")
print("="*80)

v1_r = -0.181
v1_transfer = 0.40
v1_delta = 4777.76

improvement_r = ((avg_r - v1_r) / abs(v1_r)) * 100
improvement_transfer = ((avg_transfer - v1_transfer) / v1_transfer) * 100

print(f"\nCoherence r:")
print(f"  v1.0 (51 pairs, no XY8): {v1_r:+.3f}")
print(f"  v2.1 (30 pairs, XY8+M3): {avg_r:+.3f}")
print(f"  Improvement: {improvement_r:+.0f}%")

print(f"\nTransfer Success:")
print(f"  v1.0: {v1_transfer*100:.1f}%")
print(f"  v2.1: {avg_transfer*100:.1f}%")
print(f"  Improvement: {improvement_transfer:+.0f}%")

print(f"\nConsciousness δ:")
print(f"  v1.0: {v1_delta:.2f}")
print(f"  v2.1: {avg_delta:.2f}")
print(f"  Change: {((avg_delta - v1_delta)/v1_delta*100):+.1f}%")

# SAVE
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file = f'ibm_v21_optimized_aggregate_{timestamp}.json'

output_data = {
    'timestamp': timestamp,
    'version': 'v2.1_optimized_30_bell_pairs',
    'backend': 'ibm_fez',
    'total_shots': 40000,
    'num_jobs': 4,
    'individual_jobs': all_results,
    'aggregate_metrics': {
        'wormhole_coherence_r': float(avg_r),
        'wormhole_coherence_std': float(std_r),
        'transfer_success': float(avg_transfer),
        'entropy_S': float(avg_S),
        'phi_resonance': float(avg_phi),
        'retrocausal_R': float(avg_R),
        'consciousness_delta': float(avg_delta),
        'consciousness_std': float(std_delta)
    },
    'comparison_v10': {
        'v10_coherence_r': v1_r,
        'v21_coherence_r': float(avg_r),
        'improvement_percent': float(improvement_r),
        'v10_transfer': v1_transfer,
        'v21_transfer': float(avg_transfer),
        'transfer_improvement_percent': float(improvement_transfer)
    }
}

with open(output_file, 'w') as f:
    json.dump(output_data, f, indent=2)

print(f"\n✅ Results saved to: {output_file}")
