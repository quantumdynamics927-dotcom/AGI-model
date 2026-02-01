"""
Lightweight scaffold to compute hydrogenic wavefunctions on a 2D grid slice.
This script uses NumPy and SciPy (if available) and keeps imports lazy.
Enhanced with visualization for recommended states.
"""
import numpy as np
from math import factorial

# Lazily import scipy.special if available
try:
    from scipy.special import sph_harm, assoc_laguerre
    SCIPY_AVAILABLE = True
except Exception:
    SCIPY_AVAILABLE = False

# Import matplotlib for visualization
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except Exception:
    MATPLOTLIB_AVAILABLE = False

PHI = (1 + 5 ** 0.5) / 2


def radial_wavefunc(n, l, r, a0=1.0):
    """Compute radial part R_{n,l}(r) for hydrogen-like atom (atomic units, a0=1 by default).
    Uses associated Laguerre polynomials; when SciPy not available uses simple approximations for n<=2.
    """
    if SCIPY_AVAILABLE:
        rho = 2.0 * r / (n * a0)
        # Normalization constant (atomic units)
        prefac = (2.0 / (n * a0)) ** 3 * factorial(n - l - 1) / (2.0 * n * factorial(n + l))
        prefac = np.sqrt(prefac)
        # Associated Laguerre L^{2l+1}_{n-l-1}(rho)
        L = assoc_laguerre(rho, n - l - 1, 2 * l + 1)
        R = prefac * np.exp(-rho / 2.0) * rho ** l * L
        return R
    else:
        # fallback approximate forms
        if n == 1 and l == 0:
            return 2.0 * np.exp(-r)
        if n == 2 and l == 0:
            return (1.0 / 2.0) * (2.0 - r) * np.exp(-r / 2.0)
        # generic fallback
        return np.exp(-r / n)


def hydrogen_wavefunction(n=1, l=0, m=0, grid_size=200, extent=20.0):
    """Compute wavefunction psi on a 2D xy-grid at z=0 slice for visualization.
    Returns (X, Y, psi_real, prob_density)
    """
    x = np.linspace(-extent, extent, grid_size)
    y = np.linspace(-extent, extent, grid_size)
    X, Y = np.meshgrid(x, y)
    Z = np.zeros_like(X)
    r = np.sqrt(X ** 2 + Y ** 2 + Z ** 2)

    # Angular part using spherical harmonics when available
    if SCIPY_AVAILABLE:
        # theta, phi for z=0 plane
        theta = np.arccos(np.where(r == 0, 1.0, Z / (r + 1e-12)))
        phi = np.arctan2(Y, X)
        Y_lm = sph_harm(m, l, phi, theta)
        R = radial_wavefunc(n, l, r)
        psi = R * Y_lm
        psi_real = np.real(psi)
        prob = np.abs(psi) ** 2
    else:
        R = radial_wavefunc(n, l, r)
        # approximate angular factor
        psi_real = R * np.cos(m * np.arctan2(Y, X))
        prob = psi_real ** 2

    return X, Y, psi_real, prob


def visualize_state(n, l, m, grid_size=200, extent=20.0, save_path=None):
    """Compute and visualize a hydrogen wavefunction state at z=0 slice."""
    if not MATPLOTLIB_AVAILABLE:
        print("Matplotlib not available, skipping visualization.")
        return

    X, Y, psi_real, prob = hydrogen_wavefunction(n, l, m, grid_size, extent)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Plot real part
    im1 = axes[0].imshow(psi_real, extent=[-extent, extent, -extent, extent], origin='lower', cmap='RdYlBu')
    axes[0].set_title(f'Real Part: n={n}, l={l}, m={m}')
    axes[0].set_xlabel('x')
    axes[0].set_ylabel('y')
    plt.colorbar(im1, ax=axes[0])

    # Plot probability density
    im2 = axes[1].imshow(prob, extent=[-extent, extent, -extent, extent], origin='lower', cmap='viridis')
    axes[1].set_title(f'Probability Density: n={n}, l={l}, m={m}')
    axes[1].set_xlabel('x')
    axes[1].set_ylabel('y')
    plt.colorbar(im2, ax=axes[1])

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved visualization to {save_path}")
    else:
        plt.show()


def export_for_threejs(n, l, m, grid_size=100, extent=10.0, json_path=None):
    """Export wavefunction data as JSON for Three.js visualization."""
    X, Y, psi_real, prob = hydrogen_wavefunction(n, l, m, grid_size, extent)

    # Flatten for JSON
    data = {
        'n': n,
        'l': l,
        'm': m,
        'grid_size': grid_size,
        'extent': extent,
        'x': X.flatten().tolist(),
        'y': Y.flatten().tolist(),
        'psi_real': psi_real.flatten().tolist(),
        'prob_density': prob.flatten().tolist()
    }

    if json_path:
        import json
        with open(json_path, 'w') as f:
            json.dump(data, f)
        print(f"Exported data to {json_path}")
    return data


def generate_recommended_states():
    """Generate visualizations for recommended hydrogen states."""
    states = [
        # Best looking in equatorial plane
        (3, 2, 2, '3d_xy'),
        (3, 2, -2, '3d_x²-y²'),
        # Nodal structure visible
        (3, 1, 1, '3p_x'),
        (3, 1, -1, '3p_y'),
        # Almost rotationally symmetric
        (1, 0, 0, '1s'),
        (2, 0, 0, '2s'),
        (3, 0, 0, '3s'),
        (3, 2, 0, '3d_z²'),
        # Higher n for richer radial nodes
        (4, 0, 0, '4s'),
        (5, 0, 0, '5s'),
        (6, 0, 0, '6s'),
        (7, 0, 0, '7s'),
    ]

    for n, l, m, name in states:
        if MATPLOTLIB_AVAILABLE:
            save_path = f'hydrogen_{name}.png'
            visualize_state(n, l, m, save_path=save_path)
        json_path = f'../web_ui/public/hydrogen_{name}.json'
        export_for_threejs(n, l, m, json_path=json_path)


if __name__ == '__main__':
    # Quick CLI demonstration
    X, Y, psi_real, prob = hydrogen_wavefunction(n=1, l=0, m=0, grid_size=200, extent=20.0)
    # Save a small preview to disk
    np.savez_compressed('hydrogen_wave_1s.npz', X=X, Y=Y, psi=psi_real, prob=prob)
    print('Saved hydrogen_wave_1s.npz (1s slice)')

    # Generate visualizations for recommended states
    generate_recommended_states()
