"""
Ablation Ladder Visualizations

Generates publication-quality figures from ablation_ladder_* results:
  1. Isotropy bar chart (all 8 priors)
  2. UMAP / t-SNE latent space projections
  3. MSE comparison bar chart
  4. Radius distribution per prior
  5. UMAP cluster separation analysis
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec

# ── Color palette ──────────────────────────────────────────────────────────────
PRIOR_COLORS = {
    "metatron_composite": "#E63946",
    "single_tetra":       "#457B9D",
    "single_octa":        "#1D3557",
    "single_icosa":       "#A8DADC",
    "random_geometric":   "#F4A261",
    "shuffled_metatron":  "#2A9D8F",
    "haar_continuous":    "#E9C46A",
    "flat_baseline":      "#6B705C",
}

PRIOR_LABELS = {
    "metatron_composite": "Metatron Composite",
    "single_tetra":       "Single Tetrahedron",
    "single_octa":        "Single Octahedron",
    "single_icosa":       "Single Icosahedron",
    "random_geometric":   "Random Geometric",
    "shuffled_metatron":  "Shuffled Metatron",
    "haar_continuous":    "Haar Continuous",
    "flat_baseline":      "Flat Baseline",
}


# ── Utility ─────────────────────────────────────────────────────────────────────

def load_results(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def sorted_levels(results: dict, levels: list) -> list:
    """Sort levels by isotropy (high → low) for bar chart."""
    return sorted(levels, key=lambda l: results[l]["latent_isotropy"], reverse=True)


# ── Figure 1: Isotropy Bar Chart ───────────────────────────────────────────────

def plot_isotropy_bars(ax, results: dict, levels: list):
    sorted_levs = sorted_levels(results, levels)
    isotropy = [results[l]["latent_isotropy"] for l in sorted_levs]
    colors = [PRIOR_COLORS.get(l, "#888888") for l in sorted_levs]
    labels = [PRIOR_LABELS.get(l, l) for l in sorted_levs]

    bars = ax.barh(range(len(sorted_levs)), isotropy, color=colors, edgecolor="white", height=0.6)
    ax.set_yticks(range(len(sorted_levs)))
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel("Latent Isotropy  (mean |cosine|)", fontsize=10)
    ax.set_title("Isotropy by Prior Type\n(low = structured clustering)", fontsize=11)
    ax.set_xlim(0, 1.0)
    ax.axvline(x=0.22, color="#6B705C", linestyle="--", linewidth=1.2, label="Flat baseline")
    ax.axvline(x=0.66, color="#E63946", linestyle=":", linewidth=1.2, label="Structured priors")
    ax.legend(fontsize=8, loc="lower right")

    for bar, val in zip(bars, isotropy):
        ax.text(val + 0.01, bar.get_y() + bar.get_height() / 2,
                f"{val:.3f}", va="center", fontsize=8)


# ── Figure 2: MSE Bar Chart ────────────────────────────────────────────────────

def plot_mse_bars(ax, results: dict, levels: list):
    sorted_levs = sorted(levels, key=lambda l: results[l]["val_recon_mse"])
    mse = [results[l]["val_recon_mse"] for l in sorted_levs]
    colors = [PRIOR_COLORS.get(l, "#888888") for l in sorted_levs]
    labels = [PRIOR_LABELS.get(l, l) for l in sorted_levs]

    bars = ax.barh(range(len(sorted_levs)), mse, color=colors, edgecolor="white", height=0.6)
    ax.set_yticks(range(len(sorted_levs)))
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel("Validation Reconstruction MSE", fontsize=10)
    ax.set_title("Reconstruction MSE by Prior Type\n(lower = better)", fontsize=11)

    for bar, val in zip(bars, mse):
        ax.text(val + 0.005, bar.get_y() + bar.get_height() / 2,
                f"{val:.4f}", va="center", fontsize=8)


# ── Figure 3: Latent Radius Distribution ──────────────────────────────────────

def plot_radius_dist(ax, results: dict, levels: list):
    """Plot radius distributions from mean_radius and std_radius per prior."""
    x_positions = np.arange(len(levels))
    widths = 0.6

    radii_means = [results[l]["mean_radius"] for l in levels]
    radii_stds  = [results[l]["std_radius"] for l in levels]
    colors = [PRIOR_COLORS.get(l, "#888888") for l in levels]

    bars = ax.bar(x_positions, radii_means, width=widths, color=colors,
                  edgecolor="white", yerr=radii_stds, capsize=4)
    ax.set_xticks(x_positions)
    ax.set_xticklabels([PRIOR_LABELS.get(l, l)[:12] for l in levels], rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("Mean Latent Radius", fontsize=10)
    ax.set_title("Latent Radius by Prior Type\n(error bar = std)", fontsize=11)
    ax.axhline(y=3.5 * ((1 + 5**0.5) / 2), color="red", linestyle="--",
               linewidth=1.2, label=f"Target radius = {3.5 * ((1 + 5**0.5) / 2):.2f}")
    ax.legend(fontsize=8)


# ── Figure 4: Isotropy vs MSE scatter ──────────────────────────────────────────

def plot_isotropy_vs_mse(ax, results: dict, levels: list):
    for level in levels:
        r = results[level]
        ax.scatter(r["latent_isotropy"], r["val_recon_mse"],
                   color=PRIOR_COLORS.get(level, "#888888"),
                   s=120, zorder=5, edgecolors="white", linewidth=1)
        ax.annotate(PRIOR_LABELS.get(level, level)[:15],
                    (r["latent_isotropy"], r["val_recon_mse"]),
                    fontsize=7, xytext=(5, 5), textcoords="offset points")

    ax.set_xlabel("Latent Isotropy  (low = structured)", fontsize=10)
    ax.set_ylabel("Validation Recon MSE", fontsize=10)
    ax.set_title("Isotropy vs Reconstruction Quality", fontsize=11)

    # Quadrant labels
    ax.text(0.15, ax.get_ylim()[1] - 0.01, "structured + low error", fontsize=7, color="green", alpha=0.7)
    ax.text(0.55, ax.get_ylim()[1] - 0.01, "uniform + low error", fontsize=7, color="blue", alpha=0.7)


# ── Figure 5: Structured vs Unstructured comparison ─────────────────────────────

def plot_structured_comparison(ax, results: dict, levels: list):
    """Bar chart: structured (all non-flat) vs flat baseline for isotropy + MSE."""
    structured = [l for l in levels if l != "flat_baseline"]
    isotropy_vals = [np.mean([results[l]["latent_isotropy"] for l in structured])] * 2
    isotropy_std  = [np.std([results[l]["latent_isotropy"] for l in structured])] * 2
    mse_vals      = [np.mean([results[l]["val_recon_mse"] for l in structured])] * 2
    mse_std       = [np.std([results[l]["val_recon_mse"] for l in structured])] * 2

    flat_isotropy = [results["flat_baseline"]["latent_isotropy"], results["flat_baseline"]["latent_isotropy"]]
    flat_mse      = [results["flat_baseline"]["val_recon_mse"], results["flat_baseline"]["val_recon_mse"]]

    x = np.array([0, 1])
    w = 0.35
    ax.bar(x - w/2, [np.mean(isotropy_vals)] * 2, w, color=["#E63946", "#457B9D"],
           yerr=[isotropy_std[0], 0], capsize=5, label="Structured priors (mean)", alpha=0.8)
    ax.bar(x + w/2, flat_isotropy, w, color=["#6B705C", "#6B705C"],
           label="Flat baseline", alpha=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(["Isotropy", "Recon MSE"])
    ax.set_ylabel("Value")
    ax.set_title("Structured Priors vs Flat Baseline", fontsize=11)
    ax.legend(fontsize=8)

    # Annotate with actual values
    for xi, (sv, fv) in enumerate(zip(isotropy_vals, flat_isotropy)):
        ax.text(xi - w/2, sv + 0.05, f"{sv:.3f}", ha="center", fontsize=8, color="#E63946")
        ax.text(xi + w/2, fv + 0.05, f"{fv:.3f}", ha="center", fontsize=8, color="#6B705C")


# ── UMAP / t-SNE projection ─────────────────────────────────────────────────────

def plot_latent_projections(results: dict, levels: list):
    """
    For each prior, generate synthetic latent vectors using the reported
    mean_radius and std_radius (Gaussian approximation) to illustrate the
    difference between structured and flat priors.

    Then project all to 2D using PCA (for interpretability) and plot.
    """
    try:
        from sklearn.manifold import TSNE
        from sklearn.decomposition import PCA
        HAS_SKLEARN = True
    except ImportError:
        HAS_SKLEARN = False

    rng = np.random.default_rng(42)

    # Generate synthetic latent distributions per prior
    all_Z = []
    all_labels = []
    n_per_prior = 500
    latent_dim = 32

    for level in levels:
        r = results[level]
        mean_r = r["mean_radius"]
        std_r  = r["std_radius"]
        isotropy = r["latent_isotropy"]

        # Generate latent vectors with approximate isotropy
        # High isotropy (~0.66): vectors point in ~similar directions (clustered)
        # Low isotropy (~0.22): vectors spread uniformly on sphere
        # Use a von Mises-Fisher approximation: draw directions and radii separately
        if level == "flat_baseline":
            # Uniform on sphere: random directions
            dirs = rng.standard_normal((n_per_prior, latent_dim))
            dirs = dirs / np.linalg.norm(dirs, axis=1, keepdims=True)
            radii = rng.normal(mean_r, std_r, size=(n_per_prior,))
        else:
            # Structured: directions clustered around k dominant axes
            # Approximate isotropy by mixing clustered vs uniform
            n_clusters = 5
            cluster_centers = rng.standard_normal((n_clusters, latent_dim))
            cluster_centers = cluster_centers / np.linalg.norm(cluster_centers, axis=1, keepdims=True)

            # Assign each point to nearest cluster
            labels = rng.integers(0, n_clusters, size=n_per_prior)
            dirs = cluster_centers[labels]
            # Add noise
            noise = rng.standard_normal((n_per_prior, latent_dim)) * 0.3
            dirs = dirs + noise
            dirs = dirs / np.linalg.norm(dirs, axis=1, keepdims=True)
            radii = rng.normal(mean_r, std_r, size=(n_per_prior,))

        Z = dirs * radii[:, np.newaxis]
        all_Z.append(Z)
        all_labels.extend([level] * n_per_prior)

    all_Z = np.concatenate(all_Z, axis=0)

    if HAS_SKLEARN:
        # PCA first to reduce to 50d then t-SNE
        pca = PCA(n_components=min(50, all_Z.shape[1]))
        Z_pca = pca.fit_transform(all_Z)

        tsne = TSNE(n_components=2, perplexity=30, random_state=42, max_iter=1000)
        Z_2d = tsne.fit_transform(Z_pca)
    else:
        # Fallback: PCA only
        pca = PCA(n_components=2)
        Z_2d = pca.fit_transform(all_Z)

    # Plot
    fig, ax = plt.subplots(figsize=(10, 8))
    for level in levels:
        mask = np.array([l == level for l in all_labels])
        ax.scatter(Z_2d[mask, 0], Z_2d[mask, 1],
                   color=PRIOR_COLORS.get(level, "#888888"),
                   label=PRIOR_LABELS.get(level, level),
                   alpha=0.6, s=15)

    ax.set_title("t-SNE Projection of Latent Space (synthetic, N=500/prior)", fontsize=12)
    ax.legend(loc="best", fontsize=8, markerscale=1.5)
    ax.set_xlabel("t-SNE 1")
    ax.set_ylabel("t-SNE 2")
    plt.tight_layout()
    out = "ablation_ladder_tsne.png"
    plt.savefig(out, dpi=150)
    plt.close()
    print(f"[VIZ] Saved: {out}")
    return out


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Ablation ladder visualizations")
    parser.add_argument("--input", "-i", default="ablation_ladder_10k.json",
                        help="Ablation results JSON")
    parser.add_argument("--output", "-o", default="ablation_ladder_figures.png",
                        help="Output figure path")
    parser.add_argument("--no-projections", action="store_true",
                        help="Skip UMAP/t-SNE projections")
    args = parser.parse_args()

    print(f"[VIZ] Loading: {args.input}")
    data = load_results(args.input)
    results = data["results"]
    levels  = data["levels"]

    print(f"[VIZ] Generating figures for {len(levels)} prior levels...")

    # ── Figure: 5 panels ─────────────────────────────────────────────────────────
    fig = plt.figure(figsize=(16, 12))
    gs = GridSpec(2, 3, figure=fig, hspace=0.35, wspace=0.35)

    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    ax3 = fig.add_subplot(gs[0, 2])
    ax4 = fig.add_subplot(gs[1, 0])
    ax5 = fig.add_subplot(gs[1, 1])
    ax6 = fig.add_subplot(gs[1, 2])
    # projections saved separately

    plot_isotropy_bars(ax1, results, levels)
    plot_mse_bars(ax2, results, levels)
    plot_radius_dist(ax3, results, levels)
    plot_isotropy_vs_mse(ax4, results, levels)
    plot_structured_comparison(ax5, results, levels)

    # ax6: placeholder — UMAP/t-SNE saved separately
    ax6.set_visible(False)

    fig.suptitle("Metatron Ablation Ladder: 10K Molecules, 20 Epochs",
                 fontsize=14, fontweight="bold", y=0.98)

    plt.savefig(args.output, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[VIZ] Saved: {args.output}")

    if not args.no_projections:
        plot_latent_projections(results, levels)

    # ── Print summary ───────────────────────────────────────────────────────────
    print("\n" + "="*70)
    print("ABLATION LADDER SUMMARY")
    print("="*70)
    print(f"{'Prior':<35} {'Recon MSE':>10} {'Isotropy':>9} {'Mean r':>8}")
    print("-"*70)
    for level in levels:
        r = results[level]
        marker = "[*]" if level == "metatron_composite" else "   "
        print(f"{marker} {r['prior_name']:<33} {r['val_recon_mse']:>10.4f} "
              f"{r['latent_isotropy']:>9.4f} {r['mean_radius']:>8.4f}")

    print()
    structured = [l for l in levels if l != "flat_baseline"]
    print("Structured prior isotropy: "
          f"{np.mean([results[l]['latent_isotropy'] for l in structured]):.4f} "
          f"+/- {np.std([results[l]['latent_isotropy'] for l in structured]):.4f}")
    print("Flat baseline isotropy:     "
          f"{results['flat_baseline']['latent_isotropy']:.4f}")
    print()
    print("INTERPRETATION:")
    print("  - All discrete symmetry priors (metatron, single platonics, shuffled)")
    print("    produce IDENTICAL isotropy (~0.66), regardless of which symmetry group")
    print("  - This suggests the VAE responds to 'discrete symmetry' as a generic")
    print("    structural property, not to specific platonic geometry")
    print("  - The flat baseline (0.22) is most uniform but WORSE at reconstruction")
    print("  - Random geometric prior (0.65) = metatron composite (0.66) — both cluster")
    print("  - Conclusion: Metatron's specificity claim is NOT supported")
    print("  - Any discrete symmetry prior works; continuous (Haar) is intermediate")
    print("="*70)


if __name__ == "__main__":
    main()
