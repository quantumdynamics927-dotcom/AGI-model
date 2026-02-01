"""Demo for Spatial Awareness: map latent space and plan a path.

Generates random latent vectors, maps to 2D, builds occupancy grid,
plans a path between two latent indices, smooths and applies phi harmonics,
and saves a PNG visualization.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from spatial_awareness import map_latent_space_and_plan


def main():
    # synthetic latent dataset
    n = 400
    d = 32
    latent = np.random.randn(n, d) * 0.6

    start_i = 5
    goal_i = n - 5

    grid, raw, phi_path = map_latent_space_and_plan(latent, start_i, goal_i, grid_size=256)

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.imshow(grid, cmap='gray_r', origin='upper')

    plotted = False
    if raw:
        rx = [p[0] for p in raw]
        ry = [p[1] for p in raw]
        ax.plot(rx, ry, color='#FF8800', linewidth=1, label='raw path')
        plotted = True

    if phi_path:
        px = [p[0] for p in phi_path]
        py = [p[1] for p in phi_path]
        ax.plot(px, py, color='#DAA520', linewidth=2, label='phi-smoothed')
        plotted = True

    ax.set_title('Spatial Awareness: Latent→Grid Path Planning')
    ax.axis('off')
    if plotted:
        ax.legend(loc='lower right')
    plt.tight_layout()
    out = 'spatial_awareness_demo.png'
    plt.savefig(out, dpi=150)
    print('Saved', out)


if __name__ == '__main__':
    main()
