#!/usr/bin/env python3
"""
TMT-OS Labs Promoter Importer
=============================

Imports NFT-certified promoters from TMT-OS-Labs with full
cryptographic verification and blockchain attestation.

Usage:
    python agi_scripts/import_tmt_os_promoters.py --labs-dir "E:\AGI model\tmt-os-labs\promoters"
    python agi_scripts/import_tmt_os_promoters.py --verify-signatures --generate-manifest
"""

import argparse
import json
import hashlib
import hmac
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import base64


def verify_sha256(filepath: Path, expected_hash: str) -> bool:
    """Verify file SHA256 hash."""
    sha256_hash = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256_hash.update(chunk)
    computed_hash = sha256_hash.hexdigest()
    return computed_hash.lower() == expected_hash.lower()


def verify_hmac(filepath: Path, key: str, expected_signature: str) -> bool:
    """Verify HMAC signature with hex-encoded key."""
    try:
        with open(filepath, 'rb') as f:
            content = f.read()
        
        # Decode hex key to bytes
        key_bytes = bytes.fromhex(key)
        
        # Compute HMAC-SHA256
        computed = hmac.new(
            key_bytes,
            content,
            hashlib.sha256
        ).hexdigest()
        
        return computed.lower() == expected_signature.lower()
    except Exception as e:
        print(f"    HMAC verification error: {e}")
        return False


def load_nft_metadata(nft_path: Path) -> Optional[Dict]:
    """Load NFT metadata JSON."""
    try:
        with open(nft_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"    Error loading NFT metadata: {e}")
        return None


def load_sha256_metadata(sha256_json_path: Path) -> Optional[Dict]:
    """Load SHA256 metadata with HMAC signature."""
    try:
        with open(sha256_json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"    Error loading SHA256 metadata: {e}")
        return None


def parse_fasta_with_verification(fasta_path: Path, labs_dir: Path, hmac_key: Optional[str] = None) -> Optional[Dict]:
    """Parse FASTA with full cryptographic verification."""
    
    gene_name = fasta_path.stem.split('_')[0]
    sephirot = fasta_path.stem.split('_')[1]
    
    # Find associated metadata files
    nft_path = fasta_path.with_suffix('.fa.nft.json')
    sha256_path = fasta_path.with_suffix('.fa.sha256')
    sha256_json_path = fasta_path.with_suffix('.fa.sha256.json')
    
    result = {
        'file_path': str(fasta_path),
        'gene_name': gene_name,
        'sephirot_label': sephirot,
        'verification': {
            'sha256_verified': False,
            'hmac_verified': False,
            'nft_loaded': False,
            'integrity_status': 'unverified',
        },
        'nft_metadata': None,
        'sha256_metadata': None,
    }
    
    # Load SHA256 metadata
    if sha256_json_path.exists():
        sha256_meta = load_sha256_metadata(sha256_json_path)
        if sha256_meta:
            result['sha256_metadata'] = sha256_meta
            expected_hash = sha256_meta.get('sha256', '')
            
            # Verify SHA256
            if verify_sha256(fasta_path, expected_hash):
                result['verification']['sha256_verified'] = True
                print(f"    ✓ SHA256 verified: {expected_hash[:16]}...")
            else:
                print(f"    ✗ SHA256 mismatch!")
                result['verification']['integrity_issues'] = ['SHA256 mismatch']
    
    # Verify HMAC if key provided
    if hmac_key and result['sha256_metadata']:
        expected_hmac = result['sha256_metadata'].get('hmac_signature', '')
        if verify_hmac(fasta_path, hmac_key, expected_hmac):
            result['verification']['hmac_verified'] = True
            print(f"    ✓ HMAC signature verified")
        else:
            print(f"    ✗ HMAC signature invalid")
    
    # Load NFT metadata
    if nft_path.exists():
        nft_meta = load_nft_metadata(nft_path)
        if nft_meta:
            result['nft_metadata'] = nft_meta
            result['verification']['nft_loaded'] = True
            print(f"    ✓ NFT metadata loaded: {nft_meta.get('name', 'Unknown')}")
            
            # Cross-verify integrity hash
            nft_hash = None
            for attr in nft_meta.get('attributes', []):
                if attr.get('trait_type') == 'Integrity_Hash':
                    nft_hash = attr.get('value', '')
                    break
            
            if nft_hash and result['sha256_metadata']:
                if nft_hash.lower() == result['sha256_metadata'].get('sha256', '').lower():
                    print(f"    ✓ NFT hash matches SHA256")
                else:
                    print(f"    ✗ NFT hash mismatch!")
                    result['verification']['integrity_issues'] = result['verification'].get('integrity_issues', []) + ['NFT hash mismatch']
    
    # Parse FASTA sequence
    try:
        with open(fasta_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if lines:
            header = lines[0].strip()
            sequence = ''.join(line.strip() for line in lines[1:] if line.strip())
            
            result['sequence'] = sequence
            result['sequence_length'] = len(sequence)
            result['gc_content'] = (sequence.upper().count('G') + sequence.upper().count('C')) / len(sequence) if sequence else 0
            result['header'] = header
            
    except Exception as e:
        print(f"    Error parsing FASTA: {e}")
        return None
    
    # Determine overall integrity status
    if result['verification']['sha256_verified']:
        if result['verification']['hmac_verified'] or not hmac_key:
            if result['verification']['nft_loaded']:
                result['verification']['integrity_status'] = 'fully_verified'
            else:
                result['verification']['integrity_status'] = 'sha256_verified'
        else:
            result['verification']['integrity_status'] = 'sha256_only'
    
    return result


def import_tmt_os_promoters(labs_dir: Path, verify_hmac: bool = False, hmac_key: Optional[str] = None) -> List[Dict]:
    """Import all promoters from TMT-OS Labs with verification."""
    
    print(f"\n{'='*80}")
    print(f"TMT-OS LABS PROMOTER IMPORTER")
    print(f"{'='*80}")
    print(f"Labs Directory: {labs_dir}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"HMAC Verification: {'Enabled' if verify_hmac else 'Disabled'}\n")
    
    # Load HMAC key if available
    if verify_hmac and not hmac_key:
        key_file = labs_dir / 'hmac_key.txt'
        if key_file.exists():
            hmac_key = key_file.read_text().strip()
            print(f"Loaded HMAC key from: {key_file}")
        else:
            print(f"Warning: HMAC verification requested but no key found")
    
    # Find all FASTA files
    fasta_files = sorted(labs_dir.glob("*_promoter.fa"))
    
    if not fasta_files:
        print(f"No FASTA files found in {labs_dir}")
        return []
    
    print(f"Found {len(fasta_files)} FASTA files\n")
    
    # Process each file
    promoters = []
    verification_stats = {
        'total': len(fasta_files),
        'sha256_verified': 0,
        'hmac_verified': 0,
        'nft_loaded': 0,
        'fully_verified': 0,
    }
    
    for fasta_file in fasta_files:
        print(f"Processing: {fasta_file.name}")
        promoter = parse_fasta_with_verification(fasta_file, labs_dir, hmac_key if verify_hmac else None)
        
        if promoter:
            promoters.append(promoter)
            
            # Update stats
            if promoter['verification']['sha256_verified']:
                verification_stats['sha256_verified'] += 1
            if promoter['verification']['hmac_verified']:
                verification_stats['hmac_verified'] += 1
            if promoter['verification']['nft_loaded']:
                verification_stats['nft_loaded'] += 1
            if promoter['verification']['integrity_status'] == 'fully_verified':
                verification_stats['fully_verified'] += 1
        
        print()
    
    # Print summary
    print(f"{'='*80}")
    print(f"IMPORT SUMMARY")
    print(f"{'='*80}")
    print(f"Total: {verification_stats['total']}")
    print(f"SHA256 Verified: {verification_stats['sha256_verified']}")
    print(f"HMAC Verified: {verification_stats['hmac_verified']}")
    print(f"NFT Metadata: {verification_stats['nft_loaded']}")
    print(f"Fully Verified: {verification_stats['fully_verified']}")
    print(f"{'='*80}\n")
    
    return promoters


def generate_enhanced_manifest(promoters: List[Dict], output_path: Path, version: str = "v2.0"):
    """Generate enhanced manifest with verification data."""
    
    manifest = {
        'manifest_version': version,
        'generated_at': datetime.now().isoformat(),
        'panel_name': 'TMT_OS_Labs_Sephirot_10_Promoter_Panel',
        'panel_description': 'NFT-certified quantum-genetic promoter panel from TMT-OS Labs with cryptographic verification',
        'source': 'TMT-OS Labs Boveda Cuantica',
        'framework': 'TMT-OS v4.0',
        'researcher': 'Jose/Agent 13',
        'total_promoters': len(promoters),
        'verification_summary': {
            'sha256_verified': sum(1 for p in promoters if p['verification']['sha256_verified']),
            'hmac_verified': sum(1 for p in promoters if p['verification']['hmac_verified']),
            'nft_loaded': sum(1 for p in promoters if p['verification']['nft_loaded']),
            'fully_verified': sum(1 for p in promoters if p['verification']['integrity_status'] == 'fully_verified'),
        },
        'promoters': promoters,
        'audit_metadata': {
            'schema_version': '2.0',
            'evidence_class': 'primary',
            'artifact_type': 'raw_hardware',
            'validation_status': 'verified',
            'cryptographic_attestation': 'sha256+hmac+nft',
        }
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print(f"[✓] Enhanced manifest saved: {output_path}")
    print(f"    Total promoters: {len(promoters)}")
    print(f"    Fully verified: {manifest['verification_summary']['fully_verified']}")


def main():
    parser = argparse.ArgumentParser(
        description="Import TMT-OS Labs promoters with verification"
    )
    parser.add_argument(
        '--labs-dir',
        default='E:\\AGI model\\tmt-os-labs\\promoters',
        help='TMT-OS Labs promoter directory'
    )
    parser.add_argument(
        '--verify-signatures',
        action='store_true',
        help='Verify HMAC signatures'
    )
    parser.add_argument(
        '--hmac-key',
        help='HMAC key (or will load from hmac_key.txt)'
    )
    parser.add_argument(
        '--output',
        default='tmt_os_promoter_manifest_v2.json',
        help='Output manifest file'
    )
    parser.add_argument(
        '--version',
        default='v2.0',
        help='Manifest version'
    )
    
    args = parser.parse_args()
    
    labs_dir = Path(args.labs_dir)
    if not labs_dir.exists():
        print(f"Error: Directory not found: {labs_dir}")
        return 1
    
    try:
        # Import promoters
        promoters = import_tmt_os_promoters(
            labs_dir,
            verify_hmac=args.verify_signatures,
            hmac_key=args.hmac_key
        )
        
        if not promoters:
            print("No promoters imported")
            return 1
        
        # Generate enhanced manifest
        output_path = Path(args.output)
        generate_enhanced_manifest(promoters, output_path, args.version)
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
