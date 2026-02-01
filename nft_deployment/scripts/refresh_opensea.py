#!/usr/bin/env python3
"""
OpenSea Metadata Refresh Script
Triggers metadata refresh for all minted NFTs on OpenSea Testnet (Amoy).
"""

import json
import time
import sys
from pathlib import Path

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("[ERROR] requests library required: pip install requests")
    sys.exit(1)


# Configuration
CONTRACT_ADDRESS = "0x5A1A74ca9eEBA5fB2cB623fDdDA1433AC8eB676B"
CHAIN = "amoy"
OPENSEA_API_BASE = "https://testnets-api.opensea.io/api/v2"


def load_minting_results() -> list:
    """Load minted token IDs from minting_results.json."""
    script_dir = Path(__file__).parent
    results_path = script_dir.parent / "hardhat_deploy" / "minting_results.json"

    if not results_path.exists():
        print(f"[ERROR] Minting results not found: {results_path}")
        return []

    with open(results_path, "r") as f:
        data = json.load(f)

    return data.get("tokens", [])


def refresh_token_metadata(token_id: str) -> bool:
    """Trigger OpenSea metadata refresh for a single token."""
    url = f"{OPENSEA_API_BASE}/chain/{CHAIN}/contract/{CONTRACT_ADDRESS}/nfts/{token_id}/refresh"

    headers = {
        "Accept": "application/json",
    }

    try:
        response = requests.post(url, headers=headers)

        if response.status_code == 200:
            return True
        elif response.status_code == 429:
            print(f"  Rate limited, waiting...")
            time.sleep(5)
            return refresh_token_metadata(token_id)  # Retry
        else:
            print(f"  Status {response.status_code}: {response.text[:100]}")
            return False

    except Exception as e:
        print(f"  Error: {e}")
        return False


def main():
    print("=" * 60)
    print("OpenSea Testnet Metadata Refresh")
    print("=" * 60)
    print(f"\nContract: {CONTRACT_ADDRESS}")
    print(f"Chain: {CHAIN}")
    print(f"OpenSea: https://testnets.opensea.io/assets/{CHAIN}/{CONTRACT_ADDRESS}\n")

    tokens = load_minting_results()

    if not tokens:
        print("[ERROR] No tokens found to refresh")
        return

    print(f"Found {len(tokens)} tokens to refresh\n")

    success_count = 0

    for token in tokens:
        token_id = token["tokenId"]
        original_id = token.get("originalId", "")[:8]

        print(f"Refreshing Token #{token_id} ({original_id})...", end=" ", flush=True)

        if refresh_token_metadata(token_id):
            print("OK")
            success_count += 1
        else:
            print("FAILED")

        time.sleep(1)  # Rate limiting

    print(f"\n{'=' * 60}")
    print(f"Refresh complete: {success_count}/{len(tokens)} tokens")
    print(f"\nView your collection:")
    print(f"  https://testnets.opensea.io/assets/{CHAIN}/{CONTRACT_ADDRESS}")
    print(f"\nIndividual tokens:")
    for token in tokens:
        print(f"  Token #{token['tokenId']}: https://testnets.opensea.io/assets/{CHAIN}/{CONTRACT_ADDRESS}/{token['tokenId']}")


if __name__ == "__main__":
    main()
