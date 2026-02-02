"""
Metatron Molecular Geometry Demonstration
==========================================

Standalone demonstration of Platonic solid geometry and 4D tesseract concepts
for molecular processing (NumPy-only implementation).

Date: February 1, 2026
Author: Quantum Dynamics
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import json

# Constants
PHI = 1.618033988749895  # Golden ratio
PHI_INV = 1 / PHI


def generate_platonic_vertices(solid_name, radius=1.0):
    """Generate vertex coordinates for Platonic solids"""
    
    if solid_name == 'tetrahedron':
        vertices = np.array([
            [1, 1, 1],
            [1, -1, -1],
            [-1, 1, -1],
            [-1, -1, 1]
        ], dtype=np.float32)
        
    elif solid_name == 'cube':
        vertices = np.array([
            [1, 1, 1], [1, 1, -1], [1, -1, 1], [1, -1, -1],
            [-1, 1, 1], [-1, 1, -1], [-1, -1, 1], [-1, -1, -1]
        ], dtype=np.float32)
        
    elif solid_name == 'octahedron':
        vertices = np.array([
            [1, 0, 0], [-1, 0, 0],
            [0, 1, 0], [0, -1, 0],
            [0, 0, 1], [0, 0, -1]
        ], dtype=np.float32)
        
    elif solid_name == 'dodecahedron':
        vertices = []
        # (±1, ±1, ±1)
        for i in [-1, 1]:
            for j in [-1, 1]:
                for k in [-1, 1]:
                    vertices.append([i, j, k])
        # (0, ±φ, ±1/φ)
        for i in [-1, 1]:
            for j in [-1, 1]:
                vertices.append([0, i * PHI, j * PHI_INV])
        # (±1/φ, 0, ±φ)
        for i in [-1, 1]:
            for j in [-1, 1]:
                vertices.append([i * PHI_INV, 0, j * PHI])
        # (±φ, ±1/φ, 0)
        for i in [-1, 1]:
            for j in [-1, 1]:
                vertices.append([i * PHI, j * PHI_INV, 0])
        vertices = np.array(vertices, dtype=np.float32)
        
    elif solid_name == 'icosahedron':
        vertices = []
        # (0, ±1, ±φ)
        for i in [-1, 1]:
            for j in [-1, 1]:
                vertices.append([0, i, j * PHI])
        # (±1, ±φ, 0)
        for i in [-1, 1]:
            for j in [-1, 1]:
                vertices.append([i, j * PHI, 0])
        # (±φ, 0, ±1)
        for i in [-1, 1]:
            for j in [-1, 1]:
                vertices.append([i * PHI, 0, j])
        vertices = np.array(vertices, dtype=np.float32)
        
    else:
        raise ValueError(f"Unknown Platonic solid: {solid_name}")
    
    # Normalize to specified radius
    current_radius = np.linalg.norm(vertices[0])
    vertices = vertices * (radius / current_radius)
    
    return vertices


def generate_tesseract_vertices_4d(radius=1.0):
    """Generate 4D tesseract (hypercube) vertices"""
    vertices = []
    for i in [-1, 1]:
        for j in [-1, 1]:
            for k in [-1, 1]:
                for l in [-1, 1]:
                    vertices.append([i, j, k, l])
    
    vertices = np.array(vertices, dtype=np.float32)
    current_radius = np.linalg.norm(vertices[0])
    vertices = vertices * (radius / current_radius)
    
    return vertices


def project_4d_to_3d(vertices_4d, angle_w=0.0):
    """
    Project 4D vertices to 3D using perspective projection.
    
    Args:
        vertices_4d: [N, 4] array
        angle_w: Rotation angle in 4D (w-axis)
        
    Returns:
        [N, 3] projected coordinates
    """
    # Apply 4D rotation in xy-w plane
    cos_w = np.cos(angle_w)
    sin_w = np.sin(angle_w)
    
    rotated = vertices_4d.copy()
    x, w = vertices_4d[:, 0], vertices_4d[:, 3]
    rotated[:, 0] = x * cos_w - w * sin_w
    rotated[:, 3] = x * sin_w + w * cos_w
    
    # Perspective projection (camera at w = -4)
    camera_distance = 4.0
    scale = camera_distance / (camera_distance - rotated[:, 3])
    
    projected_3d = rotated[:, :3] * scale[:, np.newaxis]
    
    return projected_3d


def compute_geometric_ratios(vertices):
    """Compute ratios between distances (for Platonic analysis)"""
    N = len(vertices)
    distances = []
    
    for i in range(N):
        for j in range(i+1, N):
            dist = np.linalg.norm(vertices[i] - vertices[j])
            distances.append(dist)
    
    distances = np.array(sorted(set(np.round(distances, 4))))
    
    if len(distances) > 1:
        ratios = distances[1:] / distances[:-1]
        return distances, ratios
    else:
        return distances, np.array([])


def visualize_platonic_solids(save_path='platonic_solids_demo.png'):
    """Create visualization of all 5 Platonic solids"""
    fig = plt.figure(figsize=(20, 8))
    
    solids = ['tetrahedron', 'cube', 'octahedron', 'dodecahedron', 'icosahedron']
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
    
    for idx, (solid, color) in enumerate(zip(solids, colors)):
        ax = fig.add_subplot(2, 5, idx + 1, projection='3d')
        
        # Generate vertices
        vertices = generate_platonic_vertices(solid)
        
        # Plot vertices
        ax.scatter(vertices[:, 0], vertices[:, 1], vertices[:, 2],
                  c=color, s=100, alpha=0.8, edgecolors='black')
        
        # Draw edges (simplified - connect nearest neighbors)
        N = len(vertices)
        for i in range(N):
            dists = np.linalg.norm(vertices - vertices[i], axis=1)
            nearest = np.argsort(dists)[1:4]  # 3 nearest neighbors
            for j in nearest:
                ax.plot([vertices[i, 0], vertices[j, 0]],
                       [vertices[i, 1], vertices[j, 1]],
                       [vertices[i, 2], vertices[j, 2]],
                       c=color, alpha=0.4, linewidth=1.5)
        
        ax.set_title(f'{solid.capitalize()}\n({len(vertices)} vertices)',
                    fontsize=12, fontweight='bold')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_xlim([-2, 2])
        ax.set_ylim([-2, 2])
        ax.set_zlim([-2, 2])
        
        # Compute geometric ratios
        ax2 = fig.add_subplot(2, 5, idx + 6)
        distances, ratios = compute_geometric_ratios(vertices)
        
        if len(ratios) > 0:
            ax2.bar(range(len(ratios)), ratios, color=color, alpha=0.7)
            ax2.axhline(y=PHI, color='gold', linestyle='--', linewidth=2, 
                       label=f'φ = {PHI:.3f}')
            ax2.axhline(y=np.sqrt(2), color='silver', linestyle='--', linewidth=2,
                       label=f'√2 = {np.sqrt(2):.3f}')
            ax2.set_title('Geometric Ratios', fontsize=10)
            ax2.set_ylabel('Ratio')
            ax2.set_xlabel('Index')
            ax2.legend(fontsize=8)
            ax2.grid(alpha=0.3)
    
    plt.suptitle('Platonic Solids & Geometric Ratios\n(Metatron Molecular Processor Foundation)',
                fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"✅ Saved Platonic solids visualization: {save_path}")
    
    return fig


def visualize_4d_tesseract(save_path='tesseract_4d_projection.png'):
    """Visualize 4D tesseract with rotating projection"""
    fig = plt.figure(figsize=(18, 6))
    
    tesseract_verts = generate_tesseract_vertices_4d()
    
    # Three different rotation angles
    angles = [0, np.pi/6, np.pi/3]
    
    for idx, angle in enumerate(angles):
        ax = fig.add_subplot(1, 3, idx + 1, projection='3d')
        
        # Project to 3D
        projected = project_4d_to_3d(tesseract_verts, angle_w=angle)
        
        # Plot vertices
        ax.scatter(projected[:, 0], projected[:, 1], projected[:, 2],
                  c='#9D4EDD', s=150, alpha=0.9, edgecolors='black', linewidth=2)
        
        # Connect edges (tesseract has 32 edges)
        # Simplified: connect vertices that differ in only one 4D coordinate
        for i in range(16):
            for j in range(i+1, 16):
                diff = np.abs(tesseract_verts[i] - tesseract_verts[j])
                # Count how many coordinates differ
                if np.sum(diff > 0.1) == 1:  # Exactly one coordinate differs
                    ax.plot([projected[i, 0], projected[j, 0]],
                           [projected[i, 1], projected[j, 1]],
                           [projected[i, 2], projected[j, 2]],
                           c='#9D4EDD', alpha=0.3, linewidth=2)
        
        ax.set_title(f'4D Tesseract Projection\n(rotation = {angle:.2f} rad)',
                    fontsize=12, fontweight='bold')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.view_init(elev=20, azim=45 + idx*30)
    
    plt.suptitle('4D Tesseract → 3D Projection (Hyperdimensional Molecular Embedding)',
                fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"✅ Saved tesseract visualization: {save_path}")
    
    return fig


def analyze_molecular_geometry_example():
    """Demonstrate Metatron processor concept on benzene molecule"""
    print("\n" + "="*70)
    print("🧬 Molecular Geometry Analysis: Benzene (C6H6)")
    print("="*70)
    
    # Benzene ring (6 carbons in hexagonal geometry)
    N_carbons = 6
    angles = np.linspace(0, 2*np.pi, N_carbons, endpoint=False)
    carbon_positions = np.stack([
        1.4 * np.cos(angles),  # 1.4 Å is C-C bond length
        1.4 * np.sin(angles),
        np.zeros(N_carbons)
    ], axis=1)
    
    print(f"\n📍 Carbon positions (Angstroms):")
    for i, pos in enumerate(carbon_positions):
        print(f"   C{i+1}: [{pos[0]:6.3f}, {pos[1]:6.3f}, {pos[2]:6.3f}]")
    
    # Compute alignment with each Platonic solid
    print(f"\n🔮 Platonic Solid Alignment Scores:")
    print(f"   {'Solid':<15} {'Vertices':<10} {'Score':<10} {'Ratio Match'}")
    print(f"   {'-'*55}")
    
    alignments = {}
    
    for solid in ['tetrahedron', 'cube', 'octahedron', 'dodecahedron', 'icosahedron']:
        template = generate_platonic_vertices(solid, radius=1.4)
        
        # Simplified alignment: average distance to nearest template point
        min_dists = []
        for carbon in carbon_positions:
            dists = np.linalg.norm(template - carbon, axis=1)
            min_dists.append(np.min(dists))
        
        alignment_score = np.exp(-np.mean(min_dists))
        alignments[solid] = alignment_score
        
        # Check geometric ratio match
        _, ratios = compute_geometric_ratios(carbon_positions)
        if solid in ['dodecahedron', 'icosahedron']:
            ratio_target = PHI
            ratio_name = "φ"
        elif solid in ['tetrahedron', 'octahedron']:
            ratio_target = np.sqrt(2)
            ratio_name = "√2"
        else:
            ratio_target = 1.0
            ratio_name = "1"
        
        if len(ratios) > 0:
            ratio_match = f"{ratio_name} ({ratio_target:.3f})"
        else:
            ratio_match = "N/A"
        
        print(f"   {solid:<15} {len(template):<10} {alignment_score:6.4f}    {ratio_match}")
    
    # Best match
    best_solid = max(alignments, key=alignments.get)
    print(f"\n   ✨ Best match: {best_solid.upper()} (score = {alignments[best_solid]:.4f})")
    
    # 4D projection demonstration
    print(f"\n🌀 4D Tesseract Projection:")
    
    # Pad carbons to 4D (add quantum coherence axis)
    carbon_4d = np.hstack([
        carbon_positions,
        np.random.randn(N_carbons, 1) * 0.2  # Random 4th dimension
    ])
    
    print(f"   3D positions → 4D embedding:")
    for i, (pos_3d, pos_4d) in enumerate(zip(carbon_positions, carbon_4d)):
        print(f"   C{i+1}: [{pos_3d[0]:6.3f}, {pos_3d[1]:6.3f}, {pos_3d[2]:6.3f}] "
              f"→ [..., w={pos_4d[3]:6.3f}]")
    
    # Hyperradius in 4D
    hyperradii = np.linalg.norm(carbon_4d, axis=1)
    print(f"\n   Hyperradii (4D distance from origin):")
    print(f"   Mean: {np.mean(hyperradii):.3f} Å")
    print(f"   Std:  {np.std(hyperradii):.3f} Å")
    
    print("\n" + "="*70)
    
    return carbon_positions, carbon_4d, alignments


def generate_research_summary():
    """Generate JSON summary of geometric properties"""
    summary = {
        "date": "2026-02-01",
        "project": "Metatron Molecular Geometry Processor",
        "platonic_solids": {},
        "tesseract_4d": {},
        "benzene_analysis": {}
    }
    
    # Platonic solids
    for solid in ['tetrahedron', 'cube', 'octahedron', 'dodecahedron', 'icosahedron']:
        vertices = generate_platonic_vertices(solid)
        distances, ratios = compute_geometric_ratios(vertices)
        
        summary["platonic_solids"][solid] = {
            "vertices": int(len(vertices)),
            "unique_distances": distances.tolist() if len(distances) > 0 else [],
            "geometric_ratios": ratios.tolist() if len(ratios) > 0 else [],
            "phi_proximity": float(np.min(np.abs(ratios - PHI))) if len(ratios) > 0 else None
        }
    
    # Tesseract
    tesseract = generate_tesseract_vertices_4d()
    summary["tesseract_4d"] = {
        "vertices": int(len(tesseract)),
        "hyperradius": float(np.linalg.norm(tesseract[0])),
        "dimension": 4,
        "edges": 32,
        "faces": 24,
        "cells": 8
    }
    
    # Save summary
    with open('metatron_geometry_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("✅ Saved research summary: metatron_geometry_summary.json")
    
    return summary


class MetatronMolecularProcessor:
    """Simple wrapper class for benchmark compatibility"""
    
    def __init__(self):
        self.phi = PHI
    
    def analyze_molecule(self, positions):
        """Analyze molecular geometry using Platonic solids"""
        N = len(positions)
        
        # Center the molecule
        center = positions.mean(axis=0)
        centered = positions - center
        
        # Compute Platonic solid alignments
        platonic_scores = {}
        for solid in ['tetrahedron', 'cube', 'octahedron', 'dodecahedron', 'icosahedron']:
            template = generate_platonic_vertices(solid, radius=1.0)
            
            # Simple alignment score based on distance matching
            if len(template) >= N:
                # Use subset of template
                dists = []
                for i in range(N):
                    min_dist = np.min(np.linalg.norm(centered[i] - template, axis=1))
                    dists.append(min_dist)
                score = np.exp(-np.mean(dists))
            else:
                # Template too small
                score = 0.1
            
            platonic_scores[solid] = float(score)
        
        # 4D tesseract projection
        tesseract_4d = np.hstack([
            centered,
            np.random.randn(N, 1) * 0.2
        ])
        
        # Compute 4D symmetry
        hyperradii = np.linalg.norm(tesseract_4d, axis=1)
        tesseract_symmetry = 1.0 - (np.std(hyperradii) / (np.mean(hyperradii) + 1e-8))
        
        # Phi resonance
        _, ratios = compute_geometric_ratios(centered)
        if len(ratios) > 0:
            phi_proximity = np.min(np.abs(ratios - self.phi))
            phi_resonance = float(np.exp(-phi_proximity))
        else:
            phi_resonance = 0.5
        
        return {
            'platonic_scores': platonic_scores,
            'tesseract_4d': tesseract_4d,
            'tesseract_symmetry': float(tesseract_symmetry),
            'phi_resonance': phi_resonance
        }


def main():
    """Main demonstration"""
    print("\n" + "="*70)
    print("🌟 METATRON MOLECULAR GEOMETRY PROCESSOR")
    print("   Sacred Geometry-Driven 4D Molecular Modeling")
    print("="*70)
    
    print("\n📐 Part 1: Platonic Solids Foundation")
    print("-" * 70)
    visualize_platonic_solids()
    
    print("\n🔷 Part 2: 4D Tesseract Hypercube")
    print("-" * 70)
    visualize_4d_tesseract()
    
    print("\n🧬 Part 3: Molecular Geometry Analysis")
    print("-" * 70)
    carbon_3d, carbon_4d, alignments = analyze_molecular_geometry_example()
    
    print("\n📊 Part 4: Research Summary")
    print("-" * 70)
    summary = generate_research_summary()
    
    print("\n" + "="*70)
    print("✨ DEMONSTRATION COMPLETE")
    print("="*70)
    print("\nGenerated files:")
    print("  • platonic_solids_demo.png")
    print("  • tesseract_4d_projection.png")
    print("  • metatron_geometry_summary.json")
    print("\nNext steps:")
    print("  1. Implement full PyTorch version (metatron_molecular_processor.py)")
    print("  2. Benchmark on QM9 and MD17 datasets")
    print("  3. Validate φ emergence in trained models")
    print("  4. Publish results as arXiv preprint")
    print("\n🚀 Ready for consciousness-aware molecular modeling!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
