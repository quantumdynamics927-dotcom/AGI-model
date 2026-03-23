#!/usr/bin/env python3
"""
Phi-Convergence Analysis for Quantum VAE Latent Space

This script performs comprehensive statistical analysis of phi-convergence 
in the Quantum VAE latent space, including significance testing and 
validation against baseline models.

Features:
- Statistical significance testing for phi-convergence
- Comparison with baseline models
- Bootstrap resampling for confidence intervals
- Visualization of convergence patterns
"""

import torch
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from pathlib import Path
import argparse
import sys
from vae_model import QuantumVAE
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

# Golden ratio constant
PHI = 1.618033988749895

def generate_quantum_states(num_samples: int, dim: int = 128) -> np.ndarray:
    """
    Generate synthetic quantum state samples for analysis.
    
    Parameters
    ----------
    num_samples : int
        Number of samples to generate
    dim : int
        Dimension of each sample
        
    Returns
    -------
    np.ndarray
        Generated quantum state samples
    """
    data = []
    for _ in range(num_samples):
        # Generate complex quantum state
        real = np.random.randn(dim // 2)
        imag = np.random.randn(dim // 2)
        state = real + 1j * imag
        state = state / np.linalg.norm(state)
        sample = np.concatenate([state.real, state.imag])
        data.append(sample)
    return np.array(data, dtype=np.float32)

def analyze_phi_convergence(latent_codes: np.ndarray, 
                           significance_level: float = 0.05,
                           bootstrap_samples: int = 1000) -> dict:
    """
    Analyze phi-convergence in latent space with statistical testing.
    
    Parameters
    ----------
    latent_codes : np.ndarray
        Latent representations from VAE
    significance_level : float
        Significance level for statistical tests
    bootstrap_samples : int
        Number of bootstrap samples for confidence intervals
        
    Returns
    -------
    dict
        Analysis results including convergence metrics and significance tests
    """
    print("🔍 Analyzing Phi-Convergence in Latent Space")
    print("=" * 50)
    
    # Calculate dimensional ratios
    ratios = []
    phi_proximities = []
    
    for i in range(latent_codes.shape[1] - 1):
        dim_ratios = latent_codes[:, i+1] / (latent_codes[:, i] + 1e-8)
        ratios.extend(dim_ratios)
        
        # Calculate proximity to golden ratio
        proximity = np.abs(dim_ratios - PHI)
        phi_proximities.extend(proximity)
    
    ratios = np.array(ratios)
    phi_proximities = np.array(phi_proximities)
    
    # Basic statistics
    mean_ratio = np.mean(ratios)
    std_ratio = np.std(ratios)
    mean_proximity = np.mean(phi_proximities)
    
    # Phi alignment score
    phi_alignment = 1.0 - (mean_proximity / PHI)
    phi_alignment = max(0.0, phi_alignment)
    
    # Statistical significance testing
    # Null hypothesis: ratios are uniformly distributed
    # Alternative hypothesis: ratios are concentrated around phi
    
    # Kolmogorov-Smirnov test against uniform distribution
    # Transform ratios to [0,1] range for comparison
    normalized_ratios = (ratios - np.min(ratios)) / (np.max(ratios) - np.min(ratios))
    ks_statistic, ks_pvalue = stats.kstest(normalized_ratios, 'uniform')
    
    # Anderson-Darling test for normality around phi
    ad_statistic, ad_critical_values, ad_significance_levels = stats.anderson(
        phi_proximities, dist='norm'
    )
    
    # Bootstrap confidence intervals
    bootstrap_means = []
    bootstrap_alignments = []
    
    for _ in range(bootstrap_samples):
        # Sample with replacement
        sample_indices = np.random.choice(len(phi_proximities), len(phi_proximities))
        sample_proximities = phi_proximities[sample_indices]
        sample_mean = np.mean(sample_proximities)
        sample_alignment = 1.0 - (sample_mean / PHI)
        sample_alignment = max(0.0, sample_alignment)
        
        bootstrap_means.append(sample_mean)
        bootstrap_alignments.append(sample_alignment)
    
    # Calculate confidence intervals
    ci_lower_mean = np.percentile(bootstrap_means, 2.5)
    ci_upper_mean = np.percentile(bootstrap_means, 97.5)
    ci_lower_alignment = np.percentile(bootstrap_alignments, 2.5)
    ci_upper_alignment = np.percentile(bootstrap_alignments, 97.5)
    
    # Count significant phi matches
    threshold = 0.1 * PHI  # Within 10% of phi
    significant_matches = np.sum(phi_proximities < threshold)
    significant_fraction = significant_matches / len(phi_proximities)
    
    results = {
        'mean_ratio': float(mean_ratio),
        'std_ratio': float(std_ratio),
        'phi_alignment_score': float(phi_alignment),
        'mean_phi_proximity': float(mean_proximity),
        'significant_fraction': float(significant_fraction),
        'total_measurements': len(ratios),
        'ks_statistic': float(ks_statistic),
        'ks_pvalue': float(ks_pvalue),
        'ad_statistic': float(ad_statistic),
        'ad_critical_values': [float(cv) for cv in ad_critical_values],
        'ci_lower_mean': float(ci_lower_mean),
        'ci_upper_mean': float(ci_upper_mean),
        'ci_lower_alignment': float(ci_lower_alignment),
        'ci_upper_alignment': float(ci_upper_alignment),
        'bootstrap_samples': bootstrap_samples
    }
    
    # Interpret statistical tests
    results['ks_significant'] = ks_pvalue < significance_level
    results['ad_significant'] = ad_statistic > ad_critical_values[2]  # 5% significance level
    
    return results

def compare_with_baseline(model_path: str, 
                         baseline_model_path: str,
                         num_samples: int = 1000) -> dict:
    """
    Compare phi-convergence between trained model and baseline.
    
    Parameters
    ----------
    model_path : str
        Path to trained QuantumVAE model
    baseline_model_path : str
        Path to baseline model (could be random weights)
    num_samples : int
        Number of samples for comparison
        
    Returns
    -------
    dict
        Comparison results
    """
    print("⚖️  Comparing with Baseline Model")
    print("=" * 40)
    
    # Load trained model
    model = QuantumVAE()
    model.load_state_dict(torch.load(model_path))
    model.eval()
    
    # Load baseline model (random weights)
    baseline_model = QuantumVAE()
    if Path(baseline_model_path).exists():
        baseline_model.load_state_dict(torch.load(baseline_model_path))
    # Else keep random weights for baseline
    baseline_model.eval()
    
    # Generate test data
    test_data = generate_quantum_states(num_samples)
    test_tensor = torch.from_numpy(test_data)
    
    # Extract latent representations
    with torch.no_grad():
        # Trained model
        mu_trained, _ = model.encode(test_tensor)
        latent_trained = mu_trained.numpy()
        
        # Baseline model
        mu_baseline, _ = baseline_model.encode(test_tensor)
        latent_baseline = mu_baseline.numpy()
    
    # Analyze both models
    trained_results = analyze_phi_convergence(latent_trained)
    baseline_results = analyze_phi_convergence(latent_baseline)
    
    # Calculate improvement
    improvement = (
        trained_results['phi_alignment_score'] - 
        baseline_results['phi_alignment_score']
    )
    
    comparison = {
        'trained_model': trained_results,
        'baseline_model': baseline_results,
        'improvement': float(improvement),
        'relative_improvement': (
            improvement / baseline_results['phi_alignment_score'] 
            if baseline_results['phi_alignment_score'] > 0 else 0
        )
    }
    
    return comparison

def create_visualizations(latent_codes: np.ndarray, 
                        analysis_results: dict,
                        output_dir: Path):
    """
    Create visualizations for phi-convergence analysis.
    
    Parameters
    ----------
    latent_codes : np.ndarray
        Latent representations
    analysis_results : dict
        Results from phi-convergence analysis
    output_dir : Path
        Directory to save visualizations
    """
    print("📊 Creating Visualizations")
    print("=" * 30)
    
    # Create output directory
    output_dir.mkdir(exist_ok=True)
    
    # Figure 1: Ratio distribution
    plt.figure(figsize=(15, 5))
    
    # Calculate ratios for visualization
    sample_ratios = []
    for i in range(min(10, latent_codes.shape[1] - 1)):  # First 10 dimensions
        dim_ratios = latent_codes[:, i+1] / (latent_codes[:, i] + 1e-8)
        sample_ratios.extend(dim_ratios[:1000])  # Sample first 1000 ratios
    
    sample_ratios = np.array(sample_ratios)
    
    plt.subplot(1, 3, 1)
    plt.hist(sample_ratios, bins=50, alpha=0.7, color='blue', edgecolor='black')
    plt.axvline(PHI, color='red', linestyle='--', linewidth=2, label=f'φ = {PHI:.3f}')
    plt.axvline(analysis_results['mean_ratio'], color='orange', linestyle='-', 
                linewidth=2, label=f'Mean = {analysis_results["mean_ratio"]:.3f}')
    plt.xlabel('Dimension Ratios')
    plt.ylabel('Frequency')
    plt.title('Latent Dimension Ratios Distribution')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Phi proximity distribution
    phi_proximities = np.abs(sample_ratios - PHI)
    
    plt.subplot(1, 3, 2)
    plt.hist(phi_proximities, bins=50, alpha=0.7, color='green', edgecolor='black')
    plt.axvline(0, color='red', linestyle='--', linewidth=2, label='Perfect φ alignment')
    threshold = 0.1 * PHI
    plt.axvline(threshold, color='orange', linestyle='--', linewidth=2, 
                label=f'Threshold = {threshold:.3f}')
    plt.xlabel('Distance from Golden Ratio')
    plt.ylabel('Frequency')
    plt.title('Phi Proximity Distribution')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Cumulative distribution
    plt.subplot(1, 3, 3)
    sorted_proximities = np.sort(phi_proximities)
    cumulative = np.arange(len(sorted_proximities)) / len(sorted_proximities)
    plt.plot(sorted_proximities, cumulative, linewidth=2, color='purple')
    plt.axvline(threshold, color='red', linestyle='--', linewidth=2, 
                label=f'Threshold = {threshold:.3f}')
    plt.xlabel('Phi Proximity')
    plt.ylabel('Cumulative Probability')
    plt.title('Cumulative Distribution of Phi Proximity')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'phi_convergence_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Visualization saved: {output_dir / 'phi_convergence_analysis.png'}")

def generate_report(analysis_results: dict, 
                   comparison_results: dict,
                   output_dir: Path):
    """
    Generate detailed analysis report.
    
    Parameters
    ----------
    analysis_results : dict
        Phi-convergence analysis results
    comparison_results : dict
        Comparison with baseline results
    output_dir : Path
        Directory to save report
    """
    report_file = output_dir / 'phi_convergence_report.md'
    
    with open(report_file, 'w') as f:
        f.write("# Phi-Convergence Analysis Report\n\n")
        f.write(f"Generated on: {np.datetime64('now')}\n\n")
        
        f.write("## Primary Analysis Results\n")
        f.write(f"- Mean Dimension Ratio: {analysis_results['mean_ratio']:.6f}\n")
        f.write(f"- Phi Alignment Score: {analysis_results['phi_alignment_score']:.6f}\n")
        f.write(f"- Significant Phi Matches: {analysis_results['significant_fraction']:.2%}\n")
        f.write(f"- KS Test P-value: {analysis_results['ks_pvalue']:.6f}\n")
        f.write(f"- KS Significant (α=0.05): {analysis_results['ks_significant']}\n")
        
        if comparison_results:
            f.write("\n## Comparison with Baseline\n")
            trained_score = comparison_results['trained_model']['phi_alignment_score']
            baseline_score = comparison_results['baseline_model']['phi_alignment_score']
            improvement = comparison_results['improvement']
            rel_improvement = comparison_results['relative_improvement']
            
            f.write(f"- Trained Model Score: {trained_score:.6f}\n")
            f.write(f"- Baseline Model Score: {baseline_score:.6f}\n")
            f.write(f"- Absolute Improvement: {improvement:.6f}\n")
            f.write(f"- Relative Improvement: {rel_improvement:.2%}\n")
        
        f.write("\n## Statistical Validation\n")
        f.write(f"- 95% CI for Mean Proximity: [{analysis_results['ci_lower_mean']:.6f}, {analysis_results['ci_upper_mean']:.6f}]\n")
        f.write(f"- 95% CI for Alignment Score: [{analysis_results['ci_lower_alignment']:.6f}, {analysis_results['ci_upper_alignment']:.6f}]\n")
        f.write(f"- Bootstrap Samples: {analysis_results['bootstrap_samples']}\n")
    
    print(f"Report generated: {report_file}")

def main(model_path: str = 'best_model.pt',
         baseline_model_path: str = 'baseline_model.pt',
         num_samples: int = 1000,
         output_dir: str = 'analysis_results'):
    """
    Main analysis function.
    
    Parameters
    ----------
    model_path : str
        Path to trained model
    baseline_model_path : str
        Path to baseline model
    num_samples : int
        Number of samples for analysis
    output_dir : str
        Output directory for results
    """
    print("🔬 Quantum VAE Phi-Convergence Analysis")
    print("=" * 50)
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Load model and generate test data
    print("Loading model and generating test data...")
    model = QuantumVAE()
    model.load_state_dict(torch.load(model_path))
    model.eval()
    
    test_data = generate_quantum_states(num_samples)
    test_tensor = torch.from_numpy(test_data)
    
    # Extract latent representations
    print("Extracting latent representations...")
    with torch.no_grad():
        mu, _ = model.encode(test_tensor)
        latent_codes = mu.numpy()
    
    # Perform phi-convergence analysis
    print("Performing phi-convergence analysis...")
    analysis_results = analyze_phi_convergence(latent_codes)
    
    # Compare with baseline
    print("Comparing with baseline model...")
    try:
        comparison_results = compare_with_baseline(
            model_path, baseline_model_path, num_samples
        )
    except Exception as e:
        print(f"Baseline comparison failed: {e}")
        comparison_results = None
    
    # Create visualizations
    print("Creating visualizations...")
    create_visualizations(latent_codes, analysis_results, output_path)
    
    # Generate report
    print("Generating report...")
    generate_report(analysis_results, comparison_results, output_path)
    
    # Print summary
    print("\n" + "=" * 50)
    print("ANALYSIS SUMMARY")
    print("=" * 50)
    print(f"Phi Alignment Score: {analysis_results['phi_alignment_score']:.6f}")
    print(f"Significant Phi Matches: {analysis_results['significant_fraction']:.2%}")
    print(f"KS Test Significant: {analysis_results['ks_significant']}")
    
    if comparison_results:
        improvement = comparison_results['improvement']
        rel_improvement = comparison_results['relative_improvement']
        print(f"Improvement over baseline: {improvement:.6f} ({rel_improvement:.2%})")
    
    print(f"\n📊 Results saved to: {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze phi-convergence in Quantum VAE latent space")
    parser.add_argument("--model-path", type=str, default="best_model.pt",
                        help="Path to trained QuantumVAE model")
    parser.add_argument("--baseline-model-path", type=str, default="baseline_model.pt",
                        help="Path to baseline model for comparison")
    parser.add_argument("--num-samples", type=int, default=1000,
                        help="Number of samples for analysis")
    parser.add_argument("--output-dir", type=str, default="phi_analysis_results",
                        help="Output directory for results")
    
    args = parser.parse_args()
    main(args.model_path, args.baseline_model_path, args.num_samples, args.output_dir)