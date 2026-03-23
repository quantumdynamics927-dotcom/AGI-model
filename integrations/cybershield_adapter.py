"""integrations/cybershield_adapter.py

Adapter to integrate CyberShield-Pro scans with the Secure Synthetic Vault.
All operations are local-only and record provenance in `vault/ledger.json`.

APIs:
- ingest_scan_file(file_path, source) -> dict
- ingest_scan_payload(payload_dict, source) -> dict

Returns a dict with sanitized_path, clean_hash, ledger_index, report
"""
from __future__ import annotations

import logging
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Optional, Dict, Any

import pandas as pd

from tools.vault_ledger import VaultLedger, vault_path
from tools.entrance import UniversalEntrance

logger = logging.getLogger("cybershield_adapter")
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def _store_raw_copy(
    file_path: str,
    dest_dir: str | Path | None = None,
) -> str:
    p = Path(file_path)
    ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    destination_dir = (
        Path(dest_dir)
        if dest_dir is not None
        else vault_path("gatekeeper_logs")
    )
    dest = destination_dir / f"raw_{ts}_{p.name}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(p, dest)
    return str(dest)


def ingest_scan_file(
    file_path: str,
    source: str = "cybershield",
    ledger: Optional[VaultLedger] = None,
    sanitize_kwargs: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Ingest a raw scan file into the vault via the Universal Entrance.

    This computes a raw hash, stores a raw copy under gatekeeper logs, records a ledger entry,
    sanitizes via the UniversalEntrance (which itself records a ledger entry), and returns
    sanitized metadata.
    """
    ledger = ledger or VaultLedger()
    sanitize_kwargs = sanitize_kwargs or {}

    # 1) raw hash and local copy
    raw_hash = ledger.generate_hash(file_path)
    raw_copy = _store_raw_copy(file_path)
    ledger.record_operation(
        "CYBERSHIELD_SCAN_RAW",
        raw_copy,
        metadata={"source": source, "raw_hash": raw_hash},
    )

    # 2) sanitize via gatekeeper (records GATEWAY_INGESTION in ledger)
    gate = UniversalEntrance(ledger=ledger)
    sanitized = gate.process_external_data(
        file_path,
        source_name=source,
        **sanitize_kwargs,
    )

    # find ledger index (last entry)
    ledger_index = len(ledger.history) - 1

    result = {
        "sanitized_path": sanitized.get("sanitized_path"),
        "clean_hash": sanitized.get("clean_hash"),
        "ledger_index": ledger_index,
        "report": sanitized.get("report"),
        "raw_copy": raw_copy,
    }
    logger.info(
        "Ingested scan file. sanitized=%s ledger_index=%s",
        result["sanitized_path"],
        ledger_index,
    )
    return result


def ingest_scan_payload(
    payload: Dict[str, Any],
    source: str = "cybershield",
    ledger: Optional[VaultLedger] = None,
    sanitize_kwargs: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Ingest a payload (dict) by writing to a temp CSV and calling ingest_scan_file."""
    # write single-row CSV
    df = pd.DataFrame([payload])
    tmp_dir = vault_path("gatekeeper_tmp")
    tmp_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    tmp_path = tmp_dir / f"payload_{ts}.csv"
    df.to_csv(tmp_path, index=False)
    return ingest_scan_file(
        str(tmp_path),
        source=source,
        ledger=ledger,
        sanitize_kwargs=sanitize_kwargs,
    )
