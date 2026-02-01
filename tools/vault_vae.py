"""tools/vault_vae.py

Local VAE generator for sanitized datasets. Trains locally and emits synthetic data.
"""
from __future__ import annotations

import os
import json
import math
from pathlib import Path
from typing import Tuple, List

import numpy as np
import pandas as pd

# Use PyTorch when available, else fallback to a PCA-based generator
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    HAS_TORCH = True
except Exception:
    HAS_TORCH = False


class BioVaultVAE(nn.Module if HAS_TORCH else object):
    def __init__(self, input_dim: int, latent_dim: int = 4):
        if not HAS_TORCH:
            return
        super().__init__()
        self.encoder = nn.Sequential(nn.Linear(input_dim, 32), nn.ReLU(), nn.Linear(32, latent_dim * 2))
        self.decoder = nn.Sequential(nn.Linear(latent_dim, 32), nn.ReLU(), nn.Linear(32, input_dim), nn.Sigmoid())

    def reparameterize(self, mu, logvar):
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std

    def forward(self, x):
        h = self.encoder(x)
        mu, logvar = torch.chunk(h, 2, dim=1)
        z = self.reparameterize(mu, logvar)
        return self.decoder(z), mu, logvar


def _train_torch_vae(data: np.ndarray, latent_dim: int = 4, epochs: int = 200, lr: float = 1e-3, device: str = "cpu") -> Tuple[object, dict]:
    device = torch.device(device)
    X = torch.tensor(data, dtype=torch.float32, device=device)
    model = BioVaultVAE(input_dim=X.shape[1], latent_dim=latent_dim).to(device)
    opt = optim.Adam(model.parameters(), lr=lr)

    for epoch in range(epochs):
        opt.zero_grad()
        recon, mu, logvar = model(X)
        recon_loss = nn.functional.mse_loss(recon, X)
        kld = -0.5 * torch.mean(1 + logvar - mu.pow(2) - logvar.exp())
        loss = recon_loss + 0.01 * kld
        loss.backward()
        opt.step()
        if (epoch + 1) % max(1, epochs // 5) == 0:
            print(f"Epoch {epoch+1}/{epochs} loss={loss.item():.6f} recon={recon_loss.item():.6f} kld={kld.item():.6f}")
    return model, {"epochs": epochs}


def _generate_torch(model: object, n_samples: int, latent_dim: int, scaler, columns: List[str]) -> pd.DataFrame:
    model.eval()
    with torch.no_grad():
        z = torch.randn(n_samples, latent_dim)
        generated = model.decoder(z).cpu().numpy()
    gen = scaler.inverse_transform(generated)
    df = pd.DataFrame(gen, columns=columns)
    return df


# PCA-based fallback generator (if torch not available)
from sklearn.decomposition import PCA


def _train_pca_generator(data: np.ndarray, n_components: int = 4):
    pca = PCA(n_components=n_components)
    pca.fit(data)
    return pca


def _generate_pca(pca, n_samples: int, scaler, columns: List[str]) -> pd.DataFrame:
    z = np.random.normal(size=(n_samples, pca.n_components_))
    gen = pca.inverse_transform(z)
    gen = scaler.inverse_transform(gen)
    return pd.DataFrame(gen, columns=columns)


def train_vault_model(input_path: str, latent_dim: int = 4, epochs: int = 200, device: str = "cpu") -> Tuple[object, object, List[str]]:
    p = Path(input_path)
    if p.suffix.lower() in ['.parquet', '.parq']:
        df = pd.read_parquet(input_path)
    else:
        # support CSV fallback when parquet engines are not available
        df = pd.read_csv(input_path)
    df_numeric = pd.get_dummies(df).astype(float)
    from sklearn.preprocessing import MinMaxScaler
    scaler = MinMaxScaler()
    data_scaled = scaler.fit_transform(df_numeric.values)

    if HAS_TORCH:
        model, info = _train_torch_vae(data_scaled, latent_dim=latent_dim, epochs=epochs, device=device)
        model_path = Path("vault/models/vault_vae.pth")
        model_path.parent.mkdir(parents=True, exist_ok=True)
        torch.save(model.state_dict(), model_path)
        return model, scaler, list(df_numeric.columns)
    else:
        pca = _train_pca_generator(data_scaled, n_components=latent_dim)
        return pca, scaler, list(df_numeric.columns)


def generate_synthetic(model_obj, scaler, columns: List[str], n_samples: int = 100, latent_dim: int = 4) -> pd.DataFrame:
    if HAS_TORCH and hasattr(model_obj, "decoder"):
        df_gen = _generate_torch(model_obj, n_samples, latent_dim, scaler, columns)
    else:
        df_gen = _generate_pca(model_obj, n_samples, scaler, columns)
    outdir = Path("vault/synthetic")
    outdir.mkdir(parents=True, exist_ok=True)
    path = outdir / "synthetic_output.csv"
    df_gen.to_csv(path, index=False)
    print(f"✨ Synthetic data written to {path}")
    return df_gen, str(path)


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, help="Input sanitized parquet file")
    p.add_argument("--epochs", type=int, default=100)
    p.add_argument("--latent", type=int, default=4)
    p.add_argument("--gen", type=int, default=100)
    args = p.parse_args()

    model, scaler, cols = train_vault_model(args.input, latent_dim=args.latent, epochs=args.epochs)
    generate_synthetic(model, scaler, cols, n_samples=args.gen, latent_dim=args.latent)
