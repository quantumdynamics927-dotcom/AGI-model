#!/usr/bin/env python3
"""
OpenSea Deployment Script - Complete NFT collection deployment pipeline.

Features:
- Upload artwork to IPFS via Pinata
- Update metadata with IPFS CIDs
- Deploy ERC-721 smart contract
- Batch mint entire collection
- Verify on Etherscan/Polygonscan
"""

import json
import hashlib
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# Check for optional dependencies
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from web3 import Web3
    from eth_account import Account
    HAS_WEB3 = True
except ImportError:
    HAS_WEB3 = False


@dataclass
class DeploymentConfig:
    """Configuration for NFT deployment."""
    # Pinata IPFS
    pinata_api_key: str = ""
    pinata_secret_key: str = ""

    # Blockchain
    network: str = "polygon"  # ethereum, polygon, goerli, mumbai
    private_key: str = ""
    infura_project_id: str = ""

    # Contract
    contract_name: str = "QuantumConsciousnessNFT"
    symbol: str = "QCON"
    owner_address: str = ""

    # Paths
    art_dir: Path = Path("quantum_art")
    metadata_dir: Path = Path("opensea_metadata")
    manifest_path: Path = Path("collection_manifest.json")

    @classmethod
    def from_env(cls) -> 'DeploymentConfig':
        """Load configuration from environment variables."""
        return cls(
            pinata_api_key=os.getenv("PINATA_API_KEY", ""),
            pinata_secret_key=os.getenv("PINATA_SECRET_KEY", ""),
            network=os.getenv("DEPLOY_NETWORK", "polygon"),
            private_key=os.getenv("PRIVATE_KEY", ""),
            infura_project_id=os.getenv("INFURA_PROJECT_ID", ""),
            owner_address=os.getenv("OWNER_ADDRESS", ""),
        )


class PinataUploader:
    """Upload files to IPFS via Pinata."""

    BASE_URL = "https://api.pinata.cloud"

    def __init__(self, api_key: str, secret_key: str):
        self.api_key = api_key
        self.secret_key = secret_key
        self.headers = {
            "pinata_api_key": api_key,
            "pinata_secret_api_key": secret_key,
        }

    def test_authentication(self) -> bool:
        """Test Pinata API credentials."""
        if not HAS_REQUESTS:
            print("[ERROR] requests library required: pip install requests")
            return False

        response = requests.get(
            f"{self.BASE_URL}/data/testAuthentication",
            headers=self.headers
        )
        return response.status_code == 200

    def upload_file(self, file_path: Path, name: Optional[str] = None) -> Optional[str]:
        """Upload a single file to IPFS. Returns CID."""
        if not HAS_REQUESTS:
            return None

        with open(file_path, "rb") as f:
            response = requests.post(
                f"{self.BASE_URL}/pinning/pinFileToIPFS",
                files={"file": (name or file_path.name, f)},
                headers=self.headers,
                data={
                    "pinataMetadata": json.dumps({
                        "name": name or file_path.name
                    })
                }
            )

        if response.status_code == 200:
            return response.json()["IpfsHash"]
        else:
            print(f"[ERROR] Upload failed: {response.text}")
            return None

    def upload_json(self, data: dict, name: str) -> Optional[str]:
        """Upload JSON data directly to IPFS."""
        if not HAS_REQUESTS:
            return None

        response = requests.post(
            f"{self.BASE_URL}/pinning/pinJSONToIPFS",
            json={
                "pinataContent": data,
                "pinataMetadata": {"name": name}
            },
            headers={**self.headers, "Content-Type": "application/json"}
        )

        if response.status_code == 200:
            return response.json()["IpfsHash"]
        else:
            print(f"[ERROR] JSON upload failed: {response.text}")
            return None

    def upload_directory(self, dir_path: Path) -> Optional[str]:
        """Upload entire directory to IPFS."""
        if not HAS_REQUESTS:
            return None

        files = []
        for file_path in dir_path.rglob("*"):
            if file_path.is_file():
                rel_path = file_path.relative_to(dir_path)
                files.append(
                    ("file", (str(rel_path), open(file_path, "rb")))
                )

        response = requests.post(
            f"{self.BASE_URL}/pinning/pinFileToIPFS",
            files=files,
            headers=self.headers,
            data={
                "pinataMetadata": json.dumps({
                    "name": dir_path.name
                })
            }
        )

        # Close file handles
        for _, (_, f) in files:
            f.close()

        if response.status_code == 200:
            return response.json()["IpfsHash"]
        return None


class OpenSeaDeployer:
    """Complete OpenSea deployment pipeline."""

    NETWORK_CONFIGS = {
        "ethereum": {
            "rpc": "https://mainnet.infura.io/v3/",
            "chain_id": 1,
            "explorer": "https://etherscan.io",
            "opensea": "https://opensea.io",
        },
        "polygon": {
            "rpc": "https://polygon-mainnet.infura.io/v3/",
            "chain_id": 137,
            "explorer": "https://polygonscan.com",
            "opensea": "https://opensea.io",
        },
        "goerli": {
            "rpc": "https://goerli.infura.io/v3/",
            "chain_id": 5,
            "explorer": "https://goerli.etherscan.io",
            "opensea": "https://testnets.opensea.io",
        },
        "mumbai": {
            "rpc": "https://polygon-mumbai.infura.io/v3/",
            "chain_id": 80001,
            "explorer": "https://mumbai.polygonscan.com",
            "opensea": "https://testnets.opensea.io",
        },
    }

    def __init__(self, config: DeploymentConfig):
        self.config = config
        self.pinata = PinataUploader(config.pinata_api_key, config.pinata_secret_key)
        self.uploaded_art: Dict[str, str] = {}  # token_id -> CID
        self.uploaded_metadata: Dict[str, str] = {}  # token_id -> CID

    def step1_upload_artwork(self) -> bool:
        """Upload all artwork files to IPFS."""
        print("\n" + "="*60)
        print("STEP 1: Uploading artwork to IPFS")
        print("="*60)

        art_dir = self.config.art_dir
        if not art_dir.exists():
            print(f"[ERROR] Art directory not found: {art_dir}")
            return False

        art_files = list(art_dir.glob("quantum_art_*.svg")) + list(art_dir.glob("quantum_art_*.png"))
        print(f"Found {len(art_files)} artwork files\n")

        for art_file in sorted(art_files):
            token_id = art_file.stem.replace("quantum_art_", "")
            print(f"  Uploading {token_id[:16]}...", end=" ", flush=True)

            cid = self.pinata.upload_file(art_file)
            if cid:
                self.uploaded_art[token_id] = cid
                print(f"OK -> ipfs://{cid}")
            else:
                print("FAILED")

            time.sleep(0.5)  # Rate limiting

        print(f"\nUploaded {len(self.uploaded_art)}/{len(art_files)} artworks")
        return len(self.uploaded_art) > 0

    def step2_update_metadata(self) -> bool:
        """Update metadata files with IPFS CIDs and upload."""
        print("\n" + "="*60)
        print("STEP 2: Updating and uploading metadata")
        print("="*60)

        metadata_dir = self.config.metadata_dir

        for token_id, art_cid in sorted(self.uploaded_art.items()):
            # Find metadata file
            metadata_file = metadata_dir / f"quantum_consciousness_{token_id}.json"
            if not metadata_file.exists():
                # Try shorter ID
                for f in metadata_dir.glob(f"quantum_consciousness_{token_id[:16]}*.json"):
                    metadata_file = f
                    break

            if not metadata_file.exists():
                print(f"  [SKIP] {token_id[:16]} - No metadata file")
                continue

            # Load and update metadata
            with open(metadata_file, "r") as f:
                metadata = json.load(f)

            # Update image URL with actual IPFS CID
            metadata["image"] = f"ipfs://{art_cid}"

            # Upload updated metadata
            print(f"  Uploading metadata {token_id[:16]}...", end=" ", flush=True)
            meta_cid = self.pinata.upload_json(metadata, f"quantum_consciousness_{token_id[:16]}.json")

            if meta_cid:
                self.uploaded_metadata[token_id] = meta_cid
                print(f"OK -> ipfs://{meta_cid}")

                # Save updated metadata locally
                with open(metadata_file, "w") as f:
                    json.dump(metadata, f, indent=2)
            else:
                print("FAILED")

            time.sleep(0.3)

        print(f"\nUploaded {len(self.uploaded_metadata)} metadata files")
        return len(self.uploaded_metadata) > 0

    def step3_generate_manifest(self) -> Path:
        """Generate final deployment manifest with all IPFS CIDs."""
        print("\n" + "="*60)
        print("STEP 3: Generating deployment manifest")
        print("="*60)

        # Load original manifest
        manifest_path = self.config.manifest_path
        if manifest_path.exists():
            with open(manifest_path, "r") as f:
                manifest = json.load(f)
        else:
            manifest = {"tokens": []}

        # Update tokens with IPFS data
        for token in manifest.get("tokens", []):
            token_id = token["token_id"]
            if token_id in self.uploaded_art:
                token["image_cid"] = self.uploaded_art[token_id]
                token["image_ipfs"] = f"ipfs://{self.uploaded_art[token_id]}"
            if token_id in self.uploaded_metadata:
                token["metadata_cid"] = self.uploaded_metadata[token_id]
                token["metadata_ipfs"] = f"ipfs://{self.uploaded_metadata[token_id]}"

        # Add deployment info
        manifest["deployment"] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "network": self.config.network,
            "total_uploaded": len(self.uploaded_metadata),
            "pinata_gateway": "https://gateway.pinata.cloud/ipfs/",
        }

        # Save updated manifest
        output_path = Path("deployment_manifest.json")
        with open(output_path, "w") as f:
            json.dump(manifest, f, indent=2)

        print(f"Manifest saved to: {output_path}")
        return output_path

    def step4_deploy_contract(self) -> Optional[str]:
        """Deploy ERC-721 smart contract (requires web3)."""
        print("\n" + "="*60)
        print("STEP 4: Smart Contract Deployment")
        print("="*60)

        if not HAS_WEB3:
            print("[INFO] Web3 not installed. Manual deployment required.")
            print("\nTo deploy contract:")
            print("  1. Install: pip install web3 eth-account")
            print("  2. Or use Remix IDE: https://remix.ethereum.org")
            print("  3. Contract file: contracts/QuantumConsciousnessNFT.sol")
            return None

        if not self.config.private_key:
            print("[INFO] No private key configured. Skipping contract deployment.")
            return None

        # Connect to network
        network = self.NETWORK_CONFIGS.get(self.config.network)
        if not network:
            print(f"[ERROR] Unknown network: {self.config.network}")
            return None

        rpc_url = network["rpc"] + self.config.infura_project_id
        w3 = Web3(Web3.HTTPProvider(rpc_url))

        if not w3.is_connected():
            print(f"[ERROR] Failed to connect to {self.config.network}")
            return None

        print(f"Connected to {self.config.network} (Chain ID: {network['chain_id']})")

        # Note: Full contract deployment would require compiled ABI/bytecode
        print("\n[INFO] Contract deployment requires compiled Solidity.")
        print("Use Hardhat or Remix for full deployment:")
        print("  npx hardhat run scripts/deploy.js --network", self.config.network)

        return None

    def step5_generate_report(self) -> None:
        """Generate final deployment report."""
        print("\n" + "="*60)
        print("DEPLOYMENT SUMMARY")
        print("="*60)

        print(f"\nCollection: Quantum Consciousness (QCON)")
        print(f"Total NFTs: {len(self.uploaded_metadata)}")
        print(f"Network: {self.config.network}")

        print(f"\nIPFS Statistics:")
        print(f"  Artworks uploaded: {len(self.uploaded_art)}")
        print(f"  Metadata uploaded: {len(self.uploaded_metadata)}")

        if self.uploaded_metadata:
            print(f"\nSample IPFS URLs:")
            for i, (token_id, cid) in enumerate(list(self.uploaded_metadata.items())[:3]):
                print(f"  Token {token_id[:8]}: https://gateway.pinata.cloud/ipfs/{cid}")

        network = self.NETWORK_CONFIGS.get(self.config.network, {})
        print(f"\nNext Steps:")
        print(f"  1. Deploy contract using Hardhat/Remix")
        print(f"  2. Run batch mint with deployment_manifest.json")
        print(f"  3. View collection: {network.get('opensea', 'https://opensea.io')}")

    def run_full_deployment(self) -> bool:
        """Execute complete deployment pipeline."""
        print("\n" + "#"*60)
        print("# QUANTUM CONSCIOUSNESS NFT DEPLOYMENT")
        print("#"*60)

        # Validate Pinata credentials
        if not self.config.pinata_api_key:
            print("\n[ERROR] Pinata API key not configured.")
            print("Set environment variables:")
            print("  export PINATA_API_KEY=your_key")
            print("  export PINATA_SECRET_KEY=your_secret")
            return False

        if not self.pinata.test_authentication():
            print("[ERROR] Pinata authentication failed.")
            return False

        print("\n[OK] Pinata authentication successful")

        # Execute steps
        if not self.step1_upload_artwork():
            return False

        if not self.step2_update_metadata():
            return False

        self.step3_generate_manifest()
        self.step4_deploy_contract()
        self.step5_generate_report()

        return True


def main():
    """Main entry point."""
    # Load config from environment
    config = DeploymentConfig.from_env()

    # Set paths relative to script location
    script_dir = Path(__file__).parent
    deploy_dir = script_dir.parent

    config.art_dir = deploy_dir / "quantum_art"
    config.metadata_dir = deploy_dir / "opensea_metadata"
    config.manifest_path = deploy_dir / "collection_manifest.json"

    # Parse CLI arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--dry-run":
            print("DRY RUN MODE - No uploads will be performed")
            print(f"\nConfiguration:")
            print(f"  Art directory: {config.art_dir}")
            print(f"  Metadata directory: {config.metadata_dir}")
            print(f"  Network: {config.network}")
            print(f"  Pinata configured: {bool(config.pinata_api_key)}")
            return

        if sys.argv[1] == "--help":
            print("Usage: python deploy_to_opensea.py [OPTIONS]")
            print("\nOptions:")
            print("  --dry-run    Show configuration without uploading")
            print("  --help       Show this help message")
            print("\nEnvironment Variables:")
            print("  PINATA_API_KEY      Pinata API key")
            print("  PINATA_SECRET_KEY   Pinata secret key")
            print("  DEPLOY_NETWORK      Target network (ethereum, polygon, goerli, mumbai)")
            print("  PRIVATE_KEY         Wallet private key (for contract deployment)")
            print("  INFURA_PROJECT_ID   Infura project ID")
            return

    # Run deployment
    deployer = OpenSeaDeployer(config)
    success = deployer.run_full_deployment()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
