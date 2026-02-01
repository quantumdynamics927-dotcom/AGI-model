import json, math
from pathlib import Path

search_paths = [Path(r"e:/AGI model/Boveda_Cuantica/logs_resonancia"), Path(r"e:/AGI model/TMT-OS/singularity")]
report = {'checked': [], 'issues': []}

def check_obj(obj, path=''):
    issues = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            issues += check_obj(v, f"{path}/{k}" if path else k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            issues += check_obj(v, f"{path}[{i}]")
    elif isinstance(obj, (int, float)):
        try:
            if isinstance(obj, float) and math.isnan(obj):
                issues.append((path, 'NaN', obj))
            if isinstance(obj, float) and math.isinf(obj):
                issues.append((path, 'Infinity', obj))
        except Exception:
            pass
    return issues

for sp in search_paths:
    if not sp.exists():
        continue
    for p in sp.rglob('*.json'):
        # Skip the report file itself to avoid self-reporting
        if p.name == 'singularity_nan_inf_report.json':
            continue
        try:
            with open(p, 'r') as f:
                data = json.load(f)
        except Exception as e:
            report['checked'].append({'file': str(p), 'error': str(e)})
            continue
        report['checked'].append({'file': str(p), 'status': 'loaded'})
        iss = check_obj(data)
        if iss:
            for path, typ, val in iss:
                # Serialize problematic numeric values safely
                safe_val = val
                try:
                    if isinstance(val, float):
                        if math.isinf(val):
                            safe_val = 'Infinity'
                        elif math.isnan(val):
                            safe_val = 'NaN'
                except Exception:
                    safe_val = str(val)
                report['issues'].append({'file': str(p), 'path': path, 'type': typ, 'value': safe_val})

report_path = Path(r"e:/AGI model/Boveda_Cuantica/logs_resonancia/singularity_nan_inf_report.json")
with open(report_path, 'w') as f:
    json.dump(report, f, indent=2, default=str)
print('Sweep complete: report written to', report_path)
