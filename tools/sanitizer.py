"""tools/sanitizer.py

Local-only dataset sanitizer for the Secure Synthetic Vault.

Purpose:
- Deterministic, salted pseudonymization of IDs
- Drop direct PII columns (names, emails, phones, ssn, addresses)
- Age binning and date coarsening (configurable)
- Produce a sanitization report manifest (JSON)
- Enforce local output dir and do not leak secrets

Usage (local only):
  export PRIVATE_VAULT_SALT="your_secret_salt"
  python tools/sanitizer.py --input data/raw_samples.csv --output vault/sanitized/ --age-bin 5

Security notes:
- PROVIDE A STRONG SECRET VIA ENV VAR `PRIVATE_VAULT_SALT` (never commit it).
- Script enforces that output directory is a local path (no http/s3/ftp) by default.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

# Try to use repository safety helper if present; fall back to simple check
try:
    from security.safety import is_local_path
except Exception:
    def is_local_path(path_str: str) -> bool:
        # conservative local check
        lower = path_str.lower()
        if lower.startswith(('http://', 'https://', 's3://', 'ftp://')):
            return False
        if '://' in path_str:
            return False
        return True


logger = logging.getLogger("sanitizer")
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Common direct identifiers to drop if present
DEFAULT_PII_COLS = [
    "name",
    "full_name",
    "first_name",
    "last_name",
    "email",
    "ssn",
    "social_security",
    "phone",
    "phone_number",
    "address",
    "street",
    "city",
    "state",
    "zip",
    "zipcode",
    "birthdate",
    "dob",
    "date_of_birth",
]

# Regex patterns for inline PII detection (used for scanning and reporting)
PII_PATTERNS = {
    "email": re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"),
    # US-style SSN: 123-45-6789 or 123456789
    "ssn": re.compile(r"\b\d{3}-?\d{2}-?\d{4}\b"),
    "phone": re.compile(r"\b\+?\d[\d\-\s]{7,}\d\b"),
}


def _get_salt() -> Optional[str]:
    """Return salt from env var or None."""
    return os.environ.get("PRIVATE_VAULT_SALT")


def pseudonymize_id(original_id: str, salt: str, prefix: Optional[str] = None) -> str:
    """Creates a deterministic (non-reversible) hash token from original_id and salt.

    Returns a short hex token (16 chars) to keep identifiers compact.
    """
    if original_id is None:
        return None
    h = hashlib.sha256()
    h.update((salt + str(original_id)).encode("utf-8"))
    token = h.hexdigest()[:16]
    return f"{prefix or ''}{token}"


def detect_inline_pii_in_df(df: pd.DataFrame, nrows: int = 100) -> Dict[str, List[str]]:
    """Scan a sample of dataframe cells for PII patterns. Returns a map of pattern name -> list of sample matches."""
    matches = {k: [] for k in PII_PATTERNS}
    sample = df.head(nrows)
    for col in sample.columns:
        for val in sample[col].astype(str).values:
            for name, pat in PII_PATTERNS.items():
                if pat.search(val):
                    matches[name].append(f"{col}:{val}")
                    # keep limited examples
                    if len(matches[name]) > 20:
                        break
    return {k: v for k, v in matches.items() if v}


def age_to_bin(age_val: float, bin_size: int = 5) -> Optional[str]:
    if pd.isna(age_val):
        return None
    try:
        age = int(float(age_val))
    except Exception:
        return None
    start = (age // bin_size) * bin_size
    return f"{start}-{start+bin_size}"


def coarsen_dates(df: pd.DataFrame, date_cols: List[str], freq: str = "M") -> List[str]:
    """Round date columns to a given period (e.g., 'M' monthly, 'D' daily). Returns list of transformed columns."""
    transformed = []
    for col in date_cols:
        try:
            df[col] = pd.to_datetime(df[col], errors="coerce")
            # convert to period string to avoid leaking exact timestamps
            df[col] = df[col].dt.to_period(freq).astype(str)
            transformed.append(col)
        except Exception as e:
            logger.debug(f"Could not coarsen {col}: {e}")
    return transformed


def sanitize_dataset(
    input_path: str,
    output_dir: str,
    salt: Optional[str] = None,
    pii_cols: Optional[List[str]] = None,
    age_col: str = "age",
    age_bin_size: int = 5,
    date_freq: str = "M",
    drop_original_dates: bool = False,
) -> Dict:
    """Sanitize a dataset and write sanitized data + report to output_dir.

    Returns a report dict with details of operations performed.
    """
    if salt is None:
        salt = _get_salt()
    if salt is None:
        raise RuntimeError("Environment variable PRIVATE_VAULT_SALT must be set for deterministic pseudonymization.")

    input_path = Path(input_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Input not found: {input_path}")

    outdir = Path(output_dir)
    if not is_local_path(str(outdir)):
        raise RuntimeError(f"Output directory '{outdir}' is not a local path. Aborting to enforce local-only operation.")
    outdir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Reading input: {input_path}")
    # Support CSV or Parquet
    if input_path.suffix.lower() in [".csv"]:
        df = pd.read_csv(input_path)
    elif input_path.suffix.lower() in [".parquet", ".parq"]:
        df = pd.read_parquet(input_path)
    else:
        # try pandas autodetect
        df = pd.read_csv(input_path)

    report = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "input_path": str(input_path),
        "input_rows": len(df),
        "input_columns": list(df.columns),
        "removed_columns": [],
        "transformed_columns": [],
        "pii_detection": {},
    }

    # 1) Detect inline PII in sample
    inline_pii = detect_inline_pii_in_df(df)
    report["pii_detection"] = inline_pii
    if inline_pii:
        logger.warning(f"PII patterns detected in sample: {list(inline_pii.keys())}")

    # 2) Drop obvious PII columns
    drop_cols = []
    maybe_pii = pii_cols or DEFAULT_PII_COLS
    for c in maybe_pii:
        if c in df.columns:
            drop_cols.append(c)
    if drop_cols:
        df.drop(columns=drop_cols, inplace=True, errors="ignore")
        report["removed_columns"].extend(drop_cols)
        logger.info(f"Dropped PII columns: {drop_cols}")

    # 3) Pseudonymize ids (patient_id, sample_id, subject_id)
    id_cols = [c for c in ["patient_id", "subject_id", "sample_id", "id"] if c in df.columns]
    for col in id_cols:
        token_col = "subject_token" if col != "sample_id" else "sample_token"
        df[token_col] = df[col].apply(lambda x: pseudonymize_id(x, salt))
        df.drop(columns=[col], inplace=True)
        report["transformed_columns"].append(f"{col} -> {token_col}")
        logger.info(f"Pseudonymized {col} -> {token_col}")

    # 4) Age binning
    if age_col in df.columns:
        df["age_group"] = df[age_col].apply(lambda v: age_to_bin(v, bin_size=age_bin_size))
        if drop_original_dates:
            df.drop(columns=[age_col], inplace=True)
        else:
            df.drop(columns=[age_col], inplace=True)
        report["transformed_columns"].append(f"{age_col} -> age_group (bin={age_bin_size})")
        logger.info("Applied age binning")

    # 5) Date coarsening
    date_cols = [c for c in df.columns if "date" in c.lower() or "time" in c.lower()]
    if date_cols:
        transformed = coarsen_dates(df, date_cols, freq=date_freq)
        report["transformed_columns"].extend([f"{c} -> period({date_freq})" for c in transformed])
        logger.info(f"Coarsened date columns: {transformed}")

    # 6) Final PII scan on sanitized df sample
    post_inline_pii = detect_inline_pii_in_df(df)
    report["post_pii_detection"] = post_inline_pii

    # 7) Save sanitized output and report
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    sanitized_path = outdir / f"sanitized_data_{timestamp}.parquet"
    report_path = outdir / f"sanitization_report_{timestamp}.json"

    # Try to write Parquet; if parquet engine not available, fall back to CSV to avoid hard dependency
    format_used = None
    try:
        df.to_parquet(sanitized_path)
        final_path = sanitized_path
        format_used = 'parquet'
        logger.info(f"Wrote sanitized dataset as parquet: {final_path}")
    except Exception as e:
        # Fallback to CSV (avoids requiring pyarrow/fastparquet in minimal environments)
        csv_path = outdir / f"sanitized_data_{timestamp}.csv"
        df.to_csv(csv_path, index=False)
        final_path = csv_path
        format_used = 'csv'
        logger.warning(f"Parquet write failed ({e}); fell back to CSV: {final_path}")

    # add output fingerprint
    sha256 = hashlib.sha256()
    with final_path.open("rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    report["sanitized_path"] = str(final_path)
    report["sanitized_format"] = format_used
    report["sanitized_sha256"] = sha256.hexdigest()

    with report_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    logger.info(f"Sanitized dataset written to {final_path}")
    logger.info(f"Sanitization report written to {report_path}")

    return report


def _build_arg_parser():
    p = argparse.ArgumentParser(prog="sanitizer.py", description="Local dataset sanitizer for Secure Synthetic Vault")
    p.add_argument("--input", required=True, help="Input CSV or Parquet file path")
    p.add_argument("--output", default="vault/sanitized/", help="Output directory (local only)")
    p.add_argument("--age-col", default="age", help="Column name for age")
    p.add_argument("--age-bin", type=int, default=5, help="Age bin size (years)")
    p.add_argument("--date-freq", default="M", help="Date coarsening period (e.g., M for month, D for day)")
    p.add_argument("--pii-cols", nargs="*", help="Additional PII columns to drop")
    p.add_argument("--insecure-allow-default-salt", action="store_true", help="If set, uses a default salt when env var not present (not recommended)")
    p.add_argument("--quiet", action="store_true")
    return p


def main(argv: Optional[List[str]] = None):
    parser = _build_arg_parser()
    args = parser.parse_args(argv)
    if args.quiet:
        logger.setLevel(logging.WARNING)

    salt = _get_salt()
    if salt is None:
        if args.insecure_allow_default_salt:
            logger.warning("PRIVATE_VAULT_SALT not set — using insecure default salt (not recommended)")
            salt = "default_local_salt"
        else:
            raise RuntimeError("PRIVATE_VAULT_SALT environment variable is required for sanitization. Use --insecure-allow-default-salt to bypass (not recommended).")

    report = sanitize_dataset(
        input_path=args.input,
        output_dir=args.output,
        salt=salt,
        pii_cols=args.pii_cols,
        age_col=args.age_col,
        age_bin_size=args.age_bin,
        date_freq=args.date_freq,
        drop_original_dates=True,
    )

    logger.info("Sanitization complete.")
    logger.info(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
