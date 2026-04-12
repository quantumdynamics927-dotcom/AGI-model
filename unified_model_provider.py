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
from typing import Dict, Any, List, Optional, Tuple
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

# Golden ratio constants
PHI = (1 + math.sqrt(5)) / 2


class FailureClass(Enum):
    """Failure classification for provider errors."""
    NONE = "none"
    PROVIDER_UNAVAILABLE_TLS = "provider_unavailable_tls"
    PROVIDER_UNAVAILABLE_TIMEOUT = "provider_unavailable_timeout"
    PROVIDER_UNAVAILABLE_CONNECTION = "provider_unavailable_connection"
    PROVIDER_UNAVAILABLE_AUTH = "provider_unavailable_auth"
    MODEL_LOAD_FAILED = "model_load_failed"
    GENERATION_FAILED = "generation_failed"
    RATE_LIMITED = "rate_limited"
    UNKNOWN = "unknown"


@dataclass
class ProviderHealthDetail:
    """Detailed provider health status with failure tracking."""
    available: bool = False
    failure_class: FailureClass = FailureClass.NONE
    last_error_at: Optional[datetime] = None
    last_error_msg: str = ""
    retry_after_s: float = 0.0
    cooldown_until: Optional[datetime] = None
    consecutive_failures: int = 0
    
    def should_retry(self) -> bool:
        """Check if provider is ready to retry after cooldown."""
        if not self.cooldown_until:
            return True
        return datetime.now() >= self.cooldown_until
    
    def mark_failure(self, failure_class: FailureClass, error_msg: str, cooldown_seconds: float = 60.0):
        """Mark a failure and set cooldown."""
        self.failure_class = failure_class
        self.last_error_at = datetime.now()
        self.last_error_msg = error_msg
        self.consecutive_failures += 1
        self.available = False
        
        # Exponential backoff for cooldown
        backoff_multiplier = min(2 ** (self.consecutive_failures - 1), 8)  # Cap at 8x
        cooldown_seconds = cooldown_seconds * backoff_multiplier
        self.cooldown_until = datetime.now() + timedelta(seconds=cooldown_seconds)
        self.retry_after_s = cooldown_seconds
    
    def mark_success(self):
        """Mark a successful operation."""
        self.failure_class = FailureClass.NONE
        self.last_error_at = None
        self.last_error_msg = ""
        self.consecutive_failures = 0
        self.available = True
        self.cooldown_until = None
        self.retry_after_s = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for status reporting."""
        return {
            'available': self.available,
            'failure_class': self.failure_class.value,
            'last_error_at': self.last_error_at.isoformat() if self.last_error_at else None,
            'last_error_msg': self.last_error_msg[:200] if self.last_error_msg else "",
            'retry_after_s': self.retry_after_s,
            'cooldown_until': self.cooldown_until.isoformat() if self.cooldown_until else None,
            'consecutive_failures': self.consecutive_failures,
            'should_retry': self.should_retry(),
        }

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
            
            # qwen3 thinking models use <think> blocks that consume tokens;
            # disable thinking mode so all tokens go to the visible response.
            is_thinking_model = 'qwen3' in model.lower()
            request_body = {
                "model": model,
                "messages": messages,
                "stream": False,  # Critical: disable streaming to avoid JSON errors
                "keep_alive": "10m",  # Keep model loaded
                "options": kwargs.get('options', {
                    "temperature": 0.8,
                    "top_p": 0.9,
                    "num_predict": kwargs.get('max_tokens', 512)
                })
            }
            if is_thinking_model:
                request_body["think"] = False  # Ollama >=0.7: suppress <think> blocks

            response = requests.post(
                f"{self.base_url}/api/chat",
                json=request_body,
                timeout=kwargs.get('timeout', 120)  # Increased for cold starts
            )

            response.raise_for_status()
            result = response.json()

            generated_text = result.get('message', {}).get('content', '')
            # Strip any residual <think>...</think> blocks that may appear in older Ollama builds
            import re as _re
            generated_text = _re.sub(r'<think>.*?</think>', '', generated_text, flags=_re.DOTALL).strip()
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
    - Automatic failure classification and cooldown
    """
    
    def __init__(self, base_url: str = "https://api.ollama.cloud", default_model: str = "claude-code"):
        self.base_url = base_url
        self.default_model = default_model
        self.available_models = []
        self.health_detail = ProviderHealthDetail()
        
        logger.info(f"Initializing Ollama Cloud Provider: {base_url}")
    
    def _classify_failure(self, error: Exception) -> FailureClass:
        """Classify failure type from exception."""
        error_str = str(error).lower()
        
        # SSL/TLS certificate errors
        if 'ssl' in error_str or 'certificate' in error_str or 'cert' in error_str:
            if 'expired' in error_str:
                return FailureClass.PROVIDER_UNAVAILABLE_TLS
            elif 'verify' in error_str:
                return FailureClass.PROVIDER_UNAVAILABLE_TLS
            else:
                return FailureClass.PROVIDER_UNAVAILABLE_TLS
        
        # Timeout errors
        if 'timeout' in error_str or 'timed out' in error_str:
            return FailureClass.PROVIDER_UNAVAILABLE_TIMEOUT
        
        # Connection errors
        if 'connection' in error_str or 'connect' in error_str:
            return FailureClass.PROVIDER_UNAVAILABLE_CONNECTION
        
        # Authentication errors
        if '401' in error_str or '403' in error_str or 'auth' in error_str:
            return FailureClass.PROVIDER_UNAVAILABLE_AUTH
        
        # Rate limiting
        if '429' in error_str or 'rate' in error_str:
            return FailureClass.RATE_LIMITED
        
        return FailureClass.UNKNOWN
    
    def generate(self, prompt: str, model: str = None, **kwargs) -> Dict[str, Any]:
        """Generate text using Ollama Cloud API with failure classification."""
        model = model or self.default_model
        
        # Check if provider is in cooldown
        if not self.health_detail.should_retry():
            logger.warning(f"Ollama Cloud in cooldown until {self.health_detail.cooldown_until}")
            return {
                'generated_text': '',
                'inference_time': 0,
                'model': model,
                'backend': 'ollama_cloud',
                'success': False,
                'error': f'Provider in cooldown: {self.health_detail.failure_class.value}',
                'failure_class': self.health_detail.failure_class.value,
                'retry_after_s': self.health_detail.retry_after_s,
                'timestamp': time.time()
            }
        
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
            
            # Mark success
            self.health_detail.mark_success()
            
            return {
                'generated_text': generated_text,
                'inference_time': inference_time,
                'model': model,
                'backend': 'ollama_cloud',
                'success': True,
                'timestamp': time.time()
            }
            
        except Exception as e:
            # Classify failure
            failure_class = self._classify_failure(e)
            error_msg = str(e)
            
            # Determine cooldown based on failure type
            cooldown_map = {
                FailureClass.PROVIDER_UNAVAILABLE_TLS: 300.0,  # 5 minutes for SSL issues
                FailureClass.PROVIDER_UNAVAILABLE_TIMEOUT: 60.0,  # 1 minute for timeouts
                FailureClass.PROVIDER_UNAVAILABLE_CONNECTION: 120.0,  # 2 minutes for connection issues
                FailureClass.PROVIDER_UNAVAILABLE_AUTH: 600.0,  # 10 minutes for auth issues
                FailureClass.RATE_LIMITED: 120.0,  # 2 minutes for rate limits
                FailureClass.UNKNOWN: 60.0,  # 1 minute default
            }
            
            cooldown_seconds = cooldown_map.get(failure_class, 60.0)
            self.health_detail.mark_failure(failure_class, error_msg, cooldown_seconds)
            
            logger.error(f"Ollama Cloud generation failed [{failure_class.value}]: {e}")
            logger.info(f"Provider demoted for {cooldown_seconds}s cooldown")
            
            return {
                'generated_text': '',
                'inference_time': time.time() - start_time,
                'model': model,
                'backend': 'ollama_cloud',
                'success': False,
                'error': error_msg,
                'failure_class': failure_class.value,
                'retry_after_s': self.health_detail.retry_after_s,
                'timestamp': time.time()
            }
    
    def healthcheck(self) -> bool:
        """Check if Ollama Cloud is available."""
        # Check cooldown first
        if not self.health_detail.should_retry():
            return False
        
        try:
            response = requests.get(f"{self.base_url}/v1/models", timeout=10)
            if response.status_code == 200:
                models = response.json().get('data', [])
                self.available_models = [model.get('id', '') for model in models]
                self.health_detail.mark_success()
                return True
            return False
        except Exception as e:
            failure_class = self._classify_failure(e)
            self.health_detail.mark_failure(failure_class, str(e), 60.0)
            return False
    
    def list_models(self) -> List[str]:
        """List available models in Ollama Cloud."""
        if not self.available_models:
            self.healthcheck()
        return self.available_models
    
    def get_status(self) -> Dict[str, Any]:
        """Get provider status with health details."""
        return {
            'provider': 'ollama_cloud',
            'base_url': self.base_url,
            'default_model': self.default_model,
            'available': self.health_detail.available,
            'models_count': len(self.available_models),
            'phi_constant': PHI,
            'health_detail': self.health_detail.to_dict()
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
    - Scientific validation: Ollama Cloud (with fallback)
    - Deep code review: Ollama Cloud (with fallback)
    - Complex planning: Ollama Cloud (with fallback)
    - Quick tasks: Ollama Local small model
    - Automatic fallback to local when cloud fails
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
        
        # Fallback chain: cloud tasks fall back to local
        self.fallback_chain = {
            'ollama_cloud': 'ollama_local',
            'bitnet': 'ollama_local',
            'airllm': 'ollama_local',
            'ollama_local': None  # No fallback for local
        }
        
        logger.info("Model Router initialized")
        logger.info(f"Default provider: {self.routing_rules['default']}")
        logger.info(f"Available providers: {list(self.providers.keys())}")
    
    def get_provider(self, task_type: str = 'default') -> ModelProvider:
        """Get appropriate provider for task type."""
        provider_name = self.routing_rules.get(task_type, 'default')
        return self.providers.get(provider_name, self.providers['ollama_local'])
    
    def generate(self, prompt: str, task_type: str = 'default', **kwargs) -> Dict[str, Any]:
        """Generate text using routed provider with automatic fallback."""
        provider_name = self.routing_rules.get(task_type, 'default')
        provider = self.providers.get(provider_name, self.providers['ollama_local'])
        
        # Try primary provider
        result = provider.generate(prompt, **kwargs)
        
        # Check if we should fallback
        if not result.get('success', False):
            failure_class = result.get('failure_class', 'unknown')
            
            # Fallback for cloud failures
            if provider_name in ['ollama_cloud', 'bitnet', 'airllm']:
                fallback_provider_name = self.fallback_chain.get(provider_name)
                
                if fallback_provider_name and fallback_provider_name in self.providers:
                    logger.warning(f"Falling back from {provider_name} to {fallback_provider_name} due to {failure_class}")
                    
                    fallback_provider = self.providers[fallback_provider_name]
                    fallback_result = fallback_provider.generate(prompt, **kwargs)
                    
                    # Add fallback metadata
                    fallback_result['fallback_from'] = provider_name
                    fallback_result['fallback_reason'] = failure_class
                    fallback_result['original_error'] = result.get('error', '')
                    
                    return fallback_result
        
        return result
    
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
def generate_biomimetic_thought(prompt: str, phi_resonance: float = PHI, model: str = None, router: 'ModelRouter' = None, enable_advanced_reasoning: bool = False, **kwargs) -> Dict[str, Any]:
    """Generate biomimetic thought using routed provider.
    
    Pass an existing `router` instance to avoid re-initialization overhead.
    
    Args:
        prompt: Input prompt for generation
        phi_resonance: Golden ratio resonance target (default: PHI)
        model: Specific model to use (optional)
        router: Existing ModelRouter instance (optional)
        enable_advanced_reasoning: Enable chain-of-thought reasoning (default: False)
        **kwargs: Additional generation parameters
        
    Returns:
        Dict with generated text and consciousness metrics
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
    
    # Use advanced reasoning if enabled
    if enable_advanced_reasoning:
        try:
            from consciousness_reasoning_engine import ConsciousnessReasoningEngine
            
            # Create reasoning engine with current router
            reasoning_engine = ConsciousnessReasoningEngine(
                model_provider=router.providers.get('ollama_local'),
                max_depth=kwargs.get('max_reasoning_depth', 3),
                phi_target=phi_resonance
            )
            
            # Execute chain-of-thought reasoning
            reasoning_result = reasoning_engine.reason(
                prompt=biomimetic_prompt,
                reasoning_type="chain_of_thought"
            )
            
            # Extract result
            result = {
                'generated_text': reasoning_result.get('final_conclusion', ''),
                'success': reasoning_result.get('success', False),
                'reasoning_steps': reasoning_result.get('reasoning_steps', []),
                'phi_coherence': reasoning_result.get('phi_coherence', 0.0),
                'phi_resonance': phi_resonance,
                'biomimetic_resonance': phi_resonance * reasoning_result.get('phi_alignment', 0.0),
                'inference_time': reasoning_result.get('inference_time', 0.0),
                'backend': 'advanced_reasoning',
                'model': model or router.providers.get('ollama_local', {}).default_model if hasattr(router, 'providers') else 'unknown'
            }
            
            return result
            
        except ImportError:
            logger.warning("Advanced reasoning requested but consciousness_reasoning_engine not available")
            # Fall through to standard generation
    
    # Standard generation
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
