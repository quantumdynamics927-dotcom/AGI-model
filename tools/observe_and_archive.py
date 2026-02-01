"""Tool: run Node 8 observation and archive the result via MetatronNervousSystem."""
from pathlib import Path
import json
import argparse
from metatron_nervous_system import MetatronNervousSystem
from integrations.quantum_observer import QuantumObserver, pinfs_gateway_from_cid


def main():
    parser = argparse.ArgumentParser(description='Run Node 8 observation and archive result')
    parser.add_argument('--metadata', type=str, required=True, help='Path to local NFT metadata JSON file')
    parser.add_argument('--rpc', type=str, default='https://80002.rpc.thirdweb.com', help='RPC URL for Polygon Amoy')
    parser.add_argument('--tx', type=str, default=None, help='Optional transaction hash to verify')
    parser.add_argument('--registry', type=str, default='cache/dna_registry_test', help='Registry folder')
    parser.add_argument('--hmac-key', type=str, default=None, help='HMAC key for packet signing')
    args = parser.parse_args()

    meta_path = Path(args.metadata)
    if not meta_path.exists():
        raise FileNotFoundError(str(meta_path))

    meta = json.loads(meta_path.read_text())
    # determine pinata URL from image or animation_url
    candidate = meta.get('animation_url') or meta.get('image')
    if candidate:
        pin_url = pinfs_gateway_from_cid(candidate)
    else:
        # fallback to file path
        pin_url = f'file://{meta_path.resolve()}'

    obs = QuantumObserver(rpc_url=args.rpc)
    res = obs.verify_observation(pin_url, tx_hash=args.tx)

    # attach observation result to metadata and save
    meta.setdefault('observations', [])
    meta['observations'].append({'observer': 'quantum_observer', 'result': res})
    meta_path.write_text(json.dumps(meta, indent=2))

    # archive the updated metadata via Metatron
    m = MetatronNervousSystem(Path(args.registry))
    packet = m.create_packet(meta_path, client='quantum_observer', hmac_key=args.hmac_key)
    archive = m.archive_packet(packet)
    print('Archived observation at', archive)


if __name__ == '__main__':
    main()
