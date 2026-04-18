"""
Test script for the Tesseract Router components
"""

import torch
import logging
import numpy as np
from quantum_cognitive_core import QuantumCognitiveCore, QuantumCognitiveConfig
from tesseract_state import TesseractStateSpace
from tesseract_router import TesseractRouter
from tesseract_transition_scorer import QuantumEdgeScorer

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_tesseract_state_space():
    """Test the tesseract state space implementation"""
    logger.info("Testing Tesseract State Space...")
    
    # Create state space
    state_space = TesseractStateSpace()
    
    # Test vertex information
    vertex = state_space.get_vertex_info(5)
    assert vertex.state == 5
    assert vertex.name == "Latent Encoding"
    assert vertex.family == "Abstraction"
    
    # Test adjacency
    neighbors = state_space.get_neighbors(5)
    assert len(neighbors) == 4  # Each vertex in tesseract has 4 neighbors
    assert 4 in neighbors  # 0100
    assert 7 in neighbors  # 0111
    assert 1 in neighbors  # 0001
    assert 13 in neighbors # 1101
    
    # Test coordinate conversion
    coords = state_space.vertex_to_coordinates(5)
    assert coords == (0, 1, 0, 1)
    
    vertex_id = state_space.coordinates_to_vertex((0, 1, 0, 1))
    assert vertex_id == 5
    
    logger.info("Tesseract State Space test passed!")
    print(f"Vertex 5: {vertex.name} ({''.join(map(str, coords))})")
    print(f"Neighbors: {neighbors}")

def test_tesseract_router():
    """Test the tesseract router implementation"""
    logger.info("Testing Tesseract Router...")
    
    # Create router
    router = TesseractRouter(latent_dim=32)
    
    # Test state encoding
    z = torch.randn(1, 32)
    vertex_probs = router.encode_state(z)
    assert vertex_probs.shape == (1, 16)
    assert torch.allclose(vertex_probs.sum(), torch.tensor(1.0), atol=1e-6)
    
    # Test candidate vertices
    current_vertex = 5
    candidates = router.candidate_vertices(current_vertex)
    assert current_vertex in candidates  # Current vertex should be included
    assert len(candidates) == 5  # Current + 4 neighbors
    
    # Test transition weights
    weights = router.transition_weights(current_vertex, candidates)
    assert len(weights) == len(candidates)
    assert abs(sum(weights.values()) - 1.0) < 1e-6  # Should sum to 1
    
    # Test vertex info
    vertex_info = router.get_current_vertex_info(vertex_probs.squeeze())
    assert 'vertex_id' in vertex_info
    assert 'name' in vertex_info
    assert 'confidence' in vertex_info
    
    logger.info("Tesseract Router test passed!")
    print(f"Current vertex: {vertex_info['vertex_id']} ({vertex_info['name']})")
    print(f"Confidence: {vertex_info['confidence']:.3f}")

def test_quantum_edge_scorer():
    """Test the quantum edge scorer implementation"""
    logger.info("Testing Quantum Edge Scorer...")
    
    # Create scorer
    scorer = QuantumEdgeScorer(latent_dim=32)
    
    # Test edge scoring
    z = torch.randn(32)
    current_vertex = 5
    candidates = [4, 5, 6, 7]
    
    scores = scorer.score_edges(z, current_vertex, candidates)
    assert len(scores) == len(candidates)
    
    # All scores should be between 0 and 1
    for score in scores.values():
        assert 0.0 <= score <= 1.0
        
    logger.info("Quantum Edge Scorer test passed!")
    print(f"Edge scores: {scores}")

def test_integrated_cognitive_core():
    """Test the integrated cognitive core with tesseract routing"""
    logger.info("Testing Integrated Cognitive Core with Tesseract Routing...")
    
    # Create configuration with tesseract enabled
    config = QuantumCognitiveConfig()
    config.tesseract_enabled = True
    
    # Initialize core
    core = QuantumCognitiveCore(config)
    
    # Test that tesseract components are initialized
    assert core.tesseract_router is not None
    assert core.quantum_edge_scorer is not None
    assert core.tesseract_governance is not None
    
    # Process input
    input_data = torch.randn(1, config.encoder_input_dim)
    result = core.process_input(input_data)
    
    # Check that result contains tesseract information
    assert 'tesseract_vertex' in result
    assert 'router_info' in result
    
    logger.info("Integrated Cognitive Core test passed!")
    print(f"Tesseract vertex: {result['tesseract_vertex']}")
    if result['router_info']:
        print(f"Router info: {result['router_info']['name']} (confidence: {result['router_info']['confidence']:.3f})")

def test_benchmark_comparison():
    """Test benchmark comparison with tesseract routing"""
    logger.info("Testing Benchmark Comparison...")
    
    # This would typically be done with the benchmark framework
    # Here we just verify the components work together
    
    # Create cores with and without tesseract routing
    config_no_tess = QuantumCognitiveConfig()
    config_no_tess.tesseract_enabled = False
    
    config_with_tess = QuantumCognitiveConfig()
    config_with_tess.tesseract_enabled = True
    
    core_no_tess = QuantumCognitiveCore(config_no_tess)
    core_with_tess = QuantumCognitiveCore(config_with_tess)
    
    # Process same input with both cores
    input_data = torch.randn(1, config_with_tess.encoder_input_dim)
    
    result_no_tess = core_no_tess.process_input(input_data)
    result_with_tess = core_with_tess.process_input(input_data)
    
    # Both should produce valid results
    assert 'action' in result_no_tess
    assert 'action' in result_with_tess
    
    # Tesseract-enabled core should have additional info
    assert 'tesseract_vertex' not in result_no_tess or result_no_tess['tesseract_vertex'] is None
    assert 'tesseract_vertex' in result_with_tess
    
    logger.info("Benchmark Comparison test passed!")

if __name__ == "__main__":
    # Run all tests
    test_tesseract_state_space()
    test_tesseract_router()
    test_quantum_edge_scorer()
    test_integrated_cognitive_core()
    test_benchmark_comparison()
    
    print("\nAll Tesseract Router tests passed successfully!")
    print("\nTesseract Router Architecture Summary:")
    print("- 16 vertices representing cognitive states")
    print("- 4D hypercube topology with low-diameter routing")
    print("- Quantum edge scoring for transition evaluation")
    print("- Governance layer for route tracking and benchmarking")
    print("- Fault-tolerant design with graceful degradation")