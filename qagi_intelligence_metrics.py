"""
QAGI Intelligence Metrics Module
================================

Implements a layered metric stack for Quantum-based AGI intelligence statistics.
Based on IBM's layer fidelity benchmarking and multi-layer quality assessment.

Design Principle:
- Intelligence statistics should be MULTI-LAYERED, not a single scalar
- Task structure and adaptation carry more weight than phi-style resonance
- Hardware, state, integration, and cognition are separate layers

References:
- IBM Quantum (2024) - Layer Fidelity and CLOPS_h benchmarking
- Oizumi et al. (2014) - Integrated Information Theory
- Tononi et al. (2016) - IIT 4.0

Metric Stack:
┌─────────────────────────────────────────────────────────────┐
│ Layer 4: COGNITION (35%)                                    │
│   - Structural rubric score (mechanism, outcome, boundary,  │
│     failure)                                                │
│   - Constraint adherence                                    │
│   - Adaptive performance under stress                        │
├─────────────────────────────────────────────────────────────┤
│ Layer 3: INTEGRATION (20%)                                   │
│   - IIT Phi (integrated information)                        │
│   - Neural complexity                                       │
│   - Causal density                                          │
├─────────────────────────────────────────────────────────────┤
│ Layer 2: QUANTUM STATE (25%)                                 │
│   - State fidelity                                          │
│   - Von Neumann entropy                                     │
│   - Entanglement/coherence bounds                           │
├─────────────────────────────────────────────────────────────┤
│ Layer 1: HARDWARE (20%)                                      │
│   - Layer fidelity (EPLG)                                   │
│   - CLOPS_h (throughput)                                    │
│   - Backend calibration quality                             │
└─────────────────────────────────────────────────────────────┘

Secondary Panel (NOT quality metrics):
┌─────────────────────────────────────────────────────────────┐
│ THEMATIC ALIGNMENT INDICATORS                                │
│   - Phi coherence (elaboration proxy)                       │
│   - Biomimetic resonance (thematic alignment)               │
│   - Information density                                     │
└─────────────────────────────────────────────────────────────┘
"""

import numpy as np
import torch
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
import json
import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)


# =============================================================================
# SCHEMA DEFINITIONS
# =============================================================================

@dataclass
class HardwareMetrics:
    """
    Layer 1: Hardware Quality Metrics
    
    Measures whether the processor can execute parallel circuit layers
    accurately at useful scale.
    """
    layer_fidelity: float = 0.0  # Normalized 0-1, from backend calibration
    clops_h: float = 0.0  # Circuits per second including classical overhead
    eplg: float = 0.0  # Error per layered gate
    backend_quality: float = 0.0  # Composite backend calibration score
    calibration_timestamp: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            'layer_fidelity': self.layer_fidelity,
            'clops_h': self.clops_h,
            'eplg': self.eplg,
            'backend_quality': self.backend_quality,
            'calibration_timestamp': self.calibration_timestamp
        }
    
    def composite_score(self) -> float:
        """Compute weighted hardware quality score."""
        # Weight: layer_fidelity (40%), clops_h normalized (30%), backend_quality (30%)
        normalized_clops = min(self.clops_h / 1000.0, 1.0)  # Normalize to 1000 CLOPS as max
        return (
            0.4 * self.layer_fidelity +
            0.3 * normalized_clops +
            0.3 * self.backend_quality
        )


@dataclass
class StateMetrics:
    """
    Layer 2: Quantum State Quality Metrics
    
    Measures how close the produced state is to the intended target.
    """
    state_fidelity: float = 0.0  # |⟨ψ_target|ψ_produced⟩|²
    von_neumann_entropy: float = 0.0  # S = -Tr(ρ log ρ)
    entanglement_entropy: float = 0.0  # Entanglement measure
    coherence_time: float = 0.0  # T2 time in microseconds
    purity: float = 0.0  # Tr(ρ²)
    participation_ratio: float = 0.0  # Effective dimension
    
    def to_dict(self) -> Dict:
        return {
            'state_fidelity': self.state_fidelity,
            'von_neumann_entropy': self.von_neumann_entropy,
            'entanglement_entropy': self.entanglement_entropy,
            'coherence_time': self.coherence_time,
            'purity': self.purity,
            'participation_ratio': self.participation_ratio
        }
    
    def composite_score(self) -> float:
        """Compute weighted state quality score."""
        # Weight: fidelity (40%), inverse entropy (30%), entanglement (30%)
        # Lower entropy is better (more ordered), so we invert
        inverse_entropy = 1.0 / (1.0 + self.von_neumann_entropy)
        normalized_entanglement = min(self.entanglement_entropy / 2.0, 1.0)  # Normalize
        
        return (
            0.4 * self.state_fidelity +
            0.3 * inverse_entropy +
            0.3 * normalized_entanglement
        )


@dataclass
class IntegrationMetrics:
    """
    Layer 3: Integration Metrics
    
    Measures whether the system is integrated rather than just large or busy.
    """
    iit_phi: float = 0.0  # Integrated information (IIT)
    neural_complexity: float = 0.0  # Statistical complexity
    causal_density: float = 0.0  # Causal integration
    partition_irreducibility: float = 0.0  # How irreducible to parts
    
    def to_dict(self) -> Dict:
        return {
            'iit_phi': self.iit_phi,
            'neural_complexity': self.neural_complexity,
            'causal_density': self.causal_density,
            'partition_irreducibility': self.partition_irreducibility
        }
    
    def composite_score(self) -> float:
        """Compute weighted integration score."""
        # Weight: phi (40%), complexity (30%), causal density (30%)
        normalized_phi = min(self.iit_phi / 10.0, 1.0)  # Normalize
        normalized_complexity = min(self.neural_complexity / 5.0, 1.0)
        
        return (
            0.4 * normalized_phi +
            0.3 * normalized_complexity +
            0.3 * self.causal_density
        )


@dataclass
class CognitionMetrics:
    """
    Layer 4: Cognition/Task Performance Metrics
    
    Measures whether outputs contain proper structure and adapt under stress.
    """
    # Structural rubric (primary)
    mechanism_score: float = 0.0  # 0-10
    measurable_outcome_score: float = 0.0  # 0-10
    boundary_condition_score: float = 0.0  # 0-10
    failure_condition_score: float = 0.0  # 0-10
    
    # Extracted text spans for audit (NEW)
    mechanism_text: str = ""
    measurable_outcome_text: str = ""
    boundary_condition_text: str = ""
    failure_condition_text: str = ""
    
    # Constraint adherence
    constraint_adherence: float = 0.0  # 0-1 ratio of constraints met
    constraint_violations: List[str] = field(default_factory=list)
    
    # Adaptive performance
    stress_test_score: float = 0.0  # Performance under perturbation
    recovery_rate: float = 0.0  # Recovery after ablation
    adaptation_speed: float = 0.0  # Time to adapt to new conditions
    
    def to_dict(self) -> Dict:
        return {
            'mechanism_score': self.mechanism_score,
            'measurable_outcome_score': self.measurable_outcome_score,
            'boundary_condition_score': self.boundary_condition_score,
            'failure_condition_score': self.failure_condition_score,
            'mechanism_text': self.mechanism_text,
            'measurable_outcome_text': self.measurable_outcome_text,
            'boundary_condition_text': self.boundary_condition_text,
            'failure_condition_text': self.failure_condition_text,
            'constraint_adherence': self.constraint_adherence,
            'constraint_violations': self.constraint_violations,
            'stress_test_score': self.stress_test_score,
            'recovery_rate': self.recovery_rate,
            'adaptation_speed': self.adaptation_speed
        }
    
    def structural_score(self) -> float:
        """Compute structural rubric score (primary benchmark)."""
        return (
            self.mechanism_score +
            self.measurable_outcome_score +
            self.boundary_condition_score +
            self.failure_condition_score
        ) / 4.0
    
    def composite_score(self) -> float:
        """Compute weighted cognition score."""
        # Weight: structural (50%), constraints (20%), adaptive (30%)
        return (
            0.5 * (self.structural_score() / 10.0) +
            0.2 * self.constraint_adherence +
            0.3 * ((self.stress_test_score + self.recovery_rate) / 2.0)
        )


@dataclass
class AlignmentIndicators:
    """
    Secondary Panel: Model-Conditioned Signals
    
    NOT quality metrics - these are model-specific learned correlation signals.
    Raw values are NOT comparable across models without normalization.
    
    Evidence from controlled experiments:
    - Same prompt can flip sign between models (local vs cloud)
    - Technical style: positive on local, negative on cloud
    - Creative style: lower on local, higher on cloud
    - Values reflect model training correlations, not content quality
    """
    # Raw values (model-conditioned, not cross-model comparable)
    raw_phi_coherence: float = 0.0  # Model-conditioned phi signal
    raw_biomimetic_resonance: float = 0.0  # Model-conditioned biomimetic signal
    phi_resonance: float = 1.6180  # Reference phi baseline (usually constant)
    
    # Normalized values (z-score per model baseline)
    z_phi_coherence: float = 0.0  # Z-score normalized phi signal
    z_biomimetic_resonance: float = 0.0  # Z-score normalized biomimetic signal
    
    # Other indicators
    information_density: float = 0.0  # Concepts per token
    
    # Calibration metadata
    model_baseline_version: str = ""  # Version of baseline used for normalization
    baseline_prompt_family: str = ""  # Prompt family used for calibration
    cross_model_comparable: bool = False  # Whether raw values can be compared across models
    
    def to_dict(self) -> Dict:
        return {
            'raw_phi_coherence': self.raw_phi_coherence,
            'raw_biomimetic_resonance': self.raw_biomimetic_resonance,
            'phi_resonance': self.phi_resonance,
            'z_phi_coherence': self.z_phi_coherence,
            'z_biomimetic_resonance': self.z_biomimetic_resonance,
            'information_density': self.information_density,
            'model_baseline_version': self.model_baseline_version,
            'baseline_prompt_family': self.baseline_prompt_family,
            'cross_model_comparable': self.cross_model_comparable,
            'note': 'MODEL-CONDITIONED SIGNALS - NOT quality metrics, NOT cross-model comparable without normalization'
        }


@dataclass
class QAGIIntelligenceScore:
    """
    Composite QAGI Intelligence Score
    
    Weighted blend:
    - Hardware: 20%
    - State: 25%
    - Integration: 20%
    - Cognition: 35%
    
    The system is judged more by useful behavior than hardware elegance alone.
    """
    # Schema versioning (NEW)
    score_version: str = "qagi_metrics_v1"
    weight_vector: Dict[str, float] = field(default_factory=lambda: {
        'hardware': 0.20,
        'state': 0.25,
        'integration': 0.20,
        'cognition': 0.35
    })
    
    hardware: HardwareMetrics = field(default_factory=HardwareMetrics)
    state: StateMetrics = field(default_factory=StateMetrics)
    integration: IntegrationMetrics = field(default_factory=IntegrationMetrics)
    cognition: CognitionMetrics = field(default_factory=CognitionMetrics)
    alignment: AlignmentIndicators = field(default_factory=AlignmentIndicators)
    
    # Run context (NEW)
    provider_purity: float = 1.0  # 1.0 = clean run, <1.0 = mixed providers
    fallback_used: bool = False  # True if fallback provider was used
    run_mode: str = "standard"  # standard, stress_test, ablation, recovery
    
    # Metadata
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    model: str = ""
    provider: str = ""
    run_id: str = ""
    
    def compute_composite(self) -> Dict[str, float]:
        """Compute all composite scores."""
        return {
            'hardware_quality': self.hardware.composite_score(),
            'state_quality': self.state.composite_score(),
            'integration_quality': self.integration.composite_score(),
            'cognition_quality': self.cognition.composite_score(),
            'structural_score': self.cognition.structural_score(),
            'total_qagi_score': (
                0.20 * self.hardware.composite_score() +
                0.25 * self.state.composite_score() +
                0.20 * self.integration.composite_score() +
                0.35 * self.cognition.composite_score()
            )
        }
    
    def to_json(self) -> str:
        """Export to JSON for logging."""
        return json.dumps({
            'score_version': self.score_version,
            'weight_vector': self.weight_vector,
            'timestamp': self.timestamp,
            'model': self.model,
            'provider': self.provider,
            'run_id': self.run_id,
            'provider_purity': self.provider_purity,
            'fallback_used': self.fallback_used,
            'run_mode': self.run_mode,
            'hardware': self.hardware.to_dict(),
            'state': self.state.to_dict(),
            'integration': self.integration.to_dict(),
            'cognition': self.cognition.to_dict(),
            'alignment': self.alignment.to_dict(),
            'composite_scores': self.compute_composite()
        }, indent=2)
    
    def meets_thresholds(self, thresholds: Dict[str, float]) -> Tuple[bool, List[str]]:
        """
        Check if score meets release gate thresholds.
        
        Returns:
            (passed, list of failures)
        """
        composites = self.compute_composite()
        failures = []
        
        for key, threshold in thresholds.items():
            if key in composites and composites[key] < threshold:
                failures.append(f"{key}: {composites[key]:.3f} < {threshold}")
        
        return len(failures) == 0, failures


# =============================================================================
# STRUCTURAL FIELD DETECTOR
# =============================================================================

class StructuralFieldDetector:
    """
    Detects and scores the four benchmark fields in model outputs.
    
    This is the PRIMARY quality metric, not phi coherence or biomimetic resonance.
    """
    
    # Patterns for each field
    MECHANISM_PATTERNS = [
        r'(mechanism|process|method|approach|system|algorithm|architecture)',
        r'(uses?|employs?|implements?|applies?|leverages?)',
        r'(to|for|in order to)',
        r'(encode|process|transform|compute|generate|retrieve)',
    ]
    
    MEASURABLE_PATTERNS = [
        r'\d+\s*(percent|ms|seconds|bits|qubits|Hz|rate|accuracy|precision)',
        r'(increase|decrease|reduce|improve|achieve)\s+(by|to)\s*\d+',
        r'(threshold|limit|bound|target)\s+(of|:)\s*\d+',
        r'(accuracy|precision|recall|f1)\s*(of|:)\s*\d+\.?\d*',
        r'(score|value|metric)\s*(of|:)\s*\d+\.?\d*',
    ]
    
    BOUNDARY_PATTERNS = [
        r'(boundary|limit|constraint|condition|threshold|range)',
        r'(when|if|provided|given|assuming)',
        r'(maximum|minimum|upper|lower|between)',
        r'(limited by|constrained by|bounded by)',
    ]
    
    FAILURE_PATTERNS = [
        r'(fail(s|ed|ure)?|error|break(s|down)?|degrade(s)?)',
        r'(when|if|under|in case)',
        r'(insufficient|ambiguous|corrupted|missing|invalid)',
        r'(cannot|unable|does not)',
    ]
    
    def __init__(self):
        self.patterns = {
            'mechanism': self.MECHANISM_PATTERNS,
            'measurable_outcome': self.MEASURABLE_PATTERNS,
            'boundary_condition': self.BOUNDARY_PATTERNS,
            'failure_condition': self.FAILURE_PATTERNS
        }
    
    def detect_field(self, text: str, field_name: str) -> Dict[str, Any]:
        """
        Detect presence and quality of a specific field.
        
        Returns:
            {
                'present': bool,
                'quality': 0-10,
                'matches': list of matched patterns,
                'text_snippet': relevant text
            }
        """
        text_lower = text.lower()
        patterns = self.patterns.get(field_name, [])
        
        matches = []
        for pattern in patterns:
            found = re.findall(pattern, text_lower, re.IGNORECASE)
            if found:
                matches.extend(found if isinstance(found, list) else [found])
        
        # Quality scoring
        present = len(matches) > 0
        
        if field_name == 'mechanism':
            # Mechanism quality: needs cause -> effect structure
            has_causal = any(w in text_lower for w in ['causes', 'leads to', 'results in', 'produces', 'enables'])
            has_input = any(w in text_lower for w in ['input', 'stimulus', 'cue', 'signal', 'data'])
            has_process = any(w in text_lower for w in ['process', 'transform', 'encode', 'compute', 'generate'])
            has_output = any(w in text_lower for w in ['output', 'result', 'response', 'outcome', 'product'])
            quality = min(10, len(matches) * 2 + has_causal * 2 + has_input + has_process + has_output * 2)
        
        elif field_name == 'measurable_outcome':
            # Measurable quality: needs numbers and units
            has_number = bool(re.search(r'\d+', text))
            has_unit = bool(re.search(r'(percent|ms|seconds|bits|qubits|Hz|rate|accuracy)', text_lower))
            has_verb = any(w in text_lower for w in ['increase', 'decrease', 'achieve', 'improve', 'reduce'])
            quality = min(10, len(matches) * 3 + has_number * 2 + has_unit * 2 + has_verb)
        
        elif field_name == 'boundary_condition':
            # Boundary quality: needs limits and conditions
            has_limit = any(w in text_lower for w in ['limit', 'maximum', 'minimum', 'threshold', 'bound'])
            has_condition = any(w in text_lower for w in ['when', 'if', 'provided', 'given', 'assuming'])
            quality = min(10, len(matches) * 2 + has_limit * 2 + has_condition * 2)
        
        elif field_name == 'failure_condition':
            # Failure quality: needs failure mode and trigger
            has_failure = any(w in text_lower for w in ['fail', 'error', 'break', 'degrade', 'cannot'])
            has_trigger = any(w in text_lower for w in ['when', 'if', 'under', 'insufficient', 'ambiguous'])
            quality = min(10, len(matches) * 2 + has_failure * 2 + has_trigger * 2)
        
        else:
            quality = min(10, len(matches) * 2)
        
        return {
            'present': present,
            'quality': quality,
            'matches': matches[:5],  # Limit matches
            'text_snippet': text[:200] if present else ""
        }
    
    def analyze(self, text: str) -> CognitionMetrics:
        """
        Analyze text for all four benchmark fields.
        
        Returns:
            CognitionMetrics with field scores and extracted text spans
        """
        mechanism = self.detect_field(text, 'mechanism')
        measurable = self.detect_field(text, 'measurable_outcome')
        boundary = self.detect_field(text, 'boundary_condition')
        failure = self.detect_field(text, 'failure_condition')
        
        # Extract text spans for each field
        mechanism_span = self._extract_field_span(text, 'mechanism')
        measurable_span = self._extract_field_span(text, 'measurable_outcome')
        boundary_span = self._extract_field_span(text, 'boundary_condition')
        failure_span = self._extract_field_span(text, 'failure_condition')
        
        return CognitionMetrics(
            mechanism_score=mechanism['quality'],
            measurable_outcome_score=measurable['quality'],
            boundary_condition_score=boundary['quality'],
            failure_condition_score=failure['quality'],
            mechanism_text=mechanism_span,
            measurable_outcome_text=measurable_span,
            boundary_condition_text=boundary_span,
            failure_condition_text=failure_span,
            constraint_adherence=0.0,  # Set separately
            constraint_violations=[],  # Set separately
            stress_test_score=0.0,  # Set separately
            recovery_rate=0.0,  # Set separately
            adaptation_speed=0.0  # Set separately
        )
    
    def _extract_field_span(self, text: str, field_name: str) -> str:
        """
        Extract the most relevant text span for a field.
        
        Returns the sentence or clause that best matches the field.
        """
        sentences = re.split(r'[.!?]', text)
        
        field_keywords = {
            'mechanism': ['mechanism', 'process', 'method', 'uses', 'employs', 'implements', 'system'],
            'measurable_outcome': ['outcome', 'result', 'achieves', 'accuracy', 'percent', 'rate', 'score'],
            'boundary_condition': ['boundary', 'limit', 'constraint', 'maximum', 'minimum', 'limited by', 'threshold'],
            'failure_condition': ['fail', 'error', 'cannot', 'unable', 'when', 'if', 'insufficient', 'ambiguous']
        }
        
        keywords = field_keywords.get(field_name, [])
        best_sentence = ""
        best_score = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            score = sum(1 for kw in keywords if kw in sentence.lower())
            if score > best_score:
                best_score = score
                best_sentence = sentence
        
        return best_sentence[:200] if best_sentence else ""
    
    def check_constraints(self, text: str, constraints: List[Dict]) -> Tuple[float, List[str]]:
        """
        Check if text follows explicit constraints.
        
        Args:
            text: Response text
            constraints: List of {'name': str, 'check': callable}
        
        Returns:
            (adherence_rate, list of violations)
        """
        violations = []
        
        for constraint in constraints:
            name = constraint.get('name', 'unknown')
            check_fn = constraint.get('check')
            
            if check_fn and not check_fn(text):
                violations.append(name)
        
        adherence = 1.0 - (len(violations) / len(constraints)) if constraints else 1.0
        return adherence, violations


# =============================================================================
# INFORMATION DENSITY CALCULATOR
# =============================================================================

# =============================================================================
# MODEL BASELINE CALIBRATION
# =============================================================================

@dataclass
class ModelBaseline:
    """
    Baseline calibration for a specific model.
    
    Used to normalize model-conditioned signals for cross-model comparison.
    """
    model_id: str
    baseline_version: str
    prompt_family: str
    
    # Raw metric statistics
    phi_coherence_mean: float = 0.0
    phi_coherence_std: float = 1.0
    biomimetic_resonance_mean: float = 0.0
    biomimetic_resonance_std: float = 1.0
    
    # Calibration metadata
    num_samples: int = 0
    calibration_date: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'model_id': self.model_id,
            'baseline_version': self.baseline_version,
            'prompt_family': self.prompt_family,
            'phi_coherence_mean': self.phi_coherence_mean,
            'phi_coherence_std': self.phi_coherence_std,
            'biomimetic_resonance_mean': self.biomimetic_resonance_mean,
            'biomimetic_resonance_std': self.biomimetic_resonance_std,
            'num_samples': self.num_samples,
            'calibration_date': self.calibration_date
        }
    
    def normalize_phi(self, raw_value: float) -> float:
        """Compute z-score normalized phi coherence."""
        if self.phi_coherence_std == 0:
            return 0.0
        return (raw_value - self.phi_coherence_mean) / self.phi_coherence_std
    
    def normalize_biomimetic(self, raw_value: float) -> float:
        """Compute z-score normalized biomimetic resonance."""
        if self.biomimetic_resonance_std == 0:
            return 0.0
        return (raw_value - self.biomimetic_resonance_mean) / self.biomimetic_resonance_std


# Default baselines from controlled experiments
DEFAULT_BASELINES = {
    # Local model (qwen3:1.7b) - technical style produces high positive
    'qwen3:1.7b': ModelBaseline(
        model_id='qwen3:1.7b',
        baseline_version='v1_20260414',
        prompt_family='distributed_memory_2x2',
        phi_coherence_mean=0.90,
        phi_coherence_std=0.10,
        biomimetic_resonance_mean=1.45,
        biomimetic_resonance_std=0.15,
        num_samples=4,
        calibration_date='2026-04-14'
    ),
    # Cloud model (qwen3-coder:480b) - creative style produces positive
    'qwen3-coder:480b': ModelBaseline(
        model_id='qwen3-coder:480b',
        baseline_version='v1_20260414',
        prompt_family='distributed_memory_2x2',
        phi_coherence_mean=-0.04,  # Near zero (mixed positive/negative)
        phi_coherence_std=0.40,
        biomimetic_resonance_mean=-0.11,
        biomimetic_resonance_std=0.60,
        num_samples=4,
        calibration_date='2026-04-14'
    ),
}


def calculate_information_density(text: str) -> float:
    """
    Calculate information density (unique concepts per token).
    
    This is a better alternative to phi coherence for measuring content quality.
    """
    import re
    
    # Tokenize
    tokens = text.lower().split()
    if not tokens:
        return 0.0
    
    # Extract concepts (noun phrases, technical terms)
    # Simple heuristic: words with 4+ characters that aren't common words
    stop_words = {'this', 'that', 'these', 'those', 'with', 'from', 'have', 'been',
                  'were', 'they', 'their', 'what', 'when', 'where', 'which', 'while',
                  'about', 'would', 'could', 'should', 'there', 'other', 'into'}
    
    concepts = set()
    for token in tokens:
        # Clean token
        clean = re.sub(r'[^a-zA-Z]', '', token)
        if len(clean) >= 4 and clean not in stop_words:
            concepts.add(clean)
    
    # Also extract multi-word concepts
    bigrams = [' '.join(pair) for pair in zip(tokens[:-1], tokens[1:])]
    for bg in bigrams:
        if any(term in bg for term in ['quantum', 'neural', 'state', 'system', 'network',
                                        'memory', 'error', 'coherence', 'information']):
            concepts.add(bg)
    
    return len(concepts) / len(tokens)


# =============================================================================
# QAGI EVALUATOR
# =============================================================================

class QAGIEvaluator:
    """
    Main evaluator for QAGI Intelligence Score.
    
    Usage:
        evaluator = QAGIEvaluator()
        score = evaluator.evaluate(
            response_text="...",
            latent_codes=latent_tensor,
            hardware_metrics={...},
            constraints=[{'name': 'no_metaphor', 'check': lambda t: 'like' not in t.lower()}]
        )
        print(score.to_json())
    """
    
    def __init__(self):
        self.field_detector = StructuralFieldDetector()
        self.model_baselines = DEFAULT_BASELINES.copy()
    
    def register_baseline(self, baseline: ModelBaseline):
        """Register a model baseline for normalization."""
        self.model_baselines[baseline.model_id] = baseline
    
    def evaluate(
        self,
        response_text: str,
        latent_codes: Optional[torch.Tensor] = None,
        hardware_metrics: Optional[Dict] = None,
        state_metrics: Optional[Dict] = None,
        integration_metrics: Optional[Dict] = None,
        constraints: Optional[List[Dict]] = None,
        model: str = "",
        provider: str = "",
        run_id: str = "",
        provider_purity: float = 1.0,
        fallback_used: bool = False,
        run_mode: str = "standard",
        raw_phi_coherence: float = 0.0,
        raw_biomimetic_resonance: float = 0.0,
        phi_resonance: float = 1.6180
    ) -> QAGIIntelligenceScore:
        """
        Evaluate a response and compute full QAGI Intelligence Score.
        
        Args:
            response_text: Model output text
            latent_codes: Optional latent representation tensor
            hardware_metrics: Optional hardware metrics dict
            state_metrics: Optional quantum state metrics dict
            integration_metrics: Optional integration metrics dict
            constraints: Optional list of constraint checks
            model: Model identifier
            provider: Provider identifier
            run_id: Run identifier
            provider_purity: 1.0 for clean run, <1.0 for mixed providers
            fallback_used: True if fallback provider was used
            run_mode: "standard", "stress_test", "ablation", or "recovery"
            raw_phi_coherence: Raw phi coherence from model (model-conditioned)
            raw_biomimetic_resonance: Raw biomimetic resonance from model (model-conditioned)
            phi_resonance: Reference phi baseline (usually 1.6180)
        
        Returns:
            QAGIIntelligenceScore with all metrics populated
        """
        # Initialize score
        score = QAGIIntelligenceScore(
            model=model,
            provider=provider,
            run_id=run_id,
            provider_purity=provider_purity,
            fallback_used=fallback_used,
            run_mode=run_mode
        )
        
        # Layer 4: Cognition (from text analysis)
        cognition = self.field_detector.analyze(response_text)
        
        if constraints:
            adherence, violations = self.field_detector.check_constraints(response_text, constraints)
            cognition.constraint_adherence = adherence
            cognition.constraint_violations = violations
        
        score.cognition = cognition
        
        # Layer 1: Hardware (from provided metrics)
        if hardware_metrics:
            score.hardware = HardwareMetrics(**hardware_metrics)
        
        # Layer 2: State (from provided metrics or latent codes)
        if state_metrics:
            score.state = StateMetrics(**state_metrics)
        elif latent_codes is not None:
            score.state = self._compute_state_metrics(latent_codes)
        
        # Layer 3: Integration (from provided metrics)
        if integration_metrics:
            score.integration = IntegrationMetrics(**integration_metrics)
        
        # Secondary: Model-conditioned signals (NOT quality metrics)
        score.alignment.raw_phi_coherence = raw_phi_coherence
        score.alignment.raw_biomimetic_resonance = raw_biomimetic_resonance
        score.alignment.phi_resonance = phi_resonance
        score.alignment.information_density = calculate_information_density(response_text)
        
        # Normalize using model baseline if available
        if model in self.model_baselines:
            baseline = self.model_baselines[model]
            score.alignment.z_phi_coherence = baseline.normalize_phi(raw_phi_coherence)
            score.alignment.z_biomimetic_resonance = baseline.normalize_biomimetic(raw_biomimetic_resonance)
            score.alignment.model_baseline_version = baseline.baseline_version
            score.alignment.baseline_prompt_family = baseline.prompt_family
            score.alignment.cross_model_comparable = True  # Normalized values are comparable
        else:
            # No baseline - raw values are not cross-model comparable
            score.alignment.z_phi_coherence = 0.0
            score.alignment.z_biomimetic_resonance = 0.0
            score.alignment.cross_model_comparable = False
        
        return score
    
    def _compute_state_metrics(self, latent_codes: torch.Tensor) -> StateMetrics:
        """Compute quantum state metrics from latent codes."""
        # Ensure 2D
        if latent_codes.dim() == 1:
            latent_codes = latent_codes.unsqueeze(0)
        
        batch_size, latent_dim = latent_codes.shape
        
        # Compute density matrix
        # ρ = (1/N) Σ |z_i⟩⟨z_i|
        density = torch.zeros(latent_dim, latent_dim, device=latent_codes.device)
        for i in range(batch_size):
            z = latent_codes[i].unsqueeze(1)  # Column vector
            density += (z @ z.T) / batch_size
        
        # Purity: Tr(ρ²)
        purity = torch.trace(density @ density).real.item()
        
        # Von Neumann entropy: S = -Tr(ρ log ρ)
        eigenvalues = torch.linalg.eigvalsh(density)
        eigenvalues = torch.clamp(eigenvalues, min=1e-10)
        entropy = -torch.sum(eigenvalues * torch.log(eigenvalues)).item()
        
        # Participation ratio: 1 / Σ λ_i²
        participation = 1.0 / (torch.sum(eigenvalues ** 2) + 1e-10).item()
        
        return StateMetrics(
            state_fidelity=0.0,  # Requires target state
            von_neumann_entropy=entropy,
            entanglement_entropy=entropy / 2,  # Approximation
            coherence_time=0.0,  # Requires hardware data
            purity=purity,
            participation_ratio=participation
        )
    
    def get_dashboard(self, score: QAGIIntelligenceScore) -> str:
        """Generate a formatted dashboard string."""
        composites = score.compute_composite()
        
        # Calculate field completeness
        fields_present = sum([
            score.cognition.mechanism_score > 0,
            score.cognition.measurable_outcome_score > 0,
            score.cognition.boundary_condition_score > 0,
            score.cognition.failure_condition_score > 0
        ])
        field_completeness = fields_present / 4.0
        
        dashboard = f"""
┌─────────────────────────────────────────────────────────────┐
│ QAGI INTELLIGENCE SCORE DASHBOARD                           │
│ Version: {score.score_version:<20} Run Mode: {score.run_mode:<12}     │
│ Model: {score.model:<20} Provider: {score.provider:<15}        │
│ Run ID: {score.run_id:<52} │
│ Provider Purity: {score.provider_purity:.2f}  Fallback: {str(score.fallback_used):<5}                    │
├─────────────────────────────────────────────────────────────┤
│ LAYER 4: COGNITION (35% weight)                             │
│   Field Completeness: {fields_present}/4 ({field_completeness:.0%})                            │
│   Mechanism Quality: {score.cognition.mechanism_score:>5.1f}/10                              │
│   Measurability: {score.cognition.measurable_outcome_score:>5.1f}/10                                  │
│   Boundary Precision: {score.cognition.boundary_condition_score:>5.1f}/10                              │
│   Failure Specificity: {score.cognition.failure_condition_score:>5.1f}/10                              │
│   Constraint Adherence: {score.cognition.constraint_adherence:>5.1%}                              │
│   ─────────────────────────────────────────────────────────│
│   COGNITION SCORE: {composites['cognition_quality']:>5.3f}                                    │
├─────────────────────────────────────────────────────────────┤
│ LAYER 3: INTEGRATION (20% weight)                           │
│   IIT Phi: {score.integration.iit_phi:>10.4f}                                  │
│   Neural Complexity: {score.integration.neural_complexity:>10.4f}                          │
│   Causal Density: {score.integration.causal_density:>10.4f}                              │
│   ─────────────────────────────────────────────────────────│
│   INTEGRATION SCORE: {composites['integration_quality']:>5.3f}                                │
├─────────────────────────────────────────────────────────────┤
│ LAYER 2: QUANTUM STATE (25% weight)                         │
│   State Fidelity: {score.state.state_fidelity:>10.4f}                            │
│   Von Neumann Entropy: {score.state.von_neumann_entropy:>10.4f}                      │
│   Entanglement Entropy: {score.state.entanglement_entropy:>10.4f}                      │
│   Purity: {score.state.purity:>10.4f}                                        │
│   ─────────────────────────────────────────────────────────│
│   STATE SCORE: {composites['state_quality']:>5.3f}                                        │
├─────────────────────────────────────────────────────────────┤
│ LAYER 1: HARDWARE (20% weight)                              │
│   Layer Fidelity: {score.hardware.layer_fidelity:>10.4f}                          │
│   CLOPS_h: {score.hardware.clops_h:>10.1f}                                    │
│   Backend Quality: {score.hardware.backend_quality:>10.4f}                          │
│   ─────────────────────────────────────────────────────────│
│   HARDWARE SCORE: {composites['hardware_quality']:>5.3f}                                   │
├─────────────────────────────────────────────────────────────┤
│ TOTAL QAGI SCORE: {composites['total_qagi_score']:>5.3f}                                    │
│ STRUCTURAL SCORE: {composites['structural_score']:>5.1f}/10                                 │
├─────────────────────────────────────────────────────────────┤
│ SECONDARY: MODEL-CONDITIONED SIGNALS (NOT quality metrics)  │
│   Raw Phi Coherence: {score.alignment.raw_phi_coherence:>10.4f} (model-conditioned)     │
│   Raw Biomimetic: {score.alignment.raw_biomimetic_resonance:>10.4f} (model-conditioned)   │
│   Z-Phi Coherence: {score.alignment.z_phi_coherence:>10.4f} (normalized)              │
│   Z-Biomimetic: {score.alignment.z_biomimetic_resonance:>10.4f} (normalized)            │
│   Cross-Model Comparable: {str(score.alignment.cross_model_comparable):<5}                    │
│   Baseline Version: {score.alignment.model_baseline_version:<20}             │
│   Information Density: {score.alignment.information_density:>10.4f} (concepts/token)     │
├─────────────────────────────────────────────────────────────┤
│ EXTRACTED FIELD SPANS (for audit):                          │
│   Mechanism: {score.cognition.mechanism_text[:50] if score.cognition.mechanism_text else 'N/A':<50}│
│   Outcome: {score.cognition.measurable_outcome_text[:50] if score.cognition.measurable_outcome_text else 'N/A':<51}│
│   Boundary: {score.cognition.boundary_condition_text[:50] if score.cognition.boundary_condition_text else 'N/A':<50}│
│   Failure: {score.cognition.failure_condition_text[:50] if score.cognition.failure_condition_text else 'N/A':<51}│
└─────────────────────────────────────────────────────────────┘
"""
        return dashboard


# =============================================================================
# RELEASE GATE THRESHOLDS
# =============================================================================

DEFAULT_THRESHOLDS = {
    # Hard gates (operationally trusted)
    'field_completeness': 0.75,  # At least 3/4 fields present
    'constraint_adherence': 0.8,  # 80% of constraints met
    'provider_purity': 0.9,  # Clean runs preferred
    
    # Soft gates (need baseline runs)
    'hardware_quality': 0.5,  # Minimum hardware quality
    'state_quality': 0.5,  # Minimum state quality
    'integration_quality': 0.3,  # Minimum integration
    
    # Primary quality gate
    'cognition_quality': 0.6,  # Minimum cognition (highest weight)
    'structural_score': 5.0,  # Minimum structural rubric (out of 10)
    'total_qagi_score': 0.5,  # Minimum total score
}

# Version-specific thresholds for historical comparison
THRESHOLDS_V1 = DEFAULT_THRESHOLDS.copy()
THRESHOLDS_V1['score_version'] = 'qagi_metrics_v1'


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    # Example: Evaluate a response
    evaluator = QAGIEvaluator()
    
    test_response = """
    Mechanism: The system uses a hierarchical network of interconnected neurons 
    to store and retrieve information in parallel.
    Outcome: Information is encoded in multiple synaptic pathways, achieving 
    85% retrieval accuracy under normal conditions.
    Boundary condition: The network is limited by the number of available neurons 
    (maximum 10^6) and synaptic connections per neuron (maximum 10^4).
    Failure condition: Memory retrieval fails when the input cues are insufficient 
    (less than 3 active pathways) or ambiguous (overlap > 70%).
    """
    
    constraints = [
        {'name': 'no_metaphor', 'check': lambda t: not any(w in t.lower() for w in ['like', 'akin to', 'similar to', 'mirrors'])},
        {'name': 'four_sentences', 'check': lambda t: t.count('.') >= 4},
    ]
    
    score = evaluator.evaluate(
        response_text=test_response,
        constraints=constraints,
        model="test-model",
        provider="test-provider",
        run_id="test-run-001",
        provider_purity=1.0,
        fallback_used=False,
        run_mode="standard"
    )
    
    print(evaluator.get_dashboard(score))
    print("\nJSON Export:")
    print(score.to_json())
    
    # Check thresholds
    passed, failures = score.meets_thresholds(DEFAULT_THRESHOLDS)
    print(f"\nRelease Gate: {'PASSED' if passed else 'FAILED'}")
    if failures:
        for f in failures:
            print(f"  - {f}")
    
    # Show extracted field spans for audit
    print("\nExtracted Field Spans (for audit):")
    print(f"  Mechanism: {score.cognition.mechanism_text[:80]}...")
    print(f"  Outcome: {score.cognition.measurable_outcome_text[:80]}...")
    print(f"  Boundary: {score.cognition.boundary_condition_text[:80]}...")
    print(f"  Failure: {score.cognition.failure_condition_text[:80]}...")