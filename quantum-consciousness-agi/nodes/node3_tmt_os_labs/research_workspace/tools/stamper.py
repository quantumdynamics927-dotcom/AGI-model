"""Simple SHA-256 stamper for delivery files.

Usage:
    python stamper.py file_or_folder [--out DELIVERY_DIR]

This script will compute SHA-256 hashes for files and emit .sha256 files and a summary JSON.
"""

from pathlib import Path
import argparse
import hashlib
import json
import time
import uuid
import hmac
import os
from typing import Optional, Any


def sha256_file(path: Path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def generate_nft_metadata(file_path: Path, client_name: str, physics_metrics: dict):
    """Generates an ERC-1155/721-compatible NFT metadata JSON for a delivered file."""
    sha256_hash = hashlib.sha256()
    with file_path.open("rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    file_checksum = sha256_hash.hexdigest()

    metadata = {
        "name": f"TMT-OS Research: {client_name} - Batch #{uuid.uuid4().hex[:8].upper()}",
        "description": "Certified Quantum-Genetic Research generated via TMT-OS Boveda Cuantica.",
        "image": "ipfs://[Link_To_Your_Graph_Or_Logo]",
        "external_url": "https://www.upwork.com/freelancers/~your_id",
        "attributes": [
            {"trait_type": "Researcher", "value": "Jose/Agent 13"},
            {"trait_type": "Framework", "value": "TMT-OS v4.0"},
            {"trait_type": "Integrity_Hash", "value": file_checksum},
            {"trait_type": "Timestamp", "value": int(time.time())}
        ]
    }

    for metric, value in (physics_metrics or {}).items():
        metadata["attributes"].append({
            "trait_type": metric.replace("_", " ").title(),
            "value": value
        })

    output_path = str(file_path) + ".nft.json"
    with open(output_path, "w") as f:
        json.dump(metadata, f, indent=4)

    print(f"[OK] NFT Metadata generated: {output_path}")
    return metadata


def stamp_file(path: Path, out_dir: Path = None, client_name: Optional[str] = None, physics_metrics: Optional[dict] = None, hmac_key: Optional[str] = None):
    digest = sha256_file(path)
    meta = {
        "path": str(path.resolve()),
        "filename": path.name,
        "sha256": digest,
        "size": path.stat().st_size,
        "timestamp": time.time()
    }
    if out_dir is None:
        out_dir = path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    # Write .sha256 companion file
    sha_file = out_dir / (path.name + ".sha256")
    sha_file.write_text(digest)
    # Write metadata json
    meta_file = out_dir / (path.name + ".sha256.json")
    meta_file.write_text(json.dumps(meta, indent=2))

    # Optionally generate NFT metadata
    nft_meta = None
    if client_name:
        nft_meta = generate_nft_metadata(path, client_name, physics_metrics or {})
        meta["nft_metadata"] = str(Path(str(path) + ".nft.json"))
        # Update metadata file with nft reference
        meta_file.write_text(json.dumps(meta, indent=2))

    # Optionally add HMAC signature if key is provided (env var or param)
    final_key = hmac_key or os.getenv('TMTOS_STAMPER_KEY')
    if final_key:
        sig = hmac_sign(digest.encode('utf-8'), final_key.encode('utf-8'))
        meta['hmac_signature'] = sig
        meta_file.write_text(json.dumps(meta, indent=2))

    return meta


def hmac_sign(message: bytes, key: bytes) -> str:
    """Return hex HMAC-SHA256 signature for message using key."""
    return hmac.new(key, message, hashlib.sha256).hexdigest()


def stamp_folder(folder: Path, out_dir: Path = None, client_name: Optional[str] = None, physics_metrics: Optional[dict] = None, hmac_key: Optional[str] = None):
    results = []
    for p in sorted(folder.rglob("*")):
        if p.is_file():
            results.append(stamp_file(p, out_dir=out_dir, client_name=client_name, physics_metrics=physics_metrics, hmac_key=hmac_key))
    summary = {
        "folder": str(folder.resolve()),
        "timestamp": time.time(),
        "files": results
    }
    if out_dir is None:
        out_dir = folder
    (out_dir / "stamps_summary.json").write_text(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate SHA-256 stamps for files or folders")
    parser.add_argument("target", type=str, help="File or folder to stamp")
    parser.add_argument("--out", type=str, help="Output directory for stamps (default: same folder)")
    parser.add_argument("--nft", action="store_true", help="Generate ERC-1155/721 compatible NFT metadata for files")
    parser.add_argument("--client-name", type=str, help="Client name to include in NFT metadata")
    parser.add_argument("--metrics", type=str, help="JSON string or path to JSON file with physics metrics")
    parser.add_argument("--hmac", action="store_true", help="Include HMAC-SHA256 signature using TMTOS_STAMPER_KEY or --stamper-key")
    parser.add_argument("--stamper-key", type=str, help="Provide HMAC key directly (overrides env var)")
    args = parser.parse_args()

    p = Path(args.target)
    out = Path(args.out) if args.out else None

    hmac_key = args.stamper_key if args.stamper_key else (os.getenv('TMTOS_STAMPER_KEY') if args.hmac else None)

    if not p.exists():
        print("Target does not exist:", p)
        raise SystemExit(1)

    def _load_metrics(s: Optional[str]):
        if not s:
            return {}
        s = s.strip()
        sp = Path(s)
        if sp.exists():
            return json.loads(sp.read_text())
        try:
            return json.loads(s)
        except Exception:
            print("Could not parse --metrics. Expecting JSON string or path to JSON file.")
            raise SystemExit(1)

    metrics = _load_metrics(args.metrics) if args.metrics else {}

    if p.is_file():
        if args.nft and not args.client_name:
            print("When using --nft, --client-name is required.")
            raise SystemExit(1)
        meta = stamp_file(p, out_dir=out, client_name=(args.client_name if args.nft else None), physics_metrics=(metrics if args.nft else None), hmac_key=hmac_key)
        print("Stamped:", meta['filename'], meta['sha256'])
        if 'nft_metadata' in meta:
            print("NFT metadata:", meta['nft_metadata'])
        if 'hmac_signature' in meta:
            print("HMAC signature:", meta['hmac_signature'])
    else:
        summary = stamp_folder(p, out_dir=out, client_name=(args.client_name if args.nft else None), physics_metrics=(metrics if args.nft else None), hmac_key=hmac_key)
        print("Stamped folder:", summary['folder'], "->", len(summary['files']), "files")
