"""
TIG QSG Mapping - Topology to QSG Component Mapping

Maps TIG node classes to QSG components for integration.

Reference: research/quantum_security/topology_integrity_graph/SCHEMA.md
"""

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set

from .tig_core import EdgeClass, NodeClass, TopologyIntegrityGraph


class QSGComponent(Enum):
    """QSG system components."""

    QRNG = "qrng"  # Entropy source
    ENTROPY_VALIDATOR = "entropy_validator"  # Validates entropy quality
    PQC = "pqc"  # Post-quantum cryptography
    AEAD = "aead"  # Authenticated encryption
    TRANSPORT = "transport"  # Network transport layer
    POLICY_ENGINE = "policy_engine"  # Policy/trust root
    EVIDENCE_CHAIN = "evidence_chain"  # Audit/evidence storage
    CLIENT_API = "client_api"  # Client interface
    KEY_MANAGER = "key_manager"  # Key management


@dataclass
class ComponentMapping:
    """Mapping between TIG node class and QSG component."""

    node_class: NodeClass
    qsg_component: QSGComponent
    description: str
    responsibilities: List[str]
    security_requirements: List[str]


# Standard QSG component mappings
QSG_MAPPINGS: Dict[NodeClass, ComponentMapping] = {
    NodeClass.SOURCE: ComponentMapping(
        node_class=NodeClass.SOURCE,
        qsg_component=QSGComponent.QRNG,
        description="Quantum Random Number Generator - entropy source",
        responsibilities=[
            "Generate quantum entropy",
            "Provide randomness to entropy validator",
            "Maintain entropy pool quality",
        ],
        security_requirements=[
            "Hardware security module",
            "Side-channel resistance",
            "Entropy quality validation",
        ],
    ),
    NodeClass.VERIFIER: ComponentMapping(
        node_class=NodeClass.VERIFIER,
        qsg_component=QSGComponent.ENTROPY_VALIDATOR,
        description="Entropy Validator - validates entropy quality",
        responsibilities=[
            "Validate entropy from QRNG",
            "Perform statistical tests",
            "Certify entropy quality",
        ],
        security_requirements=[
            "NIST SP 800-90B compliance",
            "Statistical test suite",
            "Tamper detection",
        ],
    ),
    NodeClass.CRYPTO: ComponentMapping(
        node_class=NodeClass.CRYPTO,
        qsg_component=QSGComponent.PQC,
        description="Post-Quantum Cryptography - cryptographic operations",
        responsibilities=[
            "Key generation",
            "Encryption/decryption",
            "Digital signatures",
        ],
        security_requirements=[
            "NIST PQC standards",
            "Key isolation",
            "Side-channel resistance",
        ],
    ),
    NodeClass.RELAY: ComponentMapping(
        node_class=NodeClass.RELAY,
        qsg_component=QSGComponent.TRANSPORT,
        description="Transport Layer - secure communication",
        responsibilities=[
            "Secure message routing",
            "Protocol handling",
            "Connection management",
        ],
        security_requirements=[
            "TLS 1.3+",
            "Certificate validation",
            "Connection authentication",
        ],
    ),
    NodeClass.CORE: ComponentMapping(
        node_class=NodeClass.CORE,
        qsg_component=QSGComponent.POLICY_ENGINE,
        description="Policy Engine - trust root and policy decisions",
        responsibilities=["Policy enforcement", "Trust decisions", "Authorization"],
        security_requirements=[
            "Secure boot",
            "Hardware root of trust",
            "Audit logging",
        ],
    ),
    NodeClass.AUDITOR: ComponentMapping(
        node_class=NodeClass.AUDITOR,
        qsg_component=QSGComponent.EVIDENCE_CHAIN,
        description="Evidence Chain - audit and evidence storage",
        responsibilities=[
            "Evidence collection",
            "Audit logging",
            "Compliance verification",
        ],
        security_requirements=[
            "Immutable storage",
            "Cryptographic attestation",
            "Timestamp authority",
        ],
    ),
    NodeClass.CLIENT: ComponentMapping(
        node_class=NodeClass.CLIENT,
        qsg_component=QSGComponent.CLIENT_API,
        description="Client API - external interface",
        responsibilities=["Request handling", "Authentication", "Rate limiting"],
        security_requirements=["Input validation", "Authentication", "DDoS protection"],
    ),
}


class QSGMapper:
    """
    Maps TIG topology to QSG components.

    Features:
    - Node class to component mapping
    - Edge class to data flow mapping
    - Security requirement mapping
    - Integration validation
    """

    def __init__(self, tig: TopologyIntegrityGraph):
        self.tig = tig

    def map_node(self, node_id: str) -> Optional[ComponentMapping]:
        """Map a TIG node to its QSG component."""
        node_class = self.tig.get_node_class(node_id)
        if node_class is None:
            return None
        return QSG_MAPPINGS.get(node_class)

    def map_all_nodes(self) -> Dict[str, ComponentMapping]:
        """Map all TIG nodes to QSG components."""
        mappings = {}
        for node_id in self.tig.graph.nodes():
            mapping = self.map_node(node_id)
            if mapping:
                mappings[node_id] = mapping
        return mappings

    def get_component_nodes(self, component: QSGComponent) -> List[str]:
        """Get all nodes mapped to a specific QSG component."""
        nodes = []
        for node_id in self.tig.graph.nodes():
            mapping = self.map_node(node_id)
            if mapping and mapping.qsg_component == component:
                nodes.append(node_id)
        return nodes

    def get_data_flows(self) -> List[Dict]:
        """
        Map edges to data flows between QSG components.

        Returns:
            List of data flow dictionaries
        """
        flows = []

        for src, dst in self.tig.graph.edges():
            edge_data = self.tig.graph.edges[src, dst]
            edge_class = edge_data.get("class", "unknown")

            src_mapping = self.map_node(src)
            dst_mapping = self.map_node(dst)

            if src_mapping and dst_mapping:
                flows.append(
                    {
                        "source_node": src,
                        "source_component": src_mapping.qsg_component.value,
                        "target_node": dst,
                        "target_component": dst_mapping.qsg_component.value,
                        "edge_class": edge_class,
                        "description": self._describe_flow(
                            src_mapping.qsg_component,
                            dst_mapping.qsg_component,
                            edge_class,
                        ),
                    }
                )

        return flows

    def _describe_flow(
        self, src: QSGComponent, dst: QSGComponent, edge_class: str
    ) -> str:
        """Generate human-readable description of data flow."""
        descriptions = {
            (
                QSGComponent.QRNG,
                QSGComponent.ENTROPY_VALIDATOR,
                "transport",
            ): "Raw entropy for validation",
            (
                QSGComponent.ENTROPY_VALIDATOR,
                QSGComponent.PQC,
                "trust",
            ): "Certified entropy for key generation",
            (
                QSGComponent.PQC,
                QSGComponent.TRANSPORT,
                "transport",
            ): "Encrypted data for transmission",
            (
                QSGComponent.TRANSPORT,
                QSGComponent.CLIENT_API,
                "transport",
            ): "Secure message delivery",
            (
                QSGComponent.POLICY_ENGINE,
                QSGComponent.EVIDENCE_CHAIN,
                "admin",
            ): "Policy decisions for audit",
            (
                QSGComponent.EVIDENCE_CHAIN,
                QSGComponent.POLICY_ENGINE,
                "verify",
            ): "Evidence for policy decisions",
        }

        key = (src, dst, edge_class)
        return descriptions.get(key, f"Data flow from {src.value} to {dst.value}")

    def validate_integration(self) -> List[str]:
        """
        Validate that TIG topology is compatible with QSG architecture.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # Check for required components
        required_components = {
            QSGComponent.QRNG: "Entropy source required",
            QSGComponent.ENTROPY_VALIDATOR: "Entropy validator required",
            QSGComponent.PQC: "Cryptographic module required",
            QSGComponent.POLICY_ENGINE: "Policy engine required",
        }

        for component, message in required_components.items():
            if not self.get_component_nodes(component):
                errors.append(f"Missing {component.value}: {message}")

        # Check for required flows
        flows = self.get_data_flows()
        flow_pairs = {(f["source_component"], f["target_component"]) for f in flows}

        required_flows = [
            (QSGComponent.QRNG.value, QSGComponent.ENTROPY_VALIDATOR.value),
            (QSGComponent.ENTROPY_VALIDATOR.value, QSGComponent.PQC.value),
        ]

        for src, dst in required_flows:
            if (src, dst) not in flow_pairs:
                errors.append(f"Missing required flow: {src} -> {dst}")

        # Check for forbidden edges
        forbidden = self.tig.count_forbidden_edges()
        if forbidden > 0:
            errors.append(f"Topology contains {forbidden} forbidden edges")

        return errors

    def generate_integration_report(self) -> str:
        """Generate human-readable integration report."""
        lines = ["# QSG Integration Report", "", "## Component Mapping", ""]

        for node_id, mapping in self.map_all_nodes().items():
            lines.append(
                f"- `{node_id}` -> **{mapping.qsg_component.value}** ({mapping.node_class.value})"
            )

        lines.extend(["", "## Data Flows", ""])

        for flow in self.get_data_flows():
            lines.append(
                f"- `{flow['source_node']}` ({flow['source_component']}) --[{flow['edge_class']}]--> `{flow['target_node']}` ({flow['target_component']})"
            )

        lines.extend(["", "## Security Requirements", ""])

        # Aggregate security requirements by component
        for component in QSGComponent:
            nodes = self.get_component_nodes(component)
            if nodes:
                mapping = QSG_MAPPINGS.get(
                    list(QSG_MAPPINGS.keys())[
                        list(QSG_MAPPINGS.values()).index(
                            next(
                                m
                                for m in QSG_MAPPINGS.values()
                                if m.qsg_component == component
                            )
                        )
                    ]
                )
                if mapping:
                    lines.append(f"### {component.value}")
                    for req in mapping.security_requirements:
                        lines.append(f"- {req}")
                    lines.append("")

        # Validation
        lines.extend(["## Validation", ""])

        errors = self.validate_integration()
        if errors:
            lines.append("### Errors")
            for error in errors:
                lines.append(f"- {error}")
        else:
            lines.append("✅ All validation checks passed")

        return "\n".join(lines)

    def to_json(self) -> str:
        """Export mapping as JSON."""
        mappings = {}
        for node_id, mapping in self.map_all_nodes().items():
            mappings[node_id] = {
                "component": mapping.qsg_component.value,
                "node_class": mapping.node_class.value,
                "description": mapping.description,
                "responsibilities": mapping.responsibilities,
                "security_requirements": mapping.security_requirements,
            }

        return json.dumps(
            {
                "mappings": mappings,
                "data_flows": self.get_data_flows(),
                "validation_errors": self.validate_integration(),
            },
            indent=2,
        )


if __name__ == "__main__":
    from .tig_core import create_sample_qsg_topology

    print("QSG Mapping Demo")
    print("=" * 50)

    tig = create_sample_qsg_topology()
    mapper = QSGMapper(tig)

    print(mapper.generate_integration_report())
