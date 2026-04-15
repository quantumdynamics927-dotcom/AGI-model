"""
Field Taxonomy for Scientific Governance
=========================================

Classifies all fields into four top-level classes:
- METRIC: Measured observables with equations, ranges, null models
- PARAMETER: Experiment configuration (shots, qubits, temperature)
- METADATA: File/system info (timestamps, paths, counts)
- PROVENANCE: Lineage and source tracking

This taxonomy separates true metrics from configuration and metadata,
ensuring the migration pipeline only processes decision-grade fields.

Date: April 15, 2026
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple


class FieldClass(Enum):
    """Top-level classification of fields"""
    METRIC = "metric"           # Measured observable with formal definition
    PARAMETER = "parameter"     # Experiment configuration
    METADATA = "metadata"        # File/system information
    PROVENANCE = "provenance"   # Lineage and source tracking
    DESCRIPTOR = "descriptor"    # Exploratory field without formal definition


@dataclass
class FieldDefinition:
    """Definition of a field in the taxonomy"""
    field_name: str
    field_class: FieldClass
    canonical_name: Optional[str]  # For METRIC class, maps to canonical metric
    description: str
    unit: Optional[str] = None
    valid_range: Optional[Tuple[Optional[float], Optional[float]]] = None
    is_countable: bool = False  # For METADATA counts
    notes: str = ""


# =============================================================================
# FIELD TAXONOMY REGISTRY
# =============================================================================

FIELD_TAXONOMY: Dict[str, FieldDefinition] = {
    # =========================================================================
    # METRICS - Measured observables with formal definitions
    # =========================================================================
    
    # Phi-related metrics
    "phi_resonance": FieldDefinition(
        field_name="phi_resonance",
        field_class=FieldClass.METRIC,
        canonical_name="phi_resonance_score",
        description="Golden ratio resonance measurement",
        valid_range=(0.0, 1.0),
        notes="Must be normalized to [0,1]. Raw ratios >1 indicate unnormalized data."
    ),
    "phi_coherence": FieldDefinition(
        field_name="phi_coherence",
        field_class=FieldClass.METRIC,
        canonical_name="phi_coherence",
        description="Phi-based coherence measure",
        valid_range=(0.0, 1.0),
        notes="PROVISIONAL: Needs null model validation."
    ),
    "phi_ratio": FieldDefinition(
        field_name="phi_ratio",
        field_class=FieldClass.METRIC,
        canonical_name="phi_ratio",
        description="Raw golden ratio measurement",
        valid_range=(0.0, None),
        notes="EXPLORATORY: Raw ratio, not normalized."
    ),
    "phi_alignment": FieldDefinition(
        field_name="phi_alignment",
        field_class=FieldClass.METRIC,
        canonical_name="phi_alignment",
        description="Alignment with golden ratio",
        valid_range=(0.0, 1.0),
        notes="PROVISIONAL: Normalized proximity to phi."
    ),
    "measured_phi": FieldDefinition(
        field_name="measured_phi",
        field_class=FieldClass.METRIC,
        canonical_name="phi_invariant_score",
        description="Measured phi invariant from quantum experiments",
        valid_range=(0.0, 1.0),
        notes="VALIDATED: Expected value ≈ 1/φ ≈ 0.618."
    ),
    "predicted_phi": FieldDefinition(
        field_name="predicted_phi",
        field_class=FieldClass.METRIC,
        canonical_name="phi_target_constant",
        description="Predicted/target phi value",
        valid_range=(None, None),
        notes="EXPLORATORY: Target constant, not measurement."
    ),
    
    # Quantum coherence metrics
    "quantum_coherence": FieldDefinition(
        field_name="quantum_coherence",
        field_class=FieldClass.METRIC,
        canonical_name="quantum_coherence",
        description="Quantum coherence measure",
        valid_range=(0.0, 1.0),
        notes="VALIDATED: Passed numerical validity tests."
    ),
    "entanglement_entropy": FieldDefinition(
        field_name="entanglement_entropy",
        field_class=FieldClass.METRIC,
        canonical_name="entanglement_entropy",
        description="Von Neumann entanglement entropy",
        valid_range=(0.0, None),
        notes="PASSED: Must be non-negative."
    ),
    
    # Hardware metrics
    "t1_us": FieldDefinition(
        field_name="t1_us",
        field_class=FieldClass.METRIC,
        canonical_name="t1_coherence_time",
        description="T1 relaxation time in microseconds",
        unit="μs",
        valid_range=(0.0, None),
        notes="VALIDATED: Direct hardware measurement."
    ),
    "t2_us": FieldDefinition(
        field_name="t2_us",
        field_class=FieldClass.METRIC,
        canonical_name="t2_coherence_time",
        description="T2 dephasing time in microseconds",
        unit="μs",
        valid_range=(0.0, None),
        notes="VALIDATED: T2 ≤ 2*T1."
    ),
    "gate_error": FieldDefinition(
        field_name="gate_error",
        field_class=FieldClass.METRIC,
        canonical_name="gate_error_rate",
        description="Quantum gate error rate",
        valid_range=(0.0, 1.0),
        notes="VALIDATED: Lower is better."
    ),
    "readout_error": FieldDefinition(
        field_name="readout_error",
        field_class=FieldClass.METRIC,
        canonical_name="readout_error_rate",
        description="Measurement readout error rate",
        valid_range=(0.0, 1.0),
        notes="VALIDATED: Lower is better."
    ),
    "quality_score": FieldDefinition(
        field_name="quality_score",
        field_class=FieldClass.METRIC,
        canonical_name="hardware_quality_score",
        description="Overall hardware quality score",
        valid_range=(0.0, 1.0),
        notes="PASSED: Composite metric."
    ),
    
    # Geometry metrics
    "platonic_alignment_score": FieldDefinition(
        field_name="platonic_alignment_score",
        field_class=FieldClass.METRIC,
        canonical_name="platonic_alignment_score",
        description="Platonic solid alignment score",
        valid_range=(0.0, 1.0),
        notes="VALIDATED: Methane scores higher than random."
    ),
    "tesseract_symmetry": FieldDefinition(
        field_name="tesseract_symmetry",
        field_class=FieldClass.METRIC,
        canonical_name="tesseract_symmetry",
        description="4D tesseract symmetry measure",
        valid_range=(0.0, 1.0),
        notes="PROVISIONAL: T_4 = 1 for regular hypercube."
    ),
    "sacred_score": FieldDefinition(
        field_name="sacred_score",
        field_class=FieldClass.METRIC,
        canonical_name="sacred_score",
        description="Sacred geometry alignment score",
        valid_range=(0.0, 1.0),
        notes="PROVISIONAL: Composite of multiple geometry metrics."
    ),
    
    # Consciousness/exploratory metrics
    "consciousness_level": FieldDefinition(
        field_name="consciousness_level",
        field_class=FieldClass.DESCRIPTOR,
        canonical_name="consciousness_level",
        description="Consciousness level indicator (NOT VALIDATED)",
        valid_range=(0.0, 1.0),
        notes="EXPLORATORY: No formal definition. Use with extreme caution."
    ),
    "biomimetic_resonance": FieldDefinition(
        field_name="biomimetic_resonance",
        field_class=FieldClass.METRIC,
        canonical_name="biomimetic_resonance",
        description="Biomimetic resonance measure",
        valid_range=(0.0, 1.0),
        notes="PROVISIONAL: Values >1 are INVALID."
    ),
    
    # =========================================================================
    # PARAMETERS - Experiment configuration
    # =========================================================================
    
    "shots": FieldDefinition(
        field_name="shots",
        field_class=FieldClass.PARAMETER,
        canonical_name=None,
        description="Number of quantum circuit executions",
        unit="count",
        is_countable=True,
        notes="PARAMETER: Run configuration, not a metric."
    ),
    "qubits": FieldDefinition(
        field_name="qubits",
        field_class=FieldClass.PARAMETER,
        canonical_name=None,
        description="Number of qubits in circuit",
        unit="count",
        is_countable=True,
        notes="PARAMETER: Circuit configuration."
    ),
    "temperature": FieldDefinition(
        field_name="temperature",
        field_class=FieldClass.PARAMETER,
        canonical_name=None,
        description="System temperature",
        unit="K",
        notes="PARAMETER: Environmental configuration."
    ),
    "transpiled_depth": FieldDefinition(
        field_name="transpiled_depth",
        field_class=FieldClass.PARAMETER,
        canonical_name=None,
        description="Depth of transpiled quantum circuit",
        unit="gates",
        is_countable=True,
        notes="PARAMETER: Circuit property, not a measured observable."
    ),
    "cost": FieldDefinition(
        field_name="cost",
        field_class=FieldClass.PARAMETER,
        canonical_name=None,
        description="Optimization cost function value",
        notes="PARAMETER: Optimization state, not a metric."
    ),
    "total_qubits": FieldDefinition(
        field_name="total_qubits",
        field_class=FieldClass.PARAMETER,
        canonical_name=None,
        description="Total qubits on quantum backend",
        unit="count",
        is_countable=True,
        notes="PARAMETER: Backend configuration."
    ),
    "operational_qubits": FieldDefinition(
        field_name="operational_qubits",
        field_class=FieldClass.PARAMETER,
        canonical_name=None,
        description="Operational qubits on quantum backend",
        unit="count",
        is_countable=True,
        notes="PARAMETER: Backend status."
    ),
    "operational_percentage": FieldDefinition(
        field_name="operational_percentage",
        field_class=FieldClass.PARAMETER,
        canonical_name=None,
        description="Percentage of operational qubits",
        unit="%",
        valid_range=(0.0, 100.0),
        notes="PARAMETER: Backend status."
    ),
    "backends_analyzed": FieldDefinition(
        field_name="backends_analyzed",
        field_class=FieldClass.PARAMETER,
        canonical_name=None,
        description="Number of backends analyzed",
        unit="count",
        is_countable=True,
        notes="PARAMETER: Analysis configuration."
    ),
    "ranking": FieldDefinition(
        field_name="ranking",
        field_class=FieldClass.PARAMETER,
        canonical_name=None,
        description="Backend ranking",
        unit="rank",
        is_countable=True,
        notes="PARAMETER: Backend ordering."
    ),
    
    # =========================================================================
    # METADATA - File/system information
    # =========================================================================
    
    "mtime": FieldDefinition(
        field_name="mtime",
        field_class=FieldClass.METADATA,
        canonical_name=None,
        description="File modification time",
        unit="timestamp",
        notes="METADATA: File system info."
    ),
    "size": FieldDefinition(
        field_name="size",
        field_class=FieldClass.METADATA,
        canonical_name=None,
        description="File size in bytes",
        unit="bytes",
        is_countable=True,
        notes="METADATA: File system info."
    ),
    "unique_states": FieldDefinition(
        field_name="unique_states",
        field_class=FieldClass.METADATA,
        canonical_name=None,
        description="Count of unique quantum states",
        unit="count",
        is_countable=True,
        notes="METADATA: State count, not a metric."
    ),
    "total_discoveries": FieldDefinition(
        field_name="total_discoveries",
        field_class=FieldClass.METADATA,
        canonical_name=None,
        description="Count of discoveries in artifact",
        unit="count",
        is_countable=True,
        notes="METADATA: Discovery count."
    ),
    
    # =========================================================================
    # PROVENANCE - Lineage and source tracking
    # =========================================================================
    
    "backend": FieldDefinition(
        field_name="backend",
        field_class=FieldClass.PROVENANCE,
        canonical_name=None,
        description="Quantum backend used",
        notes="PROVENANCE: Source tracking."
    ),
    "job_id": FieldDefinition(
        field_name="job_id",
        field_class=FieldClass.PROVENANCE,
        canonical_name=None,
        description="IBM Quantum job identifier",
        notes="PROVENANCE: Job tracking."
    ),
    "experiment_id": FieldDefinition(
        field_name="experiment_id",
        field_class=FieldClass.PROVENANCE,
        canonical_name=None,
        description="Experiment identifier",
        notes="PROVENANCE: Experiment tracking."
    ),
    
    # =========================================================================
    # DESCRIPTORS - Exploratory fields without formal definitions
    # =========================================================================
    
    "consciousness_signature": FieldDefinition(
        field_name="consciousness_signature",
        field_class=FieldClass.DESCRIPTOR,
        canonical_name=None,
        description="Consciousness signature (NOT FORMALIZED)",
        notes="DESCRIPTOR: No equation, range, or null model. Hypothesis-generating only."
    ),
    "parameter_set": FieldDefinition(
        field_name="parameter_set",
        field_class=FieldClass.DESCRIPTOR,
        canonical_name=None,
        description="Parameter set for discovery",
        notes="DESCRIPTOR: Nested configuration."
    ),
    
    # =========================================================================
    # ADDITIONAL METRICS - High-frequency scientific fields
    # =========================================================================
    
    "measured_phi_baseline": FieldDefinition(
        field_name="measured_phi_baseline",
        field_class=FieldClass.METRIC,
        canonical_name="phi_invariant_score",
        description="Baseline measured phi value",
        valid_range=(0.0, 1.0),
        notes="METRIC: Expected value ≈ 1/φ ≈ 0.618."
    ),
    "estimated_phi_shift": FieldDefinition(
        field_name="estimated_phi_shift",
        field_class=FieldClass.METRIC,
        canonical_name="phi_shift",
        description="Estimated shift from phi baseline",
        valid_range=(-1.0, 1.0),
        notes="METRIC: Small deviations from phi."
    ),
    "t2_t1_ratio": FieldDefinition(
        field_name="t2_t1_ratio",
        field_class=FieldClass.METRIC,
        canonical_name="t2_t1_ratio",
        description="Ratio of T2 to T1 coherence times",
        valid_range=(0.0, 2.0),
        notes="METRIC: T2/T1 ≤ 2. Higher is better."
    ),
    
    # =========================================================================
    # VALIDATION ARTIFACT FIELDS - Metadata from validation runs
    # =========================================================================
    
    "metrics_found": FieldDefinition(
        field_name="metrics_found",
        field_class=FieldClass.METADATA,
        canonical_name=None,
        description="Count of metrics found in artifact",
        is_countable=True,
        notes="METADATA: Validation artifact count."
    ),
    "passed": FieldDefinition(
        field_name="passed",
        field_class=FieldClass.METADATA,
        canonical_name=None,
        description="Count of passed validations",
        is_countable=True,
        notes="METADATA: Validation result count."
    ),
    "warnings": FieldDefinition(
        field_name="warnings",
        field_class=FieldClass.METADATA,
        canonical_name=None,
        description="Count of warnings",
        is_countable=True,
        notes="METADATA: Validation result count."
    ),
    "failed": FieldDefinition(
        field_name="failed",
        field_class=FieldClass.METADATA,
        canonical_name=None,
        description="Count of failed validations",
        is_countable=True,
        notes="METADATA: Validation result count."
    ),
    "missing": FieldDefinition(
        field_name="missing",
        field_class=FieldClass.METADATA,
        canonical_name=None,
        description="Count of missing fields",
        is_countable=True,
        notes="METADATA: Validation result count."
    ),
    "exploratory": FieldDefinition(
        field_name="exploratory",
        field_class=FieldClass.METADATA,
        canonical_name=None,
        description="Count of exploratory metrics",
        is_countable=True,
        notes="METADATA: Validation result count."
    ),
    
    # =========================================================================
    # QUANTUM INFORMATION METRICS - High-frequency scientific fields
    # =========================================================================
    
    "fidelity": FieldDefinition(
        field_name="fidelity",
        field_class=FieldClass.METRIC,
        canonical_name="quantum_fidelity",
        description="Quantum state fidelity",
        valid_range=(0.0, 1.0),
        notes="METRIC: F(ρ,σ) = (Tr√(√ρ σ √ρ))². Higher is better."
    ),
    "visibility": FieldDefinition(
        field_name="visibility",
        field_class=FieldClass.METRIC,
        canonical_name="quantum_visibility",
        description="Quantum interference visibility",
        valid_range=(0.0, 1.0),
        notes="METRIC: V = (max - min) / (max + min). Higher is better."
    ),
    "entanglement": FieldDefinition(
        field_name="entanglement",
        field_class=FieldClass.METRIC,
        canonical_name="entanglement_measure",
        description="Entanglement measure",
        valid_range=(0.0, None),
        notes="METRIC: Various measures (concurrence, negativity, etc.)."
    ),
    "decoherence_rate": FieldDefinition(
        field_name="decoherence_rate",
        field_class=FieldClass.METRIC,
        canonical_name="decoherence_rate",
        description="Decoherence rate",
        unit="Hz",
        valid_range=(0.0, None),
        notes="METRIC: Rate of quantum coherence loss."
    ),
    "hamming_weight": FieldDefinition(
        field_name="hamming_weight",
        field_class=FieldClass.METRIC,
        canonical_name="hamming_weight",
        description="Hamming weight of quantum state",
        valid_range=(0, None),
        notes="METRIC: Count of 1-bits in binary representation."
    ),
    
    # =========================================================================
    # PHI-RELATED METRICS - IIT and consciousness measures
    # =========================================================================
    
    "phi_iit": FieldDefinition(
        field_name="phi_iit",
        field_class=FieldClass.METRIC,
        canonical_name="phi_iit_score",
        description="Integrated Information Theory phi measure",
        valid_range=(0.0, None),
        notes="METRIC: IIT consciousness measure. EXPLORATORY."
    ),
    "phi_iit_measured": FieldDefinition(
        field_name="phi_iit_measured",
        field_class=FieldClass.METRIC,
        canonical_name="phi_iit_score",
        description="Measured IIT phi value",
        valid_range=(0.0, None),
        notes="METRIC: Measured integrated information."
    ),
    "phi_iit_std": FieldDefinition(
        field_name="phi_iit_std",
        field_class=FieldClass.METRIC,
        canonical_name="phi_iit_uncertainty",
        description="Uncertainty in IIT phi measurement",
        valid_range=(0.0, None),
        notes="METRIC: Standard deviation of phi measurements."
    ),
    "estimated_phi_iit": FieldDefinition(
        field_name="estimated_phi_iit",
        field_class=FieldClass.METRIC,
        canonical_name="phi_iit_score",
        description="Estimated IIT phi value",
        valid_range=(0.0, None),
        notes="METRIC: Estimated integrated information."
    ),
    
    # =========================================================================
    # STRING/COMPRESSION METRICS - DNA and information theory
    # =========================================================================
    
    "string_compression": FieldDefinition(
        field_name="string_compression",
        field_class=FieldClass.METRIC,
        canonical_name="compression_ratio",
        description="String compression ratio",
        valid_range=(0.0, 1.0),
        notes="METRIC: Compressed/original size. Lower = more structure."
    ),
    "phi_string_health": FieldDefinition(
        field_name="phi_string_health",
        field_class=FieldClass.METRIC,
        canonical_name="phi_string_health",
        description="Health of phi-encoded string",
        valid_range=(0.0, 1.0),
        notes="METRIC: Quality measure for phi-encoded sequences."
    ),
    "phi_string_tension": FieldDefinition(
        field_name="phi_string_tension",
        field_class=FieldClass.METRIC,
        canonical_name="phi_string_tension",
        description="Tension in phi-encoded string",
        valid_range=(0.0, None),
        notes="METRIC: Deviation from optimal phi encoding."
    ),
    
    # =========================================================================
    # COUPLING/INTERACTION METRICS
    # =========================================================================
    
    "coupling_strength": FieldDefinition(
        field_name="coupling_strength",
        field_class=FieldClass.METRIC,
        canonical_name="coupling_strength",
        description="Coupling strength between systems",
        valid_range=(0.0, None),
        notes="METRIC: Interaction strength measure."
    ),
    "coupling_ratio": FieldDefinition(
        field_name="coupling_ratio",
        field_class=FieldClass.METRIC,
        canonical_name="coupling_ratio",
        description="Ratio of coupling strengths",
        valid_range=(0.0, None),
        notes="METRIC: Relative coupling measure."
    ),
    
    # =========================================================================
    # DNA/GENOMIC METRICS
    # =========================================================================
    
    "gc_content": FieldDefinition(
        field_name="gc_content",
        field_class=FieldClass.METRIC,
        canonical_name="gc_content",
        description="GC content of DNA sequence",
        valid_range=(0.0, 1.0),
        notes="METRIC: Fraction of G+C bases. Biological significance."
    ),
    "dna_correlation": FieldDefinition(
        field_name="dna_correlation",
        field_class=FieldClass.METRIC,
        canonical_name="dna_correlation",
        description="Correlation in DNA sequence",
        valid_range=(-1.0, 1.0),
        notes="METRIC: Autocorrelation or cross-correlation measure."
    ),
    
    # =========================================================================
    # QCD/PHYSICS METRICS
    # =========================================================================
    
    "qcd_confinement": FieldDefinition(
        field_name="qcd_confinement",
        field_class=FieldClass.METRIC,
        canonical_name="qcd_confinement",
        description="QCD confinement measure",
        valid_range=(0.0, None),
        notes="METRIC: Quantum chromodynamics confinement measure. EXPLORATORY."
    ),
    
    # =========================================================================
    # TRAINING/ML METRICS - Parameters, not metrics
    # =========================================================================
    
    "requested_epochs": FieldDefinition(
        field_name="requested_epochs",
        field_class=FieldClass.PARAMETER,
        canonical_name=None,
        description="Number of training epochs requested",
        is_countable=True,
        notes="PARAMETER: Training configuration."
    ),
    "best_checkpoint": FieldDefinition(
        field_name="best_checkpoint",
        field_class=FieldClass.METADATA,
        canonical_name=None,
        description="Best checkpoint information",
        notes="METADATA: Training state."
    ),
    "learning_rate": FieldDefinition(
        field_name="learning_rate",
        field_class=FieldClass.PARAMETER,
        canonical_name=None,
        description="Learning rate for training",
        valid_range=(0.0, 1.0),
        notes="PARAMETER: Optimizer configuration."
    ),
    "val_loss": FieldDefinition(
        field_name="val_loss",
        field_class=FieldClass.METRIC,
        canonical_name="validation_loss",
        description="Validation loss",
        valid_range=(0.0, None),
        notes="METRIC: Model performance measure."
    ),
    "recon_loss": FieldDefinition(
        field_name="recon_loss",
        field_class=FieldClass.METRIC,
        canonical_name="reconstruction_loss",
        description="Reconstruction loss",
        valid_range=(0.0, None),
        notes="METRIC: VAE reconstruction quality."
    ),
    "kl_loss": FieldDefinition(
        field_name="kl_loss",
        field_class=FieldClass.METRIC,
        canonical_name="kl_divergence",
        description="KL divergence loss",
        valid_range=(0.0, None),
        notes="METRIC: VAE latent space regularization."
    ),
}


# =============================================================================
# PATTERN-BASED CLASSIFICATION
# =============================================================================

# Patterns for automatic classification
METADATA_PATTERNS = {
    "_time", "_date", "_at", "timestamp", "mtime", "ctime", "atime",
    "_path", "_file", "_id", "_hash", "uuid", "guid",
    "index", "count", "total", "num", "n_", "len", "length"
}

PARAMETER_PATTERNS = {
    "shots", "qubits", "depth", "temperature", "cost",
    "backend", "device", "simulator", "reps", "iterations"
}

PROVENANCE_PATTERNS = {
    "job_id", "experiment_id", "run_id", "session_id",
    "source", "origin", "lineage", "parent"
}

DESCRIPTOR_PATTERNS = {
    "signature", "pattern", "feature", "embedding",
    "latent", "hidden", "derived"
}


def classify_field(field_name: str) -> FieldDefinition:
    """
    Classify a field into the taxonomy.
    
    Args:
        field_name: Name of the field to classify
        
    Returns:
        FieldDefinition with classification
    """
    # Check if in registry
    if field_name in FIELD_TAXONOMY:
        return FIELD_TAXONOMY[field_name]
    
    # Check for wildcard patterns in canonical aliases
    field_lower = field_name.lower()
    
    # Check for nested paths (e.g., "coherence.t1_us")
    base_name = field_name.split(".")[-1].split("[")[-1].rstrip("]")
    
    if base_name in FIELD_TAXONOMY:
        return FIELD_TAXONOMY[base_name]
    
    # Pattern-based classification
    for pattern in METADATA_PATTERNS:
        if pattern in field_lower:
            return FieldDefinition(
                field_name=field_name,
                field_class=FieldClass.METADATA,
                canonical_name=None,
                description=f"Auto-classified metadata field: {field_name}",
                notes="METADATA: Auto-classified by pattern."
            )
    
    for pattern in PARAMETER_PATTERNS:
        if pattern in field_lower:
            return FieldDefinition(
                field_name=field_name,
                field_class=FieldClass.PARAMETER,
                canonical_name=None,
                description=f"Auto-classified parameter field: {field_name}",
                notes="PARAMETER: Auto-classified by pattern."
            )
    
    for pattern in PROVENANCE_PATTERNS:
        if pattern in field_lower:
            return FieldDefinition(
                field_name=field_name,
                field_class=FieldClass.PROVENANCE,
                canonical_name=None,
                description=f"Auto-classified provenance field: {field_name}",
                notes="PROVENANCE: Auto-classified by pattern."
            )
    
    for pattern in DESCRIPTOR_PATTERNS:
        if pattern in field_lower:
            return FieldDefinition(
                field_name=field_name,
                field_class=FieldClass.DESCRIPTOR,
                canonical_name=None,
                description=f"Auto-classified descriptor field: {field_name}",
                notes="DESCRIPTOR: Auto-classified by pattern. No formal definition."
            )
    
    # Default: unknown metric (needs registration)
    return FieldDefinition(
        field_name=field_name,
        field_class=FieldClass.METRIC,  # Assume metric until proven otherwise
        canonical_name=None,
        description=f"Unknown field: {field_name}",
        notes="UNKNOWN: Needs registration in field taxonomy."
    )


def get_field_class_summary() -> Dict[str, int]:
    """Get summary of registered fields by class."""
    summary = {fc.value: 0 for fc in FieldClass}
    for field_def in FIELD_TAXONOMY.values():
        summary[field_def.field_class.value] += 1
    return summary


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("FIELD TAXONOMY FOR SCIENTIFIC GOVERNANCE")
    print("=" * 70)
    
    summary = get_field_class_summary()
    print(f"\nREGISTERED FIELDS BY CLASS:")
    for field_class, count in summary.items():
        symbol = {
            "metric": "📊",
            "parameter": "⚙️",
            "metadata": "📁",
            "provenance": "🔗",
            "descriptor": "🔍"
        }.get(field_class, "?")
        print(f"  {symbol} {field_class}: {count}")
    
    print(f"\nTOTAL REGISTERED: {len(FIELD_TAXONOMY)}")
    
    # Test classification
    print("\n" + "=" * 70)
    print("CLASSIFICATION TESTS")
    print("=" * 70)
    
    test_fields = [
        "phi_resonance",
        "shots",
        "qubits",
        "temperature",
        "transpiled_depth",
        "cost",
        "consciousness_signature",
        "mtime",
        "job_id",
        "unique_states",
        "measured_phi",
        "predicted_phi",
        "backend_analyses[0].coherence.avg_t1_us",
        "unknown_new_field"
    ]
    
    for field_name in test_fields:
        field_def = classify_field(field_name)
        print(f"\n  {field_name}")
        print(f"    Class: {field_def.field_class.value}")
        print(f"    Canonical: {field_def.canonical_name or 'N/A'}")
        print(f"    Notes: {field_def.notes}")