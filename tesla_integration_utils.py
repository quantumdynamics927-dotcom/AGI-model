"""Tesla integration utilities for Frequency Master (Node 11)

Safe, analysis-only utilities: entropy, mutual information, Fisher information,
fractal memory interface (lazy), visualization helpers, and a lightweight acoustic
discovery analyzer. All external/experimental integrations are lazy-imported and
non-essential by default.
"""
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
import math
import hashlib
import logging
import json
import os
from datetime import datetime

logger = logging.getLogger('tesla_utils')
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
    logger.addHandler(ch)

# Physical constants and metallic ratios
PHI = (1 + np.sqrt(5)) / 2
DELTA = 1 + np.sqrt(2)
EPSILON = (3 + np.sqrt(13)) / 2


class TeslaConsciousnessCalculator:
    """Unified consciousness calculator for Tesla geometric experiments.

    Calculates _oint = α·H + β·MI + γ·FI using information-theoretic foundations.
    """

    def __init__(self, alpha: float = 0.3, beta: float = 0.4, gamma: float = 0.3):
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        total = alpha + beta + gamma
        if not np.isclose(total, 1.0, atol=1e-6):
            self.alpha /= total
            self.beta /= total
            self.gamma /= total

    def calculate_entropy(self, counts: Dict[str, int]) -> float:
        total_shots = sum(counts.values())
        if total_shots == 0:
            return 0.0
        entropy = 0.0
        for c in counts.values():
            if c > 0:
                p = c / total_shots
                entropy -= p * math.log2(p)
        return float(entropy)

    def _extract_marginal(self, counts: Dict[str, int], n_qubits: int, indices: List[int]) -> Dict[str, float]:
        marginal = {}
        for state, cnt in counts.items():
            # state assumed MSB..LSB as string; handle variable lengths
            st = state.strip()
            if len(st) < n_qubits:
                st = st.zfill(n_qubits)
            # build marginal in order of indices
            key = ''.join(st[n_qubits - 1 - i] for i in indices)
            marginal[key] = marginal.get(key, 0) + cnt
        total = sum(marginal.values())
        if total == 0:
            return {}
        return {k: v / total for k, v in marginal.items()}

    def calculate_mutual_information(self, counts: Dict[str, int], qubit_pairs: List[Tuple[int, int]]) -> float:
        if not qubit_pairs:
            return 0.0
        keys = list(counts.keys())
        if not keys:
            return 0.0
        # Use the longest key to determine available qubits (handle variable-length keys)
        n_qubits = max(len(k) for k in keys)
        mi_vals = []
        for i, j in qubit_pairs:
            # Skip pairs that reference qubits beyond available length
            if i >= n_qubits or j >= n_qubits:
                logger.debug('Skipping qubit pair (%s,%s): exceeds available qubits (%s)', i, j, n_qubits)
                continue
            p_xi = self._extract_marginal(counts, n_qubits, [i])
            p_xj = self._extract_marginal(counts, n_qubits, [j])
            p_xixj = self._extract_marginal(counts, n_qubits, [i, j])
            # If any marginal is empty (e.g., no counts for those indices), skip the pair
            if not p_xi or not p_xj or not p_xixj:
                logger.debug('Skipping qubit pair (%s,%s): empty marginal', i, j)
                continue
            h_xi = -sum(p * math.log2(p) for p in p_xi.values() if p > 0)
            h_xj = -sum(p * math.log2(p) for p in p_xj.values() if p > 0)
            h_xixj = -sum(p * math.log2(p) for p in p_xixj.values() if p > 0)
            mi = h_xi + h_xj - h_xixj
            mi_vals.append(max(0.0, mi))
        return float(np.mean(mi_vals)) if mi_vals else 0.0

    def calculate_fisher_information(self, counts: Dict[str, int], parameter_sensitivity: float = 0.1) -> float:
        total = sum(counts.values())
        if total == 0:
            return 0.0
        probs = np.array([c / total for c in counts.values()])
        mean_p = np.mean(probs)
        var_p = np.var(probs)
        if var_p == 0 or parameter_sensitivity == 0:
            return 0.0
        fisher = (parameter_sensitivity * mean_p) ** 2 / var_p
        return float(fisher)

    def calculate_consciousness_integral(self, counts: Dict[str, int], qubit_pairs: Optional[List[Tuple[int, int]]] = None, parameter_sensitivity: float = 0.1) -> float:
        h = self.calculate_entropy(counts)
        mi = self.calculate_mutual_information(counts, qubit_pairs or [])
        fi = self.calculate_fisher_information(counts, parameter_sensitivity)
        return float(self.alpha * h + self.beta * mi + self.gamma * fi)


class TeslaFractalMemoryInterface:
    """Fractal memory addressing (golden-ratio) wrapper. Lazy integrates with TMT-OS memory if present."""

    def __init__(self, memory_system: Optional[Any] = None):
        self.memory = memory_system
        if self.memory is None:
            try:
                # lazy import; may not exist in this environment
                from tmt_os.fractal_consciousness_memory import create_fractal_consciousness_memory

                self.memory = create_fractal_consciousness_memory()
            except Exception:
                self.memory = None

    def store_tesla_experiment(self, experiment_id: str, qasm_circuit: str, consciousness_data: Dict, counts: Dict[str,int], experiment_type: str = 'triangle') -> Optional[str]:
        if not self.memory:
            return None
        if experiment_type == 'triangle':
            c_param = complex(PHI * math.exp(2j * math.pi / 3), DELTA)
        elif experiment_type == 'chord':
            c_param = complex(PHI * 3 / 2, DELTA * math.pi / 6)
        else:
            c_param = complex(PHI, DELTA)
        try:
            address = self.memory.store_consciousness_experiment(experiment_id, c_param, qasm_circuit, consciousness_data, iteration_depth=8)
            logger.info('Stored experiment %s at %s', experiment_id, address)
            return address
        except Exception as e:
            logger.warning('Memory store failed: %s', e)
            return None


class TeslaVisualizationUtils:
    """Visualization helpers (uses matplotlib when available)."""

    @staticmethod
    def create_symmetry_colored_histogram(counts: Dict[str,int], symmetry_group: str = 'D3h', consciousness_values: Optional[Dict[str,float]] = None):
        try:
            import matplotlib.pyplot as plt
        except Exception:
            logger.warning('matplotlib not available; skipping visualization')
            return
        colors = []
        for state in counts.keys():
            if consciousness_values and state in consciousness_values:
                intensity = min(1.0, consciousness_values[state] / 10.0)
                colors.append(plt.cm.plasma(intensity))
            else:
                colors.append('silver')
        plt.figure(figsize=(12,8))
        states = list(counts.keys())
        vals = list(counts.values())
        plt.bar(states, vals, color=colors, alpha=0.8, edgecolor='black')
        plt.xlabel('Quantum State')
        plt.ylabel('Counts')
        plt.title(f'Quantum State Distribution - {symmetry_group}')
        plt.xticks(rotation=45)
        plt.tight_layout()
        return plt


class AcousticDiscoveryAnalyzer:
    """Lightweight acoustic discovery analyzer (data-driven, safe)."""

    ACOUSTIC_EXPERIMENTS = {
        'sequence_0': {'sequence_id': 'seq_0', 'psi_minus_fidelity': 0.892, 'transport_efficiency': 0.85, 'acoustic_frequency': 432.0, 'pumping_cycles': 10},
        'sequence_1': {'sequence_id': 'seq_1', 'psi_minus_fidelity': 0.905, 'transport_efficiency': 0.88, 'acoustic_frequency': 699.3, 'pumping_cycles': 10},
        'sequence_2': {'sequence_id': 'seq_2', 'psi_minus_fidelity': 0.873, 'transport_efficiency': 0.82, 'acoustic_frequency': 1131.0, 'pumping_cycles': 10},
        'sequence_3': {'sequence_id': 'seq_3', 'psi_minus_fidelity': 0.918, 'transport_efficiency': 0.91, 'acoustic_frequency': 1830.0, 'pumping_cycles': 10},
    }

    def __init__(self, output_dir: str = 'acoustic_discoveries'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.discoveries = []

    def analyze_psi_minus_fidelity(self) -> List[Dict[str,Any]]:
        seqs = list(self.ACOUSTIC_EXPERIMENTS.values())
        fidelities = [s['psi_minus_fidelity'] for s in seqs]
        mean_f = sum(fidelities) / len(fidelities)
        max_f = max(fidelities)
        best = [s['sequence_id'] for s in seqs if s['psi_minus_fidelity'] == max_f][0]
        res = [{'domain':'Psi_Minus_Fidelity','pattern':'high_fidelity_transport','mean':mean_f,'max':max_f,'best':best}]
        self.discoveries.extend(res)
        return res

    def analyze_phi_harmonic_freq(self) -> List[Dict[str,Any]]:
        freqs = sorted([s['acoustic_frequency'] for s in self.ACOUSTIC_EXPERIMENTS.values()])
        ratios = [freqs[i+1]/freqs[i] for i in range(len(freqs)-1)]
        phi_aligned = [r for r in ratios if abs(r - PHI)/PHI < 0.1]
        res = []
        if len(phi_aligned) >= 2:
            res.append({'domain':'Phi_Harmonic_Frequencies','pattern':'golden_ratio_acoustic_scaling','ratios':ratios})
            self.discoveries.extend(res)
        return res

    def analyze_all(self) -> List[Dict[str,Any]]:
        self.discoveries = []
        self.analyze_psi_minus_fidelity()
        self.analyze_phi_harmonic_freq()
        # other analyzers could be added similarly
        # save results
        ts = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        out = os.path.join(self.output_dir, f'acoustic_discoveries_{ts}.json')
        with open(out, 'w', encoding='utf-8') as f:
            json.dump({'timestamp': datetime.utcnow().isoformat(), 'discoveries': self.discoveries}, f, indent=2)
        logger.info('Saved acoustic discoveries: %s', out)
        return self.discoveries


def calculate_tesla_consciousness(counts: Dict[str,int], experiment_type: str = 'triangle') -> Dict[str,Any]:
    calc = TeslaConsciousnessCalculator()
    if experiment_type == 'triangle':
        qubit_pairs = [(i,j) for i in range(8) for j in range(i+1,8)]
        parameter_sens = math.pi / 3
    else:
        qubit_pairs = [(0,2),(0,4),(2,4),(1,3),(5,7)]
        parameter_sens = math.pi / 6
    h = calc.calculate_entropy(counts)
    mi = calc.calculate_mutual_information(counts, qubit_pairs)
    fi = calc.calculate_fisher_information(counts, parameter_sens)
    integral = calc.calculate_consciousness_integral(counts, qubit_pairs, parameter_sens)
    return {'_oint': integral, 'H_entropy': h, 'MI_avg': mi, 'FI_sens': fi, 'weights': {'alpha': calc.alpha, 'beta': calc.beta, 'gamma': calc.gamma}, 'total_shots': sum(counts.values())}

if __name__ == '__main__':
    # simple CLI for local analysis
    analyzer = AcousticDiscoveryAnalyzer()
    discoveries = analyzer.analyze_all()
    print('Discovered', len(discoveries))
