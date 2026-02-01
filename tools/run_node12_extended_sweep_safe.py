#!/usr/bin/env python3
"""
Robust extended mutation sweep: writes incremental JSON-lines and final JSON.
This prevents data loss if the run is interrupted and ensures an output file exists.
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault('ALLOW_RAW_CONNECTIVITY', '1')

OUT_DIR = Path('node12_out')
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_JSONL = OUT_DIR / 'variation_sweep_extended.jsonl'
OUT_JSON = OUT_DIR / 'variation_sweep_extended.json'

try:
    from node12_neural_synapse import stream_connectivity, _phi_correlation
except Exception:
    from node12_neural_synapse import stream_connectivity
    try:
        from node12_neural_synapse import _phi_correlation
    except Exception:
        def _phi_correlation(a, b):
            if not a or not b:
                return 0.0
            L = min(len(a), len(b))
            matches = sum(1 for i in range(L) if a[i] == b[i])
            return matches / L if L > 0 else 0.0


def emit(entry):
    with OUT_JSONL.open('a', encoding='utf8') as f:
        f.write(json.dumps(entry) + '\n')


def run():
    seeds = {'n0': 'ATCGATCG', 'n1': 'ATCGATCG', 'n2': 'GGGGGGGG'}
    bases = ['A', 'C', 'G', 'T']
    results = []

    n2 = seeds['n2']
    L = len(n2)

    # helper to process sequence
    def process(seq, etype, info=None):
        packet = {'n0': seeds['n0'], 'n1': seeds['n1'], 'n2': seq}
        p, meta = stream_connectivity(packet, allow_raw=True)
        phi = _phi_correlation(seeds['n0'], seq)
        entry = dict(timestamp=datetime.utcnow().isoformat() + 'Z', type=etype, seq=seq, meta=meta, phi_corr=phi)
        if info:
            entry.update(info)
        # attach raw path if present
        if isinstance(meta, dict):
            h = meta.get('hash')
            if h:
                candidate = OUT_DIR / f'node12_{h[:12]}.connectivity.npy'
                if candidate.exists():
                    entry['raw_path'] = str(candidate)
        emit(entry)
        results.append(entry)

    try:
        # singles
        for pos in range(L):
            orig = n2[pos]
            for b in bases:
                if b == orig:
                    continue
                seq = n2[:pos] + b + n2[pos+1:]
                process(seq, 'single', {'pos': pos, 'base': b})

        # doubles
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
                        process(seq, 'double', {'pos': (i, j), 'bases': (ba, bb)})

        # insertions (append)
        for b in bases:
            seq = n2 + b
            process(seq, 'insert', {'pos': 'end', 'base': b})

    except Exception as ex:
        # ensure partial results are preserved
        print('Sweep aborted with exception:', ex)
        # still attempt to write final JSON of collected results
    finally:
        with OUT_JSON.open('w', encoding='utf8') as f:
            json.dump(results, f, indent=2)
        print('Wrote', OUT_JSON, 'and JSON-lines at', OUT_JSONL)


if __name__ == '__main__':
    run()
