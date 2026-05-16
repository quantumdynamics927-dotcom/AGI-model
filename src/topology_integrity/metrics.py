"""
TIG Metrics - Graph Security Metrics

Computes security-relevant metrics for topology integrity.

Reference: research/quantum_security/topology_integrity_graph/SCHEMA.md
"""

import math
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

import networkx as nx

from .tig_core import LAYER_MAP, EdgeClass, NodeClass, TopologyIntegrityGraph


@dataclass
class TopologyMetrics:
    """Computed metrics for a topology."""

    # Node metrics
    total_nodes: int
    nodes_by_class: Dict[str, int]
    nodes_by_layer: Dict[int, int]

    # Edge metrics
    total_edges: int
    edges_by_class: Dict[str, int]
    forbidden_edges: int

    # Path metrics
    avg_path_to_core: float
    max_path_to_core: int
    min_path_to_core: int
    verifier_coverage: float

    # Security metrics
    privilege_escalation_risk: float
    crown_jewel_proximity: float
    entropy_source_isolation: float
    verification_coverage: float

    # Graph metrics
    density: float
    avg_degree: float
    max_degree: int
    clustering_coefficient: float

    # Fingerprint
    fingerprint: str


class MetricsCalculator:
    """
    Computes security-relevant metrics for TIG.

    Features:
    - Node/edge statistics
    - Path analysis metrics
    - Security risk scores
    - Graph structure metrics
    """

    def __init__(self, tig: TopologyIntegrityGraph):
        self.tig = tig
        self.graph = tig.graph

    def compute_all_metrics(self) -> TopologyMetrics:
        """Compute all metrics for the topology."""

        # Node metrics
        total_nodes = self.graph.number_of_nodes()
        nodes_by_class = defaultdict(int)
        nodes_by_layer = defaultdict(int)

        for node in self.graph.nodes():
            node_class = self.tig.get_node_class(node)
            if node_class:
                nodes_by_class[node_class.value] += 1
                nodes_by_layer[LAYER_MAP[node_class]] += 1

        # Edge metrics
        total_edges = self.graph.number_of_edges()
        edges_by_class = defaultdict(int)

        for src, dst in self.graph.edges():
            edge_data = self.graph.edges[src, dst]
            edge_class = edge_data.get("class", "unknown")
            edges_by_class[edge_class] += 1

        forbidden_edges = self.tig.count_forbidden_edges()

        # Path metrics
        path_metrics = self._compute_path_metrics()

        # Security metrics
        security_metrics = self._compute_security_metrics()

        # Graph metrics
        graph_metrics = self._compute_graph_metrics()

        return TopologyMetrics(
            total_nodes=total_nodes,
            nodes_by_class=dict(nodes_by_class),
            nodes_by_layer=dict(nodes_by_layer),
            total_edges=total_edges,
            edges_by_class=dict(edges_by_class),
            forbidden_edges=forbidden_edges,
            avg_path_to_core=path_metrics["avg_path"],
            max_path_to_core=path_metrics["max_path"],
            min_path_to_core=path_metrics["min_path"],
            verifier_coverage=path_metrics["verifier_coverage"],
            privilege_escalation_risk=security_metrics["privilege_escalation_risk"],
            crown_jewel_proximity=security_metrics["crown_jewel_proximity"],
            entropy_source_isolation=security_metrics["entropy_source_isolation"],
            verification_coverage=security_metrics["verification_coverage"],
            density=graph_metrics["density"],
            avg_degree=graph_metrics["avg_degree"],
            max_degree=graph_metrics["max_degree"],
            clustering_coefficient=graph_metrics["clustering_coefficient"],
            fingerprint=self.tig.compute_fingerprint(),
        )

    def _compute_path_metrics(self) -> Dict[str, float]:
        """Compute path-related metrics."""
        # Find CORE nodes
        core_nodes = [
            n
            for n in self.graph.nodes()
            if self.tig.get_node_class(n) == NodeClass.CORE
        ]

        if not core_nodes:
            return {
                "avg_path": float("inf"),
                "max_path": 0,
                "min_path": 0,
                "verifier_coverage": 1.0,
            }

        # Find outer nodes
        outer_nodes = [
            n
            for n in self.graph.nodes()
            if self.tig.get_node_class(n) in (NodeClass.CLIENT, NodeClass.SOURCE)
        ]

        if not outer_nodes:
            return {
                "avg_path": 0,
                "max_path": 0,
                "min_path": 0,
                "verifier_coverage": 1.0,
            }

        # Compute paths
        path_lengths = []
        paths_with_verifier = 0

        for outer in outer_nodes:
            for core in core_nodes:
                try:
                    path = nx.shortest_path(self.graph, outer, core)
                    path_lengths.append(len(path) - 1)

                    # Check if path goes through VERIFIER
                    has_verifier = any(
                        self.tig.get_node_class(n) == NodeClass.VERIFIER for n in path
                    )
                    if has_verifier:
                        paths_with_verifier += 1
                except nx.NetworkXNoPath:
                    continue

        if not path_lengths:
            return {
                "avg_path": float("inf"),
                "max_path": 0,
                "min_path": 0,
                "verifier_coverage": 1.0,
            }

        return {
            "avg_path": sum(path_lengths) / len(path_lengths),
            "max_path": max(path_lengths),
            "min_path": min(path_lengths),
            "verifier_coverage": paths_with_verifier / len(path_lengths),
        }

    def _compute_security_metrics(self) -> Dict[str, float]:
        """Compute security-related metrics."""
        # Privilege escalation risk
        escalations = self.tig.detect_privilege_escalation()
        privilege_escalation_risk = len(escalations) / max(
            self.graph.number_of_nodes(), 1
        )

        # Crown jewel proximity
        core_nodes = [
            n
            for n in self.graph.nodes()
            if self.tig.get_node_class(n) == NodeClass.CORE
        ]

        if not core_nodes:
            crown_jewel_proximity = 0.0
        else:
            # Average shortest path from outer nodes to core
            outer_nodes = [
                n
                for n in self.graph.nodes()
                if self.tig.get_node_class(n) in (NodeClass.CLIENT, NodeClass.SOURCE)
            ]

            if not outer_nodes:
                crown_jewel_proximity = 0.0
            else:
                distances = []
                for outer in outer_nodes:
                    for core in core_nodes:
                        try:
                            dist = nx.shortest_path_length(self.graph, outer, core)
                            distances.append(dist)
                        except nx.NetworkXNoPath:
                            distances.append(float("inf"))

                # Invert: closer = higher risk
                avg_dist = sum(d for d in distances if d != float("inf")) / max(
                    len(distances), 1
                )
                crown_jewel_proximity = 1.0 / max(avg_dist, 1)

        # Entropy source isolation
        source_nodes = [
            n
            for n in self.graph.nodes()
            if self.tig.get_node_class(n) == NodeClass.SOURCE
        ]

        if not source_nodes:
            entropy_source_isolation = 1.0
        else:
            # Check if sources only connect to CRYPTO
            isolated = 0
            for source in source_nodes:
                neighbors = list(self.graph.successors(source))
                if all(
                    self.tig.get_node_class(n) == NodeClass.CRYPTO for n in neighbors
                ):
                    isolated += 1
            entropy_source_isolation = isolated / len(source_nodes)

        # Verification coverage
        verifier_nodes = [
            n
            for n in self.graph.nodes()
            if self.tig.get_node_class(n) == NodeClass.VERIFIER
        ]

        if not verifier_nodes:
            verification_coverage = 0.0
        else:
            # Fraction of paths through verifiers
            path_metrics = self._compute_path_metrics()
            verification_coverage = path_metrics["verifier_coverage"]

        return {
            "privilege_escalation_risk": privilege_escalation_risk,
            "crown_jewel_proximity": crown_jewel_proximity,
            "entropy_source_isolation": entropy_source_isolation,
            "verification_coverage": verification_coverage,
        }

    def _compute_graph_metrics(self) -> Dict[str, float]:
        """Compute standard graph metrics."""
        n = self.graph.number_of_nodes()
        m = self.graph.number_of_edges()

        # Density
        if n <= 1:
            density = 0.0
        else:
            density = m / (n * (n - 1))  # Directed graph

        # Degree
        degrees = [d for n, d in self.graph.degree()]
        avg_degree = sum(degrees) / len(degrees) if degrees else 0
        max_degree = max(degrees) if degrees else 0

        # Clustering coefficient (for undirected view)
        try:
            clustering = nx.average_clustering(self.graph.to_undirected())
        except:
            clustering = 0.0

        return {
            "density": density,
            "avg_degree": avg_degree,
            "max_degree": max_degree,
            "clustering_coefficient": clustering,
        }

    def generate_report(self, metrics: TopologyMetrics) -> str:
        """Generate human-readable metrics report."""
        lines = [
            "# Topology Metrics Report",
            "",
            "## Node Statistics",
            f"- Total nodes: {metrics.total_nodes}",
            f"- By class: {metrics.nodes_by_class}",
            f"- By layer: {metrics.nodes_by_layer}",
            "",
            "## Edge Statistics",
            f"- Total edges: {metrics.total_edges}",
            f"- By class: {metrics.edges_by_class}",
            f"- Forbidden edges: {metrics.forbidden_edges}",
            "",
            "## Path Metrics",
            f"- Average path to core: {metrics.avg_path_to_core:.2f}",
            f"- Max path to core: {metrics.max_path_to_core}",
            f"- Min path to core: {metrics.min_path_to_core}",
            f"- Verifier coverage: {metrics.verifier_coverage:.2%}",
            "",
            "## Security Metrics",
            f"- Privilege escalation risk: {metrics.privilege_escalation_risk:.4f}",
            f"- Crown jewel proximity: {metrics.crown_jewel_proximity:.4f}",
            f"- Entropy source isolation: {metrics.entropy_source_isolation:.2%}",
            f"- Verification coverage: {metrics.verification_coverage:.2%}",
            "",
            "## Graph Metrics",
            f"- Density: {metrics.density:.4f}",
            f"- Average degree: {metrics.avg_degree:.2f}",
            f"- Max degree: {metrics.max_degree}",
            f"- Clustering coefficient: {metrics.clustering_coefficient:.4f}",
            "",
            "## Fingerprint",
            f"`{metrics.fingerprint}`",
        ]

        return "\n".join(lines)

    def compare_metrics(
        self, baseline: TopologyMetrics, current: TopologyMetrics
    ) -> Dict[str, float]:
        """
        Compare metrics between baseline and current.

        Returns:
            Dictionary of metric name -> delta
        """
        return {
            "total_nodes_delta": current.total_nodes - baseline.total_nodes,
            "total_edges_delta": current.total_edges - baseline.total_edges,
            "forbidden_edges_delta": current.forbidden_edges - baseline.forbidden_edges,
            "avg_path_delta": current.avg_path_to_core - baseline.avg_path_to_core,
            "verifier_coverage_delta": current.verifier_coverage
            - baseline.verifier_coverage,
            "privilege_escalation_risk_delta": current.privilege_escalation_risk
            - baseline.privilege_escalation_risk,
            "crown_jewel_proximity_delta": current.crown_jewel_proximity
            - baseline.crown_jewel_proximity,
            "entropy_source_isolation_delta": current.entropy_source_isolation
            - baseline.entropy_source_isolation,
            "verification_coverage_delta": current.verification_coverage
            - baseline.verification_coverage,
            "density_delta": current.density - baseline.density,
            "avg_degree_delta": current.avg_degree - baseline.avg_degree,
        }


if __name__ == "__main__":
    from .tig_core import create_sample_qsg_topology

    print("Metrics Demo")
    print("=" * 50)

    tig = create_sample_qsg_topology()
    calculator = MetricsCalculator(tig)
    metrics = calculator.compute_all_metrics()

    print(calculator.generate_report(metrics))
