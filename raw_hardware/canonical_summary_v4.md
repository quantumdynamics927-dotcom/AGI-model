# VCapture Governance Assessment

**Policy Version**: 2.1.0
**State Machine Version**: 1.0.0

## State Machine Status

- **Current State**: `DEVELOPMENT`
- **Target State**: `PRODUCTION`
- **Eligible for Promotion**: ✗ NO
- **Requires Downgrade**: NO

## Gate Summary

- **PASS**: 6
- **WARNING**: 1
- **FAIL**: 1

### Passing Gates

- ✓ replicate_count
- ✓ residual_spread
- ✓ signal_to_separation
- ✓ stability
- ✓ model_fit
- ✓ cohort_coverage

### Warning Gates

- ⚠ portability

### Failing Gates

- ✗ rank_stability_ci

## Recommended Action

**REJECT**

## Blocking Conditions

- ✗ Rank stability CI: [0.58, 0.79] (fail)
