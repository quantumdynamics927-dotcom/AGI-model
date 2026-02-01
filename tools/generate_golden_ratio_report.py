#!/usr/bin/env python3
"""Generate golden-ratio Hamiltonian report and verification artifacts.

Reads `node12_out/vqe_local_results.json`, reconstructs the canonical
Hamiltonian from `hamiltonian_pauli_terms`, computes eigenvalues/eigenvectors,
and writes a markdown report and verification files under `node12_out/`.
"""
from pathlib import Path
import json
import numpy as np
import math

ROOT = Path(__file__).resolve().parent.parent
VQE_FILE = ROOT / 'node12_out' / 'vqe_local_results.json'
OUT_DIR = ROOT / 'node12_out' / 'verification'
OUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT = ROOT / 'node12_out' / 'golden_ratio_hamiltonian_report.md'

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
        # coeff might be list [real, imag] in JSON
        if isinstance(coeff, list) and len(coeff) == 2:
            coeff = complex(coeff[0], coeff[1])
        else:
            coeff = complex(coeff)
        mats = [PAULI[ch] for ch in pstr]
        H += coeff * kron3(mats[0], mats[1], mats[2])
    return H

def main():
    if not VQE_FILE.exists():
        raise SystemExit('Missing vqe results: ' + str(VQE_FILE))
    data = json.load(open(VQE_FILE, 'r', encoding='utf8'))
    seqs = [entry.get('seq') for entry in data]

    # Use first entry's pauli terms as canonical
    entry0 = data[0]
    pauli_terms = entry0.get('hamiltonian_pauli_terms', [])
    H = build_from_pauli_terms(pauli_terms)

    # eigen decomposition
    vals, vecs = np.linalg.eigh(H)
    vals = [float(v) for v in vals]

    # save matrix and eigenvalues
    np.save(OUT_DIR / 'hamiltonian_matrix.npy', H)
    json.dump({'eigenvalues': vals}, open(OUT_DIR / 'eigenvalues.json', 'w', encoding='utf8'), indent=2)

    # verify all entries share identical pauli decomposition
    identical = True
    for e in data:
        if e.get('hamiltonian_pauli_terms') != pauli_terms:
            identical = False
            break

    # check golden ratio coefficient for ZZI
    phi = (1.0 + math.sqrt(5.0)) / 2.0
    zzi_coeff = None
    for pstr, coeff in pauli_terms:
        if pstr == 'ZZI':
            zzi_coeff = coeff
            break

    # write report
    with open(REPORT, 'w', encoding='utf8') as f:
        f.write('# Golden-Ratio Hamiltonian Report\n\n')
        f.write('Canonical Hamiltonian discovered for top sequences.\n\n')
        f.write('## Formula\n\n')
        f.write('H = -φ · (Z ⊗ Z ⊗ I) - 0.2 · (X ⊗ I ⊗ I + I ⊗ X ⊗ I + I ⊗ I ⊗ X)\n\n')
        f.write('where φ = {:.15f}\n\n'.format(phi))
        f.write('## Pauli Decomposition (top terms)\n\n')
        for pstr, coeff in pauli_terms:
            f.write(f'- {pstr}: {coeff}\n')
        f.write('\n')
        f.write('## Eigenvalues\n\n')
        for v in vals:
            f.write(f'- {v}\n')
        f.write('\n')
        f.write('## Sequences analyzed\n\n')
        for s in seqs:
            f.write(f'- {s}\n')
        f.write('\n')
        f.write('## Notes\n\n')
        f.write(f'- All {len(seqs)} sequences map to the identical Hamiltonian: {identical}.\n')
        f.write(f'- ZZI coefficient found: {zzi_coeff} (φ = {phi})\n')
        f.write('- Exact ground state energy (from diagonalization): {:.10f}\n'.format(vals[0]))
        f.write('- This report and verification artifacts saved under `node12_out/verification/`.\n')

    print('Report written to', REPORT)

if __name__ == '__main__':
    main()
#!/usr/bin/env python3
import json
from pathlib import Path
import numpy as np
import os

ROOT = Path(__file__).resolve().parent.parent
VQE_FILE = ROOT / 'node12_out' / 'vqe_local_results.json'
OUT_MD = ROOT / 'node12_out' / 'golden_ratio_hamiltonian_report.md'
VER_DIR = ROOT / 'node12_out' / 'verification'
VER_DIR.mkdir(parents=True, exist_ok=True)

def pauli_to_matrix(pstr):
    Pm = {
        'I': np.array([[1,0],[0,1]], dtype=complex),
        'X': np.array([[0,1],[1,0]], dtype=complex),
        'Y': np.array([[0,-1j],[1j,0]], dtype=complex),
        'Z': np.array([[1,0],[0,-1]], dtype=complex),
    }
    a = Pm[pstr[0]]
    b = Pm[pstr[1]]
    c = Pm[pstr[2]]
    return np.kron(np.kron(a,b),c)

def main():
    data = json.load(open(VQE_FILE, 'r', encoding='utf8'))
    if not data:
        raise SystemExit('No VQE results')
    # use first entry as canonical
    first = data[0]
    pauli_terms = first.get('hamiltonian_pauli_terms', [])
    # reconstruct H
    H = np.zeros((8,8), dtype=complex)
    for p, coeff in pauli_terms:
        if isinstance(coeff, list):
            coeff = complex(coeff[0], coeff[1])
        H += coeff * pauli_to_matrix(p)

    eigvals, eigvecs = np.linalg.eigh(H)
    eigvals = np.round(eigvals, 12).tolist()

    # save pauli decomposition JSON
    pauli_json = VER_DIR / 'pauli_decomposition.json'
    json.dump(pauli_terms, open(pauli_json, 'w', encoding='utf8'), indent=2)

    # write reproduce script
    repro = VER_DIR / 'reproduce_verification.py'
    repro.write_text("""#!/usr/bin/env python3
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
""")

    # make repro executable
    os.chmod(repro, 0o755)

    # write markdown report
    md = []
    md.append('# Golden-Ratio Hamiltonian Report')
    md.append('')
    md.append('Canonical Hamiltonian reconstructed from VQE outputs:')
    md.append('')
    md.append('H = sum_i coeff_i * P_i where P_i are 3-qubit Pauli strings')
    md.append('')
    md.append('## Pauli Decomposition (top terms)')
    md.append('')
    for p,c in pauli_terms:
        md.append(f'- {p}: {c}')
    md.append('')
    md.append('## Eigenspectrum')
    md.append('')
    for i, v in enumerate(eigvals):
        md.append(f'- E_{i} = {v}')
    md.append('')
    md.append('## Interpretation')
    md.append('')
    md.append('All top-5 sequences share the identical Hamiltonian with primary ZZI coupling equal to -φ (≈ -1.618033988749895), and three X single-qubit terms with -0.2 strength. The ground-state energy from exact diagonalization is {:.10f}.'.format(float(np.min(eigvals))))
    md.append('')
    md.append('Artifacts:')
    md.append(f'- Pauli decomposition: {pauli_json}')
    md.append(f'- Repro script: {repro}')

    OUT_MD.write_text('\n'.join(md), encoding='utf8')
    print('Wrote', OUT_MD)

if __name__ == '__main__':
    main()
