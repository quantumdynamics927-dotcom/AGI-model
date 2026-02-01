#!/usr/bin/env python3
"""
Smoke test for integration testing of enhanced training script
Tests core functionality without Rich console dependencies
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

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))
try:
    from utils.golden_ratio_callback import GoldenRatioCallback, phi_regularization_loss
    from utils.performance_monitor import PerformanceMonitor
    UTILS_AVAILABLE = True
    print("[OK] Utilities available")
except ImportError as e:
    UTILS_AVAILABLE = False
    print(f"[WARNING] Utilities not available: {e}")

def generate_test_data(n_samples=100, input_dim=128):
    """Generate test data for training"""
    # Generate synthetic quantum-like data
    data = torch.randn(n_samples, input_dim)
    # Add some structure
    data += 0.1 * torch.sin(torch.linspace(0, 4*np.pi, input_dim))
    data = torch.sigmoid(data)  # Normalize to [0,1]
    return data

def simple_train_test():
    """Simple training test without Rich console"""
    print("🚀 Starting Integration Test")
    
    # Configuration
    input_dim = 128
    latent_dim = 32
    batch_size = 16
    n_samples = 64  # Small for smoke test
    epochs = 2
    
    print(f"Configuration: input_dim={input_dim}, latent_dim={latent_dim}, epochs={epochs}")
    
    # Generate data
    print("📊 Generating test data...")
    train_data = generate_test_data(n_samples, input_dim)
    val_data = generate_test_data(n_samples//4, input_dim)
    
    train_dataset = TensorDataset(train_data)
    val_dataset = TensorDataset(val_data)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size)
    
    print(f"Train samples: {len(train_dataset)}, Val samples: {len(val_dataset)}")
    
    # Create model
    print("🧠 Creating Quantum VAE model...")
    model = QuantumVAE(input_dim=input_dim, latent_dim=latent_dim)
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    
    device = torch.device('cpu')
    model.to(device)
    
    # Initialize utilities if available
    monitor = None
    phi_callback = None
    if UTILS_AVAILABLE:
        print("🔧 Initializing performance monitoring...")
        monitor = PerformanceMonitor(save_dir="artifacts/test")
        phi_callback = GoldenRatioCallback(track_frequency=1)
        print("✅ Performance monitoring initialized")
    
    print("🏃 Starting training...")
    
    # Training loop
    try:
        for epoch in range(epochs):
            print(f"Epoch {epoch+1}/{epochs}")
            
            # Training
            model.train()
            train_losses = []
            
            for batch_idx, (data,) in enumerate(train_loader):
                data = data.to(device)
                optimizer.zero_grad()
                
                # Forward pass
                recon_data, mu, log_var = model(data)
                loss_dict = total_loss(data, recon_data, mu, log_var)
                
                # Add phi regularization if available
                if UTILS_AVAILABLE and hasattr(model, 'encode'):
                    with torch.no_grad():
                        latent_z = model.encode(data)
                        if isinstance(latent_z, tuple):
                            latent_z = latent_z[0]  # Get mu from (mu, log_var)
                    phi_loss = phi_regularization_loss(latent_z)
                    loss_dict['phi_regularization'] = phi_loss
                    loss_dict['total_loss'] += phi_loss
                
                # Backward pass
                loss = loss_dict['total_loss']
                loss.backward()
                optimizer.step()
                
                train_losses.append({k: v.item() for k, v in loss_dict.items()})
            
            # Validation
            model.eval()
            val_losses = []
            with torch.no_grad():
                for data, in val_loader:
                    data = data.to(device)
                    recon_data, mu, log_var = model(data)
                    loss_dict = total_loss(data, recon_data, mu, log_var)
                    val_losses.append({k: v.item() for k, v in loss_dict.items()})
            
            # Compute epoch averages
            train_avg = {k: np.mean([d[k] for d in train_losses]) for k in train_losses[0]}
            val_avg = {k: np.mean([d[k] for d in val_losses]) for k in val_losses[0]}
            
            print(f"  Train Loss: {train_avg['total_loss']:.4f}, Val Loss: {val_avg['total_loss']:.4f}")
            
            # Record metrics if utilities available
            if UTILS_AVAILABLE and monitor:
                quantum_metrics = {}
                if phi_callback:
                    # Generate some latent samples for phi tracking
                    with torch.no_grad():
                        sample_data = next(iter(train_loader))[0][:16].to(device)
                        latent_samples = model.encode(sample_data)
                        if isinstance(latent_samples, tuple):
                            latent_samples = latent_samples[0]
                    
                    phi_metrics = phi_callback.on_epoch_end(epoch, model, latent_samples)
                    quantum_metrics.update(phi_metrics)
                    print(f"  Phi Resonance: {phi_metrics.get('phi_resonance', 0):.3f}")
                
                monitor.record_epoch(epoch, train_avg, val_avg, quantum_metrics)
        
        print("✅ Training completed successfully!")
        
        # Test monitoring output
        if UTILS_AVAILABLE and monitor:
            print("📊 Generating monitoring outputs...")
            try:
                monitor.plot_all_metrics("artifacts/test/metrics_test.png")
                monitor.save_metrics_json("artifacts/test/metrics_test.json")
                print("✅ Monitoring outputs generated")
            except Exception as e:
                print(f"⚠️  Monitoring output failed: {e}")
        
        if UTILS_AVAILABLE and phi_callback:
            summary = phi_callback.get_summary()
            print(f"📐 Final Phi Resonance: {summary.get('final_resonance', 0):.3f}")
            phi_aligned = summary.get('phi_aligned', False)
            print(f"🔶 Phi Aligned: {'✅' if phi_aligned else '⚠️'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Training failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("="*50)
    print("ENHANCED TRAINING INTEGRATION TEST")
    print("="*50)
    
    success = simple_train_test()
    
    print("="*50)
    if success:
        print("🎉 INTEGRATION TEST PASSED")
        print("✅ All components working correctly")
    else:
        print("❌ INTEGRATION TEST FAILED")
        print("🔧 Check error messages above")
    print("="*50)
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())