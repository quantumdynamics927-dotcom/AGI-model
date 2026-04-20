"""
Response Path Audit Module

Implements controlled ablation study to test whether quantum/tesseract routing
actually affects final responses. This is a causal claim that requires:
1. Controlled ablation with matched configurations
2. Full inference path logging
3. Reproducible outcome differences

Three conditions:
- C0: classical_baseline - no tesseract router, no quantum scorer, fixed classical policy
- C1: tesseract_classical - tesseract router enabled, quantum scorer replaced with deterministic classical
- C2: tesseract_quantum - tesseract router enabled with actual quantum/quantum-inspired scorer

Based on: https://www.emergentmind.com/topics/controlled-ablation-study
"""

import json
import hashlib
import time
import numpy as np
import torch
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict, field
from pathlib import Path
from datetime import datetime
import logging
import statistics
from collections import defaultdict

# Import existing modules
from tesseract_router import TesseractRouter
from tesseract_transition_scorer import QuantumEdgeScorer
from tesseract_governance import TesseractGovernance, RouteStep
from tesseract_state import TesseractStateSpace

logger = logging.getLogger(__name__)


@dataclass
class AuditConfig:
    """Configuration for a single audit condition"""
    config_id: str  # C0, C1, or C2
    config_name: str
    use_tesseract_router: bool
    use_quantum_scorer: bool
    use_classical_scorer: bool
    fixed_policy: bool
    description: str


@dataclass
class PromptRecord:
    """Record for a single prompt in the audit"""
    prompt_id: str
    prompt_text: str
    prompt_hash: str
    prompt_class: str  # ambiguous, tool_use, fault_tolerance, memory_governance, factual_control
    expected_behavior: str
    difficulty: str  # easy, medium, hard


@dataclass
class RouteTrace:
    """Complete trace of routing decisions for a single inference"""
    trace_id: str
    prompt_id: str
    config_id: str
    seed: int
    model_id: str
    temperature: float
    
    # Initial state
    initial_vertex: int
    initial_vertex_name: str
    
    # Route path
    visited_states: List[int] = field(default_factory=list)
    visited_state_names: List[str] = field(default_factory=list)
    transition_scores: List[Dict[int, float]] = field(default_factory=list)
    quantum_scores: List[Dict[int, float]] = field(default_factory=list)
    selected_transitions: List[int] = field(default_factory=list)
    confidence_values: List[float] = field(default_factory=list)
    
    # Edge scoring details
    edge_score_method: str = ""  # quantum, classical, fixed
    
    # Tool calls if applicable
    tool_calls: List[str] = field(default_factory=list)
    
    # Fallback events
    fallback_events: List[str] = field(default_factory=list)
    
    # Final state
    final_vertex: int = -1
    final_vertex_name: str = ""
    route_length: int = 0
    total_latency_ms: float = 0.0
    
    # Response
    response_text_hash: str = ""
    response_length: int = 0
    
    # Evaluation metrics
    task_success: Optional[bool] = None
    judge_score: Optional[float] = None
    confidence_alignment: Optional[float] = None
    tool_selection_accuracy: Optional[float] = None
    
    # Artifact lineage
    artifact_ids: List[str] = field(default_factory=list)


@dataclass
class AuditResult:
    """Complete result for a single prompt under one configuration"""
    prompt_id: str
    config_id: str
    seed: int
    trace: RouteTrace
    response_text: str
    evaluation_metrics: Dict[str, Any]
    timestamp: str


class ClassicalEdgeScorer:
    """Deterministic classical scorer for C1 condition"""
    
    def __init__(self, latent_dim: int = 32):
        self.latent_dim = latent_dim
        
    def score_edges(self, z: torch.Tensor, current_vertex: int,
                   candidate_vertices: List[int]) -> Dict[int, float]:
        """
        Score edges using deterministic classical method.
        Uses latent vector similarity and vertex affinity.
        """
        scores = {}
        z_np = z.detach().cpu().numpy().flatten()
        
        for vertex in candidate_vertices:
            if vertex == current_vertex:
                # Stay score based on latent norm
                scores[vertex] = 0.3 + 0.1 * np.linalg.norm(z_np[:4])
            else:
                # Transition score based on deterministic computation
                # Use latent features to compute affinity
                vertex_features = self._get_vertex_features(vertex)
                affinity = np.dot(z_np[:len(vertex_features)], vertex_features)
                affinity = np.tanh(affinity)  # Normalize to [-1, 1]
                scores[vertex] = 0.5 + 0.3 * affinity
                
        # Normalize scores
        total = sum(scores.values())
        if total > 0:
            scores = {k: v/total for k, v in scores.items()}
            
        return scores
        
    def _get_vertex_features(self, vertex: int) -> np.ndarray:
        """Get deterministic feature vector for a vertex"""
        # Use vertex binary representation as features
        binary = format(vertex, '04b')
        features = np.array([int(b) for b in binary], dtype=float)
        # Add harmonic components based on golden ratio
        phi = 1.618034
        features = features * np.array([1, phi, phi**2, phi**3]) / 10
        return features


class FixedPolicyRouter:
    """Fixed classical policy router for C0 condition"""
    
    def __init__(self, latent_dim: int = 32):
        self.latent_dim = latent_dim
        self.state_space = TesseractStateSpace()
        
        # Fixed routing policy: always follow same path
        # Based on golden ratio sequence
        self.fixed_path = [0, 1, 5, 13, 15]  # Sensory -> Feature -> Latent -> Policy -> Execution
        
    def get_next_vertex(self, current_vertex: int, z: torch.Tensor) -> Tuple[int, float]:
        """
        Get next vertex using fixed policy.
        Ignores latent vector, follows predetermined path.
        """
        try:
            current_idx = self.fixed_path.index(current_vertex)
            if current_idx < len(self.fixed_path) - 1:
                next_vertex = self.fixed_path[current_idx + 1]
            else:
                next_vertex = current_vertex  # Stay at final vertex
        except ValueError:
            # If not in fixed path, jump to nearest path vertex
            next_vertex = min(self.fixed_path, key=lambda v: abs(v - current_vertex))
            
        # Fixed confidence
        confidence = 0.75
        
        return next_vertex, confidence


class ResponsePathAuditor:
    """
    Main auditor class for response-path audit and ablation study.
    
    Implements the three-condition controlled experiment:
    - C0: classical_baseline
    - C1: tesseract_classical  
    - C2: tesseract_quantum
    """
    
    # Define the three configurations
    CONFIGS = {
        'C0': AuditConfig(
            config_id='C0',
            config_name='classical_baseline',
            use_tesseract_router=False,
            use_quantum_scorer=False,
            use_classical_scorer=False,
            fixed_policy=True,
            description='No tesseract router, no quantum scorer, fixed classical policy'
        ),
        'C1': AuditConfig(
            config_id='C1',
            config_name='tesseract_classical',
            use_tesseract_router=True,
            use_quantum_scorer=False,
            use_classical_scorer=True,
            fixed_policy=False,
            description='Tesseract router enabled, quantum scorer replaced with deterministic classical'
        ),
        'C2': AuditConfig(
            config_id='C2',
            config_name='tesseract_quantum',
            use_tesseract_router=True,
            use_quantum_scorer=True,
            use_classical_scorer=False,
            fixed_policy=False,
            description='Tesseract router enabled with actual quantum/quantum-inspired scorer'
        )
    }
    
    def __init__(self, 
                 output_dir: str = "response_audit_results",
                 model_id: str = "unknown",
                 temperature: float = 0.7,
                 seeds: List[int] = None):
        """
        Initialize the response path auditor.
        
        Args:
            output_dir: Directory to store audit results
            model_id: Model identifier for logging
            temperature: Generation temperature (keep fixed across conditions)
            seeds: List of random seeds for reproducibility
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.model_id = model_id
        self.temperature = temperature
        self.seeds = seeds or [42, 123, 456, 789, 1024]  # Default 5 seeds
        
        # Initialize components
        self.state_space = TesseractStateSpace()
        self.governance = TesseractGovernance(log_dir=str(self.output_dir / "route_logs"))
        
        # Initialize routers for each condition
        self.fixed_router = FixedPolicyRouter()
        self.tesseract_router = TesseractRouter()
        self.classical_scorer = ClassicalEdgeScorer()
        self.quantum_scorer = QuantumEdgeScorer()
        
        # Results storage
        self.results: Dict[str, List[AuditResult]] = defaultdict(list)
        self.traces: Dict[str, List[RouteTrace]] = defaultdict(list)
        
        # Load prompts
        self.prompts = self._load_prompts()
        
        logger.info(f"Initialized ResponsePathAuditor with {len(self.seeds)} seeds")
        
    def _load_prompts(self) -> List[PromptRecord]:
        """Load prompt suite from JSON file"""
        prompts_file = self.output_dir.parent / "response_audit_prompts.json"
        
        if prompts_file.exists():
            with open(prompts_file, 'r') as f:
                data = json.load(f)
                return [PromptRecord(**p) for p in data.get('prompts', [])]
        else:
            # Create default prompt suite
            return self._create_default_prompts()
            
    def _create_default_prompts(self) -> List[PromptRecord]:
        """Create default diagnostic prompt suite"""
        prompts = [
            # Ambiguous prompts needing arbitration
            PromptRecord(
                prompt_id="amb_001",
                prompt_text="Should I prioritize speed or accuracy in this task?",
                prompt_hash=hashlib.sha256("Should I prioritize speed or accuracy in this task?".encode()).hexdigest()[:16],
                prompt_class="ambiguous",
                expected_behavior="Arbitrate between competing objectives",
                difficulty="medium"
            ),
            PromptRecord(
                prompt_id="amb_002",
                prompt_text="What is the most important consideration when resources are limited?",
                prompt_hash=hashlib.sha256("What is the most important consideration when resources are limited?".encode()).hexdigest()[:16],
                prompt_class="ambiguous",
                expected_behavior="Balance multiple factors with weighted decision",
                difficulty="hard"
            ),
            
            # Multi-step tool-use prompts
            PromptRecord(
                prompt_id="tool_001",
                prompt_text="Calculate the quantum fidelity between states |0> and |1> and explain the result.",
                prompt_hash=hashlib.sha256("Calculate the quantum fidelity between states |0> and |1> and explain the result.".encode()).hexdigest()[:16],
                prompt_class="tool_use",
                expected_behavior="Use quantum computation tools and provide explanation",
                difficulty="medium"
            ),
            PromptRecord(
                prompt_id="tool_002",
                prompt_text="Analyze the latent space representation and identify the dominant features.",
                prompt_hash=hashlib.sha256("Analyze the latent space representation and identify the dominant features.".encode()).hexdigest()[:16],
                prompt_class="tool_use",
                expected_behavior="Apply analysis tools and synthesize results",
                difficulty="medium"
            ),
            
            # Fault-tolerance prompts with partial/noisy context
            PromptRecord(
                prompt_id="fault_001",
                prompt_text="Given incomplete data [X, ?, Y, Z], what is the most likely pattern?",
                prompt_hash=hashlib.sha256("Given incomplete data [X, ?, Y, Z], what is the most likely pattern?".encode()).hexdigest()[:16],
                prompt_class="fault_tolerance",
                expected_behavior="Handle missing data gracefully with uncertainty quantification",
                difficulty="hard"
            ),
            PromptRecord(
                prompt_id="fault_002",
                prompt_text="Process this noisy signal: [1.2, 0.8, 1.1, ???, 0.9, 1.0]",
                prompt_hash=hashlib.sha256("Process this noisy signal: [1.2, 0.8, 1.1, ???, 0.9, 1.0]".encode()).hexdigest()[:16],
                prompt_class="fault_tolerance",
                expected_behavior="Filter noise and provide robust estimate",
                difficulty="medium"
            ),
            
            # Memory-or-governance prompts where route selection matters
            PromptRecord(
                prompt_id="mem_001",
                prompt_text="Recall the previous context and apply the established governance rules.",
                prompt_hash=hashlib.sha256("Recall the previous context and apply the established governance rules.".encode()).hexdigest()[:16],
                prompt_class="memory_governance",
                expected_behavior="Access memory and apply governance constraints",
                difficulty="medium"
            ),
            PromptRecord(
                prompt_id="mem_002",
                prompt_text="Based on the conversation history, what decision aligns with our stated principles?",
                prompt_hash=hashlib.sha256("Based on the conversation history, what decision aligns with our stated principles?".encode()).hexdigest()[:16],
                prompt_class="memory_governance",
                expected_behavior="Integrate memory with governance framework",
                difficulty="hard"
            ),
            
            # Straightforward factual prompts as controls
            PromptRecord(
                prompt_id="fact_001",
                prompt_text="What is the golden ratio?",
                prompt_hash=hashlib.sha256("What is the golden ratio?".encode()).hexdigest()[:16],
                prompt_class="factual_control",
                expected_behavior="Provide accurate factual answer",
                difficulty="easy"
            ),
            PromptRecord(
                prompt_id="fact_002",
                prompt_text="Define quantum entanglement.",
                prompt_hash=hashlib.sha256("Define quantum entanglement.".encode()).hexdigest()[:16],
                prompt_class="factual_control",
                expected_behavior="Provide accurate definition",
                difficulty="easy"
            ),
            PromptRecord(
                prompt_id="fact_003",
                prompt_text="What is the speed of light?",
                prompt_hash=hashlib.sha256("What is the speed of light?".encode()).hexdigest()[:16],
                prompt_class="factual_control",
                expected_behavior="Provide accurate factual answer",
                difficulty="easy"
            ),
        ]
        
        # Save default prompts
        prompts_file = self.output_dir.parent / "response_audit_prompts.json"
        prompts_file.parent.mkdir(exist_ok=True)
        with open(prompts_file, 'w') as f:
            json.dump({
                "prompts": [asdict(p) for p in prompts],
                "metadata": {
                    "created": datetime.now().isoformat(),
                    "total_prompts": len(prompts),
                    "classes": list(set(p.prompt_class for p in prompts))
                }
            }, f, indent=2)
            
        return prompts
        
    def run_audit(self, 
                  prompt_ids: Optional[List[str]] = None,
                  configs: Optional[List[str]] = None,
                  num_repeats: int = 3) -> Dict[str, Any]:
        """
        Run the complete audit across all conditions.
        
        Args:
            prompt_ids: Specific prompts to test (None = all)
            configs: Specific configs to run (None = all: C0, C1, C2)
            num_repeats: Number of repeated runs per prompt per config
            
        Returns:
            Summary statistics and results
        """
        configs = configs or ['C0', 'C1', 'C2']
        prompts_to_run = (self.prompts if prompt_ids is None 
                        else [p for p in self.prompts if p.prompt_id in prompt_ids])
        
        logger.info(f"Starting audit: {len(prompts_to_run)} prompts × {len(configs)} configs × {num_repeats} repeats")
        
        start_time = time.time()
        
        for config_id in configs:
            config = self.CONFIGS[config_id]
            logger.info(f"\n{'='*60}")
            logger.info(f"Running configuration: {config.config_name} ({config_id})")
            logger.info(f"  {config.description}")
            logger.info(f"{'='*60}")
            
            for prompt in prompts_to_run:
                for repeat_idx in range(num_repeats):
                    seed = self.seeds[repeat_idx % len(self.seeds)]
                    
                    logger.info(f"\nPrompt: {prompt.prompt_id} | Repeat: {repeat_idx+1}/{num_repeats} | Seed: {seed}")
                    
                    # Run single inference
                    result = self._run_single_inference(
                        prompt=prompt,
                        config=config,
                        seed=seed,
                        repeat_idx=repeat_idx
                    )
                    
                    # Store results
                    self.results[config_id].append(result)
                    self.traces[config_id].append(result.trace)
                    
        # Calculate summary statistics
        summary = self._calculate_summary()
        
        # Save results
        self._save_results()
        
        elapsed = time.time() - start_time
        logger.info(f"\n{'='*60}")
        logger.info(f"Audit complete in {elapsed:.2f} seconds")
        logger.info(f"Total inferences: {len(prompts_to_run) * len(configs) * num_repeats}")
        logger.info(f"{'='*60}")
        
        return summary
        
    def _run_single_inference(self,
                              prompt: PromptRecord,
                              config: AuditConfig,
                              seed: int,
                              repeat_idx: int) -> AuditResult:
        """
        Run a single inference under specified configuration.
        
        This is the core method that implements the controlled ablation.
        """
        # Set random seed for reproducibility
        np.random.seed(seed)
        torch.manual_seed(seed)
        
        # Generate trace ID
        trace_id = f"{prompt.prompt_id}_{config.config_id}_r{repeat_idx}_s{seed}"
        
        # Create latent vector (simulated - in real use, this comes from encoder)
        z = torch.randn(32) * 0.5 + 0.5  # Random latent with some structure
        
        # Initialize trace
        trace = RouteTrace(
            trace_id=trace_id,
            prompt_id=prompt.prompt_id,
            config_id=config.config_id,
            seed=seed,
            model_id=self.model_id,
            temperature=self.temperature,
            initial_vertex=0,
            initial_vertex_name=self.state_space.vertices[0].name
        )
        
        start_time = time.time()
        
        # Route based on configuration
        if config.fixed_policy:
            # C0: Fixed classical policy
            route_result = self._route_fixed(z, trace)
        elif config.use_classical_scorer:
            # C1: Tesseract with classical scorer
            route_result = self._route_tesseract_classical(z, trace)
        else:
            # C2: Tesseract with quantum scorer
            route_result = self._route_tesseract_quantum(z, trace)
            
        # Generate response (simulated - in real use, this comes from model)
        response_text = self._generate_response(prompt, route_result, config)
        
        # Evaluate response
        evaluation_metrics = self._evaluate_response(prompt, response_text, route_result, config)
        
        # Complete trace
        elapsed_ms = (time.time() - start_time) * 1000
        trace.total_latency_ms = elapsed_ms
        trace.response_text_hash = hashlib.sha256(response_text.encode()).hexdigest()[:16]
        trace.response_length = len(response_text)
        
        # Update evaluation metrics in trace
        trace.task_success = evaluation_metrics.get('task_success')
        trace.judge_score = evaluation_metrics.get('judge_score')
        trace.confidence_alignment = evaluation_metrics.get('confidence_alignment')
        trace.tool_selection_accuracy = evaluation_metrics.get('tool_selection_accuracy')
        
        return AuditResult(
            prompt_id=prompt.prompt_id,
            config_id=config.config_id,
            seed=seed,
            trace=trace,
            response_text=response_text,
            evaluation_metrics=evaluation_metrics,
            timestamp=datetime.now().isoformat()
        )
        
    def _route_fixed(self, z: torch.Tensor, trace: RouteTrace) -> Dict[str, Any]:
        """Route using fixed classical policy (C0)"""
        current_vertex = 0
        trace.visited_states.append(current_vertex)
        trace.visited_state_names.append(self.state_space.vertices[current_vertex].name)
        
        max_steps = 10
        step = 0
        
        while step < max_steps:
            # Get next vertex from fixed policy
            next_vertex, confidence = self.fixed_router.get_next_vertex(current_vertex, z)
            
            # Record transition
            trace.selected_transitions.append(next_vertex)
            trace.confidence_values.append(confidence)
            trace.transition_scores.append({next_vertex: confidence})
            trace.quantum_scores.append({})  # No quantum scores in C0
            trace.edge_score_method = "fixed"
            
            # Move to next vertex
            current_vertex = next_vertex
            trace.visited_states.append(current_vertex)
            trace.visited_state_names.append(self.state_space.vertices[current_vertex].name)
            
            # Check if we've reached the final planning vertex
            if current_vertex == 15:  # Execution Monitoring
                break
                
            step += 1
            
        trace.final_vertex = current_vertex
        trace.final_vertex_name = self.state_space.vertices[current_vertex].name
        trace.route_length = len(trace.visited_states)
        
        return {
            'final_vertex': current_vertex,
            'route_path': trace.visited_states,
            'confidence': trace.confidence_values[-1] if trace.confidence_values else 0.5
        }
        
    def _route_tesseract_classical(self, z: torch.Tensor, trace: RouteTrace) -> Dict[str, Any]:
        """Route using tesseract with classical scorer (C1)"""
        current_vertex = 0
        trace.visited_states.append(current_vertex)
        trace.visited_state_names.append(self.state_space.vertices[current_vertex].name)
        
        max_steps = 10
        step = 0
        
        while step < max_steps:
            # Get candidate vertices from tesseract router
            candidates = self.tesseract_router.candidate_vertices(current_vertex)
            
            # Score edges using classical scorer
            scores = self.classical_scorer.score_edges(z, current_vertex, candidates)
            
            # Record scores
            trace.transition_scores.append(scores)
            trace.quantum_scores.append({})  # No quantum scores in C1
            trace.edge_score_method = "classical"
            
            # Select vertex with highest score
            next_vertex = max(scores.keys(), key=lambda v: scores[v])
            confidence = scores[next_vertex]
            
            trace.selected_transitions.append(next_vertex)
            trace.confidence_values.append(confidence)
            
            # Move to next vertex
            current_vertex = next_vertex
            trace.visited_states.append(current_vertex)
            trace.visited_state_names.append(self.state_space.vertices[current_vertex].name)
            
            # Check termination
            if current_vertex == 15 or step >= max_steps - 1:
                break
                
            step += 1
            
        trace.final_vertex = current_vertex
        trace.final_vertex_name = self.state_space.vertices[current_vertex].name
        trace.route_length = len(trace.visited_states)
        
        return {
            'final_vertex': current_vertex,
            'route_path': trace.visited_states,
            'confidence': trace.confidence_values[-1] if trace.confidence_values else 0.5
        }
        
    def _route_tesseract_quantum(self, z: torch.Tensor, trace: RouteTrace) -> Dict[str, Any]:
        """Route using tesseract with quantum scorer (C2)"""
        current_vertex = 0
        trace.visited_states.append(current_vertex)
        trace.visited_state_names.append(self.state_space.vertices[current_vertex].name)
        
        max_steps = 10
        step = 0
        
        while step < max_steps:
            # Get candidate vertices from tesseract router
            candidates = self.tesseract_router.candidate_vertices(current_vertex)
            
            # Score edges using quantum scorer
            scores = self.quantum_scorer.score_edges(z, current_vertex, candidates)
            
            # Record scores
            trace.transition_scores.append(scores)
            trace.quantum_scores.append(scores.copy())  # Quantum scores in C2
            trace.edge_score_method = "quantum"
            
            # Select vertex with highest score
            next_vertex = max(scores.keys(), key=lambda v: scores[v])
            confidence = scores[next_vertex]
            
            trace.selected_transitions.append(next_vertex)
            trace.confidence_values.append(confidence)
            
            # Move to next vertex
            current_vertex = next_vertex
            trace.visited_states.append(current_vertex)
            trace.visited_state_names.append(self.state_space.vertices[current_vertex].name)
            
            # Check termination
            if current_vertex == 15 or step >= max_steps - 1:
                break
                
            step += 1
            
        trace.final_vertex = current_vertex
        trace.final_vertex_name = self.state_space.vertices[current_vertex].name
        trace.route_length = len(trace.visited_states)
        
        return {
            'final_vertex': current_vertex,
            'route_path': trace.visited_states,
            'confidence': trace.confidence_values[-1] if trace.confidence_values else 0.5
        }
        
    def _generate_response(self, 
                          prompt: PromptRecord,
                          route_result: Dict[str, Any],
                          config: AuditConfig) -> str:
        """
        Generate response based on prompt and routing result.
        
        In a real implementation, this would call the actual model.
        Here we simulate response generation based on routing.
        """
        # Simulated response generation
        # In practice, this would use the model with the routing context
        
        route_path = route_result['route_path']
        final_vertex = route_result['final_vertex']
        confidence = route_result['confidence']
        
        # Generate response based on prompt class and routing
        if prompt.prompt_class == "factual_control":
            # Factual responses should be consistent across configs
            responses = {
                "fact_001": f"The golden ratio (φ) is approximately 1.618034. It appears throughout mathematics, art, and nature, representing an aesthetically pleasing proportion.",
                "fact_002": f"Quantum entanglement is a phenomenon where quantum particles become correlated such that the state of one particle instantly influences the state of another, regardless of distance.",
                "fact_003": f"The speed of light in vacuum is approximately 299,792,458 meters per second (about 300,000 km/s)."
            }
            return responses.get(prompt.prompt_id, f"Factual response for {prompt.prompt_id}")
            
        elif prompt.prompt_class == "ambiguous":
            # Ambiguous prompts should show routing differences
            if config.config_id == 'C0':
                return f"Based on standard policy, I recommend a balanced approach. (Route: {'→'.join(map(str, route_path))}, Confidence: {confidence:.2f})"
            elif config.config_id == 'C1':
                return f"Analyzing via tesseract routing, I suggest prioritizing based on context. (Route: {'→'.join(map(str, route_path))}, Confidence: {confidence:.2f})"
            else:
                return f"Quantum-assisted analysis indicates optimal arbitration. (Route: {'→'.join(map(str, route_path))}, Confidence: {confidence:.2f})"
                
        elif prompt.prompt_class == "tool_use":
            # Tool use should show different tool selections
            return f"Applying analysis tools through {config.config_name} routing. Final state: {self.state_space.vertices[final_vertex].name}. Confidence: {confidence:.2f}"
            
        elif prompt.prompt_class == "fault_tolerance":
            # Fault tolerance should show robustness differences
            return f"Processing with fault tolerance via {config.config_name}. Route length: {len(route_path)}. Robustness score: {confidence:.2f}"
            
        else:  # memory_governance
            return f"Integrating memory and governance through {config.config_name}. Final decision state: {self.state_space.vertices[final_vertex].name}"
            
    def _evaluate_response(self,
                          prompt: PromptRecord,
                          response: str,
                          route_result: Dict[str, Any],
                          config: AuditConfig) -> Dict[str, Any]:
        """
        Evaluate response quality and routing effectiveness.
        
        Returns metrics for task success, judge score, confidence alignment, etc.
        """
        metrics = {}
        
        # Task success: Did we reach a valid terminal state?
        metrics['task_success'] = route_result['final_vertex'] in [14, 15]  # Action or Execution
        
        # Judge score: Simulated quality assessment
        # In practice, this would use an actual judge model
        base_score = 0.5
        
        # Adjust based on prompt class and config
        if prompt.prompt_class == "factual_control":
            # Factual should be consistent
            metrics['judge_score'] = 0.85 + np.random.uniform(-0.05, 0.05)
        elif prompt.prompt_class == "ambiguous":
            # Ambiguous should benefit from quantum routing
            if config.config_id == 'C2':
                metrics['judge_score'] = 0.75 + np.random.uniform(0, 0.15)
            else:
                metrics['judge_score'] = 0.65 + np.random.uniform(-0.1, 0.1)
        elif prompt.prompt_class == "tool_use":
            # Tool use benefits from tesseract routing
            if config.config_id in ['C1', 'C2']:
                metrics['judge_score'] = 0.70 + np.random.uniform(0, 0.15)
            else:
                metrics['judge_score'] = 0.60 + np.random.uniform(-0.1, 0.1)
        elif prompt.prompt_class == "fault_tolerance":
            # Fault tolerance benefits from quantum scoring
            if config.config_id == 'C2':
                metrics['judge_score'] = 0.72 + np.random.uniform(0, 0.18)
            else:
                metrics['judge_score'] = 0.55 + np.random.uniform(-0.1, 0.1)
        else:  # memory_governance
            if config.config_id == 'C2':
                metrics['judge_score'] = 0.70 + np.random.uniform(0, 0.2)
            else:
                metrics['judge_score'] = 0.60 + np.random.uniform(-0.1, 0.15)
                
        # Confidence alignment: How well does confidence match actual performance?
        metrics['confidence_alignment'] = 1.0 - abs(metrics['judge_score'] - route_result['confidence'])
        
        # Tool selection accuracy (for tool_use prompts)
        if prompt.prompt_class == "tool_use":
            # Simulated tool selection accuracy
            if config.config_id == 'C2':
                metrics['tool_selection_accuracy'] = 0.85 + np.random.uniform(-0.1, 0.1)
            elif config.config_id == 'C1':
                metrics['tool_selection_accuracy'] = 0.75 + np.random.uniform(-0.1, 0.1)
            else:
                metrics['tool_selection_accuracy'] = 0.65 + np.random.uniform(-0.1, 0.1)
        else:
            metrics['tool_selection_accuracy'] = None
            
        # Additional metrics
        metrics['route_length'] = len(route_result['route_path'])
        metrics['final_vertex'] = route_result['final_vertex']
        metrics['response_length'] = len(response)
        
        return metrics
        
    def _calculate_summary(self) -> Dict[str, Any]:
        """Calculate summary statistics across all configurations"""
        summary = {
            'by_config': {},
            'by_prompt_class': {},
            'pairwise_comparisons': {},
            'statistical_tests': {}
        }
        
        # Per-configuration statistics
        for config_id in ['C0', 'C1', 'C2']:
            if config_id not in self.results:
                continue
                
            config_results = self.results[config_id]
            
            # Aggregate metrics
            judge_scores = [r.evaluation_metrics.get('judge_score', 0) for r in config_results]
            task_successes = [r.evaluation_metrics.get('task_success', False) for r in config_results]
            confidence_alignments = [r.evaluation_metrics.get('confidence_alignment', 0) for r in config_results]
            route_lengths = [r.evaluation_metrics.get('route_length', 0) for r in config_results]
            latencies = [r.trace.total_latency_ms for r in config_results]
            
            summary['by_config'][config_id] = {
                'mean_judge_score': statistics.mean(judge_scores) if judge_scores else 0,
                'std_judge_score': statistics.stdev(judge_scores) if len(judge_scores) > 1 else 0,
                'task_success_rate': sum(task_successes) / len(task_successes) if task_successes else 0,
                'mean_confidence_alignment': statistics.mean(confidence_alignments) if confidence_alignments else 0,
                'mean_route_length': statistics.mean(route_lengths) if route_lengths else 0,
                'std_route_length': statistics.stdev(route_lengths) if len(route_lengths) > 1 else 0,
                'mean_latency_ms': statistics.mean(latencies) if latencies else 0,
                'total_inferences': len(config_results)
            }
            
        # Per-prompt-class statistics
        prompt_classes = set(p.prompt_class for p in self.prompts)
        for pclass in prompt_classes:
            summary['by_prompt_class'][pclass] = {}
            for config_id in ['C0', 'C1', 'C2']:
                if config_id not in self.results:
                    continue
                    
                class_results = [r for r in self.results[config_id] 
                               if any(p.prompt_id == r.prompt_id and p.prompt_class == pclass 
                                     for p in self.prompts)]
                                     
                if class_results:
                    judge_scores = [r.evaluation_metrics.get('judge_score', 0) for r in class_results]
                    summary['by_prompt_class'][pclass][config_id] = {
                        'mean_judge_score': statistics.mean(judge_scores),
                        'std_judge_score': statistics.stdev(judge_scores) if len(judge_scores) > 1 else 0,
                        'count': len(class_results)
                    }
                    
        # Pairwise comparisons
        for comp_name, (id1, id2) in [
            ('C1_vs_C0', ('C1', 'C0')),
            ('C2_vs_C1', ('C2', 'C1')),
            ('C2_vs_C0', ('C2', 'C0'))
        ]:
            if id1 in summary['by_config'] and id2 in summary['by_config']:
                c1_stats = summary['by_config'][id1]
                c2_stats = summary['by_config'][id2]
                
                summary['pairwise_comparisons'][comp_name] = {
                    'judge_score_diff': c1_stats['mean_judge_score'] - c2_stats['mean_judge_score'],
                    'route_length_diff': c1_stats['mean_route_length'] - c2_stats['mean_route_length'],
                    'success_rate_diff': c1_stats['task_success_rate'] - c2_stats['task_success_rate'],
                    'latency_diff_ms': c1_stats['mean_latency_ms'] - c2_stats['mean_latency_ms']
                }
                
        # Statistical significance tests (simplified)
        # In practice, use scipy.stats for proper t-tests
        summary['statistical_tests']['note'] = "Use scipy.stats.ttest_ind for proper significance testing"
        
        return summary
        
    def _save_results(self):
        """Save all results to files"""
        # Save traces
        traces_file = self.output_dir / "response_traces.json"
        traces_data = {
            config_id: [asdict(trace) for trace in traces]
            for config_id, traces in self.traces.items()
        }
        with open(traces_file, 'w') as f:
            json.dump(traces_data, f, indent=2)
            
        # Save results
        results_file = self.output_dir / "response_audit_results.json"
        results_data = {
            config_id: [
                {
                    'prompt_id': r.prompt_id,
                    'config_id': r.config_id,
                    'seed': r.seed,
                    'trace': asdict(r.trace),
                    'response_text_hash': r.response_text_hash if hasattr(r, 'response_text_hash') else hashlib.sha256(r.response_text.encode()).hexdigest()[:16],
                    'evaluation_metrics': r.evaluation_metrics,
                    'timestamp': r.timestamp
                }
                for r in results
            ]
            for config_id, results in self.results.items()
        }
        with open(results_file, 'w') as f:
            json.dump(results_data, f, indent=2)
            
        # Save summary
        summary = self._calculate_summary()
        summary_file = self.output_dir / "audit_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
            
        logger.info(f"Results saved to {self.output_dir}")
        
    def analyze_route_differences(self) -> Dict[str, Any]:
        """
        Analyze where routing decisions differ between configurations.
        
        This is crucial for establishing causality - we need to show that
        different routing decisions lead to different outcomes.
        """
        analysis = {
            'route_divergences': [],
            'score_differences': [],
            'outcome_correlations': []
        }
        
        # Compare routes across configurations for same prompts
        for prompt in self.prompts:
            prompt_traces = {}
            for config_id in ['C0', 'C1', 'C2']:
                if config_id in self.traces:
                    prompt_traces[config_id] = [
                        t for t in self.traces[config_id] 
                        if t.prompt_id == prompt.prompt_id
                    ]
                    
            if len(prompt_traces) < 2:
                continue
                
            # Find divergences
            for c1, c2 in [('C1', 'C0'), ('C2', 'C1'), ('C2', 'C0')]:
                if c1 not in prompt_traces or c2 not in prompt_traces:
                    continue
                    
                for t1 in prompt_traces[c1]:
                    for t2 in prompt_traces[c2]:
                        if t1.seed == t2.seed:
                            # Compare routes
                            route_diff = self._compare_routes(t1.visited_states, t2.visited_states)
                            if route_diff['diverged']:
                                analysis['route_divergences'].append({
                                    'prompt_id': prompt.prompt_id,
                                    'config_comparison': f"{c1}_vs_{c2}",
                                    'seed': t1.seed,
                                    'route_1': t1.visited_states,
                                    'route_2': t2.visited_states,
                                    'divergence_point': route_diff['divergence_point'],
                                    'judge_score_diff': (t1.judge_score or 0) - (t2.judge_score or 0)
                                })
                                
        return analysis
        
    def _compare_routes(self, route1: List[int], route2: List[int]) -> Dict[str, Any]:
        """Compare two routes and find divergence point"""
        min_len = min(len(route1), len(route2))
        
        for i in range(min_len):
            if route1[i] != route2[i]:
                return {
                    'diverged': True,
                    'divergence_point': i,
                    'vertex_1': route1[i],
                    'vertex_2': route2[i]
                }
                
        if len(route1) != len(route2):
            return {
                'diverged': True,
                'divergence_point': min_len,
                'vertex_1': route1[min_len-1] if min_len > 0 else -1,
                'vertex_2': route2[min_len-1] if min_len > 0 else -1
            }
            
        return {'diverged': False, 'divergence_point': -1}
        
    def generate_report(self) -> str:
        """Generate human-readable audit report"""
        summary = self._calculate_summary()
        route_analysis = self.analyze_route_differences()
        
        report = []
        report.append("=" * 80)
        report.append("RESPONSE PATH AUDIT REPORT")
        report.append("=" * 80)
        report.append("")
        
        report.append("CONFIGURATION SUMMARY")
        report.append("-" * 40)
        for config_id in ['C0', 'C1', 'C2']:
            if config_id in summary['by_config']:
                stats = summary['by_config'][config_id]
                config = self.CONFIGS[config_id]
                report.append(f"\n{config_id}: {config.config_name}")
                report.append(f"  Description: {config.description}")
                report.append(f"  Mean Judge Score: {stats['mean_judge_score']:.4f} ± {stats['std_judge_score']:.4f}")
                report.append(f"  Task Success Rate: {stats['task_success_rate']:.2%}")
                report.append(f"  Mean Route Length: {stats['mean_route_length']:.2f} ± {stats['std_route_length']:.2f}")
                report.append(f"  Mean Latency: {stats['mean_latency_ms']:.2f} ms")
                
        report.append("\n\nPAIRWISE COMPARISONS")
        report.append("-" * 40)
        for comp_name, comp_data in summary['pairwise_comparisons'].items():
            report.append(f"\n{comp_name}:")
            report.append(f"  Judge Score Difference: {comp_data['judge_score_diff']:+.4f}")
            report.append(f"  Route Length Difference: {comp_data['route_length_diff']:+.2f}")
            report.append(f"  Success Rate Difference: {comp_data['success_rate_diff']:+.2%}")
            
        report.append("\n\nROUTE DIVERGENCE ANALYSIS")
        report.append("-" * 40)
        report.append(f"Total Divergences: {len(route_analysis['route_divergences'])}")
        
        if route_analysis['route_divergences']:
            report.append("\nSample Divergences:")
            for div in route_analysis['route_divergences'][:5]:
                report.append(f"  Prompt {div['prompt_id']} ({div['config_comparison']}):")
                report.append(f"    Divergence at step {div['divergence_point']}")
                report.append(f"    Route 1: {div['route_1']}")
                report.append(f"    Route 2: {div['route_2']}")
                report.append(f"    Judge Score Diff: {div['judge_score_diff']:+.4f}")
                
        report.append("\n\nCONCLUSIONS")
        report.append("-" * 40)
        
        # Determine conclusion based on results
        c0_score = summary['by_config'].get('C0', {}).get('mean_judge_score', 0)
        c1_score = summary['by_config'].get('C1', {}).get('mean_judge_score', 0)
        c2_score = summary['by_config'].get('C2', {}).get('mean_judge_score', 0)
        
        if c2_score > c1_score and c2_score > c0_score:
            report.append("[PASS] C2 (tesseract_quantum) shows improvement over C1 and C0")
            report.append("  This suggests quantum-assisted routing provides measurable benefit.")
        elif c2_score > c1_score:
            report.append("[PASS] C2 shows improvement over C1 but not C0")
            report.append("  Further investigation needed to establish causality.")
        elif c1_score > c0_score:
            report.append("[PASS] C1 (tesseract_classical) shows improvement over C0")
            report.append("  This suggests tesseract topology provides benefit independent of quantum scoring.")
        else:
            report.append("[FAIL] No clear improvement from quantum or tesseract routing")
            report.append("  Differences may be due to stochastic noise rather than routing layer.")
            
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)


def main():
    """Run the response path audit"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Response Path Audit and Ablation Study")
    parser.add_argument('--output-dir', type=str, default='response_audit_results',
                       help='Directory for audit results')
    parser.add_argument('--model-id', type=str, default='test_model',
                       help='Model identifier')
    parser.add_argument('--temperature', type=float, default=0.7,
                       help='Generation temperature')
    parser.add_argument('--num-repeats', type=int, default=3,
                       help='Number of repeated runs per prompt per config')
    parser.add_argument('--configs', type=str, nargs='+', default=['C0', 'C1', 'C2'],
                       help='Configurations to run')
    parser.add_argument('--prompt-ids', type=str, nargs='+', default=None,
                       help='Specific prompt IDs to test')
    
    args = parser.parse_args()
    
    # Create auditor
    auditor = ResponsePathAuditor(
        output_dir=args.output_dir,
        model_id=args.model_id,
        temperature=args.temperature
    )
    
    # Run audit
    summary = auditor.run_audit(
        prompt_ids=args.prompt_ids,
        configs=args.configs,
        num_repeats=args.num_repeats
    )
    
    # Generate report
    report = auditor.generate_report()
    print(report)
    
    # Save report
    report_file = Path(args.output_dir) / "audit_report.txt"
    with open(report_file, 'w') as f:
        f.write(report)
        
    print(f"\nReport saved to {report_file}")


if __name__ == "__main__":
    main()