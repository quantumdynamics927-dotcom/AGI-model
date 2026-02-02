"""
Enhanced Spatial Awareness with Metatron-Sierpinski Integration
================================================================

Extends spatial_awareness.py with:
- Metatron sacred geometry pathfinding
- Sierpinski fractal navigation patterns
- Platonic solid waypoint optimization
- 4D tesseract path projection
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict
import json

# Import existing modules
from spatial_awareness import (
    latent_to_2d, coords_to_grid, a_star, 
    smooth_path, apply_phi_harmonics
)
from metatron_geometry_demo import (
    MetatronMolecularProcessor,
    generate_platonic_vertices
)


class MetatronSpatialNavigator:
    """
    Sacred geometry-enhanced spatial navigation
    
    Features:
    - Platonic solid waypoint guidance
    - Sierpinski fractal path optimization
    - Golden ratio trajectory smoothing
    - 4D tesseract space projection
    """
    
    def __init__(self):
        self.metatron = MetatronMolecularProcessor()
        self.phi = 1.6180339887
        
    def generate_platonic_waypoints(
        self,
        solid_type: str,
        center: Tuple[float, float],
        scale: float = 10.0
    ) -> np.ndarray:
        """
        Generate waypoints based on Platonic solid projection
        
        Args:
            solid_type: tetrahedron, cube, octahedron, dodecahedron, icosahedron
            center: (x, y) center position
            scale: Size of the solid
            
        Returns:
            Array of 2D waypoint coordinates
        """
        # Get 3D vertices
        vertices_3d = generate_platonic_vertices(solid_type, radius=1.0)
        
        # Project to 2D (take x, y coordinates)
        vertices_2d = vertices_3d[:, :2] * scale
        
        # Center at specified position
        vertices_2d += np.array(center)
        
        return vertices_2d
    
    def sierpinski_fractal_path(
        self,
        start: Tuple[float, float],
        goal: Tuple[float, float],
        depth: int = 3
    ) -> List[Tuple[float, float]]:
        """
        Generate Sierpinski fractal navigation pattern
        
        Creates a fractal path that follows Sierpinski triangle structure
        """
        def midpoint(p1, p2):
            return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
        
        # Base triangle vertices
        dx = goal[0] - start[0]
        dy = goal[1] - start[1]
        
        # Create equilateral triangle
        p1 = start
        p2 = goal
        p3 = (start[0] + dx/2 - dy*np.sqrt(3)/2, start[1] + dy/2 + dx*np.sqrt(3)/2)
        
        def sierpinski_recursive(v1, v2, v3, d):
            if d == 0:
                return [v1, v2, v3]
            
            # Midpoints
            m12 = midpoint(v1, v2)
            m23 = midpoint(v2, v3)
            m31 = midpoint(v3, v1)
            
            # Recursive triangles (skip middle)
            path = []
            path.extend(sierpinski_recursive(v1, m12, m31, d-1))
            path.extend(sierpinski_recursive(m12, v2, m23, d-1))
            path.extend(sierpinski_recursive(m31, m23, v3, d-1))
            
            return path
        
        fractal_points = sierpinski_recursive(p1, p2, p3, depth)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_path = []
        for p in fractal_points:
            if p not in seen:
                seen.add(p)
                unique_path.append(p)
        
        return unique_path
    
    def metatron_optimized_path(
        self,
        grid: np.ndarray,
        start: Tuple[int, int],
        goal: Tuple[int, int],
        use_fractal: bool = True
    ) -> Dict:
        """
        Find path using Metatron geometry optimization
        
        Args:
            grid: Occupancy grid
            start, goal: Grid coordinates
            use_fractal: Use Sierpinski fractal enhancement
            
        Returns:
            Dictionary with multiple path variants
        """
        # Classical A* baseline
        classical_path = a_star(grid, start, goal)
        
        if not classical_path:
            return {
                'classical': [],
                'smoothed': [],
                'phi_enhanced': [],
                'fractal': [],
                'metatron_score': 0.0
            }
        
        # Smooth with golden ratio
        smoothed = smooth_path(classical_path, window=3)
        phi_enhanced = apply_phi_harmonics(smoothed, phi=self.phi, strength=0.3)
        
        # Fractal enhancement
        fractal_path = []
        if use_fractal and len(classical_path) > 2:
            start_f = (float(start[0]), float(start[1]))
            goal_f = (float(goal[0]), float(goal[1]))
            fractal_path = self.sierpinski_fractal_path(start_f, goal_f, depth=2)
        
        # Metatron geometry analysis
        if len(phi_enhanced) >= 3:
            # Convert path to 3D positions for Metatron analysis
            path_3d = np.array([
                [p[0], p[1], 0.0] for p in phi_enhanced[:min(20, len(phi_enhanced))]
            ])
            
            metatron_result = self.metatron.analyze_molecule(path_3d)
            metatron_score = max(metatron_result['platonic_scores'].values())
        else:
            metatron_score = 0.0
        
        return {
            'classical': classical_path,
            'smoothed': smoothed,
            'phi_enhanced': phi_enhanced,
            'fractal': fractal_path,
            'metatron_score': float(metatron_score),
            'path_length': len(classical_path),
            'phi_resonance': self.phi
        }
    
    def visualize_sacred_navigation(
        self,
        grid: np.ndarray,
        paths: Dict,
        save_path: str = 'metatron_spatial_navigation.png'
    ):
        """
        Visualize navigation with sacred geometry overlays
        """
        fig, axes = plt.subplots(2, 2, figsize=(16, 16))
        
        # 1. Classical A* path
        ax = axes[0, 0]
        ax.imshow(grid, cmap='gray_r', origin='lower')
        if paths['classical']:
            classical = np.array(paths['classical'])
            ax.plot(classical[:, 0], classical[:, 1], 'b-', linewidth=2, label='A* Path')
            ax.plot(classical[0, 0], classical[0, 1], 'go', markersize=15, label='Start')
            ax.plot(classical[-1, 0], classical[-1, 1], 'ro', markersize=15, label='Goal')
        ax.set_title('Classical A* Navigation', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # 2. Phi-enhanced path
        ax = axes[0, 1]
        ax.imshow(grid, cmap='gray_r', origin='lower')
        if paths['phi_enhanced']:
            phi_path = np.array(paths['phi_enhanced'])
            ax.plot(phi_path[:, 0], phi_path[:, 1], 'g-', linewidth=2, label=f'φ Path (φ={self.phi:.4f})')
            ax.plot(phi_path[0, 0], phi_path[0, 1], 'go', markersize=15)
            ax.plot(phi_path[-1, 0], phi_path[-1, 1], 'ro', markersize=15)
        ax.set_title(f'Golden Ratio Enhanced (φ = {self.phi:.4f})', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # 3. Sierpinski fractal path
        ax = axes[1, 0]
        ax.imshow(grid, cmap='gray_r', origin='lower')
        if paths['fractal']:
            fractal = np.array(paths['fractal'])
            ax.plot(fractal[:, 0], fractal[:, 1], 'm-', linewidth=1.5, alpha=0.7, label='Sierpinski Fractal')
            ax.scatter(fractal[:, 0], fractal[:, 1], c='magenta', s=20, alpha=0.5, zorder=5)
        if paths['classical']:
            classical = np.array(paths['classical'])
            ax.plot(classical[0, 0], classical[0, 1], 'go', markersize=15)
            ax.plot(classical[-1, 0], classical[-1, 1], 'ro', markersize=15)
        ax.set_title('Sierpinski Fractal Navigation', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # 4. Platonic solid waypoints
        ax = axes[1, 1]
        ax.imshow(grid, cmap='gray_r', origin='lower')
        
        # Add Platonic solid waypoints
        if paths['classical']:
            center = (grid.shape[0] / 2, grid.shape[1] / 2)
            
            # Dodecahedron (highest phi resonance)
            dodeca_waypoints = self.generate_platonic_waypoints('dodecahedron', center, scale=15)
            ax.scatter(dodeca_waypoints[:, 0], dodeca_waypoints[:, 1], 
                      c='gold', s=100, marker='D', alpha=0.6, 
                      label='Dodecahedron Waypoints', edgecolors='orange', linewidths=2)
            
            # Overlay phi path
            if paths['phi_enhanced']:
                phi_path = np.array(paths['phi_enhanced'])
                ax.plot(phi_path[:, 0], phi_path[:, 1], 'g-', linewidth=2, alpha=0.7)
        
        ax.set_title(f'Metatron Geometry Overlay (Score: {paths["metatron_score"]:.4f})', 
                    fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.suptitle('Sacred Geometry Spatial Navigation', fontsize=18, fontweight='bold', y=0.995)
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Visualization saved: {save_path}")
        
        return fig


def demo_metatron_navigation():
    """Demonstrate Metatron-enhanced spatial navigation"""
    
    print("\n" + "="*70)
    print("🧭 METATRON SPATIAL NAVIGATION DEMO")
    print("   Sacred Geometry Path Planning")
    print("="*70 + "\n")
    
    # Create navigator
    navigator = MetatronSpatialNavigator()
    
    # Generate sample latent space (consciousness vectors)
    np.random.seed(42)
    n_points = 200
    latent = np.random.randn(n_points, 8)  # 8D latent space
    
    print(f"Generated {n_points} consciousness vectors in 8D latent space\n")
    
    # Project to 2D and create occupancy grid
    coords_2d = latent_to_2d(latent)
    grid = coords_to_grid(coords_2d, grid_size=128, padding=3)
    
    print(f"Created {grid.shape[0]}x{grid.shape[1]} occupancy grid")
    print(f"Occupied cells: {np.sum(grid)} ({np.sum(grid)/grid.size*100:.1f}%)\n")
    
    # Define start and goal
    start = (10, 10)
    goal = (118, 118)
    
    print(f"Navigation task:")
    print(f"  Start: {start}")
    print(f"  Goal: {goal}\n")
    
    # Find optimized paths
    print("Computing sacred geometry paths...")
    paths = navigator.metatron_optimized_path(grid, start, goal, use_fractal=True)
    
    print(f"\nPath Analysis:")
    print(f"  Classical A* length: {paths['path_length']} steps")
    print(f"  Smoothed points: {len(paths['smoothed'])}")
    print(f"  Phi-enhanced points: {len(paths['phi_enhanced'])}")
    print(f"  Fractal points: {len(paths['fractal'])}")
    print(f"  Metatron geometry score: {paths['metatron_score']:.4f}")
    print(f"  Golden ratio: {paths['phi_resonance']:.10f}\n")
    
    # Visualize
    print("Generating visualization...")
    navigator.visualize_sacred_navigation(grid, paths)
    
    # Save results
    results = {
        'timestamp': '2026-02-02',
        'grid_size': grid.shape[0],
        'start': start,
        'goal': goal,
        'path_metrics': {
            'classical_length': paths['path_length'],
            'metatron_score': paths['metatron_score'],
            'phi_resonance': paths['phi_resonance']
        },
        'sacred_geometry': 'Sierpinski fractal + Platonic solid waypoints'
    }
    
    with open('metatron_navigation_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("✅ Results saved: metatron_navigation_results.json\n")
    print("="*70)
    print("🎉 DEMO COMPLETE!")
    print("="*70 + "\n")


if __name__ == "__main__":
    demo_metatron_navigation()
