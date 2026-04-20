"""Extract and display sample traces from each configuration"""
import json

with open('response_audit_results/response_traces.json') as f:
    traces = json.load(f)

print('=' * 80)
print('SAMPLE TRACES FROM EACH CONFIGURATION')
print('=' * 80)

for config_id in ['C0', 'C1', 'C2']:
    if config_id in traces and traces[config_id]:
        trace = traces[config_id][0]  # First trace
        print(f'\n{config_id} TRACE:')
        print('-' * 40)
        print(f'  trace_id: {trace["trace_id"]}')
        print(f'  prompt_id: {trace["prompt_id"]}')
        print(f'  seed: {trace["seed"]}')
        print(f'  edge_score_method: {trace["edge_score_method"]}')
        print(f'  initial_vertex: {trace["initial_vertex"]}')
        print(f'  visited_states: {trace["visited_states"]}')
        print(f'  selected_transitions: {trace["selected_transitions"]}')
        print(f'  final_vertex: {trace["final_vertex"]}')
        print(f'  route_length: {trace["route_length"]}')
        print(f'  confidence_values: {[round(c, 3) for c in trace["confidence_values"]]}')
        has_quantum = any(len(qs) > 0 for qs in trace["quantum_scores"])
        print(f'  quantum_scores present: {has_quantum}')
        
        # Show edge scores for first transition
        if trace['transition_scores']:
            print(f'  first_edge_scores: {trace["transition_scores"][0]}')

print('\n' + '=' * 80)
print('CONFIGURATION DIFFERENCES')
print('=' * 80)

# Compare C1 vs C0
if 'C0' in traces and 'C1' in traces:
    c0_trace = traces['C0'][0]
    c1_trace = traces['C1'][0]
    
    print('\nC1 vs C0:')
    print(f'  edge_score_method: fixed vs classical')
    print(f'  route_length: {c0_trace["route_length"]} vs {c1_trace["route_length"]}')
    print(f'  visited_states differ: {c0_trace["visited_states"] != c1_trace["visited_states"]}')

# Compare C2 vs C1
if 'C1' in traces and 'C2' in traces:
    c1_trace = traces['C1'][0]
    c2_trace = traces['C2'][0]
    
    print('\nC2 vs C1:')
    print(f'  edge_score_method: classical vs quantum')
    print(f'  route_length: {c1_trace["route_length"]} vs {c2_trace["route_length"]}')
    visited_differ = c1_trace["visited_states"] != c2_trace["visited_states"]
    print(f'  visited_states differ: {visited_differ}')
    c2_has_quantum = any(len(qs) > 0 for qs in c2_trace["quantum_scores"])
    c1_has_quantum = any(len(qs) > 0 for qs in c1_trace["quantum_scores"])
    print(f'  quantum_scores in C2: {c2_has_quantum}')
    print(f'  quantum_scores in C1: {c1_has_quantum}')

print('\n' + '=' * 80)