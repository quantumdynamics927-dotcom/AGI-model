"""
Distributed training for Quantum VAE using PyTorch Lightning.
Provides multi-GPU training, mixed precision, and performance optimizations.
"""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, Dataset
from typing import Optional, Dict, Any, List
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

try:
    import pytorch_lightning as pl
    from pytorch_lightning.strategies import DDPStrategy
    from pytorch_lightning.callbacks import ModelCheckpoint, EarlyStopping, LearningRateMonitor
    from pytorch_lightning.loggers import TensorBoardLogger
    PYTORCH_LIGHTNING_AVAILABLE = True
except ImportError:
    PYTORCH_LIGHTNING_AVAILABLE = False
    logger.warning("PyTorch Lightning not available. Using standard PyTorch.")


class QuantumVAEDataset(Dataset):
    """Dataset for quantum VAE training with consciousness-guided sampling."""

    def __init__(self, data: np.ndarray, consciousness_scores: Optional[np.ndarray] = None, phi_patterns: bool = True):
        """
        Initialize dataset.

        Args:
            data: Input data array
            consciousness_scores: Optional consciousness scores for weighted sampling
            phi_patterns: Whether to include phi patterns in data
        """
        self.data = torch.FloatTensor(data)
        self.consciousness_scores = torch.FloatTensor(consciousness_scores) if consciousness_scores is not None else None
        self.phi_patterns = phi_patterns

        if phi_patterns:
            self._enhance_with_phi_patterns()

    def _enhance_with_phi_patterns(self):
        """Enhance data with phi-resonant patterns."""
        phi = (1 + np.sqrt(5)) / 2
        n_samples, n_features = self.data.shape

        # Add phi-based features
        phi_features = torch.zeros(n_samples, min(10, n_features))
        for i in range(phi_features.shape[1]):
            phi_features[:, i] = self.data[:, i % n_features] * (phi ** (i % 5))

        # Concatenate with original data
        self.data = torch.cat([self.data, phi_features], dim=1)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        if self.consciousness_scores is not None:
            return self.data[idx], self.consciousness_scores[idx]
        return self.data[idx]


class QuantumVAETrainer:
    """
    Standard PyTorch trainer for Quantum VAE (fallback when Lightning not available).
    """

    def __init__(self, model, config, device='cpu'):
        self.model = model.to(device)
        self.config = config
        self.device = device
        self.optimizer = None
        self.scheduler = None
        self.train_losses = []
        self.val_losses = []

    def fit(self, train_loader, val_loader=None, epochs=100):
        """Train the model."""
        self.optimizer = torch.optim.AdamW(
            self.model.parameters(),
            lr=self.config.learning_rate,
            weight_decay=self.config.weight_decay
        )

        self.scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer, mode='min', factor=0.5, patience=10
        )

        for epoch in range(epochs):
            # Training
            train_loss = self._train_epoch(train_loader)
            self.train_losses.append(train_loss)

            # Validation
            val_loss = None
            if val_loader is not None:
                val_loss = self._validate_epoch(val_loader)
                self.val_losses.append(val_loss)
                self.scheduler.step(val_loss)

            # Logging
            if epoch % 10 == 0:
                logger.info(f"Epoch {epoch}: Train Loss = {train_loss:.6f}, Val Loss = {val_loss:.6f if val_loss else 'N/A'}")

        return self.train_losses, self.val_losses

    def _train_epoch(self, train_loader):
        """Train for one epoch."""
        self.model.train()
        total_loss = 0
        num_batches = 0

        for batch in train_loader:
            if isinstance(batch, (list, tuple)):
                x = batch[0].to(self.device)
            else:
                x = batch.to(self.device)

            self.optimizer.zero_grad()

            recon, mu, logvar, z = self.model(x)
            loss_dict = self.model.compute_loss(x, recon, mu, logvar, z)
            loss = loss_dict['total']

            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            self.optimizer.step()

            total_loss += loss.item()
            num_batches += 1

        return total_loss / num_batches

    def _validate_epoch(self, val_loader):
        """Validate for one epoch."""
        self.model.eval()
        total_loss = 0
        num_batches = 0

        with torch.no_grad():
            for batch in val_loader:
                if isinstance(batch, (list, tuple)):
                    x = batch[0].to(self.device)
                else:
                    x = batch.to(self.device)

                recon, mu, logvar, z = self.model(x)
                loss_dict = self.model.compute_loss(x, recon, mu, logvar, z)
                loss = loss_dict['total']

                total_loss += loss.item()
                num_batches += 1

        return total_loss / num_batches


if PYTORCH_LIGHTNING_AVAILABLE:
    class QuantumVAETrainerLightning(pl.LightningModule):
        """
        PyTorch Lightning module for distributed Quantum VAE training.
        Provides multi-GPU support, mixed precision, and advanced optimizations.
        """

        def __init__(self, model, config):
            super().__init__()
            self.model = model
            self.config = config
            self.train_losses = []
            self.val_losses = []
            self.phi_resonances = []

        def forward(self, x):
            return self.model(x)

        def training_step(self, batch, batch_idx):
            """Training step with mixed precision support."""
            if isinstance(batch, (list, tuple)):
                x = batch[0]
            else:
                x = batch

            # Mixed precision forward pass
            with torch.cuda.amp.autocast(enabled=self.config.get('mixed_precision', True)):
                recon, mu, logvar, z = self(x)
                loss_dict = self.model.compute_loss(x, recon, mu, logvar, z)

            loss = loss_dict['total']

            # Log metrics
            self.log('train_loss', loss, prog_bar=True)
            self.log('train_recon_loss', loss_dict['reconstruction'], prog_bar=False)
            self.log('train_kl_loss', loss_dict['kl_divergence'], prog_bar=False)

            # Log quantum-specific metrics
            if 'fidelity' in loss_dict:
                self.log('quantum_fidelity', loss_dict['fidelity'], prog_bar=False)
            if 'entropy' in loss_dict:
                self.log('quantum_entropy', loss_dict['entropy'], prog_bar=False)

            return loss

        def validation_step(self, batch, batch_idx):
            """Validation step."""
            if isinstance(batch, (list, tuple)):
                x = batch[0]
            else:
                x = batch

            recon, mu, logvar, z = self(x)
            loss_dict = self.model.compute_loss(x, recon, mu, logvar, z)

            loss = loss_dict['total']

            # Log validation metrics
            self.log('val_loss', loss, prog_bar=True)
            self.log('val_recon_loss', loss_dict['reconstruction'], prog_bar=False)

            return loss

        def configure_optimizers(self):
            """Configure optimizer and scheduler."""
            optimizer = torch.optim.AdamW(
                self.parameters(),
                lr=self.config.learning_rate,
                weight_decay=self.config.weight_decay
            )

            scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
                optimizer, mode='min', factor=0.5, patience=10
            )

            return {
                'optimizer': optimizer,
                'lr_scheduler': {
                    'scheduler': scheduler,
                    'monitor': 'val_loss'
                }
            }

        def on_train_epoch_end(self):
            """Called at end of training epoch."""
            # Log epoch metrics
            avg_loss = self.trainer.callback_metrics.get('train_loss', 0)
            self.train_losses.append(avg_loss)

        def on_validation_epoch_end(self):
            """Called at end of validation epoch."""
            avg_loss = self.trainer.callback_metrics.get('val_loss', 0)
            self.val_losses.append(avg_loss)


class DistributedTrainer:
    """
    Distributed trainer wrapper that uses PyTorch Lightning when available,
    falls back to standard trainer otherwise.
    """

    def __init__(self, model, config, use_lightning: bool = True):
        """
        Initialize distributed trainer.

        Args:
            model: Quantum VAE model
            config: Training configuration
            use_lightning: Force use of PyTorch Lightning if available
        """
        self.model = model
        self.config = config
        self.use_lightning = use_lightning and PYTORCH_LIGHTNING_AVAILABLE

        if self.use_lightning:
            self.lightning_module = QuantumVAETrainerLightning(model, config)
            self.trainer = None
        else:
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            self.standard_trainer = QuantumVAETrainer(model, config, device)

    def fit(self, train_data: np.ndarray, val_data: Optional[np.ndarray] = None,
            epochs: int = 100, batch_size: int = 32, num_gpus: int = -1):
        """
        Train the model with distributed support.

        Args:
            train_data: Training data array
            val_data: Validation data array
            epochs: Number of training epochs
            batch_size: Batch size
            num_gpus: Number of GPUs to use (-1 for all)
        """
        if self.use_lightning:
            return self._fit_lightning(train_data, val_data, epochs, batch_size, num_gpus)
        else:
            return self._fit_standard(train_data, val_data, epochs, batch_size)

    def _fit_lightning(self, train_data, val_data, epochs, batch_size, num_gpus):
        """Train with PyTorch Lightning."""
        # Create datasets
        train_dataset = QuantumVAEDataset(train_data, phi_patterns=self.config.get('phi_patterns', True))
        val_dataset = QuantumVAEDataset(val_data, phi_patterns=self.config.get('phi_patterns', True)) if val_data is not None else None

        # Create data loaders
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=4)
        val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False, num_workers=4) if val_dataset else None

        # Configure trainer
        callbacks = [
            ModelCheckpoint(
                dirpath=self.config.get('checkpoint_dir', 'checkpoints'),
                filename='vae-{epoch:02d}-{val_loss:.2f}',
                save_top_k=3,
                monitor='val_loss' if val_loader else 'train_loss',
                mode='min'
            ),
            LearningRateMonitor(logging_interval='step')
        ]

        # Early stopping
        if self.config.get('early_stopping', True):
            callbacks.append(EarlyStopping(
                monitor='val_loss' if val_loader else 'train_loss',
                patience=self.config.get('patience', 30),
                mode='min'
            ))

        # Create trainer
        self.trainer = pl.Trainer(
            max_epochs=epochs,
            accelerator='gpu' if torch.cuda.is_available() else 'cpu',
            devices=num_gpus,
            strategy=DDPStrategy(find_unused_parameters=False) if num_gpus != 1 else 'auto',
            precision='16-mixed' if self.config.get('mixed_precision', True) else 32,
            callbacks=callbacks,
            logger=TensorBoardLogger('lightning_logs', name='quantum_vae'),
            gradient_clip_val=1.0,
            log_every_n_steps=10
        )

        # Train
        self.trainer.fit(self.lightning_module, train_loader, val_loader)

        return self.lightning_module.train_losses, self.lightning_module.val_losses

    def _fit_standard(self, train_data, val_data, epochs, batch_size):
        """Train with standard PyTorch."""
        # Create datasets
        train_dataset = QuantumVAEDataset(train_data, phi_patterns=self.config.get('phi_patterns', True))
        val_dataset = QuantumVAEDataset(val_data, phi_patterns=self.config.get('phi_patterns', True)) if val_data is not None else None

        # Create data loaders
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False) if val_dataset else None

        # Train
        return self.standard_trainer.fit(train_loader, val_loader, epochs)

    def get_training_metrics(self) -> Dict[str, List[float]]:
        """Get training metrics."""
        if self.use_lightning:
            return {
                'train_loss': self.lightning_module.train_losses,
                'val_loss': self.lightning_module.val_losses
            }
        else:
            return {
                'train_loss': self.standard_trainer.train_losses,
                'val_loss': self.standard_trainer.val_losses
            }


def benchmark_training(model, config, train_data, val_data=None, use_lightning=True):
    """
    Benchmark training performance.

    Args:
        model: Quantum VAE model
        config: Training configuration
        train_data: Training data
        val_data: Validation data
        use_lightning: Whether to use PyTorch Lightning

    Returns:
        Benchmark results
    """
    import time

    trainer = DistributedTrainer(model, config, use_lightning=use_lightning)

    start_time = time.time()
    train_losses, val_losses = trainer.fit(
        train_data, val_data,
        epochs=config.get('epochs', 10),
        batch_size=config.get('batch_size', 32)
    )
    training_time = time.time() - start_time

    return {
        "framework": "PyTorch Lightning" if use_lightning else "Standard PyTorch",
        "training_time": training_time,
        "epochs": len(train_losses),
        "final_train_loss": train_losses[-1] if train_losses else None,
        "final_val_loss": val_losses[-1] if val_losses else None,
        "avg_time_per_epoch": training_time / len(train_losses) if train_losses else 0
    }


if __name__ == "__main__":
    # Example usage
    print("Testing distributed trainer...")

    # Mock config
    class MockConfig:
        learning_rate = 0.001
        weight_decay = 1e-5
        epochs = 5
        batch_size = 32
        mixed_precision = True
        early_stopping = True
        patience = 10
        phi_patterns = True

    # Mock model
    class MockQuantumVAE(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.encoder = torch.nn.Linear(128, 32)
            self.decoder = torch.nn.Linear(32, 128)

        def forward(self, x):
            z = self.encoder(x)
            recon = self.decoder(z)
            return recon, torch.zeros_like(z), torch.zeros_like(z), z

        def compute_loss(self, x, recon, mu, logvar, z):
            return {'total': torch.nn.functional.mse_loss(recon, x)}

    # Mock data
    train_data = np.random.randn(1000, 128)
    val_data = np.random.randn(100, 128)

    # Benchmark
    model = MockQuantumVAE()
    config = MockConfig()

    result = benchmark_training(model, config, train_data, val_data, use_lightning=True)
    print(f"Benchmark results: {result}")
