import pytest

from tesla_integration_utils import TeslaConsciousnessCalculator, calculate_tesla_consciousness


def test_entropy_basic():
    calc = TeslaConsciousnessCalculator()
    counts = {'00': 50, '01': 50}
    h = calc.calculate_entropy(counts)
    assert pytest.approx(h, rel=1e-3) == 1.0  # perfect binary entropy = 1 bit


def test_consciousness_integral_smoke():
    counts = {'00': 600, '01': 200, '10': 150, '11': 50}
    res = calculate_tesla_consciousness(counts, experiment_type='triangle')
    assert '_oint' in res
    assert res['total_shots'] == 1000
