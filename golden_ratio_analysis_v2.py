"""
Golden Ratio Analysis V2 - Unified Pipeline

Comprehensive golden ratio detection with statistical rigor.
Integrates all modules: statistics, detection, and visualization.

Usage:
    from golden_ratio_analysis_v2 import ComprehensiveGoldenRatioAnalyzer

    analyzer = ComprehensiveGoldenRatioAnalyzer(latent_codes)
    results = analyzer.run_full_analysis()
"""

import numpy as np
from typing import Dict, Optional
import json
from pathlib import Path

from golden_ratio_statistics import GoldenRatioStatistics
from golden_ratio_detectors import MultiMethodDetector
from golden_ratio_visualization import GoldenRatioVisualizer, plot_quick_summary


class ComprehensiveGoldenRatioAnalyzer:
    """
    Unified pipeline for comprehensive golden ratio analysis.

    Combines statistical rigor, multi-method detection, and
    publication-quality visualization.

    Parameters
    ----------
    latent_codes : ndarray, shape (n_samples, n_dimensions)
        Latent representations from VAE
    confidence_level : float, default=0.95
        Confidence level for statistical tests
    random_state : int, optional
        Random seed for reproducibility

    Attributes
    ----------
    statistics : GoldenRatioStatistics
        Statistical analysis module
    detectors : MultiMethodDetector
        Multi-method detection module
    results : dict
        Comprehensive analysis results
    """

    def __init__(self, latent_codes: np.ndarray, confidence_level: float = 0.95,
                 random_state: Optional[int] = 42):
        self.latent_codes = latent_codes
        self.confidence_level = confidence_level
        self.random_state = random_state
        self.phi = (1 + np.sqrt(5)) / 2

        # Initialize modules
        self.statistics = GoldenRatioStatistics(
            latent_codes, confidence_level, random_state
        )
        self.detectors = MultiMethodDetector(latent_codes)

        self.results = None

    def run_full_analysis(self, n_bootstrap: int = 10000,
                         n_permutations: int = 5000,
                         run_detectors: bool = True,
                         create_visualizations: bool = True,
                         output_dir: str = '.') -> Dict:
        """
        Run comprehensive golden ratio analysis pipeline.

        Parameters
        ----------
        n_bootstrap : int, default=10000
            Number of bootstrap iterations
        n_permutations : int, default=5000
            Number of permutation test iterations
        run_detectors : bool, default=True
            Whether to run multi-method detectors
        create_visualizations : bool, default=True
            Whether to create visualization plots
        output_dir : str, default='.'
            Directory for saving outputs

        Returns
        -------
        dict
            Comprehensive analysis results containing:
            - statistical_analysis : Statistical test results
            - detection_results : Multi-method detection results (if run)
            - visualizations_created : List of visualization paths (if created)
            - summary : High-level summary and conclusions

        Notes
        -----
        This method orchestrates the full analysis workflow:
        1. Statistical threshold estimation (bootstrap)
        2. Significance testing (permutation test)
        3. Effect size calculation
        4. Multi-method detection (optional)
        5. Comprehensive visualization (optional)
        6. Summary generation
        """
        print("\n" + "="*80)
        print("COMPREHENSIVE GOLDEN RATIO ANALYSIS V2")
        print("="*80)
        print(f"Dataset: {self.latent_codes.shape[0]} samples × {self.latent_codes.shape[1]} dimensions")
        print(f"Golden ratio φ = {self.phi:.10f}")
        print("="*80 + "\n")

        # Phase 1: Statistical Analysis
        print("PHASE 1: STATISTICAL ANALYSIS")
        print("-"*80)
        statistical_results = self.statistics.comprehensive_analysis(
            n_bootstrap=n_bootstrap,
            n_permutations=n_permutations
        )
        print()

        # Phase 2: Multi-Method Detection (optional)
        detection_results = None
        if run_detectors:
            print("PHASE 2: MULTI-METHOD DETECTION")
            print("-"*80)
            adaptive_threshold = statistical_results['recommended_threshold']
            detection_results = self.detectors.detect_all(threshold=adaptive_threshold)
            print()

        # Phase 3: Visualization (optional)
        visualization_paths = []
        if create_visualizations:
            print("PHASE 3: VISUALIZATION")
            print("-"*80)

            visualizer = GoldenRatioVisualizer(
                self.latent_codes,
                statistical_results,
                detection_results
            )

            # Comprehensive plot
            comp_path = str(Path(output_dir) / 'golden_ratio_analysis_enhanced.png')
            visualizer.plot_comprehensive_analysis(save_path=comp_path)
            visualization_paths.append(comp_path)

            # Statistical summary
            summary_path = str(Path(output_dir) / 'golden_ratio_summary.png')
            visualizer.plot_statistical_summary(save_path=summary_path)
            visualization_paths.append(summary_path)

            # Quick summary
            quick_path = str(Path(output_dir) / 'golden_ratio_quick.png')
            plot_quick_summary(self.latent_codes, statistical_results, save_path=quick_path)
            visualization_paths.append(quick_path)

            print()

        # Phase 4: Generate Summary
        print("PHASE 4: SUMMARY GENERATION")
        print("-"*80)
        summary = self._generate_summary(statistical_results, detection_results)
        print()

        # Compile results
        self.results = {
            'statistical_analysis': statistical_results,
            'detection_results': detection_results,
            'visualizations_created': visualization_paths,
            'summary': summary,
            'parameters': {
                'n_bootstrap': n_bootstrap,
                'n_permutations': n_permutations,
                'confidence_level': self.confidence_level,
                'random_state': self.random_state
            }
        }

        # Save results to JSON
        results_path = Path(output_dir) / 'golden_ratio_analysis_results.json'
        self._save_results(results_path)

        print("="*80)
        print("ANALYSIS COMPLETE")
        print("="*80)
        print(f"Results saved to: {results_path}")
        print(f"Visualizations: {len(visualization_paths)} files created")
        print("="*80 + "\n")

        return self.results

    def run_quick_analysis(self, output_dir: str = '.') -> Dict:
        """
        Run quick analysis with reduced iterations for speed.

        Parameters
        ----------
        output_dir : str
            Directory for saving outputs

        Returns
        -------
        dict
            Analysis results
        """
        print("Running QUICK analysis (reduced iterations)...\n")
        return self.run_full_analysis(
            n_bootstrap=5000,
            n_permutations=2000,
            run_detectors=False,
            create_visualizations=True,
            output_dir=output_dir
        )

    def run_detailed_analysis(self, output_dir: str = '.') -> Dict:
        """
        Run detailed analysis with increased iterations for precision.

        Parameters
        ----------
        output_dir : str
            Directory for saving outputs

        Returns
        -------
        dict
            Analysis results
        """
        print("Running DETAILED analysis (increased iterations)...\n")
        return self.run_full_analysis(
            n_bootstrap=20000,
            n_permutations=10000,
            run_detectors=True,
            create_visualizations=True,
            output_dir=output_dir
        )

    def _generate_summary(self, statistical_results: Dict,
                         detection_results: Optional[Dict]) -> Dict:
        """
        Generate high-level summary and conclusions.

        Parameters
        ----------
        statistical_results : dict
            Statistical analysis results
        detection_results : dict or None
            Detection results (if run)

        Returns
        -------
        dict
            Summary with conclusions
        """
        bootstrap = statistical_results['bootstrap']
        permutation = statistical_results['permutation']
        effects = statistical_results['effect_sizes']

        # Statistical conclusion
        is_significant = permutation['is_significant']
        has_large_effect = abs(effects['cohens_d']) > 0.5

        if is_significant and has_large_effect:
            conclusion = "SIGNIFICANT"
            interpretation = ("Strong statistical evidence for golden ratio patterns. "
                            "Dimension ratios cluster around φ significantly more than "
                            "random expectations with large effect size.")
            recommendation = ("Results support φ-based optimization hypothesis. "
                            "Suitable for publication and further investigation.")
        elif is_significant and not has_large_effect:
            conclusion = "STATISTICALLY_SIGNIFICANT_BUT_SMALL"
            interpretation = ("Statistically significant but small effect. "
                            "Golden ratio patterns present but weak.")
            recommendation = ("Increase sample size or investigate specific subsets "
                            "where effect may be stronger.")
        else:
            conclusion = "NOT_SIGNIFICANT"
            interpretation = ("No significant evidence for golden ratio patterns. "
                            "Dimension ratios consistent with random distribution.")
            recommendation = ("Consider alternative organizational principles or "
                            "different architectural configurations.")

        summary = {
            'conclusion': conclusion,
            'interpretation': interpretation,
            'recommendation': recommendation,
            'key_metrics': {
                'p_value': permutation['p_value'],
                'cohens_d': effects['cohens_d'],
                'recommended_threshold': bootstrap['threshold'],
                'fraction_within_threshold': effects['fraction_within_threshold']
            }
        }

        # Add detector consensus if available
        if detection_results is not None:
            votes = detection_results['ensemble_votes']
            consensus = detection_results['consensus']
            summary['detector_consensus'] = {
                'votes': f"{votes}/4",
                'has_consensus': consensus,
                'interpretation': (f"{votes} out of 4 detection methods found golden ratio patterns. " +
                                  ("Strong multi-method agreement." if consensus else
                                   "Weak or inconsistent detection."))
            }

        # Print summary
        print("KEY FINDINGS:")
        print(f"  Conclusion: {conclusion}")
        print(f"  p-value: {permutation['p_value']:.4f} " +
              f"({'***' if permutation['p_value'] < 0.001 else '**' if permutation['p_value'] < 0.01 else '*' if permutation['p_value'] < 0.05 else 'ns'})")
        print(f"  Cohen's d: {effects['cohens_d']:.3f} " +
              f"({'small' if abs(effects['cohens_d']) < 0.5 else 'medium' if abs(effects['cohens_d']) < 0.8 else 'large'} effect)")
        print(f"  Recommended threshold: {bootstrap['threshold']:.4f}")
        if detection_results is not None:
            print(f"  Detector consensus: {votes}/4 methods")
        print()
        print("INTERPRETATION:")
        print(f"  {interpretation}")
        print()
        print("RECOMMENDATION:")
        print(f"  {recommendation}")

        return summary

    def _save_results(self, filepath: Path):
        """
        Save results to JSON file.

        Parameters
        ----------
        filepath : Path
            Path to save JSON file
        """
        # Convert numpy arrays to lists for JSON serialization
        saveable_results = {}

        for key, value in self.results.items():
            if key == 'statistical_analysis':
                saveable_results[key] = self._convert_for_json(value)
            elif key == 'detection_results' and value is not None:
                saveable_results[key] = self._convert_for_json(value)
            else:
                saveable_results[key] = value

        with open(filepath, 'w') as f:
            json.dump(saveable_results, f, indent=2)

    def _convert_for_json(self, obj):
        """Recursively convert numpy arrays to lists for JSON."""
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: self._convert_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._convert_for_json(item) for item in obj]
        elif isinstance(obj, (np.integer, np.floating)):
            return float(obj)
        else:
            return obj


# Convenience functions
def analyze_latent_codes(latent_codes: np.ndarray, mode: str = 'standard',
                        output_dir: str = '.') -> Dict:
    """
    Convenience function for quick analysis.

    Parameters
    ----------
    latent_codes : ndarray
        Latent codes from VAE
    mode : str, default='standard'
        Analysis mode: 'quick', 'standard', or 'detailed'
    output_dir : str
        Output directory

    Returns
    -------
    dict
        Analysis results
    """
    analyzer = ComprehensiveGoldenRatioAnalyzer(latent_codes)

    if mode == 'quick':
        return analyzer.run_quick_analysis(output_dir)
    elif mode == 'detailed':
        return analyzer.run_detailed_analysis(output_dir)
    else:
        return analyzer.run_full_analysis(output_dir=output_dir)


if __name__ == '__main__':
    """Example usage for testing."""
    import torch
    from vae_model import QuantumVAE

    print("Loading VAE model...")
    model = QuantumVAE(input_dim=128, latent_dim=32)
    model.load_state_dict(torch.load('best_model.pt', map_location='cpu'))
    model.eval()

    print("Generating consciousness states...")
    # Simple consciousness state generation
    n_samples = 1000
    consciousness_states = []
    for _ in range(n_samples):
        # Random quantum state
        state = np.random.randn(128)
        state = state / np.linalg.norm(state)
        consciousness_states.append(state)

    consciousness_states = np.array(consciousness_states)

    # Extract latent codes
    print("Extracting latent codes...")
    with torch.no_grad():
        data_tensor = torch.from_numpy(consciousness_states).float()
        mu, _ = model.encode(data_tensor)
        latent_codes = mu.numpy()

    print(f"Latent codes shape: {latent_codes.shape}")

    # Run comprehensive analysis
    analyzer = ComprehensiveGoldenRatioAnalyzer(latent_codes)
    results = analyzer.run_full_analysis()

    print("\nAnalysis complete! Check output files.")
