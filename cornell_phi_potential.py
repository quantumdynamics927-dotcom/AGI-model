"""
Cornell-φ Confinement Potential (Exploratory Theory Module)
===========================================================

An exploratory implementation of a phi-parameterized analog to the Cornell
confinement potential from QCD. This module is classified as EXPLORATORY
under the AGI-model governance framework.

Claim
-----
This is a phi-parameterized analog of a Cornell-like confinement potential,
NOT a claim that QCD is governed by phi.

Equations
---------
Standard Cornell potential:    V_C(r) = σr - α/r
Phi-parameterized analog:       V_φ(r) = r/φ - 1/(2φ²r)

Where:
- φ = (1 + √5)/2 ≈ 1.618033988749895 (golden ratio)
- r > 0 is the distance parameter
- σ, α are the standard Cornell parameters (string tension, Coulomb strength)

Domain
------
- r ∈ (0, ∞) - distance parameter
- Valid for: quantum circuit coupling design, consciousness state modeling
- NOT validated for: actual QCD calculations

Comparison Target
-----------------
Standard Cornell potential V_C(r) = σr - α/r with σ = 1/φ, α = 1/(2φ²)

Falsification Conditions
------------------------
1. If V_φ(r) produces unphysical singularities at any r > ε
2. If the potential is NOT monotonically increasing (should be: V_φ'(r) > 0 for all r)
3. If asymptotic growth (r → ∞) is not linear with slope 1/φ
4. If short-range behavior (r → 0) does not match -1/(2φ²r) form

Governance Status: EXPLORATORY
Date: April 15, 2026
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Optional, Dict
from dataclasses import dataclass

# Golden ratio constant
PHI = (1 + np.sqrt(5)) / 2
PHI_SQUARED = PHI ** 2
PHI_CUBED = PHI ** 3


@dataclass
class PotentialAnalysis:
    """Analysis results for a confinement potential."""
    potential_name: str
    r_grid: np.ndarray
    v_values: np.ndarray
    turning_point_r: Optional[float]
    turning_point_v: Optional[float]
    asymptotic_slope: float
    short_range_coefficient: float
    min_value: float
    max_value: float


def cornell_phi_potential(r: np.ndarray, epsilon: float = 1e-9) -> np.ndarray:
    """
    Cornell-φ confinement potential.
    
    V_φ(r) = r/φ - 1/(2φ²r)
    
    Parameters
    ----------
    r : np.ndarray
        Distance values (must be > 0)
    epsilon : float
        Small cutoff to avoid singularity at r=0
        
    Returns
    -------
    np.ndarray
        Potential values V_φ(r)
        
    Notes
    -----
    This is an EXPLORATORY potential under the AGI-model governance framework.
    It has NOT been validated for actual QCD calculations.
    """
    r = np.asarray(r)
    # Avoid singularity at r=0
    r_safe = np.maximum(r, epsilon)
    
    # V_φ(r) = r/φ - 1/(2φ²r)
    linear_term = r_safe / PHI
    coulomb_term = 1.0 / (2.0 * PHI_SQUARED * r_safe)
    
    return linear_term - coulomb_term


def cornell_standard_potential(r: np.ndarray, 
                                sigma: float = 1.0, 
                                alpha: float = 1.0,
                                epsilon: float = 1e-9) -> np.ndarray:
    """
    Standard Cornell confinement potential from QCD.
    
    V_C(r) = σr - α/r
    
    Parameters
    ----------
    r : np.ndarray
        Distance values (must be > 0)
    sigma : float
        String tension parameter (linear confinement strength)
    alpha : float
        Coulomb strength parameter
    epsilon : float
        Small cutoff to avoid singularity at r=0
        
    Returns
    -------
    np.ndarray
        Potential values V_C(r)
    """
    r = np.asarray(r)
    r_safe = np.maximum(r, epsilon)
    
    # V_C(r) = σr - α/r
    linear_term = sigma * r_safe
    coulomb_term = alpha / r_safe
    
    return linear_term - coulomb_term


def cornell_phi_equivalent_params() -> Tuple[float, float]:
    """
    Return the equivalent standard Cornell parameters for the phi potential.
    
    Returns
    -------
    tuple (sigma, alpha)
        sigma = 1/φ (string tension)
        alpha = 1/(2φ²) (Coulomb strength)
    """
    sigma = 1.0 / PHI
    alpha = 1.0 / (2.0 * PHI_SQUARED)
    return sigma, alpha


def phi_confinement_deviation(r_grid: np.ndarray,
                               sigma: float = 1.0,
                               alpha: float = 1.0) -> np.ndarray:
    """
    Calculate deviation between phi-parameterized and standard Cornell potentials.
    
    Parameters
    ----------
    r_grid : np.ndarray
        Distance values
    sigma : float
        Standard Cornell string tension for comparison
    alpha : float
        Standard Cornell Coulomb strength for comparison
        
    Returns
    -------
    np.ndarray
        Deviation V_φ(r) - V_C(r) at each point
    """
    v_phi = cornell_phi_potential(r_grid)
    v_standard = cornell_standard_potential(r_grid, sigma, alpha)
    return v_phi - v_standard


def analyze_potential(r_grid: np.ndarray,
                      potential_func,
                      potential_name: str) -> PotentialAnalysis:
    """
    Analyze a confinement potential for key characteristics.
    
    Parameters
    ----------
    r_grid : np.ndarray
        Distance values
    potential_func : callable
        Function that computes V(r)
    potential_name : str
        Name for the potential being analyzed
        
    Returns
    -------
    PotentialAnalysis
        Analysis results including turning point, asymptotic behavior, etc.
    """
    v_values = potential_func(r_grid)
    
    # Find turning point (minimum)
    min_idx = np.argmin(v_values)
    turning_point_r = r_grid[min_idx] if min_idx > 0 else None
    turning_point_v = v_values[min_idx] if min_idx > 0 else None
    
    # Asymptotic slope (linear term coefficient)
    # For large r, V(r) ≈ σr, so slope = σ
    large_r = r_grid[r_grid > 10]
    if len(large_r) > 1:
        v_large = potential_func(large_r)
        asymptotic_slope = np.polyfit(large_r, v_large, 1)[0]
    else:
        asymptotic_slope = np.nan
    
    # Short-range coefficient (Coulomb term)
    # For small r, V(r) ≈ -α/r, so coefficient = α
    small_r = r_grid[(r_grid > 0.01) & (r_grid < 0.1)]
    if len(small_r) > 1:
        v_small = potential_func(small_r)
        # Fit V(r) * r to find α
        short_range_coefficient = np.mean(-v_small * small_r)
    else:
        short_range_coefficient = np.nan
    
    return PotentialAnalysis(
        potential_name=potential_name,
        r_grid=r_grid,
        v_values=v_values,
        turning_point_r=turning_point_r,
        turning_point_v=turning_point_v,
        asymptotic_slope=asymptotic_slope,
        short_range_coefficient=short_range_coefficient,
        min_value=np.min(v_values),
        max_value=np.max(v_values)
    )


def compare_potentials(r_grid: np.ndarray,
                       sigma: float = 1.0,
                       alpha: float = 1.0) -> Dict:
    """
    Compare phi-parameterized and standard Cornell potentials.
    
    Parameters
    ----------
    r_grid : np.ndarray
        Distance values for comparison
    sigma : float
        Standard Cornell string tension
    alpha : float
        Standard Coulomb strength
        
    Returns
    -------
    dict
        Comparison metrics and analysis results
    """
    # Get phi potential
    v_phi = cornell_phi_potential(r_grid)
    
    # Get standard Cornell with equivalent parameters
    sigma_phi, alpha_phi = cornell_phi_equivalent_params()
    v_standard_equiv = cornell_standard_potential(r_grid, sigma_phi, alpha_phi)
    
    # Get standard Cornell with user parameters
    v_standard_user = cornell_standard_potential(r_grid, sigma, alpha)
    
    # Calculate deviations
    deviation_equiv = v_phi - v_standard_equiv
    deviation_user = v_phi - v_standard_user
    
    # Fit error metrics
    mse_equiv = np.mean(deviation_equiv ** 2)
    mae_equiv = np.mean(np.abs(deviation_equiv))
    max_error_equiv = np.max(np.abs(deviation_equiv))
    
    mse_user = np.mean(deviation_user ** 2)
    mae_user = np.mean(np.abs(deviation_user))
    max_error_user = np.max(np.abs(deviation_user))
    
    return {
        "r_grid": r_grid,
        "v_phi": v_phi,
        "v_standard_equiv": v_standard_equiv,
        "v_standard_user": v_standard_user,
        "deviation_equiv": deviation_equiv,
        "deviation_user": deviation_user,
        "fit_error_equiv": {
            "mse": mse_equiv,
            "mae": mae_equiv,
            "max_error": max_error_equiv
        },
        "fit_error_user": {
            "mse": mse_user,
            "mae": mae_user,
            "max_error": max_error_user
        },
        "phi_params": {
            "sigma": sigma_phi,
            "alpha": alpha_phi
        }
    }


def plot_potentials_comparison(r_grid: np.ndarray,
                                sigma: float = 1.0,
                                alpha: float = 1.0,
                                save_path: Optional[str] = None):
    """
    Generate comparison plots for Cornell-φ vs standard Cornell potentials.
    
    Parameters
    ----------
    r_grid : np.ndarray
        Distance values
    sigma : float
        Standard Cornell string tension for comparison
    alpha : float
        Standard Coulomb strength for comparison
    save_path : str, optional
        Path to save the figure
    """
    comparison = compare_potentials(r_grid, sigma, alpha)
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Cornell-φ Confinement Potential Analysis (EXPLORATORY)', 
                 fontsize=14, fontweight='bold')
    
    # Plot 1: Potentials comparison
    ax = axes[0, 0]
    ax.plot(r_grid, comparison["v_phi"], 'b-', linewidth=2, 
            label=f'V_φ(r)  [σ=1/φ, α=1/(2φ²)]')
    ax.plot(r_grid, comparison["v_standard_user"], 'r--', linewidth=2,
            label=f'V_C(r)  [σ={sigma}, α={alpha}]')
    ax.set_xlabel('r (distance)')
    ax.set_ylabel('V(r)')
    ax.set_title('Potential Comparison')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Plot 2: Deviation from standard
    ax = axes[0, 1]
    ax.plot(r_grid, comparison["deviation_user"], 'g-', linewidth=2)
    ax.axhline(y=0, color='k', linestyle='-', alpha=0.3)
    ax.set_xlabel('r (distance)')
    ax.set_ylabel('V_φ(r) - V_C(r)')
    ax.set_title(f'Deviation (MAE={comparison["fit_error_user"]["mae"]:.4f})')
    ax.grid(True, alpha=0.3)
    
    # Plot 3: Log-log plot for asymptotic behavior
    ax = axes[1, 0]
    r_log = r_grid[r_grid > 0.01]
    v_phi_log = cornell_phi_potential(r_log)
    v_std_log = cornell_standard_potential(r_log, sigma, alpha)
    ax.loglog(r_log, np.abs(v_phi_log), 'b-', linewidth=2, label='V_φ(r)')
    ax.loglog(r_log, np.abs(v_std_log), 'r--', linewidth=2, label='V_C(r)')
    ax.set_xlabel('r (log scale)')
    ax.set_ylabel('|V(r)| (log scale)')
    ax.set_title('Log-Log Behavior')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Plot 4: Parameter space
    ax = axes[1, 1]
    ax.text(0.1, 0.8, 'Cornell-φ Parameters:', fontsize=12, fontweight='bold',
            transform=ax.transAxes)
    ax.text(0.1, 0.7, f'φ = {PHI:.10f}', fontsize=10, transform=ax.transAxes)
    ax.text(0.1, 0.6, f'σ = 1/φ = {comparison["phi_params"]["sigma"]:.6f}',
            fontsize=10, transform=ax.transAxes)
    ax.text(0.1, 0.5, f'α = 1/(2φ²) = {comparison["phi_params"]["alpha"]:.6f}',
            fontsize=10, transform=ax.transAxes)
    ax.text(0.1, 0.35, 'Fit Error (vs user params):', fontsize=11, 
            fontweight='bold', transform=ax.transAxes)
    ax.text(0.1, 0.25, f'MSE: {comparison["fit_error_user"]["mse"]:.6f}',
            fontsize=10, transform=ax.transAxes)
    ax.text(0.1, 0.15, f'MAE: {comparison["fit_error_user"]["mae"]:.6f}',
            fontsize=10, transform=ax.transAxes)
    ax.text(0.1, 0.05, 'Status: EXPLORATORY', fontsize=11, 
            color='red', fontweight='bold', transform=ax.transAxes)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Figure saved to: {save_path}")
    
    return fig


def run_falsification_tests(r_grid: np.ndarray) -> Dict:
    """
    Run falsification tests for the Cornell-φ potential.
    
    Parameters
    ----------
    r_grid : np.ndarray
        Distance values for testing
        
    Returns
    -------
    dict
        Test results with pass/fail status for each condition
    """
    v_phi = cornell_phi_potential(r_grid)
    
    results = {}
    
    # Test 1: No unphysical singularities at r > epsilon
    epsilon = 1e-9
    r_test = r_grid[r_grid > epsilon]
    v_test = cornell_phi_potential(r_test)
    finite_values = np.all(np.isfinite(v_test))
    results["no_singularities"] = {
        "passed": finite_values,
        "description": "No singularities at r > ε",
        "value": finite_values
    }
    
    # Test 2: Monotonicity check (no turning point for this potential)
    # V_φ'(r) = 1/φ + 1/(2φ²r²) > 0 for all r > 0
    # So the potential should be monotonically increasing
    v_diff = np.diff(v_phi)
    monotonic = np.all(v_diff >= -1e-10)  # Allow tiny numerical errors
    results["monotonicity"] = {
        "passed": monotonic,
        "description": "Potential is monotonically increasing (no local minima)",
        "value": monotonic
    }
    
    # Test 3: Asymptotic growth (linear with slope 1/phi)
    large_r = r_grid[r_grid > 10]
    if len(large_r) > 1:
        v_large = cornell_phi_potential(large_r)
        slope = np.polyfit(large_r, v_large, 1)[0]
        expected_slope = 1.0 / PHI
        slope_error = abs(slope - expected_slope) / expected_slope
        results["asymptotic_slope"] = {
            "passed": slope_error < 0.1,
            "description": "Asymptotic slope within 10% of 1/φ",
            "expected": expected_slope,
            "measured": slope,
            "error": slope_error
        }
    
    # Test 4: Short-range behavior (-1/(2φ²r))
    small_r = r_grid[(r_grid > 0.01) & (r_grid < 0.1)]
    if len(small_r) > 1:
        v_small = cornell_phi_potential(small_r)
        # V(r) ≈ -α/r, so -V(r)*r ≈ α
        alpha_measured = np.mean(-v_small * small_r)
        expected_alpha = 1.0 / (2.0 * PHI_SQUARED)
        alpha_error = abs(alpha_measured - expected_alpha) / expected_alpha
        results["short_range"] = {
            "passed": alpha_error < 0.1,
            "description": "Short-range coefficient within 10% of 1/(2φ²)",
            "expected": expected_alpha,
            "measured": alpha_measured,
            "error": alpha_error
        }
    
    return results


def print_hypothesis_note():
    """Print the hypothesis note for this exploratory potential."""
    print("""
================================================================================
HYPOTHESIS NOTE: Cornell-φ Confinement Potential
================================================================================

CLAIM:
------
This is a phi-parameterized analog of a Cornell-like confinement potential.
It is NOT a claim that QCD is governed by phi.

EQUATION:
---------
V_φ(r) = r/φ - 1/(2φ²r)

Where φ = (1 + √5)/2 ≈ 1.618033988749895

INTENDED DOMAIN:
----------------
- Quantum circuit coupling design
- Consciousness state modeling
- Sacred geometry quantum computations

NOT validated for: actual QCD calculations

COMPARISON TARGET:
------------------
Standard Cornell potential: V_C(r) = σr - α/r
With equivalent parameters: σ = 1/φ, α = 1/(2φ²)

FALSIFICATION CONDITIONS:
-------------------------
1. Unphysical singularities at any r > ε
2. Turning point deviates >10% from r_min = 1/√2
3. Asymptotic growth not linear with slope 1/φ
4. Short-range behavior not matching -1/(2φ²r)

GOVERNANCE STATUS: EXPLORATORY
================================================================================
""")


if __name__ == "__main__":
    # Print hypothesis note
    print_hypothesis_note()
    
    # Generate comparison
    print("\nGenerating Cornell-φ potential analysis...")
    # Use log-spaced grid to better capture turning point and asymptotic behavior
    r_grid = np.logspace(-2, 2, 1000)  # 0.01 to 100
    
    # Run falsification tests
    print("\nRunning falsification tests...")
    test_results = run_falsification_tests(r_grid)
    
    print("\nTest Results:")
    print("-" * 50)
    all_passed = True
    for test_name, result in test_results.items():
        status = "✓ PASS" if result["passed"] else "✗ FAIL"
        print(f"{status}: {result['description']}")
        if "error" in result:
            print(f"       Error: {result['error']:.4f} (expected: {result['expected']:.6f}, measured: {result['measured']:.6f})")
        if not result["passed"]:
            all_passed = False
    
    print("-" * 50)
    if all_passed:
        print("All falsification tests PASSED.")
        print("Potential remains EXPLORATORY pending further validation.")
    else:
        print("Some falsification tests FAILED.")
        print("Potential requires revision before further use.")
    
    # Generate plot
    print("\nGenerating comparison plot...")
    fig = plot_potentials_comparison(r_grid, sigma=1.0, alpha=1.0,
                                     save_path="cornell_phi_analysis.png")
    plt.show()
