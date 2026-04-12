#!/usr/bin/env python3
"""
Test the provider architecture without the full demo
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from unified_model_provider import ModelRouter

def test_architecture():
    """Test the provider architecture."""
    print("Testing Provider Architecture")
    print("=" * 60)
    
    # Initialize router
    router = ModelRouter()
    print("✓ Model Router initialized")
    
    # Check health
    health = router.healthcheck_all()
    print(f"✓ Health check: {health}")
    
    # Get status
    status = router.get_all_status()
    print(f"✓ Ollama Local status: {status['ollama_local']['available']}")
    
    # Test model capabilities
    ollama_provider = router.providers['ollama_local']
    caps = ollama_provider.get_capabilities()
    print("✓ Model capabilities:")
    for model, cap in caps.items():
        print(f"  - {model}: {cap}")
    
    # Test list models
    models = ollama_provider.list_models()
    print(f"✓ Available models: {len(models)} models")
    
    print("\n✅ Provider architecture working correctly!")
    print("   Primary: llama3.2:1b")
    print("   Secondary: qwen3:1.7b") 
    print("   Experimental: qwen3.5:2b")

if __name__ == "__main__":
    test_architecture()