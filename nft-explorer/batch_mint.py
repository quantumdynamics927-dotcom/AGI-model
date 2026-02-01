#!/usr/bin/env python3
"""
Batch NFT Minter for Polygon
Mints unmapped NFT metadata files to the contract
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime

try:
    from web3 import Web3
    from eth_account import Account
except ImportError:
    print("[ERROR] web3 not installed. Run: pip install web3")
    exit(1)

# Configuration
CONTRACT_ADDRESS = "0x345b67bf9e92a6f23960a27238337d6e6a0f63f6"
POLYGON_RPC = "https://polygon-rpc.com"
# Alternative RPCs if needed:
# POLYGON_RPC = "https://rpc-mainnet.maticvigil.com"
# POLYGON_RPC = "https://polygon-mainnet.g.alchemy.com/v2/YOUR_KEY"

# Paths
BASE_DIR = Path(__file__).parent.parent
NFT_METADATA_DIR = BASE_DIR / "nft_metadata"
IPFS_UPLOADER_PATH = BASE_DIR / "TMT-OS" / "consciousness" / "ipfs_uploader.py"

# Minimal ERC721 ABI for minting
CONTRACT_ABI = [
    {
        "inputs": [{"name": "to", "type": "address"}, {"name": "tokenURI", "type": "string"}],
        "name": "safeMint",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "totalSupply",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"name": "tokenId", "type": "uint256"}],
        "name": "tokenURI",
        "outputs": [{"name": "", "type": "string"}],
        "stateMutability": "view",
        "type": "function"
    }
]

def load_private_key():
    """Load private key from environment or file"""
    # Try environment variable first
    pk = os.environ.get("POLYGON_PRIVATE_KEY") or os.environ.get("PRIVATE_KEY")
    if pk:
        return pk

    # Try config file
    config_path = BASE_DIR / "config" / "wallet_config.json"
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
            return config.get("private_key")

    # Prompt user
    print("\n[WARNING] No private key found!")
    print("Set POLYGON_PRIVATE_KEY environment variable or create config/wallet_config.json")
    return None

def get_unmapped_files():
    """Get list of NFT metadata files without token IDs"""
    unmapped = []

    for filepath in NFT_METADATA_DIR.glob("*.json"):
        if filepath.suffix == '.json' and not filepath.name.endswith('.bak'):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Check if already has token ID
                has_token_id = False
                if 'nft' in data and 'minted_tx' in data['nft']:
                    has_token_id = data['nft']['minted_tx'].get('tokenId') is not None

                if not has_token_id:
                    # Determine type
                    if 'quantum_properties' in data:
                        nft_type = 'quantum'
                    elif 'scientific_data' in data:
                        nft_type = 'molecular'
                    elif 'provenance' in data or 'quantum_hamiltonian' in data:
                        nft_type = 'metatron'
                    else:
                        nft_type = 'unknown'

                    unmapped.append({
                        'path': filepath,
                        'name': data.get('name', filepath.stem),
                        'type': nft_type,
                        'data': data
                    })
            except Exception as e:
                print(f"  [ERROR] Failed to read {filepath.name}: {e}")

    return unmapped

def upload_to_ipfs(metadata, name="nft_metadata"):
    """Upload metadata to IPFS using the ipfs_uploader module"""
    import sys
    sys.path.insert(0, str(BASE_DIR / "TMT-OS" / "consciousness"))

    try:
        from ipfs_uploader import IPFSUploader
        uploader = IPFSUploader("pinata")
        cid, uri = uploader.upload_json(metadata, name)
        return cid, uri
    except Exception as e:
        print(f"  [ERROR] IPFS upload failed: {e}")
        return None, None

def mint_nft(w3, contract, account, to_address, token_uri):
    """Mint a single NFT"""
    try:
        # Build transaction
        nonce = w3.eth.get_transaction_count(account.address)
        gas_price = w3.eth.gas_price

        # Estimate gas
        try:
            gas_estimate = contract.functions.safeMint(to_address, token_uri).estimate_gas({
                'from': account.address
            })
            gas_limit = int(gas_estimate * 1.2)  # 20% buffer
        except Exception as e:
            print(f"  [WARNING] Gas estimation failed, using default: {e}")
            gas_limit = 300000

        tx = contract.functions.safeMint(to_address, token_uri).build_transaction({
            'from': account.address,
            'nonce': nonce,
            'gas': gas_limit,
            'gasPrice': gas_price,
            'chainId': 137  # Polygon mainnet
        })

        # Sign and send
        signed_tx = w3.eth.account.sign_transaction(tx, account.key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

        print(f"  TX sent: {tx_hash.hex()}")

        # Wait for receipt
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

        if receipt['status'] == 1:
            # Extract token ID from logs
            token_id = None
            for log in receipt['logs']:
                # Transfer event topic
                if log['topics'][0].hex() == '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef':
                    token_id = int(log['topics'][3].hex(), 16)
                    break

            return {
                'success': True,
                'tx_hash': tx_hash.hex(),
                'block': receipt['blockNumber'],
                'token_id': token_id,
                'gas_used': receipt['gasUsed']
            }
        else:
            return {'success': False, 'error': 'Transaction reverted'}

    except Exception as e:
        return {'success': False, 'error': str(e)}

def update_metadata_with_mint(filepath, token_id, tx_hash, block):
    """Update metadata file with minting data"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Initialize nft section if needed
    if 'nft' not in data:
        data['nft'] = {}

    # Add minted_tx data
    data['nft']['minted_tx'] = {
        'network': 'POLYGON',
        'tokenId': token_id,
        'tx_hash': tx_hash,
        'block': block,
        'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        'from': '0x0000000000000000000000000000000000000000',
        'to': CONTRACT_ADDRESS
    }

    # Add OpenSea URL
    if 'market' not in data['nft']:
        data['nft']['market'] = {}
    data['nft']['market']['opensea'] = {
        'url': f"https://opensea.io/assets/matic/{CONTRACT_ADDRESS}/{token_id}",
        'indexed': False,
        'checked_at': datetime.utcnow().isoformat() + 'Z'
    }

    # Write updated
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    print(f"  [OK] Updated {filepath.name}")

def main():
    print("=" * 60)
    print("NFT Batch Minter - Polygon")
    print("=" * 60)
    print(f"Contract: {CONTRACT_ADDRESS}")
    print()

    # Get unmapped files
    unmapped = get_unmapped_files()
    print(f"Found {len(unmapped)} unmapped NFT files:")
    for i, nft in enumerate(unmapped):
        print(f"  [{i+1}] {nft['name'][:50]}... ({nft['type']})")

    if not unmapped:
        print("\nNo unmapped NFTs to mint!")
        return

    # Load private key
    private_key = load_private_key()
    if not private_key:
        print("\n[SIMULATION MODE] No private key - showing what would be minted")
        for nft in unmapped:
            print(f"  Would mint: {nft['name']}")
        return

    # Connect to Polygon
    print("\nConnecting to Polygon...")
    w3 = Web3(Web3.HTTPProvider(POLYGON_RPC))

    if not w3.is_connected():
        print("[ERROR] Failed to connect to Polygon RPC")
        return

    print(f"  Connected! Chain ID: {w3.eth.chain_id}")

    # Setup account
    account = Account.from_key(private_key)
    print(f"  Wallet: {account.address}")

    balance = w3.eth.get_balance(account.address)
    matic_balance = w3.from_wei(balance, 'ether')
    print(f"  Balance: {matic_balance:.4f} MATIC")

    if matic_balance < 0.1:
        print("[WARNING] Low MATIC balance! You may need more for gas.")

    # Setup contract
    contract = w3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=CONTRACT_ABI)

    # Get current total supply
    try:
        total_supply = contract.functions.totalSupply().call()
        print(f"  Current total supply: {total_supply}")
    except:
        total_supply = "unknown"

    # Confirm
    print("\n" + "-" * 60)
    print(f"Ready to mint {len(unmapped)} NFTs")
    print("-" * 60)

    confirm = input("\nProceed with minting? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("Cancelled.")
        return

    # Mint each NFT
    successful = 0
    failed = 0

    for i, nft in enumerate(unmapped):
        print(f"\n[{i+1}/{len(unmapped)}] Minting: {nft['name'][:40]}...")

        # Upload to IPFS first
        print("  Uploading to IPFS...")
        cid, ipfs_uri = upload_to_ipfs(nft['data'], nft['name'][:50])

        if not ipfs_uri:
            print("  [SKIP] IPFS upload failed")
            failed += 1
            continue

        print(f"  IPFS: {ipfs_uri}")

        # Mint NFT
        print("  Minting on Polygon...")
        result = mint_nft(w3, contract, account, account.address, ipfs_uri)

        if result['success']:
            print(f"  [OK] Token #{result['token_id']} minted!")
            print(f"       TX: {result['tx_hash']}")
            print(f"       Block: {result['block']}")
            print(f"       Gas: {result['gas_used']}")

            # Update metadata file
            update_metadata_with_mint(
                nft['path'],
                result['token_id'],
                result['tx_hash'],
                result['block']
            )

            # Update IPFS CID in metadata
            nft['data']['nft'] = nft['data'].get('nft', {})
            nft['data']['nft']['ipfs_cid'] = cid

            successful += 1
        else:
            print(f"  [FAILED] {result['error']}")
            failed += 1

        # Rate limiting
        if i < len(unmapped) - 1:
            print("  Waiting 3s before next mint...")
            time.sleep(3)

    # Summary
    print("\n" + "=" * 60)
    print("MINTING COMPLETE")
    print("=" * 60)
    print(f"  Successful: {successful}")
    print(f"  Failed: {failed}")

    if successful > 0:
        print(f"\nRun 'python sync_nft_data.py' to update nft_data.js")

if __name__ == "__main__":
    main()
