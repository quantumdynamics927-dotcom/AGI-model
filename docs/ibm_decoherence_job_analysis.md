# IBM Decoherence Job Analysis

Use the analyzer below to decode the IBM Runtime job pairs for the 8-qubit
phi-phased GHZ decoherence sweep.

## Command

Default external jobs directory:

```powershell
python analyze_ibm_decoherence_jobs.py
```

Explicit directory and output path:

```powershell
python analyze_ibm_decoherence_jobs.py E:\FILES-TO-USE --output artifacts/ibm_decoherence_job_analysis.json
```

## What It Extracts

- transpiled gate counts from the submitted circuit
- variant classification: `control`, `mild`, `moderate`, or `unknown`
- GHZ population mass: `P(00000000) + P(11111111)`
- parity expectation from measured bitstrings
- distribution entropy
- dominant bitstring and top outcomes
- aggregate summaries by variant and by backend

## Current Interpretation

These runs are Z-basis measurements of circuits with phase-only perturbations.
That makes them useful as population controls, but weak as direct coherence
diagnostics. To observe decoherence from the phase kicks more clearly, pair the
same sweep with X-basis readout.
