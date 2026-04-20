# QAGI Prompt Operating System

Versioned, schema-bound, invariant-checked prompt templates for hybrid quantum-classical AGI development.

## Quick Reference

| Prompt | Use When | Risk | Status | Schema |
|--------|----------|------|--------|--------|
| `core_system_prompt` | Starting any QAGI interaction | Low | validated | - |
| `debug_tensor_shapes` | Shape mismatches in VAE/quantum interfaces | Low | validated | - |
| `benchmark_validity` | Validating comparative evaluations | Medium | validated | ✓ |
| `interpret_results_conservatively` | Before claiming metric significance | High | validated | ✓ |
| `ibm_hardware_result_interpretation` | Analyzing IBM Quantum job outputs | High | validated | ✓ |
| `audit_custom_metric` | Evaluating phi/coherence/custom metrics | High | validated | ✓ |
| `hostile_internal_skeptic` | Before committing consciousness claims | Medium | validated | ✓ |

## Architecture

```
prompts/
├── README.md                          # This file
├── CHANGELOG.md                       # Version history
├── prompts_manifest.yaml              # Machine-readable registry with hashes
├── registry/
│   ├── aliases.yaml                   # Environment aliases (dev/staging/prod)
│   └── policies.yaml                  # Risk-based promotion gates
├── schemas/                           # JSON schemas for high-risk prompts
│   ├── benchmark_validity_output.schema.json
│   ├── ibm_hardware_output.schema.json
│   ├── metric_audit_output.schema.json
│   └── conservative_interpretation_output.schema.json
├── rubrics/                           # LLM-as-judge criteria
│   ├── benchmark_validity_rubric.yaml
│   ├── hardware_interpretation_rubric.yaml
│   ├── metric_audit_rubric.yaml
│   └── skeptic_rubric.yaml
├── eval_cases/                        # Regression test fixtures with invariants
│   ├── benchmark_validity/
│   ├── ibm_hardware/
│   ├── custom_metric/
│   └── hostile_skeptic/
├── reports/                           # Generated evaluation reports
│   ├── latest_eval_report.json
│   └── history/
├── tools/                             # Automation scripts
│   ├── run_prompt_evals.py            # Main evaluation runner
│   ├── check_prompt_headers.py        # Header validation
│   ├── diff_prompt_behavior.py        # Version behavior diffing
│   └── promote_prompt_version.py      # Environment promotion
└── [prompt files...]                  # Versioned prompt templates
```

## Usage

### Running Evaluations

```bash
# Run all prompt evals with full validation
cd prompts/tools
python run_prompt_evals.py --verbose

# Run specific prompt with scorecard generation
python run_prompt_evals.py --prompt audit_custom_metric --verbose

# Generate JSON results and markdown report
python run_prompt_evals.py --output results.json --report report.md

# Check prompt headers
python check_prompt_headers.py --verbose
```

### Environment Aliases

```bash
# Use production version
alias benchmark_validity="cat prompts/benchmark_validity.md | llm -c"

# Use staging version (when available)
# Versions are mapped in registry/aliases.yaml
```

### Promotion Workflow

```bash
# Check if promotion is allowed
python promote_prompt_version.py benchmark_validity --to staging

# Promote with reason (required for production)
python promote_prompt_version.py audit_custom_metric --to production \
  --version v1.1.0 --reason "Added invariant checks for phi metrics"

# Force promotion past failed gates (requires signoff)
python promote_prompt_version.py ibm_hardware_result_interpretation \
  --to production --force --reason "Emergency fix for calibration handling"
```

### Behavior Diffing

```bash
# Compare behavior between versions
python diff_prompt_behavior.py benchmark_validity \
  --from v1.0.0 --to v1.1.0 --output diff_report.md
```

## Risk Levels

- **Low** (`core_system_prompt`, `debug_tensor_shapes`):
  - Auto-promote after header check + 80% eval pass
  - Safe for routine debugging

- **Medium** (`benchmark_validity`, `hostile_internal_skeptic`):
  - Require 100% eval pass + behavior diff + human review
  - May affect interpretation

- **High** (`interpret_results_conservatively`, `ibm_hardware_result_interpretation`, `audit_custom_metric`):
  - Require 100% eval pass + schema validation + invariant checks + human review
  - Block auto-promotion
  - Critical path for scientific claims

## Versioning Rules

1. **Immutable once used**: Never edit a prompt version after use in important runs
2. **Bump version on change**: Create new file or update version field
3. **Run eval cases**: `python run_prompt_evals.py --verbose`
4. **Validate headers**: `python check_prompt_headers.py`
5. **Check behavior diff**: `python diff_prompt_behavior.py <prompt> --from vOLD --to vNEW`
6. **Update CHANGELOG.md**: Document all changes
7. **Update `last_validated_on`**: Date must reflect actual testing

## Status Definitions

- **draft**: Under development, not yet validated
- **validated**: Passed eval cases, safe for use
- **deprecated**: Superseded by newer version, preserved for reproducibility

## Invariant-Based Evaluation

Eval cases include `expected_invariants` that must hold regardless of output phrasing:

```json
{
  "expected_invariants": {
    "must_flag_invalid": true,
    "must_not_claim_advantage": true,
    "must_classify_raw_counts_as_direct": true
  }
}
```

This is more stable than golden-text matching for reasoning prompts.

## Schema Validation

High-risk prompts have JSON schemas defining required output fields:

```json
{
  "validity": "INVALID",
  "reasons": ["..."],
  "missing_fields": ["..."],
  "required_fixes": ["..."],
  "acceptance_criteria": ["..."]
}
```

The runner validates outputs against these schemas automatically.

## Scorecards

The evaluation runner generates promotion scorecards:

```json
{
  "prompt": "audit_custom_metric",
  "version": "v1.0.0",
  "hash": "a1b2c3d4...",
  "recommendation": "READY_FOR_REVIEW",
  "gates": {
    "header_check": {"passed": true},
    "eval_pass_rate": {"passed": true, "actual": 1.0},
    "schema_validation": {"passed": true},
    "human_review": {"passed": false}
  }
}
```

## Content Addressing

Each prompt has a SHA256 content hash in the manifest:

```yaml
- name: benchmark_validity
  version: "1.0.0"
  sha256: "a1b2c3d4e5f6..."
```

This makes prompt references unambiguous in logs and reproducibility records.

## Integration with AGI-Model

Wire your tools to log:
- prompt name
- semantic version
- content hash
- model used
- eval status
- timestamp

Example:
```python
from prompts.tools.run_prompt_evals import PromptEvaluator

evaluator = PromptEvaluator()
result = evaluator.run_evaluation("benchmark_validity")
# Log result with full provenance
```
