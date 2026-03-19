# IBM Decoherence Experiment

This experiment starts the phi-side follow-up branch recommended by the first
cloud research loop.

## Goal

Measure how quickly a phi-phased entangled probe loses integrated structure
under controlled decoherence pulses on IBM Quantum hardware.

## Why This Exists

The saved phi analysis in `research_loop_result.json` recommends a controlled
information-decoherence pulse to observe causal-integration collapse kinetics.
The existing `research-loop` does not design or execute that hardware branch.

## Probe Design

- State family: phi-phased GHZ chain
- Default width: 8 qubits
- Measurement bases:
  - `z_population`: population spreading and dominant-state decay
  - `x_coherence`: parity collapse as a coherence proxy
- Sweep axes:
  - delay in ns
  - number of decoherence pulse repetitions
  - alternating phase-kick amplitude derived from $\phi$

## Collapse Metrics

- `parity_expectation`: tracks X-basis coherence loss
- `distribution_entropy`: tracks classicalization of the output distribution
- `hamming_weight_kurtosis`: tracks whether the distribution remains sharply
  structured or flattens during collapse
- `dominant_bitstring_probability`: tracks decay of the leading integrated mode

## Command

Design only:

```powershell
python run_ibm_decoherence_experiment.py --output ibm_decoherence_experiment.json
```

Design and submit to IBM Quantum:

```powershell
python run_ibm_decoherence_experiment.py --run --backend ibm_fez --shots 4096 --output ibm_decoherence_experiment.json
```

## Interpretation

The primary collapse signature is a monotonic drop in `x_coherence`
parity expectation combined with rising entropy. A transition from peaked
Hamming-weight kurtosis to flatter kurtosis indicates that the probe has moved
from an integrated regime toward a classicalized regime.

## Relation To KL Tuning

The KL-cap change in `train_vae.py` affects training dynamics, not the current
deterministic `vae-smoke` contract. To measure the training impact, run a new
training pass and compare its checkpoint summary against the saved baseline;
rerunning the current `research-loop` alone only reproduces the contract path.
