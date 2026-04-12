#!/usr/bin/env python3
"""
Quick test to verify llama3.2:1b integration works
"""

import requests
import json

def test_llama():
    """Test llama3.2:1b model."""
    print("Testing llama3.2:1b integration...")
    
    messages = [
        {"role": "system", "content": "You are a biomimetic neural backbone. Reply concisely."},
        {"role": "user", "content": "What is consciousness?"}
    ]
    
    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "llama3.2:1b",
                "messages": messages,
                "stream": False,
                "keep_alive": "5m"
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            text = result.get('message', {}).get('content', '')
            print(f"✓ Success: {text[:100]}...")
            return True
        else:
            print(f"✗ HTTP {response.status_code}: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_llama()
    if success:
        print("\n✅ llama3.2:1b integration working! Use this model instead of qwen3.5:2b.")
    else:
        print("\n❌ Integration failed. Check if Ollama is running: ollama serve")