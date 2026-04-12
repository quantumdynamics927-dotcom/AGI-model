#!/usr/bin/env python3
"""
Quick test for llama3.2:1b
"""

import requests
import json

def test_llama():
    """Test llama3.2:1b."""
    print("Testing llama3.2:1b...")
    
    data = {
        "model": "llama3.2:1b",
        "messages": [{"role": "user", "content": "What is consciousness?"}],
        "stream": False
    }
    
    try:
        response = requests.post(
            "http://localhost:11434/api/chat",
            json=data,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            text = result.get('message', {}).get('content', '')
            print(f"✓ Success: {text[:100]}...")
            return True
        else:
            print(f"✗ Error: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"✗ Exception: {e}")
        return False

if __name__ == "__main__":
    success = test_llama()
    if success:
        print("\n✅ llama3.2:1b is working! Use this model.")
    else:
        print("\n❌ Test failed.")