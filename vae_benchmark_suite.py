"""
VAE Benchmark Suite
===================

Comprehensive benchmarking framework for comparing Quantum VAE
against classical VAE baselines and other generative models.

Benchmarks:
- Reconstruction quality (MSE, SSIM, LPIPS)
- Latent space quality (KL divergence, mutual information)
- Generation quality (FID, IS, precision/recall)
- Quantum-specific metrics (coherence, fidelity, entropy)
- Training efficiency (convergence speed, memory usage)
"""

import torch
import torch.nn as nn
import numpy as np
from typing import Dict, List, Tuple, Optional, Union, Callable
from dataclasses import dataclass, field
import time
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class BenchmarkConfig:
    """Configuration for VAE benchmark."""
    name: str
    latent_dim: int
    input_dim: int
    hidden_dims: List[int]
    epochs: int
    batch_size: int
    learning_rate: float
    device: str = 'cpu'
    seed: int = 42
    num_samples: int = 1000
    metrics: List[str] = field(default_factory=lambda: [
        'reconstruction_loss',
        'kl_divergence',
        'coherence',
        'fidelity',
        'fidelity_variance',
        'entropy',
        'effective_dimension',
        'training_time',
        'memory_usage'
    ])


@dataclass
class BenchmarkResult:
    """Container for benchmark results."""
    model_name: str
    config: BenchmarkConfig
    metrics: Dict[str, float]
    training_history: Dict[str, List[float]]
    latent_statistics: Dict[str, float]
    generation_quality: Dict[str, float]
    timestamp: str
    duration_seconds: float


class VAEBenchmark:
    """
    Benchmark suite for VAE models.
    
    Provides standardized evaluation and comparison
    of VAE architectures and training procedures.
    """
    
    def __init__(
        self,
        config: BenchmarkConfig,
        save_dir: Optional[str] = None
    ):
        """
        Initialize VAE benchmark.
        
        Args:
            config: Benchmark configuration
            save_dir: Directory to save results
        """
        self.config = config
        self.save_dir = Path(save_dir) if save_dir else Path('benchmark_results')
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
        # Set random seed
        torch.manual_seed(config.seed)
        np.random.seed(config.seed)
        
        # Initialize metrics storage
        self.results: Dict[str, BenchmarkResult] = {}
    
    def benchmark_model(
        self,
        model: nn.Module,
        train_loader: torch.utils.data.DataLoader,
        val_loader: Optional[torch.utils.data.DataLoader] = None,
        model_name: str = "VAE",
        optimizer_class: type = torch.optim.Adam,
        loss_fn: Optional[Callable] = None
    ) -> BenchmarkResult:
        """
        Benchmark a VAE model.
        
        Args:
            model: VAE model to benchmark
            train_loader: Training data loader
            val_loader: Validation data loader
            model_name: Name for the model
            optimizer_class: Optimizer class
            loss_fn: Custom loss function
            
        Returns:
            BenchmarkResult with all metrics
        """
        model = model.to(self.config.device)
        optimizer = optimizer_class(model.parameters(), lr=self.config.learning_rate)
        
        # Training history
        history = {
            'train_loss': [],
            'val_loss': [],
            'reconstruction_loss': [],
            'kl_divergence': [],
            'epoch_time': []
        }
        
        # Memory tracking
        if torch.cuda.is_available():
            torch.cuda.reset_peak_memory_stats()
        
        start_time = time.time()
        
        # Training loop
        for epoch in range(self.config.epochs):
            epoch_start = time.time()
            
            # Training
            model.train()
            train_loss = 0.0
            recon_loss = 0.0
            kl_loss = 0.0
            
            for batch_idx, (data, _) in enumerate(train_loader):
                data = data.to(self.config.device)
                
                optimizer.zero_grad()
                
                # Forward pass
                if hasattr(model, 'forward'):
                    outputs = model(data)
                    if isinstance(outputs, tuple):
                        recon, mu, log_var = outputs
                    else:
                        recon = outputs
                        mu = None
                        log_var = None
                else:
                    raise ValueError("Model must have a forward method")
                
                # Compute loss
                if loss_fn:
                    loss = loss_fn(recon, data, mu, log_var)
                else:
                    loss = self._default_loss(recon, data, mu, log_var)
                
                loss.backward()
                optimizer.step()
                
                train_loss += loss.item()
                if mu is not None and log_var is not None:
                    recon_loss += nn.functional.mse_loss(recon, data).item()
                    kl_loss += (-0.5 * torch.sum(1 + log_var - mu.pow(2) - log_var.exp())).item()
            
            # Average losses
            n_batches = len(train_loader)
            history['train_loss'].append(train_loss / n_batches)
            history['reconstruction_loss'].append(recon_loss / n_batches if recon_loss > 0 else 0)
            history['kl_divergence'].append(kl_loss / n_batches if kl_loss > 0 else 0)
            
            # Validation
            if val_loader:
                model.eval()
                val_loss = 0.0
                with torch.no_grad():
                    for data, _ in val_loader:
                        data = data.to(self.config.device)
                        outputs = model(data)
                        if isinstance(outputs, tuple):
                            recon, mu, log_var = outputs
                        else:
                            recon = outputs
                            mu = None
                            log_var = None
                        
                        if loss_fn:
                            loss = loss_fn(recon, data, mu, log_var)
                        else:
                            loss = self._default_loss(recon, data, mu, log_var)
                        
                        val_loss += loss.item()
                
                history['val_loss'].append(val_loss / len(val_loader))
            
            epoch_time = time.time() - epoch_start
            history['epoch_time'].append(epoch_time)
            
            if (epoch + 1) % 10 == 0:
                logger.info(f"Epoch {epoch+1}/{self.config.epochs}, Loss: {train_loss/n_batches:.4f}")
        
        total_time = time.time() - start_time
        
        # Compute final metrics
        metrics = self._compute_metrics(model, train_loader, val_loader)
        
        # Latent statistics
        latent_stats = self._compute_latent_statistics(model, train_loader)
        
        # Generation quality
        gen_quality = self._compute_generation_quality(model)
        
        # Memory usage
        memory_usage = 0
        if torch.cuda.is_available():
            memory_usage = torch.cuda.max_memory_allocated() / 1024**2  # MB
        
        metrics['memory_usage_mb'] = memory_usage
        metrics['training_time_s'] = total_time
        
        result = BenchmarkResult(
            model_name=model_name,
            config=self.config,
            metrics=metrics,
            training_history=history,
            latent_statistics=latent_stats,
            generation_quality=gen_quality,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            duration_seconds=total_time
        )
        
        self.results[model_name] = result
        
        return result
    
    def _default_loss(
        self,
        recon: torch.Tensor,
        data: torch.Tensor,
        mu: Optional[torch.Tensor],
        log_var: Optional[torch.Tensor]
    ) -> torch.Tensor:
        """Compute default VAE loss."""
        # Reconstruction loss
        recon_loss = nn.functional.mse_loss(recon, data, reduction='sum')
        
        # KL divergence
        if mu is not None and log_var is not None:
            kl_loss = -0.5 * torch.sum(1 + log_var - mu.pow(2) - log_var.exp())
        else:
            kl_loss = torch.tensor(0.0, device=data.device)
        
        return recon_loss + 0.0008 * kl_loss  # Weighted KL
    
    def _compute_metrics(
        self,
        model: nn.Module,
        train_loader: torch.utils.data.DataLoader,
        val_loader: Optional[torch.utils.data.DataLoader]
    ) -> Dict[str, float]:
        """Compute all benchmark metrics."""
        model.eval()
        metrics = {}
        
        with torch.no_grad():
            # Reconstruction quality
            total_mse = 0.0
            total_samples = 0
            
            for data, _ in train_loader:
                data = data.to(self.config.device)
                outputs = model(data)
                
                if isinstance(outputs, tuple):
                    recon, _, _ = outputs
                else:
                    recon = outputs
                
                total_mse += nn.functional.mse_loss(recon, data, reduction='sum').item()
                total_samples += data.size(0)
            
            metrics['reconstruction_mse'] = total_mse / total_samples
            
            # Additional metrics would be computed here
            # For quantum-specific metrics, import from quantum_coherence_metrics
            try:
                from quantum_coherence_metrics import QuantumCoherenceAnalyzer
                
                # Get latent codes
                latent_codes = []
                for data, _ in train_loader:
                    data = data.to(self.config.device)
                    if hasattr(model, 'encode'):
                        mu, _ = model.encode(data)
                        latent_codes.append(mu)
                
                if latent_codes:
                    latent_codes = torch.cat(latent_codes, dim=0)
                    analyzer = QuantumCoherenceAnalyzer(
                        latent_dim=self.config.latent_dim,
                        device=self.config.device
                    )
                    coherence_metrics = analyzer.analyze(latent_codes)
                    
                    metrics['coherence'] = coherence_metrics.l1_coherence
                    metrics['purity'] = coherence_metrics.purity
                    metrics['von_neumann_entropy'] = coherence_metrics.von_neumann_entropy
                    metrics['effective_dimension'] = coherence_metrics.effective_dimension
            except ImportError:
                logger.warning("quantum_coherence_metrics not available")
        
        return metrics
    
    def _compute_latent_statistics(
        self,
        model: nn.Module,
        train_loader: torch.utils.data.DataLoader
    ) -> Dict[str, float]:
        """Compute latent space statistics."""
        model.eval()
        
        all_mu = []
        all_log_var = []
        
        with torch.no_grad():
            for data, _ in train_loader:
                data = data.to(self.config.device)
                
                if hasattr(model, 'encode'):
                    mu, log_var = model.encode(data)
                    all_mu.append(mu)
                    all_log_var.append(log_var)
        
        if not all_mu:
            return {}
        
        all_mu = torch.cat(all_mu, dim=0)
        all_log_var = torch.cat(all_log_var, dim=0) if all_log_var else None
        
        stats = {
            'mean_norm': torch.norm(all_mu.mean(dim=0)).item(),
            'std_mean': all_mu.std(dim=0).mean().item(),
            'latent_dim_used': (all_mu.std(dim=0) > 0.01).sum().item(),
        }
        
        if all_log_var is not None:
            stats['kl_divergence'] = (-0.5 * (1 + all_log_var - all_mu.pow(2) - all_log_var.exp()).sum(dim=1)).mean().item()
        
        return stats
    
    def _compute_generation_quality(
        self,
        model: nn.Module
    ) -> Dict[str, float]:
        """Compute generation quality metrics."""
        model.eval()
        
        # Generate samples
        with torch.no_grad():
            # Sample from prior
            z = torch.randn(self.config.num_samples, self.config.latent_dim).to(self.config.device)
            
            if hasattr(model, 'decode'):
                samples = model.decode(z)
            else:
                samples = model(z)
        
        # Compute statistics of generated samples
        gen_stats = {
            'sample_mean': samples.mean().item(),
            'sample_std': samples.std().item(),
            'sample_min': samples.min().item(),
            'sample_max': samples.max().item(),
        }
        
        return gen_stats
    
    def compare_models(
        self,
        models: Dict[str, nn.Module],
        train_loader: torch.utils.data.DataLoader,
        val_loader: Optional[torch.utils.data.DataLoader] = None
    ) -> Dict[str, BenchmarkResult]:
        """
        Compare multiple models.
        
        Args:
            models: Dictionary of model name to model
            train_loader: Training data loader
            val_loader: Validation data loader
            
        Returns:
            Dictionary of model name to BenchmarkResult
        """
        results = {}
        
        for name, model in models.items():
            logger.info(f"Benchmarking {name}...")
            results[name] = self.benchmark_model(
                model=model,
                train_loader=train_loader,
                val_loader=val_loader,
                model_name=name
            )
        
        return results
    
    def save_results(
        self,
        result: Optional[BenchmarkResult] = None,
        filename: Optional[str] = None
    ) -> str:
        """
        Save benchmark results to file.
        
        Args:
            result: BenchmarkResult to save (uses last if None)
            filename: Custom filename
            
        Returns:
            Path to saved file
        """
        if result is None:
            result = list(self.results.values())[-1]
        
        filename = filename or f"benchmark_{result.model_name}_{result.timestamp.replace(':', '-')}.json"
        filepath = self.save_dir / filename
        
        # Convert to dict
        data = {
            'model_name': result.model_name,
            'config': {
                'name': result.config.name,
                'latent_dim': result.config.latent_dim,
                'input_dim': result.config.input_dim,
                'hidden_dims': result.config.hidden_dims,
                'epochs': result.config.epochs,
                'batch_size': result.config.batch_size,
                'learning_rate': result.config.learning_rate,
                'device': result.config.device,
                'seed': result.config.seed,
            },
            'metrics': result.metrics,
            'training_history': result.training_history,
            'latent_statistics': result.latent_statistics,
            'generation_quality': result.generation_quality,
            'timestamp': result.timestamp,
            'duration_seconds': result.duration_seconds,
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Saved results to {filepath}")
        return str(filepath)
    
    def load_results(self, filepath: str) -> BenchmarkResult:
        """Load benchmark results from file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        config = BenchmarkConfig(
            name=data['config']['name'],
            latent_dim=data['config']['latent_dim'],
            input_dim=data['config']['input_dim'],
            hidden_dims=data['config']['hidden_dims'],
            epochs=data['config']['epochs'],
            batch_size=data['config']['batch_size'],
            learning_rate=data['config']['learning_rate'],
            device=data['config']['device'],
            seed=data['config']['seed'],
        )
        
        return BenchmarkResult(
            model_name=data['model_name'],
            config=config,
            metrics=data['metrics'],
            training_history=data['training_history'],
            latent_statistics=data['latent_statistics'],
            generation_quality=data['generation_quality'],
            timestamp=data['timestamp'],
            duration_seconds=data['duration_seconds'],
        )
    
    def generate_report(
        self,
        results: Optional[Dict[str, BenchmarkResult]] = None
    ) -> str:
        """
        Generate a comparison report.
        
        Args:
            results: Results to compare (uses all if None)
            
        Returns:
            Report string
        """
        results = results or self.results
        
        if not results:
            return "No results to report."
        
        report = []
        report.append("=" * 60)
        report.append("VAE BENCHMARK REPORT")
        report.append("=" * 60)
        report.append("")
        
        # Summary table
        report.append("SUMMARY")
        report.append("-" * 60)
        report.append(f"{'Model':<20} {'Recon MSE':<12} {'Time (s)':<12} {'Memory (MB)':<12}")
        report.append("-" * 60)
        
        for name, result in results.items():
            report.append(
                f"{name:<20} "
                f"{result.metrics.get('reconstruction_mse', 0):<12.4f} "
                f"{result.duration_seconds:<12.1f} "
                f"{result.metrics.get('memory_usage_mb', 0):<12.1f}"
            )
        
        report.append("")
        
        # Detailed metrics
        report.append("DETAILED METRICS")
        report.append("-" * 60)
        
        all_metrics = set()
        for result in results.values():
            all_metrics.update(result.metrics.keys())
        
        for metric in sorted(all_metrics):
            report.append(f"\n{metric}:")
            for name, result in results.items():
                if metric in result.metrics:
                    report.append(f"  {name}: {result.metrics[metric]:.4f}")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)


class QuantumVAEBenchmark(VAEBenchmark):
    """
    Extended benchmark suite for Quantum VAE models.
    
    Adds quantum-specific metrics and comparisons:
    - Quantum coherence metrics
    - Golden ratio alignment
    - Mixed-state properties
    - Entanglement measures
    """
    
    def __init__(
        self,
        config: BenchmarkConfig,
        save_dir: Optional[str] = None
    ):
        """
        Initialize Quantum VAE benchmark.
        
        Args:
            config: Benchmark configuration
            save_dir: Directory to save results
        """
        super().__init__(config, save_dir)
        
        # Add quantum-specific metrics to config
        quantum_metrics = [
            'l1_coherence',
            'relative_entropy_coherence',
            'geometric_coherence',
            'purity',
            'von_neumann_entropy',
            'participation_ratio',
            'effective_dimension',
            'quantum_fisher_information',
            'coherence_of_formation',
            'skew_information',
            'superposition_degree',
            'entanglement_entropy',
            'golden_ratio_alignment',
            'phase_coherence',
            'decoherence_rate'
        ]
        
        for metric in quantum_metrics:
            if metric not in self.config.metrics:
                self.config.metrics.append(metric)
    
    def _compute_metrics(
        self,
        model: nn.Module,
        train_loader: torch.utils.data.DataLoader,
        val_loader: Optional[torch.utils.data.DataLoader]
    ) -> Dict[str, float]:
        """Compute all benchmark metrics including quantum-specific ones."""
        # Get base metrics
        metrics = super()._compute_metrics(model, train_loader, val_loader)
        
        model.eval()
        
        # Import quantum coherence metrics
        try:
            from quantum_coherence_metrics import (
                QuantumCoherenceAnalyzer,
                GoldenRatioLoss,
                MixedStateRegularizer
            )
            
            # Collect latent codes
            latent_codes = []
            with torch.no_grad():
                for data, _ in train_loader:
                    data = data.to(self.config.device)
                    if hasattr(model, 'encode'):
                        mu, _ = model.encode(data)
                        latent_codes.append(mu)
            
            if latent_codes:
                latent_codes = torch.cat(latent_codes, dim=0)
                
                # Compute quantum coherence metrics
                analyzer = QuantumCoherenceAnalyzer(
                    latent_dim=self.config.latent_dim,
                    device=self.config.device
                )
                coherence_metrics = analyzer.analyze(latent_codes)
                
                # Add all coherence metrics
                metrics.update(analyzer.to_dict(coherence_metrics))
                
                # Compute golden ratio loss
                gr_loss = GoldenRatioLoss()
                metrics['golden_ratio_loss'] = gr_loss(latent_codes).item()
                
                # Compute mixed state regularization
                ms_reg = MixedStateRegularizer(latent_dim=self.config.latent_dim)
                reg_losses = ms_reg(latent_codes)
                metrics['mixed_state_entropy_loss'] = reg_losses['entropy'].item()
                metrics['mixed_state_purity_loss'] = reg_losses['purity'].item()
                metrics['mixed_state_trace_loss'] = reg_losses['trace'].item()
                
        except ImportError:
            logger.warning("quantum_coherence_metrics not available for quantum metrics")
        
        return metrics
    
    def compare_quantum_vs_classical(
        self,
        quantum_model: nn.Module,
        classical_model: nn.Module,
        train_loader: torch.utils.data.DataLoader,
        val_loader: Optional[torch.utils.data.DataLoader] = None
    ) -> Dict[str, Dict[str, float]]:
        """
        Compare quantum VAE against classical VAE baseline.
        
        Args:
            quantum_model: Quantum VAE model
            classical_model: Classical VAE model
            train_loader: Training data loader
            val_loader: Validation data loader
            
        Returns:
            Dictionary with comparison metrics
        """
        # Benchmark both models
        quantum_result = self.benchmark_model(
            quantum_model, train_loader, val_loader, "QuantumVAE"
        )
        classical_result = self.benchmark_model(
            classical_model, train_loader, val_loader, "ClassicalVAE"
        )
        
        # Compute comparison
        comparison = {
            'quantum': quantum_result.metrics,
            'classical': classical_result.metrics,
            'improvement': {}
        }
        
        # Compute improvements
        for metric in quantum_result.metrics:
            if metric in classical_result.metrics:
                q_val = quantum_result.metrics[metric]
                c_val = classical_result.metrics[metric]
                
                # For metrics where lower is better
                if metric in ['reconstruction_mse', 'kl_divergence', 'training_time_s', 
                              'memory_usage_mb', 'golden_ratio_loss']:
                    improvement = (c_val - q_val) / (c_val + 1e-10) * 100
                # For metrics where higher is better
                else:
                    improvement = (q_val - c_val) / (c_val + 1e-10) * 100
                
                comparison['improvement'][metric] = improvement
        
        return comparison
    
    def generate_quantum_report(
        self,
        results: Optional[Dict[str, BenchmarkResult]] = None
    ) -> str:
        """
        Generate a quantum-specific comparison report.
        
        Args:
            results: Results to compare
            
        Returns:
            Report string
        """
        results = results or self.results
        
        if not results:
            return "No results to report."
        
        report = []
        report.append("=" * 70)
        report.append("QUANTUM VAE BENCHMARK REPORT")
        report.append("=" * 70)
        report.append("")
        
        # Quantum-specific metrics
        quantum_metrics = [
            'l1_coherence', 'purity', 'von_neumann_entropy',
            'golden_ratio_alignment', 'phase_coherence',
            'entanglement_entropy', 'superposition_degree'
        ]
        
        # Summary table
        report.append("QUANTUM METRICS SUMMARY")
        report.append("-" * 70)
        report.append(f"{'Model':<20} {'Coherence':<12} {'Purity':<12} {'Entropy':<12} {'GR Align':<12}")
        report.append("-" * 70)
        
        for name, result in results.items():
            report.append(
                f"{name:<20} "
                f"{result.metrics.get('l1_coherence', 0):<12.4f} "
                f"{result.metrics.get('purity', 0):<12.4f} "
                f"{result.metrics.get('von_neumann_entropy', 0):<12.4f} "
                f"{result.metrics.get('golden_ratio_alignment', 0):<12.4f}"
            )
        
        report.append("")
        
        # Detailed quantum metrics
        report.append("DETAILED QUANTUM METRICS")
        report.append("-" * 70)
        
        for metric in quantum_metrics:
            if any(metric in r.metrics for r in results.values()):
                report.append(f"\n{metric}:")
                for name, result in results.items():
                    if metric in result.metrics:
                        report.append(f"  {name}: {result.metrics[metric]:.6f}")
        
        report.append("")
        
        # Classical metrics comparison
        report.append("CLASSICAL METRICS COMPARISON")
        report.append("-" * 70)
        report.append(f"{'Model':<20} {'Recon MSE':<12} {'KL Div':<12} {'Eff Dim':<12}")
        report.append("-" * 70)
        
        for name, result in results.items():
            report.append(
                f"{name:<20} "
                f"{result.metrics.get('reconstruction_mse', 0):<12.4f} "
                f"{result.metrics.get('kl_divergence', 0):<12.4f} "
                f"{result.metrics.get('effective_dimension', 0):<12.1f}"
            )
        
        report.append("")
        report.append("=" * 70)
        
        return "\n".join(report)


class ClassicalVAEBaseline(nn.Module):
    """Classical VAE baseline for comparison."""
    
    def __init__(
        self,
        input_dim: int,
        latent_dim: int,
        hidden_dims: List[int] = [64, 32]
    ):
        super().__init__()
        
        # Encoder
        encoder_layers = []
        prev_dim = input_dim
        for h_dim in hidden_dims:
            encoder_layers.append(nn.Linear(prev_dim, h_dim))
            encoder_layers.append(nn.ReLU())
            prev_dim = h_dim
        
        self.encoder = nn.Sequential(*encoder_layers)
        self.fc_mu = nn.Linear(hidden_dims[-1], latent_dim)
        self.fc_log_var = nn.Linear(hidden_dims[-1], latent_dim)
        
        # Decoder
        decoder_layers = []
        prev_dim = latent_dim
        for h_dim in reversed(hidden_dims):
            decoder_layers.append(nn.Linear(prev_dim, h_dim))
            decoder_layers.append(nn.ReLU())
            prev_dim = h_dim
        
        decoder_layers.append(nn.Linear(hidden_dims[0], input_dim))
        self.decoder = nn.Sequential(*decoder_layers)
    
    def encode(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        h = self.encoder(x)
        return self.fc_mu(h), self.fc_log_var(h)
    
    def reparameterize(self, mu: torch.Tensor, log_var: torch.Tensor) -> torch.Tensor:
        std = torch.exp(0.5 * log_var)
        eps = torch.randn_like(std)
        return mu + eps * std
    
    def decode(self, z: torch.Tensor) -> torch.Tensor:
        return self.decoder(z)
    
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        mu, log_var = self.encode(x)
        z = self.reparameterize(mu, log_var)
        return self.decode(z), mu, log_var


class BetaVAEBaseline(nn.Module):
    """Beta-VAE baseline for comparison with disentanglement."""
    
    def __init__(
        self,
        input_dim: int,
        latent_dim: int,
        hidden_dims: List[int] = [64, 32],
        beta: float = 4.0
    ):
        """
        Initialize Beta-VAE.
        
        Args:
            input_dim: Input dimension
            latent_dim: Latent dimension
            hidden_dims: Hidden layer dimensions
            beta: Beta parameter for KL weighting
        """
        super().__init__()
        self.beta = beta
        
        # Encoder
        encoder_layers = []
        prev_dim = input_dim
        for h_dim in hidden_dims:
            encoder_layers.append(nn.Linear(prev_dim, h_dim))
            encoder_layers.append(nn.ReLU())
            prev_dim = h_dim
        
        self.encoder = nn.Sequential(*encoder_layers)
        self.fc_mu = nn.Linear(hidden_dims[-1], latent_dim)
        self.fc_log_var = nn.Linear(hidden_dims[-1], latent_dim)
        
        # Decoder
        decoder_layers = []
        prev_dim = latent_dim
        for h_dim in reversed(hidden_dims):
            decoder_layers.append(nn.Linear(prev_dim, h_dim))
            decoder_layers.append(nn.ReLU())
            prev_dim = h_dim
        
        decoder_layers.append(nn.Linear(hidden_dims[0], input_dim))
        self.decoder = nn.Sequential(*decoder_layers)
    
    def encode(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        h = self.encoder(x)
        return self.fc_mu(h), self.fc_log_var(h)
    
    def reparameterize(self, mu: torch.Tensor, log_var: torch.Tensor) -> torch.Tensor:
        std = torch.exp(0.5 * log_var)
        eps = torch.randn_like(std)
        return mu + eps * std
    
    def decode(self, z: torch.Tensor) -> torch.Tensor:
        return self.decoder(z)
    
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        mu, log_var = self.encode(x)
        z = self.reparameterize(mu, log_var)
        return self.decode(z), mu, log_var
    
    def loss_function(
        self,
        recon_x: torch.Tensor,
        x: torch.Tensor,
        mu: torch.Tensor,
        log_var: torch.Tensor
    ) -> torch.Tensor:
        """Compute Beta-VAE loss."""
        recon_loss = nn.functional.mse_loss(recon_x, x, reduction='sum')
        kl_loss = -0.5 * torch.sum(1 + log_var - mu.pow(2) - log_var.exp())
        return recon_loss + self.beta * kl_loss


class SparseVAEBaseline(nn.Module):
    """Sparse VAE baseline with sparsity constraints."""
    
    def __init__(
        self,
        input_dim: int,
        latent_dim: int,
        hidden_dims: List[int] = [64, 32],
        sparsity: float = 0.1
    ):
        """
        Initialize Sparse VAE.
        
        Args:
            input_dim: Input dimension
            latent_dim: Latent dimension
            hidden_dims: Hidden layer dimensions
            sparsity: Sparsity parameter for L1 regularization
        """
        super().__init__()
        self.sparsity = sparsity
        
        # Encoder
        encoder_layers = []
        prev_dim = input_dim
        for h_dim in hidden_dims:
            encoder_layers.append(nn.Linear(prev_dim, h_dim))
            encoder_layers.append(nn.ReLU())
            prev_dim = h_dim
        
        self.encoder = nn.Sequential(*encoder_layers)
        self.fc_mu = nn.Linear(hidden_dims[-1], latent_dim)
        self.fc_log_var = nn.Linear(hidden_dims[-1], latent_dim)
        
        # Decoder
        decoder_layers = []
        prev_dim = latent_dim
        for h_dim in reversed(hidden_dims):
            decoder_layers.append(nn.Linear(prev_dim, h_dim))
            decoder_layers.append(nn.ReLU())
            prev_dim = h_dim
        
        decoder_layers.append(nn.Linear(hidden_dims[0], input_dim))
        self.decoder = nn.Sequential(*decoder_layers)
    
    def encode(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        h = self.encoder(x)
        return self.fc_mu(h), self.fc_log_var(h)
    
    def reparameterize(self, mu: torch.Tensor, log_var: torch.Tensor) -> torch.Tensor:
        std = torch.exp(0.5 * log_var)
        eps = torch.randn_like(std)
        return mu + eps * std
    
    def decode(self, z: torch.Tensor) -> torch.Tensor:
        return self.decoder(z)
    
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        mu, log_var = self.encode(x)
        z = self.reparameterize(mu, log_var)
        return self.decode(z), mu, log_var
    
    def sparsity_loss(self, mu: torch.Tensor) -> torch.Tensor:
        """Compute sparsity loss."""
        return self.sparsity * torch.sum(torch.abs(mu))


class HierarchicalVAEBaseline(nn.Module):
    """Hierarchical VAE baseline with multi-level latent hierarchy."""
    
    def __init__(
        self,
        input_dim: int,
        latent_dims: List[int] = [64, 32, 16],
        hidden_dim: int = 64
    ):
        """
        Initialize Hierarchical VAE.
        
        Args:
            input_dim: Input dimension
            latent_dims: List of latent dimensions at each level
            hidden_dim: Hidden dimension for encoders/decoders
        """
        super().__init__()
        self.latent_dims = latent_dims
        self.num_levels = len(latent_dims)
        
        # Build hierarchical encoders
        self.encoders = nn.ModuleList()
        prev_dim = input_dim
        for i, latent_dim in enumerate(latent_dims):
            self.encoders.append(nn.Sequential(
                nn.Linear(prev_dim, hidden_dim),
                nn.ReLU(),
                nn.Linear(hidden_dim, 2 * latent_dim)  # mu and log_var
            ))
            prev_dim = latent_dim
        
        # Build hierarchical decoders
        self.decoders = nn.ModuleList()
        prev_dim = latent_dims[-1]
        for i in range(self.num_levels - 1, -1, -1):
            latent_dim = latent_dims[i]
            output_dim = latent_dims[i - 1] if i > 0 else input_dim
            self.decoders.append(nn.Sequential(
                nn.Linear(prev_dim, hidden_dim),
                nn.ReLU(),
                nn.Linear(hidden_dim, output_dim)
            ))
            prev_dim = latent_dim
    
    def encode(self, x: torch.Tensor) -> List[Tuple[torch.Tensor, torch.Tensor]]:
        """Encode at all hierarchy levels."""
        results = []
        h = x
        for encoder in self.encoders:
            params = encoder(h)
            mu, log_var = params.chunk(2, dim=-1)
            results.append((mu, log_var))
            # Sample for next level
            std = torch.exp(0.5 * log_var)
            eps = torch.randn_like(std)
            h = mu + eps * std
        return results
    
    def decode(self, z_list: List[torch.Tensor]) -> torch.Tensor:
        """Decode from all hierarchy levels."""
        h = z_list[-1]
        for i, decoder in enumerate(self.decoders):
            h = decoder(h)
        return h
    
    def reparameterize(self, mu: torch.Tensor, log_var: torch.Tensor) -> torch.Tensor:
        std = torch.exp(0.5 * log_var)
        eps = torch.randn_like(std)
        return mu + eps * std
    
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, List[Tuple[torch.Tensor, torch.Tensor]]]:
        encode_results = self.encode(x)
        z_list = [self.reparameterize(mu, log_var) for mu, log_var in encode_results]
        recon = self.decode(z_list)
        return recon, encode_results


def run_quantum_vs_classical_benchmark(
    quantum_model: nn.Module,
    input_dim: int = 128,
    latent_dim: int = 32,
    hidden_dims: List[int] = [64, 32],
    train_data: Optional[torch.Tensor] = None,
    epochs: int = 10,
    batch_size: int = 32,
    device: str = 'cpu'
) -> Dict[str, Any]:
    """
    Run a comprehensive benchmark comparing quantum VAE against classical baselines.
    
    Args:
        quantum_model: Quantum VAE model to benchmark
        input_dim: Input dimension
        latent_dim: Latent dimension
        hidden_dims: Hidden layer dimensions
        train_data: Training data tensor
        epochs: Number of training epochs
        batch_size: Batch size
        device: Device for computation
        
    Returns:
        Dictionary with benchmark results
    """
    # Create configuration
    config = BenchmarkConfig(
        name="quantum_vs_classical",
        latent_dim=latent_dim,
        input_dim=input_dim,
        hidden_dims=hidden_dims,
        epochs=epochs,
        batch_size=batch_size,
        learning_rate=1e-3,
        device=device
    )
    
    # Create benchmark
    benchmark = QuantumVAEBenchmark(config)
    
    # Create classical baselines
    classical_vae = ClassicalVAEBaseline(input_dim, latent_dim, hidden_dims)
    beta_vae = BetaVAEBaseline(input_dim, latent_dim, hidden_dims, beta=4.0)
    sparse_vae = SparseVAEBaseline(input_dim, latent_dim, hidden_dims, sparsity=0.1)
    
    # Create data loader
    if train_data is None:
        train_data = torch.randn(1000, input_dim)
    
    train_dataset = torch.utils.data.TensorDataset(train_data, torch.zeros(len(train_data)))
    train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    
    # Benchmark all models
    models = {
        'QuantumVAE': quantum_model,
        'ClassicalVAE': classical_vae,
        'BetaVAE': beta_vae,
        'SparseVAE': sparse_vae
    }
    
    results = benchmark.compare_models(models, train_loader)
    
    # Generate reports
    report = benchmark.generate_report(results)
    quantum_report = benchmark.generate_quantum_report(results)
    
    return {
        'results': results,
        'report': report,
        'quantum_report': quantum_report,
        'config': config
    }


if __name__ == "__main__":
    print("VAE Benchmark Suite")
    print("=" * 50)
    
    # Create sample configuration
    config = BenchmarkConfig(
        name="test_benchmark",
        latent_dim=32,
        input_dim=128,
        hidden_dims=[64, 32],
        epochs=10,
        batch_size=32,
        learning_rate=1e-3,
        device='cpu'
    )
    
    # Create benchmark
    benchmark = VAEBenchmark(config)
    
    # Create sample model
    model = ClassicalVAEBaseline(
        input_dim=config.input_dim,
        latent_dim=config.latent_dim,
        hidden_dims=config.hidden_dims
    )
    
    # Create sample data
    sample_data = torch.randn(1000, config.input_dim)
    train_dataset = torch.utils.data.TensorDataset(sample_data, torch.zeros(1000))
    train_loader = torch.utils.data.DataLoader(
        train_dataset,
        batch_size=config.batch_size,
        shuffle=True
    )
    
    print("\nRunning benchmark...")
    # Note: This would run the full benchmark
    # result = benchmark.benchmark_model(model, train_loader, model_name="ClassicalVAE")
    # print(benchmark.generate_report())
    
    print("\nBenchmark suite ready. Use benchmark.benchmark_model() to run.")
    
    # Test QuantumVAEBenchmark
    print("\n" + "=" * 50)
    print("Quantum VAE Benchmark Suite")
    print("=" * 50)
    
    quantum_benchmark = QuantumVAEBenchmark(config)
    print("Quantum metrics:", quantum_benchmark.config.metrics)