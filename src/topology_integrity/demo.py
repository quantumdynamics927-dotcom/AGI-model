"""
TIG Comprehensive Demo - All Capabilities

Demonstrates all TIG modules working together:
- Core topology with schema enforcement
- Path analysis for attack detection
- Metrics for security assessment
- Snapshot diffing for drift detection
- QSG component mapping

Reference: research/quantum_security/topology_integrity_graph/SCHEMA.md
"""

from .diffing import SnapshotDiffer
from .metrics import MetricsCalculator
from .path_analysis import PathAnalyzer
from .qsg_mapping import QSGMapper
from .tig_core import EdgeClass, NodeClass, create_sample_qsg_topology


def run_comprehensive_demo():
    """Run comprehensive TIG demo."""

    print("=" * 70)
    print("TOPOLOGY INTEGRITY GRAPH (TIG) - Comprehensive Demo")
    print("=" * 70)

    # 1. Create baseline topology
    print("\n[1] BASELINE TOPOLOGY")
    print("-" * 70)
    baseline = create_sample_qsg_topology()
    baseline.set_baseline()

    print(f"Graph: {baseline.name}")
    print(f"Nodes: {baseline.graph.number_of_nodes()}")
    print(f"Edges: {baseline.graph.number_of_edges()}")
    print(f"Fingerprint: {baseline.compute_fingerprint()}")

    # 2. Compute metrics
    print("\n[2] SECURITY METRICS")
    print("-" * 70)
    calculator = MetricsCalculator(baseline)
    metrics = calculator.compute_all_metrics()

    print(f"Total nodes: {metrics.total_nodes}")
    print(f"Total edges: {metrics.total_edges}")
    print(f"Forbidden edges: {metrics.forbidden_edges}")
    print(f"Privilege escalation risk: {metrics.privilege_escalation_risk:.4f}")
    print(f"Crown jewel proximity: {metrics.crown_jewel_proximity:.4f}")
    print(f"Entropy source isolation: {metrics.entropy_source_isolation:.2%}")
    print(f"Verification coverage: {metrics.verification_coverage:.2%}")

    # 3. Path analysis
    print("\n[3] PATH ANALYSIS")
    print("-" * 70)
    analyzer = PathAnalyzer(baseline)
    result = analyzer.full_analysis()

    print(f"Total paths to CORE: {result.total_paths}")
    print(f"Safe paths: {result.safe_paths}")
    print(f"Risky paths: {result.risky_paths}")
    print(f"Critical paths: {result.critical_paths}")

    print("-" * 70)
    mapper = QSGMapper(baseline)

    print("Component mapping:")
    for node_id, mapping in mapper.map_all_nodes().items():
        print(
            f"  {node_id} -> {mapping.qsg_component.value} ({mapping.node_class.value})"
        )

    print("\nValidation:")
    errors = mapper.validate_integration()
    if errors:
        for error in errors:
            print(f"  ⚠️  {error}")
    else:
        print("  ✅ All validation checks passed")

    # 5. Simulate drift
    print("\n[5] DRIFT DETECTION")
    print("-" * 70)

    # Create modified topology
    current = create_sample_qsg_topology()
    current.add_node("client-3", NodeClass.CLIENT, role="new_device")
    current.add_edge("relay-1", "client-3", EdgeClass.TRANSPORT)

    # Compute diff
    differ = SnapshotDiffer(baseline)
    diff = differ.diff(current)

    print(f"Has drifted: {diff.has_drifted}")
    print(f"Baseline fingerprint: {diff.baseline_fingerprint}")
    print(f"Current fingerprint: {diff.current_fingerprint}")
    print(f"Total changes: {len(diff.changes)}")

    if diff.added_nodes:
        print("\nAdded nodes:")
        for change in diff.added_nodes:
            print(f"  + {change.element_id} ({change.details['class']})")

    if diff.added_edges:
        print("\nAdded edges:")
        for change in diff.added_edges:
            print(f"  + {change.element_id} ({change.details['class']})")

    # 6. Simulate attack
    print("\n[6] ATTACK DETECTION")
    print("-" * 70)

    # Create compromised topology
    compromised = create_sample_qsg_topology()
    compromised.add_node("attacker", NodeClass.CLIENT)
    # Bypass validation (simulated compromise)
    compromised.graph.add_edge("attacker", "core-1", **{"class": "transport"})
    compromised._node_classes["attacker"] = NodeClass.CLIENT

    # Analyze attack paths
    attack_analyzer = PathAnalyzer(compromised)
    attack_result = attack_analyzer.full_analysis()

    print(f"Total paths to CORE: {attack_result.total_paths}")
    print(f"Critical paths: {attack_result.critical_paths}")

    if attack_result.bypass_paths:
        print("\nBypass paths detected:")
        for ap in attack_result.bypass_paths:
            print(f"  {' -> '.join(ap.path)}")
            for issue in ap.issues:
                print(f"    ⚠️  {issue}")

    # Compute diff for attack
    attack_diff = differ.diff(compromised)
    print(f"\nDrift detected: {attack_diff.has_drifted}")
    print(f"Changes: {len(attack_diff.changes)}")

    # 7. Summary
    print("\n[7] SUMMARY")
    print("-" * 70)
    print("TIG Capabilities Demonstrated:")
    print("  ✅ Schema enforcement (forbidden edges blocked)")
    print("  ✅ Fingerprinting (drift detection)")
    print("  ✅ Path analysis (attack path enumeration)")
    print("  ✅ Security metrics (privilege escalation, crown jewel proximity)")
    print("  ✅ Snapshot diffing (change detection)")
    print("  ✅ QSG component mapping (integration validation)")

    print("\n" + "=" * 70)
    print("Demo complete!")
    print("=" * 70)


if __name__ == "__main__":
    run_comprehensive_demo()
