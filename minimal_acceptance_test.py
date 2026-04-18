"""
Minimal acceptance test for tesseract routing
"""

import torch
import numpy as np
from quantum_cognitive_core import QuantumCognitiveCore, QuantumCognitiveConfig

def test_basic_functionality():
    """Test basic functionality of both routing approaches"""
    
    print("Testing basic tesseract routing functionality...")
    
    # Test flat routing
    print("1. Testing flat routing...")
    flat_config = QuantumCognitiveConfig()
    flat_config.tesseract_enabled = False
    flat_core = QuantumCognitiveCore(flat_config)
    
    input_data = torch.randn(1, 128)
    flat_result = flat_core.process_input(input_data)
    print(f"   Flat routing successful, phi_score: {flat_result['phi_score']:.4f}")
    
    # Test tesseract routing
    print("2. Testing tesseract routing...")
    tesseract_config = QuantumCognitiveConfig()
    tesseract_config.tesseract_enabled = True
    tesseract_core = QuantumCognitiveCore(tesseract_config)
    
    tesseract_result = tesseract_core.process_input(input_data)
    print(f"   Tesseract routing successful, vertex: {tesseract_result['tesseract_vertex']}")
    print(f"   Router info: {tesseract_result['router_info']['name']}")
    print(f"   Phi score: {tesseract_result['phi_score']:.4f}")
    
    # Compare results
    print("\n3. Comparison:")
    print(f"   Flat phi: {flat_result['phi_score']:.4f}")
    print(f"   Tesseract phi: {tesseract_result['phi_score']:.4f}")
    
    return flat_result, tesseract_result

def run_simple_benchmark():
    """Run a simple benchmark comparison"""
    
    print("\nRunning simple benchmark...")
    
    # Create cores
    flat_config = QuantumCognitiveConfig()
    flat_config.tesseract_enabled = False
    flat_core = QuantumCognitiveCore(flat_config)
    
    tesseract_config = QuantumCognitiveConfig()
    tesseract_config.tesseract_enabled = True
    tesseract_core = QuantumCognitiveCore(tesseract_config)
    
    # Test multiple samples
    num_samples = 10
    flat_scores = []
    tesseract_scores = []
    
    for i in range(num_samples):
        input_data = torch.randn(1, 128)
        
        # Flat routing
        flat_result = flat_core.process_input(input_data)
        flat_scores.append(flat_result['phi_score'])
        
        # Tesseract routing
        tesseract_result = tesseract_core.process_input(input_data)
        tesseract_scores.append(tesseract_result['phi_score'])
        
    # Calculate averages
    flat_avg = np.mean(flat_scores)
    tesseract_avg = np.mean(tesseract_scores)
    
    print(f"\nBenchmark Results ({num_samples} samples):")
    print(f"  Flat routing average phi: {flat_avg:.4f}")
    print(f"  Tesseract routing average phi: {tesseract_avg:.4f}")
    print(f"  Difference: {tesseract_avg - flat_avg:.4f}")
    
    return flat_avg, tesseract_avg

if __name__ == "__main__":
    # Run tests
    flat_result, tesseract_result = test_basic_functionality()
    flat_avg, tesseract_avg = run_simple_benchmark()
    
    print("\n" + "="*50)
    print("MINIMAL ACCEPTANCE TEST COMPLETE")
    print("="*50)
    print("Both routing approaches are functional and can be compared.")
    print("Ready for full acceptance testing.")
    print("="*50)