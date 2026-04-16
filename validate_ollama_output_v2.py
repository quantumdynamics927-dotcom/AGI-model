"""
Ollama Output Validator v2
==========================

Enhanced validator with semantic metric typing and improved classification.
Handles signed polarity diagnostics vs normalized scores.

Date: April 16, 2026
Governance: BIOMIMETIC_METRICS_FRAMEWORK.md
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from enum import Enum
import json


class ClassificationStatus(Enum):
    """Governance classification levels"""
    SUPPORTED = "supported"
    PARTIAL = "partial"
    EXPLORATORY = "exploratory"
    REJECTED = "rejected"


class MetricType(Enum):
    """Semantic types for metrics"""
    NORMALIZED_SCORE = "normalized_score"
    SIGNED_POLARITY = "signed_polarity"
    RAW_CONSTANT = "raw_constant"
    UNBOUNDED = "unbounded"


@dataclass
class MetricValidation:
    """Validation result for a single metric"""
    name: str
    value: float
    expected_range: Tuple[float, float]
    metric_type: MetricType
    in_range: bool
    classification: str
    issue: Optional[str] = None


@dataclass
class ValidatedOutput:
    """Fully validated output with governance classification"""
    raw_text: str
    cleaned_hypothesis: str
    metrics: Dict[str, MetricValidation]
    overall_status: ClassificationStatus
    reasoning: List[str]
    recommendations: List[str]
    recommended_post: str


class OllamaOutputValidator:
    """Validates Ollama-generated outputs against biomimetic metrics framework."""
    
    def __init__(self):
        self.phi = (1 + np.sqrt(5)) / 2
        
        # Metric definitions with semantic types
        self.metric_definitions = {
            'phi_coherence': {
                'range': (0.0, 1.0),
                'alt_range': (-1.0, 1.0),
                'classification': 'SECONDARY',
                'default_type': MetricType.NORMALIZED_SCORE,
                'alt_type': MetricType.SIGNED_POLARITY,
            },
            'phi_resonance': {
                'range': (0.0, 1.0),
                'classification': 'SECONDARY',
                'default_type': MetricType.NORMALIZED_SCORE,
            },
            'biomimetic_resonance': {
                'range': (0.0, 1.0),
                'alt_range': (-1.0, 1.0),
                'classification': 'SECONDARY',
                'default_type': MetricType.NORMALIZED_SCORE,
                'alt_type': MetricType.SIGNED_POLARITY,
            }
        }
    
    def validate_metric(self, name: str, value: float,
                       forced_type: Optional[MetricType] = None) -> MetricValidation:
        """Validate a single metric against its definition."""
        if name not in self.metric_definitions:
            return MetricValidation(
                name=name, value=value, expected_range=(0.0, 1.0),
                metric_type=MetricType.UNBOUNDED, in_range=False,
                classification="UNKNOWN",
                issue=f"Metric '{name}' not defined in framework"
            )
        
        definition = self.metric_definitions[name]
        
        # Determine metric type
        if forced_type:
            metric_type = forced_type
            expected_range = definition.get('alt_range', definition['range'])
        else:
            metric_type = definition['default_type']
            expected_range = definition['range']
        
        in_range = expected_range[0] <= value <= expected_range[1]
        
        issue = None
        if not in_range:
            if value > expected_range[1]:
                issue = f"Value {value:.4f} exceeds maximum {expected_range[1]}"
            else:
                issue = f"Value {value:.4f} below minimum {expected_range[0]}"
        
        # Check for raw constant vs score
        if name == 'phi_resonance' and abs(value - self.phi) < 0.001:
            issue = "Value appears to be raw φ constant, not normalized score"
            in_range = False
            metric_type = MetricType.RAW_CONSTANT
        
        return MetricValidation(
            name=name, value=value, expected_range=expected_range,
            metric_type=metric_type, in_range=in_range,
            classification=definition['classification'], issue=issue
        )
    
    def validate_output(self, text: str, metrics: Dict[str, float],
                       model: str = "unknown") -> ValidatedOutput:
        """Validate complete output and classify according to governance."""
        
        # Auto-detect metric types based on values
        validated_metrics = {}
        for name, value in metrics.items():
            # If value is negative, assume signed polarity
            if value < 0 and name in self.metric_definitions:
                forced = MetricType.SIGNED_POLARITY
            else:
                forced = None
            validated_metrics[name] = self.validate_metric(name, value, forced)
        
        # Analyze text for claims
        reasoning = []
        recommendations = []
        
        # Check for null model mention (positive)
        if 'null model' in text.lower() or 'null models' in text.lower():
            reasoning.append("Text explicitly mentions null models (scientific best practice)")
        else:
            recommendations.append("Add explicit null model comparison requirement")
        
        # Check for mechanistic explanation
        if 'local' in text.lower() and ('rule' in text.lower() or 'update' in text.lower()):
            reasoning.append("Provides mechanistic explanation (local rules)")
        
        # Check for cautious language
        cautious_terms = ['hypothesis', 'may', 'might', 'could', 'provisional',
                         'requires testing', 'suggests']
        has_cautious_language = any(term in text.lower() for term in cautious_terms)
        
        if has_cautious_language:
            reasoning.append("Uses cautious/hypothesis-level language")
        
        # Check for cosmological leaps
        cosmological_terms = ['deeper order in the universe', 'cosmic', 'universal truth',
                              'fundamental law of nature', 'divine', 'proof of consciousness']
        has_cosmological_leap = any(term in text.lower() for term in cosmological_terms)
        
        if has_cosmological_leap:
            reasoning.append("Text contains cosmological leap from mechanism to metaphysics")
            recommendations.append("Remove cosmological claims, keep to testable mechanisms")
        
        # Check metric validity
        invalid_metrics = [m for m in validated_metrics.values() if not m.in_range]
        raw_constants = [m for m in validated_metrics.values()
                        if m.metric_type == MetricType.RAW_CONSTANT]
        
        if invalid_metrics:
            reasoning.append(f"{len(invalid_metrics)} metric(s) outside valid range")
            for m in invalid_metrics:
                if m.issue:
                    recommendations.append(f"Fix {m.name}: {m.issue}")
        
        if raw_constants:
            reasoning.append(f"{len(raw_constants)} metric(s) appear to be raw constants")
            recommendations.append("Distinguish raw constants from computed scores in labeling")
        
        # Model-specific warning
        if 'qwen' in model.lower():
            recommendations.append("qwen models show sensitivity to phi vocabulary - verify reproducibility")
        
        # Determine classification
        has_null_model = 'null model' in text.lower()
        is_mechanistic = 'local' in text.lower() and 'rule' in text.lower()
        
        if has_cosmological_leap or len(invalid_metrics) > 1:
            status = ClassificationStatus.EXPLORATORY
        elif len(invalid_metrics) == 1 and has_null_model and is_mechanistic:
            status = ClassificationStatus.PARTIAL
        elif len(invalid_metrics) == 0 and has_null_model and is_mechanistic:
            status = ClassificationStatus.EXPLORATORY
        else:
            status = ClassificationStatus.EXPLORATORY
        
        # Generate outputs
        cleaned = self._generate_cleaned_hypothesis(text, has_cosmological_leap)
        recommended_post = self._generate_recommended_post(text, has_null_model, is_mechanistic)
        
        return ValidatedOutput(
            raw_text=text, cleaned_hypothesis=cleaned,
            metrics=validated_metrics, overall_status=status,
            reasoning=reasoning, recommendations=recommendations,
            recommended_post=recommended_post
        )
    
    def _generate_cleaned_hypothesis(self, text: str, has_cosmological_leap: bool) -> str:
        """Generate scientifically cleaned version of the hypothesis."""
        return (
            "Hypothesis: Systems governed by simple local update rules can develop "
            "stable global structure, and phi-related ratios may appear as one class "
            "of emergent scaling relation under specific constraints. This remains a "
            "provisional theoretical hypothesis requiring explicit equations, null models, "
            "and comparative testing against non-phi baselines."
        )
    
    def _generate_recommended_post(self, text: str, has_null_model: bool,
                                   is_mechanistic: bool) -> str:
        """Generate recommended social media version."""
        base = (
            "Hypothesis: decentralized systems with simple local adaptation rules "
            "may converge toward globally efficient connectivity regimes, and phi-related "
            "scaling may appear as an emergent statistical attractor rather than a "
            "programmed target."
        )
        
        if has_null_model:
            base += " This should be tested against randomized-update null models and non-phi baselines before any strong claim is made."
        
        return base
    
    def print_validation_report(self, result: ValidatedOutput):
        """Print formatted validation report."""
        print("=" * 70)
        print("OLLAMA OUTPUT VALIDATION REPORT")
        print("=" * 70)
        print(f"\n📊 OVERALL CLASSIFICATION: {result.overall_status.value.upper()}")
        print("-" * 70)
        
        print("\n🔍 METRIC VALIDATION:")
        print("-" * 40)
        for name, metric in result.metrics.items():
            status = "✅" if metric.in_range else "❌"
            type_label = f"[{metric.metric_type.value}]"
            print(f"  {status} {name} {type_label}:")
            print(f"     Value: {metric.value:.4f}")
            print(f"     Range: [{metric.expected_range[0]}, {metric.expected_range[1]}]")
            print(f"     Class: {metric.classification}")
            if metric.issue:
                print(f"     Issue: {metric.issue}")
            print()
        
        print("\n📝 REASONING:")
        print("-" * 40)
        for reason in result.reasoning:
            print(f"  • {reason}")
        
        print("\n💡 RECOMMENDATIONS:")
        print("-" * 40)
        for rec in result.recommendations:
            print(f"  • {rec}")
        
        print("\n✏️  CLEANED HYPOTHESIS:")
        print("-" * 40)
        print(f"  {result.cleaned_hypothesis}")
        
        print("\n📱 RECOMMENDED POST VERSION:")
        print("-" * 40)
        print(f"  {result.recommended_post}")
        
        print("\n" + "=" * 70)


def validate_qwen3_coder_output():
    """Validate the qwen3-coder:480b output from April 16, 2026."""
    
    generated_text = (
        "Emergent Stability in Simple Systems: A Biomimetic Perspective\n\n"
        "Consider a distributed network of agents following only these local rules:\n\n"
        "Each node adjusts its state based on the weighted average of its immediate neighbors\n"
        "Connections strengthen when nodes synchronize, weaken when they diverge\n"
        "Energy expenditure increases with deviation from local equilibrium\n"
        "Under these minimal constraints, something remarkable emerges: the system naturally "
        "evolves toward configurations where global connectivity patterns exhibit scaling ratios "
        "clustered around φ = 1.618034. This isn't programmed—the ratio appears as a statistical "
        "attractor in the phase space of possible network topologies.\n\n"
        "The biomimetic intelligence here lies in recognizing that φ emerges not as a target, "
        "but as a fingerprint of optimal balance between integration and segregation. Like how "
        "leaves arrange themselves to maximize sunlight exposure while minimizing structural "
        "cost, or how neural networks self-organize critical connectivity patterns, this system "
        "discovers that φ-related scaling represents a sweet spot where information flows "
        "efficiently without collapsing into chaos or rigidity.\n\n"
        "Testing this hypothesis requires constructing null models—identical systems with "
        "randomized update rules—and comparing the distribution of emergent scaling ratios "
        "against a baseline of non-φ values. Only through such comparative analysis can we "
        "determine whether φ's appearance reflects genuine organizational principles or mere "
        "mathematical coincidence.\n\n"
        "The deeper insight: consciousness might not require φ, but complex adaptive systems "
        "that could support consciousness may naturally gravitate toward φ-structured solutions."
    )
    
    metrics = {
        'phi_coherence': -0.8695,      # Negative - signed polarity
        'phi_resonance': 1.6180,       # Raw phi constant
        'biomimetic_resonance': -1.4069  # Negative but exceeds -1
    }
    
    validator = OllamaOutputValidator()
    result = validator.validate_output(generated_text, metrics, model="qwen3-coder:480b")
    validator.print_validation_report(result)
    
    # Save report
    output_file = "ollama_validation_report_v2.json"
    with open(output_file, 'w') as f:
        json.dump({
            'classification': result.overall_status.value,
            'metrics': {
                name: {
                    'value': m.value,
                    'metric_type': m.metric_type.value,
                    'in_range': m.in_range,
                    'issue': m.issue
                } for name, m in result.metrics.items()
            },
            'reasoning': result.reasoning,
            'recommendations': result.recommendations,
            'cleaned_hypothesis': result.cleaned_hypothesis,
            'recommended_post': result.recommended_post
        }, f, indent=2)
    
    print(f"\n📄 Report saved to: {output_file}")
    
    return result


if __name__ == "__main__":
    result = validate_qwen3_coder_output()
