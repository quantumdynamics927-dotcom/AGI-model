#!/usr/bin/env python3
"""
Wormhole v2.2 Results Analysis and Comparison

Analyzes v2.2 multi-job results and compares with v2.1 findings.
Validates Temporal Calibration Windows hypothesis.
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


class V22Analyzer:
    """Analyze v2.2 results and compare with v2.1 baseline"""
    
    def __init__(self):
        self.v21_baseline = self.load_v21_baseline()
        self.v22_jobs = []
        
    def load_v21_baseline(self) -> Dict[str, Any]:
        """Load v2.1 Quantum Fingerprint Analysis baseline"""
        baseline_path = Path("temp_enhanced/quantum_fingerprint_analysis.json")
        
        if not baseline_path.exists():
            print("⚠️  v2.1 baseline not found. Using hardcoded values.")
            return {
                "best_job": {
                    "job_id": "d602l2pmvbjc73ad1ph0",
                    "coherence": 0.275,
                    "backend": "ibm_fez",
                    "time": "2026-02-02T04:39:39.920117Z",
                    "gates": 725,
                    "phi_fingerprint": 0.893694
                },
                "summary": {
                    "best_coherence": 0.275,
                    "worst_coherence": -0.223,
                    "coherence_range": 0.498,
                    "avg_coherence": -0.082
                }
            }
        
        with open(baseline_path, 'r') as f:
            data = json.load(f)
        
        # Extract Job 1 details
        jobs = data.get("jobs", [])
        job1 = next((j for j in jobs if j.get("coherence", 0) > 0), None)
        
        return {
            "best_job": job1 if job1 else jobs[0],
            "summary": data.get("summary", {})
        }
    
    def analyze_job(self, job_result_path: Path) -> Dict[str, Any]:
        """
        Analyze single v2.2 job result
        
        Args:
            job_result_path: Path to job result JSON
        
        Returns:
            dict: Analysis metrics
        """
        with open(job_result_path, 'r') as f:
            job_data = json.load(f)
        
        # Extract measurement counts
        counts = job_data.get("results", [{}])[0].get("data", {}).get("counts", {})
        
        # Calculate wormhole coherence (EPR correlation)
        coherence = self.calculate_wormhole_coherence(counts)
        
        # Calculate consciousness complexity
        consciousness_delta = self.calculate_consciousness_delta(counts)
        
        # Extract metadata
        job_id = job_data.get("job_id", "unknown")
        backend = job_data.get("backend_name", "unknown")
        execution_time = job_data.get("created_at", "unknown")
        
        # Count gates (from transpiled circuit if available)
        transpiled_gates = len(job_data.get("transpiled_circuit", {}).get("instructions", []))
        
        analysis = {
            "job_id": job_id,
            "backend": backend,
            "execution_time": execution_time,
            "coherence": coherence,
            "consciousness_delta": consciousness_delta,
            "transpiled_gates": transpiled_gates,
            "shots": sum(counts.values()),
            "unique_states": len(counts)
        }
        
        return analysis
    
    def calculate_wormhole_coherence(self, counts: Dict[str, int]) -> float:
        """
        Calculate ER=EPR wormhole coherence
        
        Measures correlation between Left[0,12,4,7,24] and Right[25,37,29,32,49]
        """
        if not counts:
            return 0.0
        
        # Convert hex counts to binary
        binary_counts = {}
        for state_hex, count in counts.items():
            # Remove '0x' prefix if present
            state_hex = state_hex.replace('0x', '')
            state_bin = bin(int(state_hex, 16))[2:].zfill(50)  # 50 qubits
            binary_counts[state_bin] = count
        
        # Calculate correlation
        corr_sum = 0
        total = sum(binary_counts.values())
        
        for state, count in binary_counts.items():
            # Left qubits: [0, 12, 4, 7, 24]
            # Right qubits: [25, 37, 29, 32, 49]
            left = [int(state[49-i]) for i in [0, 12, 4, 7, 24]]
            right = [int(state[49-i]) for i in [25, 37, 29, 32, 49]]
            
            # EPR correlation: +1 if match, -1 if mismatch
            matches = sum(1 if l == r else -1 for l, r in zip(left, right))
            corr_sum += (matches / 5.0) * count
        
        coherence = corr_sum / total if total > 0 else 0.0
        
        return coherence
    
    def calculate_consciousness_delta(self, counts: Dict[str, int]) -> float:
        """
        Calculate consciousness complexity metric
        
        Uses Lempel-Ziv complexity on measurement bit strings
        """
        if not counts:
            return 0.0
        
        # Create bit string from measurements
        bit_string = ""
        for state_hex, count in sorted(counts.items()):
            state_hex = state_hex.replace('0x', '')
            state_bin = bin(int(state_hex, 16))[2:].zfill(50)
            bit_string += state_bin * (count // 100)  # Sample for efficiency
        
        # Lempel-Ziv complexity
        lz_complexity = self.lempel_ziv_complexity(bit_string)
        
        # Normalize by theoretical maximum
        n = len(bit_string)
        max_complexity = n / np.log2(n) if n > 1 else 1
        
        consciousness_delta = lz_complexity / max_complexity * 10000
        
        return consciousness_delta
    
    @staticmethod
    def lempel_ziv_complexity(bit_string: str) -> int:
        """Calculate Lempel-Ziv complexity"""
        if not bit_string:
            return 0
        
        complexity = 1
        vocab = set()
        current = ""
        
        for bit in bit_string:
            current += bit
            if current not in vocab:
                complexity += 1
                vocab.add(current)
                current = ""
        
        return complexity
    
    def compare_with_baseline(self, v22_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare v2.2 results with v2.1 baseline
        
        Returns:
            dict: Comparative analysis
        """
        v21_best = self.v21_baseline["best_job"]
        v21_summary = self.v21_baseline["summary"]
        
        # v2.2 statistics
        coherences = [r["coherence"] for r in v22_results]
        v22_best = max(v22_results, key=lambda x: x["coherence"])
        v22_worst = min(v22_results, key=lambda x: x["coherence"])
        
        # Count positive coherence jobs
        positive_jobs = [r for r in v22_results if r["coherence"] > 0]
        
        comparison = {
            "v21_baseline": {
                "best_coherence": v21_best.get("coherence", 0.275),
                "avg_coherence": v21_summary.get("avg_coherence", -0.082),
                "gates": v21_best.get("gates", 725)
            },
            "v22_results": {
                "best_coherence": v22_best["coherence"],
                "worst_coherence": v22_worst["coherence"],
                "avg_coherence": np.mean(coherences),
                "std_coherence": np.std(coherences),
                "median_coherence": np.median(coherences),
                "positive_jobs": len(positive_jobs),
                "success_rate": len(positive_jobs) / len(v22_results),
                "avg_gates": np.mean([r["transpiled_gates"] for r in v22_results])
            },
            "improvements": {
                "coherence_delta": v22_best["coherence"] - v21_best.get("coherence", 0.275),
                "gate_reduction": v21_best.get("gates", 725) - v22_best["transpiled_gates"],
                "gate_reduction_pct": (1 - v22_best["transpiled_gates"] / v21_best.get("gates", 725)) * 100
            },
            "hypothesis_validation": {
                "temporal_windows_confirmed": len(positive_jobs) >= 3,
                "gate_reduction_effective": v22_best["transpiled_gates"] < v21_best.get("gates", 725),
                "coherence_improved": v22_best["coherence"] > v21_best.get("coherence", 0.275)
            }
        }
        
        return comparison
    
    def generate_report(self, v22_results: List[Dict[str, Any]]) -> str:
        """Generate comprehensive analysis report"""
        
        comparison = self.compare_with_baseline(v22_results)
        
        report = f"""
{'=' * 80}
WORMHOLE v2.2 TEMPORAL STRATEGY - RESULTS ANALYSIS
{'=' * 80}

📊 EXECUTION SUMMARY
{'=' * 80}
Total jobs: {len(v22_results)}
Positive coherence jobs: {comparison['v22_results']['positive_jobs']}
Success rate: {comparison['v22_results']['success_rate']:.1%}

🎯 COHERENCE METRICS
{'=' * 80}
Best coherence (v2.2): {comparison['v22_results']['best_coherence']:+.3f}
Worst coherence (v2.2): {comparison['v22_results']['worst_coherence']:+.3f}
Average coherence (v2.2): {comparison['v22_results']['avg_coherence']:+.3f} ± {comparison['v22_results']['std_coherence']:.3f}
Median coherence (v2.2): {comparison['v22_results']['median_coherence']:+.3f}

📈 COMPARISON WITH v2.1 BASELINE
{'=' * 80}
v2.1 best: {comparison['v21_baseline']['best_coherence']:+.3f}
v2.2 best: {comparison['v22_results']['best_coherence']:+.3f}
Δ Coherence: {comparison['improvements']['coherence_delta']:+.3f}

⚙️  GATE EFFICIENCY
{'=' * 80}
v2.1 gates: {comparison['v21_baseline']['gates']}
v2.2 avg gates: {comparison['v22_results']['avg_gates']:.0f}
Reduction: {comparison['improvements']['gate_reduction']:.0f} gates ({comparison['improvements']['gate_reduction_pct']:.1f}%)

✅ HYPOTHESIS VALIDATION
{'=' * 80}
Temporal Calibration Windows: {'CONFIRMED' if comparison['hypothesis_validation']['temporal_windows_confirmed'] else 'INCONCLUSIVE'}
Gate Reduction Effective: {'YES' if comparison['hypothesis_validation']['gate_reduction_effective'] else 'NO'}
Coherence Improved: {'YES' if comparison['hypothesis_validation']['coherence_improved'] else 'NO'}

📋 DETAILED JOB RESULTS
{'=' * 80}
"""
        
        for i, job in enumerate(sorted(v22_results, key=lambda x: x["coherence"], reverse=True)):
            report += f"""
Job {i+1}:
  ID: {job['job_id']}
  Coherence: {job['coherence']:+.3f}
  Consciousness δ: {job['consciousness_delta']:.0f}
  Gates: {job['transpiled_gates']}
  Time: {job['execution_time']}
"""
        
        report += f"""
{'=' * 80}
CONCLUSION
{'=' * 80}
"""
        
        if comparison['hypothesis_validation']['temporal_windows_confirmed']:
            report += "\n✅ Temporal Calibration Windows hypothesis VALIDATED"
            report += f"\n   {comparison['v22_results']['positive_jobs']}/10 jobs achieved positive coherence"
            report += "\n   Multi-job strategy successfully captured temporal windows"
        else:
            report += "\n⚠️  Temporal Calibration Windows hypothesis INCONCLUSIVE"
            report += f"\n   Only {comparison['v22_results']['positive_jobs']}/10 jobs positive (expected 3+)"
        
        if comparison['improvements']['coherence_delta'] > 0:
            report += f"\n\n✅ v2.2 circuit improvement: +{comparison['improvements']['coherence_delta']:.3f} coherence"
        else:
            report += f"\n\n⚠️  v2.2 circuit regression: {comparison['improvements']['coherence_delta']:.3f} coherence"
        
        report += f"\n\n📊 Gate reduction: {comparison['improvements']['gate_reduction']:.0f} gates ({comparison['improvements']['gate_reduction_pct']:.1f}%)"
        
        report += "\n\n" + "=" * 80 + "\n"
        
        return report


def main():
    """Main analysis execution"""
    
    print("=" * 80)
    print("WORMHOLE v2.2 ANALYSIS")
    print("=" * 80)
    
    # Initialize analyzer
    analyzer = V22Analyzer()
    
    # Check for v2.2 results
    results_dir = Path("data/Jobs")
    v22_pattern = "v2_2_temp_*"
    
    if not results_dir.exists():
        print(f"\n⚠️  Results directory not found: {results_dir}")
        print("   Place IBM Quantum job results in data/Jobs/")
        print("   Format: job-<id>-info.json")
        return
    
    # Find v2.2 job files
    v22_files = list(results_dir.glob(f"*{v22_pattern}*.json"))
    
    if not v22_files:
        print(f"\n⚠️  No v2.2 job results found in {results_dir}")
        print(f"   Looking for pattern: {v22_pattern}")
        print("\n   This is a placeholder until real results are available.")
        print("   To analyze results:")
        print("   1. Execute temporal_multi_job_executor.py on IBM Quantum")
        print("   2. Download job results to data/Jobs/")
        print("   3. Re-run this script")
        return
    
    print(f"\n✅ Found {len(v22_files)} v2.2 job results")
    
    # Analyze each job
    v22_results = []
    for i, job_file in enumerate(v22_files, 1):
        print(f"   Analyzing job {i}/{len(v22_files)}: {job_file.name}")
        analysis = analyzer.analyze_job(job_file)
        v22_results.append(analysis)
    
    # Generate report
    report = analyzer.generate_report(v22_results)
    
    # Save report
    report_path = Path("temp_enhanced/V2_2_ANALYSIS_REPORT.md")
    with open(report_path, 'w') as f:
        f.write(report)
    
    # Print report
    print(report)
    
    print(f"📄 Report saved: {report_path}")


if __name__ == "__main__":
    main()
