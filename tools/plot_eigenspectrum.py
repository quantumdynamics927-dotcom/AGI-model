#!/usr/bin/env python3
"""Plot eigenspectrum from `node12_out/verification/eigenvalues.json` and save PNG.
"""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
EIG_FILE = ROOT / 'node12_out' / 'verification' / 'eigenvalues.json'
OUT_DIR = ROOT / 'outputs'
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_PNG = OUT_DIR / 'eigenspectrum.png'

def main():
    data = json.load(open(EIG_FILE, 'r', encoding='utf8'))
    vals = data.get('eigenvalues', [])
    if not vals:
        print('No eigenvalues found in', EIG_FILE)
        return
    plt.figure(figsize=(6,4))
    x = list(range(len(vals)))
    plt.plot(x, vals, '-o')
    plt.axhline(min(vals), color='red', linestyle='--', label='Ground')
    plt.title('Eigenspectrum')
    plt.xlabel('Index')
    plt.ylabel('Eigenvalue')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT_PNG, dpi=200)
    print('Wrote', OUT_PNG)

if __name__ == '__main__':
    main()
