# IBM Quantum Teleportation Rerun Validation

This directory contains tools for re-running and validating previously successful IBM Quantum teleportation experiments on real hardware.

## Objective

Recreate the same teleportation circuit/protocol used in prior IBM Quantum jobs, submit fresh runs, retrieve results, compute fidelity, and determine whether the result is reproducible.

## Reference Job IDs

- `d6kvddgfh9oc73emadvg`
- `d6kvdfs3pels739umfg0`
- `d6kvdjgfh9oc73emae50`
- `d6kvdm43pels739umfog`

## Target Experiment

- **Teleport the single-qubit state**: RY(π/3) · RZ(π/7) |0⟩
- **Protocol**: Standard quantum teleportation with ER=EPR-inspired circuit logic
- **Execution**: IBM Quantum real hardware only (no simulation)

## Files

| File | Description |
|------|-------------|
| `teleportation_rerun_validator.py` | Main validation script |
| `check_reference_jobs.py` | Helper script to check reference job metadata |
| `validation_report.md` | Generated validation report |
| `old_jobs_metadata.json` | Metadata from reference jobs |
| `new_jobs_metadata.json` | Metadata from rerun jobs |
| `fidelity_results.csv` | Fidelity results table |

## Usage

### Prerequisites

1. Install Qiskit and IBM Quantum Runtime:
   ```bash
   pip install qiskit qiskit-ibm-runtime
   ```

2. Save your IBM Quantum credentials:
   ```python
   from qiskit_ibm_runtime import QiskitRuntimeService
   QiskitRuntimeService.save_account(token='YOUR_TOKEN', channel='ibm_quantum')
   ```

### Check Reference Jobs

To retrieve metadata for the reference jobs without running new ones:

```bash
python check_reference_jobs.py
```

### Run Full Validation

To execute the complete validation workflow:

```bash
python teleportation_rerun_validator.py --num-reruns 4 --shots 1024
```

Options:
- `--num-reruns`: Number of rerun jobs (default: 4)
- `--shots`: Shots per job (default: 1024)
- `--backend`: Specific backend name (optional)
- `--output-dir`: Output directory (default: teleportation_rerun_validation)
- `--token`: IBM Quantum API token (optional, uses saved credentials if not provided)

### Example Output

```
================================================================================
IBM QUANTUM TELEPORTATION RERUN VALIDATION
================================================================================

📡 Step 1: Connecting to IBM Quantum...
✅ Connected to IBM Quantum Runtime
   Channel: ibm_quantum

📊 Step 2: Retrieving reference job metadata...
📊 Retrieving metadata for job d6kvddgfh9oc73emadvg...
   ✅ Retrieved: Backend=ibm_fez, Status=COMPLETED

📤 Step 3: Submitting 4 rerun jobs...
⚛️  Teleportation Circuit:
   Target state: RY(1.047198) · RZ(0.448799) |0⟩
   Qubits: 3
   Depth: 5
   Gates: {'measure': 3, 'h': 2, 'cx': 2, 'ry': 1}

🔧 Transpiling for ibm_fez...
   Transpiled depth: 12
   Transpiled gates: {'rz': 8, 'sx': 6, 'cx': 2, 'measure': 3}

📤 Submitting job 1/4...
   ✅ Job submitted: d6kvddgfh9oc73emadvg

⏳ Step 4: Monitoring jobs until completion...
   ⏳ Job d6kvddgfh9oc73emadvg: RUNNING
   ✅ Job d6kvddgfh9oc73emadvg: COMPLETED

🔬 Step 5: Analyzing job results...
🔬 Analyzing job d6kvddgfh9oc73emadvg...
   Fidelity: 0.9840
   Quality: EXCELLENT ✅
   Exceeds classical threshold: True

📝 Step 6: Generating validation report...
✅ Validation report saved to: validation_report.md

💾 Step 7: Saving artifacts...
✅ Saved: old_jobs_metadata.json
✅ Saved: new_jobs_metadata.json
✅ Saved: fidelity_results.csv

================================================================================
VALIDATION COMPLETE
================================================================================

📊 Summary:
   New Job IDs: d6kvddgfh9oc73emadvg, ...
   Best Fidelity: 0.9840
   Mean Fidelity: 0.9812
   Runs Above Classical Threshold: 4/4
   Reproducible: ✓ YES
```

## Fidelity Calculation

The teleportation fidelity is calculated as:

$$F = \sqrt{P_{\text{expected}}(0) \times P_{\text{measured}}(0)} + \sqrt{P_{\text{expected}}(1) \times P_{\text{measured}}(1)}$$

Where:
- $P_{\text{expected}}(0) = \cos^2(\theta_y/2)$
- $P_{\text{expected}}(1) = \sin^2(\theta_y/2)$
- $\theta_y = \pi/3$ for the target state

## Quality Thresholds

| Fidelity | Quality |
|----------|---------|
| F > 0.9 | EXCELLENT ✅ |
| F > 0.8 | VERY GOOD ✓ |
| F > 0.667 | GOOD (above classical) ✓ |
| F > 0.5 | MODERATE ⚠️ |
| F ≤ 0.5 | POOR ❌ |

The classical teleportation threshold is **F > 2/3 ≈ 0.667**.

## Validation Criteria

- **CONFIRMED**: All reruns exceed the classical threshold
- **PARTIALLY CONFIRMED**: ≥50% of reruns exceed the classical threshold
- **NOT CONFIRMED**: <50% of reruns exceed the classical threshold

## Technical Notes

1. **Circuit Recovery**: If the original circuit source is available locally, it is reused exactly. Otherwise, the closest executable version is reconstructed.

2. **Backend Selection**: Prefers the same backend if still available; otherwise selects the least busy compatible backend.

3. **Dynamic Circuits**: Uses Qiskit 1.x+ `if_test` syntax for conditional operations.

4. **Result Decoding**: Handles both SamplerV2 BitArray format and legacy counts format.

5. **Conservative Approach**: Prefers reproducibility over aggressive optimization.

## References

- [IBM Quantum Runtime Service](https://quantum.cloud.ibm.com/docs/api/qiskit-ibm-runtime/qiskit-runtime-service)
- [Quantum Teleportation Tutorial](https://quantum.cloud.ibm.com/learning/courses/utility-scale-quantum-computing/teleportation)
- [Run Jobs Guide](https://quantum.cloud.ibm.com/docs/guides/run-jobs-batch)
- [Save Jobs Guide](https://quantum.cloud.ibm.com/docs/en/guides/save-jobs)