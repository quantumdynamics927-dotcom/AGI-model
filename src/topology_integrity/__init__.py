"""
Topology Integrity Graph (TIG) for QSG

Graph-based security architecture with layered topology,
anomaly detection, and fingerprinting.

Reference: research/quantum_security/topology_integrity_graph/SCHEMA.md
"""

from .diffing import ChangeType, SnapshotDiffer, TopologyChange, TopologyDiff
from .metrics import MetricsCalculator, TopologyMetrics
from .path_analysis import AttackPath, PathAnalysisResult, PathAnalyzer, PathRisk
from .qsg_mapping import QSG_MAPPINGS, ComponentMapping, QSGComponent, QSGMapper
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
    # Core
    "TopologyIntegrityGraph",
    "TIGNode",
    "TIGEdge",
    "NodeClass",
    "EdgeClass",
    "ForbiddenEdgeError",
    "create_sample_qsg_topology",
    "ALLOWED_EDGES",
    "LAYER_MAP",
    # Path Analysis
    "PathRisk",
    "AttackPath",
    "PathAnalysisResult",
    "PathAnalyzer",
    # Diffing
    "ChangeType",
    "TopologyChange",
    "TopologyDiff",
    "SnapshotDiffer",
    # Metrics
    "TopologyMetrics",
    "MetricsCalculator",
    # QSG Mapping
    "QSGComponent",
    "ComponentMapping",
    "QSG_MAPPINGS",
    "QSGMapper",
]
