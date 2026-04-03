"""
Tests for Wing Occlusion Geometry Module
"""

import pytest
import numpy as np
from wing_occlusion.geometry import (
    generate_fibonacci_spiral,
    compute_distance_to_spirals,
    occlude_points,
    recover_points,
    compute_recovery_error,
    PHI,
)


class TestGenerateFibonacciSpiral:
    """Tests for spiral generation."""
    
    def test_spiral_shape(self):
        """Test spiral generates correct shape."""
        x, y = generate_fibonacci_spiral(n_points=100)
        assert x.shape == (100,)
        assert y.shape == (100,)
    
    def test_spiral_direction(self):
        """Test direction parameter produces different spirals."""
        x1, y1 = generate_fibonacci_spiral(n_points=100, direction=1)
        x2, y2 = generate_fibonacci_spiral(n_points=100, direction=-1)
        
        # At least one coordinate should be different
        # (x may be same at certain angles due to symmetry)
        different = not (np.allclose(x1, x2) and np.allclose(y1, y2))
        assert different
    
    def test_radius_monotonicity(self):
        """Test that radius increases along spiral."""
        x, y = generate_fibonacci_spiral(n_points=100)
        radii = np.sqrt(x**2 + y**2)
        
        # Radius should generally increase (may have local variations)
        assert radii[-1] > radii[0]
    
    def test_phi_constant(self):
        """Test PHI value."""
        expected = (1 + np.sqrt(5)) / 2
        assert abs(PHI - expected) < 1e-10


class TestComputeDistanceToSpirals:
    """Tests for distance computation."""
    
    def test_distance_shape(self):
        """Test distance arrays have correct shape."""
        data = np.random.randn(10, 2)
        spiral1 = np.random.randn(20, 2)
        spiral2 = np.random.randn(20, 2)
        
        dist1, dist2 = compute_distance_to_spirals(data, spiral1, spiral2)
        
        assert dist1.shape == (10,)
        assert dist2.shape == (10,)
    
    def test_distance_non_negative(self):
        """Test distances are non-negative."""
        data = np.random.randn(10, 2)
        spiral1 = np.random.randn(20, 2)
        spiral2 = np.random.randn(20, 2)
        
        dist1, dist2 = compute_distance_to_spirals(data, spiral1, spiral2)
        
        assert np.all(dist1 >= 0)
        assert np.all(dist2 >= 0)
    
    def test_distance_to_self(self):
        """Test distance from point to itself is zero."""
        data = np.array([[1.0, 2.0]])
        spiral = np.array([[1.0, 2.0], [3.0, 4.0]])
        
        dist, _ = compute_distance_to_spirals(data, spiral, spiral)
        
        assert dist[0] < 1e-10


class TestOccludePoints:
    """Tests for occlusion transform."""
    
    def test_occlusion_shape(self):
        """Test output has same shape as input."""
        data = np.random.randn(50, 2)
        occluded, mask = occlude_points(data)
        
        assert occluded.shape == data.shape
        assert mask.shape == (50,)
    
    def test_occlusion_mask_boolean(self):
        """Test mask is boolean."""
        data = np.random.randn(50, 2)
        _, mask = occlude_points(data)
        
        assert mask.dtype == bool
    
    def test_occlusion_reversible(self):
        """Test occlusion is reversible with mask."""
        np.random.seed(42)
        data = np.random.randn(50, 2)
        
        occluded, mask = occlude_points(data)
        recovered = recover_points(occluded, mask)
        
        # Should recover exactly
        assert np.allclose(data, recovered, atol=1e-10)
    
    def test_occlusion_deterministic(self):
        """Test occlusion is deterministic."""
        data = np.random.randn(50, 2)
        
        occluded1, mask1 = occlude_points(data)
        occluded2, mask2 = occlude_points(data)
        
        assert np.allclose(occluded1, occluded2)
        assert np.array_equal(mask1, mask2)


class TestRecoverPoints:
    """Tests for recovery."""
    
    def test_recovery_shape(self):
        """Test recovery has correct shape."""
        data = np.random.randn(50, 2)
        occluded, mask = occlude_points(data)
        recovered = recover_points(occluded, mask)
        
        assert recovered.shape == data.shape
    
    def test_recovery_exact(self):
        """Test recovery is exact."""
        np.random.seed(42)
        data = np.random.randn(50, 2)
        
        occluded, mask = occlude_points(data)
        recovered = recover_points(occluded, mask)
        
        assert np.allclose(data, recovered, atol=1e-10)
    
    def test_recovery_no_mask(self):
        """Test recovery with no hidden points."""
        data = np.random.randn(50, 2)
        mask = np.zeros(50, dtype=bool)
        
        recovered = recover_points(data.copy(), mask)
        
        assert np.allclose(data, recovered)


class TestComputeRecoveryError:
    """Tests for error metrics."""
    
    def test_error_metrics_keys(self):
        """Test all expected keys are present."""
        original = np.random.randn(50, 2)
        recovered = original + np.random.randn(50, 2) * 0.1
        mask = np.random.rand(50) < 0.3
        
        metrics = compute_recovery_error(original, recovered, mask)
        
        expected_keys = ['mae_hidden', 'mae_visible', 'mae_overall', 'max_error', 'n_hidden', 'n_visible']
        for key in expected_keys:
            assert key in metrics
    
    def test_error_zero_for_perfect(self):
        """Test error is zero for perfect recovery."""
        data = np.random.randn(50, 2)
        mask = np.random.rand(50) < 0.3
        
        metrics = compute_recovery_error(data, data.copy(), mask)
        
        assert metrics['mae_overall'] < 1e-10
        assert metrics['mae_hidden'] < 1e-10
    
    def test_error_positive(self):
        """Test errors are positive."""
        original = np.random.randn(50, 2)
        recovered = original + 1.0  # Deliberately wrong
        mask = np.random.rand(50) < 0.3
        
        metrics = compute_recovery_error(original, recovered, mask)
        
        assert metrics['mae_hidden'] > 0
        assert metrics['mae_visible'] >= 0
        assert metrics['mae_overall'] > 0


class TestVectorizedVsNaive:
    """Test vectorized implementation matches naive."""
    
    def naive_distance(self, data, spiral):
        """Naive O(n*m) distance computation."""
        distances = []
        for point in data:
            min_dist = float('inf')
            for spiral_point in spiral:
                dist = np.sqrt(np.sum((point - spiral_point)**2))
                min_dist = min(min_dist, dist)
            distances.append(min_dist)
        return np.array(distances)
    
    def test_vectorized_matches_naive(self):
        """Test vectorized implementation produces same results as naive."""
        np.random.seed(42)
        data = np.random.randn(20, 2)
        spiral = np.random.randn(30, 2)
        
        # Vectorized
        dist_vec, _ = compute_distance_to_spirals(data, spiral, spiral)
        
        # Naive
        dist_naive = self.naive_distance(data, spiral)
        
        assert np.allclose(dist_vec, dist_naive, atol=1e-10)
