"""Run Node12 connectivity raw export and sequence-variation sweep.

Saves results to `node12_out/variation_sweep.json` and raw connectivity `.npy` files.
"""
import os
import json
from node12_neural_synapse import stream_connectivity, _phi_correlation


def single_base_mutations(seq: str):
    bases = ['A','T','C','G']
    muts = []
    for i in range(len(seq)):
        for b in bases:
            if seq[i] == b:
                continue
            s = seq[:i] + b + seq[i+1:]
            muts.append({'pos': i, 'base': b, 'seq': s})
    return muts


def run_variation():
    outdir = 'node12_out'
    os.makedirs(outdir, exist_ok=True)

    n0 = 'ATCGATCG'
    n1 = 'ATCGATCG'
    n2_original = 'GGGGGGGG'

    mutations = single_base_mutations(n2_original)
    results = []

    for m in mutations:
        seqs = {'n0': n0, 'n1': n1, 'n2': m['seq']}
        # request raw output
        path, meta = stream_connectivity(seqs, out_dir=outdir, phi_threshold=0.95, strengthen=0.2, allow_raw=True)
        # compute phi correlation between n0 and mutated n2
        phi = _phi_correlation(n0, m['seq'])
        results.append({
            'pos': m['pos'],
            'base': m['base'],
            'seq': m['seq'],
            'meta_hash': meta.get('hash'),
            'phi_corr': phi,
            'raw_path': str(path)
        })

    out_path = os.path.join(outdir, 'variation_sweep.json')
    with open(out_path, 'w') as f:
        json.dump({'results': results}, f, indent=2)
    print('Variation sweep saved to', out_path)


if __name__ == '__main__':
    run_variation()
