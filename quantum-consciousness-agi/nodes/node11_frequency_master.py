"""Node 11 — Frequency Master wrapper

Provides a simple interface to run Tesla analysis and compute consciousness integrals.
Designed to be safe and use lazy imports for optional modules.
"""
from typing import Dict, Any, Optional
import logging
from pathlib import Path

from tesla_integration_utils import calculate_tesla_consciousness, AcousticDiscoveryAnalyzer, TeslaFractalMemoryInterface

logger = logging.getLogger('node11')
logger.setLevel(logging.INFO)
if not logger.handlers:
    import logging as _logging
    ch = _logging.StreamHandler()
    ch.setFormatter(_logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
    logger.addHandler(ch)


class FrequencyMaster:
    def __init__(self, registry: Optional[str] = None):
        self.registry = registry
        self.memory = TeslaFractalMemoryInterface()

    def analyze_counts(self, counts: Dict[str,int], experiment_type: str = 'triangle') -> Dict[str,Any]:
        result = calculate_tesla_consciousness(counts, experiment_type)
        logger.info('Computed _oint: %s', result.get('_oint'))
        return result

    def run_acoustic_discovery(self, output_dir: str = 'acoustic_discoveries'):
        analyzer = AcousticDiscoveryAnalyzer(output_dir)
        discoveries = analyzer.analyze_all()
        return discoveries

    def store_experiment(self, experiment_id: str, qasm: str, consciousness_data: Dict, counts: Dict[str,int], experiment_type: str = 'triangle'):
        return self.memory.store_tesla_experiment(experiment_id, qasm, consciousness_data, counts, experiment_type)


def main():
    # Minimal CLI-like example (safe)
    fm = FrequencyMaster()
    sample_counts = {'00': 600, '01': 200, '10': 150, '11': 50}
    res = fm.analyze_counts(sample_counts)
    print('Computed _oint:', res.get('_oint'))


if __name__ == '__main__':
    main()
