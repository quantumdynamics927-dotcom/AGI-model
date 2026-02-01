"""Pinata sync utility

- Lists pinned items via Pinata API (uses PINATA_JWT or API key/secret from .env)
- Compares pinned items to local folder `assets/pinata_downloads/Pinata_Download/Pinata_Download`
- Downloads pinned-but-missing CIDs into that local folder (preferring metadata.name as filename)
- Writes report to `assets/pinata_downloads/pinata_sync_report.json`

Usage:
    python scripts/pinata_sync.py
"""

print('pinata_sync: starting')

import os
import re
import json
import requests
import sys
from pathlib import Path
# Ensure project root is on sys.path so imports like `tmt_os_labs.*` work when running scripts
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from tmt_os_labs.tools.pinata_uploader import PinataClient

BASE_DIR = Path(__file__).resolve().parents[1]
# Manually load .env (lightweight fallback, avoids python-dotenv dependency)
_env_path = BASE_DIR / '.env'
if _env_path.exists():
    print('Loading .env from', _env_path)
    for line in _env_path.read_text(encoding='utf-8').splitlines():
        if not line or line.strip().startswith('#'):
            continue
        if '=' in line:
            k, v = line.split('=', 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            os.environ.setdefault(k, v)

LOCAL_DIR = BASE_DIR / 'assets' / 'pinata_downloads' / 'Pinata_Download' / 'Pinata_Download'
REPORT_PATH = BASE_DIR / 'assets' / 'pinata_downloads' / 'pinata_sync_report.json'

# Ensure local dir exists
LOCAL_DIR.mkdir(parents=True, exist_ok=True)

print('About to start Pinata fetch block')
try:
    print('Env PINATA_JWT present:', bool(os.environ.get('PINATA_JWT')))
    print('Env PINATA_API_KEY present:', bool(os.environ.get('PINATA_API_KEY')))
    client = PinataClient()
    headers = client._headers()
    print('Computed headers keys:', list(headers.keys()) if headers else None)

    if not headers:
        raise RuntimeError('No Pinata credentials found in environment (PINATA_JWT or API key/secret).')

    print('[1/4] Fetching pinned items from Pinata...')
    resp = requests.get('https://api.pinata.cloud/data/pinList?status=pinned&pageLimit=1000', headers=headers, timeout=30)
    resp.raise_for_status()
    rows = resp.json().get('rows', [])
    print(f'Found {len(rows)} pinned items')
except Exception as e:
    print('[ERROR] Failed to fetch pinned items:', e)
    import traceback
    traceback.print_exc()
    raise

# Build maps
pinned_cids = set()
cid_to_meta = {}
name_to_cid = {}
for r in rows:
    cid = r.get('ipfs_pin_hash')
    pinned_cids.add(cid)
    meta = r.get('metadata') or {}
    name = meta.get('name')
    cid_to_meta[cid] = {
        'name': name,
        'datePinned': r.get('date_pinned'),
        'size': r.get('size')
    }
    if name:
        name_to_cid[name] = cid

# Gather local files and local referenced cids
print('[2/4] Scanning local files for filenames and referenced IPFS CIDs...')
local_files = set(os.listdir(LOCAL_DIR))
referenced_cids = set()
ipfs_re = re.compile(r'(?:ipfs://|/ipfs/)(Qm[1-9A-Za-z]{44}|bafy[1-9A-Za-z]{50,})')
for fname in local_files:
    if fname.lower().endswith('.json'):
        try:
            data = json.loads((LOCAL_DIR / fname).read_text(encoding='utf-8'))
            dump = json.dumps(data)
            for m in ipfs_re.finditer(dump):
                referenced_cids.add(m.group(1))
        except Exception:
            pass

# Determine missing pinned files (pinned but not present locally by name or referenced)
missing_by_name = []
for cid, meta in cid_to_meta.items():
    name = meta.get('name')
    if name and name in local_files:
        continue
    if cid in referenced_cids:
        continue
    # Not present locally
    missing_by_name.append((cid, name))

print(f'[3/4] {len(missing_by_name)} pinned items appear missing locally')

# Download missing items
downloaded = []
failed = []
import time
    for cid, name in missing_by_name:
        url = f'https://gateway.pinata.cloud/ipfs/{cid}'
        print('Downloading', cid, '->', name or (cid + '.bin'))
        success = False
        attempts = 3
        for attempt in range(1, attempts + 1):
            try:
                # Use tuple timeout (connect, read) to avoid long hangs
                r = requests.get(url, headers=headers, stream=True, timeout=(5, 20))
                if r.status_code != 200:
                    raise Exception(f'HTTP {r.status_code}')
                # Determine filename: prefer metadata name
                fname = name or cid
                # Try to determine extension from content-type
                ctype = r.headers.get('Content-Type','')
                ext = ''
                if 'image/' in ctype:
                    ext = '.' + ctype.split('/')[-1].split(';')[0]
                # fallback: if name has no ext but content-length suggests png/jpg, leave as is
                out_path = LOCAL_DIR / (fname + ext if not Path(fname).suffix else fname)
                with open(out_path, 'wb') as fh:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            fh.write(chunk)
                downloaded.append({'cid': cid, 'filename': str(out_path)})
                success = True
                break
            except Exception as e:
                print(f'  attempt {attempt} failed: {e}')
                last_err = str(e)
                time.sleep(1)
        if not success:
            failed.append({'cid': cid, 'error': last_err})

# Identify local-only files (not in pin metadata names nor referencing any pinned CID)
local_only = []
for fname in local_files:
    if fname in name_to_cid:
        continue
    # Check if any referenced cid in this file matches a pinned or referenced cid
    fpath = LOCAL_DIR / fname
    if fpath.suffix.lower() == '.json':
        try:
            data = json.loads(fpath.read_text(encoding='utf-8'))
            dump = json.dumps(data)
            if ipfs_re.search(dump):
                # references some ipfs cid
                continue
        except Exception:
            pass
    # If we reach here, it's likely a local-only asset
    local_only.append(fname)

report = {
    'pinned_count': len(rows),
    'pinned_cids_sample': list(pinned_cids)[:20],
    'referenced_cids_count': len(referenced_cids),
    'missing_pinned_count': len(missing_by_name),
    'downloaded': downloaded,
    'failed': failed,
    'local_only_files': local_only
}

print('[4/4] Writing report to', REPORT_PATH)
REPORT_PATH.write_text(json.dumps(report, indent=2))
print('Done. Summary:')
print(json.dumps({'pinned': report['pinned_count'], 'missing': report['missing_pinned_count'], 'downloaded': len(downloaded), 'failed': len(failed), 'local_only': len(local_only)}, indent=2))

if failed:
    print('\nFailures:')
    for f in failed:
        print(f)

print('\nNext: review the report at', REPORT_PATH)
