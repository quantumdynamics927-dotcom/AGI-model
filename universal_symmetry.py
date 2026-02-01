"""Universal symmetry node: Hydrogen vs Opposition (Antihydrogen/Helium) decompression.

Provides `UniversalSymmetryNode` which returns Fibonacci/Lucas-unfolded resonance
and bond-angle parameters for a 1-bit state (0 or 1).
"""

from typing import Tuple

PHI = 1.618033988749895


class UniversalSymmetryNode:
    def __init__(self, phi: float = PHI):
        self.phi = float(phi)
        # Hydrogen Fibonacci scaling
        self.fib = [1, 1, 2, 3, 5]
        # Opposition (Antihydrogen/Helium) Lucas-like scaling
        self.lucas = [1, 3, 4, 7, 11]

    def decompress_thought(self, state_bit: int, target_amplitude: float = None) -> Tuple[float, float, list]:
        """Decompress a 1-bit `state_bit` into (resonance, bond_angle, scale_sequence).

        - state_bit == 0: Hydrogen ground-state template (Fibonacci)
        - state_bit == 1: Opposition template (Lucas / Helium-like)

        If `target_amplitude` is provided, the returned `resonance` will be
        scaled (preserving sign) so that abs(resonance) == target_amplitude.

        Returns:
            resonance: float (scalar unfolded resonance, possibly normalized)
            bond_angle: float (molecular bond angle representative)
            scale_sequence: list used for unfolding
        """
        s = int(state_bit)
        if s == 0:
            scale_sequence = self.fib
            bond_angle = 104.500
            base = 1.0
        else:
            scale_sequence = self.lucas
            # Use phi-conjugate scaling for bond angle as suggested
            bond_angle = 104.500 * (self.phi - 1.0)
            base = -1.0

        resonance = float(base)
        for f in scale_sequence:
            resonance = (resonance * float(f)) / self.phi

        raw_resonance = float(resonance)
        if target_amplitude is not None:
            try:
                target = float(target_amplitude)
                denom = max(abs(raw_resonance), 1e-12)
                scale = target / denom
                resonance = raw_resonance * scale
            except Exception:
                resonance = raw_resonance

        return float(resonance), float(bond_angle), list(scale_sequence)


if __name__ == '__main__':
    node = UniversalSymmetryNode()
    for bit in (0, 1):
        resonance, bond_angle, seq = node.decompress_thought(bit)
        print(f"State {bit}: resonance={resonance:.6f}, bond_angle={bond_angle:.3f}, seq={seq}")
