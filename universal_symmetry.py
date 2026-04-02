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
            "Perturbation | state=%d | idx=%s | delta=%+d | res=%.4f | stable=%s",
            state_bit, element_index, delta, perturbed_res, stable,
        )
    return results


# ---------------------------------------------------------------------------
# Three-Phase Sign Classification
# ---------------------------------------------------------------------------

def sign_phase(value: float, eps: float = 1e-12) -> str:
    """Classify a scalar as positive, zero, or negative.
    
    Args:
        value: The value to classify
        eps: Threshold for zero detection (default 1e-12)
        
    Returns:
        "positive", "zero", or "negative"
    """
    if abs(value) <= eps:
        return "zero"
    return "positive" if value > 0 else "negative"


def perturbation_probe(
    node: "UniversalSymmetryNode",
    state_bit: int,
    delta: int,
    element_index: str = "last",
    eps: float = 1e-12,
) -> dict:
    """Probe one perturbation and return full phase information.
    
    Args:
        node: UniversalSymmetryNode instance
        state_bit: 0 for Fibonacci, 1 for Lucas
        delta: Perturbation amount to add
        element_index: "first", "middle", or "last"
        eps: Threshold for zero detection
        
    Returns:
        Dictionary with base and perturbed resonance, phase classification,
        and flags for phase change, zero crossing, and sign flip.
    """
    base_seq = node.fib if state_bit == 0 else node.lucas
    base_res, _, _ = node.decompress_thought(state_bit)
    base_phase = sign_phase(base_res, eps=eps)

    seq = list(base_seq)
    if element_index == "last":
        idx = -1
    elif element_index == "first":
        idx = 0
    else:
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

    perturbed_phase = sign_phase(perturbed_res, eps=eps)

    return {
        "state_bit": state_bit,
        "delta": delta,
        "element_index": element_index,
        "base_resonance": base_res,
        "base_phase": base_phase,
        "perturbed_resonance": perturbed_res,
        "perturbed_phase": perturbed_phase,
        "phase_changed": perturbed_phase != base_phase,
        "zero_crossed": perturbed_phase == "zero",
        "sign_flipped": (
            base_phase in ("positive", "negative")
            and perturbed_phase in ("positive", "negative")
            and perturbed_phase != base_phase
        ),
        "mutated_sequence": seq,
    }


def sign_phase_analysis(
    node: "UniversalSymmetryNode",
    state_bit: int,
    element_index: str = "last",
    search_radius: int = 50,
    eps: float = 1e-12,
) -> dict:
    """Search for the earliest zero crossing or sign flip.
    
    Scans perturbations from -search_radius to +search_radius to find
    the first delta that causes zero crossing or sign flip.
    
    Args:
        node: UniversalSymmetryNode instance
        state_bit: 0 for Fibonacci, 1 for Lucas
        element_index: "first", "middle", or "last"
        search_radius: Range of deltas to test (default 50)
        eps: Threshold for zero detection
        
    Returns:
        Dictionary with first_zero, first_flip, and all trials.
    """
    trials = []
    first_zero = None
    first_flip = None

    for delta in range(-search_radius, search_radius + 1):
        probe = perturbation_probe(
            node=node,
            state_bit=state_bit,
            delta=delta,
            element_index=element_index,
            eps=eps,
        )
        trials.append(probe)

        if first_zero is None and probe["zero_crossed"]:
            first_zero = probe

        if first_flip is None and probe["sign_flipped"]:
            first_flip = probe

    return {
        "state_bit": state_bit,
        "element_index": element_index,
        "search_radius": search_radius,
        "first_zero": first_zero,
        "first_flip": first_flip,
        "trials": trials,
    }


def print_sign_phase_report(report: dict) -> None:
    """Print a formatted sign phase analysis report.
    
    Args:
        report: Dictionary from sign_phase_analysis()
    """
    state = report["state_bit"]
    loc = report["element_index"]
    print(f"\nSIGN PHASE REPORT | state={state} | location={loc}")

    if report["first_zero"] is None:
        print("  First zero : not found in search window")
    else:
        z = report["first_zero"]
        print(
            f"  First zero : delta={z['delta']:+d} | "
            f"resonance={z['perturbed_resonance']:.6f} | "
            f"seq={z['mutated_sequence']}"
        )

    if report["first_flip"] is None:
        print("  First flip : not found in search window")
    else:
        f = report["first_flip"]
        print(
            f"  First flip : delta={f['delta']:+d} | "
            f"resonance={f['perturbed_resonance']:.6f} | "
            f"seq={f['mutated_sequence']}"
        )


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
    print("SYMMETRY OPERATOR ANALYSIS  S[f] = Product(f[i]) / phi^n")
    print("=" * 60)
    for bit, label, seq in [(0, "Fibonacci", node.fib), (1, "Lucas", node.lucas)]:
        s_val = symmetry_operator(seq)
        sign_prefix = "+" if results[bit]["resonance"] >= 0 else "-"
        print(f"  {label:12s} | seq={seq} | S={sign_prefix}{abs(s_val):.4f}")

    print("\n" + "=" * 60)
    print("PERTURBATION ANALYSIS -- sign-flip robustness")
    print("=" * 60)
    deltas = [1, 2, 5, -1]
    locations = ["last", "first", "middle"]
    for bit, label in [(0, "Fibonacci"), (1, "Lucas")]:
        print(f"\n  State {bit} ({label})")
        for loc in locations:
            res_list = perturbation_analysis(node, bit, deltas, element_index=loc)
            for r in res_list:
                status = "[OK] Stable" if r["sign_stable"] else "[X] FLIPPED"
                print(
                    f"    delta={r['delta']:+d} at {r['element_index']:6s} | "
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

    # ========================================================================
    # Sign Phase Analysis (Three-Phase Classifier)
    # ========================================================================
    print("\n" + "=" * 60)
    print("SIGN PHASE ANALYSIS (Three-Phase: positive/zero/negative)")
    print("=" * 60)

    for bit, label in [(0, "Fibonacci"), (1, "Lucas")]:
        print(f"\nState {bit} ({label})")
        for loc in ["first", "middle", "last"]:
            report = sign_phase_analysis(
                node,
                state_bit=bit,
                element_index=loc,
                search_radius=20,
                eps=1e-12,
            )
            print_sign_phase_report(report)

    # ========================================================================
    # Phase Transition Summary
    # ========================================================================
    print("\n" + "=" * 60)
    print("PHASE TRANSITION SUMMARY")
    print("=" * 60)

    for bit, label in [(0, "Fibonacci"), (1, "Lucas")]:
        print(f"\n{label} Sequence:")
        base_res = results[bit]["resonance"]
        base_phase = sign_phase(base_res)
        print(f"  Base resonance: {base_res:+.6f} (phase: {base_phase})")

        for loc in ["first", "middle", "last"]:
            report = sign_phase_analysis(
                node,
                state_bit=bit,
                element_index=loc,
                search_radius=20,
                eps=1e-12,
            )

            # Find phase transitions
            transitions = []
            prev_phase = base_phase
            for t in report["trials"]:
                if t["perturbed_phase"] != prev_phase:
                    transitions.append((t["delta"], prev_phase, t["perturbed_phase"]))
                    prev_phase = t["perturbed_phase"]

            if transitions:
                print(f"  {loc:6s}: phase transitions at delta = ", end="")
                print(", ".join([f"{d:+d} ({p1}->{p2})" for d, p1, p2 in transitions[:3]]))
            else:
                print(f"  {loc:6s}: no phase transitions in search window")

    print()
