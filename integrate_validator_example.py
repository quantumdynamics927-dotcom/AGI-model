"""
Example Integration of Ollama Output Validator into Workflow
============================================================

Demonstrates how to make validation mandatory for all model outputs.

Usage:
    python integrate_validator_example.py --text "generated text" --metrics '{"phi_coherence": -0.8695}'
"""

import argparse
import json
from validate_ollama_output_v2 import OllamaOutputValidator, ClassificationStatus


def validate_model_output(text: str, metrics: dict, model: str = "unknown") -> dict:
    """
    Mandatory validation function for all model outputs.
    
    Parameters
    ----------
    text : str
        Generated text from model
    metrics : dict
        Dictionary of metric names and values
    model : str
        Model identifier
    
    Returns
    -------
    dict
        Validation results with classification and recommendations
    """
    validator = OllamaOutputValidator()
    result = validator.validate_output(text, metrics, model)
    
    # Log to audit trail
    print(f"🔍 VALIDATION RESULT: {result.overall_status.value.upper()}")
    
    # Apply hard rules
    invalid_metrics = [m for m in result.metrics.values() if not m.in_range]
    raw_constants = [m for m in result.metrics.values() 
                     if m.metric_type.value == 'raw_constant']
    
    if invalid_metrics or raw_constants:
        print("⚠️  HARD RULE APPLIED: Metric section labeled 'diagnostic_only'")
        print("🚫 Exclude metrics from evidence claims")
    
    # Print recommendations
    if result.recommendations:
        print("\n💡 RECOMMENDATIONS:")
        for rec in result.recommendations:
            print(f"  • {rec}")
    
    return {
        'classification': result.overall_status.value,
        'text_approved': result.overall_status != ClassificationStatus.REJECTED,
        'metrics_usable': len(invalid_metrics) == 0 and len(raw_constants) == 0,
        'metric_label': 'diagnostic_only' if (invalid_metrics or raw_constants) else 'validated_metrics'
    }


def main():
    parser = argparse.ArgumentParser(description='Validate AI-generated output')
    parser.add_argument('--text', required=True, help='Generated text')
    parser.add_argument('--metrics', required=True, help='JSON string of metrics')
    parser.add_argument('--model', default='unknown', help='Model identifier')
    
    args = parser.parse_args()
    
    try:
        metrics = json.loads(args.metrics)
    except json.JSONDecodeError as e:
        print(f"Error parsing metrics: {e}")
        return
    
    # Validate output
    result = validate_model_output(args.text, metrics, args.model)
    
    print(f"\n📋 FINAL DISPOSITION:")
    print(f"  Text approved for use: {'✅ YES' if result['text_approved'] else '❌ NO'}")
    print(f"  Metrics usable as evidence: {'✅ YES' if result['metrics_usable'] else '❌ NO'}")
    print(f"  Metric section label: {result['metric_label']}")
    
    # Save to audit trail
    with open('validation_audit_trail.log', 'a') as f:
        f.write(f"{result['classification']} | {result['metric_label']} | {args.model}\n")


if __name__ == "__main__":
    # Example usage with our validated outputs
    example_text = (
        "Hypothesis: decentralized systems with simple local adaptation rules "
        "may converge toward globally efficient connectivity regimes, and phi-related "
        "scaling may appear as an emergent statistical attractor rather than a "
        "programmed target. This should be tested against randomized-update null "
        "models and non-phi baselines before any strong claim is made."
    )
    
    example_metrics = {
        'phi_coherence': -0.8695,
        'phi_resonance': 1.6180,
        'biomimetic_resonance': -1.4069
    }
    
    print("🧪 TESTING WITH EXAMPLE OUTPUT...")
    validate_model_output(example_text, example_metrics, "qwen3-coder:480b")