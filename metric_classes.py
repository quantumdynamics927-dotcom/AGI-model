"""
Metric Classes: Ontology for Different Metric Types
====================================================

Separates metrics into distinct classes to prevent range validation errors.
A raw ratio of φ = 1.618 is valid; a normalized score of 1.618 is not.

Date: April 15, 2026
"""

from enum import Enum
from dataclasses import dataclass
from typing import Tuple, Optional


class MetricClass(Enum):
    """Classification of metric types by their mathematical nature"""
    
    RAW_RATIO = "raw_ratio"
    """Unnormalized ratios or constants (e.g., φ = 1.618, 1/φ = 0.618)"""
    
    NORMALIZED_SCORE = "normalized_score"
    """Bounded scores in [0, 1] (e.g., alignment scores, resonance scores)"""
    
    SIGNED_CORRELATION = "signed_correlation"
    """Correlation-like measures in [-1, 1] (e.g., Pearson correlation)"""
    
    BOUNDED_ENTROPY = "bounded_entropy"
    """Entropy-like measures in [0, log(d)] (e.g., von Neumann entropy)"""
    
    UNBOUNDED_POSITIVE = "unbounded_positive"
    """Positive measures with no upper bound (e.g., efficiency, counts)"""
    
    TARGET_CONSTANT = "target_constant"
    """Mathematical constants used as targets (e.g., φ, √2, π)"""


@dataclass
class MetricType:
    """Complete type specification for a metric"""
    
    name: str
    metric_class: MetricClass
    valid_range: Tuple[Optional[float], Optional[float]]
    description: str
    null_expected: Optional[float] = None
    
    def validate_value(self, value: float) -> Tuple[bool, str]:
        """
        Validate a value against this metric type.
        
        Returns:
            (is_valid, message)
        """
        min_val, max_val = self.valid_range
        
        # Check class-specific validation
        if self.metric_class == MetricClass.RAW_RATIO:
            # Raw ratios can be any positive value
            if value < 0:
                return False, f"Raw ratio must be non-negative, got {value}"
            return True, "Valid raw ratio"
        
        elif self.metric_class == MetricClass.NORMALIZED_SCORE:
            # Must be in [0, 1]
            if not (0 <= value <= 1):
                return False, f"Normalized score must be in [0, 1], got {value}"
            return True, "Valid normalized score"
        
        elif self.metric_class == MetricClass.SIGNED_CORRELATION:
            # Must be in [-1, 1]
            if not (-1 <= value <= 1):
                return False, f"Signed correlation must be in [-1, 1], got {value}"
            return True, "Valid signed correlation"
        
        elif self.metric_class == MetricClass.BOUNDED_ENTROPY:
            # Must be non-negative
            if value < 0:
                return False, f"Entropy must be non-negative, got {value}"
            if max_val is not None and value > max_val:
                return False, f"Entropy {value} exceeds theoretical maximum {max_val}"
            return True, "Valid entropy"
        
        elif self.metric_class == MetricClass.UNBOUNDED_POSITIVE:
            # Must be non-negative
            if value < 0:
                return False, f"Unbounded positive metric must be non-negative, got {value}"
            return True, "Valid unbounded positive"
        
        elif self.metric_class == MetricClass.TARGET_CONSTANT:
            # Target constants are reference values, not measurements
            return True, f"Target constant reference value: {value}"
        
        return True, "Unknown metric class"


# =============================================================================
# PREDEFINED METRIC TYPES
# =============================================================================

METRIC_TYPES = {
    # Raw Ratios (can be any positive value)
    "phi_ratio": MetricType(
        name="phi_ratio",
        metric_class=MetricClass.RAW_RATIO,
        valid_range=(0, None),
        description="Raw golden ratio measurement (φ ≈ 1.618 or 1/φ ≈ 0.618)",
        null_expected=1.0
    ),
    
    "geometric_ratio": MetricType(
        name="geometric_ratio",
        metric_class=MetricClass.RAW_RATIO,
        valid_range=(0, None),
        description="Ratio of geometric distances",
        null_expected=1.0
    ),
    
    # Normalized Scores (must be in [0, 1])
    "phi_resonance_score": MetricType(
        name="phi_resonance_score",
        metric_class=MetricClass.NORMALIZED_SCORE,
        valid_range=(0, 1),
        description="Normalized phi-alignment score: R_φ = exp(-α·min|r_i - φ|)",
        null_expected=0.6
    ),
    
    "phi_coherence": MetricType(
        name="phi_coherence",
        metric_class=MetricClass.NORMALIZED_SCORE,
        valid_range=(0, 1),
        description="Normalized phi coherence: C_φ = 1 - |L/L_φ - 1|/2",
        null_expected=0.5
    ),
    
    "biomimetic_resonance": MetricType(
        name="biomimetic_resonance",
        metric_class=MetricClass.NORMALIZED_SCORE,
        valid_range=(0, 1),
        description="Normalized biomimetic alignment: R_bio = (corr + 1)/2",
        null_expected=0.5
    ),
    
    "platonic_alignment_score": MetricType(
        name="platonic_alignment_score",
        metric_class=MetricClass.NORMALIZED_SCORE,
        valid_range=(0, 1),
        description="Platonic solid alignment score",
        null_expected=0.6
    ),
    
    "quantum_coherence": MetricType(
        name="quantum_coherence",
        metric_class=MetricClass.NORMALIZED_SCORE,
        valid_range=(0, 1),
        description="Quantum coherence measure",
        null_expected=0.01
    ),
    
    # Signed Correlations (must be in [-1, 1])
    "correlation_coefficient": MetricType(
        name="correlation_coefficient",
        metric_class=MetricClass.SIGNED_CORRELATION,
        valid_range=(-1, 1),
        description="Pearson or Spearman correlation",
        null_expected=0.0
    ),
    
    "biomimetic_correlation": MetricType(
        name="biomimetic_correlation",
        metric_class=MetricClass.SIGNED_CORRELATION,
        valid_range=(-1, 1),
        description="Raw correlation with biological reference",
        null_expected=0.0
    ),
    
    # Bounded Entropy (must be non-negative, upper bound depends on dimension)
    "entanglement_entropy": MetricType(
        name="entanglement_entropy",
        metric_class=MetricClass.BOUNDED_ENTROPY,
        valid_range=(0, None),  # Upper bound is log(d_A), set dynamically
        description="Von Neumann entanglement entropy",
        null_expected=None  # Depends on dimension
    ),
    
    "von_neumann_entropy": MetricType(
        name="von_neumann_entropy",
        metric_class=MetricClass.BOUNDED_ENTROPY,
        valid_range=(0, None),
        description="Von Neumann entropy of density matrix",
        null_expected=None
    ),
    
    # Unbounded Positive (must be non-negative)
    "neural_efficiency": MetricType(
        name="neural_efficiency",
        metric_class=MetricClass.UNBOUNDED_POSITIVE,
        valid_range=(0, None),
        description="Performance per parameter-FLOP",
        null_expected=None
    ),
    
    "quantum_bond_strength": MetricType(
        name="quantum_bond_strength",
        metric_class=MetricClass.UNBOUNDED_POSITIVE,
        valid_range=(0, None),
        description="Quantum overlap divided by distance",
        null_expected=0.25
    ),
    
    # Target Constants (reference values)
    "phi_target": MetricType(
        name="phi_target",
        metric_class=MetricClass.TARGET_CONSTANT,
        valid_range=(None, None),
        description="Golden ratio target: φ = 1.6180339887...",
        null_expected=None
    ),
    
    "phi_inverse_target": MetricType(
        name="phi_inverse_target",
        metric_class=MetricClass.TARGET_CONSTANT,
        valid_range=(None, None),
        description="Inverse golden ratio target: 1/φ = 0.6180339887...",
        null_expected=None
    ),
}


def get_metric_type(metric_name: str) -> Optional[MetricType]:
    """Get the metric type definition for a given metric name."""
    
    # Direct lookup
    if metric_name in METRIC_TYPES:
        return METRIC_TYPES[metric_name]
    
    # Fuzzy matching for common variations
    name_lower = metric_name.lower().replace("_", " ").replace("-", " ")
    
    # Check for phi resonance variants
    if "phi" in name_lower and "resonance" in name_lower:
        if "score" in name_lower or "normalized" in name_lower:
            return METRIC_TYPES["phi_resonance_score"]
        else:
            # Default to raw ratio if not specified as normalized
            return METRIC_TYPES["phi_ratio"]
    
    # Check for phi coherence
    if "phi" in name_lower and "coherence" in name_lower:
        return METRIC_TYPES["phi_coherence"]
    
    # Check for biomimetic resonance
    if "biomimetic" in name_lower and "resonance" in name_lower:
        return METRIC_TYPES["biomimetic_resonance"]
    
    # Check for entropy
    if "entropy" in name_lower or "entanglement" in name_lower:
        return METRIC_TYPES["entanglement_entropy"]
    
    # Check for correlation
    if "correlation" in name_lower:
        return METRIC_TYPES["correlation_coefficient"]
    
    return None


def classify_metric_value(metric_name: str, value: float) -> Tuple[str, bool, str]:
    """
    Classify and validate a metric value.
    
    Args:
        metric_name: Name of the metric
        value: Observed value
        
    Returns:
        (metric_class, is_valid, message)
    """
    metric_type = get_metric_type(metric_name)
    
    if metric_type is None:
        return "UNKNOWN", False, f"Metric '{metric_name}' not in registry"
    
    is_valid, message = metric_type.validate_value(value)
    
    return metric_type.metric_class.value, is_valid, message


# =============================================================================
# REGISTRY VALIDATION
# =============================================================================

def validate_registry_consistency(registry: dict) -> list:
    """
    Validate that the metric registry is internally consistent.
    
    Returns:
        List of validation errors
    """
    errors = []
    
    for metric_name, metric_def in registry.get("metrics", {}).items():
        # Check required fields
        required_fields = ["name", "equation", "output_range", "null_model"]
        for field in required_fields:
            if field not in metric_def:
                errors.append(f"{metric_name}: missing required field '{field}'")
        
        # Check output range consistency
        output_range = metric_def.get("output_range", {})
        min_val = output_range.get("min")
        max_val = output_range.get("max")
        
        if min_val is not None and max_val is not None:
            if min_val > max_val:
                errors.append(f"{metric_name}: invalid range [{min_val}, {max_val}]")
        
        # Check null model
        null_model = metric_def.get("null_model", {})
        if "expected_value" not in null_model:
            errors.append(f"{metric_name}: null model missing expected_value")
    
    return errors


if __name__ == "__main__":
    # Test the metric type system
    print("="*60)
    print("METRIC CLASS VALIDATION TESTS")
    print("="*60)
    
    test_cases = [
        ("phi_resonance_score", 0.85),      # Valid normalized
        ("phi_resonance_score", 1.618),    # Invalid normalized (out of range)
        ("phi_ratio", 1.618),              # Valid raw ratio
        ("phi_ratio", 0.618),              # Valid raw ratio
        ("biomimetic_resonance", 0.75),    # Valid normalized
        ("biomimetic_resonance", 1.3499),  # Invalid normalized
        ("entanglement_entropy", 1.24),    # Valid entropy
        ("entanglement_entropy", -0.5),    # Invalid entropy
        ("correlation_coefficient", 0.8),  # Valid correlation
        ("correlation_coefficient", 1.5),  # Invalid correlation
    ]
    
    for metric_name, value in test_cases:
        metric_class, is_valid, message = classify_metric_value(metric_name, value)
        status = "✅ PASS" if is_valid else "❌ FAIL"
        print(f"{status}: {metric_name} = {value}")
        print(f"       Class: {metric_class}")
        print(f"       {message}")
        print()