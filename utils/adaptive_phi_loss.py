"""
Adaptive Phi Loss Module

Dynamic loss weighting for golden ratio optimization during VAE training.
Adjusts phi regularization weight based on current resonance score and
training progress.

Features:
- Adaptive weight scheduling based on phi resonance
- Multiple annealing strategies (linear, cosine, exponential)
- Target resonance tracking with feedback control
- Integration with PyTorch training loops
"""

import torch
import torch.nn as nn
import numpy as np
from typing import Dict, Optional, List, Callable

# Golden ratio constant
PHI = 1.618033988749895


class AdaptivePhiLoss(nn.Module):
    """
    Adaptive golden ratio regularization loss.

    Dynamically adjusts the weight of phi regularization based on:
    - Current phi resonance score
    - Training epoch / progress
    - Target resonance level

    Parameters
    ----------
    target_resonance : float, default=0.7
        Target phi resonance score to achieve (0-1)
    min_weight : float, default=0.01
        Minimum loss weight
    max_weight : float, default=0.5
        Maximum loss weight
    warmup_epochs : int, default=10
        Number of epochs before phi loss is fully active
    schedule : str, default='adaptive'
        Weight schedule: 'adaptive', 'linear', 'cosine', 'exponential'
    target_phi : float, default=PHI
        Target golden ratio value

    Example
    -------
    >>> phi_loss = AdaptivePhiLoss(target_resonance=0.7, max_weight=0.3)
    >>> for epoch in range(100):
    ...     # In training loop
    ...     latent_z = model.encode(x)[0]
    ...     loss_phi = phi_loss(latent_z, epoch=epoch)
    ...     total_loss = reconstruction_loss + loss_phi
    """

    def __init__(
        self,
        target_resonance: float = 0.7,
        min_weight: float = 0.01,
        max_weight: float = 0.5,
        warmup_epochs: int = 10,
        schedule: str = 'adaptive',
        target_phi: float = PHI
    ):
        super().__init__()

        self.target_resonance = target_resonance
        self.min_weight = min_weight
        self.max_weight = max_weight
        self.warmup_epochs = warmup_epochs
        self.schedule = schedule
        self.target_phi = target_phi

        # Tracking
        self.resonance_history: List[float] = []
        self.weight_history: List[float] = []
        self.current_weight = min_weight
        self.current_resonance = 0.0

        # Feedback control parameters
        self.kp = 0.1  # Proportional gain
        self.ki = 0.01  # Integral gain
        self.integral_error = 0.0

    def forward(
        self,
        latent_z: torch.Tensor,
        epoch: Optional[int] = None,
        update_weight: bool = True
    ) -> torch.Tensor:
        """
        Compute adaptive phi regularization loss.

        Parameters
        ----------
        latent_z : Tensor
            Latent representations (batch_size, latent_dim)
        epoch : int, optional
            Current epoch for scheduling
        update_weight : bool, default=True
            Whether to update the adaptive weight

        Returns
        -------
        Tensor
            Weighted phi regularization loss (scalar)
        """
        # Compute base phi loss
        phi_loss = self._compute_phi_loss(latent_z)

        # Compute current resonance
        with torch.no_grad():
            resonance = self._compute_resonance(latent_z)
            self.current_resonance = resonance

        # Update weight if requested
        if update_weight and epoch is not None:
            self.current_weight = self.compute_weight(resonance, epoch)
            self.resonance_history.append(resonance)
            self.weight_history.append(self.current_weight)

        return self.current_weight * phi_loss

    def _compute_phi_loss(self, latent_z: torch.Tensor) -> torch.Tensor:
        """
        Compute the base phi regularization loss.

        Encourages ratios between adjacent latent dimensions to
        approximate the golden ratio.
        """
        # Compute standard deviations per dimension
        latent_std = torch.std(latent_z, dim=0)

        # Ensure we have enough dimensions
        if latent_std.numel() < 2:
            return torch.tensor(0.0, device=latent_z.device)

        # Compute ratios between adjacent dimensions
        # Add small epsilon to avoid division by zero
        ratios = latent_std[1:] / (latent_std[:-1] + 1e-10)

        # Target: all ratios should equal phi
        target_ratio = torch.full_like(ratios, self.target_phi)

        # MSE loss toward phi
        phi_loss = torch.mean((ratios - target_ratio) ** 2)

        return phi_loss

    def _compute_resonance(self, latent_z: torch.Tensor) -> float:
        """
        Compute current phi resonance score (0-1).

        Higher score = closer to golden ratio patterns.
        """
        latent_std = torch.std(latent_z, dim=0)

        if latent_std.numel() < 2:
            return 0.0

        ratios = latent_std[1:] / (latent_std[:-1] + 1e-10)
        proximity = torch.abs(ratios - self.target_phi)

        # Resonance = fraction within 10% of phi
        threshold = 0.1 * self.target_phi
        resonance = (proximity < threshold).float().mean().item()

        return resonance

    def compute_weight(
        self,
        current_resonance: float,
        epoch: int
    ) -> float:
        """
        Compute adaptive weight based on resonance and epoch.

        Parameters
        ----------
        current_resonance : float
            Current phi resonance score (0-1)
        epoch : int
            Current training epoch

        Returns
        -------
        float
            Adaptive loss weight
        """
        # Apply warmup
        if epoch < self.warmup_epochs:
            warmup_factor = epoch / self.warmup_epochs
        else:
            warmup_factor = 1.0

        if self.schedule == 'adaptive':
            # Feedback control based on distance from target
            error = self.target_resonance - current_resonance
            self.integral_error += error

            # PI control
            weight = (
                self.min_weight +
                (self.max_weight - self.min_weight) *
                (self.kp * error + self.ki * self.integral_error)
            )

            # Clip to bounds
            weight = max(self.min_weight, min(self.max_weight, weight))

        elif self.schedule == 'linear':
            # Linear increase from min to max
            max_epochs = 100  # Reach max weight by epoch 100
            progress = min(1.0, epoch / max_epochs)
            weight = self.min_weight + progress * (self.max_weight - self.min_weight)

        elif self.schedule == 'cosine':
            # Cosine annealing
            max_epochs = 100
            progress = min(1.0, epoch / max_epochs)
            weight = self.min_weight + 0.5 * (self.max_weight - self.min_weight) * (
                1 - np.cos(np.pi * progress)
            )

        elif self.schedule == 'exponential':
            # Exponential increase
            rate = 0.05
            weight = self.min_weight + (self.max_weight - self.min_weight) * (
                1 - np.exp(-rate * epoch)
            )

        else:
            # Constant weight
            weight = (self.min_weight + self.max_weight) / 2

        return weight * warmup_factor

    def update_schedule(
        self,
        resonance_history: Optional[List[float]] = None
    ):
        """
        Update weight schedule based on recent resonance history.

        Can be called periodically to adjust the adaptive parameters.

        Parameters
        ----------
        resonance_history : list of float, optional
            External resonance history. Uses internal if not provided.
        """
        history = resonance_history or self.resonance_history

        if len(history) < 10:
            return

        recent = history[-10:]
        trend = np.mean(np.diff(recent))

        # If resonance is stagnating, increase aggressiveness
        if abs(trend) < 0.001 and np.mean(recent) < self.target_resonance:
            self.kp = min(0.3, self.kp * 1.2)
            self.ki = min(0.05, self.ki * 1.1)

        # If resonance is oscillating, decrease aggressiveness
        if np.std(recent) > 0.1:
            self.kp = max(0.05, self.kp * 0.9)
            self.ki = max(0.005, self.ki * 0.9)

    def get_metrics(self) -> Dict:
        """
        Get current metrics and history.

        Returns
        -------
        dict
            Metrics including current weight, resonance, and histories
        """
        return {
            'current_weight': self.current_weight,
            'current_resonance': self.current_resonance,
            'target_resonance': self.target_resonance,
            'weight_history': self.weight_history.copy(),
            'resonance_history': self.resonance_history.copy(),
            'schedule': self.schedule,
            'kp': self.kp,
            'ki': self.ki
        }

    def reset(self):
        """Reset tracking history and adaptive parameters."""
        self.resonance_history = []
        self.weight_history = []
        self.current_weight = self.min_weight
        self.current_resonance = 0.0
        self.integral_error = 0.0
        self.kp = 0.1
        self.ki = 0.01


class PhiRegularizationLoss(nn.Module):
    """
    Simple phi regularization loss (non-adaptive version).

    For cases where fixed-weight regularization is preferred.

    Parameters
    ----------
    weight : float, default=0.1
        Loss weight
    target_phi : float, default=PHI
        Target golden ratio value
    method : str, default='ratio'
        Method: 'ratio' (dimension ratios) or 'cosine' (cosine similarity)
    """

    def __init__(
        self,
        weight: float = 0.1,
        target_phi: float = PHI,
        method: str = 'ratio'
    ):
        super().__init__()
        self.weight = weight
        self.target_phi = target_phi
        self.method = method

    def forward(self, latent_z: torch.Tensor) -> torch.Tensor:
        """
        Compute phi regularization loss.

        Parameters
        ----------
        latent_z : Tensor
            Latent representations (batch_size, latent_dim)

        Returns
        -------
        Tensor
            Phi regularization loss
        """
        if self.method == 'ratio':
            return self.weight * self._ratio_loss(latent_z)
        elif self.method == 'cosine':
            return self.weight * self._cosine_loss(latent_z)
        else:
            return self.weight * self._ratio_loss(latent_z)

    def _ratio_loss(self, latent_z: torch.Tensor) -> torch.Tensor:
        """Ratio-based phi loss."""
        latent_std = torch.std(latent_z, dim=0)

        if latent_std.numel() < 2:
            return torch.tensor(0.0, device=latent_z.device)

        ratios = latent_std[1:] / (latent_std[:-1] + 1e-10)
        target = torch.full_like(ratios, self.target_phi)

        return torch.mean((ratios - target) ** 2)

    def _cosine_loss(self, latent_z: torch.Tensor) -> torch.Tensor:
        """Cosine similarity to phi-scaled vector."""
        batch_size, latent_dim = latent_z.shape

        # Create phi-scaled target pattern
        phi_powers = torch.tensor(
            [self.target_phi ** (i / latent_dim) for i in range(latent_dim)],
            device=latent_z.device,
            dtype=latent_z.dtype
        )

        # Normalize
        latent_norm = latent_z / (torch.norm(latent_z, dim=1, keepdim=True) + 1e-10)
        phi_norm = phi_powers / (torch.norm(phi_powers) + 1e-10)

        # Cosine similarity (want to maximize, so minimize 1 - cos)
        cos_sim = torch.sum(latent_norm * phi_norm, dim=1)

        return torch.mean(1 - cos_sim)


def create_phi_loss(
    loss_type: str = 'adaptive',
    **kwargs
) -> nn.Module:
    """
    Factory function to create phi loss module.

    Parameters
    ----------
    loss_type : str
        Type of loss: 'adaptive', 'fixed', 'ratio', 'cosine'
    **kwargs
        Arguments passed to the loss class

    Returns
    -------
    nn.Module
        Phi loss module
    """
    if loss_type == 'adaptive':
        return AdaptivePhiLoss(**kwargs)
    elif loss_type in ('fixed', 'ratio'):
        return PhiRegularizationLoss(method='ratio', **kwargs)
    elif loss_type == 'cosine':
        return PhiRegularizationLoss(method='cosine', **kwargs)
    else:
        raise ValueError(f"Unknown loss type: {loss_type}")
