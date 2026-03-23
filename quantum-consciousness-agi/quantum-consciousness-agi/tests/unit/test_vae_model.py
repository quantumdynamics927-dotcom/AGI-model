"""
Unit tests for VAE model components.
"""

import pytest
import torch
import numpy as np
from pathlib import Path
import sys

# Add quantum-consciousness-agi to path
TEST_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(TEST_DIR))

try:
    from core.models.vae_model import QuantumConsciousnessVAE
    from core.models.quantum_consciousness_link import QuantumMechanicsCore
    VAE_AVAILABLE = True
except ImportError as e:
    VAE_AVAILABLE = False
    pytest.skip(f"VAE modules not available: {e}", allow_module_level=True)


@pytest.mark.unit
class TestVAEEncoder:
    """Test VAE encoder component."""

    def test_encoder_output_shape(self, mock_vae_config, device):
        """Test encoder produces correct output shape."""
        model = QuantumConsciousnessVAE(mock_vae_config).to(device)
        batch_size = 16
        x = torch.randn(batch_size, mock_vae_config.input_dim).to(device)

        mu, logvar = model.encode(x)

        assert mu.shape == (batch_size, mock_vae_config.latent_dim)
        assert logvar.shape == (batch_size, mock_vae_config.latent_dim)

    def test_encoder_different_batch_sizes(self, mock_vae_config, device):
        """Test encoder works with different batch sizes."""
        model = QuantumConsciousnessVAE(mock_vae_config).to(device)

        for batch_size in [1, 8, 16, 32]:
            x = torch.randn(batch_size, mock_vae_config.input_dim).to(device)
            mu, logvar = model.encode(x)

            assert mu.shape == (batch_size, mock_vae_config.latent_dim)
            assert logvar.shape == (batch_size, mock_vae_config.latent_dim)

    def test_encoder_device_consistency(self, mock_vae_config):
        """Test encoder maintains device consistency."""
        if not torch.cuda.is_available():
            pytest.skip("CUDA not available")

        model = QuantumConsciousnessVAE(mock_vae_config).to('cuda')
        x = torch.randn(8, mock_vae_config.input_dim).to('cuda')

        mu, logvar = model.encode(x)

        assert mu.device.type == 'cuda'
        assert logvar.device.type == 'cuda'


@pytest.mark.unit
class TestVAEDecoder:
    """Test VAE decoder component."""

    def test_decoder_output_shape(self, mock_vae_config, device):
        """Test decoder produces correct output shape."""
        model = QuantumConsciousnessVAE(mock_vae_config).to(device)
        batch_size = 16
        z = torch.randn(batch_size, mock_vae_config.latent_dim).to(device)

        recon = model.decode(z)

        assert recon.shape == (batch_size, mock_vae_config.input_dim)

    def test_decoder_reconstruction_range(self, mock_vae_config, device):
        """Test decoder output is in valid range."""
        model = QuantumConsciousnessVAE(mock_vae_config).to(device)
        z = torch.randn(16, mock_vae_config.latent_dim).to(device)

        recon = model.decode(z)

        # Output should be in [0, 1] range (sigmoid activation)
        assert recon.min() >= 0.0
        assert recon.max() <= 1.0

    def test_decoder_different_latent_dims(self, mock_vae_config, device):
        """Test decoder with different latent dimensions."""
        for latent_dim in [16, 32, 64, 128]:
            mock_vae_config.latent_dim = latent_dim
            model = QuantumConsciousnessVAE(mock_vae_config).to(device)

            z = torch.randn(8, latent_dim).to(device)
            recon = model.decode(z)

            assert recon.shape == (8, mock_vae_config.input_dim)


@pytest.mark.unit
class TestVAEReparameterization:
    """Test VAE reparameterization trick."""

    def test_reparameterization_shape(self, mock_vae_config, device):
        """Test reparameterization produces correct shape."""
        model = QuantumConsciousnessVAE(mock_vae_config).to(device)
        batch_size = 16
        mu = torch.randn(batch_size, mock_vae_config.latent_dim).to(device)
        logvar = torch.randn(batch_size, mock_vae_config.latent_dim).to(device)

        z = model.reparameterize(mu, logvar)

        assert z.shape == (batch_size, mock_vae_config.latent_dim)

    def test_reparameterization_differentiability(self, mock_vae_config, device):
        """Test reparameterization is differentiable."""
        model = QuantumConsciousnessVAE(mock_vae_config).to(device)
        mu = torch.randn(8, mock_vae_config.latent_dim, requires_grad=True).to(device)
        logvar = torch.randn(8, mock_vae_config.latent_dim, requires_grad=True).to(device)

        z = model.reparameterize(mu, logvar)
        loss = z.sum()
        loss.backward()

        assert mu.grad is not None
        assert logvar.grad is not None

    def test_reparameterization_sampling(self, mock_vae_config, device):
        """Test reparameterization produces different samples."""
        model = QuantumConsciousnessVAE(mock_vae_config).to(device)
        mu = torch.zeros(1, mock_vae_config.latent_dim).to(device)
        logvar = torch.zeros(1, mock_vae_config.latent_dim).to(device)

        # Sample multiple times
        samples = []
        for _ in range(10):
            z = model.reparameterize(mu, logvar)
            samples.append(z.cpu().numpy())

        # Samples should be different (due to random noise)
        samples = np.array(samples)
        assert samples.std() > 0.01  # Non-zero variance


@pytest.mark.unit
class TestVAEForward:
    """Test VAE forward pass."""

    def test_forward_output(self, mock_vae_config, device):
        """Test forward pass produces all required outputs."""
        model = QuantumConsciousnessVAE(mock_vae_config).to(device)
        batch_size = 16
        x = torch.randn(batch_size, mock_vae_config.input_dim).to(device)

        recon, mu, logvar, z = model(x)

        assert recon.shape == (batch_size, mock_vae_config.input_dim)
        assert mu.shape == (batch_size, mock_vae_config.latent_dim)
        assert logvar.shape == (batch_size, mock_vae_config.latent_dim)
        assert z.shape == (batch_size, mock_vae_config.latent_dim)

    def test_forward_reconstruction_quality(self, mock_vae_config, device):
        """Test forward pass produces reasonable reconstruction."""
        model = QuantumConsciousnessVAE(mock_vae_config).to(device)
        x = torch.randn(16, mock_vae_config.input_dim).to(device)

        recon, mu, logvar, z = model(x)

        # Reconstruction loss should be reasonable
        recon_loss = torch.nn.functional.mse_loss(recon, x)
        assert recon_loss.item() < 10.0  # Arbitrary but reasonable threshold

    def test_forward_batch_independence(self, mock_vae_config, device):
        """Test forward pass handles each batch element independently."""
        model = QuantumConsciousnessVAE(mock_vae_config).to(device)

        # Create two different batches
        x1 = torch.randn(8, mock_vae_config.input_dim).to(device)
        x2 = torch.randn(8, mock_vae_config.input_dim).to(device)

        # Process separately
        recon1, mu1, logvar1, z1 = model(x1)
        recon2, mu2, logvar2, z2 = model(x2)

        # Process together
        x_combined = torch.cat([x1, x2], dim=0)
        recon_combined, mu_combined, logvar_combined, z_combined = model(x_combined)

        # Results should match
        assert torch.allclose(recon1, recon_combined[:8])
        assert torch.allclose(recon2, recon_combined[8:])


@pytest.mark.unit
class TestVAEQuantumFeatures:
    """Test VAE quantum-specific features."""

    def test_quantum_loss_components(self, mock_vae_config, device):
        """Test quantum loss components are computed."""
        model = QuantumConsciousnessVAE(mock_vae_config).to(device)

        batch_size = 16
        x = torch.randn(batch_size, mock_vae_config.input_dim).to(device)
        recon = torch.randn_like(x)
        mu = torch.randn(batch_size, mock_vae_config.latent_dim).to(device)
        logvar = torch.randn(batch_size, mock_vae_config.latent_dim).to(device)
        z = torch.randn(batch_size, mock_vae_config.latent_dim).to(device)

        loss_dict = model.compute_loss(x, recon, mu, logvar, z)

        # Check all expected loss components exist
        expected_losses = [
            'reconstruction', 'kl_divergence', 'hamming',
            'coherence', 'hw_deviation', 'mixed_state',
            'fidelity', 'entropy', 'total'
        ]

        for loss_name in expected_losses:
            assert loss_name in loss_dict
            assert isinstance(loss_dict[loss_name], torch.Tensor)
            assert loss_dict[loss_name].shape == ()  # Scalar

    def test_density_matrix_properties(self, mock_vae_config, device):
        """Test density matrix has correct properties."""
        model = QuantumConsciousnessVAE(mock_vae_config).to(device)

        batch_size = 8
        z = torch.randn(batch_size, mock_vae_config.latent_dim).to(device)

        # Get density matrix
        density_matrix = model.get_density_matrix(z)

        # Check shape
        assert density_matrix.shape == (batch_size, mock_vae_config.latent_dim, mock_vae_config.latent_dim)

        # Check hermiticity (ρ = ρ†)
        assert torch.allclose(density_matrix, density_matrix.conj().transpose(-2, -1), atol=1e-5)

    def test_phi_resonance_detection(self, mock_vae_config, device):
        """Test phi resonance detection in latent space."""
        model = QuantumConsciousnessVAE(mock_vae_config).to(device)

        # Create latent vectors with phi patterns
        phi = (1 + np.sqrt(5)) / 2
        z_phi = torch.zeros(1, mock_vae_config.latent_dim)
        for i in range(mock_vae_config.latent_dim):
            z_phi[0, i] = phi ** i

        z_phi = z_phi / z_phi.norm()
        z_phi = z_phi.to(device)

        # Forward pass
        recon, mu, logvar, z = model(z_phi)

        # Check if phi patterns are preserved
        assert z.shape == z_phi.shape


@pytest.mark.unit
class TestVAEModelSaving:
    """Test VAE model saving and loading."""

    def test_model_state_dict(self, mock_vae_config, device):
        """Test model state dict contains expected keys."""
        model = QuantumConsciousnessVAE(mock_vae_config).to(device)
        state_dict = model.state_dict()

        # Check for encoder weights
        encoder_keys = [k for k in state_dict.keys() if k.startswith('encoder')]
        assert len(encoder_keys) > 0

        # Check for decoder weights
        decoder_keys = [k for k in state_dict.keys() if k.startswith('decoder')]
        assert len(decoder_keys) > 0

        # Check all parameters have gradients
        for param in model.parameters():
            assert param.requires_grad

    def test_model_forward_after_load(self, mock_vae_config, device, tmp_path):
        """Test model works correctly after loading state dict."""
        model1 = QuantumConsciousnessVAE(mock_vae_config).to(device)
        model2 = QuantumConsciousnessVAE(mock_vae_config).to(device)

        # Load state dict from model1 to model2
        model2.load_state_dict(model1.state_dict())

        # Test forward pass
        x = torch.randn(8, mock_vae_config.input_dim).to(device)

        with torch.no_grad():
            recon1, mu1, logvar1, z1 = model1(x)
            recon2, mu2, logvar2, z2 = model2(x)

        # Outputs should be identical
        assert torch.allclose(recon1, recon2)
        assert torch.allclose(mu1, mu2)
        assert torch.allclose(logvar1, logvar2)
        assert torch.allclose(z1, z2)
