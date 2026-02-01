import json
from pathlib import Path

vault_dir = Path(r"e:/AGI model/Boveda_Cuantica/logs_resonancia")
modified = []
for p in vault_dir.glob('*.json'):
    try:
        with open(p, 'r') as f:
            data = json.load(f)
    except Exception as e:
        continue
    changed = False
    ss = data.get('singularity_state')
    if ss and 'biomimetic_metrics' in ss:
        bm = ss['biomimetic_metrics']
        for k, v in list(bm.items()):
            # Only replace raw Infinity values
            if isinstance(v, float) and (v == float('inf')):
                bm[k] = {"value": None, "infinite": True}
                changed = True
        if changed:
            data['singularity_state']['biomimetic_metrics'] = bm
            with open(p, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            modified.append(str(p))

print('Modified files:', modified)