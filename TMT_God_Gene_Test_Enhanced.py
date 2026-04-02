"""
TMT-OS GOD GENE TEST: ENHANCED WITH CONTROLS AND STATISTICAL VALIDATION
DNA Sequence Analysis using Quantum-Phi Framework

Enhanced version with:
- Negative controls (shuffled sequences)
- Multiple temporal window classes
- Statistical separation analysis
- Real biological sequence panels
- Gain independence testing

Tests the hypothesis that different genetic elements exhibit distinct
quantum-phi signatures with proper statistical controls.
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from scipy import stats as scipy_stats
import random
from TMT_Unified_Analyzer import UnifiedDNAAnalyzer

# ==============================================================================
# SEQUENCE PANELS
# ==============================================================================

# Target motifs (original hypothesis)
TARGET_MOTIFS = {
    "TATA Box (Anchor)": "TATAAAA",
    "Kozak ATG (Spark)": "ACCATGG",
}

# Negative controls: shuffled versions of target motifs
def generate_shuffled_controls(sequences: Dict[str, str], n_shuffles: int = 5) -> Dict[str, str]:
    """Generate shuffled sequence controls for each motif."""
    shuffled = {}
    for name, seq in sequences.items():
        for i in range(n_shuffles):
            seq_list = list(seq)
            random.shuffle(seq_list)
            shuffled_seq = ''.join(seq_list)
            # Ensure shuffled is different from original
            while shuffled_seq == seq:
                random.shuffle(seq_list)
                shuffled_seq = ''.join(seq_list)
            shuffled[f"{name} (Shuffle {i+1})"] = shuffled_seq
    return shuffled

# Real biological sequence panels
BIOLOGICAL_PANELS = {
    # Promoter regions (TATA-containing)
    "Promoter": [
        "TATAAAA",  # Canonical TATA box
        "TATATAA",  # Variant TATA
        "TATAAAT",  # Extended TATA
        "TATATAT",  # Repetitive TATA
        "CTATAAA",  # TATA variant
    ],
    
    # Exon regions (coding)
    "Exon": [
        "ATGGCTA",  # Start codon context
        "GCTAGCT",  # Coding sequence
        "ATGCATG",  # Mixed coding
        "GCATGCA",  # GC-rich exon
        "ATGATGA",  # Repetitive coding
    ],
    
    # Intron regions (non-coding splice)
    "Intron": [
        "GTATAGT",  # Splice donor/acceptor
        "GTAAGTA",  # Splice signals
        "AGGTAGT",  # Branch point
        "TTTAAAA",  # Poly-pyrimidine tract
        "GTAAGTN",  # Intron boundary
    ],
    
    # Repetitive elements
    "Repeat": [
        "AAAAAAA",  # Poly-A
        "TTTTTTT",  # Poly-T
        "CACACAC",  # CA repeat
        "ATATATA",  # AT repeat
        "GCGCGCG",  # GC repeat
    ],
    
    # Non-functional background (random composition)
    "Nonfunctional": [
        "NNNNNNN",  # Unknown bases
        "RYRYRYR",  # Purine-pyrimidine pattern
        "ATCGATC",  # Random
        "GCTAGCT",  # Random
        "ATGCATG",  # Random
    ],
}

# Kozak sequence variants
KOZAK_VARIANTS = {
    "Kozak Strong": "ACCATGG",  # Optimal Kozak
    "Kozak Moderate": "GCCATGG",  # Moderate context
    "Kozak Weak": "AAAATGG",  # Weak context
    "Kozak Minimal": "ATGATGA",  # Minimal context
}

# ==============================================================================
# TEMPORAL WINDOW CLASSIFICATION
# ==============================================================================

class TemporalWindowClassifier:
    """
    Classify sequences into temporal window classes based on phi-correlation
    and gain metrics. Multiple classes can appear in output.
    """
    
    # Thresholds for classification (redesigned for multiple classes)
    PHI_THRESHOLDS = {
        "CRYSTALLINE": (0.60, 1.00),   # High phi-correlation, static
        "ORDERED": (0.45, 0.60),       # Moderate-high phi
        "BALANCED": (0.35, 0.45),      # Intermediate
        "DYNAMIC": (0.25, 0.35),        # Moderate-low phi
        "RESONANT": (0.00, 0.25),      # Low phi-correlation, dynamic
    }
    
    GAIN_THRESHOLDS = {
        "HIGH_GAIN": (1.5, 2.0),        # High dynamic potential
        "MODERATE_GAIN": (1.0, 1.5),   # Moderate dynamic
        "LOW_GAIN": (0.5, 1.0),         # Low dynamic
        "STATIC": (0.1, 0.5),           # Near-static
    }
    
    COHERENCE_THRESHOLDS = {
        "HIGH_COHERENCE": (0.5, 1.0),    # Strong quantum coherence
        "MODERATE_COHERENCE": (0.2, 0.5),
        "LOW_COHERENCE": (0.0, 0.2),    # Weak coherence
    }
    
    @classmethod
    def classify(cls, phi_corr: float, gain: float, coherence: float) -> Dict[str, List[str]]:
        """
        Classify sequence into multiple window classes.
        
        Returns dict with categories and their applicable classes.
        """
        result = {
            "phi_class": [],
            "gain_class": [],
            "coherence_class": [],
            "composite_role": None,
        }
        
        # Phi-correlation classes (can be multiple if on boundary)
        for class_name, (low, high) in cls.PHI_THRESHOLDS.items():
            if low <= phi_corr < high:
                result["phi_class"].append(class_name)
            # Allow overlap at boundaries (±5%)
            elif low * 0.95 <= phi_corr < high * 1.05:
                result["phi_class"].append(f"{class_name}*")
        
        # Gain classes
        for class_name, (low, high) in cls.GAIN_THRESHOLDS.items():
            if low <= gain < high:
                result["gain_class"].append(class_name)
            elif low * 0.95 <= gain < high * 1.05:
                result["gain_class"].append(f"{class_name}*")
        
        # Coherence classes
        for class_name, (low, high) in cls.COHERENCE_THRESHOLDS.items():
            if low <= coherence < high:
                result["coherence_class"].append(class_name)
            elif low * 0.95 <= coherence < high * 1.05:
                result["coherence_class"].append(f"{class_name}*")
        
        # Composite role determination
        result["composite_role"] = cls._determine_composite_role(
            result["phi_class"], result["gain_class"], result["coherence_class"]
        )
        
        return result
    
    @classmethod
    def _determine_composite_role(cls, phi_classes: List, gain_classes: List, coh_classes: List) -> str:
        """Determine composite biological role from all metrics."""
        # Extract primary classes (without boundary markers)
        phi_primary = [c.rstrip('*') for c in phi_classes if c]
        gain_primary = [c.rstrip('*') for c in gain_classes if c]
        coh_primary = [c.rstrip('*') for c in coh_classes if c]
        
        # Role determination logic
        if "CRYSTALLINE" in phi_primary:
            if "STATIC" in gain_primary:
                return "STATIC ANCHOR (Crystal)"
            else:
                return "RIGID TEMPLATE"
        elif "RESONANT" in phi_primary:
            if "HIGH_GAIN" in gain_primary:
                return "RESONANT DRIVER (Life)"
            else:
                return "DYNAMIC ELEMENT"
        elif "ORDERED" in phi_primary:
            return "STRUCTURED ELEMENT"
        elif "BALANCED" in phi_primary:
            return "TRANSITIONAL ELEMENT"
        elif "DYNAMIC" in phi_primary:
            return "FLEXIBLE ELEMENT"
        else:
            return "UNCLASSIFIED"


# ==============================================================================
# GAIN INDEPENDENCE ANALYSIS
# ==============================================================================

def analyze_gain_independence(results: List[Dict]) -> Dict:
    """
    Analyze whether gain provides independent information beyond phi-correlation.
    
    Tests:
    1. Correlation between phi and gain
    2. Mutual information
    3. Variance explained
    """
    phi_values = [r["phi_corr"] for r in results]
    gain_values = [r["gain"] for r in results]
    
    # Pearson correlation
    if len(phi_values) > 2:
        corr, p_value = scipy_stats.pearsonr(phi_values, gain_values)
    else:
        corr, p_value = 0.0, 1.0
    
    # Linear regression (gain ~ phi)
    if len(phi_values) > 2:
        slope, intercept, r_value, p_val, std_err = scipy_stats.linregress(phi_values, gain_values)
        r_squared = r_value ** 2
    else:
        slope, intercept, r_squared, p_val, std_err = 0.0, 0.0, 0.0, 1.0, 0.0
    
    # Variance of gain not explained by phi
    residual_variance = 1.0 - r_squared if r_squared < 1.0 else 0.0
    
    return {
        "pearson_correlation": corr,
        "correlation_p_value": p_value,
        "r_squared": r_squared,
        "slope": slope,
        "intercept": intercept,
        "residual_variance": residual_variance,
        "gain_independent": residual_variance > 0.1,  # >10% variance independent
        "interpretation": _interpret_gain_independence(corr, r_squared),
    }


def _interpret_gain_independence(corr: float, r_squared: float) -> str:
    """Generate interpretation of gain independence."""
    if r_squared > 0.95:
        return "Gain is nearly fully determined by phi (redundant metric)"
    elif r_squared > 0.8:
        return "Gain is strongly predicted by phi (limited independent information)"
    elif r_squared > 0.5:
        return "Gain has moderate independence from phi"
    else:
        return "Gain provides substantial independent information beyond phi"


# ==============================================================================
# STATISTICAL SEPARATION ANALYSIS
# ==============================================================================

def analyze_statistical_separation(category_results: Dict[str, List[Dict]]) -> Dict:
    """
    Test whether categories separate statistically.
    
    Uses ANOVA and post-hoc tests to determine if categories differ.
    """
    categories = list(category_results.keys())
    
    # Collect metrics by category
    phi_by_category = {cat: [r["phi_corr"] for r in results] 
                       for cat, results in category_results.items()}
    gain_by_category = {cat: [r["gain"] for r in results] 
                        for cat, results in category_results.items()}
    coh_by_category = {cat: [r["coherence"] for r in results] 
                       for cat, results in category_results.items()}
    
    results = {
        "phi_correlation": {},
        "gain": {},
        "coherence": {},
        "category_summary": {},
    }
    
    # ANOVA for phi-correlation
    if len(categories) > 1:
        phi_groups = [phi_by_category[cat] for cat in categories if phi_by_category[cat]]
        if len(phi_groups) > 1 and all(len(g) > 0 for g in phi_groups):
            f_stat, p_value = scipy_stats.f_oneway(*phi_groups)
            results["phi_correlation"] = {
                "anova_f": f_stat,
                "anova_p": p_value,
                "significant": p_value < 0.05,
            }
    
    # ANOVA for gain
    if len(categories) > 1:
        gain_groups = [gain_by_category[cat] for cat in categories if gain_by_category[cat]]
        if len(gain_groups) > 1 and all(len(g) > 0 for g in gain_groups):
            f_stat, p_value = scipy_stats.f_oneway(*gain_groups)
            results["gain"] = {
                "anova_f": f_stat,
                "anova_p": p_value,
                "significant": p_value < 0.05,
            }
    
    # ANOVA for coherence
    if len(categories) > 1:
        coh_groups = [coh_by_category[cat] for cat in categories if coh_by_category[cat]]
        if len(coh_groups) > 1 and all(len(g) > 0 for g in coh_groups):
            f_stat, p_value = scipy_stats.f_oneway(*coh_groups)
            results["coherence"] = {
                "anova_f": f_stat,
                "anova_p": p_value,
                "significant": p_value < 0.05,
            }
    
    # Category summary statistics
    for cat in categories:
        results["category_summary"][cat] = {
            "n": len(category_results[cat]),
            "phi_mean": np.mean(phi_by_category[cat]) if phi_by_category[cat] else 0,
            "phi_std": np.std(phi_by_category[cat]) if phi_by_category[cat] else 0,
            "gain_mean": np.mean(gain_by_category[cat]) if gain_by_category[cat] else 0,
            "gain_std": np.std(gain_by_category[cat]) if gain_by_category[cat] else 0,
            "coh_mean": np.mean(coh_by_category[cat]) if coh_by_category[cat] else 0,
            "coh_std": np.std(coh_by_category[cat]) if coh_by_category[cat] else 0,
        }
    
    return results


# ==============================================================================
# MAIN ANALYSIS
# ==============================================================================

def analyze_sequence(seq: str, name: str = "") -> Dict:
    """Analyze a single sequence and return all metrics."""
    analyzer = UnifiedDNAAnalyzer(seq)
    phi_corr, fractal = analyzer.analyze_static_geometry()
    gain = analyzer.predict_dynamic_gain(phi_corr)
    coherence, metrics = analyzer.run_quantum_simulation(gain)
    
    classification = TemporalWindowClassifier.classify(phi_corr, gain, coherence)
    
    return {
        "name": name,
        "sequence": seq,
        "phi_corr": phi_corr,
        "fractal": fractal,
        "gain": gain,
        "coherence": coherence,
        "entropy": metrics.get("entanglement_entropy", 0),
        "fidelity": metrics.get("fidelity", 0),
        "classification": classification,
    }


def print_results_table(results: List[Dict], title: str = "RESULTS"):
    """Print results in formatted table."""
    print(f"\n{'='*120}")
    print(f"{title}")
    print(f"{'='*120}")
    
    header = f"{'SEQUENCE':<25} | {'PHI-CORR':<10} | {'GAIN':<8} | {'COHERENCE':<10} | {'PHI CLASS':<18} | {'ROLE'}"
    print(header)
    print("-" * 120)
    
    for r in results:
        phi_class = r["classification"]["phi_class"][0] if r["classification"]["phi_class"] else "N/A"
        role = r["classification"]["composite_role"] or "N/A"
        print(f"{r['name']:<25} | {r['phi_corr']:.4f}     | {r['gain']:.4f} | {r['coherence']:.4f}    | {phi_class:<18} | {role}")


def main():
    """Run comprehensive analysis with controls and statistics."""
    random.seed(42)  # Reproducibility
    
    print("=" * 120)
    print("TMT-OS GOD GENE TEST: ENHANCED WITH CONTROLS AND STATISTICAL VALIDATION")
    print("=" * 120)
    
    all_results = []
    category_results = {}
    
    # ==========================================================================
    # 1. TARGET MOTIFS (Original Hypothesis)
    # ==========================================================================
    print("\n" + "=" * 120)
    print("1. TARGET MOTIFS (Original Hypothesis)")
    print("=" * 120)
    
    target_results = []
    for name, seq in TARGET_MOTIFS.items():
        result = analyze_sequence(seq, name)
        target_results.append(result)
        all_results.append(result)
    
    category_results["Target_Motifs"] = target_results
    print_results_table(target_results, "TARGET MOTIFS")
    
    # ==========================================================================
    # 2. SHUFFLED CONTROLS (Negative Controls)
    # ==========================================================================
    print("\n" + "=" * 120)
    print("2. SHUFFLED CONTROLS (Negative Controls)")
    print("=" * 120)
    
    shuffled_controls = generate_shuffled_controls(TARGET_MOTIFS, n_shuffles=3)
    shuffled_results = []
    for name, seq in shuffled_controls.items():
        result = analyze_sequence(seq, name)
        shuffled_results.append(result)
        all_results.append(result)
    
    category_results["Shuffled_Controls"] = shuffled_results
    print_results_table(shuffled_results, "SHUFFLED CONTROLS")
    
    # ==========================================================================
    # 3. BIOLOGICAL PANELS
    # ==========================================================================
    print("\n" + "=" * 120)
    print("3. BIOLOGICAL PANELS")
    print("=" * 120)
    
    for panel_name, sequences in BIOLOGICAL_PANELS.items():
        panel_results = []
        for i, seq in enumerate(sequences):
            # Handle ambiguous bases
            clean_seq = seq.replace('N', 'A').replace('R', 'A').replace('Y', 'T')
            result = analyze_sequence(clean_seq, f"{panel_name}_{i+1}")
            panel_results.append(result)
            all_results.append(result)
        
        category_results[panel_name] = panel_results
        print_results_table(panel_results, f"{panel_name.upper()} PANEL")
    
    # ==========================================================================
    # 4. KOZAK VARIANTS
    # ==========================================================================
    print("\n" + "=" * 120)
    print("4. KOZAK SEQUENCE VARIANTS")
    print("=" * 120)
    
    kozak_results = []
    for name, seq in KOZAK_VARIANTS.items():
        result = analyze_sequence(seq, name)
        kozak_results.append(result)
        all_results.append(result)
    
    category_results["Kozak_Variants"] = kozak_results
    print_results_table(kozak_results, "KOZAK VARIANTS")
    
    # ==========================================================================
    # 5. GAIN INDEPENDENCE ANALYSIS
    # ==========================================================================
    print("\n" + "=" * 120)
    print("5. GAIN INDEPENDENCE ANALYSIS")
    print("=" * 120)
    
    gain_analysis = analyze_gain_independence(all_results)
    
    print(f"\nPhi-Gain Correlation: r = {gain_analysis['pearson_correlation']:.4f}")
    print(f"R-squared: {gain_analysis['r_squared']:.4f}")
    print(f"Residual Variance: {gain_analysis['residual_variance']:.4f}")
    print(f"Gain Independent: {gain_analysis['gain_independent']}")
    print(f"\nInterpretation: {gain_analysis['interpretation']}")
    
    # ==========================================================================
    # 6. STATISTICAL SEPARATION ANALYSIS
    # ==========================================================================
    print("\n" + "=" * 120)
    print("6. STATISTICAL SEPARATION ANALYSIS")
    print("=" * 120)
    
    separation = analyze_statistical_separation(category_results)
    
    print("\n--- ANOVA Results ---")
    for metric in ["phi_correlation", "gain", "coherence"]:
        if separation[metric]:
            sig_marker = "***" if separation[metric]["anova_p"] < 0.001 else "**" if separation[metric]["anova_p"] < 0.01 else "*" if separation[metric]["anova_p"] < 0.05 else ""
            print(f"{metric.upper()}: F = {separation[metric]['anova_f']:.4f}, p = {separation[metric]['anova_p']:.4f} {sig_marker}")
    
    print("\n--- Category Summary ---")
    print(f"{'CATEGORY':<20} | {'N':>4} | {'PHI (mean±std)':<18} | {'GAIN (mean±std)':<18} | {'COH (mean±std)':<18}")
    print("-" * 100)
    for cat, stats in separation["category_summary"].items():
        phi_str = f"{stats['phi_mean']:.3f}±{stats['phi_std']:.3f}"
        gain_str = f"{stats['gain_mean']:.3f}±{stats['gain_std']:.3f}"
        coh_str = f"{stats['coh_mean']:.4f}±{stats['coh_std']:.4f}"
        print(f"{cat:<20} | {stats['n']:>4} | {phi_str:<18} | {gain_str:<18} | {coh_str:<18}")
    
    # ==========================================================================
    # 7. HYPOTHESIS VALIDATION
    # ==========================================================================
    print("\n" + "=" * 120)
    print("7. HYPOTHESIS VALIDATION")
    print("=" * 120)
    
    # Compare target motifs vs shuffled controls
    target_phi = [r["phi_corr"] for r in target_results]
    shuffled_phi = [r["phi_corr"] for r in shuffled_results]
    
    if len(target_phi) > 0 and len(shuffled_phi) > 0:
        t_stat, t_p = scipy_stats.ttest_ind(target_phi, shuffled_phi)
        print(f"\nTarget vs Shuffled (Phi-Correlation):")
        print(f"  Target mean: {np.mean(target_phi):.4f}")
        print(f"  Shuffled mean: {np.mean(shuffled_phi):.4f}")
        print(f"  t-statistic: {t_stat:.4f}")
        print(f"  p-value: {t_p:.4f}")
        print(f"  Significant: {'YES' if t_p < 0.05 else 'NO'}")
    
    # Compare biological categories
    print("\n--- Biological Category Separation ---")
    bio_categories = ["Promoter", "Exon", "Intron", "Repeat", "Nonfunctional"]
    bio_phi_values = {cat: [r["phi_corr"] for r in category_results.get(cat, [])] for cat in bio_categories}
    
    # Pairwise comparisons
    print("\nPairwise t-tests (Phi-Correlation):")
    comparisons_done = []
    for i, cat1 in enumerate(bio_categories):
        for cat2 in bio_categories[i+1:]:
            if bio_phi_values[cat1] and bio_phi_values[cat2]:
                t_stat, p_val = scipy_stats.ttest_ind(bio_phi_values[cat1], bio_phi_values[cat2])
                sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else ""
                comparisons_done.append((cat1, cat2, t_stat, p_val, sig))
    
    # Show top significant differences
    comparisons_done.sort(key=lambda x: x[3])
    for cat1, cat2, t_stat, p_val, sig in comparisons_done[:5]:
        print(f"  {cat1} vs {cat2}: t={t_stat:.3f}, p={p_val:.4f} {sig}")
    
    # ==========================================================================
    # 8. CONCLUSIONS
    # ==========================================================================
    print("\n" + "=" * 120)
    print("8. CONCLUSIONS")
    print("=" * 120)
    
    print("\n--- Key Findings ---")
    
    # Gain independence
    if gain_analysis["gain_independent"]:
        print(f"✓ Gain provides independent information (residual variance = {gain_analysis['residual_variance']:.1%})")
    else:
        print(f"✗ Gain is largely redundant with phi-correlation (R² = {gain_analysis['r_squared']:.3f})")
    
    # Category separation
    phi_sig = separation["phi_correlation"].get("significant", False)
    gain_sig = separation["gain"].get("significant", False)
    
    if phi_sig:
        print(f"✓ Categories separate significantly on phi-correlation (p < 0.05)")
    else:
        print(f"✗ Categories do NOT separate significantly on phi-correlation")
    
    if gain_sig:
        print(f"✓ Categories separate significantly on gain (p < 0.05)")
    else:
        print(f"✗ Categories do NOT separate significantly on gain")
    
    # Target vs control separation
    if len(target_phi) > 0 and len(shuffled_phi) > 0:
        if t_p < 0.05:
            print(f"✓ Target motifs differ from shuffled controls (p = {t_p:.4f})")
        else:
            print(f"✗ Target motifs do NOT differ from shuffled controls (p = {t_p:.4f})")
    
    print("\n--- Recommendations ---")
    print("1. Expand sequence panels with more biological examples per category")
    print("2. Consider gain as derived metric unless independent variance > 10%")
    print("3. Use shuffled controls as baseline for motif composition effects")
    print("4. Validate temporal window thresholds on larger datasets")


if __name__ == "__main__":
    main()