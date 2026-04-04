#!/usr/bin/env python3
"""
Promoter Panel Manifest Generator
=================================

Generates a versioned manifest for the 10-promoter Sephirot panel.
Validates FASTA formatting, computes SHA256 hashes, and creates
the canonical panel definition for downstream analysis.

Usage:
    python agi_scripts/generate_promoter_panel_manifest.py
    python agi_scripts/generate_promoter_panel_manifest.py --panel-dir C:\FASTA --output panel_manifest_v1.json
"""

import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re


# Sephirot mapping for the 10-promoter panel
SEPHIROT_PANEL = {
    "ACTB": "Malkuth",
    "BDNF": "Tiferet",
    "DCTN1": "Binah",
    "FOS": "Netzach",
    "FOXG1": "Kether",
    "JUN": "Hod",
    "NCAM1": "Chokmah",
    "OXT": "Chesed",
    "SRY": "Yesod",
    "TP53": "Gevurah",
}

# Valid DNA bases
VALID_BASES = set('ATCG')


def parse_fasta_header(header: str) -> Dict[str, str]:
    """Parse FASTA header for genomic coordinates."""
    # Pattern: >chromosome:GRCh38:chr:start:end:strand
    pattern = r'>chromosome:(\w+):(\d+|\w+):(\d+):(\d+):([+-]?\d+)'
    match = re.match(pattern, header)
    
    if match:
        return {
            'assembly': match.group(1),
            'chromosome': match.group(2),
            'start': int(match.group(3)),
            'end': int(match.group(4)),
            'strand': int(match.group(5)),
            'raw_header': header,
        }
    else:
        return {
            'assembly': None,
            'chromosome': None,
            'start': None,
            'end': None,
            'strand': None,
            'raw_header': header,
        }


def validate_sequence(sequence: str) -> Tuple[bool, List[str]]:
    """Validate DNA sequence for ambiguous bases."""
    errors = []
    
    # Check for empty sequence
    if not sequence:
        errors.append("Empty sequence")
        return False, errors
    
    # Check for ambiguous bases
    ambiguous_bases = set()
    for i, base in enumerate(sequence.upper()):
        if base not in VALID_BASES:
            ambiguous_bases.add((i, base))
    
    if ambiguous_bases:
        errors.append(f"Ambiguous bases found: {ambiguous_bases}")
    
    # Check length
    if len(sequence) < 10:
        errors.append(f"Sequence too short: {len(sequence)} bp")
    
    return len(errors) == 0, errors


def compute_sha256(filepath: Path) -> str:
    """Compute SHA256 hash of file contents."""
    sha256_hash = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


def parse_promoter_fasta(filepath: Path) -> Optional[Dict]:
    """Parse a promoter FASTA file with full validation."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if not lines:
            return None
        
        # Parse header
        header_line = lines[0].strip()
        if not header_line.startswith('>'):
            return {
                'file_path': str(filepath),
                'gene_name': filepath.stem.split('_')[0],
                'sephirot_label': SEPHIROT_PANEL.get(filepath.stem.split('_')[0], 'Unknown'),
                'parse_status': 'FAILED',
                'parse_errors': ['Missing FASTA header'],
            }
        
        header_info = parse_fasta_header(header_line)
        
        # Parse sequence
        sequence_lines = [line.strip() for line in lines[1:] if line.strip()]
        sequence = ''.join(sequence_lines)
        
        # Validate sequence
        is_valid, errors = validate_sequence(sequence)
        
        # Extract gene name from filename
        gene_name = filepath.stem.split('_')[0]
        sephirot_label = SEPHIROT_PANEL.get(gene_name, 'Unknown')
        
        # Compute file hash
        file_hash = compute_sha256(filepath)
        
        return {
            'file_path': str(filepath),
            'gene_name': gene_name,
            'sephirot_label': sephirot_label,
            'sequence_length': len(sequence),
            'sequence': sequence,
            'sha256': file_hash,
            'promoter_header': header_info,
            'parse_status': 'VALID' if is_valid else 'FAILED',
            'parse_errors': errors if errors else [],
            'gc_content': (sequence.upper().count('G') + sequence.upper().count('C')) / len(sequence) if sequence else 0,
        }
        
    except Exception as e:
        return {
            'file_path': str(filepath),
            'gene_name': filepath.stem.split('_')[0],
            'sephirot_label': SEPHIROT_PANEL.get(filepath.stem.split('_')[0], 'Unknown'),
            'parse_status': 'FAILED',
            'parse_errors': [str(e)],
        }


def generate_panel_manifest(panel_dir: Path, version: str = "v1.0") -> Dict:
    """Generate the complete panel manifest."""
    
    print(f"\n{'='*80}")
    print(f"PROMOTER PANEL MANIFEST GENERATOR")
    print(f"{'='*80}")
    print(f"Panel Directory: {panel_dir}")
    print(f"Version: {version}")
    print(f"Timestamp: {datetime.now().isoformat()}\n")
    
    # Find all FASTA files
    fasta_files = sorted(panel_dir.glob("*_promoter.fa"))
    
    if not fasta_files:
        raise ValueError(f"No FASTA files found in {panel_dir}")
    
    print(f"Found {len(fasta_files)} FASTA files")
    
    # Parse each file
    panel_entries = []
    valid_count = 0
    failed_count = 0
    
    for fasta_file in fasta_files:
        print(f"  Processing: {fasta_file.name}...", end=' ')
        entry = parse_promoter_fasta(fasta_file)
        panel_entries.append(entry)
        
        if entry['parse_status'] == 'VALID':
            valid_count += 1
            print(f"✓ ({entry['sequence_length']} bp, {entry['sephirot_label']})")
        else:
            failed_count += 1
            print(f"✗ ({', '.join(entry['parse_errors'])})")
    
    # Build manifest
    manifest = {
        'manifest_version': version,
        'generated_at': datetime.now().isoformat(),
        'panel_name': 'Sephirot_10_Promoter_Panel',
        'panel_description': 'Curated experimental cohort of 10 gene promoters mapped to Sephirot',
        'panel_directory': str(panel_dir),
        'total_promoters': len(panel_entries),
        'valid_promoters': valid_count,
        'failed_promoters': failed_count,
        'sephirot_mapping': SEPHIROT_PANEL,
        'validation_criteria': {
            'min_length': 10,
            'valid_bases': list(VALID_BASES),
            'required_header_format': '>chromosome:assembly:chr:start:end:strand',
        },
        'promoters': panel_entries,
        'audit_metadata': {
            'schema_version': '1.0',
            'evidence_class': 'primary',
            'artifact_type': 'raw_hardware',
            'validation_status': 'validated' if failed_count == 0 else 'partial',
        }
    }
    
    print(f"\n{'='*80}")
    print(f"MANIFEST SUMMARY")
    print(f"{'='*80}")
    print(f"Total: {len(panel_entries)}")
    print(f"Valid: {valid_count}")
    print(f"Failed: {failed_count}")
    print(f"{'='*80}\n")
    
    return manifest


def main():
    parser = argparse.ArgumentParser(
        description="Generate promoter panel manifest"
    )
    parser.add_argument(
        '--panel-dir',
        default='C:\\FASTA',
        help='Directory containing promoter FASTA files'
    )
    parser.add_argument(
        '--output',
        default='promoter_panel_manifest_v1.json',
        help='Output manifest file'
    )
    parser.add_argument(
        '--version',
        default='v1.0',
        help='Manifest version'
    )
    
    args = parser.parse_args()
    
    panel_dir = Path(args.panel_dir)
    if not panel_dir.exists():
        print(f"Error: Directory not found: {panel_dir}")
        return 1
    
    try:
        manifest = generate_panel_manifest(panel_dir, args.version)
        
        # Save manifest
        output_path = Path(args.output)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        print(f"[✓] Manifest saved: {output_path}")
        print(f"    Valid promoters: {manifest['valid_promoters']}/{manifest['total_promoters']}")
        
        return 0 if manifest['failed_promoters'] == 0 else 1
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
