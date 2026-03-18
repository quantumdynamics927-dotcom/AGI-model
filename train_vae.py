import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
import matplotlib.pyplot as plt
from vae_model import QuantumVAE, total_loss, HybridQuantumOptimizer
from src.quantum_vae.losses import kl_anneal_factor
import os
import sys
import argparse
import time
import threading
import queue
import json
from pathlib import Path

WS_BRIDGE_AVAILABLE = False
try:
    from ws_bridge import broadcast_message
    from consciousness_streamer import ConsciousnessStreamer
    WS_BRIDGE_AVAILABLE = True
except ImportError:
    pass

VAULT_INTEGRATION_AVAILABLE = False
try:
    from tmt_vault_integration import run_agent_task_validation
    from ollama_cloud_models import get_ollama_cloud_model
    VAULT_INTEGRATION_AVAILABLE = True
except ImportError:
    pass

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))
try:
    from utils.golden_ratio_callback import GoldenRatioCallback, phi_regularization_loss
    from utils.performance_monitor import PerformanceMonitor, plot_phi_shell_geometry
    UTILS_AVAILABLE = True
except ImportError:
    UTILS_AVAILABLE = False
    print("Warning: Performance monitoring utilities not available")

# Try to import enhanced phi optimization modules
try:
    from utils.adaptive_phi_loss import AdaptivePhiLoss, create_phi_loss
    from utils.phi_sampler import PhiAwareSampler, compute_phi_scores_for_dataset
    PHI_OPTIMIZATION_AVAILABLE = True
except ImportError:
    PHI_OPTIMIZATION_AVAILABLE = False

# Add Rich console support for professional output
try:
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

class RealTimeConsciousnessStreamer:
    """
    Real-time streaming of consciousness data (EEG/fMRI) for dynamic model adaptation.
    Implements reinforcement learning feedback loops.
    """
    def __init__(self, buffer_size=1000, update_interval=1.0):
        self.buffer_size = buffer_size
        self.update_interval = update_interval
        self.data_queue = queue.Queue(maxsize=buffer_size)
        self.is_streaming = False
        self.thread = None
        
        # Consciousness metrics tracking
        self.current_metrics = {
            'complexity': 0.0,
            'entropy': 0.0,
            'coherence': 0.0,
            'feedback_score': 0.0
        }
    
    def start_streaming(self, data_source='simulated'):
        """
        Start real-time data streaming.
        data_source: 'simulated', 'eeg_device', 'fmri_scanner'
        """
        self.is_streaming = True
        self.thread = threading.Thread(target=self._stream_worker, args=(data_source,))
        self.thread.daemon = True
        self.thread.start()
    
    def stop_streaming(self):
        """Stop data streaming."""
        self.is_streaming = False
        if self.thread:
            self.thread.join(timeout=2.0)
    
    def _stream_worker(self, data_source):
        """Background worker for data streaming."""
        while self.is_streaming:
            try:
                if data_source == 'simulated':
                    # Generate simulated consciousness data
                    data = self._generate_simulated_data()
                elif data_source == 'eeg_device':
                    # Interface with real EEG device
                    data = self._read_eeg_device()
                elif data_source == 'fmri_scanner':
                    # Interface with fMRI scanner
                    data = self._read_fmri_scanner()
                else:
                    data = np.random.randn(128).astype(np.float32)
                
                # Update consciousness metrics
                self._update_consciousness_metrics(data)
                
                # Add to buffer (non-blocking)
                try:
                    self.data_queue.put(data, timeout=0.1)
                except queue.Full:
                    # Remove oldest data
                    try:
                        self.data_queue.get_nowait()
                        self.data_queue.put(data)
                    except queue.Empty:
                        pass
                
                time.sleep(self.update_interval)
                
            except Exception as e:
                print(f"Streaming error: {e}")
                time.sleep(1.0)
    
    def _generate_simulated_data(self):
        """Generate simulated consciousness data with realistic patterns."""
        # Base signal with alpha/beta waves
        t = time.time()
        alpha_wave = np.sin(2 * np.pi * 10 * t) * 0.5  # 10 Hz alpha
        beta_wave = np.sin(2 * np.pi * 20 * t) * 0.3   # 20 Hz beta
        
        # Add consciousness-like complexity
        complexity_factor = 0.1 * np.sin(2 * np.pi * 0.1 * t)  # Slow modulation
        
        # Generate 128-dimensional state
        base_signal = alpha_wave + beta_wave + complexity_factor
        noise = np.random.randn(128) * 0.1
        
        return (base_signal + noise).astype(np.float32)
    
    def _read_eeg_device(self):
        """Read from real EEG device (placeholder)."""
        # In practice, would interface with EEG hardware
        return self._generate_simulated_data()
    
    def _read_fmri_scanner(self):
        """Read from fMRI scanner (placeholder)."""
        # In practice, would interface with fMRI hardware
        return self._generate_simulated_data()
    
    def _update_consciousness_metrics(self, data):
        """Update real-time consciousness metrics."""
        # Calculate Lempel-Ziv complexity
        data_binary = (data > np.mean(data)).astype(int)
        data_str = ''.join(map(str, data_binary))
        self.current_metrics['complexity'] = self._calculate_lz_complexity(data_str)
        
        # Calculate entropy
        hist, _ = np.histogram(data, bins=50, density=True)
        hist = hist[hist > 0]
        self.current_metrics['entropy'] = -np.sum(hist * np.log2(hist))
        
        # Calculate coherence (simplified)
        fft = np.fft.fft(data)
        power_spectrum = np.abs(fft)**2
        alpha_band = np.mean(power_spectrum[8:12])  # Alpha band
        total_power = np.sum(power_spectrum)
        self.current_metrics['coherence'] = alpha_band / total_power if total_power > 0 else 0
        
        # Combined feedback score
        self.current_metrics['feedback_score'] = (
            0.4 * self.current_metrics['complexity'] +
            0.3 * self.current_metrics['entropy'] +
            0.3 * self.current_metrics['coherence']
        )
    
    def _calculate_lz_complexity(self, sequence):
        """Calculate Lempel-Ziv complexity."""
        n = len(sequence)
        if n == 0:
            return 0
        
        complexity = 0
        i = 0
        
        while i < n:
            j = 1
            while i + j <= n and sequence[i:i+j] in sequence[:i]:
                j += 1
            complexity += 1
            i += j
        
        return complexity / n if n > 0 else 0
    
    def get_current_data(self):
        """Get current consciousness data batch."""
        data_batch = []
        try:
            while len(data_batch) < 32 and not self.data_queue.empty():
                data_batch.append(self.data_queue.get_nowait())
        except queue.Empty:
            pass
        
        return np.array(data_batch) if data_batch else None
    
    def get_feedback_score(self):
        """Get current consciousness feedback score for reinforcement learning."""
        return self.current_metrics['feedback_score']

def calculate_lz_complexity(sequence):
    """
    Calculate Lempel-Ziv complexity of a sequence.
    Higher values indicate more algorithmic complexity.
    """
    if isinstance(sequence, torch.Tensor):
        sequence = sequence.detach().cpu().numpy()

    sequence = sequence.flatten()
    n = len(sequence)

    if n == 0:
        return 0

    # Convert to string representation
    sequence_str = ''.join(['1' if x > 0 else '0' for x in sequence])

    # LZ complexity calculation
    complexity = 0
    i = 0

    while i < n:
        j = 1
        while i + j <= n:
            substring = sequence_str[i:i+j]
            if sequence_str[:i].find(substring) == -1:
                complexity += 1
                i += j
                break
            j += 1
        else:
            complexity += 1
            break

    return complexity

def calculate_pci(data):
    """
    Calculate Perturbational Complexity Index (PCI)
    Measures consciousness complexity by assessing response to perturbation
    """
    if isinstance(data, torch.Tensor):
        data = data.detach().cpu().numpy()

    batch_size, feature_dim = data.shape

    # Create perturbation (small random noise)
    perturbation = np.random.normal(0, 0.1, data.shape)

    # Apply perturbation
    perturbed_data = data + perturbation

    # Calculate complexity of difference
    pci_values = []
    for i in range(batch_size):
        # Difference between original and perturbed
        diff = data[i] - perturbed_data[i]

        # Calculate LZ complexity of the difference
        lz_diff = calculate_lz_complexity(diff)

        # Normalize by data size
        pci = lz_diff / len(diff.flatten())
        pci_values.append(pci)

    return np.mean(pci_values)

def contrastive_loss(z_i, z_j, temperature=0.5):
    """
    NT-Xent loss for contrastive learning
    z_i, z_j are batches of normalized embeddings
    """
    batch_size = z_i.shape[0]

    # Concatenate and normalize
    z = torch.cat([z_i, z_j], dim=0)
    z = F.normalize(z, dim=1)

    # Similarity matrix
    sim = torch.mm(z, z.t()) / temperature

    # Labels: positive pairs are (i, i+batch_size) and (i+batch_size, i)
    labels = torch.arange(batch_size, device=z.device)
    labels = torch.cat([labels + batch_size, labels])

    # Mask to remove self-similarities
    mask = torch.eye(2 * batch_size, device=z.device, dtype=torch.bool)
    sim = sim.masked_fill(mask, float('-inf'))

    # Cross entropy loss
    loss = F.cross_entropy(sim, labels)
    return loss

def phi_target_loss(latent_representations, phi=1.618034):
    """
    Loss term that encourages latent representations to follow phi patterns
    """
    # Calculate ratios between dimensions
    ratios = []
    for i in range(latent_representations.shape[1] - 1):
        ratio = latent_representations[:, i+1] / (latent_representations[:, i] + 1e-10)
        ratios.append(ratio)

    ratios = torch.stack(ratios, dim=1)

    # Target phi ratio
    phi_target = torch.full_like(ratios, phi)

    # MSE loss to phi target
    loss = F.mse_loss(ratios, phi_target)
    return loss

def load_sacred_datasets(data_dir='sacred_datasets'):
    """
    Load sacred geometry datasets across scientific domains
    """
    import json
    datasets = {}

    # Load molecular kinetics
    try:
        with open(f'{data_dir}/molecular_kinetics.json', 'r') as f:
            kinetics = json.load(f)
            kinetics_data = []
            for exp in kinetics:
                kinetics_data.append(exp['concentration'])
            datasets['kinetics'] = np.array(kinetics_data, dtype=np.float32)
            print(f"Loaded kinetics data: {datasets['kinetics'].shape}")
    except Exception as e:
        print(f"Could not load kinetics: {e}")

    # Load quantum spectra
    try:
        with open(f'{data_dir}/quantum_transport_spectra.json', 'r') as f:
            spectra = json.load(f)
            spectra_data = []
            for spec in spectra:
                spectra_data.append(spec['energies'])
            datasets['quantum'] = np.array(spectra_data, dtype=np.float32)
            print(f"Loaded quantum spectra: {datasets['quantum'].shape}")
    except Exception as e:
        print(f"Could not load quantum: {e}")

    # Load cosmological data
    try:
        with open(f'{data_dir}/cosmological_gas_fractions.json', 'r') as f:
            cosmo = json.load(f)
            cosmo_data = []
            for cluster in cosmo:
                cosmo_data.append([cluster['mass_msun'], cluster['redshift'], cluster['gas_fraction']])
            datasets['cosmological'] = np.array(cosmo_data, dtype=np.float32)
            print(f"Loaded cosmological data: {datasets['cosmological'].shape}")
    except Exception as e:
        print(f"Could not load cosmological: {e}")

    # Load Fibonacci embeddings
    try:
        with open(f'{data_dir}/fibonacci_embeddings.json', 'r') as f:
            embeddings = json.load(f)
            embed_data = []
            for emb in embeddings:
                embed_data.append(emb['embedding'])
            datasets['embeddings'] = np.array(embed_data, dtype=np.float32)
            print(f"Loaded embeddings: {datasets['embeddings'].shape}")
    except Exception as e:
        print(f"Could not load embeddings: {e}")

    return datasets

def create_unified_dataset(sacred_datasets, real_data, target_dim=128):
    """
    Create unified cross-domain dataset for consciousness VAE training

    Returns:
        unified_array: numpy array of shape (n_samples, target_dim)
        domain_labels: numpy array of domain labels for each sample (for stratification)
    """
    unified_data = []
    domain_labels = []
    domain_id = 0

    # Process each domain
    for domain, data in sacred_datasets.items():
        if len(data.shape) > 1:
            # Normalize and resize
            data_norm = (data - data.mean(axis=0)) / (data.std(axis=0) + 1e-10)

            # Resize to target dimension
            if data_norm.shape[1] > target_dim:
                data_norm = data_norm[:, :target_dim]
            elif data_norm.shape[1] < target_dim:
                padding = np.zeros((data_norm.shape[0], target_dim - data_norm.shape[1]))
                data_norm = np.concatenate([data_norm, padding], axis=1)

            unified_data.extend(data_norm)
            domain_labels.extend([domain_id] * len(data_norm))
            print(f"Added {len(data_norm)} samples from {domain} domain (label: {domain_id})")
            domain_id += 1

    # Add real consciousness data with its own domain label
    if real_data is not None:
        n_real = min(len(real_data), 1000)  # Limit to balance
        unified_data.extend(real_data[:n_real])
        domain_labels.extend([domain_id] * n_real)
        print(f"Added {n_real} samples from real consciousness domain (label: {domain_id})")

    unified_array = np.array(unified_data, dtype=np.float32)
    domain_array = np.array(domain_labels, dtype=np.int32)
    print(f"Unified dataset: {unified_array.shape}")
    print(f"Domain distribution: {np.bincount(domain_array)}")

    return unified_array, domain_array

def load_real_consciousness_data(data_dir='real_data'):
    """
    Load real consciousness data from processed datasets
    """
    try:
        # Load processed real data
        data_path = os.path.join(data_dir, 'processed_real_data.npz')
        if os.path.exists(data_path):
            data = np.load(data_path, allow_pickle=True)
            # Combine EEG and fMRI data
            eeg_data = data['eeg']
            fmri_data = data['fmri']
            
            # Normalize and resize to common dimension
            target_dim = 128  # Match sacred datasets
            
            # Process EEG data
            eeg_norm = (eeg_data - eeg_data.mean(axis=0)) / (eeg_data.std(axis=0) + 1e-10)
            if eeg_norm.shape[1] > target_dim:
                eeg_processed = eeg_norm[:, :target_dim]
            else:
                padding = np.zeros((eeg_norm.shape[0], target_dim - eeg_norm.shape[1]))
                eeg_processed = np.concatenate([eeg_norm, padding], axis=1)
            
            # Process fMRI data
            fmri_norm = (fmri_data - fmri_data.mean(axis=0)) / (fmri_data.std(axis=0) + 1e-10)
            if fmri_norm.shape[1] > target_dim:
                fmri_processed = fmri_norm[:, :target_dim]
            else:
                padding = np.zeros((fmri_norm.shape[0], target_dim - fmri_norm.shape[1]))
                fmri_processed = np.concatenate([fmri_norm, padding], axis=1)
            
            # Combine
            real_data = np.concatenate([eeg_processed, fmri_processed], axis=0)
            
            print(f"Loaded real consciousness data: {real_data.shape}")
            return real_data
        else:
            print("No processed real data found")
            return None
    except Exception as e:
        print(f"Could not load real data: {e}")
        return None

def train_vae(model, train_loader, val_loader, num_epochs=200, device='cpu', save_path='best_model.pt',
              use_phi_callback: bool = True, use_performance_monitor: bool = True,
              consciousness_streaming: bool = False, use_hybrid_optimizer: bool = False,
              use_adaptive_phi: bool = False, tensorboard_dir: str = None):
    # Initialize Rich console if available
    console = Console(legacy_windows=False) if RICH_AVAILABLE else None
    
    # Initialize performance monitoring and callbacks
    phi_callback = None
    perf_monitor = None
    
    # Initialize adaptive phi loss if enabled
    adaptive_phi_loss = None
    if use_adaptive_phi and PHI_OPTIMIZATION_AVAILABLE:
        adaptive_phi_loss = AdaptivePhiLoss(
            target_resonance=0.5,
            min_weight=0.01,
            max_weight=0.3,
            warmup_epochs=20,
            schedule='adaptive'
        )
        print("Adaptive phi loss optimization enabled")

    if UTILS_AVAILABLE:
        if use_performance_monitor:
            perf_monitor = PerformanceMonitor(save_dir='artifacts/monitoring')
        if use_phi_callback:
            phi_callback = GoldenRatioCallback(
                save_dir='artifacts/golden_ratio',
                track_frequency=5,
                tensorboard_dir=tensorboard_dir,
                save_best_checkpoint=True
            )
            
    # Initialize consciousness streaming if enabled
    consciousness_streamer = None
    if consciousness_streaming:
        consciousness_streamer = RealTimeConsciousnessStreamer()
        consciousness_streamer.start_streaming('simulated')
        print("Real-time consciousness streaming enabled")
    
    # Initialize hybrid optimizer if enabled
    if use_hybrid_optimizer:
        optimizer = HybridQuantumOptimizer(model, classical_optimizer='adam', quantum_lr=1e-3)
        print("Using hybrid quantum-classical optimizer")
    else:
        optimizer = optim.Adam(model.parameters(), lr=1e-3)
    
    # Advanced scheduling and early stopping (optimization 5)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, factor=0.5, patience=15, min_lr=1e-6)
    early_stopping_patience = 30
    min_delta = 0.0001
    best_val_loss = float('inf')
    patience_counter = 0
    early_stopped = False
    train_losses = []
    val_losses = []
    best_checkpoint_summary = {}

    if console:
        console.print("[bold blue]>> Starting Quantum VAE Training[/bold blue]")
        console.print(f"Training on device: {device}")
        console.print(f"Target epochs: {num_epochs}, Early stopping patience: {early_stopping_patience}")
        console.print()

    for epoch in range(num_epochs):

        model.train()
        epoch_train_losses = {'total': 0, 'recon': 0, 'kl': 0, 'hamming': 0, 'coherence': 0, 'hw': 0, 'mixed_state': 0, 'fidelity': 0, 'entropy': 0, 'phi': 0, 'contrastive': 0}

        # KL annealing setup
        total_steps = num_epochs * len(train_loader)
        if 'global_step' not in locals():
            global_step = 0

        for batch_x, in train_loader:
            batch_x = batch_x.to(device)
            optimizer.zero_grad()

            recon_x, mu, log_var, density_matrix = model(batch_x)

            # The first full cloud research loop in research_loop_result.json
            # flagged KL over-regularization, so halve the max beta for the
            # next tuning pass and compare smoke metrics against that run.
            beta = kl_anneal_factor(global_step, total_steps, max_beta=0.0004)

            # Loss weights including phi
            weights = {
                'recon': 1.0,
                'kl': beta,
                'hamming': 0.3,
                'coherence': 0.1,
                'mixed_state': 0.1,
                'fidelity': 0.1,
                'entropy': 0.05,
                'hw': 0.01,
                'phi': 0.01,
            }

            total_tensor, losses = model.compute_losses(recon_x, batch_x, mu, log_var, weights=weights)

            # Add contrastive loss
            batch_size = batch_x.shape[0] // 2
            if batch_size > 1:
                z_i, z_j = mu[:batch_size], mu[batch_size:2*batch_size]
                contrastive = contrastive_loss(z_i, z_j) * 0.05
                total_tensor += contrastive
            else:
                contrastive = torch.tensor(0.0, device=device)

            # Add consciousness feedback if streaming
            if consciousness_streamer:
                feedback_score = consciousness_streamer.get_feedback_score()
                consciousness_loss = (1.0 - feedback_score) * 0.1  # Encourage higher feedback
                total_tensor += consciousness_loss

            total_tensor.backward()

            # Clip gradients to prevent NaN explosion
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

            if use_hybrid_optimizer:
                optimizer.step(lambda: model.compute_losses(model(batch_x), batch_x, mu, log_var, weights=weights)[0])
            else:
                optimizer.step()

            for key in epoch_train_losses:
                if key == 'phi':
                    epoch_train_losses[key] += losses['phi']
                elif key == 'contrastive':
                    epoch_train_losses[key] += contrastive.item()
                else:
                    epoch_train_losses[key] += losses[key]

            global_step += 1

        # Average over batches
        num_batches = len(train_loader)
        for key in epoch_train_losses:
            epoch_train_losses[key] /= num_batches

        train_losses.append(epoch_train_losses)

        # Validation
        model.eval()
        epoch_val_losses = {'total': 0, 'recon': 0, 'kl': 0, 'hamming': 0, 'coherence': 0, 'hw': 0, 'mixed_state': 0, 'fidelity': 0, 'entropy': 0, 'phi': 0, 'contrastive': 0}

        # Use same loss weights as training for consistent evaluation
        weights = {
            'recon': 1.0,
            'kl': beta,  # Use current KL annealing weight
            'hamming': 0.3,
            'coherence': 0.1,
            'mixed_state': 0.1,
            'fidelity': 0.1,
            'entropy': 0.05,
            'hw': 0.01,
            'phi': 0.01,
        }

        with torch.no_grad():
            for batch_x, in val_loader:
                batch_x = batch_x.to(device)
                recon_x, mu, log_var, density_matrix = model(batch_x)

                # Use model.compute_losses like training loop for consistent metrics
                total_tensor, losses = model.compute_losses(recon_x, batch_x, mu, log_var, weights=weights)

                # Add contrastive loss (if batch size allows)
                batch_size = batch_x.shape[0] // 2
                if batch_size > 1:
                    z_i, z_j = mu[:batch_size], mu[batch_size:2*batch_size]
                    contrastive = contrastive_loss(z_i, z_j) * 0.05
                else:
                    contrastive = torch.tensor(0.0, device=device)

                for key in epoch_val_losses:
                    if key == 'contrastive':
                        epoch_val_losses[key] += contrastive.item()
                    else:
                        epoch_val_losses[key] += losses[key]

        num_val_batches = len(val_loader)
        for key in epoch_val_losses:
            epoch_val_losses[key] /= num_val_batches

        val_losses.append(epoch_val_losses)
        
        # Track quantum fidelity and other quantum metrics
        quantum_metrics = {}
        if epoch > 50:  # After advanced losses are enabled
            quantum_metrics['fidelity'] = epoch_val_losses.get('fidelity', 0.0)
            quantum_metrics['entropy'] = epoch_val_losses.get('entropy', 0.0)
            quantum_metrics['coherence'] = epoch_val_losses.get('coherence', 0.0)

        # Calculate consciousness metrics (LZ complexity and PCI)
        model.eval()
        with torch.no_grad():
            # Get a batch for metrics
            sample_batch = next(iter(val_loader))[0][:10].to(device)  # First 10 samples
            recon_batch, mu_sample, _, density_sample = model(sample_batch)

            # Calculate LZ complexity on original and reconstructed
            lz_original = np.mean([calculate_lz_complexity(sample_batch[i]) for i in range(len(sample_batch))])
            lz_reconstructed = np.mean([calculate_lz_complexity(recon_batch[i]) for i in range(len(recon_batch))])

            # Calculate PCI
            pci_original = calculate_pci(sample_batch)
            pci_reconstructed = calculate_pci(recon_batch)
            
            # Track phi-resonance if callback is available
            if phi_callback:
                phi_metrics = phi_callback.on_epoch_end(epoch, model, mu_sample)
                quantum_metrics.update(phi_metrics)
            
            # Record performance metrics
            if perf_monitor:
                perf_monitor.record_epoch(
                    epoch,
                    epoch_train_losses,
                    epoch_val_losses,
                    quantum_metrics
                )
            
            # Broadcast training progress via WebSocket
            if WS_BRIDGE_AVAILABLE:
                phi_res = quantum_metrics.get('phi_resonance', 0.0)
                broadcast_message({
                    'type': 'training_progress',
                    'epoch': epoch + 1,
                    'total_epochs': num_epochs,
                    'total_loss': float(epoch_val_losses['total']),
                    'recon_loss': float(epoch_val_losses['recon']),
                    'kl_loss': float(epoch_val_losses['kl']),
                    'coherence_loss': float(epoch_val_losses['coherence']),
                    'fidelity_loss': float(epoch_val_losses.get('fidelity', 0.0)),
                    'phi_resonance': float(phi_res),
                    'learning_rate': optimizer.param_groups[0]['lr'] if hasattr(optimizer, 'param_groups') else 0.0,
                    'timestamp': time.time()
                })

        current_val_loss = epoch_val_losses['total']
        current_learning_rate = (
            optimizer.param_groups[0]['lr']
            if hasattr(optimizer, 'param_groups')
            else None
        )
        improved = False
        scheduler.step(current_val_loss)

        # Early stopping
        if current_val_loss < best_val_loss - min_delta:
            best_val_loss = current_val_loss
            patience_counter = 0
            torch.save(model.state_dict(), save_path)
            improved = True
            print(f"Saved best model with val loss: {best_val_loss:.4f}")
        else:
            patience_counter += 1
            if patience_counter >= early_stopping_patience:
                print(f"Early stopping at epoch {epoch+1}")
                early_stopped = True
                break

        if improved:
            best_checkpoint_summary = {
                'epoch': epoch + 1,
                'path': save_path,
                'best_val_loss': float(best_val_loss),
                'train_losses': {
                    key: float(value)
                    for key, value in epoch_train_losses.items()
                },
                'val_losses': {
                    key: float(value)
                    for key, value in epoch_val_losses.items()
                },
                'learning_rate': (
                    float(current_learning_rate)
                    if current_learning_rate is not None
                    else None
                ),
                'quantum_metrics': {
                    key: float(value)
                    for key, value in quantum_metrics.items()
                },
                'consciousness_metrics': {
                    'lz_original': float(lz_original),
                    'lz_reconstructed': float(lz_reconstructed),
                    'pci_original': float(pci_original),
                    'pci_reconstructed': float(pci_reconstructed),
                },
            }

        # Display metrics with Rich table if available
        if console:
            table = Table(title=f"Epoch {epoch+1}/{num_epochs} - Quantum VAE Training")
            table.add_column("Metric", style="cyan", no_wrap=True)
            table.add_column("Train", style="magenta", justify="right")
            table.add_column("Validation", style="green", justify="right")

            table.add_row("Reconstruction", f"{epoch_train_losses['recon']:.4f}", f"{epoch_val_losses['recon']:.4f}")
            table.add_row("KL Divergence", f"{epoch_train_losses['kl']:.4f}", f"{epoch_val_losses['kl']:.4f}")
            table.add_row("Hamming Distance", f"{epoch_train_losses['hamming']:.4f}", f"{epoch_val_losses['hamming']:.4f}")
            table.add_row("Coherence", f"{epoch_train_losses['coherence']:.4f}", f"{epoch_val_losses['coherence']:.4f}")
            table.add_row("HW Deviation", f"{epoch_train_losses['hw']:.4f}", f"{epoch_val_losses['hw']:.4f}")
            table.add_row("Mixed State", f"{epoch_train_losses['mixed_state']:.4f}", f"{epoch_val_losses['mixed_state']:.4f}")
            table.add_row("Total Loss", f"{epoch_train_losses['total']:.4f}", f"{epoch_val_losses['total']:.4f}")

            if 'fidelity' in epoch_train_losses and epoch_train_losses.get('fidelity', 0) > 0:
                table.add_row("Quantum Fidelity", f"{epoch_train_losses['fidelity']:.4f}", f"{epoch_val_losses['fidelity']:.4f}")
                table.add_row("Entanglement Entropy", f"{epoch_train_losses['entropy']:.4f}", f"{epoch_val_losses['entropy']:.4f}")

            # Add consciousness metrics
            table.add_row("LZ Complexity (Orig)", f"{lz_original:.2f}", "-")
            table.add_row("LZ Complexity (Recon)", f"{lz_reconstructed:.2f}", "-")
            table.add_row("PCI (Orig)", f"{pci_original:.4f}", "-")
            table.add_row("PCI (Recon)", f"{pci_reconstructed:.4f}", "-")

            console.print(table)
        else:
            # Fallback to basic print statements
            print(f"Epoch {epoch+1}/{num_epochs}")
            print(f"  Train - Recon: {epoch_train_losses['recon']:.4f}, KL: {epoch_train_losses['kl']:.4f}, Hamming: {epoch_train_losses['hamming']:.4f}")
            print(f"  Train - Coherence: {epoch_train_losses['coherence']:.4f}, HW: {epoch_train_losses['hw']:.4f}, Mixed-State: {epoch_train_losses['mixed_state']:.4f}")
            print(f"  Val - Recon: {epoch_val_losses['recon']:.4f}, KL: {epoch_val_losses['kl']:.4f}, Hamming: {epoch_val_losses['hamming']:.4f}")
            print(f"  Val - Coherence: {epoch_val_losses['coherence']:.4f}, HW: {epoch_val_losses['hw']:.4f}, Mixed-State: {epoch_val_losses['mixed_state']:.4f}")
            print(f"  Total Loss - Train: {epoch_train_losses['total']:.4f}, Val: {epoch_val_losses['total']:.4f}")
            if 'fidelity' in epoch_train_losses and epoch_train_losses.get('fidelity', 0) > 0:
                print(f"  Advanced - Fidelity: {epoch_train_losses['fidelity']:.4f}, Entropy: {epoch_train_losses['entropy']:.4f}")
                print(f"  Advanced - Val Fidelity: {epoch_val_losses['fidelity']:.4f}, Val Entropy: {epoch_val_losses['entropy']:.4f}")

        # Remove duplicate save message - already handled above

    # Final summary and plots
    if perf_monitor:
        perf_monitor.plot_all_metrics(save_path='artifacts/training_metrics_full.png')
        perf_monitor.plot_quantum_metrics(save_path='artifacts/quantum_metrics.png')
        # Save metrics JSON but continue even if it fails
        try:
            perf_monitor.save_metrics_json()
        except Exception as e:
            print(f"⚠️ Skipping JSON save due to error: {e}")
            print("Continuing to visualization...")
        summary = perf_monitor.get_summary()
    else:
        summary = None

    # Generate Phi-shell geometry visualization
    if UTILS_AVAILABLE:
        try:
            print("\n[bold cyan]>> Generating Phi-shell Geometry Visualization...[/bold cyan]")
            phi_stats = plot_phi_shell_geometry(model, val_loader, device, save_path='artifacts/phi_shell.png')
            if console:
                console.print("\n[bold cyan]>> Phi-shell Geometry Statistics:[/bold cyan]")
                console.print(f"Mean radius: {phi_stats.get('mean_radius', 'N/A'):.3f}")
                console.print(f"Target radius: {phi_stats.get('target_radius', 'N/A'):.3f}")
                console.print(f"Phi alignment score: {phi_stats.get('phi_alignment_score', 'N/A'):.3f}")
        except Exception as e:
            print(f"Warning: Could not generate phi-shell visualization: {e}")
    
    # Cleanup consciousness streaming
    if consciousness_streamer:
        consciousness_streamer.stop_streaming()
        print("Consciousness streaming stopped")

    training_summary = {
        'save_path': save_path,
        'num_epochs_completed': len(train_losses),
        'requested_epochs': num_epochs,
        'early_stopped': early_stopped,
        'best_checkpoint': best_checkpoint_summary,
        'performance_summary': summary,
    }

    return train_losses, val_losses, training_summary

def plot_losses(train_losses, val_losses, save_path='training_curves.png'):
    epochs = range(1, len(train_losses) + 1)

    fig, axes = plt.subplots(3, 3, figsize=(18, 12))
    fig.suptitle('Quantum VAE Training Curves')

    loss_types = ['total', 'recon', 'kl', 'hamming', 'coherence', 'hw', 'mixed_state', 'fidelity', 'entropy']

    for i, loss_type in enumerate(loss_types):
        ax = axes[i // 3, i % 3]
        train_vals = [loss.get(loss_type, 0) for loss in train_losses]
        val_vals = [loss.get(loss_type, 0) for loss in val_losses]

        ax.plot(epochs, train_vals, label='Train', marker='o', markersize=2)
        ax.plot(epochs, val_vals, label='Validation', marker='s', markersize=2)
        ax.set_title(f'{loss_type.capitalize()} Loss')
        ax.set_xlabel('Epoch')
        ax.set_ylabel('Loss')
        ax.legend()
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    # plt.show()  # Remove to avoid blocking in headless environment


def write_training_summary(summary, output_path):
    """Persist a structured training summary next to the checkpoint."""
    output_file = Path(output_path)
    output_file.write_text(
        json.dumps(summary, indent=2),
        encoding='utf-8',
    )
    return output_file

def main():
    parser = argparse.ArgumentParser(description='Train Quantum Consciousness VAE')
    parser.add_argument('--epochs', type=int, default=200, help='Number of training epochs')
    parser.add_argument('--batch_size', type=int, default=32, help='Batch size')
    parser.add_argument('--latent_dim', type=int, default=32, help='Latent dimension')
    parser.add_argument('--hidden_dims', type=int, nargs='+', default=[256, 128], help='Hidden layer dimensions')
    parser.add_argument('--device', type=str, default='auto', choices=['auto', 'cpu', 'cuda', 'mps'],
                       help='Device to train on (auto=auto-detect)')
    parser.add_argument('--use_mps', action='store_true', help='Use Matrix Product State encoding')
    parser.add_argument('--mps_bond_dim', type=int, default=16, help='MPS bond dimension')
    parser.add_argument('--use_quantum_kernel', action='store_true', help='Use quantum kernel for learning')
    parser.add_argument('--kernel_qubits', type=int, default=4, help='Number of qubits for quantum kernel')
    parser.add_argument('--kernel_layers', type=int, default=2, help='Number of layers for quantum kernel')
    parser.add_argument('--use_hybrid_optimizer', action='store_true', help='Use hybrid quantum-classical optimizer')
    parser.add_argument('--consciousness_streaming', action='store_true', help='Enable real-time consciousness data streaming')
    parser.add_argument('--quantum_hardware', type=str, default='ibm_quantum', help='Target quantum hardware platform')
    parser.add_argument('--use_error_correction', action='store_true', help='Enable quantum error correction')
    parser.add_argument('--error_correction_type', type=str, default='surface', help='Type of error correction code')
    parser.add_argument('--error_correction_distance', type=int, default=3, help='Error correction code distance')
    parser.add_argument('--vault_validate', action='store_true', help='Run TMT Quantum Vault agent-task validation after training')
    parser.add_argument('--vault_repo', type=str, default=None, help='Path to a local TMT_Quantum_Vault checkout')
    parser.add_argument('--vault_mode', type=str, default='cloud', help='TMT Quantum Vault mode for post-training validation')
    parser.add_argument('--vault_model', type=str, default=None, help='Explicit Ollama model override for Vault validation')
    parser.add_argument('--vault_extra_context', type=str, default=None, help='Extra context appended to the Vault validation prompt')
    parser.add_argument('--summary_path', type=str, default='best_model.summary.json', help='Path to write structured training summary JSON')
    
    args = parser.parse_args()
    
    # Hyperparameters (can be overridden by config.yaml)
    try:
        from configs.config import load_config
        cfg = load_config()
    except Exception:
        cfg = None

    input_dim = (cfg['data']['input_dim'] if cfg and 'data' in cfg else 128)  # Size of quantum state representation
    latent_dim = args.latent_dim
    hidden_dims = args.hidden_dims
    batch_size = args.batch_size
    num_epochs = args.epochs
    use_mps = args.use_mps
    mps_bond_dim = args.mps_bond_dim
    use_quantum_kernel = args.use_quantum_kernel
    kernel_qubits = args.kernel_qubits
    kernel_layers = args.kernel_layers
    use_hybrid_optimizer = args.use_hybrid_optimizer
    consciousness_streaming = args.consciousness_streaming
    quantum_hardware = args.quantum_hardware
    use_error_correction = args.use_error_correction
    error_correction_type = args.error_correction_type
    error_correction_distance = args.error_correction_distance
    
    # Device selection
    if args.device == 'auto':
        device_setting = (cfg['training'].get('device') if cfg and 'training' in cfg else None)
        if device_setting:
            device = torch.device(device_setting)
        else:
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    else:
        device = torch.device(args.device)

    # Load unified sacred geometry and consciousness data
    print("Loading sacred geometry datasets...")
    sacred_datasets = load_sacred_datasets()

    print("Loading real consciousness data...")
    real_data = load_real_consciousness_data()

    print("Creating unified cross-domain dataset...")
    data, domain_labels = create_unified_dataset(sacred_datasets, real_data, input_dim)

    # Adjust input_dim to match data
    input_dim = data.shape[1]

    # Stratified train/val split using sklearn
    try:
        from sklearn.model_selection import train_test_split
        train_indices, val_indices = train_test_split(
            range(len(data)),
            test_size=0.2,
            stratify=domain_labels,
            random_state=42
        )
        train_data = data[train_indices]
        val_data = data[val_indices]
        train_labels = domain_labels[train_indices]
        val_labels = domain_labels[val_indices]
        print(f"Stratified split: Train samples = {len(train_data)}, Val samples = {len(val_data)}")
        print(f"Train domain distribution: {np.bincount(train_labels)}")
        print(f"Val domain distribution: {np.bincount(val_labels)}")
    except ImportError:
        print("Warning: sklearn not available, using simple split")
        train_size = int(0.8 * len(data))
        train_data = data[:train_size]
        val_data = data[train_size:]

    # Create data loaders
    train_dataset = TensorDataset(torch.from_numpy(train_data))
    val_dataset = TensorDataset(torch.from_numpy(val_data))
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    # Initialize model
    model = QuantumVAE(input_dim=input_dim, latent_dim=latent_dim, hidden_dims=hidden_dims, sparsity=0.1,
                      use_mps=use_mps, mps_bond_dim=mps_bond_dim,
                      use_quantum_kernel=use_quantum_kernel, kernel_qubits=kernel_qubits, kernel_layers=kernel_layers,
                      use_error_correction=use_error_correction, error_correction_type=error_correction_type,
                      error_correction_distance=error_correction_distance)
    model.to(device)

    print(f"Training Quantum VAE on {device}")
    print(f"Model: {model}")
    print(f"Training samples: {len(train_data)}, Validation samples: {len(val_data)}")

    # Train
    train_losses, val_losses, training_summary = train_vae(
        model,
        train_loader,
        val_loader,
        num_epochs,
        device,
        consciousness_streaming=consciousness_streaming,
        use_hybrid_optimizer=use_hybrid_optimizer,
    )

    # Plot results
    plot_losses(train_losses, val_losses)

    summary_path = write_training_summary(training_summary, args.summary_path)

    if args.vault_validate:
        if not VAULT_INTEGRATION_AVAILABLE:
            print(
                'TMT Quantum Vault integration module is not available '
                'in this environment.'
            )
        else:
            try:
                selected_vault_model = get_ollama_cloud_model(
                    'vae_checkpoint_validation',
                    override=args.vault_model,
                )
                vault_result = run_agent_task_validation(
                    training_summary,
                    checkpoint_path=training_summary.get(
                        'save_path',
                        'best_model.pt',
                    ),
                    repo_path=args.vault_repo,
                    mode=args.vault_mode,
                    model=selected_vault_model,
                    extra_context=args.vault_extra_context,
                )
                training_summary['vault_validation'] = vault_result.to_dict()
                training_summary['vault_validation']['selected_model'] = selected_vault_model
                write_training_summary(training_summary, args.summary_path)
                print('TMT Quantum Vault validation completed successfully.')
            except Exception as exc:
                print(f'TMT Quantum Vault validation failed: {exc}')

    print("Training completed!")
    print(f"Best model saved as 'best_model.pt'")
    print("Training curves saved as 'training_curves.png'")
    print(f"Training summary saved as '{summary_path}'")

if __name__ == "__main__":
    main()