import json
import csv
import sys
from pathlib import Path
from dotenv import load_dotenv
# ensure .env loaded and repo root on path
load_dotenv()
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tmt_os_labs.tools.pinata_uploader import PinataClient

# Files to pin for dry-run (5 items):
files = [
    'assets/pinata_downloads/Pinata_Download/Pinata_Download/quantum_nft_103_metadata.json',
    'assets/pinata_downloads/Pinata_Download/Pinata_Download/quantum_nft_100_metadata.json',
    'assets/pinata_downloads/Pinata_Download/Pinata_Download/quantum_nft_1_metadata.json',
    'assets/pinata_downloads/Pinata_Download/Pinata_Download/quantum_nft_11_metadata.json',
    'assets/pinata_downloads/Pinata_Download/Pinata_Download/quantum_nft_19_metadata.json'
]

pc = PinataClient()
results = []
for f in files:
    p = Path(f)
    if not p.exists():
        print('Missing file:', f)
        continue
    data = json.loads(p.read_text(encoding='utf-8'))
    print('Pinning:', p.name)
    cid = pc.upload_json(data)
    uri = f'ipfs://{cid}'
    results.append({'file': f, 'cid': cid, 'uri': uri})
    print('Pinned', p.name, '->', cid)

out_json = Path('assets/pinata_downloads/Pinata_Download/Pinata_Download/dry_run_metadata_manifest.json')
out_csv = Path('assets/pinata_downloads/Pinata_Download/Pinata_Download/dry_run_metadata_manifest.csv')

out_json.write_text(json.dumps(results, indent=2), encoding='utf-8')
with out_csv.open('w', newline='', encoding='utf-8') as cf:
    writer = csv.DictWriter(cf, fieldnames=['file','cid','uri'])
    writer.writeheader()
    for r in results:
        writer.writerow(r)

print('Wrote', out_json, 'and', out_csv)
