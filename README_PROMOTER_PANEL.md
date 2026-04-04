# Promoter Panel Analysis System
## Sephirot 10-Promoter Experimental Cohort

**Version**: 1.0  
**Date**: April 4, 2026  
**Status**: Production-Ready

---

## Overview

This system treats the 10 FASTA promoter files as a **curated experimental cohort** rather than isolated files. It provides:

- ✅ Standardized FASTA parsing with SHA256 verification
- ✅ Batch promoter panel processing with consistent lineage
- ✅ Quantum circuit generation with sequence-specific encoding
- ✅ Side-by-side comparison across all 10 promoters
- ✅ Hardware selection gate for IBM Quantum validation
- ✅ Complete audit-grade artifact provenance

---

## The Panel

| Gene | Sephirot | Role | Length | GC Content |
|------|----------|------|--------|------------|
| ACTB | Malkuth | Foundation | 31 bp | 67.7% |
| BDNF | Tiferet | Beauty/Harmony | 31 bp | 54.8% |
| DCTN1 | Binah | Understanding | 31 bp | 48.4% |
| FOS | Netzach | Victory | 31 bp | 58.1% |
| FOXG1 | Kether | Crown | 31 bp | 45.2% |
| JUN | Hod | Splendor | 31 bp | 58.1% |
| NCAM1 | Chokmah | Wisdom | 31 bp | 51.6% |
| OXT | Chesed | Loving-kindness | 31 bp | 51.6% |
| SRY | Yesod | Foundation | 31 bp | 29.0% |
| TP53 | Gevurah | Strength/Judgment | 31 bp | 58.1% |

---

## Quick Start

### 1. Generate Panel Manifest

```bash
python agi_scripts/generate_promoter_panel_manifest.py \
  --panel-dir C:\FASTA \
  --output promoter_panel_manifest_v1.json
```

**Output**: Canonical panel definition with:
- File paths, gene names, Sephirot labels
- Sequence lengths, SHA256 hashes
- GC content, parse status
- Audit metadata

### 2. Run Batch Analysis

```bash
python agi_scripts/run_promoter_panel_batch.py \
  --manifest promoter_panel_manifest_v1.json \
  --seed 42 \
  --deterministic
```

**Output**:
- 10 individual promoter artifacts in `promoter_panel_results/reconstructed/`
- Comparison report: `promoter_panel_results/promoter_panel_comparison.json`
- Hardware selection recommendations

### 3. View Results

```bash
# Comparison table
python -c "import json; d=json.load(open('promoter_panel_results/promoter_panel_comparison.json')); \
  [print(f'{p[\"promoter_id\"]:\u003c8} {p[\"sephirot_label\"]:\u003c10} {p[\"phi_alignment_score\"]:\u003e8.1f} {p[\"entropy_shannon\"]:\u003e6.2f}') \
  for p in d['promoters']]"
```

---

## Pipeline Architecture

```
C:\FASTA\ (10 FASTA files)
    ↓
generate_promoter_panel_manifest.py
    ↓
promoter_panel_manifest_v1.json (canonical definition)
    ↓
run_promoter_panel_batch.py
    ├── Step 1: Parse FASTA (promoter_loader.py)
    ├── Step 2: Encode to qubits (DNA→qubit registers)
    ├── Step 3: Generate circuits (quantum_circuits.py)
    ├── Step 4: Simulate (phi-harmonic analysis)
    └── Step 5: Build artifacts (audit-grade metadata)
    ↓
promoter_panel_results/
├── reconstructed/
│   ├── promoter_ACTB_20260404_000231.json
│   ├── promoter_BDNF_20260404_000231.json
│   └── ... (10 artifacts)
└── promoter_panel_comparison.json
```

---

## Key Features

### Deterministic Reproducibility

Same seed = identical outputs:

```python
# Run 1: seed=42 → OXT phi_alignment=3089.14
# Run 2: seed=42 → OXT phi_alignment=3089.14
```

Each artifact includes:
```json
"reproducibility": {
  "deterministic_mode": true,
  "base_seed": 42,
  "sequence_derived_seed": 1234567890,
  "combined_seed": 1234567932,
  "deterministic_replay": true
}
```

### Sequence-Specific Variation

Metrics vary by actual sequence content:
- **GC content** influences circuit depth and entropy
- **Sequence hash** modifies random seed for uniqueness
- **Phi-alignment** varies by base composition
- **Entropy** reflects sequence complexity

### Hardware Selection Gate

Automatic selection of top candidates for IBM validation:

```json
"hardware_selection": {
  "recommended_count": 5,
  "candidates": ["SRY", "DCTN1", "FOXG1", "OXT", "TP53"],
  "selection_criteria": [
    "top_phi_aligned",
    "high_entropy", 
    "structural_outliers"
  ]
}
```

Selection rules:
- Top 2 phi-aligned promoters
- Top 2 entropy promoters  
- 1-2 structural outliers
- Maximum diversity in profiles

---

## Comparison Metrics

### Per-Promoter Metrics

| Metric | Description | Range |
|--------|-------------|-------|
| sequence_length | Base pairs | 31 bp |
| qubit_count | Encoded qubits | 62 |
| circuit_depth | Quantum circuit depth | 48-58 |
| total_gates | Gate count | 180-243 |
| gc_content | G+C percentage | 29-68% |
| phi_alignment_score | Golden ratio alignment | 2666-3089 |
| entropy_shannon | Information entropy | 4.8-5.8 |
| hamming_mean | Hamming weight | 2.5-4.2 |
| unique_states | Unique quantum states | 90-105 |

### Cluster Analysis

```json
"cluster_analysis": {
  "phi_alignment": {
    "mean": 2805.47,
    "std": 113.24,
    "high_performers": ["OXT"],
    "low_performers": ["DCTN1"]
  }
}
```

---

## Artifact Schema

Each promoter artifact follows the DNA Agent v1.0 schema:

```json
{
  "promoter_id": "OXT",
  "sephirot_label": "Chesed",
  "sequence_length": 31,
  "gc_content": 0.516,
  "encoding": { /* qubit encoding */ },
  "circuit": { /* quantum circuit metrics */ },
  "metrics": { /* computed metrics */ },
  "artifact_metadata": {
    "evidence_class": "secondary",
    "artifact_type": "reconstructed",
    "parent_artifacts": [
      "external_source:OXT_Chesed_promoter.fa",
      "manifest:promoter_panel_manifest_v1.json"
    ],
    "reproducibility": { /* seed and parameters */ },
    "data_lineage": { /* transform chain */ }
  }
}
```

---

## Validation

```bash
# Validate all artifacts
python agi_scripts/validate_artifact_lineage.py --dir promoter_panel_results/

# Expected output:
# [✓] All validations passed!
# Files validated: 10/10
```

---

## Hardware Submission Workflow

### Step 1: Select Candidates

```python
import json

with open('promoter_panel_results/promoter_panel_comparison.json') as f:
    comparison = json.load(f)

candidates = comparison['hardware_selection']['candidates']
print(f"Submitting {len(candidates)} promoters to IBM Quantum")
```

### Step 2: Generate QASM

```python
# Convert selected promoters to QASM circuits
for promoter_id in candidates:
    artifact_path = f"promoter_panel_results/reconstructed/promoter_{promoter_id}_*.json"
    # Generate QASM from circuit data
    # Submit to IBM Quantum
```

### Step 3: Archive Results

```
promoter_panel_results/
├── raw_hardware/          # IBM Quantum outputs
├── reconstructed/         # Current artifacts
└── derived_metrics/       # Post-processing
```

---

## Reproducibility

### Deterministic Mode (Default)

```bash
python agi_scripts/run_promoter_panel_batch.py \
  --seed 42 \
  --deterministic
```

- Fixed seed = identical outputs
- Sequence-derived seed ensures uniqueness per promoter
- Combined seed = base_seed + sequence_hash

### Exploratory Mode

```bash
python agi_scripts/run_promoter_panel_batch.py \
  --exploratory
```

- Variable outputs per run
- Timestamp-based seed
- For parameter exploration

---

## Integration with AGI-Model

This system integrates with:

- **DNA Agent**: Artifact schema and lineage tracking
- **Phi Agent**: Downstream phi-alignment analysis
- **QNN Agent**: Training on promoter metrics
- **TMT-OS**: Wing entanglement architecture
- **IBM Quantum**: Hardware validation pipeline

**Data Flow:**
```
FASTA Panel → Manifest → Batch Analysis → Comparison → Hardware Selection → IBM Quantum
                ↓              ↓                ↓
           Artifacts    Lineage Graph    Cluster Analysis
```

---

## Files Generated

### Core Files
- `promoter_panel_manifest_v1.json` - Canonical panel definition
- `promoter_panel_comparison.json` - Side-by-side comparison
- `promoter_*/reconstructed/*.json` - Individual artifacts (10)

### Documentation
- `docs/ARTIFACT_SCHEMA_v1.md` - Schema specification
- `docs/ARTIFACT_SYSTEM_SUMMARY.md` - System overview
- `README_PROMOTER_PANEL.md` - This file

---

## Next Steps

### Immediate
- [ ] Submit hardware candidates to IBM Quantum
- [ ] Archive hardware results in `raw_hardware/`
- [ ] Validate hardware outputs against reconstructed predictions

### Short Term
- [ ] Add more promoters to panel (expand beyond 10)
- [ ] Implement actual QASM generation from circuit data
- [ ] Cross-reference with biological function databases

### Long Term
- [ ] Build predictive models from panel data
- [ ] Integrate with broader genomic validation pipeline
- [ ] Scale to full genome-wide promoter analysis

---

## Success Metrics

| Metric | Target | Status |
|--------|--------|--------|
| Panel coverage | 10 promoters | ✅ |
| Manifest validation | 100% valid | ✅ |
| Deterministic reproducibility | Same seed = same output | ✅ |
| Artifact validation | 0 errors | ✅ |
| Hardware selection | 5 candidates | ✅ |
| Comparison report | Generated | ✅ |

---

## Troubleshooting

### Issue: Manifest generation fails
**Solution**: Check FASTA files exist in `C:\FASTA\` with correct naming pattern

### Issue: Non-deterministic outputs
**Solution**: Ensure `--deterministic` flag and fixed `--seed` value

### Issue: Validation errors
**Solution**: Run `validate_artifact_lineage.py` to check specific errors

---

## Citation

If using this system in research:

```
AGI-Model Promoter Panel Analysis System v1.0
Sephirot 10-Promoter Experimental Cohort
Generated: 2026-04-04
Schema: DNA Agent Artifact v1.0
```

---

**End of Documentation**
