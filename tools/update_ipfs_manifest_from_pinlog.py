#!/usr/bin/env python3
"""Build `nft_deployment/ipfs_deployment_manifest.json` from the latest entries in `logs_resonancia/pin_actions.log`.
Keeps the contract info preserved if present, and writes `deployed_at` to now.
"""
from pathlib import Path
import json
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
PIN_LOG = ROOT / 'logs_resonancia' / 'pin_actions.log'
MANIFEST = ROOT / 'nft_deployment' / 'ipfs_deployment_manifest.json'


def main():
    if not PIN_LOG.exists():
        print('No pin log found')
        return
    entries = json.loads(PIN_LOG.read_text(encoding='utf8'))
    latest = {}
    for e in entries:
        mh = e.get('meta_hash')
        if not mh:
            continue
        latest[mh] = e

    tokens = []
    for mh, e in latest.items():
        tokens.append({'meta_hash': mh, 'meta_file': e.get('meta_file'), 'meta_cid': e.get('meta_cid'), 'art_cid': e.get('art_cid'), 'timestamp': e.get('timestamp')})

    # keep existing contract info if present
    if MANIFEST.exists():
        try:
            m = json.loads(MANIFEST.read_text(encoding='utf8'))
            contract = m.get('contract_mainnet')
        except Exception:
            contract = None
    else:
        contract = None

    out = {'collection': 'Quantum Consciousness', 'deployed_at': datetime.utcnow().isoformat() + 'Z', 'tokens': tokens}
    if contract:
        out['contract_mainnet'] = contract
    MANIFEST.write_text(json.dumps(out, indent=2), encoding='utf8')
    print('Wrote manifest with', len(tokens), 'tokens')


if __name__ == '__main__':
    main()
