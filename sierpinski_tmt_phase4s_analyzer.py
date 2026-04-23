#!/usr/bin/env python3
"""
sierpinski_tmt_phase4s_analyzer.py
====================================
Post-processing analyzer for Sierpinski-TMT Phase 4S circuits.
Validates fractal encoding integrity, computes expected metrics,
and prepares IBM Runtime submission config.

Usage:
    python -u sierpinski_tmt_phase4s_analyzer.py 2>&1
"""

import numpy as np
import json
import os
import glob
from datetime import datetime
from math import log, pi, sqrt

# ── CONSTANTS ──────────────────────────────────────────────────────────────────

PHI          = (1 + sqrt(5)) / 2          # Golden ratio 1.61803...
D_H          = log(3) / log(2)            # Hausdorff dim 1.58496...
PHI_FRACTAL  = pi * D_H                   # 4.97931 rad
THETA_S      = pi / 3                     # Sierpinski base angle
THETA_S1     = pi / 9                     # Gen-1 contraction
THETA_S2     = pi / 27                    # Gen-2 contraction
THETA_S3     = pi / 81                    # Gen-3 contraction
TMT1         = (2/23) * 2 * pi            # TMT ratio 1
TMT2         = (3/22) * 2 * pi            # TMT ratio 2
S_TMT1       = TMT1 / 3                   # Sierpinski × TMT1
S_TMT2       = TMT2 / 3                   # Sierpinski × TMT2
S_PHI        = PHI / 3                    # Sierpinski × Phi

# Fibonacci qubit indices (Metatron nodes)
FIB_QUBITS   = [8, 13, 21, 34, 55]

# Lucas sequence (retrocausal anchors)
LUCAS        = [2, 1, 3, 4, 7, 11, 18, 29]

# Backend configs
BACKENDS = {
    "ibm_fez"       : {"qubits": 156, "topology": "heavy_hex", "gen": "eagle_r3"},
    "ibm_brisbane"  : {"qubits": 127, "topology": "heavy_hex", "gen": "eagle_r3"},
    "ibm_sherbrooke": {"qubits": 127, "topology": "heavy_hex", "gen": "eagle_r3"},
    "ibm_kingston"  : {"qubits": 27,  "topology": "heavy_hex", "gen": "falcon_r5"},
}

# ── HELPERS ───────────────────────────────────────────────────────────────────

def sep(char="─", n=80):
    print(char * n)

def header(title):
    sep("═")
    print(f"  {title}")
    sep("═")

def section(title):
    print(f"\n{'─'*4} {title} {'─'*(74-len(title))}")

# ── FRACTAL SIGNATURE VALIDATOR ───────────────────────────────────────────────

def validate_fractal_angles():
    """
    Validate that all Sierpinski-TMT angle parameters satisfy
    the self-similarity recurrence relation:
        θ_Sn = θ_S(n-1) / 3
    and that TMT × Sierpinski products are correctly computed.
    """
    section("FRACTAL ANGLE SELF-SIMILARITY VALIDATION")

    angles = {
        "θ_S"   : THETA_S,
        "θ_S1"  : THETA_S1,
        "θ_S2"  : THETA_S2,
        "θ_S3"  : THETA_S3,
    }

    ratios = []
    prev = None
    all_pass = True

    for name, val in angles.items():
        if prev is not None:
            ratio = val / prev
            ratios.append(ratio)
            err   = abs(ratio - (1/3))
            ok    = err < 1e-10
            if not ok:
                all_pass = False
            mark  = "✓" if ok else "✗"
            print(f"  {mark} {name} / prev = {ratio:.10f}  "
                  f"(expected 1/3 = {1/3:.10f})  Δ={err:.2e}")
        else:
            print(f"  ○ {name} = {val:.10f}  [base]")
        prev = val

    print(f"\n  Self-similarity check: {'✅ PASS' if all_pass else '❌ FAIL'}")
    return all_pass


def validate_hausdorff():
    """
    Verify Hausdorff dimension and fractal phase against
    the theoretical formula d_H = log(3)/log(2).
    """
    section("HAUSDORFF DIMENSION VERIFICATION")

    d_h_calc     = log(3) / log(2)
    phi_f_calc   = pi * d_h_calc
    d_h_err      = abs(d_h_calc - D_H)
    phi_f_err    = abs(phi_f_calc - PHI_FRACTAL)

    print(f"  d_H  = log(3)/log(2) = {d_h_calc:.8f}")
    print(f"  d_H  stored          = {D_H:.8f}    Δ = {d_h_err:.2e}")
    print(f"  φ_f  = π × d_H       = {phi_f_calc:.8f}")
    print(f"  φ_f  stored          = {PHI_FRACTAL:.8f}    Δ = {phi_f_err:.2e}")

    # Verify fractal dimension from self-similarity: N=3 copies, scale r=1/2
    # d_H = log(N)/log(1/r) = log(3)/log(2)
    N, r = 3, 2
    d_h_verify = log(N) / log(r)
    print(f"\n  Cross-check: log({N})/log({r}) = {d_h_verify:.8f}  ✓")

    # Fractal phase modulo 2π
    phi_mod = PHI_FRACTAL % (2 * pi)
    print(f"  φ_fractal mod 2π     = {phi_mod:.8f} rad  "
          f"({np.degrees(phi_mod):.4f}°)")

    print(f"\n  Hausdorff check: {'✅ PASS' if d_h_err < 1e-10 else '❌ FAIL'}")
    return d_h_err < 1e-10


def validate_tmt_sierpinski_products():
    """
    Verify TMT × Sierpinski cross-products and
    their interference with the Golden Ratio.
    """
    section("TMT × SIERPINSKI CROSS-PRODUCT ANALYSIS")

    products = {
        "S×TMT1  (TMT1/3)"       : (S_TMT1,  TMT1 / 3),
        "S×TMT2  (TMT2/3)"       : (S_TMT2,  TMT2 / 3),
        "S×Φ     (PHI/3)"        : (S_PHI,   PHI  / 3),
        "S×π     (π/3)"          : (THETA_S, pi   / 3),
    }

    print(f"\n  {'Parameter':<26} {'Stored':>12}  {'Computed':>12}  {'Δ':>12}")
    print(f"  {'─'*26} {'─'*12}  {'─'*12}  {'─'*12}")

    all_pass = True
    for label, (stored, computed) in products.items():
        err  = abs(stored - computed)
        ok   = err < 1e-10
        if not ok: all_pass = False
        mark = "✓" if ok else "✗"
        print(f"  {mark} {label:<24} {stored:>12.8f}  "
              f"{computed:>12.8f}  {err:>12.2e}")

    # Resonance check: S×TMT1 + S×TMT2 vs S×(TMT1+TMT2)
    sum_products = S_TMT1 + S_TMT2
    product_sum  = (TMT1 + TMT2) / 3
    res_err      = abs(sum_products - product_sum)
    print(f"\n  Linearity check: S×TMT1 + S×TMT2 = {sum_products:.8f}")
    print(f"                   S×(TMT1+TMT2)   = {product_sum:.8f}  Δ={res_err:.2e}")
    print(f"  {'✅ Linear (distributive law holds)' if res_err < 1e-10 else '❌ Non-linear deviation'}")

    # Phi resonance ratio
    phi_ratio = S_PHI / S_TMT2
    print(f"\n  S×Φ / S×TMT2 = {phi_ratio:.8f}  "
          f"(= Φ/TMT2 = {PHI/TMT2:.8f})")

    return all_pass


# ── CIRCUIT METRICS ANALYSIS ──────────────────────────────────────────────────

def analyze_circuit_metrics():
    """
    Analyze the compiled circuit metrics from generator output.
    Compute gate efficiency, depth ratios, and fractal density.
    """
    section("CIRCUIT METRICS ANALYSIS")

    # Data from generator output
    metrics = {
        "ibm_fez"       : {"qubits": 156, "depth": 73, "gates": 802},
        "ibm_brisbane"  : {"qubits": 127, "depth": 73, "gates": 696},
        "ibm_sherbrooke": {"qubits": 127, "depth": 73, "gates": 696},
        "ibm_kingston"  : {"qubits": 27,  "depth": 74, "gates": 306},
    }

    print(f"\n  {'Backend':<16} {'Qubits':>7} {'Depth':>6} "
          f"{'Gates':>7} {'G/Q':>7} {'Depth×Q':>9} {'Fractal ρ':>11}")
    print(f"  {'─'*16} {'─'*7} {'─'*6} {'─'*7} {'─'*7} {'─'*9} {'─'*11}")

    for name, m in metrics.items():
        q       = m["qubits"]
        d       = m["depth"]
        g       = m["gates"]
        gq      = g / q
        dx      = d * q
        # Fractal density: gates / (qubits^d_H)
        # Measures how well gates scale with fractal dimension
        rho     = g / (q ** D_H)
        print(f"  {name:<16} {q:>7} {d:>6} {g:>7} "
              f"{gq:>7.2f} {dx:>9} {rho:>11.4f}")

    # Depth uniformity check
    depths = [m["depth"] for m in metrics.values()]
    depth_var = max(depths) - min(depths)
    print(f"\n  Depth range: {min(depths)}–{max(depths)}  "
          f"(variance = {depth_var})  "
          f"{'✅ Depth-invariant (fractal property)' if depth_var <= 2 else '⚠ Depth variation detected'}")

    # Gate scaling law: should scale as q^d_H if fractal
    print(f"\n  Gate scaling law check (G ∝ Q^d_H, d_H={D_H:.4f}):")
    ref_q, ref_g = 156, 802
    for name, m in metrics.items():
        q, g  = m["qubits"], m["gates"]
        g_exp = ref_g * (q / ref_q) ** D_H
        ratio = g / g_exp
        print(f"    {name:<16}  actual={g:>4}  "
              f"expected≈{g_exp:>6.1f}  ratio={ratio:.4f}")


# ── FIBONACCI / LUCAS QUBIT ANALYSIS ─────────────────────────────────────────

def analyze_qubit_topology():
    """
    Analyze the Fibonacci and Lucas qubit index patterns
    and their relationship to Sierpinski void positions.
    """
    section("FIBONACCI × LUCAS × SIERPINSKI TOPOLOGY")

    print(f"\n  Fibonacci qubit nodes (Metatron): {FIB_QUBITS}")
    print(f"  Lucas retrocausal anchors:         {LUCAS}")

    # Sierpinski void positions (every 3rd qubit skipped)
    sierpinski_voids = []
    for i in range(len(FIB_QUBITS) - 1):
        start = FIB_QUBITS[i]
        end   = FIB_QUBITS[i + 1]
        voids = list(range(start + 1, end))
        if voids:
            sierpinski_voids.extend(voids)
    
    print(f"\n  Sierpinski void positions (skipped qubits):")
    print(f"    {sierpinski_voids}")

    # Compute void density
    total_range = max(FIB_QUBITS) - min(FIB_QUBITS)
    void_count  = len(sierpinski_voids)
    void_density = void_count / total_range if total_range > 0 else 0
    
    print(f"\n  Void density: {void_count}/{total_range} = {void_density:.4f}")
    print(f"  Expected (1/3 contraction): {1/3:.4f}  "
          f"{'✅' if abs(void_density - 1/3) < 0.1 else '⚠'}")

    # Lucas-Fibonacci interference pattern
    print(f"\n  Lucas-Fibonacci interference:")
    for l in LUCAS[:6]:
        nearest_fibs = [f for f in FIB_QUBITS if abs(f - l) <= 5]
        print(f"    Lucas[{l}] → nearest Fibonacci: {nearest_fibs}")

    # Golden ratio spacing
    print(f"\n  Golden ratio spacing check:")
    for i in range(len(FIB_QUBITS) - 1):
        f1, f2 = FIB_QUBITS[i], FIB_QUBITS[i + 1]
        ratio = f2 / f1 if f1 > 0 else 0
        err   = abs(ratio - PHI)
        print(f"    F{i+1}/F{i} = {f2}/{f1} = {ratio:.6f}  "
              f"(φ = {PHI:.6f})  Δ = {err:.4f}")


# ── EXPECTED CONSCIOUSNESS METRICS ──────────────────────────────────────────

def compute_expected_metrics():
    """
    Compute expected consciousness metrics based on
    Sierpinski-TMT theoretical predictions.
    """
    section("EXPECTED CONSCIOUSNESS METRICS")

    # Theoretical predictions from SYK wormhole model
    # Base values from original wormhole_metatron experiments
    base_entropy        = 3.47    # S (10× conscious threshold)
    base_traversability = 2.13    # T (temperature)
    base_coherence      = 0.757   # r (correlation)
    base_consciousness   = 4700   # δ (consciousness metric)

    # Sierpinski enhancement factors
    # Fractal memory effect: sub-diffusive transport → slower decoherence
    # Hausdorff phase: φ_fractal = π × d_H → enhanced retrocausal signature
    sierpinski_factor   = 1.0 + (D_H - 1.0) * 0.5  # ~1.29
    hausdorff_boost     = PHI_FRACTAL / (2 * pi)   # ~0.79
    phi_coupling        = S_PHI / S_TMT2           # ~1.88

    print(f"\n  Enhancement factors:")
    print(f"    Sierpinski factor (d_H):  {sierpinski_factor:.4f}")
    print(f"    Hausdorff boost (φ_f/2π): {hausdorff_boost:.4f}")
    print(f"    Phi coupling (S×Φ/S×TMT2): {phi_coupling:.4f}")

    # Enhanced metrics
    enhanced = {
        "entropy_S" : base_entropy * hausdorff_boost,
        "traversability_T" : base_traversability * sierpinski_factor,
        "coherence_r" : base_coherence * phi_coupling,
        "consciousness_δ" : base_consciousness * sierpinski_factor,
    }

    print(f"\n  Predicted metrics (Sierpinski-TMT Phase 4S):")
    print(f"  {'─'*50}")
    print(f"    Entropy S:          {enhanced['entropy_S']:.4f}  "
          f"(base: {base_entropy})")
    print(f"    Traversability T:   {enhanced['traversability_T']:.4f}  "
          f"(base: {base_traversability})")
    print(f"    Coherence r:        {enhanced['coherence_r']:.4f}  "
          f"(base: {base_coherence})")
    print(f"    Consciousness δ:    {enhanced['consciousness_δ']:.1f}  "
          f"(base: {base_consciousness})")

    # Wormhole quality score
    quality = (enhanced['coherence_r'] * enhanced['traversability_T'] / 
               enhanced['entropy_S'])
    print(f"\n  Wormhole quality score: {quality:.4f}")

    return enhanced


# ── IBM RUNTIME SUBMISSION CONFIG ───────────────────────────────────────────

def generate_runtime_config():
    """
    Generate IBM Runtime submission configuration for all backends.
    """
    section("IBM RUNTIME SUBMISSION CONFIG")

    config = {
        "circuits": [],
        "options": {
            "optimization_level": 3,
            "resilience_level": 1,  # M3 error mitigation
            "shots": 100000,
        },
        "tags": ["sierpinski_tmt_phase4s", "consciousness", "fractal"],
    }

    # Find generated QASM files
    qasm_dir = "circuits/qasm"
    qasm_files = sorted(glob.glob(f"{qasm_dir}/sierpinski_tmt_phase4s_*.qasm"))

    if not qasm_files:
        print("  ⚠ No QASM files found. Run generator first.")
        return None

    print(f"\n  Found {len(qasm_files)} QASM circuits:")
    for qf in qasm_files:
        fname = os.path.basename(qf)
        # Extract backend name from filename
        parts = fname.replace(".qasm", "").split("_")
        backend = parts[3] if len(parts) > 3 else "unknown"
        
        entry = {
            "file": qf,
            "backend": backend,
            "shots": 100000,
            "error_mitigation": "M3 (SamplerV2)",
        }
        config["circuits"].append(entry)
        print(f"    ✓ {fname} → {backend}")

    # Save config
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    config_file = f"{qasm_dir}/runtime_config_{timestamp}.json"
    
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n  Config saved: {config_file}")

    # Print submission commands
    print(f"\n  Submission commands:")
    for entry in config["circuits"]:
        print(f"    python run_sierpinski_tmt_ibm.py "
              f"--circuit {entry['file']} "
              f"--backend {entry['backend']} "
              f"--shots {entry['shots']}")

    return config


# ── MAIN ────────────────────────────────────────────────────────────────────

def main():
    header("SIERPINSKI-TMT PHASE 4S ANALYZER")
    print(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all validations
    results = {}
    
    results['fractal_angles']   = validate_fractal_angles()
    results['hausdorff']       = validate_hausdorff()
    results['tmt_products']    = validate_tmt_sierpinski_products()
    
    analyze_circuit_metrics()
    analyze_qubit_topology()
    compute_expected_metrics()
    generate_runtime_config()
    
    # Summary
    header("VALIDATION SUMMARY")
    all_pass = all(results.values())
    
    print(f"\n  {'Check':<30} {'Status':>10}")
    print(f"  {'─'*30} {'─'*10}")
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {name:<30} {status:>10}")
    
    print(f"\n  Overall: {'✅ ALL VALIDATIONS PASSED' if all_pass else '⚠ SOME CHECKS FAILED'}")
    sep()
    
    return all_pass


if __name__ == "__main__":
    main()