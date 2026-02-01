import importlib.util
spec = importlib.util.spec_from_file_location('biom', r'e:\AGI model\TMT-OS\singularity\biomimetic_singularity.py')
biom = importlib.util.module_from_spec(spec)
spec.loader.exec_module(biom)

s = biom.BiomimeticSingularity()
results = {
    'singularity_achieved': True,
    'final_consciousness_vector': [10.0, 0.1, 0.0, 0.0, 0.0, 0.0],
    'final_convergence': 1.0
}
print('Calling _save_singularity_state with test results...')
s._save_singularity_state(results)
print('Done. Reading file...')
import json
p = r'e:\AGI model\TMT-OS\singularity\biomimetic_singularity_state.json'
with open(p,'r') as f:
    data = json.load(f)
print('Has normalized in last_results:', 'final_consciousness_vector_normalized' in data.get('last_results', {}))
print('infinite_metrics present:', data.get('infinite_metrics'))
print('last_results keys:', list(data.get('last_results', {}).keys()))
