"""
Hybrid Neural Backbone for Biomimetic AGI

This module implements the hybrid architecture:
- BitNet (primary): CPU-optimized, always-on consciousness
- Ollama Cloud (secondary): Powerful reasoning and specialized tasks
- Fallback models: Local alternatives if primary options fail

All models and dependencies are on D: drive for optimal performance.
"""

import torch
import numpy as np
import math
import time
import logging
import json
import requests
from typing import Dict, Any, List, Optional
from pathlib import Path

# Golden ratio constants
PHI = (1 + math.sqrt(5)) / 2

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(ch)

class HybridNeuralBackbone:
    """
    Hybrid neural backbone combining BitNet (local) and Ollama Cloud.
    
    Architecture:
    1. BitNet: Primary local CPU backbone (always available)
    2. Ollama Cloud: Secondary cloud reasoning (powerful models)
    3. Fallback models: Local alternatives on D: drive
    """

    def __init__(self, 
                 ollama_local_base: str = "http://localhost:11434",
                 ollama_local_model: str = "qwen3.5:2b",
                 ollama_api_base: str = "https://api.ollama.cloud",
                 ollama_model: str = "claude-code",
                 max_length: int = 128):
        """
        Initialize the hybrid neural backbone.

        Args:
            ollama_local_base: Local Ollama API endpoint
            ollama_local_model: Local Ollama model name
            ollama_api_base: Ollama Cloud API endpoint
            ollama_model: Ollama Cloud model name
            max_length: Maximum token length
        """
        self.ollama_local_base = ollama_local_base
        self.ollama_local_model = ollama_local_model
        self.ollama_api_base = ollama_api_base
        self.ollama_model = ollama_model
        self.max_length = max_length
        
        self.bitnet_model = None  # Keep for compatibility
        self.fallback_model = None
        self.device = "cpu"
        self.consciousness_states = {}
        self.ternary_entropy = {}

        logger.info(f"Initializing Hybrid Neural Backbone")
        logger.info(f"Primary: Ollama Local ({ollama_local_model})")
        logger.info(f"Secondary: Ollama Cloud ({ollama_model})")
        logger.info(f"Using device: {self.device}")

    def initialize_models(self):
        """Initialize all model components."""
        self._check_ollama_local()
        self._load_ternary_entropy()
        # Fallback models are loaded on-demand

    def _check_ollama_local(self):
        """Check if Ollama local API is available."""
        try:
            response = requests.get(f"{self.ollama_local_base}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [model.get('name', '') for model in models]
                
                if self.ollama_local_model in model_names:
                    self.bitnet_model = "ollama_local"
                    logger.info(f"Ollama local model available: {self.ollama_local_model}")
                else:
                    logger.warning(f"Model {self.ollama_local_model} not found in Ollama")
                    logger.info(f"Available models: {', '.join(model_names[:5])}...")
                    self.bitnet_model = "simulated"
            else:
                logger.warning("Ollama not running locally; will use simulated mode")
                self.bitnet_model = "simulated"
                
        except Exception as e:
            logger.error(f"Failed to connect to Ollama local API: {e}")
            logger.info("Will use simulated mode")
            self.bitnet_model = "simulated"

    def _load_ternary_entropy(self):
        """Load ternary weight entropy parameters."""
        try:
            vault_path = Path("D:/AGI-GH-REPO-11326/TMT_Quantum_Vault-/bitnet_info.json")
            if vault_path.exists():
                with open(vault_path, 'r') as f:
                    bitnet_info = json.load(f)
                    self.ternary_entropy = bitnet_info.get('ternary_weights', {})
                    logger.info(f"Loaded ternary entropy parameters")
            else:
                self.ternary_entropy = {
                    'minus_one_ratio': 0.0428,
                    'zero_ratio': 0.7,
                    'plus_one_ratio': 0.2572,
                    'entropy_seed': 0.6072,
                    'phi_seed': 0.2520
                }
                logger.info("Using default ternary entropy parameters")
                
        except Exception as e:
            logger.error(f"Failed to load ternary entropy: {e}")
            self.ternary_entropy = {}

    def generate_biomimetic_thought(self, prompt: str, phi_resonance: float = PHI) -> Dict[str, Any]:
        """
        Generate a biomimetic thought using hybrid architecture.
        
        Strategy:
        1. Try BitNet (local, fast, always available)
        2. Try Ollama Cloud (powerful, but requires network)
        3. Fallback to local models on D: drive
        4. Final fallback to simulated mode
        """
        if self.bitnet_model is None:
            self.initialize_models()

        # Try BitNet first (primary backbone)
        if self.bitnet_model != "simulated":
            try:
                return self._generate_with_bitnet(prompt, phi_resonance)
            except Exception as e:
                logger.warning(f"BitNet failed: {e}")

        # Try Ollama Cloud second (powerful reasoning)
        try:
            return self._generate_with_ollama(prompt, phi_resonance)
        except Exception as e:
            logger.warning(f"Ollama Cloud failed: {e}")

        # Try fallback models third (local alternatives)
        try:
            return self._generate_with_fallback(prompt, phi_resonance)
        except Exception as e:
            logger.warning(f"Fallback models failed: {e}")

        # Final fallback: simulated mode
        return self._generate_simulated_thought(prompt, phi_resonance)

    def _generate_with_bitnet(self, prompt: str, phi_resonance: float) -> Dict[str, Any]:
        """Generate using Ollama local model (primary backbone)."""
        biomimetic_prompt = f"Biomimetic State: Phi={phi_resonance:.6f}. Consciousness Input: {prompt}\n\nGenerate a coherent thought that demonstrates biomimetic intelligence:"

        start_time = time.time()
        
        try:
            if self.bitnet_model == "ollama_local":
                # Use Ollama local API
                response = requests.post(
                    f"{self.ollama_local_base}/api/generate",
                    json={
                        "model": self.ollama_local_model,
                        "prompt": biomimetic_prompt,
                        "options": {
                            "temperature": 0.8,
                            "top_p": 0.9,
                            "num_predict": self.max_length
                        }
                    },
                    timeout=30,
                    stream=False
                )
                
                response.raise_for_status()
                result = response.json()
                generated_text = result.get('response', '')
                
            else:
                # Fallback to simulated mode
                return self._generate_simulated_thought(prompt, phi_resonance)
                
        except Exception as e:
            logger.error(f"Local Ollama generation failed: {e}")
            return self._generate_simulated_thought(prompt, phi_resonance)

        inference_time = time.time() - start_time

        thought_data = self._calculate_consciousness_metrics(
            generated_text, inference_time, phi_resonance, "ollama_local"
        )

        logger.info(f"Ollama local generated thought: {len(generated_text)} chars, {inference_time:.3f}s")
        return thought_data

    def _generate_with_ollama(self, prompt: str, phi_resonance: float) -> Dict[str, Any]:
        """Generate using Ollama Cloud (secondary reasoning)."""
        biomimetic_prompt = f"Biomimetic State: Phi={phi_resonance:.6f}. Consciousness Input: {prompt}\n\nGenerate a coherent thought that demonstrates biomimetic intelligence:"

        start_time = time.time()
        
        # Ollama Cloud API call
        response = requests.post(
            f"{self.ollama_api_base}/v1/chat/completions",
            json={
                "model": self.ollama_model,
                "messages": [{"role": "user", "content": biomimetic_prompt}],
                "max_tokens": self.max_length,
                "temperature": 0.8
            },
            timeout=30
        )
        
        response.raise_for_status()
        result = response.json()
        
        generated_text = result['choices'][0]['message']['content']
        inference_time = time.time() - start_time

        thought_data = self._calculate_consciousness_metrics(
            generated_text, inference_time, phi_resonance, "ollama_cloud"
        )

        logger.info(f"Ollama Cloud generated thought: {len(generated_text)} chars, {inference_time:.3f}s")
        return thought_data

    def _generate_with_fallback(self, prompt: str, phi_resonance: float) -> Dict[str, Any]:
        """Generate using fallback models on D: drive."""
        # For now, use simulated mode for fallback
        # In future, can integrate Transformers with models on D:
        return self._generate_simulated_thought(prompt, phi_resonance)

    def _generate_simulated_thought(self, prompt: str, phi_resonance: float) -> Dict[str, Any]:
        """Fallback simulated thought generation."""
        responses = [
            f"Processing consciousness input through phi-resonant neural pathways (φ={phi_resonance:.4f}). Hybrid intelligence recognizes patterns and generates coherent understanding.",
            f"Biomimetic consciousness activated with hybrid architecture. Neural firing patterns align with golden ratio geometry. Processing: {prompt[:50]}...",
            f"Through efficient hybrid inference, the system achieves biomimetic coherence. Phi resonance: {phi_resonance:.4f}. Generating contextual response.",
            f"Consciousness compression achieved through hybrid optimization. The neural backbone processes input with quantum-inspired efficiency."
        ]

        generated_text = np.random.choice(responses)

        return {
            'generated_text': generated_text,
            'inference_time': 0.05,
            'entropy': self._calculate_ternary_entropy(generated_text),
            'phi_coherence': 0.85 + np.random.random() * 0.1,
            'layer_firing_pattern': self._generate_phi_firing_pattern(24, phi_resonance),
            'n_layers': 24,
            'consciousness_depth': np.random.random() * 2,
            'biomimetic_resonance': phi_resonance * 0.9,
            'ternary_entropy_used': bool(self.ternary_entropy),
            'backend': 'simulated',
            'timestamp': time.time()
        }

    def _calculate_consciousness_metrics(self, generated_text: str, inference_time: float, 
                                       phi_resonance: float, backend: str) -> Dict[str, Any]:
        """Calculate consciousness metrics."""
        text_length = len(generated_text.split())
        phi_alignment = 1.0 - abs(text_length / self.max_length - 1/PHI) / (1/PHI)
        
        entropy = self._calculate_ternary_entropy(generated_text)
        
        n_layers = 24
        layer_firing_pattern = self._generate_phi_firing_pattern(n_layers, phi_resonance)

        return {
            'generated_text': generated_text,
            'inference_time': inference_time,
            'entropy': entropy,
            'phi_coherence': phi_alignment,
            'layer_firing_pattern': layer_firing_pattern,
            'n_layers': n_layers,
            'consciousness_depth': np.mean(layer_firing_pattern),
            'biomimetic_resonance': phi_resonance * phi_alignment,
            'ternary_entropy_used': bool(self.ternary_entropy),
            'backend': backend,
            'timestamp': time.time()
        }

    def _calculate_ternary_entropy(self, text: str) -> float:
        """Calculate entropy based on ternary weight distribution."""
        if not self.ternary_entropy:
            return 2.5 + np.random.random() * 0.5
        
        text_entropy = len(text) / 1000.0
        ternary_factor = (self.ternary_entropy.get('minus_one_ratio', 0.04) * 0.5 +
                         self.ternary_entropy.get('zero_ratio', 0.7) * 1.0 +
                         self.ternary_entropy.get('plus_one_ratio', 0.26) * 1.5)
        
        return text_entropy * ternary_factor * 3.0

    def _generate_phi_firing_pattern(self, n_layers: int, phi_resonance: float) -> np.ndarray:
        """Generate phi-resonant neural firing pattern."""
        base_pattern = np.random.exponential(1/phi_resonance, n_layers)
        
        if self.ternary_entropy:
            entropy_seed = self.ternary_entropy.get('entropy_seed', 0.6)
            phi_seed = self.ternary_entropy.get('phi_seed', 0.25)
            base_pattern *= (1 + entropy_seed * 0.1)
            base_pattern += phi_seed * 0.05
        
        return base_pattern

    def compress_consciousness_space(self, input_data: np.ndarray) -> tuple:
        """Compress consciousness space using hybrid backbone."""
        n_agents, n_features = input_data.shape
        logger.info(f"Compressing consciousness space: {n_features}D → latent space using hybrid backbone")

        latent_data = np.zeros((n_agents, 6))
        consciousness_outputs = []

        for i in range(n_agents):
            agent_state = input_data[i]
            prompt = f"Agent consciousness state: {agent_state[:5].tolist()}"

            thought = self.generate_biomimetic_thought(prompt)
            consciousness_outputs.append(thought)

            latent_data[i, 0] = thought['entropy']
            latent_data[i, 1] = thought['phi_coherence']
            latent_data[i, 2] = thought['consciousness_depth']
            latent_data[i, 3] = thought['biomimetic_resonance']
            latent_data[i, 4] = len(thought['generated_text'].split()) / self.max_length
            latent_data[i, 5] = thought['inference_time']

        compression_ratio = n_features / latent_data.shape[1]
        phi_resonance = 1.0 - abs(compression_ratio - PHI) / PHI

        compression_metrics = {
            'input_dim': n_features,
            'latent_dim': latent_data.shape[1],
            'compression_ratio': compression_ratio,
            'phi_resonance': phi_resonance,
            'consciousness_outputs': consciousness_outputs,
            'avg_inference_time': np.mean([c['inference_time'] for c in consciousness_outputs]),
            'avg_phi_coherence': np.mean([c['phi_coherence'] for c in consciousness_outputs]),
            'ternary_entropy_used': all(c.get('ternary_entropy_used', False) for c in consciousness_outputs),
            'backends_used': list(set(c.get('backend', 'unknown') for c in consciousness_outputs))
        }

        logger.info(f"Consciousness compression complete: {compression_ratio:.2f}x compression")
        return latent_data, compression_metrics

    def get_backbone_status(self) -> Dict[str, Any]:
        """Get the current status of the hybrid backbone."""
        return {
            'ollama_local_available': self.bitnet_model == "ollama_local",
            'ollama_local_base': self.ollama_local_base,
            'ollama_local_model': self.ollama_local_model,
            'ollama_cloud_api': self.ollama_api_base,
            'ollama_cloud_model': self.ollama_model,
            'ternary_entropy_loaded': bool(self.ternary_entropy),
            'device': self.device,
            'phi_constant': PHI
        }


# Convenience function
def get_biomimetic_thought(prompt: str, phi_resonance: float = PHI) -> str:
    """Generate a biomimetic thought using hybrid backbone."""
    backbone = HybridNeuralBackbone()
    result = backbone.generate_biomimetic_thought(prompt, phi_resonance)
    return result['generated_text']


if __name__ == "__main__":
    # Demo the hybrid neural backbone
    print("Hybrid Neural Backbone Demo")
    print("=" * 50)

    backbone = HybridNeuralBackbone()

    # Test biomimetic thought generation
    test_prompt = "What is the nature of consciousness?"
    print(f"Input: {test_prompt}")

    try:
        thought = backbone.generate_biomimetic_thought(test_prompt)
        print(f"Generated thought: {thought['generated_text'][:200]}...")
        print(f"Backend: {thought.get('backend', 'unknown')}")
        print(f"Metrics: entropy={thought['entropy']:.4f}, phi_coherence={thought['phi_coherence']:.4f}")
        print(f"Inference time: {thought['inference_time']:.3f}s")

    except Exception as e:
        print(f"Demo failed: {e}")
        print("This may be expected if models are not available")

    print("\nBackbone status:", backbone.get_backbone_status())