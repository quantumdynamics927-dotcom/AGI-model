# Response Path Audit Implementation

## Overview

This implementation provides a complete framework for conducting a **controlled ablation study** to test whether quantum/tesseract routing actually affects final responses. The framework follows the methodology outlined in the user's requirements and implements the three-condition experiment.

## Files Created

| File | Purpose |
|------|---------|
| `response_path_audit.py` | Main audit framework with three routing configurations |
| `response_audit_prompts.json` | Diagnostic prompt suite (50 prompts across 5 classes) |
| `response_trace_schema.json` | JSON schema for trace validation |
| `RESPONSE_PATH_AUDIT_PROTOCOL.md` | Protocol documentation |
| `test_response_path_audit.py` | Test suite for validation |
| `run_response_audit.py` | Script to run the audit |
| `response_audit_statistics.py` | Statistical analysis module |

## Three Conditions

### C0: Classical Baseline
```python
# Fixed routing path: 0 → 1 → 5 → 13 → 15
# No tesseract router, no quantum scorer
# Tests baseline performance
```

### C1: Tesseract Classical
```python
# Tesseract router enabled
# Classical edge scorer (latent similarity + vertex affinity)
# Tests topology benefit independent of quantum
```

### C2: Tesseract Quantum
```python
# Tesseract router enabled
# Quantum edge scorer (quantum circuits or classical approximation)
# Tests full quantum-assisted routing
```

## Quick Start

```bash
# Run full audit with default settings (50 prompts × 3 configs × 3 repeats)
python run_response_audit.py

# Run specific configurations
python run_response_audit.py --configs C0 C2

# Run specific prompt classes
python run_response_audit.py --prompt-classes ambiguous tool_use

# Adjust parameters
python run_response_audit.py --num-prompts 20 --num-repeats 5

# Run statistical analysis after audit
python response_audit_statistics.py
```

## Output Structure

```
response_audit_results/
├── route_logs/                    # Individual route session logs
├── response_traces.json           # All traces by configuration
├── response_audit_results.json   # Complete results
├── audit_summary.json             # Summary statistics
├── audit_report.txt               # Human-readable report
├── run_config.json                # Run configuration
└── statistical_report.txt         # Statistical analysis
```

## Key Metrics

### Primary Metrics
- **Task Success**: Whether response achieved goal
- **Judge Score**: Quality score (0-1)
- **Confidence Alignment**: Match between confidence and performance
- **Response Consistency**: Reproducibility across runs
- **Tool Selection Accuracy**: Correct tool choice (for tool_use prompts)

### Secondary Metrics
- **Latency**: Time to complete routing
- **Route Length**: Number of steps in route
- **Invalid Transition Rate**: Rate of invalid transitions
- **Fallback Frequency**: How often fallbacks occur

## Prompt Classes

| Class | Purpose | Count |
|-------|---------|-------|
| `ambiguous` | Prompts needing arbitration | 10 |
| `tool_use` | Multi-step tool-use prompts | 10 |
| `fault_tolerance` | Partial/noisy context prompts | 10 |
| `memory_governance` | Memory and governance prompts | 10 |
| `factual_control` | Straightforward factual prompts | 10 |

## Causal Test

### Strong Result (Quantum-Assisted Response Influence)
- C2 beats C1 and C0 on primary metrics
- Route trace shows scorer changed transition choices
- Changes replicate across repeated runs

### Weak Result (Quantum-Assisted Internal Control)
- Route changes but response quality doesn't improve
- Indicates routing affects internal control but not output

### No Demonstrated Impact
- C2 doesn't outperform C1
- Differences vanish under repeated trials

## Statistical Analysis

The framework includes proper significance testing:

```python
from response_audit_statistics import ResponseAuditStatistics

analyzer = ResponseAuditStatistics('response_audit_results')

# Paired t-test (C2 vs C1)
result = analyzer.paired_t_test('judge_score', 'C2', 'C1')
print(f"t={result.statistic:.2f}, p={result.p_value:.4f}, d={result.effect_size:.2f}")

# ANOVA across all three configs
anova = analyzer.anova_test('judge_score')
print(f"F={anova.statistic:.2f}, p={anova.p_value:.4f}, η²={anova.effect_size:.3f}")

# Analysis by prompt class
class_analysis = analyzer.analyze_by_prompt_class('judge_score')
```

## Integration with Existing Code

The audit framework integrates with existing modules:

```python
from tesseract_router import TesseractRouter
from tesseract_transition_scorer import QuantumEdgeScorer
from tesseract_governance import TesseractGovernance
from tesseract_state import TesseractStateSpace
```

## Extending the Framework

### Adding New Prompts

Edit `response_audit_prompts.json`:

```json
{
  "prompt_id": "custom_001",
  "prompt_text": "Your custom prompt here",
  "prompt_hash": "...",
  "prompt_class": "ambiguous",
  "expected_behavior": "Expected behavior description",
  "difficulty": "medium"
}
```

### Adding New Metrics

Extend `_evaluate_response()` in `response_path_audit.py`:

```python
metrics['new_metric'] = self._compute_new_metric(response, route_result)
```

### Custom Scoring Functions

Create a new scorer class:

```python
class CustomEdgeScorer:
    def score_edges(self, z, current_vertex, candidates):
        # Your scoring logic
        return scores
```

## Validation

Run the test suite:

```bash
python -m pytest test_response_path_audit.py -v
```

## Pass/Fail Criteria

### Claim: Quantum-Assisted Response Influence
**PASS** if:
1. C2 shows statistically credible improvement over C1 (p < 0.05)
2. Effect size > 0.5 (medium effect)
3. Reproducible across repeated runs
4. Trace shows changed routing decisions

### Claim: Quantum-Assisted Internal Control
**PASS** if:
- Route changes but response quality doesn't improve
- Statistical test shows routing differences

### Claim: No Demonstrated Response Impact
**PASS** if:
- C2 doesn't outperform C1 (p > 0.05)
- Effect size < 0.2 (small effect)
- Differences vanish under repeated trials

## References

- [Controlled Ablation Study](https://www.emergentmind.com/topics/controlled-ablation-study)
- [arXiv:2409.09951v1](https://arxiv.org/html/2409.09951v1)
- [arXiv:2511.11275v2](https://arxiv.org/html/2511.11275v2)
- [F5: AI Observability](https://www.f5.com/company/blog/ai-observability-auditing-and-tracing-ai-decisions)
- [PMC: AI Evaluation](https://pmc.ncbi.nlm.nih.gov/articles/PMC9768678/)
- [Nature: AI Testing](https://www.nature.com/articles/s41586-026-10303-2)

---

*Implementation version: 1.0.0*
*Created: 2026-04-19*