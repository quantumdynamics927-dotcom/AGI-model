from pathlib import Path
import os, json, sys

# Ensure portal package is importable by adding the portal root to sys.path when available
ROOT = Path(__file__).resolve().parents[1] / 'TMT-OS-Labs-Portal'
if ROOT.exists():
    sys.path.insert(0, str(ROOT))
    print(f"[INFO] Added portal root to sys.path: {ROOT}")
else:
    # Fallback: try to add parent folder if script is running elsewhere
    alt = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(alt))
    print(f"[WARN] Expected portal root not found, added parent path to sys.path: {alt}")

# Point DELIVERY_ROOT to promoters BEFORE importing the app
os.environ['TMTOS_DELIVERY_ROOT'] = str(Path('e:/AGI model/data/promoters').resolve())

# Import FastAPI TestClient and the app
from fastapi.testclient import TestClient
try:
    from portal.api import main
except Exception as e:
    print('[ERROR] Could not import portal.api:', e)
    raise

client = TestClient(main.app)
resp = client.get('/certificates')
print('STATUS', resp.status_code)
data = resp.json()
print('FOUND', len(data), 'certificates')
for item in data[:50]:
    name = item.get('name') or item.get('metadata', {}).get('name')
    path = item.get('path')
    print('-', name, path)

# Print full JSON for first entry if exists
if data:
    print('\nSAMPLE METADATA:\n', json.dumps(data[0].get('metadata', {}), indent=2))
