"""Enhanced Schema-Invalid Burn-Down with Error Leaderboard and Regression Tests.

This module extends the base burn-down with:
- Top-3 schema error leaderboard for targeted fixes
- Retry-adjusted success rate gate
- P95 latency threshold gate
- Regression test suite for canonical failure cases
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
import json


@dataclass
class ErrorLeaderboard:
    """
    Top-N schema error leaderboard for targeted burn-down.
    
    Tracks the highest-frequency violations to prioritize fixes.
    """
    by_error: Dict[str, int] = field(default_factory=dict)
    by_field: Dict[str, int] = field(default_factory=dict)
    by_error_field: Dict[str, int] = field(default_factory=dict)
    recent: List[Dict[str, Any]] = field(default_factory=list)
    
    def record(self, error: str, field: str, value: Any = None) -> None:
        """Record a violation and update leaderboard."""
        self.by_error[error] = self.by_error.get(error, 0) + 1
        self.by_field[field] = self.by_field.get(field, 0) + 1
        
        key = f"{error}:{field}"
        self.by_error_field[key] = self.by_error_field.get(key, 0) + 1
        
        self.recent.append({
            "error": error,
            "field": field,
            "value": value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        if len(self.recent) > 100:
            self.recent = self.recent[-100:]
    
    def get_top_errors(self, n: int = 3) -> List[Tuple[str, int]]:
        """Get top-N errors by frequency."""
        sorted_errors = sorted(self.by_error.items(), key=lambda x: x[1], reverse=True)
        return sorted_errors[:n]
    
    def get_top_fields(self, n: int = 3) -> List[Tuple[str, int]]:
        """Get top-N fields by violation frequency."""
        sorted_fields = sorted(self.by_field.items(), key=lambda x: x[1], reverse=True)
        return sorted_fields[:n]
    
    def get_top_combinations(self, n: int = 5) -> List[Tuple[str, int]]:
        """Get top-N error-field combinations."""
        sorted_combos = sorted(self.by_error_field.items(), key=lambda x: x[1], reverse=True)
        return sorted_combos[:n]
    
    def get_leaderboard(self) -> Dict[str, Any]:
        """Get full leaderboard summary."""
        return {
            "top_errors": self.get_top_errors(3),
            "top_fields": self.get_top_fields(3),
            "top_combinations": self.get_top_combinations(5),
            "total_violations": sum(self.by_error.values()),
            "unique_errors": len(self.by_error),
            "unique_fields": len(self.by_field),
        }
    
    def get_burn_down_targets(self, n: int = 3) -> List[Dict[str, Any]]:
        """Get prioritized burn-down targets."""
        top_combos = self.get_top_combinations(n)
        targets = []
        
        for combo, count in top_combos:
            parts = combo.split(":", 1)
            error = parts[0]
            field = parts[1] if len(parts) > 1 else ""
            
            targets.append({
                "error": error,
                "field": field,
                "count": count,
                "priority": "high" if count > 5 else "medium" if count > 2 else "low",
                "suggested_fix": self._suggest_fix(error, field),
            })
        
        return targets
    
    def _suggest_fix(self, error: str, field: str) -> str:
        """Suggest a fix for the error-field combination."""
        suggestions = {
            ("Missing required field", "verdict"): "Add explicit 'verdict' field with enum constraint in prompt",
            ("Invalid enum value", "verdict"): "Add enum examples and anti-patterns for 'verdict' values",
            ("Out of range", "confidence"): "Add numeric bounds validation and example values",
            ("Missing required field", "metrics_summary"): "Add metrics_summary object structure in prompt",
            ("Invalid type", "recommendation"): "Add type constraint and example for 'recommendation' field",
        }
        return suggestions.get((error, field), f"Review {field} requirements and add validation")


@dataclass
class EnhancedReleaseGate:
    """
    Enhanced release gate with retry-adjusted success rate and P95 latency.
    
    An operation is considered stable when:
    - Success rate ≥ threshold
    - Retry-adjusted success rate ≥ threshold
    - Schema-invalid share < transport-failure share
    - Schema-invalid count < threshold
    - P95 latency < threshold
    """
    operation: str
    min_success_rate: float = 0.90
    min_retry_adjusted_success_rate: float = 0.80
    max_schema_invalid_share: float = 0.50
    max_schema_invalid_count: int = 9
    max_p95_latency_s: float = 3.0
    
    def evaluate(
        self,
        success_rate: float,
        retry_adjusted_success_rate: float,
        schema_invalid_count: int,
        transport_failure_count: int,
        p95_latency_s: float,
    ) -> Dict[str, Any]:
        """Evaluate if operation passes release gate."""
        total_failures = schema_invalid_count + transport_failure_count
        schema_invalid_share = (
            schema_invalid_count / total_failures if total_failures > 0 else 0.0
        )
        
        checks = {
            "success_rate": {
                "value": success_rate,
                "threshold": self.min_success_rate,
                "pass": success_rate >= self.min_success_rate,
            },
            "retry_adjusted_success_rate": {
                "value": retry_adjusted_success_rate,
                "threshold": self.min_retry_adjusted_success_rate,
                "pass": retry_adjusted_success_rate >= self.min_retry_adjusted_success_rate,
            },
            "schema_invalid_share": {
                "value": schema_invalid_share,
                "threshold": self.max_schema_invalid_share,
                "pass": schema_invalid_share < self.max_schema_invalid_share,
            },
            "schema_invalid_count": {
                "value": schema_invalid_count,
                "threshold": self.max_schema_invalid_count,
                "pass": schema_invalid_count < self.max_schema_invalid_count,
            },
            "p95_latency": {
                "value": p95_latency_s,
                "threshold": self.max_p95_latency_s,
                "pass": p95_latency_s < self.max_p95_latency_s,
            },
        }
        
        all_pass = all(c["pass"] for c in checks.values())
        
        return {
            "operation": self.operation,
            "stable": all_pass,
            "checks": checks,
            "summary": self._generate_summary(checks, all_pass),
        }
    
    def _generate_summary(self, checks: Dict[str, Any], all_pass: bool) -> str:
        if all_pass:
            return f"✅ {self.operation} is STABLE and passes all release gates."
        
        failures = [name for name, check in checks.items() if not check["pass"]]
        return f"❌ {self.operation} is NOT STABLE. Failed checks: {', '.join(failures)}"


@dataclass
class RegressionTestCase:
    """A canonical failure case for regression testing."""
    id: str
    name: str
    description: str
    input_data: Dict[str, Any]
    expected_errors: List[str]
    expected_fields: List[str]
    fixed: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "input_data": self.input_data,
            "expected_errors": self.expected_errors,
            "expected_fields": self.expected_fields,
            "fixed": self.fixed,
        }


@dataclass
class RegressionTestSuite:
    """
    Prompt-contract regression test suite.
    
    Tests schema fixes against canonical failure cases.
    """
    test_cases: List[RegressionTestCase] = field(default_factory=list)
    
    def add_case(
        self,
        name: str,
        description: str,
        input_data: Dict[str, Any],
        expected_errors: List[str],
        expected_fields: List[str],
    ) -> RegressionTestCase:
        """Add a regression test case."""
        import uuid
        case = RegressionTestCase(
            id=str(uuid.uuid4())[:8],
            name=name,
            description=description,
            input_data=input_data,
            expected_errors=expected_errors,
            expected_fields=expected_fields,
        )
        self.test_cases.append(case)
        return case
    
    def run_validation(
        self,
        validator_func,
    ) -> Dict[str, Any]:
        """Run all test cases through a validator function."""
        results = []
        passed = 0
        failed = 0
        
        for case in self.test_cases:
            validation_result = validator_func(case.input_data)
            
            # Check if expected errors were caught
            errors_caught = []
            for expected_error in case.expected_errors:
                if any(expected_error in str(e) for e in validation_result.get("errors", [])):
                    errors_caught.append(expected_error)
            
            # Check if expected fields were validated
            fields_validated = []
            for expected_field in case.expected_fields:
                if expected_field in str(validation_result):
                    fields_validated.append(expected_field)
            
            case_passed = (
                len(errors_caught) == len(case.expected_errors) and
                not validation_result.get("valid", True)
            )
            
            if case_passed:
                passed += 1
            else:
                failed += 1
            
            results.append({
                "id": case.id,
                "name": case.name,
                "passed": case_passed,
                "errors_caught": errors_caught,
                "fields_validated": fields_validated,
                "validation_result": validation_result,
            })
        
        return {
            "total": len(self.test_cases),
            "passed": passed,
            "failed": failed,
            "pass_rate": passed / len(self.test_cases) if self.test_cases else 1.0,
            "results": results,
        }
    
    def get_unfixed_cases(self) -> List[RegressionTestCase]:
        """Get test cases that haven't been fixed yet."""
        return [c for c in self.test_cases if not c.fixed]
    
    def mark_fixed(self, case_id: str) -> bool:
        """Mark a test case as fixed."""
        for case in self.test_cases:
            if case.id == case_id:
                case.fixed = True
                return True
        return False


# Canonical regression test cases for vae_checkpoint_validation
VAE_CHECKPOINT_REGRESSION_SUITE = RegressionTestSuite(test_cases=[
    RegressionTestCase(
        id="missing_verdict",
        name="Missing verdict field",
        description="Output missing required 'verdict' field",
        input_data={
            "confidence": 0.95,
            "metrics_summary": {"loss": 0.02},
            "recommendation": "OK",
        },
        expected_errors=["Missing required field", "verdict"],
        expected_fields=["verdict"],
    ),
    RegressionTestCase(
        id="invalid_verdict_enum",
        name="Invalid verdict enum value",
        description="Output has 'valid' instead of 'pass', 'fail', or 'warning'",
        input_data={
            "verdict": "valid",
            "confidence": 0.95,
            "metrics_summary": {"loss": 0.02},
            "recommendation": "OK",
        },
        expected_errors=["Invalid enum value", "verdict"],
        expected_fields=["verdict"],
    ),
    RegressionTestCase(
        id="confidence_out_of_range",
        name="Confidence out of range",
        description="Confidence value > 1.0",
        input_data={
            "verdict": "pass",
            "confidence": 1.5,
            "metrics_summary": {"loss": 0.02},
            "recommendation": "OK",
        },
        expected_errors=["Out of range", "confidence"],
        expected_fields=["confidence"],
    ),
    RegressionTestCase(
        id="empty_metrics_summary",
        name="Empty metrics_summary object",
        description="metrics_summary is empty object",
        input_data={
            "verdict": "pass",
            "confidence": 0.95,
            "metrics_summary": {},
            "recommendation": "OK",
        },
        expected_errors=["Empty", "metrics_summary"],
        expected_fields=["metrics_summary"],
    ),
    RegressionTestCase(
        id="extra_fields",
        name="Extra fields not in schema",
        description="Output contains additional fields",
        input_data={
            "verdict": "pass",
            "confidence": 0.95,
            "metrics_summary": {"loss": 0.02},
            "recommendation": "OK",
            "extra_field": "not allowed",
        },
        expected_errors=["Extra field", "additionalProperties"],
        expected_fields=["extra_field"],
    ),
])


class EnhancedBurnDown:
    """
    Enhanced burn-down with error leaderboard and regression tests.
    
    Features:
    - Top-3 error leaderboard for targeted fixes
    - Retry-adjusted success rate tracking
    - P95 latency threshold
    - Regression test suite
    """
    
    def __init__(self):
        self.leaderboard = ErrorLeaderboard()
        self.release_gate = EnhancedReleaseGate(
            operation="vae_checkpoint_validation",
            min_success_rate=0.90,
            min_retry_adjusted_success_rate=0.80,
            max_schema_invalid_share=0.50,
            max_schema_invalid_count=9,
            max_p95_latency_s=3.0,
        )
        self.regression_suite = VAE_CHECKPOINT_REGRESSION_SUITE
        self.history: List[Dict[str, Any]] = []
    
    def record_violation(self, error: str, field: str, value: Any = None) -> None:
        """Record a violation and update leaderboard."""
        self.leaderboard.record(error, field, value)
    
    def get_leaderboard(self) -> Dict[str, Any]:
        """Get the error leaderboard."""
        return self.leaderboard.get_leaderboard()
    
    def get_burn_down_targets(self, n: int = 3) -> List[Dict[str, Any]]:
        """Get prioritized burn-down targets."""
        return self.leaderboard.get_burn_down_targets(n)
    
    def evaluate_release_gate(
        self,
        success_rate: float,
        retry_adjusted_success_rate: float,
        schema_invalid_count: int,
        transport_failure_count: int,
        p95_latency_s: float,
    ) -> Dict[str, Any]:
        """Evaluate if operation passes release gate."""
        return self.release_gate.evaluate(
            success_rate,
            retry_adjusted_success_rate,
            schema_invalid_count,
            transport_failure_count,
            p95_latency_s,
        )
    
    def record_progress(
        self,
        schema_invalid: int,
        transport: int,
        success_rate: float,
        retry_adjusted_success_rate: float,
        p95_latency_s: float,
    ) -> Dict[str, Any]:
        """Record burn-down progress."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "schema_invalid": schema_invalid,
            "transport": transport,
            "success_rate": success_rate,
            "retry_adjusted_success_rate": retry_adjusted_success_rate,
            "p95_latency_s": p95_latency_s,
            "leaderboard": self.get_leaderboard(),
        }
        self.history.append(entry)
        return entry
    
    def run_regression_tests(self, validator_func) -> Dict[str, Any]:
        """Run regression test suite."""
        return self.regression_suite.run_validation(validator_func)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current burn-down status."""
        if not self.history:
            return {
                "status": "no_data",
                "leaderboard": self.get_leaderboard(),
                "regression_tests": {
                    "total": len(self.regression_suite.test_cases),
                    "unfixed": len(self.regression_suite.get_unfixed_cases()),
                },
            }
        
        latest = self.history[-1]
        return {
            "status": "active",
            "latest": latest,
            "leaderboard": self.get_leaderboard(),
            "regression_tests": {
                "total": len(self.regression_suite.test_cases),
                "unfixed": len(self.regression_suite.get_unfixed_cases()),
            },
        }


def create_enhanced_burn_down() -> EnhancedBurnDown:
    """Create an enhanced burn-down instance."""
    return EnhancedBurnDown()


# Export
__all__ = [
    "ErrorLeaderboard",
    "EnhancedReleaseGate",
    "RegressionTestCase",
    "RegressionTestSuite",
    "VAE_CHECKPOINT_REGRESSION_SUITE",
    "EnhancedBurnDown",
    "create_enhanced_burn_down",
]


if __name__ == "__main__":
    import json
    
    print("=" * 80)
    print("ENHANCED SCHEMA-INVALID BURN-DOWN")
    print("=" * 80)
    
    burn_down = create_enhanced_burn_down()
    
    # Record violations
    print("\n" + "=" * 80)
    print("ERROR LEADERBOARD")
    print("=" * 80)
    
    burn_down.record_violation("Missing required field", "verdict", None)
    burn_down.record_violation("Invalid enum value", "verdict", "valid")
    burn_down.record_violation("Out of range", "confidence", 1.5)
    burn_down.record_violation("Missing required field", "verdict", None)
    burn_down.record_violation("Empty object", "metrics_summary", {})
    
    leaderboard = burn_down.get_leaderboard()
    print(f"\nTotal violations: {leaderboard['total_violations']}")
    print(f"Unique errors: {leaderboard['unique_errors']}")
    print(f"Unique fields: {leaderboard['unique_fields']}")
    print(f"\nTop errors: {leaderboard['top_errors']}")
    print(f"Top fields: {leaderboard['top_fields']}")
    print(f"Top combinations: {leaderboard['top_combinations']}")
    
    # Show burn-down targets
    print("\n" + "=" * 80)
    print("BURN-DOWN TARGETS")
    print("=" * 80)
    
    targets = burn_down.get_burn_down_targets(3)
    for i, target in enumerate(targets, 1):
        print(f"\n{i}. {target['error']} -> {target['field']}")
        print(f"   Count: {target['count']}")
        print(f"   Priority: {target['priority']}")
        print(f"   Fix: {target['suggested_fix']}")
    
    # Show regression test suite
    print("\n" + "=" * 80)
    print("REGRESSION TEST SUITE")
    print("=" * 80)
    
    for case in burn_down.regression_suite.test_cases:
        print(f"\n{case.id}: {case.name}")
        print(f"  Description: {case.description}")
        print(f"  Expected errors: {case.expected_errors}")
    
    # Evaluate release gate
    print("\n" + "=" * 80)
    print("RELEASE GATE EVALUATION")
    print("=" * 80)
    
    # Simulate progress
    progress_points = [
        (12, 9, 0.58, 0.52, 5.0),   # Baseline
        (10, 9, 0.65, 0.58, 4.5),   # Week 1
        (8, 8, 0.75, 0.68, 4.0),    # Week 2
        (6, 7, 0.85, 0.78, 3.5),    # Week 3
        (4, 6, 0.92, 0.85, 2.8),    # Week 4 - Target reached
    ]
    
    for schema_invalid, transport, success_rate, retry_adj, p95 in progress_points:
        result = burn_down.evaluate_release_gate(
            success_rate, retry_adj, schema_invalid, transport, p95
        )
        print(f"\nSchema-invalid: {schema_invalid}, Transport: {transport}, Success: {success_rate:.2f}, Retry-adj: {retry_adj:.2f}, P95: {p95:.1f}s")
        print(f"  Stable: {result['stable']}")
        print(f"  Summary: {result['summary']}")
    
    # Final status
    print("\n" + "=" * 80)
    print("FINAL STATUS")
    print("=" * 80)
    
    status = burn_down.get_status()
    print(f"\n{json.dumps(status, indent=2)}")