#!/usr/bin/env python3
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent.parent
VQE_FILE = ROOT / 'node12_out' / 'vqe_local_results.json'
NFT_DIR = ROOT / 'nft_metadata'
BACKUP_DIR = NFT_DIR / 'updates'
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

def find_nft_for_hash(meta_hash):
    candidate = NFT_DIR / (meta_hash + '.nft.json')
    if candidate.exists():
        return candidate
    # fallback: search files
    for f in NFT_DIR.glob('*.json'):
        try:
            d = json.load(open(f,'r',encoding='utf8'))
            if d.get('meta_hash') == meta_hash or d.get('hash') == meta_hash:
                return f
        except Exception:
            continue
    return None

def main():
    data = json.load(open(VQE_FILE,'r',encoding='utf8'))
    for entry in data:
        mh = entry.get('meta_hash')
        nft_path = find_nft_for_hash(mh)
        if nft_path is None:
            print('No NFT file found for', mh)
            continue
        # backup
        shutil.copy2(nft_path, BACKUP_DIR / nft_path.name)
        nft = json.load(open(nft_path,'r',encoding='utf8'))
        # add fields
        nft['quantum_hamiltonian'] = 'H = -φ * (Z⊗Z⊗I) - 0.2 * (X⊗I⊗I + I⊗X⊗I + I⊗I⊗X)'
        nft['golden_ratio_coupling'] = 1.618033988749895
        nft['ground_state_energy'] = entry.get('exact_ground_energy')
        nft['sacred_geometry_class'] = 'Phi-weighted quantum state'
        nft['consciousness_metric'] = f"Φ(E={entry.get('exact_ground_energy'):.10f}, φ_info={entry.get('phi_corr'):.4f})"
        json.dump(nft, open(nft_path,'w',encoding='utf8'), indent=2)
        print('Updated', nft_path, '-> backup at', BACKUP_DIR / nft_path.name)

if __name__ == '__main__':
    main()
