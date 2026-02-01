"""
Synapse update: encode seq_3 metrics into DNA blueprint and register artifacts.
Generates:
 - e:\AGI model\dna_registry\seq_3_blueprint.json
 - e:\AGI model\nft_metadata\seq_3_nft.json
 - e:\AGI model\reports\sync_report.md (appends an entry)

Safe: uses MetatronNervousSystem for encoding and hashing.
"""
from pathlib import Path
import json
import hashlib
import time
import os

from metatron_nervous_system import MetatronNervousSystem

ROOT = Path(r"e:\AGI model")
REGISTRY = ROOT / "dna_registry"
NFT_DIR = ROOT / "nft_metadata"
REPORTS = ROOT / "reports"

REGISTRY.mkdir(parents=True, exist_ok=True)
NFT_DIR.mkdir(parents=True, exist_ok=True)
REPORTS.mkdir(parents=True, exist_ok=True)

m = MetatronNervousSystem(REGISTRY)

# seq_3 metrics from research
sequence_id = "seq_3"
metrics = {
    "fidelity_gain": 1.8935219924718318,
    "phi_correlation": 1.1439986700106974
}

print(f"[*] Starting synapse update for {sequence_id}...")

compressed_gain = m.phi_compress(metrics['fidelity_gain'])
dna_blueprint = m.encode_to_dna(compressed_gain)

# Prepare DNA blueprint file
blueprint = {
    "sequence_id": sequence_id,
    "dna_blueprint": dna_blueprint,
    "phi_scaling": compressed_gain,
    "source_metrics": metrics,
    "certification": "TMT-OS v4.0 DNA-Verified",
    "timestamp": int(time.time())
}

blueprint_path = REGISTRY / f"{sequence_id}_blueprint.json"
blueprint_path.write_text(json.dumps(blueprint, indent=2))

# Compute SHA-256 of the blueprint file and add manifest_hash
def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()

blueprint_sha = sha256_of_file(blueprint_path)
blueprint['sha256'] = blueprint_sha
blueprint_path.write_text(json.dumps(blueprint, indent=2))

print(f"[✅] Blueprint written: {blueprint_path}")
print(f"[✅] Blueprint SHA-256: {blueprint_sha}")

# Prepare NFT metadata
nft_meta = {
    "name": "TMT-OS Research: seq_3 Crystallization",
    "description": "Certificado de Procedencia Cuántica: Optimización de fidelidad mediante bombeo acústico.",
    "attributes": [
        {"trait_type": "Researcher", "value": "Agent 13 / Metatron Core"},
        {"trait_type": "Framework", "value": "TMT-OS v4.0"},
        {"trait_type": "Phi Correlation", "value": metrics['phi_correlation']},
        {"trait_type": "Fidelity Gain", "value": metrics['fidelity_gain']},
        {"trait_type": "DNA Blueprint", "value": dna_blueprint},
        {"trait_type": "Integrity SHA256", "value": blueprint_sha}
    ],
    "provenance": {
        "timestamp": int(time.time()),
        "manifest_hash": blueprint_sha
    }
}

nft_path = NFT_DIR / f"{sequence_id}_nft.json"
nft_path.write_text(json.dumps(nft_meta, indent=2))

print(f"[✅] NFT metadata written: {nft_path}")

# Append or create Sync Report
report_path = REPORTS / "sync_report.md"
report_entry = f"""
## Sync Entry — {sequence_id}

- Sequence ID: `{sequence_id}`
- Phi Correlation: `{metrics['phi_correlation']}`
- Fidelity Gain: `{metrics['fidelity_gain']}`
- Compressed (phi-scaled): `{compressed_gain}`
- DNA Blueprint: `{dna_blueprint}`
- Blueprint SHA-256: `{blueprint_sha}`
- Blueprint Path: `{str(blueprint_path)}`
- NFT Metadata: `{str(nft_path)}`
- Timestamp: `{int(time.time())}`

"""
if report_path.exists():
    with report_path.open('a', encoding='utf-8') as f:
        f.write(report_entry)
else:
    report_header = "# Sync Report\n\nThis report contains synched DNA blueprints and provenance.\n\n"
    report_header += report_entry
    report_path.write_text(report_header)

print(f"[✅] Report updated: {report_path}")

print("[🎯] Synapse update complete.")

if __name__ == '__main__':
    pass
