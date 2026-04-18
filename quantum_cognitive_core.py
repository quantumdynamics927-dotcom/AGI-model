"""
Quantum Cognitive Core: Hybrid Quantum-Classical Reasoning System with Tesseract Routing

This module implements a focused hybrid quantum-classical cognitive core that:
1. Encodes world models using classical neural networks
2. Routes cognition through a 4D tesseract topology
3. Scores transitions using quantum circuits
4. Integrates memory and learning across both substrates
5. Provides policy control for agentic behavior

The system uses a tesseract-based router for structured, interpretable cognition
while maintaining the benefits of hybrid quantum-classical processing.
"""

import torch
import torch.nn as nn
import numpy as np
import time
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from vae_model import QuantumVAE
from utils.iit_metrics import IITAnalyzer
import logging

# Tesseract modules
from tesseract_router import TesseractRouter
from tesseract_transition_scorer import QuantumEdgeScorer
from tesseract_governance import TesseractGovernance, RouteStep

logger = logging.getLogger(__name__)

@dataclass
class QuantumCognitiveConfig:
    """Configuration for the Quantum Cognitive Core"""
    # Classical encoder settings
    encoder_input_dim: int = 128
    encoder_hidden_dims: list = None
    encoder_latent_dim: int = 32
    
    # Quantum kernel settings
    quantum_qubits: int = 32
    quantum_layers: int = 8
    quantum_ansatz: str = "hardware_efficient"
    
    # Tesseract router settings
    tesseract_enabled: bool = True
    tesseract_latent_dim: int = 32
    
    # Integration settings
    memory_size: int = 1000
    policy_hidden_dims: list = None
    
    def __post_init__(self):
        if self.encoder_hidden_dims is None:
            self.encoder_hidden_dims = [64, 32]
        if self.policy_hidden_dims is None:
            self.policy_hidden_dims = [64, 32]

class ClassicalWorldModelEncoder(nn.Module):
    """Classical neural network encoder for world model representation"""
    
    def __init__(self, config: QuantumCognitiveConfig):
        super().__init__()
        self.config = config
        
        # Build encoder layers
        encoder_layers = []
        prev_dim = config.encoder_input_dim
        for hidden_dim in config.encoder_hidden_dims:
            encoder_layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.ReLU(),
                nn.LayerNorm(hidden_dim)
            ])
            prev_dim = hidden_dim
            
        encoder_layers.append(nn.Linear(prev_dim, config.encoder_latent_dim))
        self.encoder = nn.Sequential(*encoder_layers)
        
        # Output normalization
        self.output_norm = nn.LayerNorm(config.encoder_latent_dim)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Encode input to latent representation"""
        encoded = self.encoder(x)
        return self.output_norm(encoded)

class QuantumReasoningKernel:
    """Quantum kernel for reasoning in compressed latent spaces"""
    
    def __init__(self, config: QuantumCognitiveConfig):
        self.config = config
        # Use fewer qubits to avoid memory issues
        self.qubits = min(config.quantum_qubits, 8)
        self.layers = min(config.quantum_layers, 2)
        self.ansatz = config.quantum_ansatz
        
        # Initialize quantum simulator or hardware connection
        self._initialize_quantum_backend()
        
    def _initialize_quantum_backend(self):
        """Initialize quantum backend (simulator or hardware)"""
        try:
            from qiskit import QuantumCircuit, QuantumRegister
            from qiskit_aer import AerSimulator
            
            # Create quantum register and circuit
            self.qr = QuantumRegister(self.qubits)
            self.qc = QuantumCircuit(self.qr)
            
            # Initialize simulator
            self.backend = AerSimulator()
            logger.info("Initialized quantum simulator backend")
            
        except ImportError:
            logger.warning("Qiskit not available, using classical approximation")
            self.backend = None
            
    def process_latent_state(self, latent_vector: np.ndarray) -> np.ndarray:
        """Process latent state using quantum circuits"""
        if self.backend is None:
            # Classical approximation when quantum backend unavailable
            return self._classical_approximation(latent_vector)
            
        # Prepare quantum circuit with latent vector as parameters
        circuit = self._build_reasoning_circuit(latent_vector)
        
        # Execute on backend
        try:
            job = self.backend.run(circuit, shots=1024)
            result = job.result()
            counts = result.get_counts(circuit)
            
            # Convert counts to output vector
            return self._counts_to_vector(counts)
        except Exception as e:
            logger.warning(f"Quantum execution failed: {e}, falling back to classical")
            return self._classical_approximation(latent_vector)
            
    def _build_reasoning_circuit(self, latent_vector: np.ndarray) -> 'QuantumCircuit':
        """Build quantum circuit for reasoning with latent input"""
        from qiskit import QuantumCircuit
        
        # Use fewer qubits to avoid memory issues
        effective_qubits = min(self.qubits, 8)  # Limit to 8 qubits
        
        # Normalize latent vector to parameter range
        normalized_params = np.arctan(latent_vector) * 2
        
        # Create new quantum register and circuit with limited qubits
        from qiskit import QuantumRegister
        qr = QuantumRegister(effective_qubits)
        qc = QuantumCircuit(qr)
        
        # Encode latent vector as rotation angles
        for i, param in enumerate(normalized_params[:effective_qubits]):
            # Ensure param is a scalar value, not an array
            if isinstance(param, np.ndarray):
                param = float(param.item()) if param.ndim == 0 else float(param[0])
            qc.ry(float(param), i)
            
        # Add variational layers (reduce number of layers)
        layers = min(self.layers, 2)  # Limit to 2 layers
        for layer in range(layers):
            # Entangling layer
            for i in range(0, effective_qubits - 1, 2):
                qc.cx(i, i + 1)
            for i in range(1, effective_qubits - 1, 2):
                qc.cx(i, i + 1)
                
            # Rotation layer
            for i in range(effective_qubits):
                param = normalized_params[(layer * effective_qubits + i) % len(normalized_params)]
                # Ensure param is a scalar value
                if isinstance(param, np.ndarray):
                    param = float(param.item()) if param.ndim == 0 else float(param[0])
                qc.ry(float(param), i)
                
        # Measurement
        qc.measure_all()
        
        return qc
        
    def _classical_approximation(self, latent_vector: np.ndarray) -> np.ndarray:
        """Classical approximation of quantum reasoning"""
        # Simple transformation to simulate quantum effects
        transformed = np.sin(latent_vector) * np.cos(latent_vector[::-1])
        return transformed / np.linalg.norm(transformed)

    def _counts_to_vector(self, counts: dict) -> np.ndarray:
        """Convert measurement counts to output vector"""
        # Convert bitstrings to integers and create probability distribution
        prob_dict = {}
        total_shots = sum(counts.values())
        
        for bitstring, count in counts.items():
            # Convert bitstring to integer index
            idx = int(bitstring[::-1], 2)  # Reverse for little-endian
            prob_dict[idx] = count / total_shots
            
        # Create output vector
        output_vector = np.zeros(2**self.qubits)
        for idx, prob in prob_dict.items():
            if idx < len(output_vector):
                output_vector[idx] = prob
                
        return output_vector[:self.config.encoder_latent_dim]  # Match latent dimension

class MemoryIntegrationLayer:
    """Memory and integration layer for the cognitive core"""
    
    def __init__(self, config: QuantumCognitiveConfig):
        self.config = config
        self.memory_size = config.memory_size
        self.latent_dim = config.encoder_latent_dim
        
        # Initialize memory buffer
        self.memory_buffer = np.zeros((self.memory_size, self.latent_dim))
        self.memory_ptr = 0
        self.memory_filled = False
        
    def store_experience(self, latent_state: np.ndarray, reward: float = 0.0):
        """Store latent state in memory buffer"""
        self.memory_buffer[self.memory_ptr] = latent_state
        self.memory_ptr = (self.memory_ptr + 1) % self.memory_size
        if self.memory_ptr == 0:
            self.memory_filled = True
            
    def retrieve_relevant_memories(self, query_state: np.ndarray, k: int = 5) -> np.ndarray:
        """Retrieve k most relevant memories based on cosine similarity"""
        if not self.memory_filled and self.memory_ptr == 0:
            return np.zeros((0, self.latent_dim))
            
        # Calculate similarities
        if self.memory_filled:
            memory_used = self.memory_size
        else:
            memory_used = self.memory_ptr
            
        memories = self.memory_buffer[:memory_used]
        
        # Normalize vectors for cosine similarity
        query_norm = query_state / (np.linalg.norm(query_state) + 1e-8)
        memories_norm = memories / (np.linalg.norm(memories, axis=1, keepdims=True) + 1e-8)
        
        # Calculate similarities (ensure proper dimensions)
        if query_norm.ndim == 1:
            query_norm = query_norm.reshape(-1, 1)
        if memories_norm.ndim == 1:
            memories_norm = memories_norm.reshape(1, -1)
            
        # Calculate similarities using proper matrix multiplication
        similarities = np.dot(memories_norm, query_norm).flatten()
        
        # Get top-k indices
        k = min(k, len(similarities))
        top_k_indices = np.argpartition(similarities, -k)[-k:]
        
        return memories[top_k_indices]

class AgentPolicyController(nn.Module):
    """Agent policy controller for decision making"""
    
    def __init__(self, config: QuantumCognitiveConfig):
        super().__init__()
        self.config = config
        
        # Build policy network
        policy_layers = []
        prev_dim = config.encoder_latent_dim * 2  # State + memories
        
        for hidden_dim in config.policy_hidden_dims:
            policy_layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.ReLU(),
                nn.Dropout(0.1)
            ])
            prev_dim = hidden_dim
            
        policy_layers.append(nn.Linear(prev_dim, config.encoder_latent_dim))  # Action output
        self.policy_network = nn.Sequential(*policy_layers)
        
        # Value head for policy evaluation
        self.value_head = nn.Sequential(
            nn.Linear(config.encoder_latent_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 1)
        )
        
    def forward(self, state: torch.Tensor, memories: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward pass to get action and value"""
        # Concatenate state and memories
        if memories.size(0) == 0:
            # No memories, use zero padding
            memories = torch.zeros_like(state)
        else:
            # Average memories
            memories = torch.mean(memories, dim=0, keepdim=True)
            
        combined_input = torch.cat([state, memories], dim=-1)
        
        # Get action
        action = self.policy_network(combined_input)
        
        # Get value
        value = self.value_head(action)
        
        return action, value

class QuantumCognitiveCore:
    """Main Quantum Cognitive Core class integrating all components"""
    
    def __init__(self, config: QuantumCognitiveConfig = None):
        self.config = config or QuantumCognitiveConfig()
        
        # Initialize components
        self.encoder = ClassicalWorldModelEncoder(self.config)
        self.quantum_kernel = QuantumReasoningKernel(self.config)
        self.memory_layer = MemoryIntegrationLayer(self.config)
        self.policy_controller = AgentPolicyController(self.config)
        
        # Initialize tesseract components if enabled
        if self.config.tesseract_enabled:
            self.tesseract_router = TesseractRouter(self.config.tesseract_latent_dim)
            self.quantum_edge_scorer = QuantumEdgeScorer(self.config.tesseract_latent_dim)
            self.tesseract_governance = TesseractGovernance()
        else:
            self.tesseract_router = None
            self.quantum_edge_scorer = None
            self.tesseract_governance = None
        
        # IIT metrics for consciousness tracking
        self.iit_metrics = IITAnalyzer()
        
        logger.info("Initialized Quantum Cognitive Core" + 
                   (" with Tesseract Router" if self.config.tesseract_enabled else ""))
        
    def process_input(self, input_data: torch.Tensor, current_vertex: int = 0) -> Dict[str, Any]:
        """Process input through the full cognitive pipeline with tesseract routing"""
        # Start governance session if enabled
        session_id = None
        if self.tesseract_governance:
            session_id = self.tesseract_governance.start_route_session()
            
        try:
            # Encode input to latent space
            latent_state = self.encoder(input_data)
            
            # Tesseract routing if enabled
            if self.config.tesseract_enabled and self.tesseract_router:
                # Route through tesseract topology
                vertex_probs = self.tesseract_router.encode_state(latent_state)
                router_info = self.tesseract_router.get_current_vertex_info(vertex_probs.squeeze())
                
                # Get candidate vertices
                candidates = self.tesseract_router.candidate_vertices(router_info['vertex_id'])
                
                # Score transitions with quantum edge scorer
                if self.quantum_edge_scorer:
                    transition_scores = self.quantum_edge_scorer.score_edges(
                        latent_state, router_info['vertex_id'], candidates
                    )
                else:
                    transition_scores = {v: 0.5 for v in candidates}
                
                # Log route step
                if self.tesseract_governance:
                    route_step = RouteStep(
                        timestamp=time.time(),
                        vertex_id=router_info['vertex_id'],
                        vertex_name=router_info['name'],
                        confidence=router_info['confidence'],
                        latency_ms=0.0,  # Would be measured in real implementation
                        transition_score=max(transition_scores.values()) if transition_scores else 0.5,
                        quantum_score=transition_scores.get(router_info['vertex_id'], 0.5)
                    )
                    self.tesseract_governance.log_route_step(route_step)
                    
                # Use the best candidate vertex for processing
                best_vertex = max(transition_scores, key=transition_scores.get)
                logger.info(f"Tesseract routing: {router_info['vertex_id']} -> {best_vertex}")
                
            else:
                # Classic processing without tesseract routing
                best_vertex = current_vertex
                
            # Convert to numpy for quantum processing
            latent_np = latent_state.detach().cpu().numpy()
            
            # Process with quantum kernel
            quantum_processed = self.quantum_kernel.process_latent_state(latent_np)
            
            # Store in memory
            self.memory_layer.store_experience(quantum_processed)
            
            # Retrieve relevant memories
            memories = self.memory_layer.retrieve_relevant_memories(quantum_processed)
            memories_tensor = torch.from_numpy(memories).float()
            
            # Get policy action
            # Ensure quantum_processed is 2D for the policy controller
            if quantum_processed.ndim == 1:
                quantum_processed = quantum_processed.reshape(1, -1)
                
            action, value = self.policy_controller(
                torch.from_numpy(quantum_processed).float(), 
                memories_tensor
            )
            
            # Calculate consciousness metrics
            phi_result = self.iit_metrics.compute_phi(quantum_processed.reshape(1, -1))
            phi_score = phi_result.get('phi', 0.0)
            
            # End governance session
            if self.tesseract_governance and session_id:
                self.tesseract_governance.end_route_session(success=True)
            
            return {
                'latent_state': latent_state,
                'quantum_processed': quantum_processed,
                'memories': memories,
                'action': action,
                'value': value,
                'phi_score': phi_score,
                'tesseract_vertex': best_vertex if self.config.tesseract_enabled else None,
                'router_info': router_info if self.config.tesseract_enabled else None
            }
            
        except Exception as e:
            # End governance session with error
            if self.tesseract_governance and session_id:
                self.tesseract_governance.end_route_session(success=False, error=str(e))
            raise
        
    def benchmark_comparison(self, input_data: torch.Tensor) -> Dict[str, Any]:
        """Compare quantum vs classical processing for benchmarking"""
        # Classical-only processing
        latent_state = self.encoder(input_data)
        classical_action, classical_value = self.policy_controller(
            latent_state, torch.zeros_like(latent_state).unsqueeze(0)
        )
        
        # Quantum-enhanced processing
        full_result = self.process_input(input_data)
        
        return {
            'classical_only': {
                'action': classical_action,
                'value': classical_value
            },
            'quantum_enhanced': full_result
        }

# Example usage
if __name__ == "__main__":
    # Create configuration
    config = QuantumCognitiveConfig()
    
    # Initialize core
    core = QuantumCognitiveCore(config)
    
    # Example input
    input_data = torch.randn(1, config.encoder_input_dim)
    
    # Process input
    result = core.process_input(input_data)
    
    print("Quantum Cognitive Core processing complete")
    print(f"Phi score: {result['phi_score']:.4f}")
    print(f"Action shape: {result['action'].shape}")