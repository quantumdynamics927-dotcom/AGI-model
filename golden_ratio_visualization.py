"""
Golden Ratio Enhanced Visualization Module

Creates publication-quality visualizations with confidence intervals,
significance markers, and comprehensive multi-panel plots.
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import gaussian_kde, probplot
from typing import Dict, Optional
import warnings
warnings.filterwarnings('ignore')


class GoldenRatioVisualizer:
    """
    Create enhanced visualizations for golden ratio analysis.

    Parameters
    ----------
    latent_codes : ndarray
        Latent representations
    statistical_results : dict
        Results from GoldenRatioStatistics analysis
    detection_results : dict, optional
        Results from multi-method detection
    """

    def __init__(self, latent_codes: np.ndarray,
                 statistical_results: Dict,
                 detection_results: Optional[Dict] = None):
        self.latent_codes = latent_codes
        self.stats_results = statistical_results
        self.detection_results = detection_results
        self.phi = (1 + np.sqrt(5)) / 2

        # Extract ratios
        self.ratios = self._compute_ratios()

    def _compute_ratios(self) -> np.ndarray:
        """Compute all pairwise dimension ratios."""
        ratios = []
        n_dims = self.latent_codes.shape[1]
        for i in range(n_dims - 1):
            for j in range(i + 1, n_dims):
                ratio = np.abs(self.latent_codes[:, i]) / (np.abs(self.latent_codes[:, j]) + 1e-10)
                ratios.extend(ratio)
        return np.array(ratios)

    def plot_comprehensive_analysis(self, save_path: str = 'golden_ratio_analysis_enhanced.png'):
        """
        Create comprehensive 6-panel visualization with confidence intervals.

        Panels:
        1. Histogram with Bootstrap CI
        2. KDE with Confidence Envelope
        3. Q-Q Plot
        4. Bootstrap Distribution
        5. Proximity Distribution Bins
        6. Statistical Summary

        Parameters
        ----------
        save_path : str
            Path to save the figure
        """
        fig = plt.figure(figsize=(20, 12))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

        bootstrap_results = self.stats_results['bootstrap']
        permutation_results = self.stats_results['permutation']
        effect_results = self.stats_results['effect_sizes']

        # Panel 1: Histogram with Bootstrap CI
        ax1 = fig.add_subplot(gs[0, 0])
        self._plot_histogram_with_ci(ax1, bootstrap_results)

        # Panel 2: KDE with Confidence Envelope
        ax2 = fig.add_subplot(gs[0, 1])
        self._plot_kde_with_envelope(ax2)

        # Panel 3: Q-Q Plot
        ax3 = fig.add_subplot(gs[0, 2])
        self._plot_qq(ax3)

        # Panel 4: Bootstrap Distribution
        ax4 = fig.add_subplot(gs[1, 0])
        self._plot_bootstrap_distribution(ax4, bootstrap_results)

        # Panel 5: Proximity Distribution Bins
        ax5 = fig.add_subplot(gs[1, 1])
        self._plot_proximity_bins(ax5)

        # Panel 6: Permutation Test Results
        ax6 = fig.add_subplot(gs[1, 2])
        self._plot_permutation_results(ax6, permutation_results)

        # Panel 7: Dimension Pair Heatmap (large bottom panel)
        ax7 = fig.add_subplot(gs[2, :])
        self._plot_dimension_heatmap(ax7)

        # Super title
        conclusion = self.stats_results.get('conclusion', 'unknown')
        fig.suptitle(f'Enhanced Golden Ratio Analysis - {conclusion.replace("_", " ").title()}',
                    fontsize=18, fontweight='bold', y=0.995)

        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"\nVisualization saved to: {save_path}")

        return fig

    def _plot_histogram_with_ci(self, ax, bootstrap_results):
        """Plot histogram of ratios with bootstrap confidence interval."""
        threshold = self.stats_results['recommended_threshold']
        ci_lower = bootstrap_results['ci_lower']
        ci_upper = bootstrap_results['ci_upper']

        # Histogram
        n, bins, patches = ax.hist(self.ratios, bins=100, alpha=0.6,
                                   color='skyblue', edgecolor='black',
                                   density=True, label='Observed Ratios')

        # Shade confidence region around phi
        ax.axvspan(self.phi - threshold, self.phi + threshold,
                  alpha=0.2, color='gold',
                  label=f'Threshold ±{threshold:.3f}')

        # Phi line
        ax.axvline(self.phi, color='red', linewidth=2.5, linestyle='--',
                  label=f'φ = {self.phi:.4f}', zorder=10)

        # CI lines
        ax.axvline(self.phi - ci_lower, color='orange', linewidth=1.5,
                  linestyle=':', alpha=0.7, label='95% CI bounds')
        ax.axvline(self.phi + ci_upper, color='orange', linewidth=1.5,
                  linestyle=':', alpha=0.7)

        ax.set_xlabel('Dimension Ratios', fontsize=11, fontweight='bold')
        ax.set_ylabel('Density', fontsize=11, fontweight='bold')
        ax.set_title('Ratio Distribution with Bootstrap CI', fontsize=12, fontweight='bold')
        ax.legend(fontsize=9, loc='best')
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, min(10, np.percentile(self.ratios, 99)))

    def _plot_kde_with_envelope(self, ax):
        """Plot KDE with bootstrap confidence envelope."""
        # Main KDE
        kde = gaussian_kde(self.ratios)
        x_range = np.linspace(0, min(10, np.percentile(self.ratios, 99)), 1000)
        kde_values = kde(x_range)

        # Bootstrap KDE for confidence envelope
        n_bootstrap_kde = 100
        kde_bootstrap = []
        for _ in range(n_bootstrap_kde):
            sample = np.random.choice(self.ratios, size=len(self.ratios), replace=True)
            kde_boot = gaussian_kde(sample)
            kde_bootstrap.append(kde_boot(x_range))

        kde_bootstrap = np.array(kde_bootstrap)
        kde_lower = np.percentile(kde_bootstrap, 2.5, axis=0)
        kde_upper = np.percentile(kde_bootstrap, 97.5, axis=0)

        # Plot
        ax.plot(x_range, kde_values, 'b-', linewidth=2.5, label='KDE', zorder=5)
        ax.fill_between(x_range, kde_lower, kde_upper, alpha=0.3,
                        color='blue', label='95% CI', zorder=3)
        ax.axvline(self.phi, color='red', linewidth=2.5, linestyle='--',
                  label='φ', zorder=10)

        ax.set_xlabel('Dimension Ratios', fontsize=11, fontweight='bold')
        ax.set_ylabel('Density', fontsize=11, fontweight='bold')
        ax.set_title('Kernel Density Estimate with CI', fontsize=12, fontweight='bold')
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)

    def _plot_qq(self, ax):
        """Plot Q-Q plot to test for normality."""
        probplot(self.ratios, dist="norm", plot=ax)
        ax.set_title('Q-Q Plot (Normality Test)', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)

    def _plot_bootstrap_distribution(self, ax, bootstrap_results):
        """Plot bootstrap distribution of proximity to phi."""
        bootstrap_dist = bootstrap_results['bootstrap_dist']
        threshold = bootstrap_results['threshold']
        ci_lower = bootstrap_results['ci_lower']
        ci_upper = bootstrap_results['ci_upper']

        ax.hist(bootstrap_dist, bins=50, alpha=0.7, color='green',
               edgecolor='black', label='Bootstrap Distribution')

        ax.axvline(np.mean(bootstrap_dist), color='darkgreen', linewidth=2.5,
                  linestyle='--', label=f'Mean = {np.mean(bootstrap_dist):.4f}')
        ax.axvline(ci_lower, color='orange', linewidth=1.5, linestyle=':',
                  label=f'CI = [{ci_lower:.4f}, {ci_upper:.4f}]')
        ax.axvline(ci_upper, color='orange', linewidth=1.5, linestyle=':')

        ax.set_xlabel('Bootstrap Proximity to φ', fontsize=11, fontweight='bold')
        ax.set_ylabel('Frequency', fontsize=11, fontweight='bold')
        ax.set_title('Bootstrap Distribution', fontsize=12, fontweight='bold')
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)

    def _plot_proximity_bins(self, ax):
        """Plot proximity distribution in bins."""
        proximity = np.abs(self.ratios - self.phi)

        bins_edges = np.array([0, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, np.inf])
        bin_labels = ['0-0.05\n(Very Close)', '0.05-0.1\n(Close)',
                     '0.1-0.2\n(Moderate)', '0.2-0.5\n(Far)',
                     '0.5-1.0\n(Very Far)', '1.0-2.0\n(Distant)', '>2.0\n(Extreme)']
        counts, _ = np.histogram(proximity, bins=bins_edges)

        colors = ['darkgreen', 'green', 'yellowgreen', 'yellow',
                 'orange', 'red', 'darkred']

        bars = ax.bar(range(len(counts)), counts, color=colors, alpha=0.8,
                     edgecolor='black', linewidth=1.5)

        # Add percentage labels on bars
        total = sum(counts)
        for i, (bar, count) in enumerate(zip(bars, counts)):
            height = bar.get_height()
            pct = 100 * count / total
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{count}\n({pct:.1f}%)',
                   ha='center', va='bottom', fontsize=9, fontweight='bold')

        ax.set_xticks(range(len(counts)))
        ax.set_xticklabels(bin_labels, rotation=0, fontsize=9)
        ax.set_xlabel('Distance from φ', fontsize=11, fontweight='bold')
        ax.set_ylabel('Count', fontsize=11, fontweight='bold')
        ax.set_title('Proximity Distribution to Golden Ratio', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')

    def _plot_permutation_results(self, ax, permutation_results):
        """Plot permutation test results."""
        null_dist = permutation_results['null_distribution']
        observed = permutation_results['observed_stat']
        p_value = permutation_results['p_value']

        # Histogram of null distribution
        ax.hist(null_dist, bins=50, alpha=0.7, color='gray',
               edgecolor='black', label='Null Distribution', density=True)

        # Observed statistic
        ax.axvline(observed, color='red', linewidth=2.5, linestyle='--',
                  label=f'Observed = {observed:.4f}', zorder=10)

        # Mean of null
        null_mean = np.mean(null_dist)
        ax.axvline(null_mean, color='blue', linewidth=1.5, linestyle=':',
                  label=f'Null Mean = {null_mean:.4f}')

        # Significance annotation
        significance = 'p < 0.001 ***' if p_value < 0.001 else \
                      'p < 0.01 **' if p_value < 0.01 else \
                      'p < 0.05 *' if p_value < 0.05 else \
                      f'p = {p_value:.3f} ns'

        ax.text(0.95, 0.95, significance,
               transform=ax.transAxes,
               fontsize=12, fontweight='bold',
               verticalalignment='top', horizontalalignment='right',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

        ax.set_xlabel('Fraction within Threshold', fontsize=11, fontweight='bold')
        ax.set_ylabel('Density', fontsize=11, fontweight='bold')
        ax.set_title('Permutation Test Results', fontsize=12, fontweight='bold')
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)

    def _plot_dimension_heatmap(self, ax):
        """Plot heatmap of dimension pair proximities to phi."""
        n_dims = self.latent_codes.shape[1]
        proximity_matrix = np.zeros((n_dims, n_dims))

        for i in range(n_dims):
            for j in range(n_dims):
                if i != j:
                    ratio = np.abs(self.latent_codes[:, i]) / (np.abs(self.latent_codes[:, j]) + 1e-10)
                    proximity = np.mean(np.abs(ratio - self.phi))
                    proximity_matrix[i, j] = proximity

        # Plot heatmap
        im = ax.imshow(proximity_matrix, cmap='RdYlGn_r', aspect='auto',
                      vmin=0, vmax=1, interpolation='nearest')

        # Colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Mean Proximity to φ (lower = closer)', fontsize=11, fontweight='bold')

        # Mark golden pairs
        threshold = self.stats_results['recommended_threshold']
        for i in range(n_dims):
            for j in range(n_dims):
                if proximity_matrix[i, j] < threshold and i != j:
                    ax.plot(j, i, 'w*', markersize=8, markeredgecolor='black', markeredgewidth=0.5)

        ax.set_xlabel('Dimension Index', fontsize=11, fontweight='bold')
        ax.set_ylabel('Dimension Index', fontsize=11, fontweight='bold')
        ax.set_title(f'Dimension Pair Proximity Heatmap (★ = golden pairs, threshold={threshold:.3f})',
                    fontsize=12, fontweight='bold')

        # Set ticks
        tick_spacing = max(1, n_dims // 10)
        ax.set_xticks(range(0, n_dims, tick_spacing))
        ax.set_yticks(range(0, n_dims, tick_spacing))

    def plot_statistical_summary(self, save_path: str = 'golden_ratio_summary.png'):
        """
        Create a text-based statistical summary visualization.

        Parameters
        ----------
        save_path : str
            Path to save the figure
        """
        fig, ax = plt.subplots(figsize=(12, 10))
        ax.axis('off')

        bootstrap_results = self.stats_results['bootstrap']
        permutation_results = self.stats_results['permutation']
        effect_results = self.stats_results['effect_sizes']

        summary_text = f"""
╔══════════════════════════════════════════════════════════════════════╗
║         GOLDEN RATIO STATISTICAL ANALYSIS SUMMARY                    ║
╚══════════════════════════════════════════════════════════════════════╝

GOLDEN RATIO CONSTANT
  φ (phi) = {self.phi:.10f}

DATASET STATISTICS
  Total samples: {self.latent_codes.shape[0]}
  Latent dimensions: {self.latent_codes.shape[1]}
  Total dimension pairs tested: {self.latent_codes.shape[1] * (self.latent_codes.shape[1]-1) // 2}
  Total ratio measurements: {len(self.ratios)}

BOOTSTRAP THRESHOLD ESTIMATION
  Recommended threshold: {bootstrap_results['threshold']:.4f}
  Mean proximity to φ: {bootstrap_results['mean_proximity']:.4f}
  Std proximity: {bootstrap_results['std_proximity']:.4f}
  95% CI: [{bootstrap_results['ci_lower']:.4f}, {bootstrap_results['ci_upper']:.4f}]

RATIO DISTRIBUTION STATISTICS
  Mean ratio: {np.mean(self.ratios):.4f}
  Median ratio: {np.median(self.ratios):.4f}
  Std ratio: {np.std(self.ratios):.4f}
  Within threshold: {np.sum(np.abs(self.ratios - self.phi) < bootstrap_results['threshold'])} ({100*np.sum(np.abs(self.ratios - self.phi) < bootstrap_results['threshold'])/len(self.ratios):.1f}%)
  Within 0.1: {np.sum(np.abs(self.ratios - self.phi) < 0.1)} ({100*np.sum(np.abs(self.ratios - self.phi) < 0.1)/len(self.ratios):.1f}%)
  Within 0.05: {np.sum(np.abs(self.ratios - self.phi) < 0.05)} ({100*np.sum(np.abs(self.ratios - self.phi) < 0.05)/len(self.ratios):.1f}%)

PERMUTATION TEST RESULTS
  p-value: {permutation_results['p_value']:.4f} {"***" if permutation_results['p_value'] < 0.001 else "**" if permutation_results['p_value'] < 0.01 else "*" if permutation_results['p_value'] < 0.05 else "ns"}
  Observed statistic: {permutation_results['observed_stat']:.4f}
  Null mean: {permutation_results['null_mean']:.4f}
  z-score: {permutation_results['z_score']:.2f}
  Result: {"SIGNIFICANT (H0 rejected)" if permutation_results['is_significant'] else "NOT SIGNIFICANT (H0 retained)"}

EFFECT SIZE ANALYSIS
  Cohen's d: {effect_results['cohens_d']:.3f} ({"small" if abs(effect_results['cohens_d']) < 0.5 else "medium" if abs(effect_results['cohens_d']) < 0.8 else "large"} effect)
  Odds ratio: {effect_results['odds_ratio']:.2f}
  Mean proximity (observed): {effect_results['mean_proximity']:.4f}
  Mean proximity (random): {effect_results['random_mean_proximity']:.4f}
  Improvement over random: {(1 - effect_results['mean_proximity']/effect_results['random_mean_proximity'])*100:.1f}%

CONCLUSION
  {'✓ SIGNIFICANT GOLDEN RATIO PATTERNS DETECTED' if self.stats_results['conclusion'] == 'significant' else '✗ NO SIGNIFICANT GOLDEN RATIO PATTERNS'}
  {'  Strong evidence for φ-based optimization in consciousness' if self.stats_results['conclusion'] == 'significant' else '  Patterns consistent with random distribution'}

INTERPRETATION
  {"The data shows statistically significant clustering of dimension ratios" if self.stats_results['conclusion'] == 'significant' else "The data does not show significant golden ratio patterns beyond"}
  {"around the golden ratio (φ = 1.618), with large effect size." if self.stats_results['conclusion'] == 'significant' else "random expectations. Alternative hypotheses should be explored."}
  {"This suggests consciousness representations may follow φ-based" if self.stats_results['conclusion'] == 'significant' else ""}
  {"optimization principles similar to phyllotaxis patterns in nature." if self.stats_results['conclusion'] == 'significant' else ""}

╚══════════════════════════════════════════════════════════════════════╝
"""

        ax.text(0.05, 0.95, summary_text, fontsize=10, family='monospace',
               verticalalignment='top', transform=ax.transAxes)

        plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"Summary visualization saved to: {save_path}")

        return fig


def plot_quick_summary(latent_codes: np.ndarray, statistical_results: Dict,
                       save_path: str = 'golden_ratio_quick.png'):
    """
    Create a quick 2x2 summary plot.

    Parameters
    ----------
    latent_codes : ndarray
        Latent representations
    statistical_results : dict
        Results from statistical analysis
    save_path : str
        Path to save figure
    """
    visualizer = GoldenRatioVisualizer(latent_codes, statistical_results)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Golden Ratio Quick Summary', fontsize=16, fontweight='bold')

    bootstrap_results = statistical_results['bootstrap']
    permutation_results = statistical_results['permutation']

    # Panel 1: Histogram
    visualizer._plot_histogram_with_ci(axes[0, 0], bootstrap_results)

    # Panel 2: KDE
    visualizer._plot_kde_with_envelope(axes[0, 1])

    # Panel 3: Proximity bins
    visualizer._plot_proximity_bins(axes[1, 0])

    # Panel 4: Permutation results
    visualizer._plot_permutation_results(axes[1, 1], permutation_results)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"Quick summary saved to: {save_path}")

    return fig
