"""
Canonical Alias Mapping Layer
=============================

Maps legacy nested paths to canonical registry names.
Collapses 199 unknown fields into a smaller set of canonical definitions.

Date: April 15, 2026
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class MetricClass(Enum):
    """Classification of metric types"""
    RAW_RATIO = "raw_ratio"              # Unnormalized ratios (can be any positive value)
    TARGET_CONSTANT = "target_constant"  # Mathematical constants used as targets
    NORMALIZED_SCORE = "normalized_score"  # Bounded scores in [0, 1]
    SIGNED_CORRELATION = "signed_correlation"  # Correlation-like measures in [-1, 1]
    BOUNDED_ENTROPY = "bounded_entropy"  # Entropy-like measures in [0, log(d)]
    UNBOUNDED_POSITIVE = "unbounded_positive"  # Positive measures with no upper bound
    UNBOUNDED_SIGNED = "unbounded_signed"  # Signed measures with no bounds


class GovernanceStatus(Enum):
    """Governance status for metrics"""
    VALIDATED = "validated"      # Passed all tests, can support claims
    PASSED = "passed"            # Passed numerical validity
    PROVISIONAL = "provisional"  # Defined but needs validation
    EXPLORATORY = "exploratory"  # Hypothesis-generating only
    INVALID = "invalid"          # Must be repaired
    UNKNOWN = "unknown"          # Not in registry


@dataclass
class CanonicalMetric:
    """Canonical metric definition"""
    canonical_name: str
    metric_class: MetricClass
    governance_status: GovernanceStatus
    valid_range: Tuple[Optional[float], Optional[float]]
    description: str
    equation: Optional[str]
    null_model: Optional[str]
    legacy_aliases: List[str]
    notes: str


# =============================================================================
# CANONICAL METRIC REGISTRY
# =============================================================================

CANONICAL_METRICS: Dict[str, CanonicalMetric] = {
    
    # =========================================================================
    # VALIDATED METRICS (Hardware-backed, passed all tests)
    # =========================================================================
    
    "phi_invariant_score": CanonicalMetric(
        canonical_name="phi_invariant_score",
        metric_class=MetricClass.NORMALIZED_SCORE,
        governance_status=GovernanceStatus.VALIDATED,
        valid_range=(0.0, 1.0),
        description="Sierpinski circuit invariant score, validated on IBM hardware",
        equation="S_inv = surviving_patterns / total_patterns",
        null_model="Random circuit: expected ~0.5",
        legacy_aliases=[
            "phi_invariant_score",
            "sierpinski_invariant",
            "invariant_score"
        ],
        notes="VALIDATED: 40+ IBM runs, 225k+ shots. Expected value ≈ 1/φ ≈ 0.618"
    ),
    
    "platonic_alignment_score": CanonicalMetric(
        canonical_name="platonic_alignment_score",
        metric_class=MetricClass.NORMALIZED_SCORE,
        governance_status=GovernanceStatus.VALIDATED,
        valid_range=(0.0, 1.0),
        description="Alignment score between molecular geometry and Platonic solids",
        equation="P_s = exp(-mean(min_distances))",
        null_model="Random point cloud: expected ~0.6",
        legacy_aliases=[
            "platonic_alignment_score",
            "platonic_scores.*",
            "geometry.platonic_alignment"
        ],
        notes="VALIDATED: Methane scores higher than random (0.65 > 0.42)"
    ),
    
    "quantum_coherence": CanonicalMetric(
        canonical_name="quantum_coherence",
        metric_class=MetricClass.NORMALIZED_SCORE,
        governance_status=GovernanceStatus.VALIDATED,
        valid_range=(0.0, 1.0),
        description="Quantum coherence via off-diagonal density matrix elements",
        equation="C = sum(|rho_ij|) / (n*(n-1))",
        null_model="Random phases: expected ~2/(π*n)",
        legacy_aliases=[
            "quantum_coherence",
            "coherence",
            "quantum_coherence_value",
            "*.quantum_coherence"
        ],
        notes="VALIDATED: Passed numerical validity tests"
    ),
    
    # =========================================================================
    # PASSED METRICS (Numerical validity confirmed)
    # =========================================================================
    
    "entanglement_entropy": CanonicalMetric(
        canonical_name="entanglement_entropy",
        metric_class=MetricClass.BOUNDED_ENTROPY,
        governance_status=GovernanceStatus.PASSED,
        valid_range=(0.0, None),  # Upper bound is log(d_A)
        description="Von Neumann entanglement entropy",
        equation="S = -sum(lambda_i * log(lambda_i))",
        null_model="Random state: expected ~log(d_A) - O(1/d_A)",
        legacy_aliases=[
            "entanglement_entropy",
            "entropy",
            "metrics.entanglement_entropy",
            "wormhole.entropy_s",
            "*.entanglement_entropy",
            "*.metrics.entanglement_entropy"
        ],
        notes="PASSED: Non-negative values confirmed. Complexity prediction WEAKENED."
    ),
    
    "phi_ratio_proximity": CanonicalMetric(
        canonical_name="phi_ratio_proximity",
        metric_class=MetricClass.NORMALIZED_SCORE,
        governance_status=GovernanceStatus.PASSED,
        valid_range=(0.0, 1.0),
        description="Proximity to golden ratio in geometric ratios",
        equation="R_phi = exp(-alpha * min|r_i - phi|)",
        null_model="Random geometry: expected ~0.6",
        legacy_aliases=[
            "phi_ratio_proximity",
            "near_phi_ratio",
            "phi_proximity"
        ],
        notes="PASSED: Icosahedron has proximity < 1e-4"
    ),
    
    # =========================================================================
    # PROVISIONAL METRICS (Defined but need validation)
    # =========================================================================
    
    "phi_resonance_score": CanonicalMetric(
        canonical_name="phi_resonance_score",
        metric_class=MetricClass.NORMALIZED_SCORE,
        governance_status=GovernanceStatus.PROVISIONAL,
        valid_range=(0.0, 1.0),
        description="Normalized phi-alignment score",
        equation="R_phi = exp(-alpha * min|r_i - phi|)",
        null_model="Random geometry: expected ~0.6",
        legacy_aliases=[
            "phi_resonance",
            "phi_resonance_score",
            "mean_phi_resonance",
            "geometry.phi_resonance",
            "*.phi_resonance",
            "results.*.phi_resonance"
        ],
        notes="PROVISIONAL: Must be in [0,1]. Values >1 indicate raw ratio, not normalized score."
    ),
    
    "phi_coherence": CanonicalMetric(
        canonical_name="phi_coherence",
        metric_class=MetricClass.NORMALIZED_SCORE,
        governance_status=GovernanceStatus.PROVISIONAL,
        valid_range=(0.0, 1.0),
        description="Phi-based coherence measure",
        equation="C_phi = 1 - |L/L_phi - 1| / 2",
        null_model="Random sequence: expected ~0.5",
        legacy_aliases=[
            "phi_coherence",
            "mean_phi_coherence",
            "*.phi_coherence"
        ],
        notes="PROVISIONAL: Not significant vs null model (z=1.95). Needs more data."
    ),
    
    "biomimetic_resonance": CanonicalMetric(
        canonical_name="biomimetic_resonance",
        metric_class=MetricClass.NORMALIZED_SCORE,
        governance_status=GovernanceStatus.PROVISIONAL,
        valid_range=(0.0, 1.0),
        description="Correlation with biological reference patterns",
        equation="R_bio = (corr(X_system, X_bio) + 1) / 2",
        null_model="Random features: expected ~0.5",
        legacy_aliases=[
            "biomimetic_resonance",
            "biomimetic_resonance_value",
            "*.biomimetic_resonance"
        ],
        notes="PROVISIONAL: Values >1 are INVALID. Must be normalized to [0,1]."
    ),
    
    "tesseract_symmetry": CanonicalMetric(
        canonical_name="tesseract_symmetry",
        metric_class=MetricClass.NORMALIZED_SCORE,
        governance_status=GovernanceStatus.PROVISIONAL,
        valid_range=(0.0, 1.0),
        description="4D tesseract symmetry measure",
        equation="T_4 = 1 - std(R) / mean(R)",
        null_model="Random 4D points: expected ~0.3",
        legacy_aliases=[
            "tesseract_symmetry",
            "geometry.tesseract_symmetry",
            "*.tesseract_symmetry",
            "results.*.tesseract_symmetry"
        ],
        notes="PROVISIONAL: T_4 = 1 for regular hypercube."
    ),
    
    # =========================================================================
    # RAW RATIOS (Unnormalized, can be any positive value)
    # =========================================================================
    
    "phi_ratio": CanonicalMetric(
        canonical_name="phi_ratio",
        metric_class=MetricClass.RAW_RATIO,
        governance_status=GovernanceStatus.EXPLORATORY,
        valid_range=(0.0, None),
        description="Raw golden ratio measurement",
        equation="r = d_i / d_j for geometric distances",
        null_model="Random distances: expected ~1.0",
        legacy_aliases=[
            "phi_ratio",
            "dna_phi_ratio",
            "golden_ratio",
            "*.phi_ratio"
        ],
        notes="EXPLORATORY: Raw ratio, not normalized. Can be any positive value."
    ),
    
    "phi_ratio_inverse": CanonicalMetric(
        canonical_name="phi_ratio_inverse",
        metric_class=MetricClass.RAW_RATIO,
        governance_status=GovernanceStatus.EXPLORATORY,
        valid_range=(0.0, None),
        description="Inverse golden ratio measurement",
        equation="1/phi ≈ 0.618",
        null_model="N/A - this is a derived constant",
        legacy_aliases=[
            "phi_ratio_inverse",
            "phi_inv",
            "tmt_ratios.phi_inv"
        ],
        notes="EXPLORATORY: Derived constant. Expected value ≈ 0.618."
    ),
    
    # =========================================================================
    # TARGET CONSTANTS (Mathematical constants, not measurements)
    # =========================================================================
    
    "phi_target_constant": CanonicalMetric(
        canonical_name="phi_target_constant",
        metric_class=MetricClass.TARGET_CONSTANT,
        governance_status=GovernanceStatus.EXPLORATORY,
        valid_range=(None, None),
        description="Golden ratio target constant",
        equation="phi = (1 + sqrt(5)) / 2 ≈ 1.618",
        null_model="N/A - this is a mathematical constant",
        legacy_aliases=[
            "phi_target",
            "phi_resonance_target",
            "tmt_ratios.phi",
            "*.phi_target",
            "config.phi_resonance_target"
        ],
        notes="EXPLORATORY: This is a CONSTANT, not a measurement. Value should be ≈ 1.618."
    ),
    
    # =========================================================================
    # EXPLORATORY METRICS (Hypothesis-generating only)
    # =========================================================================
    
    "consciousness_level": CanonicalMetric(
        canonical_name="consciousness_level",
        metric_class=MetricClass.NORMALIZED_SCORE,
        governance_status=GovernanceStatus.EXPLORATORY,
        valid_range=(0.0, 1.0),
        description="Consciousness level indicator (NOT VALIDATED)",
        equation="NOT FORMALLY DEFINED",
        null_model="NOT DEFINED",
        legacy_aliases=[
            "consciousness_level",
            "consciousness",
            "*.consciousness_level",
            "tmt_ratios.observed_consciousness",
            "tmt_ratios.expected_consciousness"
        ],
        notes="EXPLORATORY: NO FORMAL DEFINITION. Values >1 are INVALID. Use with extreme caution."
    ),
    
    "temporal_asymmetry": CanonicalMetric(
        canonical_name="temporal_asymmetry",
        metric_class=MetricClass.NORMALIZED_SCORE,
        governance_status=GovernanceStatus.EXPLORATORY,
        valid_range=(0.0, 1.0),
        description="Temporal asymmetry measure",
        equation="NOT FORMALLY DEFINED",
        null_model="NOT DEFINED",
        legacy_aliases=[
            "temporal_asymmetry",
            "retrocausal.temporal_asymmetry",
            "*.temporal_asymmetry"
        ],
        notes="EXPLORATORY: Needs formal definition and validation."
    ),
    
    "lucas_resonance": CanonicalMetric(
        canonical_name="lucas_resonance",
        metric_class=MetricClass.NORMALIZED_SCORE,
        governance_status=GovernanceStatus.EXPLORATORY,
        valid_range=(0.0, 1.0),
        description="Lucas number resonance measure",
        equation="NOT FORMALLY DEFINED",
        null_model="NOT DEFINED",
        legacy_aliases=[
            "lucas_resonance",
            "retrocausal.lucas_resonance",
            "*.lucas_resonance"
        ],
        notes="EXPLORATORY: Needs formal definition and validation."
    ),
    
    "wormhole_coherence": CanonicalMetric(
        canonical_name="wormhole_coherence",
        metric_class=MetricClass.NORMALIZED_SCORE,
        governance_status=GovernanceStatus.EXPLORATORY,
        valid_range=(0.0, 1.0),
        description="Wormhole coherence measure",
        equation="NOT FORMALLY DEFINED",
        null_model="NOT DEFINED",
        legacy_aliases=[
            "wormhole_coherence",
            "wormhole.coherence_r",
            "*.wormhole_coherence"
        ],
        notes="EXPLORATORY: Needs formal definition. Values >1 are INVALID."
    ),
    
    # =========================================================================
    # QUANTUM HARDWARE METRICS (IBM backend calibration)
    # =========================================================================
    
    "t1_coherence_time": CanonicalMetric(
        canonical_name="t1_coherence_time",
        metric_class=MetricClass.UNBOUNDED_POSITIVE,
        governance_status=GovernanceStatus.VALIDATED,
        valid_range=(0.0, None),
        description="T1 relaxation time in microseconds",
        equation="T1 = time for |1⟩ to decay to |0⟩",
        null_model="N/A - hardware measurement",
        legacy_aliases=[
            "t1", "t1_us", "avg_t1_us", "median_t1_us",
            "coherence.t1", "coherence.avg_t1_us", "coherence.median_t1_us",
            "*.t1_us", "*.avg_t1_us"
        ],
        notes="VALIDATED: Direct hardware measurement. Higher is better."
    ),
    
    "t2_coherence_time": CanonicalMetric(
        canonical_name="t2_coherence_time",
        metric_class=MetricClass.UNBOUNDED_POSITIVE,
        governance_status=GovernanceStatus.VALIDATED,
        valid_range=(0.0, None),
        description="T2 dephasing time in microseconds",
        equation="T2 = time for phase coherence loss",
        null_model="N/A - hardware measurement",
        legacy_aliases=[
            "t2", "t2_us", "avg_t2_us", "median_t2_us",
            "coherence.t2", "coherence.avg_t2_us", "coherence.median_t2_us",
            "*.t2_us", "*.avg_t2_us"
        ],
        notes="VALIDATED: Direct hardware measurement. T2 ≤ 2*T1."
    ),
    
    "gate_error_rate": CanonicalMetric(
        canonical_name="gate_error_rate",
        metric_class=MetricClass.NORMALIZED_SCORE,
        governance_status=GovernanceStatus.VALIDATED,
        valid_range=(0.0, 1.0),
        description="Quantum gate error rate",
        equation="error_rate = 1 - fidelity",
        null_model="N/A - hardware measurement",
        legacy_aliases=[
            "gate_error", "error_rate", "single_qubit_error", "two_qubit_error",
            "gate_performance.single_qubit_error", "gate_performance.two_qubit_error",
            "*.gate_error", "*.error_rate"
        ],
        notes="VALIDATED: Lower is better. Typical: 1e-4 to 1e-2."
    ),
    
    "readout_error_rate": CanonicalMetric(
        canonical_name="readout_error_rate",
        metric_class=MetricClass.NORMALIZED_SCORE,
        governance_status=GovernanceStatus.VALIDATED,
        valid_range=(0.0, 1.0),
        description="Measurement readout error rate",
        equation="error = P(wrong readout)",
        null_model="N/A - hardware measurement",
        legacy_aliases=[
            "readout_error", "readout_error_rate",
            "gate_performance.readout_error",
            "*.readout_error"
        ],
        notes="VALIDATED: Lower is better. Typical: 1e-3 to 5e-2."
    ),
    
    "hardware_quality_score": CanonicalMetric(
        canonical_name="hardware_quality_score",
        metric_class=MetricClass.NORMALIZED_SCORE,
        governance_status=GovernanceStatus.PASSED,
        valid_range=(0.0, 1.0),
        description="Overall hardware quality score",
        equation="composite of T1, T2, gate errors",
        null_model="N/A - composite metric",
        legacy_aliases=[
            "quality_score", "overall_quality", "hardware_quality",
            "coherence.quality_score", "gate_performance.quality_score",
            "overall.quality_score", "*.quality_score"
        ],
        notes="PASSED: Composite metric. Higher is better."
    ),
    
    # =========================================================================
    # SACRED GEOMETRY DISCOVERY METRICS
    # =========================================================================
    
    "sacred_score": CanonicalMetric(
        canonical_name="sacred_score",
        metric_class=MetricClass.NORMALIZED_SCORE,
        governance_status=GovernanceStatus.PROVISIONAL,
        valid_range=(0.0, 1.0),
        description="Sacred geometry alignment score",
        equation="composite of phi, platonic, and tesseract measures",
        null_model="Random geometry: expected ~0.3",
        legacy_aliases=[
            "sacred_score", "geometry_score", "sacred_alignment",
            "*.sacred_score", "discoveries.*.sacred_score"
        ],
        notes="PROVISIONAL: Must be in [0,1]. Composite of multiple geometry metrics."
    ),
    
    "phi_alignment": CanonicalMetric(
        canonical_name="phi_alignment",
        metric_class=MetricClass.NORMALIZED_SCORE,
        governance_status=GovernanceStatus.PROVISIONAL,
        valid_range=(0.0, 1.0),
        description="Alignment with golden ratio",
        equation="1 - |ratio - phi| / phi",
        null_model="Random ratios: expected ~0.38",
        legacy_aliases=[
            "phi_alignment", "golden_alignment",
            "*.phi_alignment", "discoveries.*.phi_alignment"
        ],
        notes="PROVISIONAL: Must be in [0,1]. Values >1 indicate raw ratio."
    ),
    
    "total_discoveries": CanonicalMetric(
        canonical_name="total_discoveries",
        metric_class=MetricClass.UNBOUNDED_POSITIVE,
        governance_status=GovernanceStatus.PASSED,
        valid_range=(0, None),
        description="Count of significant discoveries",
        equation="count(discoveries where score > threshold)",
        null_model="N/A - count metric",
        legacy_aliases=[
            "total_discoveries", "discovery_count", "num_discoveries",
            "*.total_discoveries"
        ],
        notes="PASSED: Count metric. Non-negative integer."
    ),
    
    "phi_shift": CanonicalMetric(
        canonical_name="phi_shift",
        metric_class=MetricClass.SIGNED_CORRELATION,
        governance_status=GovernanceStatus.EXPLORATORY,
        valid_range=(-1.0, 1.0),
        description="Deviation from phi baseline",
        equation="shift = measured - expected_phi",
        null_model="Random: expected ~0",
        legacy_aliases=[
            "phi_shift", "estimated_phi_shift", "*.estimated_phi_shift"
        ],
        notes="EXPLORATORY: Small deviations from phi baseline."
    ),
    
    "t2_t1_ratio": CanonicalMetric(
        canonical_name="t2_t1_ratio",
        metric_class=MetricClass.NORMALIZED_SCORE,
        governance_status=GovernanceStatus.PASSED,
        valid_range=(0.0, 2.0),
        description="Ratio of T2 to T1 coherence times",
        equation="T2/T1",
        null_model="N/A - hardware measurement",
        legacy_aliases=[
            "t2_t1_ratio", "coherence.t2_t1_ratio", "*.t2_t1_ratio"
        ],
        notes="PASSED: T2 ≤ 2*T1. Higher is better."
    ),
    
    # =========================================================================
    # QUANTUM INFORMATION METRICS
    # =========================================================================
    
    "quantum_fidelity": CanonicalMetric(
        canonical_name="quantum_fidelity",
        metric_class=MetricClass.NORMALIZED_SCORE,
        governance_status=GovernanceStatus.VALIDATED,
        valid_range=(0.0, 1.0),
        description="Quantum state fidelity",
        equation="F(ρ,σ) = (Tr√(√ρ σ √ρ))²",
        null_model="Random states: expected ~1/d",
        legacy_aliases=[
            "fidelity", "quantum_fidelity", "*.fidelity",
            "quantum_metrics.fidelity", "best_checkpoint.quantum_metrics.fidelity"
        ],
        notes="VALIDATED: Higher is better. F=1 for identical states."
    ),
    
    "quantum_visibility": CanonicalMetric(
        canonical_name="quantum_visibility",
        metric_class=MetricClass.NORMALIZED_SCORE,
        governance_status=GovernanceStatus.PASSED,
        valid_range=(0.0, 1.0),
        description="Quantum interference visibility",
        equation="V = (max - min) / (max + min)",
        null_model="Random: expected ~0.5",
        legacy_aliases=[
            "visibility", "quantum_visibility", "*.visibility",
            "stealth_visibility"
        ],
        notes="PASSED: Higher is better. V=1 for perfect coherence."
    ),
    
    "entanglement_measure": CanonicalMetric(
        canonical_name="entanglement_measure",
        metric_class=MetricClass.UNBOUNDED_POSITIVE,
        governance_status=GovernanceStatus.PASSED,
        valid_range=(0.0, None),
        description="Entanglement measure",
        equation="Various: concurrence, negativity, entropy",
        null_model="Separable states: expected 0",
        legacy_aliases=[
            "entanglement", "entanglement_measure", "*.entanglement"
        ],
        notes="PASSED: Non-negative. 0 for separable states."
    ),
    
    "decoherence_rate": CanonicalMetric(
        canonical_name="decoherence_rate",
        metric_class=MetricClass.UNBOUNDED_POSITIVE,
        governance_status=GovernanceStatus.PASSED,
        valid_range=(0.0, None),
        description="Decoherence rate",
        equation="Γ = 1/T2",
        null_model="N/A - hardware measurement",
        legacy_aliases=[
            "decoherence_rate", "decoherence_Hz", "*.decoherence_rate"
        ],
        notes="PASSED: Rate of coherence loss. Lower is better."
    ),
    
    "hamming_weight": CanonicalMetric(
        canonical_name="hamming_weight",
        metric_class=MetricClass.UNBOUNDED_POSITIVE,
        governance_status=GovernanceStatus.VALIDATED,
        valid_range=(0, None),
        description="Hamming weight of quantum state",
        equation="HW = count of 1-bits",
        null_model="Random: expected n/2",
        legacy_aliases=[
            "hamming_weight", "hw", "*.hamming_weight",
            "val_losses.hamming"
        ],
        notes="VALIDATED: Count metric. Non-negative integer."
    ),
    
    # =========================================================================
    # IIT/CONSCIOUSNESS METRICS (EXPLORATORY)
    # =========================================================================
    
    "phi_iit_score": CanonicalMetric(
        canonical_name="phi_iit_score",
        metric_class=MetricClass.UNBOUNDED_POSITIVE,
        governance_status=GovernanceStatus.EXPLORATORY,
        valid_range=(0.0, None),
        description="Integrated Information Theory phi measure",
        equation="Φ = minimum information partition",
        null_model="NOT FORMALIZED",
        legacy_aliases=[
            "phi_iit", "phi_iit_measured", "estimated_phi_iit",
            "*.phi_iit", "*.phi_iit_measured"
        ],
        notes="EXPLORATORY: IIT consciousness measure. No formal validation."
    ),
    
    "phi_iit_uncertainty": CanonicalMetric(
        canonical_name="phi_iit_uncertainty",
        metric_class=MetricClass.UNBOUNDED_POSITIVE,
        governance_status=GovernanceStatus.EXPLORATORY,
        valid_range=(0.0, None),
        description="Uncertainty in IIT phi measurement",
        equation="σ_Φ",
        null_model="NOT FORMALIZED",
        legacy_aliases=[
            "phi_iit_std", "*.phi_iit_std"
        ],
        notes="EXPLORATORY: Measurement uncertainty."
    ),
    
    # =========================================================================
    # STRING/COMPRESSION METRICS
    # =========================================================================
    
    "compression_ratio": CanonicalMetric(
        canonical_name="compression_ratio",
        metric_class=MetricClass.NORMALIZED_SCORE,
        governance_status=GovernanceStatus.PASSED,
        valid_range=(0.0, 1.0),
        description="String compression ratio",
        equation="CR = compressed_size / original_size",
        null_model="Random: expected ~1.0",
        legacy_aliases=[
            "string_compression", "compression_ratio", "*.string_compression"
        ],
        notes="PASSED: Lower = more structure. Random data ~1.0."
    ),
    
    "phi_string_health": CanonicalMetric(
        canonical_name="phi_string_health",
        metric_class=MetricClass.NORMALIZED_SCORE,
        governance_status=GovernanceStatus.PROVISIONAL,
        valid_range=(0.0, 1.0),
        description="Health of phi-encoded string",
        equation="NOT FORMALIZED",
        null_model="NOT DEFINED",
        legacy_aliases=[
            "phi_string_health", "*.phi_string_health"
        ],
        notes="PROVISIONAL: Quality measure for phi-encoded sequences."
    ),
    
    "phi_string_tension": CanonicalMetric(
        canonical_name="phi_string_tension",
        metric_class=MetricClass.UNBOUNDED_POSITIVE,
        governance_status=GovernanceStatus.PROVISIONAL,
        valid_range=(0.0, None),
        description="Tension in phi-encoded string",
        equation="NOT FORMALIZED",
        null_model="NOT DEFINED",
        legacy_aliases=[
            "phi_string_tension", "*.phi_string_tension"
        ],
        notes="PROVISIONAL: Deviation from optimal phi encoding."
    ),
    
    # =========================================================================
    # COUPLING METRICS
    # =========================================================================
    
    "coupling_strength": CanonicalMetric(
        canonical_name="coupling_strength",
        metric_class=MetricClass.UNBOUNDED_POSITIVE,
        governance_status=GovernanceStatus.PROVISIONAL,
        valid_range=(0.0, None),
        description="Coupling strength between systems",
        equation="J (coupling constant)",
        null_model="N/A - system property",
        legacy_aliases=[
            "coupling_strength", "*.coupling_strength"
        ],
        notes="PROVISIONAL: Interaction strength measure."
    ),
    
    "coupling_ratio": CanonicalMetric(
        canonical_name="coupling_ratio",
        metric_class=MetricClass.RAW_RATIO,
        governance_status=GovernanceStatus.PROVISIONAL,
        valid_range=(0.0, None),
        description="Ratio of coupling strengths",
        equation="J₁/J₂",
        null_model="Random: expected ~1.0",
        legacy_aliases=[
            "coupling_ratio", "*.coupling_ratio"
        ],
        notes="PROVISIONAL: Relative coupling measure."
    ),
    
    # =========================================================================
    # DNA/GENOMIC METRICS
    # =========================================================================
    
    "gc_content": CanonicalMetric(
        canonical_name="gc_content",
        metric_class=MetricClass.NORMALIZED_SCORE,
        governance_status=GovernanceStatus.VALIDATED,
        valid_range=(0.0, 1.0),
        description="GC content of DNA sequence",
        equation="GC = (G+C) / (A+T+G+C)",
        null_model="Random: expected ~0.5",
        legacy_aliases=[
            "gc_content", "*.gc_content"
        ],
        notes="VALIDATED: Fraction of G+C bases. Biological significance."
    ),
    
    "dna_correlation": CanonicalMetric(
        canonical_name="dna_correlation",
        metric_class=MetricClass.SIGNED_CORRELATION,
        governance_status=GovernanceStatus.PROVISIONAL,
        valid_range=(-1.0, 1.0),
        description="Correlation in DNA sequence",
        equation="Autocorrelation or cross-correlation",
        null_model="Random: expected ~0",
        legacy_aliases=[
            "dna_correlation", "*.dna_correlation"
        ],
        notes="PROVISIONAL: Sequence correlation measure."
    ),
    
    # =========================================================================
    # QCD/PHYSICS METRICS
    # =========================================================================
    
    "qcd_confinement": CanonicalMetric(
        canonical_name="qcd_confinement",
        metric_class=MetricClass.UNBOUNDED_POSITIVE,
        governance_status=GovernanceStatus.EXPLORATORY,
        valid_range=(0.0, None),
        description="QCD confinement measure",
        equation="NOT FORMALIZED",
        null_model="NOT DEFINED",
        legacy_aliases=[
            "qcd_confinement", "*.qcd_confinement"
        ],
        notes="EXPLORATORY: Quantum chromodynamics measure. No formal definition."
    ),
    
    # =========================================================================
    # TRAINING/ML METRICS
    # =========================================================================
    
    "validation_loss": CanonicalMetric(
        canonical_name="validation_loss",
        metric_class=MetricClass.UNBOUNDED_POSITIVE,
        governance_status=GovernanceStatus.PASSED,
        valid_range=(0.0, None),
        description="Validation loss",
        equation="L_val = Σ(y - ŷ)²",
        null_model="N/A - model performance",
        legacy_aliases=[
            "val_loss", "validation_loss", "best_val_loss",
            "*.val_loss", "*.best_val_loss"
        ],
        notes="PASSED: Model performance measure. Lower is better."
    ),
    
    "reconstruction_loss": CanonicalMetric(
        canonical_name="reconstruction_loss",
        metric_class=MetricClass.UNBOUNDED_POSITIVE,
        governance_status=GovernanceStatus.PASSED,
        valid_range=(0.0, None),
        description="Reconstruction loss",
        equation="L_recon = ||x - x̂||²",
        null_model="N/A - model performance",
        legacy_aliases=[
            "recon_loss", "reconstruction_loss", "val_losses.recon",
            "*.recon_loss"
        ],
        notes="PASSED: VAE reconstruction quality. Lower is better."
    ),
    
    "kl_divergence": CanonicalMetric(
        canonical_name="kl_divergence",
        metric_class=MetricClass.UNBOUNDED_POSITIVE,
        governance_status=GovernanceStatus.VALIDATED,
        valid_range=(0.0, None),
        description="KL divergence loss",
        equation="KL(q(z|x) || p(z))",
        null_model="N/A - regularization",
        legacy_aliases=[
            "kl_loss", "kl_divergence", "val_losses.kl",
            "*.kl_loss"
        ],
        notes="VALIDATED: VAE latent space regularization. Non-negative."
    ),
}


# =============================================================================
# ALIAS RESOLVER
# =============================================================================

class AliasResolver:
    """Resolves legacy metric names to canonical names."""
    
    def __init__(self):
        self.canonical_metrics = CANONICAL_METRICS
        self._build_alias_map()
    
    def _build_alias_map(self):
        """Build reverse lookup from aliases to canonical names."""
        self.alias_map: Dict[str, str] = {}
        
        for canonical_name, metric in self.canonical_metrics.items():
            for alias in metric.legacy_aliases:
                # Handle wildcard patterns
                if "*" in alias:
                    # Store pattern for later matching
                    if "_patterns" not in dir(self):
                        self._patterns = []
                    self._patterns.append((alias, canonical_name))
                else:
                    self.alias_map[alias.lower()] = canonical_name
    
    def resolve(self, legacy_name: str) -> Tuple[Optional[str], Optional[CanonicalMetric]]:
        """
        Resolve a legacy metric name to its canonical form.
        
        Args:
            legacy_name: Legacy metric name (may include path like "geometry.phi_resonance")
            
        Returns:
            (canonical_name, canonical_metric) or (None, None) if not found
        """
        # Normalize name
        name_lower = legacy_name.lower()
        
        # Direct lookup
        if name_lower in self.alias_map:
            canonical_name = self.alias_map[name_lower]
            return canonical_name, self.canonical_metrics[canonical_name]
        
        # Try extracting last component
        if "." in legacy_name:
            last_component = legacy_name.split(".")[-1].lower()
            if last_component in self.alias_map:
                canonical_name = self.alias_map[last_component]
                return canonical_name, self.canonical_metrics[canonical_name]
        
        # Try pattern matching
        if hasattr(self, '_patterns'):
            for pattern, canonical_name in self._patterns:
                # Convert wildcard pattern to regex
                regex_pattern = pattern.replace(".", r"\.").replace("*", ".*")
                if re.match(regex_pattern, legacy_name, re.IGNORECASE):
                    return canonical_name, self.canonical_metrics[canonical_name]
        
        return None, None
    
    def get_all_aliases(self, canonical_name: str) -> List[str]:
        """Get all legacy aliases for a canonical metric."""
        if canonical_name in self.canonical_metrics:
            return self.canonical_metrics[canonical_name].legacy_aliases
        return []
    
    def get_metrics_by_status(self, status: GovernanceStatus) -> List[str]:
        """Get all canonical metrics with a given status."""
        return [
            name for name, metric in self.canonical_metrics.items()
            if metric.governance_status == status
        ]
    
    def get_metrics_by_class(self, metric_class: MetricClass) -> List[str]:
        """Get all canonical metrics of a given class."""
        return [
            name for name, metric in self.canonical_metrics.items()
            if metric.metric_class == metric_class
        ]


# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

def validate_metric_value(canonical_name: str, value: float) -> Tuple[bool, str]:
    """
    Validate a metric value against its canonical definition.
    
    Returns:
        (is_valid, message)
    """
    if canonical_name not in CANONICAL_METRICS:
        return False, f"Unknown metric: {canonical_name}"
    
    metric = CANONICAL_METRICS[canonical_name]
    min_val, max_val = metric.valid_range
    
    # Check range
    if min_val is not None and value < min_val:
        return False, f"Value {value} below minimum {min_val} for {canonical_name}"
    
    if max_val is not None and value > max_val:
        # Special handling for target constants
        if metric.metric_class == MetricClass.TARGET_CONSTANT:
            return True, f"Target constant value: {value}"
        return False, f"Value {value} above maximum {max_val} for {canonical_name}"
    
    return True, f"Valid value for {canonical_name}"


def classify_value_status(canonical_name: str, value: float) -> GovernanceStatus:
    """
    Classify the governance status of a metric value.
    
    Returns:
        Governance status
    """
    if canonical_name not in CANONICAL_METRICS:
        return GovernanceStatus.UNKNOWN
    
    metric = CANONICAL_METRICS[canonical_name]
    is_valid, _ = validate_metric_value(canonical_name, value)
    
    if not is_valid:
        return GovernanceStatus.INVALID
    
    return metric.governance_status


# =============================================================================
# MIGRATION FUNCTIONS
# =============================================================================

def migrate_legacy_metric(legacy_name: str, value: float) -> Dict:
    """
    Migrate a legacy metric to canonical form.
    
    Returns:
        Migration record with canonical name, status, and notes
    """
    resolver = AliasResolver()
    canonical_name, canonical_metric = resolver.resolve(legacy_name)
    
    if canonical_name is None:
        return {
            "legacy_name": legacy_name,
            "canonical_name": None,
            "value": value,
            "status": GovernanceStatus.UNKNOWN.value,
            "metric_class": None,
            "valid_range": None,
            "notes": "Unknown metric - not in registry"
        }
    
    is_valid, validation_msg = validate_metric_value(canonical_name, value)
    status = classify_value_status(canonical_name, value)
    
    return {
        "legacy_name": legacy_name,
        "canonical_name": canonical_name,
        "value": value,
        "status": status.value,
        "metric_class": canonical_metric.metric_class.value,
        "valid_range": canonical_metric.valid_range,
        "is_valid": is_valid,
        "validation_message": validation_msg,
        "notes": canonical_metric.notes
    }


def get_migration_summary() -> Dict:
    """Get summary of canonical metrics by status."""
    resolver = AliasResolver()
    
    return {
        "total_canonical_metrics": len(CANONICAL_METRICS),
        "by_status": {
            "validated": len(resolver.get_metrics_by_status(GovernanceStatus.VALIDATED)),
            "passed": len(resolver.get_metrics_by_status(GovernanceStatus.PASSED)),
            "provisional": len(resolver.get_metrics_by_status(GovernanceStatus.PROVISIONAL)),
            "exploratory": len(resolver.get_metrics_by_status(GovernanceStatus.EXPLORATORY)),
        },
        "by_class": {
            "normalized_score": len(resolver.get_metrics_by_class(MetricClass.NORMALIZED_SCORE)),
            "raw_ratio": len(resolver.get_metrics_by_class(MetricClass.RAW_RATIO)),
            "target_constant": len(resolver.get_metrics_by_class(MetricClass.TARGET_CONSTANT)),
            "bounded_entropy": len(resolver.get_metrics_by_class(MetricClass.BOUNDED_ENTROPY)),
        },
        "total_legacy_aliases": sum(len(m.legacy_aliases) for m in CANONICAL_METRICS.values())
    }


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("="*70)
    print("CANONICAL ALIAS MAPPING")
    print("="*70)
    
    resolver = AliasResolver()
    
    # Print summary
    summary = get_migration_summary()
    print(f"\nCANONICAL METRICS SUMMARY:")
    print(f"  Total canonical metrics: {summary['total_canonical_metrics']}")
    print(f"  Total legacy aliases: {summary['total_legacy_aliases']}")
    
    print(f"\nBY STATUS:")
    for status, count in summary['by_status'].items():
        print(f"  {status}: {count}")
    
    print(f"\nBY CLASS:")
    for metric_class, count in summary['by_class'].items():
        print(f"  {metric_class}: {count}")
    
    # Test resolution
    print("\n" + "="*70)
    print("ALIAS RESOLUTION TESTS")
    print("="*70)
    
    test_cases = [
        "phi_resonance",
        "geometry.phi_resonance",
        "results.experiment_1.phi_resonance",
        "entanglement_entropy",
        "metrics.entanglement_entropy",
        "wormhole.entropy_s",
        "consciousness_level",
        "tmt_ratios.phi",
        "phi_resonance_target",
        "unknown_metric"
    ]
    
    for legacy_name in test_cases:
        canonical_name, metric = resolver.resolve(legacy_name)
        if canonical_name:
            print(f"\n  {legacy_name}")
            print(f"    → {canonical_name}")
            print(f"    Class: {metric.metric_class.value}")
            print(f"    Status: {metric.governance_status.value}")
            print(f"    Range: {metric.valid_range}")
        else:
            print(f"\n  {legacy_name}")
            print(f"    → UNKNOWN")
    
    # Print all canonical metrics
    print("\n" + "="*70)
    print("ALL CANONICAL METRICS")
    print("="*70)
    
    for name, metric in CANONICAL_METRICS.items():
        status_icon = {
            GovernanceStatus.VALIDATED: "✅",
            GovernanceStatus.PASSED: "✓",
            GovernanceStatus.PROVISIONAL: "📋",
            GovernanceStatus.EXPLORATORY: "🔍",
            GovernanceStatus.INVALID: "❌",
            GovernanceStatus.UNKNOWN: "❓"
        }.get(metric.governance_status, "?")
        
        print(f"\n{status_icon} {name}")
        print(f"   Class: {metric.metric_class.value}")
        print(f"   Status: {metric.governance_status.value}")
        print(f"   Range: {metric.valid_range}")
        print(f"   Aliases: {len(metric.legacy_aliases)}")
        print(f"   Notes: {metric.notes[:80]}...")
    
    print("\n" + "="*70)
    print("GOVERNANCE POLICY:")
    print("  ✅ VALIDATED: Can support claims")
    print("  ✓ PASSED: Can appear in reports")
    print("  📋 PROVISIONAL: Needs validation")
    print("  🔍 EXPLORATORY: Hypothesis-generating only")
    print("  ❌ INVALID: Must be repaired")
    print("  ❓ UNKNOWN: Must be registered")
    print("="*70)