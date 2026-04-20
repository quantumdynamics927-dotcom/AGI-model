# Prompt Evaluation Report

**Generated**: 2026-04-20T23:51:44.019499
**Evaluator Version**: 2.0.0

## Summary
- Total prompts: 7
- Total cases: 1
- Cases passed: 1
- Cases failed: 0
- Schema valid: 1
- Invariants passed: 1

**Overall Status**: ✅ PASS

## Promotion Scorecards

### core_system_prompt (v1.0.0) 🟢
- Risk: low | Status: validated
- Hash: `dc808e710fae29fd`
- Cases: 0/0 passed (0%)
- **Recommendation**: AUTO_PROMOTE

**Gates**:
- [✓] header_check
- [✓] eval_pass_rate

### debug_tensor_shapes (v1.0.0) 🟢
- Risk: low | Status: validated
- Hash: `c9fb27803d938c9f`
- Cases: 0/0 passed (0%)
- **Recommendation**: AUTO_PROMOTE

**Gates**:
- [✓] header_check
- [✓] eval_pass_rate

### benchmark_validity (v1.0.0) 🟡
- Risk: medium | Status: validated
- Hash: `1028f35453377b3a`
- Cases: 1/1 passed (100%)
- **Recommendation**: READY_FOR_REVIEW

**Gates**:
- [✓] header_check
- [✓] eval_pass_rate

### interpret_results_conservatively (v1.0.0) 🟡
- Risk: high | Status: validated
- Hash: `1d8e9c2c94cd0ad8`
- Cases: 0/0 passed (0%)
- **Recommendation**: READY_FOR_REVIEW

**Gates**:
- [✓] header_check
- [✓] eval_pass_rate
- [✓] schema_validation
- [✓] invariant_checks

### ibm_hardware_result_interpretation (v1.0.0) 🟡
- Risk: high | Status: validated
- Hash: `3f4b6d8c71c5de95`
- Cases: 0/0 passed (0%)
- **Recommendation**: READY_FOR_REVIEW

**Gates**:
- [✓] header_check
- [✓] eval_pass_rate
- [✓] schema_validation
- [✓] invariant_checks

### audit_custom_metric (v1.0.0) 🟡
- Risk: high | Status: validated
- Hash: `d0fe2f9f30564aac`
- Cases: 0/0 passed (0%)
- **Recommendation**: READY_FOR_REVIEW

**Gates**:
- [✓] header_check
- [✓] eval_pass_rate
- [✓] schema_validation
- [✓] invariant_checks

### hostile_internal_skeptic (v1.0.0) 🟡
- Risk: medium | Status: validated
- Hash: `5eadc5c2cdad7aa3`
- Cases: 0/0 passed (0%)
- **Recommendation**: READY_FOR_REVIEW

**Gates**:
- [✓] header_check
- [✓] eval_pass_rate

## Detailed Results

### core_system_prompt
- Version: 1.0.0 | Hash: `dc808e710fae29fd`
- Cases: 0/0 passed

### debug_tensor_shapes
- Version: 1.0.0 | Hash: `c9fb27803d938c9f`
- Cases: 0/0 passed

### benchmark_validity
- Version: 1.0.0 | Hash: `1028f35453377b3a`
- Cases: 1/1 passed

| Case | Status | Schema | Invariants |
|------|--------|--------|------------|
| case_01_failed_baseline | ✓ | ✓ | ✓ |

### interpret_results_conservatively
- Version: 1.0.0 | Hash: `1d8e9c2c94cd0ad8`
- Cases: 0/0 passed

### ibm_hardware_result_interpretation
- Version: 1.0.0 | Hash: `3f4b6d8c71c5de95`
- Cases: 0/0 passed

### audit_custom_metric
- Version: 1.0.0 | Hash: `d0fe2f9f30564aac`
- Cases: 0/0 passed

### hostile_internal_skeptic
- Version: 1.0.0 | Hash: `5eadc5c2cdad7aa3`
- Cases: 0/0 passed

---

*Note: This is structural validation. Full LLM-based evaluation requires model integration.*