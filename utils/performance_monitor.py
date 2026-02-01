"""
Performance Monitoring and Visualization Utilities for Quantum VAE

Provides comprehensive monitoring of training metrics, model performance,
and quantum-specific measurements.
"""

import torch
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for headless environments
import matplotlib.pyplot as plt
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import json
from datetime import datetime

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
            'total_loss', 'recon', 'kl', 'hamming', 'coherence',
            'hw', 'mixed_state', 'fidelity', 'entropy'
        ]
        
        for name in metric_names:
            self.train_metrics[name] = []
            self.val_metrics[name] = []
    
    def record_epoch(self, 
                    epoch: int,
                    train_metrics: Dict[str, float],
                    val_metrics: Dict[str, float],
                    quantum_metrics: Optional[Dict[str, float]] = None):
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
        
        fig = plt.figure(figsize=(16, 12))
        
        # Loss components (3x3 grid)
        loss_metrics = ['total_loss', 'recon', 'kl', 'hamming', 'coherence', 
                       'hw', 'mixed_state', 'fidelity', 'entropy']
        
        for i, metric in enumerate(loss_metrics):
            ax = plt.subplot(3, 3, i + 1)
            
            if metric in self.train_metrics and len(self.train_metrics[metric]) > 0:
                ax.plot(self.epochs, self.train_metrics[metric], 
                       'b-', marker='o', markersize=2, label='Train', alpha=0.7)
            if metric in self.val_metrics and len(self.val_metrics[metric]) > 0:
                ax.plot(self.epochs, self.val_metrics[metric], 
                       'r-', marker='s', markersize=2, label='Val', alpha=0.7)
            
            ax.set_xlabel('Epoch')
            ax.set_ylabel('Loss')
            ax.set_title(f'{metric.replace("_", " ").title()}')
            ax.legend()
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Metrics plot saved to {save_path}")
        else:
            plt.show()
    
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
        
        fig, axes = plt.subplots(rows, cols, figsize=(5*cols, 4*rows))
        if n_metrics == 1:
            axes = [axes]
        else:
            axes = axes.flatten()
        
        for i, (metric, values) in enumerate(self.quantum_metrics.items()):
            ax = axes[i] if n_metrics > 1 else axes[0]
            epochs_to_plot = self.epochs[-len(values):] if len(values) < len(self.epochs) else self.epochs
            ax.plot(epochs_to_plot, values, 'g-', marker='o', markersize=3)
            ax.set_xlabel('Epoch')
            ax.set_ylabel('Value')
            ax.set_title(f'{metric.replace("_", " ").title()}')
            ax.grid(True, alpha=0.3)
        
        # Hide unused subplots
        for i in range(n_metrics, len(axes)):
            axes[i].axis('off')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Quantum metrics plot saved to {save_path}")
        else:
            plt.show()
    
    def save_metrics_json(self, save_path: Optional[str] = None):
        """
        Save all metrics to JSON file
        
        Args:
            save_path: Path to save JSON (optional)
        """
        data = {
            'epochs': self.epochs,
            'timestamps': self.timestamps,
            'train_metrics': self.train_metrics,
            'val_metrics': self.val_metrics,
            'quantum_metrics': self.quantum_metrics
        }
        
        if save_path is None and self.save_dir:
            save_path = self.save_dir / f'metrics_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        elif save_path is None:
            save_path = f'metrics_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        with open(save_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Metrics saved to {save_path}")
    
    def get_best_epoch(self, metric: str = 'total_loss', mode: str = 'val') -> Tuple[int, float]:
        """
        Get epoch with best metric value
        
        Args:
            metric: Metric name to check
            mode: 'train' or 'val'
            
        Returns:
            Tuple of (best_epoch, best_value)
        """
        metrics_dict = self.val_metrics if mode == 'val' else self.train_metrics
        
        if metric not in metrics_dict or len(metrics_dict[metric]) == 0:
            return -1, float('inf')
        
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
            return {'status': 'No data collected'}
        
        summary = {
            'total_epochs': len(self.epochs),
            'best_val_loss_epoch': self.get_best_epoch('total_loss', 'val')[0],
            'best_val_loss': self.get_best_epoch('total_loss', 'val')[1],
            'final_val_loss': self.val_metrics['total_loss'][-1] if len(self.val_metrics['total_loss']) > 0 else None,
            'final_train_loss': self.train_metrics['total_loss'][-1] if len(self.train_metrics['total_loss']) > 0 else None,
        }
        
        # Add quantum metrics summary
        if len(self.quantum_metrics) > 0:
            summary['quantum_metrics'] = {
                k: {
                    'final': v[-1] if len(v) > 0 else None,
                    'mean': np.mean(v) if len(v) > 0 else None,
                    'max': np.max(v) if len(v) > 0 else None,
                    'min': np.min(v) if len(v) > 0 else None
                }
                for k, v in self.quantum_metrics.items()
            }
        
        return summary
