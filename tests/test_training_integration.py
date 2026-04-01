"""
Integration tests for training script with new utilities

Tests that the enhanced training script works correctly with:
- Golden ratio callback
- Performance monitor
- All new features
"""

import pytest
import torch
import numpy as np
import tempfile
import shutil
from pathlib import Path
import sys
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from vae_model import QuantumVAE, total_loss
from utils.golden_ratio_callback import GoldenRatioCallback
from utils.performance_monitor import PerformanceMonitor
from torch.utils.data import DataLoader, TensorDataset


@pytest.fixture
def temp_dir():
    """Create temporary directory for test outputs"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_data():
    """Generate sample training data"""
    np.random.seed(42)
    data = np.random.rand(100, 128).astype(np.float32)
    train_data = data[:80]
    val_data = data[80:]
    return train_data, val_data


@pytest.fixture
def sample_model():
    """Create sample QuantumVAE model"""
    return QuantumVAE(input_dim=128, latent_dim=32, use_phi_init=True)


@pytest.fixture
def sample_loaders(sample_data):
    """Create sample data loaders"""
    train_data, val_data = sample_data
    train_dataset = TensorDataset(torch.from_numpy(train_data))
    val_dataset = TensorDataset(torch.from_numpy(val_data))
    train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=16, shuffle=False)
    return train_loader, val_loader


def test_model_with_phi_init(sample_model):
    """Test that model initializes correctly with phi-aware init"""
    # Model should initialize without errors
    assert sample_model is not None
    assert sample_model.use_phi_init == True
    
    # Test forward pass
    x = torch.randn(4, 128)
    recon, mu, log_var, density = sample_model(x, return_density=True)
    
    assert recon.shape == x.shape
    assert mu.shape == (4, 32)
    assert log_var.shape == (4, 32)
    assert density.shape == (4, 32, 32)


def test_phi_resonance_computation(sample_model):
    """Test phi-resonance computation from model"""
    x = torch.randn(8, 128)
    recon, mu, log_var, density = sample_model(x, return_density=True)
    
    # Test compute_phi_resonance method
    if hasattr(sample_model, 'compute_phi_resonance'):
        resonance = sample_model.compute_phi_resonance(mu)
        assert 0.0 <= resonance <= 1.0
        assert isinstance(resonance, float)


def test_golden_ratio_callback_integration(sample_model, sample_loaders, temp_dir):
    """Test golden ratio callback integrated with training loop"""
    train_loader, val_loader = sample_loaders
    callback = GoldenRatioCallback(save_dir=str(temp_dir), track_frequency=1)
    
    # Simulate a few training steps
    sample_model.eval()
    with torch.no_grad():
        for epoch in range(3):
            # Get a batch
            batch_x = next(iter(train_loader))[0]
            recon, mu, log_var, density = sample_model(batch_x, return_density=True)
            
            # Track resonance
            metrics = callback.on_epoch_end(epoch, sample_model, mu)
            
            assert 'phi_resonance' in metrics
            assert len(callback.epochs) == epoch + 1
    
    # Verify summary
    summary = callback.get_summary()
    assert summary['epochs_tracked'] == 3


def test_performance_monitor_integration(sample_model, sample_loaders, temp_dir):
    """Test performance monitor integrated with training loop"""
    train_loader, val_loader = sample_loaders
    monitor = PerformanceMonitor(save_dir=str(temp_dir))
    
    # Simulate training metrics
    for epoch in range(3):
        train_metrics = {
            'total_loss': 0.5 - epoch * 0.05,
            'recon': 0.3 - epoch * 0.03,
            'kl': 0.1,
            'hamming': 0.05,
            'coherence': 0.02,
            'hw': 0.01,
            'mixed_state': 0.1,
            'fidelity': 0.05 if epoch > 1 else 0.0,
            'entropy': 0.03 if epoch > 1 else 0.0
        }
        val_metrics = {k: v + 0.02 for k, v in train_metrics.items()}
        quantum_metrics = {'phi_resonance': 0.7 + epoch * 0.05} if epoch > 0 else None
        
        monitor.record_epoch(epoch, train_metrics, val_metrics, quantum_metrics)
    
    # Verify metrics recorded
    assert len(monitor.epochs) == 3
    assert len(monitor.train_metrics['total_loss']) == 3
    assert len(monitor.val_metrics['total_loss']) == 3
    
    # Test best epoch detection
    best_epoch, best_loss = monitor.get_best_epoch('total_loss', 'val')
    assert best_epoch == 2  # Last epoch should have lowest loss
    assert best_loss < 0.5
    
    # Test summary
    summary = monitor.get_summary()
    assert summary['total_epochs'] == 3


def test_training_step_with_utilities(sample_model, sample_loaders):
    """Test a single training step with new utilities"""
    train_loader, _ = sample_loaders
    optimizer = torch.optim.Adam(sample_model.parameters(), lr=1e-3)
    
    sample_model.train()
    batch_x = next(iter(train_loader))[0]
    
    # Forward pass
    optimizer.zero_grad()
    recon, mu, log_var, density = sample_model(batch_x, return_density=True)
    
    # Compute loss
    total_loss_val, loss_dict = total_loss(
        recon, batch_x, mu, log_var, density, 
        include_advanced=True
    )
    
    # Add phi regularization if available
    try:
        from utils.golden_ratio_callback import phi_regularization_loss
        phi_loss = phi_regularization_loss(mu, weight=0.05)
        total_loss_val += phi_loss
    except ImportError:
        pass
    
    # Backward pass
    total_loss_val.backward()
    optimizer.step()
    
    # Verify loss computed correctly
    assert isinstance(total_loss_val.item(), float)
    assert total_loss_val.item() >= 0.0
    assert 'total' in loss_dict


def test_artifact_generation(temp_dir, sample_model, sample_loaders):
    """Test that artifacts are generated correctly"""
    train_loader, val_loader = sample_loaders
    callback = GoldenRatioCallback(save_dir=str(temp_dir / 'phi'), track_frequency=1)
    monitor = PerformanceMonitor(save_dir=str(temp_dir / 'metrics'))
    
    # Simulate a few epochs
    sample_model.eval()
    with torch.no_grad():
        for epoch in range(5):
            batch_x = next(iter(train_loader))[0]
            recon, mu, log_var, density = sample_model(batch_x, return_density=True)
            
            # Track metrics
            phi_metrics = callback.on_epoch_end(epoch, sample_model, mu)
            train_metrics = {
                'total_loss': 0.5 - epoch * 0.01,
                'recon': 0.3, 'kl': 0.1, 'hamming': 0.05,
                'coherence': 0.02, 'hw': 0.01, 'mixed_state': 0.1,
                'fidelity': 0.05 if epoch > 2 else 0.0,
                'entropy': 0.03 if epoch > 2 else 0.0
            }
            val_metrics = {k: v + 0.01 for k, v in train_metrics.items()}
            monitor.record_epoch(epoch, train_metrics, val_metrics, phi_metrics)
    
    # Generate plots
    callback.plot_resonance_history(save_path=str(temp_dir / 'phi' / 'resonance.png'))
    monitor.plot_all_metrics(save_path=str(temp_dir / 'metrics' / 'all_metrics.png'))
    monitor.plot_quantum_metrics(save_path=str(temp_dir / 'metrics' / 'quantum.png'))
    
    # Export JSON
    monitor.save_metrics_json(save_path=str(temp_dir / 'metrics' / 'metrics.json'))
    
    # Verify artifacts created
    assert (temp_dir / 'phi' / 'resonance.png').exists()
    assert (temp_dir / 'metrics' / 'all_metrics.png').exists()
    assert (temp_dir / 'metrics' / 'quantum.png').exists()
    assert (temp_dir / 'metrics' / 'metrics.json').exists()


def test_backward_compatibility():
    """Test that old code still works without new utilities"""
    # Model should work without phi_init
    model_old = QuantumVAE(input_dim=128, latent_dim=32, use_phi_init=False)
    x = torch.randn(4, 128)
    recon, mu, log_var, density = model_old(x, return_density=True)
    assert recon.shape == x.shape
    
    # Training should work without callbacks
    optimizer = torch.optim.Adam(model_old.parameters(), lr=1e-3)
    model_old.train()
    optimizer.zero_grad()
    recon, mu, log_var, density = model_old(x, return_density=True)
    loss, _ = total_loss(recon, x, mu, log_var, density)
    loss.backward()
    optimizer.step()
    
    # Should complete without errors
    assert loss.item() >= 0.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
