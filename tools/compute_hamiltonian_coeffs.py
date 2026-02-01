#!/usr/bin/env python3
"""
Compute Hamiltonian coupling coefficients from top sweep connectivity matrices.

Output: `node12_out/hamiltonian_coeffs.json` containing entries with
`meta_hash`, `seq`, `phi_corr`, `c01`, `c02`, `c12`, and `phi_scaled` coefficients.
"""
import json
import sys
from pathlib import Path
import math

ROOT = Path(__file__).resolve().parent.parent
SWEEP = ROOT / 'node12_out' / 'variation_sweep_extended.json'
OUT = ROOT / 'node12_out' / 'hamiltonian_coeffs.json'

PHI = (1.0 + math.sqrt(5.0)) / 2.0

def load_sweep():
    if not SWEEP.exists():
        raise SystemExit('Sweep file not found: ' + str(SWEEP))
    data = json.load(open(SWEEP, 'r', encoding='utf8'))
    return data

def main(top_n=15):
    data = load_sweep()
    # If file uses 'results' envelope, unwrap
    if isinstance(data, dict) and 'results' in data:
        entries = data['results']
    else:
        entries = data

    # sort by phi_corr desc
    entries_sorted = sorted(entries, key=lambda x: -float(x.get('phi_corr', 0)))
    selected = entries_sorted[:top_n]

    results = []
    for e in selected:
        meta = e.get('meta', {})
        h = meta.get('hash')
        seq = e.get('seq')
        phi = float(e.get('phi_corr', 0))
        raw = e.get('raw_path')
        if not raw:
            # try to reconstruct path from hash
            if h:
                candidate = ROOT / 'node12_out' / f'node12_{h[:12]}.connectivity.npy'
                raw = str(candidate) if candidate.exists() else None
        entry_out = {'meta_hash': h, 'seq': seq, 'phi_corr': phi}
        if raw:
            try:
                import numpy as np
                mat = np.load(raw)
                # expects 3x3 matrix for ids n0,n1,n2
                c01 = float(mat[0,1])
                c02 = float(mat[0,2])
                c12 = float(mat[1,2])
                entry_out.update({'c01': c01, 'c02': c02, 'c12': c12})
                entry_out.update({'c01_phi': c01 * PHI, 'c02_phi': c02 * PHI, 'c12_phi': c12 * PHI})
            except Exception as ex:
                entry_out['error'] = str(ex)
        else:
            entry_out['error'] = 'raw matrix not found'
        results.append(entry_out)

    OUT.write_text(json.dumps(results, indent=2))
    print('Wrote', OUT)

if __name__ == '__main__':
    main()
