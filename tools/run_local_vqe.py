#!/usr/bin/env python3
"""
Compute local VQE / exact diagonalization for top-N Hamiltonians.

Writes `node12_out/vqe_local_results.json` containing ground energies (exact)
and, if possible, VQE-estimated energies using Qiskit.
"""
from pathlib import Path
import json
import math
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
HC_FILE = ROOT / 'node12_out' / 'hamiltonian_coeffs.json'
OUT = ROOT / 'node12_out' / 'vqe_local_results.json'

# Load hamiltonian_debug_fix dynamically to allow running this script from tools/
import importlib.util, sys
_mod_path = ROOT / 'tools' / 'hamiltonian_debug_fix.py'
if _mod_path.exists():
    spec = importlib.util.spec_from_file_location('hamiltonian_debug_fix', str(_mod_path))
    _mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(_mod)
    hamiltonian_to_pauli_decomposition = _mod.hamiltonian_to_pauli_decomposition
else:
    # fallback: try normal import
    try:
        from tools.hamiltonian_debug_fix import hamiltonian_to_pauli_decomposition
    except Exception:
        raise

PHI = (1.0 + math.sqrt(5.0)) / 2.0

def pauli_matrices():
    I = np.array([[1,0],[0,1]], dtype=complex)
    X = np.array([[0,1],[1,0]], dtype=complex)
    Y = np.array([[0,-1j],[1j,0]], dtype=complex)
    Z = np.array([[1,0],[0,-1]], dtype=complex)
    return I,X,Y,Z

def kron3(a,b,c):
    return np.kron(np.kron(a,b),c)

def build_hamiltonian(c01, c02, c12, phi_scale=True):
    I,X,Y,Z = pauli_matrices()
    if phi_scale:
        scale = PHI
    else:
        scale = 1.0
    # ZZ terms
    Hzz = 0.0
    Hzz += (c01 * scale) * kron3(Z,Z,I)
    Hzz += (c02 * scale) * kron3(Z,I,Z)
    Hzz += (c12 * scale) * kron3(I,Z,Z)
    # transverse X terms (strengthen = 0.2)
    Hx = 0.2 * (kron3(X,I,I) + kron3(I,X,I) + kron3(I,I,X))
    # Total Hamiltonian per architecture: -phi*ZZ - 0.2*Xsum
    H = -1.0 * Hzz - Hx
    return H

def exact_ground_energy(H):
    vals, vecs = np.linalg.eigh(H)
    return float(np.min(vals))

def try_qiskit_vqe(H, op_matrices=None):
    # Attempt a Qiskit VQE run if available; return None if not.
    # We'll attempt multiple strategies to run a VQE-like optimization:
    # 1) Try to use a simulator-based expectation evaluation over an ansatz
    #    (build ansatz, run statevector on Aer, compute <psi|H|psi>) and
    #    optimize parameters using COBYLA from qiskit.algorithms.optimizers.
    # 2) If that fails, fall back to returning None.
    try:
        try:
            # prefer qiskit_aer if available
            from qiskit_aer import Aer as _AerPkg
            AerPkg = _AerPkg
        except Exception:
            from qiskit import Aer as _AerPkg
            AerPkg = _AerPkg

        from qiskit.circuit.library import RealAmplitudes
        from qiskit import transpile
        try:
            from qiskit.quantum_info import Statevector
        except Exception:
            Statevector = None
        print('VQE: qiskit imports OK')
    except Exception as ex:
        print('VQE import setup failed:', ex)
        return None

    try:
        backend = None
        try:
            backend = AerPkg.get_backend('aer_simulator')
        except Exception:
            # try to construct AerSimulator if present
            try:
                from qiskit_aer import Aer
                backend = Aer.get_backend('aer_simulator')
            except Exception:
                backend = None

        if backend is None:
            print('No Aer backend available for VQE simulation')
            return None

        # ansatz and parameter handling
        ansatz = RealAmplitudes(3, reps=2)
        param_symbols = list(ansatz.parameters)
        n_params = len(param_symbols)
        print('VQE: ansatz params', n_params)

        # initial point (zeros)
        x0 = [0.0] * n_params

        def expectation_fn(x):
            try:
                print('VQE: expectation eval start')
                param_map = {p: v for p, v in zip(param_symbols, x)}
                if hasattr(ansatz, 'bind_parameters'):
                    bound = ansatz.bind_parameters(param_map)
                elif hasattr(ansatz, 'assign_parameters'):
                    # assign_parameters can accept a dict or list depending on Qiskit
                    try:
                        bound = ansatz.assign_parameters(param_map)
                    except Exception:
                        bound = ansatz.assign_parameters(list(x))
                else:
                    raise RuntimeError('No parameter binding API available on ansatz')
                circ = bound.copy()

                # Prefer constructing the statevector locally via Qiskit's
                # Statevector if available to avoid backend/transpile overhead.
                if Statevector is not None:
                    try:
                        sv = Statevector.from_instruction(circ)
                        psi = np.array(sv.data, dtype=complex)
                        # if op_matrices provided, use them; otherwise use H
                        if op_matrices is not None:
                            total = 0.0
                            for _p, coeff, op in op_matrices:
                                total += (coeff * np.vdot(psi, op.dot(psi)).real)
                            return float(total)
                        val = float(np.vdot(psi, H.dot(psi)).real)
                        return val
                    except Exception:
                        # fall through to backend run if Statevector fails
                        pass

                # As a fallback, run on Aer backend requesting a statevector
                try:
                    job = backend.run(circ, shots=1, method='statevector')
                except Exception:
                    job = backend.run(circ, shots=1)
                res = job.result()
                try:
                    psi = res.get_statevector()
                except Exception:
                    try:
                        psi = res.get_statevector(circ)
                    except Exception:
                        try:
                            psi = list(res.data().values())[0].get('statevector')
                        except Exception:
                            raise
                psi = np.array(psi, dtype=complex)
                if op_matrices is not None:
                    total = 0.0
                    for _p, coeff, op in op_matrices:
                        total += (coeff * np.vdot(psi, op.dot(psi)).real)
                    return float(total)
                val = float(np.vdot(psi, H.dot(psi)).real)
                return val
            except Exception as e:
                import traceback
                print('Expectation eval failed:', e)
                print(traceback.format_exc())
                # return large value to discourage optimizer
                return 1e6

        # Try to use COBYLA optimizer if available; otherwise use a simple
        # randomized search as a fallback to get an approximate VQE estimate.
        try:
            print('VQE: attempting COBYLA optimizer')
            try:
                from qiskit.algorithms.optimizers import COBYLA
            except Exception:
                # try legacy aqua optimizer
                try:
                    from qiskit.aqua.components.optimizers import COBYLA
                except Exception:
                    raise
            optimizer = COBYLA(maxiter=200)
            opt_res = optimizer.optimize(n_params, expectation_fn, x0)
            print('VQE: optimizer result', opt_res)
            if isinstance(opt_res, tuple) and len(opt_res) >= 2:
                return float(opt_res[1])
            if hasattr(opt_res, 'fun'):
                return float(opt_res.fun)
        except Exception as ex:
            print('COBYLA unavailable or failed:', ex)

        # Fallback: random-restart local search
        try:
            print('VQE: starting randomized search fallback')
            best_x = np.array(x0, dtype=float)
            best_val = expectation_fn(best_x)
            rng = np.random.default_rng(42)
            n_iter = 200
            sigma = 0.5
            for i in range(n_iter):
                cand = best_x + rng.normal(scale=sigma, size=best_x.shape)
                val = expectation_fn(cand)
                if val < best_val:
                    best_val = val
                    best_x = cand
                    # reduce step size slowly
                    sigma *= 0.98
            print('VQE: randomized search best', best_val)
            return float(best_val)
        except Exception as ex:
            print('Randomized search failed:', ex)
            return None
    except Exception as ex:
        print('VQE simulation strategy failed:', ex)
        return None

def main(top_n=5):
    if not HC_FILE.exists():
        raise SystemExit('Hamiltonian coeffs not found: ' + str(HC_FILE))
    data = json.load(open(HC_FILE, 'r', encoding='utf8'))
    results = []
    for entry in data[:top_n]:
        c01 = float(entry.get('c01', 0.0))
        c02 = float(entry.get('c02', 0.0))
        c12 = float(entry.get('c12', 0.0))
        seq = entry.get('seq')
        phi = float(entry.get('phi_corr', 0.0))
        H = build_hamiltonian(c01, c02, c12, phi_scale=True)
        e_exact = exact_ground_energy(H)

        # decompose H into Pauli basis and include in output for debugging/VQE
        pauli_terms = hamiltonian_to_pauli_decomposition(H)

        # Precompute operator matrices for the pauli terms for use by VQE
        op_matrices = []
        Pm = {
            'I': np.array([[1, 0], [0, 1]], dtype=complex),
            'X': np.array([[0, 1], [1, 0]], dtype=complex),
            'Y': np.array([[0, -1j], [1j, 0]], dtype=complex),
            'Z': np.array([[1, 0], [0, -1]], dtype=complex),
        }
        def kron3_mat(a,b,c):
            return np.kron(np.kron(a,b),c)
        for pstr, coeff in pauli_terms:
            mats = [Pm[ch] for ch in pstr]
            op = kron3_mat(mats[0], mats[1], mats[2])
            op_matrices.append((pstr, coeff, op))

        e_vqe = try_qiskit_vqe(H, op_matrices)
        # include pauli terms in readable form (string, coeff)
        pauli_terms_out = [[p, (c if not isinstance(c, complex) else [c.real, c.imag])] for p, c in pauli_terms]
        results.append({'seq': seq, 'meta_hash': entry.get('meta_hash'), 'phi_corr': phi, 'exact_ground_energy': e_exact, 'vqe_estimate': e_vqe, 'c01': c01, 'c02': c02, 'c12': c12, 'hamiltonian_pauli_terms': pauli_terms_out})

    OUT.write_text(json.dumps(results, indent=2))
    print('Wrote', OUT)

if __name__ == '__main__':
    main()
