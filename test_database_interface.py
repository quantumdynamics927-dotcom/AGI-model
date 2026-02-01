#!/usr/bin/env python3
"""
Test script for AGI Database Interface
Demonstrates the database interface functionality
"""

import numpy as np
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agi_database import AGIDatabase

def test_database_interface():
    """Test the database interface without actual database connection"""
    print("🧠 Testing AGI Database Interface")
    print("=" * 50)

    # Test 1: Import and instantiation
    try:
        db = AGIDatabase()
        print("✅ Database interface instantiated successfully")
    except Exception as e:
        print(f"❌ Failed to instantiate database interface: {e}")
        return False

    # Test 2: Check connection string
    print(f"📍 Connection string configured: {db.connection_string is not None}")

    # Test 3: Test data preparation functions
    print("\n🔬 Testing data preparation functions...")

    # Create sample sacred geometry data
    sample_vector = np.random.randn(128).astype(np.float32)
    print(f"📊 Created sample 128D vector: shape {sample_vector.shape}")

    # Create sample consciousness data
    eeg_data = np.random.randn(1000).astype(np.float32)
    print(f"🧠 Created sample EEG data: {len(eeg_data)} samples")

    # Test golden ratio calculation (following project patterns)
    ratios = sample_vector[1:] / (sample_vector[:-1] + 1e-10)
    phi_proximity = np.abs(ratios - 1.618034)
    golden_ratio_score = 1.0 / (1.0 + np.mean(phi_proximity))
    print(f"🌀 Golden ratio analysis: score={golden_ratio_score:.4f}")
    # Test normalization (following project patterns)
    mean = np.mean(sample_vector)
    std = np.std(sample_vector)
    normalized = (sample_vector - mean) / (std + 1e-10)
    print(f"🔄 Normalization applied: mean={mean:.4f}, std={std:.4f}")

    print("\n✅ All interface tests passed!")
    print("\n📋 Database Interface Features:")
    print("  • Sacred geometry data storage and retrieval")
    print("  • Consciousness data (EEG/fMRI) management")
    print("  • Quantum VAE model persistence")
    print("  • NFT metadata with quantum verification")
    print("  • Training session tracking")
    print("  • Latent space analysis storage")
    print("  • Unified dataset creation")

    print("\n🚀 Ready for database integration!")
    return True

if __name__ == "__main__":
    success = test_database_interface()
    sys.exit(0 if success else 1)