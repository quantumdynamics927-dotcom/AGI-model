#!/usr/bin/env python3
"""
Test QAGI Intelligence Score Validator Integration
==================================================

Tests the qagi_validator module to ensure it integrates correctly
with AGI-model runtime evaluation.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from qagi_intelligence_metrics import (
    QAGIEvaluator,
    QAGIIntelligenceScore,
    DEFAULT_THRESHOLDS,
    calculate_information_density,
)
from agi_model.qagi_validator import (
    evaluate_response,
    compare_with_prior,
    run_qagi_validation,
    _generate_run_id,
)


def test_structural_field_detector():
    """Test the structural field detector."""
    print("\n" + "="*60)
    print("TEST: Structural Field Detector")
    print("="*60)
    
    from qagi_intelligence_metrics import StructuralFieldDetector
    
    detector = StructuralFieldDetector()
    
    # Test response with all four fields
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
    
    cognition = detector.analyze(test_response)
    
    print(f"Mechanism Score: {cognition.mechanism_score:.1f}/10")
    print(f"Measurable Outcome Score: {cognition.measurable_outcome_score:.1f}/10")
    print(f"Boundary Condition Score: {cognition.boundary_condition_score:.1f}/10")
    print(f"Failure Condition Score: {cognition.failure_condition_score:.1f}/10")
    print(f"Structural Score: {cognition.structural_score():.1f}/10")
    
    # Check extracted spans
    print(f"\nExtracted Mechanism: {cognition.mechanism_text[:60]}...")
    print(f"Extracted Outcome: {cognition.measurable_outcome_text[:60]}...")
    
    assert cognition.mechanism_score > 0, "Mechanism should be detected"
    assert cognition.measurable_outcome_score > 0, "Outcome should be detected"
    assert cognition.boundary_condition_score > 0, "Boundary should be detected"
    assert cognition.failure_condition_score > 0, "Failure should be detected"
    
    print("\n✓ Structural field detector working correctly")


def test_constraint_checker():
    """Test the constraint checker."""
    print("\n" + "="*60)
    print("TEST: Constraint Checker")
    print("="*60)
    
    from qagi_intelligence_metrics import StructuralFieldDetector
    
    detector = StructuralFieldDetector()
    
    # Test response with metaphors (should fail constraint)
    metaphor_response = """
    The system is like a brain, using neural pathways akin to highways.
    It achieves 90% accuracy, similar to how nature optimizes.
    """
    
    # Test response without metaphors (should pass constraint)
    clean_response = """
    The system uses hierarchical neural networks for distributed memory.
    It achieves 90% retrieval accuracy with 10^6 neurons maximum.
    """
    
    constraints = [
        {'name': 'no_metaphor', 'check': lambda t: not any(w in t.lower() for w in ['like', 'akin', 'similar to', 'mirrors'])},
        {'name': 'has_numbers', 'check': lambda t: any(c.isdigit() for c in t)},
    ]
    
    # Check metaphor response
    adherence, violations = detector.check_constraints(metaphor_response, constraints)
    print(f"Metaphor response adherence: {adherence:.1%}")
    print(f"Violations: {violations}")
    assert adherence < 1.0, "Should detect metaphor violation"
    
    # Check clean response
    adherence, violations = detector.check_constraints(clean_response, constraints)
    print(f"\nClean response adherence: {adherence:.1%}")
    print(f"Violations: {violations}")
    assert adherence == 1.0, "Should pass all constraints"
    
    print("\n✓ Constraint checker working correctly")


def test_qagi_evaluator():
    """Test the full QAGI evaluator."""
    print("\n" + "="*60)
    print("TEST: QAGI Evaluator")
    print("="*60)
    
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
        {'name': 'no_metaphor', 'check': lambda t: not any(w in t.lower() for w in ['like', 'akin', 'similar to', 'mirrors'])},
        {'name': 'has_four_fields', 'check': lambda t: all(w in t.lower() for w in ['mechanism', 'outcome', 'boundary', 'fail'])},
    ]
    
    score = evaluator.evaluate(
        response_text=test_response,
        constraints=constraints,
        model="test-model",
        provider="test-provider",
        run_id="test-run-001",
        provider_purity=1.0,
        fallback_used=False,
        run_mode="standard",
    )
    
    print(f"Score Version: {score.score_version}")
    print(f"Model: {score.model}")
    print(f"Provider: {score.provider}")
    print(f"Run Mode: {score.run_mode}")
    print(f"Provider Purity: {score.provider_purity}")
    print(f"Fallback Used: {score.fallback_used}")
    
    composites = score.compute_composite()
    print(f"\nComposite Scores:")
    for key, value in composites.items():
        print(f"  {key}: {value:.4f}")
    
    print(f"\nStructural Score: {score.cognition.structural_score():.1f}/10")
    print(f"Constraint Adherence: {score.cognition.constraint_adherence:.1%}")
    print(f"Constraint Violations: {score.cognition.constraint_violations}")
    
    # Check thresholds
    passed, failures = score.meets_thresholds(DEFAULT_THRESHOLDS)
    print(f"\nRelease Gate: {'PASSED' if passed else 'FAILED'}")
    if failures:
        for f in failures:
            print(f"  - {f}")
    
    print("\n✓ QAGI evaluator working correctly")


def test_qagi_validator():
    """Test the QAGI validator integration."""
    print("\n" + "="*60)
    print("TEST: QAGI Validator Integration")
    print("="*60)
    
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
    
    score, gate_result = evaluate_response(
        response_text=test_response,
        model="test-model",
        provider="test-provider",
        save_artifact=False,  # Don't save for test
    )
    
    print(f"Run ID: {score.run_id}")
    print(f"Passed: {gate_result['passed']}")
    print(f"Field Completeness: {gate_result['field_completeness']:.0%}")
    print(f"Constraint Adherence: {gate_result['constraint_adherence']:.1%}")
    
    if gate_result['failures']:
        print(f"Failures: {gate_result['failures']}")
    
    assert gate_result['field_completeness'] >= 0.75, "Should have at least 3/4 fields"
    
    print("\n✓ QAGI validator integration working correctly")


def test_information_density():
    """Test information density calculation."""
    print("\n" + "="*60)
    print("TEST: Information Density")
    print("="*60)
    
    # Dense response
    dense_response = """
    The quantum VAE uses hierarchical latent encoding with 128-dimensional input
    and 32-dimensional latent space. The system achieves 0.95 fidelity with
    coherence time of 100 microseconds. Error correction uses surface codes
    with threshold of 1% gate error rate.
    """
    
    # Sparse response
    sparse_response = """
    The system works well. It does things. There are some results.
    The output is good. Everything is fine.
    """
    
    dense_density = calculate_information_density(dense_response)
    sparse_density = calculate_information_density(sparse_response)
    
    print(f"Dense response density: {dense_density:.4f}")
    print(f"Sparse response density: {sparse_density:.4f}")
    
    assert dense_density > sparse_density, "Dense response should have higher information density"
    
    print("\n✓ Information density calculation working correctly")


def test_dashboard_output():
    """Test dashboard output."""
    print("\n" + "="*60)
    print("TEST: Dashboard Output")
    print("="*60)
    
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
    
    score = evaluator.evaluate(
        response_text=test_response,
        model="glm-5",
        provider="ollama-cloud",
        run_id="test-dashboard-001",
    )
    
    dashboard = evaluator.get_dashboard(score)
    print(dashboard)
    
    print("\n✓ Dashboard output working correctly")


def run_all_tests():
    """Run all tests."""
    print("="*60)
    print("QAGI Intelligence Score Validator Test Suite")
    print("="*60)
    
    tests = [
        test_structural_field_detector,
        test_constraint_checker,
        test_qagi_evaluator,
        test_qagi_validator,
        test_information_density,
        test_dashboard_output,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"\n✗ Test failed: {e}")
            failed += 1
        except Exception as e:
            print(f"\n✗ Test error: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("="*60)
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(run_all_tests())