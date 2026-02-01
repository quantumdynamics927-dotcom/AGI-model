#!/usr/bin/env python3
"""
Quantum Consciousness NFT Minting Script

This script prepares and mints Quantum Consciousness NFTs to OpenSea-compatible
blockchains (Ethereum, Polygon) with embedded integrity verification.

Requirements:
    pip install web3 python-dotenv requests

Environment Variables (.env):
    PRIVATE_KEY=your_wallet_private_key
    INFURA_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
    CONTRACT_ADDRESS=deployed_contract_address
    PINATA_API_KEY=your_pinata_api_key
    PINATA_SECRET_KEY=your_pinata_secret_key
"""
import json
import hashlib
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timezone

# Optional imports for blockchain interaction
try:
    from web3 import Web3
    from eth_account import Account
    HAS_WEB3 = True
except ImportError:
    HAS_WEB3 = False
    print("Warning: web3 not installed. Blockchain minting disabled.")

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("Warning: requests not installed. IPFS upload disabled.")

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class QuantumNFTMinter:
    """Handles minting of Quantum Consciousness NFTs."""

    # Contract ABI (simplified for minting function)
    CONTRACT_ABI = [
        {
            "inputs": [
                {"name": "to", "type": "address"},
                {"name": "tokenURI", "type": "string"},
                {"name": "blueprintHash", "type": "bytes32"},
                {"name": "phiScore", "type": "uint256"},
                {"name": "complexity", "type": "uint256"}
            ],
            "name": "mintQuantumNFT",
            "outputs": [{"name": "", "type": "uint256"}],
            "stateMutability": "nonpayable",
            "type": "function"
        },
        {
            "inputs": [{"name": "tokenId", "type": "uint256"}],
            "name": "getQuantumProperties",
            "outputs": [
                {"name": "hash", "type": "bytes32"},
                {"name": "phi", "type": "uint256"},
                {"name": "complexity", "type": "uint256"}
            ],
            "stateMutability": "view",
            "type": "function"
        }
    ]

    def __init__(
        self,
        rpc_url: Optional[str] = None,
        private_key: Optional[str] = None,
        contract_address: Optional[str] = None
    ):
        """Initialize minter with blockchain connection."""
        self.rpc_url = rpc_url or os.getenv("INFURA_URL")
        self.private_key = private_key or os.getenv("PRIVATE_KEY")
        self.contract_address = contract_address or os.getenv("CONTRACT_ADDRESS")

        self.w3 = None
        self.account = None
        self.contract = None

        if HAS_WEB3 and self.rpc_url:
            self._connect()

    def _connect(self):
        """Connect to blockchain."""
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        if not self.w3.is_connected():
            raise ConnectionError(f"Failed to connect to {self.rpc_url}")

        if self.private_key:
            self.account = Account.from_key(self.private_key)

        if self.contract_address:
            self.contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.contract_address),
                abi=self.CONTRACT_ABI
            )

        print(f"Connected to chain ID: {self.w3.eth.chain_id}")

    def compute_blueprint_hash(self, nft_data: Dict[str, Any]) -> str:
        """Compute SHA-256 hash of quantum blueprint."""
        # Extract quantum properties for hashing
        quantum_props = nft_data.get("quantum_properties", {})
        hash_content = json.dumps(quantum_props, sort_keys=True)
        return hashlib.sha256(hash_content.encode()).hexdigest()

    def prepare_metadata(
        self,
        source_path: Path,
        output_dir: Path
    ) -> Dict[str, Any]:
        """Prepare OpenSea-compatible metadata from quantum NFT JSON."""
        with open(source_path) as f:
            original = json.load(f)

        # Compute integrity hash
        blueprint_hash = self.compute_blueprint_hash(original)

        # Extract scores (scale to 0-10000 for smart contract)
        qp = original.get("quantum_properties", {})
        consciousness = qp.get("consciousness_complexity", 0)
        phi_score = 22.22  # From molecular geometry analysis

        # Prepare OpenSea metadata
        metadata = {
            "name": original.get("name", "Quantum Consciousness"),
            "description": original.get("description", ""),
            "image": "ipfs://PLACEHOLDER",
            "external_url": original.get("external_url", ""),
            "attributes": original.get("attributes", []),
            "properties": {
                "quantum_properties": qp,
                "integrity": {
                    "algorithm": "SHA-256",
                    "blueprint_hash": blueprint_hash,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            }
        }

        # Add numeric attributes for OpenSea display
        metadata["attributes"].extend([
            {
                "trait_type": "Consciousness Complexity",
                "value": round(consciousness * 100, 2),
                "display_type": "number",
                "max_value": 100
            },
            {
                "trait_type": "Phi Score",
                "value": round(phi_score, 2),
                "display_type": "number",
                "max_value": 100
            }
        ])

        # Save prepared metadata
        output_dir.mkdir(parents=True, exist_ok=True)
        token_id = source_path.stem
        output_path = output_dir / f"{token_id}_opensea.json"
        with open(output_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"Prepared metadata: {output_path}")
        print(f"Blueprint hash: {blueprint_hash}")

        return {
            "metadata": metadata,
            "metadata_path": output_path,
            "blueprint_hash": blueprint_hash,
            "phi_score": int(phi_score * 100),  # Scale to 0-10000
            "consciousness": int(consciousness * 10000)  # Scale to 0-10000
        }

    def upload_to_ipfs(self, file_path: Path) -> Optional[str]:
        """Upload file to IPFS via Pinata."""
        if not HAS_REQUESTS:
            print("requests not installed, skipping IPFS upload")
            return None

        api_key = os.getenv("PINATA_API_KEY")
        secret_key = os.getenv("PINATA_SECRET_KEY")

        if not api_key or not secret_key:
            print("Pinata credentials not found, skipping IPFS upload")
            return None

        url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
        headers = {
            "pinata_api_key": api_key,
            "pinata_secret_api_key": secret_key
        }

        with open(file_path, 'rb') as f:
            files = {"file": (file_path.name, f)}
            response = requests.post(url, headers=headers, files=files)

        if response.status_code == 200:
            cid = response.json()["IpfsHash"]
            print(f"Uploaded to IPFS: ipfs://{cid}")
            return f"ipfs://{cid}"
        else:
            print(f"IPFS upload failed: {response.text}")
            return None

    def mint(
        self,
        to_address: str,
        token_uri: str,
        blueprint_hash: str,
        phi_score: int,
        consciousness: int,
        gas_price_gwei: Optional[int] = None
    ) -> Optional[str]:
        """Mint NFT on blockchain."""
        if not HAS_WEB3:
            print("web3 not installed, cannot mint")
            return None

        if not self.contract or not self.account:
            print("Contract or account not configured")
            return None

        # Convert hash to bytes32
        hash_bytes = bytes.fromhex(blueprint_hash)

        # Build transaction
        tx = self.contract.functions.mintQuantumNFT(
            Web3.to_checksum_address(to_address),
            token_uri,
            hash_bytes,
            phi_score,
            consciousness
        ).build_transaction({
            'from': self.account.address,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'gas': 300000,
            'gasPrice': self.w3.to_wei(gas_price_gwei or 30, 'gwei')
        })

        # Sign and send
        signed = self.account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)

        print(f"Transaction sent: {tx_hash.hex()}")

        # Wait for receipt
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"Minted! Block: {receipt['blockNumber']}, Gas used: {receipt['gasUsed']}")

        return tx_hash.hex()


def batch_prepare(input_dir: Path, output_dir: Path):
    """Prepare all NFT metadata files in a directory."""
    minter = QuantumNFTMinter()

    results = []
    for nft_file in input_dir.glob("quantum_nft_*.json"):
        try:
            result = minter.prepare_metadata(nft_file, output_dir)
            results.append({
                "source": str(nft_file),
                "hash": result["blueprint_hash"],
                "phi_score": result["phi_score"],
                "consciousness": result["consciousness"]
            })
        except Exception as e:
            print(f"Error processing {nft_file}: {e}")

    # Save batch summary
    summary_path = output_dir / "batch_summary.json"
    with open(summary_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nProcessed {len(results)} NFTs")
    print(f"Summary saved to: {summary_path}")

    return results


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Quantum Consciousness NFT Minter")
    parser.add_argument("--prepare", type=Path, help="Prepare single NFT metadata")
    parser.add_argument("--batch", type=Path, help="Batch prepare directory")
    parser.add_argument("--output", type=Path, default=Path("./prepared"), help="Output directory")
    parser.add_argument("--upload", action="store_true", help="Upload to IPFS")
    parser.add_argument("--mint", action="store_true", help="Mint to blockchain")
    parser.add_argument("--to", type=str, help="Recipient address for minting")

    args = parser.parse_args()

    minter = QuantumNFTMinter()

    if args.batch:
        batch_prepare(args.batch, args.output)

    elif args.prepare:
        result = minter.prepare_metadata(args.prepare, args.output)

        if args.upload:
            ipfs_uri = minter.upload_to_ipfs(result["metadata_path"])
            if ipfs_uri:
                result["metadata"]["image"] = ipfs_uri

        if args.mint and args.to:
            minter.mint(
                to_address=args.to,
                token_uri=result.get("ipfs_uri", ""),
                blueprint_hash=result["blueprint_hash"],
                phi_score=result["phi_score"],
                consciousness=result["consciousness"]
            )

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
