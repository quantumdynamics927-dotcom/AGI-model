# conftest.py
"""
Pytest configuration for Quantum Consciousness AGI.
Adds project directories to Python path for imports.
"""

import sys
from pathlib import Path

# Get project root directory
project_root = Path(__file__).parent

# Directories to add to Python path
dirs_to_add = [
    project_root,
    project_root / "TMT-OS",
    project_root / "tmt-os-labs",
    project_root / "tmt_os_labs",
    project_root / "integrations",
    project_root / "agi_scripts",
    project_root / "agi_app",
    project_root / "agi_model",
    project_root / "src",
    project_root / "utils",
    project_root / "quantum_observer",
    project_root / "data_provenance",
]

# Add directories to sys.path if not already present
for d in dirs_to_add:
    dir_path = str(d)
    if dir_path not in sys.path and d.exists():
        sys.path.insert(0, dir_path)

# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "quantum: marks tests that require quantum backend"
    )
    config.addinivalue_line(
        "markers", "gpu: marks tests that require GPU"
    )