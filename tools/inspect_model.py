"""tools/inspect_model.py

Inspect a PyTorch model file: size, SHA256, try to load, list state_dict keys, attempt to load into `QuantumVAE` if compatible, run a short inference, and record the import in the vault ledger.

Usage (local-only):
  python tools/inspect_model.py --path "e:\AGI model\best_model.pt" --record

Note: sets PRIVATE_VAULT_SALT not required. No network access.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import traceback
from pathlib import Path
from typing import Optional


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def main(argv: Optional[list] = None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', required=True)
    parser.add_argument('--record', action='store_true', help='Record model import in ledger')
    args = parser.parse_args(argv)

    p = Path(args.path)
    if not p.exists():
        print(f"ERROR: file not found: {p}")
        sys.exit(1)

    size = p.stat().st_size
    sha = compute_sha256(p)
    print(f"Model file: {p}")
    print(f"Size: {size} bytes")
    print(f"SHA256: {sha}")

    result = {'path': str(p), 'size': size, 'sha256': sha}

    # Attempt to load with torch
    try:
        import torch
        print('PyTorch available:', torch.__version__)
        obj = torch.load(str(p), map_location='cpu')
        # Determine what we loaded
        if isinstance(obj, dict):
            # Could be a state_dict or a checkpoint dict
            if 'state_dict' in obj:
                st = obj['state_dict']
                result['loaded_type'] = 'checkpoint_dict'
            else:
                st = obj
                result['loaded_type'] = 'state_dict'
            result['state_keys'] = list(st.keys())[:50]
            result['num_keys'] = len(st.keys())
            print('State dict keys (sample):', result['state_keys'])
            # Try to load into known model
            try:
                from vae_model import QuantumVAE
                model = QuantumVAE()
                # adapt keys if saved with 'module.' prefix
                try:
                    model.load_state_dict(st)
                except Exception:
                    # try stripping module. prefix
                    new_st = {k.replace('module.', ''): v for k, v in st.items()}
                    model.load_state_dict(new_st)
                model.eval()
                import torch
                import numpy as np
                with torch.no_grad():
                    inp = torch.rand(1, model.decoder[-2].out_features) if hasattr(model.decoder[-2], 'out_features') else torch.rand(1, 128)
                    # fallback input size guess
                    try:
                        recon, mu, logvar, density = model(inp, return_density=True)
                        result['inference_ok'] = True
                        result['recon_shape'] = list(recon.shape)
                    except Exception as e:
                        result['inference_ok'] = False
                        result['inference_error'] = str(e)
                result['model_loaded_as'] = 'QuantumVAE'
                print('Loaded into QuantumVAE; inference_ok=', result.get('inference_ok', False))
            except Exception as e:
                result['model_loaded_as'] = 'unknown_or_incompatible'
                result['model_load_error'] = str(e)
                print('Could not load into QuantumVAE:', e)
        else:
            # Loaded as a model object or other
            result['loaded_type'] = type(obj).__name__
            result['object_repr'] = str(obj)[:400]
            print('Loaded object type:', result['loaded_type'])
            # If object has state_dict method, try to get keys
            try:
                st = obj.state_dict()
                result['state_keys'] = list(st.keys())[:50]
                result['num_keys'] = len(st.keys())
                print('State dict keys (sample):', result['state_keys'])
            except Exception:
                pass
    except Exception as e:
        tb = traceback.format_exc()
        print('PyTorch load error:', e)
        print(tb)
        result['load_error'] = str(e)

    # Optionally record in ledger
    if args.record:
        try:
            from tools.vault_ledger import VaultLedger
            ledger = VaultLedger()
            entry = ledger.record_operation('MODEL_IMPORT', str(p), metadata={'sha256': sha, 'size': size})
            print('Recorded ledger index:', len(ledger.history)-1)
            result['ledger_index'] = len(ledger.history)-1
        except Exception as e:
            print('Failed to record ledger entry:', e)
            result['ledger_error'] = str(e)

    print('\nSummary:')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
