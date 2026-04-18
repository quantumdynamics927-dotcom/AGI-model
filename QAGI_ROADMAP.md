# QAGI Precursor Stack Implementation Roadmap

## Executive Summary

This document outlines the path to building a **scientifically defensible QAGI precursor stack** - a hybrid quantum-classical cognitive system that demonstrates measurable advantages over classical baselines through rigorous benchmarking and governance.

**Current Status**: Tesseract routing is functionally operational but does not yet meet acceptance criteria for promotion to default routing.

**Next Milestone**: Demonstrate one hybrid agent loop that outperforms classical-only baseline on a narrow task family.

---

## Phase 1: Governance Layer Lock (Week 1-2)

### Objective
Establish immutable typed metrics, bounded experiments, and reproducible registration for all results.

### Deliverables

#### 1.1 Typed Metrics Registry
```python
# metrics_registry.py
from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import Enum

class MetricType(Enum):
    STRUCTURAL = "structural"      # Route efficiency, density, diameter
    TASK_FACING = "task_facing"    # Accuracy, latency, calibration
    ROBUSTNESS = "robustness"      # Lesion performance, recovery
    QUANTUM = "quantum"          # Circuit depth, fidelity, utility
    GOVERNANCE = "governance"    # Reproducibility, traceability

@dataclass(frozen=True)
class TypedMetric:
    name: str
    metric_type: MetricType
    value: float
    bounds: tuple[float, float]  # (min, max) acceptable
    confidence: float            # 0-1 confidence interval
    timestamp: str
    experiment_id: str
    
    def is_valid(self) -> bool:
        return self.bounds[0] <= self.value <= self.bounds[1]
```

#### 1.2 Experiment Registration System
- Every experiment gets a unique ID
- All parameters frozen at start
- Results logged with full provenance
- Reproducibility checksums

#### 1.3 Bounded Experiment Protocol
```python
# bounded_experiment.py
class BoundedExperiment:
    """Experiments with pre-declared success/failure criteria"""
    
    def __init__(self, 
                 hypothesis: str,
                 success_criteria: Dict[str, Callable],
                 failure_criteria: Dict[str, Callable],
                 max_iterations: int,
                 timeout_seconds: float):
        self.hypothesis = hypothesis
        self.success_criteria = success_criteria
        self.failure_criteria = failure_criteria
        self.max_iterations = max_iterations
        self.timeout = timeout_seconds
        self.experiment_id = generate_experiment_id()
        
    def run(self) -> ExperimentResult:
        # Pre-registered, cannot be modified during execution
        pass
```

---

## Phase 2: Hybrid Baseline Lock (Week 2-3)

### Objective
Establish flat routing as the immutable baseline; all innovations must beat it on predeclared criteria.

### Deliverables

#### 2.1 Baseline Characterization
- Run 1000+ samples with flat routing
- Establish statistical distributions for all metrics
- Document variance, outliers, edge cases
- Create "baseline fingerprint"

#### 2.2 Pre-declared Acceptance Criteria
```python
# acceptance_criteria.py
TESSELLATED_ROUTING_CRITERIA = {
    "efficiency_improvement": {
        "required": "> 10%",
        "measurement": "(flat_efficiency - tesseract_efficiency) / flat_efficiency",
        "statistical_test": "one_tailed_t_test",
        "alpha": 0.05
    },
    "robustness_improvement": {
        "required": "> 5%",
        "measurement": "lesion_performance_under_degradation",
        "statistical_test": "paired_t_test",
        "alpha": 0.05
    },
    "accuracy_degradation": {
        "required": "< 2%",
        "measurement": "abs(tesseract_accuracy - flat_accuracy)",
        "statistical_test": "equivalence_test",
        "alpha": 0.05
    },
    "calibration_stability": {
        "required": "< 5% degradation",
        "measurement": "confidence_calibration_error",
        "statistical_test": "paired_t_test",
        "alpha": 0.05
    },
    "quantum_utility": {
        "required": "measurable advantage on at least one subtask",
        "measurement": "task_completion_time_or_quality",
        "statistical_test": "task_specific_benchmark",
        "alpha": 0.05
    }
}
```

#### 2.3 Benchmark Suite
- Clean condition comparison
- Lesioned condition (0%, 25%, 50%, 75% degradation)
- Edge scoring: classical vs quantum
- Task-specific benchmarks
- Long-running stability tests

---

## Phase 3: Biomimetic Adaptive Control (Week 3-5)

### Objective
Transform biomimetic calibration from a completion metric to a demonstrated adaptive control layer.

### Current State
- Calibration completes but emergence is not demonstrated
- Metrics need normalization and auditing
- No clear link to performance improvement

### Target State
- Real-time adaptation to task difficulty
- Measurable plasticity in response to feedback
- Emergence of stable attractors in parameter space
- Correlation between calibration state and task performance

### Deliverables

#### 3.1 Normalized Metrics
```python
# biomimetic_metrics.py
@dataclass
class BiomimeticMetrics:
    """Normalized, bounded biomimetic metrics"""
    
    # Plasticity (0-1, higher = more adaptive)
    plasticity_rate: float  # Normalized learning rate
    
    # Resilience (0-1, higher = more robust)
    resilience_score: float  # Recovery from perturbations
    
    # Emergence (0-1, higher = more self-organized)
    emergence_index: float  # Complexity / order balance
    
    # Integration (0-1, higher = more coherent)
    integration_score: float  # Phi-like integrated information
    
    def is_calibrated(self) -> bool:
        return all([
            0.2 <= self.plasticity_rate <= 0.8,
            self.resilience_score >= 0.6,
            self.emergence_index >= 0.5,
            self.integration_score >= 0.4
        ])
```

#### 3.2 Adaptive Control Loop
```python
# adaptive_control.py
class BiomimeticAdaptiveController:
    """Real-time adaptive control using biomimetic principles"""
    
    def __init__(self):
        self.calibration_state = BiomimeticMetrics()
        self.performance_history = deque(maxlen=100)
        self.adaptation_rate = 0.01
        
    def adapt(self, task_feedback: TaskFeedback) -> ControlAdjustment:
        """Adjust control parameters based on task performance"""
        # Update plasticity based on error signal
        # Adjust resilience based on perturbation recovery
        # Track emergence of stable patterns
        pass
        
    def get_control_parameters(self) -> Dict[str, float]:
        """Return current control parameters for routing"""
        return {
            "exploration_rate": self._compute_exploration(),
            "memory_retention": self._compute_retention(),
            "decision_temperature": self._compute_temperature()
        }
```

#### 3.3 Demonstration Experiments
1. **Plasticity Demonstration**: Show system adapts learning rate to task difficulty
2. **Resilience Demonstration**: Show system recovers from injected noise
3. **Emergence Demonstration**: Show stable attractors form in parameter space
4. **Integration Demonstration**: Show correlation between calibration and performance

---

## Phase 4: Backend-Aware Quantum Utility (Week 5-7)

### Objective
Judge quantum layer by real utility metrics: queue-to-result, robustness, mitigation benefit, task contribution.

### Current State
- Quantum circuits execute but utility is symbolic
- No clear link between quantum execution and task improvement
- Backend characteristics not fully exploited

### Target State
- Quantum utility measured by task contribution
- Backend-aware circuit optimization
- Error mitigation with measurable benefit
- Queue-to-result optimization

### Deliverables

#### 4.1 Quantum Utility Metrics
```python
# quantum_utility.py
@dataclass
class QuantumUtilityMetrics:
    """Backend-aware quantum utility measurement"""
    
    # Execution metrics
    queue_time_seconds: float
    execution_time_seconds: float
    total_shots: int
    
    # Quality metrics
    raw_fidelity: float
    mitigated_fidelity: float
    mitigation_benefit: float  # % improvement from mitigation
    
    # Task contribution
    task_speedup: float  # vs classical alternative
    task_quality_improvement: float  # accuracy/quality gain
    utility_score: float  # composite: task_benefit / resource_cost
    
    def is_useful(self) -> bool:
        return self.utility_score > 1.0  # Benefit exceeds cost
```

#### 4.2 Backend-Aware Circuit Optimization
```python
# backend_optimizer.py
class BackendAwareOptimizer:
    """Optimize circuits for specific IBM backends"""
    
    def __init__(self, backend_name: str):
        self.backend = load_backend(backend_name)
        self.noise_model = self._build_noise_model()
        
    def optimize_for_backend(self, circuit: QuantumCircuit) -> OptimizedCircuit:
        """Apply backend-specific optimizations"""
        # Map to native gate set
        # Optimize for connectivity
        # Insert dynamical decoupling if beneficial
        # Choose optimal measurement strategy
        pass
        
    def estimate_utility(self, circuit: QuantumCircuit) -> float:
        """Predict utility before execution"""
        # Use noise model to estimate fidelity
        # Compare to classical alternative
        # Return expected utility score
        pass
```

#### 4.3 Demonstration Experiments
1. **Queue Optimization**: Show reduced queue time through intelligent job batching
2. **Mitigation Benefit**: Demonstrate measurable improvement from error mitigation
3. **Task Contribution**: Show quantum scoring improves routing decisions vs classical
4. **Backend Comparison**: Compare utility across different IBM backends

---

## Phase 5: Closed-Loop Agent Cognition (Week 7-10)

### Objective
Integrate perception, routing, memory, planning, self-evaluation, and adaptation in one recurrent loop.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CLOSED-LOOP AGENT                         │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │ Perception│───▶│  Router  │───▶│  Memory  │              │
│  │  (VAE)   │    │(Tesseract│    │ (Store/  │              │
│  │          │◀───│ / Flat)  │◀───│ Retrieve)│              │
│  └──────────┘    └────┬─────┘    └──────────┘              │
│                       │                                      │
│                       ▼                                      │
│              ┌──────────────┐                               │
│              │   Planning     │                               │
│              │  (Policy Net)  │                               │
│              └──────┬─────────┘                               │
│                     │                                        │
│                     ▼                                        │
│        ┌────────────────────────┐                            │
│        │   Self-Evaluation    │                            │
│        │ (Performance Monitor)│                            │
│        └──────────┬────────────┘                            │
│                   │                                          │
│                   ▼                                          │
│        ┌────────────────────────┐                            │
│        │  Biomimetic Adaptation │                            │
│        │   (Control Update)     │                            │
│        └──────────┬────────────┘                            │
│                   │                                          │
│                   └────────────────▶ (back to Router)       │
└─────────────────────────────────────────────────────────────┘
```

### Deliverables

#### 5.1 Agent Loop Implementation
```python
# agent_loop.py
class HybridCognitiveAgent:
    """Closed-loop hybrid quantum-classical agent"""
    
    def __init__(self):
        self.perception = VAEEncoder()
        self.router = TesseractRouter()  # or FlatRouter
        self.memory = EpisodicMemory()
        self.planner = PolicyController()
        self.evaluator = PerformanceMonitor()
        self.adaptation = BiomimeticAdaptiveController()
        
    def cognitive_cycle(self, observation: Observation) -> Action:
        """One complete cognitive cycle"""
        # 1. Perception: Encode observation
        latent_state = self.perception.encode(observation)
        
        # 2. Memory: Retrieve relevant context
        context = self.memory.retrieve(latent_state)
        
        # 3. Routing: Choose cognitive path
        route = self.router.select_route(latent_state, context)
        
        # 4. Planning: Generate action
        action = self.planner.generate_action(route, context)
        
        # 5. Execution: Act (and observe result)
        result = self.execute(action)
        
        # 6. Memory: Store experience
        self.memory.store(latent_state, action, result)
        
        # 7. Evaluation: Assess performance
        feedback = self.evaluator.assess(observation, action, result)
        
        # 8. Adaptation: Update control parameters
        self.adaptation.adapt(feedback)
        
        return action
```

#### 5.2 Narrow Task Families

**Task Family 1: Structured Reasoning with Memory Switching**
- Multi-step logical reasoning
- Requires switching between working memory and long-term memory
- Success metric: Accuracy vs steps, memory retrieval efficiency

**Task Family 2: Adaptive Scientific Hypothesis Scoring**
- Given experimental data, score competing hypotheses
- Adapt scoring based on new evidence
- Success metric: Correlation with ground truth, adaptation speed

**Task Family 3: Hardware-Aware Experimental Planning**
- Plan sequence of quantum experiments
- Optimize for backend characteristics
- Success metric: Information gain per shot, queue efficiency

#### 5.3 Benchmark Protocol
```python
# benchmark_protocol.py
class NarrowTaskBenchmark:
    """Benchmark hybrid agent on narrow task family"""
    
    def __init__(self, task_family: TaskFamily):
        self.task_family = task_family
        self.classical_baseline = ClassicalAgent()
        self.hybrid_agent = HybridCognitiveAgent()
        
    def run_comparison(self, n_trials: int = 100) -> BenchmarkResult:
        """Compare hybrid vs classical on task family"""
        classical_results = []
        hybrid_results = []
        
        for task in self.task_family.sample(n_trials):
            # Classical baseline
            classical_result = self.classical_baseline.solve(task)
            classical_results.append(classical_result)
            
            # Hybrid agent
            hybrid_result = self.hybrid_agent.solve(task)
            hybrid_results.append(hybrid_result)
            
        return self._analyze_results(classical_results, hybrid_results)
```

---

## Success Criteria

### Phase Success Gates

| Phase | Success Criteria | Metric |
|-------|-----------------|--------|
| 1. Governance | All experiments reproducible | 100% reproducibility score |
| 2. Baseline | Baseline characterized | <5% variance across runs |
| 3. Biomimetic | Emergence demonstrated | Emergence index > 0.5 |
| 4. Quantum Utility | Quantum benefit shown | Utility score > 1.0 on ≥1 task |
| 5. Closed Loop | Hybrid beats classical | Statistically significant (p<0.05) on ≥1 task family |

### Final Milestone

**Demonstrate one hybrid agent loop that outperforms classical-only baseline on a narrow task family.**

Requirements:
- [ ] Reproducible experimental protocol
- [ ] Pre-declared success/failure criteria
- [ ] Statistical significance (p < 0.05)
- [ ] No hidden regressions (all metrics bounded)
- [ ] Full provenance and governance trail

---

## Implementation Schedule

| Week | Focus | Key Deliverable |
|------|-------|---------------|
| 1-2 | Governance Lock | Typed metrics registry, experiment registration |
| 2-3 | Baseline Lock | Baseline characterization, acceptance criteria |
| 3-5 | Biomimetic Control | Adaptive control layer, emergence demonstration |
| 5-7 | Quantum Utility | Backend-aware optimization, utility metrics |
| 7-10 | Closed Loop | Integrated agent, narrow task benchmarks |
| 10+ | Validation | Full benchmark suite, scientific documentation |

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Tesseract never beats baseline | Keep flat as default; tesseract remains experimental |
| Quantum utility not demonstrable | Focus on classical biomimetic advantages first |
| Biomimetic emergence not shown | Use simpler adaptive control; revisit emergence later |
| Integration complexity | Build incrementally; validate each module independently |
| Backend instability | Design backend-agnostic interfaces; test on multiple backends |

---

## Documentation Requirements

Every phase must produce:
1. **Technical Specification**: Architecture, interfaces, data flows
2. **Benchmark Protocol**: Pre-declared criteria, statistical tests, success/failure thresholds
3. **Experimental Results**: Raw data, analysis, conclusions
4. **Governance Report**: Provenance, reproducibility, limitations
5. **Next Phase Gate**: Go/no-go decision with justification

---

## Conclusion

This roadmap provides a **scientifically defensible path** to QAGI by:
- Prioritizing governance and reproducibility
- Maintaining rigorous baselines
- Demonstrating measurable improvements
- Avoiding premature AGI claims

The immediate next step is **Phase 1: Governance Layer Lock** - establishing the infrastructure for typed, bounded, reproducible experiments.

---

*Document Version: 1.0*
*Last Updated: April 18, 2026*
*Status: Draft - Pending Review*
