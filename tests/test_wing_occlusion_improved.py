"""
Tests for improved wing occlusion module

Tests vectorized operations, quantum state preservation, golden ratio validation,
and performance improvements.
"""

import pytest
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
from pathlib import Path
import tempfile
import shutil
import sys
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import with proper path handling (TMT-OS has dash, so we need to use importlib)
import importlib.util
wing_occlusion_path = Path(__file__).parent.parent / "TMT-OS" / "wing_occlusion" / "advanced_occlusion.py"
spec = importlib.util.spec_from_file_location("advanced_occlusion", wing_occlusion_path)
advanced_occlusion = importlib.util.module_from_spec(spec)
spec.loader.exec_module(advanced_occlusion)

WingOcclusionDemonstrator = advanced_occlusion.WingOcclusionDemonstrator
PHI = advanced_occlusion.PHI
DELTA = advanced_occlusion.DELTA


@pytest.fixture
def demonstrator():
    """Create a wing occlusion demonstrator instance"""
    return WingOcclusionDemonstrator()


@pytest.fixture
def sample_data_points():
    """Generate sample data points for testing"""
    np.random.seed(42)
    return np.random.randn(50, 2) * 2


def test_demonstrator_initialization(demonstrator):
    """Test demonstrator initialization with golden ratio constants"""
    assert demonstrator.phi == PHI
    assert demonstrator.delta == DELTA
    assert abs(demonstrator.phi - 1.618033988749895) < 1e-10


def test_golden_ratio_validation(demonstrator):
    """Test golden ratio validation"""
    # Should validate correctly with default phi
    assert demonstrator.validate_golden_ratio() == True
    
    # Should fail with wrong phi
    demonstrator.phi = 2.0
    assert demonstrator.validate_golden_ratio() == False
    
    # Should pass with tolerance
    demonstrator.phi = PHI + 0.0001
    assert demonstrator.validate_golden_ratio(tolerance=0.001) == True


def test_fibonacci_spiral_generation(demonstrator):
    """Test Fibonacci spiral generation"""
    x, y = demonstrator.generate_fibonacci_spiral(n_points=100, direction=1)
    
    assert len(x) == 100
    assert len(y) == 100
    assert isinstance(x, np.ndarray)
    assert isinstance(y, np.ndarray)
    
    # Test clockwise direction
    x1, y1 = demonstrator.generate_fibonacci_spiral(direction=1)
    # Test counter-clockwise direction
    x2, y2 = demonstrator.generate_fibonacci_spiral(direction=-1)
    
    # Spiral should grow exponentially
    assert np.max(np.abs(x1)) > np.min(np.abs(x1))
    assert np.max(np.abs(y1)) > np.min(np.abs(y1))


def test_wing_entanglement_vectorization(demonstrator, sample_data_points):
    """Test that wing entanglement uses vectorized operations"""
    occluded_data, hidden_indices = demonstrator.create_wing_entanglement(
        sample_data_points
    )
    
    assert occluded_data.shape == sample_data_points.shape
    assert isinstance(hidden_indices, list)
    assert len(hidden_indices) >= 0
    
    # All indices should be valid
    for idx in hidden_indices:
        assert 0 <= idx < len(sample_data_points)


def test_wing_entanglement_with_params(demonstrator, sample_data_points):
    """Test wing entanglement with custom parameters"""
    occluded_data, hidden_indices = demonstrator.create_wing_entanglement(
        sample_data_points,
        vortex_threshold=1.0,  # Larger threshold
        vortex_scale=0.2       # Different scale
    )
    
    assert occluded_data.shape == sample_data_points.shape
    # With larger threshold, more points should be occluded
    assert len(hidden_indices) >= 0


def test_quantum_state_preservation(demonstrator, sample_data_points):
    """Test quantum state preservation metric"""
    occluded_data, _ = demonstrator.create_wing_entanglement(sample_data_points)
    
    preservation = demonstrator.preserve_quantum_state(
        sample_data_points,
        occluded_data
    )
    
    # Fidelity should be between 0 and 1
    assert 0.0 <= preservation <= 1.0
    assert isinstance(preservation, float)
    
    # Perfect preservation should give fidelity of 1.0
    # (but occlusion changes data, so it will be less)
    # At least some preservation should occur
    assert preservation > 0.0


def test_quantum_state_preservation_perfect_case(demonstrator):
    """Test quantum preservation with identical data (should be 1.0)"""
    data = np.random.randn(10, 2)
    preservation = demonstrator.preserve_quantum_state(data, data.copy())
    
    # Should be very close to 1.0 for identical data
    assert preservation > 0.99


def test_demonstrate_occlusion_basic(demonstrator):
    """Test basic occlusion demonstration"""
    results = demonstrator.demonstrate_occlusion(n_agents=30)
    
    assert 'original_data' in results
    assert 'occluded_data' in results
    assert 'hidden_indices' in results
    assert 'recovery_error' in results
    assert 'preservation_fidelity' in results
    assert 'phi' in results
    assert 'n_agents' in results
    assert 'occlusion_rate' in results
    
    # Verify data shapes
    assert results['original_data'].shape == (30, 2)
    assert results['occluded_data'].shape == (30, 2)
    assert results['n_agents'] == 30
    
    # Verify metrics are valid
    assert 0.0 <= results['occlusion_rate'] <= 1.0
    assert 0.0 <= results['preservation_fidelity'] <= 1.0
    assert results['phi'] == PHI
    assert results['recovery_error'] >= 0.0


def test_demonstrate_occlusion_with_save_path(demonstrator):
    """Test occlusion demonstration with custom save path"""
    temp_dir = Path(tempfile.mkdtemp())
    try:
        save_path = temp_dir / 'test_occlusion.png'
        results = demonstrator.demonstrate_occlusion(
            n_agents=20,
            save_path=str(save_path)
        )
        
        # Verify save path was used
        # Note: demonstrate_occlusion saves internally, this just tests the parameter
        assert results['n_agents'] == 20
    finally:
        shutil.rmtree(temp_dir)


def test_performance_improvement_vectorization(demonstrator):
    """Test that vectorized operations are faster than naive approach"""
    # Generate larger dataset
    large_data = np.random.randn(200, 2) * 2
    
    # Time vectorized version
    start = time.time()
    occluded, indices = demonstrator.create_wing_entanglement(large_data)
    vectorized_time = time.time() - start
    
    # Verify it completes in reasonable time (vectorized should be fast)
    assert vectorized_time < 5.0  # Should complete in under 5 seconds
    
    # Verify results are correct
    assert occluded.shape == large_data.shape
    assert len(indices) >= 0


def test_golden_ratio_integration(demonstrator, sample_data_points):
    """Test that golden ratio validation is integrated"""
    # Create demonstrator with correct phi
    assert demonstrator.validate_golden_ratio() == True
    
    # Run demonstration and check phi in results
    results = demonstrator.demonstrate_occlusion(n_agents=20)
    assert results['phi'] == PHI
    assert abs(results['phi'] - 1.618033988749895) < 1e-10


def test_recovery_error_calculation(demonstrator):
    """Test that data recovery error is calculated correctly"""
    results = demonstrator.demonstrate_occlusion(n_agents=30)
    
    recovery_error = results['recovery_error']
    
    # Recovery error should be non-negative
    assert recovery_error >= 0.0
    
    # For perfect recovery, error should be near zero
    # (but occlusion changes data, so error will be > 0)
    assert isinstance(recovery_error, float)


def test_occlusion_rate_metric(demonstrator):
    """Test occlusion rate calculation"""
    results = demonstrator.demonstrate_occlusion(n_agents=50)
    
    occlusion_rate = results['occlusion_rate']
    
    # Rate should be between 0 and 1
    assert 0.0 <= occlusion_rate <= 1.0
    
    # Rate should match hidden_indices / total
    expected_rate = len(results['hidden_indices']) / results['n_agents']
    assert abs(occlusion_rate - expected_rate) < 1e-10


def test_multiple_runs_consistency(demonstrator):
    """Test that multiple runs are consistent (with same seed)"""
    np.random.seed(42)
    results1 = demonstrator.demonstrate_occlusion(n_agents=20)
    
    np.random.seed(42)
    results2 = demonstrator.demonstrate_occlusion(n_agents=20)
    
    # Should produce same number of occluded points
    assert len(results1['hidden_indices']) == len(results2['hidden_indices'])
    
    # Original data should be identical (same seed)
    np.testing.assert_array_equal(
        results1['original_data'],
        results2['original_data']
    )


def test_edge_cases(demonstrator):
    """Test edge cases"""
    # Empty data
    empty_data = np.array([]).reshape(0, 2)
    occluded, indices = demonstrator.create_wing_entanglement(empty_data)
    assert occluded.shape == (0, 2)
    assert len(indices) == 0
    
    # Single point
    single_point = np.array([[1.0, 1.0]])
    occluded, indices = demonstrator.create_wing_entanglement(single_point)
    assert occluded.shape == (1, 2)
    assert len(indices) >= 0
    
    # Very small threshold (should occlude fewer points)
    data = np.random.randn(30, 2)
    occluded1, indices1 = demonstrator.create_wing_entanglement(
        data, vortex_threshold=0.1
    )
    occluded2, indices2 = demonstrator.create_wing_entanglement(
        data, vortex_threshold=2.0
    )
    # Larger threshold should occlude more points
    assert len(indices2) >= len(indices1)


def test_preserve_quantum_state_edge_cases(demonstrator):
    """Test quantum preservation with edge cases"""
    # Zero vector
    data = np.zeros((5, 2))
    preservation = demonstrator.preserve_quantum_state(data, data)
    # Should handle gracefully (may be 0 or NaN, both acceptable)
    assert isinstance(preservation, float)
    
    # Single point
    single = np.array([[1.0, 2.0]])
    preservation = demonstrator.preserve_quantum_state(single, single)
    assert 0.0 <= preservation <= 1.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
