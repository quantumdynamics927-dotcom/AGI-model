"""
Golden Ratio Optimization Callback for Quantum VAE Training

Tracks and optimizes phi-resonance during training to maintain golden ratio
alignment in the latent space.

Enhanced Features (v2.0):
- Per-dimension-pair resonance tracking
- Fibonacci sequence detection in latent trajectories
- Automatic best-phi-epoch checkpoint saving
- TensorBoard integration for real-time monitoring
- Convergence detection and early stopping support
"""

import torch
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend for headless environments
import matplotlib.pyplot as plt
from pathlib import Path
import json

# Golden ratio constant (project standard)
PHI = 1.618033988749895

# Try to import TensorBoard
try:
    from torch.utils.tensorboard import SummaryWriter

    TENSORBOARD_AVAILABLE = True
except ImportError:
    TENSORBOARD_AVAILABLE = False


class GoldenRatioCallback:
    """
    Enhanced callback to monitor and optimize golden ratio resonance during training.

    Tracks phi-resonance in latent space with per-dimension-pair analysis,
    Fibonacci trajectory detection, and TensorBoard integration.

    Parameters
    ----------
    target_phi : float, default=PHI
        Target golden ratio value (1.618033988749895)
    resonance_threshold : float, default=0.7
        Minimum resonance score for "good" alignment
    save_dir : str, optional
        Directory to save plots and checkpoints
    track_frequency : int, default=10
        Track resonance every N epochs
    tensorboard_dir : str, optional
        Directory for TensorBoard logs. If provided, enables TensorBoard logging.
    save_best_checkpoint : bool, default=True
        Save model checkpoint when best phi resonance is achieved
    proximity_threshold : float, default=0.1
        Threshold for counting dimension ratios as phi-proximate
    """

    def __init__(
        self,
        target_phi: float = PHI,
        resonance_threshold: float = 0.7,
        save_dir: Optional[str] = None,
        track_frequency: int = 10,
        tensorboard_dir: Optional[str] = None,
        save_best_checkpoint: bool = True,
        proximity_threshold: float = 0.1,
    ):
        self.target_phi = target_phi
        self.resonance_threshold = resonance_threshold
        self.save_dir = Path(save_dir) if save_dir else None
        self.track_frequency = track_frequency
        self.save_best_checkpoint = save_best_checkpoint
        self.proximity_threshold = proximity_threshold

        # Tracking history - basic
        self.epochs: List[int] = []
        self.resonance_scores: List[float] = []
        self.phi_deviations: List[float] = []

        # Enhanced tracking - per-dimension-pair
        self.dimension_pair_history: Dict[Tuple[int, int], List[float]] = {}
        self.fibonacci_sequences: List[Dict] = []
        self.latent_trajectory: List[np.ndarray] = []

        # Best checkpoint tracking
        self.best_resonance = 0.0
        self.best_epoch = -1
        self.best_model_state = None

        # TensorBoard setup
        self.tensorboard_writer = None
        if tensorboard_dir and TENSORBOARD_AVAILABLE:
            self.tensorboard_writer = SummaryWriter(tensorboard_dir)
        elif tensorboard_dir and not TENSORBOARD_AVAILABLE:
            print(
                "Warning: TensorBoard not available. Install with: pip install tensorboard"
            )

        if self.save_dir:
            self.save_dir.mkdir(parents=True, exist_ok=True)

    def on_epoch_end(
        self,
        epoch: int,
        model: torch.nn.Module,
        latent_samples: Optional[torch.Tensor] = None,
    ) -> Dict[str, Any]:
        """
        Called at the end of each epoch to track phi-resonance.

        Parameters
        ----------
        epoch : int
            Current epoch number
        model : nn.Module
            QuantumVAE model instance
        latent_samples : Tensor, optional
            Latent space samples (batch_size, latent_dim)

        Returns
        -------
        dict
            Dictionary with resonance metrics
        """
        if epoch % self.track_frequency != 0 and epoch > 0:
            return {}

        # Compute resonance from latent samples if available
        if latent_samples is not None and latent_samples.numel() > 0:
            latent_np = latent_samples.detach().cpu().numpy()

            # Compute overall resonance
            resonance = self._compute_resonance_from_latent(latent_np)

            # Track per-dimension-pair resonance
            pair_resonances = self.track_dimension_pairs(latent_np)

            # Store latent trajectory for Fibonacci detection
            mean_latent = np.mean(latent_np, axis=0)
            self.latent_trajectory.append(mean_latent)

            # Detect Fibonacci sequences if enough history
            if len(self.latent_trajectory) >= 3:
                self.detect_fibonacci_trajectories()

        elif latent_samples is not None and hasattr(model, "compute_phi_resonance"):
            resonance = model.compute_phi_resonance(latent_samples)
            pair_resonances = {}
        else:
            resonance = self._compute_resonance_from_weights(model)
            pair_resonances = {}

        # Calculate phi deviation
        phi_deviation = abs(self.target_phi - self.target_phi * (1 - resonance))

        # Store metrics
        self.epochs.append(epoch)
        self.resonance_scores.append(resonance)
        self.phi_deviations.append(phi_deviation)

        # Check for best resonance and save checkpoint
        if resonance > self.best_resonance:
            self.best_resonance = resonance
            self.best_epoch = epoch
            if self.save_best_checkpoint:
                self.save_best_phi_checkpoint(model, epoch)

        # Log to TensorBoard
        if self.tensorboard_writer is not None:
            self.log_to_tensorboard(epoch, resonance, phi_deviation, pair_resonances)

        metrics = {
            "phi_resonance": resonance,
            "phi_deviation": phi_deviation,
            "phi_aligned": resonance >= self.resonance_threshold,
            "best_resonance": self.best_resonance,
            "best_epoch": self.best_epoch,
            "pair_resonances": pair_resonances,
        }

        return metrics

    def _compute_resonance_from_latent(self, latent_np: np.ndarray) -> float:
        """
        Compute phi resonance directly from latent codes.

        Parameters
        ----------
        latent_np : ndarray
            Latent codes (n_samples, n_dims)

        Returns
        -------
        float
            Resonance score (0-1)
        """
        n_samples, n_dims = latent_np.shape
        if n_dims < 2:
            return 0.0

        phi_count = 0
        total_count = 0

        for i in range(n_dims - 1):
            ratios = np.abs(latent_np[:, i + 1]) / (np.abs(latent_np[:, i]) + 1e-10)
            proximity = np.abs(ratios - self.target_phi)
            phi_count += np.sum(proximity < self.proximity_threshold)
            total_count += len(ratios)

        return phi_count / total_count if total_count > 0 else 0.0

    def _compute_resonance_from_weights(self, model: torch.nn.Module) -> float:
        """
        Compute phi-resonance from model weights as fallback.

        Parameters
        ----------
        model : nn.Module
            QuantumVAE model

        Returns
        -------
        float
            Resonance score (0-1)
        """
        resonance_scores = []

        for name, param in model.named_parameters():
            if "weight" in name and param.dim() >= 2:
                shape = param.shape
                if shape[0] > 0 and shape[1] > 0:
                    ratio = shape[0] / shape[1]
                    if ratio > 0:
                        # Measure proximity to phi
                        phi_proximity = (
                            1.0 - abs(ratio - self.target_phi) / self.target_phi
                        )
                        resonance_scores.append(max(0.0, phi_proximity))

        return np.mean(resonance_scores) if resonance_scores else 0.0

    def track_dimension_pairs(
        self, latent_np: np.ndarray
    ) -> Dict[Tuple[int, int], float]:
        """
        Track phi resonance for each dimension pair.

        Parameters
        ----------
        latent_np : ndarray
            Latent codes (n_samples, n_dims)

        Returns
        -------
        dict
            Resonance score for each adjacent dimension pair
        """
        n_samples, n_dims = latent_np.shape
        pair_resonances = {}

        for i in range(n_dims - 1):
            pair = (i, i + 1)
            ratios = np.abs(latent_np[:, i + 1]) / (np.abs(latent_np[:, i]) + 1e-10)
            proximity = np.abs(ratios - self.target_phi)
            resonance = np.mean(proximity < self.proximity_threshold)

            pair_resonances[pair] = resonance

            # Store in history
            if pair not in self.dimension_pair_history:
                self.dimension_pair_history[pair] = []
            self.dimension_pair_history[pair].append(resonance)

        return pair_resonances

    def detect_fibonacci_trajectories(self) -> List[Dict]:
        """
        Detect Fibonacci-like sequences in latent trajectory.

        Fibonacci property: L[n] + L[n+1] ≈ L[n+2] (scaled by phi)

        Returns
        -------
        list of dict
            Detected Fibonacci patterns
        """
        if len(self.latent_trajectory) < 3:
            return []

        trajectory = np.array(self.latent_trajectory)
        n_epochs, n_dims = trajectory.shape

        patterns = []
        tolerance = 0.2  # 20% tolerance

        for dim in range(n_dims):
            dim_values = trajectory[:, dim]

            for i in range(len(dim_values) - 2):
                v1, v2, v3 = dim_values[i], dim_values[i + 1], dim_values[i + 2]

                # Check Fibonacci-like relationship
                if abs(v1) > 1e-6 and abs(v2) > 1e-6:
                    expected_v3 = v1 + v2
                    if abs(expected_v3) > 1e-6:
                        ratio = v3 / expected_v3
                        if 1 - tolerance < ratio < 1 + tolerance:
                            patterns.append(
                                {
                                    "dimension": dim,
                                    "start_epoch": i,
                                    "values": (v1, v2, v3),
                                    "ratio": ratio,
                                    "quality": 1 - abs(1 - ratio),
                                }
                            )

        # Store high-quality patterns
        self.fibonacci_sequences = [p for p in patterns if p["quality"] > 0.8]

        return self.fibonacci_sequences

    def save_best_phi_checkpoint(self, model: torch.nn.Module, epoch: int):
        """
        Save model checkpoint when best phi resonance is achieved.

        Parameters
        ----------
        model : nn.Module
            Model to save
        epoch : int
            Current epoch
        """
        self.best_model_state = {
            "epoch": epoch,
            "model_state_dict": model.state_dict(),
            "resonance": self.best_resonance,
            "phi_deviation": self.phi_deviations[-1] if self.phi_deviations else 0.0,
        }

        if self.save_dir:
            checkpoint_path = self.save_dir / "best_phi_model.pt"
            torch.save(self.best_model_state, checkpoint_path)

    def log_to_tensorboard(
        self,
        epoch: int,
        resonance: float,
        phi_deviation: float,
        pair_resonances: Dict[Tuple[int, int], float],
    ):
        """
        Log metrics to TensorBoard.

        Parameters
        ----------
        epoch : int
            Current epoch
        resonance : float
            Overall resonance score
        phi_deviation : float
            Deviation from target phi
        pair_resonances : dict
            Per-pair resonance scores
        """
        if self.tensorboard_writer is None:
            return

        writer = self.tensorboard_writer

        # Log scalar metrics
        writer.add_scalar("phi/resonance", resonance, epoch)
        writer.add_scalar("phi/deviation", phi_deviation, epoch)
        writer.add_scalar("phi/best_resonance", self.best_resonance, epoch)

        # Log per-dimension-pair resonances (top 5 pairs)
        if pair_resonances:
            sorted_pairs = sorted(
                pair_resonances.items(), key=lambda x: x[1], reverse=True
            )
            for (i, j), res in sorted_pairs[:5]:
                writer.add_scalar(f"phi/pair_{i}_{j}", res, epoch)

        # Log histogram of resonances if we have enough data
        if len(self.resonance_scores) > 10:
            writer.add_histogram(
                "phi/resonance_history", np.array(self.resonance_scores), epoch
            )

        writer.flush()

    def get_best_dimension_pairs(self, top_k: int = 5) -> List[Dict]:
        """
        Get dimension pairs with highest average phi resonance.

        Parameters
        ----------
        top_k : int, default=5
            Number of top pairs to return

        Returns
        -------
        list of dict
            Top dimension pairs with their average resonance
        """
        pair_averages = []

        for pair, history in self.dimension_pair_history.items():
            if len(history) > 0:
                pair_averages.append(
                    {
                        "pair": pair,
                        "mean_resonance": np.mean(history),
                        "max_resonance": np.max(history),
                        "trend": np.mean(np.diff(history)) if len(history) > 1 else 0.0,
                        "n_observations": len(history),
                    }
                )

        # Sort by mean resonance
        pair_averages.sort(key=lambda x: x["mean_resonance"], reverse=True)

        return pair_averages[:top_k]

    def close(self):
        """Clean up resources (close TensorBoard writer)."""
        if self.tensorboard_writer is not None:
            self.tensorboard_writer.close()

    def plot_resonance_history(self, save_path: Optional[str] = None):
        """
        Plot phi-resonance history over training

        Args:
            save_path: Path to save plot (optional)
        """
        if len(self.epochs) == 0:
            print("No resonance data to plot")
            return

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

        # Plot resonance scores
        ax1.plot(
            self.epochs, self.resonance_scores, "b-", marker="o", label="Phi Resonance"
        )
        ax1.axhline(
            y=self.resonance_threshold,
            color="r",
            linestyle="--",
            label=f"Threshold ({self.resonance_threshold})",
        )
        ax1.axhline(
            y=1.0, color="g", linestyle="--", alpha=0.3, label="Perfect Alignment"
        )
        ax1.set_xlabel("Epoch")
        ax1.set_ylabel("Resonance Score")
        ax1.set_title("Golden Ratio Resonance During Training")
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_ylim(0, 1.1)

        # Plot phi deviations
        ax2.plot(
            self.epochs, self.phi_deviations, "r-", marker="s", label="Phi Deviation"
        )
        ax2.set_xlabel("Epoch")
        ax2.set_ylabel("Deviation from Target Phi")
        ax2.set_title("Phi Deviation Over Time")
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"Resonance plot saved to {save_path}")
        else:
            plt.show()

    def get_summary(self) -> Dict[str, Any]:
        """
        Get comprehensive summary statistics of phi-resonance tracking.

        Returns
        -------
        dict
            Dictionary with summary statistics including:
            - Basic metrics (mean, max, min, final resonance)
            - Best checkpoint info
            - Top dimension pairs
            - Fibonacci patterns detected
            - Trend information
        """
        if len(self.resonance_scores) == 0:
            return {"status": "No data collected"}

        # Basic statistics
        summary = {
            "epochs_tracked": len(self.epochs),
            "mean_resonance": float(np.mean(self.resonance_scores)),
            "max_resonance": float(np.max(self.resonance_scores)),
            "min_resonance": float(np.min(self.resonance_scores)),
            "std_resonance": float(np.std(self.resonance_scores)),
            "final_resonance": float(self.resonance_scores[-1]),
            "resonance_above_threshold": sum(
                1 for r in self.resonance_scores if r >= self.resonance_threshold
            ),
            "phi_aligned": self.resonance_scores[-1] >= self.resonance_threshold,
            "target_phi": self.target_phi,
        }

        # Best checkpoint info
        summary["best_epoch"] = self.best_epoch
        summary["best_resonance"] = float(self.best_resonance)

        # Trend analysis
        if len(self.resonance_scores) > 1:
            summary["overall_trend"] = float(np.mean(np.diff(self.resonance_scores)))
            if len(self.resonance_scores) >= 5:
                recent = self.resonance_scores[-5:]
                summary["recent_trend"] = float(np.mean(np.diff(recent)))
            else:
                summary["recent_trend"] = summary["overall_trend"]
        else:
            summary["overall_trend"] = 0.0
            summary["recent_trend"] = 0.0

        # Top dimension pairs
        summary["top_dimension_pairs"] = self.get_best_dimension_pairs(top_k=5)

        # Fibonacci patterns
        summary["fibonacci_patterns_found"] = len(self.fibonacci_sequences)
        if self.fibonacci_sequences:
            best_fib = max(self.fibonacci_sequences, key=lambda x: x["quality"])
            summary["best_fibonacci_pattern"] = {
                "dimension": best_fib["dimension"],
                "quality": best_fib["quality"],
            }

        # Convergence check
        if len(self.resonance_scores) >= 10:
            recent_10 = self.resonance_scores[-10:]
            summary["is_converged"] = np.std(recent_10) < 0.01
        else:
            summary["is_converged"] = False

        return summary

    def save_history(self, filepath: Optional[str] = None):
        """
        Save tracking history to JSON file.

        Parameters
        ----------
        filepath : str, optional
            Path to save file. Uses save_dir if not specified.
        """
        if filepath is None:
            if self.save_dir:
                filepath = self.save_dir / "phi_tracking_history.json"
            else:
                filepath = "phi_tracking_history.json"

        history = {
            "epochs": self.epochs,
            "resonance_scores": self.resonance_scores,
            "phi_deviations": self.phi_deviations,
            "best_epoch": self.best_epoch,
            "best_resonance": self.best_resonance,
            "target_phi": self.target_phi,
            "dimension_pair_history": {
                f"{k[0]}_{k[1]}": v for k, v in self.dimension_pair_history.items()
            },
        }

        with open(filepath, "w") as f:
            json.dump(history, f, indent=2)

    def load_history(self, filepath: str):
        """
        Load tracking history from JSON file.

        Parameters
        ----------
        filepath : str
            Path to history file
        """
        with open(filepath, "r") as f:
            history = json.load(f)

        self.epochs = history.get("epochs", [])
        self.resonance_scores = history.get("resonance_scores", [])
        self.phi_deviations = history.get("phi_deviations", [])
        self.best_epoch = history.get("best_epoch", -1)
        self.best_resonance = history.get("best_resonance", 0.0)

        # Reconstruct dimension pair history
        pair_history = history.get("dimension_pair_history", {})
        self.dimension_pair_history = {}
        for key, value in pair_history.items():
            i, j = map(int, key.split("_"))
            self.dimension_pair_history[(i, j)] = value


def phi_regularization_loss(
    latent_z: torch.Tensor, target_phi: float = PHI, weight: float = 0.1
) -> torch.Tensor:
    """
    Compute golden ratio regularization loss

    Encourages latent dimensions to have phi-resonant relationships.

    Args:
        latent_z: Latent representations (batch, latent_dim)
        target_phi: Target golden ratio value
        weight: Loss weight

    Returns:
        Scalar regularization loss
    """
    # Compute standard deviations per dimension
    latent_std = torch.std(latent_z, dim=0)  # (latent_dim,)

    # Compute ratios between adjacent dimensions
    ratios = latent_std[1:] / (latent_std[:-1] + 1e-10)

    # Target phi ratio
    target_ratio = torch.full_like(ratios, target_phi)

    # MSE loss to phi target
    phi_loss = torch.mean((ratios - target_ratio) ** 2)

    return weight * phi_loss
