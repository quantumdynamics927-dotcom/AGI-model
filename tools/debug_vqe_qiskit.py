#!/usr/bin/env python3
"""
Debug Qiskit VQE pipeline: check imports, backend availability, operator conversion
and run a tiny VQE flow for the first Hamiltonian to capture exceptions and logs.
"""
import json
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HC_FILE = ROOT / 'node12_out' / 'hamiltonian_coeffs.json'

def main():
    print('Debug VQE start')
    try:
        import qiskit
        from qiskit import Aer
        from qiskit.utils import QuantumInstance
        from qiskit.opflow import PauliSumOp
        from qiskit.algorithms import VQE
        from qiskit.circuit.library import RealAmplitudes
        from qiskit.algorithms.optimizers import COBYLA
        from qiskit.quantum_info import Operator
        print('Qiskit version:', qiskit.__version__)
    except Exception as e:
        print('Qiskit import error:')
        traceback.print_exc()
        return

    if not HC_FILE.exists():
        print('Hamiltonian coeffs missing:', HC_FILE)
        return

    data = json.load(open(HC_FILE))
    if not data:
        print('No entries in hamiltonian coeffs')
        return
    entry = data[0]
    c01 = float(entry.get('c01',0))
    c02 = float(entry.get('c02',0))
    c12 = float(entry.get('c12',0))

    # build H dense exactly like run_local_vqe
    import numpy as np
    PHI = (1.0 + 5**0.5)/2.0
    I = np.array([[1,0],[0,1]], dtype=complex)
    X = np.array([[0,1],[1,0]], dtype=complex)
    Z = np.array([[1,0],[0,-1]], dtype=complex)
    def kron3(a,b,c):
        return np.kron(np.kron(a,b),c)
    Hzz = (c01*PHI)*kron3(Z,Z,I) + (c02*PHI)*kron3(Z,I,Z) + (c12*PHI)*kron3(I,Z,Z)
    Hx = 0.2*(kron3(X,I,I)+kron3(I,X,I)+kron3(I,I,X))
    H = -1.0*Hzz - Hx

    print('Hamiltonian shape:', H.shape)

    try:
        op = Operator(H)
        print('Operator built, dim:', op.dim)
    except Exception:
        print('Operator conversion failed:')
        traceback.print_exc()
        return

    try:
        pauli_op = PauliSumOp.from_operator(op)
        print('PauliSumOp built:', pauli_op)
    except Exception:
        print('PauliSumOp.from_operator failed:')
        traceback.print_exc()
        return

    try:
        backend = Aer.get_backend('aer_simulator')
        print('Backend available:', backend.name())
    except Exception:
        print('Aer backend not available:')
        traceback.print_exc()
        return

    try:
        qi = QuantumInstance(backend)
        ansatz = RealAmplitudes(3, reps=1)
        optimizer = COBYLA(maxiter=100)
        vqe = VQE(ansatz, optimizer=optimizer, quantum_instance=qi)
        print('Starting VQE compute_minimum_eigenvalue (this may take a moment)...')
        res = vqe.compute_minimum_eigenvalue(operator=pauli_op)
        print('VQE result:', res)
    except Exception:
        print('VQE execution failed:')
        traceback.print_exc()
        return

if __name__ == '__main__':
    main()
