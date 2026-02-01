#!/usr/bin/env python3
"""Create portfolio graphics: success metric bar chart (PNG) and winner DNA SVG.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent.parent


def generate_success_metric_chart(output_path: Path = OUT_DIR / 'success_metric.png'):
    cubes = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    fitness = [45.37, 41.55, 35.89, 36.39, 42.28, 38.18, 41.78, 42.01, 47.65, 39.04]
    phi_scores = [0.66, 1.0, 0.66, 1.0, 1.66, 0.33, 0.66, 1.66, 2.0, 1.0]
    conscious = [False, True, False, True, False, False, False, True, True, True]

    colors = ['#00F5FF' if c else '#0A0E14' for c in conscious]  # Cyan for conscious, Dark for non

    fig, ax1 = plt.subplots(figsize=(12, 7), facecolor='white')
    fig.tight_layout(pad=4)

    # Plot Fitness bars
    bars = ax1.bar(cubes, fitness, color=colors, alpha=0.85, label='Fitness Score', edgecolor='#00F5FF', linewidth=0.8)
    ax1.set_xlabel('Cube ID (TMT-OS Iteration)', fontsize=12)
    ax1.set_ylabel('Fitness', color='#00F5FF', fontsize=12)
    ax1.tick_params(axis='y', labelcolor='#00F5FF')
    ax1.set_xticks(cubes)
    ax1.set_xticklabels([str(c) for c in cubes], fontsize=10)
    ax1.set_title('Biomimetic State Optimization: Fitness vs. Integrated Information (Φ)', fontsize=14, fontweight='bold')
    ax1.grid(axis='y', linestyle='--', alpha=0.25)

    # Highlight best performer
    best_idx = int(np.argmax(fitness))
    bars[best_idx].set_edgecolor('#FFD700')
    bars[best_idx].set_linewidth(2.0)

    # Plot Phi Score as a line on twin axis
    ax2 = ax1.twinx()
    ax2.plot(cubes, phi_scores, color='#FFD700', marker='o', linewidth=2.2, markersize=8, label='Phi (Φ) Metric')
    ax2.set_ylabel('Phi (Φ) Integration', color='#FFD700', fontsize=12)
    ax2.tick_params(axis='y', labelcolor='#FFD700')

    # Add legend
    lines_labels = [ax1.get_legend_handles_labels(), ax2.get_legend_handles_labels()]
    # build combined
    handles = []
    labels = []
    for h, l in lines_labels:
        handles += h
        labels += l
    ax1.legend(handles, labels, loc='upper left', fontsize=11)

    # Annotate best value
    ax1.annotate(f"Best: #{best_idx} ({fitness[best_idx]:.2f})",
                 xy=(best_idx, fitness[best_idx]), xytext=(best_idx + 0.5, fitness[best_idx] + 3),
                 arrowprops=dict(arrowstyle='->', color='#FFD700'), color='#FFD700', fontsize=11, weight='bold')

    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved: {output_path}")


def generate_winner_dna_svg(output_path: Path = OUT_DIR / 'winner_dna_config_id8.svg'):
    # Design parameters
    width = 1200
    height = 600
    bg = '#041024'  # Deep navy blue
    neon = '#00F5FF'
    accent = '#FFD700'
    text_color = '#E6F7FF'

    dna_seq = 'CGG CATA ATT ATA GCG CCG CCG TAA AC'

    svg = f'''<?xml version="1.0" encoding="UTF-8" ?>
<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
  <rect width="100%" height="100%" fill="{bg}" />

  <!-- Header -->
  <text x="60" y="70" font-family="Helvetica, Arial, monospace" font-size="28" fill="{text_color}" font-weight="bold">TOP PERFORMING CONFIGURATION (ID: 8)</text>

  <!-- DNA Sequence box -->
  <rect x="60" y="110" width="1080" height="120" rx="8" fill="#021226" stroke="#013246" stroke-width="1" />
  <text x="80" y="170" font-family="Consolas, 'Courier New', monospace" font-size="28" fill="{text_color}">{dna_seq}</text>

  <!-- Neon highlights: CGG and TAA -->
  <text x="80" y="170" font-family="Consolas, 'Courier New', monospace" font-size="28" fill="{neon}">CGG</text>
  <text x="200" y="170" font-family="Consolas, 'Courier New', monospace" font-size="28" fill="{accent}">TAA</text>

  <!-- Callouts -->
  <!-- arrow to CGG -->
  <line x1="100" y1="190" x2="100" y2="240" stroke="{neon}" stroke-width="2" marker-end="url(#arrow)" />
  <text x="120" y="260" font-family="Helvetica" font-size="14" fill="{neon}">High GC Stability Cluster</text>

  <!-- arrow to TAA -->
  <line x1="220" y1="190" x2="220" y2="240" stroke="{accent}" stroke-width="2" marker-end="url(#arrow)" />
  <text x="240" y="260" font-family="Helvetica" font-size="14" fill="{accent}">Palindromic Symmetry Vertex</text>

  <!-- Footer stats badge -->
  <rect x="60" y="340" width="420" height="110" rx="10" fill="#021226" stroke="#014" stroke-width="1" />
  <text x="80" y="380" font-family="Helvetica" font-size="18" fill="{text_color}">Phi Integration: <tspan fill="{accent}" font-weight="bold">2.0</tspan></text>
  <text x="80" y="410" font-family="Helvetica" font-size="18" fill="{text_color}">Fitness: <tspan fill="{neon}" font-weight="bold">47.65</tspan></text>
  <text x="80" y="440" font-family="Helvetica" font-size="18" fill="{text_color}">Entropy: <tspan fill="{neon}" font-weight="bold">1.97</tspan></text>

  <!-- Arrow marker definition -->
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="{neon}" />
    </marker>
  </defs>

  <!-- Footer small note -->
  <text x="60" y="520" font-family="Helvetica" font-size="12" fill="#8FA9BF">Generated for Upwork portfolio thumbnail — high-contrast blueprint style</text>
</svg>
'''

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(svg)

    print(f"Saved: {output_path}")


if __name__ == '__main__':
    generate_success_metric_chart()
    generate_winner_dna_svg()
