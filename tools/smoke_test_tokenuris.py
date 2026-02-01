import requests
RPC='https://polygon-rpc.com'
CONTRACT='0x345b67bf9e92a6f23960a27238337d6e6a0f63f6'
print('Starting smoke test (tokenURI + ownerOf)')
method='0xc87b56dd'  # tokenURI(uint256)
owner_method='0x6352211e'  # ownerOf(uint256)
ids=[8,9,10,11,12]

import time

for tid in ids:
    print(f"Querying token {tid}...")
    tid_hex = format(tid, 'x').rjust(64, '0')
    # Try tokenURI with retries
    tokenURI = None
    for attempt in range(1,4):
        data = method + tid_hex
        payload={"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":CONTRACT,"data":data},"latest"]}
        try:
            r = requests.post(RPC, json=payload, timeout=30)
            if r.ok:
                res = r.json().get('result')
                if res and res!='0x':
                    try:
                        hexdata = res[2:]
                        length = int(hexdata[64:128],16)
                        start = 128
                        raw = hexdata[start:start+length*2]
                        tokenURI = bytes.fromhex(raw).decode('utf-8')
                    except Exception as e:
                        tokenURI = f"<decode error: {e}>"
                    break
                else:
                    print(f"  attempt {attempt}: empty result")
            else:
                print(f"  attempt {attempt}: HTTP {r.status_code} {r.text[:200]}")
        except Exception as e:
            print(f"  attempt {attempt}: RPC error {e}")
        time.sleep(1)
    if tokenURI:
        print(f"Token {tid}: tokenURI -> {tokenURI}")
        if tokenURI.startswith('ipfs://'):
            url = tokenURI.replace('ipfs://','https://gateway.pinata.cloud/ipfs/')
            try:
                rr = requests.get(url, timeout=20)
                print(f"  -> gateway status: {rr.status_code}; content-type: {rr.headers.get('Content-Type')} ; size: {len(rr.content)}")
            except Exception as e:
                print(f"  -> gateway fetch error: {e}")
        else:
            try:
                rr = requests.get(tokenURI, timeout=20)
                print(f"  -> http status: {rr.status_code}; content-type: {rr.headers.get('Content-Type')} ; size: {len(rr.content)}")
            except Exception as e:
                print(f"  -> http fetch error: {e}")
    else:
        print(f"Token {tid}: tokenURI unavailable after retries")
    # ownerOf check
    for attempt in range(1,3):
        try:
            data = owner_method + tid_hex
            payload={"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":CONTRACT,"data":data},"latest"]}
            r = requests.post(RPC, json=payload, timeout=20)
            if r.ok:
                res = r.json().get('result')
                if res and res!='0x':
                    addr = '0x' + res[-40:]
                    print(f"  ownerOf: {addr}")
                    break
            print(f"  ownerOf attempt {attempt}: no result")
        except Exception as e:
            print(f"  ownerOf attempt {attempt}: RPC error {e}")
        time.sleep(0.5)
print('\nSmoke test complete')