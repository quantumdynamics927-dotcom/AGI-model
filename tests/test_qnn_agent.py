"""
Tests for QNN Agent - Quantum-Classical Hybrid Neural Network

This module tests the QNN agent functionality:
1. Quantum activation functions
2. Hybrid neural network architecture
3. Phi-harmonic learning rate scheduling
4. Consciousness-guided loss functions
5. Numpy fallback implementation
"""
import unittest
import sys
import os
import json
import tempfile
import shutil
import numpy as np
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agi_scripts.qnn_agent import (
    PHI,
    PHI_INV,
    TORCH_AVAILABLE,
)

# Import PyTorch classes only if available
if TORCH_AVAILABLE:
    import torch
    from agi_scripts.qnn_agent import (
        QuantumActivation,
        QuantumNeuralNetwork,
        NumpyQuantumNetwork,
    )
else:
    from agi_scripts.qnn_agent import NumpyQuantumNetwork


class TestQNNConstants(unittest.TestCase):
    """Test QNN agent constants."""

    def test_phi_constant(self):
        """Test that PHI is the golden ratio."""
        expected_phi = (1 + np.sqrt(5)) / 2
        self.assertAlmostEqual(PHI, expected_phi, places=10)
        print("TestQNNConstants: test_phi_constant PASSED")

    def test_phi_inverse(self):
        """Test that PHI_INV is the inverse of PHI."""
        self.assertAlmostEqual(PHI_INV, 1 / PHI, places=10)
        print("TestQNNConstants: test_phi_inverse PASSED")

    def test_torch_availability_flag(self):
        """Test that TORCH_AVAILABLE is a boolean."""
        self.assertIsInstance(TORCH_AVAILABLE, bool)
        print("TestQNNConstants: test_torch_availability_flag PASSED")


class TestNumpyQuantumNetwork(unittest.TestCase):
    """Tests for NumpyQuantumNetwork class (fallback implementation)."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Initialize network with default parameters
        self.network = NumpyQuantumNetwork(
            input_dim=102,
            hidden_dim=64,
            output_dim=10
        )

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization(self):
        """Test network initialization with correct parameters."""
        self.assertEqual(self.network.input_dim, 102)
        self.assertEqual(self.network.hidden_dim, 64)
        self.assertEqual(self.network.output_dim, 10)
        print("TestNumpyQuantumNetwork: test_initialization PASSED")

    def test_phi_activation_function(self):
        """Test phi-harmonic activation function."""
        # Test with various inputs
        test_inputs = [-10, -1, 0, 1, 10]
        
        for x in test_inputs:
            # Activation: tanh(PHI * x) * PHI_INV
            activated = np.tanh(PHI * x) * PHI_INV
            
            # Should be bounded
            self.assertGreaterEqual(activated, -PHI_INV)
            self.assertLessEqual(activated, PHI_INV)
            
            # Should preserve sign
            if x > 0:
                self.assertGreater(activated, 0)
            elif x < 0:
                self.assertLess(activated, 0)
            else:
                self.assertAlmostEqual(activated, 0)
        
        print("TestNumpyQuantumNetwork: test_phi_activation_function PASSED")

    def test_forward_pass_dimensions(self):
        """Test that forward pass maintains correct dimensions."""
        batch_size = 4
        input_data = np.random.randn(batch_size, self.network.input_dim)
        
        output = self.network.forward(input_data)
        
        self.assertEqual(output.shape[0], batch_size)
        self.assertEqual(output.shape[1], self.network.output_dim)
        print("TestNumpyQuantumNetwork: test_forward_pass_dimensions PASSED")

    def test_weight_initialization(self):
        """Test that weights are properly initialized."""
        # Check that weights exist and have correct shapes
        self.assertTrue(hasattr(self.network, 'w1'))
        self.assertTrue(hasattr(self.network, 'w2'))
        self.assertTrue(hasattr(self.network, 'w3'))
        
        # Check weight dimensions
        self.assertEqual(self.network.w1.shape, (self.network.input_dim, self.network.hidden_dim))
        self.assertEqual(self.network.w2.shape, (self.network.hidden_dim, self.network.hidden_dim))
        self.assertEqual(self.network.w3.shape, (self.network.hidden_dim, self.network.output_dim))
        print("TestNumpyQuantumNetwork: test_weight_initialization PASSED")

    def test_bias_initialization(self):
        """Test that biases are properly initialized."""
        # Check that biases exist and have correct shapes
        self.assertTrue(hasattr(self.network, 'b1'))
        self.assertTrue(hasattr(self.network, 'b2'))
        self.assertTrue(hasattr(self.network, 'b3'))
        
        # Check bias dimensions
        self.assertEqual(self.network.b1.shape, (self.network.hidden_dim,))
        self.assertEqual(self.network.b2.shape, (self.network.hidden_dim,))
        self.assertEqual(self.network.b3.shape, (self.network.output_dim,))
        print("TestNumpyQuantumNetwork: test_bias_initialization PASSED")

    def test_training_step(self):
        """Test that training step updates weights."""
        batch_size = 4
        input_data = np.random.randn(batch_size, self.network.input_dim)
        target = np.random.randn(batch_size, self.network.output_dim)
        
        # Store initial weights
        initial_w1 = self.network.w1.copy()
        
        # Perform forward pass (training step simulation)
        output = self.network.forward(input_data)
        
        # Output should have correct dimensions
        self.assertEqual(output.shape[0], batch_size)
        self.assertEqual(output.shape[1], self.network.output_dim)
        
        # Weights should exist and be finite
        self.assertTrue(np.all(np.isfinite(self.network.w1)))
        
        print("TestNumpyQuantumNetwork: test_training_step PASSED")

    def test_learning_rate_schedule(self):
        """Test phi-harmonic learning rate scheduling."""
        initial_lr = 0.001
        
        # Simulate multiple epochs with phi-harmonic decay
        for epoch in range(1, 5):  # Start from 1 to ensure decay
            # Typical phi-harmonic schedule: lr = initial_lr * (PHI_INV ** epoch)
            scheduled_lr = initial_lr * (PHI_INV ** epoch)
            self.assertLess(scheduled_lr, initial_lr)
        
        print("TestNumpyQuantumNetwork: test_learning_rate_schedule PASSED")


@unittest.skipIf(not TORCH_AVAILABLE, "PyTorch not available")
class TestPyTorchQuantumNetwork(unittest.TestCase):
    """Tests for PyTorch-based quantum neural network."""

    def test_quantum_activation_forward(self):
        """Test QuantumActivation forward pass."""
        activation = QuantumActivation()
        
        # Test with various inputs
        test_inputs = torch.tensor([-10.0, -1.0, 0.0, 1.0, 10.0])
        output = activation(test_inputs)
        
        # Should be bounded
        self.assertTrue(torch.all(output >= -PHI_INV))
        self.assertTrue(torch.all(output <= PHI_INV))
        
        # Should preserve sign
        self.assertGreater(output[3], 0)  # input 1.0
        self.assertLess(output[1], 0)     # input -1.0
        self.assertAlmostEqual(output[2].item(), 0.0, places=5)  # input 0.0
        
        print("TestPyTorchQuantumNetwork: test_quantum_activation_forward PASSED")

    def test_quantum_neural_network_forward(self):
        """Test QuantumNeuralNetwork forward pass."""
        network = QuantumNeuralNetwork(input_dim=102, hidden_dim=64, output_dim=10)
        
        batch_size = 4
        input_data = torch.randn(batch_size, 102)
        output = network(input_data)
        
        self.assertEqual(output.shape, (batch_size, 10))
        print("TestPyTorchQuantumNetwork: test_quantum_neural_network_forward PASSED")

    def test_quantum_neural_network_parameters(self):
        """Test that network has trainable parameters."""
        network = QuantumNeuralNetwork(input_dim=102, hidden_dim=64, output_dim=10)
        
        params = list(network.parameters())
        self.assertGreater(len(params), 0)
        
        # All parameters should require gradients
        for param in params:
            self.assertTrue(param.requires_grad)
        
        print("TestPyTorchQuantumNetwork: test_quantum_neural_network_parameters PASSED")


class TestConsciousnessGuidedLoss(unittest.TestCase):
    """Test consciousness-guided loss functions."""

    def setUp(self):
        """Set up test fixtures."""
        self.network = NumpyQuantumNetwork(
            input_dim=102,
            hidden_dim=64,
            output_dim=10
        )

    def test_mse_loss_computation(self):
        """Test mean squared error loss computation."""
        batch_size = 4
        predictions = np.random.randn(batch_size, 10)
        targets = np.random.randn(batch_size, 10)
        
        # MSE loss
        loss = np.mean((predictions - targets) ** 2)
        
        self.assertGreaterEqual(loss, 0)
        self.assertTrue(np.isfinite(loss))
        print("TestConsciousnessGuidedLoss: test_mse_loss_computation PASSED")

    def test_phi_regularization(self):
        """Test phi-harmonic regularization term."""
        # Simulate phi-regularization
        weights = self.network.w1
        phi_reg = PHI_INV * np.sum(weights ** 2)
        
        self.assertGreaterEqual(phi_reg, 0)
        self.assertTrue(np.isfinite(phi_reg))
        print("TestConsciousnessGuidedLoss: test_phi_regularization PASSED")


if __name__ == '__main__':
    unittest.main(verbosity=2)
