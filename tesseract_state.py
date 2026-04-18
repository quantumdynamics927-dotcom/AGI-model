"""
Tesseract State Module

Defines the 4-dimensional hypercube state space for cognitive routing.
Each vertex represents a cognitive state or processing mode.
"""

import numpy as np
from typing import List, Tuple, Dict
from dataclasses import dataclass

@dataclass
class TesseractVertex:
    """Represents a vertex in the 4D tesseract cognitive space"""
    # 4-bit state: b3 b2 b1 b0
    state: int  # 0-15
    coordinates: Tuple[int, int, int, int]  # (b3, b2, b1, b0)
    name: str
    description: str
    family: str  # Grouping for semantic organization

class TesseractStateSpace:
    """4D hypercube state space for cognitive routing"""
    
    def __init__(self):
        # Define the 16 vertices of the tesseract
        self.vertices = self._create_vertices()
        self.adjacency_matrix = self._create_adjacency_matrix()
        
    def _create_vertices(self) -> Dict[int, TesseractVertex]:
        """Create all 16 vertices of the tesseract"""
        vertices = {}
        
        # Vertex definitions based on the 4 cognitive axes
        vertex_definitions = {
            # 0000-0011: Sensory/Perception preprocessing
            0: ("0000", "Sensory Input", "Raw sensory data intake and preprocessing", "Perception"),
            1: ("0001", "Feature Extraction", "Low-level feature detection from sensory input", "Perception"),
            2: ("0010", "Pattern Recognition", "Pattern matching and basic recognition", "Perception"),
            3: ("0011", "Sensor Fusion", "Combining multiple sensory inputs", "Perception"),
            
            # 0100-0111: World-model inference and latent compression
            4: ("0100", "World Model Init", "Initializing world model representation", "Abstraction"),
            5: ("0101", "Latent Encoding", "Compressing observations into latent space", "Abstraction"),
            6: ("0110", "Model Update", "Updating internal world model", "Abstraction"),
            7: ("0111", "Prediction", "Generating predictions from world model", "Abstraction"),
            
            # 1000-1011: Memory retrieval, synthesis, and cross-agent fusion
            8: ("1000", "Memory Recall", "Retrieving relevant memories", "Memory"),
            9: ("1001", "Memory Synthesis", "Creating new memories from experiences", "Memory"),
            10: ("1010", "Cross-Agent Fusion", "Integrating knowledge from multiple agents", "Memory"),
            11: ("1011", "Knowledge Integration", "Synthesizing knowledge across domains", "Memory"),
            
            # 1100-1111: Planning, policy selection, and action arbitration
            12: ("1100", "Goal Formation", "Setting objectives and subgoals", "Planning"),
            13: ("1101", "Policy Selection", "Choosing optimal policy for current state", "Planning"),
            14: ("1110", "Action Arbitration", "Deciding on specific actions to take", "Planning"),
            15: ("1111", "Execution Monitoring", "Monitoring action execution and feedback", "Planning")
        }
        
        for state, (binary, name, desc, family) in vertex_definitions.items():
            coordinates = tuple(int(bit) for bit in binary)
            vertices[state] = TesseractVertex(state, coordinates, name, desc, family)
            
        return vertices
        
    def _create_adjacency_matrix(self) -> np.ndarray:
        """Create adjacency matrix for the tesseract (4D hypercube)"""
        # In a 4D hypercube, two vertices are adjacent if they differ by exactly one bit
        adj_matrix = np.zeros((16, 16), dtype=bool)
        
        for i in range(16):
            for j in range(16):
                # Count differing bits
                xor_result = i ^ j
                bit_count = bin(xor_result).count('1')
                # Adjacent if exactly one bit differs
                if bit_count == 1:
                    adj_matrix[i, j] = True
                    
        return adj_matrix
        
    def get_neighbors(self, vertex: int) -> List[int]:
        """Get all neighboring vertices of a given vertex"""
        if vertex < 0 or vertex >= 16:
            raise ValueError("Vertex must be between 0 and 15")
            
        neighbors = []
        for i in range(16):
            if self.adjacency_matrix[vertex, i]:
                neighbors.append(i)
                
        return neighbors
        
    def get_vertex_info(self, vertex: int) -> TesseractVertex:
        """Get information about a specific vertex"""
        if vertex not in self.vertices:
            raise ValueError(f"Vertex {vertex} not found")
        return self.vertices[vertex]
        
    def get_axis_description(self, axis: int) -> str:
        """Get description of a cognitive axis"""
        axes = {
            0: "Perception <-> Abstraction",
            1: "Exploitation <-> Exploration",
            2: "Local Memory <-> Global Memory",
            3: "Classical Routing <-> Quantum Routing"
        }
        return axes.get(axis, "Unknown Axis")
        
    def vertex_to_coordinates(self, vertex: int) -> Tuple[int, int, int, int]:
        """Convert vertex number to 4D coordinates"""
        if vertex < 0 or vertex >= 16:
            raise ValueError("Vertex must be between 0 and 15")
            
        binary = format(vertex, '04b')
        return tuple(int(bit) for bit in binary)
        
    def coordinates_to_vertex(self, coordinates: Tuple[int, int, int, int]) -> int:
        """Convert 4D coordinates to vertex number"""
        if len(coordinates) != 4:
            raise ValueError("Coordinates must be 4-dimensional")
            
        # Check that all coordinates are 0 or 1
        for coord in coordinates:
            if coord not in [0, 1]:
                raise ValueError("Coordinates must be binary (0 or 1)")
                
        # Convert binary to decimal
        vertex = 0
        for i, coord in enumerate(coordinates):
            vertex += coord * (2 ** (3 - i))
            
        return vertex

# Example usage
if __name__ == "__main__":
    tesseract = TesseractStateSpace()
    
    # Show all vertices
    print("Tesseract Vertices:")
    for i in range(16):
        vertex = tesseract.get_vertex_info(i)
        coords = ''.join(map(str, vertex.coordinates))
        print(f"  {i:2d} ({coords}): {vertex.name} [{vertex.family}]")
        
    # Show adjacency for a few vertices
    print("\nAdjacency Examples:")
    for vertex_id in [0, 5, 10, 15]:
        neighbors = tesseract.get_neighbors(vertex_id)
        vertex = tesseract.get_vertex_info(vertex_id)
        print(f"  {vertex_id} ({''.join(map(str, vertex.coordinates))} - {vertex.name}): {neighbors}")