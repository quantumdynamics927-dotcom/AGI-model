#!/usr/bin/env python3
"""Reproduce Hamiltonian matrix and eigenvalues from `vqe_local_results.json`.

Saves `hamiltonian_matrix.npy` and `eigenvalues.json` in the same folder.
"""
from pathlib import Path
import json
import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent
VQE_FILE = ROOT / 'node12_out' / 'vqe_local_results.json'
OUT_DIR = ROOT / 'node12_out' / 'verification'
OUT_DIR.mkdir(parents=True, exist_ok=True)

PAULI = {
    'I': np.array([[1,0],[0,1]], dtype=complex),
    'X': np.array([[0,1],[1,0]], dtype=complex),
    'Y': np.array([[0,-1j],[1j,0]], dtype=complex),
    'Z': np.array([[1,0],[0,-1]], dtype=complex),
}

def kron3(a,b,c):
    return np.kron(np.kron(a,b),c)

def build_from_pauli_terms(pauli_terms):
    H = np.zeros((8,8), dtype=complex)
    for pstr, coeff in pauli_terms:
        if isinstance(coeff, list) and len(coeff) == 2:
            coeff = complex(coeff[0], coeff[1])
        else:
            coeff = complex(coeff)
        mats = [PAULI[ch] for ch in pstr]
        H += coeff * kron3(mats[0], mats[1], mats[2])
    return H

def main():
    data = json.load(open(VQE_FILE, 'r', encoding='utf8'))
    entry0 = data[0]
    pauli_terms = entry0.get('hamiltonian_pauli_terms', [])
    H = build_from_pauli_terms(pauli_terms)
    vals, vecs = np.linalg.eigh(H)
    np.save(OUT_DIR / 'hamiltonian_matrix.npy', H)
    json.dump({'eigenvalues': [float(v) for v in vals]}, open(OUT_DIR / 'eigenvalues.json', 'w', encoding='utf8'), indent=2)
    json.dump(pauli_terms, open(OUT_DIR / 'pauli_decomposition.json', 'w', encoding='utf8'), indent=2)
    print('Wrote verification artifacts to', OUT_DIR)

if __name__ == '__main__':
    main()
#!/usr/bin/env python3
import json
import numpy as np
from pathlib import Path

pauli = json.load(open(Path(__file__).resolve().parent / 'pauli_decomposition.json','r'))
Pm = {
    'I': np.array([[1,0],[0,1]], dtype=complex),
    'X': np.array([[0,1],[1,0]], dtype=complex),
    'Y': np.array([[0,-1j],[1j,0]], dtype=complex),
    'Z': np.array([[1,0],[0,-1]], dtype=complex),
}
def kron3(a,b,c):
    return np.kron(np.kron(a,b),c)

H = np.zeros((8,8), dtype=complex)
for p,c in pauli:
    if isinstance(c, list):
        c = complex(c[0], c[1])
    P = kron3(Pm[p[0]], Pm[p[1]], Pm[p[2]])
    H += c * P

vals, vecs = np.linalg.eigh(H)
print('Eigenvalues:')
print(vals)
print('Ground energy:', float(np.min(vals)))
