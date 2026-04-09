# AGI Model Artifacts

This directory contains reference examples and generated artifacts from the AGI Model platform.

## Directory Structure

### `reference_examples/`
Contains sample output files generated during testing and demonstration:

- **Certificate Examples**: Sample discovery certificates from Node 7 validation
- **Circuit History**: DNA quantum circuit generation examples
- **Statistics**: Performance and analysis metrics

## Usage

These files serve as:
1. **Reproducibility References**: Example outputs for validation
2. **Documentation Aids**: Concrete examples of system output
3. **Testing Fixtures**: Sample data for integration tests

## Important Notes

- Files in this directory are **generated artifacts** from specific runs
- For production use, generate fresh artifacts using the current codebase
- These examples represent the system state at commit `9ddf3b8` (April 9, 2026)

## Generating New Artifacts

### Discovery Certificates
```python
from node7_discovery_validator import Node7DiscoveryValidator

validator = Node7DiscoveryValidator(validation_dir='artifacts/reference_examples')
certificate = validator.validate_and_certify(your_discovery)
```

### DNA Circuit History
```bash
python test_dna_circuits.py --output-dir artifacts/reference_examples
```

### Circuit Statistics
```bash
python dna_features_demo.py --save-history --output-dir artifacts/reference_examples
```

## File Descriptions

| File | Type | Description |
|------|------|-------------|
| `discovery_*.certificate.json` | Certificate | TMT-OS certified discovery examples |
| `demo_circuit_history.json` | History | DNA circuit generation history |
| `demo_circuit_statistics.json` | Statistics | Circuit analysis metrics |
| `dna_circuit_history.json` | History | DNA encoding examples |

## Version

**Artifacts generated from**: AGI Model v0.98.0-rc  
**Date**: April 9, 2026  
**Commit**: `9ddf3b8`

---

*These artifacts are for reference purposes. Generate fresh outputs for production use.*
