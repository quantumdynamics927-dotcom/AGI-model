#!/usr/bin/env python3
"""
VCapture Golden Test Suite v1.0
==============================

Frozen historical assessments that must always produce the same canonical
decision under the same policy version.

This ensures the governance system is reproducible and regression-safe.

Golden tests include:
- Known-good assessments with expected outputs
- Edge cases (boundary values, warnings, failures)
- Adversarial cases (out-of-range, missing data)
- Version compatibility checks

Usage:
    python vcapture_golden_tests.py --run
    python vcapture_golden_tests.py --update  # Update expected outputs
"""

import json
import hashlib
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import unittest
import tempfile
import shutil

# Import governance modules
from vcapture_canonical_schema import (
    CanonicalGovernanceOutput,
    CalibrationState,
    GateStatus,
    RecommendedAction,
    GateSummary,
)
from vcapture_metric_schema import MetricSchema, validate_metric


# =============================================================================
# GOLDEN TEST CASES
# =============================================================================

@dataclass
class GoldenTestCase:
    """
    A frozen test case with known input and expected output.
    
    The test passes if the canonical output matches the expected output
    under the same policy version.
    """
    name: str
    description: str
    policy_version: str
    input_assessment: Dict[str, Any]
    expected_output: Dict[str, Any]
    expected_gate_counts: Dict[str, int]
    expected_state: str
    expected_action: str
    tags: List[str]  # e.g., ["edge-case", "boundary", "adversarial"]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# =============================================================================
# FROZEN TEST CASES
# =============================================================================

# Test Case 1: Current Development State (2026-04-21)
GOLDEN_DEVELOPMENT_2026_04_21 = GoldenTestCase(
    name="development_2026_04_21",
    description="Current calibration assessment from 2026-04-21",
    policy_version="2.1.0",
    input_assessment={
        "current_state": "development",
        "target_state": "production",
        "eligible_for_promotion": True,
        "requires_downgrade": False,
        "gates": {
            "replicate": {
                "gate_name": "replicate_count",
                "status": "pass",
                "value": 3.0,
                "pass_threshold": 1,
                "warning_threshold": 1,
                "margin_to_pass": 2.0,
                "message": "Replicate count: 3 per cell, 30 total (pass)",
            },
            "residual": {
                "gate_name": "residual_spread",
                "status": "warning",
                "value": 0.0848,
                "pass_threshold": 0.2,
                "warning_threshold": 0.3,
                "margin_to_pass": 0.1152,
                "message": "Residual spread: std=0.0848, mean=0.1417 (warning)",
            },
            "separation": {
                "gate_name": "signal_to_separation",
                "status": "pass",
                "value": 1.4236,
                "pass_threshold": 1.0,
                "warning_threshold": 0.8,
                "margin_to_pass": 0.4236,
                "message": "Signal-to-separation: mean S/S=1.42 (pass)",
            },
            "portability": {
                "gate_name": "portability",
                "status": "warning",
                "value": 0.8498,
                "pass_threshold": 0.85,
                "warning_threshold": 0.75,
                "margin_to_pass": -0.0002,
                "message": "Portability: efficiency=100.0%, ranking=0.70, score=85.0% (warning)",
            },
            "stability": {
                "gate_name": "stability",
                "status": "pass",
                "value": 0.0015,
                "pass_threshold": 0.01,
                "warning_threshold": 0.02,
                "margin_to_pass": 0.0085,
                "message": "Stability: within-promoter std=0.001521 (pass)",
            },
            "model_fit": {
                "gate_name": "model_fit",
                "status": "pass",
                "value": 0.9002,
                "pass_threshold": 0.5,
                "warning_threshold": 0.4,
                "margin_to_pass": 0.4002,
                "message": "Model fit: R²=0.9002 (pass)",
            },
            "rank_ci": {
                "gate_name": "rank_stability_ci",
                "status": "warning",
                "value": 0.6,
                "pass_threshold": 0.7,
                "warning_threshold": 0.6,
                "margin_to_pass": -0.1,
                "message": "Rank stability CI: [0.60, 0.80] (warning)",
            },
            "coverage": {
                "gate_name": "cohort_coverage",
                "status": "pass",
                "value": 1.0,
                "pass_threshold": 0.8,
                "warning_threshold": 0.7,
                "margin_to_pass": 0.2,
                "message": "Cohort coverage: 2/2 cells (pass)",
            },
        },
        "blocking_issues": [],
        "assessed_at": "2026-04-21T04:05:55.584733",
        "ledger_path": "raw_hardware/vcapture_ledger_report.json",
        "calibration_version": "1.0",
    },
    expected_output={
        "current_state": "development",
        "target_state": "production",
        "eligible_for_promotion": True,
        "requires_downgrade": False,
        "gate_counts": {"pass": 5, "warning": 3, "fail": 0},
        "recommended_action": "promote",
    },
    expected_gate_counts={"pass": 5, "warning": 3, "fail": 0},
    expected_state="development",
    expected_action="promote",
    tags=["historical", "development", "warnings"],
)

# Test Case 2: All Passing Gates
GOLDEN_ALL_PASS = GoldenTestCase(
    name="all_pass",
    description="All gates passing, ready for production",
    policy_version="2.1.0",
    input_assessment={
        "current_state": "staging",
        "target_state": "production",
        "eligible_for_promotion": True,
        "requires_downgrade": False,
        "gates": {
            "replicate": {"gate_name": "replicate_count", "status": "pass", "value": 5.0, "pass_threshold": 3, "warning_threshold": 2, "margin_to_pass": 2.0, "message": "OK"},
            "residual": {"gate_name": "residual_spread", "status": "pass", "value": 0.05, "pass_threshold": 0.1, "warning_threshold": 0.15, "margin_to_pass": 0.05, "message": "OK"},
            "separation": {"gate_name": "signal_to_separation", "status": "pass", "value": 2.5, "pass_threshold": 2.0, "warning_threshold": 1.5, "margin_to_pass": 0.5, "message": "OK"},
            "portability": {"gate_name": "portability", "status": "pass", "value": 0.92, "pass_threshold": 0.85, "warning_threshold": 0.75, "margin_to_pass": 0.07, "message": "OK"},
            "stability": {"gate_name": "stability", "status": "pass", "value": 0.005, "pass_threshold": 0.01, "warning_threshold": 0.02, "margin_to_pass": 0.005, "message": "OK"},
            "model_fit": {"gate_name": "model_fit", "status": "pass", "value": 0.85, "pass_threshold": 0.70, "warning_threshold": 0.60, "margin_to_pass": 0.15, "message": "OK"},
        },
        "blocking_issues": [],
        "assessed_at": "2026-04-21T12:00:00",
        "ledger_path": "test/all_pass.json",
        "calibration_version": "test",
    },
    expected_output={
        "current_state": "staging",
        "target_state": "production",
        "eligible_for_promotion": True,
        "requires_downgrade": False,
        "gate_counts": {"pass": 6, "warning": 0, "fail": 0},
        "recommended_action": "promote",
    },
    expected_gate_counts={"pass": 6, "warning": 0, "fail": 0},
    expected_state="staging",
    expected_action="promote",
    tags=["synthetic", "all-pass", "production-ready"],
)

# Test Case 3: Critical Failure (Downgrade Required)
GOLDEN_CRITICAL_FAILURE = GoldenTestCase(
    name="critical_failure",
    description="Critical gate failure requiring downgrade",
    policy_version="2.1.0",
    input_assessment={
        "current_state": "staging",
        "target_state": "production",
        "eligible_for_promotion": False,
        "requires_downgrade": True,
        "gates": {
            "replicate": {"gate_name": "replicate_count", "status": "pass", "value": 3.0, "pass_threshold": 3, "warning_threshold": 2, "margin_to_pass": 0.0, "message": "OK"},
            "residual": {"gate_name": "residual_spread", "status": "fail", "value": 0.25, "pass_threshold": 0.1, "warning_threshold": 0.15, "margin_to_pass": -0.15, "message": "FAIL"},
            "separation": {"gate_name": "signal_to_separation", "status": "pass", "value": 2.0, "pass_threshold": 2.0, "warning_threshold": 1.5, "margin_to_pass": 0.0, "message": "OK"},
            "portability": {"gate_name": "portability", "status": "fail", "value": 0.50, "pass_threshold": 0.85, "warning_threshold": 0.75, "margin_to_pass": -0.35, "message": "FAIL"},
            "stability": {"gate_name": "stability", "status": "fail", "value": 0.05, "pass_threshold": 0.01, "warning_threshold": 0.02, "margin_to_pass": -0.04, "message": "FAIL"},
            "model_fit": {"gate_name": "model_fit", "status": "pass", "value": 0.75, "pass_threshold": 0.70, "warning_threshold": 0.60, "margin_to_pass": 0.05, "message": "OK"},
        },
        "blocking_issues": ["residual_spread failed", "portability failed", "stability failed"],
        "assessed_at": "2026-04-21T12:00:00",
        "ledger_path": "test/critical_failure.json",
        "calibration_version": "test",
    },
    expected_output={
        "current_state": "staging",
        "target_state": "production",
        "eligible_for_promotion": False,
        "requires_downgrade": True,
        "gate_counts": {"pass": 3, "warning": 0, "fail": 3},
        "recommended_action": "downgrade",
    },
    expected_gate_counts={"pass": 3, "warning": 0, "fail": 3},
    expected_state="staging",
    expected_action="downgrade",
    tags=["synthetic", "critical-failure", "downgrade"],
)

# Test Case 4: Boundary Values (Edge Case)
GOLDEN_BOUNDARY_VALUES = GoldenTestCase(
    name="boundary_values",
    description="Metrics exactly at threshold boundaries",
    policy_version="2.1.0",
    input_assessment={
        "current_state": "candidate",
        "target_state": "staging",
        "eligible_for_promotion": True,
        "requires_downgrade": False,
        "gates": {
            "replicate": {"gate_name": "replicate_count", "status": "pass", "value": 3.0, "pass_threshold": 3.0, "warning_threshold": 2.0, "margin_to_pass": 0.0, "message": "Boundary"},
            "residual": {"gate_name": "residual_spread", "status": "pass", "value": 0.10, "pass_threshold": 0.10, "warning_threshold": 0.15, "margin_to_pass": 0.0, "message": "Boundary"},
            "separation": {"gate_name": "signal_to_separation", "status": "pass", "value": 2.0, "pass_threshold": 2.0, "warning_threshold": 1.5, "margin_to_pass": 0.0, "message": "Boundary"},
            "portability": {"gate_name": "portability", "status": "pass", "value": 0.85, "pass_threshold": 0.85, "warning_threshold": 0.75, "margin_to_pass": 0.0, "message": "Boundary"},
            "stability": {"gate_name": "stability", "status": "pass", "value": 0.01, "pass_threshold": 0.01, "warning_threshold": 0.02, "margin_to_pass": 0.0, "message": "Boundary"},
            "model_fit": {"gate_name": "model_fit", "status": "pass", "value": 0.70, "pass_threshold": 0.70, "warning_threshold": 0.60, "margin_to_pass": 0.0, "message": "Boundary"},
        },
        "blocking_issues": [],
        "assessed_at": "2026-04-21T12:00:00",
        "ledger_path": "test/boundary.json",
        "calibration_version": "test",
    },
    expected_output={
        "current_state": "candidate",
        "target_state": "staging",
        "eligible_for_promotion": True,
        "requires_downgrade": False,
        "gate_counts": {"pass": 6, "warning": 0, "fail": 0},
        "recommended_action": "promote",
    },
    expected_gate_counts={"pass": 6, "warning": 0, "fail": 0},
    expected_state="candidate",
    expected_action="promote",
    tags=["synthetic", "boundary", "edge-case"],
)

# Test Case 5: Adversarial - Out of Range Value
GOLDEN_ADVERSARIAL_OUT_OF_RANGE = GoldenTestCase(
    name="adversarial_out_of_range",
    description="Metric value outside valid range (should warn)",
    policy_version="2.1.0",
    input_assessment={
        "current_state": "development",
        "target_state": "production",
        "eligible_for_promotion": False,
        "requires_downgrade": False,
        "gates": {
            "replicate": {"gate_name": "replicate_count", "status": "pass", "value": 3.0, "pass_threshold": 1, "warning_threshold": 1, "margin_to_pass": 2.0, "message": "OK"},
            "residual": {"gate_name": "residual_spread", "status": "pass", "value": 0.05, "pass_threshold": 0.2, "warning_threshold": 0.3, "margin_to_pass": 0.15, "message": "OK"},
            "separation": {"gate_name": "signal_to_separation", "status": "pass", "value": 1.5, "pass_threshold": 1.0, "warning_threshold": 0.8, "margin_to_pass": 0.5, "message": "OK"},
            "portability": {"gate_name": "portability", "status": "pass", "value": 0.80, "pass_threshold": 0.85, "warning_threshold": 0.75, "margin_to_pass": -0.05, "message": "OK"},
            "stability": {"gate_name": "stability", "status": "pass", "value": 0.005, "pass_threshold": 0.01, "warning_threshold": 0.02, "margin_to_pass": 0.005, "message": "OK"},
            "model_fit": {"gate_name": "model_fit", "status": "pass", "value": 0.75, "pass_threshold": 0.5, "warning_threshold": 0.4, "margin_to_pass": 0.25, "message": "OK"},
            "coverage": {"gate_name": "cohort_coverage", "status": "pass", "value": 5.0, "pass_threshold": 0.8, "warning_threshold": 0.7, "margin_to_pass": 4.2, "message": "OUT OF RANGE"},
        },
        "blocking_issues": [],
        "assessed_at": "2026-04-21T12:00:00",
        "ledger_path": "test/out_of_range.json",
        "calibration_version": "test",
    },
    expected_output={
        "current_state": "development",
        "target_state": "production",
        "eligible_for_promotion": True,
        "requires_downgrade": False,
        "gate_counts": {"pass": 7, "warning": 0, "fail": 0},
        "recommended_action": "promote",
    },
    expected_gate_counts={"pass": 7, "warning": 0, "fail": 0},
    expected_state="development",
    expected_action="promote",
    tags=["synthetic", "adversarial", "out-of-range", "semantic-validation"],
)


# =============================================================================
# TEST SUITE
# =============================================================================

class GoldenTestSuite(unittest.TestCase):
    """
    Golden test suite for VCapture governance system.
    
    Tests that frozen historical assessments produce the same canonical
    decision under the same policy version.
    """
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_cases = [
            GOLDEN_DEVELOPMENT_2026_04_21,
            GOLDEN_ALL_PASS,
            GOLDEN_CRITICAL_FAILURE,
            GOLDEN_BOUNDARY_VALUES,
            GOLDEN_ADVERSARIAL_OUT_OF_RANGE,
        ]
    
    def test_development_2026_04_21(self):
        """Test historical development assessment from 2026-04-21."""
        tc = GOLDEN_DEVELOPMENT_2026_04_21
        
        # Create canonical output
        canonical = CanonicalGovernanceOutput.from_assessment(tc.input_assessment)
        
        # Check gate counts
        self.assertEqual(canonical.gate_counts, tc.expected_gate_counts,
                         f"Gate counts mismatch for {tc.name}")
        
        # Check state
        self.assertEqual(canonical.current_state.value, tc.expected_state,
                         f"State mismatch for {tc.name}")
        
        # Check action
        self.assertEqual(canonical.recommended_action.value, tc.expected_action,
                         f"Action mismatch for {tc.name}")
        
        # Check consistency
        self.assertEqual(len(canonical.passing_gates), canonical.gate_counts["pass"])
        self.assertEqual(len(canonical.warning_gates), canonical.gate_counts["warning"])
        self.assertEqual(len(canonical.failing_gates), canonical.gate_counts["fail"])
    
    def test_all_pass(self):
        """Test all gates passing scenario."""
        tc = GOLDEN_ALL_PASS
        
        canonical = CanonicalGovernanceOutput.from_assessment(tc.input_assessment)
        
        self.assertEqual(canonical.gate_counts, {"pass": 6, "warning": 0, "fail": 0})
        self.assertEqual(canonical.recommended_action.value, "promote")
    
    def test_critical_failure(self):
        """Test critical failure requiring downgrade."""
        tc = GOLDEN_CRITICAL_FAILURE
        
        canonical = CanonicalGovernanceOutput.from_assessment(tc.input_assessment)
        
        self.assertEqual(canonical.gate_counts, {"pass": 3, "warning": 0, "fail": 3})
        self.assertEqual(canonical.recommended_action.value, "downgrade")
        self.assertTrue(canonical.requires_downgrade)
    
    def test_boundary_values(self):
        """Test metrics at exact threshold boundaries."""
        tc = GOLDEN_BOUNDARY_VALUES
        
        canonical = CanonicalGovernanceOutput.from_assessment(tc.input_assessment)
        
        # All boundary values should pass (>= threshold)
        self.assertEqual(canonical.gate_counts, {"pass": 6, "warning": 0, "fail": 0})
    
    def test_adversarial_out_of_range(self):
        """Test adversarial case with out-of-range value."""
        tc = GOLDEN_ADVERSARIAL_OUT_OF_RANGE
        
        # This should trigger a warning from metric validation
        import warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            canonical = CanonicalGovernanceOutput.from_assessment(tc.input_assessment)
            
            # Should have caught a warning about out-of-range value
            # (cohort_coverage = 5.0 is out of range [0, 1])
            self.assertTrue(len(w) > 0, "Expected warning for out-of-range value")
    
    def test_canonical_consistency(self):
        """Test that all outputs are consistent."""
        for tc in self.test_cases:
            canonical = CanonicalGovernanceOutput.from_assessment(tc.input_assessment)
            
            # Gate counts must match gate lists
            self.assertEqual(
                len(canonical.passing_gates),
                canonical.gate_counts["pass"],
                f"Pass count mismatch for {tc.name}"
            )
            self.assertEqual(
                len(canonical.warning_gates),
                canonical.gate_counts["warning"],
                f"Warning count mismatch for {tc.name}"
            )
            self.assertEqual(
                len(canonical.failing_gates),
                canonical.gate_counts["fail"],
                f"Fail count mismatch for {tc.name}"
            )
    
    def test_json_serialization(self):
        """Test that canonical output can be serialized to JSON."""
        tc = GOLDEN_DEVELOPMENT_2026_04_21
        canonical = CanonicalGovernanceOutput.from_assessment(tc.input_assessment)
        
        # Should not raise
        json_str = canonical.to_json()
        
        # Should be valid JSON
        parsed = json.loads(json_str)
        self.assertIsInstance(parsed, dict)
    
    def test_text_report_generation(self):
        """Test that text report can be generated."""
        tc = GOLDEN_DEVELOPMENT_2026_04_21
        canonical = CanonicalGovernanceOutput.from_assessment(tc.input_assessment)
        
        # Should not raise
        report = canonical.to_text_report()
        
        # Should contain key sections
        self.assertIn("GATE SUMMARY", report)
        self.assertIn("PASS", report)
        self.assertIn("WARNING", report)
    
    def test_markdown_generation(self):
        """Test that markdown summary can be generated."""
        tc = GOLDEN_DEVELOPMENT_2026_04_21
        canonical = CanonicalGovernanceOutput.from_assessment(tc.input_assessment)
        
        # Should not raise
        markdown = canonical.to_markdown_summary()
        
        # Should contain key sections
        self.assertIn("# VCapture", markdown)
        self.assertIn("Gate Summary", markdown)


# =============================================================================
# TEST RUNNER
# =============================================================================

def run_tests():
    """Run the golden test suite."""
    import sys
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(GoldenTestSuite)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("GOLDEN TEST SUITE SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success: {result.wasSuccessful()}")
    print("=" * 70)
    
    return 0 if result.wasSuccessful() else 1


def save_golden_tests(output_dir: Path):
    """Save golden test cases to JSON files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    test_cases = [
        GOLDEN_DEVELOPMENT_2026_04_21,
        GOLDEN_ALL_PASS,
        GOLDEN_CRITICAL_FAILURE,
        GOLDEN_BOUNDARY_VALUES,
        GOLDEN_ADVERSARIAL_OUT_OF_RANGE,
    ]
    
    for tc in test_cases:
        output_path = output_dir / f"{tc.name}.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(tc.to_dict(), f, indent=2)
        print(f"Saved: {output_path}")
    
    # Save index
    index = {
        "policy_version": "2.1.0",
        "created_at": datetime.now().isoformat(),
        "test_cases": [tc.name for tc in test_cases],
    }
    
    index_path = output_dir / "index.json"
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2)
    print(f"Saved: {index_path}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="VCapture Golden Test Suite")
    parser.add_argument("--run", action="store_true", help="Run golden tests")
    parser.add_argument("--save", action="store_true", help="Save golden test cases to JSON")
    parser.add_argument("--output-dir", type=str, default="golden_tests", help="Output directory for saved tests")
    
    args = parser.parse_args()
    
    if args.run:
        return run_tests()
    elif args.save:
        save_golden_tests(Path(args.output_dir))
        return 0
    else:
        # Default: run tests
        return run_tests()


if __name__ == "__main__":
    import sys
    sys.exit(main())