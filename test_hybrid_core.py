"""
Test script for the Quantum Cognitive Core components
"""

import torch
import logging
from quantum_cognitive_core import QuantumCognitiveCore, QuantumCognitiveConfig
from benchmark_framework import BenchmarkFramework

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_quantum_cognitive_core():
    """Test the basic functionality of the Quantum Cognitive Core"""
    logger.info("Testing Quantum Cognitive Core...")
    
    # Create configuration
    config = QuantumCognitiveConfig()
    
    # Initialize core
    core = QuantumCognitiveCore(config)
    
    # Create test input
    input_data = torch.randn(1, config.encoder_input_dim)
    
    # Process input
    result = core.process_input(input_data)
    
    # Check results
    assert 'latent_state' in result
    assert 'quantum_processed' in result
    assert 'action' in result
    assert 'phi_score' in result
    
    logger.info("Quantum Cognitive Core test passed!")
    print(f"Phi score: {result['phi_score']:.4f}")
    print(f"Action shape: {result['action'].shape}")
    
def test_benchmark_framework():
    """Test the benchmark framework"""
    logger.info("Testing Benchmark Framework...")
    
    # Initialize benchmark framework
    benchmark = BenchmarkFramework()
    
    # Define simple task generator and evaluator
    def task_generator():
        input_data = torch.randn(1, 128)
        target = torch.randn(1, 32)
        return input_data, target
        
    def task_evaluator(action, target):
        # Simple cosine similarity
        action_norm = action / (torch.norm(action) + 1e-8)
        target_norm = target / (torch.norm(target) + 1e-8)
        similarity = torch.dot(action_norm.flatten(), target_norm.flatten()).item()
        return (similarity + 1.0) / 2.0
    
    # Run comparative benchmark
    results = benchmark.run_comparative_benchmark(
        task_generator, task_evaluator,
        num_samples=5, task_name="test_task"
    )
    
    # Check results
    assert 'classical' in results
    assert 'quantum' in results
    assert 'quantum_inspired' in results
    
    logger.info("Benchmark Framework test passed!")
    print("Benchmark results:")
    for system_type, result in results.items():
        print(f"  {system_type}: {result.accuracy:.4f} accuracy")

if __name__ == "__main__":
    # Run tests
    test_quantum_cognitive_core()
    test_benchmark_framework()
    
    print("\nAll tests passed successfully!")