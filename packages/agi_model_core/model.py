"""Canonical model exports for the restructuring foundation."""

from importlib import import_module

_root_model = import_module("vae_model")

QuantumVAE = _root_model.QuantumVAE
total_loss = _root_model.total_loss
HybridQuantumOptimizer = _root_model.HybridQuantumOptimizer

__all__ = ["HybridQuantumOptimizer", "QuantumVAE", "total_loss"]
