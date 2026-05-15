"""
Analyze Parity Witness Results

Statistical analysis of parity witness experiment results.

Usage:
    python analyze_pw_results.py --input results/pw_baseline_*.json
"""

import argparse
import json
from pathlib import Path
from typing import Dict, Optional

import numpy as np
from scipy import stats


def load_results(filepath: Path) -> dict:
    """Load experiment results from JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)


def kl_divergence(p: np.ndarray, q: np.ndarray, epsilon: float = 1e-10) -> float:
    """Compute KL divergence D_KL(p || q)."""
    p = np.clip(p, epsilon, 1.0)
    q = np.clip(q, epsilon, 1.0)
    return float(np.sum(p * np.log(p / q)))


def chi_square_test(observed: np.ndarray, expected: np.ndarray) -> tuple:
    """Perform chi-square test comparing observed to expected distribution."""
    total_obs = np.sum(observed)
    observed_counts = observed * total_obs
    expected_counts = expected * total_obs
    expected_counts = np.clip(expected_counts, 1e-10, None)
    
    chi2, p = stats.chisquare(observed_counts, expected_counts)
    return chi2, p


def compute_witness_score(
    parity_kl: float,
    joint_kl: float,
    correlation_drift: float,
    weights: Optional[Dict[str, float]] = None
) -> float:
    """Compute composite witness score."""
    if weights is None:
        weights = {
            'parity_kl': 0.4,
            'joint_kl': 0.3,
            'correlation_drift': 0.3
        }
    
    return (
        weights['parity_kl'] * parity_kl +
        weights['joint_kl'] * joint_kl +
        weights['correlation_drift'] * abs(correlation_drift)
    )


def analyze_experiment(results: dict) -> dict:
    """
    Perform complete analysis of parity witness experiment results.
    
    Args:
        results: Loaded experiment results
        
    Returns:
        Analysis dictionary with all metrics and tests
    """
    analysis = {
        'experiment_info': {
            'timestamp': results['timestamp'],
            'shots': results['shots'],
            'backend': results['backend'],
            'seed': results['seed'],
            'variant': results['variant']
        },
        'modes': {},
        'comparisons': {},
        'detection_analysis': {}
    }
    
    # Extract baseline distributions
    baseline_parity = np.array(results['modes']['none']['parity_distribution'])
    
    # Analyze each interception mode
    for mode_name, mode_data in results['modes'].items():
        if mode_name == 'none':
            continue
        
        mode_parity = np.array(mode_data['parity_distribution'])
        
        # Compute parity metrics
        parity_kl = mode_data.get('parity_kl_from_baseline', kl_divergence(mode_parity, baseline_parity))
        
        # Compute joint metrics if available
        joint_kl = 0.0
        correlation_drift = 0.0
        
        if 'joint_distribution' in mode_data:
            # For baseline, we need joint distribution
            # Since baseline only measures ancilla, we use a uniform prior
            # This is a limitation - ideally baseline should also measure all qubits
            baseline_joint = np.array([0.25, 0.25, 0.25, 0.25])  # Uniform prior
            mode_joint = np.array(mode_data['joint_distribution'])
            joint_kl = kl_divergence(mode_joint, baseline_joint)
            
            # Correlation drift
            mode_mi = mode_data.get('mutual_information', 0)
            # Baseline MI would be 0 for independent qubits (uniform prior)
            correlation_drift = -mode_mi  # Negative because interception reduces correlation
        
        # Statistical tests
        chi2, chi2_p = chi_square_test(mode_parity, baseline_parity)
        
        # Witness score
        witness_score = compute_witness_score(parity_kl, joint_kl, correlation_drift)
        
        analysis['modes'][mode_name] = {
            'parity_kl': parity_kl,
            'joint_kl': joint_kl,
            'correlation_drift': correlation_drift,
            'chi_square': {
                'statistic': chi2,
                'p_value': chi2_p,
                'significant': chi2_p < 0.01
            },
            'witness_score': witness_score,
            'detected': witness_score > 0.1 or parity_kl > 0.05
        }
    
    # Compare D0 vs D1 interception
    if 'd0' in analysis['modes'] and 'd1' in analysis['modes']:
        d0_score = analysis['modes']['d0']['witness_score']
        d1_score = analysis['modes']['d1']['witness_score']
        
        analysis['comparisons']['d0_vs_d1'] = {
            'd0_witness_score': d0_score,
            'd1_witness_score': d1_score,
            'difference': abs(d0_score - d1_score),
            'symmetric': abs(d0_score - d1_score) < 0.05
        }
    
    # Overall detection analysis
    detected_modes = [
        mode for mode, data in analysis['modes'].items()
        if data['detected']
    ]
    
    analysis['detection_analysis'] = {
        'modes_detected': detected_modes,
        'detection_rate': len(detected_modes) / max(len(analysis['modes']), 1),
        'best_detection': max(
            analysis['modes'].items(),
            key=lambda x: x[1]['witness_score'],
            default=(None, {'witness_score': 0})
        )[0]
    }
    
    return analysis


def generate_report(analysis: dict) -> str:
    """Generate human-readable report from analysis."""
    lines = [
        "# Parity Witness Analysis Report",
        "",
        "## Experiment Info",
        f"- Timestamp: {analysis['experiment_info']['timestamp']}",
        f"- Shots: {analysis['experiment_info']['shots']}",
        f"- Backend: {analysis['experiment_info']['backend']}",
        f"- Variant: {analysis['experiment_info']['variant']}",
        "",
        "## Mode Analysis",
        ""
    ]
    
    for mode_name, mode_data in analysis['modes'].items():
        lines.extend([
            f"### {mode_name.upper()} Interception",
            f"- Parity KL Divergence: {mode_data['parity_kl']:.4f}",
            f"- Joint KL Divergence: {mode_data['joint_kl']:.4f}",
            f"- Correlation Drift: {mode_data['correlation_drift']:.4f}",
            f"- Witness Score: {mode_data['witness_score']:.4f}",
            f"- Chi-square p-value: {mode_data['chi_square']['p_value']:.4f}",
            f"- Significant (p<0.01): {'Yes' if mode_data['chi_square']['significant'] else 'No'}",
            f"- **Detected**: {'Yes' if mode_data['detected'] else 'No'}",
            ""
        ])
    
    if 'd0_vs_d1' in analysis.get('comparisons', {}):
        comp = analysis['comparisons']['d0_vs_d1']
        lines.extend([
            "## D0 vs D1 Comparison",
            f"- D0 Witness Score: {comp['d0_witness_score']:.4f}",
            f"- D1 Witness Score: {comp['d1_witness_score']:.4f}",
            f"- Difference: {comp['difference']:.4f}",
            f"- Symmetric: {'Yes' if comp['symmetric'] else 'No'}",
            ""
        ])
    
    det = analysis['detection_analysis']
    lines.extend([
        "## Detection Summary",
        f"- Modes Detected: {', '.join(det['modes_detected']) or 'None'}",
        f"- Detection Rate: {det['detection_rate']:.1%}",
        f"- Best Detection: {det['best_detection'] or 'N/A'}",
        ""
    ])
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description='Analyze parity witness results')
    parser.add_argument('--input', type=str, required=True, help='Input JSON file')
    parser.add_argument('--output', type=str, default=None, help='Output report file')
    
    args = parser.parse_args()
    
    # Load results
    results = load_results(Path(args.input))
    
    # Analyze
    analysis = analyze_experiment(results)
    
    # Generate report
    report = generate_report(analysis)
    
    # Output
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(report)
        print(f"Report saved to: {output_path}")
    else:
        print(report)
    
    # Also save analysis as JSON
    analysis_path = Path(args.input).with_suffix('.analysis.json')
    with open(analysis_path, 'w') as f:
        json.dump(analysis, f, indent=2, default=str)
    print(f"Analysis saved to: {analysis_path}")


if __name__ == '__main__':
    main()