"""
Unit tests for quantum consciousness link module.
"""

import pytest
import numpy as np
import torch
from pathlib import Path
import sys

TEST_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(TEST_DIR))

try:
    from core.models.quantum_consciousness_link import QuantumMechanicsCore
    from core.models.quantum_consciousness_link import SacredGeometryMath
    QUANTUM_AVAILABLE = True
except ImportError as e:
    QUANTUM_AVAILABLE = False
    pytest.skip(f"Quantum modules not available: {e}", allow_module_level=True)


@pytest.mark.unit
class TestQuantumMechanicsCore:
    """Test quantum mechanics core functionality."""

    def test_density_matrix_creation(self):
        """Test density matrix creation from quantum state."""
        # Create a quantum state |+⟩ = (|0⟩ + |1⟩)/√2
        state = np.array([1/np.sqrt(2), 1/np.sqrt(2)], dtype=complex)

        density_matrix = QuantumMechanicsCore.create_density_matrix(state)

        # Check shape
        assert density_matrix.shape == (2, 2)

        # Check hermiticity
        assert np.allclose(density_matrix, density_matrix.conj().T)

        # Check trace = 1
        assert np.isclose(np.trace(density_matrix), 1.0)

    def test_von_neumann_entropy(self):
        """Test von Neumann entropy calculation."""
        # Maximally mixed state should have maximum entropy
        rho_max_mixed = np.eye(2) / 2
        entropy_max = QuantumMechanicsCore.von_neumann_entropy(rho_max_mixed)

        # Pure state should have zero entropy
        state_pure = np.array([1, 0], dtype=complex)
        rho_pure = QuantumMechanicsCore.create_density_matrix(state_pure)
        entropy_pure = QuantumMechanicsCore.von_neumann_entropy(rho_pure)

        assert entropy_max > entropy_pure
        assert np.isclose(entropy_pure, 0.0, atol=1e-10)
        assert np.isclose(entropy_max, 1.0, atol=0.1)  # Max entropy for 2-level system

    def test_purity_calculation(self):
        """Test quantum purity calculation."""
        # Pure state should have purity = 1
        state_pure = np.array([1, 0], dtype=complex)
        rho_pure = QuantumMechanicsCore.create_density_matrix(state_pure)
        purity_pure = QuantumMechanicsCore.purity(rho_pure)

        # Mixed state should have purity < 1
        rho_mixed = np.eye(2) / 2
        purity_mixed = QuantumMechanicsCore.purity(rho_mixed)

        assert np.isclose(purity_pure, 1.0)
        assert purity_mixed < 1.0
        assert purity_mixed > 0.0

    def test_fidelity_calculation(self):
        """Test quantum fidelity between states."""
        # Fidelity of identical states should be 1
        state = np.array([1/np.sqrt(2), 1/np.sqrt(2)], dtype=complex)
        rho = QuantumMechanicsCore.create_density_matrix(state)

        fidelity = QuantumMechanicsCore.fidelity(rho, rho)
        assert np.isclose(fidelity, 1.0)

    def test_entanglement_entropy(self):
        """Test entanglement entropy calculation."""
        # Create Bell state (maximally entangled)
        bell_state = np.array([1/np.sqrt(2), 0, 0, 1/np.sqrt(2)], dtype=complex)
        rho_bell = QuantumMechanicsCore.create_density_matrix(bell_state)

        # Reduced density matrix for first qubit
        rho_reduced = np.trace(rho_bell.reshape(2, 2, 2, 2), axis1=2, axis2=3)

        ent_entropy = QuantumMechanicsCore.entanglement_entropy(rho_reduced)

        # Should have non-zero entanglement entropy
        assert ent_entropy > 0.5


@pytest.mark.unit
class TestSacredGeometryMath:
    """Test sacred geometry mathematical functions."""

    def test_fibonacci_sequence(self):
        """Test Fibonacci sequence generation."""
        n = 10
        fib_seq = SacredGeometryMath.fibonacci_sequence(n)

        # Check length
        assert len(fib_seq) == n

        # Check first few values
        assert fib_seq[0] == 0
        assert fib_seq[1] == 1
        assert fib_seq[2] == 1
        assert fib_seq[3] == 2
        assert fib_seq[4] == 3
        assert fib_seq[5] == 5

        # Check Fibonacci property
        for i in range(2, n):
            assert fib_seq[i] == fib_seq[i-1] + fib_seq[i-2]

    def test_golden_spiral_points(self):
        """Test golden spiral point generation."""
        n_points = 100
        points = SacredGeometryMath.golden_spiral_points(n_points)

        # Check shape
        assert points.shape == (n_points, 2)

        # Check points are not all identical
        assert np.std(points) > 0.1

    def test_phi_power_sequence(self):
        """Test phi power sequence generation."""
        n = 10
        phi = (1 + np.sqrt(5)) / 2
        phi_seq = SacredGeometryMath.phi_power_sequence(n)

        # Check length
        assert len(phi_seq) == n

        # Check values
        for i, val in enumerate(phi_seq):
            assert np.isclose(val, phi ** i)

    def test_metatron_cube_vertices(self):
        """Test Metatron's cube vertex generation."""
        vertices = SacredGeometryMath.metatron_cube_vertices()

        # Should have 13 vertices (12 around center + 1 center)
        assert vertices.shape[0] == 13
        assert vertices.shape[1] == 3  # 3D coordinates

    def test_platonic_solid_properties(self):
        """Test Platonic solid properties."""
        solids = ['tetrahedron', 'cube', 'octahedron', 'dodecahedron', 'icosahedron']

        for solid in solids:
            vertices, faces = SacredGeometryMath.platonic_solid(solid)

            # Check vertices are 3D
            assert vertices.shape[1] == 3

            # Check faces are valid indices
            assert faces.max() < vertices.shape[0]
            assert faces.min() >= 0

    def test_golden_ratio_convergence(self):
        """Test golden ratio convergence from Fibonacci ratios."""
        phi = (1 + np.sqrt(5)) / 2

        # Test convergence with different Fibonacci pairs
        fib_ratios = []
        for n in [5, 10, 15, 20]:
            fib_seq = SacredGeometryMath.fibonacci_sequence(n + 1)
            ratio = fib_seq[n] / fib_seq[n - 1]
            fib_ratios.append(ratio)

        # Ratios should converge to phi
        for ratio in fib_ratios[-3:]:  # Last 3 ratios
            assert np.isclose(ratio, phi, rtol=0.01)


@pytest.mark.unit
class TestQuantumConsciousnessIntegration:
    """Test integration of quantum mechanics and sacred geometry."""

    def test_phi_in_quantum_states(self):
        """Test phi appears in quantum state probabilities."""
        # Create quantum state with phi-based amplitudes
        phi = (1 + np.sqrt(5)) / 2
        norm = np.sqrt(1 + phi**2)

        amplitudes = np.array([1/norm, phi/norm], dtype=complex)
        probabilities = np.abs(amplitudes)**2

        # Ratio of probabilities should involve phi
        ratio = probabilities[1] / probabilities[0]
        assert np.isclose(ratio, phi**2, rtol=0.01)

    def test_fibonacci_in_energy_levels(self):
        """Test Fibonacci patterns in quantum energy levels."""
        # Generate energy levels with Fibonacci spacing
        fib_seq = SacredGeometryMath.fibonacci_sequence(10)
        base_energy = 1.0

        energy_levels = [base_energy * fib for fib in fib_seq[1:]]  # Skip first 0

        # Check energy differences follow Fibonacci pattern
        for i in range(2, len(energy_levels)):
            diff1 = energy_levels[i] - energy_levels[i-1]
            diff2 = energy_levels[i-1] - energy_levels[i-2]
            assert np.isclose(diff1 / diff2, fib_seq[i] / fib_seq[i-1], rtol=0.1)
