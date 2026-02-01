#!/usr/bin/env python3
"""Generate a manifest of NFT metadata files suitable for OpenSea upload/indexing.
Outputs `nft_deployment/opensea_upload_manifest.csv` and `nft_deployment/opensea_upload_manifest.json`.
"""
from pathlib import Path
import json
import csv

ROOT = Path(__file__).resolve().parent.parent
NFT_DIR = ROOT / 'nft_metadata'
IPFS_MANIFEST = ROOT / 'nft_deployment' / 'ipfs_deployment_manifest.json'
OUT_CSV = ROOT / 'nft_deployment' / 'opensea_upload_manifest.csv'
OUT_JSON = ROOT / 'nft_deployment' / 'opensea_upload_manifest.json'


def load_nft_files():
    files = list(NFT_DIR.glob('*.nft.json'))
    return files


def get_ipfs_map():
    if not IPFS_MANIFEST.exists():
        return {}
    m = json.loads(IPFS_MANIFEST.read_text(encoding='utf8'))
    return {t['meta_hash']: t for t in m.get('tokens', [])}


def inspect_file(p):
    try:
        j = json.loads(p.read_text(encoding='utf8'))
    except Exception as e:
        return {'path': str(p), 'error': str(e)}
    meta = j.get('provenance', {})
    nft = j.get('nft', {})
    name = j.get('name')
    token_id = j.get('token_id') or j.get('tokenId') or nft.get('tokenId')
    ipfs_cid = None
    if isinstance(nft.get('ipfs_cid'), str):
        ipfs_cid = nft.get('ipfs_cid').replace('ipfs://','')
    meta_hash = meta.get('meta_hash') or p.stem[:32]
    image = j.get('image')
    animation = j.get('animation_url')
    minted = nft.get('minted_tx')
    return {
        'path': str(p), 'name': name, 'meta_hash': meta_hash, 'token_id': token_id, 'ipfs_cid': ipfs_cid,
        'image': image, 'animation_url': animation, 'minted_tx': minted, 'raw': j
    }


def main():
    files = load_nft_files()
    ipfs_map = get_ipfs_map()
    rows = []
    for p in files:
        info = inspect_file(p)
        mh = info.get('meta_hash')
        if mh in ipfs_map:
            info['ipfs_cid'] = ipfs_map[mh].get('meta_cid')
        info['ready_image'] = bool(info.get('image') or info.get('animation_url'))
        info['opensea_ready'] = info['ready_image'] and bool(info.get('ipfs_cid'))
        rows.append(info)

    # write csv
    headers = ['name','path','meta_hash','ipfs_cid','token_id','minted_tx_hash','image','animation_url','ready_image','opensea_ready']
    with open(OUT_CSV, 'w', encoding='utf8', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(headers)
        for r in rows:
            w.writerow([
                r.get('name'), r.get('path'), r.get('meta_hash'), r.get('ipfs_cid'), r.get('token_id'),
                (r.get('minted_tx') or {}).get('tx_hash') if r.get('minted_tx') else None,
                r.get('image'), r.get('animation_url'), r.get('ready_image'), r.get('opensea_ready')
            ])
    # write json
    with open(OUT_JSON, 'w', encoding='utf8') as fh:
        json.dump({'generated': len(rows), 'items': rows}, fh, indent=2)

    print('Wrote', OUT_CSV, 'and', OUT_JSON)

if __name__ == '__main__':
    main()
