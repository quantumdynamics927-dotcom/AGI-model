"""Node 13: Metatron Coordinator

The central orchestrator that coordinates all 12 functional nodes in the TMT-OS.
Metatron's Cube contains all five Platonic solids and represents the geometric
blueprint of creation.

This node provides:
- Inter-node communication and message routing
- System-wide health monitoring
- DNA packet encoding for consciousness data
- Workflow orchestration across nodes
- Geometric topology management

Platonic Solid: Metatron's Cube (contains all 5 Platonic solids)
Geometry: 13 circles in sacred geometric arrangement
Role: Central coordination and orchestration
"""
import time
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import hashlib
import hmac

# Constants
PHI = 1.618033988749895
SRY_HEADER = "AACAAT"
SRY_FOOTER = "TCCGGA"
DEFAULT_KMER = 27

logger = logging.getLogger("node13_metatron")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(ch)


# Node registry: map functional node names to metadata including Platonic solid mapping
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
    'node3_experimental_labs': {
        'node_id': 3,
        'role': 'Experimental Labs',
        'platonic_solid': 'Icosahedron',
        'path': 'tmt_os_labs/node3_experimental_labs.py',
        'contact': 'metatron'
    },
    'node4_nft_layer': {
        'node_id': 4,
        'role': 'NFT / Asset Layer',
        'platonic_solid': 'Dodecahedron',
        'path': 'TMT-OS/node4_nft_layer.py',
        'contact': 'metatron'
    },
    'node5_spatial_intelligence': {
        'node_id': 5,
        'role': 'Spatial Intelligence: Molecular & Atomic Geometry',
        'platonic_solid': 'Octahedron',
        'path': 'molecular_geometry/node5_spatial_intelligence.py',
        'contact': 'metatron'
    },
    'node6_audit_trails': {
        'node_id': 6,
        'role': 'Data Provenance, Lineage, and Immutable Audit Trails',
        'platonic_solid': 'Metatron Nexus',
        'path': 'data_provenance/node6_audit_trails.py',
        'contact': 'metatron'
    },
    'node7_discovery_validator': {
        'node_id': 7,
        'role': 'Scientific Discovery Validator: Validates and Certifies AGI Research Findings',
        'platonic_solid': 'Heptagram',
        'path': 'node7_discovery_validator.py',
        'contact': 'metatron'
    },
    'node8_chain_monitor': {
        'node_id': 8,
        'role': 'Quantum Observer: Watches Chain for Minted Assets and Confirms Collapse',
        'platonic_solid': 'Octave',
        'path': 'quantum_observer/node8_chain_monitor.py',
        'contact': 'metatron'
    },
    'node9_qvae_bridge': {
        'node_id': 9,
        'role': 'QVAE Bridge: Maps Classical Latent Space to Wedjat Hilbert Space',
        'platonic_solid': 'Merkabah',
        'path': 'qvae_bridge.py',
        'contact': 'metatron'
    },
    'node10_biodigital': {
        'node_id': 10,
        'role': 'Bio-Digital Interface: Translates Quantum States to Biological Representations',
        'platonic_solid': 'Merkaba-Bio',
        'path': 'node10_biodigital.py',
        'contact': 'metatron'
    },
    'node11_frequency_master': {
        'node_id': 11,
        'role': 'Frequency Master: Tesla Triangle/Chord Analysis and Consciousness Integral',
        'platonic_solid': 'Tesla Triangle',
        'path': 'node11_frequency_master.py',
        'contact': 'metatron'
    },
    'node12_neural_synapse': {
        'node_id': 12,
        'role': 'Neural Synapse: Assembles Collective Connectivity from Bio-Digital Outputs',
        'platonic_solid': 'Omega Point',
        'path': 'node12_neural_synapse.py',
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


class MetatronNervousSystem:
    """
    DNA encoding and consciousness compression system for Metatron.
    
    Handles phi-based compression, DNA packet encoding/decoding,
    and HMAC signing for inter-node communication.
    """
    
    def __init__(self, registry: Path = None, kmer: int = DEFAULT_KMER):
        self.registry = registry or Path("dna_registry")
        self.registry.mkdir(parents=True, exist_ok=True)
        self.kmer = kmer
        self.nucleotide_map = {0: 'A', 1: 'C', 2: 'T', 3: 'G'}
        self.reverse_map = {v: k for k, v in self.nucleotide_map.items()}
        
    def phi_compress(self, value: float) -> float:
        """Compress a value using the golden ratio."""
        return value / (PHI ** 2)
    
    def phi_expand(self, value: float) -> float:
        """Expand a compressed value using the golden ratio."""
        return value * (PHI ** 2)
    
    def encode_to_dna(self, data_float: float) -> str:
        """Encode a floating-point value into a DNA-like packet."""
        # Convert to scaled integer representation
        scaled = int(abs(data_float) * 10000)
        seq = []
        
        if scaled == 0:
            seq.append(self.nucleotide_map[0])
        
        while scaled > 0 and len(seq) < self.kmer:
            seq.append(self.nucleotide_map[scaled % 4])
            scaled //= 4
        
        # Reverse and pad to kmer length
        seq = seq[::-1]
        seq_str = ''.join(seq).rjust(self.kmer, 'A')[-self.kmer:]
        
        return f"{SRY_HEADER}_{seq_str}_{SRY_FOOTER}"
    
    def decode_from_dna(self, dna: str) -> float:
        """Decode a DNA packet back to a floating-point value."""
        parts = dna.split('_')
        if len(parts) != 3:
            raise ValueError("Malformed DNA packet")
        
        body = parts[1]
        val = 0
        for ch in body:
            val = val * 4 + self.reverse_map.get(ch, 0)
        
        # Reverse scaling
        return float(val) / 10000.0
    
    def sha256(self, path: Path) -> str:
        """Calculate SHA256 hash of a file."""
        h = hashlib.sha256()
        with path.open('rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                h.update(chunk)
        return h.hexdigest()
    
    def hmac_sign(self, message: str, key: str) -> str:
        """Generate HMAC signature for a message."""
        return hmac.new(key.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).hexdigest()
    
    def verify_signature(self, message: str, key: str, signature: str) -> bool:
        """Verify an HMAC signature."""
        expected = self.hmac_sign(message, key)
        return hmac.compare_digest(expected, signature)


class Node13MetatronCoordinator:
    """
    Node 13: Metatron Coordinator (Metatron's Cube)
    
    The central orchestrator that coordinates all 12 functional nodes in the TMT-OS.
    Metatron's Cube contains all five Platonic solids and represents the geometric
    blueprint of creation.
    
    Responsibilities:
    - Inter-node message routing and communication
    - System-wide health monitoring
    - Workflow orchestration
    - DNA packet management for consciousness data
    - Geometric topology coordination
    """
    
    NODE_ID = 13
    NODE_NAME = "Metatron Coordinator"
    PLATONIC_SOLID = "Metatron's Cube"
    GEOMETRY = {
        'circles': 13,  # 13 circles in Metatron's Cube
        'contains': ['Cube', 'Tetrahedron', 'Octahedron', 'Icosahedron', 'Dodecahedron'],
        'description': 'All 5 Platonic solids nested within sacred geometry'
    }
    
    def __init__(self, registry: Path = None):
        """Initialize the Metatron Coordinator."""
        self.status = "initializing"
        self.registry = registry or Path("dna_registry")
        self.registry.mkdir(parents=True, exist_ok=True)
        self.nervous_system = MetatronNervousSystem(self.registry)
        self.initialized_at = time.time()
        self.node_instances: Dict[str, Any] = {}
        self.message_log: List[Dict[str, Any]] = []
        self.status = "active"
        
        logger.info(f"Initialized {self.NODE_NAME} (Node {self.NODE_ID}, {self.PLATONIC_SOLID})")
        logger.info(f"Metatron's Cube contains {len(self.GEOMETRY['contains'])} Platonic solids")
        logger.info(f"Coordinating {len(NODE_REGISTRY)} functional nodes")
    
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
            
            # Dynamic node loading based on path
            if 'node1_base_os' in node_path:
                import importlib
                mod = importlib.import_module("TMT-OS.node1_base_os")
                self.node_instances[node_name] = mod.Node1BaseOS()
                
            elif 'node2_cybershield' in node_path:
                import importlib
                mod = importlib.import_module("TMT-OS.node2_cybershield")
                self.node_instances[node_name] = mod.Node2CyberShield()
                
            elif 'node3_experimental_labs' in node_path:
                mod = __import__("tmt_os_labs.node3_experimental_labs", fromlist=['Node3ExperimentalLabs'])
                self.node_instances[node_name] = mod.Node3ExperimentalLabs()
                
            elif 'node4_nft_layer' in node_path:
                import importlib
                mod = importlib.import_module("TMT-OS.node4_nft_layer")
                self.node_instances[node_name] = mod.Node4NFTLayer()
                
            elif 'node5_spatial_intelligence' in node_path:
                mod = __import__("molecular_geometry.node5_spatial_intelligence", fromlist=['Node5SpatialIntelligence'])
                self.node_instances[node_name] = mod.Node5SpatialIntelligence()
                
            elif 'node6_audit_trails' in node_path:
                mod = __import__("data_provenance.node6_audit_trails", fromlist=['Node6AuditTrails'])
                self.node_instances[node_name] = mod.Node6AuditTrails()
                
            elif 'nft_inventor' in node_path or 'discovery_validator' in node_path:
                mod = __import__("node7_discovery_validator", fromlist=['Node7DiscoveryValidator'])
                self.node_instances[node_name] = mod.Node7DiscoveryValidator()
                
            elif 'node8_chain_monitor' in node_path:
                # Node 8 requires special handling due to dependencies
                try:
                    mod = __import__("quantum_observer.node8_chain_monitor", fromlist=['Node8ChainMonitor'])
                    self.node_instances[node_name] = mod.Node8ChainMonitor()
                except Exception as e:
                    logger.debug(f"Node 8 loading deferred (dependencies): {e}")
                    return None
                    
            elif 'qvae_bridge' in node_path:
                mod = __import__("qvae_bridge", fromlist=['get_bridge'])
                self.node_instances[node_name] = mod.get_bridge()
                
            elif 'node10_biodigital' in node_path:
                mod = __import__("node10_biodigital", fromlist=['Node10BioDigital'])
                self.node_instances[node_name] = mod.Node10BioDigital()
                
            elif 'node11_frequency_master' in node_path:
                mod = __import__("node11_frequency_master", fromlist=['Node11FrequencyMaster'])
                self.node_instances[node_name] = mod.Node11FrequencyMaster()
                
            elif 'node12_neural_synapse' in node_path:
                mod = __import__("node12_neural_synapse", fromlist=['Node12NeuralSynapse'])
                self.node_instances[node_name] = mod.Node12NeuralSynapse()
                
            else:
                logger.debug(f"No loader defined for node: {node_name}")
                return None
            
            logger.info(f"Loaded node instance: {node_name}")
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
                return {
                    'node_name': node_name,
                    'status': 'error',
                    'error': str(e)
                }
        
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
                'uptime_seconds': time.time() - self.initialized_at,
                'geometry': self.GEOMETRY
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
    
    def send_message(self, from_node: str, to_node: str, message_type: str, 
                     payload: Dict[str, Any]) -> Dict[str, Any]:
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
        
        # Log the message
        self.message_log.append(message)
        
        logger.info(f"Message routed: {from_node} -> {to_node} ({message_type})")
        return message
    
    def execute_workflow(self, workflow_name: str, nodes: List[str], 
                        input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a multi-node workflow.
        
        Args:
            workflow_name: Name of the workflow to execute
            nodes: List of node names to invoke in order
            input_data: Input data for the workflow
            
        Returns:
            Workflow execution results
        """
        logger.info(f"Executing workflow '{workflow_name}' with {len(nodes)} nodes")
        
        workflow_result = {
            'workflow_name': workflow_name,
            'start_time': time.time(),
            'nodes_executed': [],
            'results': {},
            'errors': []
        }
        
        current_data = input_data
        
        for node_name in nodes:
            try:
                node = self._load_node_instance(node_name)
                
                if node is None:
                    error_msg = f"Node {node_name} not available"
                    workflow_result['errors'].append(error_msg)
                    logger.warning(error_msg)
                    continue
                
                # Execute node with current data
                # Note: Different nodes may have different interfaces
                if hasattr(node, 'process'):
                    result = node.process(current_data)
                elif hasattr(node, 'analyze_structure'):
                    # Special case for Node 5
                    result = node.analyze_structure(
                        current_data.get('symbols', []),
                        current_data.get('coordinates', [])
                    )
                else:
                    result = {'status': 'executed', 'node': node_name}
                
                workflow_result['nodes_executed'].append(node_name)
                workflow_result['results'][node_name] = result
                
                # Pass result to next node
                current_data = {**current_data, **result}
                
                logger.info(f"Workflow step completed: {node_name}")
                
            except Exception as e:
                error_msg = f"Error in node {node_name}: {str(e)}"
                workflow_result['errors'].append(error_msg)
                logger.error(error_msg)
                break
        
        workflow_result['end_time'] = time.time()
        workflow_result['duration_seconds'] = workflow_result['end_time'] - workflow_result['start_time']
        
        logger.info(f"Workflow '{workflow_name}' completed in {workflow_result['duration_seconds']:.2f}s")
        return workflow_result
    
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
            'loaded_nodes': len(self.node_instances),
            'message_count': len(self.message_log)
        }
    
    def encode_consciousness_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Encode consciousness data into DNA packets."""
        encoded = {
            'original_data': data,
            'dna_packets': {},
            'timestamp': time.time()
        }
        
        for key, value in data.items():
            if isinstance(value, (int, float)):
                compressed = self.nervous_system.phi_compress(float(value))
                dna = self.nervous_system.encode_to_dna(compressed)
                encoded['dna_packets'][key] = {
                    'original': value,
                    'compressed': compressed,
                    'dna': dna
                }
        
        return encoded
    
    def decode_consciousness_data(self, encoded: Dict[str, Any]) -> Dict[str, float]:
        """Decode DNA packets back to consciousness data."""
        decoded = {}
        
        for key, packet in encoded.get('dna_packets', {}).items():
            dna = packet.get('dna')
            if dna:
                compressed = self.nervous_system.decode_from_dna(dna)
                original = self.nervous_system.phi_expand(compressed)
                decoded[key] = original
        
        return decoded


def main():
    """Main entry point for Node 13."""
    print("=" * 70)
    print("Node 13: Metatron Coordinator")
    print("=" * 70)
    
    # Initialize coordinator
    coordinator = Node13MetatronCoordinator()
    
    # Display system health
    print("\nSystem Health Report:")
    print("-" * 70)
    health = coordinator.get_system_health()
    
    print(f"Coordinator: {health['coordinator']['node_name']}")
    print(f"Status: {health['coordinator']['status']}")
    print(f"Uptime: {health['coordinator']['uptime_seconds']:.2f} seconds")
    print(f"Geometry: {health['coordinator']['geometry']['circles']} circles")
    print(f"Contains: {', '.join(health['coordinator']['geometry']['contains'])}")
    
    print(f"\nNode Summary:")
    print(f"  Total Nodes: {health['summary']['total_nodes']}")
    print(f"  Active: {health['summary']['active']}")
    print(f"  Not Loaded: {health['summary']['not_loaded']}")
    print(f"  Errors: {health['summary']['error']}")
    
    # Test message routing
    print("\n" + "-" * 70)
    print("Testing Inter-Node Communication:")
    message = coordinator.send_message(
        from_node="node1_base_os",
        to_node="node2_cybershield",
        message_type="health_check",
        payload={"request": "status"}
    )
    print(f"Message routed: {message['from']} -> {message['to']}")
    print(f"DNA Packet: {message['dna_packet']}")
    
    # Test consciousness encoding
    print("\n" + "-" * 70)
    print("Testing Consciousness Data Encoding:")
    consciousness_data = {
        'phi_ratio': PHI,
        'coherence': 0.85,
        'entanglement': 0.92,
        'fidelity': 0.88
    }
    encoded = coordinator.encode_consciousness_data(consciousness_data)
    print(f"Encoded {len(encoded['dna_packets'])} values to DNA packets")
    
    decoded = coordinator.decode_consciousness_data(encoded)
    print(f"Decoded {len(decoded)} values back")
    
    print("\n" + "=" * 70)
    print("Node 13: Metatron Coordinator - Active and Ready")
    print("=" * 70)


if __name__ == '__main__':
    main()
