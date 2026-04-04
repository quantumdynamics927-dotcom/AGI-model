#!/usr/bin/env python3
"""
IBM Quantum Results Analyzer
============================

Analyzes raw hardware results from IBM Quantum and compares
with reconstructed predictions.

Usage:
    python agi_scripts/analyze_ibm_results.py --results-dir raw_hardware/
    python agi_scripts/analyze_ibm_results.py --compare-with tmt_os_panel_results/promoter_panel_comparison.json
"""

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import numpy as np


def load_ibm_results(results_dir: Path) -> List[Dict]:
    """Load IBM Quantum hardware results."""
    
    results = []
    
    # Find all result files
    for result_file in results_dir.glob("promoter_*.json"):
        if 'manifest' in result_file.name:
            continue
        
        with open(result_file, 'r') as f:
            data = json.load(f)
            results.append(data)
    
    return results


def analyze_hardware_vs_reconstructed(
    hardware_results: List[Dict],
    comparison_report: Path
) -> Dict:
    """Compare hardware results with reconstructed predictions."""
    
    # Load comparison report
    with open(comparison_report, 'r') as f:
        comparison = json.load(f)
    
    analysis = {
        'analysis_type': 'hardware_vs_reconstructed',
        'generated_at': datetime.now().isoformat(),
        'hardware_jobs': len(hardware_results),
        'comparisons': [],
        'validation_summary': {
            'total': 0,
            'validated': 0,
            'failed': 0,
        }
    }
    
    for hw_result in hardware_results:
        promoter_id = hw_result.get('promoter_id', 'unknown')
        
        # Find corresponding reconstructed data
        recon_data = next(
            (p for p in comparison['promoters'] if p['promoter_id'] == promoter_id),
            None
        )
        
        if not recon_data:
            continue
        
        # Compare metrics
        comparison_entry = {
            'promoter_id': promoter_id,
            'sephirot_label': recon_data['sephirot_label'],
            'hardware': {
                'job_id': hw_result.get('job_id'),
                'backend': hw_result.get('backend'),
                'shots': hw_result.get('shots'),
                'unique_states_measured': len(hw_result.get('counts', {})),
            },
            'reconstructed': {
                'unique_states_predicted': recon_data['unique_states'],
                'phi_alignment_score': recon_data['phi_alignment_score'],
                'entropy_shannon': recon_data['entropy_shannon'],
            },
            'validation': {
                'unique_states_match': None,  # To be computed
                'phi_alignment_correlation': None,
            }
        }
        
        analysis['comparisons'].append(comparison_entry)
        analysis['validation_summary']['total'] += 1
    
    return analysis


def generate_validation_report(analysis: Dict, output_path: Path):
    """Generate validation report comparing hardware vs reconstructed."""
    
    print(f"\n{'='*80}")
    print(f"HARDWARE VS RECONSTRUCTED VALIDATION REPORT")
    print(f"{'='*80}\n")
    
    print(f"Total Comparisons: {analysis['validation_summary']['total']}")
    print(f"Timestamp: {analysis['generated_at']}\n")
    
    print(f"{'Promoter':<10} {'Sephirot':<10} {'Hardware':<15} {'Reconstructed':<15} {'Status':<10}")
    print("-" * 80)
    
    for comp in analysis['comparisons']:
        promoter_id = comp['promoter_id']
        sephirot = comp['sephirot_label']
        hw_states = comp['hardware']['unique_states_measured']
        recon_states = comp['reconstructed']['unique_states_predicted']
        
        # Simple validation: within 20% is "match"
        if recon_states > 0:
            deviation = abs(hw_states - recon_states) / recon_states
            status = "✓ MATCH" if deviation < 0.2 else "⚠ DEVIATION"
        else:
            status = "? UNKNOWN"
        
        print(f"{promoter_id:<10} {sephirot:<10} {hw_states:<15} {recon_states:<15} {status:<10}")
    
    print(f"\n{'='*80}")
    print(f"VALIDATION SUMMARY")
    print(f"{'='*80}")
    
    matches = sum(1 for c in analysis['comparisons'] 
                if c['hardware']['unique_states_measured'] > 0)
    print(f"Successful hardware runs: {matches}/{len(analysis['comparisons'])}")
    
    # Save report
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    
    print(f"\n[✓] Validation report saved: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze IBM Quantum hardware results"
    )
    parser.add_argument(
        '--results-dir',
        default='raw_hardware',
        help='Directory containing IBM Quantum results'
    )
    parser.add_argument(
        '--compare-with',
        default='tmt_os_panel_results/promoter_panel_comparison.json',
        help='Comparison report for validation'
    )
    parser.add_argument(
        '--output',
        default='hardware_validation_report.json',
        help='Output validation report'
    )
    
    args = parser.parse_args()
    
    results_dir = Path(args.results_dir)
    if not results_dir.exists():
        print(f"Error: Results directory not found: {results_dir}")
        return 1
    
    # Load hardware results
    print(f"Loading IBM Quantum results from: {results_dir}")
    hardware_results = load_ibm_results(results_dir)
    
    if not hardware_results:
        print("No hardware results found")
        return 1
    
    print(f"Found {len(hardware_results)} hardware results")
    
    # Compare with reconstructed
    comparison_report = Path(args.compare_with)
    if comparison_report.exists():
        analysis = analyze_hardware_vs_reconstructed(
            hardware_results,
            comparison_report
        )
        
        # Generate report
        output_path = Path(args.output)
        generate_validation_report(analysis, output_path)
        
        return 0
    else:
        print(f"Warning: Comparison report not found: {comparison_report}")
        print("Hardware results loaded but no comparison performed")
        return 0


if __name__ == '__main__':
    exit(main())
