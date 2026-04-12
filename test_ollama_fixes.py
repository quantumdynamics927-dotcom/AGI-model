#!/usr/bin/env python3
"""
Quick test of Ollama fixes: streaming=False, keep_alive, longer timeout
"""

import requests
import json

def test_model(model_name):
    """Test a model with proper parameters."""
    print(f"\nTesting {model_name}...")
    
    messages = [
        {"role": "system", "content": "Reply concisely."},
        {"role": "user", "content": "What is consciousness? Answer in one sentence."}
    ]
    
    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": model_name,
                "messages": messages,
                "stream": False,  # Critical fix
                "keep_alive": "10m"  # Keep model loaded
            },
            timeout=120  # Longer timeout for cold starts
        )
        
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            text = result.get('message', {}).get('content', '')
            print(f"  ✓ Success: {text[:100]}...")
            return True
        else:
            print(f"  ✗ HTTP {response.status_code}: {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"  ✗ Timeout after 120s (model may be loading)")
        return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing Ollama Fixes")
    print("=" * 60)
    
    # Test models in order of size
    models = ["llama3.2:1b", "qwen3:1.7b", "qwen3.5:2b"]
    
    results = {}
    for model in models:
        results[model] = test_model(model)
    
    print("\n" + "=" * 60)
    print("Summary:")
    for model, success in results.items():
        status = "✓" if success else "✗"
        print(f"  {status} {model}")
