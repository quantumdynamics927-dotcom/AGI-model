"""Staged Promotion Gates and Targeted Burn-Down.

Implements:
- Staged promotion path (candidate, preprod, prod)
- Required-field-miss per 1000 metric
- Targeted v1.2.1 contract revision for verdict and confidence
- Like-for-like comparison across versions

This completes the production-readiness framework with staged gates.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
from enum import Enum
import json


class PromotionStage(Enum):
    """Staged promotion stages."""
    CANDIDATE = "candidate"  # Improving, safe to test
    PREPROD = "preprod"      # Operationally safe for pre-production
    PROD = "prod"            # Safe to promote to production


@dataclass
class StagedGate:
    """
    Staged promotion gate with different thresholds per stage.
    
    candidate: first_pass >= 0.80, P95 < 3.0s, schema/1K < 150
    preprod: retry_adjusted >= 0.88, schema/1K < 75
    prod: retry_adjusted >= 0.90, schema/1K < 50
    """
    operation: str
    
    # Candidate thresholds
    candidate_min_first_pass: float = 0.80
    candidate_max_p95_latency_s: float = 3.0
    candidate_max_schema_per_1000: float = 150.0
    
    # Preprod thresholds
    preprod_min_retry_adjusted: float = 0.88
    preprod_max_schema_per_1000: float = 75.0
    
    # Prod thresholds
    prod_min_retry_adjusted: float = 0.90
    prod_max_schema_per_1000: float = 50.0
    
    def evaluate(
        self,
        first_pass_validity: float,
        retry_adjusted_success: float,
        p95_latency_s: float,
        schema_invalid_per_1000: float,
    ) -> Dict[str, Any]:
        """Evaluate which promotion stage the operation qualifies for."""
        
        # Check candidate
        candidate_pass = (
            first_pass_validity >= self.candidate_min_first_pass and
            p95_latency_s < self.candidate_max_p95_latency_s and
            schema_invalid_per_1000 < self.candidate_max_schema_per_1000
        )
        
        # Check preprod
        preprod_pass = (
            retry_adjusted_success >= self.preprod_min_retry_adjusted and
            schema_invalid_per_1000 < self.preprod_max_schema_per_1000
        )
        
        # Check prod
        prod_pass = (
            retry_adjusted_success >= self.prod_min_retry_adjusted and
            schema_invalid_per_1000 < self.prod_max_schema_per_1000
        )
        
        # Determine stage
        if prod_pass:
            stage = PromotionStage.PROD
        elif preprod_pass:
            stage = PromotionStage.PREPROD
        elif candidate_pass:
            stage = PromotionStage.CANDIDATE
        else:
            stage = None
        
        return {
            "operation": self.operation,
            "stage": stage.value if stage else "none",
            "checks": {
                "candidate": {
                    "pass": candidate_pass,
                    "first_pass_validity": {
                        "value": first_pass_validity,
                        "threshold": self.candidate_min_first_pass,
                        "pass": first_pass_validity >= self.candidate_min_first_pass,
                    },
                    "p95_latency": {
                        "value": p95_latency_s,
                        "threshold": self.candidate_max_p95_latency_s,
                        "pass": p95_latency_s < self.candidate_max_p95_latency_s,
                    },
                    "schema_per_1000": {
                        "value": schema_invalid_per_1000,
                        "threshold": self.candidate_max_schema_per_1000,
                        "pass": schema_invalid_per_1000 < self.candidate_max_schema_per_1000,
                    },
                },
                "preprod": {
                    "pass": preprod_pass,
                    "retry_adjusted_success": {
                        "value": retry_adjusted_success,
                        "threshold": self.preprod_min_retry_adjusted,
                        "pass": retry_adjusted_success >= self.preprod_min_retry_adjusted,
                    },
                    "schema_per_1000": {
                        "value": schema_invalid_per_1000,
                        "threshold": self.preprod_max_schema_per_1000,
                        "pass": schema_invalid_per_1000 < self.preprod_max_schema_per_1000,
                    },
                },
                "prod": {
                    "pass": prod_pass,
                    "retry_adjusted_success": {
                        "value": retry_adjusted_success,
                        "threshold": self.prod_min_retry_adjusted,
                        "pass": retry_adjusted_success >= self.prod_min_retry_adjusted,
                    },
                    "schema_per_1000": {
                        "value": schema_invalid_per_1000,
                        "threshold": self.prod_max_schema_per_1000,
                        "pass": schema_invalid_per_1000 < self.prod_max_schema_per_1000,
                    },
                },
            },
            "summary": self._generate_summary(stage, candidate_pass, preprod_pass, prod_pass),
        }
    
    def _generate_summary(
        self,
        stage: Optional[PromotionStage],
        candidate_pass: bool,
        preprod_pass: bool,
        prod_pass: bool,
    ) -> str:
        if stage == PromotionStage.PROD:
            return f"✅ {self.operation} qualifies for PROD promotion."
        elif stage == PromotionStage.PREPROD:
            return f"⚠️ {self.operation} qualifies for PREPROD (not yet PROD)."
        elif stage == PromotionStage.CANDIDATE:
            return f"📋 {self.operation} qualifies for CANDIDATE (improving, safe to test)."
        else:
            return f"❌ {self.operation} does not qualify for any promotion stage."


@dataclass
class RequiredFieldMetrics:
    """
    Required-field-miss per 1000 metric.
    
    Tracks structural failures (missing required fields) separately
    from semantic edge cases.
    """
    required_field_misses: Dict[str, int] = field(default_factory=dict)
    total_executions: int = 0
    
    def record_miss(self, field: str) -> None:
        """Record a required field miss."""
        self.required_field_misses[field] = self.required_field_misses.get(field, 0) + 1
    
    def get_miss_rate_per_1000(self, field: Optional[str] = None) -> float:
        """Get miss rate per 1000 for a specific field or all fields."""
        if self.total_executions == 0:
            return 0.0
        
        if field:
            count = self.required_field_misses.get(field, 0)
        else:
            count = sum(self.required_field_misses.values())
        
        return (count / self.total_executions) * 1000
    
    def get_top_miss_fields(self, n: int = 3) -> List[Tuple[str, int]]:
        """Get top-N fields by miss count."""
        sorted_fields = sorted(self.required_field_misses.items(), key=lambda x: x[1], reverse=True)
        return sorted_fields[:n]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "required_field_misses": self.required_field_misses,
            "total_executions": self.total_executions,
            "total_miss_rate_per_1000": self.get_miss_rate_per_1000(),
            "top_miss_fields": self.get_top_miss_fields(3),
        }


@dataclass
class TargetedContractRevision:
    """
    Targeted contract revision for specific failure modes.
    
    v1.2.1: Focus on verdict presence and confidence bounds
    """
    version: str
    target_fields: List[str]
    changes: List[str]
    expected_improvement: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "target_fields": self.target_fields,
            "changes": self.changes,
            "expected_improvement": self.expected_improvement,
        }


# v1.2.1 Contract Revision
V121_CONTRACT_REVISION = TargetedContractRevision(
    version="1.2.1",
    target_fields=["verdict", "confidence"],
    changes=[
        "Added explicit verdict field requirement at top of prompt",
        "Added verdict enum examples in first sentence",
        "Added confidence bounds (0.0-1.0) with example values",
        "Added anti-pattern: 'verdict' must be one of: pass, fail, warning",
        "Added anti-pattern: 'confidence' must be between 0.0 and 1.0",
        "Added validation hint: 'Check verdict field before confidence'",
    ],
    expected_improvement={
        "verdict_miss_rate": 0.5,  # Expect 50% reduction
        "confidence_bounds_rate": 0.6,  # Expect 60% reduction
    },
)


# v1.2.2 Contract Revision - Narrow scope for verdict and confidence
V122_CONTRACT_REVISION = TargetedContractRevision(
    version="1.2.2",
    target_fields=["verdict", "confidence"],
    changes=[
        # Explicit instruction block near end of prompt
        "Added instruction block: 'Return a JSON object only'",
        "Added instruction: 'verdict is required and must be one of: healthy, warning, fail'",
        "Added instruction: 'confidence is required and must be a number in the allowed range'",
        # Positive and negative examples
        "Added positive example: {\"verdict\": \"healthy\", \"confidence\": 0.95}",
        "Added negative example (missing verdict): {\"confidence\": 0.9} - INVALID",
        "Added negative example (invalid verdict): {\"verdict\": \"pass\", \"confidence\": 0.9} - INVALID",
        "Added negative example (confidence out of range): {\"verdict\": \"healthy\", \"confidence\": 1.5} - INVALID",
        # Checklist immediately before generation
        "Added pre-generation checklist: 'Required fields: verdict, confidence'",
        "Added checklist item: 'verdict ∈ {healthy, warning, fail}'",
        "Added checklist item: 'confidence ∈ [0.0, 1.0]'",
    ],
    expected_improvement={
        "verdict_miss_rate": 0.6,  # Expect 60% reduction (from 5/100 to <3/100)
        "confidence_bounds_rate": 0.7,  # Expect 70% reduction (from 3/100 to <2/100)
        "schema_per_1000": 0.0625,  # Target: 80 → 75 to reach PREPROD
    },
)


@dataclass
class LikeForLikeComparison:
    """
    Like-for-like comparison across versions on same workload.
    
    Ensures fair comparison by using identical test cases.
    """
    test_cases: List[Dict[str, Any]] = field(default_factory=list)
    version_results: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    def add_test_case(self, input_data: Dict[str, Any], expected_output: Dict[str, Any]) -> None:
        """Add a test case for comparison."""
        import uuid
        self.test_cases.append({
            "id": str(uuid.uuid4())[:8],
            "input": input_data,
            "expected": expected_output,
        })
    
    def record_version_result(
        self,
        version: str,
        results: List[Dict[str, Any]],
    ) -> None:
        """Record results for a version on all test cases."""
        self.version_results[version] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "results": results,
            "pass_count": sum(1 for r in results if r.get("valid", False)),
            "fail_count": sum(1 for r in results if not r.get("valid", False)),
            "pass_rate": sum(1 for r in results if r.get("valid", False)) / len(results) if results else 0.0,
        }
    
    def get_comparison_table(self) -> List[Dict[str, Any]]:
        """Get comparison table across versions."""
        table = []
        for version, data in sorted(self.version_results.items()):
            table.append({
                "version": version,
                "pass_count": data["pass_count"],
                "fail_count": data["fail_count"],
                "pass_rate": data["pass_rate"],
                "timestamp": data["timestamp"],
            })
        return table
    
    def get_improvement(self, from_version: str, to_version: str) -> Dict[str, Any]:
        """Calculate improvement between versions."""
        if from_version not in self.version_results or to_version not in self.version_results:
            return {"error": "Version not found"}
        
        from_rate = self.version_results[from_version]["pass_rate"]
        to_rate = self.version_results[to_version]["pass_rate"]
        
        return {
            "from_version": from_version,
            "to_version": to_version,
            "from_pass_rate": from_rate,
            "to_pass_rate": to_rate,
            "absolute_improvement": to_rate - from_rate,
            "relative_improvement": (to_rate - from_rate) / from_rate if from_rate > 0 else 0.0,
        }


class StagedReadiness:
    """
    Staged production readiness with targeted burn-down.
    
    Features:
    - Staged promotion gates (candidate, preprod, prod)
    - Required-field-miss per 1000 metric
    - Targeted contract revision tracking
    - Like-for-like comparison
    """
    
    def __init__(
        self,
        prompt_version: str = "1.2.1",
        model_id: str = "qwen3-coder-next:cloud",
    ):
        self.prompt_version = prompt_version
        self.model_id = model_id
        
        # Components
        self.staged_gate = StagedGate(operation="vae_checkpoint_validation")
        self.required_field_metrics = RequiredFieldMetrics()
        self.comparison = LikeForLikeComparison()
        
        # Metrics
        self.first_pass_successes: int = 0
        self.first_pass_failures: int = 0
        self.retry_successes: int = 0
        self.retry_failures: int = 0
        self.latencies: List[float] = []
        self.schema_invalid_count: int = 0
        
        # Dedicated metrics for v1.2.2
        self.verdict_miss_count: int = 0
        self.confidence_bounds_violation_count: int = 0
        
        # Version history
        self.version_metrics: Dict[str, Dict[str, Any]] = {}
    
    def record_execution(
        self,
        first_pass_success: bool,
        retry_success: bool = False,
        latency_s: float = 0.0,
        schema_invalid: bool = False,
    ) -> None:
        """Record an execution outcome."""
        self.required_field_metrics.total_executions += 1
        
        if first_pass_success:
            self.first_pass_successes += 1
        else:
            self.first_pass_failures += 1
            if retry_success:
                self.retry_successes += 1
            else:
                self.retry_failures += 1
        
        self.latencies.append(latency_s)
        
        if schema_invalid:
            self.schema_invalid_count += 1
    
    def record_required_field_miss(self, field: str) -> None:
        """Record a required field miss."""
        self.required_field_metrics.record_miss(field)
        
        # Track dedicated metrics for verdict and confidence
        if field == "verdict":
            self.verdict_miss_count += 1
        elif field == "confidence":
            self.confidence_bounds_violation_count += 1
    
    def record_confidence_bounds_violation(self) -> None:
        """Record a confidence bounds violation."""
        self.confidence_bounds_violation_count += 1
    
    def get_first_pass_validity(self) -> float:
        """Get first-pass validity rate."""
        total = self.first_pass_successes + self.first_pass_failures
        if total == 0:
            return 0.0
        return self.first_pass_successes / total
    
    def get_retry_adjusted_success(self) -> float:
        """Get retry-adjusted success rate."""
        total = self.first_pass_successes + self.first_pass_failures + self.retry_successes + self.retry_failures
        if total == 0:
            return 0.0
        return (self.first_pass_successes + self.retry_successes) / total
    
    def get_p95_latency(self) -> float:
        """Get P95 latency."""
        if not self.latencies:
            return 0.0
        sorted_latencies = sorted(self.latencies)
        index = int(len(sorted_latencies) * 0.95)
        return sorted_latencies[min(index, len(sorted_latencies) - 1)]
    
    def get_schema_invalid_per_1000(self) -> float:
        """Get schema-invalid rate per 1000."""
        total = self.required_field_metrics.total_executions
        if total == 0:
            return 0.0
        return (self.schema_invalid_count / total) * 1000
    
    def get_verdict_miss_per_1000(self) -> float:
        """Get verdict miss rate per 1000."""
        total = self.required_field_metrics.total_executions
        if total == 0:
            return 0.0
        return (self.verdict_miss_count / total) * 1000
    
    def get_confidence_bounds_per_1000(self) -> float:
        """Get confidence bounds violation rate per 1000."""
        total = self.required_field_metrics.total_executions
        if total == 0:
            return 0.0
        return (self.confidence_bounds_violation_count / total) * 1000
    
    def evaluate_staged_gate(self) -> Dict[str, Any]:
        """Evaluate staged promotion gate."""
        return self.staged_gate.evaluate(
            first_pass_validity=self.get_first_pass_validity(),
            retry_adjusted_success=self.get_retry_adjusted_success(),
            p95_latency_s=self.get_p95_latency(),
            schema_invalid_per_1000=self.get_schema_invalid_per_1000(),
        )
    
    def save_version_metrics(self) -> None:
        """Save current version metrics to history."""
        self.version_metrics[self.prompt_version] = {
            "prompt_version": self.prompt_version,
            "model_id": self.model_id,
            "first_pass_validity": self.get_first_pass_validity(),
            "retry_adjusted_success": self.get_retry_adjusted_success(),
            "p95_latency_s": self.get_p95_latency(),
            "schema_invalid_per_1000": self.get_schema_invalid_per_1000(),
            "verdict_miss_per_1000": self.get_verdict_miss_per_1000(),
            "confidence_bounds_per_1000": self.get_confidence_bounds_per_1000(),
            "required_field_miss_per_1000": self.required_field_metrics.get_miss_rate_per_1000(),
            "top_miss_fields": self.required_field_metrics.get_top_miss_fields(3),
            "total_executions": self.required_field_metrics.total_executions,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    
    def get_version_table(self) -> List[Dict[str, Any]]:
        """Get per-version metrics table."""
        return list(self.version_metrics.values())
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status."""
        return {
            "prompt_version": self.prompt_version,
            "model_id": self.model_id,
            "staged_gate": self.evaluate_staged_gate(),
            "required_field_metrics": self.required_field_metrics.to_dict(),
            "metrics": {
                "first_pass_validity": self.get_first_pass_validity(),
                "retry_adjusted_success": self.get_retry_adjusted_success(),
                "p95_latency_s": self.get_p95_latency(),
                "schema_invalid_per_1000": self.get_schema_invalid_per_1000(),
                "verdict_miss_per_1000": self.get_verdict_miss_per_1000(),
                "confidence_bounds_per_1000": self.get_confidence_bounds_per_1000(),
                "required_field_miss_per_1000": self.required_field_metrics.get_miss_rate_per_1000(),
            },
            "version_table": self.get_version_table(),
        }
    
    def compare_versions(self, from_version: str, to_version: str) -> Dict[str, Any]:
        """Compare two versions on same metrics."""
        if from_version not in self.version_metrics or to_version not in self.version_metrics:
            return {"error": "Version not found", "available_versions": list(self.version_metrics.keys())}
        
        from_data = self.version_metrics[from_version]
        to_data = self.version_metrics[to_version]
        
        metrics_to_compare = [
            "first_pass_validity",
            "retry_adjusted_success",
            "p95_latency_s",
            "schema_invalid_per_1000",
            "verdict_miss_per_1000",
            "confidence_bounds_per_1000",
        ]
        
        comparison = {
            "from_version": from_version,
            "to_version": to_version,
            "metrics": {},
            "verdict": None,
        }
        
        all_improved = True
        for metric in metrics_to_compare:
            from_val = from_data.get(metric, 0.0)
            to_val = to_data.get(metric, 0.0)
            
            # For latency and error rates, lower is better
            if metric in ["p95_latency_s", "schema_invalid_per_1000", "verdict_miss_per_1000", "confidence_bounds_per_1000"]:
                improved = to_val < from_val
                delta = from_val - to_val
            else:
                improved = to_val > from_val
                delta = to_val - from_val
            
            comparison["metrics"][metric] = {
                "from": from_val,
                "to": to_val,
                "delta": delta,
                "improved": improved,
            }
            
            if not improved:
                all_improved = False
        
        comparison["verdict"] = "✅ IMPROVED" if all_improved else "⚠️ MIXED"
        return comparison


def create_staged_readiness(
    prompt_version: str = "1.2.1",
    model_id: str = "qwen3-coder-next:cloud",
) -> StagedReadiness:
    """Create a staged readiness instance."""
    return StagedReadiness(
        prompt_version=prompt_version,
        model_id=model_id,
    )


# Export
__all__ = [
    "PromotionStage",
    "StagedGate",
    "RequiredFieldMetrics",
    "TargetedContractRevision",
    "V121_CONTRACT_REVISION",
    "V122_CONTRACT_REVISION",
    "LikeForLikeComparison",
    "StagedReadiness",
    "create_staged_readiness",
]


if __name__ == "__main__":
    import json
    
    print("=" * 80)
    print("STAGED PROMOTION GATES AND TARGETED BURN-DOWN")
    print("=" * 80)
    
    readiness = create_staged_readiness(
        prompt_version="1.2.1",
        model_id="qwen3-coder-next:cloud",
    )
    
    # Show v1.2.1 contract revision
    print("\n" + "=" * 80)
    print("v1.2.1 CONTRACT REVISION")
    print("=" * 80)
    print(f"\nVersion: {V121_CONTRACT_REVISION.version}")
    print(f"Target Fields: {V121_CONTRACT_REVISION.target_fields}")
    print(f"\nChanges:")
    for change in V121_CONTRACT_REVISION.changes:
        print(f"  - {change}")
    print(f"\nExpected Improvement:")
    for field, improvement in V121_CONTRACT_REVISION.expected_improvement.items():
        print(f"  {field}: {improvement:.0%} reduction")
    
    # Simulate versions
    print("\n" + "=" * 80)
    print("SIMULATING VERSIONS")
    print("=" * 80)
    
    # Version 1.2.0 (before targeted fix)
    readiness.prompt_version = "1.2.0"
    for _ in range(85):
        readiness.record_execution(first_pass_success=True, latency_s=1.0)
    for _ in range(10):
        readiness.record_execution(first_pass_success=False, retry_success=True, latency_s=1.8, schema_invalid=True)
        readiness.record_required_field_miss("verdict")
    for _ in range(5):
        readiness.record_execution(first_pass_success=False, retry_success=False, latency_s=2.5, schema_invalid=True)
        readiness.record_required_field_miss("confidence")
    
    readiness.save_version_metrics()
    
    # Version 1.2.1 (after targeted fix)
    readiness.prompt_version = "1.2.1"
    readiness.first_pass_successes = 0
    readiness.first_pass_failures = 0
    readiness.retry_successes = 0
    readiness.retry_failures = 0
    readiness.latencies = []
    readiness.schema_invalid_count = 0
    readiness.required_field_metrics = RequiredFieldMetrics()
    
    for _ in range(92):
        readiness.record_execution(first_pass_success=True, latency_s=0.9)
    for _ in range(5):
        readiness.record_execution(first_pass_success=False, retry_success=True, latency_s=1.5, schema_invalid=True)
        readiness.record_required_field_miss("verdict")
    for _ in range(3):
        readiness.record_execution(first_pass_success=False, retry_success=False, latency_s=2.0, schema_invalid=True)
        readiness.record_required_field_miss("confidence")
    
    readiness.save_version_metrics()
    
    # Show version table
    print("\n" + "=" * 80)
    print("PER-VERSION METRICS TABLE")
    print("=" * 80)
    
    version_table = readiness.get_version_table()
    print(f"\n{'Version':<10} {'First-Pass':<12} {'Retry-Adj':<12} {'P95 (s)':<10} {'Schema/1K':<12} {'ReqMiss/1K':<12} {'Stage'}")
    print("-" * 90)
    
    for v in version_table:
        # Evaluate stage for this version
        gate = readiness.staged_gate.evaluate(
            v["first_pass_validity"],
            v["retry_adjusted_success"],
            v["p95_latency_s"],
            v["schema_invalid_per_1000"],
        )
        stage = gate["stage"]
        
        print(f"{v['prompt_version']:<10} {v['first_pass_validity']:<12.2%} {v['retry_adjusted_success']:<12.2%} {v['p95_latency_s']:<10.2f} {v['schema_invalid_per_1000']:<12.1f} {v['required_field_miss_per_1000']:<12.1f} {stage}")
    
    # Show required field metrics
    print("\n" + "=" * 80)
    print("REQUIRED FIELD METRICS")
    print("=" * 80)
    
    rfm = readiness.required_field_metrics.to_dict()
    print(f"\nTotal Miss Rate: {rfm['total_miss_rate_per_1000']:.1f}/1000")
    print(f"Top Miss Fields: {rfm['top_miss_fields']}")
    
    # Show staged gate
    print("\n" + "=" * 80)
    print("STAGED PROMOTION GATE")
    print("=" * 80)
    
    gate = readiness.evaluate_staged_gate()
    print(f"\n{gate['summary']}")
    print(f"\nStage: {gate['stage'].upper()}")
    
    print(f"\nCandidate Gate:")
    for name, check in gate["checks"]["candidate"].items():
        if name == "pass":
            continue
        status = "✅" if check["pass"] else "❌"
        print(f"  {status} {name}: {check['value']:.2f} {'>=' if 'validity' in name else '<'} {check['threshold']}")
    
    print(f"\nPreprod Gate:")
    for name, check in gate["checks"]["preprod"].items():
        if name == "pass":
            continue
        status = "✅" if check["pass"] else "❌"
        print(f"  {status} {name}: {check['value']:.2f} {'>=' if 'success' in name else '<'} {check['threshold']}")
    
    print(f"\nProd Gate:")
    for name, check in gate["checks"]["prod"].items():
        if name == "pass":
            continue
        status = "✅" if check["pass"] else "❌"
        print(f"  {status} {name}: {check['value']:.2f} {'>=' if 'success' in name else '<'} {check['threshold']}")
    
    # Show improvement
    print("\n" + "=" * 80)
    print("IMPROVEMENT FROM v1.2.0 TO v1.2.1")
    print("=" * 80)
    
    v120 = readiness.version_metrics.get("1.2.0", {})
    v121 = readiness.version_metrics.get("1.2.1", {})
    
    if v120 and v121:
        print(f"\nFirst-Pass Validity: {v120['first_pass_validity']:.2%} → {v121['first_pass_validity']:.2%} ({(v121['first_pass_validity'] - v120['first_pass_validity']):+.2%})")
        print(f"Retry-Adjusted Success: {v120['retry_adjusted_success']:.2%} → {v121['retry_adjusted_success']:.2%} ({(v121['retry_adjusted_success'] - v120['retry_adjusted_success']):+.2%})")
        print(f"P95 Latency: {v120['p95_latency_s']:.2f}s → {v121['p95_latency_s']:.2f}s ({(v121['p95_latency_s'] - v120['p95_latency_s']):+.2f}s)")
        print(f"Schema/1K: {v120['schema_invalid_per_1000']:.1f} → {v121['schema_invalid_per_1000']:.1f} ({(v121['schema_invalid_per_1000'] - v120['schema_invalid_per_1000']):+.1f})")
        print(f"ReqMiss/1K: {v120['required_field_miss_per_1000']:.1f} → {v121['required_field_miss_per_1000']:.1f} ({(v121['required_field_miss_per_1000'] - v120['required_field_miss_per_1000']):+.1f})")
    
    # Final status
    print("\n" + "=" * 80)
    print("FINAL STATUS")
    print("=" * 80)
    
    status = readiness.get_status()
    print(f"\n{json.dumps(status, indent=2)}")