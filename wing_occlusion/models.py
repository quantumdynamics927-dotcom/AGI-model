"""
Wing Occlusion Neural Models

PyTorch implementations of encoder/decoder architectures with phi-scaled layers.
Includes training utilities for learning wing-consciousness bridge representations.
"""

import torch
import torch.nn as nn
import torch.optim as optim
from typing import Tuple, Optional, List
import numpy as np

PHI = 1.618033988749895


class WingInterferenceEncoder(nn.Module):
    """
    Encoder inspired by wing interference patterns.
    
    Transforms 2D points through phi-scaled hidden layers.
    """
    
    def __init__(
        self,
        input_dim: int = 2,
        hidden_dims: Optional[List[int]] = None,
        latent_dim: int = 6,
        phi_scale: bool = True
    ):
        super().__init__()
        
        if hidden_dims is None:
            # Phi-scaled architecture: 2 -> 3 -> 5 -> 8 -> 13 -> ...
            hidden_dims = [int(PHI**i * input_dim) for i in range(1, 5)]
            hidden_dims = [max(d, 2) for d in hidden_dims]
        
        layers = []
        prev_dim = input_dim
        for hidden_dim in hidden_dims:
            layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.ReLU(),
                nn.BatchNorm1d(hidden_dim),
            ])
            prev_dim = hidden_dim
        
        layers.append(nn.Linear(prev_dim, latent_dim))
        
        self.encoder = nn.Sequential(*layers)
        self.latent_dim = latent_dim
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Encode input to latent representation."""
        return self.encoder(x)


class ConsciousnessLatentEncoder(nn.Module):
    """
    Autoencoder for latent consciousness-like representations.
    
    Architecture uses phi-scaled hidden dimensions.
    """
    
    def __init__(
        self,
        input_dim: int = 2,
        latent_dim: int = 6,
        phi_scale: bool = True
    ):
        super().__init__()
        
        if phi_scale:
            # Encoder: input -> phi*input -> phi^2*input -> latent
            h1 = int(PHI * input_dim)
            h2 = int(PHI**2 * input_dim)
            h1 = max(h1, latent_dim * 2)
            h2 = max(h2, latent_dim * 4)
        else:
            h1 = 64
            h2 = 32
        
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, h1),
            nn.ReLU(),
            nn.BatchNorm1d(h1),
            nn.Linear(h1, h2),
            nn.ReLU(),
            nn.Linear(h2, latent_dim),
        )
        
        # Decoder mirrors encoder
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, h2),
            nn.ReLU(),
            nn.Linear(h2, h1),
            nn.ReLU(),
            nn.Linear(h1, input_dim),
        )
        
        self.latent_dim = latent_dim
    
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Encode and decode, returning (latent, reconstruction)."""
        latent = self.encoder(x)
        reconstructed = self.decoder(latent)
        return latent, reconstructed


def train_autoencoder(
    model: nn.Module,
    data: torch.Tensor,
    n_epochs: int = 100,
    learning_rate: float = 1e-3,
    batch_size: int = 32,
    verbose: bool = True
) -> List[float]:
    """
    Train autoencoder on data.
    
    Args:
        model: Autoencoder model
        data: Training data tensor
        n_epochs: Number of training epochs
        learning_rate: Learning rate
        batch_size: Batch size
        verbose: Print progress
        
    Returns:
        List of epoch losses
    """
    model.train()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    criterion = nn.MSELoss()
    
    losses = []
    n_samples = len(data)
    
    for epoch in range(n_epochs):
        epoch_loss = 0.0
        n_batches = 0
        
        # Shuffle data
        indices = torch.randperm(n_samples)
        
        for i in range(0, n_samples, batch_size):
            batch_indices = indices[i:i+batch_size]
            batch = data[batch_indices]
            
            optimizer.zero_grad()
            
            if isinstance(model, ConsciousnessLatentEncoder):
                _, reconstructed = model(batch)
            else:
                latent = model(batch)
                reconstructed = model.decoder(latent) if hasattr(model, 'decoder') else latent
            
            loss = criterion(reconstructed, batch)
            loss.backward()
            optimizer.step()
            
            epoch_loss += loss.item()
            n_batches += 1
        
        avg_loss = epoch_loss / n_batches
        losses.append(avg_loss)
        
        if verbose and (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch+1}/{n_epochs}, Loss: {avg_loss:.6f}")
    
    return losses


def compute_wing_consciousness_metrics(
    wing_encoded: np.ndarray,
    consciousness_latent: np.ndarray
) -> dict:
    """
    Compute comparison metrics between wing and consciousness representations.
    
    Note: These are exploratory metrics, not validated equivalence measures.
    
    Args:
        wing_encoded: Wing-transformed data
        consciousness_latent: Latent vectors from neural model
        
    Returns:
        Dictionary of comparison metrics
    """
    # Dimensionality comparison
    wing_dim = wing_encoded.shape[1] if len(wing_encoded.shape) > 1 else 1
    consciousness_dim = consciousness_latent.shape[1] if len(consciousness_latent.shape) > 1 else 1
    
    # Variance preservation (proxy for information content)
    wing_variance = np.var(wing_encoded)
    consciousness_variance = np.var(consciousness_latent)
    
    # Sparsity (fraction of near-zero elements)
    wing_sparsity = np.mean(np.abs(wing_encoded) < 0.1)
    consciousness_sparsity = np.mean(np.abs(consciousness_latent) < 0.1)
    
    return {
        'wing_dimensionality': wing_dim,
        'consciousness_dimensionality': consciousness_dim,
        'dimensionality_ratio': consciousness_dim / wing_dim,
        'wing_variance': float(wing_variance),
        'consciousness_variance': float(consciousness_variance),
        'variance_ratio': float(consciousness_variance / (wing_variance + 1e-10)),
        'wing_sparsity': float(wing_sparsity),
        'consciousness_sparsity': float(consciousness_sparsity),
    }
