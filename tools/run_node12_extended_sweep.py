#!/usr/bin/env python3
"""
Extended mutation sweep for Node 12.
Performs single-base, double-base, and single-base insertions on `n2` and
saves results (including provenance hashes and phi-correlation) to
`node12_out/variation_sweep_extended.json`.
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime

# When running this script from `tools/` the CWD may be tools/; ensure repo root
# is on sys.path so top-level modules (e.g. `node12_neural_synapse`) import.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

OUT_DIR = Path('node12_out')
OUT_DIR.mkdir(parents=True, exist_ok=True)

os.environ.setdefault('ALLOW_RAW_CONNECTIVITY', '1')

try:
    from node12_neural_synapse import stream_connectivity, _phi_correlation
except Exception:
    # fallback to importing build_connectivity and computing phi manually
    from node12_neural_synapse import stream_connectivity
    try:
        from node12_neural_synapse import _phi_correlation
    except Exception:
        def _phi_correlation(a, b):
            # conservative fallback: simple fraction of matches
            if not a or not b:
                return 0.0
            L = min(len(a), len(b))
            matches = sum(1 for i in range(L) if a[i] == b[i])
            return matches / L if L > 0 else 0.0


def run():
    seeds = {'n0': 'ATCGATCG', 'n1': 'ATCGATCG', 'n2': 'GGGGGGGG'}
    bases = ['A', 'C', 'G', 'T']
    results = []

    n2 = seeds['n2']
    L = len(n2)

    # Single-base (already run previously but included here for completeness)
    for pos in range(L):
        orig = n2[pos]
        for b in bases:
            if b == orig:
                continue
            seq = n2[:pos] + b + n2[pos+1:]
            packet = {'n0': seeds['n0'], 'n1': seeds['n1'], 'n2': seq}
            p, meta = stream_connectivity(packet, allow_raw=True)
            phi = _phi_correlation(seeds['n0'], seq)
            entry = dict(timestamp=datetime.utcnow().isoformat() + 'Z', type='single', pos=pos, base=b, seq=seq, meta=meta, phi_corr=phi)
            # attach raw path if exists
            if isinstance(meta, dict):
                h = meta.get('hash')
                if h:
                    candidate = OUT_DIR / f'node12_{h[:12]}.connectivity.npy'
                    if candidate.exists():
                        entry['raw_path'] = str(candidate)
            results.append(entry)

    # Double-base mutations (all i<j)
    for i in range(L):
        for j in range(i+1, L):
            for ba in bases:
                if ba == n2[i]:
                    continue
                for bb in bases:
                    if bb == n2[j]:
                        continue
                    seq = list(n2)
                    seq[i] = ba
                    seq[j] = bb
                    seq = ''.join(seq)
                    packet = {'n0': seeds['n0'], 'n1': seeds['n1'], 'n2': seq}
                    p, meta = stream_connectivity(packet, allow_raw=True)
                    phi = _phi_correlation(seeds['n0'], seq)
                    entry = dict(timestamp=datetime.utcnow().isoformat() + 'Z', type='double', pos=(i, j), bases=(ba, bb), seq=seq, meta=meta, phi_corr=phi)
                    if isinstance(meta, dict):
                        h = meta.get('hash')
                        if h:
                            candidate = OUT_DIR / f'node12_{h[:12]}.connectivity.npy'
                            if candidate.exists():
                                entry['raw_path'] = str(candidate)
                    results.append(entry)

    # Single-base insertions at end (length +1)
    for b in bases:
        seq = n2 + b
        packet = {'n0': seeds['n0'], 'n1': seeds['n1'], 'n2': seq}
        p, meta = stream_connectivity(packet, allow_raw=True)
        phi = _phi_correlation(seeds['n0'], seq)
        entry = dict(timestamp=datetime.utcnow().isoformat() + 'Z', type='insert', pos='end', base=b, seq=seq, meta=meta, phi_corr=phi)
        if isinstance(meta, dict):
            h = meta.get('hash')
            if h:
                candidate = OUT_DIR / f'node12_{h[:12]}.connectivity.npy'
                if candidate.exists():
                    entry['raw_path'] = str(candidate)
        results.append(entry)

    out_file = OUT_DIR / 'variation_sweep_extended.json'
    with out_file.open('w', encoding='utf8') as f:
        json.dump(results, f, indent=2)

    print('Wrote', out_file)


if __name__ == '__main__':
    run()
