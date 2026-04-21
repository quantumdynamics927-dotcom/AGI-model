# Response Path Audit Protocol

## Overview

This protocol implements a **controlled ablation study** to test whether the quantum/tesseract routing layer actually affects final responses. The core claim being tested is:

> **"The final response depends on the quantum-assisted routing/control path."**

This is a **causal claim** that requires controlled ablation: keep prompts, model, temperature, seeds, tools, and evaluation harness fixed, then vary only the routing/control component.

## Three Conditions

The audit runs every prompt under **three matched configurations**:

### C0: Classical Baseline
- **No tesseract router**
- **No quantum edge scorer**
- **Fixed classical policy**
- Follows predetermined path: `0 → 1 → 5 → 13 → 15` (Sensory → Feature → Latent → Policy → Execution)

### C1: Tesseract Classical
- **Tesseract router enabled**
- **Quantum scorer replaced with deterministic classical scoring**
- Uses latent vector similarity and vertex affinity for edge scoring
- Tests whether tesseract topology itself provides benefit

### C2: Tesseract Quantum
- **Tesseract router enabled**
- **Actual quantum/quantum-inspired scorer**
- Uses quantum circuits (or classical approximation when qiskit unavailable) for edge scoring
- Tests specifically quantum-scoring value

## What We Log

For every response, we log:

| Field | Description |
|-------|-------------|
| `prompt_id` | Unique identifier for the prompt |
| `prompt_hash` | SHA-256 hash of exact prompt text |
| `config_id` | Configuration (C0, C1, or C2) |
| `seed` | Random seed for reproducibility |
| `model_id` | Model version identifier |
| `generation_settings` | Temperature, top_p, max_tokens (held constant) |
| `initial_state` | Starting vertex and latent vector hash |
| `visited_states` | Sequence of vertices visited |
| `selected_transitions` | Which transitions were chosen |
| `edge_scores` | Scores for all candidate edges at each step |
| `quantum_scores` | Quantum-specific scores (C2 only) |
| `confidence_values` | Confidence at each routing step |
| `tool_calls` | Any tool invocations during routing |
| `fallback_events` | Error recovery or fallback events |
| `final_state` | Terminal vertex and route statistics |
| `response_hash` | Hash of final response text |
| `evaluation_metrics` | Task success, judge score, confidence alignment |
| `artifact_lineage` | IDs of created/modified artifacts |

## Metrics

### Primary Metrics

| Metric | Description | Goal |
|--------|-------------|------|
| **Task Success** | Whether response achieved goal | C2 > C1 > C0 |
| **Judge Score** | Quality score from judge model | C2 > C1 > C0 |
| **Confidence Alignment** | Match between confidence and performance | Higher is better |
| **Response Consistency** | Reproducibility across repeated runs | Higher is better |
| **Tool Selection Accuracy** | Correct tool choice (for tool_use prompts) | C2 > C1 > C0 |

### Secondary Metrics

| Metric | Description |
|--------|-------------|
| **Latency** | Time to complete routing |
| **Route Length** | Number of steps in route |
| **Invalid Transition Rate** | Rate of invalid state transitions |
| **Fallback Frequency** | How often fallbacks occur |

## Prompt Suite

The audit uses a **diagnostic set of prompt classes**:

| Class | Purpose | Count |
|-------|---------|-------|
| **ambiguous** | Prompts needing arbitration | 10 |
| **tool_use** | Multi-step tool-use prompts | 10 |
| **fault_tolerance** | Partial/noisy context prompts | 10 |
| **memory_governance** | Memory and governance prompts | 10 |
| **factual_control** | Straightforward factual prompts | 10 |

**Control prompts are critical**: If the quantum layer affects everything equally, that may indicate noise rather than targeted reasoning benefit.

## Causal Test

### Strong Result
- C2 beats C1 and C0 on predeclared primary metrics
- Route trace shows scorer changed transition choices
- Changes replicate across repeated prompts and seeds

### Weak Result
- Traces differ, but final answers do not improve
- Outputs differ only due to stochastic generation noise

### No Demonstrated Impact
- C2 does not outperform C1
- Differences vanish under repeated trials

## Pass/Fail Rules

### Claim: Quantum-Assisted Response Influence
**PASS** if:
1. C2 shows statistically credible improvement over C1 on at least one primary response metric
2. Effect is reproducible across repeated runs
3. Trace demonstrates changed outputs coincide with changed routing decisions caused by scorer

### Claim: Quantum-Assisted Internal Control
**PASS** if:
- Route changes but response quality does not materially improve
- This indicates routing affects internal control but not final output quality

### Claim: No Demonstrated Response Impact
**PASS** if:
- C2 does not outperform C1
- Differences vanish under repeated trials

## File Structure

```
response_audit_results/
├── route_logs/                    # Individual route session logs
│   └── route_*.json
├── response_traces.json           # All traces by configuration
├── response_audit_results.json   # Complete results
├── audit_summary.json             # Summary statistics
└── audit_report.txt               # Human-readable report
```

## Running the Audit

```bash
# Run full audit with default settings
python response_path_audit.py

# Run specific configurations
python response_path_audit.py --configs C0 C2

# Run specific prompts
python response_path_audit.py --prompt-ids amb_001 amb_002 fact_001

# Adjust parameters
python response_path_audit.py --num-repeats 5 --temperature 0.7
```

## Statistical Analysis

For proper significance testing:

```python
from scipy import stats

# Compare C2 vs C1
c2_scores = [r.evaluation_metrics['judge_score'] for r in results['C2']]
c1_scores = [r.evaluation_metrics['judge_score'] for r in results['C1']]

t_stat, p_value = stats.ttest_ind(c2_scores, c1_scores)
print(f"C2 vs C1: t={t_stat:.4f}, p={p_value:.4f}")
```

## Interpretation Guide

### If C2 > C1 > C0
- **Quantum-assisted routing provides measurable benefit**
- Both topology and quantum scoring contribute
- Strong evidence for causal influence

### If C2 > C1 but C1 ≈ C0
- **Quantum scoring specifically provides benefit**
- Tesseract topology alone doesn't help
- Quantum scoring is the key differentiator

### If C1 > C0 but C2 ≈ C1
- **Tesseract topology provides benefit**
- Quantum scoring doesn't add value beyond classical
- Topology is the key differentiator

### If C2 ≈ C1 ≈ C0
- **No demonstrated response impact**
- Routing layer doesn't affect final outputs
- Differences are stochastic noise

## References

- [Controlled Ablation Study](https://www.emergentmind.com/topics/controlled-ablation-study)
- [arXiv:2409.09951v1](https://arxiv.org/html/2409.09951v1) - Causal claims in AI systems
- [arXiv:2511.11275v2](https://arxiv.org/html/2511.11275v2) - Inference path logging
- [F5: AI Observability](https://www.f5.com/company/blog/ai-observability-auditing-and-tracing-ai-decisions)
- [PMC: AI Evaluation](https://pmc.ncbi.nlm.nih.gov/articles/PMC9768678/)
- [Nature: AI Testing](https://www.nature.com/articles/s41586-026-10303-2)

## Governance Compliance

This audit follows the project's governance style:
- **Typed artifacts**: All traces are typed and validated
- **Validated records**: JSON schema validation for all traces
- **Reconstructable**: Every response can be reconstructed from input through control decisions to output
- **Lineage tracking**: Artifact IDs tracked throughout inference

---

*Protocol version: 1.0.0*
*Created: 2026-04-19*