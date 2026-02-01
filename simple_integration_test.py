#!/usr/bin/env python3
"""
Simple Integration Test for Enhanced Training Script
Tests core functionality without Unicode issues
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from vae_model import QuantumVAE, total_loss

def test_basic_functionality():
    """Test basic VAE functionality"""
    print("Testing basic VAE functionality...")
    
    # Configuration
    input_dim = 128
    latent_dim = 32
    batch_size = 16
    n_samples = 64
    
    # Generate test data
    data = torch.randn(n_samples, input_dim)
    dataset = TensorDataset(data)
    loader = DataLoader(dataset, batch_size=batch_size)
    
    # Create model
    model = QuantumVAE(input_dim=input_dim, latent_dim=latent_dim)
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    print(f"Model created with {sum(p.numel() for p in model.parameters())} parameters")
    
    # Test forward pass
    model.eval()
    with torch.no_grad():
        batch = next(iter(loader))[0]
        outputs = model(batch)
        if len(outputs) == 4:
            recon, mu, log_var, density_matrix = outputs
        else:
            recon, mu, log_var = outputs
            density_matrix = None
        
        assert recon.shape == batch.shape, f"Reconstruction shape mismatch: {recon.shape} vs {batch.shape}"
        assert mu.shape == (batch.shape[0], latent_dim), f"Mu shape mismatch: {mu.shape}"
        assert log_var.shape == (batch.shape[0], latent_dim), f"Log var shape mismatch: {log_var.shape}"
        
        print(f"Forward pass successful: input {batch.shape} -> recon {recon.shape}, mu {mu.shape}, log_var {log_var.shape}")
        if density_matrix is not None:
            print(f"Density matrix: {density_matrix.shape}")
    
    # Test loss computation
    model.train()
    optimizer.zero_grad()
    outputs = model(batch)
    if len(outputs) == 4:
        recon, mu, log_var, density_matrix = outputs
    else:
        recon, mu, log_var = outputs
        density_matrix = torch.zeros(batch.shape[0], 32, 32)  # Create dummy density matrix
    
    total_loss_tensor, loss_dict = total_loss(recon, batch, mu, log_var, density_matrix)
    
    assert 'total' in loss_dict, "Missing 'total' in loss dict"
    assert isinstance(total_loss_tensor, torch.Tensor), "Loss should be tensor"
    assert total_loss_tensor.item() > 0, "Loss should be positive"
    
    print(f"Loss computation successful: total_loss = {total_loss_tensor.item():.4f}")
    
    # Test backward pass
    loss = total_loss_tensor
    loss.backward()
    optimizer.step()
    
    print("Backward pass successful")
    
    return True

def test_utilities():
    """Test utilities if available"""
    print("Testing utilities...")
    
    try:
        # Add utils to path
        sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))
        from utils.golden_ratio_callback import GoldenRatioCallback
        from utils.performance_monitor import PerformanceMonitor
        from utils.golden_ratio_callback import phi_regularization_loss
        
        print("Utilities imported successfully")
        
        # Test callback
        callback = GoldenRatioCallback(track_frequency=1)
        print(f"GoldenRatioCallback created: target_phi={callback.target_phi}")
        
        # Test monitor
        monitor = PerformanceMonitor(save_dir="artifacts/test")
        print("PerformanceMonitor created")
        
        # Test phi regularization loss
        latent_z = torch.randn(16, 32, requires_grad=True)
        phi_loss = phi_regularization_loss(latent_z)
        assert phi_loss.item() >= 0, "Phi loss should be non-negative"
        print(f"Phi regularization loss: {phi_loss.item():.4f}")
        
        # Test backward pass on phi loss
        phi_loss.backward()
        assert latent_z.grad is not None, "Should have gradients"
        print("Phi loss backward pass successful")
        
        print("All utility tests passed")
        return True
        
    except ImportError as e:
        print(f"Utilities not available: {e}")
        return False

def test_training_loop():
    """Test minimal training loop"""
    print("Testing training loop...")
    
    # Configuration
    input_dim = 128
    latent_dim = 32
    batch_size = 16
    n_samples = 64
    epochs = 2
    
    # Generate data
    data = torch.randn(n_samples, input_dim)
    train_data = data[:n_samples*3//4]
    val_data = data[n_samples*3//4:]
    
    train_dataset = TensorDataset(train_data)
    val_dataset = TensorDataset(val_data)
    train_loader = DataLoader(train_dataset, batch_size=batch_size)
    val_loader = DataLoader(val_dataset, batch_size=batch_size)
    
    # Create model
    model = QuantumVAE(input_dim=input_dim, latent_dim=latent_dim)
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    print(f"Training {epochs} epochs with {len(train_dataset)} train, {len(val_dataset)} val samples")
    
    # Training loop
    for epoch in range(epochs):
        # Training
        model.train()
        train_losses = []
        for batch, in train_loader:
            optimizer.zero_grad()
            outputs = model(batch)
            if len(outputs) == 4:
                recon, mu, log_var, density_matrix = outputs
            else:
                recon, mu, log_var = outputs
                density_matrix = torch.zeros(batch.shape[0], 32, 32)
            
            total_loss_tensor, loss_dict = total_loss(recon, batch, mu, log_var, density_matrix)
            loss = total_loss_tensor
            loss.backward()
            optimizer.step()
            train_losses.append(loss.item())
        
        # Validation
        model.eval()
        val_losses = []
        with torch.no_grad():
            for batch, in val_loader:
                outputs = model(batch)
                if len(outputs) == 4:
                    recon, mu, log_var, density_matrix = outputs
                else:
                    recon, mu, log_var = outputs
                    density_matrix = torch.zeros(batch.shape[0], 32, 32)
                
                total_loss_tensor, loss_dict = total_loss(recon, batch, mu, log_var, density_matrix)
                val_losses.append(total_loss_tensor.item())
        
        train_avg = np.mean(train_losses)
        val_avg = np.mean(val_losses)
        
        print(f"Epoch {epoch+1}/{epochs}: Train Loss = {train_avg:.4f}, Val Loss = {val_avg:.4f}")
    
    print("Training loop completed successfully")
    return True

def main():
    """Main test function"""
    print("="*60)
    print("INTEGRATION TEST FOR ENHANCED TRAINING")
    print("="*60)
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Basic functionality
    try:
        if test_basic_functionality():
            tests_passed += 1
            print("TEST 1 PASSED: Basic functionality")
        else:
            print("TEST 1 FAILED: Basic functionality")
    except Exception as e:
        print(f"TEST 1 FAILED: {e}")
    
    print("-" * 40)
    
    # Test 2: Utilities
    try:
        if test_utilities():
            tests_passed += 1
            print("TEST 2 PASSED: Utilities")
        else:
            print("TEST 2 SKIPPED: Utilities not available")
            total_tests -= 1  # Don't count if utilities not available
    except Exception as e:
        print(f"TEST 2 FAILED: {e}")
    
    print("-" * 40)
    
    # Test 3: Training loop
    try:
        if test_training_loop():
            tests_passed += 1
            print("TEST 3 PASSED: Training loop")
        else:
            print("TEST 3 FAILED: Training loop")
    except Exception as e:
        print(f"TEST 3 FAILED: {e}")
    
    print("="*60)
    print(f"RESULTS: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("SUCCESS: All integration tests passed!")
        return 0
    else:
        print("FAILURE: Some integration tests failed!")
        return 1

if __name__ == "__main__":
    exit(main())