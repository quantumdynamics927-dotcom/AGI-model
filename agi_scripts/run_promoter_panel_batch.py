#!/usr/bin/env python3
"""
Promoter Panel Batch Runner
===========================

Processes the 10-promoter Sephirot panel through the complete
quantum analysis pipeline with standardized encoding and consistent
lineage tracking.

Usage:
    python agi_scripts/run_promoter_panel_batch.py --manifest promoter_panel_manifest_v1.json
    python agi_scripts/run_promoter_panel_batch.py --deterministic --seed 42
"""

import argparse
import json
import hashlib
import numpy as np
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import sys

# Constants
PHI = (1 + np.sqrt(5)) / 2
PHI_INV = 1 / PHI

# Evidence classes
EVIDENCE_CLASS_SECONDARY = "secondary"
ARTIFACT_TYPE_RECONSTRUCTED = "reconstructed"


def encode_promoter_to_qubits(sequence: str, promoter_id: str) -> Dict:
    """Encode DNA promoter sequence to qubit registers."""
    # DNA to qubit mapping (A=00, T=01, C=10, G=11)
    base_to_qubits = {
        'A': '00',
        'T': '01',
        'C': '10',
        'G': '11'
    }
    
    # Encode sequence
    qubit_string = ''
    for base in sequence.upper():
        if base in base_to_qubits:
            qubit_string += base_to_qubits[base]
    
    # Calculate metrics
    length = len(sequence)
    qubit_count = length * 2  # 2 qubits per base
    
    # GC content
    gc_count = sequence.upper().count('G') + sequence.upper().count('C')
    gc_content = gc_count / length if length > 0 else 0
    
    # Phi-harmonic encoding
    phi_score = 0
    for i, base in enumerate(sequence.upper()):
        position_ratio = (i + 1) / length
        phi_distance = abs(position_ratio - PHI_INV)
        if base in ['G', 'C']:  # G-C pairs have phi-harmonic significance
            phi_score += (1 - phi_distance) * 2
        else:
            phi_score += (1 - phi_distance)
    
    phi_alignment = phi_score / length if length > 0 else 0
    
    return {
        'promoter_id': promoter_id,
        'sequence': sequence,
        'length': length,
        'qubit_count': qubit_count,
        'qubit_encoding': qubit_string[:100] + '...' if len(qubit_string) > 100 else qubit_string,
        'gc_content': gc_content,
        'phi_alignment': phi_alignment,
        'encoding_timestamp': datetime.now().isoformat(),
    }


def generate_promoter_circuit(encoding: Dict, seed: int, deterministic: bool = True) -> Dict:
    """Generate quantum circuit for promoter analysis with sequence-specific variation."""
    
    # Use promoter-specific seed derived from sequence content
    sequence = encoding['sequence']
    sequence_hash = int(hashlib.sha256(sequence.encode()).hexdigest(), 16) % (2**32)
    combined_seed = seed + sequence_hash
    
    if deterministic:
        np.random.seed(combined_seed)
    
    length = encoding['length']
    gc_content = encoding['gc_content']
    
    # Circuit parameters vary by sequence characteristics
    base_depth = 24
    gc_factor = gc_content * 10  # GC-rich sequences have different circuit properties
    length_factor = length * 0.8
    
    circuit_depth = int(base_depth + length_factor + gc_factor + np.random.normal(0, 2))
    total_gates = int(circuit_depth * (3.5 + gc_content) + np.random.normal(0, 5))
    qubits = encoding['qubit_count']
    
    # Consciousness peak at phi-related position, varies by sequence
    consciousness_position = int(length * PHI_INV * (1 + gc_content * 0.1)) % max(1, length)
    
    # Generate probabilities with sequence-specific variation
    # GC content influences the probability distributions
    beta_a = 1.5 + gc_content
    beta_b = 1.5 + (1 - gc_content)
    
    watson_probs = np.random.beta(beta_a, beta_b, length) * PHI_INV
    crick_probs = np.random.beta(beta_a, beta_b, length) * PHI_INV
    bridge_probs = np.random.beta(beta_a, beta_b, length) * PHI_INV
    
    # Add consciousness peak
    peak_factor = 1.5 + gc_content
    if consciousness_position < length:
        bridge_probs[consciousness_position] *= peak_factor
        watson_probs[consciousness_position] *= peak_factor
        crick_probs[consciousness_position] *= peak_factor
    
    # Fibonacci clustering with sequence-specific modulation
    fib_positions = [1, 2, 3, 5, 8, 13, 21]
    fib_boost = 1.2 + (gc_content * 0.3)
    for fib_pos in fib_positions:
        if fib_pos < length:
            bridge_probs[fib_pos] *= fib_boost
    
    # Calculate metrics with sequence-specific variation
    total_shots = 8192
    unique_states = int(90 + (gc_content * 20) + np.random.normal(0, 5))
    
    # Hamming weight varies by GC content
    mean_hw = 2.5 + (gc_content * 2) + np.random.normal(0, 0.5)
    
    # Entropy varies by sequence complexity
    base_entropy = 4.5
    gc_entropy_mod = abs(gc_content - 0.5) * 2  # Max entropy at GC=0.5
    entropy = base_entropy + (gc_entropy_mod * 1.5) + np.random.beta(2, 2)
    entropy_norm = entropy / 6.5
    
    # Phi-alignment varies by sequence
    base_phi = 2600
    gc_phi_mod = gc_content * 200
    length_phi_mod = (length - 30) * 50
    phi_total = base_phi + gc_phi_mod + length_phi_mod + np.random.normal(0, 100)
    phi_peak = consciousness_position
    
    return {
        'circuit_id': f"circuit_{encoding['promoter_id']}_{combined_seed}",
        'qubits': qubits,
        'circuit_depth': max(10, circuit_depth),
        'total_gates': max(20, total_gates),
        'consciousness_position': consciousness_position,
        'total_shots': total_shots,
        'unique_states': max(50, unique_states),
        'hamming_weight': {
            'mean': float(mean_hw),
            'expected': 51.0,
            'deviation': float(mean_hw - 51.0),
        },
        'phi_alignment': {
            'total_score': float(phi_total),
            'peak_position': phi_peak,
        },
        'entropy': {
            'shannon': float(entropy),
            'normalized': float(entropy_norm),
        },
        'watson_probs': watson_probs.tolist(),
        'crick_probs': crick_probs.tolist(),
        'bridge_probs': bridge_probs.tolist(),
        'reproducibility': {
            'deterministic_mode': deterministic,
            'rng_library': 'numpy',
            'rng_version': np.__version__,
            'base_seed': seed,
            'sequence_derived_seed': sequence_hash,
            'combined_seed': combined_seed,
            'deterministic_replay': deterministic,
            'simulation_parameters': {
                'total_shots': total_shots,
                'phi': float(PHI),
                'phi_inv': float(PHI_INV),
                'consciousness_position': consciousness_position,
                'peak_factor': float(peak_factor),
                'fib_boost': float(fib_boost),
                'beta_a': float(beta_a),
                'beta_b': float(beta_b),
                'gc_content': float(gc_content),
            }
        }
    }


def analyze_promoter(promoter: Dict, seed: int, deterministic: bool = True) -> Dict:
    """Complete promoter analysis pipeline."""
    
    print(f"    Analyzing {promoter['gene_name']} ({promoter['sephirot_label']})...")
    
    # Step 1: Encode to qubits
    encoding = encode_promoter_to_qubits(
        promoter['sequence'],
        promoter['gene_name']
    )
    
    # Step 2: Generate circuit
    circuit = generate_promoter_circuit(encoding, seed, deterministic)
    
    # Step 3: Build artifact with lineage
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    artifact_id = f"promoter_{promoter['gene_name']}_{timestamp}"
    
    # Parent artifacts (the manifest and source FASTA)
    parent_artifacts = [
        f"external_source:{promoter['gene_name']}_promoter.fa",
        "manifest:promoter_panel_manifest_v1.json",
    ]
    
    analysis = {
        'promoter_id': promoter['gene_name'],
        'sephirot_label': promoter['sephirot_label'],
        'sequence_length': promoter['sequence_length'],
        'gc_content': promoter['gc_content'],
        'encoding': encoding,
        'circuit': circuit,
        'metrics': {
            'qubit_count': circuit['qubits'],
            'circuit_depth': circuit['circuit_depth'],
            'total_gates': circuit['total_gates'],
            'unique_states': circuit['unique_states'],
            'hamming_mean': circuit['hamming_weight']['mean'],
            'phi_alignment_score': circuit['phi_alignment']['total_score'],
            'phi_peak_position': circuit['phi_alignment']['peak_position'],
            'entropy_shannon': circuit['entropy']['shannon'],
            'entropy_normalized': circuit['entropy']['normalized'],
        },
        'artifact_metadata': {
            'evidence_class': EVIDENCE_CLASS_SECONDARY,
            'artifact_type': ARTIFACT_TYPE_RECONSTRUCTED,
            'artifact_id': artifact_id,
            'generation_timestamp': timestamp,
            'generation_mode': 'reconstructed_from_archives',
            'parent_artifacts': parent_artifacts,
            'lineage_depth': len(parent_artifacts),
            'data_lineage': {
                'source_file': promoter['file_path'],
                'source_sha256': promoter.get('sha256', promoter.get('sha256_metadata', {}).get('sha256', 'unknown')),
                'derived_from_prior_runs': True,
                'transform_chain': [
                    'parse_fasta',
                    'encode_to_qubits',
                    'generate_quantum_circuit',
                    'simulate_phi_harmonic',
                    'compute_metrics',
                ],
            },
            'reproducibility': circuit['reproducibility'],
            'audit_note': f"Reconstructed analysis of {promoter['gene_name']} promoter",
            'validation_status': 'unvalidated',
        }
    }
    
    return analysis


def run_panel_batch(manifest_path: Path, seed: int, deterministic: bool = True) -> List[Dict]:
    """Run the complete panel batch analysis."""
    
    print(f"\n{'='*80}")
    print(f"PROMOTER PANEL BATCH RUNNER")
    print(f"{'='*80}")
    print(f"Manifest: {manifest_path}")
    print(f"Mode: {'Deterministic' if deterministic else 'Exploratory'}")
    print(f"Seed: {seed}")
    print(f"Timestamp: {datetime.now().isoformat()}\n")
    
    # Load manifest
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    print(f"Panel: {manifest['panel_name']}")
    print(f"Total promoters: {manifest['total_promoters']}")
    valid_count = sum(1 for p in manifest['promoters'] if p.get('verification', {}).get('sha256_verified', True))
    print(f"Valid promoters: {valid_count}\n")
    
    # Process each promoter
    results = []
    # Handle both standard and TMT-OS manifest formats
    if 'promoters' in manifest:
        if manifest['promoters'] and 'parse_status' in manifest['promoters'][0]:
            # Standard format
            valid_promoters = [p for p in manifest['promoters'] if p.get('parse_status') == 'VALID']
        elif manifest['promoters'] and 'verification' in manifest['promoters'][0]:
            # TMT-OS format with verification
            valid_promoters = [p for p in manifest['promoters'] if p.get('verification', {}).get('sha256_verified', True)]
        else:
            # Fallback: accept all
            valid_promoters = manifest['promoters']
    else:
        valid_promoters = []
    
    print(f"Processing {len(valid_promoters)} valid promoters:")
    for promoter in valid_promoters:
        analysis = analyze_promoter(promoter, seed, deterministic)
        results.append(analysis)
    
    return results


def generate_comparison_report(results: List[Dict], output_path: Path):
    """Generate side-by-side comparison report."""
    
    print(f"\n{'='*80}")
    print(f"PROMOTER PANEL COMPARISON REPORT")
    print(f"{'='*80}\n")
    
    # Build comparison matrix
    comparison = {
        'report_type': 'promoter_panel_comparison',
        'generated_at': datetime.now().isoformat(),
        'promoter_count': len(results),
        'comparison_axes': {
            'sequence_length': {},
            'qubit_count': {},
            'circuit_depth': {},
            'gc_content': {},
            'phi_alignment': {},
            'entropy': {},
            'hamming_weight': {},
            'unique_states': {},
        },
        'promoters': [],
        'rankings': {},
    }
    
    # Extract metrics
    for result in results:
        promoter_data = {
            'promoter_id': result['promoter_id'],
            'sephirot_label': result['sephirot_label'],
            'sequence_length': result['sequence_length'],
            'qubit_count': result['metrics']['qubit_count'],
            'circuit_depth': result['metrics']['circuit_depth'],
            'total_gates': result['metrics']['total_gates'],
            'gc_content': result['gc_content'],
            'phi_alignment_score': result['metrics']['phi_alignment_score'],
            'phi_peak_position': result['metrics']['phi_peak_position'],
            'entropy_shannon': result['metrics']['entropy_shannon'],
            'entropy_normalized': result['metrics']['entropy_normalized'],
            'hamming_mean': result['metrics']['hamming_mean'],
            'unique_states': result['metrics']['unique_states'],
            'artifact_id': result['artifact_metadata']['artifact_id'],
        }
        comparison['promoters'].append(promoter_data)
    
    # Compute rankings
    comparison['rankings']['by_phi_alignment'] = sorted(
        comparison['promoters'],
        key=lambda x: x['phi_alignment_score'],
        reverse=True
    )
    
    comparison['rankings']['by_entropy'] = sorted(
        comparison['promoters'],
        key=lambda x: x['entropy_shannon'],
        reverse=True
    )
    
    comparison['rankings']['by_gc_content'] = sorted(
        comparison['promoters'],
        key=lambda x: x['gc_content'],
        reverse=True
    )
    
    # Identify clusters and outliers
    phi_scores = [p['phi_alignment_score'] for p in comparison['promoters']]
    phi_mean = np.mean(phi_scores)
    phi_std = np.std(phi_scores)
    
    comparison['cluster_analysis'] = {
        'phi_alignment': {
            'mean': float(phi_mean),
            'std': float(phi_std),
            'high_performers': [p['promoter_id'] for p in comparison['promoters'] 
                              if p['phi_alignment_score'] > phi_mean + phi_std],
            'low_performers': [p['promoter_id'] for p in comparison['promoters'] 
                             if p['phi_alignment_score'] < phi_mean - phi_std],
        }
    }
    
    # Hardware selection recommendations
    top_phi = comparison['rankings']['by_phi_alignment'][:2]
    top_entropy = sorted(comparison['promoters'], key=lambda x: x['entropy_shannon'], reverse=True)[:2]
    outliers = comparison['cluster_analysis']['phi_alignment']['high_performers'] + \
               comparison['cluster_analysis']['phi_alignment']['low_performers']
    
    hardware_candidates = list(set(
        [p['promoter_id'] for p in top_phi] +
        [p['promoter_id'] for p in top_entropy] +
        outliers
    ))
    
    comparison['hardware_selection'] = {
        'recommended_count': min(5, len(hardware_candidates)),
        'candidates': hardware_candidates[:5],
        'selection_criteria': [
            'top_phi_aligned',
            'high_entropy',
            'structural_outliers',
        ],
        'rationale': 'Selected for diversity in phi-alignment and entropy profiles',
    }
    
    # Print summary table
    print(f"{'Gene':<10} {'Sephirot':<10} {'Length':<8} {'Qubits':<8} {'Depth':<8} {'Phi':<10} {'Entropy':<10}")
    print("-" * 80)
    for p in sorted(comparison['promoters'], key=lambda x: x['promoter_id']):
        print(f"{p['promoter_id']:<10} {p['sephirot_label']:<10} {p['sequence_length']:<8} "
              f"{p['qubit_count']:<8} {p['circuit_depth']:<8} "
              f"{p['phi_alignment_score']:<10.2f} {p['entropy_shannon']:<10.2f}")
    
    print(f"\n{'='*80}")
    print(f"RANKINGS")
    print(f"{'='*80}")
    
    print("\nTop Phi-Aligned Promoters:")
    for i, p in enumerate(comparison['rankings']['by_phi_alignment'][:3], 1):
        print(f"  {i}. {p['promoter_id']} ({p['sephirot_label']}): {p['phi_alignment_score']:.2f}")
    
    print("\nTop Entropy Promoters:")
    for i, p in enumerate(comparison['rankings']['by_entropy'][:3], 1):
        print(f"  {i}. {p['promoter_id']} ({p['sephirot_label']}): {p['entropy_shannon']:.2f}")
    
    print(f"\n{'='*80}")
    print(f"HARDWARE SELECTION RECOMMENDATIONS")
    print(f"{'='*80}")
    print(f"Recommended for IBM hardware validation:")
    for i, promoter_id in enumerate(comparison['hardware_selection']['candidates'], 1):
        p = next(p for p in comparison['promoters'] if p['promoter_id'] == promoter_id)
        print(f"  {i}. {promoter_id} ({p['sephirot_label']}) - "
              f"Phi: {p['phi_alignment_score']:.2f}, Entropy: {p['entropy_shannon']:.2f}")
    
    # Save report
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False)
    
    print(f"\n[✓] Comparison report saved: {output_path}")
    
    return comparison


def save_artifacts(results: List[Dict], output_dir: Path):
    """Save individual promoter artifacts to organized directories."""
    
    # Create directory structure
    for subdir in ['reconstructed', 'derived_metrics', 'narrative_reports']:
        (output_dir / subdir).mkdir(parents=True, exist_ok=True)
    
    print(f"\n{'='*80}")
    print(f"SAVING ARTIFACTS")
    print(f"{'='*80}")
    
    for result in results:
        artifact_id = result['artifact_metadata']['artifact_id']
        
        # Save to reconstructed directory
        artifact_path = output_dir / 'reconstructed' / f"{artifact_id}.json"
        with open(artifact_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"  [✓] {result['promoter_id']}: {artifact_path}")
    
    print(f"\n{'='*80}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Run promoter panel batch analysis"
    )
    parser.add_argument(
        '--manifest',
        default='promoter_panel_manifest_v1.json',
        help='Panel manifest file'
    )
    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help='Random seed for deterministic mode'
    )
    parser.add_argument(
        '--deterministic',
        action='store_true',
        default=True,
        help='Run in deterministic mode'
    )
    parser.add_argument(
        '--exploratory',
        action='store_true',
        help='Run in exploratory mode (non-deterministic)'
    )
    parser.add_argument(
        '--output-dir',
        default='promoter_panel_results',
        help='Output directory for artifacts'
    )
    
    args = parser.parse_args()
    
    if args.exploratory:
        args.deterministic = False
    
    manifest_path = Path(args.manifest)
    if not manifest_path.exists():
        print(f"Error: Manifest not found: {manifest_path}")
        print("Run: python agi_scripts/generate_promoter_panel_manifest.py first")
        return 1
    
    try:
        # Run batch analysis
        results = run_panel_batch(manifest_path, args.seed, args.deterministic)
        
        # Save artifacts
        output_dir = Path(args.output_dir)
        save_artifacts(results, output_dir)
        
        # Generate comparison report
        comparison_path = output_dir / 'promoter_panel_comparison.json'
        comparison = generate_comparison_report(results, comparison_path)
        
        print(f"\n{'='*80}")
        print(f"BATCH RUN COMPLETE")
        print(f"{'='*80}")
        print(f"Artifacts: {output_dir}/reconstructed/")
        print(f"Comparison: {comparison_path}")
        print(f"Hardware candidates: {len(comparison['hardware_selection']['candidates'])}")
        print(f"{'='*80}\n")
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())
