import json
import os
from pathlib import Path
import sys
from dotenv import load_dotenv
# Ensure repo root is on sys.path so local packages (tmt_os_labs) can be imported when the script
# is executed from CI or different working directories.
load_dotenv()
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tmt_os_labs.tools.pinata_uploader import PinataClient

BASE = Path('assets/pinata_downloads/Pinata_Download/Pinata_Download')
REPORT = BASE / 'metadata_validation_report.json'
PIN_REPORT = Path('assets/pinata_downloads/pinata_sync_report.json')
OUT_DIR = BASE / 'normalized_metadata'
OUT_DIR.mkdir(parents=True, exist_ok=True)

with open(PIN_REPORT, 'r', encoding='utf-8') as f:
    pin_report = json.load(f)

# Build filename -> cid mapping (for files we downloaded / reported)
filename_to_cid = {}
for item in pin_report.get('downloaded', []):
    filename = Path(item['filename']).name
    filename_to_cid[filename] = item['cid']

# helper: try to find cid for a given image reference
def find_image_cid(ref):
    # if ipfs:// already, extract cid
    if not ref:
        return None
    if ref.startswith('ipfs://'):
        return ref[len('ipfs://'):]
    if ref.startswith('Qm') or ref.startswith('baf'):
        return ref
    # else treat as filename
    # try direct filename matching
    base = Path(ref).name
    if base in filename_to_cid:
        return filename_to_cid[base]
    # try same basename with different ext
    stem = Path(base).stem
    for ext in ['.png', '.jpg', '.jpeg', '.svg', '.gif']:
        candidate = f"{stem}{ext}"
        if candidate in filename_to_cid:
            return filename_to_cid[candidate]
    return None

pc = PinataClient()

# Load validation report to get invalid files
with open(REPORT, 'r', encoding='utf-8') as f:
    vreport = json.load(f)

processed = []

for err in vreport.get('errors', []):
    filepath = Path(err['file'])
    if not filepath.exists():
        print('Missing file in workspace, skipping:', filepath)
        continue
    print('Processing:', filepath)
    try:
        data = json.loads(filepath.read_text(encoding='utf-8'))
    except Exception as e:
        print('Failed to parse JSON:', filepath, e)
        continue
    updated = False
    notes = []
    # name
    if not data.get('name'):
        derived_name = filepath.stem.replace('_', ' ').replace('-', ' ').title()
        data['name'] = derived_name
        updated = True
        notes.append('added name')
    # description
    if not data.get('description'):
        data['description'] = f'{data.get("name")} — Normalized by TMT-OS metadata sanitizer.'
        updated = True
        notes.append('added description')
    # image
    image_ref = data.get('image') or data.get('image_url') or data.get('image_url')
    image_cid = find_image_cid(image_ref)
    if image_cid:
        ipfs_uri = f'ipfs://{image_cid}'
        if data.get('image') != ipfs_uri:
            data['image'] = ipfs_uri
            updated = True
            notes.append(f'image set to {ipfs_uri}')
    else:
        # try to find an image file with same stem
        stem = filepath.stem
        found_cid = None
        for ext in ['.png', '.jpg', '.svg']:
            candidate = f"{stem}{ext}"
            if candidate in filename_to_cid:
                found_cid = filename_to_cid[candidate]
                break
        if found_cid:
            data['image'] = f'ipfs://{found_cid}'
            updated = True
            notes.append(f'image set to ipfs://{found_cid}')
        else:
            # mark with placeholder and trait
            placeholder = pin_report.get('pinned_cids_sample', [None])[0]
            if placeholder:
                data['image'] = f'ipfs://{placeholder}'
                updated = True
                notes.append('image set to placeholder')
            data.setdefault('attributes', [])
            data['attributes'].append({'trait_type':'Metadata_Status','value':'Reconstructed'})
            updated = True
            notes.append('added Metadata_Status')

    # ensure attributes exist and include normalized tag if reconstructed
    if 'Metadata_Status' not in ''.join([str(a) for a in data.get('attributes', [])]):
        # only add if we added things
        pass

    # write normalized file
    out_path = OUT_DIR / filepath.name
    out_path.write_text(json.dumps(data, indent=2), encoding='utf-8')

    # pin to Pinata
    try:
        cid = pc.upload_json(data)
        manifest_entry = {
            'local_metadata': str(filepath),
            'normalized_metadata': str(out_path),
            'metadata_cid': cid,
            'metadata_ipfs_uri': f'ipfs://{cid}',
            'notes': notes
        }
        processed.append(manifest_entry)
        print('Pinned normalized metadata:', out_path, '->', cid)
    except Exception as e:
        print('Failed to pin metadata:', out_path, e)
        processed.append({'local_metadata': str(filepath), 'normalized_metadata': str(out_path), 'error': str(e), 'notes': notes})

# write manifest
manifest_path = BASE / 'normalized_manifest.json'
manifest_path.write_text(json.dumps(processed, indent=2), encoding='utf-8')

# also write CSV
import csv
csv_path = BASE / 'normalized_manifest.csv'
with open(csv_path, 'w', newline='', encoding='utf-8') as cf:
    writer = csv.DictWriter(cf, fieldnames=['local_metadata','normalized_metadata','metadata_cid','metadata_ipfs_uri','notes'])
    writer.writeheader()
    for row in processed:
        writer.writerow({k: row.get(k, '') for k in writer.fieldnames})

print('Done. Wrote', manifest_path, 'and', csv_path)
