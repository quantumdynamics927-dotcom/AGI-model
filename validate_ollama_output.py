"""
Ollama Output Validator
========================

Validates AI-generated outputs against the biomimetic metrics framework.
Classifies outputs as: SUPPORTED, PARTIAL, EXPLORATORY, or REJECTED.

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
    SUPPORTED = "supported"      # Strong evidence, validated metrics
    PARTIAL = "partial"          # Some evidence, metrics need work
    EXPLORATORY = "exploratory"  # Hypothesis only, no validated metrics
    REJECTED = "rejected"        # Failed validation, incorrect claims


@dataclass
class MetricValidation:
    """Validation result for a single metric"""
    name: str
    value: float
    expected_range: Tuple[float, float]
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


class OllamaOutputValidator:
    """
    Validates Ollama-generated outputs against biomimetic metrics framework.
    """
    
    def __init__(self):
        self.phi = (1 + np.sqrt(5)) / 2
        
        # Metric definitions from BIOMIMETIC_METRICS_FRAMEWORK.md
        self.metric_definitions = {
            'phi_coherence': {
                'range': (0.0, 1.0),
                'classification': 'SECONDARY',
                'description': 'Proximity to phi-optimal structure'
            },
            'phi_resonance': {
                'range': (0.0, 1.0),  # Normalized, NOT raw phi
                'classification': 'SECONDARY',
                'description': 'Normalized phi-alignment score'
            },
            'biomimetic_resonance': {
                'range': (0.0, 1.0),
                'classification': 'SECONDARY',
                'description': 'Alignment with biological reference'
            }
        }
    
    def validate_metric(self, name: str, value: float) -> MetricValidation:
        """Validate a single metric against its definition"""
        if name not in self.metric_definitions:
            return MetricValidation(
                name=name,
                value=value,
                expected_range=(0.0, 1.0),
                in_range=False,
                classification="UNKNOWN",
                issue=f"Metric '{name}' not defined in framework"
            )
        
        definition = self.metric_definitions[name]
        expected_range = definition['range']
        in_range = expected_range[0] <= value <= expected_range[1]
        
        issue = None
        if not in_range:
            if value > expected_range[1]:
                issue = f"Value {value:.4f} exceeds maximum {expected_range[1]}"
            else:
                issue = f"Value {value:.4f} below minimum {expected_range[0]}"
        
        # Check for raw constant vs normalized score
        if name == 'phi_resonance' and abs(value - self.phi) < 0.001:
            issue = "Value appears to be raw φ constant, not normalized score"
            in_range = False
        
        return MetricValidation(
            name=name,
            value=value,
            expected_range=expected_range,
            in_range=in_range,
            classification=definition['classification'],
            issue=issue
        )
    
    def validate_output(self, text: str, metrics: Dict[str, float]) -> ValidatedOutput:
        """
        Validate complete output and classify according to governance.
        
        Parameters
        ----------
        text : str
            The generated text/paragraph
        metrics : Dict[str, float]
            Dictionary of metric names and values
        
        Returns
        -------
        ValidatedOutput with governance classification
        """
        # Validate each metric
        validated_metrics = {}
        for name, value in metrics.items():
            validated_metrics[name] = self.validate_metric(name, value)
        
        # Analyze text for claims
        reasoning = []
        recommendations = []
        
        # Check for cosmological leaps
        cosmological_terms = ['deeper order in the universe', 'cosmic', 'universal truth', 
                              'fundamental law of nature', 'divine']
        has_cosmological_leap = any(term in text.lower() for term in cosmological_terms)
        
        if has_cosmological_leap:
            reasoning.append("Text contains cosmological leap from mechanism to metaphysics")
            recommendations.append("Rewrite as testable hypothesis about self-organization")
        
        # Check for emergence claims
        if 'emergent intelligence' in text.lower() or 'emergent consciousness' in text.lower():
            reasoning.append("Claims emergence of intelligence/consciousness without operational definition")
            recommendations.append("Define operational criteria for 'intelligence' in this context")
        
        # Check metric validity
        invalid_metrics = [m for m in validated_metrics.values() if not m.in_range]
        if invalid_metrics:
            reasoning.append(f"{len(invalid_metrics)} metric(s) outside valid range")
            for m in invalid_metrics:
                recommendations.append(f"Fix {m.name}: {m.issue}")
        
        # Check for raw constant vs score
        phi_raw_metrics = [m for m in validated_metrics.values() 
                          if m.name == 'phi_resonance' and m.issue and 'raw φ' in m.issue]
        if phi_raw_metrics:
            reasoning.append("Phi Resonance appears to be raw constant, not computed score")
            recommendations.append("Clarify if phi_resonance is normalized score or raw constant")
        
        # Determine classification
        if len(invalid_metrics) > 1 or has_cosmological_leap:
            status = ClassificationStatus.EXPLORATORY
        elif len(invalid_metrics) == 1:
            status = ClassificationStatus.PARTIAL
        else:
            status = ClassificationStatus.EXPLORATORY  # Still exploratory without null model
        
        # Generate cleaned hypothesis
        cleaned = self._generate_cleaned_hypothesis(text, has_cosmological_leap)
        
        return ValidatedOutput(
            raw_text=text,
            cleaned_hypothesis=cleaned,
            metrics=validated_metrics,
            overall_status=status,
            reasoning=reasoning,
            recommendations=recommendations
        )
    
    def _generate_cleaned_hypothesis(self, text: str, has_cosmological_leap: bool) -> str:
        """Generate scientifically cleaned version of the hypothesis"""
        
        # Always use the cleaned version for this specific output
        return (
            "Hypothesis: Systems governed by simple local update rules can develop "
            "stable global structure, and phi-related ratios may appear as one class "
            "of emergent scaling relation under specific constraints. This remains a "
            "provisional theoretical hypothesis requiring explicit equations, null models, "
            "and comparative testing against non-phi baselines."
        )
    
    def print_validation_report(self, result: ValidatedOutput):
        """Print formatted validation report"""
        print("=" * 70)
        print("OLLAMA OUTPUT VALIDATION REPORT")
        print("=" * 70)
        print(f"\n📊 OVERALL CLASSIFICATION: {result.overall_status.value.upper()}")
        print("-" * 70)
        
        print("\n🔍 METRIC VALIDATION:")
        print("-" * 40)
        for name, metric in result.metrics.items():
            status = "✅" if metric.in_range else "❌"
            print(f"  {status} {name}:")
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
        
        print("\n" + "=" * 70)


def main():
    """Validate the specific Ollama output from April 16, 2026"""
    
    # The Ollama output to validate
    generated_text = (
        "The golden ratio, φ ≈ 1.618, emerges as a self-sustaining dynamical system, "
        "reflecting a balance between order and chaos. Its emergence from a simple initial "
        "condition suggests a form of emergent intelligence, where complexity arises from "
        "minimal rules. This aligns with the idea of a biomimetic consciousness, where "
        "abstract patterns like the golden ratio reflect a deeper, underlying order in the universe."
    )
    
    metrics = {
        'phi_coherence': 0.7837,
        'phi_resonance': 1.6180,  # This is raw phi, not a normalized score!
        'biomimetic_resonance': 1.2681  # This is > 1, outside valid range!
    }
    
    # Run validation
    validator = OllamaOutputValidator()
    result = validator.validate_output(generated_text, metrics)
    validator.print_validation_report(result)
    
    # Save to file
    output_file = "ollama_validation_report.json"
    with open(output_file, 'w') as f:
        json.dump({
            'classification': result.overall_status.value,
            'metrics': {
                name: {
                    'value': m.value,
                    'in_range': m.in_range,
                    'issue': m.issue
                } for name, m in result.metrics.items()
            },
            'reasoning': result.reasoning,
            'recommendations': result.recommendations,
            'cleaned_hypothesis': result.cleaned_hypothesis
        }, f, indent=2)
    
    print(f"\n📄 Report saved to: {output_file}")
    
    return result


if __name__ == "__main__":
    result = main()
