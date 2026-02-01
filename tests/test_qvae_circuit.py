import pytest


def test_qvae_circuit_structure():
    """Build the WEDJAT circuit and validate basic structural properties.

    This test will be skipped if Qiskit is not installed (CI-friendly).
    """
    qiskit = pytest.importorskip('qiskit', reason='Qiskit not installed; skipping QVAE circuit tests')
    try:
        from qvae_bridge import create_wedjat_qvae_circuit
    except Exception as e:
        pytest.skip(f'QVAE bridge unavailable: {e}')

    qc = create_wedjat_qvae_circuit()
    # basic checks
    assert hasattr(qc, 'num_qubits')
    assert qc.num_qubits == 127

    # check presence of at least one ry and one cx instruction
    instrs = [inst[0].name for inst in qc.data]
    assert 'ry' in instrs or 'u' in instrs
    assert 'cx' in instrs
