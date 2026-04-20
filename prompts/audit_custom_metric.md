---
name: audit_custom_metric
version: 1.0.0
owner: Quantum Dynamics
purpose: Evaluate trustworthiness of custom metrics before using for decisions.
inputs:
  - metric name
  - formula or code
  - inputs
expected_output:
  - metric type
  - hidden assumptions
  - failure modes
  - minimal controls
  - safe use category
risk_level: high
last_validated_on: 2026-04-20
---

# Audit Custom Metric

```text
Audit this custom metric before I trust it.

Metric name:
[NAME]

Definition:
[FORMULA OR CODE]

Inputs:
[INPUTS]

Task:
- identify whether it is directly measured or constructed
- identify invariances and failure cases
- test whether it collapses to a proxy for something simpler
- state what control experiments are needed
- decide whether it is safe as a diagnostic only or unsafe for decision-making

Output:
1. Metric type
2. Hidden assumptions
3. Failure modes
4. Minimal controls
5. Safe use category
```

## Usage

Use for phi-based metrics, coherence scores, and any model-specific "consciousness indicators" before treating them as universal signals.
