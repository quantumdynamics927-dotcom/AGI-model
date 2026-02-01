"""
Mint script to upload manifest to Web3.storage (IPFS) and call `safeMint` on the deployed TMTGenesis contract.

Usage:
  - Copy `.env.example` to `.env` and fill the values
  - Create `manifest.json` or modify the `manifest` variable below
  - python scripts/mint.py

Notes:
  - This script uses Web3.storage for pinning (WEB3_STORAGE_API_KEY). You can replace with Pinata or Web3.Storage SDK.
  - The contract ABI is minimal (safeMint). Replace or expand ABI as needed.
"""

import os
import json
import hashlib
import requests
from dotenv import load_dotenv
from web3 import Web3

load_dotenv()

RPC_URL = os.getenv("POLYGON_RPC_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
WEB3_STORAGE_API_KEY = os.getenv("WEB3_STORAGE_API_KEY")
TO_ADDRESS = os.getenv("WALLET_ADDRESS")  # recipient

if not RPC_URL or not PRIVATE_KEY or not CONTRACT_ADDRESS or not WEB3_STORAGE_API_KEY:
    raise SystemExit("Missing required .env variables. See .env.example")

w3 = Web3(Web3.HTTPProvider(RPC_URL))
if not w3.is_connected():
    raise SystemExit("Cannot connect to RPC_URL")

# Minimal ABI with safeMint
ABI = [
    {
        "inputs": [
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "string", "name": "cid", "type": "string"},
            {"internalType": "bytes32", "name": "manifestHash", "type": "bytes32"}
        ],
        "name": "safeMint",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

contract = w3.eth.contract(address=Web3.toChecksumAddress(CONTRACT_ADDRESS), abi=ABI)

# Example manifest — replace or load file
manifest = {
    "project": "TMT-OS",
    "milestone": "Genesis Vault Implementation",
    "tech_stack": ["VAE", "Quantum-Safe Hashing", "Zero-Trust Gateway"],
    "integrity_hash": "GENERATED_BY_TMT_OS_ENGINE"
}


def pin_to_web3_storage(json_obj):
    """Pin JSON object to web3.storage and return CID."""
    url = "https://api.web3.storage/upload"
    headers = {"Authorization": f"Bearer {WEB3_STORAGE_API_KEY}"}
    # web3.storage accepts files multipart, we send a small json file
    files = {"file": ("manifest.json", json.dumps(json_obj).encode())}
    print("Uploading manifest to Web3.storage...")
    r = requests.post(url, headers=headers, files=files)
    r.raise_for_status()
    data = r.json()
    cid = data.get("cid")
    if not cid:
        raise RuntimeError("No CID returned from web3.storage: %s" % data)
    print("Pinned CID:", cid)
    return cid


def compute_manifest_hash(json_obj):
    """Compute sha256(manifest) -> bytes32"""
    raw = json.dumps(json_obj, separators=(',', ':'), sort_keys=True).encode()
    digest = hashlib.sha256(raw).digest()  # 32 bytes
    return digest


def build_and_send_tx(to_address, cid, manifest_hash_bytes):
    acct = w3.eth.account.from_key(PRIVATE_KEY)
    nonce = w3.eth.get_transaction_count(acct.address)

    # manifest_hash_bytes is raw bytes (32). Web3 will encode as bytes32.
    txn = contract.functions.safeMint(Web3.toChecksumAddress(to_address), cid, manifest_hash_bytes).build_transaction({
        "chainId": w3.eth.chain_id,
        "gas": 400000,
        "nonce": nonce,
    })

    signed = acct.sign_transaction(txn)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    print("Sent tx:", tx_hash.hex())
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print("Receipt:", receipt)
    return receipt


if __name__ == "__main__":
    cid = pin_to_web3_storage(manifest)
    manifest_hash = compute_manifest_hash(manifest)
    print("Manifest hash (sha256 - hex):", manifest_hash.hex())

    if not TO_ADDRESS:
        print("WALLET_ADDRESS env var not set; using deployer as recipient")
        TO_ADDRESS = w3.eth.account.from_key(PRIVATE_KEY).address

    receipt = build_and_send_tx(TO_ADDRESS, cid, manifest_hash)
    print("Mint completed in tx:", receipt.transactionHash.hex())
