#!/usr/bin/env python3
"""Attach art IPFS CIDs from manifest to local metadata files and repin metadata.
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
    changed = 0
    for t in m.get('tokens', []):
        meta_file = Path(t.get('meta_file'))
        art_cid = t.get('art_cid')
        if not meta_file.exists():
            print('Missing metadata file', meta_file); continue
        md = json.loads(meta_file.read_text(encoding='utf8'))
        # add image field if art_cid present and not already set
        if art_cid:
            if md.get('image') is None and md.get('animation_url') is None:
                md['image'] = f'ipfs://{art_cid}'
                # backup and write
                bak = meta_file.with_suffix(meta_file.suffix + '.bak')
                meta_file.replace(bak)
                meta_file.write_text(json.dumps(md, indent=2), encoding='utf8')
                changed += 1
                print('Updated', meta_file, 'with image ipfs://'+art_cid)
    print('Updated', changed, 'metadata files')

if __name__ == '__main__':
    main()
