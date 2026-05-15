# Topology Integrity Graph (TIG)

## Purpose

Formalize the layered graph topology from geometric patterns into an engineering framework for QSG security architecture, access control, and anomaly detection.

## Background

Geometric patterns with central hub, concentric layers, and dense constrained connectivity can be abstracted into graph structures useful for:
- Topology fingerprinting
- Anomaly detection
- Access control graphs
- Routing/segmentation shells

This research extracts the topology as a graph template, removing symbolic associations while preserving structural properties.

## Graph Schema

### Node Classes

| Class | Description | QSG Mapping |
|-------|-------------|-------------|
| `CORE` | Central authority node | Root trust, policy decision core |
| `VERIFIER` | Validation nodes | Entropy validation, audit checkpoints, signature verification |
| `CRYPTO` | Cryptographic service nodes | PQC key exchange, payload sealing, session orchestration |
| `RELAY` | Transport nodes | Secure relay logic, gateways |
| `CLIENT` | External interface nodes | Devices, external gateways, ingress/egress points |
| `SOURCE` | Entropy/data sources | QRNG, entropy pools, data inputs |
| `AUDITOR` | Monitoring nodes | Audit chains, logging, compliance checks |

### Edge Classes

| Class | Description | Constraints |
|-------|-------------|-------------|
| `TRUST` | Root trust relationship | CORE → any node |
| `VERIFY` | Verification authority | VERIFIER → CRYPTO, RELAY |
| `DERIVE` | Key/entropy derivation | SOURCE → CRYPTO |
| `TRANSPORT` | Secure communication | RELAY → RELAY, RELAY → CLIENT |
| `ADMIN` | Administrative access | CORE → any (with audit) |
| `READ` | Data read access | CRYPTO → CLIENT (authorized) |
| `SIGN` | Signing authority | CRYPTO → AUDITOR |

### Layer Structure

```
Layer 0 (Center):     [CORE]
                      /    \
Layer 1 (Inner):   [VERIFIER] [AUDITOR]
                   /    |    \
Layer 2 (Middle): [CRYPTO] [RELAY] [RELAY]
                  /   |   |   \
Layer 3 (Outer): [CLIENT] [CLIENT] [CLIENT] [SOURCE]
```

## Topology Properties

### Structural Constraints

1. **Hub-and-Spoke**: All paths to CORE must pass through VERIFIER layer
2. **Ring Isolation**: Nodes in layer N can only communicate with:
   - Same layer (peer-to-peer)
   - Adjacent layers (N-1, N+1)
   - No skip-layer edges
3. **Core Protection**: CORE has no direct edges to outer layers
4. **Source Isolation**: SOURCE nodes only connect to CRYPTO layer
5. **Client Boundary**: CLIENT nodes only connect to RELAY layer

### Connectivity Rules

```python
ALLOWED_EDGES = {
    CORE: [VERIFIER, AUDITOR],
    VERIFIER: [CORE, CRYPTO, RELAY, AUDITOR],
    AUDITOR: [CORE, VERIFIER],
    CRYPTO: [VERIFIER, RELAY, AUDITOR],
    RELAY: [VERIFIER, CRYPTO, CLIENT],
    CLIENT: [RELAY],
    SOURCE: [CRYPTO]
}
```

## Metrics

### Structural Metrics

| Metric | Description | Formula |
|--------|-------------|---------|
| `degree_drift` | Change in node degree over time | Δ deg(v) / deg(v) |
| `forbidden_edges` | Count of edges violating ALLOWED_EDGES | Σ 1(edge ∉ ALLOWED) |
| `path_to_core` | Shortest path length to CORE | min(dist(v, CORE)) |
| `community_deviation` | Modularity change in community structure | Q(t) - Q(t-1) |
| `structural_hash` | Hash of canonical edge list | H(sorted(edges)) |

### Security Metrics

| Metric | Description | Threshold |
|--------|-------------|-----------|
| `crown_jewel_proximity` | Unauthorized path length to CORE | Alert if < 2 |
| `privilege_escalation_risk` | Path from CLIENT to CORE without VERIFIER | Alert if exists |
| `entropy_source_isolation` | SOURCE node connectivity | Alert if connected to non-CRYPTO |
| `verification_coverage` | Fraction of operations passing through VERIFIER | Target > 0.95 |

### Anomaly Detection

```python
def compute_anomaly_score(graph, baseline) -> float:
    """
    Compute anomaly score based on structural drift.
    
    Returns score in [0, 1] where 1 = high anomaly
    """
    scores = {
        'degree_drift': compute_degree_drift(graph, baseline),
        'forbidden_edges': count_forbidden_edges(graph) / MAX_FORBIDDEN,
        'community_deviation': abs(compute_modularity(graph) - compute_modularity(baseline)),
        'hash_delta': 1 if hash_graph(graph) != hash_graph(baseline) else 0
    }
    
    # Weighted combination
    weights = {'degree_drift': 0.3, 'forbidden_edges': 0.4, 
               'community_deviation': 0.2, 'hash_delta': 0.1}
    
    return sum(scores[k] * weights[k] for k in scores)
```

## Fingerprinting

### Canonical Representation

```python
def canonical_graph_representation(graph) -> str:
    """
    Create canonical string representation for hashing.
    
    Format: "node_class:id;edge:src_class:src_id:dst_class:dst_id;..."
    """
    nodes = sorted([(n['class'], n['id']) for n in graph.nodes()])
    edges = sorted([
        (e['src_class'], e['src_id'], e['dst_class'], e['dst_id'])
        for e in graph.edges()
    ])
    
    node_str = ';'.join([f"{cls}:{id}" for cls, id in nodes])
    edge_str = ';'.join([f"{sc}:{si}:{dc}:{di}" for sc, si, dc, di in edges])
    
    return f"{node_str}|{edge_str}"


def compute_topology_hash(graph) -> str:
    """Compute SHA-256 hash of canonical representation."""
    import hashlib
    canonical = canonical_graph_representation(graph)
    return hashlib.sha256(canonical.encode()).hexdigest()[:32]
```

### Fingerprint Comparison

```python
def compare_fingerprints(fp1: str, fp2: str) -> dict:
    """
    Compare two topology fingerprints.
    
    Returns:
        {
            'identical': bool,
            'hamming_distance': int,
            'structural_similarity': float
        }
    """
    # Hamming distance
    hamming = sum(c1 != c2 for c1, c2 in zip(fp1, fp2))
    
    # Structural similarity (Jaccard of edge sets)
    # Requires decoding fingerprints back to graphs
    
    return {
        'identical': fp1 == fp2,
        'hamming_distance': hamming,
        'structural_similarity': 1 - (hamming / len(fp1))
    }
```

## QSG Integration

### Module Mapping

```
qsg_topology_integrity/
├── __init__.py
├── graph_schema.py          # Node/edge class definitions
├── topology_builder.py        # Graph construction
├── fingerprint.py             # Hashing and comparison
├── anomaly_detector.py        # Drift detection
├── metrics.py                 # Metric computation
└── validator.py               # Constraint checking
```

### API Interface

```python
class TopologyIntegrityGraph:
    """QSG Topology Integrity Graph manager."""
    
    def __init__(self, schema: GraphSchema):
        self.graph = nx.DiGraph()
        self.schema = schema
        self.baseline_hash = None
    
    def add_node(self, node_id: str, node_class: NodeClass) -> None:
        """Add node with class validation."""
        if node_class not in self.schema.allowed_classes:
            raise ValueError(f"Invalid node class: {node_class}")
        self.graph.add_node(node_id, class=node_class)
    
    def add_edge(self, src: str, dst: str, edge_class: EdgeClass) -> None:
        """Add edge with constraint validation."""
        if not self.schema.is_edge_allowed(src, dst, edge_class):
            raise ForbiddenEdgeError(f"Edge {src} -> {dst} violates schema")
        self.graph.add_edge(src, dst, class=edge_class)
    
    def compute_fingerprint(self) -> str:
        """Compute topology fingerprint."""
        return compute_topology_hash(self.graph)
    
    def detect_anomalies(self) -> List[Anomaly]:
        """Detect structural anomalies."""
        if self.baseline_hash is None:
            raise ValueError("Baseline not set")
        
        current_hash = self.compute_fingerprint()
        if current_hash == self.baseline_hash:
            return []
        
        # Compute detailed anomalies
        return self._compute_anomaly_details()
    
    def set_baseline(self) -> None:
        """Set current topology as baseline."""
        self.baseline_hash = self.compute_fingerprint()
```

## Validation Criteria

### Success Criteria

- [ ] Graph schema enforces all structural constraints
- [ ] Fingerprint is deterministic (same graph → same hash)
- [ ] Anomaly detection identifies forbidden edges
- [ ] Metrics correlate with intentional topology changes
- [ ] Performance scales to 1000+ nodes

### Failure Criteria

- [ ] Non-deterministic fingerprinting
- [ ] False positive rate > 5% for valid changes
- [ ] Cannot detect privilege escalation paths
- [ ] Performance degrades with < 100 nodes

## References

- Graph-based anomaly detection: nature.com/nature-index/topics/l4/graph-based-anomaly-detection-in-network-systems
- Access control graphs: enterprise-knowledge.com/graph-based-security-entitlements
- Topology-aware security: lpasquale.github.io/papers/Computer2017.pdf
- Graph fingerprinting: arxiv.org/html/2410.21936v1