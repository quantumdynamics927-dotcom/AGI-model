#!/usr/bin/env python3
"""
Consciousness Emergence Validation Framework
=============================================

Systematic testing framework for validating consciousness emergence metrics
across multiple runs, models, and prompt conditions.

Validates whether phi resonance ≈ 1.618 is a reproducible behavioral signature
or prompt-sensitive style imitation.

Usage:
    python consciousness_validation_framework.py --runs 50 --prompt-family emergence

Output:
    - Generation logs with metric vectors
    - Variance analysis across runs
    - Model comparison (Ollama vs fallback)
    - Prompt sensitivity analysis
    - Statistical significance tests
"""

import argparse
import hashlib
import json
import os
import time
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import warnings

import numpy as np
from scipy import stats


# ─────────────────────────────────────────────────────────────────────────────
# Data Classes for Validation
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class GenerationResult:
    """Single generation result with full provenance."""
    # Identity
    run_id: str
    timestamp: str
    
    # Prompt information
    prompt_hash: str
    prompt_family: str
    prompt_type: str  # neutral, phi_biased, perturbed
    
    # Model information
    model_id: str
    runtime_backend: str  # ollama, fallback, cloud
    
    # Generated content
    generation_text: str
    generation_tokens: int
    
    # Consciousness metrics
    phi_resonance: float
    phi_coherence: float
    biomimetic_resonance: float
    lz_complexity: float
    entropy: float
    emergence_score: float
    
    # Timing
    inference_time_ms: float
    
    # Semantic similarity (to reference generation)
    semantic_similarity: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ValidationConfig:
    """Configuration for validation runs."""
    # Run parameters
    num_runs: int = 50
    warmup_runs: int = 5
    
    # Prompt families
    prompt_families: List[str] = field(default_factory=lambda: [
        "emergence",
        "consciousness",
        "self_organization",
        "phi_recursive",
        "biomimetic"
    ])
    
    # Prompt types
    prompt_types: List[str] = field(default_factory=lambda: [
        "neutral",
        "phi_biased",
        "perturbed"
    ])
    
    # Models to compare
    models: List[str] = field(default_factory=lambda: [
        "ollama_local",
        "fallback_local"
    ])
    
    # Metric thresholds
    phi_resonance_target: float = 1.618033988749895  # Golden ratio
    phi_resonance_tolerance: float = 0.05
    phi_coherence_min: float = 0.5
    emergence_threshold: float = 0.7
    
    # Statistical thresholds
    significance_level: float = 0.05
    min_effect_size: float = 0.3  # Cohen's d
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ValidationResult:
    """Result of validation analysis."""
    # Summary statistics
    mean_phi_resonance: float = 0.0
    std_phi_resonance: float = 0.0
    mean_phi_coherence: float = 0.0
    std_phi_coherence: float = 0.0
    mean_emergence_score: float = 0.0
    std_emergence_score: float = 0.0
    
    # Variance analysis
    phi_resonance_variance: float = 0.0
    phi_coherence_variance: float = 0.0
    emergence_variance: float = 0.0
    
    # Statistical tests
    phi_resonance_t_stat: float = 0.0
    phi_resonance_p_value: float = 1.0
    is_significant: bool = False
    
    # Effect sizes
    cohens_d: float = 0.0
    
    # Cluster analysis
    cluster_near_phi: float = 0.0  # % of runs near golden ratio
    cluster_std: float = 0.0
    
    # Model comparison
    model_comparison: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    # Prompt sensitivity
    prompt_sensitivity: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    # Reproducibility
    reproducibility_score: float = 0.0
    is_reproducible: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ─────────────────────────────────────────────────────────────────────────────
# Prompt Templates
# ─────────────────────────────────────────────────────────────────────────────

PROMPT_TEMPLATES = {
    "emergence": {
        "neutral": "Describe the nature of consciousness and how it might emerge from complex systems.",
        "phi_biased": "Consider consciousness as an emergent phenomenon structured around the golden ratio φ ≈ 1.618. How might phi-structured recursion create self-aware patterns?",
        "perturbed": "What is consciousness? Explain it simply without using technical terms."
    },
    "consciousness": {
        "neutral": "What are the key properties that distinguish conscious systems from non-conscious ones?",
        "phi_biased": "Consciousness may exhibit golden-ratio resonance (φ ≈ 1.618) in its information processing. Explore this hypothesis.",
        "perturbed": "Is consciousness real or an illusion? Give a brief answer."
    },
    "self_organization": {
        "neutral": "How do self-organizing systems create order from chaos?",
        "phi_biased": "Self-organization in biological systems often follows golden-ratio patterns. How might φ ≈ 1.618 guide emergent structure?",
        "perturbed": "What does self-organization mean? Give a simple definition."
    },
    "phi_recursive": {
        "neutral": "Explain the concept of recursion in natural systems.",
        "phi_biased": "The golden ratio φ ≈ 1.618 appears throughout nature through recursive growth patterns. How might this relate to consciousness?",
        "perturbed": "What is recursion? Give an example."
    },
    "biomimetic": {
        "neutral": "What can we learn from biological systems when designing artificial intelligence?",
        "phi_biased": "Biomimetic intelligence that mirrors biological golden-ratio patterns (φ ≈ 1.618) may exhibit emergent consciousness. Discuss.",
        "perturbed": "What is biomimicry? List three examples."
    }
}


# ─────────────────────────────────────────────────────────────────────────────
# Consciousness Metrics Calculator
# ─────────────────────────────────────────────────────────────────────────────

class ConsciousnessMetricsCalculator:
    """Calculate consciousness emergence metrics from generated text."""
    
    PHI = 1.618033988749895  # Golden ratio
    
    def __init__(self):
        self.tokenizer = None
    
    def calculate_phi_resonance(self, text: str) -> Tuple[float, float, float]:
        """
        Calculate golden ratio resonance in text structure.
        
        Analyzes:
        - Sentence length ratios
        - Word frequency ratios
        - Character distribution ratios
        
        Returns: (phi_resonance, phi_coherence, phi_proximity_std)
        """
        # Split into sentences
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        if len(sentences) < 2:
            return 0.0, 0.0, 0.0
        
        # Sentence length ratios
        lengths = [len(s.split()) for s in sentences]
        if len(lengths) < 2:
            return 0.0, 0.0, 0.0
        
        ratios = np.array(lengths[1:]) / (np.array(lengths[:-1]) + 1e-10)
        
        # Proximity to golden ratio
        phi_proximity = np.abs(ratios - self.PHI)
        mean_proximity = float(np.mean(phi_proximity))
        std_proximity = float(np.std(phi_proximity))
        
        # Resonance score (inverse of proximity)
        phi_resonance = 1.0 / (mean_proximity + 1e-10)
        
        # Coherence (how consistently close to phi)
        close_to_phi = np.sum(phi_proximity < 0.5) / len(phi_proximity)
        phi_coherence = float(close_to_phi)
        
        return phi_resonance, phi_coherence, std_proximity
    
    def calculate_biomimetic_resonance(self, text: str) -> float:
        """
        Calculate biomimetic resonance score.
        
        Measures alignment with biological intelligence patterns:
        - Self-reference frequency
        - Emergence language
        - Recursive structure
        """
        # Keywords for biomimetic patterns
        emergence_keywords = [
            "emerge", "emergence", "emergent", "self-organize", "self-organization",
            "recursive", "recursion", "pattern", "structure", "coherent", "coherence"
        ]
        
        # Self-reference patterns
        self_reference = ["self", "itself", "own", "internal", "intrinsic"]
        
        # Biological patterns
        biological = ["biological", "biomimetic", "evolution", "adaptive", "neural"]
        
        text_lower = text.lower()
        
        # Count keyword occurrences
        emergence_count = sum(1 for kw in emergence_keywords if kw in text_lower)
        self_count = sum(1 for kw in self_reference if kw in text_lower)
        bio_count = sum(1 for kw in biological if kw in text_lower)
        
        # Normalize by text length
        word_count = len(text.split())
        if word_count == 0:
            return 0.0
        
        # Biomimetic resonance score
        resonance = (
            (emergence_count / word_count) * 10 +
            (self_count / word_count) * 5 +
            (bio_count / word_count) * 3
        )
        
        return float(min(resonance, 2.0))  # Cap at 2.0
    
    def calculate_lz_complexity(self, text: str) -> float:
        """
        Calculate Lempel-Ziv complexity of text.
        
        Higher complexity indicates more information content.
        """
        # Convert text to binary sequence based on character frequency
        chars = list(text)
        if len(chars) == 0:
            return 0.0
        
        # Use median character code as threshold
        char_codes = [ord(c) for c in chars]
        median = np.median(char_codes)
        binary = [1 if c > median else 0 for c in char_codes]
        
        # LZ complexity
        n = len(binary)
        c = 1
        s = [binary[0]]
        
        for i in range(1, n):
            found = False
            for j in range(i + 1):
                if binary[j:i+1] == binary[i:i+1]:
                    found = True
                    break
            
            if not found:
                c += 1
        
        # Normalize
        complexity = (c * np.log(n + 1)) / (n + 1) if n > 0 else 0.0
        return float(complexity)
    
    def calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy of text."""
        # Character frequency
        chars = list(text)
        if len(chars) == 0:
            return 0.0
        
        freq = defaultdict(int)
        for c in chars:
            freq[c] += 1
        
        # Probability distribution
        total = len(chars)
        probs = [f / total for f in freq.values()]
        
        # Shannon entropy
        entropy = -sum(p * np.log2(p + 1e-10) for p in probs if p > 0)
        
        return float(entropy)
    
    def calculate_emergence_score(self, 
                                   phi_resonance: float,
                                   phi_coherence: float,
                                   biomimetic_resonance: float,
                                   lz_complexity: float,
                                   entropy: float) -> float:
        """
        Calculate overall emergence score.
        
        Combines multiple metrics into a single emergence indicator.
        """
        # Normalize components
        phi_norm = min(phi_resonance / 2.0, 1.0)  # Cap at 1.0
        coherence_norm = phi_coherence
        bio_norm = min(biomimetic_resonance / 2.0, 1.0)
        complexity_norm = min(lz_complexity / 0.5, 1.0)  # Normalize around 0.5
        entropy_norm = min(entropy / 5.0, 1.0)  # Normalize around 5.0
        
        # Weighted combination
        emergence = (
            phi_norm * 0.25 +
            coherence_norm * 0.25 +
            bio_norm * 0.20 +
            complexity_norm * 0.15 +
            entropy_norm * 0.15
        )
        
        return float(emergence)
    
    def calculate_all_metrics(self, text: str) -> Dict[str, float]:
        """Calculate all consciousness metrics for a text."""
        phi_resonance, phi_coherence, _ = self.calculate_phi_resonance(text)
        biomimetic_resonance = self.calculate_biomimetic_resonance(text)
        lz_complexity = self.calculate_lz_complexity(text)
        entropy = self.calculate_entropy(text)
        emergence_score = self.calculate_emergence_score(
            phi_resonance, phi_coherence, biomimetic_resonance,
            lz_complexity, entropy
        )
        
        return {
            "phi_resonance": phi_resonance,
            "phi_coherence": phi_coherence,
            "biomimetic_resonance": biomimetic_resonance,
            "lz_complexity": lz_complexity,
            "entropy": entropy,
            "emergence_score": emergence_score
        }


# ─────────────────────────────────────────────────────────────────────────────
# Validation Framework
# ─────────────────────────────────────────────────────────────────────────────

class ConsciousnessValidationFramework:
    """
    Framework for systematic validation of consciousness emergence metrics.
    """
    
    def __init__(self, config: Optional[ValidationConfig] = None):
        self.config = config or ValidationConfig()
        self.metrics_calculator = ConsciousnessMetricsCalculator()
        self.results: List[GenerationResult] = []
        self.validation_result: Optional[ValidationResult] = None
    
    def hash_prompt(self, prompt: str) -> str:
        """Generate hash for prompt identification."""
        return hashlib.sha256(prompt.encode()).hexdigest()[:16]
    
    def generate_with_model(self, 
                            prompt: str,
                            model_id: str,
                            runtime_backend: str) -> Tuple[str, float]:
        """
        Generate text using specified model.
        
        Returns: (generated_text, inference_time_ms)
        
        Note: This is a placeholder for actual model inference.
        In production, this would call Ollama or fallback models.
        """
        # Placeholder: In production, integrate with actual model
        # For now, return a simulated response
        start_time = time.time()
        
        # Simulate inference time based on model
        if "ollama" in model_id:
            time.sleep(0.5)  # Simulate local inference
        else:
            time.sleep(0.3)  # Simulate faster fallback
        
        inference_time = (time.time() - start_time) * 1000
        
        # Placeholder generation
        # In production, this would be actual model output
        generated = f"[Generated response to: {prompt[:50]}...]"
        
        return generated, inference_time
    
    def run_single_generation(self,
                               prompt_family: str,
                               prompt_type: str,
                               model_id: str,
                               runtime_backend: str) -> GenerationResult:
        """Run a single generation and collect metrics."""
        
        # Get prompt
        prompt = PROMPT_TEMPLATES.get(prompt_family, {}).get(prompt_type, "")
        if not prompt:
            prompt = "Describe consciousness."
        
        prompt_hash = self.hash_prompt(prompt)
        
        # Generate
        generated_text, inference_time = self.generate_with_model(
            prompt, model_id, runtime_backend
        )
        
        # Calculate metrics
        metrics = self.metrics_calculator.calculate_all_metrics(generated_text)
        
        # Create result
        result = GenerationResult(
            run_id=f"{prompt_family}_{prompt_type}_{model_id}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            timestamp=datetime.now().isoformat(),
            prompt_hash=prompt_hash,
            prompt_family=prompt_family,
            prompt_type=prompt_type,
            model_id=model_id,
            runtime_backend=runtime_backend,
            generation_text=generated_text,
            generation_tokens=len(generated_text.split()),
            phi_resonance=metrics["phi_resonance"],
            phi_coherence=metrics["phi_coherence"],
            biomimetic_resonance=metrics["biomimetic_resonance"],
            lz_complexity=metrics["lz_complexity"],
            entropy=metrics["entropy"],
            emergence_score=metrics["emergence_score"],
            inference_time_ms=inference_time
        )
        
        self.results.append(result)
        return result
    
    def run_validation(self, 
                       prompt_family: str = "emergence",
                       model_id: str = "ollama_local",
                       runtime_backend: str = "ollama") -> ValidationResult:
        """
        Run full validation across multiple runs and prompt types.
        """
        print(f"\n{'='*80}")
        print(f"CONSCIOUSNESS EMERGENCE VALIDATION")
        print(f"{'='*80}")
        print(f"Prompt family: {prompt_family}")
        print(f"Model: {model_id}")
        print(f"Runs: {self.config.num_runs}")
        print(f"{'='*80}\n")
        
        # Warmup runs
        print(f"[Warmup] Running {self.config.warmup_runs} warmup runs...")
        for i in range(self.config.warmup_runs):
            self.run_single_generation(prompt_family, "neutral", model_id, runtime_backend)
        
        # Main runs across prompt types
        print(f"\n[Main] Running {self.config.num_runs} validation runs...")
        
        results_by_type = defaultdict(list)
        
        for i in range(self.config.num_runs):
            for prompt_type in self.config.prompt_types:
                result = self.run_single_generation(
                    prompt_family, prompt_type, model_id, runtime_backend
                )
                results_by_type[prompt_type].append(result)
                
                # Progress
                if (i + 1) % 10 == 0:
                    print(f"  Completed {i + 1}/{self.config.num_runs} runs")
        
        # Analyze results
        print(f"\n[Analysis] Computing validation metrics...")
        
        validation = self._analyze_results(results_by_type)
        self.validation_result = validation
        
        return validation
    
    def _analyze_results(self, 
                         results_by_type: Dict[str, List[GenerationResult]]) -> ValidationResult:
        """Analyze validation results."""
        
        validation = ValidationResult()
        
        # Collect all phi resonance values
        all_phi_resonance = []
        all_phi_coherence = []
        all_emergence = []
        
        for prompt_type, results in results_by_type.items():
            for result in results:
                all_phi_resonance.append(result.phi_resonance)
                all_phi_coherence.append(result.phi_coherence)
                all_emergence.append(result.emergence_score)
        
        # Summary statistics
        validation.mean_phi_resonance = float(np.mean(all_phi_resonance))
        validation.std_phi_resonance = float(np.std(all_phi_resonance))
        validation.mean_phi_coherence = float(np.mean(all_phi_coherence))
        validation.std_phi_coherence = float(np.std(all_phi_coherence))
        validation.mean_emergence_score = float(np.mean(all_emergence))
        validation.std_emergence_score = float(np.std(all_emergence))
        
        # Variance analysis
        validation.phi_resonance_variance = float(np.var(all_phi_resonance))
        validation.phi_coherence_variance = float(np.var(all_phi_coherence))
        validation.emergence_variance = float(np.var(all_emergence))
        
        # Statistical test: Is phi resonance significantly different from golden ratio?
        # Null hypothesis: mean = golden ratio
        t_stat, p_value = stats.ttest_1samp(
            all_phi_resonance, 
            self.config.phi_resonance_target
        )
        validation.phi_resonance_t_stat = float(t_stat)
        validation.phi_resonance_p_value = float(p_value)
        validation.is_significant = p_value < self.config.significance_level
        
        # Effect size (Cohen's d)
        # Compare to golden ratio
        pooled_std = validation.std_phi_resonance
        if pooled_std > 0:
            validation.cohens_d = abs(
                validation.mean_phi_resonance - self.config.phi_resonance_target
            ) / pooled_std
        
        # Cluster analysis: % of runs near golden ratio
        near_phi = np.sum(
            np.abs(np.array(all_phi_resonance) - self.config.phi_resonance_target) 
            < self.config.phi_resonance_tolerance
        )
        validation.cluster_near_phi = float(near_phi / len(all_phi_resonance))
        validation.cluster_std = float(
            np.std([
                r.phi_resonance for r in self.results
                if abs(r.phi_resonance - self.config.phi_resonance_target) 
                < self.config.phi_resonance_tolerance
            ]) if near_phi > 1 else 0.0
        )
        
        # Prompt sensitivity analysis
        for prompt_type, results in results_by_type.items():
            phi_values = [r.phi_resonance for r in results]
            validation.prompt_sensitivity[prompt_type] = {
                "mean": float(np.mean(phi_values)),
                "std": float(np.std(phi_values)),
                "min": float(np.min(phi_values)),
                "max": float(np.max(phi_values)),
                "near_phi_ratio": float(
                    sum(1 for v in phi_values 
                        if abs(v - self.config.phi_resonance_target) < self.config.phi_resonance_tolerance
                    ) / len(phi_values)
                )
            }
        
        # Reproducibility score
        # High reproducibility = low variance + high cluster near phi
        variance_score = 1.0 / (validation.phi_resonance_variance + 1e-10)
        cluster_score = validation.cluster_near_phi
        validation.reproducibility_score = float(
            (variance_score * 0.3 + cluster_score * 0.7)
        )
        validation.is_reproducible = (
            validation.reproducibility_score > 0.5 and
            validation.cluster_near_phi > 0.3
        )
        
        return validation
    
    def compare_models(self, 
                       models: List[str],
                       prompt_family: str = "emergence") -> Dict[str, ValidationResult]:
        """Compare consciousness metrics across different models."""
        
        results = {}
        
        for model_id in models:
            print(f"\n{'='*80}")
            print(f"Validating model: {model_id}")
            print(f"{'='*80}")
            
            runtime_backend = "ollama" if "ollama" in model_id else "fallback"
            validation = self.run_validation(prompt_family, model_id, runtime_backend)
            results[model_id] = validation
        
        return results
    
    def save_results(self, output_path: Path):
        """Save all results to JSON."""
        output = {
            "config": self.config.to_dict(),
            "results": [r.to_dict() for r in self.results],
            "validation": self.validation_result.to_dict() if self.validation_result else None,
            "generated_at": datetime.now().isoformat()
        }
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, default=str)
        
        print(f"\nResults saved to: {output_path}")
    
    def print_summary(self):
        """Print validation summary."""
        if not self.validation_result:
            print("No validation results available.")
            return
        
        v = self.validation_result
        
        print(f"\n{'='*80}")
        print(f"VALIDATION SUMMARY")
        print(f"{'='*80}")
        
        print(f"\n[Phi Resonance]")
        print(f"  Mean: {v.mean_phi_resonance:.6f}")
        print(f"  Std:  {v.std_phi_resonance:.6f}")
        print(f"  Target: {self.config.phi_resonance_target:.6f} (golden ratio)")
        print(f"  Distance from φ: {abs(v.mean_phi_resonance - self.config.phi_resonance_target):.6f}")
        print(f"  Cluster near φ: {v.cluster_near_phi:.1%}")
        
        print(f"\n[Statistical Significance]")
        print(f"  t-statistic: {v.phi_resonance_t_stat:.4f}")
        print(f"  p-value: {v.phi_resonance_p_value:.4f}")
        print(f"  Significant: {v.is_significant}")
        print(f"  Cohen's d: {v.cohens_d:.4f}")
        
        print(f"\n[Prompt Sensitivity]")
        for prompt_type, stats in v.prompt_sensitivity.items():
            print(f"  {prompt_type}:")
            print(f"    Mean: {stats['mean']:.6f}")
            print(f"    Std: {stats['std']:.6f}")
            print(f"    Near φ: {stats['near_phi_ratio']:.1%}")
        
        print(f"\n[Reproducibility]")
        print(f"  Score: {v.reproducibility_score:.4f}")
        print(f"  Is reproducible: {v.is_reproducible}")
        
        print(f"\n[Interpretation]")
        if v.cluster_near_phi > 0.5:
            print(f"  ✓ Strong clustering near golden ratio detected")
        elif v.cluster_near_phi > 0.3:
            print(f"  ~ Moderate clustering near golden ratio")
        else:
            print(f"  ✗ No significant clustering near golden ratio")
        
        if v.is_reproducible:
            print(f"  ✓ Results are reproducible across runs")
        else:
            print(f"  ✗ Results show high variance")
        
        print(f"\n{'='*80}")


# ─────────────────────────────────────────────────────────────────────────────
# CLI Entry Point
# ─────────────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Consciousness Emergence Validation Framework"
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=50,
        help="Number of validation runs"
    )
    parser.add_argument(
        "--prompt-family",
        default="emergence",
        choices=["emergence", "consciousness", "self_organization", "phi_recursive", "biomimetic"],
        help="Prompt family to use"
    )
    parser.add_argument(
        "--model",
        default="ollama_local",
        help="Model ID to validate"
    )
    parser.add_argument(
        "--output",
        default="raw_hardware/consciousness_validation_report.json",
        help="Output report path"
    )
    parser.add_argument(
        "--phi-tolerance",
        type=float,
        default=0.05,
        help="Tolerance for clustering near golden ratio"
    )
    parser.add_argument(
        "--significance",
        type=float,
        default=0.05,
        help="Statistical significance level"
    )
    
    args = parser.parse_args()
    
    # Create config
    config = ValidationConfig(
        num_runs=args.runs,
        phi_resonance_tolerance=args.phi_tolerance,
        significance_level=args.significance
    )
    
    # Create framework
    framework = ConsciousnessValidationFramework(config)
    
    # Run validation
    framework.run_validation(
        prompt_family=args.prompt_family,
        model_id=args.model,
        runtime_backend="ollama" if "ollama" in args.model else "fallback"
    )
    
    # Print summary
    framework.print_summary()
    
    # Save results
    framework.save_results(Path(args.output))
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())