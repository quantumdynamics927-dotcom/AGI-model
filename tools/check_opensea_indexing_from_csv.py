#!/usr/bin/env python3
"""Check OpenSea indexing for tokens referenced in a transaction CSV.

Usage: python tools/check_opensea_indexing_from_csv.py --csv "E:\\Descargas\\export-0x345b67bf9e92a6f23960a27238337d6e6a0f63f6.csv"

Outputs: nft_deployment/opensea_indexing_check.json and .csv
"""
import argparse
import csv
import json
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parent.parent
MINT_RESULTS = ROOT / 'nft_deployment' / 'minting_results_mainnet.json'
OUT_JSON = ROOT / 'nft_deployment' / 'opensea_indexing_check.json'
OUT_CSV = ROOT / 'nft_deployment' / 'opensea_indexing_check.csv'


def load_mint_results():
    return json.loads(MINT_RESULTS.read_text(encoding='utf8')) if MINT_RESULTS.exists() else {'tokens': []}


def read_csv(path):
    rows = []
    with open(path, 'r', encoding='utf8') as fh:
        r = csv.DictReader(fh)
        for row in r:
            rows.append(row)
    return rows


def check_opensea(url):
    try:
        # Use simple GET with a short timeout
        r = requests.get(url, timeout=10)
        return {'status_code': r.status_code, 'ok': r.status_code == 200, 'url': url}
    except Exception as e:
        return {'status_code': None, 'ok': False, 'error': str(e), 'url': url}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--csv', required=True)
    args = p.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.exists():
        print('CSV not found:', csv_path); return

    csv_rows = read_csv(csv_path)
    mint = load_mint_results()
    tx_to_token = {t['txHash'].lower(): t.get('tokenId') for t in mint.get('tokens', [])}
    contract = None
    if 'contract_mainnet' in (json.loads((ROOT / 'nft_deployment' / 'ipfs_deployment_manifest.json').read_text(encoding='utf8')) if (ROOT / 'nft_deployment' / 'ipfs_deployment_manifest.json').exists() else {}):
        contract = json.loads((ROOT / 'nft_deployment' / 'ipfs_deployment_manifest.json').read_text(encoding='utf8')).get('contract_mainnet', {}).get('contractAddress')

    results = []
    for r in csv_rows:
        tx = r.get('Transaction Hash','').lower()
        if tx in tx_to_token:
            tokenId = tx_to_token[tx]
            if tokenId is None:
                continue
            # Construct OpenSea URL
            if not contract:
                # fallback to contract used earlier
                contract = '0x345B67bF9e92a6f23960a27238337d6E6A0f63F6'
            url = f'https://opensea.io/assets/matic/{contract}/{tokenId}'
            check = check_opensea(url)
            results.append({'tx': tx, 'tokenId': tokenId, 'opensea_url': url, 'opensea_check': check, 'csv_row': r})

    # write outputs
    OUT_JSON.write_text(json.dumps({'checked': len(results), 'results': results}, indent=2), encoding='utf8')
    # CSV
    with open(OUT_CSV, 'w', encoding='utf8', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(['tx','tokenId','opensea_url','status_code','ok','error'])
        for it in results:
            ch = it['opensea_check']
            w.writerow([it['tx'], it['tokenId'], it['opensea_url'], ch.get('status_code'), ch.get('ok'), ch.get('error','')])

    print('Checked', len(results), 'tokens, results in', OUT_JSON, 'and', OUT_CSV)


if __name__ == '__main__':
    main()
