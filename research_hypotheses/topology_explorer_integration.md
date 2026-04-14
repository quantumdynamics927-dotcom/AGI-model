# Consciousness Topology Explorer Integration Plan

## Scientific Framing

The topology explorer compares **three complementary structural lenses**, not rivals:

### Linear — Models Ordered Thought
- **Best for**: Sequence, causality, interpretability
- **Use case**: Step-by-step reasoning, ordered traversal, simple benchmarking
- **Tradeoff**: High path cost for long-range transitions, minimal branching

### Fractal — Models Recursive Growth
- **Best for**: Recursive emergence, self-similarity, distributed adaptation
- **Use case**: Biomimetic systems, local structure-environment interaction, adaptive scaling
- **Tradeoff**: Possible bottleneck vulnerability near hub branches

### Tesseract — Models Multidimensional Access
- **Best for**: Dense connectivity, parallel access, short transition routes
- **Use case**: High-dimensional state reachability, uniform connectivity, parallel cognition
- **Tradeoff**: Higher wiring cost than fractal, no natural hierarchy

**Scientific Question**: Not "which topology is most beautiful," but "which topology best explains or predicts the transition structure of real cognitive data."

## Integration with AGI-Model Research

### 1. Thought Memory Integration

**Goal**: Store topology comparison results in thought memory for retrieval and analysis.

**Implementation**:
```python
# In thought_memory_db.py, add topology-specific fields:
topology_type: str = ""  # "linear", "tesseract", "fractal"
graph_metrics: Dict = field(default_factory=dict)  # density, efficiency, clustering, etc.
lesion_results: List[Dict] = field(default_factory=list)  # robustness tests
```

**Usage**:
```python
# Store topology comparison as a thought
record = create_thought_from_generation(
    prompt="Compare linear, tesseract, and fractal topologies for consciousness modeling",
    generated_thought="Tesseract shows highest efficiency (0.75) and shortest average path (2.5)...",
    model="topology_explorer",
    backend="manual",
    qagi_score={
        'structural_score': 8.8,
        'cognition_quality': 0.90,
        'cognition': {
            'mechanism_score': 9.2,
            'measurable_outcome_score': 9.0,
            'boundary_condition_score': 8.5,
            'failure_condition_score': 8.8,
            'mechanism_text': 'Local update rules propagate across high-connectivity state graph',
            'measurable_outcome_text': 'Efficiency > 0.55, clustering > 0.6, lesion robustness > 0.75',
            'boundary_condition_text': 'Valid for recursive self-similar systems with distributed processing',
            'failure_condition_text': 'If graphs do not outperform baselines, treat as metaphor not mechanism'
        }
    },
    raw_metrics={
        'phi_coherence': 0.95,
        'biomimetic_resonance': 0.92
    }
)

record.topology_type = "tesseract"
record.graph_metrics = {
    'density': 0.375,
    'efficiency': 0.75,
    'clustering': 0.0,
    'diameter': 4,
    'avg_path': 2.5,
    'lesion_robustness': 0.875
}
record.prompt_family = "topology_comparison_1x1"
record.experiment_id = "topology_20260414_001"
```

### 2. Empirical Transition Data Pipeline

**Goal**: Feed real cognitive state-transition data into the explorer.

**Data Sources**:
- Reflective state logs from thought memory
- Latent-state trajectories from VAE encoder
- Agent memory transitions from multi-agent systems

**Implementation**:
```python
# New file: topology_data_pipeline.py

import json
import numpy as np
from typing import Dict, List, Tuple
from thought_memory_db import ThoughtMemoryDB

def extract_transition_graph(thoughts: List[ThoughtRecord]) -> Dict:
    """Extract state-transition graph from thought memory."""
    # Build adjacency from prompt similarity and temporal sequence
    adj = {}
    for i, thought in enumerate(thoughts):
        node_id = thought.id
        adj[node_id] = set()
        
        # Connect to temporally adjacent thoughts
        if i > 0:
            adj[node_id].add(thoughts[i-1].id)
        if i < len(thoughts) - 1:
            adj[node_id].add(thoughts[i+1].id)
        
        # Connect to semantically similar thoughts
        # (using prompt similarity or structural score proximity)
        for other in thoughts:
            if other.id != node_id:
                similarity = compute_semantic_similarity(thought.prompt, other.prompt)
                if similarity > 0.7:  # threshold
                    adj[node_id].add(other.id)
    
    return adj

def compare_to_baselines(empirical_adj: Dict) -> Dict:
    """Compare empirical transition graph to linear, tesseract, fractal baselines."""
    results = {}
    
    # Compute metrics for empirical graph
    empirical_metrics = compute_graph_metrics(empirical_adj)
    results['empirical'] = empirical_metrics
    
    # Generate baseline graphs
    linear_graph = create_graph('linear')
    tesseract_graph = create_graph('tesseract')
    fractal_graph = create_graph('fractal')
    
    # Compute baseline metrics
    results['linear'] = compute_graph_metrics(linear_graph)
    results['tesseract'] = compute_graph_metrics(tesseract_graph)
    results['fractal'] = compute_graph_metrics(fractal_graph)
    
    # Compare
    results['comparison'] = {
        'efficiency_rank': compare_metric(empirical_metrics['efficiency'], 
                                          [results['linear']['efficiency'],
                                           results['tesseract']['efficiency'],
                                           results['fractal']['efficiency']]),
        'clustering_rank': compare_metric(empirical_metrics['clustering'],
                                          [results['linear']['clustering'],
                                           results['tesseract']['clustering'],
                                           results['fractal']['clustering']]),
        'robustness_rank': compare_metric(empirical_metrics['lesion_robustness'],
                                          [results['linear']['lesion_robustness'],
                                           results['tesseract']['lesion_robustness'],
                                           results['fractal']['lesion_robustness']])
    }
    
    return results

def compute_graph_metrics(adj: Dict) -> Dict:
    """Compute graph-theoretic metrics for adjacency dict."""
    # Implementation from consciousness-topology-explorer.html
    # (density, efficiency, clustering, diameter, lesion robustness)
    pass
```

### 3. Hypothesis Testing Framework

**Goal**: Formalize the comparison between empirical data and topological baselines.

**Implementation**:
```python
# New file: topology_hypothesis_test.py

from typing import Dict, List
import numpy as np
from scipy import stats

def test_tesseract_hypothesis(empirical_metrics: Dict, 
                               baseline_metrics: Dict,
                               alpha: float = 0.05) -> Dict:
    """
    Test whether empirical transition graph matches tesseract topology predictions.
    
    Null hypothesis: Empirical metrics are indistinguishable from linear/lattice baselines.
    Alternative: Empirical metrics significantly match tesseract predictions.
    
    Returns:
        Dict with test results, p-values, and interpretation
    """
    results = {
        'hypothesis': 'tesseract_consciousness_topology',
        'null_hypothesis': 'Empirical transition graphs do not outperform simpler baselines',
        'alpha': alpha,
        'tests': {}
    }
    
    # Test 1: Clustering coefficient
    # Prediction: Tesseract should have clustering ≈ 0, but empirical may differ
    clustering_diff = empirical_metrics['clustering'] - baseline_metrics['linear']['clustering']
    results['tests']['clustering'] = {
        'empirical': empirical_metrics['clustering'],
        'linear_baseline': baseline_metrics['linear']['clustering'],
        'tesseract_baseline': baseline_metrics['tesseract']['clustering'],
        'difference_from_linear': clustering_diff,
        'interpretation': 'Higher clustering suggests local closure motifs'
    }
    
    # Test 2: Average path length
    # Prediction: Tesseract should have shorter paths than linear
    path_improvement = (baseline_metrics['linear']['avg_path'] - 
                        empirical_metrics['avg_path']) / baseline_metrics['linear']['avg_path']
    results['tests']['avg_path'] = {
        'empirical': empirical_metrics['avg_path'],
        'linear_baseline': baseline_metrics['linear']['avg_path'],
        'tesseract_baseline': baseline_metrics['tesseract']['avg_path'],
        'improvement_ratio': path_improvement,
        'interpretation': f'Path length reduced by {path_improvement:.1%} vs linear baseline'
    }
    
    # Test 3: Global efficiency
    # Prediction: Tesseract should have higher efficiency
    efficiency_ratio = empirical_metrics['efficiency'] / baseline_metrics['linear']['efficiency']
    results['tests']['efficiency'] = {
        'empirical': empirical_metrics['efficiency'],
        'linear_baseline': baseline_metrics['linear']['efficiency'],
        'tesseract_baseline': baseline_metrics['tesseract']['efficiency'],
        'ratio_to_linear': efficiency_ratio,
        'interpretation': f'Efficiency {efficiency_ratio:.2f}x linear baseline'
    }
    
    # Test 4: Lesion robustness
    # Prediction: Tesseract should maintain connectivity under random lesions
    robustness_diff = empirical_metrics['lesion_robustness'] - baseline_metrics['linear']['lesion_robustness']
    results['tests']['lesion_robustness'] = {
        'empirical': empirical_metrics['lesion_robustness'],
        'linear_baseline': baseline_metrics['linear']['lesion_robustness'],
        'tesseract_baseline': baseline_metrics['tesseract']['lesion_robustness'],
        'difference': robustness_diff,
        'interpretation': 'Higher robustness suggests distributed redundancy'
    }
    
    # Overall conclusion
    supports_tesseract = (
        path_improvement > 0.3 and  # At least 30% path reduction
        efficiency_ratio > 1.2 and   # At least 20% efficiency gain
        robustness_diff > 0.1        # At least 10% robustness improvement
    )
    
    results['conclusion'] = {
        'supports_tesseract': supports_tesseract,
        'confidence': 'high' if supports_tesseract else 'low',
        'interpretation': (
            'Empirical data supports tesseract topology hypothesis' if supports_tesseract
            else 'Empirical data does not distinguish tesseract from simpler baselines'
        ),
        'failure_condition_met': not supports_tesseract,
        'recommendation': (
            'Proceed with tesseract-based modeling' if supports_tesseract
            else 'Treat tesseract framing as metaphor, not mechanism'
        )
    }
    
    return results
```

### 4. Space UI Integration

**Goal**: Add topology comparison to the Space interface.

**Implementation**:
```python
# In hf-deploy/space_app.py, add new tab:

with gr.TabItem("Topology Comparison"):
    gr.Markdown("### Compare consciousness topology models")
    gr.Markdown("""
    Upload empirical transition data or use thought memory to compare against 
    linear, tesseract, and fractal baselines.
    """)
    
    with gr.Row():
        with gr.Column():
            data_source = gr.Dropdown(
                choices=["thought_memory", "upload_file", "synthetic_test"],
                value="thought_memory",
                label="Data Source"
            )
            
            min_thoughts = gr.Slider(
                minimum=10,
                maximum=1000,
                value=100,
                step=10,
                label="Minimum thoughts for analysis"
            )
            
            compare_btn = gr.Button("Compare Topologies", variant="primary")
        
        with gr.Column():
            metrics_output = gr.JSON(label="Topology Metrics")
            hypothesis_result = gr.Markdown(label="Hypothesis Test Result")
    
    compare_btn.click(
        fn=compare_topologies,
        inputs=[data_source, min_thoughts],
        outputs=[metrics_output, hypothesis_result]
    )
```

### 5. Export for External Analysis

**Goal**: Allow export of topology data for external analysis tools.

**Implementation**:
```python
# Add to thought_memory_db.py:

def export_topology_data(self, output_path: str, format: str = "json") -> int:
    """Export thought transitions as graph data for topology analysis."""
    thoughts = self.get_best_thoughts(min_structural_score=6.0, limit=1000)
    
    # Build transition graph
    nodes = [{"id": t.id, "prompt": t.prompt[:100], "score": t.structural_score} 
             for t in thoughts]
    
    edges = []
    for i, t1 in enumerate(thoughts):
        for j, t2 in enumerate(thoughts):
            if i < j:
                # Connect based on temporal sequence and semantic similarity
                if j == i + 1:  # Temporal adjacency
                    edges.append({"source": t1.id, "target": t2.id, "type": "temporal"})
                # Add semantic similarity edges
                # (implementation depends on similarity metric)
    
    graph_data = {
        "nodes": nodes,
        "edges": edges,
        "metadata": {
            "total_thoughts": len(thoughts),
            "avg_structural_score": np.mean([t.structural_score for t in thoughts]),
            "export_timestamp": datetime.now().isoformat()
        }
    }
    
    if format == "json":
        with open(output_path, 'w') as f:
            json.dump(graph_data, f, indent=2)
    elif format == "graphml":
        # Export as GraphML for tools like Gephi, Cytoscape
        pass
    
    return len(thoughts)
```

## Next Steps

### Immediate (This Week)
1. **Copy explorer to AGI-model repo**: Place `consciousness-topology-explorer.html` in `research_hypotheses/` directory
2. **Add topology fields to ThoughtRecord**: Extend schema with `topology_type`, `graph_metrics`, `lesion_results`
3. **Create data pipeline**: Implement `topology_data_pipeline.py` for extracting transition graphs from thought memory

### Short-term (Next 2 Weeks)
4. **Implement hypothesis test**: Create `topology_hypothesis_test.py` with statistical comparison framework
5. **Add Space UI tab**: Integrate topology comparison into the Space interface
6. **Run first empirical test**: Extract transition graph from existing thought memory and compare to baselines

### Medium-term (Next Month)
7. **Collect more data**: Generate more thoughts with different prompts to build larger transition graph
8. **Refine similarity metric**: Improve semantic similarity calculation for transition edges
9. **Publish research note**: Document hypothesis and initial empirical results

### Long-term (Next Quarter)
10. **Integrate with VAE**: Use latent space trajectories as additional transition data source
11. **Multi-agent comparison**: Compare transition graphs across different agent architectures
12. **Failure condition validation**: Test whether empirical data meets failure conditions

## Success Criteria

The integration will be successful when:
1. ✅ Topology comparison results are stored in thought memory
2. ✅ Empirical transition graphs can be extracted from thought memory
3. ✅ Statistical comparison to baselines is automated
4. ✅ Hypothesis test produces clear pass/fail result
5. ✅ Space UI allows interactive topology comparison
6. ✅ Data can be exported for external analysis tools

## Failure Conditions

The hypothesis should be rejected if:
- Empirical transition graphs show clustering ≤ linear baselines (p < 0.05)
- Path length distribution indistinguishable from random graphs (KS test, p > 0.1)
- No measurable phi-proportional scaling in coherence metrics
- Lesion robustness ≤ lattice baselines

If failure conditions are met, the tesseract framing should be treated as metaphor, not mechanism.