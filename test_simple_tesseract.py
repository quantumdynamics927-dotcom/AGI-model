"""
Simple test for tesseract integration
"""

import torch
import logging
from quantum_cognitive_core import QuantumCognitiveCore, QuantumCognitiveConfig

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_tesseract_integration():
    """Test basic tesseract integration"""
    logger.info("Testing tesseract integration...")
    
    # Create configuration with tesseract enabled
    config = QuantumCognitiveConfig()
    config.tesseract_enabled = True
    
    # Initialize core
    core = QuantumCognitiveCore(config)
    
    # Verify tesseract components are present
    assert core.tesseract_router is not None
    assert core.quantum_edge_scorer is not None
    assert core.tesseract_governance is not None
    
    # Process input
    input_data = torch.randn(1, config.encoder_input_dim)
    result = core.process_input(input_data)
    
    # Check that result contains tesseract information
    assert 'tesseract_vertex' in result
    assert 'router_info' in result
    assert result['tesseract_vertex'] is not None
    
    logger.info("Tesseract integration test passed!")
    print(f"Tesseract vertex: {result['tesseract_vertex']}")
    print(f"Router info: {result['router_info']['name']} (confidence: {result['router_info']['confidence']:.3f})")
    
    return result

def test_flat_routing():
    """Test flat routing (without tesseract)"""
    logger.info("Testing flat routing...")
    
    # Create configuration with tesseract disabled
    config = QuantumCognitiveConfig()
    config.tesseract_enabled = False
    
    # Initialize core
    core = QuantumCognitiveCore(config)
    
    # Verify tesseract components are not present
    assert core.tesseract_router is None
    assert core.quantum_edge_scorer is None
    assert core.tesseract_governance is None
    
    # Process input
    input_data = torch.randn(1, config.encoder_input_dim)
    result = core.process_input(input_data)
    
    # Check that result does not contain tesseract information
    assert 'tesseract_vertex' in result
    assert result['tesseract_vertex'] is None
    
    logger.info("Flat routing test passed!")
    print(f"Phi score: {result['phi_score']:.4f}")
    
    return result

if __name__ == "__main__":
    # Run tests
    tesseract_result = test_tesseract_integration()
    flat_result = test_flat_routing()
    
    print("\n" + "="*50)
    print("SIMPLE TESSERACT INTEGRATION TEST RESULTS")
    print("="*50)
    print(f"Tesseract vertex: {tesseract_result['tesseract_vertex']}")
    print(f"Router: {tesseract_result['router_info']['name']}")
    print(f"Phi score (tesseract): {tesseract_result['phi_score']:.4f}")
    print(f"Phi score (flat): {flat_result['phi_score']:.4f}")
    print("="*50)