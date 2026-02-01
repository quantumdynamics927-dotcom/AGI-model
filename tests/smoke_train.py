import torch
from vae_model import QuantumVAE, total_loss


def test_vae_forward_and_loss_smoke():
    # Small smoke test: forward pass and loss computation
    model = QuantumVAE(input_dim=128, latent_dim=32)
    model.eval()

    x = torch.randn(2, 128)
    recon, mu, log_var, density = model(x)

    assert recon.shape == x.shape

    loss, loss_dict = total_loss(recon, x, mu, log_var, density)
    assert isinstance(loss.item(), float)
    assert 'total' in loss_dict
