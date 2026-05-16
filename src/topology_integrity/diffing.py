"""
TIG Snapshot Diffing - Topology Change Detection

Produces precise structural diffs when drift occurs,
listing added/removed nodes and edges with rule violations.

Reference: research/quantum_security/topology_integrity_graph/SCHEMA.md
"""

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple

from .tig_core import EdgeClass, ForbiddenEdgeError, NodeClass, TopologyIntegrityGraph


class ChangeType(Enum):
    """Type of topology change."""

    NODE_ADDED = "node_added"
    NODE_REMOVED = "node_removed"
    NODE_MODIFIED = "node_modified"
    EDGE_ADDED = "edge_added"
    EDGE_REMOVED = "edge_removed"
    EDGE_MODIFIED = "edge_modified"


@dataclass
class TopologyChange:
    """Represents a single topology change."""

    change_type: ChangeType
    element_id: str
    details: Dict
    rule_violation: Optional[str] = None
    severity: str = "info"  # info, warning, error, critical


@dataclass
class TopologyDiff:
    """Complete diff between two topology snapshots."""

    baseline_fingerprint: str
    current_fingerprint: str
    has_drifted: bool
    changes: List[TopologyChange] = field(default_factory=list)

    @property
    def added_nodes(self) -> List[TopologyChange]:
        return [c for c in self.changes if c.change_type == ChangeType.NODE_ADDED]

    @property
    def removed_nodes(self) -> List[TopologyChange]:
        return [c for c in self.changes if c.change_type == ChangeType.NODE_REMOVED]

    @property
    def added_edges(self) -> List[TopologyChange]:
        return [c for c in self.changes if c.change_type == ChangeType.EDGE_ADDED]

    @property
    def removed_edges(self) -> List[TopologyChange]:
        return [c for c in self.changes if c.change_type == ChangeType.EDGE_REMOVED]

    @property
    def violations(self) -> List[TopologyChange]:
        return [c for c in self.changes if c.rule_violation is not None]


class SnapshotDiffer:
    """
    Computes structural diffs between topology snapshots.

    Features:
    - Detect added/removed nodes
    - Detect added/removed edges
    - Identify rule violations
    - Classify severity
    """

    def __init__(self, baseline: TopologyIntegrityGraph):
        self.baseline = baseline

    def diff(self, current: TopologyIntegrityGraph) -> TopologyDiff:
        """
        Compute diff between baseline and current topology.

        Args:
            current: Current topology to compare

        Returns:
            TopologyDiff with all changes
        """
        changes = []

        # Get node sets
        baseline_nodes = set(self.baseline.graph.nodes())
        current_nodes = set(current.graph.nodes())

        # Detect added nodes
        for node_id in current_nodes - baseline_nodes:
            node_class = current.get_node_class(node_id)
            node_data = dict(current.graph.nodes[node_id])
            changes.append(
                TopologyChange(
                    change_type=ChangeType.NODE_ADDED,
                    element_id=node_id,
                    details={
                        "class": node_class.value if node_class else "unknown",
                        "attributes": node_data,
                    },
                    severity="warning",
                )
            )

        # Detect removed nodes
        for node_id in baseline_nodes - current_nodes:
            node_class = self.baseline.get_node_class(node_id)
            node_data = dict(self.baseline.graph.nodes[node_id])
            changes.append(
                TopologyChange(
                    change_type=ChangeType.NODE_REMOVED,
                    element_id=node_id,
                    details={
                        "class": node_class.value if node_class else "unknown",
                        "attributes": node_data,
                    },
                    severity="warning",
                )
            )

        # Detect modified nodes
        for node_id in baseline_nodes & current_nodes:
            baseline_data = dict(self.baseline.graph.nodes[node_id])
            current_data = dict(current.graph.nodes[node_id])

            if baseline_data != current_data:
                changes.append(
                    TopologyChange(
                        change_type=ChangeType.NODE_MODIFIED,
                        element_id=node_id,
                        details={"baseline": baseline_data, "current": current_data},
                        severity="info",
                    )
                )

        # Get edge sets
        baseline_edges = set(self.baseline.graph.edges())
        current_edges = set(current.graph.edges())

        # Detect added edges
        for src, dst in current_edges - baseline_edges:
            edge_data = dict(current.graph.edges[src, dst])
            edge_class = edge_data.get("class", "unknown")

            # Check for rule violation
            violation = None
            src_class = current.get_node_class(src)
            dst_class = current.get_node_class(dst)

            if src_class and dst_class:
                try:
                    # Try to validate the edge
                    EdgeClass(edge_class)  # Validate enum
                except ValueError:
                    violation = f"Unknown edge class: {edge_class}"

            severity = "error" if violation else "warning"

            changes.append(
                TopologyChange(
                    change_type=ChangeType.EDGE_ADDED,
                    element_id=f"{src} -> {dst}",
                    details={
                        "source": src,
                        "target": dst,
                        "class": edge_class,
                        "attributes": edge_data,
                    },
                    rule_violation=violation,
                    severity=severity,
                )
            )

        # Detect removed edges
        for src, dst in baseline_edges - current_edges:
            edge_data = dict(self.baseline.graph.edges[src, dst])
            changes.append(
                TopologyChange(
                    change_type=ChangeType.EDGE_REMOVED,
                    element_id=f"{src} -> {dst}",
                    details={
                        "source": src,
                        "target": dst,
                        "class": edge_data.get("class", "unknown"),
                        "attributes": edge_data,
                    },
                    severity="warning",
                )
            )

        # Detect modified edges
        for src, dst in baseline_edges & current_edges:
            baseline_data = dict(self.baseline.graph.edges[src, dst])
            current_data = dict(current.graph.edges[src, dst])

            if baseline_data != current_data:
                changes.append(
                    TopologyChange(
                        change_type=ChangeType.EDGE_MODIFIED,
                        element_id=f"{src} -> {dst}",
                        details={"baseline": baseline_data, "current": current_data},
                        severity="info",
                    )
                )

        return TopologyDiff(
            baseline_fingerprint=self.baseline.compute_fingerprint(),
            current_fingerprint=current.compute_fingerprint(),
            has_drifted=self.baseline.compute_fingerprint()
            != current.compute_fingerprint(),
            changes=changes,
        )

    def classify_severity(self, diff: TopologyDiff) -> Dict[str, int]:
        """
        Classify changes by severity.

        Returns:
            Dictionary of severity -> count
        """
        severity_counts = {"info": 0, "warning": 0, "error": 0, "critical": 0}

        for change in diff.changes:
            severity_counts[change.severity] += 1

        return severity_counts

    def generate_report(self, diff: TopologyDiff) -> str:
        """Generate human-readable diff report."""
        lines = [
            "# Topology Diff Report",
            "",
            "## Summary",
            f"- Baseline fingerprint: `{diff.baseline_fingerprint}`",
            f"- Current fingerprint: `{diff.current_fingerprint}`",
            f"- Has drifted: {diff.has_drifted}",
            f"- Total changes: {len(diff.changes)}",
            "",
            "## Severity Breakdown",
        ]

        severity = self.classify_severity(diff)
        for sev, count in severity.items():
            lines.append(f"- {sev.upper()}: {count}")

        if diff.added_nodes:
            lines.extend(
                [
                    "",
                    "## Added Nodes",
                ]
            )
            for change in diff.added_nodes:
                lines.append(f"- `{change.element_id}` ({change.details['class']})")

        if diff.removed_nodes:
            lines.extend(
                [
                    "",
                    "## Removed Nodes",
                ]
            )
            for change in diff.removed_nodes:
                lines.append(f"- `{change.element_id}` ({change.details['class']})")

        if diff.added_edges:
            lines.extend(
                [
                    "",
                    "## Added Edges",
                ]
            )
            for change in diff.added_edges:
                violation_str = (
                    f" [VIOLATION: {change.rule_violation}]"
                    if change.rule_violation
                    else ""
                )
                lines.append(
                    f"- `{change.element_id}` ({change.details['class']}){violation_str}"
                )

        if diff.removed_edges:
            lines.extend(
                [
                    "",
                    "## Removed Edges",
                ]
            )
            for change in diff.removed_edges:
                lines.append(f"- `{change.element_id}` ({change.details['class']})")

        if diff.violations:
            lines.extend(
                [
                    "",
                    "## Rule Violations",
                ]
            )
            for change in diff.violations:
                lines.append(f"- {change.element_id}: {change.rule_violation}")

        return "\n".join(lines)

    def to_json(self, diff: TopologyDiff) -> str:
        """Export diff as JSON."""
        return json.dumps(
            {
                "baseline_fingerprint": diff.baseline_fingerprint,
                "current_fingerprint": diff.current_fingerprint,
                "has_drifted": diff.has_drifted,
                "changes": [
                    {
                        "type": c.change_type.value,
                        "element": c.element_id,
                        "details": c.details,
                        "violation": c.rule_violation,
                        "severity": c.severity,
                    }
                    for c in diff.changes
                ],
            },
            indent=2,
        )


if __name__ == "__main__":
    from .tig_core import create_sample_qsg_topology

    print("Snapshot Diffing Demo")
    print("=" * 50)

    # Create baseline
    baseline = create_sample_qsg_topology()
    baseline.set_baseline()

    # Create modified version
    current = create_sample_qsg_topology()
    current.add_node("client-3", NodeClass.CLIENT, role="new_device")
    current.add_edge("relay-1", "client-3", EdgeClass.TRANSPORT)

    # Compute diff
    differ = SnapshotDiffer(baseline)
    diff = differ.diff(current)

    print(differ.generate_report(diff))

    print("\n" + "=" * 50)
    print("Testing with unauthorized change...")

    # Create version with unauthorized edge (simulated)
    current2 = create_sample_qsg_topology()
    current2.add_node("attacker", NodeClass.CLIENT)
    # Directly add to graph (bypassing validation for demo)
    current2.graph.add_edge("attacker", "core-1", **{"class": "transport"})
    current2._node_classes["attacker"] = NodeClass.CLIENT

    diff2 = differ.diff(current2)
    print(differ.generate_report(diff2))
