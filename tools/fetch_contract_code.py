#!/usr/bin/env python3
"""Fetch on-chain contract bytecode for address in verification_manifest.json and save to file."""
from pathlib import Path
import json
import os
import requests

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / 'nft_deployment' / 'verification_manifest.json'
OUT = ROOT / 'nft_deployment' / 'contract_onchain_code.bin'


def load_env():
    envp = ROOT / '.env'
    if envp.exists():
        for ln in envp.read_text(encoding='utf8').splitlines():
            ln = ln.strip()
            if ln and not ln.startswith('#') and '=' in ln:
                k, v = ln.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def rpc_post(rpc, method, params):
    r = requests.post(rpc, json={'jsonrpc':'2.0','id':1,'method':method,'params':params}, timeout=20)
    r.raise_for_status()
    return r.json()


def main():
    load_env()
    rpc = os.environ.get('POLYGON_RPC_URL') or os.environ.get('RPC_URL')
    if not rpc:
        print('No RPC in env (POLYGON_RPC_URL)')
        return
    if not MANIFEST.exists():
        print('No verification manifest', MANIFEST)
        return
    m = json.loads(MANIFEST.read_text(encoding='utf8'))
    contract = m.get('contract')
    if not contract:
        print('No contract in manifest')
        return
    try:
        res = rpc_post(rpc, 'eth_getCode', [contract, 'latest'])
        code = res.get('result')
        if not code:
            print('No code returned')
            return
        OUT.write_text(code, encoding='utf8')
        print('Wrote on-chain code to', OUT, 'len', len(code))
    except Exception as e:
        print('RPC error', e)

if __name__ == '__main__':
    main()
