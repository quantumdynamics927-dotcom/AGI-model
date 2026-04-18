"""
Tesseract Router Module

Implements the cognitive routing mechanism using a 4D hypercube topology.
Routes between cognitive states based on latent representations and contextual priorities.
"""

import torch
import torch.nn as nn
import numpy as np
from typing import List, Tuple, Dict, Optional
import logging

from tesseract_state import TesseractStateSpace, TesseractVertex

logger = logging.getLogger(__name__)

class TesseractRouter(nn.Module):
    """Cognitive router using 4D hypercube topology"""
    
    def __init__(self, latent_dim: int = 32):
        super().__init__()
        self.latent_dim = latent_dim
        self.state_space = TesseractStateSpace()
        
        # Neural network to map latent space to vertex probabilities
        self.vertex_encoder = nn.Sequential(
            nn.Linear(latent_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 16),  # 16 outputs for 16 vertices
            nn.Softmax(dim=-1)  # Probability distribution over vertices
        )
        
        # Fault mask for degraded components
        self.fault_mask = np.ones(16, dtype=bool)  # Initially all vertices available
        
    def encode_state(self, z: torch.Tensor) -> torch.Tensor:
        """
        Map latent vector to probability distribution over tesseract vertices.
        
        Args:
            z: Latent vector from encoder (batch_size, latent_dim)
            
        Returns:
            Vertex probabilities (batch_size, 16)
        """
        if z.dim() == 1:
            z = z.unsqueeze(0)  # Add batch dimension
            
        # Ensure correct dimensionality
        if z.shape[-1] != self.latent_dim:
            raise ValueError(f"Expected latent dimension {self.latent_dim}, got {z.shape[-1]}")
            
        # Encode to vertex probabilities
        vertex_probs = self.vertex_encoder(z)
        return vertex_probs
        
    def candidate_vertices(self, current_vertex: int) -> List[int]:
        """
        Get candidate vertices for transition from current vertex.
        Includes current vertex and all adjacent vertices.
        
        Args:
            current_vertex: Current vertex ID (0-15)
            
        Returns:
            List of candidate vertex IDs
        """
        if current_vertex < 0 or current_vertex >= 16:
            raise ValueError("Vertex must be between 0 and 15")
            
        # Get neighbors
        neighbors = self.state_space.get_neighbors(current_vertex)
        
        # Include current vertex as candidate
        candidates = [current_vertex] + neighbors
        
        # Apply fault mask - remove unavailable vertices
        filtered_candidates = [v for v in candidates if self.fault_mask[v]]
        
        return filtered_candidates
        
    def transition_weights(self, current_vertex: int, candidates: List[int], 
                          phi_prior: bool = True) -> Dict[int, float]:
        """
        Compute transition weights for candidate vertices.
        
        Args:
            current_vertex: Current vertex ID
            candidates: List of candidate vertex IDs
            phi_prior: Whether to apply phi-based weighting
            
        Returns:
            Dictionary mapping vertex IDs to weights
        """
        weights = {}
        
        # Base weights - equal probability for all candidates
        base_weight = 1.0 / len(candidates) if candidates else 0.0
        
        for vertex in candidates:
            weight = base_weight
            
            # Apply phi prior if requested
            if phi_prior and vertex != current_vertex:
                # Phi weighting favors transitions that maintain or increase coherence
                # This is a simplified implementation - in practice, this would use
                # actual phi calculations from the IIT analyzer
                phi_score = self._compute_phi_affinity(current_vertex, vertex)
                weight *= phi_score
                
            weights[vertex] = weight
            
        # Normalize weights
        total_weight = sum(weights.values())
        if total_weight > 0:
            weights = {k: v/total_weight for k, v in weights.items()}
            
        return weights
        
    def _compute_phi_affinity(self, from_vertex: int, to_vertex: int) -> float:
        """
        Compute phi-based affinity between two vertices.
        This is a simplified heuristic - in practice, this would use actual
        integrated information calculations.
        """
        # Simple heuristic: prefer transitions that change fewer axes
        from_coords = self.state_space.vertex_to_coordinates(from_vertex)
        to_coords = self.state_space.vertex_to_coordinates(to_vertex)
        
        # Count differing coordinates
        differences = sum(1 for a, b in zip(from_coords, to_coords) if a != b)
        
        # Prefer single-axis changes (adjacent vertices)
        if differences == 0:
            return 1.0  # Stay in same vertex
        elif differences == 1:
            return 0.8  # Adjacent vertex
        else:
            return 0.3  # Multi-axis change (less preferred)
            
    def apply_fault_mask(self, weights: Dict[int, float], 
                        system_health: Dict[str, float]) -> Dict[int, float]:
        """
        Apply fault mask to transition weights based on system health.
        
        Args:
            weights: Current transition weights
            system_health: Health status of system components
            
        Returns:
            Updated weights with fault penalties applied
        """
        # In a real implementation, this would check specific components
        # associated with each vertex and apply penalties accordingly
        
        # For now, we'll simulate some random degradation
        updated_weights = weights.copy()
        
        for vertex in weights:
            # Apply penalty based on fault mask
            if not self.fault_mask[vertex]:
                updated_weights[vertex] *= 0.1  # Heavy penalty for faulty vertices
                
        # Renormalize
        total_weight = sum(updated_weights.values())
        if total_weight > 0:
            updated_weights = {k: v/total_weight for k, v in updated_weights.items()}
            
        return updated_weights
        
    def update_fault_mask(self, degraded_vertices: List[int]):
        """
        Update fault mask to mark degraded vertices.
        
        Args:
            degraded_vertices: List of vertex IDs that are currently degraded
        """
        # Reset fault mask
        self.fault_mask = np.ones(16, dtype=bool)
        
        # Mark degraded vertices
        for vertex in degraded_vertices:
            if 0 <= vertex < 16:
                self.fault_mask[vertex] = False
                
        logger.info(f"Updated fault mask: {np.sum(~self.fault_mask)} vertices marked as degraded")
        
    def get_current_vertex_info(self, vertex_probs: torch.Tensor) -> Dict:
        """
        Get information about the current vertex based on probabilities.
        
        Args:
            vertex_probs: Probability distribution over vertices (16,)
            
        Returns:
            Dictionary with vertex information
        """
        # Get most likely vertex
        current_vertex = torch.argmax(vertex_probs).item()
        
        # Get vertex info
        vertex_info = self.state_space.get_vertex_info(current_vertex)
        
        return {
            'vertex_id': current_vertex,
            'coordinates': vertex_info.coordinates,
            'name': vertex_info.name,
            'family': vertex_info.family,
            'confidence': vertex_probs[current_vertex].item(),
            'top_candidates': self._get_top_candidates(vertex_probs)
        }
        
    def _get_top_candidates(self, vertex_probs: torch.Tensor, k: int = 3) -> List[Dict]:
        """
        Get top k candidate vertices with their probabilities.
        
        Args:
            vertex_probs: Probability distribution over vertices
            k: Number of top candidates to return
            
        Returns:
            List of candidate information dictionaries
        """
        # Get top k indices
        top_indices = torch.topk(vertex_probs, k).indices.tolist()
        
        candidates = []
        for idx in top_indices:
            vertex_info = self.state_space.get_vertex_info(idx)
            candidates.append({
                'vertex_id': idx,
                'name': vertex_info.name,
                'probability': vertex_probs[idx].item()
            })
            
        return candidates

# Example usage
if __name__ == "__main__":
    # Create router
    router = TesseractRouter(latent_dim=32)
    
    # Example latent vector
    z = torch.randn(1, 32)
    
    # Encode state
    vertex_probs = router.encode_state(z)
    print(f"Vertex probabilities shape: {vertex_probs.shape}")
    
    # Get current vertex info
    current_info = router.get_current_vertex_info(vertex_probs.squeeze())
    print(f"Current vertex: {current_info['vertex_id']} ({current_info['name']})")
    print(f"Confidence: {current_info['confidence']:.3f}")
    
    # Get candidates
    candidates = router.candidate_vertices(current_info['vertex_id'])
    print(f"Candidate vertices: {candidates}")
    
    # Compute transition weights
    weights = router.transition_weights(current_info['vertex_id'], candidates)
    print(f"Transition weights: {weights}")