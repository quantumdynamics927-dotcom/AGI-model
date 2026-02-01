"""Metatron Nervous System

Scans result files under specified directories, encodes numeric metrics into DNA-like packets using
phi-based compression and base-4 encoding, signs packets with HMAC, and archives packets to a dna_registry.

Usage:
    python metatron_nervous_system.py --scan "E:\\AGI model" "E:\\tmt-os" --registry "E:\\AGI model\\dna_registry"

Environment:
    TMTOS_STAMPER_KEY (optional) - HMAC key; if not provided, signatures are omitted unless --stamper-key is used.
"""
from pathlib import Path
import argparse
import hashlib
import json
import time
import os
import math
import hmac
import logging
from typing import Dict, Any, List, Optional

PHI = 1.618033988749895
SRY_HEADER = "AACAAT"
SRY_FOOTER = "TCCGGA"
DEFAULT_KMER = 27

logger = logging.getLogger("metatron")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(ch)


# Node registry: map functional node names to metadata including Platonic solid mapping.
# This allows Metatron (Node 13) to reason about geometric relationships between nodes.
NODE_REGISTRY = {
    'node1_base_os': {
        'node_id': 1,
        'role': 'TMT-OS Base Environment',
        'platonic_solid': 'Cube',
        'path': 'TMT-OS/node1_base_os.py',
        'contact': 'metatron'
    },
    'node2_cybershield': {
        'node_id': 2,
        'role': 'CyberShield Security Layer',
        'platonic_solid': 'Tetrahedron',
        'path': 'TMT-OS/node2_cybershield.py',
        'contact': 'metatron'
    },
    'tmt-os-labs': {
        'node_id': 3,
        'role': 'Experimental labs',
        'platonic_solid': 'Icosahedron',
        'path': 'TMT-OS-Labs/node3_experimental_labs.py',
        'contact': 'metatron'
    },
    'node4_nft_layer': {
        'node_id': 4,
        'role': 'NFT / Asset Layer',
        'platonic_solid': 'Dodecahedron',
        'path': 'TMT-OS/node4_nft_layer.py',
        'contact': 'metatron'
    }
}


def register_node(name: str, node_id: int, role: str, path: str, platonic_solid: str = None, contact: str = None):
    """Register or update a functional node in the Metatron node registry."""
    NODE_REGISTRY[name] = {
        'node_id': node_id,
        'role': role,
        'platonic_solid': platonic_solid,
        'path': path,
        'contact': contact
    }
    logger.info('Registered node: %s (id=%s, solid=%s)', name, node_id, platonic_solid)


def get_node_info(name: str) -> Optional[Dict[str, Any]]:
    """Retrieve registered node metadata by name."""
    return NODE_REGISTRY.get(name)


# Ensure Molecular Geometry node is registered and mapped to the Octahedron (Node 5)
if 'node5_spatial_intelligence' not in NODE_REGISTRY:
    register_node(
        name='node5_spatial_intelligence',
        node_id=5,
        role='Spatial intelligence: molecular & atomic geometry',
        path='molecular_geometry/node5_spatial_intelligence.py',
        platonic_solid='Octahedron',
        contact='metatron'
    )


# Register Data Provenance node (Node 6)
if 'node6_audit_trails' not in NODE_REGISTRY:
    register_node(
        name='node6_audit_trails',
        node_id=6,
        role='Data provenance, lineage, and immutable audit trails',
        path='data_provenance/node6_audit_trails.py',
        platonic_solid='Metatron Nexus',
        contact='metatron'
    )


# Register NFT Inventor node (Node 7)
if 'node7_nft_inventor' not in NODE_REGISTRY:
    register_node(
        name='node7_nft_inventor',
        node_id=7,
        role='NFT Inventor: crystallizes research into sovereign digital assets',
        path='nft_inventor.py',
        platonic_solid='Heptagram',
        contact='metatron'
    )


# Register Quantum Observer node (Node 8)
if 'node8_chain_monitor' not in NODE_REGISTRY:
    register_node(
        name='node8_chain_monitor',
        node_id=8,
        role='Quantum Observer: watches chain for minted assets and confirms collapse',
        path='quantum_observer/node8_chain_monitor.py',
        platonic_solid='Octave',
        contact='metatron'
    )


# Register QVAE Bridge node (Node 9)
if 'node9_qvae_bridge' not in NODE_REGISTRY:
    register_node(
        name='node9_qvae_bridge',
        node_id=9,
        role='QVAE Bridge: maps classical latent space to Wedjat Hilbert space and manages QVAE jobs',
        path='qvae_bridge.py',
        platonic_solid='Merkabah',
        contact='metatron'
    )


# Register Bio-Digital Interface node (Node 10)
if 'bio_digital_interface' not in NODE_REGISTRY:
    register_node(
        name='bio_digital_interface',
        node_id=10,
        role='Bio-Digital Interface: translates quantum states into symbolic biological representations',
        path='Node10_BioDigital',
        platonic_solid='Merkaba-Bio',
        contact='metatron'
    )


# Register Frequency Master node (Node 11)
if 'frequency_master' not in NODE_REGISTRY:
    register_node(
        name='frequency_master',
        node_id=11,
        role='Frequency Master: Tesla Triangle/Chord analysis and consciousness integral computation',
        path='FrequencyMaster',
        platonic_solid='Tesla Triangle',
        contact='metatron'
    )


# Register Neural Synapse node (Node 12)
if 'neural_synapse' not in NODE_REGISTRY:
    register_node(
        name='neural_synapse',
        node_id=12,
        role='Neural Synapse: assembles collective connectivity from bio-digital outputs',
        path='NeuralSynapse',
        platonic_solid='Omega Point',
        contact='metatron'
    )


class MetatronNervousSystem:
    def __init__(self, registry: Path, kmer: int = DEFAULT_KMER):
        self.registry = registry
        self.registry.mkdir(parents=True, exist_ok=True)
        self.kmer = kmer
        self.nucleotide_map = {0: 'A', 1: 'C', 2: 'T', 3: 'G'}
        self.reverse_map = {v: k for k, v in self.nucleotide_map.items()}

    def phi_compress(self, value: float) -> float:
        return value / (PHI ** 2)

    def encode_to_dna(self, data_float: float) -> str:
        # scaled integer representation
        scaled = int(abs(data_float) * 10000)
        seq = []
        if scaled == 0:
            seq.append(self.nucleotide_map[0])
        while scaled > 0 and len(seq) < self.kmer:
            seq.append(self.nucleotide_map[scaled % 4])
            scaled //= 4
        seq = seq[::-1]
        seq_str = ''.join(seq).rjust(self.kmer, 'A')[-self.kmer:]
        return f"{SRY_HEADER}_{seq_str}_{SRY_FOOTER}"

    def decode_from_dna(self, dna: str) -> float:
        # expects header_body_footer
        parts = dna.split('_')
        if len(parts) != 3:
            raise ValueError("Malformed DNA packet")
        body = parts[1]
        val = 0
        for ch in body:
            val = val * 4 + self.reverse_map.get(ch, 0)
        # reverse scaling
        return float(val) / 10000.0

    def sha256(self, path: Path) -> str:
        h = hashlib.sha256()
        with path.open('rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                h.update(chunk)
        return h.hexdigest()

    def hmac_sign(self, message: str, key: str) -> str:
        return hmac.new(key.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).hexdigest()

    def extract_metrics_from_file(self, path: Path) -> Dict[str, Any]:
        # Try CSV with fitness and phi_score columns, else fallback to file size
        metrics = {}
        try:
            if path.suffix.lower() in ['.csv']:
                import pandas as pd
                df = pd.read_csv(path)
                if 'fitness' in df.columns and 'phi_score' in df.columns:
                    metrics['phi_mean'] = float(((df['fitness'] / PHI) * df['phi_score']).mean())
                metrics['rows'] = int(len(df))
            elif path.suffix.lower() in ['.json']:
                data = json.loads(path.read_text())
                metrics['keys'] = len(data) if isinstance(data, dict) else 0
        except Exception as e:
            logger.debug('Metric extraction failed for %s: %s', path, e)
        metrics['size'] = path.stat().st_size
        return metrics

    def create_packet(self, source_path: Path, client: str = 'internal', hmac_key: Optional[str] = None) -> Dict[str, Any]:
        sha = self.sha256(source_path)
        metrics = self.extract_metrics_from_file(source_path)
        # pick a numeric seed value: phi_mean if present else size
        num_val = metrics.get('phi_mean', metrics.get('size', 0))
        compressed = self.phi_compress(float(num_val))
        dna = self.encode_to_dna(compressed)
        packet = {
            'source': str(source_path.resolve()),
            'filename': source_path.name,
            'sha256': sha,
            'timestamp': int(time.time()),
            'metrics': metrics,
            'compressed_value': compressed,
            'dna_packet': dna,
            'client': client
        }
        if hmac_key:
            # Prefer using the provenance.signature helper if available (HMAC + optional PKI support).
            try:
                from provenance import signature as prov_sig
                packet['hmac_signature'] = prov_sig.create_hmac_signature(sha, hmac_key)
            except Exception:
                # Fallback to built-in HMAC implementation
                packet['hmac_signature'] = self.hmac_sign(sha, hmac_key)
        return packet

    def verify_packet_signature(self, packet: Dict[str, Any], hmac_key: str) -> bool:
        """Verify an archival packet's HMAC signature. Uses provenance helper when available.

        Returns True if signature verifies, False otherwise.
        """
        sha = packet.get('sha256')
        sig = packet.get('hmac_signature')
        if not sha or not sig:
            return False
        try:
            from provenance import signature as prov_sig
            return prov_sig.verify_hmac_signature(sha, hmac_key, sig)
        except Exception:
            # Fallback to local verification
            return hmac.compare_digest(self.hmac_sign(sha, hmac_key), sig)

    def archive_packet(self, packet: Dict[str, Any]) -> Path:
        fname = f"{int(time.time())}_{packet['filename']}.dna.json"
        out = self.registry / fname
        out.write_text(json.dumps(packet, indent=2))
        logger.info('Archived DNA packet: %s', out)
        return out

    def scan_and_archive(self, roots: List[Path], client: str = 'internal', hmac_key: Optional[str] = None, extensions: Optional[List[str]] = None) -> List[Path]:
        if extensions is None:
            extensions = ['.csv', '.json', '.txt']
        archived = []
        seen = set()
        for root in roots:
            if not root.exists():
                logger.warning('Root does not exist: %s', root)
                continue
            for p in root.rglob('*'):
                if p.is_file() and p.suffix.lower() in extensions:
                    key = (p.resolve(), p.stat().st_mtime)
                    if key in seen:
                        continue
                    seen.add(key)
                    packet = self.create_packet(p, client=client, hmac_key=hmac_key)
                    out = self.archive_packet(packet)
                    archived.append(out)
        return archived

    def generate_molecular_nft(self, structure_input, model_path: str = 'best_model.pt', token_id: Optional[str] = None,
                               client: str = 'internal', hmac_key: Optional[str] = None, save_metadata: bool = True):
        """Generate NFT metadata for a molecular structure using the MolecularNFTGenerator.

        This method attempts to import the molecular geometry integration module lazily so that the
        broader system does not import heavy molecular-analysis dependencies unless needed.

        Args:
            structure_input: Input structure (path or molecule object) to pass to the generator.
            model_path: Path to a model or resources required by the generator.
            token_id: Optional token id to assign.
            client: Client identifier for archival packet creation.
            hmac_key: Optional HMAC key to sign the archival packet.
            save_metadata: If True, save NFT metadata under `nft_metadata/` and archive packet.

        Returns:
            Tuple(metadata_dict, token_id, archive_path or None)
        """
        # Try importing the MolecularNFTGenerator from likely locations
        MolecularNFTGenerator = None
        possible_imports = [
            'molecular_geometry.integration',
            'MolecularGeometry.integration',
            'integration',
        ]
        for mod in possible_imports:
            try:
                module = __import__(mod, fromlist=['MolecularNFTGenerator'])
                MolecularNFTGenerator = getattr(module, 'MolecularNFTGenerator', None)
                if MolecularNFTGenerator:
                    break
            except Exception:
                continue

        if MolecularNFTGenerator is None:
            # Fallback: if no MolecularNFTGenerator is available, attempt to use the local NFTInventor
            try:
                from nft_inventor import NFTInventor
            except Exception:
                raise ImportError('MolecularNFTGenerator not found and NFTInventor unavailable. Ensure an integration module is installed or nft_inventor.py exists.')

        archive_path = None

        # If we have a MolecularNFTGenerator, attempt to use it; otherwise fallback to NFTInventor.
        if MolecularNFTGenerator:
            try:
                try:
                    gen = MolecularNFTGenerator(model_path=model_path)
                except TypeError:
                    gen = MolecularNFTGenerator()
                metadata, assigned_token = gen.create_nft_metadata(structure_input, token_id=token_id)
            except Exception as e:
                logger.info('MolecularNFTGenerator present but failed to instantiate/use: %s; falling back to NFTInventor', e)
                # fallback to NFTInventor (import locally since it may not have been imported earlier)
                try:
                    from nft_inventor import NFTInventor
                except Exception:
                    raise RuntimeError('NFTInventor unavailable for fallback after MolecularNFTGenerator failure')
                inv = NFTInventor()
                base = {
                    'title': structure_input.get('title', 'Molecular Discovery'),
                    'description': structure_input.get('description', ''),
                }
                params = structure_input.get('params', structure_input)
                fingerprint = inv.generate_quantum_fingerprint(params)
                glb_path = inv.render_glb(structure_input.get('coordinates'), out_name=fingerprint[:8])
                attributes = structure_input.get('attributes')
                scientific_data = structure_input.get('scientific_data', {})
                scientific_data.setdefault('wave_function', structure_input.get('wave_function', {}))
                scientific_data['fingerprint'] = fingerprint
                scientific_data['agi_validation_id'] = scientific_data.get('agi_validation_id', 'METATRON-13-ALPHA')
                metadata = inv.create_ipnft_metadata(
                    name=base['title'],
                    description=base['description'],
                    image_cid=structure_input.get('image_cid'),
                    glb_cid=None,
                    attributes=attributes,
                    scientific_data=scientific_data,
                    license=structure_input.get('license', 'MIT-Open-Science-2026-v2')
                )
                assigned_token = metadata.get('token_id')
        else:
            # Use NFTInventor fallback to assemble metadata from structure_input
            inv = NFTInventor()
            base = {
                'title': structure_input.get('title', 'Molecular Discovery'),
                'description': structure_input.get('description', ''),
            }
            params = structure_input.get('params', structure_input)
            fingerprint = inv.generate_quantum_fingerprint(params)
            glb_path = inv.render_glb(structure_input.get('coordinates'), out_name=fingerprint[:8])
            attributes = structure_input.get('attributes')
            scientific_data = structure_input.get('scientific_data', {})
            scientific_data.setdefault('wave_function', structure_input.get('wave_function', {}))
            scientific_data['fingerprint'] = fingerprint
            scientific_data['agi_validation_id'] = scientific_data.get('agi_validation_id', 'METATRON-13-ALPHA')
            metadata = inv.create_ipnft_metadata(
                name=base['title'],
                description=base['description'],
                image_cid=structure_input.get('image_cid'),
                glb_cid=None,
                attributes=attributes,
                scientific_data=scientific_data,
                license=structure_input.get('license', 'MIT-Open-Science-2026-v2')
            )
            assigned_token = metadata.get('token_id')

        # Save and archive metadata if requested. We update the metadata with provenance info after archiving.
        if save_metadata:
            out_dir = Path('nft_metadata')
            out_dir.mkdir(parents=True, exist_ok=True)
            fname = f"{assigned_token}.nft.json"
            out_path = out_dir / fname
            out_path.write_text(json.dumps(metadata, indent=2))
            logger.info('Saved molecular NFT metadata: %s', out_path)
            # Create and archive DNA packet for Metatron registry; then embed provenance reference
            try:
                packet = self.create_packet(out_path, client=client, hmac_key=hmac_key)
                archive_path = self.archive_packet(packet)
                # attach provenance reference to metadata and rewrite
                prov_ref = {
                    'sha256': packet.get('sha256'),
                    'hmac_signature': packet.get('hmac_signature')
                }
                metadata.setdefault('scientific_data', {})['provenance_hash'] = prov_ref
                out_path.write_text(json.dumps(metadata, indent=2))
            except Exception as e:
                logger.warning('Failed to archive NFT metadata packet: %s', e)

            # Attempt to upload metadata and assets to IPFS (adapter supports placeholders if no node)
            try:
                from integrations import ipfs_adapter
                # upload GLB asset if present in metadata.scientific_data.animation_asset path
                glb_path = None
                asset_path = metadata.get('scientific_data', {}).get('asset')
                if asset_path:
                    try:
                        glb_path = Path(asset_path)
                        cid_glb = ipfs_adapter.upload_file(glb_path)
                        metadata['animation_url'] = f'ipfs://{cid_glb}'
                    except Exception as e:
                        logger.debug('GLB upload failed: %s', e)

                # upload metadata JSON itself
                cid_meta = ipfs_adapter.upload_file(out_path)
                metadata['image'] = metadata.get('image') or f'ipfs://{cid_meta}'
                metadata['external_url'] = metadata.get('external_url') or None
                out_path.write_text(json.dumps(metadata, indent=2))
                logger.info('Uploaded metadata to IPFS (or placeholder): %s', cid_meta)
            except Exception as e:
                logger.debug('IPFS upload skipped or failed: %s', e)

        return metadata, assigned_token, archive_path


class MetatronCoordinator:
    """
    Node 13: Metatron Coordinator (Metatron's Cube)

    The central orchestrator that coordinates all 12 functional nodes in the TMT-OS.
    Metatron's Cube contains all five Platonic solids and represents the geometric
    blueprint of creation.
    """
    NODE_ID = 13
    NODE_NAME = "Metatron Coordinator"
    PLATONIC_SOLID = "Metatron's Cube"
    GEOMETRY = {
        'circles': 13,  # 13 circles in Metatron's Cube
        'contains': ['Cube', 'Tetrahedron', 'Octahedron', 'Icosahedron', 'Dodecahedron']
    }

    def __init__(self, registry: Path = None):
        """Initialize the Metatron Coordinator."""
        self.status = "initializing"
        self.registry = registry or Path("dna_registry")
        self.registry.mkdir(parents=True, exist_ok=True)
        self.nervous_system = MetatronNervousSystem(self.registry)
        self.initialized_at = time.time()
        self.node_instances: Dict[str, Any] = {}
        self.status = "active"
        logger.info(f"Initialized {self.NODE_NAME} (Node {self.NODE_ID}, {self.PLATONIC_SOLID})")

    def _load_node_instance(self, node_name: str) -> Optional[Any]:
        """Lazily load and cache a node instance by name."""
        if node_name in self.node_instances:
            return self.node_instances[node_name]

        node_info = NODE_REGISTRY.get(node_name)
        if not node_info:
            logger.warning(f"Node '{node_name}' not found in registry")
            return None

        try:
            node_path = node_info.get('path', '')
            # Try to import and instantiate the node dynamically
            if 'node1_base_os' in node_path:
                import importlib
                mod = importlib.import_module("TMT-OS.node1_base_os")
                self.node_instances[node_name] = mod.Node1BaseOS()
            elif 'node2_cybershield' in node_path:
                import importlib
                mod = importlib.import_module("TMT-OS.node2_cybershield")
                self.node_instances[node_name] = mod.Node2CyberShield()
            elif 'node3_experimental_labs' in node_path:
                from tmt_os_labs.node3_experimental_labs import Node3ExperimentalLabs
                self.node_instances[node_name] = Node3ExperimentalLabs()
            elif 'node4_nft_layer' in node_path:
                import importlib
                mod = importlib.import_module("TMT-OS.node4_nft_layer")
                self.node_instances[node_name] = mod.Node4NFTLayer()
            elif 'node5_spatial_intelligence' in node_path:
                from molecular_geometry.node5_spatial_intelligence import Node5SpatialIntelligence
                self.node_instances[node_name] = Node5SpatialIntelligence()
            elif 'node6_audit_trails' in node_path:
                from data_provenance.node6_audit_trails import Node6AuditTrails
                self.node_instances[node_name] = Node6AuditTrails()
            elif 'nft_inventor' in node_path:
                from nft_inventor import Node7NFTInventor
                self.node_instances[node_name] = Node7NFTInventor()
            elif 'node8_chain_monitor' in node_path:
                # Node 8 requires dependencies, return None for now
                return None
            elif 'qvae_bridge' in node_path:
                from qvae_bridge import get_bridge
                self.node_instances[node_name] = get_bridge()
            else:
                logger.debug(f"No loader defined for node: {node_name}")
                return None

            return self.node_instances.get(node_name)
        except Exception as e:
            logger.debug(f"Could not load node '{node_name}': {e}")
            return None

    def get_node_health(self, node_name: str) -> Dict[str, Any]:
        """Get health status from a specific node."""
        node = self._load_node_instance(node_name)
        if node and hasattr(node, 'get_health_status'):
            try:
                return node.get_health_status()
            except Exception as e:
                return {'node_name': node_name, 'status': 'error', 'error': str(e)}

        # Return registry info if node can't be instantiated
        node_info = NODE_REGISTRY.get(node_name, {})
        return {
            'node_name': node_name,
            'node_id': node_info.get('node_id'),
            'status': 'not_loaded',
            'platonic_solid': node_info.get('platonic_solid'),
            'role': node_info.get('role')
        }

    def get_system_health(self) -> Dict[str, Any]:
        """Get health status from all registered nodes."""
        health_report = {
            'coordinator': {
                'node_id': self.NODE_ID,
                'node_name': self.NODE_NAME,
                'status': self.status,
                'platonic_solid': self.PLATONIC_SOLID,
                'uptime_seconds': time.time() - self.initialized_at
            },
            'nodes': {},
            'summary': {
                'total_nodes': len(NODE_REGISTRY),
                'active': 0,
                'not_loaded': 0,
                'error': 0
            }
        }

        for node_name in NODE_REGISTRY:
            node_health = self.get_node_health(node_name)
            health_report['nodes'][node_name] = node_health

            status = node_health.get('status', 'unknown')
            if status == 'active':
                health_report['summary']['active'] += 1
            elif status == 'not_loaded':
                health_report['summary']['not_loaded'] += 1
            else:
                health_report['summary']['error'] += 1

        return health_report

    def send_message(self, from_node: str, to_node: str, message_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Route a message between nodes through the Metatron coordinator."""
        message = {
            'from': from_node,
            'to': to_node,
            'type': message_type,
            'payload': payload,
            'timestamp': time.time(),
            'routed_by': self.NODE_NAME
        }

        # Create DNA packet for the message
        message_str = json.dumps(message)
        dna_packet = self.nervous_system.encode_to_dna(len(message_str))
        message['dna_packet'] = dna_packet

        logger.info(f"Message routed: {from_node} -> {to_node} ({message_type})")
        return message

    def get_health_status(self) -> Dict[str, Any]:
        """Returns the health status of the coordinator itself."""
        return {
            'node_id': self.NODE_ID,
            'node_name': self.NODE_NAME,
            'status': self.status,
            'platonic_solid': self.PLATONIC_SOLID,
            'geometry': self.GEOMETRY,
            'uptime_seconds': time.time() - self.initialized_at,
            'registered_nodes': len(NODE_REGISTRY),
            'loaded_nodes': len(self.node_instances)
        }


def main():
    parser = argparse.ArgumentParser(description='Metatron Nervous System: encode results as DNA packets')
    parser.add_argument('--scan', nargs='+', help='Directories to scan', required=True)
    parser.add_argument('--registry', type=str, help='Registry directory', default=r'E:\\AGI model\\dna_registry')
    parser.add_argument('--client', type=str, default='internal')
    parser.add_argument('--stamper-key', type=str, help='HMAC key to sign packets (overrides env var)')
    parser.add_argument('--watch', action='store_true', help='Watch mode (polling)')
    parser.add_argument('--interval', type=int, default=30, help='Polling interval seconds for watch mode')
    args = parser.parse_args()

    registry = Path(args.registry)
    m = MetatronNervousSystem(registry)
    hmac_key = args.stamper_key or os.getenv('TMTOS_STAMPER_KEY')
    roots = [Path(s) for s in args.scan]

    if args.watch:
        logger.info('Entering watch mode - scanning every %s seconds', args.interval)
        try:
            while True:
                m.scan_and_archive(roots, client=args.client, hmac_key=hmac_key)
                time.sleep(args.interval)
        except KeyboardInterrupt:
            logger.info('Watch stopped by user')
    else:
        archived = m.scan_and_archive(roots, client=args.client, hmac_key=hmac_key)
        print(f'Archived {len(archived)} packets to {registry}')


if __name__ == '__main__':
    main()
