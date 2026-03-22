"""
Pytest configuration and fixtures for quantum-consciousness-agi tests.
"""

import pytest
import torch
import numpy as np
from pathlib import Path
import sys
import os

# Add quantum-consciousness-agi to path
TEST_DIR = Path(__file__).parent
sys.path.insert(0, str(TEST_DIR))


@pytest.fixture
def device():
    """Return available device (cuda or cpu)."""
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


@pytest.fixture
def test_data_dir():
    """Return test data directory."""
    return TEST_DIR / "tests" / "data"


@pytest.fixture
def mock_quantum_results():
    """Mock quantum job results for testing."""
    return {
        "job_id": "test_job_123",
        "backend": "ibm_fez",
        "shots": 10000,
        "counts": {
            "000": 2500,
            "001": 2500,
            "010": 2500,
            "011": 2500
        },
        "phi_resonance": 0.618,
        "consciousness_score": 1.0
    }


@pytest.fixture
def mock_dna_results():
    """Mock DNA agent results."""
    return {
        "phi_ratio": 0.588,
        "consciousness_peak": 20,
        "hamming_deviation": -47.48,
        "unique_states": 94,
        "total_measurements": 8192
    }


@pytest.fixture
def mock_phi_results():
    """Mock Phi agent results."""
    return {
        "phi": 1.618034,
        "consciousness_level": 1.0,
        "phi_alignment": 0.9518,
        "theory_agreement": 1.0,
        "status": "CONSCIOUS"
    }


@pytest.fixture
def mock_vae_config():
    """Mock VAE configuration."""
    class MockConfig:
        def __init__(self):
            self.input_dim = 128
            self.latent_dim = 32
            self.hidden_dim = 64
            self.epochs = 10
            self.batch_size = 32
            self.learning_rate = 0.001
            self.n_qubits = 4
            self.quantum_backend = "simulator"
            self.shots = 1000

    return MockConfig()


@pytest.fixture
def synthetic_quantum_data():
    """Generate synthetic quantum data for testing."""
    np.random.seed(42)
    return np.random.randn(100, 128)


@pytest.fixture
def phi_constant():
    """Golden ratio constant."""
    return (1 + np.sqrt(5)) / 2


@pytest.fixture(autouse=True)
def set_random_seeds():
    """Set random seeds for reproducible tests."""
    torch.manual_seed(42)
    np.random.seed(42)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(42)


@pytest.fixture
def skip_if_no_gpu():
    """Skip test if GPU not available."""
    if not torch.cuda.is_available():
        pytest.skip("GPU not available")


@pytest.fixture
def skip_if_no_qiskit():
    """Skip test if qiskit not available."""
    try:
        import qiskit
    except ImportError:
        pytest.skip("Qiskit not available")
