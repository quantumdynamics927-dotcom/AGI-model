import os, json
from pathlib import Path

os.environ.setdefault('ALLOW_RAW_CONNECTIVITY', '1')
OUT = Path('node12_out')
OUT.mkdir(exist_ok=True)

from node12_neural_synapse import stream_connectivity

seeds = {'n0':'ATCGATCG','n1':'ATCGATCG','n2':'GGGGGGGG'}
bases = ['A','C','G','T']
results = []
for pos in range(len(seeds['n2'])):
    for b in bases:
        if b == seeds['n2'][pos]:
            continue
        seq = seeds['n2'][:pos] + b + seeds['n2'][pos+1:]
        print('Running pos', pos, '->', seq)
        p, meta = stream_connectivity({'n0':seeds['n0'],'n1':seeds['n1'],'n2':seq}, allow_raw=True)
        print('  meta hash:', meta.get('hash'))
        results.append({'pos':pos,'base':b,'seq':seq,'meta':meta})

OUT.joinpath('variation_sweep_gradual.json').write_text(json.dumps(results, indent=2))
print('Done; wrote node12_out/variation_sweep_gradual.json')
