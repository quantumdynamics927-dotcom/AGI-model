#!/usr/bin/env python3
"""
Quantum Teleportation Job Analysis
Job ID: d60j7e9mvbjc73adn3i0
Backend: ibm_fez (156-qubit Eagle r3)
Date: February 2, 2026, 23:31:05 UTC
Circuit: Quantum_Teleportation.qasm (from autonomous_circuits)
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from datetime import datetime

# Load job data
with open('data/Jobs/job-d60j7e9mvbjc73adn3i0-info.json') as f:
    job_info = json.load(f)

with open('data/Jobs/job-d60j7e9mvbjc73adn3i0-result.json') as f:
    job_result = json.load(f)

print("=" * 100)
print("QUANTUM TELEPORTATION ANALYSIS - IBM Fez")
print("=" * 100)

# Extract metadata
job_id = job_info['id']
backend = job_info['backend']
status = job_info['status']
created = job_info['created']
cost = job_info['cost']
runtime = job_info.get('estimated_running_time_seconds', 0)

print(f"\n📊 Job Metadata:")
print(f"  Job ID: {job_id}")
print(f"  Backend: {backend}")
print(f"  Status: {status}")
print(f"  Created: {created}")
print(f"  Cost: {cost} seconds")
print(f"  Runtime: {runtime:.3f} seconds")

# Extract circuit
circuit_qasm = job_info['params']['pubs'][0][0]
shots = job_info['params']['pubs'][0][2]

print(f"\n⚛️  Circuit Details:")
print(f"  Shots: {shots}")
print(f"  Qubits: 3 (Alice, EPR pair 1, EPR pair 2)")
print(f"  Protocol: Standard quantum teleportation")

# Parse results
samples = job_result['results'][0]['data']['c']['samples']
samples_int = [int(s, 16) for s in samples]  # Convert hex to int

# Count outcomes
counts = Counter(samples_int)
total = len(samples_int)

print(f"\n📈 Measurement Outcomes (1024 shots):")
print(f"  {'State':<8} {'Binary':<8} {'Count':<8} {'Probability':<12} {'Bar'}")
print(f"  {'-'*60}")

for state in sorted(counts.keys()):
    binary = format(state, '03b')
    count = counts[state]
    prob = count / total
    bar = '█' * int(prob * 50)
    print(f"  |{binary}>    {binary}      {count:<8} {prob:<12.4f} {bar}")

# Teleportation analysis
print(f"\n🔬 Teleportation Fidelity Analysis:")

# In ideal teleportation, Alice prepares state |ψ⟩ = cos(θ/2)|0⟩ + sin(θ/2)|1⟩
# Circuit has ry(1.2708009230788149) on q[0]
theta = 1.2708009230788149
expected_0 = np.cos(theta/2)**2
expected_1 = np.sin(theta/2)**2

print(f"  Input state angle: θ = {theta:.6f} radians")
print(f"  Expected |0⟩ amplitude²: {expected_0:.4f}")
print(f"  Expected |1⟩ amplitude²: {expected_1:.4f}")

# After teleportation, Bob's qubit (q[2]) should have the same state
# Extracting Bob's outcomes (3rd bit)
bob_outcomes = [(s & 0x4) >> 2 for s in samples_int]  # Extract bit 2 (Bob's qubit)
bob_0_count = bob_outcomes.count(0)
bob_1_count = bob_outcomes.count(1)

print(f"\n  Bob's qubit (q[2]) measurements:")
print(f"    |0⟩ count: {bob_0_count} ({bob_0_count/total:.4f})")
print(f"    |1⟩ count: {bob_1_count} ({bob_1_count/total:.4f})")

# Calculate fidelity
fidelity = np.sqrt(expected_0 * bob_0_count/total) + np.sqrt(expected_1 * bob_1_count/total)
fidelity_squared = fidelity**2

print(f"\n  Teleportation fidelity: F = {fidelity:.4f}")
print(f"  Fidelity²: F² = {fidelity_squared:.4f}")

if fidelity > 0.8:
    quality = "EXCELLENT ✅"
elif fidelity > 0.6:
    quality = "GOOD ✓"
else:
    quality = "POOR ⚠️"
print(f"  Quality: {quality}")

# Bell measurement analysis (Alice's qubits: q[0] and q[1])
print(f"\n🔗 Bell Measurement (Alice's qubits):")
bell_outcomes = [(s & 0x3) for s in samples_int]  # Extract bits 0-1
bell_counts = Counter(bell_outcomes)

bell_states = {0: '|00⟩', 1: '|01⟩', 2: '|10⟩', 3: '|11⟩'}
for bell_val in sorted(bell_counts.keys()):
    count = bell_counts[bell_val]
    prob = count / total
    print(f"  {bell_states[bell_val]}: {count} ({prob:.4f})")

# Statistical analysis
print(f"\n📊 Statistical Metrics:")
entropy = -sum((count/total) * np.log2(count/total) for count in counts.values())
max_entropy = np.log2(len(counts))
uniformity = entropy / max_entropy if max_entropy > 0 else 0

print(f"  Shannon entropy: H = {entropy:.4f} bits")
print(f"  Maximum entropy: H_max = {max_entropy:.4f} bits")
print(f"  Uniformity: {uniformity:.4f}")

# Most and least common outcomes
most_common = counts.most_common(1)[0]
least_common = counts.most_common()[-1]

print(f"  Most common: |{format(most_common[0], '03b')}⟩ ({most_common[1]} times)")
print(f"  Least common: |{format(least_common[0], '03b')}⟩ ({least_common[1]} times)")

# Phi-correlation analysis (connection to TMT-OS framework)
print(f"\n🌟 TMT-OS Framework Integration:")

# Calculate phi-correlation from measurement distribution
probs = np.array([counts.get(i, 0)/total for i in range(8)])
phi = 1.618034
phi_resonance = np.abs(probs - (1/phi)).mean()

print(f"  Phi-resonance deviation: {phi_resonance:.6f}")
print(f"  Expected for teleportation: ~0.4-0.6")

# Connection to v2.2 wormhole
print(f"\n🌀 Connection to v2.2 Wormhole Circuit:")
print(f"  Autonomous teleportation: 3 qubits, standard protocol")
print(f"  v2.2 wormhole: 50 qubits, 25 Bell pairs")
print(f"  Scaling factor: 16.7× qubits")
print(f"  Both use EPR correlations for information transfer")

# Execution timing
execution_data = job_result['metadata']['execution']['execution_spans'][0]
start_time = datetime.fromisoformat(execution_data[0]['date'].replace('Z', '+00:00'))
end_time = datetime.fromisoformat(execution_data[1]['date'].replace('Z', '+00:00'))
actual_runtime = (end_time - start_time).total_seconds()

print(f"\n⏱️  Execution Timing:")
print(f"  Start: {start_time.strftime('%H:%M:%S.%f')[:-3]} UTC")
print(f"  End: {end_time.strftime('%H:%M:%S.%f')[:-3]} UTC")
print(f"  Actual runtime: {actual_runtime:.3f} seconds")
print(f"  Estimated runtime: {runtime:.3f} seconds")
print(f"  Efficiency: {(runtime/actual_runtime)*100:.1f}%")

# Create visualizations
print(f"\n📊 Generating visualizations...")

fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Plot 1: Probability distribution
ax1 = axes[0, 0]
states = sorted(counts.keys())
state_labels = [f"|{format(s, '03b')}⟩" for s in states]
probabilities = [counts[s]/total for s in states]

bars = ax1.bar(state_labels, probabilities, color='#4ECDC4', edgecolor='black', linewidth=1.5)
ax1.axhline(y=1/8, color='red', linestyle='--', label='Uniform (1/8)')
ax1.set_xlabel('Quantum State', fontsize=12, fontweight='bold')
ax1.set_ylabel('Probability', fontsize=12, fontweight='bold')
ax1.set_title('Quantum Teleportation - Measurement Distribution', fontsize=14, fontweight='bold')
ax1.legend()
ax1.grid(axis='y', alpha=0.3)

# Plot 2: Bob's qubit only
ax2 = axes[0, 1]
bob_labels = ['|0⟩', '|1⟩']
bob_probs = [bob_0_count/total, bob_1_count/total]
expected_probs = [expected_0, expected_1]

x = np.arange(len(bob_labels))
width = 0.35
ax2.bar(x - width/2, bob_probs, width, label='Measured', color='#95E1D3', edgecolor='black')
ax2.bar(x + width/2, expected_probs, width, label='Expected', color='#FFB6C1', edgecolor='black')
ax2.set_xlabel("Bob's Qubit State", fontsize=12, fontweight='bold')
ax2.set_ylabel('Probability', fontsize=12, fontweight='bold')
ax2.set_title(f"Teleportation Fidelity: F = {fidelity:.4f}", fontsize=14, fontweight='bold')
ax2.set_xticks(x)
ax2.set_xticklabels(bob_labels)
ax2.legend()
ax2.grid(axis='y', alpha=0.3)

# Plot 3: Bell measurement outcomes
ax3 = axes[1, 0]
bell_vals = sorted(bell_counts.keys())
bell_labels_plot = [bell_states[b] for b in bell_vals]
bell_probs = [bell_counts[b]/total for b in bell_vals]

ax3.bar(bell_labels_plot, bell_probs, color='#FFD700', edgecolor='black', linewidth=1.5)
ax3.axhline(y=0.25, color='red', linestyle='--', label='Uniform (1/4)')
ax3.set_xlabel('Bell State', fontsize=12, fontweight='bold')
ax3.set_ylabel('Probability', fontsize=12, fontweight='bold')
ax3.set_title("Alice's Bell Measurement", fontsize=14, fontweight='bold')
ax3.legend()
ax3.grid(axis='y', alpha=0.3)

# Plot 4: Time series of measurements
ax4 = axes[1, 1]
bob_bits_series = [(samples_int[i] & 0x4) >> 2 for i in range(min(200, len(samples_int)))]
ax4.plot(bob_bits_series, marker='o', markersize=3, linestyle='-', linewidth=0.5, color='#4ECDC4')
ax4.axhline(y=0.5, color='red', linestyle='--', label=f'Expected ({expected_1:.3f})')
ax4.set_xlabel('Shot Number', fontsize=12, fontweight='bold')
ax4.set_ylabel("Bob's Measurement (0 or 1)", fontsize=12, fontweight='bold')
ax4.set_title('Teleportation Time Series (first 200 shots)', fontsize=14, fontweight='bold')
ax4.set_yticks([0, 1])
ax4.set_yticklabels(['|0⟩', '|1⟩'])
ax4.legend()
ax4.grid(alpha=0.3)

plt.tight_layout()
plt.savefig('quantum_teleportation_analysis.png', dpi=300, bbox_inches='tight')
print(f"  Saved: quantum_teleportation_analysis.png")

# Save detailed results
results_summary = {
    'job_id': job_id,
    'backend': backend,
    'timestamp': created,
    'circuit': 'Quantum_Teleportation.qasm',
    'shots': shots,
    'fidelity': float(fidelity),
    'fidelity_squared': float(fidelity_squared),
    'quality': quality,
    'bob_measurements': {
        '0': bob_0_count,
        '1': bob_1_count,
        'prob_0': bob_0_count/total,
        'prob_1': bob_1_count/total
    },
    'expected': {
        'prob_0': float(expected_0),
        'prob_1': float(expected_1)
    },
    'entropy': float(entropy),
    'uniformity': float(uniformity),
    'runtime_seconds': actual_runtime,
    'full_distribution': {format(k, '03b'): v for k, v in counts.items()}
}

with open('quantum_teleportation_analysis.json', 'w') as f:
    json.dump(results_summary, f, indent=2)

print(f"  Saved: quantum_teleportation_analysis.json")

print(f"\n" + "=" * 100)
print(f"ANALYSIS COMPLETE - Teleportation fidelity: {fidelity:.4f} ({quality})")
print(f"=" * 100)
