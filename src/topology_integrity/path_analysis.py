"""
TIG Path Analysis - Attack Path Enumeration

Enumerates all paths from outer-layer nodes to CORE nodes,
flagging privilege escalation and disallowed edge sequences.

Reference: research/quantum_security/topology_integrity_graph/SCHEMA.md
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple

import networkx as nx

from .tig_core import LAYER_MAP, EdgeClass, NodeClass, TopologyIntegrityGraph


class PathRisk(Enum):
    """Risk level for paths."""

    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AttackPath:
    """Represents a potential attack path."""

    source: str
    target: str
    path: List[str]
    edge_classes: List[EdgeClass]
    risk: PathRisk
    issues: List[str] = field(default_factory=list)

    @property
    def length(self) -> int:
        return len(self.path) - 1

    @property
    def crosses_verifier(self) -> bool:
        return any(node for node in self.path if "verifier" in node.lower())


@dataclass
class PathAnalysisResult:
    """Result of path analysis."""

    total_paths: int
    safe_paths: int
    risky_paths: int
    critical_paths: int
    attack_paths: List[AttackPath]
    privilege_escalations: List[AttackPath]
    bypass_paths: List[AttackPath]


class PathAnalyzer:
    """
    Analyzes paths in TIG for security risks.

    Features:
    - Enumerate all paths from outer layers to CORE
    - Detect privilege escalation paths
    - Flag disallowed edge sequences
    - Identify bypass paths (missing VERIFIER)
    """

    def __init__(self, tig: TopologyIntegrityGraph):
        self.tig = tig
        self.graph = tig.graph

    def find_all_paths_to_core(self, max_depth: int = 10) -> List[List[str]]:
        """
        Find all paths from outer-layer nodes to CORE nodes.

        Args:
            max_depth: Maximum path length to search

        Returns:
            List of paths (each path is a list of node IDs)
        """
        # Find CORE nodes
        core_nodes = [
            n
            for n in self.graph.nodes()
            if self.tig.get_node_class(n) == NodeClass.CORE
        ]

        if not core_nodes:
            return []

        # Find outer-layer nodes (CLIENT, SOURCE)
        outer_nodes = [
            n
            for n in self.graph.nodes()
            if self.tig.get_node_class(n) in (NodeClass.CLIENT, NodeClass.SOURCE)
        ]

        all_paths = []

        for outer in outer_nodes:
            for core in core_nodes:
                try:
                    paths = nx.all_simple_paths(
                        self.graph, outer, core, cutoff=max_depth
                    )
                    all_paths.extend([list(p) for p in paths])
                except nx.NetworkXNoPath:
                    continue

        return all_paths

    def analyze_path(self, path: List[str]) -> AttackPath:
        """
        Analyze a single path for security risks.

        Args:
            path: List of node IDs forming the path

        Returns:
            AttackPath with risk assessment
        """
        # Get edge classes along path
        edge_classes = []
        issues = []

        for i in range(len(path) - 1):
            src, dst = path[i], path[i + 1]
            edge_data = self.graph.edges[src, dst]
            edge_class = EdgeClass(edge_data.get("class", "unknown"))
            edge_classes.append(edge_class)

        # Determine risk level
        risk = PathRisk.SAFE

        # Check for privilege escalation (layer decrease > 1)
        for i in range(len(path) - 1):
            src_layer = self.tig.get_layer(path[i])
            dst_layer = self.tig.get_layer(path[i + 1])

            if dst_layer < src_layer - 1:
                risk = PathRisk.HIGH
                issues.append(
                    f"Layer skip: {path[i]}(L{src_layer}) -> {path[i+1]}(L{dst_layer})"
                )

        # Check for missing VERIFIER
        has_verifier = any(
            self.tig.get_node_class(n) == NodeClass.VERIFIER for n in path
        )

        source_class = self.tig.get_node_class(path[0])
        target_class = self.tig.get_node_class(path[-1])

        if source_class in (NodeClass.CLIENT, NodeClass.SOURCE):
            if target_class == NodeClass.CORE and not has_verifier:
                risk = PathRisk.CRITICAL
                issues.append("Path to CORE bypasses VERIFIER layer")

        # Check for disallowed edge sequences
        for i, edge_class in enumerate(edge_classes):
            if edge_class == EdgeClass.ADMIN:
                if i > 0:  # ADMIN should only be from CORE
                    risk = max(risk, PathRisk.HIGH)
                    issues.append(f"ADMIN edge not from CORE at position {i}")

        return AttackPath(
            source=path[0],
            target=path[-1],
            path=path,
            edge_classes=edge_classes,
            risk=risk,
            issues=issues,
        )

    def find_privilege_escalations(self) -> List[AttackPath]:
        """
        Find all privilege escalation paths.

        Returns:
            List of paths that escalate privileges
        """
        all_paths = self.find_all_paths_to_core()
        escalations = []

        for path in all_paths:
            attack_path = self.analyze_path(path)
            if attack_path.risk in (PathRisk.HIGH, PathRisk.CRITICAL):
                escalations.append(attack_path)

        return escalations

    def find_bypass_paths(self) -> List[AttackPath]:
        """
        Find paths that bypass VERIFIER layer.

        Returns:
            List of paths that bypass VERIFIER
        """
        all_paths = self.find_all_paths_to_core()
        bypasses = []

        for path in all_paths:
            attack_path = self.analyze_path(path)
            if "Path to CORE bypasses VERIFIER layer" in attack_path.issues:
                bypasses.append(attack_path)

        return bypasses

    def compute_path_metrics(self) -> Dict[str, float]:
        """
        Compute path-related security metrics.

        Returns:
            Dictionary of metric name -> value
        """
        all_paths = self.find_all_paths_to_core()

        if not all_paths:
            return {
                "total_paths": 0,
                "avg_path_length": 0,
                "max_path_length": 0,
                "min_path_length": 0,
                "verifier_coverage": 1.0,
                "critical_path_ratio": 0.0,
            }

        path_lengths = [len(p) - 1 for p in all_paths]

        # Count paths through VERIFIER
        paths_with_verifier = sum(
            1
            for p in all_paths
            if any(self.tig.get_node_class(n) == NodeClass.VERIFIER for n in p)
        )

        # Analyze risks
        analyzed = [self.analyze_path(p) for p in all_paths]
        critical_count = sum(1 for a in analyzed if a.risk == PathRisk.CRITICAL)

        return {
            "total_paths": len(all_paths),
            "avg_path_length": sum(path_lengths) / len(path_lengths),
            "max_path_length": max(path_lengths),
            "min_path_length": min(path_lengths),
            "verifier_coverage": paths_with_verifier / len(all_paths),
            "critical_path_ratio": critical_count / len(all_paths),
        }

    def full_analysis(self) -> PathAnalysisResult:
        """
        Perform complete path analysis.

        Returns:
            PathAnalysisResult with all findings
        """
        all_paths = self.find_all_paths_to_core()
        analyzed = [self.analyze_path(p) for p in all_paths]

        safe_paths = sum(1 for a in analyzed if a.risk == PathRisk.SAFE)
        risky_paths = sum(
            1 for a in analyzed if a.risk in (PathRisk.LOW, PathRisk.MEDIUM)
        )
        critical_paths = sum(
            1 for a in analyzed if a.risk in (PathRisk.HIGH, PathRisk.CRITICAL)
        )

        return PathAnalysisResult(
            total_paths=len(all_paths),
            safe_paths=safe_paths,
            risky_paths=risky_paths,
            critical_paths=critical_paths,
            attack_paths=analyzed,
            privilege_escalations=self.find_privilege_escalations(),
            bypass_paths=self.find_bypass_paths(),
        )

    def generate_report(self) -> str:
        """Generate human-readable path analysis report."""
        result = self.full_analysis()

        lines = [
            "# Path Analysis Report",
            "",
            "## Summary",
            f"- Total paths to CORE: {result.total_paths}",
            f"- Safe paths: {result.safe_paths}",
            f"- Risky paths: {result.risky_paths}",
            f"- Critical paths: {result.critical_paths}",
            "",
            "## Metrics",
        ]

        metrics = self.compute_path_metrics()
        for name, value in metrics.items():
            if isinstance(value, float):
                lines.append(f"- {name}: {value:.4f}")
            else:
                lines.append(f"- {name}: {value}")

        if result.privilege_escalations:
            lines.extend(
                [
                    "",
                    "## Privilege Escalation Paths",
                ]
            )
            for ap in result.privilege_escalations:
                lines.append(f"- {ap.source} -> {ap.target}: {ap.risk.value}")
                for issue in ap.issues:
                    lines.append(f"  - {issue}")

        if result.bypass_paths:
            lines.extend(
                [
                    "",
                    "## VERIFIER Bypass Paths",
                ]
            )
            for ap in result.bypass_paths:
                lines.append(f"- {' -> '.join(ap.path)}")

        return "\n".join(lines)


if __name__ == "__main__":
    from .tig_core import create_sample_qsg_topology

    print("Path Analysis Demo")
    print("=" * 50)

    tig = create_sample_qsg_topology()
    analyzer = PathAnalyzer(tig)

    print(analyzer.generate_report())

    print("\n" + "=" * 50)
    print("Testing with unauthorized path...")

    # Add a bypass path
    tig2 = create_sample_qsg_topology()
    tig2.add_node("malicious", NodeClass.CLIENT)
    # This would normally be blocked, but let's simulate a compromised system
    # by directly modifying the graph
    tig2.graph.add_edge("malicious", "core-1", **{"class": "transport"})
    tig2._node_classes["malicious"] = NodeClass.CLIENT

    analyzer2 = PathAnalyzer(tig2)
    result2 = analyzer2.full_analysis()

    print(f"\nWith bypass path:")
    print(f"  Total paths: {result2.total_paths}")
    print(f"  Critical paths: {result2.critical_paths}")

    for ap in result2.bypass_paths:
        print(f"  Bypass: {' -> '.join(ap.path)}")
        for issue in ap.issues:
            print(f"    - {issue}")
