"""Vault Governance Policy Engine - Failure-Class-Aware Governance.

Extends the governance runtime with:
- Full jitter backoff strategy
- Retry outcome taxonomy (transient, schema_invalid, business_invalid, etc.)
- Percentile latency metrics (p50, p95, p99)
- Separate validation vs transport failure tracking
- Dead-letter quarantine for exhausted failures

This completes the transition to failure-class-aware governance.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import json
import random
import time
import statistics


class BackoffStrategy(Enum):
    """Backoff strategy for retries."""
    FIXED = "fixed"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    EXPONENTIAL_JITTER = "exponential_jitter"  # Exponential + slight jitter
    FULL_JITTER = "full_jitter"  # Uniform random from 0 to exponential cap


class RetryOutcome(Enum):
    """Taxonomy of retry outcomes."""
    SUCCESS = "success"
    TRANSIENT = "transient"              # Temporary failure, retry recommended
    SCHEMA_INVALID = "schema_invalid"    # JSON Schema validation failed
    BUSINESS_INVALID = "business_invalid"  # Business rule validation failed
    TIMEOUT = "timeout"                  # Execution timeout
    BREAKER_OPEN = "breaker_open"        # Circuit breaker blocked execution
    NON_RETRYABLE = "non_retryable"      # Permanent failure, do not retry
    EXHAUSTED = "exhausted"              # Retry budget exhausted


class FailureClass(Enum):
    """Class of failure for policy decisions."""
    VALIDATION = "validation"      # Schema or business rule violation
    TRANSPORT = "transport"        # Network, timeout, model errors
    GOVERNANCE = "governance"      # Circuit breaker, policy violations
    PERMANENT = "permanent"        # Non-retryable errors


@dataclass(frozen=True)
class BackoffPolicy:
    """Backoff policy for retries."""
    strategy: BackoffStrategy
    base_delay_s: float = 1.0
    max_delay_s: float = 60.0
    multiplier: float = 2.0
    jitter_factor: float = 0.1
    
    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt number (0-indexed)."""
        if self.strategy == BackoffStrategy.FIXED:
            return min(self.base_delay_s, self.max_delay_s)
        
        elif self.strategy == BackoffStrategy.LINEAR:
            delay = self.base_delay_s * (attempt + 1)
            return min(delay, self.max_delay_s)
        
        elif self.strategy == BackoffStrategy.EXPONENTIAL:
            delay = self.base_delay_s * (self.multiplier ** attempt)
            return min(delay, self.max_delay_s)
        
        elif self.strategy == BackoffStrategy.EXPONENTIAL_JITTER:
            delay = self.base_delay_s * (self.multiplier ** attempt)
            # Slight jitter: ±jitter_factor%
            jitter = delay * self.jitter_factor * (2 * random.random() - 1)
            delay += jitter
            return min(delay, self.max_delay_s)
        
        elif self.strategy == BackoffStrategy.FULL_JITTER:
            # Full jitter: uniform random from 0 to exponential cap
            cap = self.base_delay_s * (self.multiplier ** attempt)
            cap = min(cap, self.max_delay_s)
            delay = random.uniform(0, cap)
            return delay
        
        return self.base_delay_s


@dataclass(frozen=True)
class RetryPolicy:
    """Policy for retry decisions based on failure class."""
    max_retries: Dict[FailureClass, int] = field(default_factory=lambda: {
        FailureClass.VALIDATION: 3,
        FailureClass.TRANSPORT: 5,
        FailureClass.GOVERNANCE: 0,  # No retry for governance failures
        FailureClass.PERMANENT: 0,   # No retry for permanent failures
    })
    
    backoff_by_class: Dict[FailureClass, BackoffStrategy] = field(default_factory=lambda: {
        FailureClass.VALIDATION: BackoffStrategy.EXPONENTIAL_JITTER,
        FailureClass.TRANSPORT: BackoffStrategy.FULL_JITTER,
        FailureClass.GOVERNANCE: BackoffStrategy.FIXED,
        FailureClass.PERMANENT: BackoffStrategy.FIXED,
    })
    
    def get_max_retries(self, failure_class: FailureClass) -> int:
        return self.max_retries.get(failure_class, 0)
    
    def get_backoff_strategy(self, failure_class: FailureClass) -> BackoffStrategy:
        return self.backoff_by_class.get(failure_class, BackoffStrategy.EXPONENTIAL_JITTER)
    
    def should_retry(self, outcome: RetryOutcome, attempt: int) -> bool:
        """Determine if retry is appropriate."""
        if outcome == RetryOutcome.SUCCESS:
            return False
        if outcome in (RetryOutcome.BREAKER_OPEN, RetryOutcome.NON_RETRYABLE):
            return False
        
        failure_class = self._outcome_to_class(outcome)
        max_retries = self.get_max_retries(failure_class)
        return attempt < max_retries
    
    def _outcome_to_class(self, outcome: RetryOutcome) -> FailureClass:
        mapping = {
            RetryOutcome.TRANSIENT: FailureClass.TRANSPORT,
            RetryOutcome.TIMEOUT: FailureClass.TRANSPORT,
            RetryOutcome.SCHEMA_INVALID: FailureClass.VALIDATION,
            RetryOutcome.BUSINESS_INVALID: FailureClass.VALIDATION,
            RetryOutcome.BREAKER_OPEN: FailureClass.GOVERNANCE,
            RetryOutcome.NON_RETRYABLE: FailureClass.PERMANENT,
            RetryOutcome.EXHAUSTED: FailureClass.PERMANENT,
        }
        return mapping.get(outcome, FailureClass.PERMANENT)


@dataclass
class LatencyMetrics:
    """Percentile latency metrics."""
    samples: List[float] = field(default_factory=list)
    max_samples: int = 1000
    
    def record(self, latency_s: float) -> None:
        self.samples.append(latency_s)
        if len(self.samples) > self.max_samples:
            self.samples = self.samples[-self.max_samples:]
    
    def p50(self) -> float:
        if not self.samples:
            return 0.0
        return statistics.median(self.samples)
    
    def p95(self) -> float:
        if not self.samples:
            return 0.0
        return statistics.quantiles(self.samples, n=20)[18]  # 95th percentile
    
    def p99(self) -> float:
        if not self.samples:
            return 0.0
        return statistics.quantiles(self.samples, n=100)[98]  # 99th percentile
    
    def mean(self) -> float:
        if not self.samples:
            return 0.0
        return statistics.mean(self.samples)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "count": len(self.samples),
            "mean_s": self.mean(),
            "p50_s": self.p50(),
            "p95_s": self.p95(),
            "p99_s": self.p99(),
        }


@dataclass
class FailureMetrics:
    """Separate tracking for validation vs transport failures."""
    validation_failures: int = 0
    transport_failures: int = 0
    governance_failures: int = 0
    permanent_failures: int = 0
    
    # By outcome
    by_outcome: Dict[str, int] = field(default_factory=dict)
    
    def record(self, outcome: RetryOutcome) -> None:
        outcome_str = outcome.value
        self.by_outcome[outcome_str] = self.by_outcome.get(outcome_str, 0) + 1
        
        if outcome in (RetryOutcome.SCHEMA_INVALID, RetryOutcome.BUSINESS_INVALID):
            self.validation_failures += 1
        elif outcome in (RetryOutcome.TRANSIENT, RetryOutcome.TIMEOUT):
            self.transport_failures += 1
        elif outcome == RetryOutcome.BREAKER_OPEN:
            self.governance_failures += 1
        elif outcome in (RetryOutcome.NON_RETRYABLE, RetryOutcome.EXHAUSTED):
            self.permanent_failures += 1
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "validation_failures": self.validation_failures,
            "transport_failures": self.transport_failures,
            "governance_failures": self.governance_failures,
            "permanent_failures": self.permanent_failures,
            "by_outcome": self.by_outcome,
        }


@dataclass
class DeadLetterEntry:
    """Entry in the dead-letter quarantine."""
    id: str
    operation: str
    model: str
    timestamp: str
    failure_category: str
    retry_count: int
    last_error: str
    input_hash: str
    input_data: Dict[str, Any]
    last_output: Optional[Dict[str, Any]]
    recovery_attempts: int = 0
    last_recovery_attempt: Optional[str] = None
    status: str = "quarantined"  # quarantined, recovered, abandoned
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "operation": self.operation,
            "model": self.model,
            "timestamp": self.timestamp,
            "failure_category": self.failure_category,
            "retry_count": self.retry_count,
            "last_error": self.last_error,
            "input_hash": self.input_hash,
            "input_data": self.input_data,
            "last_output": self.last_output,
            "recovery_attempts": self.recovery_attempts,
            "last_recovery_attempt": self.last_recovery_attempt,
            "status": self.status,
        }


@dataclass
class OperationMetricsV2:
    """Enhanced metrics with percentile latencies and failure class tracking."""
    operation: str
    total_executions: int = 0
    successful_executions: int = 0
    latency: LatencyMetrics = field(default_factory=LatencyMetrics)
    failures: FailureMetrics = field(default_factory=FailureMetrics)
    total_retries: int = 0
    total_backoff_time_s: float = 0.0
    
    @property
    def success_rate(self) -> float:
        if self.total_executions == 0:
            return 0.0
        return self.successful_executions / self.total_executions
    
    @property
    def validation_failure_rate(self) -> float:
        total = self.failures.validation_failures + self.failures.transport_failures
        if total == 0:
            return 0.0
        return self.failures.validation_failures / total
    
    @property
    def transport_failure_rate(self) -> float:
        total = self.failures.validation_failures + self.failures.transport_failures
        if total == 0:
            return 0.0
        return self.failures.transport_failures / total
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "operation": self.operation,
            "total_executions": self.total_executions,
            "successful_executions": self.successful_executions,
            "success_rate": self.success_rate,
            "latency": self.latency.to_dict(),
            "failures": self.failures.to_dict(),
            "validation_failure_rate": self.validation_failure_rate,
            "transport_failure_rate": self.transport_failure_rate,
            "total_retries": self.total_retries,
            "total_backoff_time_s": self.total_backoff_time_s,
        }


class DeadLetterQuarantine:
    """
    Dead-letter quarantine for exhausted failures.
    
    Features:
    - Durable capture of failures that exhausted retries
    - Recovery attempt tracking
    - Status management (quarantined, recovered, abandoned)
    """
    
    def __init__(self, max_entries: int = 10000):
        self.entries: Dict[str, DeadLetterEntry] = {}
        self.max_entries = max_entries
    
    def add(
        self,
        operation: str,
        model: str,
        failure_category: str,
        retry_count: int,
        last_error: str,
        input_hash: str,
        input_data: Dict[str, Any],
        last_output: Optional[Dict[str, Any]] = None,
    ) -> DeadLetterEntry:
        """Add a failure to the quarantine."""
        import uuid
        entry_id = str(uuid.uuid4())[:8]
        
        entry = DeadLetterEntry(
            id=entry_id,
            operation=operation,
            model=model,
            timestamp=datetime.now(timezone.utc).isoformat(),
            failure_category=failure_category,
            retry_count=retry_count,
            last_error=last_error,
            input_hash=input_hash,
            input_data=input_data,
            last_output=last_output,
        )
        
        self.entries[entry_id] = entry
        
        # Enforce max entries
        if len(self.entries) > self.max_entries:
            # Remove oldest entries
            sorted_ids = sorted(self.entries.keys(), 
                               key=lambda x: self.entries[x].timestamp)
            for old_id in sorted_ids[:len(self.entries) - self.max_entries]:
                del self.entries[old_id]
        
        return entry
    
    def get(self, entry_id: str) -> Optional[DeadLetterEntry]:
        return self.entries.get(entry_id)
    
    def list(
        self,
        operation: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> List[DeadLetterEntry]:
        """List entries with optional filtering."""
        entries = list(self.entries.values())
        
        if operation:
            entries = [e for e in entries if e.operation == operation]
        if status:
            entries = [e for e in entries if e.status == status]
        
        # Sort by timestamp descending
        entries.sort(key=lambda x: x.timestamp, reverse=True)
        return entries[:limit]
    
    def mark_recovered(self, entry_id: str) -> bool:
        """Mark an entry as recovered."""
        entry = self.entries.get(entry_id)
        if entry:
            entry.status = "recovered"
            entry.last_recovery_attempt = datetime.now(timezone.utc).isoformat()
            return True
        return False
    
    def mark_abandoned(self, entry_id: str) -> bool:
        """Mark an entry as abandoned."""
        entry = self.entries.get(entry_id)
        if entry:
            entry.status = "abandoned"
            return True
        return False
    
    def attempt_recovery(self, entry_id: str) -> bool:
        """Record a recovery attempt."""
        entry = self.entries.get(entry_id)
        if entry:
            entry.recovery_attempts += 1
            entry.last_recovery_attempt = datetime.now(timezone.utc).isoformat()
            return True
        return False
    
    def stats(self) -> Dict[str, Any]:
        """Get quarantine statistics."""
        by_status = {"quarantined": 0, "recovered": 0, "abandoned": 0}
        by_operation: Dict[str, int] = {}
        
        for entry in self.entries.values():
            by_status[entry.status] = by_status.get(entry.status, 0) + 1
            by_operation[entry.operation] = by_operation.get(entry.operation, 0) + 1
        
        return {
            "total_entries": len(self.entries),
            "by_status": by_status,
            "by_operation": by_operation,
        }


class VaultPolicyEngine:
    """
    Failure-class-aware governance engine.
    
    Features:
    - Retry outcome taxonomy
    - Failure class-based policies
    - Percentile latency metrics
    - Separate validation/transport failure tracking
    - Dead-letter quarantine
    """
    
    def __init__(
        self,
        retry_policy: Optional[RetryPolicy] = None,
        default_backoff: Optional[BackoffPolicy] = None,
    ):
        self.retry_policy = retry_policy or RetryPolicy()
        self.default_backoff = default_backoff or BackoffPolicy(
            strategy=BackoffStrategy.FULL_JITTER,
            base_delay_s=1.0,
            max_delay_s=60.0,
            multiplier=2.0,
        )
        
        self.metrics: Dict[str, OperationMetricsV2] = {}
        self.quarantine = DeadLetterQuarantine()
        self.backoff_policies: Dict[str, BackoffPolicy] = {}
    
    def configure_backoff(
        self,
        operation: str,
        strategy: BackoffStrategy,
        base_delay_s: float = 1.0,
        max_delay_s: float = 60.0,
    ) -> None:
        """Configure backoff for a specific operation."""
        self.backoff_policies[operation] = BackoffPolicy(
            strategy=strategy,
            base_delay_s=base_delay_s,
            max_delay_s=max_delay_s,
        )
    
    def get_backoff(self, operation: str) -> BackoffPolicy:
        """Get backoff policy for operation."""
        return self.backoff_policies.get(operation, self.default_backoff)
    
    def classify_outcome(
        self,
        validation_result: Dict[str, Any],
        execution_error: Optional[str] = None,
        timed_out: bool = False,
    ) -> RetryOutcome:
        """Classify the outcome of an execution."""
        if timed_out:
            return RetryOutcome.TIMEOUT
        
        if execution_error:
            # Check if error is transient
            transient_indicators = ["timeout", "connection", "rate limit", "503", "502", "429"]
            if any(ind in execution_error.lower() for ind in transient_indicators):
                return RetryOutcome.TRANSIENT
            return RetryOutcome.NON_RETRYABLE
        
        if validation_result.get("valid", False):
            return RetryOutcome.SUCCESS
        
        # Check validation errors
        errors = validation_result.get("errors", [])
        for error in errors:
            if "schema" in error.lower() or "required" in error.lower():
                return RetryOutcome.SCHEMA_INVALID
            if "business" in error.lower() or "invalid" in error.lower():
                return RetryOutcome.BUSINESS_INVALID
        
        return RetryOutcome.SCHEMA_INVALID
    
    def should_retry(
        self,
        outcome: RetryOutcome,
        attempt: int,
        failure_class: Optional[FailureClass] = None,
    ) -> bool:
        """Determine if retry is appropriate."""
        return self.retry_policy.should_retry(outcome, attempt)
    
    def get_backoff_delay(
        self,
        operation: str,
        outcome: RetryOutcome,
        attempt: int,
    ) -> float:
        """Calculate backoff delay based on failure class."""
        failure_class = self.retry_policy._outcome_to_class(outcome)
        strategy = self.retry_policy.get_backoff_strategy(failure_class)
        
        backoff = BackoffPolicy(
            strategy=strategy,
            base_delay_s=self.get_backoff(operation).base_delay_s,
            max_delay_s=self.get_backoff(operation).max_delay_s,
            multiplier=self.get_backoff(operation).multiplier,
        )
        
        return backoff.calculate_delay(attempt)
    
    def record_execution(
        self,
        operation: str,
        outcome: RetryOutcome,
        latency_s: float,
        retries: int,
        backoff_time_s: float,
    ) -> None:
        """Record execution metrics."""
        metrics = self._get_metrics(operation)
        metrics.total_executions += 1
        metrics.total_retries += retries
        metrics.total_backoff_time_s += backoff_time_s
        
        if outcome == RetryOutcome.SUCCESS:
            metrics.successful_executions += 1
        else:
            metrics.failures.record(outcome)
        
        metrics.latency.record(latency_s)
    
    def quarantine_failure(
        self,
        operation: str,
        model: str,
        outcome: RetryOutcome,
        retry_count: int,
        last_error: str,
        input_hash: str,
        input_data: Dict[str, Any],
        last_output: Optional[Dict[str, Any]] = None,
    ) -> DeadLetterEntry:
        """Add exhausted failure to quarantine."""
        return self.quarantine.add(
            operation=operation,
            model=model,
            failure_category=outcome.value,
            retry_count=retry_count,
            last_error=last_error,
            input_hash=input_hash,
            input_data=input_data,
            last_output=last_output,
        )
    
    def get_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive governance dashboard."""
        total_executions = sum(m.total_executions for m in self.metrics.values())
        total_successes = sum(m.successful_executions for m in self.metrics.values())
        
        total_validation = sum(m.failures.validation_failures for m in self.metrics.values())
        total_transport = sum(m.failures.transport_failures for m in self.metrics.values())
        
        return {
            "summary": {
                "total_executions": total_executions,
                "total_successes": total_successes,
                "overall_success_rate": total_successes / total_executions if total_executions > 0 else 0.0,
            },
            "failures": {
                "validation_failures": total_validation,
                "transport_failures": total_transport,
                "validation_failure_rate": total_validation / (total_validation + total_transport) if (total_validation + total_transport) > 0 else 0.0,
                "transport_failure_rate": total_transport / (total_validation + total_transport) if (total_validation + total_transport) > 0 else 0.0,
            },
            "quarantine": self.quarantine.stats(),
            "operations": {op: m.to_dict() for op, m in self.metrics.items()},
        }
    
    def _get_metrics(self, operation: str) -> OperationMetricsV2:
        if operation not in self.metrics:
            self.metrics[operation] = OperationMetricsV2(operation=operation)
        return self.metrics[operation]


def create_policy_engine(
    retry_policy: Optional[RetryPolicy] = None,
    backoff: Optional[BackoffPolicy] = None,
) -> VaultPolicyEngine:
    """Create a new policy engine instance."""
    return VaultPolicyEngine(
        retry_policy=retry_policy,
        default_backoff=backoff,
    )


# Export
__all__ = [
    "BackoffStrategy",
    "RetryOutcome",
    "FailureClass",
    "BackoffPolicy",
    "RetryPolicy",
    "LatencyMetrics",
    "FailureMetrics",
    "DeadLetterEntry",
    "OperationMetricsV2",
    "DeadLetterQuarantine",
    "VaultPolicyEngine",
    "create_policy_engine",
]


if __name__ == "__main__":
    import json
    
    print("=" * 80)
    print("VAULT POLICY ENGINE")
    print("=" * 80)
    
    # Create policy engine
    engine = create_policy_engine(
        retry_policy=RetryPolicy(
            max_retries={
                FailureClass.VALIDATION: 3,
                FailureClass.TRANSPORT: 5,
                FailureClass.GOVERNANCE: 0,
                FailureClass.PERMANENT: 0,
            },
            backoff_by_class={
                FailureClass.VALIDATION: BackoffStrategy.EXPONENTIAL_JITTER,
                FailureClass.TRANSPORT: BackoffStrategy.FULL_JITTER,
                FailureClass.GOVERNANCE: BackoffStrategy.FIXED,
                FailureClass.PERMANENT: BackoffStrategy.FIXED,
            },
        ),
        backoff=BackoffPolicy(
            strategy=BackoffStrategy.FULL_JITTER,
            base_delay_s=1.0,
            max_delay_s=60.0,
        ),
    )
    
    # Demo backoff strategies
    print("\nBACKOFF STRATEGY COMPARISON")
    print("-" * 40)
    
    strategies = [
        BackoffStrategy.EXPONENTIAL_JITTER,
        BackoffStrategy.FULL_JITTER,
    ]
    
    for strategy in strategies:
        policy = BackoffPolicy(strategy=strategy, base_delay_s=1.0, max_delay_s=30.0)
        print(f"\n{strategy.value}:")
        delays = [policy.calculate_delay(i) for i in range(5)]
        print(f"  Delays: {[f'{d:.2f}s' for d in delays]}")
    
    # Demo outcome classification
    print("\n" + "=" * 80)
    print("OUTCOME CLASSIFICATION")
    print("=" * 80)
    
    test_cases = [
        ({"valid": True}, None, False),
        ({"valid": False, "errors": ["'verdict' is required"]}, None, False),
        ({"valid": False, "errors": ["Business rule violated"]}, None, False),
        ({"valid": True}, "Connection timeout", False),
        ({"valid": True}, "Rate limit exceeded", False),
        ({"valid": True}, None, True),
    ]
    
    for validation, error, timeout in test_cases:
        outcome = engine.classify_outcome(validation, error, timeout)
        print(f"\nValidation: {validation.get('valid')}, Error: {error}, Timeout: {timeout}")
        print(f"  Outcome: {outcome.value}")
    
    # Demo latency metrics
    print("\n" + "=" * 80)
    print("LATENCY METRICS (Percentiles)")
    print("=" * 80)
    
    latency = LatencyMetrics()
    # Simulate latencies
    import random
    for _ in range(100):
        latency.record(random.uniform(0.5, 5.0))
    
    print(f"\nSamples: {len(latency.samples)}")
    print(f"Mean: {latency.mean():.3f}s")
    print(f"P50: {latency.p50():.3f}s")
    print(f"P95: {latency.p95():.3f}s")
    print(f"P99: {latency.p99():.3f}s")
    
    # Demo failure metrics
    print("\n" + "=" * 80)
    print("FAILURE METRICS (Validation vs Transport)")
    print("=" * 80)
    
    failures = FailureMetrics()
    outcomes = [
        RetryOutcome.SCHEMA_INVALID,
        RetryOutcome.BUSINESS_INVALID,
        RetryOutcome.TRANSIENT,
        RetryOutcome.TIMEOUT,
        RetryOutcome.SCHEMA_INVALID,
    ]
    
    for outcome in outcomes:
        failures.record(outcome)
    
    print(f"\n{json.dumps(failures.to_dict(), indent=2)}")
    
    # Demo quarantine
    print("\n" + "=" * 80)
    print("DEAD-LETTER QUARANTINE")
    print("=" * 80)
    
    entry = engine.quarantine_failure(
        operation="vae_checkpoint_validation",
        model="qwen3-coder-next:cloud",
        outcome=RetryOutcome.EXHAUSTED,
        retry_count=3,
        last_error="Schema validation failed after 3 retries",
        input_hash="abc123",
        input_data={"checkpoint": "best_model.pt"},
        last_output={"invalid": "output"},
    )
    
    print(f"\nQuarantined entry:")
    print(f"  ID: {entry.id}")
    print(f"  Operation: {entry.operation}")
    print(f"  Status: {entry.status}")
    
    # Dashboard
    print("\n" + "=" * 80)
    print("GOVERNANCE DASHBOARD")
    print("=" * 80)
    
    # Record some executions
    for _ in range(50):
        engine.record_execution(
            operation="vae_checkpoint_validation",
            outcome=random.choice([RetryOutcome.SUCCESS, RetryOutcome.SUCCESS, 
                                   RetryOutcome.SCHEMA_INVALID, RetryOutcome.TRANSIENT]),
            latency_s=random.uniform(0.5, 2.0),
            retries=random.randint(0, 2),
            backoff_time_s=random.uniform(0, 1),
        )
    
    dashboard = engine.get_dashboard()
    print(f"\n{json.dumps(dashboard, indent=2)}")