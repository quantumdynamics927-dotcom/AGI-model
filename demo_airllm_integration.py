#!/usr/bin/env python3
"""
AirLLM Biomimetic AGI Integration Demo

This script demonstrates the integration of AirLLM into the biomimetic AGI framework,
showing how layered LLM inference replaces simulated neural consciousness.
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def demo_airllm_integration():
    """Demonstrate AirLLM integration with biomimetic AGI."""
    print("🚀 AirLLM Biomimetic AGI Integration Demo")
    print("=" * 60)

    try:
        # Import the AirLLM neural backbone
        from airllm_neural_backbone import AirLLMNeuralBackbone, get_biomimetic_thought
        print("✓ AirLLM Neural Backbone imported successfully")

        # Initialize the neural backbone
        backbone = AirLLMNeuralBackbone()
        print("✓ Neural backbone initialized")

        # Test biomimetic thought generation
        test_prompt = "What is the fundamental nature of biomimetic intelligence?"
        phi_resonance = 1.618033988749895  # Golden ratio

        print(f"\n🧠 Generating biomimetic thought...")
        print(f"Input: {test_prompt}")
        print(f"Phi resonance: {phi_resonance:.6f}")

        thought = backbone.generate_biomimetic_thought(test_prompt, phi_resonance)

        print("\n📝 Generated Thought:")
        print(f"  {thought['generated_text']}")
        print("\n📊 Consciousness Metrics:")
        print(f"  Entropy: {thought['entropy']:.4f}")
        print(f"  Phi Coherence: {thought['phi_coherence']:.4f}")
        print(f"  Consciousness Depth: {thought['consciousness_depth']:.4f}")
        print(f"  Biomimetic Resonance: {thought['biomimetic_resonance']:.4f}")
        print(f"  Inference Time: {thought['inference_time']:.3f}s")
        print(f"  Neural Layers: {thought['n_layers']}")

        if thought.get('fallback'):
            print("  ⚠ Using fallback mode (AirLLM model not available)")

        # Test consciousness space compression
        print("\n🗜️ Testing Consciousness Space Compression...")
        import numpy as np

        # Create sample consciousness data
        n_agents = 5
        consciousness_data = np.random.randn(n_agents, 64) * 0.5

        print(f"  Compressing {consciousness_data.shape[1]}D consciousness space for {n_agents} agents...")

        latent_data, metrics = backbone.compress_consciousness_space(consciousness_data)

        print("  Compression Results:")
        print(f"    Latent dimensions: {latent_data.shape[1]}D")
        print(f"    Compression ratio: {metrics['compression_ratio']:.2f}x")
        print(f"    Phi resonance: {metrics['phi_resonance']:.4f}")
        print(f"    Avg inference time: {metrics['avg_inference_time']:.3f}s")
        print(f"    Generated consciousness outputs: {len(metrics['consciousness_outputs'])}")

        # Test convenience function
        print("\n🔧 Testing Convenience Function...")
        simple_thought = get_biomimetic_thought("Hello, biomimetic consciousness!")
        print(f"  Simple thought: {simple_thought[:100]}...")

        print("\n✅ AirLLM Integration Demo Complete!")
        print("  The neural backbone is ready for biomimetic AGI!")

    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("  Install AirLLM with: pip install airllm")
    except Exception as e:
        print(f"❌ Demo Error: {e}")
        print("  This may be expected if model weights are not downloaded")

def demo_full_biomimetic_agi():
    """Run the full biomimetic AGI demo with AirLLM integration."""
    print("\n🌟 Full Biomimetic AGI Demo with AirLLM")
    print("=" * 60)

    try:
        from biomimetic_agi_demo import BiomimeticAGIDemonstrator

        # Run the complete demonstration
        demonstrator = BiomimeticAGIDemonstrator()
        results = demonstrator.run_complete_demonstration()

        print("\n🎉 Full Biomimetic AGI Demo Results:")
        print(f"   Convergence Status: {results['convergence_status']}")
        print(f"   Overall Convergence: {results['overall_convergence']:.4f}")
        print("   Visualization saved as: biomimetic_agi_unified_demo.png")

        # Check if AirLLM was used
        if demonstrator.metrics['neural'].get('airllm_enabled'):
            print("   AirLLM Status: ✓ Active - Real neural inference achieved!")
        else:
            print("   AirLLM Status: ✗ Simulated - Install AirLLM for real inference")

    except Exception as e:
        print(f"❌ Full Demo Error: {e}")

if __name__ == "__main__":
    import sys

    # Run the AirLLM integration demo
    demo_airllm_integration()

    # Check for command line argument to run full demo
    if len(sys.argv) > 1 and sys.argv[1] == "--full":
        demo_full_biomimetic_agi()
    else:
        print("\nDemo complete! Run 'python demo_airllm_integration.py --full' to see the full biomimetic AGI system.")