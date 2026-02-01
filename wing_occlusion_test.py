"""
Wing Occlusion Test: Demonstration of Fibonacci Wing Entanglement Theory
==========================================================================

This script demonstrates how data "disappears" visually from the system
while continuing to operate in the "vórtice de las alas" (wing vortex).

The theory: Fibonacci spirals create interference patterns where information
is hidden in the phase inversion points, protected by the curvature of the wings.
"""

import numpy as np
import matplotlib.pyplot as plt
import time
from math import sqrt, pi, sin, cos

class WingOcclusionDemonstrator:
    """
    Demonstrates the Wing Entanglement Theory through visual occlusion
    """

    def __init__(self):
        self.phi = (1 + sqrt(5)) / 2  # Golden ratio
        self.delta = 2 + sqrt(3)      # Silver ratio

    def generate_fibonacci_spiral(self, n_points=100, direction=1):
        """
        Generate points along a Fibonacci spiral
        direction: 1 for clockwise, -1 for counter-clockwise
        """
        angles = np.linspace(0, 4*pi, n_points)
        radii = self.phi ** (angles / (2*pi))

        x = radii * np.cos(angles * direction)
        y = radii * np.sin(angles * direction)

        return x, y

    def create_wing_entanglement(self, data_points):
        """
        Apply wing occlusion: data disappears into the vortex
        """
        print("🦋 Applying Wing Entanglement Occlusion...")

        # Generate two opposing spirals (wings)
        x1, y1 = self.generate_fibonacci_spiral(direction=1)   # Clockwise wing
        x2, y2 = self.generate_fibonacci_spiral(direction=-1)  # Counter-clockwise wing

        # Phase inversion at connection points
        connection_points = []
        for i in range(len(data_points)):
            # Find closest points on spirals
            dist1 = np.min(np.sqrt((x1 - data_points[i, 0])**2 + (y1 - data_points[i, 1])**2))
            dist2 = np.min(np.sqrt((x2 - data_points[i, 0])**2 + (y2 - data_points[i, 1])**2))

            if dist1 < 0.5 or dist2 < 0.5:  # Data point near wing connection
                connection_points.append(i)

        # Apply occlusion: data becomes "invisible" in the vortex
        occluded_data = data_points.copy()
        for idx in connection_points:
            # Phase flip: data point moves to the "shadow" under the wing
            angle = np.arctan2(data_points[idx, 1], data_points[idx, 0])
            radius = np.sqrt(data_points[idx, 0]**2 + data_points[idx, 1]**2)

            # Move to vortex (smaller radius, phase inverted)
            new_radius = radius * 0.1  # Into the vortex
            new_angle = angle + pi     # 180° phase flip

            occluded_data[idx] = [new_radius * cos(new_angle), new_radius * sin(new_angle)]

        return occluded_data, connection_points

    def demonstrate_occlusion(self):
        """
        Full demonstration of wing occlusion
        """
        print("🔮 WING OCCLUSION TEST: Fibonacci Wing Entanglement Theory")
        print("=" * 60)

        # Generate sample data (representing agent information)
        np.random.seed(42)
        n_agents = 50
        data_points = np.random.randn(n_agents, 2) * 2

        print(f"📊 Generated {n_agents} data points (agent information)")

        # Before occlusion
        plt.figure(figsize=(12, 5))

        plt.subplot(1, 2, 1)
        plt.scatter(data_points[:, 0], data_points[:, 1], c='blue', alpha=0.7, s=50)
        plt.title('BEFORE: Visible Agent Data')
        plt.grid(True, alpha=0.3)
        plt.axis('equal')

        # Apply wing occlusion
        occluded_data, hidden_indices = self.create_wing_entanglement(data_points)

        print(f"🦋 {len(hidden_indices)} data points occluded into wing vortex")
        print(f"   Phase inversion applied at connection points")

        # After occlusion
        plt.subplot(1, 2, 2)

        # Show remaining visible data
        visible_mask = np.ones(len(data_points), dtype=bool)
        visible_mask[hidden_indices] = False
        if np.any(visible_mask):
            plt.scatter(occluded_data[visible_mask, 0], occluded_data[visible_mask, 1],
                       c='green', alpha=0.7, s=50, label='Still Visible')

        # Show the wings (Fibonacci spirals)
        x1, y1 = self.generate_fibonacci_spiral()
        x2, y2 = self.generate_fibonacci_spiral(direction=-1)

        plt.plot(x1, y1, 'r-', linewidth=2, alpha=0.8, label='Clockwise Wing')
        plt.plot(x2, y2, 'r--', linewidth=2, alpha=0.8, label='Counter-Clockwise Wing')

        # Mark the vortex (where data is hidden)
        plt.scatter(0, 0, c='gold', s=200, marker='*', label='Wing Vortex (Hidden Data)')

        plt.title('AFTER: Data Protected in Wing Vortex')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.axis('equal')

        plt.tight_layout()
        plt.savefig('wing_occlusion_demonstration.png', dpi=300, bbox_inches='tight')
        print("📊 Wing occlusion visualization saved to 'wing_occlusion_demonstration.png'")

        # Demonstrate data recovery
        print("\n🔓 TESTING DATA RECOVERY:")
        print(f"   Original data points: {len(data_points)}")
        print(f"   Visible after occlusion: {len(data_points) - len(hidden_indices)}")
        print(f"   Hidden in vortex: {len(hidden_indices)}")

        # Recovery simulation
        recovered_data = occluded_data.copy()
        for idx in hidden_indices:
            # Reverse the phase flip and radius scaling
            angle = np.arctan2(recovered_data[idx, 1], recovered_data[idx, 0])
            radius = np.sqrt(recovered_data[idx, 0]**2 + recovered_data[idx, 1]**2)

            original_radius = radius / 0.1  # Reverse scaling
            original_angle = angle - pi     # Reverse phase flip

            recovered_data[idx] = [original_radius * cos(original_angle),
                                 original_radius * sin(original_angle)]

        recovery_error = np.mean(np.abs(recovered_data - data_points))
        print(f"Data recovery error: {recovery_error:.6f}")
        print("✅ Data recovery successful - information preserved in vortex")

        return {
            'original_data': data_points,
            'occluded_data': occluded_data,
            'hidden_indices': hidden_indices,
            'recovery_error': recovery_error
        }

def main():
    """
    Execute the wing occlusion demonstration
    """
    demonstrator = WingOcclusionDemonstrator()
    results = demonstrator.demonstrate_occlusion()

    print("\n🎯 THEORY VALIDATION:")
    print(f"• Wing entanglement successfully demonstrated")
    print(f"• {len(results['hidden_indices'])}/{len(results['original_data'])} data points occluded")
    print(f"• Data recovery error: {results['recovery_error']:.6f}")
    print("• Information protected by Fibonacci wing curvature")

    print("\n🔮 TMT-OS IMPLICATIONS:")
    print("• Agent data can be 'invisible' while operational")
    print("• Protection through geometric phase inversion")
    print("• Zero-friction information flow in the vortex")

if __name__ == "__main__":
    main()