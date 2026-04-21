"""Verify reproducibility and pseudo-ablation risks"""
import json

with open('response_audit_results/response_traces.json') as f:
    traces = json.load(f)

print('=' * 80)
print('REPRODUCIBILITY CHECK (same seed, same config)')
print('=' * 80)

# Check if same seed produces same trace
for config_id in ['C0', 'C1', 'C2']:
    if config_id in traces:
        config_traces = traces[config_id]
        
        # Group by seed
        by_seed = {}
        for t in config_traces:
            seed = t['seed']
            if seed not in by_seed:
                by_seed[seed] = []
            by_seed[seed].append(t)
        
        print(f'\n{config_id}:')
        for seed, seed_traces in by_seed.items():
            if len(seed_traces) > 1:
                # Compare traces with same seed
                t1, t2 = seed_traces[0], seed_traces[1]
                same_route = t1['visited_states'] == t2['visited_states']
                same_transitions = t1['selected_transitions'] == t2['selected_transitions']
                print(f'  seed {seed}: route_match={same_route}, transition_match={same_transitions}')

print('\n' + '=' * 80)
print('PSEUDO-ABLATION CHECK')
print('=' * 80)

# Check that C1 and C2 differ ONLY in scorer
c1_traces = traces.get('C1', [])
c2_traces = traces.get('C2', [])

if c1_traces and c2_traces:
    # Find traces with same prompt_id and seed
    for c1 in c1_traces:
        for c2 in c2_traces:
            if c1['prompt_id'] == c2['prompt_id'] and c1['seed'] == c2['seed']:
                prompt_id = c1['prompt_id']
                seed = c1['seed']
                print(f'\nPrompt {prompt_id}, seed {seed}:')
                print(f'  C1 edge_score_method: {c1["edge_score_method"]}')
                print(f'  C2 edge_score_method: {c2["edge_score_method"]}')
                c1_has_quantum = any(len(qs) > 0 for qs in c1["quantum_scores"])
                c2_has_quantum = any(len(qs) > 0 for qs in c2["quantum_scores"])
                print(f'  C1 quantum_scores: {c1_has_quantum}')
                print(f'  C2 quantum_scores: {c2_has_quantum}')
                routes_differ = c1["visited_states"] != c2["visited_states"]
                print(f'  Routes differ: {routes_differ}')
                print(f'  Same prompt handling: {c1["prompt_id"] == c2["prompt_id"]}')
                print(f'  Same seed: {c1["seed"] == c2["seed"]}')
                print(f'  Same initial_vertex: {c1["initial_vertex"] == c2["initial_vertex"]}')
                break
        break

print('\n' + '=' * 80)
print('ABLATION ISOLATION VERIFICATION')
print('=' * 80)

# Verify that ONLY the scorer differs between C1 and C2
print('\nChecking that C1 and C2 differ ONLY in scorer:')

c1_sample = c1_traces[0] if c1_traces else None
c2_sample = c2_traces[0] if c2_traces else None

if c1_sample and c2_sample:
    # These should be the same
    same_prompt = c1_sample['prompt_id'] == c2_sample['prompt_id']
    same_seed = c1_sample['seed'] == c2_sample['seed']
    same_initial = c1_sample['initial_vertex'] == c2_sample['initial_vertex']
    same_model = c1_sample['model_id'] == c2_sample['model_id']
    same_temp = c1_sample['temperature'] == c2_sample['temperature']
    
    # These should differ
    diff_method = c1_sample['edge_score_method'] != c2_sample['edge_score_method']
    diff_quantum = any(len(qs) > 0 for qs in c2_sample["quantum_scores"]) and not any(len(qs) > 0 for qs in c1_sample["quantum_scores"])
    
    print(f'  Same prompt_id: {same_prompt} (expected: True)')
    print(f'  Same seed: {same_seed} (expected: True)')
    print(f'  Same initial_vertex: {same_initial} (expected: True)')
    print(f'  Same model_id: {same_model} (expected: True)')
    print(f'  Same temperature: {same_temp} (expected: True)')
    print(f'  Different edge_score_method: {diff_method} (expected: True)')
    print(f'  C2 has quantum_scores, C1 does not: {diff_quantum} (expected: True)')
    
    all_pass = same_prompt and same_seed and same_initial and same_model and same_temp and diff_method and diff_quantum
    print(f'\n  ABLATION ISOLATION: {"PASS" if all_pass else "FAIL"}')

print('\n' + '=' * 80)