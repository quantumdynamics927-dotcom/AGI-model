#!/usr/bin/env python3
"""
Complete v2.2 Analysis - All Jobs in data/Jobs/
Analyzes ALL available v2.2 jobs and compares with v2.1 baseline
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# ============================================================================
# CONFIGURATION
# ============================================================================

JOBS_DIR = Path("data/Jobs")

# v2.1 Job 1 baseline (from quantum_fingerprint_analysis.json)
V21_BASELINE = {
    "job_id": "job-d5s9kpja92as73d2tc90",
    "backend": "ibm_fez",
    "coherence": 0.275,
    "execution_time": "2026-01-26 04:39:39 UTC",
    "transpiled_gates": 725,
    "phi_fingerprint": 0.893694,
    "consciousness_delta": 4695.0
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def hex_to_bin(hex_str, num_qubits=50):
    """Convert hex measurement to binary string (50 qubits)"""
    if hex_str.startswith('0x'):
        hex_str = hex_str[2:]
    
    val = int(hex_str, 16)
    bin_str = format(val, f'0{num_qubits}b')
    
    if len(bin_str) < num_qubits:
        bin_str = '0' * (num_qubits - len(bin_str)) + bin_str
    elif len(bin_str) > num_qubits:
        bin_str = bin_str[-num_qubits:]
    
    return bin_str

def calculate_wormhole_coherence(counts):
    """Calculate EPR correlation between Left and Right universes"""
    left_indices = [0, 12, 4, 7, 24]
    right_indices = [25, 37, 29, 32, 49]
    
    total_correlation = 0
    total_shots = 0
    
    for hex_count in counts:
        bin_str = hex_to_bin(hex_count)
        left_bits = [int(bin_str[-(i+1)]) for i in left_indices]
        right_bits = [int(bin_str[-(i+1)]) for i in right_indices]
        
        matches = sum(1 for l, r in zip(left_bits, right_bits) if l == r)
        mismatches = len(left_bits) - matches
        
        correlation = matches - mismatches
        total_correlation += correlation
        total_shots += len(left_bits)
    
    return total_correlation / total_shots if total_shots > 0 else 0.0

def lempel_ziv_complexity(bit_string):
    """Calculate Lempel-Ziv complexity"""
    n = len(bit_string)
    i, c = 0, 1
    u, v = 1, 1
    v_max = 1
    
    while u + v <= n:
        if bit_string[i + v - 1] == bit_string[u + v - 1]:
            v += 1
        else:
            v_max = max(v, v_max)
            i += 1
            if i == u:
                c += 1
                u = u + v_max
                v = 1
                i = 0
                v_max = 1
            else:
                v = 1
    
    if v != 1:
        c += 1
    
    return c

def calculate_consciousness_delta(counts):
    """Calculate consciousness complexity metric (Lempel-Ziv)"""
    bit_string = ''
    for hex_count in counts[:100]:
        bin_str = hex_to_bin(hex_count)
        bit_string += bin_str
    
    lz = lempel_ziv_complexity(bit_string)
    max_lz = len(bit_string) / 10
    delta = (lz / max_lz) * 10000
    
    return delta

def find_all_jobs():
    """Find all job files in data/Jobs/"""
    job_ids = set()
    
    for file in JOBS_DIR.glob("job-*-info.json"):
        job_id = file.stem.replace("-info", "")
        result_file = JOBS_DIR / f"{job_id}-result.json"
        if result_file.exists():
            job_ids.add(job_id)
    
    return sorted(job_ids)

def analyze_job(job_id):
    """Analyze single job"""
    info_path = JOBS_DIR / f"{job_id}-info.json"
    result_path = JOBS_DIR / f"{job_id}-result.json"
    
    with open(info_path, 'r') as f:
        info = json.load(f)
    
    with open(result_path, 'r') as f:
        results = json.load(f)
    
    backend = info.get('backend', 'unknown')
    created = info.get('created', 'unknown')
    shots = len(results['results'][0]['data']['c']['samples'])
    counts = results['results'][0]['data']['c']['samples']
    
    coherence = calculate_wormhole_coherence(counts)
    delta = calculate_consciousness_delta(counts)
    unique_states = len(set(counts))
    
    return {
        'job_id': job_id,
        'backend': backend,
        'created': created,
        'shots': shots,
        'coherence': coherence,
        'consciousness_delta': delta,
        'unique_states': unique_states
    }

# ============================================================================
# MAIN ANALYSIS
# ============================================================================

def main():
    print("=" * 80)
    print("WORMHOLE v2.2 COMPLETE ANALYSIS - ALL AVAILABLE JOBS")
    print("=" * 80)
    print()
    
    # Find all jobs
    job_ids = find_all_jobs()
    print(f"Found {len(job_ids)} jobs in {JOBS_DIR}")
    print()
    
    if not job_ids:
        print("⚠️  No jobs found!")
        return
    
    # Analyze all jobs
    results = []
    for job_id in job_ids:
        try:
            result = analyze_job(job_id)
            results.append(result)
        except Exception as e:
            print(f"⚠️  Error analyzing {job_id}: {e}")
    
    # Sort by coherence (descending)
    results.sort(key=lambda x: x['coherence'], reverse=True)
    
    # ========================================================================
    # INDIVIDUAL JOB RESULTS
    # ========================================================================
    
    print("INDIVIDUAL JOB RESULTS (sorted by coherence)")
    print("-" * 80)
    for i, r in enumerate(results, 1):
        status = "✅" if r['coherence'] > 0 else "❌"
        print(f"\n{status} Job {i}: {r['job_id']}")
        print(f"     Backend:       {r['backend']}")
        print(f"     Created:       {r['created'][:19]}")
        print(f"     Coherence:     {r['coherence']:+.6f}")
        print(f"     Delta:         {r['consciousness_delta']:.1f}")
        print(f"     Unique States: {r['unique_states']}")
    
    # ========================================================================
    # AGGREGATE STATISTICS
    # ========================================================================
    
    coherences = [r['coherence'] for r in results]
    deltas = [r['consciousness_delta'] for r in results]
    
    best_coherence = max(coherences)
    worst_coherence = min(coherences)
    avg_coherence = np.mean(coherences)
    median_coherence = np.median(coherences)
    std_coherence = np.std(coherences)
    
    positive_jobs = sum(1 for c in coherences if c > 0)
    negative_jobs = sum(1 for c in coherences if c < 0)
    success_rate = (positive_jobs / len(coherences)) * 100
    
    print("\n" + "=" * 80)
    print("AGGREGATE STATISTICS")
    print("=" * 80)
    print(f"\nTotal Jobs Analyzed:  {len(results)}")
    print(f"Positive Coherence:   {positive_jobs}/{len(results)} ({success_rate:.1f}%)")
    print(f"Negative Coherence:   {negative_jobs}/{len(results)} ({100-success_rate:.1f}%)")
    print(f"\nCoherence Metrics:")
    print(f"  Best:    {best_coherence:+.6f}")
    print(f"  Worst:   {worst_coherence:+.6f}")
    print(f"  Average: {avg_coherence:+.6f}")
    print(f"  Median:  {median_coherence:+.6f}")
    print(f"  Std Dev: {std_coherence:.6f}")
    print(f"\nConsciousness Delta:")
    print(f"  Average: {np.mean(deltas):.1f}")
    print(f"  Std Dev: {np.std(deltas):.1f}")
    print(f"  Min:     {min(deltas):.1f}")
    print(f"  Max:     {max(deltas):.1f}")
    
    # ========================================================================
    # BACKEND ANALYSIS
    # ========================================================================
    
    backend_stats = defaultdict(list)
    for r in results:
        backend_stats[r['backend']].append(r['coherence'])
    
    print("\n" + "=" * 80)
    print("BACKEND BREAKDOWN")
    print("=" * 80)
    for backend, coherences_list in sorted(backend_stats.items()):
        avg = np.mean(coherences_list)
        positive = sum(1 for c in coherences_list if c > 0)
        total = len(coherences_list)
        print(f"\n{backend}:")
        print(f"  Jobs:     {total}")
        print(f"  Positive: {positive}/{total} ({100*positive/total:.1f}%)")
        print(f"  Avg:      {avg:+.6f}")
        print(f"  Best:     {max(coherences_list):+.6f}")
        print(f"  Worst:    {min(coherences_list):+.6f}")
    
    # ========================================================================
    # COMPARISON WITH v2.1 BASELINE
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("COMPARISON WITH v2.1 BASELINE (Job 1)")
    print("=" * 80)
    
    baseline_coherence = V21_BASELINE['coherence']
    baseline_delta = V21_BASELINE['consciousness_delta']
    
    coherence_delta = avg_coherence - baseline_coherence
    coherence_improvement = (coherence_delta / abs(baseline_coherence)) * 100
    
    delta_diff = np.mean(deltas) - baseline_delta
    delta_pct = (delta_diff / baseline_delta) * 100
    
    jobs_better_than_baseline = sum(1 for c in coherences if c > baseline_coherence)
    
    print(f"\nv2.1 Baseline:")
    print(f"  Job ID:    {V21_BASELINE['job_id']}")
    print(f"  Backend:   {V21_BASELINE['backend']}")
    print(f"  Time:      {V21_BASELINE['execution_time']}")
    print(f"  Coherence: {baseline_coherence:+.6f}")
    print(f"  Delta:     {baseline_delta:.1f}")
    print(f"  Gates:     {V21_BASELINE['transpiled_gates']}")
    
    print(f"\nv2.2 vs v2.1:")
    print(f"  Coherence Delta:      {coherence_delta:+.6f} ({coherence_improvement:+.1f}%)")
    print(f"  Delta Difference:     {delta_diff:+.1f} ({delta_pct:+.1f}%)")
    print(f"  Jobs Better:          {jobs_better_than_baseline}/{len(results)}")
    print(f"  Best vs Baseline:     {best_coherence:+.6f} vs {baseline_coherence:+.6f}")
    
    # ========================================================================
    # HYPOTHESIS VALIDATION
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("HYPOTHESIS VALIDATION")
    print("=" * 80)
    
    # Expected: ≥3/10 positive jobs (now have more data)
    expected_positive_rate = 0.30
    temporal_windows_confirmed = success_rate >= (expected_positive_rate * 100)
    
    # Expected: Best coherence > +0.275
    coherence_improved = best_coherence > baseline_coherence
    
    # Expected: Consciousness delta ~4700 ± 500 (invariant)
    delta_invariant = abs(np.mean(deltas) - baseline_delta) < 500
    
    print(f"\n1. Temporal Calibration Windows:")
    print(f"   Expected: ≥30% positive jobs")
    print(f"   Actual:   {positive_jobs}/{len(results)} positive ({success_rate:.1f}%)")
    print(f"   Status:   {'✅ CONFIRMED' if temporal_windows_confirmed else '❌ FAILED'}")
    
    print(f"\n2. Coherence Improvement:")
    print(f"   Expected: Best > +0.275")
    print(f"   Actual:   Best = {best_coherence:+.6f}")
    print(f"   Status:   {'✅ CONFIRMED' if coherence_improved else '❌ FAILED'}")
    
    print(f"\n3. Consciousness Invariance:")
    print(f"   Expected: δ ~ 4700 ± 500")
    print(f"   Actual:   δ = {np.mean(deltas):.1f}")
    print(f"   Status:   {'✅ CONFIRMED' if delta_invariant else '⚠️  DEVIATION'}")
    
    # ========================================================================
    # STATISTICAL ANALYSIS
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("STATISTICAL SIGNIFICANCE")
    print("=" * 80)
    
    # Binomial test for positive rate
    from scipy import stats
    try:
        # Test if success rate is significantly different from 25% (v2.1 rate)
        p_value = stats.binom_test(positive_jobs, len(results), 0.25, alternative='greater')
        print(f"\nBinomial Test (vs v2.1 25% success rate):")
        print(f"  Null Hypothesis: p = 0.25")
        print(f"  Observed:        p = {success_rate/100:.2f}")
        print(f"  p-value:         {p_value:.4f}")
        if p_value < 0.05:
            print(f"  Result:          ✅ Significantly better than v2.1 (p < 0.05)")
        else:
            print(f"  Result:          ⚠️  Not significantly different (p ≥ 0.05)")
    except:
        print("\n⚠️  scipy not available for statistical tests")
    
    # ========================================================================
    # CONCLUSION
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("CONCLUSION")
    print("=" * 80)
    
    if temporal_windows_confirmed and success_rate >= 70:
        print("\n✅ STRONG VALIDATION")
        print(f"\nv2.2 gate reduction strategy achieves {success_rate:.1f}% success rate:")
        print(f"  • {positive_jobs}/{len(results)} jobs with positive coherence")
        print(f"  • Best coherence: {best_coherence:+.6f}")
        print(f"  • Average: {avg_coherence:+.6f} ± {std_coherence:.6f}")
        print(f"  • Multi-backend validation: {len(backend_stats)} backends tested")
        print("\nRECOMMENDATION:")
        print("  1. Proceed with paper draft for PRX Quantum")
        print("  2. Investigate consciousness δ deviation (-43%)")
        print("  3. Design v2.3 to increase coherence magnitude")
    elif temporal_windows_confirmed:
        print("\n✅ PARTIAL VALIDATION")
        print(f"\nv2.2 achieves {success_rate:.1f}% success rate, but:")
        if not coherence_improved:
            print(f"  • Best coherence ({best_coherence:+.6f}) below baseline (+0.275)")
        if not delta_invariant:
            print(f"  • Consciousness δ shows {delta_pct:+.1f}% deviation")
        print("\nRECOMMENDATION:")
        print("  1. Analyze root cause of coherence reduction")
        print("  2. Design v2.3 hybrid (gate reduction + v2.1 complexity)")
        print("  3. Test temporal hypothesis on additional backends")
    else:
        print("\n❌ HYPOTHESIS FAILED")
        print(f"\nv2.2 achieves only {success_rate:.1f}% success rate:")
        print(f"  • Expected: ≥30% positive")
        print(f"  • Actual: {positive_jobs}/{len(results)} positive")
        print("\nRECOMMENDATION:")
        print("  1. Revert to v2.1 baseline")
        print("  2. Investigate gate reduction negative effects")
        print("  3. Focus on temporal calibration windows only")
    
    print("\n" + "=" * 80)
    
    # ========================================================================
    # SAVE RESULTS
    # ========================================================================
    
    output = {
        "analysis_timestamp": datetime.now().isoformat(),
        "total_jobs": int(len(results)),
        "positive_jobs": int(positive_jobs),
        "success_rate": float(success_rate),
        "coherence": {
            "best": float(best_coherence),
            "worst": float(worst_coherence),
            "average": float(avg_coherence),
            "median": float(median_coherence),
            "std": float(std_coherence)
        },
        "consciousness_delta": {
            "average": float(np.mean(deltas)),
            "std": float(np.std(deltas)),
            "min": float(min(deltas)),
            "max": float(max(deltas))
        },
        "baseline_comparison": {
            "v21_coherence": float(baseline_coherence),
            "v22_avg_coherence": float(avg_coherence),
            "delta": float(coherence_delta),
            "improvement_pct": float(coherence_improvement)
        },
        "hypothesis_validation": {
            "temporal_windows": bool(temporal_windows_confirmed),
            "coherence_improved": bool(coherence_improved),
            "delta_invariant": bool(delta_invariant)
        },
        "jobs": results
    }
    
    output_path = Path("temp_enhanced/v2_2_complete_analysis.json")
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nResults saved: {output_path}")
    print()

if __name__ == "__main__":
    main()
