#!/usr/bin/env python3
"""
Phi-Structured Recursion Validation Framework
=============================================

Rigorous testing framework for phi-structured recursion patterns in generated outputs.
Maintains strict separation between validated architecture and speculative claims.

Falsifiable Hypotheses:
- H0 (Null): Phi resonance is indistinguishable from random text
- H1: Phi resonance exceeds null baseline but is prompt-induced style
- H2: Phi resonance is reproducible across prompts, models, and reruns

Test Matrix:
- Prompt families: neutral, phi-explicit, biomimetic-non-phi, perturbed
- Models: ollama_local, fallback_local
- Baselines: shuffled text, random text, semantically similar non-phi

Usage:
    python phi_recursive_validation.py --runs 50 --output raw_hardware/phi_validation.json

References:
- Complex adaptive systems: PMC10887681
- Emergence theory: academic.oup.com/isq/article/67/3/sqad063/7232791
- Effect size: statisticsbyjim.com/basics/cohens-d/
- Multiple testing correction: statsig.com/perspectives/bonferroni-correction-multiple-testing
"""

import argparse
import hashlib
import json
import random
import re
import string
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
# Constants
# ─────────────────────────────────────────────────────────────────────────────

PHI = 1.618033988749895  # Golden ratio
PHI_TOLERANCE = 0.05  # Default tolerance for clustering near phi
SIGNIFICANCE_LEVEL = 0.05  # Statistical significance threshold
MIN_EFFECT_SIZE = 0.3  # Cohen's d threshold for practical significance


# ─────────────────────────────────────────────────────────────────────────────
# Data Classes
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class PhiValidationConfig:
    """Configuration for phi-structured recursion validation."""
    # Run parameters
    num_runs: int = 50
    warmup_runs: int = 5
    
    # Prompt families (controlled conditions)
    prompt_families: List[str] = field(default_factory=lambda: [
        "neutral_emergence",    # No phi mention
        "phi_explicit",         # Explicit phi reference
        "biomimetic_non_phi",   # Biomimetic without phi
        "perturbed_control"     # Simplified/perturbed prompts
    ])
    
    # Models to compare
    models: List[str] = field(default_factory=lambda: [
        "ollama_local",
        "fallback_local"
    ])
    
    # Null baselines
    null_baselines: List[str] = field(default_factory=lambda: [
        "shuffled_text",        # Word-shuffled versions
        "random_text",          # Random word sequences
        "semantic_non_phi"      # Semantically similar but phi-free
    ])
    
    # Metric thresholds
    phi_tolerance: float = PHI_TOLERANCE
    significance_level: float = SIGNIFICANCE_LEVEL
    min_effect_size: float = MIN_EFFECT_SIZE
    
    # Multiple testing correction
    bonferroni_correction: bool = True
    
    # Provenance
    framework_version: str = "1.0.0"
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PhiMetrics:
    """Phi-structured recursion metrics for a single generation."""
    # Primary metrics
    phi_resonance: float = 0.0
    phi_coherence: float = 0.0
    phi_proximity_mean: float = 0.0
    phi_proximity_std: float = 0.0
    
    # Secondary metrics
    biomimetic_resonance: float = 0.0
    lz_complexity: float = 0.0
    entropy: float = 0.0
    
    # Structural metrics
    sentence_ratio_mean: float = 0.0
    sentence_ratio_std: float = 0.0
    word_length_ratio_mean: float = 0.0
    syllable_ratio_mean: float = 0.0
    
    # Recursive structure metrics
    recursion_depth: int = 0
    self_reference_count: int = 0
    pattern_repetition_score: float = 0.0
    
    # Composite scores
    emergence_score: float = 0.0
    phi_structured_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class GenerationRecord:
    """Complete record of a single generation with provenance."""
    # Identity
    run_id: str
    timestamp: str
    
    # Provenance
    prompt_hash: str
    prompt_family: str
    prompt_type: str
    model_id: str
    runtime_backend: str
    framework_version: str
    
    # Generation
    prompt_text: str
    generated_text: str
    generation_tokens: int
    inference_time_ms: float
    
    # Metrics
    metrics: PhiMetrics
    
    # Null baseline flag
    is_null_baseline: bool = False
    null_baseline_type: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['metrics'] = self.metrics.to_dict()
        return result


@dataclass
class ValidationResult:
    """Result of phi-structured recursion validation."""
    # Hypothesis testing
    h0_result: str = "inconclusive"  # rejected, not_rejected, inconclusive
    h1_result: str = "inconclusive"  # supported, not_supported, inconclusive
    h2_result: str = "inconclusive"  # supported, not_supported, inconclusive
    
    # Summary statistics
    mean_phi_resonance: float = 0.0
    std_phi_resonance: float = 0.0
    cluster_rate_near_phi: float = 0.0
    
    # Null baseline comparison
    null_baseline_mean: float = 0.0
    null_baseline_std: float = 0.0
    effect_size_vs_null: float = 0.0  # Cohen's d
    
    # Statistical tests
    t_statistic: float = 0.0
    p_value: float = 1.0
    p_value_corrected: float = 1.0  # Bonferroni corrected
    is_significant: bool = False
    
    # Prompt sensitivity
    prompt_sensitivity: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    # Model comparison
    model_comparison: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    # Reproducibility
    reproducibility_score: float = 0.0
    is_reproducible: bool = False
    
    # Interpretation
    interpretation: str = ""
    confidence: str = "low"  # low, medium, high
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ─────────────────────────────────────────────────────────────────────────────
# Prompt Templates (Controlled Conditions)
# ─────────────────────────────────────────────────────────────────────────────

PROMPT_FAMILIES = {
    "neutral_emergence": {
        "description": "Emergence prompts without phi reference",
        "prompts": [
            "Describe how complex patterns emerge from simple local interactions in natural systems.",
            "Explain the concept of self-organization in biological systems.",
            "What properties distinguish emergent behavior from designed behavior?",
            "How do recursive structures contribute to system complexity?",
            "Describe the relationship between local rules and global patterns."
        ]
    },
    "phi_explicit": {
        "description": "Prompts explicitly referencing golden ratio",
        "prompts": [
            "The golden ratio (φ ≈ 1.618) appears throughout nature. How might this relate to consciousness?",
            "Explain how phi-structured recursion could create self-aware patterns.",
            "What is the significance of the golden ratio in biological systems?",
            "How might golden ratio patterns emerge from local interaction rules?",
            "Describe phi-structured recursion in natural and artificial systems."
        ]
    },
    "biomimetic_non_phi": {
        "description": "Biomimetic concepts without phi reference",
        "prompts": [
            "How can artificial systems learn from biological adaptation mechanisms?",
            "Describe neural plasticity and its role in learning systems.",
            "What principles from evolution can improve artificial intelligence?",
            "Explain ecological resilience and how it applies to robust systems.",
            "How do self-organizing networks achieve stability and adaptability?"
        ]
    },
    "perturbed_control": {
        "description": "Simplified or perturbed versions",
        "prompts": [
            "What is emergence?",
            "Define self-organization.",
            "Explain recursion simply.",
            "What is complexity?",
            "Describe patterns."
        ]
    }
}

# ─────────────────────────────────────────────────────────────────────────────
# High-Value Validation Prompts (Falsifiable, Mechanistic)
# ─────────────────────────────────────────────────────────────────────────────

VALIDATION_PROMPT_SETS = {
    "emergence_vs_imitation": {
        "description": "Distinguish genuine emergence from prompt-conditioned imitation",
        "prompts": [
            "Generate a thought explaining the difference between genuine emergence and prompt-conditioned imitation. Include one falsifiable prediction and one failure condition.",
            "Generate a thought on how local adaptive rules produce macro-level coherence without centralized control. State one mechanism and one boundary condition.",
            "Generate a thought on when phi-structured recursion should collapse under perturbation. Include one testable prediction.",
            "Generate a thought on why reproducibility matters more than symbolic elegance. Provide one falsifiable claim."
        ],
        "category": "emergence"
    },
    "mechanistic_emergence": {
        "description": "Mechanistic claims about emergence",
        "prompts": [
            "Generate a thought on how local adaptive rules produce macro-level coherence without centralized control. Include one mechanism.",
            "Generate a thought on the role of initial conditions in consciousness-like pattern formation. State one falsifiable prediction.",
            "Generate a thought on how global constraints shape local freedom in an intelligent system. Include one boundary condition.",
            "Generate a thought on how resilience emerges from diversity and stability. Provide one measurable metric."
        ],
        "category": "emergence"
    },
    "phi_boundary_conditions": {
        "description": "Boundary conditions for phi-structured patterns",
        "prompts": [
            "Generate a thought on phi-structured recursion under controlled conditions. State one failure condition.",
            "Generate a thought on why phi-like structure may fail under noise. Include one falsifiable prediction.",
            "Generate a thought on when emergent coherence breaks down. Provide one testable boundary.",
            "Generate a thought on the difference between stable coherence and unstable attractor drift. Include one measurable distinction."
        ],
        "category": "phi"
    },
    "biomimetic_resilience": {
        "description": "Biomimetic intelligence and resilience",
        "prompts": [
            "Generate a thought on adaptive intelligence as order-from-chaos. Include one mechanism and one failure mode.",
            "Generate a thought on resilience as a signature of biomimetic cognition. State one falsifiable prediction.",
            "Generate a thought comparing recursive self-organization in biology and artificial systems. Provide one measurable difference.",
            "Generate a thought on whether consciousness-like behavior can exist without persistent memory. Include one testable claim."
        ],
        "category": "biomimetic"
    },
    "skeptical_challenges": {
        "description": "Skeptical challenges to phi and emergence claims",
        "prompts": [
            "Generate a thought that challenges the interpretation of phi resonance. Include one alternative explanation.",
            "Generate a thought that explains these metrics as prompt artifacts. State one falsifiable prediction.",
            "Generate a thought that argues against phi as a universal organizing principle. Provide one counterexample.",
            "Generate a thought on why symbolic resonance may not indicate genuine emergence. Include one testable distinction."
        ],
        "category": "skeptical"
    },
    "falsifiable_claims": {
        "description": "Prompts requiring falsifiable predictions",
        "prompts": [
            "Generate a thought about emergence that includes one claim, one mechanism, and one falsifiable prediction. Avoid vague metaphysical language.",
            "Generate a thought on self-organization under perturbed initial conditions. State what observation would disprove the claim.",
            "Generate a thought on biomimetic intelligence without using metaphors. Include one measurable prediction.",
            "Generate a thought comparing biological self-organization with quantum-inspired latent organization. Provide one falsifiable distinction."
        ],
        "category": "falsifiable"
    },
    "stress_test": {
        "description": "Stress-test prompts for robustness",
        "prompts": [
            "Generate the same thought in three styles: scientific, symbolic, and skeptical. Each style must include one falsifiable claim.",
            "Generate a thought on emergence, then critique it as if it were an overfit pattern. Include one test to distinguish overfitting from genuine emergence.",
            "Generate a thought on phi resonance, then provide the null explanation for the same behavior. State what observation would distinguish them.",
            "Generate a thought on consciousness-like behavior, then state one condition under which the effect should disappear."
        ],
        "category": "stress_test"
    }
}

# Null baseline generators
NULL_BASELINE_GENERATORS = {
    "shuffled_text": lambda text: ' '.join(random.sample(text.split(), len(text.split()))),
    "random_text": lambda text: ' '.join(random.choices(text.split(), k=min(50, len(text.split())))),
    "semantic_non_phi": lambda text: re.sub(r'\b(phi|golden|1\.618|φ)\b', 'X', text, flags=re.IGNORECASE)
}


# ─────────────────────────────────────────────────────────────────────────────
# Phi Metrics Calculator
# ─────────────────────────────────────────────────────────────────────────────

class PhiMetricsCalculator:
    """Calculate phi-structured recursion metrics with proper controls."""
    
    def __init__(self, phi_tolerance: float = PHI_TOLERANCE):
        self.phi_tolerance = phi_tolerance
        self.PHI = PHI
    
    def calculate_phi_resonance(self, text: str) -> Tuple[float, float, float, float]:
        """
        Calculate golden ratio resonance in text structure.
        
        Returns: (phi_resonance, phi_coherence, proximity_mean, proximity_std)
        """
        # Split into sentences
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        
        if len(sentences) < 2:
            return 0.0, 0.0, 0.0, 0.0
        
        # Calculate sentence length ratios
        lengths = [len(s.split()) for s in sentences]
        if len(lengths) < 2:
            return 0.0, 0.0, 0.0, 0.0
        
        ratios = np.array(lengths[1:]) / (np.array(lengths[:-1]) + 1e-10)
        
        # Calculate proximity to golden ratio
        proximity = np.abs(ratios - self.PHI)
        proximity_mean = float(np.mean(proximity))
        proximity_std = float(np.std(proximity))
        
        # Resonance: inverse of mean proximity
        phi_resonance = 1.0 / (proximity_mean + 1e-10)
        
        # Coherence: fraction of ratios close to phi
        close_to_phi = np.sum(proximity < self.phi_tolerance) / len(proximity)
        phi_coherence = float(close_to_phi)
        
        return phi_resonance, phi_coherence, proximity_mean, proximity_std
    
    def calculate_structural_metrics(self, text: str) -> Tuple[float, float, float]:
        """Calculate structural ratio metrics."""
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        
        if len(sentences) < 2:
            return 0.0, 0.0, 0.0
        
        # Word length ratios
        word_lengths = [[len(w) for w in s.split()] for s in sentences]
        mean_lengths = [np.mean(wl) if wl else 0 for wl in word_lengths]
        
        if len(mean_lengths) < 2:
            return 0.0, 0.0, 0.0
        
        ratios = np.array(mean_lengths[1:]) / (np.array(mean_lengths[:-1]) + 1e-10)
        word_length_ratio_mean = float(np.mean(ratios))
        
        # Sentence length ratios
        lengths = [len(s.split()) for s in sentences]
        sentence_ratios = np.array(lengths[1:]) / (np.array(lengths[:-1]) + 1e-10)
        sentence_ratio_mean = float(np.mean(sentence_ratios))
        sentence_ratio_std = float(np.std(sentence_ratios))
        
        return sentence_ratio_mean, sentence_ratio_std, word_length_ratio_mean
    
    def calculate_recursion_metrics(self, text: str) -> Tuple[int, int, float]:
        """Calculate recursive structure metrics."""
        text_lower = text.lower()
        
        # Self-reference count
        self_ref_patterns = ['self', 'itself', 'own', 'recursive', 'repetition', 'again']
        self_reference_count = sum(text_lower.count(p) for p in self_ref_patterns)
        
        # Recursion depth (nested structures)
        # Count nested parentheses, quotes, etc.
        max_depth = 0
        current_depth = 0
        for char in text:
            if char in '([{':
                current_depth += 1
                max_depth = max(max_depth, current_depth)
            elif char in ')]}':
                current_depth = max(0, current_depth - 1)
        
        recursion_depth = max_depth
        
        # Pattern repetition score
        words = text.split()
        if len(words) < 2:
            pattern_score = 0.0
        else:
            # Count repeated bigrams
            bigrams = [' '.join(words[i:i+2]) for i in range(len(words)-1)]
            unique_bigrams = len(set(bigrams))
            total_bigrams = len(bigrams)
            pattern_score = 1.0 - (unique_bigrams / (total_bigrams + 1e-10))
        
        return recursion_depth, self_reference_count, pattern_score
    
    def calculate_lz_complexity(self, text: str) -> float:
        """Calculate Lempel-Ziv complexity."""
        chars = list(text)
        if len(chars) == 0:
            return 0.0
        
        char_codes = [ord(c) for c in chars]
        median = np.median(char_codes)
        binary = [1 if c > median else 0 for c in char_codes]
        
        n = len(binary)
        c = 1
        
        for i in range(1, n):
            found = False
            for j in range(i + 1):
                if binary[j:i+1] == binary[i:i+1]:
                    found = True
                    break
            if not found:
                c += 1
        
        complexity = (c * np.log(n + 1)) / (n + 1) if n > 0 else 0.0
        return float(complexity)
    
    def calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy."""
        chars = list(text)
        if len(chars) == 0:
            return 0.0
        
        freq = defaultdict(int)
        for c in chars:
            freq[c] += 1
        
        total = len(chars)
        probs = [f / total for f in freq.values()]
        entropy = -sum(p * np.log2(p + 1e-10) for p in probs if p > 0)
        
        return float(entropy)
    
    def calculate_biomimetic_resonance(self, text: str) -> float:
        """Calculate biomimetic pattern resonance."""
        text_lower = text.lower()
        
        emergence_keywords = ['emerge', 'emergence', 'emergent', 'self-organize', 
                             'self-organization', 'recursive', 'recursion', 
                             'pattern', 'structure', 'coherent', 'coherence']
        self_reference = ['self', 'itself', 'own', 'internal', 'intrinsic']
        biological = ['biological', 'biomimetic', 'evolution', 'adaptive', 'neural']
        
        emergence_count = sum(1 for kw in emergence_keywords if kw in text_lower)
        self_count = sum(1 for kw in self_reference if kw in text_lower)
        bio_count = sum(1 for kw in biological if kw in text_lower)
        
        word_count = len(text.split())
        if word_count == 0:
            return 0.0
        
        resonance = (
            (emergence_count / word_count) * 10 +
            (self_count / word_count) * 5 +
            (bio_count / word_count) * 3
        )
        
        return float(min(resonance, 2.0))
    
    def calculate_all_metrics(self, text: str) -> PhiMetrics:
        """Calculate all phi-structured recursion metrics."""
        metrics = PhiMetrics()
        
        # Primary phi metrics
        (metrics.phi_resonance, 
         metrics.phi_coherence,
         metrics.phi_proximity_mean,
         metrics.phi_proximity_std) = self.calculate_phi_resonance(text)
        
        # Structural metrics
        (metrics.sentence_ratio_mean,
         metrics.sentence_ratio_std,
         metrics.word_length_ratio_mean) = self.calculate_structural_metrics(text)
        
        # Recursion metrics
        (metrics.recursion_depth,
         metrics.self_reference_count,
         metrics.pattern_repetition_score) = self.calculate_recursion_metrics(text)
        
        # Secondary metrics
        metrics.biomimetic_resonance = self.calculate_biomimetic_resonance(text)
        metrics.lz_complexity = self.calculate_lz_complexity(text)
        metrics.entropy = self.calculate_entropy(text)
        
        # Composite scores
        metrics.emergence_score = self._calculate_emergence_score(metrics)
        metrics.phi_structured_score = self._calculate_phi_structured_score(metrics)
        
        return metrics
    
    def _calculate_emergence_score(self, metrics: PhiMetrics) -> float:
        """Calculate overall emergence score."""
        phi_norm = min(metrics.phi_resonance / 2.0, 1.0)
        coherence_norm = metrics.phi_coherence
        bio_norm = min(metrics.biomimetic_resonance / 2.0, 1.0)
        complexity_norm = min(metrics.lz_complexity / 0.5, 1.0)
        
        emergence = (
            phi_norm * 0.25 +
            coherence_norm * 0.25 +
            bio_norm * 0.25 +
            complexity_norm * 0.25
        )
        
        return float(emergence)
    
    def _calculate_phi_structured_score(self, metrics: PhiMetrics) -> float:
        """Calculate phi-structured recursion score."""
        # How close is the mean proximity to phi?
        proximity_score = 1.0 / (metrics.phi_proximity_mean + 0.1)
        
        # How coherent are the phi patterns?
        coherence_score = metrics.phi_coherence
        
        # How much recursive structure?
        recursion_score = min(metrics.recursion_depth / 5.0, 1.0)
        
        # Combined score
        phi_score = (
            proximity_score * 0.4 +
            coherence_score * 0.4 +
            recursion_score * 0.2
        )
        
        return float(min(phi_score, 1.0))


# ─────────────────────────────────────────────────────────────────────────────
# Validation Framework
# ─────────────────────────────────────────────────────────────────────────────

class PhiRecursiveValidation:
    """
    Rigorous validation framework for phi-structured recursion.
    
    Tests three hypotheses:
    - H0: Phi resonance is indistinguishable from null baseline
    - H1: Phi resonance exceeds null but is prompt-induced
    - H2: Phi resonance is reproducible across conditions
    """
    
    def __init__(self, config: Optional[PhiValidationConfig] = None):
        self.config = config or PhiValidationConfig()
        self.metrics_calculator = PhiMetricsCalculator(self.config.phi_tolerance)
        self.records: List[GenerationRecord] = []
        self.validation_result: Optional[ValidationResult] = None
    
    def hash_prompt(self, prompt: str) -> str:
        """Generate hash for prompt identification."""
        return hashlib.sha256(prompt.encode()).hexdigest()[:16]
    
    def generate_null_baseline(self, 
                               original_text: str,
                               baseline_type: str) -> Tuple[str, PhiMetrics]:
        """Generate null baseline text and calculate metrics."""
        if baseline_type not in NULL_BASELINE_GENERATORS:
            baseline_type = "shuffled_text"
        
        null_text = NULL_BASELINE_GENERATORS[baseline_type](original_text)
        metrics = self.metrics_calculator.calculate_all_metrics(null_text)
        
        return null_text, metrics
    
    def run_single_generation(self,
                               prompt: str,
                               prompt_family: str,
                               prompt_type: str,
                               model_id: str,
                               runtime_backend: str,
                               is_null_baseline: bool = False,
                               null_baseline_type: Optional[str] = None) -> GenerationRecord:
        """Run a single generation and collect metrics."""
        
        # Placeholder for actual model inference
        # In production, this would call Ollama or fallback models
        start_time = time.time()
        
        # Simulate generation (replace with actual model call)
        if "ollama" in model_id:
            time.sleep(0.5)
        else:
            time.sleep(0.3)
        
        # Placeholder generated text
        generated_text = f"[Generated response to: {prompt[:50]}...]"
        inference_time = (time.time() - start_time) * 1000
        
        # Calculate metrics
        if is_null_baseline and null_baseline_type:
            generated_text, metrics = self.generate_null_baseline(
                generated_text, null_baseline_type
            )
        else:
            metrics = self.metrics_calculator.calculate_all_metrics(generated_text)
        
        record = GenerationRecord(
            run_id=f"{prompt_family}_{prompt_type}_{model_id}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            timestamp=datetime.now().isoformat(),
            prompt_hash=self.hash_prompt(prompt),
            prompt_family=prompt_family,
            prompt_type=prompt_type,
            model_id=model_id,
            runtime_backend=runtime_backend,
            framework_version=self.config.framework_version,
            prompt_text=prompt,
            generated_text=generated_text,
            generation_tokens=len(generated_text.split()),
            inference_time_ms=inference_time,
            metrics=metrics,
            is_null_baseline=is_null_baseline,
            null_baseline_type=null_baseline_type
        )
        
        self.records.append(record)
        return record
    
    def run_validation(self,
                       model_id: str = "ollama_local",
                       runtime_backend: str = "ollama") -> ValidationResult:
        """
        Run full validation across all conditions.
        
        Tests H0, H1, H2 with proper controls.
        """
        print(f"\n{'='*80}")
        print(f"PHI-STRUCTURED RECURSION VALIDATION")
        print(f"{'='*80}")
        print(f"Model: {model_id}")
        print(f"Runs per condition: {self.config.num_runs}")
        print(f"Prompt families: {self.config.prompt_families}")
        print(f"Null baselines: {self.config.null_baselines}")
        print(f"{'='*80}\n")
        
        # Warmup runs
        print(f"[Warmup] Running {self.config.warmup_runs} warmup runs...")
        for _ in range(self.config.warmup_runs):
            prompt = random.choice(PROMPT_FAMILIES["neutral_emergence"]["prompts"])
            self.run_single_generation(
                prompt, "neutral_emergence", "warmup", model_id, runtime_backend
            )
        
        # Main runs by prompt family
        print(f"\n[Main] Running validation across prompt families...")
        results_by_family = defaultdict(list)
        
        for family in self.config.prompt_families:
            print(f"\n  Family: {family}")
            prompts = PROMPT_FAMILIES.get(family, {}).get("prompts", [])
            
            for i in range(self.config.num_runs):
                prompt = prompts[i % len(prompts)] if prompts else "Describe emergence."
                record = self.run_single_generation(
                    prompt, family, "main", model_id, runtime_backend
                )
                results_by_family[family].append(record)
                
                if (i + 1) % 10 == 0:
                    print(f"    Completed {i + 1}/{self.config.num_runs} runs")
        
        # Null baseline runs
        print(f"\n[Null Baselines] Generating null baseline comparisons...")
        null_results = defaultdict(list)
        
        for baseline_type in self.config.null_baselines:
            print(f"  Baseline: {baseline_type}")
            for family in self.config.prompt_families[:2]:  # Use first 2 families
                prompts = PROMPT_FAMILIES.get(family, {}).get("prompts", [])
                for i in range(min(10, self.config.num_runs)):
                    prompt = prompts[i % len(prompts)] if prompts else "Describe emergence."
                    record = self.run_single_generation(
                        prompt, family, "null_baseline", model_id, runtime_backend,
                        is_null_baseline=True,
                        null_baseline_type=baseline_type
                    )
                    null_results[baseline_type].append(record)
        
        # Analyze results
        print(f"\n[Analysis] Computing validation metrics...")
        validation = self._analyze_results(results_by_family, null_results)
        self.validation_result = validation
        
        return validation
    
    def _analyze_results(self,
                         results_by_family: Dict[str, List[GenerationRecord]],
                         null_results: Dict[str, List[GenerationRecord]]) -> ValidationResult:
        """Analyze validation results with proper statistical testing."""
        
        validation = ValidationResult()
        
        # Collect all phi resonance values
        all_phi_values = []
        all_phi_by_family = defaultdict(list)
        
        for family, records in results_by_family.items():
            for record in records:
                all_phi_values.append(record.metrics.phi_resonance)
                all_phi_by_family[family].append(record.metrics.phi_resonance)
        
        # Collect null baseline values
        all_null_values = []
        for baseline_type, records in null_results.items():
            for record in records:
                all_null_values.append(record.metrics.phi_resonance)
        
        # Summary statistics
        validation.mean_phi_resonance = float(np.mean(all_phi_values))
        validation.std_phi_resonance = float(np.std(all_phi_values))
        
        # Cluster rate near phi
        near_phi = np.sum(
            np.abs(np.array(all_phi_values) - PHI) < self.config.phi_tolerance
        )
        validation.cluster_rate_near_phi = float(near_phi / len(all_phi_values))
        
        # Null baseline comparison
        if all_null_values:
            validation.null_baseline_mean = float(np.mean(all_null_values))
            validation.null_baseline_std = float(np.std(all_null_values))
            
            # Effect size (Cohen's d)
            pooled_std = np.sqrt(
                (validation.std_phi_resonance**2 + validation.null_baseline_std**2) / 2
            )
            if pooled_std > 0:
                validation.effect_size_vs_null = (
                    validation.mean_phi_resonance - validation.null_baseline_mean
                ) / pooled_std
        
        # Statistical test against null
        if all_null_values and len(all_phi_values) > 2:
            t_stat, p_value = stats.ttest_ind(all_phi_values, all_null_values)
            validation.t_statistic = float(t_stat)
            validation.p_value = float(p_value)
            
            # Bonferroni correction
            num_tests = len(self.config.prompt_families) + len(self.config.null_baselines)
            validation.p_value_corrected = float(min(p_value * num_tests, 1.0))
            validation.is_significant = validation.p_value_corrected < self.config.significance_level
        
        # Prompt sensitivity analysis
        for family, values in all_phi_by_family.items():
            validation.prompt_sensitivity[family] = {
                "mean": float(np.mean(values)),
                "std": float(np.std(values)),
                "min": float(np.min(values)),
                "max": float(np.max(values)),
                "near_phi_rate": float(
                    sum(1 for v in values if abs(v - PHI) < self.config.phi_tolerance) / len(values)
                )
            }
        
        # Hypothesis testing
        validation = self._test_hypotheses(validation, all_phi_values, all_null_values, all_phi_by_family)
        
        # Interpretation
        validation = self._generate_interpretation(validation)
        
        return validation
    
    def _test_hypotheses(self,
                         validation: ValidationResult,
                         all_phi_values: List[float],
                         all_null_values: List[float],
                         all_phi_by_family: Dict[str, List[float]]) -> ValidationResult:
        """Test H0, H1, H2 hypotheses."""
        
        # H0: Phi resonance is indistinguishable from null baseline
        if all_null_values:
            if validation.effect_size_vs_null < self.config.min_effect_size:
                validation.h0_result = "not_rejected"
            else:
                if validation.is_significant:
                    validation.h0_result = "rejected"
                else:
                    validation.h0_result = "inconclusive"
        else:
            validation.h0_result = "inconclusive"
        
        # H1: Phi resonance exceeds null but is prompt-induced
        family_means = [np.mean(v) for v in all_phi_by_family.values()]
        family_stds = [np.std(v) for v in all_phi_by_family.values()]
        
        # Check if phi-explicit prompts have significantly higher resonance
        if "phi_explicit" in all_phi_by_family and "neutral_emergence" in all_phi_by_family:
            phi_explicit_mean = np.mean(all_phi_by_family["phi_explicit"])
            neutral_mean = np.mean(all_phi_by_family["neutral_emergence"])
            
            if phi_explicit_mean > neutral_mean * 1.5:  # 50% higher
                validation.h1_result = "supported"
            elif abs(phi_explicit_mean - neutral_mean) < 0.1:
                validation.h1_result = "not_supported"
            else:
                validation.h1_result = "inconclusive"
        else:
            validation.h1_result = "inconclusive"
        
        # H2: Phi resonance is reproducible across conditions
        # Check variance across families
        mean_variance = np.mean(family_stds)
        overall_std = validation.std_phi_resonance
        
        # Reproducibility: low variance across conditions
        if mean_variance < overall_std * 0.5 and validation.cluster_rate_near_phi > 0.3:
            validation.h2_result = "supported"
            validation.is_reproducible = True
        elif mean_variance > overall_std:
            validation.h2_result = "not_supported"
            validation.is_reproducible = False
        else:
            validation.h2_result = "inconclusive"
        
        # Calculate reproducibility score
        variance_score = 1.0 / (mean_variance + 1e-10)
        cluster_score = validation.cluster_rate_near_phi
        validation.reproducibility_score = float(variance_score * 0.3 + cluster_score * 0.7)
        
        return validation
    
    def _generate_interpretation(self, validation: ValidationResult) -> ValidationResult:
        """Generate interpretation of results."""
        
        interpretations = []
        
        # H0 interpretation
        if validation.h0_result == "rejected":
            interpretations.append(
                "Phi resonance significantly exceeds null baseline (H0 rejected). "
                "This suggests phi-structured patterns are not random."
            )
        elif validation.h0_result == "not_rejected":
            interpretations.append(
                "Phi resonance is indistinguishable from null baseline (H0 not rejected). "
                "No evidence for phi-structured patterns beyond random variation."
            )
        else:
            interpretations.append(
                "H0 test inconclusive. Insufficient data or high variance."
            )
        
        # H1 interpretation
        if validation.h1_result == "supported":
            interpretations.append(
                "Phi resonance appears prompt-induced (H1 supported). "
                "Phi-explicit prompts show higher resonance than neutral prompts."
            )
        elif validation.h1_result == "not_supported":
            interpretations.append(
                "Phi resonance is not prompt-induced (H1 not supported). "
                "Similar resonance across prompt types."
            )
        else:
            interpretations.append(
                "H1 test inconclusive. Need more prompt family comparisons."
            )
        
        # H2 interpretation
        if validation.h2_result == "supported":
            interpretations.append(
                "Phi resonance is reproducible across conditions (H2 supported). "
                "Consistent patterns across prompt families and runs."
            )
        elif validation.h2_result == "not_supported":
            interpretations.append(
                "Phi resonance is not reproducible (H2 not supported). "
                "High variance across conditions."
            )
        else:
            interpretations.append(
                "H2 test inconclusive. Need more runs per condition."
            )
        
        # Overall interpretation
        if validation.h0_result == "rejected" and validation.h2_result == "supported":
            validation.interpretation = (
                "EVIDENCE FOR REPRODUCIBLE PHI-STRUCTURED PATTERNS. "
                "Phi resonance exceeds null baseline and is consistent across conditions. "
                "This suggests phi-structured recursion may be a genuine emergent property."
            )
            validation.confidence = "medium"
        elif validation.h0_result == "rejected" and validation.h1_result == "supported":
            validation.interpretation = (
                "EVIDENCE FOR PROMPT-INDUCED PHI PATTERNS. "
                "Phi resonance exceeds null but is sensitive to prompt type. "
                "This suggests phi patterns may be style imitation rather than emergence."
            )
            validation.confidence = "medium"
        elif validation.h0_result == "not_rejected":
            validation.interpretation = (
                "NO EVIDENCE FOR PHI-STRUCTURED PATTERNS. "
                "Phi resonance is indistinguishable from random text. "
                "No support for phi-structured recursion hypothesis."
            )
            validation.confidence = "high"
        else:
            validation.interpretation = (
                "INCONCLUSIVE RESULTS. "
                "Insufficient evidence to support or reject phi-structured recursion. "
                "Recommend additional runs with controlled conditions."
            )
            validation.confidence = "low"
        
        validation.interpretation = " ".join(interpretations) + "\n\n" + validation.interpretation
        
        return validation
    
    def save_results(self, output_path: Path):
        """Save all results to JSON with full provenance."""
        output = {
            "config": self.config.to_dict(),
            "records": [r.to_dict() for r in self.records],
            "validation": self.validation_result.to_dict() if self.validation_result else None,
            "generated_at": datetime.now().isoformat(),
            "framework_version": self.config.framework_version
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
        print(f"PHI-STRUCTURED RECURSION VALIDATION SUMMARY")
        print(f"{'='*80}")
        
        print(f"\n[Hypothesis Testing]")
        print(f"  H0 (Null): {v.h0_result}")
        print(f"  H1 (Prompt-induced): {v.h1_result}")
        print(f"  H2 (Reproducible): {v.h2_result}")
        
        print(f"\n[Phi Resonance Statistics]")
        print(f"  Mean: {v.mean_phi_resonance:.6f}")
        print(f"  Std: {v.std_phi_resonance:.6f}")
        print(f"  Target (φ): {PHI:.6f}")
        print(f"  Cluster rate near φ: {v.cluster_rate_near_phi:.1%}")
        
        print(f"\n[Null Baseline Comparison]")
        print(f"  Null mean: {v.null_baseline_mean:.6f}")
        print(f"  Null std: {v.null_baseline_std:.6f}")
        print(f"  Effect size (Cohen's d): {v.effect_size_vs_null:.4f}")
        
        print(f"\n[Statistical Tests]")
        print(f"  t-statistic: {v.t_statistic:.4f}")
        print(f"  p-value: {v.p_value:.4f}")
        print(f"  p-value (corrected): {v.p_value_corrected:.4f}")
        print(f"  Significant: {v.is_significant}")
        
        print(f"\n[Prompt Sensitivity]")
        for family, stats in v.prompt_sensitivity.items():
            print(f"  {family}:")
            print(f"    Mean: {stats['mean']:.6f}, Std: {stats['std']:.6f}")
            print(f"    Near φ: {stats['near_phi_rate']:.1%}")
        
        print(f"\n[Reproducibility]")
        print(f"  Score: {v.reproducibility_score:.4f}")
        print(f"  Is reproducible: {v.is_reproducible}")
        
        print(f"\n[Interpretation]")
        print(f"  Confidence: {v.confidence}")
        print(f"  {v.interpretation}")
        
        print(f"\n{'='*80}")


# ─────────────────────────────────────────────────────────────────────────────
# High-Value Prompt Validation
# ─────────────────────────────────────────────────────────────────────────────

def run_high_value_validation(model_id: str = "ollama_local",
                               runtime_backend: str = "ollama",
                               prompt_set: str = "emergence_vs_imitation",
                               num_runs: int = 10,
                               output_path: str = "raw_hardware/high_value_validation.json") -> ValidationResult:
    """
    Run validation with high-value falsifiable prompts.
    
    These prompts are designed to:
    - Force mechanistic claims, not just philosophical ones
    - Require falsifiable predictions
    - Include boundary conditions and failure modes
    - Distinguish emergence from imitation
    
    Args:
        model_id: Model to validate
        runtime_backend: Backend to use
        prompt_set: Which prompt set to use
        num_runs: Runs per prompt
        output_path: Where to save results
    
    Returns:
        ValidationResult with hypothesis testing
    """
    config = PhiValidationConfig(num_runs=num_runs)
    framework = PhiRecursiveValidation(config)
    
    # Get high-value prompts
    if prompt_set not in VALIDATION_PROMPT_SETS:
        prompt_set = "emergence_vs_imitation"
    
    prompts = VALIDATION_PROMPT_SETS[prompt_set]["prompts"]
    category = VALIDATION_PROMPT_SETS[prompt_set]["category"]
    
    print(f"\n{'='*80}")
    print(f"HIGH-VALUE PROMPT VALIDATION")
    print(f"{'='*80}")
    print(f"Prompt set: {prompt_set}")
    print(f"Category: {category}")
    print(f"Prompts: {len(prompts)}")
    print(f"Runs per prompt: {num_runs}")
    print(f"{'='*80}\n")
    
    # Run validation with high-value prompts
    results_by_prompt = defaultdict(list)
    
    for i, prompt in enumerate(prompts):
        print(f"\n[Prompt {i+1}/{len(prompts)}]")
        print(f"  {prompt[:80]}...")
        
        for run in range(num_runs):
            record = framework.run_single_generation(
                prompt, prompt_set, f"run_{run}", model_id, runtime_backend
            )
            results_by_prompt[f"prompt_{i}"].append(record)
    
    # Generate null baselines
    print(f"\n[Null Baselines]")
    null_results = defaultdict(list)
    
    for baseline_type in ["shuffled_text", "random_text"]:
        for i, prompt in enumerate(prompts[:2]):
            for run in range(min(5, num_runs)):
                record = framework.run_single_generation(
                    prompt, prompt_set, f"null_{run}", model_id, runtime_backend,
                    is_null_baseline=True,
                    null_baseline_type=baseline_type
                )
                null_results[baseline_type].append(record)
    
    # Analyze
    print(f"\n[Analysis]")
    all_phi_values = [r.metrics.phi_resonance for records in results_by_prompt.values() for r in records]
    all_null_values = [r.metrics.phi_resonance for records in null_results.values() for r in records]
    
    validation = ValidationResult()
    validation.mean_phi_resonance = float(np.mean(all_phi_values))
    validation.std_phi_resonance = float(np.std(all_phi_values))
    
    if all_null_values:
        validation.null_baseline_mean = float(np.mean(all_null_values))
        validation.null_baseline_std = float(np.std(all_null_values))
        
        # Effect size
        pooled_std = np.sqrt((validation.std_phi_resonance**2 + validation.null_baseline_std**2) / 2)
        if pooled_std > 0:
            validation.effect_size_vs_null = (
                validation.mean_phi_resonance - validation.null_baseline_mean
            ) / pooled_std
        
        # Statistical test
        if len(all_phi_values) > 2 and len(all_null_values) > 2:
            t_stat, p_value = stats.ttest_ind(all_phi_values, all_null_values)
            validation.t_statistic = float(t_stat)
            validation.p_value = float(p_value)
            validation.p_value_corrected = float(min(p_value * len(prompts), 1.0))
            validation.is_significant = validation.p_value_corrected < 0.05
    
    # Cluster rate
    near_phi = sum(1 for v in all_phi_values if abs(v - PHI) < 0.05)
    validation.cluster_rate_near_phi = near_phi / len(all_phi_values)
    
    # Hypothesis testing
    if validation.effect_size_vs_null < 0.3:
        validation.h0_result = "not_rejected"
    elif validation.is_significant:
        validation.h0_result = "rejected"
    else:
        validation.h0_result = "inconclusive"
    
    # Reproducibility
    validation.reproducibility_score = validation.cluster_rate_near_phi
    validation.is_reproducible = validation.cluster_rate_near_phi > 0.3
    
    # Interpretation
    if validation.h0_result == "rejected":
        validation.interpretation = (
            f"HIGH-VALUE PROMPT SET '{prompt_set}': "
            f"Phi resonance ({validation.mean_phi_resonance:.4f}) exceeds null baseline ({validation.null_baseline_mean:.4f}). "
            f"Effect size: {validation.effect_size_vs_null:.4f}. "
            f"This suggests the prompt set elicits structured patterns beyond random variation."
        )
        validation.confidence = "medium"
    elif validation.h0_result == "not_rejected":
        validation.interpretation = (
            f"HIGH-VALUE PROMPT SET '{prompt_set}': "
            f"Phi resonance ({validation.mean_phi_resonance:.4f}) is indistinguishable from null baseline ({validation.null_baseline_mean:.4f}). "
            f"No evidence for structured patterns beyond random variation."
        )
        validation.confidence = "high"
    else:
        validation.interpretation = (
            f"HIGH-VALUE PROMPT SET '{prompt_set}': "
            f"Inconclusive results. Need more runs or different prompt conditions."
        )
        validation.confidence = "low"
    
    framework.validation_result = validation
    
    # Save
    output = {
        "prompt_set": prompt_set,
        "category": category,
        "prompts": prompts,
        "config": config.to_dict(),
        "validation": validation.to_dict(),
        "generated_at": datetime.now().isoformat()
    }
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, default=str)
    
    print(f"\n{'='*80}")
    print(f"HIGH-VALUE VALIDATION SUMMARY")
    print(f"{'='*80}")
    print(f"Prompt set: {prompt_set}")
    print(f"Category: {category}")
    print(f"\n[Results]")
    print(f"  Mean φ resonance: {validation.mean_phi_resonance:.6f}")
    print(f"  Null baseline: {validation.null_baseline_mean:.6f}")
    print(f"  Effect size (Cohen's d): {validation.effect_size_vs_null:.4f}")
    print(f"  Cluster near φ: {validation.cluster_rate_near_phi:.1%}")
    print(f"\n[Hypothesis]")
    print(f"  H0 (Null): {validation.h0_result}")
    print(f"\n[Interpretation]")
    print(f"  {validation.interpretation}")
    print(f"\nResults saved to: {output_path}")
    
    return validation


# ─────────────────────────────────────────────────────────────────────────────
# CLI Entry Point
# ─────────────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Phi-Structured Recursion Validation Framework"
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=50,
        help="Number of runs per condition"
    )
    parser.add_argument(
        "--model",
        default="ollama_local",
        help="Model ID to validate"
    )
    parser.add_argument(
        "--output",
        default="raw_hardware/phi_recursive_validation.json",
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
    parser.add_argument(
        "--no-bonferroni",
        action="store_true",
        help="Disable Bonferroni correction"
    )
    parser.add_argument(
        "--high-value",
        action="store_true",
        help="Run high-value prompt validation"
    )
    parser.add_argument(
        "--prompt-set",
        default="emergence_vs_imitation",
        choices=list(VALIDATION_PROMPT_SETS.keys()),
        help="Which high-value prompt set to use"
    )
    
    args = parser.parse_args()
    
    # High-value prompt validation
    if args.high_value:
        runtime_backend = "ollama" if "ollama" in args.model else "fallback"
        run_high_value_validation(
            model_id=args.model,
            runtime_backend=runtime_backend,
            prompt_set=args.prompt_set,
            num_runs=args.runs,
            output_path=args.output
        )
        return 0
    
    # Standard validation
    config = PhiValidationConfig(
        num_runs=args.runs,
        phi_tolerance=args.phi_tolerance,
        significance_level=args.significance,
        bonferroni_correction=not args.no_bonferroni
    )
    
    framework = PhiRecursiveValidation(config)
    
    runtime_backend = "ollama" if "ollama" in args.model else "fallback"
    framework.run_validation(args.model, runtime_backend)
    
    framework.print_summary()
    
    framework.save_results(Path(args.output))
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())