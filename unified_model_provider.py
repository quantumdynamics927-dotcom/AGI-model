#!/usr/bin/env python3
"""
Unified Model Provider for Biomimetic AGI

This module provides a clean abstraction layer for model routing:
- Ollama Local: Primary backbone (fast, always available)
- Ollama Cloud: Heavy reasoning (powerful, for complex tasks)
- BitNet Adapter: Future CPU optimization (optional)
- AirLLM: Experimental oversized models (research only)

Architecture:
- Single provider interface: generate(), healthcheck(), list_models()
- Routing logic external to providers
- OpenAI-compatible API support
- Startup warm-up included
"""

import requests
import numpy as np
import math
import time
import logging
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod

# Golden ratio constants
PHI = (1 + math.sqrt(5)) / 2

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(ch)


class ModelProvider(ABC):
    """Abstract base class for all model providers."""
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate text from prompt."""
        pass
    
    @abstractmethod
    def healthcheck(self) -> bool:
        """Check if provider is available."""
        pass
    
    @abstractmethod
    def list_models(self) -> List[str]:
        """List available models."""
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Get provider status."""
        pass


class OllamaLocalProvider(ModelProvider):
    """
    Ollama Local Provider - Primary backbone for biomimetic AGI.
    
    Features:
    - Local API at localhost:11434
    - No authentication required
    - OpenAI-compatible /v1 interface
    - Model listing via /api/tags
    """
    
    def __init__(self, base_url: str = "http://localhost:11434", default_model: str = "llama3.2:1b"):
        self.base_url = base_url
        self.default_model = default_model
        self.available_models = []
        self._warmup_done = False
        self.model_capabilities = {
            "llama3.2:1b": {"stable": True, "thinking": False, "speed": "fast", "status": "primary"},
            "qwen3:1.7b": {"stable": "partial", "thinking": True, "speed": "medium", "status": "secondary"},
            "qwen3.5:2b": {"stable": False, "thinking": True, "speed": "slow", "status": "experimental"}
        }
        
        logger.info(f"Initializing Ollama Local Provider: {base_url}")
        self._warmup()
    
    def _warmup(self):
        """Warm up the provider on startup."""
        try:
            # First check if Ollama is available
            if not self.healthcheck():
                logger.warning("Ollama not available during warmup")
                return
            
            # Warm up the default model with a simple ping
            logger.info(f"Warming up default model: {self.default_model}")
            warmup_result = self.generate("ping", model=self.default_model, max_tokens=1)
            
            if warmup_result['success']:
                self._warmup_done = True
                logger.info("Ollama Local Provider warmed up successfully")
            else:
                logger.warning(f"Model warmup failed: {warmup_result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.warning(f"Warmup failed: {e}")
    
    def generate(self, prompt: str, model: str = None, **kwargs) -> Dict[str, Any]:
        """Generate text using Ollama local API with proper streaming handling."""
        model = model or self.default_model
        
        start_time = time.time()
        
        try:
            # Use /api/chat for better conversational handling
            messages = [
                {"role": "system", "content": "You are a biomimetic neural backbone. Reply concisely."},
                {"role": "user", "content": prompt}
            ]
            
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": False,  # Critical: disable streaming to avoid JSON errors
                    "keep_alive": "10m",  # Keep model loaded
                    "options": kwargs.get('options', {
                        "temperature": 0.8,
                        "top_p": 0.9,
                        "num_predict": kwargs.get('max_tokens', 128)
                    })
                },
                timeout=kwargs.get('timeout', 120)  # Increased for cold starts
            )
            
            response.raise_for_status()
            result = response.json()
            
            generated_text = result.get('message', {}).get('content', '')
            inference_time = time.time() - start_time
            
            return {
                'generated_text': generated_text,
                'inference_time': inference_time,
                'model': model,
                'backend': 'ollama_local',
                'success': True,
                'timestamp': time.time()
            }
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout after {kwargs.get('timeout', 120)}s - model may be loading (cold start)")
            return {
                'generated_text': '',
                'inference_time': time.time() - start_time,
                'model': model,
                'backend': 'ollama_local',
                'success': False,
                'error': f'Timeout: Model cold start exceeded {kwargs.get("timeout", 120)}s',
                'timestamp': time.time()
            }
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Ollama Local generation failed: {e}")
            if '500' in error_msg:
                logger.error("Server error (500) - try: ollama run <model> or check Ollama logs")
            return {
                'generated_text': '',
                'inference_time': time.time() - start_time,
                'model': model,
                'backend': 'ollama_local',
                'success': False,
                'error': error_msg,
                'timestamp': time.time()
            }
    
    def healthcheck(self) -> bool:
        """Check if Ollama local is available."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                self.available_models = [model.get('name', '') for model in models]
                return True
            return False
        except Exception:
            return False
    
    def list_models(self) -> List[str]:
        """List available models in Ollama local."""
        if not self.available_models:
            self.healthcheck()
        return self.available_models
    
    def get_status(self) -> Dict[str, Any]:
        """Get provider status."""
        return {
            'provider': 'ollama_local',
            'base_url': self.base_url,
            'default_model': self.default_model,
            'available': self.healthcheck(),
            'models_count': len(self.available_models),
            'warmup_done': self._warmup_done,
            'phi_constant': PHI
        }
    
    def get_capabilities(self, model_name: str = None) -> Dict[str, Any]:
        """Get capabilities for a specific model or all models."""
        if model_name:
            return self.model_capabilities.get(model_name, {"stable": False, "thinking": False, "speed": "unknown", "status": "unknown"})
        
        # Return capabilities for all known models
        return self.model_capabilities


class OllamaCloudProvider(ModelProvider):
    """
    Ollama Cloud Provider - Heavy reasoning and validation.
    
    Features:
    - Cloud-based powerful models
    - OpenAI-compatible /v1 interface
    - Authentication via local sign-in or API keys
    """
    
    def __init__(self, base_url: str = "https://api.ollama.cloud", default_model: str = "claude-code"):
        self.base_url = base_url
        self.default_model = default_model
        self.available_models = []
        
        logger.info(f"Initializing Ollama Cloud Provider: {base_url}")
    
    def generate(self, prompt: str, model: str = None, **kwargs) -> Dict[str, Any]:
        """Generate text using Ollama Cloud API."""
        model = model or self.default_model
        
        start_time = time.time()
        
        try:
            # Use OpenAI-compatible interface
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": kwargs.get('max_tokens', 128),
                    "temperature": kwargs.get('temperature', 0.8)
                },
                timeout=kwargs.get('timeout', 60),
                verify=kwargs.get('verify_ssl', True)
            )
            
            response.raise_for_status()
            result = response.json()
            
            generated_text = result['choices'][0]['message']['content']
            inference_time = time.time() - start_time
            
            return {
                'generated_text': generated_text,
                'inference_time': inference_time,
                'model': model,
                'backend': 'ollama_cloud',
                'success': True,
                'timestamp': time.time()
            }
            
        except Exception as e:
            logger.error(f"Ollama Cloud generation failed: {e}")
            return {
                'generated_text': '',
                'inference_time': time.time() - start_time,
                'model': model,
                'backend': 'ollama_cloud',
                'success': False,
                'error': str(e),
                'timestamp': time.time()
            }
    
    def healthcheck(self) -> bool:
        """Check if Ollama Cloud is available."""
        try:
            response = requests.get(f"{self.base_url}/v1/models", timeout=10)
            if response.status_code == 200:
                models = response.json().get('data', [])
                self.available_models = [model.get('id', '') for model in models]
                return True
            return False
        except Exception:
            return False
    
    def list_models(self) -> List[str]:
        """List available models in Ollama Cloud."""
        if not self.available_models:
            self.healthcheck()
        return self.available_models
    
    def get_status(self) -> Dict[str, Any]:
        """Get provider status."""
        return {
            'provider': 'ollama_cloud',
            'base_url': self.base_url,
            'default_model': self.default_model,
            'available': self.healthcheck(),
            'models_count': len(self.available_models),
            'phi_constant': PHI
        }


class BitNetAdapter(ModelProvider):
    """
    BitNet Adapter - Future CPU-optimized backbone (optional).
    
    This is a placeholder for future BitNet integration.
    Currently disabled by default - enable when you have stable builds.
    """
    
    def __init__(self, model_path: str = "D:\\MODELS\\bitnet-b1.58-2B-4T-i2_s.gguf"):
        self.model_path = model_path
        self.available = False
        self.model = None
        
        logger.info(f"Initializing BitNet Adapter (optional): {model_path}")
        logger.warning("BitNet is currently disabled - enable when ready")
    
    def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate text using BitNet (placeholder)."""
        return {
            'generated_text': 'BitNet adapter not yet enabled',
            'inference_time': 0,
            'model': 'bitnet',
            'backend': 'bitnet',
            'success': False,
            'error': 'BitNet adapter not enabled',
            'timestamp': time.time()
        }
    
    def healthcheck(self) -> bool:
        """Check if BitNet is available."""
        return self.available
    
    def list_models(self) -> List[str]:
        """List available BitNet models."""
        return ['bitnet-b1.58-2B-4T'] if self.available else []
    
    def get_status(self) -> Dict[str, Any]:
        """Get provider status."""
        return {
            'provider': 'bitnet',
            'model_path': self.model_path,
            'available': False,
            'enabled': False,
            'phi_constant': PHI
        }


class AirLLMExperimental(ModelProvider):
    """
    AirLLM Experimental - Oversized local models (research only).
    
    This is for research when you need to run models that don't fit in memory.
    Not recommended for production use.
    """
    
    def __init__(self):
        self.available = False
        logger.info("Initializing AirLLM Experimental (research only)")
        logger.warning("AirLLM is experimental - not for production")
    
    def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate text using AirLLM (placeholder)."""
        return {
            'generated_text': 'AirLLM experimental not enabled',
            'inference_time': 0,
            'model': 'airllm',
            'backend': 'airllm_experimental',
            'success': False,
            'error': 'AirLLM not enabled',
            'timestamp': time.time()
        }
    
    def healthcheck(self) -> bool:
        """Check if AirLLM is available."""
        return self.available
    
    def list_models(self) -> List[str]:
        """List available AirLLM models."""
        return []
    
    def get_status(self) -> Dict[str, Any]:
        """Get provider status."""
        return {
            'provider': 'airllm_experimental',
            'available': False,
            'enabled': False,
            'phi_constant': PHI
        }


class ModelRouter:
    """
    Model Router - Routes requests to appropriate provider.
    
    Routing Rules:
    - Default: Ollama Local (fast, always available)
    - Scientific validation: Ollama Cloud
    - Deep code review: Ollama Cloud
    - Complex planning: Ollama Cloud
    - Quick tasks: Ollama Local small model
    """
    
    def __init__(self):
        # Initialize providers
        self.providers = {
            'ollama_local': OllamaLocalProvider(default_model="llama3.2:1b"),  # Use working model
            'ollama_cloud': OllamaCloudProvider(default_model="claude-code"),
            'bitnet': BitNetAdapter(),  # Disabled by default
            'airllm': AirLLMExperimental()  # Disabled by default
        }
        
        # Routing rules
        self.routing_rules = {
            'scientific_validation': 'ollama_cloud',
            'deep_code_review': 'ollama_cloud',
            'complex_planning': 'ollama_cloud',
            'research_synthesis': 'ollama_cloud',
            'default': 'ollama_local',
            'quick_task': 'ollama_local',
            'consciousness_processing': 'ollama_local'
        }
        
        logger.info("Model Router initialized")
        logger.info(f"Default provider: {self.routing_rules['default']}")
        logger.info(f"Available providers: {list(self.providers.keys())}")
    
    def get_provider(self, task_type: str = 'default') -> ModelProvider:
        """Get appropriate provider for task type."""
        provider_name = self.routing_rules.get(task_type, 'default')
        return self.providers.get(provider_name, self.providers['ollama_local'])
    
    def generate(self, prompt: str, task_type: str = 'default', **kwargs) -> Dict[str, Any]:
        """Generate text using routed provider."""
        provider = self.get_provider(task_type)
        return provider.generate(prompt, **kwargs)
    
    def healthcheck_all(self) -> Dict[str, bool]:
        """Check health of all providers."""
        return {
            name: provider.healthcheck()
            for name, provider in self.providers.items()
        }
    
    def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all providers."""
        return {
            name: provider.get_status()
            for name, provider in self.providers.items()
        }


# Convenience functions
def generate_biomimetic_thought(prompt: str, phi_resonance: float = PHI, model: str = None, router: 'ModelRouter' = None, **kwargs) -> Dict[str, Any]:
    """Generate biomimetic thought using routed provider.
    
    Pass an existing `router` instance to avoid re-initialization overhead.
    """
    if router is None:
        router = ModelRouter()
    
    # Add phi context to prompt
    biomimetic_prompt = f"Biomimetic State: Phi={phi_resonance:.6f}. Consciousness Input: {prompt}\n\nGenerate a coherent thought that demonstrates biomimetic intelligence:"
    
    # Pass model parameter if specified
    generate_kwargs = {'task_type': 'consciousness_processing'}
    if model:
        generate_kwargs['model'] = model
    generate_kwargs.update(kwargs)
    
    result = router.generate(biomimetic_prompt, **generate_kwargs)
    
    # Calculate consciousness metrics
    if result.get('success'):
        text = result['generated_text']
        text_length = len(text.split())
        phi_alignment = 1.0 - abs(text_length / 128 - 1/PHI) / (1/PHI)
        
        result['phi_coherence'] = phi_alignment
        result['phi_resonance'] = phi_resonance
        result['biomimetic_resonance'] = phi_resonance * phi_alignment
    
    return result


def get_quick_thought(prompt: str, router: 'ModelRouter' = None) -> str:
    """Generate quick thought using local model."""
    if router is None:
        router = ModelRouter()
    result = router.generate(prompt, task_type='quick_task')
    return result.get('generated_text', '')


def get_deep_reasoning(prompt: str) -> str:
    """Generate deep reasoning using cloud model."""
    router = ModelRouter()
    result = router.generate(prompt, task_type='complex_planning')
    return result.get('generated_text', '')


if __name__ == "__main__":
    # Demo the unified model provider
    print("Unified Model Provider Demo")
    print("=" * 60)
    
    # Initialize router
    router = ModelRouter()
    
    # Check provider health
    print("\nProvider Health:")
    health = router.healthcheck_all()
    for provider, status in health.items():
        print(f"  {provider}: {'✓' if status else '✗'}")
    
    # Get all status
    print("\nProvider Status:")
    status = router.get_all_status()
    for provider, info in status.items():
        print(f"\n{provider}:")
        for key, value in info.items():
            print(f"  {key}: {value}")
    
    # Test generation
    print("\n" + "=" * 60)
    print("Testing Generation:")
    
    test_prompt = "What is the nature of consciousness?"
    print(f"\nPrompt: {test_prompt}")
    
    # Local generation
    print("\nLocal (qwen3.5:2b):")
    result = router.generate(test_prompt, task_type='default')
    if result.get('success'):
        print(f"  Generated: {result['generated_text'][:100]}...")
        print(f"  Time: {result['inference_time']:.3f}s")
    else:
        print(f"  Failed: {result.get('error', 'Unknown error')}")
    
    # Cloud generation
    print("\nCloud (claude-code):")
    result = router.generate(test_prompt, task_type='complex_planning')
    if result.get('success'):
        print(f"  Generated: {result['generated_text'][:100]}...")
        print(f"  Time: {result['inference_time']:.3f}s")
    else:
        print(f"  Failed: {result.get('error', 'Unknown error')}")
    
    print("\nDemo complete!")
