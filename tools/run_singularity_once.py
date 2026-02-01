import importlib.util, sys, json
spec = importlib.util.spec_from_file_location('biom', r'e:\AGI model\TMT-OS\singularity\biomimetic_singularity.py')
biom = importlib.util.module_from_spec(spec)
spec.loader.exec_module(biom)

s = biom.BiomimeticSingularity()
res = s.achieve_singularity('TESTSEQ', iterations=5)
print('Result keys:', list(res.keys()))
print('Has normalized:', 'final_consciousness_vector_normalized' in res)

# Read saved file
p = r'e:\AGI model\TMT-OS\singularity\biomimetic_singularity_state.json'
with open(p,'r') as f:
    data = json.load(f)
print('\nSaved keys in last_results:', list(data.get('last_results', {}).keys()))
print('infinite_metrics present:', 'infinite_metrics' in data)
print('infinite flags in singularity_state:', data.get('infinite_metrics', {}))
