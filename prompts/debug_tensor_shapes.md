---
name: debug_tensor_shapes
version: 1.0.0
owner: Quantum Dynamics
purpose: Diagnose shape mismatches in PyTorch/NumPy/Qiskit interfaces.
inputs:
  - error traceback
  - relevant function code
expected_output:
  - shape diagnosis
  - root cause
  - patch
  - assertions to add
  - retest checklist
risk_level: low
last_validated_on: 2026-04-20
---

# Debug Tensor Shapes

```text
Analyze this PyTorch / NumPy / Qiskit interface failure.

Need:
- exact likely tensor shapes before failure
- where rank mismatch was introduced
- whether batching or flattening is wrong
- minimal code patch
- assertion checks I should add

Input:
[PASTE TRACEBACK + RELEVANT FUNCTIONS]

Output:
1. Shape diagnosis
2. Root cause
3. Patch
4. Assertions to add
5. Retest checklist
```

## Usage

Use when encountering shape mismatches in `vae_model.py`, training loops, or quantum-classical interfaces.
