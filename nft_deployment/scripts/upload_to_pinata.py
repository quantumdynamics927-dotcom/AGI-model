#!/usr/bin/env python3
"""
Upload NFT collection to IPFS via Pinata.
Reads credentials from .env file.
"""

import os
import json
import time
import requests
from pathlib import Path
from datetime import datetime

def load_env(env_path: Path):
    """Load environment variables from .env file."""
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, val = line.split('=', 1)
            val = val.strip('"').strip("'")
            os.environ[key] = val

def upload_file(file_path: Path, headers: dict) -> str | None:
    """Upload a file to Pinata IPFS."""
    with open(file_path, 'rb') as f:
        response = requests.post(
            'https://api.pinata.cloud/pinning/pinFileToIPFS',
            files={'file': (file_path.name, f)},
            headers=headers,
            data={'pinataMetadata': json.dumps({'name': file_path.name})}
        )
    if response.status_code == 200:
        return response.json()['IpfsHash']
    return None

def upload_json(data: dict, name: str, headers: dict) -> str | None:
    """Upload JSON directly to Pinata IPFS."""
    response = requests.post(
        'https://api.pinata.cloud/pinning/pinJSONToIPFS',
        json={'pinataContent': data, 'pinataMetadata': {'name': name}},
        headers={**headers, 'Content-Type': 'application/json'}
    )
    if response.status_code == 200:
        return response.json()['IpfsHash']
    return None

def main():
    # Load .env
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    load_env(project_root / '.env')

    PINATA_API_KEY = os.environ.get('PINATA_API_KEY', '')
    PINATA_SECRET = os.environ.get('PINATA_SECRET', '')

    if not PINATA_API_KEY or not PINATA_SECRET:
        print('[ERROR] Pinata credentials not found in .env')
        return

    headers = {
        'pinata_api_key': PINATA_API_KEY,
        'pinata_secret_api_key': PINATA_SECRET,
    }

    # Test auth
    print('Testing Pinata authentication...')
    response = requests.get('https://api.pinata.cloud/data/testAuthentication', headers=headers)
    if response.status_code != 200:
        print(f'[ERROR] Auth failed: {response.text}')
        return
    print('[OK] Authenticated!\n')

    deploy_dir = script_dir.parent
    art_dir = deploy_dir / 'quantum_art'
    metadata_dir = deploy_dir / 'opensea_metadata'

    # Upload artwork
    print('=' * 60)
    print('STEP 1: Uploading Artwork to IPFS')
    print('=' * 60)

    art_files = sorted(art_dir.glob('quantum_art_*.svg'))
    uploaded_art = {}

    for i, art_file in enumerate(art_files, 1):
        token_id = art_file.stem.replace('quantum_art_', '')
        print(f'  [{i:2}/{len(art_files)}] {token_id[:16]}...', end=' ', flush=True)

        cid = upload_file(art_file, headers)
        if cid:
            uploaded_art[token_id] = cid
            print(f'OK -> {cid[:16]}...')
        else:
            print('FAILED')
        time.sleep(0.3)

    print(f'\nUploaded {len(uploaded_art)}/{len(art_files)} artworks\n')

    # Update and upload metadata
    print('=' * 60)
    print('STEP 2: Updating and Uploading Metadata')
    print('=' * 60)

    uploaded_meta = {}
    metadata_files = sorted(metadata_dir.glob('quantum_consciousness_*.json'))

    for i, meta_file in enumerate(metadata_files, 1):
        # Extract token_id from filename
        token_id = meta_file.stem.replace('quantum_consciousness_', '')

        # Find matching art CID
        art_cid = None
        for art_id, cid in uploaded_art.items():
            if art_id.startswith(token_id) or token_id.startswith(art_id[:16]):
                art_cid = cid
                break

        if not art_cid:
            print(f'  [{i:2}/{len(metadata_files)}] {token_id[:16]}... SKIP (no art)')
            continue

        print(f'  [{i:2}/{len(metadata_files)}] {token_id[:16]}...', end=' ', flush=True)

        # Load and update metadata
        with open(meta_file, 'r') as f:
            metadata = json.load(f)

        # Update image URL
        metadata['image'] = f'ipfs://{art_cid}'

        # Upload metadata
        meta_cid = upload_json(metadata, meta_file.name, headers)
        if meta_cid:
            uploaded_meta[token_id] = {'art_cid': art_cid, 'meta_cid': meta_cid}
            print(f'OK -> {meta_cid[:16]}...')

            # Save updated metadata locally
            with open(meta_file, 'w') as f:
                json.dump(metadata, f, indent=2)
        else:
            print('FAILED')

        time.sleep(0.3)

    print(f'\nUploaded {len(uploaded_meta)}/{len(metadata_files)} metadata files\n')

    # Generate final manifest
    print('=' * 60)
    print('STEP 3: Generating Deployment Manifest')
    print('=' * 60)

    manifest = {
        'collection': 'Quantum Consciousness',
        'symbol': 'QCON',
        'deployed_at': datetime.utcnow().isoformat() + 'Z',
        'pinata_gateway': 'https://gateway.pinata.cloud/ipfs/',
        'tokens': []
    }

    for token_id, cids in uploaded_meta.items():
        manifest['tokens'].append({
            'token_id': token_id,
            'image_ipfs': f"ipfs://{cids['art_cid']}",
            'metadata_ipfs': f"ipfs://{cids['meta_cid']}",
            'opensea_url': f"https://gateway.pinata.cloud/ipfs/{cids['meta_cid']}"
        })

    manifest_path = deploy_dir / 'ipfs_deployment_manifest.json'
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    print(f'Manifest saved: {manifest_path}')
    print(f'Total tokens ready: {len(manifest["tokens"])}')

    # Summary
    print('\n' + '=' * 60)
    print('DEPLOYMENT COMPLETE')
    print('=' * 60)
    print(f'\nSample IPFS URLs:')
    for token in manifest['tokens'][:3]:
        print(f"  {token['token_id'][:8]}: {token['opensea_url']}")

    print(f'\nNext: Deploy contract and mint with token URIs from manifest')

if __name__ == '__main__':
    main()
