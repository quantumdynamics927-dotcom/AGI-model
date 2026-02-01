#!/usr/bin/env python3
"""Apply OpenSea indexing check results to manifest and per-metadata files.
Reads nft_deployment/opensea_indexing_check.json and updates:
- nft_deployment/ipfs_deployment_manifest.json.tokens[*].opensea_url
- nft_metadata/<meta>.nft.json -> nft.market.opensea = { 'url': ..., 'indexed': True }
- append a log entry to logs_resonancia/mint_actions.log
"""
from pathlib import Path
import json
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
CHECK = ROOT / 'nft_deployment' / 'opensea_indexing_check.json'
MANIFEST = ROOT / 'nft_deployment' / 'ipfs_deployment_manifest.json'
PIN_LOG = ROOT / 'logs_resonancia' / 'pin_actions.log'
MINT_LOG = ROOT / 'logs_resonancia' / 'mint_actions.log'
NFT_DIR = ROOT / 'nft_metadata'


def main():
    if not CHECK.exists():
        print('No opensea check results found at', CHECK); return
    res = json.loads(CHECK.read_text(encoding='utf8'))
    results = res.get('results', [])

    # update manifest tokens by meta_hash
    if MANIFEST.exists():
        manifest = json.loads(MANIFEST.read_text(encoding='utf8'))
    else:
        manifest = {'tokens': []}

    mh_map = {t['meta_hash']: t for t in manifest.get('tokens', [])}

    updated = 0
    for r in results:
        tx = r.get('tx')
        tokenId = r.get('tokenId')
        url = r.get('opensea_url')
        # find meta by matching tokenId in minting_results_mainnet
        # fallback: find nft metadata file that contains tokenId
        for p in NFT_DIR.glob('*.nft.json'):
            j = json.loads(p.read_text(encoding='utf8'))
            nft = j.get('nft', {})
            minted = nft.get('minted_tx', {})
            if minted.get('tokenId') == tokenId:
                j.setdefault('nft', {})['market'] = {'opensea': {'url': url, 'indexed': True, 'checked_at': datetime.utcnow().isoformat() + 'Z'}}
                # backup and write
                bak = p.with_suffix(p.suffix + '.bak')
                p.replace(bak)
                p.write_text(json.dumps(j, indent=2), encoding='utf8')
                updated += 1
                break

    # update manifest tokens entries by tokenId if present
    for t in manifest.get('tokens', []):
        # if token_id in manifest (string) matches any tokenId
        for r in results:
            tid = r.get('tokenId')
            # token_id in manifest stored as hex-like string; compare integer or prefix
            token_id_field = t.get('token_id') or t.get('tokenId') or t.get('token_id_hex') or t.get('token_id_str')
            if token_id_field:
                try:
                    # if token_id_field startswith hex of meta, skip; else try to compare numerically
                    if isinstance(token_id_field, int) and token_id_field == tid:
                        t['opensea_url'] = r.get('opensea_url')
                        t['opensea_indexed'] = True
                    else:
                        # try string compare
                        if str(tid) in str(token_id_field):
                            t['opensea_url'] = r.get('opensea_url')
                            t['opensea_indexed'] = True
                except Exception:
                    pass
    # write manifest backup
    if MANIFEST.exists():
        MANIFEST.replace(MANIFEST.with_suffix('.json.bak'))
    MANIFEST.write_text(json.dumps(manifest, indent=2), encoding='utf8')

    # append mint log entries
    try:
        mint_l = json.loads(MINT_LOG.read_text(encoding='utf8')) if MINT_LOG.exists() else []
    except Exception:
        mint_l = []
    for r in results:
        mint_l.append({'action': 'opensea_indexed', 'tx': r.get('tx'), 'tokenId': r.get('tokenId'), 'opensea_url': r.get('opensea_url'), 'timestamp': datetime.utcnow().isoformat() + 'Z'})
    MINT_LOG.write_text(json.dumps(mint_l, indent=2), encoding='utf8')

    print('Updated', updated, 'metadata files and manifest')

if __name__ == '__main__':
    main()
