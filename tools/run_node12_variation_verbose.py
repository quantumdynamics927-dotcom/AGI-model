import os
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

def main():
    outdir = 'node12_out'
    os.makedirs(outdir, exist_ok=True)
    n0 = 'ATCGATCG'
    n1 = 'ATCGATCG'
    n2_original = 'GGGGGGGG'
    mutations = single_base_mutations(n2_original)
    for idx, m in enumerate(mutations):
        print(f'Running mutation {idx+1}/{len(mutations)}: pos={m["pos"]} base={m["base"]} seq={m["seq"]}')
        path, meta = stream_connectivity({'n0':n0,'n1':n1,'n2':m['seq']}, out_dir=outdir, phi_threshold=0.95, strengthen=0.2, allow_raw=True)
        print('  -> meta_hash', meta.get('hash'), 'saved_to', path)

if __name__ == '__main__':
    main()
