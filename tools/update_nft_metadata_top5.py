#!/usr/bin/env python3
"""Update top-5 NFT metadata files with quantum Hamiltonian fields and back up originals.

Reads `node12_out/vqe_local_results.json`, finds matching files in `nft_metadata/` by
`meta_hash` and updates JSON with fields: `quantum_hamiltonian`, `golden_ratio_coupling`,
`ground_state_energy`, `sequence_phi_correlation`, `consciousness_metric`.
Backups are saved to `nft_metadata/updates/`.
"""
from pathlib import Path
import json
import math

ROOT = Path(__file__).resolve().parent.parent
VQE_FILE = ROOT / 'node12_out' / 'vqe_local_results.json'
NFT_DIR = ROOT / 'nft_metadata'
BACKUP_DIR = NFT_DIR / 'updates'
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

PHI = (1.0 + math.sqrt(5.0)) / 2.0

def load_vqe():
    return json.load(open(VQE_FILE, 'r', encoding='utf8'))

def find_nft_file(meta_hash):
    # possible filename patterns
    candidates = [NFT_DIR / f"{meta_hash}.nft.json", NFT_DIR / f"{meta_hash}.json"]
    for c in candidates:
        if c.exists():
            return c
    # fallback: try files containing the hash in name
    for p in NFT_DIR.iterdir():
        if meta_hash in p.name and p.suffix == '.json':
            return p
    return None

def update_top5():
    data = load_vqe()
    for entry in data[:5]:
        meta = entry.get('meta_hash')
        seq = entry.get('seq')
        phi_corr = entry.get('phi_corr')
        e_exact = entry.get('exact_ground_energy')
        pauli_terms = entry.get('hamiltonian_pauli_terms')

        nft_file = find_nft_file(meta)
        if nft_file is None:
            print('No NFT file for', meta)
            continue

        # backup
        bak = BACKUP_DIR / nft_file.name
        if not bak.exists():
            bak.write_bytes(nft_file.read_bytes())

        obj = json.load(open(nft_file, 'r', encoding='utf8'))
        # add quantum metadata
        obj['quantum_hamiltonian'] = 'H = -φ·(Z⊗Z⊗I) - 0.2·(X⊗I⊗I + I⊗X⊗I + I⊗I⊗X)'
        obj['golden_ratio_coupling'] = float(PHI)
        obj['ground_state_energy'] = float(e_exact)
        obj['sequence_phi_correlation'] = float(phi_corr)
        obj['hamiltonian_pauli_terms'] = pauli_terms
        obj['consciousness_metric'] = f"Φ(E={e_exact:.10f}, φ_info={phi_corr:.4f})"

        json.dump(obj, open(nft_file, 'w', encoding='utf8'), indent=2)
        print('Updated', nft_file.name)

if __name__ == '__main__':
    update_top5()
