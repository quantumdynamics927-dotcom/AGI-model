"""Canonical model exports for the restructuring foundation."""

from importlib import import_module

import torch

# Transitional bridge: the root-level ``vae_model`` module remains the
# canonical implementation until the migration finishes, while package
# consumers switch to importing through ``packages.agi_model_core``.
_root_model = import_module("vae_model")

QuantumVAE = _root_model.QuantumVAE


def _default_density_matrix(mu: torch.Tensor) -> torch.Tensor:
    """Create a trace-normalized Hermitian density matrix for compatibility callers."""
    amplitudes = torch.sqrt(torch.softmax(mu.abs(), dim=-1)).to(torch.complex64)
    phases = torch.exp(1j * mu.to(torch.complex64))
    state = amplitudes * phases
    density_matrix = state.unsqueeze(-1) * state.conj().unsqueeze(-2)
    trace = torch.diagonal(density_matrix, dim1=-2, dim2=-1).sum(dim=-1, keepdim=True)
    return density_matrix / trace.unsqueeze(-1)


class HybridQuantumOptimizer(_root_model.HybridQuantumOptimizer):
    """Package-level optimizer shim with a default model for compatibility tests."""

    def __init__(self, model=None, *args, input_dim=128, latent_dim=32, **kwargs):
        if model is None:
            model = QuantumVAE(input_dim=input_dim, latent_dim=latent_dim)
        super().__init__(model=model, *args, **kwargs)


def total_loss(recon_x, x, mu, log_var, density_matrix=None, *args, **kwargs):
    """
    Preserve the root tuple-returning API when density is provided, while allowing
    package-level convenience calls without an explicit density matrix.
    """
    if density_matrix is None:
        density_matrix = _default_density_matrix(mu)
        total, _ = _root_model.total_loss(
            recon_x, x, mu, log_var, density_matrix, *args, **kwargs
        )
        return total.real
    return _root_model.total_loss(
        recon_x, x, mu, log_var, density_matrix, *args, **kwargs
    )


__all__ = ["HybridQuantumOptimizer", "QuantumVAE", "total_loss"]
