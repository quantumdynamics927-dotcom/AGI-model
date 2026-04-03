"""
Wing Occlusion Metrics Module

Quantitative metrics for evaluating occlusion transform quality.
All metrics are explicitly defined and independently testable.
"""

import numpy as np
from typing import Dict, Optional


def compute_reconstruction_mae(
    original: np.ndarray,
    reconstructed: np.ndarray,
    mask: Optional[np.ndarray] = None
) -> float:
    """
    Compute Mean Absolute Error between original and reconstructed points.
    
    Args:
        original: Array of shape (n, 2)
        reconstructed: Array of shape (n, 2)
        mask: Optional boolean mask to compute error on subset
        
    Returns:
        MAE value (scalar)
    """
    errors = np.sqrt(np.sum((original - reconstructed)**2, axis=1))
    
    if mask is not None:
        return float(np.mean(errors[mask]))
    else:
        return float(np.mean(errors))


def compute_hidden_fraction(hidden_mask: np.ndarray) -> float:
    """
    Compute fraction of points that were hidden/occluded.
    
    Args:
        hidden_mask: Boolean array
        
    Returns:
        Fraction in range [0, 1]
    """
    return float(np.mean(hidden_mask))


def compute_distance_preservation(
    original: np.ndarray,
    transformed: np.ndarray,
    visible_mask: np.ndarray,
    n_samples: int = 100
) -> float:
    """
    Compute how well pairwise distances are preserved for visible points.
    
    Args:
        original: Original points (n, 2)
        transformed: Transformed points (n, 2)
        visible_mask: Boolean mask of visible points
        n_samples: Number of point pairs to sample
        
    Returns:
        Correlation coefficient of pairwise distances (1.0 = perfect preservation)
    """
    visible_original = original[visible_mask]
    visible_transformed = transformed[visible_mask]
    
    n_points = len(visible_original)
    if n_points < 2:
        return 1.0
    
    # Sample random point pairs
    n_pairs = min(n_samples, n_points * (n_points - 1) // 2)
    indices1 = np.random.choice(n_points, n_pairs, replace=True)
    indices2 = np.random.choice(n_points, n_pairs, replace=True)
    
    # Compute pairwise distances
    diff_orig = visible_original[indices1] - visible_original[indices2]
    diff_trans = visible_transformed[indices1] - visible_transformed[indices2]
    
    dist_orig = np.sqrt(np.sum(diff_orig**2, axis=1))
    dist_trans = np.sqrt(np.sum(diff_trans**2, axis=1))
    
    # Correlation (measure of preservation)
    if np.std(dist_orig) < 1e-10 or np.std(dist_trans) < 1e-10:
        return 1.0
    
    correlation = np.corrcoef(dist_orig, dist_trans)[0, 1]
    return float(correlation) if not np.isnan(correlation) else 0.0


def compute_structural_preservation(
    original: np.ndarray,
    recovered: np.ndarray,
    hidden_mask: np.ndarray
) -> Dict[str, float]:
    """
    Compute structural preservation metrics.
    
    Args:
        original: Original points
        recovered: Recovered points
        hidden_mask: Mask of hidden points
        
    Returns:
        Dictionary of metrics
    """
    from .geometry import compute_recovery_error
    
    recovery_metrics = compute_recovery_error(original, recovered, hidden_mask)
    
    # Additional structural metrics
    original_centroid = np.mean(original, axis=0)
    recovered_centroid = np.mean(recovered, axis=0)
    centroid_shift = np.sqrt(np.sum((original_centroid - recovered_centroid)**2))
    
    original_spread = np.std(np.sqrt(np.sum((original - original_centroid)**2, axis=1)))
    recovered_spread = np.std(np.sqrt(np.sum((recovered - recovered_centroid)**2, axis=1)))
    spread_ratio = recovered_spread / (original_spread + 1e-10)
    
    return {
        'recovery_mae_hidden': recovery_metrics['mae_hidden'],
        'recovery_mae_visible': recovery_metrics['mae_visible'],
        'recovery_max_error': recovery_metrics['max_error'],
        'centroid_shift': float(centroid_shift),
        'spread_ratio': float(spread_ratio),
        'hidden_fraction': compute_hidden_fraction(hidden_mask),
    }


def compute_runtime_metrics(
    times: list,
    warmup_runs: int = 0
) -> Dict[str, float]:
    """
    Compute runtime statistics from timing samples.
    
    Args:
        times: List of timing measurements (seconds)
        warmup_runs: Number of initial runs to exclude
        
    Returns:
        Dictionary of runtime metrics
    """
    if warmup_runs > 0:
        times = times[warmup_runs:]
    
    if len(times) == 0:
        return {
            'mean': 0.0,
            'median': 0.0,
            'std': 0.0,
            'p95': 0.0,
            'min': 0.0,
            'max': 0.0,
        }
    
    return {
        'mean': float(np.mean(times)),
        'median': float(np.median(times)),
        'std': float(np.std(times)),
        'p95': float(np.percentile(times, 95)),
        'min': float(np.min(times)),
        'max': float(np.max(times)),
    }
