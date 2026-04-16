# Cornell-φ Benchmark Experiment Proposal
## Comparing Unconstrained vs φ-Constrained Cornell Fits

## Objective

Design and execute a benchmark experiment comparing the performance of unconstrained Cornell potential fits versus φ-constrained Cornell potential fits on synthetic and real quarkonium observables. This addresses the key scientific question:

> **"When does a φ-constraint help, hurt, or leave performance unchanged relative to standard Cornell parameter freedom?"**

## Experimental Design

### Synthetic Validation Targets

#### 1. Charmonium Spectrum Fitting
- **Target Data**: Ground state and excited state masses for η_c, J/ψ, χ_{c0}, χ_{c1}, χ_{c2}, h_c, ψ(2S), ψ(3S)
- **Hamiltonian**: H = m₁ + m₂ + V_φ(r) or H = m₁ + m₂ + V_C(r; σ, α)
- **Fitting Parameters**: 
  - Unconstrained: σ, α (2 parameters)
  - φ-Constrained: None (0 parameters, σ=1/φ, α=1/(2φ²))
- **Metrics**: Root Mean Square Deviation (RMSD) from experimental masses

#### 2. Bottomonium Spectrum Fitting
- **Target Data**: η_b, Υ(1S), χ_{b0}, χ_{b1}, χ_{b2}, h_b, Υ(2S), Υ(3S)
- **Same methodology as charmonium**

#### 3. Hybrid Potential Fitting
- **Target Data**: Lattice QCD potential data V(r) at various distances
- **Potentials Compared**:
  - V_C(r; σ, α) - Standard Cornell with free parameters
  - V_φ(r) - Fixed φ-constrained Cornell
  - V_{C+φ}(r) - Cornell with φ-inspired parameter priors
- **Metrics**: χ² per degree of freedom, Bayesian Information Criterion (BIC)

### Real Data Validation

#### 1. Quarkonium Decay Widths
- **Target Observables**: Radiative and hadronic decay widths
- **Method**: Compute using potential model wavefunctions from fitted potentials
- **Comparison**: Theoretical predictions vs experimental measurements

#### 2. Quarkonium Production Cross Sections
- **Target Observables**: e⁺e⁻ → Υ(nS), pp → Υ(nS) + X
- **Method**: NRQCD factorization with potential model matrix elements
- **Comparison**: Theoretical predictions vs collider data

## Methodology

### Potential Definitions

#### Standard Cornell Potential
```
V_C(r; σ, α) = -α/r + σr + c
```
Where σ (string tension) and α (Coulomb strength) are free parameters.

#### Cornell-φ Potential
```
V_φ(r) = r/φ - 1/(2φ²r)
```
Where φ = (1 + √5)/2 ≈ 1.618034 (no free parameters).

#### φ-Prior Constrained Cornell
```
V_{C,φ}(r; λ) = -α(λ)/r + σ(λ)r + c
```
Where σ(λ) = λ/φ and α(λ) = λ/(2φ²) (1 free parameter λ).

### Fitting Procedure

#### 1. Spectral Fitting
For bound state energies E_n:
1. Solve Schrödinger equation: H|ψ_n⟩ = E_n|ψ_n⟩
2. H = m₁ + m₂ + V(r) (reduced mass formalism)
3. Minimize χ² = Σᵢ [(Eᵢ^(theory) - Eᵢ^(exp))/σᵢ]²

#### 2. Potential Fitting
For lattice QCD potential data Vᵢ at distances rᵢ:
1. Minimize χ² = Σᵢ [(V(rᵢ) - Vᵢ^(lattice))/σᵢ]²
2. Compare V_C(r; σ, α) vs V_φ(r) vs V_{C,φ}(r; λ)

### Statistical Analysis

#### Model Comparison Metrics
1. **Akaike Information Criterion (AIC)**: AIC = 2k - 2ln(L)
2. **Bayesian Information Criterion (BIC)**: BIC = k·ln(n) - 2ln(L)
3. **Cross-Validation Error**: Leave-one-out CV error

Where k = number of parameters, n = number of data points, L = maximum likelihood.

#### Hypothesis Testing
- **Null Hypothesis**: φ-constrained model performs equally to unconstrained
- **Alternative Hypothesis**: φ-constrained model performs differently
- **Test Statistic**: Likelihood ratio test Δ = -2ln(L₀/L₁)
- **Distribution**: χ² with degrees of freedom = parameter difference

## Implementation Plan

### Phase 1: Synthetic Data Generation (Weeks 1-2)
1. Generate synthetic quarkonium spectra with known parameters
2. Create synthetic lattice QCD potential data with noise
3. Establish baseline performance metrics

### Phase 2: Model Implementation (Weeks 3-4)
1. Implement Schrödinger equation solver for Cornell-type potentials
2. Create fitting routines for spectral and potential data
3. Validate against known solutions

### Phase 3: Benchmark Execution (Weeks 5-6)
1. Run unconstrained Cornell fits on all datasets
2. Run φ-constrained Cornell fits on all datasets
3. Run φ-prior constrained fits on all datasets
4. Collect performance metrics

### Phase 4: Analysis and Reporting (Weeks 7-8)
1. Statistical comparison of model performances
2. Identify conditions where φ-constraints help/hurt
3. Document results with visualization

## Expected Outcomes

### Primary Results
1. **Performance Comparison**: Quantitative assessment of model quality
2. **Condition Identification**: When φ-constraints are beneficial vs detrimental
3. **Cross-Domain Validation**: Consistency with neural network benchmark results

### Secondary Results
1. **Theoretical Insights**: Understanding of φ-optimality in physical systems
2. **Methodological Advances**: Improved fitting techniques for constrained models
3. **Framework Validation**: Demonstration of unified research approach

## Success Criteria

### Quantitative Thresholds
- **Model Quality**: BIC difference > 5 considered significant
- **Fitting Accuracy**: RMSD < 10 MeV for quarkonium spectra
- **Cross-Validation**: Consistent performance across datasets

### Qualitative Assessments
- **Scientific Rigor**: Proper statistical treatment of uncertainties
- **Methodological Soundness**: Reproducible results with clear documentation
- **Cross-Domain Consistency**: Alignment with neural network benchmark findings

## Risk Mitigation

### Technical Risks
1. **Computational Complexity**: Spectral calculations may be expensive
   - *Mitigation*: Use efficient numerical methods and parallelization
   
2. **Convergence Issues**: Fitting algorithms may fail to converge
   - *Mitigation*: Multiple starting points and robust optimization
   
3. **Synthetic Data Realism**: Artificial data may not represent real physics
   - *Mitigation*: Validate against known theoretical results

### Scientific Risks
1. **Overinterpretation**: Drawing strong conclusions from limited data
   - *Mitigation*: Conservative statistical analysis with proper uncertainty quantification
   
2. **Domain Mismatch**: Physics and ML domains may behave differently
   - *Mitigation*: Focus on methodological parallels rather than direct transfer

## Resource Requirements

### Computational Resources
- **Hardware**: Multi-core CPU cluster for parallel spectral calculations
- **Software**: Python with NumPy, SciPy, and quantum mechanics libraries
- **Storage**: ~10 GB for intermediate results and datasets

### Personnel Resources
- **Lead Researcher**: 50% effort for 8 weeks
- **Collaborator**: 25% effort for validation and cross-checking
- **Consultant**: Occasional advice on potential model specifics

## Timeline

| Week | Activity | Deliverable |
|------|----------|-------------|
| 1-2 | Synthetic data generation | Datasets with known parameters |
| 3-4 | Model implementation | Working code for all potential types |
| 5-6 | Benchmark execution | Performance metrics for all models |
| 7-8 | Analysis and reporting | Comparative analysis report |

## Conclusion

This benchmark experiment will provide definitive answers to whether φ-constraints offer practical advantages in physical modeling contexts. By comparing directly against unconstrained baselines using standard physics validation metrics, we can determine the genuine utility of golden ratio priors in potential models. The results will inform both the theoretical understanding of φ-optimality and the practical application of constrained parameterization approaches in scientific modeling.

The experiment directly mirrors our neural network benchmark strategy, establishing methodological unity across domains while maintaining domain-appropriate validation standards. This approach strengthens our cross-domain phi research program by grounding it in rigorous comparative analysis rather than qualitative assertions.