# Observer Symmetry Metrics

## Primary Metrics

### 1. Symmetry Score (S)

Measures the bilateral balance between left and right reservoir correlations.

```
S = 1 - |P(L=1|C=0) - P(R=1|C=0)| - |P(L=1|C=1) - P(R=1|C=1)|
```

- **Range**: [0, 1]
- **Interpretation**: S = 1 indicates perfect symmetry, S = 0 indicates maximum asymmetry
- **Target**: S > 0.95 for undisturbed circuits

### 2. Left-Right KL Divergence (D_LR)

Kullback-Leibler divergence between left and right conditional distributions.

```
D_LR = D_KL(P(L|C) || P(R|C))
```

- **Range**: [0, ∞)
- **Interpretation**: D_LR = 0 indicates identical distributions
- **Target**: D_LR < 0.01 for undisturbed circuits
- **Tamper threshold**: D_LR > 0.1 indicates likely interception

### 3. Measurement Disturbance Delta (Δ_M)

Difference in output distribution between disturbed and undisturbed cases.

```
Δ_M = D_KL(P_disturbed(C) || P_baseline(C))
```

- **Range**: [0, ∞)
- **Interpretation**: Higher values indicate greater disturbance
- **Target**: Δ_M < 0.01 for undisturbed circuits
- **Detection threshold**: Δ_M > 0.05 triggers tamper alert

### 4. Mutual Information Shift (Δ_I)

Change in mutual information between reservoir qubits after interception.

```
Δ_I = I(L:R)_baseline - I(L:R)_intercepted
```

- **Range**: (-∞, ∞)
- **Interpretation**: Positive values indicate information loss due to interception
- **Target**: Δ_I ≈ 0 for undisturbed circuits
- **Tamper indicator**: Δ_I > 0.1 bits

### 5. Output Distribution Drift (δ)

Temporal stability of measurement outcomes across runs.

```
δ = max_t |P_t(C) - P_baseline(C)|
```

- **Range**: [0, 1]
- **Interpretation**: Lower values indicate more stable outputs
- **Target**: δ < 0.02 for stable circuits

### 6. Fidelity Loss (F_loss)

Reduction in state fidelity due to intermediate measurement.

```
F_loss = 1 - F(ρ_intercepted, ρ_baseline)
```

- **Range**: [0, 1]
- **Interpretation**: Higher values indicate greater state disturbance
- **Target**: F_loss < 0.01 for undisturbed circuits

### 7. Min-Entropy (H_min)

For QRNG mode, the minimum entropy of the output distribution.

```
H_min = -log2(max_x P(x))
```

- **Range**: [0, n] for n-bit output
- **Interpretation**: Higher values indicate better randomness
- **Target**: H_min > 0.95 bits/qubit

## Composite Detection Score

A weighted combination of primary metrics for tamper detection:

```
Detection_Score = w1 * Δ_M + w2 * D_LR + w3 * Δ_I + w4 * F_loss
```

Default weights: w1=0.3, w2=0.3, w3=0.2, w4=0.2

- **Detection threshold**: Detection_Score > 0.1
- **High confidence threshold**: Detection_Score > 0.2

## Statistical Tests

### Chi-Square Test

Compare observed distribution to expected baseline:

```
χ² = Σ (O_i - E_i)² / E_i
```

- **Null hypothesis**: No interception occurred
- **Significance level**: α = 0.01
- **Degrees of freedom**: 2^n - 1 for n measurement outcomes

### Two-Sample Kolmogorov-Smirnov Test

Compare distributions before and after potential interception:

```
D_KS = sup_x |F_1(x) - F_2(x)|
```

- **Null hypothesis**: Distributions are identical
- **Significance level**: α = 0.01

### Bootstrapped Confidence Intervals

For all metrics, compute 95% confidence intervals via bootstrap:

```
CI_95 = [percentile_2.5, percentile_97.5]
```

## Metric Collection Protocol

```python
def collect_metrics(
    circuit: QuantumCircuit,
    backend: Backend,
    shots: int = 8192,
    interception_qubit: Optional[int] = None
) -> Dict[str, float]:
    """
    Run circuit and collect all metrics.
    
    Returns:
        Dictionary with all metric values and confidence intervals
    """
    metrics = {}
    
    # Run baseline
    baseline_results = run_circuit(circuit, backend, shots)
    metrics['baseline'] = compute_distribution(baseline_results)
    
    # Run with interception if specified
    if interception_qubit is not None:
        intercepted_results = run_with_interception(
            circuit, backend, shots, interception_qubit
        )
        metrics['intercepted'] = compute_distribution(intercepted_results)
        metrics['delta_m'] = kl_divergence(
            metrics['intercepted'], metrics['baseline']
        )
    
    # Compute all metrics
    metrics['symmetry_score'] = compute_symmetry(metrics['baseline'])
    metrics['kl_divergence_lr'] = compute_lr_kl(metrics['baseline'])
    metrics['mutual_information'] = compute_mutual_info(metrics['baseline'])
    metrics['min_entropy'] = compute_min_entropy(metrics['baseline'])
    
    return metrics
```

## Reporting Format

All experiment reports must include:

| Metric | Value | 95% CI | Target | Pass/Fail |
|--------|-------|--------|--------|-----------|
| Symmetry Score | X.XX | [X.XX, X.XX] | > 0.95 | ✓/✗ |
| KL Divergence (L-R) | X.XX | [X.XX, X.XX] | < 0.01 | ✓/✗ |
| Measurement Disturbance | X.XX | [X.XX, X.XX] | < 0.05 | ✓/✗ |
| Mutual Information Shift | X.XX | [X.XX, X.XX] | < 0.1 | ✓/✗ |
| Min-Entropy | X.XX | [X.XX, X.XX] | > 0.95 | ✓/✗ |