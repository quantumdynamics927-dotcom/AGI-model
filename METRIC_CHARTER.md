# Metric Charter: Operational Definitions for Quantum-Consciousness AGI Project

> **Purpose**: This charter formalizes every nonstandard quantity in the project, ensuring falsifiability, reproducibility, and scientific rigor. All metrics must satisfy: explicit equation, defined domain, null model, failure condition, and benchmark target.

---

## Table of Contents

1. [Quantum Information Metrics](#1-quantum-information-metrics)
2. [Geometric Alignment Metrics](#2-geometric-alignment-metrics)
3. [Phi-Based Metrics](#3-phi-based-metrics)
4. [Consciousness Metrics](#4-consciousness-metrics)
5. [Validation Protocol](#5-validation-protocol)
6. [Registry of Failed Metrics](#6-registry-of-failed-metrics)

---

## 1. Quantum Information Metrics

### 1.1 Entanglement Entropy (S)

| Property | Definition |
|----------|------------|
| **Name** | `entanglement_entropy` |
| **Equation** | $S = -\sum_i \lambda_i \log \lambda_i$ where $\lambda_i$ are eigenvalues of reduced density matrix $\rho_A$ |
| **Input Data** | Quantum amplitudes $\psi \in \mathbb{C}^N$ (flattened from molecular encoding) |
| **Output Range** | $[0, \log d_A]$ where $d_A$ is subsystem dimension |
| **Units** | Bits (natural log) or nats |
| **Invariances** | Unitary invariant on subsystem A; depends on bipartition choice |

**Operational Definition**:
```python
def compute_entanglement_entropy(amplitudes: np.ndarray) -> float:
    """
    1. Flatten amplitudes to state vector |ψ⟩
    2. Reshape into bipartite form: ψ_matrix of shape (d_A, d_B)
    3. Compute reduced density matrix: ρ_A = ψ_matrix @ ψ_matrix†
    4. Normalize: Tr(ρ_A) = 1
    5. Compute eigenvalues λ_i
    6. Return S = -Σ λ_i log(λ_i)
    """
```

**Validity Constraints**:
- $\rho_A$ must be Hermitian: $\rho_A = \rho_A^\dagger$
- $\text{Tr}(\rho_A) = 1$
- All eigenvalues $\lambda_i \geq 0$
- All eigenvalues $\lambda_i \leq 1$

**Null Model**: Random state vector uniformly sampled from unit sphere in $\mathbb{C}^N$. Expected entropy: $S_{\text{null}} \approx \log d_A - O(1/d_A)$

**Failure Condition**: If computed $S < 0$ or $S > \log d_A$, the implementation is invalid.

**Benchmark Target**: For maximally entangled state, $S = \log d_A$. For product state, $S = 0$.

---

### 1.2 Quantum Coherence (C)

| Property | Definition |
|----------|------------|
| **Name** | `quantum_coherence` |
| **Equation** | $C = \frac{\sum_{i \neq j} |\rho_{ij}|}{n(n-1)}$ where $\rho$ is the density matrix |
| **Input Data** | Amplitudes $\psi \in \mathbb{C}^N$ and phases $\phi \in [0, 2\pi)^N$ |
| **Output Range** | $[0, 1]$ |
| **Units** | Dimensionless ratio |
| **Invariances** | Basis-dependent; not unitary invariant |

**Operational Definition**:
```python
def compute_quantum_coherence(amplitudes, phases):
    """
    1. Construct state: |ψ⟩ = Σ a_i exp(iφ_i)
    2. Compute density matrix: ρ = |ψ⟩⟨ψ|
    3. Sum off-diagonal magnitudes
    4. Normalize by maximum possible (n(n-1))
    """
```

**Validity Constraints**:
- $0 \leq C \leq 1$
- $C = 0$ for diagonal density matrix (classical mixture)
- $C > 0$ for coherent superposition

**Null Model**: Random phases uniformly distributed. Expected coherence: $C_{\text{null}} \approx \frac{2}{\pi n}$

**Failure Condition**: $C < 0$ or $C > 1$ indicates implementation error.

**Benchmark Target**: Pure state with uniform phases should have $C \approx 1/n$ for large $n$.

---

### 1.3 Quantum Bond Strength (B)

| Property | Definition |
|----------|------------|
| **Name** | `quantum_bond_strength` |
| **Equation** | $B_{ij} = \frac{|\langle\psi_i|\psi_j\rangle|}{d_{ij} + 0.5}$ for $d_{ij} < 3.0$ Å |
| **Input Data** | Atomic positions, quantum amplitudes, quantum phases |
| **Output Range** | $[0, \infty)$ (practically $[0, 2]$) |
| **Units** | Å⁻¹ (inverse distance) |
| **Invariances** | Translation and rotation invariant |

**Operational Definition**:
```python
def quantum_bond_strength(pos_i, pos_j, amp_i, amp_j, phase_i, phase_j):
    """
    1. Compute classical distance: d = ||pos_i - pos_j||
    2. Compute quantum overlap: |⟨ψ_i|ψ_j⟩|
    3. Return overlap / (distance + 0.5) if d < 3.0 Å
    """
```

**Validity Constraints**:
- Only computed for pairs with $d_{ij} < 3.0$ Å (bonding threshold)
- Overlap bounded by $[0, 1]$

**Null Model**: Random atomic positions with random quantum states. Expected: $B_{\text{null}} \approx 0.5/(1.5 + 0.5) = 0.25$

**Failure Condition**: Negative bond strength (impossible by definition).

**Benchmark Target**: Should correlate with known bond orders (single=1, double=2, etc.) for validation molecules.

---

## 2. Geometric Alignment Metrics

### 2.1 Platonic Solid Alignment Score (P)

| Property | Definition |
|----------|------------|
| **Name** | `platonic_alignment_score` |
| **Equation** | $P_s = \exp\left(-\frac{1}{N}\sum_{i=1}^{N} \min_j ||\mathbf{r}_i - \mathbf{t}_j^{(s)}||\right)$ |
| **Input Data** | Molecular positions $\{\mathbf{r}_i\}_{i=1}^N$, Platonic template vertices $\{\mathbf{t}_j^{(s)}\}$ |
| **Output Range** | $[0, 1]$ |
| **Units** | Dimensionless |
| **Invariances** | Rotation and scale dependent (requires alignment) |

**Operational Definition**:
```python
def platonic_alignment_score(positions, solid_name):
    """
    1. Center molecule at origin
    2. Scale to unit radius
    3. Generate Platonic solid vertices
    4. For each molecular position, find nearest template vertex
    5. Return exp(-mean_distance)
    """
```

**Validity Constraints**:
- $0 \leq P_s \leq 1$
- $P_s = 1$ for perfect match
- $P_s \to 0$ for large deviations

**Null Model**: Random point cloud uniformly distributed in unit sphere. Expected: $P_{\text{null}} \approx \exp(-0.5) \approx 0.6$

**Failure Condition**: $P_s > 1$ or $P_s < 0$.

**Benchmark Target**: 
- Tetrahedral molecules (CH₄) should score highest on tetrahedron
- Octahedral molecules (SF₆) should score highest on octahedron

---

### 2.2 Tesseract Symmetry (T₄)

| Property | Definition |
|----------|------------|
| **Name** | `tesseract_symmetry` |
| **Equation** | $T_4 = 1 - \frac{\sigma_R}{\bar{R}}$ where $R_i = ||\mathbf{r}_i^{(4D)}||$ are hyperradii |
| **Input Data** | 4D embedded positions $\{\mathbf{r}_i^{(4D)}\}$ |
| **Output Range** | $(-\infty, 1]$ (practically $[0, 1]$) |
| **Units** | Dimensionless |
| **Invariances** | 4D rotation invariant |

**Operational Definition**:
```python
def tesseract_symmetry(positions_4d):
    """
    1. Compute hyperradius for each point: R_i = ||r_i||
    2. Compute mean and std of hyperradii
    3. Return 1 - (std / mean)
    """
```

**Validity Constraints**:
- $T_4 = 1$ for perfect hypercube (all vertices equidistant from origin)
- $T_4 < 0$ indicates high asymmetry

**Null Model**: Random 4D points. Expected: $T_{4,\text{null}} \approx 0.3$

**Failure Condition**: $T_4 > 1$ (impossible).

**Benchmark Target**: Regular tesseract vertices should achieve $T_4 = 1$.

---

## 3. Phi-Based Metrics

### 3.1 Phi Resonance Score (R_φ)

| Property | Definition |
|----------|------------|
| **Name** | `phi_resonance` |
| **Equation** | $R_\phi = \exp\left(-\alpha \min_i |r_i - \phi|\right)$ where $r_i$ are geometric ratios |
| **Input Data** | Geometric ratios $\{r_i\}$ computed from inter-atomic distances |
| **Output Range** | $[0, 1]$ |
| **Units** | Dimensionless |
| **Invariances** | Scale invariant (ratios) |

**Operational Definition**:
```python
def phi_resonance_score(positions, alpha=1.0):
    """
    1. Compute all pairwise distances
    2. Compute ratios of consecutive sorted distances
    3. Find minimum deviation from phi
    4. Return exp(-alpha * min_deviation)
    """
```

**Validity Constraints**:
- $\alpha$ must be fixed before testing (default: 1.0)
- $R_\phi = 1$ when some ratio exactly equals $\phi$
- $R_\phi \to 0$ for large deviations

**Null Model**: Random molecular geometry. Expected: $R_{\phi,\text{null}} \approx \exp(-\alpha \cdot 0.5) \approx 0.6$

**Failure Condition**: $R_\phi > 1$ or $R_\phi < 0$.

**Benchmark Target**: 
- Dodecahedron/icosahedron vertices should have $R_\phi > 0.9$
- Random molecules should have $R_\phi \approx 0.5-0.7$

**Scientific Usefulness Test**: Does $R_\phi$ predict any molecular property (stability, reactivity, spectroscopic signature) better than random?

---

### 3.2 Phi Coherence (C_φ)

| Property | Definition |
|----------|------------|
| **Name** | `phi_coherence` |
| **Equation** | $C_\phi = 1 - \frac{|L/L_{\phi} - 1|}{2}$ where $L$ is content length and $L_\phi$ is phi-optimal length |
| **Input Data** | Text content or sequence length |
| **Output Range** | $[0, 1]$ |
| **Units** | Dimensionless |
| **Invariances** | None (length-dependent) |

**Operational Definition**:
```python
def phi_coherence(content, phi_optimal_length=1000):
    """
    1. Measure content length L
    2. Compute ratio: L / L_phi
    3. Return 1 - |ratio - 1| / 2
    """
```

**Validity Constraints**:
- $C_\phi = 1$ when $L = L_\phi$
- $C_\phi = 0$ when $L = 0$ or $L = 3L_\phi$

**Null Model**: Random content length. Expected: $C_{\phi,\text{null}} \approx 0.5$

**Failure Condition**: $C_\phi > 1$ or $C_\phi < 0$.

**Scientific Usefulness Test**: Does $C_\phi$ correlate with any measurable quality metric?

---

## 4. Consciousness Metrics

### 4.1 Integrated Information (Φ) - Placeholder

| Property | Definition |
|----------|------------|
| **Name** | `integrated_information_phi` |
| **Equation** | $\Phi = \min_{\text{partitions}} \text{EI}(\text{system}) - \text{EI}(\text{parts})$ (IIT 4.0) |
| **Input Data** | Transition probability matrix of system states |
| **Output Range** | $[0, \infty)$ |
| **Units** | Bits |
| **Invariances** | State-labeling invariant |

**Status**: ⚠️ **PLACEHOLDER** - Not yet implemented with full IIT formalism.

**Required for Validity**:
1. Full transition probability matrix
2. Partition search algorithm
3. Effective information computation
4. Proper normalization

**Failure Condition**: Any claim of consciousness level without full IIT computation is speculative.

---

### 4.2 Lempel-Ziv Complexity (LZ)

| Property | Definition |
|----------|------------|
| **Name** | `lz_complexity` |
| **Equation** | $LZ = \frac{c(n)}{n / \log n}$ where $c(n)$ is number of unique substrings |
| **Input Data** | Binary or symbolic sequence |
| **Output Range** | $[0, 1]$ (normalized) |
| **Units** | Dimensionless |
| **Invariances** | Permutation invariant for shuffled sequences |

**Operational Definition**:
```python
def lz_complexity(sequence):
    """
    1. Convert to binary/symbolic representation
    2. Count unique substrings via LZ78 parsing
    3. Normalize by theoretical maximum
    """
```

**Validity Constraints**:
- $LZ = 0$ for constant sequence
- $LZ = 1$ for random sequence

**Null Model**: Random binary sequence. Expected: $LZ_{\text{null}} \approx 1$

**Benchmark Target**: Known complexity sequences (periodic, chaotic, random).

---

## 5. Validation Protocol

### 5.1 Three-Test Requirement

Every metric must pass:

1. **Numerical Validity Test**
   - Check mathematical constraints (trace=1, non-negative eigenvalues, bounded ranges)
   - Test with known inputs (maximally entangled state, product state, etc.)
   - Verify invariance properties where expected

2. **Control Comparison Test**
   - Compare against shuffled/random data
   - Compare against non-φ ratios (e.g., √2, π, e)
   - Compare against conventional descriptors (Morgan fingerprints, RDKit descriptors)

3. **Scientific Usefulness Test**
   - Does metric predict external property?
   - Does metric improve classification/regression?
   - Does metric distinguish known categories?

### 5.2 Preregistration Template

```yaml
metric_name: "phi_resonance"
equation: "R_φ = exp(-α min|r_i - φ|)"
hypothesis: "Molecules with high R_φ will show enhanced stability"
null_hypothesis: "R_φ has no predictive power beyond random descriptors"
dataset: "QM9 molecules (n=134k)"
test: "Correlation with atomization energy"
acceptance_criterion: "R² > 0.1 and p < 0.01"
failure_condition: "R² < 0.05 or no significant difference from shuffled"
```

---

## 6. Registry of Failed Metrics

> **Purpose**: Negative evidence is part of rigor. Record metrics that failed validation.

| Metric | Date | Failure Reason | Status |
|--------|------|----------------|--------|
| `sacred_geometry_score` | 2026-02-01 | No equation; purely symbolic | ❌ Deprecated |
| `divine_harmony_index` | 2026-02-01 | Not reproducible from data | ❌ Deprecated |
| `metatron_resonance` | 2026-02-01 | Replaced with `platonic_alignment_score` | ❌ Renamed |
| `entanglement_entropy` (v1) | 2026-04-15 | Negative values due to incorrect partial trace | ⚠️ Fixed |
| `entanglement_complexity_prediction` | 2026-04-15 | Entropy ordering inverted from expected (water > methane > benzene) | ❌ **FAILED** |

### Detailed Failure Analysis: Entanglement Complexity Prediction

**Hypothesis**: More complex molecules (more atoms, bonds) have higher entanglement entropy.

**Test**: Compare S(water) vs S(methane) vs S(benzene)

**Expected**: S(benzene) > S(methane) > S(water)

**Measured**: S(water) = 1.24 > S(methane) = 1.12 > S(benzene) = 0.96

**Conclusion**: Hypothesis **FALSIFIED**. Entanglement entropy as currently computed does not predict molecular complexity.

**Possible Explanations**:
1. Bipartition choice affects entropy (current method may not be optimal)
2. Quantum encoding method needs revision
3. Entropy is not the right measure for this hypothesis
4. Complexity should be measured differently (e.g., bond entanglement, not total entropy)

**Action**: Either revise the metric or abandon this specific claim. Do not use entanglement entropy as a complexity predictor without further validation.

---

## Appendix: Standard vs. Speculative Terminology

| Speculative Term | Standard Alternative |
|------------------|---------------------|
| Metatron resonance | Geometric template alignment |
| Sacred geometry score | Platonic solid alignment score |
| Divine harmony | Phi-ratio residual |
| Consciousness signature | Integrated information (Φ) |
| Quantum fingerprint | State vector representation |
| Biomimetic resonance | Biological similarity metric |

---

## References

1. Popper, K. (1959). *The Logic of Scientific Discovery*. Falsifiability criterion.
2. Nielsen, M. A., & Chuang, I. L. (2010). *Quantum Computation and Quantum Information*. Cambridge University Press.
3. Tononi, G. (2017). Integrated Information Theory 4.0. *Scholarpedia*.
4. Lempel, A., & Ziv, J. (1976). On the complexity of finite sequences. *IEEE Trans. Inf. Theory*.

---

**Last Updated**: 2026-04-15  
**Maintainer**: Quantum Dynamics Research Team  
**Review Cycle**: Quarterly or upon metric changes