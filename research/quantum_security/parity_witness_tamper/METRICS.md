# Parity Witness Metrics

## Primary Metrics

### 1. Parity Distribution KL Divergence (D_parity)

KL divergence between intercepted and baseline parity distributions.

```
D_parity = D_KL(P_parity_intercept || P_parity_baseline)
```

- **Range**: [0, ∞)
- **Interpretation**: Higher values indicate greater parity disturbance
- **Target**: D_parity > 0.05 for detection
- **Detection threshold**: D_parity > 0.1 for high confidence

### 2. Correlation Drift (Δ_corr)

Change in mutual information between data qubits after interception.

```
Δ_corr = I(D0:D1)_baseline - I(D0:D1)_intercepted
```

- **Range**: (-∞, ∞)
- **Interpretation**: Positive values indicate correlation loss
- **Target**: Δ_corr > 0.1 bits for detection

### 3. Witness Score (W)

Composite metric combining parity deviation and correlation drift.

```
W = w1 * D_parity + w2 * |Δ_corr| + w3 * (1 - Fidelity)
```

Default weights: w1=0.4, w2=0.3, w3=0.3

- **Range**: [0, ∞)
- **Detection threshold**: W > 0.1
- **High confidence threshold**: W > 0.2

### 4. Parity Oscillation Amplitude (A_osc)

For coherence-sensitive circuits, the amplitude of parity oscillation as function of phase.

```
A_osc = max_θ P(parity=1|θ) - min_θ P(parity=1|θ)
```

- **Range**: [0, 1]
- **Interpretation**: Higher amplitude indicates better coherence
- **Detection**: Amplitude reduction under interception

### 5. Parity Oscillation Frequency (f_osc)

Frequency of parity oscillation, related to coherence time.

```
f_osc = d(P(parity=1))/dθ
```

- **Detection**: Frequency shift or damping under interception

### 6. Joint Marginal KL Divergence (D_joint)

KL divergence on two-bit joint marginals (D0, D1).

```
D_joint = D_KL(P(D0,D1)_intercept || P(D0,D1)_baseline)
```

- **Range**: [0, ∞)
- **Target**: D_joint > 0.05 for detection

### 7. Chi-Square Statistic (χ²)

Statistical test comparing parity distributions.

```
χ² = Σ (O_i - E_i)² / E_i
```

- **Null hypothesis**: No interception occurred
- **Significance level**: α = 0.01
- **Detection**: p < 0.01

## Secondary Metrics

### 8. Parity Bias (B_parity)

Deviation from balanced parity distribution.

```
B_parity = |P(parity=0) - 0.5|
```

- **Range**: [0, 0.5]
- **Baseline target**: B_parity < 0.02

### 9. Ancilla Fidelity (F_ancilla)

Fidelity of ancilla state relative to expected parity state.

```
F_ancilla = |⟨ψ_expected|ψ_actual⟩|²
```

- **Range**: [0, 1]
- **Target**: F_ancilla > 0.95 for baseline

### 10. Cross-Parity Correlation (C_cross)

For mirrored circuits, correlation between left and right parity ancillas.

```
C_cross = I(A_L : A_R)
```

- **Range**: [0, 1] bits
- **Detection**: Correlation change under asymmetric interception

## Metric Collection Protocol

```python
def collect_parity_metrics(
    circuit: QuantumCircuit,
    backend: Backend,
    shots: int = 8192,
    interception_qubit: Optional[int] = None,
    phase_angles: Optional[List[float]] = None
) -> Dict[str, float]:
    """
    Run parity witness circuit and collect all metrics.
    
    Args:
        circuit: Parity witness circuit
        backend: Quantum backend
        shots: Number of shots
        interception_qubit: Qubit to intercept (None for baseline)
        phase_angles: List of phase angles for oscillation measurement
        
    Returns:
        Dictionary with all metric values
    """
    metrics = {}
    
    # Run baseline
    baseline_results = run_circuit(circuit, backend, shots)
    metrics['baseline_parity'] = compute_parity_distribution(baseline_results)
    metrics['baseline_joint'] = compute_joint_distribution(baseline_results)
    
    # Run with interception if specified
    if interception_qubit is not None:
        intercepted_results = run_with_interception(
            circuit, backend, shots, interception_qubit
        )
        metrics['intercepted_parity'] = compute_parity_distribution(intercepted_results)
        metrics['intercepted_joint'] = compute_joint_distribution(intercepted_results)
        metrics['parity_kl'] = kl_divergence(
            metrics['intercepted_parity'],
            metrics['baseline_parity']
        )
        metrics['joint_kl'] = kl_divergence(
            metrics['intercepted_joint'],
            metrics['baseline_joint']
        )
    
    # Compute correlation metrics
    metrics['correlation_baseline'] = compute_mutual_info(metrics['baseline_joint'])
    if interception_qubit is not None:
        metrics['correlation_intercepted'] = compute_mutual_info(metrics['intercepted_joint'])
        metrics['correlation_drift'] = (
            metrics['correlation_baseline'] - metrics['correlation_intercepted']
        )
    
    # Compute witness score
    metrics['witness_score'] = compute_witness_score(metrics)
    
    # Phase-sensitive metrics if angles provided
    if phase_angles:
        metrics['oscillation'] = compute_oscillation_metrics(
            circuit, backend, shots, phase_angles, interception_qubit
        )
    
    return metrics
```

## Reporting Format

| Metric | Baseline | Intercepted | Delta | 95% CI | Pass/Fail |
|--------|----------|-------------|-------|--------|-----------|
| Parity KL | - | X.XX | - | [X.XX, X.XX] | ✓/✗ |
| Joint KL | - | X.XX | - | [X.XX, X.XX] | ✓/✗ |
| Correlation Drift | X.XX | X.XX | X.XX | [X.XX, X.XX] | ✓/✗ |
| Witness Score | - | X.XX | - | [X.XX, X.XX] | ✓/✗ |
| Chi-square p | - | X.XX | - | - | ✓/✗ |

## Detection Decision Tree

```
                    ┌─────────────────┐
                    │ Parity KL > 0.1? │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              │ Yes                         │ No
              ▼                             ▼
      ┌───────────────┐           ┌─────────────────┐
      │ DETECTED      │           │ Joint KL > 0.1? │
      │ (High Conf.)  │           └────────┬────────┘
      └───────────────┘                    │
                                  ┌───────┴───────┐
                                  │ Yes           │ No
                                  ▼               ▼
                          ┌───────────┐   ┌─────────────┐
                          │ DETECTED  │   │ Witness     │
                          │ (Medium)  │   │ Score > 0.1?│
                          └───────────┘   └──────┬──────┘
                                                 │
                                         ┌───────┴───────┐
                                         │ Yes           │ No
                                         ▼               ▼
                                 ┌───────────┐   ┌───────────┐
                                 │ DETECTED  │   │ NOT       │
                                 │ (Low)     │   │ DETECTED  │
                                 └───────────┘   └───────────┘
```