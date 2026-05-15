"""
Topology Integrity Graph (TIG) Implementation

Graph-based security architecture for QSG with layered topology,
anomaly detection, and fingerprinting.

Reference: research/quantum_security/topology_integrity_graph/SCHEMA.md
"""

import hashlib
import json
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set, Tuple

import networkx as nx


class NodeClass(Enum):
    """Node classes in TIG."""

    CORE = "core"
    VERIFIER = "verifier"
    AUDITOR = "auditor"
    CRYPTO = "crypto"
    RELAY = "relay"
    CLIENT = "client"
    SOURCE = "source"


class EdgeClass(Enum):
    """Edge classes in TIG."""

    TRUST = "trust"
    VERIFY = "verify"
    DERIVE = "derive"
    TRANSPORT = "transport"
    ADMIN = "admin"
    READ = "read"
    SIGN = "sign"


# Layer structure: class -> layer number
LAYER_MAP = {
    NodeClass.CORE: 0,
    NodeClass.VERIFIER: 1,
    NodeClass.AUDITOR: 1,
    NodeClass.CRYPTO: 2,
    NodeClass.RELAY: 2,
    NodeClass.CLIENT: 3,
    NodeClass.SOURCE: 3,
}

# Allowed edges: source class -> set of (destination class, edge class)
ALLOWED_EDGES = {
    NodeClass.CORE: {
        (NodeClass.VERIFIER, EdgeClass.TRUST),
        (NodeClass.AUDITOR, EdgeClass.TRUST),
        (NodeClass.VERIFIER, EdgeClass.ADMIN),
        (NodeClass.AUDITOR, EdgeClass.ADMIN),
    },
    NodeClass.VERIFIER: {
        (NodeClass.CORE, EdgeClass.TRUST),
        (NodeClass.CRYPTO, EdgeClass.VERIFY),
        (NodeClass.RELAY, EdgeClass.VERIFY),
        (NodeClass.AUDITOR, EdgeClass.TRUST),
    },
    NodeClass.AUDITOR: {
        (NodeClass.CORE, EdgeClass.TRUST),
        (NodeClass.VERIFIER, EdgeClass.TRUST),
    },
    NodeClass.CRYPTO: {
        (NodeClass.VERIFIER, EdgeClass.VERIFY),
        (NodeClass.RELAY, EdgeClass.TRANSPORT),
        (NodeClass.AUDITOR, EdgeClass.SIGN),
    },
    NodeClass.RELAY: {
        (NodeClass.VERIFIER, EdgeClass.VERIFY),
        (NodeClass.CRYPTO, EdgeClass.TRANSPORT),
        (NodeClass.CLIENT, EdgeClass.TRANSPORT),
    },
    NodeClass.CLIENT: {
        (NodeClass.RELAY, EdgeClass.TRANSPORT),
    },
    NodeClass.SOURCE: {
        (NodeClass.CRYPTO, EdgeClass.DERIVE),
    },
}


@dataclass
class TIGNode:
    """Topology Integrity Graph node."""

    node_id: str
    node_class: NodeClass
    attributes: Dict[str, Any] = field(default_factory=dict)

    @property
    def layer(self) -> int:
        return LAYER_MAP[self.node_class]


@dataclass
class TIGEdge:
    """Topology Integrity Graph edge."""

    source_id: str
    target_id: str
    edge_class: EdgeClass
    attributes: Dict[str, Any] = field(default_factory=dict)


class ForbiddenEdgeError(Exception):
    """Raised when attempting to add a forbidden edge."""

    pass


class TopologyIntegrityGraph:
    """
    Topology Integrity Graph for QSG security architecture.

    Implements layered graph with structural constraints,
    anomaly detection, and fingerprinting.
    """

    def __init__(self, name: str = "TIG"):
        self.name = name
        self.graph = nx.DiGraph()
        self.baseline_hash: Optional[str] = None
        self._node_classes: Dict[str, NodeClass] = {}

    def add_node(self, node_id: str, node_class: NodeClass, **attributes) -> TIGNode:
        """
        Add a node to the graph.

        Args:
            node_id: Unique node identifier
            node_class: Node class (CORE, VERIFIER, etc.)
            **attributes: Additional node attributes

        Returns:
            TIGNode object
        """
        node = TIGNode(node_id=node_id, node_class=node_class, attributes=attributes)

        self.graph.add_node(
            node_id, **{"class": node_class.value, "layer": node.layer, **attributes}
        )
        self._node_classes[node_id] = node_class

        return node

    def add_edge(
        self, source_id: str, target_id: str, edge_class: EdgeClass, **attributes
    ) -> TIGEdge:
        """
        Add an edge to the graph with constraint validation.

        Args:
            source_id: Source node ID
            target_id: Target node ID
            edge_class: Edge class (TRUST, VERIFY, etc.)
            **attributes: Additional edge attributes

        Returns:
            TIGEdge object

        Raises:
            ForbiddenEdgeError: If edge violates schema constraints
        """
        # Validate nodes exist
        if source_id not in self.graph:
            raise ValueError(f"Source node {source_id} does not exist")
        if target_id not in self.graph:
            raise ValueError(f"Target node {target_id} does not exist")

        # Get node classes
        source_class = self._node_classes[source_id]
        target_class = self._node_classes[target_id]

        # Validate edge is allowed
        allowed = ALLOWED_EDGES.get(source_class, set())
        if (target_class, edge_class) not in allowed:
            raise ForbiddenEdgeError(
                f"Edge {source_id}({source_class.value}) -> "
                f"{target_id}({target_class.value}) with class {edge_class.value} "
                f"violates schema"
            )

        edge = TIGEdge(
            source_id=source_id,
            target_id=target_id,
            edge_class=edge_class,
            attributes=attributes,
        )

        self.graph.add_edge(
            source_id, target_id, **{"class": edge_class.value, **attributes}
        )

        return edge

    def get_node_class(self, node_id: str) -> Optional[NodeClass]:
        """Get the class of a node."""
        return self._node_classes.get(node_id)

    def get_layer(self, node_id: str) -> int:
        """Get the layer of a node."""
        node_class = self.get_node_class(node_id)
        if node_class is None:
            raise ValueError(f"Node {node_id} does not exist")
        return LAYER_MAP[node_class]

    def compute_fingerprint(self) -> str:
        """
        Compute topology fingerprint (SHA-256 hash of canonical representation).

        Returns:
            32-character hex string fingerprint
        """
        # Build canonical representation
        nodes = []
        for node_id in sorted(self.graph.nodes()):
            node_class = self._node_classes[node_id]
            nodes.append(f"{node_class.value}:{node_id}")

        edges = []
        for src, dst in sorted(self.graph.edges()):
            edge_data = self.graph.edges[src, dst]
            edge_class = edge_data.get("class", "unknown")
            edges.append(f"{edge_class}:{src}:{dst}")

        canonical = "|".join([",".join(nodes), ",".join(edges)])

        # Compute hash
        return hashlib.sha256(canonical.encode()).hexdigest()[:32]

    def set_baseline(self) -> None:
        """Set current topology as baseline."""
        self.baseline_hash = self.compute_fingerprint()

    def has_drifted(self) -> bool:
        """Check if topology has drifted from baseline."""
        if self.baseline_hash is None:
            raise ValueError("Baseline not set")
        return self.compute_fingerprint() != self.baseline_hash

    def count_forbidden_edges(self) -> int:
        """
        Count edges that violate schema constraints.

        Returns:
            Number of forbidden edges
        """
        forbidden = 0
        for src, dst in self.graph.edges():
            src_class = self._node_classes.get(src)
            dst_class = self._node_classes.get(dst)
            edge_data = self.graph.edges[src, dst]
            edge_class_val = edge_data.get("class")

            if src_class is None or dst_class is None:
                forbidden += 1
                continue

            # Map edge class string back to enum
            try:
                edge_class = EdgeClass(edge_class_val)
            except ValueError:
                forbidden += 1
                continue

            allowed = ALLOWED_EDGES.get(src_class, set())
            if (dst_class, edge_class) not in allowed:
                forbidden += 1

        return forbidden

    def compute_degree_drift(self, other: "TopologyIntegrityGraph") -> Dict[str, float]:
        """
        Compute degree drift between this graph and another.

        Args:
            other: Another TIG to compare against

        Returns:
            Dictionary of node_id -> degree drift ratio
        """
        drift = {}
        all_nodes = set(self.graph.nodes()) | set(other.graph.nodes())

        for node_id in all_nodes:
            deg1 = self.graph.degree(node_id) if node_id in self.graph else 0
            deg2 = other.graph.degree(node_id) if node_id in other.graph else 0

            if deg1 == 0 and deg2 == 0:
                drift[node_id] = 0.0
            elif deg1 == 0:
                drift[node_id] = float("inf")
            else:
                drift[node_id] = abs(deg2 - deg1) / deg1

        return drift

    def path_to_core(self, node_id: str) -> Optional[int]:
        """
        Compute shortest path length to CORE node.

        Args:
            node_id: Starting node

        Returns:
            Path length, or None if no path exists
        """
        # Find CORE node
        core_nodes = [
            n for n in self.graph.nodes() if self._node_classes.get(n) == NodeClass.CORE
        ]

        if not core_nodes:
            return None

        core = core_nodes[0]

        try:
            path = nx.shortest_path(self.graph, node_id, core)
            return len(path) - 1  # Number of edges
        except nx.NetworkXNoPath:
            return None

    def detect_privilege_escalation(self) -> List[Tuple[str, str]]:
        """
        Detect potential privilege escalation paths.

        Returns:
            List of (client_node, core_node) paths that bypass VERIFIER
        """
        escalations = []

        # Find all CLIENT nodes
        clients = [
            n
            for n in self.graph.nodes()
            if self._node_classes.get(n) == NodeClass.CLIENT
        ]

        # Find CORE node
        cores = [
            n for n in self.graph.nodes() if self._node_classes.get(n) == NodeClass.CORE
        ]

        if not cores:
            return escalations

        core = cores[0]

        for client in clients:
            try:
                path = nx.shortest_path(self.graph, client, core)
                # Check if path bypasses VERIFIER
                has_verifier = any(
                    self._node_classes.get(n) == NodeClass.VERIFIER for n in path
                )
                if not has_verifier:
                    escalations.append((client, core))
            except nx.NetworkXNoPath:
                continue

        return escalations

    def to_dict(self) -> dict:
        """Serialize graph to dictionary."""
        return {
            "name": self.name,
            "nodes": [
                {
                    "id": n,
                    "class": self._node_classes[n].value,
                    "layer": self.get_layer(n),
                    **self.graph.nodes[n],
                }
                for n in self.graph.nodes()
            ],
            "edges": [
                {"source": src, "target": dst, **self.graph.edges[src, dst]}
                for src, dst in self.graph.edges()
            ],
            "fingerprint": self.compute_fingerprint(),
            "baseline_hash": self.baseline_hash,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TopologyIntegrityGraph":
        """Deserialize graph from dictionary."""
        tig = cls(name=data.get("name", "TIG"))

        for node_data in data.get("nodes", []):
            node_id = node_data.pop("id")
            node_class = NodeClass(node_data.pop("class"))
            node_data.pop("layer", None)  # Computed property
            tig.add_node(node_id, node_class, **node_data)

        for edge_data in data.get("edges", []):
            src = edge_data.pop("source")
            dst = edge_data.pop("target")
            edge_class = EdgeClass(edge_data.pop("class"))
            tig.add_edge(src, dst, edge_class, **edge_data)

        if data.get("baseline_hash"):
            tig.baseline_hash = data["baseline_hash"]

        return tig


def create_sample_qsg_topology() -> TopologyIntegrityGraph:
    """
    Create a sample QSG topology for demonstration.

    Returns:
        TopologyIntegrityGraph with sample nodes and edges
    """
    tig = TopologyIntegrityGraph(name="QSG-Sample")

    # Layer 0: Core
    tig.add_node("core-1", NodeClass.CORE, role="policy_decision")

    # Layer 1: Verifiers and Auditors
    tig.add_node("verifier-1", NodeClass.VERIFIER, role="entropy_validation")
    tig.add_node("verifier-2", NodeClass.VERIFIER, role="signature_check")
    tig.add_node("auditor-1", NodeClass.AUDITOR, role="compliance")

    # Layer 2: Crypto and Relays
    tig.add_node("crypto-1", NodeClass.CRYPTO, role="pqc_key_exchange")
    tig.add_node("crypto-2", NodeClass.CRYPTO, role="payload_sealing")
    tig.add_node("relay-1", NodeClass.RELAY, role="secure_gateway")
    tig.add_node("relay-2", NodeClass.RELAY, role="session_orchestration")

    # Layer 3: Clients and Sources
    tig.add_node("client-1", NodeClass.CLIENT, role="external_device")
    tig.add_node("client-2", NodeClass.CLIENT, role="external_gateway")
    tig.add_node("source-1", NodeClass.SOURCE, role="qrng_entropy")

    # Add edges (following schema constraints)
    tig.add_edge("core-1", "verifier-1", EdgeClass.TRUST)
    tig.add_edge("core-1", "verifier-2", EdgeClass.TRUST)
    tig.add_edge("core-1", "auditor-1", EdgeClass.TRUST)

    tig.add_edge("verifier-1", "crypto-1", EdgeClass.VERIFY)
    tig.add_edge("verifier-1", "relay-1", EdgeClass.VERIFY)
    tig.add_edge("verifier-2", "crypto-2", EdgeClass.VERIFY)
    tig.add_edge("verifier-2", "relay-2", EdgeClass.VERIFY)

    tig.add_edge("crypto-1", "relay-1", EdgeClass.TRANSPORT)
    tig.add_edge("crypto-2", "relay-2", EdgeClass.TRANSPORT)

    tig.add_edge("relay-1", "client-1", EdgeClass.TRANSPORT)
    tig.add_edge("relay-2", "client-2", EdgeClass.TRANSPORT)

    tig.add_edge("source-1", "crypto-1", EdgeClass.DERIVE)

    tig.add_edge("crypto-1", "auditor-1", EdgeClass.SIGN)
    tig.add_edge("crypto-2", "auditor-1", EdgeClass.SIGN)

    return tig


if __name__ == "__main__":
    # Demo
    print("Topology Integrity Graph Demo")
    print("=" * 50)

    tig = create_sample_qsg_topology()

    print(f"\nGraph: {tig.name}")
    print(f"Nodes: {tig.graph.number_of_nodes()}")
    print(f"Edges: {tig.graph.number_of_edges()}")

    print(f"\nFingerprint: {tig.compute_fingerprint()}")

    tig.set_baseline()
    print(f"Baseline set: {tig.baseline_hash}")

    print(f"\nForbidden edges: {tig.count_forbidden_edges()}")

    print("\nPaths to CORE:")
    for node in tig.graph.nodes():
        path_len = tig.path_to_core(node)
        if path_len is not None:
            print(f"  {node}: {path_len} hops")

    print("\nPrivilege escalations (bypass VERIFIER):")
    escalations = tig.detect_privilege_escalation()
    if escalations:
        for client, core in escalations:
            print(f"  {client} -> {core}")
    else:
        print("  None detected")

    # Test drift detection
    print("\nAdding unauthorized node...")
    tig.add_node("attacker", NodeClass.CLIENT)
    tig.add_edge("attacker", "core-1", EdgeClass.TRANSPORT)  # Bypass!

    print(f"Has drifted: {tig.has_drifted()}")
    print(f"Forbidden edges: {tig.count_forbidden_edges()}")

    escalations = tig.detect_privilege_escalation()
    print(f"Privilege escalations: {len(escalations)}")
    for client, core in escalations:
        print(f"  {client} -> {core}")
