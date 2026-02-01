import os
from pathlib import Path
import sys
# Ensure portal package is importable by adding the portal root to sys.path
ROOT = Path(__file__).resolve().parents[1] / 'TMT-OS-Labs-Portal'
if ROOT.exists():
    sys.path.insert(0, str(ROOT))
    print(f"[INFO] Added portal root to sys.path: {ROOT}")
else:
    alt = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(alt))
    print(f"[WARN] Expected portal root not found, added parent path to sys.path: {alt}")

# Point DELIVERY_ROOT to promoters
os.environ['TMTOS_DELIVERY_ROOT'] = str(Path('e:/AGI model/data/promoters').resolve())

from fastapi.testclient import TestClient
from portal.api import main

client = TestClient(main.app)
resp = client.get('/certificates')
print('STATUS', resp.status_code)
try:
    data = resp.json()
    print('FOUND', len(data), 'certificates')
    for item in data:
        print('-', item.get('name') or item.get('metadata', {}).get('name'), item.get('path'))
except Exception as e:
    print('ERROR parsing response:', e)

# Attempt to fetch first certificate image URL via TestClient
if data:
    name = data[0].get('name')
    r2 = client.get(f'/certificate/{name}/image')
    print('IMG_STATUS', r2.status_code)
    print('IMG_LEN', len(r2.content) if r2.status_code == 200 else None)
