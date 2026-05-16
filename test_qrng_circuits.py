#!/usr/bin/env python3
"""
Test Suite for QRNG Circuits
============================

Validates all 5 QRNG circuits with comprehensive tests:
- Golden Ratio Phase QRNG
- DNA Entropic QRNG
- BitNet Ternary QRNG
- Hybrid Consciousness QRNG
- Metatron Fractal QRNG

Author: AGI-model Quantum Computing Team
Date: April 27, 2026
"""

import sys
import numpy as np
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from qrng_circuits import (
        GoldenRatioPhaseQRNG,
        DNAEntropicQRNG,
        BitNetTernaryQRNG,
        HybridConsciousnessQRNG,
        MetatronFractalQRNG,
        compare_qrng_circuits,
        generate_random_bytes,
        PHI, PHI_INV
    )
    QISKIT_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import QRNG circuits: {e}")
    QISKIT_AVAILABLE = False


def test_golden_ratio_qrng():
    """Test Golden Ratio Phase QRNG."""
    print("\n" + "="*60)
    print("Testing Golden Ratio Phase QRNG")
    print("="*60)
    
    if not QISKIT_AVAILABLE:
        print("⚠️  Skipping: Qiskit not available")
        return None
    
    # Create circuit
    qrng = GoldenRatioPhaseQRNG(num_qubits=8)
    circuit = qrng.generate_circuit()
    
    print(f"✓ Circuit created with {qrng.num_qubits} qubits")
    print(f"✓ Circuit depth: {circuit.depth()}")
    print(f"✓ Number of gates: {len(circuit)}")
    
    # Extract randomness
    result = qrng.extract_randomness(shots=1024)
    
    print(f"\n📊 Results:")
    print(f"  Random bitstring: {result['bitstring']}")
    print(f"  Shannon entropy: {result['shannon_entropy']:.4f} bits")
    print(f"  Max entropy: {result['max_entropy']}")
    print(f"  Entropy ratio: {result['entropy_ratio']:.4f}")
    print(f"  φ proximity: {result['phi_proximity']:.6f}")
    
    # Validate
    assert result['shannon_entropy'] > 0, "Entropy should be positive"
    assert len(result['random_bits']) == qrng.num_qubits, "Bit count mismatch"
    
    print("✅ Golden Ratio QRNG test passed!")
    return result


def test_dna_entropic_qrng():
    """Test DNA Entropic QRNG."""
    print("\n" + "="*60)
    print("Testing DNA Entropic QRNG")
    print("="*60)
    
    if not QISKIT_AVAILABLE:
        print("⚠️  Skipping: Qiskit not available")
        return None
    
    # Test with different DNA sequences
    test_sequences = [
        "ATGCATGC",
        "GCTAGCTA",
        "AAAATTTT",
        "GGGGCCCC"
    ]
    
    results = []
    for seq in test_sequences:
        qrng = DNAEntropicQRNG(dna_sequence=seq, num_qubits=len(seq))
        circuit = qrng.generate_circuit()
        result = qrng.extract_randomness(shots=1024)
        results.append(result)
        
        print(f"\n🧬 DNA Sequence: {seq}")
        print(f"  GC content: {result['gc_content']:.2%}")
        print(f"  Shannon entropy: {result['shannon_entropy']:.4f} bits")
        print(f"  Entropy per base: {result['entropy_per_base']:.4f}")
    
    # Validate
    for result in results:
        assert result['shannon_entropy'] > 0, "Entropy should be positive"
    
    print("\n✅ DNA Entropic QRNG test passed!")
    return results[0]


def test_bitnet_ternary_qrng():
    """Test BitNet Ternary QRNG."""
    print("\n" + "="*60)
    print("Testing BitNet Ternary QRNG")
    print("="*60)
    
    if not QISKIT_AVAILABLE:
        print("⚠️  Skipping: Qiskit not available")
        return None
    
    # Create circuit with default BitNet distribution
    qrng = BitNetTernaryQRNG(num_qubits=8, seed=42)
    circuit = qrng.generate_circuit()
    
    print(f"✓ Circuit created with {qrng.num_qubits} qubits")
    print(f"✓ Weight distribution: {qrng.weight_dist}")
    print(f"✓ Generated weights: {qrng.weights}")
    
    # Extract randomness
    result = qrng.extract_randomness(shots=1024)
    
    print(f"\n📊 Results:")
    print(f"  Random bitstring: {result['bitstring']}")
    print(f"  Shannon entropy: {result['shannon_entropy']:.4f} bits")
    print(f"  Weight entropy: {result['weight_entropy']:.4f}")
    print(f"  Ternary balance: {result['ternary_balance']:.2%}")
    
    # Validate
    assert result['shannon_entropy'] > 0, "Entropy should be positive"
    assert 0 <= result['ternary_balance'] <= 1, "Balance should be in [0,1]"
    
    print("✅ BitNet Ternary QRNG test passed!")
    return result


def test_hybrid_consciousness_qrng():
    """Test Hybrid Consciousness QRNG."""
    print("\n" + "="*60)
    print("Testing Hybrid Consciousness QRNG")
    print("="*60)
    
    if not QISKIT_AVAILABLE:
        print("⚠️  Skipping: Qiskit not available")
        return None
    
    # Create circuit with custom parameters
    qrng = HybridConsciousnessQRNG(
        num_qubits=8,
        dna_sequence="ATGCATGC",
        bitnet_weights=[0, 1, -1, 0, 1, 0, -1, 0],
        consciousness_phi=0.8524
    )
    circuit = qrng.generate_circuit()
    
    print(f"✓ Circuit created with {qrng.num_qubits} qubits")
    print(f"✓ Consciousness φ: {qrng.consciousness_phi}")
    print(f"✓ DNA sequence: {qrng.dna_sequence}")
    print(f"✓ BitNet weights: {qrng.bitnet_weights}")
    
    # Extract randomness
    result = qrng.extract_randomness(shots=1024)
    
    print(f"\n📊 Results:")
    print(f"  Random bitstring: {result['bitstring']}")
    print(f"  Shannon entropy: {result['shannon_entropy']:.4f} bits")
    print(f"  DNA entropy: {result['dna_entropy']:.4f}")
    print(f"  BitNet entropy: {result['bitnet_entropy']:.4f}")
    print(f"  Hybrid entropy score: {result['hybrid_entropy_score']:.4f}")
    
    # Validate
    assert result['shannon_entropy'] > 0, "Entropy should be positive"
    assert result['hybrid_entropy_score'] > 0, "Hybrid score should be positive"
    
    print("✅ Hybrid Consciousness QRNG test passed!")
    return result


def test_metatron_fractal_qrng():
    """Test Metatron Fractal QRNG."""
    print("\n" + "="*60)
    print("Testing Metatron Fractal QRNG")
    print("="*60)
    
    if not QISKIT_AVAILABLE:
        print("⚠️  Skipping: Qiskit not available")
        return None
    
    # Create circuit with Sierpinski fractal
    qrng = MetatronFractalQRNG(num_qubits=21, fractal_depth=3)
    circuit = qrng.generate_circuit()
    
    print(f"✓ Circuit created with {qrng.num_qubits} qubits")
    print(f"✓ Fractal depth: {qrng.fractal_depth}")
    print(f"✓ Circuit depth: {circuit.depth()}")
    print(f"✓ Number of gates: {len(circuit)}")
    
    # Extract randomness
    result = qrng.extract_randomness(shots=1024)
    
    print(f"\n📊 Results:")
    print(f"  Random bitstring: {result['bitstring'][:21]}...")  # Truncate for display
    print(f"  Shannon entropy: {result['shannon_entropy']:.4f} bits")
    print(f"  Fractal depth: {result['fractal_depth']}")
    print(f"  Consciousness density: {result['consciousness_density']:.4f}")
    print(f"  Metatron enhancement: {result['metatron_enhancement']}")
    
    # Validate
    assert result['shannon_entropy'] > 0, "Entropy should be positive"
    assert result['consciousness_density'] > 0, "Density should be positive"
    
    print("✅ Metatron Fractal QRNG test passed!")
    return result


def test_comparison():
    """Test comparison of all QRNG circuits."""
    print("\n" + "="*60)
    print("Testing QRNG Circuit Comparison")
    print("="*60)
    
    if not QISKIT_AVAILABLE:
        print("⚠️  Skipping: Qiskit not available")
        return None
    
    # Compare all circuits
    comparison = compare_qrng_circuits(num_qubits=8, shots=1024)
    
    print("\n📊 Entropy Ranking:")
    for name, entropy in comparison['comparison']['entropy_ranking']:
        print(f"  {name:25s}: {entropy:.4f} bits")
    
    print(f"\n🏆 Best Entropy: {comparison['comparison']['best_entropy']}")
    print(f"📈 Average Entropy: {comparison['comparison']['average_entropy']:.4f} bits")
    
    print("\n📐 Circuit Depth Ranking:")
    for name, depth in comparison['comparison']['circuit_depth_ranking']:
        print(f"  {name:25s}: {depth} layers")
    
    # Validate
    assert len(comparison['comparison']['entropy_ranking']) == 5, "Should have 5 circuits"
    assert comparison['comparison']['average_entropy'] > 0, "Average entropy should be positive"
    
    print("\n✅ Comparison test passed!")
    return comparison


def test_random_bytes_generation():
    """Test random bytes generation."""
    print("\n" + "="*60)
    print("Testing Random Bytes Generation")
    print("="*60)
    
    if not QISKIT_AVAILABLE:
        print("⚠️  Skipping: Qiskit not available")
        return None
    
    circuit_types = ['golden', 'dna', 'bitnet', 'hybrid', 'metatron']
    
    for circuit_type in circuit_types:
        random_bytes = generate_random_bytes(circuit_type, num_bytes=32)
        
        print(f"\n🎲 {circuit_type.upper()} QRNG:")
        print(f"  Hex: {random_bytes.hex()[:64]}...")
        print(f"  Length: {len(random_bytes)} bytes")
        
        # Validate
        assert len(random_bytes) == 32, f"Should generate 32 bytes, got {len(random_bytes)}"
        assert isinstance(random_bytes, bytes), "Should return bytes"
    
    print("\n✅ Random bytes generation test passed!")
    return True


def test_golden_ratio_properties():
    """Test golden ratio mathematical properties."""
    print("\n" + "="*60)
    print("Testing Golden Ratio Properties")
    print("="*60)
    
    # Test φ properties
    print(f"φ (phi) = {PHI:.15f}")
    print(f"1/φ = {PHI_INV:.15f}")
    print(f"φ² = {PHI_SQUARED:.15f}")
    
    # Validate golden ratio identities
    assert abs(PHI - (1 + np.sqrt(5)) / 2) < 1e-10, "φ should equal (1+√5)/2"
    assert abs(PHI_INV - 1/PHI) < 1e-10, "1/φ should equal φ⁻¹"
    assert abs(PHI_SQUARED - PHI**2) < 1e-10, "φ² should equal φ*φ"
    assert abs(PHI_SQUARED - PHI - 1) < 1e-10, "φ² = φ + 1 (golden ratio identity)"
    
    print("✓ φ² = φ + 1: {PHI_SQUARED:.6f} ≈ {PHI + 1:.6f}")
    print("✓ 1/φ = φ - 1: {PHI_INV:.6f} ≈ {PHI - 1:.6f}")
    
    print("\n✅ Golden ratio properties validated!")


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*70)
    print("🧪 QRNG Circuit Test Suite")
    print("="*70)
    
    if not QISKIT_AVAILABLE:
        print("\n⚠️  Qiskit not available. Install with: pip install qiskit qiskit-aer")
        return
    
    results = {}
    
    # Run tests
    results['golden_ratio'] = test_golden_ratio_qrng()
    results['dna_entropic'] = test_dna_entropic_qrng()
    results['bitnet_ternary'] = test_bitnet_ternary_qrng()
    results['hybrid_consciousness'] = test_hybrid_consciousness_qrng()
    results['metatron_fractal'] = test_metatron_fractal_qrng()
    results['comparison'] = test_comparison()
    results['random_bytes'] = test_random_bytes_generation()
    results['golden_ratio_props'] = test_golden_ratio_properties()
    
    # Summary
    print("\n" + "="*70)
    print("📋 Test Summary")
    print("="*70)
    
    passed = sum(1 for r in results.values() if r is not None)
    total = len(results)
    
    print(f"\n✅ Passed: {passed}/{total} tests")
    
    if passed == total:
        print("\n🎉 All tests passed successfully!")
    else:
        print(f"\n⚠️  {total - passed} tests skipped or failed")
    
    return results


if __name__ == "__main__":
    run_all_tests()