# Prompt Changelog

All notable changes to the QAGI prompt registry.

Format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [1.0.0] - 2026-04-20

### Added
- Initial prompt registry with 7 prompts
- `core_system_prompt` - Persistent instruction block for all QAGI interactions
- `debug_tensor_shapes` - Shape mismatch diagnosis for VAE/quantum interfaces
- `benchmark_validity` - Benchmark validation with mode failure detection
- `interpret_results_conservatively` - Conservative metric classification
- `ibm_hardware_result_interpretation` - Hardware-provenance-first analysis
- `audit_custom_metric` - Custom metric trustworthiness evaluation
- `hostile_internal_skeptic` - Adversarial claim review

### Added (Infrastructure)
- YAML frontmatter with version, risk_level, status, last_validated_on
- `prompts_manifest.yaml` - Machine-readable registry
- `README.md` - Quick reference and usage guide
- `run_prompt_evals.py` - Evaluation runner with pass/fail reporting
- `eval_cases/` - Regression test fixtures (5 initial cases)

### Risk Levels
- **Low**: `core_system_prompt`, `debug_tensor_shapes`
- **Medium**: `benchmark_validity`, `hostile_internal_skeptic`
- **High**: `interpret_results_conservatively`, `ibm_hardware_result_interpretation`, `audit_custom_metric`

### Eval Cases
- `debug_tensor/case_01_vae_mismatch.json` - VAE encoder/decoder shape mismatch
- `benchmark_validity/case_01_failed_baseline.json` - Invalid benchmark with failed baseline
- `ibm_hardware/case_01_mitigation_artifact.json` - Mitigation-dependent metric
- `custom_metric/case_01_phi_collapses_to_variance.json` - Phi metric proxy collapse
- `hostile_skeptic/case_01_consciousness_claim.json` - Consciousness overclaim review

## Versioning Rules

1. **Immutable once used**: Never edit a prompt version after use in important runs
2. **Bump version on change**: Create new file or update version field
3. **Validate with eval cases**: Run `run_prompt_evals.py` before committing
4. **Update `last_validated_on`**: Date must reflect actual testing
5. **Document in changelog**: All changes must be recorded here

## Status Definitions

- **draft**: Under development, not yet validated
- **validated**: Passed eval cases, safe for use
- **deprecated**: Superseded by newer version, preserved for reproducibility
