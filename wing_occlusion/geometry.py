"""
Wing Occlusion Geometry Module

Core geometric operations for phi-spiral based point transformation.
All functions are deterministic, reproducible, and have strict input/output contracts.
"""

import numpy as np
from typing import Tuple, Optional

PHI = 1.618033988749895


def generate_fibonacci_spiral(
    n_points: int = 100,
    direction: int = 1,
    phi: float = PHI
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate Fibonacci spiral points.
    
    Args:
        n_points: Number of spiral points to generate
        direction: Rotation direction (1=counter-clockwise, -1=clockwise)
        phi: Golden ratio constant
        
    Returns:
        Tuple of (x_coords, y_coords) arrays
    """
    angles = np.linspace(0, 4 * np.pi, n_points)
    radii = phi ** (angles / (2 * np.pi))
    x = radii * np.cos(angles * direction)
    y = radii * np.sin(angles * direction)
    return x, y


def compute_distance_to_spirals(
    data_points: np.ndarray,
    spiral1_points: np.ndarray,
    spiral2_points: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute minimum distance from each data point to both spirals.
    
    Vectorized implementation: O(n*m) operations in batched NumPy.
    
    Args:
        data_points: Array of shape (n_data, 2)
        spiral1_points: Array of shape (n_spiral, 2)
        spiral2_points: Array of shape (n_spiral, 2)
        
    Returns:
        Tuple of (distances_to_spiral1, distances_to_spiral2), 
        each of shape (n_data,)
    """
    # Reshape for broadcasting: (n_data, 1, 2) - (1, n_spiral, 2) -> (n_data, n_spiral, 2)
    diff1 = data_points[:, np.newaxis, :] - spiral1_points[np.newaxis, :, :]
    diff2 = data_points[:, np.newaxis, :] - spiral2_points[np.newaxis, :, :]
    
    # Compute Euclidean distances: (n_data, n_spiral)
    distances1 = np.sqrt(np.sum(diff1**2, axis=2))
    distances2 = np.sqrt(np.sum(diff2**2, axis=2))
    
    # Minimum distance to any spiral point
    min_distances1 = np.min(distances1, axis=1)
    min_distances2 = np.min(distances2, axis=1)
    
    return min_distances1, min_distances2


def occlude_points(
    data_points: np.ndarray,
    vortex_threshold: float = 0.5,
    spiral_scale: float = 0.1,
    rotation_offset: float = np.pi,
    n_spiral_points: int = 200,
    seed: Optional[int] = None
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Apply wing occlusion transform to data points.
    
    Points closer than threshold to either spiral are relocated:
    (r, θ) -> (spiral_scale * r, θ + rotation_offset)
    
    Args:
        data_points: Input array of shape (n_points, 2)
        vortex_threshold: Distance threshold for occlusion
        spiral_scale: Scale factor for relocated radius
        rotation_offset: Angular rotation for relocated points
        n_spiral_points: Number of spiral points to generate
        seed: Random seed for reproducibility (not used currently)
        
    Returns:
        Tuple of (occluded_points, hidden_mask)
        - occluded_points: Transformed array of shape (n_points, 2)
        - hidden_mask: Boolean array indicating which points were occluded
    """
    # Generate spirals once
    x1, y1 = generate_fibonacci_spiral(n_spiral_points, direction=1)
    x2, y2 = generate_fibonacci_spiral(n_spiral_points, direction=-1)
    
    spiral1_points = np.column_stack([x1, y1])
    spiral2_points = np.column_stack([x2, y2])
    
    # Compute distances (vectorized)
    distances1, distances2 = compute_distance_to_spirals(
        data_points, spiral1_points, spiral2_points
    )
    
    # Identify points to occlude
    hidden_mask = (distances1 < vortex_threshold) | (distances2 < vortex_threshold)
    
    # Apply transform
    occluded_points = data_points.copy()
    
    if np.any(hidden_mask):
        hidden_indices = np.where(hidden_mask)[0]
        hidden_points = data_points[hidden_indices]
        
        # Convert to polar coordinates
        angles = np.arctan2(hidden_points[:, 1], hidden_points[:, 0])
        radii = np.sqrt(hidden_points[:, 0]**2 + hidden_points[:, 1]**2)
        
        # Apply occlusion transform
        new_radii = radii * spiral_scale
        new_angles = angles + rotation_offset
        
        # Convert back to Cartesian
        occluded_points[hidden_indices, 0] = new_radii * np.cos(new_angles)
        occluded_points[hidden_indices, 1] = new_radii * np.sin(new_angles)
    
    return occluded_points, hidden_mask


def recover_points(
    occluded_points: np.ndarray,
    hidden_mask: np.ndarray,
    spiral_scale: float = 0.1,
    rotation_offset: float = np.pi
) -> np.ndarray:
    """
    Reverse the occlusion transform using side information (hidden_mask).
    
    This is NOT blind recovery - it requires the hidden_mask from encoding.
    
    Args:
        occluded_points: Occluded array of shape (n_points, 2)
        hidden_mask: Boolean mask from occlude_points()
        spiral_scale: Scale factor used in occlusion
        rotation_offset: Rotation offset used in occlusion
        
    Returns:
        Recovered array of shape (n_points, 2)
    """
    recovered = occluded_points.copy()
    
    if np.any(hidden_mask):
        hidden_indices = np.where(hidden_mask)[0]
        occluded_hidden = occluded_points[hidden_indices]
        
        # Reverse the transform
        angles = np.arctan2(occluded_hidden[:, 1], occluded_hidden[:, 0])
        radii = np.sqrt(occluded_hidden[:, 0]**2 + occluded_hidden[:, 1]**2)
        
        # Inverse: (r, θ) -> (r / scale, θ - offset)
        original_radii = radii / spiral_scale
        original_angles = angles - rotation_offset
        
        recovered[hidden_indices, 0] = original_radii * np.cos(original_angles)
        recovered[hidden_indices, 1] = original_radii * np.sin(original_angles)
    
    return recovered


def compute_recovery_error(
    original: np.ndarray,
    recovered: np.ndarray,
    hidden_mask: np.ndarray
) -> dict:
    """
    Compute recovery quality metrics.
    
    Args:
        original: Original data points
        recovered: Recovered data points
        hidden_mask: Mask of hidden points
        
    Returns:
        Dictionary of metrics:
        - mae_hidden: MAE on hidden points only
        - mae_visible: MAE on visible (non-hidden) points
        - mae_overall: Overall MAE
        - max_error: Maximum error on hidden points
    """
    errors = np.sqrt(np.sum((original - recovered)**2, axis=1))
    
    if np.any(hidden_mask):
        mae_hidden = np.mean(errors[hidden_mask])
        max_error = np.max(errors[hidden_mask])
    else:
        mae_hidden = 0.0
        max_error = 0.0
    
    mae_visible = np.mean(errors[~hidden_mask]) if np.any(~hidden_mask) else 0.0
    mae_overall = np.mean(errors)
    
    return {
        'mae_hidden': mae_hidden,
        'mae_visible': mae_visible,
        'mae_overall': mae_overall,
        'max_error': max_error,
        'n_hidden': int(np.sum(hidden_mask)),
        'n_visible': int(np.sum(~hidden_mask)),
    }
