"""
Performance Monitoring and Visualization Utilities for Quantum VAE

Provides comprehensive monitoring of training metrics, model performance,
and quantum-specific measurements.
"""

import torch
import numpy as np
import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend for headless environments
import matplotlib.pyplot as plt
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import json
from datetime import datetime

# Flag for sklearn availability (PAC already imported directly)
SKLEARN_AVAILABLE = True


class SafeJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle PyTorch/NumPy types and other non-serializable objects."""

    def default(self, obj):
        # Handle Python bool explicitly (shouldn't be needed but defensive)
        if isinstance(obj, bool):
            return bool(obj)
        # Handle Python int and float explicitly (defensive)
        if isinstance(obj, (int, float)):
            return obj
        if hasattr(obj, "item"):  # Handles PyTorch 0-dim tensors and NumPy scalars
            return obj.item()
        if hasattr(obj, "tolist"):  # Handles PyTorch tensors and NumPy arrays
            return obj.tolist()
        # Fallback for other non-serializable objects
        if isinstance(obj, np.bool_):
            return bool(obj)
        return super().default(obj)

    def encode(self, obj):
        """Override encode to handle dict keys that aren't JSON serializable."""

        def sanitize_keys(o):
            """Recursively convert tuple/non-string keys to strings."""
            if isinstance(o, dict):
                return {
                    str(k)
                    if not isinstance(k, (str, int, float, bool, type(None)))
                    else k: sanitize_keys(v)
                    for k, v in o.items()
                }
            elif isinstance(o, (list, tuple)):
                return [sanitize_keys(item) for item in o]
            return o

        return super().encode(sanitize_keys(obj))


class PerformanceMonitor:
    """
    Comprehensive performance monitoring for Quantum VAE training

    Tracks:
    - All loss components
    - Quantum metrics (fidelity, entropy, coherence)
    - Training efficiency
    - Model convergence
    """

    def __init__(self, save_dir: Optional[str] = None):
        """
        Initialize performance monitor

        Args:
            save_dir: Directory to save monitoring data and plots
        """
        self.save_dir = Path(save_dir) if save_dir else None
        if self.save_dir:
            self.save_dir.mkdir(parents=True, exist_ok=True)

        # Metrics storage
        self.epochs: List[int] = []
        self.train_metrics: Dict[str, List[float]] = {}
        self.val_metrics: Dict[str, List[float]] = {}
        self.quantum_metrics: Dict[str, List[float]] = {}
        self.timestamps: List[str] = []

        # Initialize metric lists
        self._init_metric_lists()

    def _init_metric_lists(self):
        """Initialize all metric lists"""
        metric_names = [
            "total_loss",
            "recon",
            "kl",
            "hamming",
            "coherence",
            "hw",
            "mixed_state",
            "fidelity",
            "entropy",
        ]

        for name in metric_names:
            self.train_metrics[name] = []
            self.val_metrics[name] = []

    def record_metric(self, name: str, value: float, mode: str = "train"):
        """
        Record a single metric value.

        Args:
            name: Metric name
            value: Metric value
            mode: 'train' or 'val'
        """
        metrics_dict = self.train_metrics if mode == "train" else self.val_metrics
        if name not in metrics_dict:
            metrics_dict[name] = []
        metrics_dict[name].append(float(value))

    def record_epoch(
        self,
        epoch: int,
        train_metrics: Dict[str, float],
        val_metrics: Dict[str, float],
        quantum_metrics: Optional[Dict[str, float]] = None,
    ):
        """
        Record metrics for an epoch

        Args:
            epoch: Epoch number
            train_metrics: Training metrics dictionary
            val_metrics: Validation metrics dictionary
            quantum_metrics: Optional quantum-specific metrics
        """
        self.epochs.append(epoch)
        self.timestamps.append(datetime.now().isoformat())

        # Record training metrics
        for key in self.train_metrics:
            if key in train_metrics:
                self.train_metrics[key].append(train_metrics[key])
            else:
                self.train_metrics[key].append(0.0)

        # Record validation metrics
        for key in self.val_metrics:
            if key in val_metrics:
                self.val_metrics[key].append(val_metrics[key])
            else:
                self.val_metrics[key].append(0.0)

        # Record quantum metrics
        if quantum_metrics:
            for key, value in quantum_metrics.items():
                if key not in self.quantum_metrics:
                    self.quantum_metrics[key] = []
                self.quantum_metrics[key].append(value)

    def plot_all_metrics(self, save_path: Optional[str] = None):
        """
        Create comprehensive visualization of all metrics

        Args:
            save_path: Path to save plot (optional)
        """
        if len(self.epochs) == 0:
            print("No metrics to plot")
            return

        plt.figure(figsize=(16, 12))

        # Loss components (3x3 grid)
        loss_metrics = [
            "total_loss",
            "recon",
            "kl",
            "hamming",
            "coherence",
            "hw",
            "mixed_state",
            "fidelity",
            "entropy",
        ]

        for i, metric in enumerate(loss_metrics):
            ax = plt.subplot(3, 3, i + 1)

            if metric in self.train_metrics and len(self.train_metrics[metric]) > 0:
                ax.plot(
                    self.epochs,
                    self.train_metrics[metric],
                    "b-",
                    marker="o",
                    markersize=2,
                    label="Train",
                    alpha=0.7,
                )
            if metric in self.val_metrics and len(self.val_metrics[metric]) > 0:
                ax.plot(
                    self.epochs,
                    self.val_metrics[metric],
                    "r-",
                    marker="s",
                    markersize=2,
                    label="Val",
                    alpha=0.7,
                )

            ax.set_xlabel("Epoch")
            ax.set_ylabel("Loss")
            ax.set_title(f"{metric.replace('_', ' ').title()}")
            ax.legend()
            ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"Metrics plot saved to {save_path}")
        else:
            plt.show()

    def _extract_scalar(self, v, key=None):
        """Extract scalar value from potentially dict input."""
        if isinstance(v, dict):
            if key and key in v:
                return float(v[key])
            # Try to extract first numeric value from dict
            for val in v.values():
                try:
                    return float(val)
                except (TypeError, ValueError):
                    continue
            return float("nan")
        try:
            return float(v)
        except (TypeError, ValueError):
            return float("nan")

    def plot_quantum_metrics(self, save_path: Optional[str] = None):
        """
        Plot quantum-specific metrics

        Args:
            save_path: Path to save plot (optional)
        """
        if len(self.quantum_metrics) == 0:
            print("No quantum metrics to plot")
            return

        n_metrics = len(self.quantum_metrics)
        cols = min(3, n_metrics)
        rows = (n_metrics + cols - 1) // cols

        fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 4 * rows))
        if n_metrics == 1:
            axes = [axes]
        else:
            axes = axes.flatten()

        for i, (metric, values) in enumerate(self.quantum_metrics.items()):
            ax = axes[i] if n_metrics > 1 else axes[0]
            epochs_to_plot = (
                self.epochs[-len(values) :]
                if len(values) < len(self.epochs)
                else self.epochs
            )
            scalar_values = [self._extract_scalar(v, key=metric) for v in values]
            ax.plot(epochs_to_plot, scalar_values, "g-", marker="o", markersize=3)
            ax.set_xlabel("Epoch")
            ax.set_ylabel("Value")
            ax.set_title(f"{metric.replace('_', ' ').title()}")
            ax.grid(True, alpha=0.3)

        # Hide unused subplots
        for i in range(n_metrics, len(axes)):
            axes[i].axis("off")

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"Quantum metrics plot saved to {save_path}")
        else:
            plt.show()

    def save_metrics_json(
        self,
        filepath="artifacts/metrics_summary.json",
        save_path=None,
    ):
        """Save all metrics to JSON file with sanitized keys."""
        import os

        if save_path is not None:
            filepath = save_path

        def sanitize_for_json(obj):
            if isinstance(obj, dict):
                # Force all keys to be strings to ensure JSON compatibility
                sanitized_dict = {}
                for k, v in obj.items():
                    # Convert key to string, handling potential tuple keys
                    str_key = (
                        str(k)
                        if not isinstance(k, (str, int, float, bool, type(None)))
                        else k
                    )
                    sanitized_dict[str_key] = sanitize_for_json(v)
                return sanitized_dict
            elif isinstance(obj, (list, tuple, set)):
                return [sanitize_for_json(i) for i in obj]
            elif hasattr(obj, "item"):
                return obj.item()
            elif hasattr(obj, "tolist"):
                return obj.tolist()
            elif type(obj).__name__ == "bool":
                return bool(obj)
            return obj

        directory = os.path.dirname(filepath)
        if directory:
            os.makedirs(directory, exist_ok=True)

        # Build data structure with existing attributes
        data = {
            "epochs": self.epochs,
            "timestamps": self.timestamps,
            "train_metrics": self.train_metrics,
            "val_metrics": self.val_metrics,
            "quantum_metrics": self.quantum_metrics,
        }

        # Sanitize everything to ensure JSON compatibility
        safe_data = sanitize_for_json(data)

        # Dump without the cls argument to avoid conflicts
        with open(filepath, "w") as f:
            json.dump(safe_data, f, indent=2)

        print(f"Metrics saved to {filepath}")

    def get_best_epoch(
        self, metric: str = "total_loss", mode: str = "val"
    ) -> Tuple[int, float]:
        """
        Get epoch with best metric value

        Args:
            metric: Metric name to check
            mode: 'train' or 'val'

        Returns:
            Tuple of (best_epoch, best_value)
        """
        metrics_dict = self.val_metrics if mode == "val" else self.train_metrics

        if metric not in metrics_dict or len(metrics_dict[metric]) == 0:
            return -1, float("inf")

        values = metrics_dict[metric]
        best_idx = np.argmin(values)  # Assuming lower is better
        best_epoch = self.epochs[best_idx]
        best_value = values[best_idx]

        return best_epoch, best_value

    def get_summary(self) -> Dict[str, any]:
        """
        Get summary statistics

        Returns:
            Dictionary with summary statistics
        """
        if len(self.epochs) == 0:
            return {"status": "No data collected"}

        summary = {
            "total_epochs": len(self.epochs),
            "best_val_loss_epoch": self.get_best_epoch("total_loss", "val")[0],
            "best_val_loss": self.get_best_epoch("total_loss", "val")[1],
            "final_val_loss": self.val_metrics["total_loss"][-1]
            if len(self.val_metrics["total_loss"]) > 0
            else None,
            "final_train_loss": self.train_metrics["total_loss"][-1]
            if len(self.train_metrics["total_loss"]) > 0
            else None,
        }

        # Add quantum metrics summary
        if len(self.quantum_metrics) > 0:
            summary["quantum_metrics"] = {
                k: {
                    "final": v[-1] if len(v) > 0 else None,
                    "mean": np.mean(v) if len(v) > 0 else None,
                    "max": np.max(v) if len(v) > 0 else None,
                    "min": np.min(v) if len(v) > 0 else None,
                }
                for k, v in self.quantum_metrics.items()
            }

        return summary


def plot_phi_shell_geometry(
    model, dataloader, device, save_path="artifacts/phi_shell.png"
):
    """
    Visualize the Phi-shell geometry in the latent space.

    This function extracts latent embeddings (mu) from the model and creates:
    1. A histogram of L2 radii showing concentration around the golden ratio shell
    2. A 2D PCA projection with the theoretical phi-shell circle overlay

    Args:
        model: The trained VAE model with .encode() or forward method returning mu
        dataloader: DataLoader containing the data to visualize
        device: torch device ('cpu', 'cuda', etc.)
        save_path: Path to save the visualization

    Note: This requires sklearn.decomposition.PCA for dimensionality reduction.
    """
    import numpy as np
    import matplotlib.pyplot as plt

    model.eval()

    all_mu = []
    all_labels = []

    # Extract latent embeddings
    with torch.no_grad():
        for batch_data in dataloader:
            # Handle different dataloader formats (single tensor vs tuple)
            if isinstance(batch_data, (list, tuple)):
                batch_x = batch_data[0].to(device)
            else:
                batch_x = batch_data.to(device)

            # Forward pass to get mu (latent mean)
            if hasattr(model, "encode"):
                mu, log_var = model.encode(batch_x)
            else:
                # Assume forward returns (recon, mu, log_var, ...)
                recon_x, mu, log_var, _ = model(batch_x, return_density=True)

            all_mu.append(mu.cpu().numpy())

            # Try to extract labels if available
            if len(batch_data) > 1 and batch_data[1] is not None:
                labels = batch_data[1].cpu().numpy()
                all_labels.append(labels)
            else:
                # No labels provided, assign dummy label
                all_labels.append(np.zeros(len(mu)))

    # Concatenate all batches
    mu_array = np.concatenate(all_mu, axis=0)
    labels_array = np.concatenate(all_labels, axis=0)

    # Calculate radii (L2 norm of each latent vector)
    radii = np.linalg.norm(mu_array, axis=1)

    # Target phi-shell radius (k * PHI where k=3.5, PHI=1.618...)
    PHI = (1 + 5**0.5) / 2
    r_star = 3.5 * PHI  # ≈ 5.66

    # Create figure with 2 subplots
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Subplot 1: Histogram of radii
    ax1 = axes[0]
    ax1.hist(
        radii, bins=50, alpha=0.7, color="steelblue", edgecolor="black", density=True
    )
    ax1.axvline(
        r_star,
        color="red",
        linestyle="--",
        linewidth=2,
        label=f"φ-Shell (r* ≈ {r_star:.2f})",
    )
    ax1.axvline(
        radii.mean(),
        color="green",
        linestyle="-",
        linewidth=2,
        label=f"Mean (μ ≈ {radii.mean():.2f})",
    )
    ax1.set_xlabel("Latent Radius ||μ||₂", fontsize=12)
    ax1.set_ylabel("Density", fontsize=12)
    ax1.set_title(
        "Phi-Shell Formation: Latent Radius Distribution",
        fontsize=14,
        fontweight="bold",
    )
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(0, max(radii.max() * 1.1, r_star * 1.5))

    # Add statistics text
    stats_text = f"Mean: {radii.mean():.3f}\nStd: {radii.std():.3f}\nMedian: {np.median(radii):.3f}"
    ax1.text(
        0.95,
        0.95,
        stats_text,
        transform=ax1.transAxes,
        fontsize=9,
        verticalalignment="top",
        horizontalalignment="right",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
    )

    # Subplot 2: 2D PCA projection
    ax2 = axes[1]
    try:
        from sklearn.decomposition import PCA

        # Reduce to 2D
        pca = PCA(n_components=2)
        mu_2d = pca.fit_transform(mu_array)

        # Scatter plot colored by domain labels
        unique_labels = np.unique(labels_array)
        colors = plt.cm.tab10(np.linspace(0, 1, len(unique_labels)))

        for i, label in enumerate(unique_labels):
            mask = labels_array == label
            ax2.scatter(
                mu_2d[mask, 0],
                mu_2d[mask, 1],
                c=[colors[i]],
                label=f"Domain {int(label)}",
                alpha=0.6,
                s=20,
                edgecolors="none",
            )

        # Draw theoretical phi-shell circle (projected to 2D)
        # The circle in PCA space will be an ellipse, but we draw as circle for visualization
        theta = np.linspace(0, 2 * np.pi, 100)
        circle_x = r_star * np.cos(theta)
        circle_y = r_star * np.sin(theta)
        ax2.plot(
            circle_x, circle_y, "r--", linewidth=2, label=f"φ-Shell (r* ≈ {r_star:.2f})"
        )

        ax2.set_xlabel(
            f"PC1 ({pca.explained_variance_ratio_[0] * 100:.1f}% var)", fontsize=12
        )
        ax2.set_ylabel(
            f"PC2 ({pca.explained_variance_ratio_[1] * 100:.1f}% var)", fontsize=12
        )
        ax2.set_title(
            "Phi-Shell Geometry: 2D PCA Projection", fontsize=14, fontweight="bold"
        )
        ax2.legend(fontsize=9, loc="upper right")
        ax2.grid(True, alpha=0.3)
        ax2.axis("equal")

        # Center the view
        max_radius_2d = np.max(np.abs(mu_2d)) * 1.1
        ax2.set_xlim(-max_radius_2d, max_radius_2d)
        ax2.set_ylim(-max_radius_2d, max_radius_2d)

    except ImportError:
        ax2.text(
            0.5,
            0.5,
            "sklearn not available\nCannot perform PCA projection",
            transform=ax2.transAxes,
            ha="center",
            va="center",
            fontsize=12,
            bbox=dict(boxstyle="round", facecolor="orange", alpha=0.5),
        )
        ax2.set_title(
            "Phi-Shell Geometry: PCA Unavailable", fontsize=14, fontweight="bold"
        )

    plt.tight_layout()

    # Ensure save directory exists
    import os

    os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)

    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close(fig)

    print(f"Phi-shell geometry visualization saved to: {save_path}")
    print(
        f"  Latent radius statistics: mean={radii.mean():.3f}, std={radii.std():.3f}, target={r_star:.3f}"
    )

    # Return statistics for analysis
    return {
        "mean_radius": float(radii.mean()),
        "std_radius": float(radii.std()),
        "median_radius": float(np.median(radii)),
        "target_radius": float(r_star),
        "phi_alignment_score": float(
            np.exp(-np.abs(radii.mean() - r_star) / r_star)
        ),  # Higher = better alignment
    }
