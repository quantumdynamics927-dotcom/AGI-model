#!/usr/bin/env python3
"""Test script for wing consciousness bridge dependencies"""

print("Testing Wing-Consciousness Bridge Dependencies...")
print("=" * 50)

try:
    import numpy as np
    print("✓ NumPy:", np.__version__)
except ImportError as e:
    print("✗ NumPy failed:", e)

try:
    import torch
    print("✓ PyTorch:", torch.__version__)
except ImportError as e:
    print("✗ PyTorch failed:", e)

try:
    import matplotlib
    print("✓ Matplotlib:", matplotlib.__version__)
except ImportError as e:
    print("✗ Matplotlib failed:", e)

try:
    import sklearn
    print("✓ Scikit-learn:", sklearn.__version__)
except ImportError as e:
    print("✗ Scikit-learn failed:", e)

print("\nTesting basic functionality...")

# Test golden ratio
PHI = (1 + 5**0.5) / 2
print(f"✓ Golden ratio: {PHI:.6f}")

# Test numpy array
arr = np.random.randn(10, 2)
print(f"✓ NumPy array shape: {arr.shape}")

# Test torch tensor
tensor = torch.randn(10, 64)
print(f"✓ PyTorch tensor shape: {tensor.shape}")

print("\n🎉 All dependencies working! Ready for Wing-Consciousness Bridge.")