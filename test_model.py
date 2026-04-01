import torch
from vae_model import QuantumVAE, total_loss

# Test the model
model = QuantumVAE(input_dim=128, latent_dim=32)
x = torch.randn(10, 128)  # Batch of 10 samples

print("Testing QuantumVAE forward pass...")
recon_x, mu, log_var, density_matrix = model(x, return_density=True)
print(f"Input shape: {x.shape}")
print(f"Reconstructed shape: {recon_x.shape}")
print(f"Mu shape: {mu.shape}")
print(f"Log var shape: {log_var.shape}")
print(f"Density matrix shape: {density_matrix.shape}")

print("\nTesting loss computation...")
total_tensor, losses = total_loss(recon_x, x, mu, log_var, density_matrix, include_advanced=True)
print("Losses:")
for key, value in losses.items():
    print(f"  {key}: {value:.4f}")

print("\nModel test passed!")
