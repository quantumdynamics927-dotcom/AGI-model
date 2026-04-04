# DNA Agent Artifact Schema v1.0
## Audit-Grade Reconstructed Artifact Specification

**Version**: 1.0  
**Status**: Production-Ready for Internal Research Use  
**Date**: April 3, 2026  
**Scope**: Reconstructed DNA analysis artifacts from multi-source quantum data

---

## Schema Overview

This schema defines the complete metadata structure for audit-grade reconstructed artifacts produced by the DNA Agent pipeline. It ensures:

- ✅ Machine-verifiable lineage
- ✅ Deterministic reproducibility  
- ✅ Evidence class alignment
- ✅ Cross-agent audit compatibility

---

## Required Top-Level Fields

### 1. `artifact_metadata` (Object, REQUIRED)

The core classification and provenance container.

#### 1.1 Evidence Classification

| Field | Type | Values | Description |
|-------|------|--------|-------------|
| `evidence_class` | string | `primary`, `secondary`, `interpretive` | Required top-level classification |
| `evidence_class_description` | string | - | Human-readable explanation |

**Evidence Class Definitions:**
- `primary`: Raw hardware, immutable vendor-linked payloads, counts, backend metadata, job receipts
- `secondary`: Machine-produced analysis artifacts, computed metrics, reconstructed data
- `interpretive`: Human-readable narrative, prose reports, executive summaries, claim-heavy documents

#### 1.2 Artifact Taxonomy

| Field | Type | Values | Description |
|-------|------|--------|-------------|
| `artifact_type` | string | `raw_hardware`, `derived_metrics`, `reconstructed`, `narrative` | Artifact category |
| `artifact_type_description` | string | - | Human-readable explanation |

**Artifact Type → Evidence Class Mapping:**
- `raw_hardware` → `primary`
- `derived_metrics` → `secondary`
- `reconstructed` → `secondary`
- `narrative` → `interpretive`

#### 1.3 Machine-Verifiable Lineage

| Field | Type | Description |
|-------|------|-------------|
| `artifact_id` | string | Unique identifier (e.g., `dna_agent_reconstructed_20260403_230223`) |
| `generation_timestamp` | string | ISO 8601 timestamp |
| `generation_mode` | string | `reconstructed_from_archives` or `direct_hardware` |
| `parent_artifacts` | array | List of parent artifact IDs (REQUIRED for reconstructed) |
| `lineage_depth` | integer | Number of parent generations |

**Parent Artifact Format:**
- Internal artifacts: `<artifact_id>`
- External sources: `external_source:<source_name>`
- Legacy references: `legacy:<description>`

#### 1.4 Data Lineage

```json
"data_lineage": {
  "job_id": "string",
  "sources": ["path/to/source1", "path/to/source2"],
  "source_hashes": {
    "path/to/source1": "sha256_hash",
    "path/to/source2": "sha256_hash"
  },
  "source_manifests": {
    "path/to/dir": {
      "path": "path/to/dir",
      "file_count": 10,
      "files": [
        {"relative_path": "file1.json", "hash": "abc123..."}
      ]
    }
  },
  "derived_from_prior_runs": boolean,
  "transform_chain": [
    "load_multi_source_data",
    "simulate_phi_harmonic_dna",
    "analyze_dna_34bp_results",
    "generate_report"
  ]
}
```

#### 1.5 Provenance (Raw Hardware Only)

```json
"provenance": {
  "backend_name": "ibm_fez",
  "vendor_job_id": "d5a95n7p3tbc73astm10",
  "original_timestamp": "2026-04-03T23:02:23",
  "source_file_hash": "sha256_of_raw_payload"
}
```

*Note: `provenance` is null for non-raw artifacts*

#### 1.6 Audit and Validation

| Field | Type | Values | Description |
|-------|------|--------|-------------|
| `audit_note` | string | - | Human-readable audit context |
| `validation_status` | string | `unvalidated`, `validated`, `failed`, `legacy_migrated`, `partial` | Current validation state |
| `validator_version` | string | - | Version of validator that checked this artifact |

#### 1.7 Reproducibility (Reconstructed Artifacts Only)

```json
"reproducibility": {
  "deterministic_mode": true,
  "rng_library": "numpy",
  "rng_version": "2.4.2",
  "timestamp": "2026-04-03T23:02:23.587017",
  "reconstruction_seed": 42,
  "deterministic_replay": true,
  "simulation_parameters": {
    "total_shots": 8192,
    "phi": 1.618033988749895,
    "phi_inv": 0.6180339887498948,
    "consciousness_position": 20,
    "peak_factor": 1.5,
    "fib_positions": [1, 2, 3, 5, 8, 13, 21, 33],
    "fib_boost": 1.2,
    "beta_a": 1.5,
    "beta_b": 1.5
  }
}
```

*Note: `reproducibility` is null for raw hardware artifacts*

---

## Directory Structure

```
dna_34bp_results/
├── raw_hardware/              # Primary evidence
│   └── dna_agent_raw_hardware_<timestamp>.json
├── derived_metrics/           # Secondary evidence (deterministic)
│   └── dna_agent_derived_metrics_<timestamp>.json
├── reconstructed/             # Secondary evidence (reconstructed)
│   └── dna_agent_reconstructed_<timestamp>.json
├── narrative_reports/         # Interpretive evidence
│   └── dna_agent_narrative_report_<timestamp>.json
└── legacy_unclassified/       # Migrated legacy files
    └── <original_name>.json.backup
```

---

## Validation Rules

### Required for All Artifacts
1. `evidence_class` must be present and valid
2. `artifact_type` must be present and valid
3. `artifact_type` → `evidence_class` mapping must be correct
4. `artifact_id` must be present and unique

### Required for Reconstructed Artifacts
1. `parent_artifacts` must be non-empty array
2. `reproducibility` must be present
3. `reproducibility.deterministic_mode` must be boolean
4. `reproducibility.reconstruction_seed` must be present if deterministic
5. `data_lineage.sources` should list source directories
6. `data_lineage.transform_chain` should document transformations

### Required for Raw Hardware
1. `provenance` must be non-null object
2. `provenance.vendor_job_id` must be present
3. `provenance.backend_name` should be present

### Prohibited
1. Reconstructed artifacts cannot claim `evidence_class: "primary"`
2. Raw hardware must have `provenance` object
3. `parent_artifacts` cannot be empty for reconstructed/derived

---

## Example Artifact

```json
{
  "job_id": "d5a95n7p3tbc73astm10",
  "total_shots": 8192,
  "unique_states": 93,
  "hamming_weight": {
    "mean": 3.36,
    "std": 1.42,
    "expected": 51.0,
    "deviation": -47.64
  },
  "consciousness_peak": {
    "position": 20,
    "watson": 419.27,
    "crick": 385.04,
    "bridge": 189.06,
    "phi_ratio": 0.5882
  },
  "wormhole_activation": 240.94,
  "phi_alignment": {
    "total_score": 2961.04,
    "peak_position": 21
  },
  "entropy": {
    "shannon": 5.15,
    "max": 6.54,
    "normalized": 0.7876
  },
  "multi_source_data": {
    "sources_loaded": [
      "E:\\tmt-os\\dna_quantum_analysis",
      "E:\\tmt-os\\dna_quantum_circuits",
      "E:\\tmt-os\\dna_rubiks_cube_results",
      "E:\\tmt-os\\autonomous_synthesis_results\\scientific_synthesis_discoveries.json"
    ],
    "dna_circuits": [...],
    "dna_rubiks_results": [...],
    "scientific_synthesis": [...]
  },
  "reconstruction_params": {
    "deterministic_mode": true,
    "rng_library": "numpy",
    "rng_version": "2.4.2",
    "timestamp": "2026-04-03T23:02:23.587017",
    "reconstruction_seed": 42,
    "deterministic_replay": true,
    "simulation_parameters": {...}
  },
  "artifact_metadata": {
    "evidence_class": "secondary",
    "evidence_class_description": "Machine-produced analysis artifacts, computed metrics, reconstructed data",
    "artifact_type": "reconstructed",
    "artifact_type_description": "Simulated/reconstructed from archived multi-source inputs - machine-produced analysis",
    "artifact_id": "dna_agent_reconstructed_20260403_230223",
    "generation_timestamp": "20260403_230223",
    "generation_mode": "reconstructed_from_archives",
    "parent_artifacts": [
      "external_source:dna_quantum_analysis",
      "external_source:dna_quantum_circuits",
      "external_source:dna_rubiks_cube_results",
      "external_source:scientific_synthesis_discoveries.json"
    ],
    "lineage_depth": 4,
    "data_lineage": {
      "job_id": "d5a95n7p3tbc73astm10",
      "sources": [...],
      "source_hashes": {...},
      "source_manifests": {...},
      "derived_from_prior_runs": true,
      "transform_chain": [
        "load_multi_source_data",
        "simulate_phi_harmonic_dna",
        "analyze_dna_34bp_results",
        "generate_report"
      ]
    },
    "provenance": null,
    "audit_note": "Machine-produced analysis artifact. See evidence_class for classification.",
    "validation_status": "unvalidated",
    "validator_version": null,
    "reproducibility": {...}
  }
}
```

---

## Migration from Legacy

Legacy unclassified artifacts are migrated with:
- `validation_status`: `legacy_migrated`
- `migration_metadata.completeness`: `partial`
- Retroactive `artifact_metadata` appended
- Original file moved to `legacy_unclassified/` as `.backup`

---

## Version History

- **v1.0** (2026-04-03): Initial production-ready schema
  - Complete evidence class hierarchy
  - Machine-verifiable lineage
  - Deterministic reproducibility
  - Validator compliance

---

## Future Work (Out of Scope for v1)

- Metric semantics cleanup (percentage values >100%, score vs probability definitions)
- Schema-level units and bounds
- Publication-grade metric vocabulary
- Cross-agent lineage verification
- Distributed provenance graphs

---

## Validator

Use `agi_scripts/validate_artifact_lineage.py` to check compliance:

```bash
# Validate single artifact
python agi_scripts/validate_artifact_lineage.py path/to/artifact.json

# Validate all artifacts
python agi_scripts/validate_artifact_lineage.py --all
```

Exit codes:
- 0: All validations passed
- 1: Validation failures detected
- 2: Invalid arguments

---

## Compliance Checklist

- [ ] `evidence_class` is present and valid
- [ ] `artifact_type` is present and valid
- [ ] Evidence class matches artifact type
- [ ] `artifact_id` is unique
- [ ] `parent_artifacts` populated (for reconstructed)
- [ ] `reproducibility` present (for reconstructed)
- [ ] `provenance` present (for raw hardware)
- [ ] File located in correct subdirectory
- [ ] Validator passes with 0 errors

---

**End of Schema v1.0**
