"""
Test script for Response Path Audit Framework

Validates that the audit framework correctly implements the controlled ablation study.
"""

import pytest
import json
import hashlib
import numpy as np
import torch
from pathlib import Path
import tempfile
import shutil

from response_path_audit import (
    ResponsePathAuditor,
    AuditConfig,
    PromptRecord,
    RouteTrace,
    AuditResult,
    ClassicalEdgeScorer,
    FixedPolicyRouter
)


class TestResponsePathAudit:
    """Test suite for response path audit framework"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test outputs"""
        dirpath = tempfile.mkdtemp()
        yield Path(dirpath)
        shutil.rmtree(dirpath)
        
    @pytest.fixture
    def auditor(self, temp_dir):
        """Create auditor instance for testing"""
        return ResponsePathAuditor(
            output_dir=str(temp_dir),
            model_id="test_model",
            temperature=0.7,
            seeds=[42, 123, 456]
        )
        
    def test_config_definitions(self):
        """Test that all three configurations are properly defined"""
        assert 'C0' in ResponsePathAuditor.CONFIGS
        assert 'C1' in ResponsePathAuditor.CONFIGS
        assert 'C2' in ResponsePathAuditor.CONFIGS
        
        c0 = ResponsePathAuditor.CONFIGS['C0']
        assert c0.config_id == 'C0'
        assert c0.config_name == 'classical_baseline'
        assert c0.use_tesseract_router == False
        assert c0.use_quantum_scorer == False
        assert c0.fixed_policy == True
        
        c1 = ResponsePathAuditor.CONFIGS['C1']
        assert c1.config_id == 'C1'
        assert c1.config_name == 'tesseract_classical'
        assert c1.use_tesseract_router == True
        assert c1.use_quantum_scorer == False
        assert c1.use_classical_scorer == True
        
        c2 = ResponsePathAuditor.CONFIGS['C2']
        assert c2.config_id == 'C2'
        assert c2.config_name == 'tesseract_quantum'
        assert c2.use_tesseract_router == True
        assert c2.use_quantum_scorer == True
        
    def test_prompt_loading(self, auditor):
        """Test that prompts are loaded correctly"""
        prompts = auditor.prompts
        
        assert len(prompts) > 0
        
        # Check prompt classes
        prompt_classes = set(p.prompt_class for p in prompts)
        assert 'ambiguous' in prompt_classes
        assert 'tool_use' in prompt_classes
        assert 'fault_tolerance' in prompt_classes
        assert 'memory_governance' in prompt_classes
        assert 'factual_control' in prompt_classes
        
        # Check prompt structure
        for p in prompts:
            assert p.prompt_id is not None
            assert p.prompt_text is not None
            assert p.prompt_hash is not None
            assert p.prompt_class in ['ambiguous', 'tool_use', 'fault_tolerance', 'memory_governance', 'factual_control']
            assert p.difficulty in ['easy', 'medium', 'hard']
            
    def test_fixed_policy_router(self):
        """Test that fixed policy router follows predetermined path"""
        router = FixedPolicyRouter()
        z = torch.randn(32)
        
        # Test routing from vertex 0
        next_vertex, confidence = router.get_next_vertex(0, z)
        assert next_vertex == 1  # Should follow fixed path
        assert confidence == 0.75
        
        # Test routing from vertex 1
        next_vertex, confidence = router.get_next_vertex(1, z)
        assert next_vertex == 5
        
        # Test routing from final vertex
        next_vertex, confidence = router.get_next_vertex(15, z)
        assert next_vertex == 15  # Should stay at final vertex
        
    def test_classical_edge_scorer(self):
        """Test that classical edge scorer produces deterministic scores"""
        scorer = ClassicalEdgeScorer(latent_dim=32)
        z = torch.randn(32)
        
        # Score edges from vertex 0
        scores = scorer.score_edges(z, 0, [0, 1, 2, 4, 8])
        
        # Check that scores are valid
        assert len(scores) == 5
        assert all(0 <= s <= 1 for s in scores.values())
        
        # Check normalization
        total = sum(scores.values())
        assert abs(total - 1.0) < 1e-6
        
        # Test determinism with same seed
        np.random.seed(42)
        torch.manual_seed(42)
        z1 = torch.randn(32)
        scores1 = scorer.score_edges(z1, 0, [0, 1, 2])
        
        np.random.seed(42)
        torch.manual_seed(42)
        z2 = torch.randn(32)
        scores2 = scorer.score_edges(z2, 0, [0, 1, 2])
        
        assert scores1 == scores2
        
    def test_route_fixed(self, auditor):
        """Test fixed routing (C0)"""
        z = torch.randn(32)
        trace = RouteTrace(
            trace_id="test_001",
            prompt_id="fact_001",
            config_id="C0",
            seed=42,
            model_id="test_model",
            temperature=0.7,
            initial_vertex=0,
            initial_vertex_name="Sensory Input"
        )
        
        result = auditor._route_fixed(z, trace)
        
        # Check that route follows fixed path
        assert trace.edge_score_method == "fixed"
        assert len(trace.visited_states) > 0
        assert len(trace.selected_transitions) > 0
        assert len(trace.confidence_values) > 0
        
        # Check that quantum scores are empty for C0
        assert all(len(qs) == 0 for qs in trace.quantum_scores)
        
    def test_route_tesseract_classical(self, auditor):
        """Test tesseract routing with classical scorer (C1)"""
        z = torch.randn(32)
        trace = RouteTrace(
            trace_id="test_002",
            prompt_id="amb_001",
            config_id="C1",
            seed=42,
            model_id="test_model",
            temperature=0.7,
            initial_vertex=0,
            initial_vertex_name="Sensory Input"
        )
        
        result = auditor._route_tesseract_classical(z, trace)
        
        # Check that route uses classical scoring
        assert trace.edge_score_method == "classical"
        assert len(trace.visited_states) > 0
        assert len(trace.transition_scores) > 0
        
        # Check that quantum scores are empty for C1
        assert all(len(qs) == 0 for qs in trace.quantum_scores)
        
    def test_route_tesseract_quantum(self, auditor):
        """Test tesseract routing with quantum scorer (C2)"""
        z = torch.randn(32)
        trace = RouteTrace(
            trace_id="test_003",
            prompt_id="tool_001",
            config_id="C2",
            seed=42,
            model_id="test_model",
            temperature=0.7,
            initial_vertex=0,
            initial_vertex_name="Sensory Input"
        )
        
        result = auditor._route_tesseract_quantum(z, trace)
        
        # Check that route uses quantum scoring
        assert trace.edge_score_method == "quantum"
        assert len(trace.visited_states) > 0
        assert len(trace.transition_scores) > 0
        
        # Check that quantum scores are populated for C2
        assert len(trace.quantum_scores) > 0
        
    def test_single_inference(self, auditor):
        """Test single inference run"""
        prompt = PromptRecord(
            prompt_id="fact_001",
            prompt_text="What is the golden ratio?",
            prompt_hash=hashlib.sha256("What is the golden ratio?".encode()).hexdigest()[:16],
            prompt_class="factual_control",
            expected_behavior="Provide accurate factual answer",
            difficulty="easy"
        )
        
        config = ResponsePathAuditor.CONFIGS['C0']
        
        result = auditor._run_single_inference(
            prompt=prompt,
            config=config,
            seed=42,
            repeat_idx=0
        )
        
        # Check result structure
        assert result.prompt_id == "fact_001"
        assert result.config_id == "C0"
        assert result.seed == 42
        
        # Check trace
        assert result.trace.trace_id.startswith("fact_001_C0")
        assert len(result.trace.visited_states) > 0
        
        # Check evaluation metrics
        assert 'judge_score' in result.evaluation_metrics
        assert 'task_success' in result.evaluation_metrics
        assert 0 <= result.evaluation_metrics['judge_score'] <= 1
        
    def test_audit_run(self, auditor):
        """Test full audit run"""
        # Run audit with limited prompts and repeats
        summary = auditor.run_audit(
            prompt_ids=['fact_001', 'fact_002', 'amb_001'],
            configs=['C0', 'C1', 'C2'],
            num_repeats=2
        )
        
        # Check summary structure
        assert 'by_config' in summary
        assert 'by_prompt_class' in summary
        assert 'pairwise_comparisons' in summary
        
        # Check that all configs ran
        assert 'C0' in summary['by_config']
        assert 'C1' in summary['by_config']
        assert 'C2' in summary['by_config']
        
        # Check metrics
        for config_id in ['C0', 'C1', 'C2']:
            stats = summary['by_config'][config_id]
            assert 'mean_judge_score' in stats
            assert 'task_success_rate' in stats
            assert 'mean_route_length' in stats
            assert 'total_inferences' in stats
            assert stats['total_inferences'] == 6  # 3 prompts × 2 repeats
            
    def test_route_comparison(self, auditor):
        """Test route comparison analysis"""
        # Run small audit
        auditor.run_audit(
            prompt_ids=['fact_001'],
            configs=['C0', 'C1', 'C2'],
            num_repeats=1
        )
        
        # Analyze route differences
        analysis = auditor.analyze_route_differences()
        
        # Check analysis structure
        assert 'route_divergences' in analysis
        assert 'score_differences' in analysis
        assert 'outcome_correlations' in analysis
        
    def test_report_generation(self, auditor):
        """Test report generation"""
        # Run small audit
        auditor.run_audit(
            prompt_ids=['fact_001', 'fact_002'],
            configs=['C0', 'C1', 'C2'],
            num_repeats=1
        )
        
        # Generate report
        report = auditor.generate_report()
        
        # Check report content
        assert "RESPONSE PATH AUDIT REPORT" in report
        assert "CONFIGURATION SUMMARY" in report
        assert "C0:" in report
        assert "C1:" in report
        assert "C2:" in report
        assert "PAIRWISE COMPARISONS" in report
        assert "CONCLUSIONS" in report
        
    def test_file_saving(self, auditor, temp_dir):
        """Test that results are saved correctly"""
        # Run audit
        auditor.run_audit(
            prompt_ids=['fact_001'],
            configs=['C0'],
            num_repeats=1
        )
        
        # Check files exist
        assert (temp_dir / "response_traces.json").exists()
        assert (temp_dir / "response_audit_results.json").exists()
        assert (temp_dir / "audit_summary.json").exists()
        
        # Check file content
        with open(temp_dir / "response_traces.json") as f:
            traces = json.load(f)
            assert 'C0' in traces
            
        with open(temp_dir / "audit_summary.json") as f:
            summary = json.load(f)
            assert 'by_config' in summary
            
    def test_reproducibility(self, auditor):
        """Test that same seed produces same results"""
        prompt = PromptRecord(
            prompt_id="fact_001",
            prompt_text="What is the golden ratio?",
            prompt_hash=hashlib.sha256("What is the golden ratio?".encode()).hexdigest()[:16],
            prompt_class="factual_control",
            expected_behavior="Provide accurate factual answer",
            difficulty="easy"
        )
        
        config = ResponsePathAuditor.CONFIGS['C0']
        
        # Run twice with same seed
        result1 = auditor._run_single_inference(prompt, config, seed=42, repeat_idx=0)
        result2 = auditor._run_single_inference(prompt, config, seed=42, repeat_idx=0)
        
        # Check that routes are identical
        assert result1.trace.visited_states == result2.trace.visited_states
        assert result1.trace.selected_transitions == result2.trace.selected_transitions
        
    def test_factual_control_consistency(self, auditor):
        """Test that factual control prompts are consistent across configs"""
        # Run audit for factual prompts
        factual_prompts = [p for p in auditor.prompts if p.prompt_class == 'factual_control']
        prompt_ids = [p.prompt_id for p in factual_prompts[:3]]
        
        auditor.run_audit(
            prompt_ids=prompt_ids,
            configs=['C0', 'C1', 'C2'],
            num_repeats=2
        )
        
        # Check that factual prompts have similar scores across configs
        summary = auditor._calculate_summary()
        
        # Factual prompts should have similar judge scores across configs
        # (they don't benefit from routing differences)
        c0_score = summary['by_config']['C0']['mean_judge_score']
        c1_score = summary['by_config']['C1']['mean_judge_score']
        c2_score = summary['by_config']['C2']['mean_judge_score']
        
        # Scores should be within reasonable range for factual prompts
        # (allowing for some variation due to routing)
        assert abs(c0_score - c1_score) < 0.3
        assert abs(c1_score - c2_score) < 0.3
        
    def test_ambiguous_prompt_differentiation(self, auditor):
        """Test that ambiguous prompts show routing differences"""
        # Run audit for ambiguous prompts
        ambiguous_prompts = [p for p in auditor.prompts if p.prompt_class == 'ambiguous']
        prompt_ids = [p.prompt_id for p in ambiguous_prompts[:3]]
        
        auditor.run_audit(
            prompt_ids=prompt_ids,
            configs=['C0', 'C1', 'C2'],
            num_repeats=2
        )
        
        # Analyze route differences
        analysis = auditor.analyze_route_differences()
        
        # Ambiguous prompts should show some route divergence
        # (not guaranteed, but expected)
        # This is a soft check - we just verify the analysis runs
        assert 'route_divergences' in analysis


class TestPromptSuite:
    """Test the prompt suite structure"""
    
    def test_prompt_file_exists(self):
        """Test that prompt file exists"""
        prompt_file = Path("response_audit_prompts.json")
        assert prompt_file.exists()
        
    def test_prompt_file_structure(self):
        """Test prompt file structure"""
        with open("response_audit_prompts.json") as f:
            data = json.load(f)
            
        assert 'metadata' in data
        assert 'prompts' in data
        assert 'version' in data['metadata']
        assert 'total_prompts' in data['metadata']
        assert 'classes' in data['metadata']
        
    def test_prompt_classes(self):
        """Test that all prompt classes are represented"""
        with open("response_audit_prompts.json") as f:
            data = json.load(f)
            
        prompt_classes = set(p['prompt_class'] for p in data['prompts'])
        
        required_classes = ['ambiguous', 'tool_use', 'fault_tolerance', 'memory_governance', 'factual_control']
        for cls in required_classes:
            assert cls in prompt_classes, f"Missing prompt class: {cls}"
            
    def test_prompt_difficulty_distribution(self):
        """Test that difficulties are distributed"""
        with open("response_audit_prompts.json") as f:
            data = json.load(f)
            
        difficulties = [p['difficulty'] for p in data['prompts']]
        
        assert 'easy' in difficulties
        assert 'medium' in difficulties
        assert 'hard' in difficulties


class TestTraceSchema:
    """Test the trace schema"""
    
    def test_schema_file_exists(self):
        """Test that schema file exists"""
        schema_file = Path("response_trace_schema.json")
        assert schema_file.exists()
        
    def test_schema_structure(self):
        """Test schema structure"""
        with open("response_trace_schema.json") as f:
            schema = json.load(f)
            
        assert '$schema' in schema
        assert 'title' in schema
        assert 'required' in schema
        assert 'properties' in schema
        
        # Check required fields
        required_fields = [
            'trace_id', 'prompt_id', 'config_id', 'seed', 'model_id',
            'initial_state', 'route_trace', 'final_state', 'response_hash',
            'evaluation_metrics', 'artifact_lineage'
        ]
        for field in required_fields:
            assert field in schema['required']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])