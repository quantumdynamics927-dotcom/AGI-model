"""
Tests for Performance Monitor utility

Tests metric tracking, visualization, and export functionality.
"""

import pytest
import numpy as np
from pathlib import Path
import tempfile
import shutil
import json

# Add parent directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.performance_monitor import PerformanceMonitor


@pytest.fixture
def temp_dir():
    """Create temporary directory for test outputs"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_train_metrics():
    """Sample training metrics"""
    return {
        'total_loss': 0.5,
        'recon': 0.3,
        'kl': 0.1,
        'hamming': 0.05,
        'coherence': 0.02,
        'hw': 0.01,
        'mixed_state': 0.1,
        'fidelity': 0.05,
        'entropy': 0.03
    }


@pytest.fixture
def sample_val_metrics():
    """Sample validation metrics"""
    return {
        'total_loss': 0.52,
        'recon': 0.32,
        'kl': 0.11,
        'hamming': 0.06,
        'coherence': 0.03,
        'hw': 0.01,
        'mixed_state': 0.11,
        'fidelity': 0.06,
        'entropy': 0.04
    }


@pytest.fixture
def sample_quantum_metrics():
    """Sample quantum metrics"""
    return {
        'phi_resonance': 0.85,
        'quantum_fidelity': 0.92,
        'entanglement_entropy': 1.2
    }


def test_monitor_initialization(temp_dir):
    """Test monitor initialization"""
    monitor = PerformanceMonitor(save_dir=str(temp_dir))
    
    assert monitor.save_dir == temp_dir
    assert len(monitor.epochs) == 0
    assert len(monitor.train_metrics) > 0
    assert len(monitor.val_metrics) > 0


def test_metric_recording(temp_dir, sample_train_metrics, sample_val_metrics):
    """Test metric recording"""
    monitor = PerformanceMonitor(save_dir=str(temp_dir))
    
    # Record metrics
    monitor.record_epoch(
        epoch=0,
        train_metrics=sample_train_metrics,
        val_metrics=sample_val_metrics
    )
    
    assert len(monitor.epochs) == 1
    assert monitor.epochs[0] == 0
    assert len(monitor.train_metrics['total_loss']) == 1
    assert monitor.train_metrics['total_loss'][0] == 0.5
    assert monitor.val_metrics['total_loss'][0] == 0.52


def test_quantum_metrics_recording(temp_dir, sample_train_metrics, 
                                   sample_val_metrics, sample_quantum_metrics):
    """Test quantum metrics recording"""
    monitor = PerformanceMonitor(save_dir=str(temp_dir))
    
    monitor.record_epoch(
        epoch=0,
        train_metrics=sample_train_metrics,
        val_metrics=sample_val_metrics,
        quantum_metrics=sample_quantum_metrics
    )
    
    assert 'phi_resonance' in monitor.quantum_metrics
    assert monitor.quantum_metrics['phi_resonance'][0] == 0.85


def test_plot_generation(temp_dir, sample_train_metrics, sample_val_metrics):
    """Test plot generation"""
    monitor = PerformanceMonitor(save_dir=str(temp_dir))
    
    # Record multiple epochs
    for epoch in range(5):
        train = {k: v * (1 - epoch * 0.01) for k, v in sample_train_metrics.items()}
        val = {k: v * (1 - epoch * 0.01) for k, v in sample_val_metrics.items()}
        monitor.record_epoch(epoch, train, val)
    
    # Generate plot
    plot_path = temp_dir / 'test_metrics.png'
    monitor.plot_all_metrics(save_path=str(plot_path))
    
    # Check plot was created
    assert plot_path.exists()


def test_quantum_metrics_plotting(temp_dir, sample_train_metrics, sample_val_metrics,
                                  sample_quantum_metrics):
    """Test quantum metrics plotting"""
    monitor = PerformanceMonitor(save_dir=str(temp_dir))
    
    # Record with quantum metrics
    for epoch in range(5):
        monitor.record_epoch(
            epoch,
            sample_train_metrics,
            sample_val_metrics,
            sample_quantum_metrics
        )
    
    plot_path = temp_dir / 'test_quantum.png'
    monitor.plot_quantum_metrics(save_path=str(plot_path))
    
    assert plot_path.exists()


def test_json_export(temp_dir, sample_train_metrics, sample_val_metrics):
    """Test JSON export"""
    monitor = PerformanceMonitor(save_dir=str(temp_dir))
    
    # Record metrics
    for epoch in range(3):
        monitor.record_epoch(epoch, sample_train_metrics, sample_val_metrics)
    
    # Export to JSON
    json_path = temp_dir / 'test_metrics.json'
    monitor.save_metrics_json(save_path=str(json_path))
    
    # Check JSON was created and is valid
    assert json_path.exists()
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    assert 'epochs' in data
    assert 'train_metrics' in data
    assert 'val_metrics' in data
    assert len(data['epochs']) == 3


def test_best_epoch_detection(temp_dir, sample_train_metrics, sample_val_metrics):
    """Test best epoch detection"""
    monitor = PerformanceMonitor(save_dir=str(temp_dir))
    
    # Record metrics with varying loss
    losses = [0.6, 0.5, 0.4, 0.45, 0.35]  # Best at epoch 4
    for epoch, loss in enumerate(losses):
        train = sample_train_metrics.copy()
        val = sample_val_metrics.copy()
        train['total_loss'] = loss
        val['total_loss'] = loss + 0.02
        monitor.record_epoch(epoch, train, val)
    
    best_epoch, best_value = monitor.get_best_epoch('total_loss', 'val')
    
    assert best_epoch == 4
    assert best_value == pytest.approx(0.37, rel=0.01)


def test_get_summary(temp_dir, sample_train_metrics, sample_val_metrics,
                    sample_quantum_metrics):
    """Test summary generation"""
    monitor = PerformanceMonitor(save_dir=str(temp_dir))
    
    # Record multiple epochs
    for epoch in range(10):
        monitor.record_epoch(
            epoch,
            sample_train_metrics,
            sample_val_metrics,
            sample_quantum_metrics
        )
    
    summary = monitor.get_summary()
    
    assert 'total_epochs' in summary
    assert 'best_val_loss_epoch' in summary
    assert 'best_val_loss' in summary
    assert 'final_val_loss' in summary
    assert 'quantum_metrics' in summary
    assert summary['total_epochs'] == 10


def test_empty_summary():
    """Test summary with no data"""
    monitor = PerformanceMonitor()
    summary = monitor.get_summary()
    
    assert summary['status'] == 'No data collected'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
