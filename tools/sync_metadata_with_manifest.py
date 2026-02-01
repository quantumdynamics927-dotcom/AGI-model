#!/usr/bin/env python3
"""Synchronize `nft_metadata/*.nft.json` with `nft_deployment/ipfs_deployment_manifest.json`.
Sets `nft.ipfs_cid` to `ipfs://<meta_cid>` and records pin details under `nft.pinning`.
"""
from pathlib import Path
import json
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / 'nft_deployment' / 'ipfs_deployment_manifest.json'
NFT_DIR = ROOT / 'nft_metadata'


def main():
    if not MANIFEST.exists():
        print('No manifest found')
        return
    m = json.loads(MANIFEST.read_text(encoding='utf8'))
    tokens = m.get('tokens', [])
    count = 0
    for t in tokens:
        mh = t.get('meta_hash')
        cid = t.get('meta_cid')
        file_path = Path(t.get('meta_file')) if t.get('meta_file') else NFT_DIR / f'{mh}.nft.json'
        if not file_path.exists():
            print('Missing file for', mh)
            continue
        md = json.loads(file_path.read_text(encoding='utf8'))
        md.setdefault('nft', {})['ipfs_cid'] = f'ipfs://{cid}'
        md['nft']['pinning'] = {'pin_cid': cid, 'pinned_at': datetime.utcnow().isoformat() + 'Z'}
        # write backup
        bak = file_path.with_suffix(file_path.suffix + '.bak')
        file_path.replace(bak)
        file_path.write_text(json.dumps(md, indent=2), encoding='utf8')
        count += 1
    print('Updated', count, 'metadata files')

if __name__ == '__main__':
    main()
