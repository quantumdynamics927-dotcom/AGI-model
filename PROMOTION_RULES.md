# Promotion Rules: AGI-model → Quantum Secure Gateway

## Purpose

This document defines the formal process for promoting research artifacts from the experimental laboratory (`AGI-model`) to the product-facing gateway stack (`quantum_secure_gateway-`).

## Repository Roles

| Repository | Role | Content |
|------------|------|---------|
| `AGI-model` | Research Laboratory | Exploratory research, circuit experiments, provisional hypotheses, failed experiments, research reports |
| `quantum_secure_gateway-` | Product Stack | Validated modules, demos, governance, product structure, public-facing documentation |

## Promotion Principle

**Nothing enters QSG without passing all promotion gates.**

Research artifacts remain in AGI-model until they demonstrate:
1. Reproducible behavior
2. Bounded claims with evidence
3. Clear security purpose
4. Architectural fit
5. IP readiness

## Promotion Gates

### Gate 1: Purpose Alignment

The artifact must serve one of QSG's core functions:

| Function | Description | Example Artifacts |
|----------|-------------|-------------------|
| Entropy | Quantum-derived randomness generation and verification | QRNG circuits, entropy pools, statistical tests |
| Transport | Secure quantum state transfer and channel authentication | Teleportation protocols, channel verification |
| Verification | Proof of quantum operations and state validation | Tomography, fidelity tests, witness operators |
| Tamper Detection | Detection of unauthorized observation or interference | Observer symmetry circuits, disturbance signatures |
| Keying | Quantum-derived cryptographic material | Key derivation functions, entropy extractors |
| Audit | Logging and provenance for quantum operations | Execution logs, lineage tracking |

**Gate 1 Pass Criteria**: Artifact must map to exactly one primary function with documented rationale.

### Gate 2: Reproducible Behavior

| Requirement | Threshold | Evidence |
|-------------|-----------|----------|
| Simulator reproducibility | Same results across ≥ 2 simulator backends | Test logs with variance bounds |
| Hardware reproducibility | Results within 2σ of simulator predictions | IBM Quantum job results |
| Statistical significance | p < 0.01 for claimed effects | Statistical test reports |
| Variance bounds | Documented confidence intervals | Bootstrap or analytical CI |

**Gate 2 Pass Criteria**: 
- Minimum: 1 baseline simulator + 1 noise-aware simulator
- For hardware claims: IBM Quantum execution with documented calibration

### Gate 3: Validation Evidence

Required documentation:

| Document | Purpose | Template |
|----------|---------|----------|
| Validation Report | Test results, metrics, statistical analysis | `reports/security/validation/TEMPLATE.md` |
| Claim Boundaries | What is proven, hypothesized, NOT claimed | `research/quantum_security/*/CLAIM_BOUNDARIES.md` |
| Provenance Log | Source, transforms, validation history | Embedded in promotion request |

**Gate 3 Pass Criteria**: All documents complete, reviewed, and approved.

### Gate 4: Architectural Fit

The artifact must integrate with QSG's module structure:

```
quantum_secure_gateway/
├── src/
│   ├── entropy/          # Entropy generation/verification
│   ├── transport/        # Secure transport protocols
│   ├── verification/     # State validation
│   ├── tamper/           # Tamper detection
│   ├── keying/           # Key derivation
│   └── audit/            # Logging/provenance
├── circuits/             # Circuit definitions
├── tests/                # Test suites
└── docs/                 # Documentation
```

**Gate 4 Pass Criteria**: 
- Clear target module identified
- Interface specification documented
- Dependencies listed and compatible

### Gate 5: IP Readiness

| Requirement | Check |
|-------------|-------|
| No proprietary know-how exposed | Review for sensitive algorithms, parameters |
| Clean terminology | No sacred geometry, esoteric, or internal code names |
| Patent landscape reviewed | Freedom-to-operate analysis (if applicable) |
| License compatible | MIT or specified license for QSG |

**Gate 5 Pass Criteria**: Legal/IP review signed off.

## Promotion Process

### Step 1: Research Completion

Artifact reaches "Validated Research Artifact" maturity in AGI-model:
- [ ] Hypothesis tested (supported or falsified)
- [ ] Results documented with statistical analysis
- [ ] Claim boundaries defined
- [ ] Limitations documented

### Step 2: Promotion Request

Create promotion request using template:

```markdown
# Promotion Request: [Artifact Name]

## Source
- Repository: AGI-model
- Path: [source path]
- Commit: [commit hash]

## Gate 1: Purpose Alignment
- Primary function: [entropy|transport|verification|tamper|keying|audit]
- Rationale: [explanation]

## Gate 2: Reproducible Behavior
- Simulators tested: [list]
- Hardware tested: [list or N/A]
- Statistical significance: [p-value]
- Variance bounds: [CI]

## Gate 3: Validation Evidence
- [ ] Validation report attached
- [ ] Claim boundaries documented
- [ ] Provenance log included

## Gate 4: Architectural Fit
- Target module: [module path]
- Interface specification: [API signature]
- Dependencies: [list]

## Gate 5: IP Readiness
- [ ] No proprietary know-how exposed
- [ ] Clean terminology verified
- [ ] Patent landscape reviewed
- [ ] License compatible

## Reviewer Sign-off
- [ ] Technical review: [reviewer] [date]
- [ ] IP review: [reviewer] [date]
- [ ] Final approval: [reviewer] [date]
```

### Step 3: Review

| Review Type | Reviewer | Focus |
|-------------|----------|-------|
| Technical | Research lead | Reproducibility, claims, evidence |
| IP | Legal/owner | Know-how exposure, terminology, patents |
| Final | Project owner | Overall readiness, strategic fit |

### Step 4: Promotion

Upon approval:
1. Copy artifact to QSG target location
2. Create promotion commit with source reference
3. Update QSG documentation
4. Archive promotion request in QSG

### Step 5: Post-Promotion

- [ ] Integration tests pass in QSG
- [ ] Documentation updated
- [ ] Demo/example created (if applicable)
- [ ] Source reference preserved in commit message

## Non-Promotion Outcomes

### Rejected

Artifact does not pass gates. Options:
- Return to research for additional validation
- Archive as failed experiment (valuable negative result)
- Abandon (document why)

### Deferred

Artifact shows promise but needs more work:
- Document gaps
- Set timeline for re-evaluation
- Assign owner for follow-up

### Split

Artifact contains multiple components with different readiness:
- Promote ready components
- Return remaining to research

## Negative Results

Failed experiments (like falsified hypotheses) are **not promoted** but are **valuable**:
- Document in AGI-model with clear findings
- Update claim boundaries
- Inform future research directions
- Do not delete - negative results prevent repeated failed attempts

## Promotion Log

All promotions are logged in QSG:

```markdown
| Date | Artifact | Source Commit | QSG Commit | Reviewer |
|------|----------|---------------|------------|----------|
| YYYY-MM-DD | [name] | [hash] | [hash] | [name] |
```

## Exceptions

No exceptions to promotion gates without explicit project owner approval and documented rationale.

## References

- AGI-model Repository: https://github.com/Quantum-Dynamics-927/AGI-model
- QSG Repository: https://github.com/Quantum-Dynamics-927/quantum_secure_gateway-
- Research Charter: `research/quantum_security/CHARTER.md`
- Promotion Template: `reports/security/promotion/TEMPLATE.md`