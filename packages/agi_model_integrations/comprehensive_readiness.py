"""Comprehensive Production Readiness with Error Budgets and Schema Heatmap.

Extends production burn-down with:
- First-pass release gate (first_pass_validity >= 0.80)
- Error budget per prompt version
- Schema-clause heatmap (required, enum, minimum/maximum, additionalProperties)
- Live-traffic regression sampling
- Per-version metrics table

This completes the transition to evidence-based production readiness.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
import json


@dataclass
class SchemaClauseFailure:
    """Failure mapped to specific JSON Schema clause."""
    clause_type: str  # required, enum, minimum, maximum, additionalProperties, type
    field: str
    error: str
    count: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "clause_type": self.clause_type,
            "field": self.field,
            "error": self.error,
            "count": self.count,
        }


@dataclass
class SchemaHeatmap:
    """
    Schema-clause heatmap mapping failures to JSON Schema clauses.
    
    Maps failures to:
    - required: Missing required fields
    - enum: Invalid enum values
    - minimum/maximum: Out of range values
    - additionalProperties: Extra fields not in schema
    - type: Type mismatches
    """
    required_failures: Dict[str, int] = field(default_factory=dict)
    enum_failures: Dict[str, int] = field(default_factory=dict)
    minimum_failures: Dict[str, int] = field(default_factory=dict)
    maximum_failures: Dict[str, int] = field(default_factory=dict)
    additional_properties_failures: Dict[str, int] = field(default_factory=dict)
    type_failures: Dict[str, int] = field(default_factory=dict)
    
    def record(self, clause_type: str, field: str, error: str) -> None:
        """Record a failure for a schema clause."""
        if clause_type == "required":
            self.required_failures[field] = self.required_failures.get(field, 0) + 1
        elif clause_type == "enum":
            self.enum_failures[field] = self.enum_failures.get(field, 0) + 1
        elif clause_type == "minimum":
            self.minimum_failures[field] = self.minimum_failures.get(field, 0) + 1
        elif clause_type == "maximum":
            self.maximum_failures[field] = self.maximum_failures.get(field, 0) + 1
        elif clause_type == "additionalProperties":
            self.additional_properties_failures[field] = self.additional_properties_failures.get(field, 0) + 1
        elif clause_type == "type":
            self.type_failures[field] = self.type_failures.get(field, 0) + 1
    
    def get_hotspots(self, n: int = 3) -> List[Dict[str, Any]]:
        """Get top-N failure hotspots across all clauses."""
        all_failures = []
        
        for field, count in self.required_failures.items():
            all_failures.append({"clause": "required", "field": field, "count": count})
        for field, count in self.enum_failures.items():
            all_failures.append({"clause": "enum", "field": field, "count": count})
        for field, count in self.minimum_failures.items():
            all_failures.append({"clause": "minimum", "field": field, "count": count})
        for field, count in self.maximum_failures.items():
            all_failures.append({"clause": "maximum", "field": field, "count": count})
        for field, count in self.additional_properties_failures.items():
            all_failures.append({"clause": "additionalProperties", "field": field, "count": count})
        for field, count in self.type_failures.items():
            all_failures.append({"clause": "type", "field": field, "count": count})
        
        sorted_failures = sorted(all_failures, key=lambda x: x["count"], reverse=True)
        return sorted_failures[:n]
    
    def get_clause_summary(self) -> Dict[str, int]:
        """Get summary of failures by clause type."""
        return {
            "required": sum(self.required_failures.values()),
            "enum": sum(self.enum_failures.values()),
            "minimum": sum(self.minimum_failures.values()),
            "maximum": sum(self.maximum_failures.values()),
            "additionalProperties": sum(self.additional_properties_failures.values()),
            "type": sum(self.type_failures.values()),
        }
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "required": self.required_failures,
            "enum": self.enum_failures,
            "minimum": self.minimum_failures,
            "maximum": self.maximum_failures,
            "additionalProperties": self.additional_properties_failures,
            "type": self.type_failures,
            "hotspots": self.get_hotspots(5),
            "clause_summary": self.get_clause_summary(),
        }


@dataclass
class ErrorBudget:
    """
    Error budget per prompt version.
    
    Defines maximum allowed failures per 1000 executions.
    """
    prompt_version: str
    max_schema_invalid_per_1000: int = 50
    max_transport_failures_per_1000: int = 30
    max_first_pass_failures_per_1000: int = 200
    
    # Current counts
    schema_invalid_count: int = 0
    transport_failure_count: int = 0
    first_pass_failure_count: int = 0
    total_executions: int = 0
    
    def record_execution(
        self,
        schema_invalid: bool = False,
        transport_failure: bool = False,
        first_pass_failure: bool = False,
    ) -> None:
        """Record an execution outcome."""
        self.total_executions += 1
        if schema_invalid:
            self.schema_invalid_count += 1
        if transport_failure:
            self.transport_failure_count += 1
        if first_pass_failure:
            self.first_pass_failure_count += 1
    
    def get_schema_invalid_rate(self) -> float:
        """Get schema-invalid rate per 1000."""
        if self.total_executions == 0:
            return 0.0
        return (self.schema_invalid_count / self.total_executions) * 1000
    
    def get_transport_failure_rate(self) -> float:
        """Get transport failure rate per 1000."""
        if self.total_executions == 0:
            return 0.0
        return (self.transport_failure_count / self.total_executions) * 1000
    
    def get_first_pass_failure_rate(self) -> float:
        """Get first-pass failure rate per 1000."""
        if self.total_executions == 0:
            return 0.0
        return (self.first_pass_failure_count / self.total_executions) * 1000
    
    def is_budget_exceeded(self) -> bool:
        """Check if any budget is exceeded."""
        return (
            self.get_schema_invalid_rate() > self.max_schema_invalid_per_1000 or
            self.get_transport_failure_rate() > self.max_transport_failures_per_1000 or
            self.get_first_pass_failure_rate() > self.max_first_pass_failures_per_1000
        )
    
    def get_budget_status(self) -> Dict[str, Any]:
        """Get detailed budget status."""
        return {
            "prompt_version": self.prompt_version,
            "schema_invalid": {
                "count": self.schema_invalid_count,
                "rate_per_1000": self.get_schema_invalid_rate(),
                "budget": self.max_schema_invalid_per_1000,
                "remaining": max(0, self.max_schema_invalid_per_1000 - self.get_schema_invalid_rate()),
                "exceeded": self.get_schema_invalid_rate() > self.max_schema_invalid_per_1000,
            },
            "transport_failures": {
                "count": self.transport_failure_count,
                "rate_per_1000": self.get_transport_failure_rate(),
                "budget": self.max_transport_failures_per_1000,
                "remaining": max(0, self.max_transport_failures_per_1000 - self.get_transport_failure_rate()),
                "exceeded": self.get_transport_failure_rate() > self.max_transport_failures_per_1000,
            },
            "first_pass_failures": {
                "count": self.first_pass_failure_count,
                "rate_per_1000": self.get_first_pass_failure_rate(),
                "budget": self.max_first_pass_failures_per_1000,
                "remaining": max(0, self.max_first_pass_failures_per_1000 - self.get_first_pass_failure_rate()),
                "exceeded": self.get_first_pass_failure_rate() > self.max_first_pass_failures_per_1000,
            },
            "total_executions": self.total_executions,
            "budget_exceeded": self.is_budget_exceeded(),
        }


@dataclass
class FirstPassReleaseGate:
    """
    First-pass release gate.
    
    A system cannot pass readiness purely by getting better at retries.
    """
    operation: str
    min_first_pass_validity: float = 0.80
    min_retry_adjusted_success: float = 0.90
    max_p95_latency_s: float = 3.0
    max_schema_invalid_per_1000: int = 50
    
    def evaluate(
        self,
        first_pass_validity: float,
        retry_adjusted_success: float,
        p95_latency_s: float,
        schema_invalid_per_1000: float,
    ) -> Dict[str, Any]:
        """Evaluate if operation passes first-pass release gate."""
        checks = {
            "first_pass_validity": {
                "value": first_pass_validity,
                "threshold": self.min_first_pass_validity,
                "pass": first_pass_validity >= self.min_first_pass_validity,
            },
            "retry_adjusted_success": {
                "value": retry_adjusted_success,
                "threshold": self.min_retry_adjusted_success,
                "pass": retry_adjusted_success >= self.min_retry_adjusted_success,
            },
            "p95_latency": {
                "value": p95_latency_s,
                "threshold": self.max_p95_latency_s,
                "pass": p95_latency_s < self.max_p95_latency_s,
            },
            "schema_invalid_per_1000": {
                "value": schema_invalid_per_1000,
                "threshold": self.max_schema_invalid_per_1000,
                "pass": schema_invalid_per_1000 < self.max_schema_invalid_per_1000,
            },
        }
        
        all_pass = all(c["pass"] for c in checks.values())
        
        return {
            "operation": self.operation,
            "stable": all_pass,
            "checks": checks,
            "summary": self._generate_summary(checks, all_pass),
        }
    
    def _generate_summary(self, checks: Dict[str, Any], all_pass: bool) -> str:
        if all_pass:
            return f"✅ {self.operation} is STABLE and passes first-pass release gate."
        
        failures = [name for name, check in checks.items() if not check["pass"]]
        return f"❌ {self.operation} is NOT STABLE. Failed checks: {', '.join(failures)}"


@dataclass
class LiveTrafficSample:
    """A live traffic sample for regression testing."""
    sample_id: str
    timestamp: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    validation_result: Dict[str, Any]
    prompt_version: str
    model_id: str
    first_pass: bool
    retry_count: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "sample_id": self.sample_id,
            "timestamp": self.timestamp,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "validation_result": self.validation_result,
            "prompt_version": self.prompt_version,
            "model_id": self.model_id,
            "first_pass": self.first_pass,
            "retry_count": self.retry_count,
        }


@dataclass
class VersionMetrics:
    """Metrics for a single prompt version."""
    prompt_version: str
    first_pass_validity: float
    retry_adjusted_success: float
    p95_latency_s: float
    top_3_schema_failures: List[Tuple[str, int]]
    total_executions: int
    schema_invalid_per_1000: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "prompt_version": self.prompt_version,
            "first_pass_validity": self.first_pass_validity,
            "retry_adjusted_success": self.retry_adjusted_success,
            "p95_latency_s": self.p95_latency_s,
            "top_3_schema_failures": self.top_3_schema_failures,
            "total_executions": self.total_executions,
            "schema_invalid_per_1000": self.schema_invalid_per_1000,
        }


class ComprehensiveReadiness:
    """
    Comprehensive production readiness with error budgets and schema heatmap.
    
    Features:
    - First-pass release gate
    - Error budget per prompt version
    - Schema-clause heatmap
    - Live-traffic regression sampling
    - Per-version metrics table
    """
    
    def __init__(
        self,
        prompt_version: str = "1.2.0",
        model_id: str = "qwen3-coder-next:cloud",
    ):
        self.prompt_version = prompt_version
        self.model_id = model_id
        
        # Components
        self.schema_heatmap = SchemaHeatmap()
        self.error_budget = ErrorBudget(prompt_version=prompt_version)
        self.release_gate = FirstPassReleaseGate(
            operation="vae_checkpoint_validation",
            min_first_pass_validity=0.80,
            min_retry_adjusted_success=0.90,
            max_p95_latency_s=3.0,
            max_schema_invalid_per_1000=50,
        )
        
        # Metrics
        self.first_pass_successes: int = 0
        self.first_pass_failures: int = 0
        self.retry_successes: int = 0
        self.retry_failures: int = 0
        self.latencies: List[float] = []
        
        # Live traffic samples
        self.live_samples: List[LiveTrafficSample] = []
        
        # Version history
        self.version_metrics: Dict[str, VersionMetrics] = {}
    
    def record_execution(
        self,
        first_pass_success: bool,
        retry_success: bool = False,
        latency_s: float = 0.0,
        schema_invalid: bool = False,
        transport_failure: bool = False,
    ) -> None:
        """Record an execution outcome."""
        if first_pass_success:
            self.first_pass_successes += 1
        else:
            self.first_pass_failures += 1
            if retry_success:
                self.retry_successes += 1
            else:
                self.retry_failures += 1
        
        self.latencies.append(latency_s)
        
        self.error_budget.record_execution(
            schema_invalid=schema_invalid,
            transport_failure=transport_failure,
            first_pass_failure=not first_pass_success,
        )
    
    def record_schema_failure(
        self,
        clause_type: str,
        field: str,
        error: str,
    ) -> None:
        """Record a schema clause failure."""
        self.schema_heatmap.record(clause_type, field, error)
    
    def record_live_sample(
        self,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        validation_result: Dict[str, Any],
        first_pass: bool,
        retry_count: int,
    ) -> LiveTrafficSample:
        """Record a live traffic sample for regression."""
        import uuid
        sample = LiveTrafficSample(
            sample_id=str(uuid.uuid4())[:8],
            timestamp=datetime.now(timezone.utc).isoformat(),
            input_data=input_data,
            output_data=output_data,
            validation_result=validation_result,
            prompt_version=self.prompt_version,
            model_id=self.model_id,
            first_pass=first_pass,
            retry_count=retry_count,
        )
        self.live_samples.append(sample)
        return sample
    
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
        return self.error_budget.get_schema_invalid_rate()
    
    def evaluate_release_gate(self) -> Dict[str, Any]:
        """Evaluate first-pass release gate."""
        return self.release_gate.evaluate(
            first_pass_validity=self.get_first_pass_validity(),
            retry_adjusted_success=self.get_retry_adjusted_success(),
            p95_latency_s=self.get_p95_latency(),
            schema_invalid_per_1000=self.get_schema_invalid_per_1000(),
        )
    
    def get_version_metrics(self) -> VersionMetrics:
        """Get metrics for current prompt version."""
        hotspots = self.schema_heatmap.get_hotspots(3)
        top_3 = [(f"{h['clause']}:{h['field']}", h['count']) for h in hotspots]
        
        return VersionMetrics(
            prompt_version=self.prompt_version,
            first_pass_validity=self.get_first_pass_validity(),
            retry_adjusted_success=self.get_retry_adjusted_success(),
            p95_latency_s=self.get_p95_latency(),
            top_3_schema_failures=top_3,
            total_executions=self.error_budget.total_executions,
            schema_invalid_per_1000=self.get_schema_invalid_per_1000(),
        )
    
    def save_version_metrics(self) -> None:
        """Save current version metrics to history."""
        metrics = self.get_version_metrics()
        self.version_metrics[self.prompt_version] = metrics
    
    def get_version_table(self) -> List[Dict[str, Any]]:
        """Get per-version metrics table."""
        return [v.to_dict() for v in self.version_metrics.values()]
    
    def get_live_samples_for_regression(self, n: int = 10) -> List[LiveTrafficSample]:
        """Get live samples for regression testing."""
        # Prioritize failures
        failures = [s for s in self.live_samples if not s.validation_result.get("valid", True)]
        successes = [s for s in self.live_samples if s.validation_result.get("valid", True)]
        
        # Return failures first, then successes
        return (failures + successes)[:n]
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status."""
        return {
            "prompt_version": self.prompt_version,
            "model_id": self.model_id,
            "release_gate": self.evaluate_release_gate(),
            "error_budget": self.error_budget.get_budget_status(),
            "schema_heatmap": self.schema_heatmap.to_dict(),
            "first_pass_validity": self.get_first_pass_validity(),
            "retry_adjusted_success": self.get_retry_adjusted_success(),
            "p95_latency_s": self.get_p95_latency(),
            "schema_invalid_per_1000": self.get_schema_invalid_per_1000(),
            "live_samples_count": len(self.live_samples),
            "version_table": self.get_version_table(),
        }


def create_readiness(
    prompt_version: str = "1.2.0",
    model_id: str = "qwen3-coder-next:cloud",
) -> ComprehensiveReadiness:
    """Create a comprehensive readiness instance."""
    return ComprehensiveReadiness(
        prompt_version=prompt_version,
        model_id=model_id,
    )


# Export
__all__ = [
    "SchemaClauseFailure",
    "SchemaHeatmap",
    "ErrorBudget",
    "FirstPassReleaseGate",
    "LiveTrafficSample",
    "VersionMetrics",
    "ComprehensiveReadiness",
    "create_readiness",
]


if __name__ == "__main__":
    import json
    
    print("=" * 80)
    print("COMPREHENSIVE PRODUCTION READINESS")
    print("=" * 80)
    
    readiness = create_readiness(
        prompt_version="1.2.0",
        model_id="qwen3-coder-next:cloud",
    )
    
    # Simulate executions
    print("\n" + "=" * 80)
    print("SIMULATING EXECUTIONS")
    print("=" * 80)
    
    # Version 1.0.0 (baseline)
    readiness.prompt_version = "1.0.0"
    for _ in range(50):
        readiness.record_execution(first_pass_success=True, latency_s=1.5)
    for _ in range(30):
        readiness.record_execution(first_pass_success=False, retry_success=True, latency_s=2.5, schema_invalid=True)
    for _ in range(20):
        readiness.record_execution(first_pass_success=False, retry_success=False, latency_s=3.5, schema_invalid=True)
    
    readiness.record_schema_failure("required", "verdict", "Missing required field")
    readiness.record_schema_failure("required", "verdict", "Missing required field")
    readiness.record_schema_failure("required", "verdict", "Missing required field")
    readiness.record_schema_failure("enum", "verdict", "Invalid enum value")
    readiness.record_schema_failure("maximum", "confidence", "Value exceeds maximum")
    
    readiness.save_version_metrics()
    
    # Version 1.1.0 (improved)
    readiness.prompt_version = "1.1.0"
    readiness.first_pass_successes = 0
    readiness.first_pass_failures = 0
    readiness.retry_successes = 0
    readiness.retry_failures = 0
    readiness.latencies = []
    readiness.error_budget = ErrorBudget(prompt_version="1.1.0")
    readiness.schema_heatmap = SchemaHeatmap()
    
    for _ in range(65):
        readiness.record_execution(first_pass_success=True, latency_s=1.2)
    for _ in range(20):
        readiness.record_execution(first_pass_success=False, retry_success=True, latency_s=2.0, schema_invalid=True)
    for _ in range(15):
        readiness.record_execution(first_pass_success=False, retry_success=False, latency_s=2.8, schema_invalid=True)
    
    readiness.record_schema_failure("required", "verdict", "Missing required field")
    readiness.record_schema_failure("enum", "verdict", "Invalid enum value")
    readiness.record_schema_failure("maximum", "confidence", "Value exceeds maximum")
    
    readiness.save_version_metrics()
    
    # Version 1.2.0 (target)
    readiness.prompt_version = "1.2.0"
    readiness.first_pass_successes = 0
    readiness.first_pass_failures = 0
    readiness.retry_successes = 0
    readiness.retry_failures = 0
    readiness.latencies = []
    readiness.error_budget = ErrorBudget(prompt_version="1.2.0")
    readiness.schema_heatmap = SchemaHeatmap()
    
    for _ in range(85):
        readiness.record_execution(first_pass_success=True, latency_s=1.0)
    for _ in range(10):
        readiness.record_execution(first_pass_success=False, retry_success=True, latency_s=1.8, schema_invalid=True)
    for _ in range(5):
        readiness.record_execution(first_pass_success=False, retry_success=False, latency_s=2.5, schema_invalid=True)
    
    readiness.record_schema_failure("required", "verdict", "Missing required field")
    readiness.record_schema_failure("maximum", "confidence", "Value exceeds maximum")
    
    readiness.save_version_metrics()
    
    # Show version table
    print("\n" + "=" * 80)
    print("PER-VERSION METRICS TABLE")
    print("=" * 80)
    
    version_table = readiness.get_version_table()
    print(f"\n{'Version':<12} {'First-Pass':<12} {'Retry-Adj':<12} {'P95 (s)':<10} {'Schema/1K':<12} {'Top 3 Failures'}")
    print("-" * 80)
    
    for v in version_table:
        top_3 = ", ".join([f"{f}:{c}" for f, c in v["top_3_schema_failures"]]) if v["top_3_schema_failures"] else "None"
        print(f"{v['prompt_version']:<12} {v['first_pass_validity']:<12.2%} {v['retry_adjusted_success']:<12.2%} {v['p95_latency_s']:<10.2f} {v['schema_invalid_per_1000']:<12.1f} {top_3}")
    
    # Show schema heatmap
    print("\n" + "=" * 80)
    print("SCHEMA-CLAUSE HEATMAP")
    print("=" * 80)
    
    heatmap = readiness.schema_heatmap.to_dict()
    print(f"\nClause Summary:")
    for clause, count in heatmap["clause_summary"].items():
        print(f"  {clause}: {count}")
    
    print(f"\nTop 5 Hotspots:")
    for hotspot in heatmap["hotspots"]:
        print(f"  {hotspot['clause']}:{hotspot['field']} - {hotspot['count']} failures")
    
    # Show error budget
    print("\n" + "=" * 80)
    print("ERROR BUDGET STATUS")
    print("=" * 80)
    
    budget = readiness.error_budget.get_budget_status()
    print(f"\nSchema Invalid: {budget['schema_invalid']['rate_per_1000']:.1f}/1000 (budget: {budget['schema_invalid']['budget']})")
    print(f"  Remaining: {budget['schema_invalid']['remaining']:.1f}")
    print(f"  Exceeded: {budget['schema_invalid']['exceeded']}")
    
    print(f"\nFirst-Pass Failures: {budget['first_pass_failures']['rate_per_1000']:.1f}/1000 (budget: {budget['first_pass_failures']['budget']})")
    print(f"  Remaining: {budget['first_pass_failures']['remaining']:.1f}")
    print(f"  Exceeded: {budget['first_pass_failures']['exceeded']}")
    
    # Show release gate
    print("\n" + "=" * 80)
    print("FIRST-PASS RELEASE GATE")
    print("=" * 80)
    
    gate = readiness.evaluate_release_gate()
    print(f"\n{gate['summary']}")
    print(f"\nChecks:")
    for name, check in gate["checks"].items():
        status = "✅" if check["pass"] else "❌"
        print(f"  {status} {name}: {check['value']:.2%} >= {check['threshold']:.2%}" if "validity" in name or "success" in name else f"  {status} {name}: {check['value']:.2f} < {check['threshold']:.2f}")
    
    # Record live samples
    print("\n" + "=" * 80)
    print("LIVE TRAFFIC SAMPLES")
    print("=" * 80)
    
    sample = readiness.record_live_sample(
        input_data={"checkpoint": "best_model.pt"},
        output_data={"verdict": "pass", "confidence": 0.95},
        validation_result={"valid": True},
        first_pass=True,
        retry_count=0,
    )
    print(f"\nRecorded sample: {sample.sample_id}")
    print(f"  First-pass: {sample.first_pass}")
    print(f"  Version: {sample.prompt_version}")
    
    # Final status
    print("\n" + "=" * 80)
    print("FINAL STATUS")
    print("=" * 80)
    
    status = readiness.get_status()
    print(f"\n{json.dumps(status, indent=2)}")