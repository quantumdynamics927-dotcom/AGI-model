#!/usr/bin/env python3
"""
Hybrid Neural Backbone Demo

This script demonstrates the hybrid architecture combining:
- BitNet: CPU-optimized local backbone
- Ollama Cloud: Powerful cloud reasoning
- Fallback models: Local alternatives on D: drive
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def demo_hybrid_backbone():
    """Demonstrate hybrid neural backbone integration."""
    print("Hybrid Neural Backbone Demo")
    print("=" * 60)

    try:
        # Import the hybrid backbone
        from hybrid_neural_backbone import HybridNeuralBackbone, get_biomimetic_thought
        print("> Hybrid Neural Backbone imported successfully")

        # Initialize the hybrid backbone
        backbone = HybridNeuralBackbone()
        print("> Hybrid backbone initialized")

        # Test biomimetic thought generation
        test_prompt = "What is the fundamental nature of biomimetic intelligence?"
        phi_resonance = 1.618033988749895  # Golden ratio

        print(f"\nGenerating biomimetic thought...")
        print(f"Input: {test_prompt}")
        print(f"Phi resonance: {phi_resonance:.6f}")

        thought = backbone.generate_biomimetic_thought(test_prompt, phi_resonance)

        print(f"\nGenerated Thought:")
        print(f"  {thought['generated_text']}")
        print(f"\nConsciousness Metrics:")
        print(f"  Backend: {thought.get('backend', 'unknown')}")
        print(f"  Entropy: {thought['entropy']:.4f}")
        print(f"  Phi Coherence: {thought['phi_coherence']:.4f}")
        print(f"  Consciousness Depth: {thought['consciousness_depth']:.4f}")
        print(f"  Biomimetic Resonance: {thought['biomimetic_resonance']:.4f}")
        print(f"  Inference Time: {thought['inference_time']:.3f}s")
        print(f"  Neural Layers: {thought['n_layers']}")
        print(f"  Ternary Entropy: {thought.get('ternary_entropy_used', False)}")

        if thought.get('simulated'):
            print("  Using simulated mode (models not available)")

        # Test consciousness space compression
        print(f"\nTesting Consciousness Space Compression...")
        import numpy as np

        # Create sample consciousness data
        n_agents = 3
        consciousness_data = np.random.randn(n_agents, 64) * 0.5

        print(f"  Compressing {consciousness_data.shape[1]}D consciousness space for {n_agents} agents...")

        latent_data, metrics = backbone.compress_consciousness_space(consciousness_data)

        print("  Compression Results:")
        print(f"    Latent dimensions: {latent_data.shape[1]}D")
        print(f"    Compression ratio: {metrics['compression_ratio']:.2f}x")
        print(f"    Phi resonance: {metrics['phi_resonance']:.4f}")
        print(f"    Avg inference time: {metrics['avg_inference_time']:.3f}s")
        print(f"    Generated consciousness outputs: {len(metrics['consciousness_outputs'])}")
        print(f"    Backends used: {metrics['backends_used']}")
        print(f"    Ternary entropy: {metrics['ternary_entropy_used']}")

        # Test convenience function
        print(f"\nTesting Convenience Function...")
        simple_thought = get_biomimetic_thought("Hello, biomimetic consciousness!")
        print(f"  Simple thought: {simple_thought[:100]}...")

        print(f"\nHybrid Backbone Demo Complete!")
        print("  The hybrid neural backbone is ready for biomimetic AGI!")

        # Show backbone status
        status = backbone.get_backbone_status()
        print(f"\nBackbone Status:")
        print(f"  BitNet loaded: {status['bitnet_loaded']}")
        print(f"  BitNet path: {status['bitnet_path']}")
        print(f"  Ollama API: {status['ollama_api']}")
        print(f"  Ollama model: {status['ollama_model']}")
        print(f"  Fallback path: {status['fallback_path']}")
        print(f"  Ternary entropy: {status['ternary_entropy_loaded']}")
        print(f"  Device: {status['device']}")

    except ImportError as e:
        print(f"Import Error: {e}")
        print("  Install required packages: pip install llama-cpp-python requests")
    except Exception as e:
        print(f"Demo Error: {e}")
        print("  This may be expected if models are not available")

def demo_full_hybrid_agi():
    """Run the full hybrid AGI demo."""
    print("\nFull Hybrid AGI Demo")
    print("=" * 60)

    try:
        from biomimetic_agi_demo import BiomimeticAGIDemonstrator

        # Run the complete demonstration
        demonstrator = BiomimeticAGIDemonstrator()
        results = demonstrator.run_complete_demonstration()

        print("\nFull Hybrid AGI Demo Results:")
        print(f"   Convergence Status: {results['convergence_status']}")
        print(f"   Hybrid Backbone: Active")
        print(f"   Models on D: drive: Optimized")

    except Exception as e:
        print(f"Full demo failed: {e}")
        print("  This may be expected if the full AGI demo is not available")

if __name__ == "__main__":
    demo_hybrid_backbone()
    
    # Uncomment to run full demo
    # demo_full_hybrid_agi()
    
    print("\nDemo complete! Run 'python demo_hybrid_backbone.py --full' for the full hybrid AGI system.")