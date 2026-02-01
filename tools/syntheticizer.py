"""tools/syntheticizer.py

Produce synthetic equivalents of sanitized scan results using the vault VAE (or PCA fallback).
All operations are local-only and recorded in the vault ledger.
"""
from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from tools.vault_vae import train_vault_model, generate_synthetic
from tools.vault_ledger import VaultLedger

logger = logging.getLogger("syntheticizer")
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


class Syntheticizer:
    @staticmethod
    def _sha256_of_file(path: str) -> str:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                h.update(chunk)
        return h.hexdigest()

    @classmethod
    def syntheticize_file(cls, sanitized_path: str, n_samples: int = 100, latent: int = 4, epochs: int = 50, ledger: Optional[VaultLedger] = None, noise: float = 0.0) -> Dict[str, Any]:
        ledger = ledger or VaultLedger()
        sanitized_path = str(sanitized_path)
        # Train model (small by default) and generate synthetic samples
        model, scaler, columns = train_vault_model(sanitized_path, latent_dim=latent, epochs=epochs)
        df_gen, synthetic_path = generate_synthetic(model, scaler, columns, n_samples=n_samples, latent_dim=latent)

        # record in ledger
        file_hash = cls._sha256_of_file(synthetic_path)
        entry = ledger.record_operation("SYNTHESIS", synthetic_path, metadata={"n_samples": n_samples, "latent": latent, "epochs": epochs, "noise": noise, "source_sanitized": sanitized_path})

        logger.info(f"Synthetic data generated: {synthetic_path} (hash={file_hash[:12]})")
        return {"synthetic_path": synthetic_path, "synthetic_hash": file_hash, "ledger_index": len(ledger.history)-1}

    @classmethod
    def syntheticize_row(cls, row: Dict[str, Any], n_samples: int = 1, **kwargs) -> Dict[str, Any]:
        # Write single-row sanitized CSV then call syntheticize_file
        from pathlib import Path
        import pandas as pd
        tmp_dir = Path("vault/single_row_tmp")
        tmp_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        p = tmp_dir / f"row_{ts}.csv"
        pd.DataFrame([row]).to_csv(p, index=False)
        return cls.syntheticize_file(str(p), n_samples=n_samples, **kwargs)
