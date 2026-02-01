#!/usr/bin/env python3
"""Pin top-5 NFT metadata + associated art files to Pinata and log actions.

Requires PINATA_API_KEY/PINATA_SECRET or PINATA_JWT in project .env.
Writes manifest to `nft_deployment/ipfs_deployment_manifest.json` and logs to `logs_resonancia/pin_actions.log`.
"""
import os
import json
import time
import requests
from pathlib import Path
from datetime import datetime

# load .env
from pathlib import Path as _P
# load .env by simple parsing to avoid package import issues
def load_env_from(path:_P):
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line=line.strip()
        if line and not line.startswith('#') and '=' in line:
            k,v=line.split('=',1)
            v=v.strip().strip('"').strip("'")
            os.environ[k]=v

ROOT = Path(__file__).resolve().parent.parent
load_env_from(ROOT / '.env')

PINATA_JWT = os.environ.get('PINATA_JWT')
PINATA_API_KEY = os.environ.get('PINATA_API_KEY')
PINATA_SECRET = os.environ.get('PINATA_SECRET')

HEADERS = {}
if PINATA_JWT:
    HEADERS['Authorization'] = f'Bearer {PINATA_JWT}'
elif PINATA_API_KEY and PINATA_SECRET:
    HEADERS['pinata_api_key'] = PINATA_API_KEY
    HEADERS['pinata_secret_api_key'] = PINATA_SECRET
else:
    raise SystemExit('Pinata credentials not found in .env')

VQE_FILE = ROOT / 'node12_out' / 'vqe_local_results.json'
NFT_DIR = ROOT / 'nft_metadata'
MANIFEST = ROOT / 'nft_deployment' / 'ipfs_deployment_manifest.json'
PIN_LOG = ROOT / 'logs_resonancia' / 'pin_actions.log'


def upload_file(file_path: Path):
    with open(file_path, 'rb') as f:
        files = {'file': (file_path.name, f)}
        resp = requests.post('https://api.pinata.cloud/pinning/pinFileToIPFS', files=files, headers=HEADERS)
    if resp.status_code == 200:
        return resp.json()['IpfsHash']
    else:
        print('Pin file failed', file_path, resp.status_code, resp.text)
        return None


def upload_json(data: dict, name: str):
    resp = requests.post('https://api.pinata.cloud/pinning/pinJSONToIPFS', json={'pinataContent': data, 'pinataMetadata': {'name': name}}, headers={**HEADERS, 'Content-Type': 'application/json'})
    if resp.status_code == 200:
        return resp.json()['IpfsHash']
    else:
        print('Pin json failed', name, resp.status_code, resp.text)
        return None


def find_nft_file(meta_hash):
    candidate = NFT_DIR / f"{meta_hash}.nft.json"
    if candidate.exists():
        return candidate
    # fallback: try any json containing the hash
    for p in NFT_DIR.glob('*.json'):
        if meta_hash in p.name:
            return p
    return None


def find_art_file(meta_hash):
    # try glb, svg with meta_hash as prefix
    for ext in ['.glb', '.svg', '.png', '.jpg']:
        p = NFT_DIR / f"{meta_hash}{ext}"
        if p.exists():
            return p
    # fallback: find nearest GLB or svg in nft_metadata
    for p in NFT_DIR.iterdir():
        if p.suffix.lower() in ['.glb', '.svg', '.png', '.jpg'] and meta_hash[:8] in p.name:
            return p
    return None


def record_pin_action(entry):
    l = json.load(open(PIN_LOG, 'r', encoding='utf8'))
    l.append(entry)
    open(PIN_LOG, 'w', encoding='utf8').write(json.dumps(l, indent=2))


def main():
    data = json.load(open(VQE_FILE, 'r', encoding='utf8'))
    manifest = {'collection': 'Quantum Consciousness', 'deployed_at': datetime.utcnow().isoformat() + 'Z', 'tokens': []}

    for entry in data[:5]:
        meta_hash = entry.get('meta_hash')
        nft_file = find_nft_file(meta_hash)
        if not nft_file:
            print('No metadata file found for', meta_hash)
            continue

        # find art
        art_file = find_art_file(meta_hash)

        # pin art first if exists
        art_cid = None
        if art_file:
            print('Pinning art', art_file.name)
            art_cid = upload_file(art_file)
            time.sleep(0.3)

        # load metadata and update image/animation_url
        meta = json.load(open(nft_file, 'r', encoding='utf8'))
        if art_cid:
            # choose field depending on type
            if art_file.suffix.lower() == '.glb':
                meta['animation_url'] = f'ipfs://{art_cid}'
            else:
                meta['image'] = f'ipfs://{art_cid}'

        # ensure pauli terms exist
        if 'hamiltonian_pauli_terms' not in meta:
            meta['hamiltonian_pauli_terms'] = entry.get('hamiltonian_pauli_terms')

        # pin metadata
        print('Pinning metadata', nft_file.name)
        meta_cid = upload_json(meta, nft_file.name)
        time.sleep(0.3)

        if meta_cid:
            # write back updated metadata locally
            open(nft_file, 'w', encoding='utf8').write(json.dumps(meta, indent=2))
            manifest['tokens'].append({'meta_hash': meta_hash, 'meta_file': str(nft_file), 'meta_cid': meta_cid, 'art_cid': art_cid})
            # log action
            record_pin_action({'meta_hash': meta_hash, 'meta_file': str(nft_file), 'meta_cid': meta_cid, 'art_file': str(art_file) if art_file else None, 'art_cid': art_cid, 'timestamp': datetime.utcnow().isoformat() + 'Z'})
            print('Pinned', meta_hash, 'meta_cid=', meta_cid)
        else:
            print('Failed to pin metadata for', meta_hash)

    # save manifest
    open(MANIFEST, 'w', encoding='utf8').write(json.dumps(manifest, indent=2))
    print('Manifest saved to', MANIFEST)


if __name__ == '__main__':
    main()
