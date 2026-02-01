"""
Golden Ratio Time-Series Analysis Module

Track and analyze phi resonance evolution during VAE training, including:
- Epoch-by-epoch resonance tracking
- Convergence detection and prediction
- Change-point detection for phi emergence events
- Trend analysis with exponential smoothing
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Callable
import warnings

# Golden ratio constant
PHI = 1.618033988749895


class PhiTimeSeriesAnalyzer:
    """
    Analyze golden ratio patterns over training time.

    Tracks how phi resonance evolves during VAE training, detects
    convergence points, and predicts future trajectories.

    Parameters
    ----------
    random_state : int, optional
        Random seed for reproducibility

    Attributes
    ----------
    phi : float
        Golden ratio constant
    resonance_history : list
        Recorded resonance scores over epochs
    epoch_history : list
        Corresponding epoch numbers
    """

    def __init__(self, random_state: Optional[int] = 42):
        self.phi = PHI
        self.random_state = random_state

        # History tracking
        self.resonance_history: List[float] = []
        self.epoch_history: List[int] = []
        self.latent_history: List[np.ndarray] = []

        # Analysis results cache
        self._smoothed = None
        self._convergence_point = None

        if random_state is not None:
            np.random.seed(random_state)

    def record_epoch(
        self,
        epoch: int,
        latent_codes: np.ndarray,
        threshold: float = 0.1
    ) -> Dict:
        """
        Record phi resonance for a single training epoch.

        Parameters
        ----------
        epoch : int
            Current epoch number
        latent_codes : ndarray
            Latent codes from VAE for this epoch (n_samples, n_dims)
        threshold : float, default=0.1
            Threshold for phi proximity

        Returns
        -------
        dict
            Resonance metrics for this epoch
        """
        # Compute resonance score
        resonance = self._compute_resonance(latent_codes, threshold)

        # Store history
        self.epoch_history.append(epoch)
        self.resonance_history.append(resonance['score'])
        self.latent_history.append(latent_codes.copy())

        # Invalidate caches
        self._smoothed = None
        self._convergence_point = None

        return resonance

    def _compute_resonance(
        self,
        latent_codes: np.ndarray,
        threshold: float
    ) -> Dict:
        """Compute phi resonance score for latent codes."""
        n_samples, n_dims = latent_codes.shape

        # Compute dimension ratios
        phi_counts = 0
        total_ratios = 0
        proximities = []

        for i in range(n_dims - 1):
            ratios = np.abs(latent_codes[:, i + 1]) / (
                np.abs(latent_codes[:, i]) + 1e-10
            )
            proximity = np.abs(ratios - self.phi)
            proximities.extend(proximity)
            phi_counts += np.sum(proximity < threshold)
            total_ratios += len(ratios)

        score = phi_counts / total_ratios if total_ratios > 0 else 0.0
        mean_proximity = np.mean(proximities) if proximities else float('inf')

        return {
            'score': score,
            'mean_proximity': mean_proximity,
            'phi_count': phi_counts,
            'total_ratios': total_ratios
        }

    def track_epoch_resonance(
        self,
        model,
        data_loader,
        epochs: int,
        threshold: float = 0.1,
        callback: Optional[Callable] = None,
        verbose: bool = True
    ) -> Dict:
        """
        Track resonance across multiple training epochs.

        Note: This is for analysis only - it doesn't train the model.
        Use this to analyze an already-training model by hooking into
        the training loop.

        Parameters
        ----------
        model : nn.Module
            VAE model with encode() method
        data_loader : DataLoader
            Data loader for extracting latent codes
        epochs : int
            Number of epochs to track
        threshold : float, default=0.1
            Threshold for phi proximity
        callback : callable, optional
            Function called each epoch with (epoch, resonance_dict)
        verbose : bool, default=True
            Print progress

        Returns
        -------
        dict
            Complete tracking results
        """
        import torch

        model.eval()

        for epoch in range(epochs):
            # Extract latent codes for this epoch
            latent_codes_list = []

            with torch.no_grad():
                for batch_data in data_loader:
                    if isinstance(batch_data, (list, tuple)):
                        batch_data = batch_data[0]
                    mu, _ = model.encode(batch_data)
                    latent_codes_list.append(mu.cpu().numpy())

            latent_codes = np.concatenate(latent_codes_list, axis=0)

            # Record this epoch
            resonance = self.record_epoch(epoch, latent_codes, threshold)

            if callback:
                callback(epoch, resonance)

            if verbose and (epoch % 10 == 0 or epoch == epochs - 1):
                print(f"Epoch {epoch}: resonance={resonance['score']:.4f}, "
                      f"proximity={resonance['mean_proximity']:.4f}")

        return self.get_summary()

    def get_smoothed_resonance(
        self,
        alpha: float = 0.3,
        method: str = 'ewma'
    ) -> np.ndarray:
        """
        Get exponentially smoothed resonance history.

        Parameters
        ----------
        alpha : float, default=0.3
            Smoothing factor (0-1). Higher = less smoothing.
        method : str, default='ewma'
            Smoothing method: 'ewma' (exponential), 'sma' (simple moving avg)

        Returns
        -------
        ndarray
            Smoothed resonance values
        """
        if len(self.resonance_history) == 0:
            return np.array([])

        history = np.array(self.resonance_history)

        if method == 'ewma':
            # Exponentially weighted moving average
            smoothed = np.zeros_like(history)
            smoothed[0] = history[0]
            for i in range(1, len(history)):
                smoothed[i] = alpha * history[i] + (1 - alpha) * smoothed[i - 1]
        elif method == 'sma':
            # Simple moving average
            window = max(1, int(1 / alpha))
            smoothed = np.convolve(
                history,
                np.ones(window) / window,
                mode='same'
            )
        else:
            smoothed = history

        self._smoothed = smoothed
        return smoothed

    def detect_convergence_point(
        self,
        patience: int = 10,
        min_improvement: float = 0.001
    ) -> Dict:
        """
        Detect when phi resonance converges.

        Parameters
        ----------
        patience : int, default=10
            Number of epochs without improvement to declare convergence
        min_improvement : float, default=0.001
            Minimum improvement to count as progress

        Returns
        -------
        dict
            Convergence information:
            - converged : bool
            - convergence_epoch : int or None
            - final_resonance : float
            - convergence_rate : float (improvement per epoch at convergence)
        """
        if len(self.resonance_history) < patience + 1:
            return {
                'converged': False,
                'convergence_epoch': None,
                'final_resonance': self.resonance_history[-1] if self.resonance_history else 0.0,
                'convergence_rate': None,
                'message': 'Not enough epochs to detect convergence'
            }

        history = np.array(self.resonance_history)
        best_resonance = history[0]
        epochs_without_improvement = 0
        convergence_epoch = None

        for i in range(1, len(history)):
            if history[i] > best_resonance + min_improvement:
                best_resonance = history[i]
                epochs_without_improvement = 0
            else:
                epochs_without_improvement += 1

            if epochs_without_improvement >= patience:
                convergence_epoch = i - patience
                break

        converged = convergence_epoch is not None

        # Calculate convergence rate (slope at convergence point)
        if converged and convergence_epoch > 5:
            window = min(10, convergence_epoch)
            recent = history[convergence_epoch - window:convergence_epoch]
            convergence_rate = (recent[-1] - recent[0]) / window
        else:
            convergence_rate = None

        self._convergence_point = convergence_epoch

        return {
            'converged': converged,
            'convergence_epoch': convergence_epoch,
            'final_resonance': history[-1],
            'best_resonance': best_resonance,
            'convergence_rate': convergence_rate,
            'message': f'Converged at epoch {convergence_epoch}' if converged else 'Not yet converged'
        }

    def predict_phi_trajectory(
        self,
        n_future_epochs: int = 20,
        method: str = 'linear'
    ) -> Dict:
        """
        Predict future phi resonance trajectory.

        Parameters
        ----------
        n_future_epochs : int, default=20
            Number of future epochs to predict
        method : str, default='linear'
            Prediction method: 'linear', 'exponential', 'asymptotic'

        Returns
        -------
        dict
            Prediction results:
            - predicted_epochs : ndarray
            - predicted_resonance : ndarray
            - confidence_bounds : tuple of ndarray (lower, upper)
            - predicted_convergence : int or None
        """
        if len(self.resonance_history) < 5:
            return {
                'predicted_epochs': np.array([]),
                'predicted_resonance': np.array([]),
                'confidence_bounds': (np.array([]), np.array([])),
                'predicted_convergence': None,
                'message': 'Need at least 5 epochs for prediction'
            }

        history = np.array(self.resonance_history)
        epochs = np.array(self.epoch_history)

        last_epoch = epochs[-1]
        future_epochs = np.arange(last_epoch + 1, last_epoch + n_future_epochs + 1)

        if method == 'linear':
            # Linear regression
            slope, intercept = np.polyfit(epochs, history, 1)
            predicted = slope * future_epochs + intercept

        elif method == 'exponential':
            # Exponential fit: y = a * (1 - exp(-b * x)) + c
            # Simplified: use log transform for linear fit
            try:
                # Fit to log of complement
                y_transform = np.log(1.01 - np.clip(history, 0, 1))
                slope, intercept = np.polyfit(epochs, y_transform, 1)
                predicted = 1.01 - np.exp(slope * future_epochs + intercept)
                predicted = np.clip(predicted, 0, 1)
            except (ValueError, RuntimeWarning):
                # Fallback to linear
                slope, intercept = np.polyfit(epochs, history, 1)
                predicted = slope * future_epochs + intercept

        elif method == 'asymptotic':
            # Asymptotic approach to a limit
            # Estimate asymptote from recent trend
            recent = history[-10:]
            asymptote = np.max(recent) * 1.1  # Assume 10% higher than max
            rate = 0.1  # Decay rate

            # y = asymptote - (asymptote - current) * exp(-rate * t)
            current = history[-1]
            t = future_epochs - last_epoch
            predicted = asymptote - (asymptote - current) * np.exp(-rate * t)

        else:
            # Default to last value
            predicted = np.full(n_future_epochs, history[-1])

        # Confidence bounds (simple estimate based on recent variance)
        recent_std = np.std(history[-10:]) if len(history) >= 10 else np.std(history)
        uncertainty = recent_std * np.sqrt(np.arange(1, n_future_epochs + 1))
        lower_bound = predicted - 1.96 * uncertainty
        upper_bound = predicted + 1.96 * uncertainty

        # Clip to valid range
        predicted = np.clip(predicted, 0, 1)
        lower_bound = np.clip(lower_bound, 0, 1)
        upper_bound = np.clip(upper_bound, 0, 1)

        # Predict convergence (when improvement drops below threshold)
        predicted_convergence = None
        for i in range(1, len(predicted)):
            if abs(predicted[i] - predicted[i - 1]) < 0.0001:
                predicted_convergence = future_epochs[i]
                break

        return {
            'predicted_epochs': future_epochs,
            'predicted_resonance': predicted,
            'confidence_bounds': (lower_bound, upper_bound),
            'predicted_convergence': predicted_convergence,
            'method': method
        }

    def find_phi_emergence_events(
        self,
        window: int = 5,
        significance_threshold: float = 2.0
    ) -> List[Dict]:
        """
        Find sudden phi emergence events (significant jumps in resonance).

        Parameters
        ----------
        window : int, default=5
            Window size for computing local statistics
        significance_threshold : float, default=2.0
            Number of standard deviations for significance

        Returns
        -------
        list of dict
            List of emergence events with:
            - epoch : int
            - magnitude : float (z-score)
            - before_resonance : float
            - after_resonance : float
            - type : str ('emergence' or 'collapse')
        """
        if len(self.resonance_history) < 2 * window:
            return []

        history = np.array(self.resonance_history)
        events = []

        for i in range(window, len(history) - window):
            before = history[i - window:i]
            after = history[i:i + window]

            before_mean = np.mean(before)
            before_std = np.std(before)

            # Compute z-score of transition
            if before_std > 1e-10:
                z_score = (np.mean(after) - before_mean) / before_std
            else:
                z_score = 0.0

            if abs(z_score) > significance_threshold:
                event_type = 'emergence' if z_score > 0 else 'collapse'
                events.append({
                    'epoch': self.epoch_history[i],
                    'index': i,
                    'magnitude': abs(z_score),
                    'z_score': z_score,
                    'before_resonance': before_mean,
                    'after_resonance': np.mean(after),
                    'type': event_type
                })

        return events

    def compute_trend_metrics(self) -> Dict:
        """
        Compute various trend metrics for the resonance history.

        Returns
        -------
        dict
            Trend metrics:
            - overall_trend : float (slope)
            - recent_trend : float (slope of last 20%)
            - acceleration : float (change in slope)
            - volatility : float (standard deviation)
            - monotonicity : float (fraction of positive changes)
        """
        if len(self.resonance_history) < 3:
            return {
                'overall_trend': 0.0,
                'recent_trend': 0.0,
                'acceleration': 0.0,
                'volatility': 0.0,
                'monotonicity': 0.5
            }

        history = np.array(self.resonance_history)
        epochs = np.array(self.epoch_history)

        # Overall trend (slope)
        overall_slope, _ = np.polyfit(epochs, history, 1)

        # Recent trend (last 20% of epochs)
        n_recent = max(3, len(history) // 5)
        recent_slope, _ = np.polyfit(epochs[-n_recent:], history[-n_recent:], 1)

        # Acceleration (second derivative approximation)
        if len(history) >= 10:
            first_half = history[:len(history) // 2]
            second_half = history[len(history) // 2:]
            epochs_first = epochs[:len(epochs) // 2]
            epochs_second = epochs[len(epochs) // 2:]

            slope1, _ = np.polyfit(epochs_first, first_half, 1)
            slope2, _ = np.polyfit(epochs_second, second_half, 1)
            acceleration = slope2 - slope1
        else:
            acceleration = 0.0

        # Volatility
        volatility = np.std(history)

        # Monotonicity (fraction of epochs with improvement)
        changes = np.diff(history)
        monotonicity = np.mean(changes > 0) if len(changes) > 0 else 0.5

        return {
            'overall_trend': overall_slope,
            'recent_trend': recent_slope,
            'acceleration': acceleration,
            'volatility': volatility,
            'monotonicity': monotonicity
        }

    def get_summary(self) -> Dict:
        """
        Get complete summary of phi resonance evolution.

        Returns
        -------
        dict
            Complete summary including history, trends, and predictions
        """
        if len(self.resonance_history) == 0:
            return {
                'n_epochs': 0,
                'message': 'No data recorded'
            }

        history = np.array(self.resonance_history)

        summary = {
            'n_epochs': len(self.epoch_history),
            'epochs': self.epoch_history.copy(),
            'resonance_history': self.resonance_history.copy(),
            'current_resonance': history[-1],
            'max_resonance': np.max(history),
            'max_resonance_epoch': self.epoch_history[np.argmax(history)],
            'min_resonance': np.min(history),
            'mean_resonance': np.mean(history),
            'std_resonance': np.std(history),
            'trend_metrics': self.compute_trend_metrics(),
            'convergence': self.detect_convergence_point(),
            'emergence_events': self.find_phi_emergence_events(),
            'smoothed_resonance': self.get_smoothed_resonance().tolist()
        }

        # Add prediction if enough data
        if len(self.resonance_history) >= 5:
            summary['prediction'] = self.predict_phi_trajectory()

        return summary

    def reset(self):
        """Clear all recorded history."""
        self.resonance_history = []
        self.epoch_history = []
        self.latent_history = []
        self._smoothed = None
        self._convergence_point = None


# Convenience function for quick analysis
def analyze_training_resonance(
    resonance_scores: List[float],
    epochs: Optional[List[int]] = None,
    verbose: bool = True
) -> Dict:
    """
    Quick analysis of pre-recorded resonance history.

    Parameters
    ----------
    resonance_scores : list of float
        Phi resonance scores per epoch
    epochs : list of int, optional
        Epoch numbers. If None, uses 0, 1, 2, ...
    verbose : bool, default=True
        Print results

    Returns
    -------
    dict
        Analysis results
    """
    analyzer = PhiTimeSeriesAnalyzer()

    if epochs is None:
        epochs = list(range(len(resonance_scores)))

    # Manually populate history (without latent codes)
    analyzer.resonance_history = list(resonance_scores)
    analyzer.epoch_history = list(epochs)

    summary = analyzer.get_summary()

    if verbose:
        print("=" * 60)
        print("PHI RESONANCE TIME-SERIES ANALYSIS")
        print("=" * 60)
        print(f"Total epochs: {summary['n_epochs']}")
        print(f"Current resonance: {summary['current_resonance']:.4f}")
        print(f"Max resonance: {summary['max_resonance']:.4f} "
              f"(epoch {summary['max_resonance_epoch']})")
        print(f"Mean resonance: {summary['mean_resonance']:.4f}")
        print()

        print("Trend Metrics:")
        trend = summary['trend_metrics']
        print(f"  Overall trend: {trend['overall_trend']:.6f}")
        print(f"  Recent trend: {trend['recent_trend']:.6f}")
        print(f"  Acceleration: {trend['acceleration']:.6f}")
        print(f"  Volatility: {trend['volatility']:.4f}")
        print(f"  Monotonicity: {trend['monotonicity']:.2f}")
        print()

        conv = summary['convergence']
        print(f"Convergence: {conv['message']}")
        if conv['converged']:
            print(f"  Best resonance: {conv['best_resonance']:.4f}")
        print()

        events = summary['emergence_events']
        if events:
            print(f"Emergence Events ({len(events)} found):")
            for e in events[:5]:  # Show top 5
                print(f"  Epoch {e['epoch']}: {e['type']} "
                      f"(magnitude={e['magnitude']:.2f})")
        else:
            print("No significant emergence events detected")

        print("=" * 60)

    return summary
