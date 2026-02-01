"""tools/vault_pipeline.py

One-click local pipeline:
- sanitize raw CSV (calls tools.sanitizer.sanitize_dataset)
- record sanitization in ledger
- train VAE (tools.vault_vae.train_vault_model)
- record model hash in ledger
- generate synthetic data
- record synthetic file in ledger

All operations are local-only and require PRIVATE_VAULT_SALT env var for deterministic pseudonymization.
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
import tempfile
from pathlib import Path

# Import local tools
try:
    from tools.sanitizer import sanitize_dataset
    from tools.vault_vae import train_vault_model, generate_synthetic
    from tools.vault_ledger import VaultLedger
except Exception as e:
    print("Error importing local tools; ensure you're running from repository root and files exist:", e)
    raise


def run_pipeline(input_path: str, output_dir: str = "vault/sanitized/", epochs: int = 100, latent: int = 4, gen_n: int = 100, sign_keys: bool = False):
    log_path = Path("vault/pipeline.log")
    try:
        ledger = VaultLedger()
        if sign_keys:
            try:
                ledger.generate_or_get_keys()
            except Exception:
                print("Signing not available (cryptography not installed). Continuing without signatures.")

        # 1) sanitize via Universal Entrance (gateway)
        from tools.entrance import UniversalEntrance
        gate = UniversalEntrance(ledger=ledger)
        gateway_result = gate.process_external_data(input_path, source_name="pipeline_ingest", output_dir=output_dir, age_bin_size=5, date_freq="M", drop_original_dates=True)
        sanitized_file = gateway_result["sanitized_path"]
        # gateway already recorded the ingestion in the ledger (GATEWAY_INGESTION)

        # 2) Train VAE (or PCA fallback)
        print("Training VAE (local-only)...")
        model_obj, scaler, cols = train_vault_model(sanitized_file, latent_dim=latent, epochs=epochs)
        # It's possible model save path is in vault/models/ — find it
        model_candidate = Path("vault/models/vault_vae.pth")
        if model_candidate.exists():
            ledger.record_operation("VAE Model Saved", str(model_candidate), metadata={"latent": latent, "epochs": epochs})
        else:
            # fallback: we still record that training completed and include metadata
            ledger.record_operation("VAE Training Completed", sanitized_file, metadata={"latent": latent, "epochs": epochs})

        # 3) Generate synthetic data
        df_gen, synthetic_path = generate_synthetic(model_obj, scaler, cols, n_samples=gen_n, latent_dim=latent)
        ledger.record_operation("Synthetic Generation", synthetic_path, metadata={"n_samples": gen_n})

        print("Pipeline complete. Check vault/ledger.json for provenance entries.")
        return {
            "sanitized": sanitized_file,
            "synthetic": synthetic_path,
            "ledger": str(ledger.ledger_path),
        }
    except Exception as e:
        # write traceback to pipeline log for offline inspection
        import traceback
        tb = traceback.format_exc()
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as lf:
            lf.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Pipeline error: {e}\n")
            lf.write(tb + "\n")
        # re-raise so callers can handle if desired
        raise


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--epochs", type=int, default=50)
    p.add_argument("--latent", type=int, default=4)
    p.add_argument("--gen", type=int, default=100)
    p.add_argument("--sign-keys", action="store_true")
    args = p.parse_args()
    run_pipeline(args.input, epochs=args.epochs, latent=args.latent, gen_n=args.gen, sign_keys=args.sign_keys)
