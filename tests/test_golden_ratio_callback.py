"""
Tests for Golden Ratio Callback utility

Tests phi-resonance tracking, visualization, and regularization.
"""

import pytest
import torch
import numpy as np
from pathlib import Path
import tempfile
import shutil

# Add parent directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.golden_ratio_callback import GoldenRatioCallback, phi_regularization_loss
from vae_model import QuantumVAE


@pytest.fixture
def temp_dir():
    """Create temporary directory for test outputs"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_model():
    """Create sample QuantumVAE model for testing"""
    return QuantumVAE(input_dim=128, latent_dim=32)


@pytest.fixture
def sample_latent():
    """Generate sample latent representations"""
    return torch.randn(16, 32)  # (batch, latent_dim)


def test_phi_callback_initialization(temp_dir):
    """Test callback initialization"""
    callback = GoldenRatioCallback(
        target_phi=1.618033988749895,
        resonance_threshold=0.7,
        save_dir=str(temp_dir),
        track_frequency=5
    )
    
    assert callback.target_phi == 1.618033988749895
    assert callback.resonance_threshold == 0.7
    assert callback.track_frequency == 5
    assert len(callback.epochs) == 0
    assert len(callback.resonance_scores) == 0


def test_resonance_tracking(sample_model, sample_latent):
    """Test resonance tracking functionality"""
    callback = GoldenRatioCallback(track_frequency=1)
    
    # Test tracking
    metrics = callback.on_epoch_end(
        epoch=0,
        model=sample_model,
        latent_samples=sample_latent
    )
    
    assert 'phi_resonance' in metrics
    assert 'phi_deviation' in metrics
    assert 'phi_aligned' in metrics
    assert isinstance(metrics['phi_resonance'], float)
    assert 0.0 <= metrics['phi_resonance'] <= 1.0


def test_resonance_tracking_frequency(sample_model, sample_latent):
    """Test that tracking respects frequency setting"""
    callback = GoldenRatioCallback(track_frequency=5)
    
    # Epoch 0 should be tracked (first epoch)
    metrics = callback.on_epoch_end(0, sample_model, sample_latent)
    assert len(metrics) > 0
    
    # Epoch 1 should not be tracked
    metrics = callback.on_epoch_end(1, sample_model, sample_latent)
    assert len(metrics) == 0
    
    # Epoch 5 should be tracked
    metrics = callback.on_epoch_end(5, sample_model, sample_latent)
    assert len(metrics) > 0


def test_resonance_plotting(temp_dir, sample_model, sample_latent):
    """Test resonance history plotting"""
    callback = GoldenRatioCallback(save_dir=str(temp_dir), track_frequency=1)
    
    # Track a few epochs
    for epoch in range(5):
        callback.on_epoch_end(epoch, sample_model, sample_latent)
    
    # Generate plot
    plot_path = temp_dir / 'test_resonance.png'
    callback.plot_resonance_history(save_path=str(plot_path))
    
    # Check plot was created
    assert plot_path.exists()


def test_phi_regularization_loss():
    """Test phi regularization loss function"""
    # Test with requires_grad to ensure it's differentiable
    latent_z = torch.randn(32, 16, requires_grad=True)  # (batch, latent_dim)
    
    loss = phi_regularization_loss(latent_z, target_phi=1.618033988749895, weight=0.1)
    
    assert isinstance(loss, torch.Tensor)
    assert loss.item() >= 0.0
    assert loss.requires_grad  # Should be differentiable when input has gradients
    
    # Test that we can backpropagate
    loss.backward()
    assert latent_z.grad is not None


def test_resonance_from_weights(sample_model):
    """Test fallback resonance computation from weights"""
    callback = GoldenRatioCallback()
    
    # Track without latent samples (should use weight-based method)
    metrics = callback.on_epoch_end(epoch=0, model=sample_model, latent_samples=None)
    
    assert 'phi_resonance' in metrics
    assert isinstance(metrics['phi_resonance'], float)


def test_get_summary(temp_dir, sample_model, sample_latent):
    """Test summary generation"""
    callback = GoldenRatioCallback(save_dir=str(temp_dir), track_frequency=1)
    
    # Track a few epochs
    for epoch in range(10):
        callback.on_epoch_end(epoch, sample_model, sample_latent)
    
    summary = callback.get_summary()
    
    assert 'epochs_tracked' in summary
    assert 'mean_resonance' in summary
    assert 'max_resonance' in summary
    assert 'min_resonance' in summary
    assert 'final_resonance' in summary
    assert summary['epochs_tracked'] == 10


def test_empty_summary():
    """Test summary with no data"""
    callback = GoldenRatioCallback()
    summary = callback.get_summary()
    
    assert summary['status'] == 'No data collected'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
