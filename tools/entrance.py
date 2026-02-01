"""tools/entrance.py

Universal Entrance (Gatekeeper) for the Secure Synthetic Vault.
All incoming data files should be routed through this gateway before any downstream processing.
This enforces: raw hash -> sanitize -> sanitized hash -> ledger record (local-only).

Usage (local-only):
  python tools/entrance.py --input path/to/raw.csv --source "external_lab"
"""
from __future__ import annotations

import argparse
import logging
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from tools.vault_ledger import VaultLedger
from tools.sanitizer import sanitize_dataset

logger = logging.getLogger("entrance")
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


class UniversalEntrance:
    def __init__(self, ledger: Optional[VaultLedger] = None, gate_dir: str = "vault/gatekeeper_logs"):
        self.ledger = ledger or VaultLedger()
        self.gate_dir = Path(gate_dir)
        self.gate_dir.mkdir(parents=True, exist_ok=True)

    def _store_raw_copy(self, file_path: str) -> str:
        p = Path(file_path)
        ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        dest = self.gate_dir / f"raw_{ts}_{p.name}"
        shutil.copy2(p, dest)
        return str(dest)

    def process_external_data(self, file_path: str, source_name: str = "External_Input", output_dir: str = "vault/sanitized", **sanitize_kwargs) -> dict:
        file_path = str(file_path)
        logger.info(f"GATEWAY: processing {file_path} (source={source_name})")

        # 1) Hash the raw input immediately
        raw_hash = self.ledger.generate_hash(file_path)

        # Optionally keep a copy of raw file in gate logs (local only)
        try:
            raw_copy = self._store_raw_copy(file_path)
        except Exception as e:
            logger.warning(f"Could not copy raw file to gate logs: {e}")
            raw_copy = None

        # 2) Sanitize using local sanitizer
        report = sanitize_dataset(input_path=file_path, output_dir=output_dir, **sanitize_kwargs)
        sanitized_path = report.get("sanitized_path")

        # 3) Hash sanitized output
        clean_hash = self.ledger.generate_hash(sanitized_path)

        # 4) Record in ledger
        metadata = {
            "source": source_name,
            "raw_sha256": raw_hash,
            "clean_sha256": clean_hash,
            "raw_copy": raw_copy,
            "removed_columns": report.get("removed_columns"),
        }
        self.ledger.record_operation("GATEWAY_INGESTION", sanitized_path, metadata=metadata)

        logger.info(f"GATEWAY: ingestion complete. sanitized_hash={clean_hash[:12]}")
        ret = {
            "sanitized_path": sanitized_path,
            "report": report,
            "raw_hash": raw_hash,
            "clean_hash": clean_hash,
            "raw_copy": raw_copy,
        }
        return ret


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, help="Raw input file path")
    p.add_argument("--source", default="External_Input")
    p.add_argument("--output", default="vault/sanitized/")
    p.add_argument("--age-bin", type=int, default=5)
    p.add_argument("--date-freq", default="M")
    p.add_argument("--insecure-allow-default-salt", action="store_true")
    args = p.parse_args()

    # Entrypoint expects PRIVATE_VAULT_SALT to be set; exit if not provided unless insecure flag given
    if os.environ.get("PRIVATE_VAULT_SALT") is None and not args.insecure_allow_default_salt:
        raise RuntimeError("PRIVATE_VAULT_SALT is required for sanitization. Set it in the environment before running the entrance.")

    gate = UniversalEntrance()
    result = gate.process_external_data(args.input, source_name=args.source, output_dir=args.output, age_bin_size=args.age_bin, date_freq=args.date_freq, drop_original_dates=True)
    print(result)
