import json
import math
from pathlib import Path

# Paths
sing_path = Path(r"e:/AGI model/TMT-OS/singularity/biomimetic_singularity_state.json")
vault_path = Path(r"e:/AGI model/Boveda_Cuantica/logs_resonancia/biomimetic_singularity_state.json")
report_path = Path(r"e:/AGI model/Boveda_Cuantica/logs_resonancia/biomimetic_singularity_diagnostic.json")
backup_path = vault_path.with_suffix('.json.bak')

if not sing_path.exists():
    print(f"Source state not found: {sing_path}")
    raise SystemExit(1)

with open(sing_path, 'r') as f:
    state = json.load(f)

vec = state.get('last_results', {}).get('final_consciousness_vector')
if vec is None:
    print('No final_consciousness_vector found in source state')
    raise SystemExit(1)

# Compute norms and normalized vector
norm = math.sqrt(sum((float(x) ** 2) for x in vec))
normalized = [float(x) / norm for x in vec] if norm > 0 else [0.0 for _ in vec]

# Create diagnostic object
diagnostic = {
    'source': str(sing_path),
    'copied_to_vault': False,
    'original_vector': vec,
    'norm': norm,
    'normalized_vector': normalized,
}

# Backup existing vault file if present
if vault_path.exists():
    vault_path.replace(backup_path)
    print(f"Backed up existing vault state to: {backup_path}")

# Write normalized vector into a copy of state and save to vault
state_copy = state.copy()
state_copy['last_results'] = dict(state_copy.get('last_results', {}))
state_copy['last_results']['final_consciousness_vector_normalized'] = normalized

vault_path.parent.mkdir(parents=True, exist_ok=True)
with open(vault_path, 'w') as f:
    json.dump(state_copy, f, indent=2)
print(f"Wrote normalized state to vault: {vault_path}")

diagnostic['copied_to_vault'] = True
with open(report_path, 'w') as f:
    json.dump(diagnostic, f, indent=2)
print(f"Diagnostic written to: {report_path}")

# Print brief summary
print('\nSummary:')
print(f"  norm = {norm:.6f}")
print(f"  normalized vector (first 3 elements): {normalized[:3]}")
print('Done.')