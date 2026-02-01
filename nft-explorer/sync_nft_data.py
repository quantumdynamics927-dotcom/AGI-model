#!/usr/bin/env python3
"""
NFT Metadata Scanner & Data Generator
Scans nft_metadata/ folder and generates nft_data.js for the explorer
"""

import os
import json
import glob
from datetime import datetime
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
NFT_METADATA_DIR = BASE_DIR / "nft_metadata"
OUTPUT_FILE = Path(__file__).parent / "nft_data.js"

def classify_nft_type(data, filename):
    """Classify NFT type based on content and filename"""
    if "quantum_nft_" in filename:
        return "quantum"
    elif "quantum_properties" in data:
        return "quantum"
    elif "scientific_data" in data:
        return "molecular"
    elif "provenance" in data and "phi_corr" in str(data.get("provenance", {})):
        return "metatron"
    elif "quantum_hamiltonian" in data:
        return "metatron"
    elif "golden_ratio_coupling" in data:
        return "metatron"
    else:
        return "quantum"  # default

def extract_nft_id(filename, data):
    """Extract NFT ID from filename or data"""
    basename = os.path.basename(filename)

    # quantum_nft_XXXX.json format
    if basename.startswith("quantum_nft_"):
        return basename.replace("quantum_nft_", "").replace(".json", "")

    # XXXX.nft.json format
    if ".nft.json" in basename:
        return basename.replace(".nft.json", "")

    # Try from data
    if "token_id" in data:
        return str(data["token_id"])

    # Fallback to filename hash
    return basename.replace(".json", "")

def normalize_metatron(data, nft_id):
    """Normalize Metatron Node NFT data"""
    provenance = data.get("provenance", {})
    nft_info = data.get("nft", {})
    minted_tx = nft_info.get("minted_tx", {})
    market = nft_info.get("market", {})

    return {
        "id": nft_id,
        "type": "metatron",
        "name": data.get("name", f"Metatron Node #{nft_id[:12]}"),
        "description": data.get("description", ""),
        "category": "Metatron Node",
        "phiCorrelation": provenance.get("phi_corr") or data.get("sequence_phi_correlation", 0),
        "sequence": provenance.get("seq", ""),
        "groundStateEnergy": data.get("ground_state_energy", 0),
        "goldenRatioCoupling": data.get("golden_ratio_coupling", 1.618033988749895),
        "sacredGeometryClass": data.get("sacred_geometry_class", ""),
        "consciousnessMetric": data.get("consciousness_metric", ""),
        "quantumHamiltonian": data.get("quantum_hamiltonian", ""),
        "network": minted_tx.get("network", "POLYGON"),
        "tokenId": minted_tx.get("tokenId"),
        "txHash": minted_tx.get("tx_hash", ""),
        "block": minted_tx.get("block"),
        "ipfsCid": nft_info.get("ipfs_cid", ""),
        "pinCid": nft_info.get("pinning", {}).get("pin_cid", ""),
        "mintStatus": "Minted" if minted_tx.get("tx_hash") else "Pending",
        "openSeaUrl": market.get("opensea", {}).get("url", ""),
        "attributes": data.get("attributes", []),
        "created": data.get("created", ""),
        "hamiltonianPauliTerms": data.get("hamiltonian_pauli_terms", [])
    }

def normalize_molecular(data, nft_id):
    """Normalize Molecular Discovery NFT data"""
    sci_data = data.get("scientific_data", {})
    wave_fn = sci_data.get("wave_function", {})

    return {
        "id": nft_id,
        "type": "molecular",
        "name": data.get("name", f"Molecular Discovery #{nft_id[:8]}"),
        "description": data.get("description", ""),
        "category": "Molecular Discovery",
        "phiResonance": wave_fn.get("phi_resonance_ratio", 1.618033),
        "element": wave_fn.get("psi_state", ""),
        "probabilityDensityMax": wave_fn.get("probability_density_max", ""),
        "agiValidation": sci_data.get("agi_validation_id", ""),
        "fingerprint": sci_data.get("fingerprint", ""),
        "license": data.get("license", ""),
        "image": data.get("image", ""),
        "attributes": data.get("attributes", [])
    }

def normalize_quantum(data, nft_id):
    """Normalize Quantum Consciousness NFT data"""
    qprops = data.get("quantum_properties", {})
    gen_params = data.get("generation_parameters", {})
    tmt_cert = data.get("tmt_os_certification", {})

    return {
        "id": nft_id,
        "type": "quantum",
        "name": data.get("name", f"Quantum Consciousness #{nft_id}"),
        "description": data.get("description", ""),
        "category": "Quantum Consciousness",
        "fidelityScore": qprops.get("fidelity_score", 0),
        "entanglementEntropy": qprops.get("entanglement_entropy", 0),
        "consciousnessComplexity": qprops.get("consciousness_complexity", 0),
        "klDivergence": qprops.get("kl_divergence", 0),
        "quantumProof": qprops.get("quantum_randomness_proof", {}).get("proof", ""),
        "latentSignature": qprops.get("latent_signature", [])[:8],  # First 8 values
        "modelVersion": gen_params.get("model_version", ""),
        "latentDimensions": gen_params.get("latent_dimensions", 32),
        "tmtCertified": tmt_cert.get("quantum_verified", False),
        "consciousnessMapping": tmt_cert.get("consciousness_mapping", False),
        "entanglementPreserved": tmt_cert.get("entanglement_preserved", False),
        "image": data.get("image", ""),
        "externalUrl": data.get("external_url", ""),
        "attributes": data.get("attributes", [])
    }

def scan_nft_metadata():
    """Scan all NFT metadata files and return normalized data"""
    nfts = []

    # Find all JSON files
    patterns = [
        str(NFT_METADATA_DIR / "*.json"),
        str(NFT_METADATA_DIR / "*.nft.json")
    ]

    files = set()
    for pattern in patterns:
        files.update(glob.glob(pattern))

    print(f"Found {len(files)} NFT metadata files")

    for filepath in sorted(files):
        filename = os.path.basename(filepath)

        # Skip non-NFT files
        if filename in ["updates", "seq_3_nft.json"]:
            continue

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            nft_id = extract_nft_id(filename, data)
            nft_type = classify_nft_type(data, filename)

            # Normalize based on type
            if nft_type == "metatron":
                normalized = normalize_metatron(data, nft_id)
            elif nft_type == "molecular":
                normalized = normalize_molecular(data, nft_id)
            else:
                normalized = normalize_quantum(data, nft_id)

            nfts.append(normalized)
            print(f"  [OK] {filename} -> {nft_type} ({normalized['name'][:40]}...)")

        except Exception as e:
            print(f"  [ERROR] Error processing {filename}: {e}")

    return nfts

def generate_js_file(nfts):
    """Generate nft_data.js file"""

    # Sort NFTs: minted first (by tokenId), then by type
    def sort_key(nft):
        token_id = nft.get("tokenId")
        if token_id is not None:
            return (0, token_id, nft["type"])
        return (1, 0, nft["type"], nft["id"])

    nfts_sorted = sorted(nfts, key=sort_key)

    js_content = f"""// Auto-generated NFT data - {datetime.now().isoformat()}
// Generated by sync_nft_data.py
// Total NFTs: {len(nfts_sorted)}

const NFT_DATA = {json.dumps(nfts_sorted, indent=2)};

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {{
    module.exports = NFT_DATA;
}}
"""

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(js_content)

    print(f"\n[OK] Generated {OUTPUT_FILE}")
    print(f"  Total NFTs: {len(nfts_sorted)}")
    print(f"  - Metatron Nodes: {len([n for n in nfts_sorted if n['type'] == 'metatron'])}")
    print(f"  - Molecular: {len([n for n in nfts_sorted if n['type'] == 'molecular'])}")
    print(f"  - Quantum: {len([n for n in nfts_sorted if n['type'] == 'quantum'])}")

def main():
    print("=" * 50)
    print("NFT Metadata Scanner")
    print("=" * 50)
    print(f"Scanning: {NFT_METADATA_DIR}")
    print()

    if not NFT_METADATA_DIR.exists():
        print(f"Error: Directory not found: {NFT_METADATA_DIR}")
        return

    nfts = scan_nft_metadata()

    if nfts:
        generate_js_file(nfts)
    else:
        print("No NFT metadata found!")

if __name__ == "__main__":
    main()
