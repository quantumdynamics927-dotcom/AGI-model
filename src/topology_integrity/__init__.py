"""
Topology Integrity Graph (TIG) for QSG

Graph-based security architecture with layered topology,
anomaly detection, and fingerprinting.

Reference: research/quantum_security/topology_integrity_graph/SCHEMA.md
"""

from .tig_core import (
    ALLOWED_EDGES,
    LAYER_MAP,
    EdgeClass,
    ForbiddenEdgeError,
    NodeClass,
    TIGEdge,
    TIGNode,
    TopologyIntegrityGraph,
    create_sample_qsg_topology,
)

__all__ = [
    "TopologyIntegrityGraph",
    "TIGNode",
    "TIGEdge",
    "NodeClass",
    "EdgeClass",
    "ForbiddenEdgeError",
    "create_sample_qsg_topology",
    "ALLOWED_EDGES",
    "LAYER_MAP",
]
