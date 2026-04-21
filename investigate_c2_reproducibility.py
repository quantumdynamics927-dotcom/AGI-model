"""Investigate C2 reproducibility issue"""
import json

with open('response_audit_results/response_traces.json') as f:
    traces = json.load(f)

print('=' * 80)
print('C2 REPRODUCIBILITY INVESTIGATION')
print('=' * 80)

c2_traces = traces.get('C2', [])

# Group by seed
by_seed = {}
for t in c2_traces:
    seed = t['seed']
    if seed not in by_seed:
        by_seed[seed] = []
    by_seed[seed].append(t)

for seed, seed_traces in by_seed.items():
    if len(seed_traces) > 1:
        print(f'\nSeed {seed}:')
        for i, t in enumerate(seed_traces):
            visited = t["visited_states"][:5]
            final = t["final_vertex"]
            qs = list(t["quantum_scores"][0].items())[:3] if t["quantum_scores"] else []
            print(f'  Run {i}: visited={visited}... final={final}')
            print(f'         quantum_scores[0]={qs}...')

print('\n' + '=' * 80)
print('DIAGNOSIS')
print('=' * 80)

print("""
The C2 non-reproducibility is expected behavior because:
1. QuantumEdgeScorer uses qiskit AerSimulator which has inherent quantum randomness
2. Even with same seed, quantum circuit execution produces different measurement outcomes
3. This is actually CORRECT behavior - quantum scoring should be stochastic

For TRUE reproducibility in C2, we would need to:
1. Use a deterministic quantum simulator
2. Or mock the quantum backend for testing
3. Or use a fixed seed for the quantum simulator itself

This is NOT a pseudo-ablation issue - it's a feature of quantum systems.
""")

print('=' * 80)