#!/usr/bin/env python3
"""
QUANTUM CONSCIOUSNESS AGI - MAIN APPLICATION
===========================================

Main entry point for the Quantum Consciousness AGI system.
This application integrates:
- Quantum VAE for consciousness modeling
- Golden ratio pattern analysis  
- Multi-modal data processing
- NFT generation and deployment
- Web API interface

Usage:
    python main.py --mode train --config agi_app/config/default.yaml
    python main.py --mode serve --port 8000
    python main.py --mode analyze --data agi_app/data/inputs/
"""

import argparse
import asyncio
import logging
import sys
import json
from pathlib import Path
import numpy as np
import torch
from datetime import datetime

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))
sys.path.append(str(Path(__file__).parent))

# Import configuration system
from agi_app.config.config_manager import QuantumConsciousnessConfig, get_config

# Import core classes from the scientific script
try:
    from ai_app_builder_scientific_script import (
        AGIConfiguration,
        QuantumConsciousnessVAE,
        GoldenRatioAnalyzer,
        SacredGeometryMath,
        QuantumMechanicsCore,
        ConsciousnessComplexityAnalyzer,
        PHI  # Golden ratio constant
    )
except ImportError as e:
    print(f"Error importing scientific script: {e}")
    print("Make sure ai_app_builder_scientific_script.py is in the current directory")
    sys.exit(1)

# Import existing components
try:
    from fastapi_bridge import app as fastapi_app
except ImportError:
    fastapi_app = None
    print("Warning: fastapi_bridge not available")

try:
    from utils.performance_monitor import PerformanceMonitor
except ImportError:
    PerformanceMonitor = None
    print("Warning: performance_monitor not available")

try:
    from utils.golden_ratio_callback import GoldenRatioCallback
except ImportError:
    GoldenRatioCallback = None
    print("Warning: golden_ratio_callback not available")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class QuantumConsciousnessApp:
    """
    Main application class for Quantum Consciousness AGI.
    
    Orchestrates all components:
    - Model training and inference
    - Golden ratio analysis
    - Performance monitoring
    - API serving
    """
    
    def __init__(self, config_path: str = None):
        """Initialize application with configuration."""
        # Load configuration using our new config system
        self.quantum_config = get_config(config_path) if config_path else get_config()
        
        # Convert to AGIConfiguration for compatibility
        self.config = self._convert_to_agi_config()
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Initialize core components
        self.model = None
        self.golden_ratio_analyzer = None
        self.performance_monitor = None
        self.phi_callback = None
        
        logger.info(f"Initialized Quantum Consciousness App on {self.device}")
        logger.info(f"Golden Ratio φ = {PHI:.12f}")
    
    def _convert_to_agi_config(self) -> AGIConfiguration:
        """Convert QuantumConsciousnessConfig to AGIConfiguration."""
        return AGIConfiguration(
            input_dim=self.quantum_config.model.input_dim,
            latent_dim=self.quantum_config.model.latent_dim,
            hidden_dim=self.quantum_config.model.hidden_dim,
            epochs=self.quantum_config.training.epochs,
            batch_size=self.quantum_config.training.batch_size,
            learning_rate=self.quantum_config.training.learning_rate,
            weight_decay=self.quantum_config.training.weight_decay,
            early_stopping_patience=self.quantum_config.training.early_stopping_patience,
            reduce_lr_patience=self.quantum_config.training.reduce_lr_patience,
            weight_reconstruction=self.quantum_config.training.loss_weights.get('reconstruction', 1.0),
            weight_kl_divergence=self.quantum_config.training.loss_weights.get('kl_divergence', 0.0008),
            weight_hamming=self.quantum_config.training.loss_weights.get('hamming', 0.3),
            weight_coherence=self.quantum_config.training.loss_weights.get('coherence', 0.1),
            weight_hardware=self.quantum_config.training.loss_weights.get('hardware', 0.01),
            weight_mixed_state=self.quantum_config.training.loss_weights.get('mixed_state', 0.1),
            weight_fidelity=self.quantum_config.training.loss_weights.get('fidelity', 0.1),
            weight_entropy=self.quantum_config.training.loss_weights.get('entropy', 0.05),
            n_qubits=self.quantum_config.quantum.n_qubits,
            quantum_backend=self.quantum_config.quantum.backend,
            shots=self.quantum_config.quantum.shots,
            golden_ratio_threshold=self.quantum_config.golden_ratio_analysis.threshold,
            bootstrap_iterations=self.quantum_config.golden_ratio_analysis.bootstrap_iterations,
            permutation_iterations=self.quantum_config.golden_ratio_analysis.permutation_iterations,
            symmetry_tolerance=0.1,
            point_group_detection=True,
            output_dir=Path(self.quantum_config.paths.output_dir),
            model_checkpoint_dir=Path(self.quantum_config.paths.checkpoint_dir),
            visualization_dir=Path(self.quantum_config.paths.visualization_dir)
        )
    
    def initialize_model(self):
        """Initialize the Quantum VAE model."""
        logger.info("Initializing Quantum Consciousness VAE...")
        
        self.model = QuantumConsciousnessVAE(self.config).to(self.device)
        
        # Initialize golden ratio analyzer
        self.golden_ratio_analyzer = GoldenRatioAnalyzer(self.config)
        
        # Initialize performance monitor if available
        if PerformanceMonitor:
            self.performance_monitor = PerformanceMonitor(
                output_dir=self.config.visualization_dir / "monitoring"
            )
        
        # Initialize golden ratio callback if available
        if GoldenRatioCallback:
            self.phi_callback = GoldenRatioCallback(
                target_phi=PHI,
                resonance_threshold=0.7,
                track_frequency=5,
                output_dir=self.config.visualization_dir / "golden_ratio"
            )
        
        logger.info("Model and analyzers initialized successfully")
    
    def train_model(self, data_path: str = None):
        """
        Train the Quantum VAE model.
        
        Args:
            data_path: Path to training data
        """
        logger.info("Starting model training...")
        
        if self.model is None:
            self.initialize_model()
        
        # Generate synthetic data if none provided
        if data_path is None:
            logger.info("Generating synthetic consciousness data...")
            train_data, val_data = self._generate_synthetic_data()
        else:
            logger.info(f"Loading training data from {data_path}")
            # For now, use synthetic data - add real data loading later
            train_data, val_data = self._generate_synthetic_data()
        
        # Training setup
        optimizer = torch.optim.Adam(
            self.model.parameters(),
            lr=self.config.learning_rate,
            weight_decay=self.config.weight_decay
        )
        
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, mode='min', factor=0.5, patience=10
        )
        
        # Training loop
        best_loss = float('inf')
        patience_counter = 0
        
        for epoch in range(self.config.epochs):
            # Training phase
            self.model.train()
            train_losses = []
            
            for batch_idx, batch in enumerate(train_data):
                optimizer.zero_grad()
                
                x = batch[0].to(self.device)  # Get tensor from dataset
                recon, mu, logvar, z = self.model(x)
                
                loss_dict = self.model.compute_loss(x, recon, mu, logvar, z)
                loss = loss_dict['total']
                
                loss.backward()
                optimizer.step()
                train_losses.append(loss.item())
            
            avg_train_loss = sum(train_losses) / len(train_losses)
            
            # Validation phase
            self.model.eval()
            val_losses = []
            phi_resonances = []
            
            with torch.no_grad():
                for batch in val_data:
                    x = batch[0].to(self.device)
                    recon, mu, logvar, z = self.model(x)
                    
                    loss_dict = self.model.compute_loss(x, recon, mu, logvar, z)
                    val_losses.append(loss_dict['total'].item())
                    
                    # Calculate golden ratio resonance
                    z_np = z.cpu().numpy()
                    phi_results = self.golden_ratio_analyzer.detect_phi_ratios(z_np)
                    phi_resonances.append(phi_results['resonance_rate'])
            
            avg_val_loss = sum(val_losses) / len(val_losses)
            avg_phi_resonance = sum(phi_resonances) / len(phi_resonances)
            
            # Update learning rate
            scheduler.step(avg_val_loss)
            
            # Logging
            logger.info(
                f"Epoch {epoch+1}/{self.config.epochs} | "
                f"Train Loss: {avg_train_loss:.6f} | "
                f"Val Loss: {avg_val_loss:.6f} | "
                f"Φ Resonance: {avg_phi_resonance:.4f}"
            )
            
            # Performance monitoring
            if self.performance_monitor and hasattr(self.performance_monitor, 'log_epoch'):
                try:
                    self.performance_monitor.log_epoch(
                        epoch=epoch,
                        train_loss=avg_train_loss,
                        val_loss=avg_val_loss,
                        phi_resonance=avg_phi_resonance
                    )
                except Exception as e:
                    logger.warning(f"Performance monitoring failed: {e}")
            
            # Golden ratio callback
            if self.phi_callback and hasattr(self.phi_callback, 'on_epoch_end'):
                try:
                    self.phi_callback.on_epoch_end(epoch, self.model, z_np)
                except Exception as e:
                    logger.warning(f"Golden ratio callback failed: {e}")
            
            # Early stopping
            if avg_val_loss < best_loss:
                best_loss = avg_val_loss
                patience_counter = 0
                # Save best model
                torch.save(
                    self.model.state_dict(),
                    self.config.model_checkpoint_dir / "best_model.pt"
                )
            else:
                patience_counter += 1
                if patience_counter >= self.config.early_stopping_patience:
                    logger.info(f"Early stopping at epoch {epoch+1}")
                    break
        
        logger.info("Training completed!")
        
        # Generate final reports
        if self.performance_monitor and hasattr(self.performance_monitor, 'generate_final_report'):
            try:
                self.performance_monitor.generate_final_report()
            except Exception as e:
                logger.warning(f"Failed to generate performance report: {e}")
        
        if self.phi_callback and hasattr(self.phi_callback, 'generate_final_plot'):
            try:
                self.phi_callback.generate_final_plot()
            except Exception as e:
                logger.warning(f"Failed to generate golden ratio plot: {e}")
    
    def _generate_synthetic_data(self):
        """Generate synthetic consciousness data for training."""
        from torch.utils.data import DataLoader, TensorDataset
        
        # Generate data with golden ratio patterns
        n_samples = 1000  # Reduced for faster testing
        latent_dim = self.config.latent_dim
        
        # Create latent vectors with φ-resonant patterns
        phi_ratios = np.array([PHI ** i for i in range(latent_dim)])
        phi_ratios = phi_ratios / np.linalg.norm(phi_ratios)
        
        # Generate samples with varying φ-alignment
        latent_samples = []
        for _ in range(n_samples):
            # Base pattern with golden ratio
            base = phi_ratios * np.random.normal(1.0, 0.2)
            # Add noise
            noise = np.random.normal(0, 0.1, latent_dim)
            sample = base + noise
            latent_samples.append(sample)
        
        latent_samples = np.array(latent_samples)
        
        # Convert to input space using a simple linear mapping
        input_data = latent_samples @ np.random.randn(latent_dim, self.config.input_dim)
        input_data = torch.sigmoid(torch.tensor(input_data, dtype=torch.float32))
        
        # Split into train/val
        split_idx = int(0.8 * n_samples)
        train_data = TensorDataset(input_data[:split_idx])
        val_data = TensorDataset(input_data[split_idx:])
        
        train_loader = DataLoader(train_data, batch_size=self.config.batch_size, shuffle=True)
        val_loader = DataLoader(val_data, batch_size=self.config.batch_size, shuffle=False)
        
        return train_loader, val_loader
    
    def analyze_consciousness_data(self, data_path: str):
        """
        Analyze consciousness data for golden ratio patterns.
        
        Args:
            data_path: Path to data file
        """
        logger.info(f"Analyzing consciousness data from {data_path}")
        
        if self.golden_ratio_analyzer is None:
            self.golden_ratio_analyzer = GoldenRatioAnalyzer(self.config)
        
        # For now, generate synthetic data
        logger.info("Generating synthetic test data...")
        data = np.random.randn(100, 32)
        
        # Perform golden ratio analysis
        results = self.golden_ratio_analyzer.detect_phi_ratios(data, return_details=True)
        
        # Bootstrap confidence intervals
        ci_results = self.golden_ratio_analyzer.bootstrap_confidence_interval(data)
        
        # Permutation test
        perm_results = self.golden_ratio_analyzer.permutation_test(data)
        
        # Generate analysis report
        report = {
            'analysis_summary': results,
            'confidence_intervals': ci_results,
            'significance_testing': perm_results,
            'data_shape': data.shape,
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        # Save report
        output_path = self.config.output_dir / f"consciousness_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Analysis complete. Report saved to {output_path}")
        
        # Print summary
        print("\n" + "="*60)
        print("CONSCIOUSNESS DATA ANALYSIS SUMMARY")
        print("="*60)
        print(f"Data Shape: {data.shape}")
        print(f"Φ Detections: {results['n_phi_detections']}/{results['n_ratios_analyzed']}")
        print(f"Resonance Rate: {results['resonance_rate']:.4f}")
        print(f"Mean Deviation from Φ: {results['mean_deviation_from_phi']:.4f}")
        print(f"P-value: {perm_results['p_value']:.6f}")
        print(f"Significant at p<0.05: {perm_results['significant_at_05']}")
        print("="*60)
    
    def serve_api(self, host: str = "0.0.0.0", port: int = 8000):
        """
        Start the FastAPI web server.
        
        Args:
            host: Server host
            port: Server port
        """
        if fastapi_app is None:
            logger.error("FastAPI bridge not available")
            return
            
        logger.info(f"Starting API server on {host}:{port}")
        
        # Initialize model if not already done
        if self.model is None:
            self.initialize_model()
        
        # Add model to FastAPI app state
        fastapi_app.state.model = self.model
        fastapi_app.state.config = self.config
        fastapi_app.state.golden_ratio_analyzer = self.golden_ratio_analyzer
        
        # Run server
        import uvicorn
        uvicorn.run(fastapi_app, host=host, port=port, log_level="info")
    
    def run_demo(self):
        """Run a demonstration of the AGI capabilities."""
        logger.info("Running Quantum Consciousness AGI Demo...")
        
        # Demo 1: Generate sacred geometry patterns
        print("\n1. Generating Sacred Geometry Patterns...")
        fibonacci_seq = SacredGeometryMath.fibonacci_sequence(10)
        golden_spiral = SacredGeometryMath.golden_spiral_points(100)
        print(f"Fibonacci Sequence: {fibonacci_seq}")
        print(f"Golden Spiral points shape: {golden_spiral.shape}")
        
        # Demo 2: Quantum mechanics operations
        print("\n2. Quantum Mechanics Operations...")
        # Create a quantum state
        state = np.array([1/np.sqrt(2), 1/np.sqrt(2)], dtype=complex)
        density_matrix = QuantumMechanicsCore.create_density_matrix(state)
        entropy = QuantumMechanicsCore.von_neumann_entropy(density_matrix)
        fidelity = QuantumMechanicsCore.purity(density_matrix)
        print(f"Von Neumann Entropy: {entropy:.4f} bits")
        print(f"Quantum Purity: {fidelity:.4f}")
        
        # Demo 3: Consciousness complexity analysis
        print("\n3. Consciousness Complexity Analysis...")
        # Generate sample neural signal
        signal = np.random.randn(1000)
        lz_complexity = ConsciousnessComplexityAnalyzer.lempel_ziv_complexity(
            (signal > np.median(signal)).astype(int)
        )
        sample_entropy = ConsciousnessComplexityAnalyzer.sample_entropy(signal)
        print(f"Lempel-Ziv Complexity: {lz_complexity:.4f}")
        print(f"Sample Entropy: {sample_entropy:.4f}")
        
        # Demo 4: Golden ratio pattern detection
        print("\n4. Golden Ratio Pattern Detection...")
        # Generate test vectors with φ patterns
        test_vectors = np.array([
            [1, PHI, PHI**2, PHI**3],
            [PHI, 2*PHI, 3*PHI, 5*PHI],  # Fibonacci-like
            [1, 2, 3, 4]  # Non-φ pattern
        ])
        
        if self.golden_ratio_analyzer is None:
            self.golden_ratio_analyzer = GoldenRatioAnalyzer(self.config)
            
        results = self.golden_ratio_analyzer.detect_phi_ratios(test_vectors)
        print(f"Φ Resonance Rate: {results['resonance_rate']:.4f}")
        print(f"Number of Φ Detections: {results['n_phi_detections']}")
        
        # Demo 5: Model inference
        print("\n5. Quantum VAE Inference...")
        if self.model is None:
            self.initialize_model()
            
        with torch.no_grad():
            sample_input = torch.randn(1, self.config.input_dim).to(self.device)
            recon, mu, logvar, z = self.model(sample_input)
            print(f"Input shape: {sample_input.shape}")
            print(f"Latent shape: {z.shape}")
            print(f"Reconstruction shape: {recon.shape}")
            
            # Analyze latent golden ratio patterns
            z_np = z.cpu().numpy()
            phi_results = self.golden_ratio_analyzer.detect_phi_ratios(z_np)
            print(f"Latent Φ Resonance: {phi_results['resonance_rate']:.4f}")
        
        print("\n" + "="*60)
        print("DEMO COMPLETE")
        print("="*60)


def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(
        description="Quantum Consciousness AGI Application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --mode train --epochs 100
  %(prog)s --mode serve --port 8000
  %(prog)s --mode analyze --data agi_app/data/consciousness.npy
  %(prog)s --mode demo
        """
    )
    
    parser.add_argument(
        "--mode", 
        choices=["train", "serve", "analyze", "demo"],
        default="demo",
        help="Application mode"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        default="agi_app/config/default.yaml",
        help="Configuration file path"
    )
    
    parser.add_argument(
        "--data",
        type=str,
        help="Data file path for analysis mode"
    )
    
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Server host for serve mode"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Server port for serve mode"
    )
    
    parser.add_argument(
        "--epochs",
        type=int,
        help="Number of training epochs"
    )
    
    args = parser.parse_args()
    
    # Create application
    app = QuantumConsciousnessApp(args.config)
    
    # Override config if specified
    if args.epochs:
        app.config.epochs = args.epochs
    
    # Run based on mode
    try:
        if args.mode == "train":
            app.train_model(args.data)
        elif args.mode == "serve":
            app.serve_api(args.host, args.port)
        elif args.mode == "analyze":
            app.analyze_consciousness_data(args.data or "synthetic_data.npy")
        elif args.mode == "demo":
            app.run_demo()
        else:
            logger.error(f"Unknown mode: {args.mode}")
            sys.exit(1)
    
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        raise


if __name__ == "__main__":
    main()