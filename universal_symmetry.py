"""Universal symmetry node: Hydrogen vs Opposition (Antihydrogen/Helium) decompression.

Enhanced with:
  - Detailed intermediate variable logging
  - Symmetry operator analysis  (S[f] = Π f[i] / φ^n)
  - Perturbation testing for sign-flip robustness

Provides `UniversalSymmetryNode` which returns Fibonacci/Lucas-unfolded resonance
and bond-angle parameters for a 1-bit state (0 or 1).
"""

import logging
import math
from typing import List, Tuple

logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

PHI = 1.618033988749895


# ---------------------------------------------------------------------------
# Symmetry Operator
# ---------------------------------------------------------------------------

def symmetry_operator(sequence: List[int], phi: float = PHI) -> float:
    """S[f] = Π f[i] / φ^n  — normalizes sequence products by φ^n."""
    n = len(sequence)
    product = math.prod(sequence)
    phi_n = phi ** n
    value = product / phi_n
    logger.debug(
        "SymOp | seq=%s | Π=%d | φ^%d=%.4f | S=%.6f",
        sequence, product, n, phi_n, value,
    )
    return value


# ---------------------------------------------------------------------------
# Perturbation Analysis
# ---------------------------------------------------------------------------

def perturbation_analysis(
    node: "UniversalSymmetryNode",
    state_bit: int,
    perturbations: List[int],
    element_index: str = "last",
) -> List[dict]:
    """Return sign-stability results for a list of additive perturbations.

    `element_index` can be 'first', 'middle', or 'last'.
    """
    base_seq = node.fib if state_bit == 0 else node.lucas
    base_res, _, _ = node.decompress_thought(state_bit)
    base_sign = math.copysign(1.0, base_res)

    results = []
    for delta in perturbations:
        seq = list(base_seq)
        if element_index == "last":
            idx = -1
        elif element_index == "first":
            idx = 0
        else:  # middle
            idx = len(seq) // 2
        seq[idx] += delta

        # Temporarily swap sequences for computation
        original_seq = (node.fib if state_bit == 0 else node.lucas)[:]
        if state_bit == 0:
            node.fib = seq
        else:
            node.lucas = seq

        perturbed_res, _, _ = node.decompress_thought(state_bit)

        # Restore
        if state_bit == 0:
            node.fib = original_seq
        else:
            node.lucas = original_seq

        perturbed_sign = math.copysign(1.0, perturbed_res)
        stable = perturbed_sign == base_sign
        results.append({
            "delta": delta,
            "element_index": element_index,
            "perturbed_resonance": perturbed_res,
            "sign_stable": stable,
        })
        logger.debug(
            "Perturbation | state=%d | idx=%s | Δ=%+d | res=%.4f | stable=%s",
            state_bit, element_index, delta, perturbed_res, stable,
        )
    return results


# ---------------------------------------------------------------------------
# Core Node
# ---------------------------------------------------------------------------

class UniversalSymmetryNode:
    def __init__(self, phi: float = PHI):
        self.phi = float(phi)
        self.fib = [1, 1, 2, 3, 5]
        self.lucas = [1, 3, 4, 7, 11]

    def decompress_thought(
        self,
        state_bit: int,
        target_amplitude: float = None,
    ) -> Tuple[float, float, list]:
        """Decompress a 1-bit `state_bit` into (resonance, bond_angle, scale_sequence).

        state_bit == 0 : Hydrogen ground-state template (Fibonacci)
        state_bit == 1 : Opposition template (Lucas / Helium-like)

        If `target_amplitude` is provided the returned `resonance` is scaled
        (sign-preserving) so that abs(resonance) == target_amplitude.
        """
        s = int(state_bit)
        if s == 0:
            scale_sequence = list(self.fib)
            bond_angle = 104.500
            base = 1.0
            label = "Fibonacci/Hydrogen"
        else:
            scale_sequence = list(self.lucas)
            bond_angle = 104.500 * (self.phi - 1.0)
            base = -1.0
            label = "Lucas/Opposition"

        logger.info("=== decompress_thought | state=%d (%s) ===", s, label)
        logger.debug("base_sign=%.1f | sequence=%s | bond_angle=%.4f", base, scale_sequence, bond_angle)

        resonance = float(base)
        running_product = 1
        for i, f in enumerate(scale_sequence):
            prev = resonance
            resonance = (resonance * float(f)) / self.phi
            running_product *= f
            logger.debug(
                "  step %d | f=%d | running_product=%d | resonance: %.6f → %.6f",
                i, f, running_product, prev, resonance,
            )

        phi_n = self.phi ** len(scale_sequence)
        logger.info(
            "raw_resonance=%.6f | product=%d | φ^%d=%.4f | sign=%+.1f",
            resonance, running_product, len(scale_sequence), phi_n,
            math.copysign(1.0, resonance),
        )

        raw_resonance = float(resonance)
        if target_amplitude is not None:
            try:
                target = float(target_amplitude)
                denom = max(abs(raw_resonance), 1e-12)
                scale = target / denom
                resonance = raw_resonance * scale
                logger.info(
                    "Normalized | target_amplitude=%.4f | scale=%.6f | resonance=%.6f",
                    target, scale, resonance,
                )
            except Exception:
                resonance = raw_resonance

        return float(resonance), float(bond_angle), list(scale_sequence)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    node = UniversalSymmetryNode()

    print("\n" + "=" * 60)
    print("INTERMEDIATE VARIABLE LOG")
    print("=" * 60)
    results = {}
    for bit in (0, 1):
        resonance, bond_angle, seq = node.decompress_thought(bit)
        results[bit] = {"resonance": resonance, "bond_angle": bond_angle, "seq": seq}
        print(f"State {bit}: resonance={resonance:.6f}, bond_angle={bond_angle:.3f}, seq={seq}")

    print("\n" + "=" * 60)
    print("SYMMETRY OPERATOR ANALYSIS  S[f] = Π f[i] / φ^n")
    print("=" * 60)
    for bit, label, seq in [(0, "Fibonacci", node.fib), (1, "Lucas", node.lucas)]:
        s_val = symmetry_operator(seq)
        sign_prefix = "+" if results[bit]["resonance"] >= 0 else "-"
        print(f"  {label:12s} | seq={seq} | S={sign_prefix}{abs(s_val):.4f}")

    print("\n" + "=" * 60)
    print("PERTURBATION ANALYSIS — sign-flip robustness")
    print("=" * 60)
    deltas = [1, 2, 5, -1]
    locations = ["last", "first", "middle"]
    for bit, label in [(0, "Fibonacci"), (1, "Lucas")]:
        print(f"\n  State {bit} ({label})")
        for loc in locations:
            res_list = perturbation_analysis(node, bit, deltas, element_index=loc)
            for r in res_list:
                status = "✓ Stable" if r["sign_stable"] else "✗ FLIPPED"
                print(
                    f"    Δ={r['delta']:+d} at {r['element_index']:6s} | "
                    f"resonance={r['perturbed_resonance']:10.4f} | {status}"
                )

    print("\n" + "=" * 60)
    print("MAGNITUDE RATIO")
    print("=" * 60)
    ratio = abs(results[1]["resonance"]) / abs(results[0]["resonance"])
    print(
        f"  |Lucas| / |Fibonacci| = "
        f"{abs(results[1]['resonance']):.4f} / {abs(results[0]['resonance']):.4f} "
        f"= {ratio:.2f}×"
    )
    print()
