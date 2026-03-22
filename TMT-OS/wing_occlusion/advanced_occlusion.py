import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

PHI = 1.618033988749895
DELTA = 2 + np.sqrt(3)


class WingOcclusionDemonstrator:
    def __init__(self):
        self.phi = PHI
        self.delta = DELTA
        self.last_vortex_scale = 0.1

    def validate_golden_ratio(self, tolerance: float = 1e-9) -> bool:
        return abs(self.phi - PHI) <= tolerance

    def generate_fibonacci_spiral(self, n_points: int = 100, direction: int = 1):
        angles = np.linspace(0, 4 * np.pi, n_points)
        radii = self.phi ** (angles / (2 * np.pi))
        x = radii * np.cos(angles * direction)
        y = radii * np.sin(angles * direction)
        return x, y

    def create_wing_entanglement(self, data_points: np.ndarray, vortex_threshold: float = 0.5, vortex_scale: float = 0.1):
        data_points = np.asarray(data_points, dtype=float)
        self.last_vortex_scale = float(vortex_scale)
        if data_points.size == 0:
            return data_points.reshape(0, 2), []

        x1, y1 = self.generate_fibonacci_spiral(direction=1)
        x2, y2 = self.generate_fibonacci_spiral(direction=-1)
        s1 = np.column_stack([x1, y1])
        s2 = np.column_stack([x2, y2])

        d1 = np.linalg.norm(data_points[:, None, :] - s1[None, :, :], axis=2).min(axis=1)
        d2 = np.linalg.norm(data_points[:, None, :] - s2[None, :, :], axis=2).min(axis=1)
        hidden_mask = (d1 < vortex_threshold) | (d2 < vortex_threshold)
        hidden_indices = np.flatnonzero(hidden_mask).tolist()

        occluded = data_points.copy()
        if hidden_indices:
            idx = np.array(hidden_indices)
            angles = np.arctan2(occluded[idx, 1], occluded[idx, 0]) + np.pi
            radii = np.linalg.norm(occluded[idx], axis=1) * vortex_scale
            occluded[idx, 0] = radii * np.cos(angles)
            occluded[idx, 1] = radii * np.sin(angles)

        return occluded, hidden_indices

    def preserve_quantum_state(self, original: np.ndarray, transformed: np.ndarray) -> float:
        a = np.asarray(original, dtype=float)
        b = np.asarray(transformed, dtype=float)
        if a.shape != b.shape:
            return 0.0
        an = np.linalg.norm(a)
        bn = np.linalg.norm(b)
        if an == 0.0 and bn == 0.0:
            return 1.0
        if an == 0.0 or bn == 0.0:
            return 0.0
        fidelity = float(abs(np.vdot(a.reshape(-1), b.reshape(-1))) / (an * bn))
        return float(np.clip(fidelity, 0.0, 1.0))

    def demonstrate_occlusion(self, n_agents: int = 50, save_path: str | None = None):
        original = np.random.randn(n_agents, 2) * 2
        occluded, hidden_indices = self.create_wing_entanglement(original)

        recovered = occluded.copy()
        if hidden_indices:
            idx = np.array(hidden_indices)
            angles = np.arctan2(recovered[idx, 1], recovered[idx, 0]) - np.pi
            denom = self.last_vortex_scale if self.last_vortex_scale != 0 else 0.1
            radii = np.linalg.norm(recovered[idx], axis=1) / denom
            recovered[idx, 0] = radii * np.cos(angles)
            recovered[idx, 1] = radii * np.sin(angles)

        recovery_error = float(np.mean(np.abs(recovered - original)))
        fidelity = self.preserve_quantum_state(original, occluded)
        occlusion_rate = len(hidden_indices) / n_agents if n_agents else 0.0

        if save_path:
            x1, y1 = self.generate_fibonacci_spiral(direction=1)
            x2, y2 = self.generate_fibonacci_spiral(direction=-1)
            fig, ax = plt.subplots(figsize=(6, 6))
            ax.scatter(occluded[:, 0], occluded[:, 1], s=8, alpha=0.7)
            ax.plot(x1, y1, 'r-', alpha=0.5)
            ax.plot(x2, y2, 'r--', alpha=0.5)
            ax.set_aspect('equal', adjustable='box')
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close(fig)

        return {
            'original_data': original,
            'occluded_data': occluded,
            'hidden_indices': hidden_indices,
            'recovery_error': recovery_error,
            'preservation_fidelity': fidelity,
            'phi': self.phi,
            'n_agents': n_agents,
            'occlusion_rate': occlusion_rate,
        }
