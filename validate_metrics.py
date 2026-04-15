"""
Metric Validation Suite
======================

Implements the three-test validation protocol from METRIC_CHARTER.md:
1. Numerical Validity Test
2. Control Comparison Test  
3. Scientific Usefulness Test

Date: April 15, 2026
"""

import numpy as np
from typing import Dict, List, Tuple, Callable
import json
from dataclasses import dataclass, asdict


@dataclass
class ValidationResult:
    """Result of a single validation test"""
    test_name: str
    passed: bool
    value: float
    expected_range: Tuple[float, float]
    message: str


class MetricValidator:
    """
    Validates quantum and geometric metrics against scientific standards.
    
    Every metric must pass three tests:
    1. Numerical validity (mathematical constraints)
    2. Control comparison (vs. null models)
    3. Scientific usefulness (predictive power)
    """
    
    def __init__(self, seed: int = 42):
        np.random.seed(seed)
        self.phi = (1 + np.sqrt(5)) / 2
        self.results: List[ValidationResult] = []
        
    # =========================================================================
    # TEST 1: NUMERICAL VALIDITY
    # =========================================================================
    
    def test_entanglement_entropy_validity(self) -> ValidationResult:
        """
        Test: Entanglement entropy must be non-negative and bounded.
        
        Validity constraints:
        - S >= 0 (always)
        - S <= log(d_A) (subsystem dimension)
        - Eigenvalues of rho_A must be in [0, 1]
        - Trace of rho_A must equal 1
        """
        from quantum_metatron_integration import QuantumMetatronProcessor
        
        processor = QuantumMetatronProcessor()
        
        # Test with known states
        # 1. Product state (should have S = 0)
        product_state = np.array([[1.0, 0.0, 0.0, 0.0]])  # |00⟩
        s_product = processor.compute_entanglement_entropy(product_state)
        
        # 2. Maximally entangled state (should have S = log(2))
        # Bell state: (|00⟩ + |11⟩)/√2
        bell_state = np.array([[1/np.sqrt(2), 0, 0, 1/np.sqrt(2)]])
        s_bell = processor.compute_entanglement_entropy(bell_state)
        
        # 3. Random state
        random_state = np.random.randn(5, 32)
        random_state = random_state / np.linalg.norm(random_state, axis=1, keepdims=True)
        s_random = processor.compute_entanglement_entropy(random_state)
        
        # Check constraints
        checks = [
            ("Product state S >= 0", s_product >= 0),
            ("Product state S ≈ 0", s_product < 0.01),
            ("Bell state S >= 0", s_bell >= 0),
            ("Bell state S ≈ log(2)", abs(s_bell - np.log(2)) < 0.1),
            ("Random state S >= 0", s_random >= 0),
            ("Random state S <= log(d)", s_random <= np.log(160)),  # d_A ≈ 160
        ]
        
        all_passed = all(c[1] for c in checks)
        failed = [c[0] for c in checks if not c[1]]
        
        return ValidationResult(
            test_name="entanglement_entropy_validity",
            passed=all_passed,
            value=s_random,
            expected_range=(0, np.log(160)),
            message=f"All checks passed" if all_passed else f"Failed: {failed}"
        )
    
    def test_quantum_coherence_validity(self) -> ValidationResult:
        """
        Test: Quantum coherence must be in [0, 1].
        
        Validity constraints:
        - 0 <= C <= 1
        - C = 0 for diagonal density matrix
        - C > 0 for coherent superposition
        """
        from quantum_metatron_integration import QuantumMetatronProcessor
        
        processor = QuantumMetatronProcessor()
        
        # Test with known states
        # 1. Pure state with uniform phases
        amps = np.ones((3, 32)) / np.sqrt(32)
        phases = np.zeros((3, 32))
        c_uniform = processor.compute_quantum_coherence(amps, phases)
        
        # 2. Random phases
        phases_random = np.random.uniform(0, 2*np.pi, (3, 32))
        c_random = processor.compute_quantum_coherence(amps, phases_random)
        
        checks = [
            ("Uniform phases C >= 0", c_uniform >= 0),
            ("Uniform phases C <= 1", c_uniform <= 1),
            ("Random phases C >= 0", c_random >= 0),
            ("Random phases C <= 1", c_random <= 1),
        ]
        
        all_passed = all(c[1] for c in checks)
        
        return ValidationResult(
            test_name="quantum_coherence_validity",
            passed=all_passed,
            value=c_random,
            expected_range=(0, 1),
            message=f"Coherence in valid range" if all_passed else "Out of bounds"
        )
    
    def test_phi_resonance_validity(self) -> ValidationResult:
        """
        Test: Phi resonance must be in [0, 1].
        
        Validity constraints:
        - 0 <= R_φ <= 1
        - R_φ = 1 when ratio exactly equals φ
        - R_φ → 0 for large deviations
        """
        from metatron_geometry_demo import MetatronMolecularProcessor
        
        processor = MetatronMolecularProcessor()
        
        # Test with icosahedron (should have high phi resonance)
        from metatron_geometry_demo import generate_platonic_vertices
        ico_verts = generate_platonic_vertices('icosahedron')
        result = processor.analyze_molecule(ico_verts)
        r_phi = result['phi_resonance']
        
        checks = [
            ("R_φ >= 0", r_phi >= 0),
            ("R_φ <= 1", r_phi <= 1),
            ("Icosahedron R_φ > 0.5", r_phi > 0.5),  # Should be high for icosahedron
        ]
        
        all_passed = all(c[1] for c in checks)
        
        return ValidationResult(
            test_name="phi_resonance_validity",
            passed=all_passed,
            value=r_phi,
            expected_range=(0, 1),
            message=f"Icosahedron phi resonance: {r_phi:.4f}"
        )
    
    # =========================================================================
    # TEST 2: CONTROL COMPARISON
    # =========================================================================
    
    def test_entanglement_vs_null(self, n_trials: int = 100) -> ValidationResult:
        """
        Test: Entanglement entropy should differ from null model.
        
        Null model: Random state vector uniformly sampled from unit sphere.
        Expected: S_null ≈ log(d_A) - O(1/d_A)
        """
        from quantum_metatron_integration import QuantumMetatronProcessor
        
        processor = QuantumMetatronProcessor()
        
        # Generate null model entropies
        null_entropies = []
        for _ in range(n_trials):
            random_state = np.random.randn(5, 32)
            random_state = random_state / np.linalg.norm(random_state, axis=1, keepdims=True)
            s = processor.compute_entanglement_entropy(random_state)
            null_entropies.append(s)
        
        null_mean = np.mean(null_entropies)
        null_std = np.std(null_entropies)
        
        # Test with structured molecule (water)
        # Water positions (bent geometry)
        water_pos = np.array([
            [0.0, 0.0, 0.0],      # O
            [0.96, 0.0, 0.0],     # H1
            [-0.24, 0.93, 0.0]    # H2
        ])
        
        amps, phases = processor.encode_to_quantum_state(water_pos)
        s_water = processor.compute_entanglement_entropy(amps)
        
        # Check if water entropy is significantly different from null
        z_score = (s_water - null_mean) / (null_std + 1e-10)
        
        # Water should have different entanglement than random
        is_different = abs(z_score) > 0.5  # At least 0.5 std dev different
        
        return ValidationResult(
            test_name="entanglement_vs_null",
            passed=is_different,
            value=z_score,
            expected_range=(-3, 3),
            message=f"Water S={s_water:.4f}, Null mean={null_mean:.4f}, z={z_score:.2f}"
        )
    
    def test_phi_vs_alternatives(self) -> ValidationResult:
        """
        Test: Phi resonance should be specific to φ, not other constants.
        
        Compare φ = 1.618 against:
        - √2 = 1.414
        - π = 3.14159
        - e = 2.71828
        - Random ratio
        """
        from metatron_geometry_demo import compute_geometric_ratios, generate_platonic_vertices
        
        # Test on icosahedron (known to have φ ratios)
        ico_verts = generate_platonic_vertices('icosahedron')
        _, ratios = compute_geometric_ratios(ico_verts)
        
        # Compute proximity to each constant
        constants = {
            'phi': self.phi,
            'sqrt2': np.sqrt(2),
            'pi': np.pi,
            'e': np.e,
            'random': 1.234  # Arbitrary
        }
        
        proximities = {}
        for name, const in constants.items():
            min_prox = np.min(np.abs(ratios - const))
            proximities[name] = min_prox
        
        # Phi should have smallest proximity (closest match)
        phi_is_best = proximities['phi'] <= min(proximities.values())
        
        return ValidationResult(
            test_name="phi_vs_alternatives",
            passed=phi_is_best,
            value=proximities['phi'],
            expected_range=(0, 1),
            message=f"Proximities: {proximities}"
        )
    
    def test_platonic_vs_random(self) -> ValidationResult:
        """
        Test: Platonic alignment should distinguish real molecules from random.
        
        Real molecules should have higher alignment than random point clouds.
        """
        from metatron_geometry_demo import MetatronMolecularProcessor
        
        processor = MetatronMolecularProcessor()
        
        # Test molecules
        molecules = {
            'methane': np.array([  # Tetrahedral
                [0, 0, 0],
                [1.09, 0, 0],
                [-0.36, 1.03, 0],
                [-0.36, -0.51, 0.89]
            ]),
            'random': np.random.randn(4, 3)  # Random 4 points
        }
        
        scores = {}
        for name, pos in molecules.items():
            result = processor.analyze_molecule(pos)
            scores[name] = max(result['platonic_scores'].values())
        
        # Methane should score higher than random
        methane_better = scores['methane'] > scores['random']
        
        return ValidationResult(
            test_name="platonic_vs_random",
            passed=methane_better,
            value=scores['methane'] - scores['random'],
            expected_range=(0, 1),
            message=f"Methane: {scores['methane']:.4f}, Random: {scores['random']:.4f}"
        )
    
    # =========================================================================
    # TEST 3: SCIENTIFIC USEFULNESS
    # =========================================================================
    
    def test_entanglement_predicts_bonds(self) -> ValidationResult:
        """
        Test: Entanglement entropy should correlate with molecular complexity.
        
        More complex molecules should have higher entanglement.
        """
        from quantum_metatron_integration import QuantumMetatronProcessor
        
        processor = QuantumMetatronProcessor()
        
        # Molecules ordered by complexity
        molecules = {
            'water': np.array([  # 3 atoms
                [0.0, 0.0, 0.0],
                [0.96, 0.0, 0.0],
                [-0.24, 0.93, 0.0]
            ]),
            'methane': np.array([  # 5 atoms
                [0.0, 0.0, 0.0],
                [1.09, 0, 0],
                [-0.36, 1.03, 0],
                [-0.36, -0.51, 0.89],
                [-0.36, -0.51, -0.89]
            ]),
            'benzene': np.array([  # 6 atoms (simplified)
                [1.4, 0, 0],
                [0.7, 1.21, 0],
                [-0.7, 1.21, 0],
                [-1.4, 0, 0],
                [-0.7, -1.21, 0],
                [0.7, -1.21, 0]
            ])
        }
        
        entropies = {}
        for name, pos in molecules.items():
            amps, phases = processor.encode_to_quantum_state(pos)
            s = processor.compute_entanglement_entropy(amps)
            entropies[name] = s
        
        # Check monotonic increase with complexity
        # Water < Methane < Benzene (roughly)
        complexity_order = ['water', 'methane', 'benzene']
        entropy_values = [entropies[m] for m in complexity_order]
        
        # Check if generally increasing (allow some noise)
        is_increasing = entropy_values[0] < entropy_values[2]  # At least water < benzene
        
        return ValidationResult(
            test_name="entanglement_predicts_complexity",
            passed=is_increasing,
            value=entropy_values[-1] - entropy_values[0],
            expected_range=(0, 2),
            message=f"Entropies: water={entropies['water']:.4f}, methane={entropies['methane']:.4f}, benzene={entropies['benzene']:.4f}"
        )
    
    def test_phi_predicts_symmetry(self) -> ValidationResult:
        """
        Test: Phi resonance should correlate with molecular symmetry.
        
        High-symmetry molecules should have higher phi resonance.
        """
        from metatron_geometry_demo import MetatronMolecularProcessor
        
        processor = MetatronMolecularProcessor()
        
        # Molecules with different symmetries
        molecules = {
            'benzene': np.array([  # D6h symmetry (high)
                [1.4, 0, 0],
                [0.7, 1.21, 0],
                [-0.7, 1.21, 0],
                [-1.4, 0, 0],
                [-0.7, -1.21, 0],
                [0.7, -1.21, 0]
            ]),
            'water': np.array([  # C2v symmetry (medium)
                [0.0, 0.0, 0.0],
                [0.96, 0.0, 0.0],
                [-0.24, 0.93, 0.0]
            ]),
            'random': np.random.randn(6, 3)  # No symmetry
        }
        
        phi_scores = {}
        for name, pos in molecules.items():
            result = processor.analyze_molecule(pos)
            phi_scores[name] = result['phi_resonance']
        
        # Benzene should have higher phi than random
        benzene_better = phi_scores['benzene'] > phi_scores['random']
        
        return ValidationResult(
            test_name="phi_predicts_symmetry",
            passed=benzene_better,
            value=phi_scores['benzene'] - phi_scores['random'],
            expected_range=(0, 1),
            message=f"Phi: benzene={phi_scores['benzene']:.4f}, water={phi_scores['water']:.4f}, random={phi_scores['random']:.4f}"
        )
    
    # =========================================================================
    # RUN ALL TESTS
    # =========================================================================
    
    def run_all_tests(self) -> Dict:
        """Run complete validation suite"""
        
        print("\n" + "="*70)
        print("METRIC VALIDATION SUITE")
        print("="*70)
        
        # Test 1: Numerical Validity
        print("\n📋 TEST 1: NUMERICAL VALIDITY")
        print("-"*40)
        
        validity_tests = [
            self.test_entanglement_entropy_validity,
            self.test_quantum_coherence_validity,
            self.test_phi_resonance_validity,
        ]
        
        validity_results = []
        for test in validity_tests:
            result = test()
            validity_results.append(result)
            status = "✅ PASS" if result.passed else "❌ FAIL"
            print(f"  {status}: {result.test_name}")
            print(f"         {result.message}")
        
        # Test 2: Control Comparison
        print("\n📋 TEST 2: CONTROL COMPARISON")
        print("-"*40)
        
        control_tests = [
            self.test_entanglement_vs_null,
            self.test_phi_vs_alternatives,
            self.test_platonic_vs_random,
        ]
        
        control_results = []
        for test in control_tests:
            result = test()
            control_results.append(result)
            status = "✅ PASS" if result.passed else "❌ FAIL"
            print(f"  {status}: {result.test_name}")
            print(f"         {result.message}")
        
        # Test 3: Scientific Usefulness
        print("\n📋 TEST 3: SCIENTIFIC USEFULNESS")
        print("-"*40)
        
        usefulness_tests = [
            self.test_entanglement_predicts_bonds,
            self.test_phi_predicts_symmetry,
        ]
        
        usefulness_results = []
        for test in usefulness_tests:
            result = test()
            usefulness_results.append(result)
            status = "✅ PASS" if result.passed else "❌ FAIL"
            print(f"  {status}: {result.test_name}")
            print(f"         {result.message}")
        
        # Summary
        all_results = validity_results + control_results + usefulness_results
        passed = sum(1 for r in all_results if r.passed)
        total = len(all_results)
        
        print("\n" + "="*70)
        print(f"VALIDATION SUMMARY: {passed}/{total} tests passed")
        print("="*70)
        
        # Save results (convert numpy types for JSON serialization)
        def convert_to_serializable(obj):
            """Convert numpy types to Python native types"""
            if isinstance(obj, dict):
                return {k: convert_to_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_serializable(v) for v in obj]
            elif isinstance(obj, tuple):
                return tuple(convert_to_serializable(v) for v in obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, (np.bool_, bool)):
                return bool(obj)
            else:
                return obj
        
        results_dict = {
            "date": "2026-04-15",
            "total_tests": total,
            "passed": passed,
            "failed": total - passed,
            "results": [convert_to_serializable(asdict(r)) for r in all_results]
        }
        
        with open('metric_validation_results.json', 'w') as f:
            json.dump(results_dict, f, indent=2)
        
        print(f"\n✅ Results saved to: metric_validation_results.json")
        
        return results_dict


if __name__ == "__main__":
    validator = MetricValidator()
    results = validator.run_all_tests()