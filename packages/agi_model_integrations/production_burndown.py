"""Production Burn-Down with First-Pass Validity and Trend Tracking.

Extends the enhanced burn-down with:
- First-pass validity rate metric
- Per-error regression history (trend-aware)
- Prompt-template version and model ID tracking
- Comprehensive regression result logging

This completes the transition to evidence-based readiness.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
import json


@dataclass
class ErrorTrendPoint:
    """A single data point in an error's history."""
    timestamp: str
    count: int
    prompt_version: str
    model_id: str
    total_executions: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "count": self.count,
            "prompt_version": self.prompt_version,
            "model_id": self.model_id,
            "total_executions": self.total_executions,
        }


@dataclass
class ErrorTrendHistory:
    """
    Per-error regression history for trend-aware leaderboard.
    
    Tracks each error type over time with prompt/model context.
    """
    error_type: str
    history: List[ErrorTrendPoint] = field(default_factory=list)
    
    def record(
        self,
        count: int,
        prompt_version: str,
        model_id: str,
        total_executions: int,
        timestamp: Optional[str] = None,
    ) -> ErrorTrendPoint:
        """Record a data point for this error."""
        if timestamp is None:
            timestamp = datetime.now(timezone.utc).isoformat()
        
        point = ErrorTrendPoint(
            timestamp=timestamp,
            count=count,
            prompt_version=prompt_version,
            model_id=model_id,
            total_executions=total_executions,
        )
        self.history.append(point)
        return point
    
    def get_trend(self, n: int = 5) -> List[Dict[str, Any]]:
        """Get the last N data points."""
        return [p.to_dict() for p in self.history[-n:]]
    
    def get_rate_of_change(self) -> float:
        """Calculate rate of change (errors per period)."""
        if len(self.history) < 2:
            return 0.0
        
        recent = self.history[-1].count
        previous = self.history[-2].count
        return recent - previous
    
    def is_improving(self) -> bool:
        """Check if error count is trending down."""
        return self.get_rate_of_change() < 0
    
    def get_current_rate(self) -> float:
        """Get current error rate (errors per execution)."""
        if not self.history:
            return 0.0
        
        latest = self.history[-1]
        if latest.total_executions == 0:
            return 0.0
        return latest.count / latest.total_executions
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "error_type": self.error_type,
            "history_length": len(self.history),
            "current_count": self.history[-1].count if self.history else 0,
            "current_rate": self.get_current_rate(),
            "rate_of_change": self.get_rate_of_change(),
            "improving": self.is_improving(),
            "trend": self.get_trend(5),
        }


@dataclass
class FirstPassMetrics:
    """
    First-pass validity rate tracking.
    
    Distinguishes between:
    - First-pass validity: Success on first attempt (prompt quality)
    - Retry-adjusted success: Success after retries (recovery quality)
    """
    first_pass_successes: int = 0
    first_pass_failures: int = 0
    retry_successes: int = 0
    retry_failures: int = 0
    
    def record_first_pass_success(self) -> None:
        self.first_pass_successes += 1
    
    def record_first_pass_failure(self) -> None:
        self.first_pass_failures += 1
    
    def record_retry_success(self) -> None:
        self.retry_successes += 1
    
    def record_retry_failure(self) -> None:
        self.retry_failures += 1
    
    @property
    def total_executions(self) -> int:
        return (
            self.first_pass_successes + self.first_pass_failures +
            self.retry_successes + self.retry_failures
        )
    
    @property
    def first_pass_validity_rate(self) -> float:
        """Rate of success on first attempt (prompt quality indicator)."""
        total = self.first_pass_successes + self.first_pass_failures
        if total == 0:
            return 0.0
        return self.first_pass_successes / total
    
    @property
    def retry_adjusted_success_rate(self) -> float:
        """Rate of success after retries (recovery quality indicator)."""
        total = self.total_executions
        if total == 0:
            return 0.0
        return (self.first_pass_successes + self.retry_successes) / total
    
    @property
    def overall_success_rate(self) -> float:
        """Overall success rate including retries."""
        total = self.total_executions
        if total == 0:
            return 0.0
        return (self.first_pass_successes + self.retry_successes) / total
    
    @property
    def retry_recovery_rate(self) -> float:
        """Rate at which failures are recovered via retry."""
        total_failures = self.first_pass_failures
        if total_failures == 0:
            return 0.0
        return self.retry_successes / total_failures
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "first_pass_successes": self.first_pass_successes,
            "first_pass_failures": self.first_pass_failures,
            "retry_successes": self.retry_successes,
            "retry_failures": self.retry_failures,
            "total_executions": self.total_executions,
            "first_pass_validity_rate": self.first_pass_validity_rate,
            "retry_adjusted_success_rate": self.retry_adjusted_success_rate,
            "overall_success_rate": self.overall_success_rate,
            "retry_recovery_rate": self.retry_recovery_rate,
        }


@dataclass
class RegressionResult:
    """
    Regression test result with prompt version and model ID.
    
    Ties each pass/fail to specific contract version and generation context.
    """
    test_id: str
    test_name: str
    passed: bool
    prompt_version: str
    model_id: str
    timestamp: str
    errors_caught: List[str]
    fields_validated: List[str]
    validation_result: Dict[str, Any]
    execution_time_s: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_id": self.test_id,
            "test_name": self.test_name,
            "passed": self.passed,
            "prompt_version": self.prompt_version,
            "model_id": self.model_id,
            "timestamp": self.timestamp,
            "errors_caught": self.errors_caught,
            "fields_validated": self.fields_validated,
            "execution_time_s": self.execution_time_s,
        }


@dataclass
class PromptContractVersion:
    """Version information for a prompt contract."""
    version: str
    created_at: str
    changes: List[str]
    schema_name: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "created_at": self.created_at,
            "changes": self.changes,
            "schema_name": self.schema_name,
        }


# Current prompt contract version
CURRENT_PROMPT_VERSION = PromptContractVersion(
    version="1.2.0",
    created_at="2026-04-12T00:00:00Z",
    changes=[
        "Added explicit verdict enum constraint",
        "Added confidence bounds validation",
        "Added metrics_summary non-empty check",
        "Added anti-patterns for common mistakes",
    ],
    schema_name="vae_checkpoint_validation",
)


class ProductionBurnDown:
    """
    Production burn-down with first-pass validity and trend tracking.
    
    Features:
    - First-pass validity rate (prompt quality)
    - Retry-adjusted success rate (recovery quality)
    - Per-error trend history
    - Prompt version and model ID tracking
    - Comprehensive regression result logging
    """
    
    def __init__(
        self,
        prompt_version: str = "1.2.0",
        model_id: str = "qwen3-coder-next:cloud",
    ):
        self.prompt_version = prompt_version
        self.model_id = model_id
        
        # Metrics
        self.first_pass_metrics = FirstPassMetrics()
        
        # Error trends
        self.error_trends: Dict[str, ErrorTrendHistory] = {}
        
        # Regression results
        self.regression_results: List[RegressionResult] = []
        
        # History
        self.history: List[Dict[str, Any]] = []
    
    def record_execution(
        self,
        first_pass_success: bool,
        retry_success: bool = False,
    ) -> None:
        """Record an execution outcome."""
        if first_pass_success:
            self.first_pass_metrics.record_first_pass_success()
        else:
            self.first_pass_metrics.record_first_pass_failure()
            if retry_success:
                self.first_pass_metrics.record_retry_success()
            else:
                self.first_pass_metrics.record_retry_failure()
    
    def record_error(
        self,
        error_type: str,
        count: int,
        total_executions: int,
    ) -> ErrorTrendPoint:
        """Record an error count with trend tracking."""
        if error_type not in self.error_trends:
            self.error_trends[error_type] = ErrorTrendHistory(error_type=error_type)
        
        return self.error_trends[error_type].record(
            count=count,
            prompt_version=self.prompt_version,
            model_id=self.model_id,
            total_executions=total_executions,
        )
    
    def record_regression_result(
        self,
        test_id: str,
        test_name: str,
        passed: bool,
        errors_caught: List[str],
        fields_validated: List[str],
        validation_result: Dict[str, Any],
        execution_time_s: float = 0.0,
    ) -> RegressionResult:
        """Record a regression test result."""
        result = RegressionResult(
            test_id=test_id,
            test_name=test_name,
            passed=passed,
            prompt_version=self.prompt_version,
            model_id=self.model_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            errors_caught=errors_caught,
            fields_validated=fields_validated,
            validation_result=validation_result,
            execution_time_s=execution_time_s,
        )
        self.regression_results.append(result)
        return result
    
    def get_error_trend(self, error_type: str) -> Optional[Dict[str, Any]]:
        """Get trend for a specific error type."""
        if error_type in self.error_trends:
            return self.error_trends[error_type].to_dict()
        return None
    
    def get_all_error_trends(self) -> Dict[str, Dict[str, Any]]:
        """Get trends for all error types."""
        return {
            error_type: trend.to_dict()
            for error_type, trend in self.error_trends.items()
        }
    
    def get_improving_errors(self) -> List[str]:
        """Get list of error types that are improving."""
        return [
            error_type
            for error_type, trend in self.error_trends.items()
            if trend.is_improving()
        ]
    
    def get_worsening_errors(self) -> List[str]:
        """Get list of error types that are worsening."""
        return [
            error_type
            for error_type, trend in self.error_trends.items()
            if not trend.is_improving() and len(trend.history) > 1
        ]
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary."""
        return {
            "prompt_version": self.prompt_version,
            "model_id": self.model_id,
            "first_pass_metrics": self.first_pass_metrics.to_dict(),
            "error_trends": self.get_all_error_trends(),
            "improving_errors": self.get_improving_errors(),
            "worsening_errors": self.get_worsening_errors(),
            "regression_results_count": len(self.regression_results),
        }
    
    def record_progress(
        self,
        schema_invalid: int,
        transport: int,
        success_rate: float,
        p95_latency_s: float,
    ) -> Dict[str, Any]:
        """Record burn-down progress."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "prompt_version": self.prompt_version,
            "model_id": self.model_id,
            "schema_invalid": schema_invalid,
            "transport": transport,
            "success_rate": success_rate,
            "p95_latency_s": p95_latency_s,
            "first_pass_validity_rate": self.first_pass_metrics.first_pass_validity_rate,
            "retry_adjusted_success_rate": self.first_pass_metrics.retry_adjusted_success_rate,
            "overall_success_rate": self.first_pass_metrics.overall_success_rate,
            "retry_recovery_rate": self.first_pass_metrics.retry_recovery_rate,
        }
        self.history.append(entry)
        return entry
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status."""
        return {
            "prompt_version": self.prompt_version,
            "model_id": self.model_id,
            "metrics": self.get_metrics_summary(),
            "history_length": len(self.history),
            "latest": self.history[-1] if self.history else None,
        }


def create_production_burn_down(
    prompt_version: str = "1.2.0",
    model_id: str = "qwen3-coder-next:cloud",
) -> ProductionBurnDown:
    """Create a production burn-down instance."""
    return ProductionBurnDown(
        prompt_version=prompt_version,
        model_id=model_id,
    )


# Export
__all__ = [
    "ErrorTrendPoint",
    "ErrorTrendHistory",
    "FirstPassMetrics",
    "RegressionResult",
    "PromptContractVersion",
    "CURRENT_PROMPT_VERSION",
    "ProductionBurnDown",
    "create_production_burn_down",
]


if __name__ == "__main__":
    import json
    
    print("=" * 80)
    print("PRODUCTION BURN-DOWN WITH FIRST-PASS VALIDITY")
    print("=" * 80)
    
    burn_down = create_production_burn_down(
        prompt_version="1.2.0",
        model_id="qwen3-coder-next:cloud",
    )
    
    # Show current prompt version
    print("\n" + "=" * 80)
    print("CURRENT PROMPT CONTRACT VERSION")
    print("=" * 80)
    print(f"\nVersion: {CURRENT_PROMPT_VERSION.version}")
    print(f"Schema: {CURRENT_PROMPT_VERSION.schema_name}")
    print(f"Changes:")
    for change in CURRENT_PROMPT_VERSION.changes:
        print(f"  - {change}")
    
    # Record executions
    print("\n" + "=" * 80)
    print("FIRST-PASS VALIDITY TRACKING")
    print("=" * 80)
    
    # Simulate executions
    # Week 1: 58% first-pass, 42% need retry, 20% of retries succeed
    for _ in range(58):
        burn_down.record_execution(first_pass_success=True)
    for _ in range(34):
        burn_down.record_execution(first_pass_success=False, retry_success=True)
    for _ in range(8):
        burn_down.record_execution(first_pass_success=False, retry_success=False)
    
    metrics = burn_down.first_pass_metrics.to_dict()
    print(f"\nFirst-pass successes: {metrics['first_pass_successes']}")
    print(f"First-pass failures: {metrics['first_pass_failures']}")
    print(f"Retry successes: {metrics['retry_successes']}")
    print(f"Retry failures: {metrics['retry_failures']}")
    print(f"\nFirst-pass validity rate: {metrics['first_pass_validity_rate']:.2%}")
    print(f"Retry-adjusted success rate: {metrics['retry_adjusted_success_rate']:.2%}")
    print(f"Overall success rate: {metrics['overall_success_rate']:.2%}")
    print(f"Retry recovery rate: {metrics['retry_recovery_rate']:.2%}")
    
    # Record error trends
    print("\n" + "=" * 80)
    print("ERROR TREND TRACKING")
    print("=" * 80)
    
    # Week 1
    burn_down.record_error("Missing required field", 12, 100)
    burn_down.record_error("Invalid enum value", 5, 100)
    burn_down.record_error("Out of range", 3, 100)
    
    # Week 2 (improving)
    burn_down.record_error("Missing required field", 8, 100)
    burn_down.record_error("Invalid enum value", 3, 100)
    burn_down.record_error("Out of range", 2, 100)
    
    # Week 3 (more improvement)
    burn_down.record_error("Missing required field", 4, 100)
    burn_down.record_error("Invalid enum value", 1, 100)
    burn_down.record_error("Out of range", 1, 100)
    
    trends = burn_down.get_all_error_trends()
    for error_type, trend in trends.items():
        print(f"\n{error_type}:")
        print(f"  Current count: {trend['current_count']}")
        print(f"  Current rate: {trend['current_rate']:.2%}")
        print(f"  Rate of change: {trend['rate_of_change']}")
        print(f"  Improving: {trend['improving']}")
    
    print(f"\nImproving errors: {burn_down.get_improving_errors()}")
    print(f"Worsening errors: {burn_down.get_worsening_errors()}")
    
    # Record regression results
    print("\n" + "=" * 80)
    print("REGRESSION RESULTS WITH VERSION TRACKING")
    print("=" * 80)
    
    test_cases = [
        ("missing_verdict", "Missing verdict field", True, ["Missing required field"], ["verdict"]),
        ("invalid_verdict_enum", "Invalid verdict enum value", True, ["Invalid enum value"], ["verdict"]),
        ("confidence_out_of_range", "Confidence out of range", True, ["Out of range"], ["confidence"]),
        ("empty_metrics_summary", "Empty metrics_summary object", False, [], []),
        ("extra_fields", "Extra fields not in schema", True, ["Extra field"], ["extra_field"]),
    ]
    
    for test_id, test_name, passed, errors, fields in test_cases:
        result = burn_down.record_regression_result(
            test_id=test_id,
            test_name=test_name,
            passed=passed,
            errors_caught=errors,
            fields_validated=fields,
            validation_result={"valid": passed},
            execution_time_s=0.5,
        )
        print(f"\n{test_id}:")
        print(f"  Passed: {result.passed}")
        print(f"  Prompt version: {result.prompt_version}")
        print(f"  Model ID: {result.model_id}")
        print(f"  Timestamp: {result.timestamp}")
    
    # Final status
    print("\n" + "=" * 80)
    print("FINAL STATUS")
    print("=" * 80)
    
    status = burn_down.get_status()
    print(f"\n{json.dumps(status, indent=2)}")