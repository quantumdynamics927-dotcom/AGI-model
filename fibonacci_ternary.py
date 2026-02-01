"""Fibonacci Ternary Decompressor and Quantum-Fibonacci Bridge

Provides:
- `FibonacciTernaryNode`: dequantize ternary {-1,0,1} arrays through 5-layer
  Fibonacci scaling.
- `QuantumFibonacciBridge`: convert bitstrings to ternary and unfold via
  Fibonacci scaling; utility to modulate torch model weights.
- `fibonacci_sigmoid`: activation function (NumPy + PyTorch) that biases
  firing toward fibonacci/harmonic frequencies.
"""
from __future__ import annotations

import math
from typing import Sequence, List

import numpy as np

try:
    import torch
    _HAS_TORCH = True
except Exception:
    _HAS_TORCH = False


PHI = 1.618033988749895
DEFAULT_FIB_SCALE = [1, 1, 2, 3, 5]


class FibonacciTernaryNode:
    """Dequantizer for ternary-weight representations using 5-layer Fibonacci scaling.

    Attributes
    ----------
    fib_scale: list of int
        Fibonacci scaling constants applied per layer.
    phi: float
        Golden ratio used to dampen growth per layer.
    """

    def __init__(self, fib_scale: Sequence[int] = DEFAULT_FIB_SCALE, phi: float = PHI):
        self.fib_scale = list(fib_scale)
        self.phi = float(phi)

    def dequantize(self, ternary_weights: np.ndarray) -> np.ndarray:
        """Expand ternary weights {-1,0,1} into a high-precision harmonic space.

        The transform applies each Fibonacci scale in sequence and damps by
        phi^(layer_index+1) to keep values stable.

        Args:
            ternary_weights: np.ndarray of integers in {-1,0,1}

        Returns:
            np.ndarray float64 of same shape with decompressed values.
        """
        arr = np.asarray(ternary_weights, dtype=float)
        resonance = arr.copy()
        for i, s in enumerate(self.fib_scale):
            resonance = (resonance * float(s)) / (self.phi ** (i + 1))
        return resonance


class QuantumFibonacciBridge:
    """Bridge that converts quantum bitstrings into Fibonacci-scaled ternary resonance.

    Default mapping (2-bit -> ternary):
        '00' -> 0  (Neural Rest)
        '01' -> 1  (Excitation)
        '10' -> -1 (Inhibition)
        '11' -> 0  (Entanglement Null)
    """

    def __init__(self, fib_scale: Sequence[int] = DEFAULT_FIB_SCALE, phi: float = PHI):
        self.fib_scale = list(fib_scale)
        self.phi = float(phi)
        self.ternary_map = {
            '00': 0,
            '01': 1,
            '10': -1,
            '11': 0,
        }

    def process_bitstrings(self, bitstrings: Sequence[str]) -> np.ndarray:
        """Convert bitstrings (list of '01','10',...) into Fibonacci-unfolded resonance.

        Returns a 1D numpy array of floats.
        """
        tern = np.array([self.ternary_map.get(b, 0) for b in bitstrings], dtype=float)
        return self.unfold_fibonacci(tern)

    def unfold_fibonacci(self, ternary_tensor: np.ndarray) -> np.ndarray:
        """Apply the 5-layer Fibonacci scaling to the ternary input.

        Each layer scales by the Fibonacci number and damps by phi^(layer_index+1).
        """
        resonance = ternary_tensor.astype(float)
        for i, scale in enumerate(self.fib_scale):
            resonance = (resonance * float(scale)) / (self.phi ** (i + 1))
        return resonance

    def inject_to_torch_weights(self, model_weights: 'torch.Tensor', quantum_resonance: np.ndarray) -> 'torch.Tensor':
        """Modulate PyTorch tensor `model_weights` by the quantum_resonance vector.

        The resonance vector is broadcast-multiplied across weight dimensions when possible.
        Requires torch.
        """
        if not _HAS_TORCH:
            raise RuntimeError('PyTorch not available')

        import torch as _torch

        resonance = _torch.tensor(quantum_resonance, dtype=model_weights.dtype, device=model_weights.device)

        # Attempt to broadcast by matching trailing dimensions
        try:
            shaped = resonance.view(*([1] * (model_weights.dim() - resonance.dim())), *resonance.shape)
        except Exception:
            # Fallback: expand resonance to a single-dim multiplier
            shaped = resonance.view(-1)

        return model_weights * (1.0 + shaped)


def fibonacci_sigmoid_numpy(x: np.ndarray, alpha: float = 4.0, beta: float = 0.25, fib_scale: List[int] = DEFAULT_FIB_SCALE, phi: float = PHI) -> np.ndarray:
    """Activation that biases firing toward harmonic/fibonacci frequencies.

    Output = sigmoid(alpha * x) * (1 + beta * harmonic), where harmonic is a
    normalized cosine-sum over scaled frequencies derived from `fib_scale` and `phi`.
    """
    x = np.asarray(x, dtype=float)
    sigmoid = 1.0 / (1.0 + np.exp(-alpha * x))

    # Harmonic probe: sum cos(x / (phi**i) * scale)
    harmonics = np.zeros_like(x, dtype=float)
    for i, s in enumerate(fib_scale):
        freq = s / (phi ** (i + 1))
        harmonics += np.cos(x * freq)

    # Normalize harmonic to [-1,1]
    harmonics = harmonics / max(1.0, len(fib_scale))
    return sigmoid * (1.0 + beta * harmonics)


def fibonacci_sigmoid_torch(x: 'torch.Tensor', alpha: float = 4.0, beta: float = 0.25, fib_scale: List[int] = DEFAULT_FIB_SCALE, phi: float = PHI) -> 'torch.Tensor':
    """Torch version of `fibonacci_sigmoid_numpy`.
    Requires PyTorch available.
    """
    if not _HAS_TORCH:
        raise RuntimeError('PyTorch not available')
    import torch as _torch

    sigmoid = _torch.sigmoid(alpha * x)
    harmonics = _torch.zeros_like(x, dtype=x.dtype)
    for i, s in enumerate(fib_scale):
        freq = float(s) / (phi ** (i + 1))
        harmonics = harmonics + _torch.cos(x * freq)
    harmonics = harmonics / max(1.0, len(fib_scale))
    return sigmoid * (1.0 + beta * harmonics)


__all__ = [
    'FibonacciTernaryNode',
    'QuantumFibonacciBridge',
    'fibonacci_sigmoid_numpy',
    'fibonacci_sigmoid_torch',
]
