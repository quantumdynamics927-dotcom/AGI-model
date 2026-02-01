import json
from pathlib import Path

base = Path('assets/pinata_downloads/Pinata_Download/Pinata_Download')
meta_files = sorted(list(base.glob('**/*metadata*.json')) + list(base.glob('phi_consciousness_*.json')) + list(base.glob('*.json')))

report = {
    'checked': 0,
    'valid': 0,
    'invalid': 0,
    'errors': []
}

seen = set()
for p in meta_files:
    # limit to files inside root folder only
    try:
        if not p.is_file():
            continue
        text = p.read_text(encoding='utf-8')
        data = json.loads(text)
        report['checked'] += 1
        # heuristics: look for name/description/image fields
        name = data.get('name')
        image = data.get('image') or data.get('image_url') or data.get('image_url')
        desc = data.get('description')
        problems = []
        if not name:
            problems.append('missing name')
        if not image:
            problems.append('missing image')
        else:
            # check if image is ipfs:// or a cid or filename
            if image.startswith('ipfs://'):
                pass
            elif image.startswith('Qm') or image.startswith('baf'):
                pass
            else:
                # possibly local filename; check for file existence in folder
                img_path = base / image
                if not img_path.exists():
                    problems.append(f'image references missing file: {image}')
        if problems:
            report['invalid'] += 1
            report['errors'].append({'file': str(p), 'problems': problems})
        else:
            report['valid'] += 1
    except Exception as e:
        report['invalid'] += 1
        report['errors'].append({'file': str(p), 'error': repr(e)})

print('Validation report:')
print(json.dumps(report, indent=2))

out = base / 'metadata_validation_report.json'
out.write_text(json.dumps(report, indent=2), encoding='utf-8')
print('Wrote report to', out)
