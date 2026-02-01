"""
Run Comprehensive Golden Ratio Analysis

This script demonstrates the enhanced golden ratio detection system
integrated with quantum consciousness analysis.

Usage:
    python run_golden_ratio_analysis.py
"""

import torch
import numpy as np
from vae_model import QuantumVAE
from golden_ratio_analysis_v2 import ComprehensiveGoldenRatioAnalyzer

def main():
    print("="*80)
    print("QUANTUM CONSCIOUSNESS GOLDEN RATIO ANALYSIS")
    print("Enhanced Statistical Methods (V2)")
    print("="*80)
    print()

    # Load trained VAE model
    print("[1/5] Loading QuantumVAE model...")
    model = QuantumVAE(input_dim=128, latent_dim=32)
    try:
        model.load_state_dict(torch.load('best_model.pt', map_location='cpu', weights_only=True))
        model.eval()
        print("  Model loaded successfully")
    except Exception as e:
        print(f"  Error loading model: {e}")
        print("  Continuing with untrained model for demonstration...")
    print()

    # Generate consciousness states
    print("[2/5] Generating consciousness states...")
    phi = (1 + np.sqrt(5)) / 2

    consciousness_archetypes = {
        'baseline': {'coherence': 0.5, 'complexity': 0.3},
        'focused': {'coherence': 0.8, 'complexity': 0.2},
        'creative': {'coherence': 0.6, 'complexity': 0.8},
        'transcendent': {'coherence': 0.9, 'complexity': 0.9},
        'chaotic': {'coherence': 0.2, 'complexity': 0.9}
    }

    n_samples_per_archetype = 200
    consciousness_states = []

    for archetype_name, params in consciousness_archetypes.items():
        for _ in range(n_samples_per_archetype):
            # Generate base quantum state (64 complex dimensions → 128 real)
            real = np.random.randn(64)
            imag = np.random.randn(64)
            state = real + 1j * imag

            # Apply coherence
            coherence = params['coherence']
            state = coherence * state * np.exp(1j * np.random.uniform(0, 2*np.pi))

            # Apply complexity
            complexity = params['complexity']
            state = state + complexity * np.random.randn(64) * (1 + 1j)

            # Normalize
            state = state / np.linalg.norm(state)

            # Convert to real representation
            state_real = np.concatenate([state.real, state.imag])
            consciousness_states.append(state_real)

    consciousness_states = np.array(consciousness_states)
    print(f"  Generated {len(consciousness_states)} consciousness states")
    print(f"  Archetypes: {list(consciousness_archetypes.keys())}")
    print()

    # Extract latent codes
    print("[3/5] Extracting latent representations...")
    with torch.no_grad():
        data_tensor = torch.from_numpy(consciousness_states).float()
        mu, log_var = model.encode(data_tensor)
        latent_codes = mu.numpy()

    print(f"  Latent codes shape: {latent_codes.shape}")
    print(f"  Latent statistics: mean={latent_codes.mean():.3f}, std={latent_codes.std():.3f}")
    print()

    # Run comprehensive golden ratio analysis
    print("[4/5] Running comprehensive golden ratio analysis...")
    print("  This may take a few minutes...")
    print()

    analyzer = ComprehensiveGoldenRatioAnalyzer(
        latent_codes,
        confidence_level=0.95,
        random_state=42
    )

    results = analyzer.run_full_analysis(
        n_bootstrap=10000,      # 10k bootstrap iterations for robust threshold
        n_permutations=5000,    # 5k permutations for significance testing
        run_detectors=True,     # Run all 4 detection methods
        create_visualizations=True,  # Create publication-quality plots
        output_dir='.'
    )

    # Display results summary
    print()
    print("[5/5] Results Summary")
    print("="*80)

    summary = results['summary']
    print(f"\nCONCLUSION: {summary['conclusion']}")
    print(f"\n{summary['interpretation']}")
    print(f"\nRECOMMENDATION:\n{summary['recommendation']}")

    print("\n" + "="*80)
    print("KEY METRICS")
    print("="*80)
    metrics = summary['key_metrics']
    print(f"  p-value: {metrics['p_value']:.4f} " +
          f"({'***' if metrics['p_value'] < 0.001 else '**' if metrics['p_value'] < 0.01 else '*' if metrics['p_value'] < 0.05 else 'ns'})")
    print(f"  Cohen's d: {metrics['cohens_d']:.3f} " +
          f"({'small' if abs(metrics['cohens_d']) < 0.5 else 'medium' if abs(metrics['cohens_d']) < 0.8 else 'large'} effect)")
    print(f"  Recommended threshold: {metrics['recommended_threshold']:.4f}")
    print(f"  Fraction within threshold: {metrics['fraction_within_threshold']:.3f} ({metrics['fraction_within_threshold']*100:.1f}%)")

    if 'detector_consensus' in summary:
        consensus = summary['detector_consensus']
        print(f"\n  Multi-method detector votes: {consensus['votes']}")
        print(f"  Consensus: {'YES' if consensus['has_consensus'] else 'NO'}")

    print("\n" + "="*80)
    print("OUTPUT FILES")
    print("="*80)
    if results['visualizations_created']:
        for viz_path in results['visualizations_created']:
            print(f"  {viz_path}")
    print(f"  golden_ratio_analysis_results.json")

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE!")
    print("="*80)
    print("\nNext steps:")
    print("  1. Review the enhanced visualizations")
    print("  2. Check golden_ratio_analysis_results.json for detailed statistics")
    print("  3. Compare with original analysis (quantum_consciousness_link.png)")
    print("  4. Consider publishing results if significant patterns found")
    print()


if __name__ == '__main__':
    main()
