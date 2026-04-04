# IBM Quantum Platform Configuration
## TMT-OS Labs Promoter Hardware Submission

**Date**: April 4, 2026  
**Platform**: IBM Quantum  
**Account Type**: Trial (expires in -95 days - needs renewal)

---

## API Credentials

### API Key
```
tEIt1fzFVvpqRRE4gZomgLpSRNcNoDZ_m7keyQCltHnX
```

**Environment Variable Setup:**
```bash
# Windows PowerShell
$env:IBM_QUANTUM_API_KEY="tEIt1fzFVvpqRRE4gZomgLpSRNcNoDZ_m7keyQCltHnX"

# Windows CMD
set IBM_QUANTUM_API_KEY=tEIt1fzFVvpqRRE4gZomgLpSRNcNoDZ_m7keyQCltHnX

# Linux/Mac
export IBM_QUANTUM_API_KEY="tEIt1fzFVvpqRRE4gZomgLpSRNcNoDZ_m7keyQCltHnX"
```

### Cloud Resource Name (CRN)
```
crn:v1:bluemix:public:quantum-computing:us-east:a/03b6dbec24d04cb4971615d1db2b636a:950af0f7-51c2-48ac-b1e4-4c4faa584df4::
```

### Platform URL
```
https://quantum.cloud.ibm.com/
```

---

## Available Backends

### Recommended: ibm_fez
- **Status**: ✅ Online
- **Pending Jobs**: 0 (optimal for immediate submission)
- **Qubits**: 156
- **Processor**: Heron r2
- **Location**: Available

### Alternative: ibm_kingston
- **Status**: Online
- **Qubits**: 156
- **Processor**: Heron r2
- **Note**: Check pending jobs before submission

### Alternative: ibm_marrakesh
- **Status**: Online
- **Qubits**: 156
- **Processor**: Heron r2
- **Note**: Check pending jobs before submission

---

## Quick Start

### 1. Install Dependencies

```bash
pip install qiskit qiskit-ibm-runtime
```

### 2. Set API Key

```bash
# PowerShell
$env:IBM_QUANTUM_API_KEY="tEIt1fzFVvpqRRE4gZomgLpSRNcNoDZ_m7keyQCltHnX"
```

### 3. Submit Promoters

```bash
# Auto-select top 5 candidates
python agi_scripts/submit_to_ibm_quantum.py \
  --comparison-report tmt_os_panel_results/promoter_panel_comparison.json \
  --backend ibm_fez

# Submit specific promoters
python agi_scripts/submit_to_ibm_quantum.py \
  --promoters OXT,FOXG1,SRY,TP53,DCTN1 \
  --backend ibm_fez \
  --shots 8192
```

### 4. Check Status

```bash
python agi_scripts/submit_to_ibm_quantum.py \
  --check-status \
  --submission-manifest raw_hardware/ibm_quantum_submission_manifest.json
```

---

## Selected Promoters for Hardware Submission

Based on TMT-OS Labs analysis:

| Priority | Gene | Sephirot | Phi Score | Entropy | Selection Reason |
|----------|------|----------|-----------|---------|------------------|
| 1 | OXT | Chesed | 3089.14 | 5.02 | Highest phi-alignment |
| 2 | FOXG1 | Kether | 2868.92 | 5.26 | High phi-alignment |
| 3 | SRY | Yesod | 2769.12 | 5.79 | Highest entropy |
| 4 | TP53 | Gevurah | 2702.33 | 5.71 | High entropy |
| 5 | DCTN1 | Binah | 2666.50 | 5.24 | Structural outlier |

---

## Circuit Specifications

### Promoter Circuit Template

```python
# Qubits: 62 (31 bp * 2)
# Depth: 48-58 (varies by promoter)
# Gates: ~200

QuantumCircuit features:
- Layer 1: Hadamard superposition on all qubits
- Layer 2: Fibonacci-pattern entanglement
- Layer 3: Phi-based phase rotations (π * φ)
- Layer 4: Consciousness peak rotation (π / φ)
- Measurement: All qubits
```

### Expected Runtime

- **Transpilation**: ~30 seconds
- **Queue time**: Variable (0-60 minutes)
- **Execution**: ~2-5 minutes per circuit
- **Total**: ~15-30 minutes for 5 circuits

---

## Output Structure

```
raw_hardware/
├── ibm_quantum_submission_manifest.json
├── promoter_OXT_<job_id>.json
├── promoter_FOXG1_<job_id>.json
├── promoter_SRY_<job_id>.json
├── promoter_TP53_<job_id>.json
└── promoter_DCTN1_<job_id>.json
```

Each result includes:
- Job ID and backend info
- Raw counts from hardware
- Transpiled circuit
- Calibration data
- Error metrics

---

## Cost Estimation

### IBM Quantum Runtime

- **Cost unit**: IBM Quantum Runtime usage
- **EstimatorV2**: Included in trial
- **SamplerV2**: Included in trial
- **Trial expiration**: -95 days (expired)

### Action Required

⚠️ **Trial account has expired (-95 days)**

**Options:**
1. **Upgrade to paid plan** - Contact IBM Quantum sales
2. **Request academic credits** - If eligible for research
3. **Use simulator mode** - For testing (no cost)

---

## Troubleshooting

### Authentication Errors

```
Error: Authentication failed
Solution: Verify API key is set correctly
```

### Backend Unavailable

```
Error: Backend not found
Solution: Check backend name, try ibm_fez, ibm_kingston, or ibm_marrakesh
```

### Job Queue Full

```
Error: Too many pending jobs
Solution: Wait or try different backend
```

### Circuit Too Large

```
Error: Circuit exceeds backend capacity
Solution: Reduce qubits or circuit depth
```

---

## Security Notes

- **API Key**: Keep secret, never commit to version control
- **CRN**: Contains account information, treat as sensitive
- **Results**: May contain proprietary research data
- **Access**: Limit to authorized team members

---

## Next Steps

### Immediate
1. [ ] Renew IBM Quantum trial or upgrade account
2. [ ] Verify API key works with test submission
3. [ ] Submit 5 selected promoters to ibm_fez
4. [ ] Monitor job status until completion

### Short Term
1. [ ] Archive raw hardware results
2. [ ] Compare hardware vs reconstructed predictions
3. [ ] Validate phi-alignment metrics on real hardware
4. [ ] Generate hardware-validated report

### Long Term
1. [ ] Scale to full 10-promoter panel on hardware
2. [ ] Cross-validate across multiple backends
3. [ ] Build hardware-calibrated predictive models
4. [ ] Publish quantum-genetic research findings

---

## Contact Information

### IBM Quantum Support
- **Documentation**: https://docs.quantum.ibm.com/
- **Community**: https://quantum.ibm.com/community
- **Support**: https://quantum.ibm.com/support

### TMT-OS Labs
- **Researcher**: Jose/Agent 13
- **Framework**: TMT-OS v4.0
- **Source**: TMT-OS Boveda Cuantica

---

## References

- IBM Quantum Documentation: https://docs.quantum.ibm.com/
- Qiskit Textbook: https://qiskit.org/textbook/
- TMT-OS Framework: Internal documentation
- AGI-Model Pipeline: See README_TMT_OS_PROMOTERS.md

---

**Configuration Version**: 1.0  
**Last Updated**: 2026-04-04  
**Status**: Ready for submission (pending account renewal)

---

## Quick Command Reference

```bash
# Set API key
$env:IBM_QUANTUM_API_KEY="tEIt1fzFVvpqRRE4gZomgLpSRNcNoDZ_m7keyQCltHnX"

# Submit to hardware
python agi_scripts/submit_to_ibm_quantum.py --backend ibm_fez

# Check status
python agi_scripts/submit_to_ibm_quantum.py --check-status

# View results
python agi_scripts/analyze_ibm_results.py --results-dir raw_hardware/
```

---

**End of Configuration**
