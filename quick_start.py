#!/usr/bin/env python3
"""
QUICK START for Quantum Consciousness AGI
======================================

This script provides a quick way to test and run the AGI application
without complex setup or dependencies on optional components.
"""

import sys
import os
import logging
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

try:
    import numpy as np
    import torch
    import matplotlib.pyplot as plt
    import yaml
    print("✓ Core dependencies available")
except ImportError as e:
    print(f"✗ Missing core dependency: {e}")
    print("Please install: pip install numpy torch matplotlib pyyaml")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """Test all major imports and report status."""
    print("\n" + "="*50)
    print("TESTING IMPORTS")
    print("="*50)
    
    # Test scientific script
    try:
        from ai_app_builder_scientific_script import (
            PHI, SacredGeometryMath, QuantumMechanicsCore,
            ConsciousnessComplexityAnalyzer, GoldenRatioAnalyzer
        )
        print("✓ Scientific script imported successfully")
        print(f"  Golden Ratio φ = {PHI:.12f}")
    except ImportError as e:
        print(f"✗ Scientific script import failed: {e}")
        return False
    
    # Test configuration system
    try:
        from agi_app.config.config_manager import get_config
        config = get_config()
        print("✓ Configuration system working")
        print(f"  Model: {config.model.input_dim}→{config.model.latent_dim} dims")
    except Exception as e:
        print(f"✗ Configuration system failed: {e}")
        return False
    
    # Test PyTorch
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"✓ PyTorch working on {device}")
    
    return True

def test_sacred_geometry():
    """Test sacred geometry computations."""
    print("\n" + "="*50)
    print("TESTING SACRED GEOMETRY")
    print("="*50)
    
    try:
        from ai_app_builder_scientific_script import SacredGeometryMath, PHI
        
        # Fibonacci sequence
        fib = SacredGeometryMath.fibonacci_sequence(10)
        print(f"Fibonacci Sequence (n=10): {fib}")
        
        # Check convergence to φ
        if len(fib) >= 3:
            ratios = [fib[i]/fib[i-1] for i in range(2, len(fib))]
            print(f"Fibonacci Ratios: {[f'{r:.6f}' for r in ratios]}")
            print(f"Convergence to φ: {ratios[-1]:.6f} (target: {PHI:.6f})")
        
        # Golden spiral
        spiral = SacredGeometryMath.golden_spiral_points(100, scale=1.0)
        print(f"Golden Spiral: {spiral.shape} points generated")
        
        # Platonic solids
        for solid in ['tetrahedron', 'cube', 'octahedron']:
            vertices = SacredGeometryMath.platonic_solid_vertices(solid)
            print(f"{solid.capitalize()}: {vertices.shape} vertices")
        
        return True
        
    except Exception as e:
        print(f"✗ Sacred geometry test failed: {e}")
        return False

def test_quantum_mechanics():
    """Test quantum mechanics operations."""
    print("\n" + "="*50)
    print("TESTING QUANTUM MECHANICS")
    print("="*50)
    
    try:
        from ai_app_builder_scientific_script import QuantumMechanicsCore
        
        # Create quantum state |ψ⟩ = (|0⟩ + |1⟩)/√2
        psi = np.array([1/np.sqrt(2), 1/np.sqrt(2)], dtype=complex)
        print(f"Quantum State |ψ⟩: {psi}")
        
        # Density matrix ρ = |ψ⟩⟨ψ|
        rho = QuantumMechanicsCore.create_density_matrix(psi)
        print(f"Density Matrix ρ:\n{rho}")
        
        # Quantum properties
        entropy = QuantumMechanicsCore.von_neumann_entropy(rho)
        purity = QuantumMechanicsCore.purity(rho)
        coherence = QuantumMechanicsCore.quantum_coherence_l1(rho)
        
        print(f"Von Neumann Entropy: {entropy:.4f} bits")
        print(f"Quantum Purity: {purity:.4f}")
        print(f"L1 Coherence: {coherence:.4f}")
        
        # Mixed state example
        mixed_rho = QuantumMechanicsCore.mixed_state_density_matrix(
            [psi, np.array([1, 0])], [0.7, 0.3]
        )
        mixed_entropy = QuantumMechanicsCore.von_neumann_entropy(mixed_rho)
        print(f"Mixed State Entropy: {mixed_entropy:.4f} bits (vs pure: {entropy:.4f})")
        
        return True
        
    except Exception as e:
        print(f"✗ Quantum mechanics test failed: {e}")
        return False

def test_consciousness_analysis():
    """Test consciousness complexity analysis."""
    print("\n" + "="*50)
    print("TESTING CONSCIOUSNESS ANALYSIS")
    print("="*50)
    
    try:
        from ai_app_builder_scientific_script import (
            ConsciousnessComplexityAnalyzer, GoldenRatioAnalyzer, get_config
        )
        
        # Generate synthetic neural signal
        np.random.seed(42)  # For reproducible results
        signal = np.random.randn(1000)
        
        # Convert to binary signal for LZ complexity
        binary_signal = (signal > np.median(signal)).astype(int)
        
        # Complexity measures
        lz_complexity = ConsciousnessComplexityAnalyzer.lempel_ziv_complexity(binary_signal)
        sample_entropy = ConsciousnessComplexityAnalyzer.sample_entropy(signal)
        fractal_dim = ConsciousnessComplexityAnalyzer.fractal_dimension_higuchi(signal)
        
        print(f"Lempel-Ziv Complexity: {lz_complexity:.4f}")
        print(f"Sample Entropy: {sample_entropy:.4f}")
        print(f"Higuchi Fractal Dimension: {fractal_dim:.4f}")
        
        # Golden ratio analysis
        config = get_config()
        analyzer = GoldenRatioAnalyzer(config._config if hasattr(config, '_config') else config)
        
        # Test with φ-patterns
        test_data = np.array([
            [1, PHI, PHI**2, PHI**3],
            [PHI, 2*PHI, 3*PHI, 5*PHI],
            [1, 2, 3, 4]
        ])
        
        results = analyzer.detect_phi_ratios(test_data)
        print(f"Golden Ratio Analysis:")
        print(f"  Resonance Rate: {results['resonance_rate']:.4f}")
        print(f"  Φ Detections: {results['n_phi_detections']}")
        print(f"  Mean Deviation: {results['mean_deviation_from_phi']:.4f}")
        
        return True
        
    except Exception as e:
        print(f"✗ Consciousness analysis test failed: {e}")
        return False

def test_model_creation():
    """Test basic model creation and forward pass."""
    print("\n" + "="*50)
    print("TESTING MODEL CREATION")
    print("="*50)
    
    try:
        from ai_app_builder_scientific_script import AGIConfiguration, QuantumConsciousnessVAE
        
        # Create minimal config for testing
        config = AGIConfiguration(
            input_dim=32,
            latent_dim=8,
            hidden_dim=16,
            epochs=1  # Just for testing
        )
        
        # Create model
        model = QuantumConsciousnessVAE(config)
        print(f"✓ Model created with {sum(p.numel() for p in model.parameters())} parameters")
        
        # Test forward pass
        batch_size = 4
        x = torch.randn(batch_size, config.input_dim)
        
        with torch.no_grad():
            recon, mu, logvar, z = model(x)
            
        print(f"✓ Forward pass successful:")
        print(f"  Input: {x.shape}")
        print(f"  Latent μ: {mu.shape}")
        print(f"  Latent logσ²: {logvar.shape}")
        print(f"  Latent z: {z.shape}")
        print(f"  Reconstruction: {recon.shape}")
        
        # Test loss computation
        loss_dict = model.compute_loss(x, recon, mu, logvar, z)
        print(f"✓ Loss computation successful:")
        for key, value in loss_dict.items():
            print(f"  {key}: {value:.6f}")
        
        return True
        
    except Exception as e:
        print(f"✗ Model creation test failed: {e}")
        return False

def generate_simple_visualization():
    """Generate a simple visualization to test matplotlib."""
    print("\n" + "="*50)
    print("GENERATING VISUALIZATION")
    print("="*50)
    
    try:
        import matplotlib.pyplot as plt
        from ai_app_builder_scientific_script import SacredGeometryMath, PHI
        
        # Create golden spiral
        spiral = SacredGeometryMath.golden_spiral_points(200, scale=2.0)
        
        # Create Fibonacci visualization
        fib = SacredGeometryMath.fibonacci_sequence(15)
        ratios = [fib[i]/fib[i-1] for i in range(2, len(fib))]
        
        # Create subplot
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # Plot golden spiral
        ax1.plot(spiral[:, 0], spiral[:, 1], 'b-', linewidth=2)
        ax1.scatter(spiral[::20, 0], spiral[::20, 1], c='red', s=50, zorder=5)
        ax1.set_title('Golden Spiral (φ ≈ 1.618)')
        ax1.set_xlabel('X')
        ax1.set_ylabel('Y')
        ax1.grid(True, alpha=0.3)
        ax1.set_aspect('equal')
        
        # Plot Fibonacci convergence
        indices = list(range(2, len(fib)))
        ax2.plot(indices, ratios, 'go-', linewidth=2, markersize=6)
        ax2.axhline(y=PHI, color='r', linestyle='--', label=f'Golden Ratio φ = {PHI:.6f}')
        ax2.set_title('Fibonacci Ratio Convergence to φ')
        ax2.set_xlabel('n')
        ax2.set_ylabel('F(n)/F(n-1)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save visualization
        output_path = "agi_app/outputs/quick_start_visualization.png"
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"✓ Visualization saved to {output_path}")
        
        plt.close()
        return True
        
    except Exception as e:
        print(f"✗ Visualization failed: {e}")
        return False

def main():
    """Run all quick start tests."""
    print("QUANTUM CONSCIOUSNESS AGI - QUICK START")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_imports),
        ("Sacred Geometry", test_sacred_geometry),
        ("Quantum Mechanics", test_quantum_mechanics),
        ("Consciousness Analysis", test_consciousness_analysis),
        ("Model Creation", test_model_creation),
        ("Visualization", generate_simple_visualization)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("QUICK START SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:<25} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The AGI application is ready to use.")
        print("\nNext steps:")
        print("  python main.py --mode demo      # Run full demo")
        print("  python main.py --mode train      # Train model")
        print("  python main.py --mode serve      # Start API server")
    else:
        print(f"\n⚠️  {total-passed} tests failed. Check the errors above.")
        print("Make sure all dependencies are installed correctly.")
    
    print("="*60)

if __name__ == "__main__":
    main()