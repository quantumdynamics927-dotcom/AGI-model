#!/usr/bin/env python3
import os, json, requests
from pathlib import Path
# load .env
p = Path(__file__).resolve().parent.parent / '.env'
if p.exists():
    for L in p.read_text().splitlines():
        if '=' in L and not L.strip().startswith('#'):
            k,v = L.split('=',1)
            os.environ[k.strip()] = v.strip().strip('"').strip("'")
RPC = os.environ.get('POLYGON_RPC_URL')
ADDR = os.environ.get('WALLET_ADDRESS')
if not RPC or not ADDR:
    print('Missing RPC or address in .env')
    raise SystemExit(1)
body = {"jsonrpc":"2.0","id":1,"method":"eth_getBalance","params":[ADDR, "latest"]}
resp = requests.post(RPC, json=body, timeout=10)
if resp.status_code!=200:
    print('RPC error', resp.status_code, resp.text); raise SystemExit(1)
res = resp.json()
bal_hex = res.get('result')
bal = int(bal_hex,16)/1e18
print(ADDR, 'balance MATIC=', bal)