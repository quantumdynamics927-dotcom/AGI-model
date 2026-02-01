"""Fetch on-chain receipts for mint txs and finalize minting records.

Usage: python tools/fetch_and_finalize_mints.py [--rpc RPC_URL]

Reads `nft_deployment/minting_results_mainnet.json` and `logs_resonancia/mint_actions.log`,
fetches receipts via RPC, extracts token IDs from Transfer events, updates tokens entries
with `tokenId` (int), `tokenId_hex`, `gasUsed`, `status`, `block`, `blockHash`, and
writes back the minting_results file and updates matching `nft_metadata/*.nft.json` files
adding `nft.minted_tx.receipt` with full receipt info.
"""
import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
import requests

TRANSFER_TOPIC = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'

ROOT = Path(__file__).resolve().parents[1]
MINT_RESULTS = ROOT / 'nft_deployment' / 'minting_results_mainnet.json'
MINT_LOG = ROOT / 'logs_resonancia' / 'mint_actions.log'
NFT_DIR = ROOT / 'nft_metadata'


def load_env_dotenv():
    # simple .env loader if not present in os.environ
    env_path = ROOT / '.env'
    if env_path.exists():
        with env_path.open('r', encoding='utf-8') as fh:
            for ln in fh:
                ln = ln.strip()
                if not ln or ln.startswith('#'):
                    continue
                if '=' in ln:
                    k,v = ln.split('=',1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def rpc_post(rpc_url, method, params):
    body = {'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params}
    r = requests.post(rpc_url, json=body, timeout=20)
    r.raise_for_status()
    return r.json()


def fetch_receipt(rpc_url, tx_hash):
    res = rpc_post(rpc_url, 'eth_getTransactionReceipt', [tx_hash])
    if 'result' not in res:
        raise RuntimeError(f'RPC returned unexpected: {res}')
    return res['result']


def hex_to_int(h):
    if h is None:
        return None
    return int(h, 16)


def addr_from_topic(topic):
    # topic like 0x000...<40 hex address>
    if not topic:
        return None
    t = topic
    if t.startswith('0x'):
        t = t[2:]
    return '0x' + t[-40:]


def map_meta_to_file():
    mapping = {}
    for p in NFT_DIR.glob('*.nft.json'):
        try:
            j = json.loads(p.read_text(encoding='utf-8'))
            meta = j.get('provenance',{})
            meta_hash = meta.get('meta_hash')
            if meta_hash:
                mapping[meta_hash] = p
        except Exception:
            continue
    return mapping


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--rpc', type=str, default=os.environ.get('POLYGON_RPC_URL') or os.environ.get('RPC_URL'))
    parser.add_argument('--confirmations', type=int, default=3)
    args = parser.parse_args()

    if not args.rpc:
        print('Need RPC URL (set POLYGON_RPC_URL or pass --rpc)'); sys.exit(1)

    if not MINT_RESULTS.exists():
        print('Missing', MINT_RESULTS); sys.exit(1)

    # load existing minting results
    mint_json = json.loads(MINT_RESULTS.read_text(encoding='utf-8'))
    tokens = mint_json.get('tokens', [])

    # load mint log to map meta_hash -> txHash
    if MINT_LOG.exists():
        log_entries = json.loads(MINT_LOG.read_text(encoding='utf-8'))
        meta_to_tx = {e.get('meta_hash'): e.get('txHash') for e in log_entries if e.get('action') == 'mainnet_mint' and e.get('txHash')}
    else:
        meta_to_tx = {}

    meta_map = map_meta_to_file()

    updated_tokens = []
    summary = []
    for token in tokens:
        tx = token.get('txHash')
        if not tx:
            summary.append({'status':'missing_tx','token': token})
            updated_tokens.append(token)
            continue
        try:
            receipt = fetch_receipt(args.rpc, tx)
        except Exception as e:
            summary.append({'tx':tx,'error':str(e)})
            updated_tokens.append(token)
            continue
        # parse useful fields
        block = hex_to_int(receipt.get('blockNumber'))
        gasUsed = hex_to_int(receipt.get('gasUsed'))
        status = hex_to_int(receipt.get('status')) if receipt.get('status') is not None else None
        blockHash = receipt.get('blockHash')
        logs = receipt.get('logs', [])
        token_id = None
        token_id_hex = None
        from_addr = None
        to_addr = None
        for l in logs:
            topics = l.get('topics', [])
            if topics and topics[0].lower() == TRANSFER_TOPIC:
                # topics[1] = from, topics[2] = to, topics[3] = tokenId
                if len(topics) >= 4:
                    token_id_hex = topics[3]
                    try:
                        token_id = int(token_id_hex, 16)
                    except Exception:
                        token_id = None
                from_addr = addr_from_topic(topics[1]) if len(topics) >= 2 else None
                to_addr = addr_from_topic(topics[2]) if len(topics) >= 3 else None
                break
        # update token entry
        token.update({'tokenId': token_id if token_id is not None else token.get('tokenId'),
                      'tokenId_hex': token_id_hex,
                      'gasUsed': gasUsed,
                      'status': status,
                      'block': block,
                      'blockHash': blockHash,
                      'from': from_addr,
                      'to': to_addr,
                      'receipt': receipt})
        updated_tokens.append(token)

        # update corresponding nft metadata file
        # find meta_hash mapping by matching txHash in mint log
        meta_hash = None
        for mh, txh in meta_to_tx.items():
            if txh == tx:
                meta_hash = mh
                break
        if meta_hash and meta_hash in meta_map:
            md_path = meta_map[meta_hash]
            try:
                md = json.loads(md_path.read_text(encoding='utf-8'))
                minted = md.get('nft', {}).get('minted_tx', {})
                minted.update({'tx_hash': tx, 'block': block, 'tokenId': token_id, 'tx_receipt': receipt, 'timestamp': datetime.utcnow().isoformat() + 'Z'})
                md.setdefault('nft', {})['minted_tx'] = minted
                # backup
                bak = md_path.with_suffix(md_path.suffix + '.bak')
                md_path.replace(bak)
                md_path.write_text(json.dumps(md, indent=2), encoding='utf-8')
                summary.append({'meta_hash': str(meta_hash), 'md_file': str(md_path), 'tokenId': token_id})
            except Exception as e:
                summary.append({'meta_hash': meta_hash, 'error_updating_meta': str(e)})
        else:
            summary.append({'tx': tx, 'note': 'no matching meta file found for tx'})

    # write updated minting results (backup first)
    bak = MINT_RESULTS.with_suffix('.json.bak')
    MINT_RESULTS.replace(bak)
    mint_json['tokens'] = updated_tokens
    MINT_RESULTS.write_text(json.dumps(mint_json, indent=2), encoding='utf-8')

    # append to mint_actions.log with receipts fetched
    try:
        log_entries = json.loads(MINT_LOG.read_text(encoding='utf-8')) if MINT_LOG.exists() else []
    except Exception:
        log_entries = []
    for t in updated_tokens:
        log_entries.append({'action':'receipt_fetched','txHash': t.get('txHash'), 'tokenId': t.get('tokenId'), 'block': t.get('block'), 'timestamp': datetime.utcnow().isoformat() + 'Z'})
    MINT_LOG.write_text(json.dumps(log_entries, indent=2), encoding='utf-8')

    print('Done. Summary:')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    load_env_dotenv()
    main()
