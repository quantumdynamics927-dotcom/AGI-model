"""
Tests for AGI Model Core Package

This module tests the core model package functionality:
1. Model exports and imports
2. QuantumVAE model accessibility
3. Loss function exports
4. Optimizer exports
5. Package structure validation
"""
import unittest
import sys
import os
import torch
import numpy as np
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestAGIModelCorePackage(unittest.TestCase):
    """Tests for the agi_model_core package structure."""

    def test_package_import(self):
        """Test that agi_model_core package can be imported."""
        try:
            import packages.agi_model_core
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import packages.agi_model_core: {e}")
        print("TestAGIModelCorePackage: test_package_import PASSED")

    def test_init_exports(self):
        """Test that __init__.py exports the correct modules."""
        from packages.agi_model_core import (
            QuantumVAE,
            HybridQuantumOptimizer,
            total_loss,
        )
        
        # Check that exports are not None
        self.assertIsNotNone(QuantumVAE)
        self.assertIsNotNone(HybridQuantumOptimizer)
        self.assertIsNotNone(total_loss)
        print("TestAGIModelCorePackage: test_init_exports PASSED")

    def test_quantum_vae_import(self):
        """Test that QuantumVAE can be imported from package."""
        from packages.agi_model_core import QuantumVAE
        
        # Check that it's a class
        self.assertIsInstance(QuantumVAE, type)
        print("TestAGIModelCorePackage: test_quantum_vae_import PASSED")

    def test_optimizer_import(self):
        """Test that HybridQuantumOptimizer can be imported."""
        from packages.agi_model_core import HybridQuantumOptimizer
        
        # Check that it's a class
        self.assertIsInstance(HybridQuantumOptimizer, type)
        print("TestAGIModelCorePackage: test_optimizer_import PASSED")

    def test_loss_function_import(self):
        """Test that total_loss function can be imported."""
        from packages.agi_model_core import total_loss
        
        # Check that it's callable
        self.assertTrue(callable(total_loss))
        print("TestAGIModelCorePackage: test_loss_function_import PASSED")


class TestQuantumVAEFromPackage(unittest.TestCase):
    """Tests for QuantumVAE model imported from package."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        from packages.agi_model_core import QuantumVAE
        cls.QuantumVAE = QuantumVAE
        cls.model = QuantumVAE()

    def test_model_instantiation(self):
        """Test that QuantumVAE can be instantiated."""
        self.assertIsNotNone(self.model)
        print("TestQuantumVAEFromPackage: test_model_instantiation PASSED")

    def test_model_has_encoder(self):
        """Test that model has encoder method."""
        self.assertTrue(hasattr(self.model, 'encode'))
        self.assertTrue(callable(getattr(self.model, 'encode')))
        print("TestQuantumVAEFromPackage: test_model_has_encoder PASSED")

    def test_model_has_decoder(self):
        """Test that model has decoder method."""
        self.assertTrue(hasattr(self.model, 'decode'))
        self.assertTrue(callable(getattr(self.model, 'decode')))
        print("TestQuantumVAEFromPackage: test_model_has_decoder PASSED")

    def test_model_has_forward(self):
        """Test that model has forward method."""
        self.assertTrue(hasattr(self.model, 'forward'))
        self.assertTrue(callable(getattr(self.model, 'forward')))
        print("TestQuantumVAEFromPackage: test_model_has_forward PASSED")

    def test_model_encoder_output(self):
        """Test encoder output dimensions."""
        batch_size = 2
        input_dim = 128
        test_input = torch.randn(batch_size, input_dim)
        
        with torch.no_grad():
            mu, log_var = self.model.encode(test_input)
        
        # Check output dimensions
        self.assertEqual(mu.shape[0], batch_size)
        self.assertEqual(log_var.shape[0], batch_size)
        print("TestQuantumVAEFromPackage: test_model_encoder_output PASSED")

    def test_model_decoder_output(self):
        """Test decoder output dimensions."""
        batch_size = 2
        latent_dim = 32
        latent_code = torch.randn(batch_size, latent_dim)
        
        with torch.no_grad():
            output = self.model.decode(latent_code)
        
        # Check output dimensions (should match input: 128)
        self.assertEqual(output.shape[0], batch_size)
        self.assertEqual(output.shape[1], 128)
        print("TestQuantumVAEFromPackage: test_model_decoder_output PASSED")

    def test_model_forward_pass(self):
        """Test complete forward pass through model."""
        batch_size = 2
        input_dim = 128
        test_input = torch.randn(batch_size, input_dim)
        
        with torch.no_grad():
            output, mu, log_var = self.model(test_input)
        
        # Check output dimensions
        self.assertEqual(output.shape, (batch_size, input_dim))
        self.assertEqual(mu.shape[0], batch_size)
        self.assertEqual(log_var.shape[0], batch_size)
        print("TestQuantumVAEFromPackage: test_model_forward_pass PASSED")

    def test_model_reparameterization(self):
        """Test reparameterization trick."""
        batch_size = 2
        latent_dim = 32
        mu = torch.randn(batch_size, latent_dim)
        log_var = torch.randn(batch_size, latent_dim)
        
        with torch.no_grad():
            latent = self.model.reparameterize(mu, log_var)
        
        # Check output dimensions
        self.assertEqual(latent.shape, (batch_size, latent_dim))
        print("TestQuantumVAEFromPackage: test_model_reparameterization PASSED")


class TestHybridQuantumOptimizerFromPackage(unittest.TestCase):
    """Tests for HybridQuantumOptimizer imported from package."""

    def test_optimizer_instantiation(self):
        """Test that HybridQuantumOptimizer can be instantiated."""
        from packages.agi_model_core import HybridQuantumOptimizer
        
        optimizer = HybridQuantumOptimizer()
        self.assertIsNotNone(optimizer)
        print("TestHybridQuantumOptimizerFromPackage: test_optimizer_instantiation PASSED")

    def test_optimizer_has_methods(self):
        """Test that optimizer has required methods."""
        from packages.agi_model_core import HybridQuantumOptimizer
        
        optimizer = HybridQuantumOptimizer()
        
        # Check for common optimizer methods
        self.assertTrue(hasattr(optimizer, 'step') or callable(getattr(optimizer, 'optimize', None)))
        print("TestHybridQuantumOptimizerFromPackage: test_optimizer_has_methods PASSED")


class TestTotalLossFromPackage(unittest.TestCase):
    """Tests for total_loss function imported from package."""

    def test_loss_function_signature(self):
        """Test that total_loss has correct signature."""
        from packages.agi_model_core import total_loss
        
        # Should be callable
        self.assertTrue(callable(total_loss))
        print("TestTotalLossFromPackage: test_loss_function_signature PASSED")

    def test_loss_function_computation(self):
        """Test that total_loss computes a valid loss value."""
        from packages.agi_model_core import total_loss
        
        # Create dummy inputs
        batch_size = 2
        input_dim = 128
        recon = torch.randn(batch_size, input_dim)
        original = torch.randn(batch_size, input_dim)
        mu = torch.randn(batch_size, 32)
        log_var = torch.randn(batch_size, 32)
        
        # Compute loss
        loss = total_loss(recon, original, mu, log_var)
        
        # Loss should be a scalar tensor
        self.assertIsInstance(loss, torch.Tensor)
        self.assertEqual(loss.dim(), 0)
        
        # Loss should be finite and non-negative
        self.assertTrue(torch.isfinite(loss))
        self.assertGreaterEqual(loss.item(), 0)
        print("TestTotalLossFromPackage: test_loss_function_computation PASSED")


if __name__ == '__main__':
    unittest.main(verbosity=2)
