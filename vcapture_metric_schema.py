#!/usr/bin/env python3
"""
VCapture Metric Schema v2.2
==========================

Schema-level metadata for every canonical metric to prevent semantic
normalization issues and ensure interpretability.

Each metric has:
- name: Canonical metric name
- type: Data type (float, int, fraction, percentage)
- unit: Physical unit (count, ratio, seconds, etc.)
- range: Valid range [min, max]
- comparison_direction: higher_is_better or lower_is_better
- threshold_semantics: What the threshold means (minimum, maximum, target)
- normalization: How to normalize to canonical scale

This prevents comparing incomparable scales while appearing formally valid.

Usage:
    from vcapture_metric_schema import MetricSchema, normalize_metric
    
    # Get metric metadata
    schema = MetricSchema.get("cohort_coverage")
    
    # Normalize to canonical scale
    normalized = normalize_metric("cohort_coverage", raw_value)
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any


# =============================================================================
# METRIC TYPES
# =============================================================================

class MetricType(str, Enum):
    """Data type for metrics."""
    FLOAT = "float"              # Continuous floating-point value
    INTEGER = "integer"          # Discrete count
    FRACTION = "fraction"        # Ratio in [0, 1]
    PERCENTAGE = "percentage"   # Ratio in [0, 100]
    RATIO = "ratio"             # Ratio with no upper bound
    SCORE = "score"             # Arbitrary scale


class ComparisonDirection(str, Enum):
    """Comparison direction for metrics."""
    HIGHER_IS_BETTER = "higher_is_better"  # Higher values are better
    LOWER_IS_BETTER = "lower_is_better"    # Lower values are better
    TARGET = "target"                        # Values should be close to target


class ThresholdSemantics(str, Enum):
    """What the threshold means."""
    MINIMUM = "minimum"    # Value must be at least this
    MAXIMUM = "maximum"    # Value must be at most this
    TARGET = "target"      # Value should be close to this
    BAND = "band"          # Value should be within band


# =============================================================================
# METRIC SCHEMA
# =============================================================================

@dataclass
class MetricMetadata:
    """
    Schema-level metadata for a single metric.
    
    This prevents semantic normalization issues by explicitly defining:
    - What the metric represents
    - What units it uses
    - What range is valid
    - How to compare it
    - How to normalize it
    """
    # Canonical name
    name: str
    
    # Data type
    type: MetricType
    
    # Physical unit
    unit: str
    
    # Valid range [min, max]
    range: Tuple[float, float]
    
    # Comparison direction
    comparison_direction: ComparisonDirection
    
    # Threshold semantics
    threshold_semantics: ThresholdSemantics
    
    # Human-readable description
    description: str
    
    # How to normalize to canonical scale [0, 1]
    # None means already canonical
    normalization: Optional[str] = None
    
    # Example values for documentation
    example_good: Optional[float] = None
    example_warning: Optional[float] = None
    example_fail: Optional[float] = None
    
    def normalize(self, value: float) -> float:
        """
        Normalize metric to canonical scale [0, 1].
        
        Higher values are always better after normalization.
        """
        if self.normalization is None:
            # Already canonical
            if self.comparison_direction == ComparisonDirection.HIGHER_IS_BETTER:
                return value
            else:
                # Lower is better, so invert
                return 1.0 - value
        
        # Apply normalization formula
        if self.normalization == "fraction":
            # Already in [0, 1]
            return value
        elif self.normalization == "percentage":
            # Convert from [0, 100] to [0, 1]
            return value / 100.0
        elif self.normalization == "count_to_fraction":
            # Convert count to fraction (need denominator)
            # This requires context, so return as-is
            return value
        elif self.normalization == "invert":
            # Lower is better, so invert
            return 1.0 - value
        elif self.normalization == "log":
            # Logarithmic normalization
            import math
            return math.log(1 + value) / math.log(1 + self.range[1])
        else:
            # Unknown normalization, return as-is
            return value
    
    def is_in_range(self, value: float) -> bool:
        """Check if value is in valid range."""
        return self.range[0] <= value <= self.range[1]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "type": self.type.value,
            "unit": self.unit,
            "range": list(self.range),
            "comparison_direction": self.comparison_direction.value,
            "threshold_semantics": self.threshold_semantics.value,
            "description": self.description,
            "normalization": self.normalization,
            "example_good": self.example_good,
            "example_warning": self.example_warning,
            "example_fail": self.example_fail,
        }


# =============================================================================
# METRIC REGISTRY
# =============================================================================

class MetricSchema:
    """
    Registry of all canonical metrics with schema-level metadata.
    
    This ensures all metrics are properly defined and normalized.
    """
    
    # Core gates
    REPLICATE_COUNT = MetricMetadata(
        name="replicate_count",
        type=MetricType.INTEGER,
        unit="count",
        range=(1, 100),
        comparison_direction=ComparisonDirection.HIGHER_IS_BETTER,
        threshold_semantics=ThresholdSemantics.MINIMUM,
        description="Number of replicates per promoter-backend cell",
        normalization=None,  # Already canonical
        example_good=5,
        example_warning=2,
        example_fail=1,
    )
    
    RESIDUAL_SPREAD = MetricMetadata(
        name="residual_spread",
        type=MetricType.FLOAT,
        unit="std_dev",
        range=(0.0, 1.0),
        comparison_direction=ComparisonDirection.LOWER_IS_BETTER,
        threshold_semantics=ThresholdSemantics.MAXIMUM,
        description="Standard deviation of residuals after calibration",
        normalization="invert",
        example_good=0.05,
        example_warning=0.12,
        example_fail=0.25,
    )
    
    SIGNAL_TO_SEPARATION = MetricMetadata(
        name="signal_to_separation",
        type=MetricType.RATIO,
        unit="ratio",
        range=(0.0, 10.0),
        comparison_direction=ComparisonDirection.HIGHER_IS_BETTER,
        threshold_semantics=ThresholdSemantics.MINIMUM,
        description="Ratio of between-promoter to within-promoter variance",
        normalization=None,
        example_good=3.0,
        example_warning=1.5,
        example_fail=0.8,
    )
    
    PORTABILITY = MetricMetadata(
        name="portability",
        type=MetricType.FRACTION,
        unit="fraction",
        range=(0.0, 1.0),
        comparison_direction=ComparisonDirection.HIGHER_IS_BETTER,
        threshold_semantics=ThresholdSemantics.MINIMUM,
        description="Fraction of calibration quality preserved across backends",
        normalization="fraction",
        example_good=0.92,
        example_warning=0.78,
        example_fail=0.60,
    )
    
    STABILITY = MetricMetadata(
        name="stability",
        type=MetricType.FLOAT,
        unit="std_dev",
        range=(0.0, 1.0),
        comparison_direction=ComparisonDirection.LOWER_IS_BETTER,
        threshold_semantics=ThresholdSemantics.MAXIMUM,
        description="Within-promoter standard deviation across replicates",
        normalization="invert",
        example_good=0.005,
        example_warning=0.015,
        example_fail=0.05,
    )
    
    MODEL_FIT = MetricMetadata(
        name="model_fit",
        type=MetricType.FRACTION,
        unit="r_squared",
        range=(0.0, 1.0),
        comparison_direction=ComparisonDirection.HIGHER_IS_BETTER,
        threshold_semantics=ThresholdSemantics.MINIMUM,
        description="R-squared of mixed-effects model",
        normalization="fraction",
        example_good=0.85,
        example_warning=0.65,
        example_fail=0.40,
    )
    
    # Optional gates
    HELDOUT_PERFORMANCE = MetricMetadata(
        name="heldout_performance",
        type=MetricType.FRACTION,
        unit="fraction",
        range=(0.0, 1.0),
        comparison_direction=ComparisonDirection.HIGHER_IS_BETTER,
        threshold_semantics=ThresholdSemantics.MINIMUM,
        description="Correlation with held-out promoter performance",
        normalization="fraction",
        example_good=0.80,
        example_warning=0.68,
        example_fail=0.50,
    )
    
    BACKEND_DRIFT = MetricMetadata(
        name="backend_drift",
        type=MetricType.FLOAT,
        unit="magnitude",
        range=(0.0, 1.0),
        comparison_direction=ComparisonDirection.LOWER_IS_BETTER,
        threshold_semantics=ThresholdSemantics.MAXIMUM,
        description="Magnitude of backend parameter drift over time",
        normalization="invert",
        example_good=0.02,
        example_warning=0.06,
        example_fail=0.12,
    )
    
    RANK_STABILITY_CI = MetricMetadata(
        name="rank_stability_ci",
        type=MetricType.FRACTION,
        unit="fraction",
        range=(0.0, 1.0),
        comparison_direction=ComparisonDirection.HIGHER_IS_BETTER,
        threshold_semantics=ThresholdSemantics.MINIMUM,
        description="Lower bound of 95% CI for ranking correlation",
        normalization="fraction",
        example_good=0.75,
        example_warning=0.62,
        example_fail=0.45,
    )
    
    COHORT_COVERAGE = MetricMetadata(
        name="cohort_coverage",
        type=MetricType.FRACTION,
        unit="fraction",
        range=(0.0, 1.0),
        comparison_direction=ComparisonDirection.HIGHER_IS_BETTER,
        threshold_semantics=ThresholdSemantics.MINIMUM,
        description="Fraction of promoter-backend cells with minimum replicates",
        normalization="fraction",
        example_good=0.95,
        example_warning=0.72,
        example_fail=0.50,
    )
    
    # Registry
    _registry: Dict[str, MetricMetadata] = {}
    
    @classmethod
    def get(cls, name: str) -> Optional[MetricMetadata]:
        """Get metric metadata by name."""
        if not cls._registry:
            # Initialize registry
            cls._registry = {
                "replicate_count": cls.REPLICATE_COUNT,
                "residual_spread": cls.RESIDUAL_SPREAD,
                "signal_to_separation": cls.SIGNAL_TO_SEPARATION,
                "portability": cls.PORTABILITY,
                "stability": cls.STABILITY,
                "model_fit": cls.MODEL_FIT,
                "heldout_performance": cls.HELDOUT_PERFORMANCE,
                "backend_drift": cls.BACKEND_DRIFT,
                "rank_stability_ci": cls.RANK_STABILITY_CI,
                "cohort_coverage": cls.COHORT_COVERAGE,
            }
        return cls._registry.get(name)
    
    @classmethod
    def all(cls) -> Dict[str, MetricMetadata]:
        """Get all metric metadata."""
        if not cls._registry:
            cls.get("replicate_count")  # Initialize
        return cls._registry
    
    @classmethod
    def validate_value(cls, name: str, value: float) -> Tuple[bool, str]:
        """
        Validate a metric value against its schema.
        
        Returns:
            (is_valid, message)
        """
        schema = cls.get(name)
        if schema is None:
            return False, f"Unknown metric: {name}"
        
        if not schema.is_in_range(value):
            return False, f"Value {value} out of range {schema.range} for {name}"
        
        return True, "Valid"
    
    @classmethod
    def normalize_value(cls, name: str, value: float) -> float:
        """
        Normalize a metric value to canonical scale [0, 1].
        
        Higher values are always better after normalization.
        """
        schema = cls.get(name)
        if schema is None:
            return value
        
        return schema.normalize(value)
    
    @classmethod
    def compare_values(cls, name: str, value: float, threshold: float) -> int:
        """
        Compare a value to a threshold.
        
        Returns:
            1 if value is better than threshold
            0 if value is equal to threshold
            -1 if value is worse than threshold
        """
        schema = cls.get(name)
        if schema is None:
            # Default: higher is better
            if value > threshold:
                return 1
            elif value < threshold:
                return -1
            else:
                return 0
        
        if schema.comparison_direction == ComparisonDirection.HIGHER_IS_BETTER:
            if value > threshold:
                return 1
            elif value < threshold:
                return -1
            else:
                return 0
        else:  # LOWER_IS_BETTER
            if value < threshold:
                return 1
            elif value > threshold:
                return -1
            else:
                return 0
    
    @classmethod
    def to_json_schema(cls) -> Dict[str, Any]:
        """
        Export schema as JSON Schema for validation.
        
        This can be used to validate JSON outputs against the schema.
        """
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "VCapture Metric Schema",
            "description": "Schema for VCapture governance metrics",
            "type": "object",
            "properties": {
                name: {
                    "type": "number",
                    "minimum": schema.range[0],
                    "maximum": schema.range[1],
                    "description": schema.description,
                    "unit": schema.unit,
                    "comparison": schema.comparison_direction.value,
                }
                for name, schema in cls.all().items()
            },
        }


# =============================================================================
# NORMALIZATION UTILITIES
# =============================================================================

def normalize_metric(name: str, value: float) -> float:
    """
    Normalize a metric to canonical scale [0, 1].
    
    Higher values are always better after normalization.
    """
    return MetricSchema.normalize_value(name, value)


def validate_metric(name: str, value: float) -> Tuple[bool, str]:
    """
    Validate a metric value against its schema.
    
    Returns:
        (is_valid, message)
    """
    return MetricSchema.validate_value(name, value)


def compute_margin(name: str, value: float, threshold: float) -> float:
    """
    Compute margin from threshold in canonical direction.
    
    Positive margin = better than threshold
    Negative margin = worse than threshold
    """
    schema = MetricSchema.get(name)
    
    if schema is None:
        # Default: higher is better
        return value - threshold
    
    if schema.comparison_direction == ComparisonDirection.HIGHER_IS_BETTER:
        return value - threshold
    else:  # LOWER_IS_BETTER
        return threshold - value


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

def main():
    """Example usage of metric schema."""
    import json
    
    print("=" * 70)
    print("VCapture Metric Schema v2.2")
    print("=" * 70)
    print()
    
    # Get all metrics
    all_metrics = MetricSchema.all()
    
    print("Registered Metrics:")
    print()
    for name, schema in all_metrics.items():
        print(f"  {name}:")
        print(f"    Type: {schema.type.value}")
        print(f"    Unit: {schema.unit}")
        print(f"    Range: [{schema.range[0]}, {schema.range[1]}]")
        print(f"    Comparison: {schema.comparison_direction.value}")
        print(f"    Description: {schema.description}")
        print()
    
    # Validate examples
    print("=" * 70)
    print("Validation Examples")
    print("=" * 70)
    print()
    
    examples = [
        ("cohort_coverage", 5.0),  # WRONG: count instead of fraction
        ("cohort_coverage", 0.85),  # CORRECT: fraction
        ("residual_spread", 0.08),  # CORRECT: in range
        ("residual_spread", 1.5),  # WRONG: out of range
        ("signal_to_separation", 2.5),  # CORRECT: in range
    ]
    
    for name, value in examples:
        is_valid, message = validate_metric(name, value)
        status = "✓" if is_valid else "✗"
        print(f"  {status} {name}={value}: {message}")
    
    print()
    
    # Compute margins
    print("=" * 70)
    print("Margin Examples")
    print("=" * 70)
    print()
    
    margin_examples = [
        ("cohort_coverage", 0.85, 0.80),
        ("residual_spread", 0.08, 0.10),
        ("signal_to_separation", 2.5, 2.0),
    ]
    
    for name, value, threshold in margin_examples:
        margin = compute_margin(name, value, threshold)
        schema = MetricSchema.get(name)
        direction = "above" if margin > 0 else "below"
        print(f"  {name}: {value} vs threshold {threshold}")
        print(f"    Margin: {margin:+.4f} ({direction} threshold)")
        print(f"    Comparison: {schema.comparison_direction.value}")
        print()
    
    # Export JSON Schema
    print("=" * 70)
    print("JSON Schema Export")
    print("=" * 70)
    print()
    print(json.dumps(MetricSchema.to_json_schema(), indent=2))


if __name__ == "__main__":
    main()