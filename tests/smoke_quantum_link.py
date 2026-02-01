import numpy as np
from quantum_consciousness_link import QuantumConsciousnessAnalyzer
from vae_model import QuantumVAE


class FakeAnalyzer(QuantumConsciousnessAnalyzer):
    def __init__(self):
        # Do not load external model, create a fresh small model for smoke testing
        self.model = QuantumVAE(input_dim=128, latent_dim=32)
        self.model.eval()
        self.phi = (1 + np.sqrt(5)) / 2


def test_generate_and_extract_smoke():
    analyzer = FakeAnalyzer()
    states = analyzer._generate_consciousness_states(50)
    assert states.shape[0] == 50

    latent_codes = analyzer._extract_latent_patterns(states[:10])
    assert latent_codes.shape[1] == 32
    assert np.isfinite(latent_codes).all()
