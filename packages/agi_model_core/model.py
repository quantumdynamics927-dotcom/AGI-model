"""Canonical model exports for the restructuring foundation."""

from importlib import import_module

# Transitional bridge: the root-level ``vae_model`` module remains the
# canonical implementation until the migration finishes, while package
# consumers switch to importing through ``packages.agi_model_core``.
_root_model = import_module("vae_model")

QuantumVAE = _root_model.QuantumVAE
total_loss = _root_model.total_loss
HybridQuantumOptimizer = _root_model.HybridQuantumOptimizer

__all__ = ["HybridQuantumOptimizer", "QuantumVAE", "total_loss"]
