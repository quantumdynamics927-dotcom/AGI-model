"""
Analyze Symmetry Breaking

Statistical analysis of observer symmetry experiment results.

Usage:
    python analyze_symmetry_breaking.py --input results/baseline_3q_*.json
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
from scipy import stats


def load_results(filepath: Path) -> dict:
    """Load experiment results from JSON file."""
    with open(filepath, "r") as f:
        return json.load(f)


def kl_divergence(p: np.ndarray, q: np.ndarray, epsilon: float = 1e-10) -> float:
    """Compute KL divergence D_KL(p || q)."""
    p = np.clip(p, epsilon, 1.0)
    q = np.clip(q, epsilon, 1.0)
    return float(np.sum(p * np.log(p / q)))


def chi_square_test(observed: np.ndarray, expected: np.ndarray) -> tuple:
    """
    Perform chi-square test comparing observed to expected distribution.

    Returns:
        (chi2_statistic, p_value)
    """
    # Scale to counts
    total_obs = np.sum(observed)
    observed_counts = observed * total_obs
    expected_counts = expected * total_obs

    # Avoid division by zero
    expected_counts = np.clip(expected_counts, 1e-10, None)

    chi2, p = stats.chisquare(observed_counts, expected_counts)
    return chi2, p


def ks_test(sample1: np.ndarray, sample2: np.ndarray) -> tuple:
    """
    Perform two-sample Kolmogorov-Smirnov test.

    Returns:
        (ks_statistic, p_value)
    """
    return stats.ks_2samp(sample1, sample2)


def bootstrap_ci(
    data: np.ndarray, statistic: callable, n_bootstrap: int = 1000, ci: float = 0.95
) -> tuple:
    """
    Compute bootstrap confidence interval.

    Args:
        data: Input data
        statistic: Function to compute statistic
        n_bootstrap: Number of bootstrap samples
        ci: Confidence level (0.95 for 95% CI)

    Returns:
        (lower_bound, upper_bound)
    """
    bootstrap_stats = []
    n = len(data)

    for _ in range(n_bootstrap):
        sample = np.random.choice(data, size=n, replace=True)
        bootstrap_stats.append(statistic(sample))

    alpha = 1 - ci
    lower = np.percentile(bootstrap_stats, alpha / 2 * 100)
    upper = np.percentile(bootstrap_stats, (1 - alpha / 2) * 100)

    return lower, upper


def compute_detection_score(
    kl_divergence: float,
    symmetry_loss: float,
    entropy_loss: float,
    weights: Optional[Dict[str, float]] = None,
) -> float:
    """
    Compute composite detection score.

    Args:
        kl_divergence: KL divergence from baseline
        symmetry_loss: Loss in symmetry score
        entropy_loss: Loss in min-entropy
        weights: Custom weights for each component

    Returns:
        Detection score (higher = more likely tampered)
    """
    if weights is None:
        weights = {"kl": 0.4, "symmetry": 0.3, "entropy": 0.3}

    return (
        weights["kl"] * kl_divergence
        + weights["symmetry"] * symmetry_loss
        + weights["entropy"] * entropy_loss
    )


def analyze_experiment(results: dict) -> dict:
    """
    Perform complete analysis of experiment results.

    Args:
        results: Loaded experiment results

    Returns:
        Analysis dictionary with all metrics and tests
    """
    analysis = {
        "experiment_info": {
            "timestamp": results["timestamp"],
            "shots": results["shots"],
            "backend": results["backend"],
            "seed": results["seed"],
        },
        "modes": {},
        "comparisons": {},
        "detection_analysis": {},
    }

    # Extract baseline distribution (center qubit only)
    baseline_dist = np.array(results["modes"]["none"]["distribution"])
    baseline_symmetry = results["modes"]["none"]["symmetry_score"]
    baseline_entropy = results["modes"]["none"]["min_entropy"]

    # Analyze each mode
    for mode_name, mode_data in results["modes"].items():
        if mode_name == "none":
            continue

        # Extract center qubit marginal for fair comparison with baseline
        # For 3-qubit measurement, extract marginal of center qubit (Q1)
        counts = mode_data["counts"]
        total = sum(counts.values())
        p_center_0 = 0.0
        p_center_1 = 0.0

        for bitstring, count in counts.items():
            if isinstance(bitstring, str):
                bits = bitstring.zfill(3)
                center_bit = bits[1]  # Middle bit is center qubit
            else:
                center_bit = "1" if (bitstring >> 1) & 1 else "0"

            if center_bit == "0":
                p_center_0 += count / total
            else:
                p_center_1 += count / total

        center_marginal = np.array([p_center_0, p_center_1])

        mode_symmetry = mode_data["symmetry_score"]
        mode_entropy = mode_data["min_entropy"]

        # Compute metrics using center marginal
        kl_div = kl_divergence(center_marginal, baseline_dist)
        symmetry_loss = baseline_symmetry - mode_symmetry
        entropy_loss = baseline_entropy - mode_entropy

        # Statistical tests
        chi2, chi2_p = chi_square_test(center_marginal, baseline_dist)

        # Detection score
        detection_score = compute_detection_score(
            kl_div, abs(symmetry_loss), abs(entropy_loss)
        )

        analysis["modes"][mode_name] = {
            "kl_divergence": kl_div,
            "symmetry_loss": symmetry_loss,
            "entropy_loss": entropy_loss,
            "chi_square": {
                "statistic": chi2,
                "p_value": chi2_p,
                "significant": chi2_p < 0.01,
            },
            "detection_score": detection_score,
            "detected": detection_score > 0.1,
        }

    # Compare left vs right interception
    if "left" in analysis["modes"] and "right" in analysis["modes"]:
        left_score = analysis["modes"]["left"]["detection_score"]
        right_score = analysis["modes"]["right"]["detection_score"]

        analysis["comparisons"]["left_vs_right"] = {
            "left_detection_score": left_score,
            "right_detection_score": right_score,
            "difference": abs(left_score - right_score),
            "symmetric": abs(left_score - right_score) < 0.05,
        }

    # Overall detection analysis
    detected_modes = [
        mode for mode, data in analysis["modes"].items() if data["detected"]
    ]

    analysis["detection_analysis"] = {
        "modes_detected": detected_modes,
        "detection_rate": len(detected_modes) / max(len(analysis["modes"]), 1),
        "best_detection": max(
            analysis["modes"].items(),
            key=lambda x: x[1]["detection_score"],
            default=(None, {"detection_score": 0}),
        )[0],
    }

    return analysis


def generate_report(analysis: dict) -> str:
    """
    Generate human-readable report from analysis.

    Args:
        analysis: Analysis dictionary

    Returns:
        Formatted report string
    """
    lines = [
        "# Observer Symmetry Analysis Report",
        "",
        "## Experiment Info",
        f"- Timestamp: {analysis['experiment_info']['timestamp']}",
        f"- Shots: {analysis['experiment_info']['shots']}",
        f"- Backend: {analysis['experiment_info']['backend']}",
        "",
        "## Mode Analysis",
        "",
    ]

    for mode_name, mode_data in analysis["modes"].items():
        lines.extend(
            [
                f"### {mode_name.upper()} Interception",
                f"- KL Divergence: {mode_data['kl_divergence']:.4f}",
                f"- Symmetry Loss: {mode_data['symmetry_loss']:.4f}",
                f"- Entropy Loss: {mode_data['entropy_loss']:.4f}",
                f"- Detection Score: {mode_data['detection_score']:.4f}",
                f"- Chi-square p-value: {mode_data['chi_square']['p_value']:.4f}",
                f"- Significant (p<0.01): {'Yes' if mode_data['chi_square']['significant'] else 'No'}",
                f"- **Detected**: {'Yes' if mode_data['detected'] else 'No'}",
                "",
            ]
        )

    if "left_vs_right" in analysis.get("comparisons", {}):
        comp = analysis["comparisons"]["left_vs_right"]
        lines.extend(
            [
                "## Left vs Right Comparison",
                f"- Left Detection Score: {comp['left_detection_score']:.4f}",
                f"- Right Detection Score: {comp['right_detection_score']:.4f}",
                f"- Difference: {comp['difference']:.4f}",
                f"- Symmetric: {'Yes' if comp['symmetric'] else 'No'}",
                "",
            ]
        )

    det = analysis["detection_analysis"]
    lines.extend(
        [
            "## Detection Summary",
            f"- Modes Detected: {', '.join(det['modes_detected']) or 'None'}",
            f"- Detection Rate: {det['detection_rate']:.1%}",
            f"- Best Detection: {det['best_detection'] or 'N/A'}",
            "",
        ]
    )

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Analyze symmetry breaking")
    parser.add_argument("--input", type=str, required=True, help="Input JSON file")
    parser.add_argument("--output", type=str, default=None, help="Output report file")

    args = parser.parse_args()

    # Load results
    results = load_results(Path(args.input))

    # Analyze
    analysis = analyze_experiment(results)

    # Generate report
    report = generate_report(analysis)

    # Output
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            f.write(report)
        print(f"Report saved to: {output_path}")
    else:
        print(report)

    # Also save analysis as JSON
    analysis_path = Path(args.input).with_suffix(".analysis.json")
    with open(analysis_path, "w") as f:
        json.dump(analysis, f, indent=2, default=str)
    print(f"Analysis saved to: {analysis_path}")


if __name__ == "__main__":
    main()
