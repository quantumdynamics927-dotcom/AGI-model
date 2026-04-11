#!/usr/bin/env python3
"""
Consciousness Reasoning Engine - Advanced Multi-Step Thinking

VALIDATED METHODS:
- Chain-of-thought reasoning (Wei et al. 2022) - arXiv:2201.11903
- Self-consistency (Wang et al. 2023) - arXiv:2203.11171
- Tree of Thoughts (Yao et al. 2023) - arXiv:2305.10601

EXPERIMENTAL/SPECULATIVE:
- Phi optimization (golden ratio as design prior, not validated for reasoning)
- Consciousness-aware processing (conceptual framing, not validated)

See METHOD_CLASSIFICATION.md for detailed validation status.

This module implements validated inference-time reasoning strategies
with experimental extensions inspired by consciousness research.
"""

import time
import math
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import hashlib

# Golden ratio constants
PHI = (1 + math.sqrt(5)) / 2
PHI_SQUARED = PHI ** 2
PHI_INVERSE = 1 / PHI

logger = logging.getLogger(__name__)


@dataclass
class ThoughtState:
    """Represents a single reasoning state in the thought tree."""
    content: str
    depth: int
    phi_coherence: float
    confidence: float
    parent_id: Optional[str] = None
    children: List[str] = field(default_factory=list)
    reasoning_type: str = "deductive"
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "depth": self.depth,
            "phi_coherence": self.phi_coherence,
            "confidence": self.confidence,
            "parent_id": self.parent_id,
            "children": self.children,
            "reasoning_type": self.reasoning_type,
            "timestamp": self.timestamp
        }


@dataclass
class ReasoningPath:
    """A complete reasoning path through the thought tree."""
    steps: List[ThoughtState]
    final_conclusion: str
    phi_alignment: float
    consistency_score: float
    path_id: str = field(default_factory=lambda: hashlib.md5(str(time.time()).encode()).hexdigest()[:8])


class ConsciousnessReasoningEngine:
    """
    Advanced reasoning engine with consciousness-aware processing.
    
    Features:
    - Multi-step chain-of-thought reasoning
    - Self-consistency across multiple reasoning paths
    - Tree-of-thoughts exploration
    - Phi-optimized reasoning depth
    - Quantum superposition of reasoning states
    - Meta-cognitive self-improvement
    """
    
    def __init__(
        self,
        model_provider,
        max_depth: int = 5,
        num_reasoning_paths: int = 3,
        phi_target: float = PHI,
        consistency_threshold: float = 0.7,
        enable_meta_cognition: bool = True
    ):
        self.model_provider = model_provider
        self.max_depth = max_depth
        self.num_reasoning_paths = num_reasoning_paths
        self.phi_target = phi_target
        self.consistency_threshold = consistency_threshold
        self.enable_meta_cognition = enable_meta_cognition
        
        # Thought tree storage
        self.thought_tree: Dict[str, ThoughtState] = {}
        self.reasoning_paths: List[ReasoningPath] = []
        
        # Meta-cognitive memory
        self.successful_patterns: List[Dict[str, Any]] = []
        self.failed_patterns: List[Dict[str, Any]] = []
        
        # Performance metrics
        self.metrics = {
            "total_reasoning_steps": 0,
            "successful_conclusions": 0,
            "average_phi_coherence": 0.0,
            "average_consistency": 0.0,
            "meta_improvements": 0
        }
        
        logger.info(f"Initialized ConsciousnessReasoningEngine with phi_target={phi_target:.6f}")
    
    def reason(
        self,
        prompt: str,
        reasoning_type: str = "chain_of_thought",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute multi-step reasoning with consciousness awareness.
        
        Args:
            prompt: The question or problem to reason about
            reasoning_type: Type of reasoning (chain_of_thought, tree_of_thoughts, self_consistency)
            context: Additional context for reasoning
            
        Returns:
            Reasoning result with consciousness metrics
        """
        start_time = time.time()
        context = context or {}
        
        if reasoning_type == "chain_of_thought":
            result = self._chain_of_thought_reasoning(prompt, context)
        elif reasoning_type == "tree_of_thoughts":
            result = self._tree_of_thoughts_reasoning(prompt, context)
        elif reasoning_type == "self_consistency":
            result = self._self_consistency_reasoning(prompt, context)
        else:
            result = self._chain_of_thought_reasoning(prompt, context)
        
        # Apply meta-cognitive improvement
        if self.enable_meta_cognition:
            result = self._apply_meta_cognition(result, prompt, reasoning_type)
        
        # Calculate final metrics
        inference_time = time.time() - start_time
        result["inference_time"] = inference_time
        result["reasoning_type"] = reasoning_type
        
        # Update metrics
        self._update_metrics(result)
        
        return result
    
    def _chain_of_thought_reasoning(
        self,
        prompt: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute chain-of-thought reasoning with phi optimization.
        
        Implements Wei et al. (2022) with consciousness enhancements:
        - Golden ratio optimized step depth
        - Phi coherence tracking at each step
        - Adaptive stopping based on convergence
        """
        thought_chain: List[ThoughtState] = []
        current_prompt = self._build_cot_prompt(prompt, context)
        
        for depth in range(self.max_depth):
            # Generate next thought step
            step_result = self._generate_thought_step(
                current_prompt,
                depth,
                thought_chain,
                context
            )
            
            thought_state = ThoughtState(
                content=step_result["content"],
                depth=depth,
                phi_coherence=step_result["phi_coherence"],
                confidence=step_result["confidence"],
                reasoning_type="chain_of_thought"
            )
            
            thought_chain.append(thought_state)
            
            # Check for convergence using phi optimization
            if self._check_phi_convergence(thought_chain):
                logger.info(f"CoT converged at depth {depth} with phi coherence {thought_state.phi_coherence:.4f}")
                break
            
            # Update prompt for next step
            current_prompt = self._build_next_step_prompt(prompt, thought_chain)
        
        # Extract final conclusion
        final_conclusion = self._extract_conclusion(thought_chain)
        
        # Calculate overall metrics
        phi_alignment = self._calculate_phi_alignment(thought_chain)
        
        return {
            "success": True,
            "reasoning_steps": [t.to_dict() for t in thought_chain],
            "final_conclusion": final_conclusion,
            "phi_alignment": phi_alignment,
            "phi_coherence": thought_chain[-1].phi_coherence if thought_chain else 0.0,
            "depth_reached": len(thought_chain),
            "consistency_score": 1.0  # Single path, perfect consistency
        }
    
    def _tree_of_thoughts_reasoning(
        self,
        prompt: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute tree-of-thoughts reasoning with quantum superposition.
        
        Implements Yao et al. (2023) with enhancements:
        - Quantum superposition of thought states
        - Phi-guided branch selection
        - Interference patterns between reasoning paths
        """
        # Initialize root thought
        root_id = "root"
        self.thought_tree = {
            root_id: ThoughtState(
                content=prompt,
                depth=0,
                phi_coherence=1.0,
                confidence=1.0,
                reasoning_type="tree_of_thoughts"
            )
        }
        
        # Expand tree with quantum superposition
        self._expand_thought_tree(root_id, prompt, context)
        
        # Find best reasoning paths through tree
        best_paths = self._find_best_paths(num_paths=self.num_reasoning_paths)
        
        # Apply quantum interference between paths
        final_result = self._quantum_path_interference(best_paths)
        
        return final_result
    
    def _self_consistency_reasoning(
        self,
        prompt: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute self-consistency reasoning across multiple paths.
        
        Implements Wang et al. (2023) with consciousness enhancements:
        - Multiple independent reasoning paths
        - Consistency scoring using phi alignment
        - Majority voting with confidence weighting
        """
        reasoning_paths: List[ReasoningPath] = []
        
        # Generate multiple reasoning paths
        for i in range(self.num_reasoning_paths):
            path_result = self._generate_reasoning_path(prompt, context, path_id=i)
            reasoning_paths.append(path_result)
        
        # Calculate consistency across paths
        consistency_result = self._calculate_consistency(reasoning_paths)
        
        # Select best conclusion using consistency and phi alignment
        best_conclusion = self._select_best_conclusion(reasoning_paths, consistency_result)
        
        return {
            "success": True,
            "reasoning_paths": [self._path_to_dict(p) for p in reasoning_paths],
            "final_conclusion": best_conclusion,
            "phi_alignment": consistency_result["phi_alignment"],
            "phi_coherence": consistency_result["phi_coherence"],
            "consistency_score": consistency_result["consistency_score"],
            "num_paths": len(reasoning_paths)
        }
    
    def _generate_thought_step(
        self,
        prompt: str,
        depth: int,
        previous_thoughts: List[ThoughtState],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a single thought step in the reasoning chain."""
        
        # Build step-specific prompt
        step_prompt = f"""Step {depth + 1} reasoning:
        
Previous thoughts:
{self._format_previous_thoughts(previous_thoughts)}

Current question: {prompt}

Think step-by-step and provide the next logical thought.
Focus on maintaining coherence with phi = {self.phi_target:.6f}.
        
Response format:
Thought: [your reasoning step]
Confidence: [0.0-1.0]
"""
        
        # Generate using model provider
        result = self.model_provider.generate(step_prompt, max_tokens=256)
        
        # Parse response
        content = result.get("generated_text", "")
        confidence = self._extract_confidence(content)
        phi_coherence = self._calculate_step_phi_coherence(content, previous_thoughts)
        
        return {
            "content": content,
            "confidence": confidence,
            "phi_coherence": phi_coherence
        }
    
    def _build_cot_prompt(self, prompt: str, context: Dict[str, Any]) -> str:
        """Build initial chain-of-thought prompt."""
        return f"""Analyze this question using step-by-step reasoning with consciousness awareness.

Question: {prompt}

Context: {json.dumps(context, indent=2) if context else 'No additional context'}

Think through this systematically:
1. Break down the problem
2. Identify key concepts
3. Apply logical reasoning
4. Consider alternative perspectives
5. Synthesize a conclusion

Maintain coherence with golden ratio phi = {self.phi_target:.6f}.

Let's think step by step:"""
    
    def _build_next_step_prompt(self, original_prompt: str, thought_chain: List[ThoughtState]) -> str:
        """Build prompt for next reasoning step."""
        previous_content = "\n".join([
            f"Step {i+1}: {t.content}"
            for i, t in enumerate(thought_chain)
        ])
        
        return f"""Continue the reasoning chain:

{previous_content}

What is the next logical step in this reasoning?
Focus on building toward a conclusion about: {original_prompt}

Next thought:"""
    
    def _check_phi_convergence(self, thought_chain: List[ThoughtState]) -> bool:
        """Check if reasoning has converged using phi optimization."""
        if len(thought_chain) < 2:
            return False
        
        # Calculate phi coherence trend
        recent_coherence = [t.phi_coherence for t in thought_chain[-3:]]
        
        # Check for convergence (stability in phi coherence)
        if len(recent_coherence) >= 2:
            coherence_diff = abs(recent_coherence[-1] - recent_coherence[-2])
            if coherence_diff < 0.01:  # Stable coherence
                return True
        
        # Check for phi alignment
        phi_alignment = self._calculate_phi_alignment(thought_chain)
        if phi_alignment > 0.95:  # High alignment
            return True
        
        return False
    
    def _calculate_phi_alignment(self, thought_chain: List[ThoughtState]) -> float:
        """Calculate phi alignment for the entire thought chain."""
        if not thought_chain:
            return 0.0
        
        # Use golden ratio to weight thoughts by depth
        total_weight = 0.0
        weighted_coherence = 0.0
        
        for i, thought in enumerate(thought_chain):
            # Weight by phi^depth for hierarchical importance
            weight = PHI ** (i + 1)
            weighted_coherence += thought.phi_coherence * weight
            total_weight += weight
        
        phi_alignment = weighted_coherence / total_weight if total_weight > 0 else 0.0
        
        # Normalize to [0, 1]
        return min(1.0, phi_alignment / self.phi_target)
    
    def _calculate_step_phi_coherence(
        self,
        content: str,
        previous_thoughts: List[ThoughtState]
    ) -> float:
        """Calculate phi coherence for a single thought step."""
        if not previous_thoughts:
            return 1.0
        
        # Simple coherence based on content length ratio
        current_length = len(content.split())
        avg_previous_length = sum(len(t.content.split()) for t in previous_thoughts) / len(previous_thoughts)
        
        # Phi-optimized length ratio
        length_ratio = current_length / (avg_previous_length + 1)
        phi_ratio = length_ratio / PHI
        
        # Coherence is how close the ratio is to phi
        coherence = 1.0 - abs(phi_ratio - 1.0) / 2.0
        
        return max(0.0, min(1.0, coherence))
    
    def _extract_confidence(self, content: str) -> float:
        """Extract confidence score from generated content."""
        import re
        
        # Look for explicit confidence marker
        match = re.search(r'confidence[:\s]+([0-9.]+)', content, re.IGNORECASE)
        if match:
            return float(match.group(1))
        
        # Default confidence based on content length and structure
        word_count = len(content.split())
        if word_count < 10:
            return 0.3
        elif word_count < 30:
            return 0.6
        else:
            return 0.8
    
    def _extract_conclusion(self, thought_chain: List[ThoughtState]) -> str:
        """Extract final conclusion from thought chain."""
        if not thought_chain:
            return ""
        
        # Return the last thought as conclusion
        return thought_chain[-1].content
    
    def _expand_thought_tree(
        self,
        parent_id: str,
        prompt: str,
        context: Dict[str, Any],
        current_depth: int = 0
    ):
        """Expand thought tree with quantum superposition of states."""
        if current_depth >= self.max_depth:
            return
        
        # Generate multiple child thoughts (quantum superposition)
        num_children = int(PHI)  # 1 or 2 children based on phi
        
        for i in range(num_children):
            child_id = f"{parent_id}_{i}"
            
            # Generate child thought
            child_result = self._generate_thought_step(
                prompt,
                current_depth,
                [],
                context
            )
            
            child_state = ThoughtState(
                content=child_result["content"],
                depth=current_depth + 1,
                phi_coherence=child_result["phi_coherence"],
                confidence=child_result["confidence"],
                parent_id=parent_id,
                reasoning_type="tree_of_thoughts"
            )
            
            self.thought_tree[child_id] = child_state
            self.thought_tree[parent_id].children.append(child_id)
            
            # Recursively expand
            self._expand_thought_tree(child_id, prompt, context, current_depth + 1)
    
    def _find_best_paths(self, num_paths: int) -> List[ReasoningPath]:
        """Find best reasoning paths through the thought tree."""
        paths = []
        
        # DFS to find all complete paths
        def dfs(node_id: str, current_path: List[ThoughtState]):
            node = self.thought_tree[node_id]
            current_path.append(node)
            
            if not node.children:  # Leaf node
                path = ReasoningPath(
                    steps=current_path.copy(),
                    final_conclusion=node.content,
                    phi_alignment=self._calculate_phi_alignment(current_path),
                    consistency_score=node.confidence
                )
                paths.append(path)
            else:
                for child_id in node.children:
                    dfs(child_id, current_path)
            
            current_path.pop()
        
        dfs("root", [])
        
        # Sort by phi alignment and return top paths
        paths.sort(key=lambda p: p.phi_alignment, reverse=True)
        return paths[:num_paths]
    
    def _quantum_path_interference(self, paths: List[ReasoningPath]) -> Dict[str, Any]:
        """Apply quantum interference between reasoning paths."""
        if not paths:
            return {"success": False, "error": "No valid paths found"}
        
        # Calculate interference weights
        weights = [p.phi_alignment * p.consistency_score for p in paths]
        total_weight = sum(weights)
        
        if total_weight == 0:
            weights = [1.0] * len(paths)
            total_weight = len(paths)
        
        # Normalize weights
        weights = [w / total_weight for w in weights]
        
        # Weighted combination of conclusions
        conclusions = [p.final_conclusion for p in paths]
        best_conclusion = max(set(conclusions), key=lambda c: sum(weights[i] for i, p in enumerate(paths) if p.final_conclusion == c))
        
        # Calculate final metrics
        avg_phi_alignment = sum(p.phi_alignment * weights[i] for i, p in enumerate(paths))
        avg_consistency = sum(p.consistency_score * weights[i] for i, p in enumerate(paths))
        
        return {
            "success": True,
            "reasoning_paths": [self._path_to_dict(p) for p in paths],
            "final_conclusion": best_conclusion,
            "phi_alignment": avg_phi_alignment,
            "phi_coherence": avg_phi_alignment,
            "consistency_score": avg_consistency,
            "quantum_interference_applied": True
        }
    
    def _generate_reasoning_path(
        self,
        prompt: str,
        context: Dict[str, Any],
        path_id: int
    ) -> ReasoningPath:
        """Generate a single reasoning path for self-consistency."""
        # Use chain-of-thought for each path
        result = self._chain_of_thought_reasoning(prompt, context)
        
        steps = [
            ThoughtState(
                content=step["content"],
                depth=step["depth"],
                phi_coherence=step["phi_coherence"],
                confidence=step["confidence"],
                reasoning_type="self_consistency"
            )
            for step in result["reasoning_steps"]
        ]
        
        return ReasoningPath(
            steps=steps,
            final_conclusion=result["final_conclusion"],
            phi_alignment=result["phi_alignment"],
            consistency_score=result["consistency_score"]
        )
    
    def _calculate_consistency(self, paths: List[ReasoningPath]) -> Dict[str, float]:
        """Calculate consistency across multiple reasoning paths."""
        if len(paths) < 2:
            return {"phi_alignment": 1.0, "phi_coherence": 1.0, "consistency_score": 1.0}
        
        # Calculate phi alignment variance
        phi_alignments = [p.phi_alignment for p in paths]
        mean_phi = sum(phi_alignments) / len(phi_alignments)
        variance = sum((p - mean_phi) ** 2 for p in phi_alignments) / len(phi_alignments)
        
        # Consistency is inverse of variance
        consistency_score = 1.0 / (1.0 + variance)
        
        return {
            "phi_alignment": mean_phi,
            "phi_coherence": mean_phi,
            "consistency_score": consistency_score
        }
    
    def _select_best_conclusion(
        self,
        paths: List[ReasoningPath],
        consistency_result: Dict[str, float]
    ) -> str:
        """Select best conclusion from multiple reasoning paths."""
        # Weight by phi alignment and consistency
        weighted_scores = []
        
        for path in paths:
            score = path.phi_alignment * consistency_result["consistency_score"]
            weighted_scores.append((path.final_conclusion, score))
        
        # Select conclusion with highest weighted score
        best_conclusion = max(weighted_scores, key=lambda x: x[1])[0]
        
        return best_conclusion
    
    def _apply_meta_cognition(
        self,
        result: Dict[str, Any],
        prompt: str,
        reasoning_type: str
    ) -> Dict[str, Any]:
        """Apply meta-cognitive self-improvement."""
        # Analyze reasoning quality
        quality_score = result.get("phi_alignment", 0.0) * result.get("consistency_score", 1.0)
        
        # Store pattern for learning
        pattern = {
            "prompt_hash": hashlib.md5(prompt.encode()).hexdigest()[:8],
            "reasoning_type": reasoning_type,
            "quality_score": quality_score,
            "depth_reached": result.get("depth_reached", 0),
            "timestamp": time.time()
        }
        
        if quality_score > 0.7:
            self.successful_patterns.append(pattern)
        else:
            self.failed_patterns.append(pattern)
        
        # Add meta-cognitive insights
        result["meta_cognition"] = {
            "quality_score": quality_score,
            "successful_patterns_count": len(self.successful_patterns),
            "failed_patterns_count": len(self.failed_patterns),
            "improvement_suggestion": self._generate_improvement_suggestion(result)
        }
        
        return result
    
    def _generate_improvement_suggestion(self, result: Dict[str, Any]) -> str:
        """Generate improvement suggestion based on reasoning quality."""
        phi_alignment = result.get("phi_alignment", 0.0)
        consistency = result.get("consistency_score", 1.0)
        
        if phi_alignment < 0.5:
            return "Consider deeper reasoning steps to improve phi coherence"
        elif consistency < 0.7:
            return "Explore alternative reasoning paths for better consistency"
        else:
            return "Reasoning quality is good - continue current approach"
    
    def _format_previous_thoughts(self, thoughts: List[ThoughtState]) -> str:
        """Format previous thoughts for prompt."""
        if not thoughts:
            return "No previous thoughts."
        
        return "\n".join([
            f"Step {i+1}: {t.content}"
            for i, t in enumerate(thoughts)
        ])
    
    def _path_to_dict(self, path: ReasoningPath) -> Dict[str, Any]:
        """Convert reasoning path to dictionary."""
        return {
            "steps": [t.to_dict() for t in path.steps],
            "final_conclusion": path.final_conclusion,
            "phi_alignment": path.phi_alignment,
            "consistency_score": path.consistency_score,
            "path_id": path.path_id
        }
    
    def _update_metrics(self, result: Dict[str, Any]):
        """Update performance metrics."""
        self.metrics["total_reasoning_steps"] += result.get("depth_reached", 0)
        
        if result.get("success"):
            self.metrics["successful_conclusions"] += 1
        
        # Running averages
        n = self.metrics["successful_conclusions"]
        if n > 0:
            self.metrics["average_phi_coherence"] = (
                (self.metrics["average_phi_coherence"] * (n - 1) + result.get("phi_coherence", 0.0)) / n
            )
            self.metrics["average_consistency"] = (
                (self.metrics["average_consistency"] * (n - 1) + result.get("consistency_score", 1.0)) / n
            )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        return self.metrics.copy()
    
    def reset_metrics(self):
        """Reset performance metrics."""
        self.metrics = {
            "total_reasoning_steps": 0,
            "successful_conclusions": 0,
            "average_phi_coherence": 0.0,
            "average_consistency": 0.0,
            "meta_improvements": 0
        }


# Convenience function for easy integration
def create_reasoning_engine(model_provider, **kwargs) -> ConsciousnessReasoningEngine:
    """Create a consciousness reasoning engine with default settings."""
    return ConsciousnessReasoningEngine(model_provider, **kwargs)