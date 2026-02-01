import torch
import torch.nn as nn
import torch.nn.functional as F
import losses

class QuantumVAE(nn.Module):
    """Minimal QuantumVAE scaffold.

    Encoder: 128 -> 256 -> 128 -> (mu, logvar) of size 32
    Decoder: latent 32 -> 128 -> 256 -> 128
    """
    def __init__(self, input_dim=128, latent_dim=32):
        super().__init__()
        self.input_dim = input_dim
        self.latent_dim = latent_dim

        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
        )
        self.mu_layer = nn.Linear(128, latent_dim)
        self.logvar_layer = nn.Linear(128, latent_dim)

        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 256),
            nn.ReLU(),
            nn.Linear(256, input_dim),
            nn.Sigmoid()
        )

    def encode(self, x):
        h = self.encoder(x)
        mu = self.mu_layer(h)
        logvar = self.logvar_layer(h)
        return mu, logvar

    def reparameterize(self, mu, logvar):
        std = (0.5 * logvar).exp()
        eps = torch.randn_like(std)
        return mu + eps * std

    def decode(self, z):
        return self.decoder(z)

    def forward(self, x):
        mu, logvar = self.encode(x)
        z = self.reparameterize(mu, logvar)
        recon = self.decode(z)
        return recon, mu, logvar

    def compute_losses(self, recon, x, mu, logvar, weights=None):
        """Compute composite quantum-specific losses.

        weights: dict of loss weights. Uses project defaults if None.
        Returns (total_loss, breakdown_dict)
        """
        if weights is None:
            weights = {
                'recon': 1.0, 'kl': 0.0008, 'hamming': 0.3, 'coherence': 0.1,
                'hw': 0.01, 'mixed_state': 0.1, 'fidelity': 0.1, 'entropy': 0.05
            }

        recon_l = losses.reconstruction_loss(recon, x)
        kl_l = losses.kl_divergence(mu, logvar)
        hamming_l = losses.hamming_loss(recon, x)
        coherence_l = losses.coherence_loss(recon, x)
        mixed_l = losses.mixed_state_loss(mu)
        fidelity_l = losses.fidelity_loss(recon, x)
        entropy_l = losses.entropy_loss(mu)
        hw_l = losses.hw_deviation_loss(mu)

        total = (
            weights['recon'] * recon_l +
            weights['kl'] * kl_l +
            weights['hamming'] * hamming_l +
            weights['coherence'] * coherence_l +
            weights['mixed_state'] * mixed_l +
            weights['fidelity'] * fidelity_l +
            weights['entropy'] * entropy_l +
            weights['hw'] * hw_l
        )

        breakdown = {
            'total': total,
            'recon': recon_l.item(),
            'kl': kl_l.item(),
            'hamming': hamming_l.item(),
            'coherence': coherence_l.item(),
            'mixed_state': mixed_l.item(),
            'fidelity': fidelity_l.item(),
            'entropy': entropy_l.item(),
            'hw': hw_l.item(),
        }
        return total, breakdown
