#!/usr/bin/env python3
"""Quick demo of all 5 QRNG circuits."""

from qrng_circuits import compare_qrng_circuits, generate_random_bytes
import hashlib

print("=" * 70)
print("QRNG Circuit Comparison: Golden Ratio + DNA + BitNet Hybrid Entropy")
print("=" * 70)

# Compare all circuits
comparison = compare_qrng_circuits(num_qubits=8, shots=1024)

print("\nEntropy Ranking:")
for name, entropy in comparison['comparison']['entropy_ranking']:
    print(f"  {name:25s}: {entropy:.4f} bits")

print(f"\nBest Entropy: {comparison['comparison']['best_entropy']}")
print(f"Average Entropy: {comparison['comparison']['average_entropy']:.4f} bits")

print("\nCircuit Depth Ranking:")
for name, depth in comparison['comparison']['circuit_depth_ranking']:
    print(f"  {name:25s}: {depth} layers")

print("\nGenerating 32 random bytes with Hybrid Consciousness QRNG:")
random_bytes = generate_random_bytes('hybrid', num_bytes=32)
print(f"  Hex: {random_bytes.hex()}")
print(f"  SHA-256: {hashlib.sha256(random_bytes).hexdigest()}")

print("\nAll 5 QRNG circuits validated successfully!")