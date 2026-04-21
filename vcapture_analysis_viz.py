#!/usr/bin/env python3
"""
VCapture Analysis Visualization Module
=====================================

Generates publication-quality visualizations for VCapture measurement ledger:
1. Within-promoter variance plots (replicate stability)
2. Between-promoter separation heatmaps
3. Residual distribution comparisons
4. Cross-backend transferability plots
5. Mixed-effects variance decomposition

Usage:
    python vcapture_analysis_viz.py --report raw_hardware/vcapture_ledger_report.json
"""

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Any, Optional

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Headless
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import seaborn as sns


# ─────────────────────────────────────────────────────────────────────────────
# STYLE CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.size': 10,
    'axes.titlesize': 12,
    'axes.labelsize': 11,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.titlesize': 14,
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'axes.grid': True,
    'grid.alpha': 0.3,
})

# Color palette
COLORS = {
    'ibm_fez': '#1f77b4',
    'ibm_kingston': '#ff7f0e',
    'promoter': '#2ca02c',
    'backend': '#d62728',
    'interaction': '#9467bd',
    'residual': '#8c564b',
}

PHI = 1.618033988749895  # Golden ratio


# ─────────────────────────────────────────────────────────────────────────────
# VISUALIZATION FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def plot_within_promoter_variance(report: Dict[str, Any], output_dir: Path):
    """
    Plot within-promoter variance across replicates.
    Shows measurement stability for each promoter.
    """
    variance = report.get('variance_structure', {})
    within_var = variance.get('within_promoter_variance', {})
    
    if not within_var:
        print("No within-promoter variance data available")
        return
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    promoters = list(within_var.keys())
    variances = [within_var[p] for p in promoters]
    
    # Convert to standard deviations for interpretability
    stds = [np.sqrt(v) for v in variances]
    
    x = np.arange(len(promoters))
    bars = ax.bar(x, stds, color=COLORS['promoter'], alpha=0.7, edgecolor='black')
    
    # Add mean line
    mean_std = np.mean(stds)
    ax.axhline(y=mean_std, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_std:.6f}')
    
    ax.set_xlabel('Promoter ID')
    ax.set_ylabel('Within-Promoter Std Dev (φ)')
    ax.set_title('Within-Promoter Variance: Replicate Stability')
    ax.set_xticks(x)
    ax.set_xticklabels(promoters, rotation=45, ha='right')
    ax.legend()
    
    # Add value labels
    for bar, std in zip(bars, stds):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.00001,
                f'{std:.6f}', ha='center', va='bottom', fontsize=8)
    
    plt.tight_layout()
    fig.savefig(output_dir / 'within_promoter_variance.png')
    plt.close(fig)
    print(f"Saved: {output_dir / 'within_promoter_variance.png'}")


def plot_between_promoter_separation(report: Dict[str, Any], output_dir: Path):
    """
    Plot between-promoter separation heatmap.
    Shows identity recoverability above noise.
    """
    variance = report.get('variance_structure', {})
    separation_matrix = variance.get('separation_matrix', {})
    
    if not separation_matrix:
        print("No separation matrix data available")
        return
    
    promoters = list(separation_matrix.keys())
    n = len(promoters)
    
    # Build matrix
    matrix = np.zeros((n, n))
    for i, p1 in enumerate(promoters):
        for j, p2 in enumerate(promoters):
            val = separation_matrix[p1].get(p2)
            matrix[i, j] = val if val is not None else 0
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Heatmap
    im = ax.imshow(matrix, cmap='RdYlGn_r', aspect='auto')
    
    # Labels
    ax.set_xticks(np.arange(n))
    ax.set_yticks(np.arange(n))
    ax.set_xticklabels(promoters, rotation=45, ha='right')
    ax.set_yticklabels(promoters)
    
    # Colorbar
    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label('Distance (φ units)')
    
    # Add values
    for i in range(n):
        for j in range(n):
            text = ax.text(j, i, f'{matrix[i, j]:.4f}',
                          ha='center', va='center', color='black' if matrix[i, j] < 0.001 else 'white',
                          fontsize=8)
    
    ax.set_title('Between-Promoter Separation Matrix\n(Calibrated φ)')
    ax.set_xlabel('Promoter')
    ax.set_ylabel('Promoter')
    
    plt.tight_layout()
    fig.savefig(output_dir / 'between_promoter_separation.png')
    plt.close(fig)
    print(f"Saved: {output_dir / 'between_promoter_separation.png'}")


def plot_residual_distributions(report: Dict[str, Any], output_dir: Path):
    """
    Plot residual distributions by backend.
    Shows calibration effectiveness.
    """
    variance = report.get('variance_structure', {})
    residual_dist = variance.get('residual_distribution', {})
    
    if not residual_dist:
        print("No residual distribution data available")
        return
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    backends = list(residual_dist.keys())
    
    # Left: Box plot summary
    ax1 = axes[0]
    box_data = []
    labels = []
    for backend in backends:
        stats = residual_dist[backend]
        # Reconstruct approximate distribution from summary stats
        mean = stats.get('mean', 0)
        std = stats.get('std', 1)
        q25 = stats.get('q25', mean - std)
        q75 = stats.get('q75', mean + std)
        median = stats.get('median', mean)
        
        box_data.append([stats.get('min', q25), q25, median, q75, stats.get('max', q75)])
        labels.append(backend)
    
    bp = ax1.boxplot(box_data, labels=labels, patch_artist=True)
    for patch, backend in zip(bp['boxes'], backends):
        patch.set_facecolor(COLORS.get(backend, 'gray'))
        patch.set_alpha(0.7)
    
    ax1.axhline(y=0, color='black', linestyle='--', linewidth=1, label='Zero residual')
    ax1.set_xlabel('Backend')
    ax1.set_ylabel('Residual (φ)')
    ax1.set_title('Residual Distribution by Backend')
    ax1.legend()
    
    # Right: Before/After calibration comparison
    ax2 = axes[1]
    x = np.arange(len(backends))
    width = 0.35
    
    raw_means = [residual_dist[b].get('mean', 0) for b in backends]
    raw_stds = [residual_dist[b].get('std', 0) for b in backends]
    calibrated_means = [residual_dist[b].get('calibrated_mean', 0) or 0 for b in backends]
    calibrated_stds = [residual_dist[b].get('calibrated_std', 0) or 0 for b in backends]
    
    bars1 = ax2.bar(x - width/2, raw_means, width, yerr=raw_stds, 
                    label='Raw', color='red', alpha=0.7, capsize=5)
    bars2 = ax2.bar(x + width/2, calibrated_means, width, yerr=calibrated_stds,
                    label='Calibrated', color='green', alpha=0.7, capsize=5)
    
    ax2.axhline(y=0, color='black', linestyle='--', linewidth=1)
    ax2.set_xlabel('Backend')
    ax2.set_ylabel('Mean Residual (φ)')
    ax2.set_title('Calibration Effect: Residual Mean Shift')
    ax2.set_xticks(x)
    ax2.set_xticklabels(backends)
    ax2.legend()
    
    plt.tight_layout()
    fig.savefig(output_dir / 'residual_distributions.png')
    plt.close(fig)
    print(f"Saved: {output_dir / 'residual_distributions.png'}")


def plot_transferability(report: Dict[str, Any], output_dir: Path):
    """
    Plot cross-backend transferability results.
    Shows portability assessment.
    """
    transfer_reports = report.get('transferability', [])
    
    if not transfer_reports:
        print("No transferability data available")
        return
    
    n_reports = len(transfer_reports)
    fig, axes = plt.subplots(1, max(n_reports, 1), figsize=(5 * max(n_reports, 1), 5))
    
    # Ensure axes is always iterable
    if n_reports == 1:
        axes = [axes]
    
    for i, tr in enumerate(transfer_reports):
        source = tr.get('source_backend', 'unknown')
        target = tr.get('target_backend', 'unknown')
        
        # Create comparison bar chart
        ax = axes[i]
        
        metrics = ['Transfer\nEfficiency', 'Ranking\nCorrelation', 'Portability\nScore']
        values = [
            tr.get('transfer_efficiency', 0),
            abs(tr.get('promoter_ranking_correlation', 0)),
            tr.get('portability_score', 0),
        ]
        
        colors = ['green' if v >= 0.9 else 'orange' if v >= 0.7 else 'red' for v in values]
        
        bars = ax.bar(metrics, values, color=colors, alpha=0.7, edgecolor='black')
        
        # Add threshold line
        ax.axhline(y=0.9, color='green', linestyle='--', linewidth=2, label='Portability threshold (90%)')
        ax.axhline(y=0.8, color='orange', linestyle=':', linewidth=1, label='Marginal threshold (80%)')
        
        ax.set_ylim(0, 1.1)
        ax.set_ylabel('Score')
        ax.set_title(f'{source} → {target}\nPortable: {tr.get("is_portable", False)}')
        ax.legend(loc='lower right')
        
        # Add value labels
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                    f'{val:.1%}', ha='center', va='bottom', fontsize=10)
    
    plt.suptitle('Cross-Backend Transferability Assessment', fontsize=14, y=1.02)
    plt.tight_layout()
    fig.savefig(output_dir / 'transferability.png')
    plt.close(fig)
    print(f"Saved: {output_dir / 'transferability.png'}")


def plot_mixed_effects(report: Dict[str, Any], output_dir: Path):
    """
    Plot mixed-effects model variance decomposition.
    Shows identity, hardware, and interaction effects.
    """
    mixed = report.get('mixed_effects', {})
    
    if not mixed:
        print("No mixed-effects data available")
        return
    
    var_components = mixed.get('variance_components', {})
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Left: Variance components pie chart
    ax1 = axes[0]
    labels = ['Promoter\n(Identity)', 'Backend\n(Hardware)', 'Interaction', 'Residual']
    sizes = [
        var_components.get('promoter', 0),
        var_components.get('backend', 0),
        var_components.get('interaction', 0),
        var_components.get('residual', 0),
    ]
    
    # Filter out zero components
    non_zero = [(l, s) for l, s in zip(labels, sizes) if s > 0]
    if non_zero:
        labels_nz, sizes_nz = zip(*non_zero)
        colors = [COLORS['promoter'], COLORS['backend'], COLORS['interaction'], COLORS['residual']][:len(sizes_nz)]
        
        wedges, texts, autotexts = ax1.pie(sizes_nz, labels=labels_nz, colors=colors,
                                           autopct='%1.1f%%', startangle=90,
                                           explode=[0.02] * len(sizes_nz))
        ax1.set_title('Variance Components Decomposition')
    
    # Right: Model statistics
    ax2 = axes[1]
    model_stats = mixed.get('model_statistics', {})
    
    stats_labels = ['R²', 'Adjusted R²', 'F-statistic\n(normalized)']
    stats_values = [
        model_stats.get('r_squared', 0),
        model_stats.get('adjusted_r_squared', 0),
        min(model_stats.get('f_statistic', 0) / 100, 1.0),  # Normalize for display
    ]
    
    bars = ax2.bar(stats_labels, stats_values, color=['blue', 'purple', 'orange'], alpha=0.7, edgecolor='black')
    ax2.set_ylim(0, 1.1)
    ax2.set_ylabel('Value')
    ax2.set_title('Model Fit Statistics')
    
    # Add value labels
    for bar, val in zip(bars, stats_values):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f'{val:.3f}', ha='center', va='bottom', fontsize=10)
    
    # Add significance indicators
    sig = mixed.get('significance', {})
    sig_text = f"Promoter: {'✓' if sig.get('promoter_significant') else '✗'}\n"
    sig_text += f"Backend: {'✓' if sig.get('backend_significant') else '✗'}\n"
    sig_text += f"Interaction: {'✓' if sig.get('interaction_significant') else '✗'}"
    ax2.text(0.95, 0.05, sig_text, transform=ax2.transAxes, fontsize=10,
             verticalalignment='bottom', horizontalalignment='right',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    fig.savefig(output_dir / 'mixed_effects.png')
    plt.close(fig)
    print(f"Saved: {output_dir / 'mixed_effects.png'}")


def plot_promoter_backend_heatmap(report: Dict[str, Any], output_dir: Path):
    """
    Plot promoter-backend mean phi heatmap.
    Shows systematic patterns across experimental design.
    """
    summaries = report.get('variance_structure', {}).get('promoter_backend_summaries', [])
    
    if not summaries:
        print("No promoter-backend summary data available")
        return
    
    # Build matrix
    promoters = sorted(set(s['promoter_id'] for s in summaries))
    backends = sorted(set(s['backend'] for s in summaries))
    
    mean_matrix = np.zeros((len(promoters), len(backends)))
    std_matrix = np.zeros((len(promoters), len(backends)))
    
    for s in summaries:
        i = promoters.index(s['promoter_id'])
        j = backends.index(s['backend'])
        mean_matrix[i, j] = s['mean_measured_phi']
        std_matrix[i, j] = s['std_measured_phi']
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 8))
    
    # Left: Mean phi
    ax1 = axes[0]
    im1 = ax1.imshow(mean_matrix, cmap='viridis', aspect='auto')
    ax1.set_xticks(np.arange(len(backends)))
    ax1.set_yticks(np.arange(len(promoters)))
    ax1.set_xticklabels(backends, rotation=45, ha='right')
    ax1.set_yticklabels(promoters)
    ax1.set_xlabel('Backend')
    ax1.set_ylabel('Promoter')
    ax1.set_title('Mean Measured φ')
    
    # Add values
    for i in range(len(promoters)):
        for j in range(len(backends)):
            ax1.text(j, i, f'{mean_matrix[i, j]:.4f}',
                    ha='center', va='center', color='white' if mean_matrix[i, j] < mean_matrix.mean() else 'black',
                    fontsize=9)
    
    cbar1 = plt.colorbar(im1, ax=ax1, shrink=0.8)
    cbar1.set_label('φ value')
    
    # Right: Std phi
    ax2 = axes[1]
    im2 = ax2.imshow(std_matrix, cmap='RdYlGn_r', aspect='auto')
    ax2.set_xticks(np.arange(len(backends)))
    ax2.set_yticks(np.arange(len(promoters)))
    ax2.set_xticklabels(backends, rotation=45, ha='right')
    ax2.set_yticklabels(promoters)
    ax2.set_xlabel('Backend')
    ax2.set_ylabel('Promoter')
    ax2.set_title('Std Dev (Replicate Variability)')
    
    # Add values
    for i in range(len(promoters)):
        for j in range(len(backends)):
            ax2.text(j, i, f'{std_matrix[i, j]:.6f}',
                    ha='center', va='center', color='black',
                    fontsize=8)
    
    cbar2 = plt.colorbar(im2, ax=ax2, shrink=0.8)
    cbar2.set_label('Std Dev')
    
    plt.suptitle('Promoter-Backend Experimental Matrix', fontsize=14, y=1.02)
    plt.tight_layout()
    fig.savefig(output_dir / 'promoter_backend_heatmap.png')
    plt.close(fig)
    print(f"Saved: {output_dir / 'promoter_backend_heatmap.png'}")


def plot_signal_to_separation(report: Dict[str, Any], output_dir: Path):
    """
    Plot signal-to-separation statistics.
    Shows whether promoter identity is recoverable above noise.
    """
    summaries = report.get('variance_structure', {}).get('promoter_backend_summaries', [])
    
    if not summaries:
        print("No signal-to-separation data available")
        return
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Group by promoter
    promoters = sorted(set(s['promoter_id'] for s in summaries))
    backends = sorted(set(s['backend'] for s in summaries))
    
    x = np.arange(len(promoters))
    width = 0.35
    
    for i, backend in enumerate(backends):
        backend_summaries = [s for s in summaries if s['backend'] == backend]
        s_s_values = []
        for p in promoters:
            matching = [s for s in backend_summaries if s['promoter_id'] == p]
            s_s_values.append(matching[0]['signal_to_separation'] if matching else 0)
        
        offset = width * (i - len(backends)/2 + 0.5)
        bars = ax.bar(x + offset, s_s_values, width, label=backend,
                     color=COLORS.get(backend, 'gray'), alpha=0.7, edgecolor='black')
    
    # Add threshold line
    ax.axhline(y=2.0, color='red', linestyle='--', linewidth=2, label='Detection threshold (S/S ≥ 2)')
    ax.axhline(y=3.0, color='green', linestyle='--', linewidth=2, label='Strong separation (S/S ≥ 3)')
    
    ax.set_xlabel('Promoter')
    ax.set_ylabel('Signal-to-Separation Ratio')
    ax.set_title('Promoter Identity Recoverability\n(Distance to Nearest Promoter / Pooled Std)')
    ax.set_xticks(x)
    ax.set_xticklabels(promoters, rotation=45, ha='right')
    ax.legend(loc='upper right')
    
    plt.tight_layout()
    fig.savefig(output_dir / 'signal_to_separation.png')
    plt.close(fig)
    print(f"Saved: {output_dir / 'signal_to_separation.png'}")


def generate_summary_dashboard(report: Dict[str, Any], output_dir: Path):
    """
    Generate comprehensive summary dashboard.
    """
    fig = plt.figure(figsize=(20, 16))
    gs = GridSpec(3, 3, figure=fig, hspace=0.3, wspace=0.3)
    
    # 1. Metadata summary (top-left)
    ax1 = fig.add_subplot(gs[0, 0])
    metadata = report.get('metadata', {})
    meta_text = f"Total Records: {metadata.get('total_records', 0)}\n"
    meta_text += f"Unique Promoters: {metadata.get('unique_promoters', 0)}\n"
    meta_text += f"Unique Backends: {metadata.get('unique_backends', 0)}\n"
    meta_text += f"Calibration Version: {metadata.get('calibration_version', 'N/A')}\n"
    meta_text += f"Offset Model Version: {metadata.get('offset_model_version', 'N/A')}"
    ax1.text(0.1, 0.5, meta_text, fontsize=12, verticalalignment='center',
             family='monospace', transform=ax1.transAxes)
    ax1.axis('off')
    ax1.set_title('Dataset Summary', fontsize=12, fontweight='bold')
    
    # 2. Variance summary (top-center)
    ax2 = fig.add_subplot(gs[0, 1])
    variance = report.get('variance_structure', {})
    var_text = f"Within-Promoter Variance:\n  Mean: {variance.get('within_promoter_mean', 0):.2e}\n  Std: {variance.get('within_promoter_std', 0):.2e}\n\n"
    var_text += f"Between-Promoter Variance:\n  Mean: {variance.get('between_promoter_mean', 0):.2e}\n  Std: {variance.get('between_promoter_std', 0):.2e}\n\n"
    var_text += f"Residual:\n  Mean: {variance.get('residual_mean', 0):.4f}\n  Std: {variance.get('residual_std', 0):.4f}"
    ax2.text(0.1, 0.5, var_text, fontsize=10, verticalalignment='center',
             family='monospace', transform=ax2.transAxes)
    ax2.axis('off')
    ax2.set_title('Variance Structure', fontsize=12, fontweight='bold')
    
    # 3. Transferability summary (top-right)
    ax3 = fig.add_subplot(gs[0, 2])
    transfer = report.get('transferability', [])
    if transfer:
        tr = transfer[0]
        trans_text = f"Source: {tr.get('source_backend', 'N/A')}\n"
        trans_text += f"Target: {tr.get('target_backend', 'N/A')}\n\n"
        trans_text += f"Transfer Efficiency: {tr.get('transfer_efficiency', 0):.1%}\n"
        trans_text += f"Portability Score: {tr.get('portability_score', 0):.1%}\n\n"
        trans_text += f"Is Portable: {'✓ YES' if tr.get('is_portable') else '✗ NO'}\n\n"
        trans_text += f"Ranking Correlation: {tr.get('promoter_ranking_correlation', 0):.2f}"
        ax3.text(0.1, 0.5, trans_text, fontsize=10, verticalalignment='center',
                 family='monospace', transform=ax3.transAxes)
    ax3.axis('off')
    ax3.set_title('Transferability', fontsize=12, fontweight='bold')
    
    # 4. Within-promoter variance (middle-left)
    ax4 = fig.add_subplot(gs[1, 0])
    within_var = variance.get('within_promoter_variance', {})
    if within_var:
        promoters = list(within_var.keys())
        stds = [np.sqrt(within_var[p]) for p in promoters]
        ax4.bar(promoters, stds, color=COLORS['promoter'], alpha=0.7)
        ax4.axhline(y=np.mean(stds), color='red', linestyle='--')
        ax4.set_xlabel('Promoter')
        ax4.set_ylabel('Std Dev')
        ax4.set_title('Within-Promoter Variance')
        ax4.tick_params(axis='x', rotation=45)
    
    # 5. Separation heatmap (middle-center)
    ax5 = fig.add_subplot(gs[1, 1])
    separation_matrix = variance.get('separation_matrix', {})
    if separation_matrix:
        promoters = list(separation_matrix.keys())
        n = len(promoters)
        matrix = np.zeros((n, n))
        for i, p1 in enumerate(promoters):
            for j, p2 in enumerate(promoters):
                val = separation_matrix[p1].get(p2)
                matrix[i, j] = val if val is not None else 0
        im = ax5.imshow(matrix, cmap='RdYlGn_r')
        ax5.set_xticks(range(n))
        ax5.set_yticks(range(n))
        ax5.set_xticklabels(promoters, rotation=45, ha='right', fontsize=8)
        ax5.set_yticklabels(promoters, fontsize=8)
        ax5.set_title('Separation Matrix')
    
    # 6. Mixed-effects (middle-right)
    ax6 = fig.add_subplot(gs[1, 2])
    mixed = report.get('mixed_effects', {})
    var_comp = mixed.get('variance_components', {})
    if var_comp:
        labels = ['Promoter', 'Backend', 'Interaction', 'Residual']
        sizes = [var_comp.get('promoter', 0), var_comp.get('backend', 0),
                var_comp.get('interaction', 0), var_comp.get('residual', 0)]
        non_zero = [(l, s) for l, s in zip(labels, sizes) if s > 0]
        if non_zero:
            labels_nz, sizes_nz = zip(*non_zero)
            ax6.pie(sizes_nz, labels=labels_nz, autopct='%1.1f%%', startangle=90)
            ax6.set_title('Variance Components')
    
    # 7. Residual distribution (bottom-left)
    ax7 = fig.add_subplot(gs[2, 0])
    residual_dist = variance.get('residual_distribution', {})
    if residual_dist:
        backends = list(residual_dist.keys())
        means = [residual_dist[b].get('mean', 0) for b in backends]
        stds = [residual_dist[b].get('std', 0) for b in backends]
        ax7.bar(backends, means, yerr=stds, color=[COLORS.get(b, 'gray') for b in backends],
               alpha=0.7, capsize=5)
        ax7.axhline(y=0, color='black', linestyle='--')
        ax7.set_xlabel('Backend')
        ax7.set_ylabel('Mean Residual')
        ax7.set_title('Residual by Backend')
    
    # 8. Signal-to-separation (bottom-center)
    ax8 = fig.add_subplot(gs[2, 1])
    summaries = variance.get('promoter_backend_summaries', [])
    if summaries:
        promoters = sorted(set(s['promoter_id'] for s in summaries))
        for backend in sorted(set(s['backend'] for s in summaries)):
            backend_sums = [s for s in summaries if s['backend'] == backend]
            values = [next((s['signal_to_separation'] for s in backend_sums if s['promoter_id'] == p), 0) for p in promoters]
            ax8.plot(promoters, values, 'o-', label=backend, color=COLORS.get(backend, 'gray'))
        ax8.axhline(y=2.0, color='red', linestyle='--', label='Threshold')
        ax8.set_xlabel('Promoter')
        ax8.set_ylabel('S/S Ratio')
        ax8.set_title('Signal-to-Separation')
        ax8.legend(fontsize=8)
        ax8.tick_params(axis='x', rotation=45)
    
    # 9. Model fit (bottom-right)
    ax9 = fig.add_subplot(gs[2, 2])
    model_stats = mixed.get('model_statistics', {})
    if model_stats:
        stats = ['R²', 'Adj R²']
        values = [model_stats.get('r_squared', 0), model_stats.get('adjusted_r_squared', 0)]
        ax9.bar(stats, values, color=['blue', 'purple'], alpha=0.7)
        ax9.set_ylim(0, 1)
        ax9.set_ylabel('Value')
        ax9.set_title('Model Fit')
    
    fig.suptitle('VCapture Measurement Ledger Dashboard', fontsize=16, fontweight='bold', y=0.98)
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(output_dir / 'vcapture_dashboard.png')
    plt.close(fig)
    print(f"Saved: {output_dir / 'vcapture_dashboard.png'}")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="VCapture Analysis Visualization")
    parser.add_argument("--report", type=str, required=True, help="Path to VCapture ledger report JSON")
    parser.add_argument("--output-dir", type=str, default="vcapture_analysis", help="Output directory for plots")
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("VCapture Analysis Visualization")
    print("=" * 70)
    
    # Load report
    report_path = Path(args.report)
    with open(report_path, 'r', encoding='utf-8') as f:
        report = json.load(f)
    
    print(f"Loaded report: {report_path}")
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {output_dir}")
    
    # Generate all plots
    print("\nGenerating visualizations...")
    
    plot_within_promoter_variance(report, output_dir)
    plot_between_promoter_separation(report, output_dir)
    plot_residual_distributions(report, output_dir)
    plot_transferability(report, output_dir)
    plot_mixed_effects(report, output_dir)
    plot_promoter_backend_heatmap(report, output_dir)
    plot_signal_to_separation(report, output_dir)
    generate_summary_dashboard(report, output_dir)
    
    print("\n" + "=" * 70)
    print("Visualization complete!")
    print(f"All plots saved to: {output_dir}")


if __name__ == "__main__":
    main()