#!/usr/bin/env python3
"""Generate NFT-style metadata JSON files from a sweep results file.
Selects top-N entries by `phi_corr` and writes `nft_metadata/<hash>.nft.json`.
Does not perform any external pinning or minting.
"""
import json
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
SWEEP = ROOT / 'node12_out' / 'variation_sweep_extended.json'
OUT_DIR = ROOT / 'nft_metadata'
OUT_DIR.mkdir(parents=True, exist_ok=True)

def make_metadata(entry):
    meta_hash = entry.get('meta', {}).get('hash')
    name = f"Metatron Node12 Connectivity {meta_hash[:12]}"
    description = (
        f"Connectivity snapshot from Node12 sweep. Sequence: {entry.get('seq')} | "
        f"Type: {entry.get('type')} | phi_corr: {entry.get('phi_corr'):.6f}"
    )
    created = datetime.utcnow().isoformat() + 'Z'
    payload = {
        'name': name,
        'description': description,
        'created': created,
        'provenance': {
            'meta_hash': meta_hash,
            'phi_corr': entry.get('phi_corr'),
            'seq': entry.get('seq'),
            'type': entry.get('type'),
            'raw_path': entry.get('raw_path'),
            'source': str(SWEEP),
        },
        'nft': {
            'pinning': None,
            'ipfs_cid': None,
            'minted_tx': None
        },
        'governance': {
            'raw_export_allowed': True,
            'governance_doc': str(ROOT / 'node11_readme.md')
        }
    }
    return payload

def main(top_n=5):
    if not SWEEP.exists():
        raise SystemExit('Sweep file not found: ' + str(SWEEP))
    data = json.load(open(SWEEP, 'r', encoding='utf8'))
    # ensure list of entries
    if isinstance(data, dict) and 'results' in data:
        entries = data['results']
    else:
        entries = data

    entries_sorted = sorted(entries, key=lambda x: -float(x.get('phi_corr', 0)))
    selected = entries_sorted[:top_n]
    written = []
    for e in selected:
        h = e.get('meta', {}).get('hash')
        if not h:
            continue
        outp = OUT_DIR / f'{h}.nft.json'
        outp.write_text(json.dumps(make_metadata(e), indent=2))
        written.append(str(outp))

    print('Wrote', len(written), 'metadata files:')
    for p in written:
        print(' -', p)

if __name__ == '__main__':
    main()
