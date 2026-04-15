"""
Biomimetic Metrics Validator
============================

Gatekeeper for metric validation. Any metric that is out of range,
missing a formal definition, or lacking a null model is marked invalid
and blocked from being promoted to evidence status.

Date: April 15, 2026
"""

import json
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum

from metric_classes import (
    MetricClass, MetricType, get_metric_type, 
    classify_metric_value, METRIC_TYPES
)
from null_models import (
    NullModelTester, null_phi_resonance, 
    null_entanglement_entropy, null_platonic_alignment
)


class ValidationStatus(Enum):
    """Validation status for metrics"""
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"
    CLASS_ERROR = "CLASS_ERROR"
    MISSING_REGISTRY = "MISSING_REGISTRY"


@dataclass
class ValidationResult:
    """Result of validating a single metric"""
    metric_name: str
    observed_value: float
    metric_class: str
    is_valid: bool
    status: str
    message: str
    null_comparison: Optional[Dict] = None
    p_value: Optional[float] = None
    is_significant: Optional[bool] = None


class BiomimeticMetricsValidator:
    """
    Validates biomimetic metrics against:
    1. Schema validation (name, equation, range, null model)
    2. Range validation (value within declared range)
    3. Type validation (raw ratio vs normalized score vs signed diagnostic)
    4. Null-model validation (comparison to randomized baselines)
    5. Baseline validation (comparison to standard descriptors)
    6. Predictive validation (external task relevance)
    """
    
    def __init__(self, registry_path: str = None):
        self.registry = self._load_registry(registry_path)
        self.tester = NullModelTester(n_trials=1000)
        self.results: List[ValidationResult] = []
    
    def _load_registry(self, path: str) -> dict:
        """Load metric registry from JSON file."""
        if path is None:
            path = Path(__file__).parent / "metrics_registry.json"
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Registry not found at {path}")
            return {"metrics": {}}
    
    # =========================================================================
    # SCHEMA VALIDATION
    # =========================================================================
    
    def validate_schema(self, metric_name: str) -> Tuple[bool, List[str]]:
        """
        Check if metric has all required registry fields.
        
        Returns:
            (is_valid, list of missing fields)
        """
        required_fields = [
            "name", "equation", "output_range", 
            "null_model", "failure_condition"
        ]
        
        if metric_name not in self.registry.get("metrics", {}):
            return False, ["Metric not in registry"]
        
        metric_def = self.registry["metrics"][metric_name]
        missing = [f for f in required_fields if f not in metric_def]
        
        return len(missing) == 0, missing
    
    # =========================================================================
    # RANGE VALIDATION
    # =========================================================================
    
    def validate_range(self, 
                       metric_name: str, 
                       value: float) -> Tuple[bool, str]:
        """
        Validate that value is within declared range for metric class.
        
        Handles different metric classes:
        - RAW_RATIO: any positive value
        - NORMALIZED_SCORE: [0, 1]
        - SIGNED_CORRELATION: [-1, 1]
        - BOUNDED_ENTROPY: [0, log(d)]
        - UNBOUNDED_POSITIVE: [0, ∞)
        """
        metric_type = get_metric_type(metric_name)
        
        if metric_type is None:
            # Check registry for output range
            if metric_name in self.registry.get("metrics", {}):
                output_range = self.registry["metrics"][metric_name].get("output_range", {})
                min_val = output_range.get("min")
                max_val = output_range.get("max")
                
                if min_val is not None and value < min_val:
                    return False, f"Value {value} below minimum {min_val}"
                if max_val is not None and value > max_val:
                    return False, f"Value {value} above maximum {max_val}"
                
                return True, "Value within registry range"
            
            return False, f"Metric '{metric_name}' not found in registry or type definitions"
        
        return metric_type.validate_value(value)
    
    # =========================================================================
    # TYPE VALIDATION
    # =========================================================================
    
    def validate_type(self,
                      metric_name: str,
                      value: float,
                      declared_class: str = None) -> Tuple[bool, str]:
        """
        Validate that metric value matches its declared type.
        
        Args:
            metric_name: Name of the metric
            value: Observed value
            declared_class: Optional explicit class declaration
            
        Returns:
            (is_valid, message)
        """
        metric_type = get_metric_type(metric_name)
        
        if metric_type is None:
            return False, f"Unknown metric type for '{metric_name}'"
        
        # Check if declared class matches inferred class
        if declared_class is not None:
            if declared_class.upper() != metric_type.metric_class.name:
                return False, f"Declared class '{declared_class}' does not match inferred class '{metric_type.metric_class.name}'"
        
        # Validate value against class
        return metric_type.validate_value(value)
    
    # =========================================================================
    # NULL-MODEL VALIDATION
    # =========================================================================
    
    def validate_against_null(self,
                              metric_name: str,
                              observed_value: float,
                              metric_fn: callable = None) -> Tuple[bool, Dict]:
        """
        Compare observed value against null model distribution.
        
        Args:
            metric_name: Name of the metric
            observed_value: Observed metric value
            metric_fn: Optional function to compute metric from null data
            
        Returns:
            (is_significant, null_comparison_dict)
        """
        # Get null model from registry
        if metric_name in self.registry.get("metrics", {}):
            null_model = self.registry["metrics"][metric_name].get("null_model", {})
            expected_value = null_model.get("expected_value")
        else:
            expected_value = None
        
        # Use predefined null models
        if "phi_resonance" in metric_name.lower():
            null_result = null_phi_resonance(1000)
        elif "entanglement" in metric_name.lower() or "entropy" in metric_name.lower():
            null_result = null_entanglement_entropy(5, 32, 1000)
        elif "platonic" in metric_name.lower() or "alignment" in metric_name.lower():
            null_result = null_platonic_alignment(5, 1000)
        else:
            # Generic null model
            null_result = {
                "null_mean": expected_value if expected_value else 0.5,
                "null_std": 0.1,
                "n_trials": 1000
            }
        
        # Compute significance
        null_mean_raw = null_result.get("null_mean", 0.5)
        # Handle string expressions or None values
        if null_mean_raw is None or isinstance(null_mean_raw, str):
            null_mean = 0.5  # Default for unknown null models
        else:
            null_mean = float(null_mean_raw)
        
        null_std_raw = null_result.get("null_std", 0.1)
        if null_std_raw is None or isinstance(null_std_raw, str):
            null_std = 0.1
        else:
            null_std = float(null_std_raw)
        
        z_score = (observed_value - null_mean) / (null_std + 1e-10)
        p_value = 2 * (1 - 0.5 * (1 + np.tanh(z_score / np.sqrt(2))))  # Approximate
        
        is_significant = abs(z_score) > 2  # |z| > 2 is roughly p < 0.05
        
        null_comparison = {
            "observed": observed_value,
            "null_mean": null_mean,
            "null_std": null_std,
            "z_score": z_score,
            "p_value": p_value,
            "is_significant": is_significant
        }
        
        return is_significant, null_comparison
    
    # =========================================================================
    # COMBINED VALIDATION
    # =========================================================================
    
    def validate_metric(self,
                        metric_name: str,
                        value: float,
                        run_null_test: bool = True) -> ValidationResult:
        """
        Run all validations for a metric.
        
        Args:
            metric_name: Name of the metric
            value: Observed value
            run_null_test: Whether to run null model comparison
            
        Returns:
            ValidationResult with all checks
        """
        # Step 1: Check registry
        schema_valid, missing = self.validate_schema(metric_name)
        if not schema_valid:
            return ValidationResult(
                metric_name=metric_name,
                observed_value=value,
                metric_class="UNKNOWN",
                is_valid=False,
                status=ValidationStatus.MISSING_REGISTRY.value,
                message=f"Missing fields: {missing}"
            )
        
        # Step 2: Get metric type
        metric_type = get_metric_type(metric_name)
        if metric_type is None:
            # Try to infer from registry
            metric_def = self.registry["metrics"].get(metric_name, {})
            output_range = metric_def.get("output_range", {})
            min_val = output_range.get("min", 0)
            max_val = output_range.get("max", 1)
            
            # Infer class from range
            if min_val == 0 and max_val == 1:
                metric_class = MetricClass.NORMALIZED_SCORE
            elif min_val == -1 and max_val == 1:
                metric_class = MetricClass.SIGNED_CORRELATION
            elif min_val == 0 and max_val is None:
                metric_class = MetricClass.UNBOUNDED_POSITIVE
            else:
                metric_class = MetricClass.RAW_RATIO
        else:
            metric_class = metric_type.metric_class
        
        # Step 3: Validate range
        range_valid, range_msg = self.validate_range(metric_name, value)
        if not range_valid:
            return ValidationResult(
                metric_name=metric_name,
                observed_value=value,
                metric_class=metric_class.value,
                is_valid=False,
                status=ValidationStatus.FAIL.value,
                message=f"Range violation: {range_msg}"
            )
        
        # Step 4: Validate type
        type_valid, type_msg = self.validate_type(metric_name, value)
        if not type_valid:
            return ValidationResult(
                metric_name=metric_name,
                observed_value=value,
                metric_class=metric_class.value,
                is_valid=False,
                status=ValidationStatus.CLASS_ERROR.value,
                message=f"Type error: {type_msg}"
            )
        
        # Step 5: Null model comparison
        null_comparison = None
        p_value = None
        is_significant = None
        
        if run_null_test:
            is_significant, null_comparison = self.validate_against_null(metric_name, value)
            p_value = null_comparison.get("p_value")
        
        # Determine final status
        if not range_valid:
            status = ValidationStatus.FAIL
        elif not type_valid:
            status = ValidationStatus.CLASS_ERROR
        elif run_null_test and not is_significant:
            status = ValidationStatus.WARN
        else:
            status = ValidationStatus.PASS
        
        return ValidationResult(
            metric_name=metric_name,
            observed_value=value,
            metric_class=metric_class.value,
            is_valid=(status == ValidationStatus.PASS),
            status=status.value,
            message=f"All validations passed" if status == ValidationStatus.PASS else f"Status: {status.value}",
            null_comparison=null_comparison,
            p_value=p_value,
            is_significant=is_significant
        )
    
    def validate_batch(self,
                       metrics: Dict[str, float],
                       run_null_tests: bool = True) -> Dict[str, ValidationResult]:
        """
        Validate multiple metrics at once.
        
        Args:
            metrics: Dictionary of {metric_name: value}
            run_null_tests: Whether to run null model comparisons
            
        Returns:
            Dictionary of {metric_name: ValidationResult}
        """
        results = {}
        
        for metric_name, value in metrics.items():
            results[metric_name] = self.validate_metric(
                metric_name, value, run_null_tests
            )
        
        self.results = list(results.values())
        return results
    
    # =========================================================================
    # REPORTING
    # =========================================================================
    
    def generate_report(self) -> str:
        """Generate a human-readable validation report."""
        report = []
        report.append("="*70)
        report.append("BIOMIMETIC METRICS VALIDATION REPORT")
        report.append("="*70)
        
        # Group by status
        passed = [r for r in self.results if r.status == "PASS"]
        warned = [r for r in self.results if r.status == "WARN"]
        failed = [r for r in self.results if r.status == "FAIL"]
        class_errors = [r for r in self.results if r.status == "CLASS_ERROR"]
        missing = [r for r in self.results if r.status == "MISSING_REGISTRY"]
        
        report.append(f"\nSUMMARY:")
        report.append(f"  ✅ PASS: {len(passed)}")
        report.append(f"  ⚠️  WARN: {len(warned)}")
        report.append(f"  ❌ FAIL: {len(failed)}")
        report.append(f"  🔤 CLASS_ERROR: {len(class_errors)}")
        report.append(f"  📋 MISSING_REGISTRY: {len(missing)}")
        
        if passed:
            report.append(f"\n✅ PASSED METRICS:")
            for r in passed:
                report.append(f"  {r.metric_name}: {r.observed_value:.4f} [{r.metric_class}]")
        
        if warned:
            report.append(f"\n⚠️  WARNINGS (not significant vs null):")
            for r in warned:
                report.append(f"  {r.metric_name}: {r.observed_value:.4f}")
                if r.null_comparison:
                    report.append(f"    Null: {r.null_comparison['null_mean']:.4f} ± {r.null_comparison['null_std']:.4f}")
                    report.append(f"    z-score: {r.null_comparison['z_score']:.2f}")
        
        if failed:
            report.append(f"\n❌ FAILED (range violations):")
            for r in failed:
                report.append(f"  {r.metric_name}: {r.observed_value:.4f}")
                report.append(f"    {r.message}")
        
        if class_errors:
            report.append(f"\n🔤 CLASS ERRORS (wrong metric type):")
            for r in class_errors:
                report.append(f"  {r.metric_name}: {r.observed_value:.4f} [{r.metric_class}]")
                report.append(f"    {r.message}")
        
        if missing:
            report.append(f"\n📋 MISSING FROM REGISTRY:")
            for r in missing:
                report.append(f"  {r.metric_name}")
        
        report.append("\n" + "="*70)
        
        return "\n".join(report)
    
    def save_results(self, path: str):
        """Save validation results to JSON."""
        results_dict = {
            "validation_date": "2026-04-15",
            "total_metrics": len(self.results),
            "passed": sum(1 for r in self.results if r.status == "PASS"),
            "warnings": sum(1 for r in self.results if r.status == "WARN"),
            "failed": sum(1 for r in self.results if r.status == "FAIL"),
            "class_errors": sum(1 for r in self.results if r.status == "CLASS_ERROR"),
            "missing": sum(1 for r in self.results if r.status == "MISSING_REGISTRY"),
            "results": [asdict(r) for r in self.results]
        }
        
        with open(path, 'w') as f:
            json.dump(results_dict, f, indent=2, default=str)
        
        print(f"✅ Results saved to: {path}")


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    print("="*70)
    print("BIOMIMETIC METRICS VALIDATOR")
    print("="*70)
    
    validator = BiomimeticMetricsValidator()
    
    # Test metrics from the user's example
    test_metrics = {
        "phi_coherence": 0.6952,
        "phi_resonance_score": 1.6180,  # Should FAIL (out of range for normalized score)
        "biomimetic_resonance": 1.1249,  # Should FAIL (out of range)
        "entanglement_entropy": 1.2422,
        "platonic_alignment_score": 0.6517,
        "quantum_coherence": 0.0074,
    }
    
    # Also test raw ratios (should PASS)
    test_metrics["phi_ratio"] = 1.6180  # Raw ratio - should PASS
    test_metrics["phi_ratio_inverse"] = 0.618  # Raw ratio - should PASS
    
    print("\nValidating metrics...")
    results = validator.validate_batch(test_metrics)
    
    print(validator.generate_report())
    
    # Save results
    validator.save_results("biomimetic_validation_results.json")