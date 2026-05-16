# IBM Quantum Teleportation Rerun Validation - Summary

## Quick Reference

**Task**: Re-run and validate previously successful IBM Quantum teleportation experiments on real hardware.

**Reference Job IDs**:
- `d6kvddgfh9oc73emadvg`
- `d6kvdfs3pels739umfg0`
- `d6kvdjgfh9oc73emae50`
- `d6kvdm43pels739umfog`

**Target State**: RY(π/3) · RZ(π/7) |0⟩

**Classical Threshold**: F > 2/3 ≈ 0.667

## Files Created

```
teleportation_rerun_validation/
├── teleportation_rerun_validator.py  # Main validation script
├── check_reference_jobs.py            # Helper to check reference jobs
├── quick_start.py                     # Streamlined interface
├── requirements.txt                   # Python dependencies
├── README.md                          # Detailed documentation
└── VALIDATION_SUMMARY.md              # This file
```

## Usage

### 1. Install Dependencies

```bash
cd teleportation_rerun_validation
pip install -r requirements.txt
```

### 2. Save IBM Quantum Credentials

```python
from qiskit_ibm_runtime import QiskitRuntimeService
QiskitRuntimeService.save_account(token='YOUR_TOKEN', channel='ibm_quantum')
```

### 3. Check Reference Jobs (No Execution)

```bash
python quick_start.py
```

### 4. Run Full Validation

```bash
# Default: 4 jobs, 1024 shots
python quick_start.py --run

# Minimum: 2 jobs
python quick_start.py --run --jobs 2

# Specific backend
python quick_start.py --run --backend ibm_fez
```

## Validation Workflow

1. **Connect to IBM Quantum** - Authenticate with IBM Quantum Runtime
2. **Retrieve Reference Metadata** - Get metadata for the 4 reference jobs
3. **Submit Rerun Jobs** - Submit 2-4 fresh hardware jobs
4. **Monitor Completion** - Wait for all jobs to complete
5. **Analyze Results** - Decode results and compute fidelity
6. **Generate Report** - Create validation_report.md
7. **Save Artifacts** - Save JSON and CSV files

## Fidelity Calculation

For the target state RY(θ_y) · RZ(θ_z) |0⟩:

$$F = \sqrt{P_{\text{expected}}(0) \times P_{\text{measured}}(0)} + \sqrt{P_{\text{expected}}(1) \times P_{\text{measured}}(1)}$$

Where:
- $P_{\text{expected}}(0) = \cos^2(\theta_y/2)$
- $P_{\text{expected}}(1) = \sin^2(\theta_y/2)$
- $\theta_y = \pi/3$

## Quality Thresholds

| Fidelity | Quality | Above Classical |
|----------|---------|-----------------|
| F > 0.9 | EXCELLENT ✅ | Yes |
| F > 0.8 | VERY GOOD ✓ | Yes |
| F > 0.667 | GOOD ✓ | Yes |
| F > 0.5 | MODERATE ⚠️ | No |
| F ≤ 0.5 | POOR ❌ | No |

## Validation Criteria

- **CONFIRMED**: All reruns exceed classical threshold (F > 2/3)
- **PARTIALLY CONFIRMED**: ≥50% of reruns exceed classical threshold
- **NOT CONFIRMED**: <50% of reruns exceed classical threshold

## Expected Output

```
================================================================================
IBM QUANTUM TELEPORTATION RERUN VALIDATION
================================================================================

📊 Summary:
   New Job IDs: <job_id_1>, <job_id_2>, ...
   Best Fidelity: 0.XXXX
   Mean Fidelity: 0.XXXX ± 0.XXXX
   Runs Above Classical Threshold: N/M
   Reproducible: ✓ YES / ✗ NO
```

## Technical Notes

1. **Circuit**: Standard 3-qubit teleportation with dynamic corrections
2. **Backend**: Prefers same backend as reference; otherwise least busy
3. **Shots**: 1024 per job (configurable)
4. **Dynamic Circuits**: Uses Qiskit 1.x+ `if_test` syntax
5. **Result Decoding**: Handles SamplerV2 BitArray format

## Evidence-Based Summary Template

After running validation, use this template:

```text
## Teleportation Rerun Validation Results

**Reference Jobs**: d6kvddgfh9oc73emadvg, d6kvdfs3pels739umfg0, d6kvdjgfh9oc73emae50, d6kvdm43pels739umfog

**New Job IDs**: [List new job IDs]

**Target State**: RY(π/3) · RZ(π/7) |0⟩

**Results**:
- Best Fidelity: [F_best]
- Mean Fidelity: [F_mean] ± [F_std]
- Runs Above Classical Threshold: [N]/[M]

**Conclusion**: [CONFIRMED / PARTIALLY CONFIRMED / NOT CONFIRMED]

**Evidence**: [Number] out of [total] reruns exceeded the classical teleportation threshold of 2/3, [supporting statement].
```

## References

- [IBM Quantum Runtime Service](https://quantum.cloud.ibm.com/docs/api/qiskit-ibm-runtime/qiskit-runtime-service)
- [Quantum Teleportation Tutorial](https://quantum.cloud.ibm.com/learning/courses/utility-scale-quantum-computing/teleportation)
- [Run Jobs Guide](https://quantum.cloud.ibm.com/docs/guides/run-jobs-batch)
- [Save Jobs Guide](https://quantum.cloud.ibm.com/docs/en/guides/save-jobs)

## Contact

For issues or questions, refer to the main project documentation in the parent directory.