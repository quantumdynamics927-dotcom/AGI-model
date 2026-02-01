#!/usr/bin/env python3
"""
Run a graduated single-base mutation sweep for Node 12 and save a summary JSON.
Creates `node12_out/variation_sweep_gradual.json` with entries for each mutation.
"""
import os
import json
from pathlib import Path
from datetime import datetime

OUT_DIR = Path("node12_out")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def main():
    # Default sequences (mirror state for n0/n1, perturbation n2)
    seeds = {
        'n0': 'ATCGATCG',
        'n1': 'ATCGATCG',
        'n2': 'GGGGGGGG',
    }

    # Ensure raw connectivity allowed
    os.environ.setdefault('ALLOW_RAW_CONNECTIVITY', '1')

    try:
        from node12_neural_synapse import stream_connectivity
    except Exception as e:
        print('Error importing node12_neural_synapse:', e)
        raise

    bases = ['A', 'C', 'G', 'T']
    results = []

    n2 = seeds['n2']
    L = len(n2)
    for pos in range(L):
        orig = n2[pos]
        for b in bases:
            if b == orig:
                continue
            seq = n2[:pos] + b + n2[pos+1:]
            seq_packet = {'n0': seeds['n0'], 'n1': seeds['n1'], 'n2': seq}
            try:
                p, meta = stream_connectivity(seq_packet, allow_raw=True)
            except TypeError:
                # older API which ignores allow_raw named arg
                p, meta = stream_connectivity(seq_packet)

            entry = {
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'pos': pos,
                'base': b,
                'seq': seq,
                'meta': meta,
            }

            # Add raw path if raw npy was saved and meta contains hash
            if isinstance(meta, dict):
                h = meta.get('hash')
                if h:
                    raw_candidate = OUT_DIR / f'node12_{h[:12]}.connectivity.npy'
                    if raw_candidate.exists():
                        entry['raw_path'] = str(raw_candidate)

            results.append(entry)

    out_file = OUT_DIR / 'variation_sweep_gradual.json'
    with out_file.open('w', encoding='utf8') as f:
        json.dump(results, f, indent=2)

    print('Saved', out_file)

if __name__ == '__main__':
    main()
