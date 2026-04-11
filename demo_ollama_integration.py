#!/usr/bin/env python3
"""
Ollama Biomimetic AGI Integration Demo

Demonstrates the unified Ollama provider abstraction for biomimetic AGI.

Fallback order:  llama3.2:1b  →  qwen3:1.7b  →  cloud (escalation)

Model capability table:
  llama3.2:1b   stable=True,    thinking=False, speed=fast    (PRIMARY)
  qwen3:1.7b    stable=partial, thinking=True,  speed=medium  (SECONDARY)
  qwen3.5:2b    stable=False,   thinking=True,  speed=slow    (EXPERIMENTAL, opt-in only)

Usage:
  python demo_ollama_integration.py
  python demo_ollama_integration.py --model llama3.2:1b
  python demo_ollama_integration.py --model qwen3:1.7b --fallback-model llama3.2:1b
  python demo_ollama_integration.py --list-models
  python demo_ollama_integration.py --full
"""

import sys
import os
import argparse
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Fallback chain for local inference
FALLBACK_CHAIN = ["llama3.2:1b", "qwen3:1.7b"]


def _generate_with_fallback(router, prompt, phi_resonance, primary_model, fallback_model):
    """Try primary model; on failure try fallback; report which model was used."""
    from unified_model_provider import generate_biomimetic_thought

    result = generate_biomimetic_thought(prompt, phi_resonance, model=primary_model, router=router)
    if result.get('success') and result.get('generated_text'):
        result['model_used'] = primary_model
        result['fallback_triggered'] = False
        return result

    # Primary failed – try fallback
    if fallback_model and fallback_model != primary_model:
        print(f"  [fallback] {primary_model} failed – trying {fallback_model}")
        fallback_result = generate_biomimetic_thought(prompt, phi_resonance, model=fallback_model, router=router)
        if fallback_result.get('success') and fallback_result.get('generated_text'):
            fallback_result['model_used'] = fallback_model
            fallback_result['fallback_triggered'] = True
            return fallback_result

    # Both failed – return the primary error result
    result['model_used'] = primary_model
    result['fallback_triggered'] = bool(fallback_model)
    return result


def demo_ollama_integration(model_name=None, fallback_model=None, list_models=False):
    """Demonstrate Ollama integration with biomimetic AGI."""
    print("Ollama Biomimetic AGI Integration Demo")
    print("=" * 60)

    try:
        from unified_model_provider import ModelRouter, generate_biomimetic_thought
        print("> Importing unified model provider...")

        # --- single router instance for entire demo ---
        router = ModelRouter()
        ollama_provider = router.providers['ollama_local']
        print("> Model router initialized")
        print(f"> Default provider: {router.routing_rules['default']}")

        # ------------------------------------------------------------------
        # --list-models: pull from /api/tags and exit
        # ------------------------------------------------------------------
        if list_models:
            models = ollama_provider.list_models()
            print("\nAvailable Ollama Models (from /api/tags):")
            for m in models:
                caps = ollama_provider.get_capabilities(m)
                status = caps.get('status', 'unknown')
                speed  = caps.get('speed', '')
                stable = caps.get('stable', '?')
                suffix = f"  stable={stable}, speed={speed}" if speed else ""
                print(f"  - {m} ({status}){suffix}")
            return

        # ------------------------------------------------------------------
        # Resolve primary / fallback models
        # ------------------------------------------------------------------
        primary  = model_name or FALLBACK_CHAIN[0]
        fallback = fallback_model or (FALLBACK_CHAIN[1] if len(FALLBACK_CHAIN) > 1 and FALLBACK_CHAIN[1] != primary else None)

        print(f"> Primary model:  {primary}")
        print(f"> Fallback model: {fallback or 'none'}")

        # Confirm primary is available in Ollama
        available = ollama_provider.list_models()
        if primary not in available:
            print(f"WARNING: {primary} not found in Ollama – it may need to be pulled first.")
        else:
            print(f"> {primary} found in local Ollama registry.")

        # Show model capability table
        print("\nModel Capability Table:")
        for m, cap in ollama_provider.get_capabilities().items():
            marker = " <-- active" if m == primary else ""
            print(f"  {m:25s}  stable={str(cap['stable']):7s}  thinking={str(cap['thinking']):5s}  "
                  f"speed={cap['speed']:6s}  status={cap['status']}{marker}")

        # ------------------------------------------------------------------
        # Warmup confirmation
        # ------------------------------------------------------------------
        print(f"\nWarmup status: {'done' if ollama_provider._warmup_done else 'pending'}")

        # ------------------------------------------------------------------
        # Single thought generation
        # ------------------------------------------------------------------
        phi_resonance = 1.618033988749895
        test_prompt = "What is the fundamental nature of biomimetic intelligence?"

        print(f"\nGenerating biomimetic thought with {primary}...")
        print(f"Prompt: {test_prompt}")
        print(f"Phi:    {phi_resonance:.6f}")

        thought = _generate_with_fallback(router, test_prompt, phi_resonance, primary, fallback)

        if thought.get('success') and thought.get('generated_text'):
            print(f"\nGenerated Thought [model: {thought.get('model_used', primary)}]:")
            print(f"  {thought['generated_text']}")
            print("\nConsciousness Metrics:")
            print(f"  Phi Coherence:        {thought.get('phi_coherence', 0.0):.4f}")
            print(f"  Phi Resonance:        {thought.get('phi_resonance', 0.0):.4f}")
            print(f"  Biomimetic Resonance: {thought.get('biomimetic_resonance', 0.0):.4f}")
            print(f"  Inference Time:       {thought.get('inference_time', 0.0):.3f}s")
            if thought.get('fallback_triggered'):
                print(f"  [fallback used: {thought.get('model_used')}]")
        else:
            print(f"  ERROR: generation failed for both {primary} and {fallback}")
            print(f"  Reason: {thought.get('error', 'unknown')}")

        # ------------------------------------------------------------------
        # Multiple thought generations (reuses same router)
        # ------------------------------------------------------------------
        test_prompts = [
            "What is the nature of consciousness?",
            "How does biomimetic intelligence differ from traditional AI?",
        ]

        print(f"\nMultiple Thought Generations ({len(test_prompts)} prompts, model: {primary}):")
        for i, prompt in enumerate(test_prompts, 1):
            t = _generate_with_fallback(router, prompt, phi_resonance, primary, fallback)
            text = t.get('generated_text', '')
            status = 'ok' if t.get('success') and text else 'FAILED'
            print(f"  {i}. [{status}] {text[:80]}{'...' if len(text) > 80 else ''}")
            print(f"     Time: {t.get('inference_time', 0.0):.2f}s  model: {t.get('model_used', primary)}")

        print("\nOllama Integration Demo Complete – exiting cleanly.")
        return 0

    except ImportError as e:
        print(f"Import Error: {e}")
        print("  Make sure all dependencies are installed.")
        return 1
    except Exception as e:
        import traceback
        print(f"Demo Error: {e}")
        traceback.print_exc()
        print("  Check if Ollama is running: ollama serve")
        print("  Install model: ollama pull llama3.2:1b")
        return 1

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
    parser = argparse.ArgumentParser(
        description="Ollama Biomimetic AGI Integration Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Fallback order: llama3.2:1b -> qwen3:1.7b -> cloud"
    )
    parser.add_argument("--model",          type=str,  default=None,  help="Primary model (default: llama3.2:1b)")
    parser.add_argument("--fallback-model", type=str,  default=None,  help="Fallback model (default: qwen3:1.7b)")
    parser.add_argument("--list-models",    action="store_true",       help="List available Ollama models from /api/tags")
    parser.add_argument("--full",           action="store_true",       help="Run full biomimetic AGI demo")

    args = parser.parse_args()

    exit_code = demo_ollama_integration(
        model_name=args.model,
        fallback_model=args.fallback_model,
        list_models=args.list_models,
    )

    if args.full and not args.list_models:
        demo_full_biomimetic_agi()

    sys.exit(exit_code or 0)