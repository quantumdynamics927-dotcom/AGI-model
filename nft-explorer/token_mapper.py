#!/usr/bin/env python3
"""
NFT Token ID Mapper & Transaction Data Updater
Maps Token IDs from Polygonscan CSV to NFT metadata files
"""

import os
import json
import csv
from pathlib import Path
from datetime import datetime

# Paths
BASE_DIR = Path(__file__).parent.parent
NFT_METADATA_DIR = BASE_DIR / "nft_metadata"
POLYGONSCAN_CSV = Path(r"E:\Descargas\export-token-nft-0x345b67bf9e92a6f23960a27238337d6e6a0f63f6.csv")
CONTRACT_ADDRESS = "0x345b67bf9e92a6f23960a27238337d6e6a0f63f6"

def load_polygonscan_data(csv_path):
    """Load minted NFT data from Polygonscan CSV export"""
    minted = {}
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            token_id = int(row['Token_ID'].strip())
            minted[token_id] = {
                'tx_hash': row['Transaction Hash'].strip(),
                'block': int(row['Blockno'].strip()),
                'timestamp': row['UnixTimestamp'].strip(),
                'datetime': row['DateTime (UTC)'].strip(),
                'from': row['From'].strip(),
                'to': row['To'].strip(),
                'method': row['Method'].strip()
            }
    return minted

def scan_metadata_files():
    """Scan all NFT metadata files and extract token ID info"""
    metadata_files = {}

    for filepath in NFT_METADATA_DIR.glob("*.json"):
        if filepath.suffix == '.json' and not filepath.name.endswith('.bak'):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Extract token ID if present
                token_id = None
                if 'nft' in data and 'minted_tx' in data['nft']:
                    token_id = data['nft']['minted_tx'].get('tokenId')

                # Get file type
                if 'quantum_properties' in data:
                    nft_type = 'quantum'
                elif 'scientific_data' in data:
                    nft_type = 'molecular'
                elif 'provenance' in data or 'quantum_hamiltonian' in data:
                    nft_type = 'metatron'
                else:
                    nft_type = 'unknown'

                metadata_files[filepath.name] = {
                    'path': filepath,
                    'token_id': token_id,
                    'type': nft_type,
                    'name': data.get('name', 'Unknown'),
                    'has_tx_data': 'nft' in data and 'minted_tx' in data['nft'] and data['nft']['minted_tx'].get('tx_hash'),
                    'ipfs_cid': data.get('nft', {}).get('ipfs_cid', ''),
                    'data': data
                }
            except Exception as e:
                print(f"  [ERROR] Failed to read {filepath.name}: {e}")

    return metadata_files

def generate_report(minted, metadata_files):
    """Generate a detailed mapping report"""
    print("\n" + "=" * 70)
    print("NFT TOKEN MAPPING REPORT")
    print("=" * 70)
    print(f"Contract: {CONTRACT_ADDRESS}")
    print(f"Total minted on-chain: {len(minted)} NFTs (Token IDs 0-{max(minted.keys())})")
    print(f"Total metadata files: {len(metadata_files)}")
    print()

    # Group by token ID status
    mapped = {}      # Has token ID assigned
    unmapped = []    # No token ID

    for filename, info in metadata_files.items():
        if info['token_id'] is not None:
            mapped[info['token_id']] = {'filename': filename, **info}
        else:
            unmapped.append({'filename': filename, **info})

    # Find missing token IDs
    missing_token_ids = []
    for token_id in minted.keys():
        if token_id not in mapped:
            missing_token_ids.append(token_id)

    print("-" * 70)
    print("MAPPED TOKEN IDs (have metadata files with minting data):")
    print("-" * 70)
    for token_id in sorted(mapped.keys()):
        info = mapped[token_id]
        status = "[OK]" if info['has_tx_data'] else "[NO TX]"
        print(f"  Token #{token_id}: {info['filename'][:50]}... {status}")
        print(f"           Type: {info['type']} | Name: {info['name'][:40]}")

    print()
    print("-" * 70)
    print(f"MISSING TOKEN IDs ({len(missing_token_ids)} NFTs minted but no metadata mapping):")
    print("-" * 70)
    for token_id in missing_token_ids:
        tx = minted[token_id]
        print(f"  Token #{token_id}:")
        print(f"    TX: {tx['tx_hash']}")
        print(f"    Minted: {tx['datetime']} UTC")
        print(f"    Block: {tx['block']}")

    print()
    print("-" * 70)
    print(f"UNMAPPED METADATA FILES ({len(unmapped)} files without Token ID):")
    print("-" * 70)

    # Group unmapped by type
    by_type = {'quantum': [], 'molecular': [], 'metatron': [], 'unknown': []}
    for info in unmapped:
        by_type[info['type']].append(info)

    for nft_type, items in by_type.items():
        if items:
            print(f"\n  {nft_type.upper()} ({len(items)} files):")
            for info in items:
                print(f"    - {info['filename'][:55]}")
                print(f"      Name: {info['name'][:50]}")

    print()
    print("=" * 70)
    print("SUGGESTED MAPPING")
    print("=" * 70)
    print("Based on minting order and file types, here are suggested mappings:")
    print()

    # Suggest mappings based on creation time and type
    quantum_unmapped = [f for f in unmapped if f['type'] == 'quantum']

    if missing_token_ids and quantum_unmapped:
        print("Token IDs 0-7 were minted early - likely Quantum Consciousness NFTs:")
        for i, token_id in enumerate(sorted(missing_token_ids)[:8]):
            if i < len(quantum_unmapped):
                suggested = quantum_unmapped[i]
                print(f"  Token #{token_id} -> {suggested['filename']}")
            else:
                print(f"  Token #{token_id} -> [No suitable candidate]")

    return {
        'minted': minted,
        'mapped': mapped,
        'unmapped': unmapped,
        'missing': missing_token_ids
    }

def update_metadata_with_tx(filepath, token_id, tx_data):
    """Update a metadata file with transaction data"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Initialize nft section if needed
    if 'nft' not in data:
        data['nft'] = {}

    # Add minted_tx data
    data['nft']['minted_tx'] = {
        'network': 'POLYGON',
        'tokenId': token_id,
        'tx_hash': tx_data['tx_hash'],
        'block': tx_data['block'],
        'timestamp': tx_data['datetime'],
        'from': tx_data['from'],
        'to': tx_data['to']
    }

    # Add OpenSea URL
    if 'market' not in data['nft']:
        data['nft']['market'] = {}
    data['nft']['market']['opensea'] = {
        'url': f"https://opensea.io/assets/matic/{CONTRACT_ADDRESS}/{token_id}",
        'indexed': False,
        'checked_at': datetime.now().isoformat() + 'Z'
    }

    # Backup original
    backup_path = filepath.with_suffix('.json.bak')
    if not backup_path.exists():
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    # Write updated
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    print(f"  [OK] Updated {filepath.name} with Token #{token_id}")

def interactive_mapping(report):
    """Interactive mode to map token IDs to files"""
    minted = report['minted']
    unmapped = report['unmapped']
    missing = report['missing']

    if not missing:
        print("\nAll token IDs are already mapped!")
        return

    print("\n" + "=" * 70)
    print("INTERACTIVE MAPPING MODE")
    print("=" * 70)
    print("Enter the filename to map to each token ID (or 'skip' to skip):")
    print()

    # Create lookup by filename
    unmapped_lookup = {f['filename']: f for f in unmapped}

    for token_id in sorted(missing):
        tx = minted[token_id]
        print(f"\nToken #{token_id} (minted {tx['datetime']})")
        print(f"  TX: {tx['tx_hash'][:20]}...")
        print()
        print("Available unmapped files:")
        for i, f in enumerate(unmapped):
            print(f"  [{i+1}] {f['filename'][:50]}... ({f['type']})")

        choice = input(f"\nEnter number (1-{len(unmapped)}), filename, or 'skip': ").strip()

        if choice.lower() == 'skip':
            continue

        try:
            # Try as number
            idx = int(choice) - 1
            if 0 <= idx < len(unmapped):
                selected = unmapped[idx]
                update_metadata_with_tx(selected['path'], token_id, tx)
                unmapped.remove(selected)
        except ValueError:
            # Try as filename
            if choice in unmapped_lookup:
                selected = unmapped_lookup[choice]
                update_metadata_with_tx(selected['path'], token_id, tx)
                unmapped.remove(selected)
                del unmapped_lookup[choice]
            else:
                print("  [SKIP] Invalid choice")

def auto_map_quantum_nfts(report):
    """Automatically map quantum NFTs to missing token IDs based on creation order"""
    minted = report['minted']
    unmapped = report['unmapped']
    missing = report['missing']

    # Filter quantum NFTs that are unmapped
    quantum_files = [f for f in unmapped if f['type'] == 'quantum']

    # Sort by filename (which contains timestamp-based IDs)
    quantum_files.sort(key=lambda x: x['filename'])

    print("\n" + "=" * 70)
    print("AUTO-MAPPING QUANTUM NFTs TO MISSING TOKEN IDs")
    print("=" * 70)

    mappings = []
    for i, token_id in enumerate(sorted(missing)):
        if i < len(quantum_files):
            mappings.append({
                'token_id': token_id,
                'file': quantum_files[i],
                'tx': minted[token_id]
            })

    if not mappings:
        print("No suitable mappings found.")
        return

    print("\nProposed mappings:")
    for m in mappings:
        print(f"  Token #{m['token_id']} -> {m['file']['filename']}")

    confirm = input("\nApply these mappings? (yes/no): ").strip().lower()
    if confirm == 'yes':
        for m in mappings:
            update_metadata_with_tx(m['file']['path'], m['token_id'], m['tx'])
        print(f"\n[OK] Applied {len(mappings)} mappings!")
    else:
        print("Cancelled.")

def main():
    print("=" * 70)
    print("NFT Token Mapper")
    print("=" * 70)

    # Load data
    print(f"\nLoading Polygonscan data from: {POLYGONSCAN_CSV}")
    if not POLYGONSCAN_CSV.exists():
        print(f"[ERROR] CSV file not found: {POLYGONSCAN_CSV}")
        return

    minted = load_polygonscan_data(POLYGONSCAN_CSV)
    print(f"  Found {len(minted)} minted tokens")

    print(f"\nScanning metadata files from: {NFT_METADATA_DIR}")
    metadata_files = scan_metadata_files()
    print(f"  Found {len(metadata_files)} metadata files")

    # Generate report
    report = generate_report(minted, metadata_files)

    # Menu
    print("\n" + "=" * 70)
    print("OPTIONS")
    print("=" * 70)
    print("1. Auto-map quantum NFTs to missing token IDs")
    print("2. Interactive mapping mode")
    print("3. Exit (report only)")

    choice = input("\nSelect option (1-3): ").strip()

    if choice == '1':
        auto_map_quantum_nfts(report)
    elif choice == '2':
        interactive_mapping(report)
    else:
        print("\nReport complete. No changes made.")

if __name__ == "__main__":
    main()
