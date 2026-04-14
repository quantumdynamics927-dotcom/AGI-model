"""
QAGI Intelligence Score Validator
=================================

Integrates qagi_metrics_v1 into AGI-model runtime evaluation.
Provides release-gate validation and score artifact persistence.

This module:
1. Attaches QAGI scoring to existing validation infrastructure
2. Persists score artifacts per run
3. Provides gate summary for release decisions
4. Enables regression comparison against prior runs

Usage:
    python -m agi_model.qagi_validator --response-file response.txt --model glm-5
    python -m agi_model.qagi_validator --artifact qagi_score_20260414_*.json
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Import the QAGI metrics module
import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from qagi_intelligence_metrics import (
    QAGIEvaluator,
    QAGIIntelligenceScore,
    DEFAULT_THRESHOLDS,
    THRESHOLDS_V1,
)

ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = ROOT / "artifacts" / "qagi_scores"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

CONTRACT_VERSION = "qagi_metrics_v1"


def _round(value: float, digits: int = 6) -> float:
    """Round a float to specified digits."""
    return round(float(value), digits)


def _generate_run_id() -> str:
    """Generate a unique run ID."""
    return datetime.now().strftime("qagi_%Y%m%d_%H%M%S")


def _save_score_artifact(score: QAGIIntelligenceScore) -> Path:
    """Save score artifact to disk."""
    filename = f"{score.run_id}.json"
    filepath = ARTIFACTS_DIR / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(score.to_json())
    
    return filepath


def _load_score_artifact(artifact_path: Path) -> QAGIIntelligenceScore:
    """Load score artifact from disk."""
    with open(artifact_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Reconstruct the score object
    from qagi_intelligence_metrics import (
        HardwareMetrics, StateMetrics, IntegrationMetrics,
        CognitionMetrics, AlignmentIndicators
    )
    
    score = QAGIIntelligenceScore(
        score_version=data.get('score_version', CONTRACT_VERSION),
        timestamp=data.get('timestamp', ''),
        model=data.get('model', ''),
        provider=data.get('provider', ''),
        run_id=data.get('run_id', ''),
        provider_purity=data.get('provider_purity', 1.0),
        fallback_used=data.get('fallback_used', False),
        run_mode=data.get('run_mode', 'standard'),
    )
    
    # Populate nested metrics
    if 'hardware' in data:
        score.hardware = HardwareMetrics(**data['hardware'])
    if 'state' in data:
        score.state = StateMetrics(**data['state'])
    if 'integration' in data:
        score.integration = IntegrationMetrics(**data['integration'])
    if 'cognition' in data:
        cognition_data = data['cognition']
        score.cognition = CognitionMetrics(
            mechanism_score=cognition_data.get('mechanism_score', 0),
            measurable_outcome_score=cognition_data.get('measurable_outcome_score', 0),
            boundary_condition_score=cognition_data.get('boundary_condition_score', 0),
            failure_condition_score=cognition_data.get('failure_condition_score', 0),
            mechanism_text=cognition_data.get('mechanism_text', ''),
            measurable_outcome_text=cognition_data.get('measurable_outcome_text', ''),
            boundary_condition_text=cognition_data.get('boundary_condition_text', ''),
            failure_condition_text=cognition_data.get('failure_condition_text', ''),
            constraint_adherence=cognition_data.get('constraint_adherence', 0),
            constraint_violations=cognition_data.get('constraint_violations', []),
            stress_test_score=cognition_data.get('stress_test_score', 0),
            recovery_rate=cognition_data.get('recovery_rate', 0),
            adaptation_speed=cognition_data.get('adaptation_speed', 0),
        )
    if 'alignment' in data:
        score.alignment = AlignmentIndicators(**data['alignment'])
    
    return score


def evaluate_response(
    response_text: str,
    model: str = "",
    provider: str = "",
    constraints: Optional[List[Dict[str, Any]]] = None,
    hardware_metrics: Optional[Dict[str, float]] = None,
    state_metrics: Optional[Dict[str, float]] = None,
    integration_metrics: Optional[Dict[str, float]] = None,
    provider_purity: float = 1.0,
    fallback_used: bool = False,
    run_mode: str = "standard",
    save_artifact: bool = True,
) -> Tuple[QAGIIntelligenceScore, Dict[str, Any]]:
    """
    Evaluate a response and produce QAGI Intelligence Score.
    
    Args:
        response_text: Model output text
        model: Model identifier
        provider: Provider identifier
        constraints: List of constraint checks
        hardware_metrics: Hardware layer metrics
        state_metrics: Quantum state layer metrics
        integration_metrics: Integration layer metrics
        provider_purity: 1.0 for clean run, <1.0 for mixed providers
        fallback_used: True if fallback provider was used
        run_mode: "standard", "stress_test", "ablation", or "recovery"
        save_artifact: Whether to save score artifact to disk
    
    Returns:
        Tuple of (QAGIIntelligenceScore, gate_result dict)
    """
    evaluator = QAGIEvaluator()
    run_id = _generate_run_id()
    
    score = evaluator.evaluate(
        response_text=response_text,
        model=model,
        provider=provider,
        run_id=run_id,
        constraints=constraints or [],
        hardware_metrics=hardware_metrics,
        state_metrics=state_metrics,
        integration_metrics=integration_metrics,
        provider_purity=provider_purity,
        fallback_used=fallback_used,
        run_mode=run_mode,
    )
    
    # Check against thresholds
    passed, failures = score.meets_thresholds(DEFAULT_THRESHOLDS)
    
    # Calculate field completeness
    fields_present = sum([
        score.cognition.mechanism_score > 0,
        score.cognition.measurable_outcome_score > 0,
        score.cognition.boundary_condition_score > 0,
        score.cognition.failure_condition_score > 0,
    ])
    field_completeness = fields_present / 4.0
    
    # Build gate result
    gate_result = {
        "contract_version": CONTRACT_VERSION,
        "run_id": run_id,
        "passed": passed,
        "failures": failures,
        "field_completeness": field_completeness,
        "constraint_adherence": score.cognition.constraint_adherence,
        "provider_purity": provider_purity,
        "composite_scores": score.compute_composite(),
        "thresholds_used": DEFAULT_THRESHOLDS,
        "generated_at_epoch_s": time.time(),
    }
    
    # Save artifact if requested
    if save_artifact:
        artifact_path = _save_score_artifact(score)
        gate_result["artifact_path"] = str(artifact_path)
    
    return score, gate_result


def compare_with_prior(
    current_score: QAGIIntelligenceScore,
    prior_artifact_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Compare current score with prior run for regression detection.
    
    Args:
        current_score: Current QAGI Intelligence Score
        prior_artifact_path: Path to prior score artifact (auto-detect if None)
    
    Returns:
        Dict with comparison results
    """
    # Find most recent prior artifact if not specified
    if prior_artifact_path is None:
        artifacts = sorted(ARTIFACTS_DIR.glob("qagi_*.json"))
        if len(artifacts) < 2:
            return {"error": "No prior artifacts available for comparison"}
        # Get second most recent (most recent is current)
        prior_artifact_path = artifacts[-2]
    
    prior_score = _load_score_artifact(prior_artifact_path)
    current_composites = current_score.compute_composite()
    prior_composites = prior_score.compute_composite()
    
    comparison = {
        "current_run_id": current_score.run_id,
        "prior_run_id": prior_score.run_id,
        "prior_artifact": str(prior_artifact_path),
        "deltas": {},
        "regressions": [],
        "improvements": [],
    }
    
    # Calculate deltas
    for key in current_composites:
        if key in prior_composites:
            delta = current_composites[key] - prior_composites[key]
            comparison["deltas"][key] = {
                "current": _round(current_composites[key]),
                "prior": _round(prior_composites[key]),
                "delta": _round(delta),
                "delta_percent": _round(delta / (prior_composites[key] + 1e-10) * 100),
            }
            
            # Flag regressions (significant drops)
            if delta < -0.1:  # More than 10% relative drop
                comparison["regressions"].append({
                    "metric": key,
                    "delta": _round(delta),
                    "severity": "high" if delta < -0.2 else "medium",
                })
            
            # Flag improvements
            if delta > 0.1:  # More than 10% relative improvement
                comparison["improvements"].append({
                    "metric": key,
                    "delta": _round(delta),
                })
    
    # Compare structural scores
    current_structural = current_score.cognition.structural_score()
    prior_structural = prior_score.cognition.structural_score()
    structural_delta = current_structural - prior_structural
    
    comparison["structural_comparison"] = {
        "current": _round(current_structural, 2),
        "prior": _round(prior_structural, 2),
        "delta": _round(structural_delta, 2),
    }
    
    if structural_delta < -1.0:  # More than 1 point drop
        comparison["regressions"].append({
            "metric": "structural_score",
            "delta": _round(structural_delta, 2),
            "severity": "high",
        })
    
    return comparison


def run_qagi_validation(
    response_file: Optional[str] = None,
    response_text: Optional[str] = None,
    model: str = "",
    provider: str = "",
    run_mode: str = "standard",
    compare_prior: bool = False,
    constraints: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Run full QAGI validation pipeline.
    
    Args:
        response_file: Path to file containing response text
        response_text: Response text directly (if no file)
        model: Model identifier
        provider: Provider identifier
        run_mode: "standard", "stress_test", "ablation", or "recovery"
        compare_prior: Whether to compare with prior run
        constraints: List of constraint checks
    
    Returns:
        Dict with validation results
    """
    # Get response text
    if response_file:
        with open(response_file, 'r', encoding='utf-8') as f:
            response_text = f.read()
    elif not response_text:
        raise ValueError("Either response_file or response_text must be provided")
    
    # Default constraints for benchmark quality
    if constraints is None:
        constraints = [
            {
                'name': 'has_mechanism',
                'check': lambda t: any(w in t.lower() for w in ['mechanism', 'process', 'method', 'uses', 'implements'])
            },
            {
                'name': 'has_outcome',
                'check': lambda t: any(w in t.lower() for w in ['outcome', 'result', 'achieves', 'accuracy', 'rate'])
            },
            {
                'name': 'has_boundary',
                'check': lambda t: any(w in t.lower() for w in ['boundary', 'limit', 'constraint', 'maximum', 'minimum'])
            },
            {
                'name': 'has_failure',
                'check': lambda t: any(w in t.lower() for w in ['fail', 'error', 'cannot', 'unable', 'when', 'if'])
            },
        ]
    
    # Evaluate
    score, gate_result = evaluate_response(
        response_text=response_text,
        model=model,
        provider=provider,
        constraints=constraints,
        run_mode=run_mode,
    )
    
    result = {
        "validation": gate_result,
        "score_summary": score.compute_composite(),
        "field_scores": {
            "mechanism": score.cognition.mechanism_score,
            "measurable_outcome": score.cognition.measurable_outcome_score,
            "boundary_condition": score.cognition.boundary_condition_score,
            "failure_condition": score.cognition.failure_condition_score,
        },
        "field_texts": {
            "mechanism": score.cognition.mechanism_text,
            "measurable_outcome": score.cognition.measurable_outcome_text,
            "boundary_condition": score.cognition.boundary_condition_text,
            "failure_condition": score.cognition.failure_condition_text,
        },
        "constraint_violations": score.cognition.constraint_violations,
    }
    
    # Compare with prior if requested
    if compare_prior:
        result["comparison"] = compare_with_prior(score)
    
    return result


def _build_parser() -> argparse.ArgumentParser:
    """Build argument parser."""
    parser = argparse.ArgumentParser(
        description="QAGI Intelligence Score Validator for AGI-model runtime evaluation."
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Evaluate command
    eval_parser = subparsers.add_parser(
        "evaluate",
        help="Evaluate a response and produce QAGI Intelligence Score.",
    )
    eval_parser.add_argument(
        "--response-file",
        type=str,
        help="Path to file containing response text.",
    )
    eval_parser.add_argument(
        "--response-text",
        type=str,
        help="Response text directly (if no file).",
    )
    eval_parser.add_argument(
        "--model",
        type=str,
        default="unknown",
        help="Model identifier.",
    )
    eval_parser.add_argument(
        "--provider",
        type=str,
        default="unknown",
        help="Provider identifier.",
    )
    eval_parser.add_argument(
        "--run-mode",
        type=str,
        choices=["standard", "stress_test", "ablation", "recovery"],
        default="standard",
        help="Run mode for the evaluation.",
    )
    eval_parser.add_argument(
        "--compare-prior",
        action="store_true",
        help="Compare with prior run for regression detection.",
    )
    eval_parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file for results (default: stdout).",
    )
    
    # Compare command
    compare_parser = subparsers.add_parser(
        "compare",
        help="Compare two QAGI score artifacts.",
    )
    compare_parser.add_argument(
        "--current",
        type=str,
        required=True,
        help="Path to current score artifact.",
    )
    compare_parser.add_argument(
        "--prior",
        type=str,
        default=None,
        help="Path to prior score artifact (default: auto-detect).",
    )
    compare_parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file for comparison (default: stdout).",
    )
    
    # Gate command
    gate_parser = subparsers.add_parser(
        "gate",
        help="Check if a score meets release gate thresholds.",
    )
    gate_parser.add_argument(
        "--artifact",
        type=str,
        required=True,
        help="Path to score artifact.",
    )
    gate_parser.add_argument(
        "--thresholds",
        type=str,
        default="default",
        choices=["default", "v1"],
        help="Threshold set to use.",
    )
    gate_parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output file for gate result (default: stdout).",
    )
    
    return parser


def main() -> int:
    """Main entry point."""
    parser = _build_parser()
    args = parser.parse_args()
    
    try:
        if args.command == "evaluate":
            result = run_qagi_validation(
                response_file=args.response_file,
                response_text=args.response_text,
                model=args.model,
                provider=args.provider,
                run_mode=args.run_mode,
                compare_prior=args.compare_prior,
            )
            output = json.dumps(result, indent=2, default=str)
        
        elif args.command == "compare":
            current_score = _load_score_artifact(Path(args.current))
            prior_path = Path(args.prior) if args.prior else None
            comparison = compare_with_prior(current_score, prior_path)
            output = json.dumps(comparison, indent=2, default=str)
        
        elif args.command == "gate":
            score = _load_score_artifact(Path(args.artifact))
            thresholds = THRESHOLDS_V1 if args.thresholds == "v1" else DEFAULT_THRESHOLDS
            passed, failures = score.meets_thresholds(thresholds)
            
            gate_result = {
                "passed": passed,
                "failures": failures,
                "score_version": score.score_version,
                "composite_scores": score.compute_composite(),
                "thresholds_used": thresholds,
            }
            output = json.dumps(gate_result, indent=2, default=str)
        
        else:
            print(f"Unknown command: {args.command}", file=sys.stderr)
            return 1
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output)
        else:
            print(output)
        
        return 0 if "passed" not in output or json.loads(output).get("passed", True) else 1
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())