"""Vault Governance Runtime - Operational Hardening.

Extends the governance layer with:
- Circuit breaker cooldowns and explicit state transitions
- Retry backoff policy (exponential, jitter)
- Typed failure artifacts for exhausted retries
- Per-operation metrics dashboards

This completes the transition from "model config" to runtime governance.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timezone
import json
import random
import time


class BackoffStrategy(Enum):
    """Backoff strategy for retries."""
    FIXED = "fixed"               # Fixed delay between retries
    LINEAR = "linear"             # Linearly increasing delay
    EXPONENTIAL = "exponential"   # Exponentially increasing delay
    EXPONENTIAL_JITTER = "exponential_jitter"  # Exponential with jitter


class FailureCategory(Enum):
    """Category of governance failure."""
    SCHEMA_VIOLATION = "schema_violation"
    BUSINESS_RULE_VIOLATION = "business_rule_violation"
    MODEL_ERROR = "model_error"
    TIMEOUT = "timeout"
    CIRCUIT_BREAKER_OPEN = "circuit_breaker_open"
    RETRY_EXHAUSTED = "retry_exhausted"


@dataclass(frozen=True)
class BackoffPolicy:
    """Backoff policy for retries."""
    strategy: BackoffStrategy
    base_delay_s: float = 1.0
    max_delay_s: float = 60.0
    multiplier: float = 2.0
    jitter_factor: float = 0.1  # 10% jitter
    
    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt number (0-indexed)."""
        if self.strategy == BackoffStrategy.FIXED:
            delay = self.base_delay_s
        
        elif self.strategy == BackoffStrategy.LINEAR:
            delay = self.base_delay_s * (attempt + 1)
        
        elif self.strategy == BackoffStrategy.EXPONENTIAL:
            delay = self.base_delay_s * (self.multiplier ** attempt)
        
        elif self.strategy == BackoffStrategy.EXPONENTIAL_JITTER:
            delay = self.base_delay_s * (self.multiplier ** attempt)
            # Add jitter: random value between -jitter% and +jitter%
            jitter = delay * self.jitter_factor * (2 * random.random() - 1)
            delay += jitter
        
        return min(delay, self.max_delay_s)


@dataclass(frozen=True)
class CircuitBreakerPolicy:
    """Policy for circuit breaker behavior."""
    failure_threshold: int = 5           # Failures before opening
    success_threshold: int = 1          # Successes in half-open to close
    cooldown_s: float = 30.0            # Time before half-open transition
    half_open_max_calls: int = 3        # Max calls allowed in half-open
    
    def should_open(self, failure_count: int) -> bool:
        """Check if circuit should open."""
        return failure_count >= self.failure_threshold
    
    def should_close(self, success_count: int) -> bool:
        """Check if circuit should close from half-open."""
        return success_count >= self.success_threshold


@dataclass
class GovernanceFailureV1:
    """
    Typed failure artifact for exhausted retries.
    
    Schema: governance_failure_v1
    Version: 1.0.0
    """
    schema: str = "governance_failure_v1"
    schema_version: str = "1.0.0"
    operation: str = ""
    model: str = ""
    timestamp: str = ""
    failure_category: FailureCategory = FailureCategory.RETRY_EXHAUSTED
    retry_count: int = 0
    retry_budget: int = 0
    last_error: str = ""
    last_validation_result: Dict[str, Any] = field(default_factory=dict)
    input_hash: str = ""
    circuit_breaker_state: str = ""
    backoff_delays_ms: List[float] = field(default_factory=list)
    recovery_hint: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema": self.schema,
            "schema_version": self.schema_version,
            "operation": self.operation,
            "model": self.model,
            "timestamp": self.timestamp,
            "failure_category": self.failure_category.value,
            "retry_count": self.retry_count,
            "retry_budget": self.retry_budget,
            "last_error": self.last_error,
            "last_validation_result": self.last_validation_result,
            "input_hash": self.input_hash,
            "circuit_breaker_state": self.circuit_breaker_state,
            "backoff_delays_ms": self.backoff_delays_ms,
            "recovery_hint": self.recovery_hint,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GovernanceFailureV1":
        return cls(
            schema=data.get("schema", "governance_failure_v1"),
            schema_version=data.get("schema_version", "1.0.0"),
            operation=data.get("operation", ""),
            model=data.get("model", ""),
            timestamp=data.get("timestamp", ""),
            failure_category=FailureCategory(data.get("failure_category", "retry_exhausted")),
            retry_count=data.get("retry_count", 0),
            retry_budget=data.get("retry_budget", 0),
            last_error=data.get("last_error", ""),
            last_validation_result=data.get("last_validation_result", {}),
            input_hash=data.get("input_hash", ""),
            circuit_breaker_state=data.get("circuit_breaker_state", ""),
            backoff_delays_ms=data.get("backoff_delays_ms", []),
            recovery_hint=data.get("recovery_hint", ""),
        )


@dataclass
class CircuitBreakerV2:
    """
    Enhanced circuit breaker with explicit state transitions.
    
    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Requests blocked, waiting for cooldown
    - HALF_OPEN: Limited requests allowed to test recovery
    """
    operation: str
    model: str
    policy: CircuitBreakerPolicy
    state: str = "closed"
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[datetime] = None
    last_state_change: Optional[datetime] = None
    half_open_calls: int = 0
    
    def __post_init__(self):
        if self.last_state_change is None:
            self.last_state_change = datetime.now(timezone.utc)
    
    def can_execute(self) -> bool:
        """Check if execution is allowed."""
        if self.state == "closed":
            return True
        
        if self.state == "open":
            # Check if cooldown has passed
            if self.last_failure_time:
                elapsed = (datetime.now(timezone.utc) - self.last_failure_time).total_seconds()
                if elapsed >= self.policy.cooldown_s:
                    self._transition_to_half_open()
                    return True
            return False
        
        if self.state == "half_open":
            # Allow limited calls in half-open
            return self.half_open_calls < self.policy.half_open_max_calls
        
        return False
    
    def record_success(self) -> bool:
        """Record success and potentially close circuit."""
        self.success_count += 1
        
        if self.state == "half_open":
            self.half_open_calls += 1
            if self.policy.should_close(self.success_count):
                self._transition_to_closed()
                return True
        
        return False
    
    def record_failure(self) -> bool:
        """Record failure and potentially open circuit."""
        self.failure_count += 1
        self.last_failure_time = datetime.now(timezone.utc)
        self.success_count = 0  # Reset success count
        
        if self.state == "half_open":
            # Failure in half-open -> back to open
            self._transition_to_open()
            return True
        
        if self.state == "closed" and self.policy.should_open(self.failure_count):
            self._transition_to_open()
            return True
        
        return False
    
    def _transition_to_open(self):
        """Transition to OPEN state."""
        self.state = "open"
        self.last_state_change = datetime.now(timezone.utc)
        self.half_open_calls = 0
    
    def _transition_to_half_open(self):
        """Transition to HALF_OPEN state."""
        self.state = "half_open"
        self.last_state_change = datetime.now(timezone.utc)
        self.half_open_calls = 0
        self.success_count = 0
    
    def _transition_to_closed(self):
        """Transition to CLOSED state."""
        self.state = "closed"
        self.last_state_change = datetime.now(timezone.utc)
        self.failure_count = 0
        self.success_count = 0
        self.half_open_calls = 0
    
    def time_in_state_s(self) -> float:
        """Get time spent in current state."""
        if self.last_state_change:
            return (datetime.now(timezone.utc) - self.last_state_change).total_seconds()
        return 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "operation": self.operation,
            "model": self.model,
            "state": self.state,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "last_state_change": self.last_state_change.isoformat() if self.last_state_change else None,
            "half_open_calls": self.half_open_calls,
            "time_in_state_s": self.time_in_state_s(),
            "policy": {
                "failure_threshold": self.policy.failure_threshold,
                "success_threshold": self.policy.success_threshold,
                "cooldown_s": self.policy.cooldown_s,
                "half_open_max_calls": self.policy.half_open_max_calls,
            }
        }


@dataclass
class OperationMetrics:
    """Metrics for a single operation."""
    operation: str
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    total_execution_time_s: float = 0.0
    total_retries: int = 0
    total_backoff_time_s: float = 0.0
    circuit_breaker_opens: int = 0
    circuit_breaker_recoveries: int = 0
    failure_artifacts_generated: int = 0
    
    @property
    def success_rate(self) -> float:
        if self.total_executions == 0:
            return 0.0
        return self.successful_executions / self.total_executions
    
    @property
    def avg_execution_time_s(self) -> float:
        if self.total_executions == 0:
            return 0.0
        return self.total_execution_time_s / self.total_executions
    
    @property
    def avg_retries(self) -> float:
        if self.total_executions == 0:
            return 0.0
        return self.total_retries / self.total_executions
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "operation": self.operation,
            "total_executions": self.total_executions,
            "successful_executions": self.total_executions,
            "failed_executions": self.failed_executions,
            "success_rate": self.success_rate,
            "avg_execution_time_s": self.avg_execution_time_s,
            "avg_retries": self.avg_retries,
            "total_backoff_time_s": self.total_backoff_time_s,
            "circuit_breaker_opens": self.circuit_breaker_opens,
            "circuit_breaker_recoveries": self.circuit_breaker_recoveries,
            "failure_artifacts_generated": self.failure_artifacts_generated,
        }


class VaultGovernanceRuntime:
    """
    Production governance runtime with:
    - Circuit breaker cooldowns and state transitions
    - Retry backoff policy
    - Typed failure artifacts
    - Per-operation metrics dashboards
    """
    
    def __init__(
        self,
        default_backoff: Optional[BackoffPolicy] = None,
        default_breaker_policy: Optional[CircuitBreakerPolicy] = None,
    ):
        self.default_backoff = default_backoff or BackoffPolicy(
            strategy=BackoffStrategy.EXPONENTIAL_JITTER,
            base_delay_s=1.0,
            max_delay_s=60.0,
            multiplier=2.0,
            jitter_factor=0.1,
        )
        self.default_breaker_policy = default_breaker_policy or CircuitBreakerPolicy(
            failure_threshold=5,
            success_threshold=1,
            cooldown_s=30.0,
            half_open_max_calls=3,
        )
        
        self.circuit_breakers: Dict[str, CircuitBreakerV2] = {}
        self.metrics: Dict[str, OperationMetrics] = {}
        self.failure_artifacts: List[GovernanceFailureV1] = []
        self.backoff_policies: Dict[str, BackoffPolicy] = {}
        self.breaker_policies: Dict[str, CircuitBreakerPolicy] = {}
    
    def configure_operation(
        self,
        operation: str,
        backoff: Optional[BackoffPolicy] = None,
        breaker_policy: Optional[CircuitBreakerPolicy] = None,
    ) -> None:
        """Configure governance for a specific operation."""
        if backoff:
            self.backoff_policies[operation] = backoff
        if breaker_policy:
            self.breaker_policies[operation] = breaker_policy
    
    def get_circuit_breaker(
        self,
        operation: str,
        model: str,
    ) -> CircuitBreakerV2:
        """Get or create circuit breaker for operation/model pair."""
        key = f"{operation}:{model}"
        if key not in self.circuit_breakers:
            policy = self.breaker_policies.get(operation, self.default_breaker_policy)
            self.circuit_breakers[key] = CircuitBreakerV2(
                operation=operation,
                model=model,
                policy=policy,
            )
        return self.circuit_breakers[key]
    
    def get_backoff_policy(self, operation: str) -> BackoffPolicy:
        """Get backoff policy for operation."""
        return self.backoff_policies.get(operation, self.default_backoff)
    
    def can_execute(self, operation: str, model: str) -> bool:
        """Check if execution is allowed."""
        breaker = self.get_circuit_breaker(operation, model)
        return breaker.can_execute()
    
    def execute_with_governance(
        self,
        operation: str,
        model: str,
        retry_budget: int,
        input_data: Dict[str, Any],
        executor: Callable[[], Dict[str, Any]],
        validator: Callable[[Dict[str, Any]], Dict[str, Any]],
        input_hash: str = "",
    ) -> tuple[Optional[Dict[str, Any]], Optional[GovernanceFailureV1]]:
        """
        Execute with full governance:
        1. Check circuit breaker
        2. Execute with backoff retries
        3. Validate each attempt
        4. Generate failure artifact on exhaustion
        """
        breaker = self.get_circuit_breaker(operation, model)
        backoff = self.get_backoff_policy(operation)
        metrics = self._get_metrics(operation)
        
        # Check circuit breaker
        if not breaker.can_execute():
            failure = GovernanceFailureV1(
                operation=operation,
                model=model,
                failure_category=FailureCategory.CIRCUIT_BREAKER_OPEN,
                retry_count=0,
                retry_budget=retry_budget,
                last_error="Circuit breaker is open",
                input_hash=input_hash,
                circuit_breaker_state=breaker.state,
                recovery_hint=f"Wait {breaker.policy.cooldown_s}s for circuit breaker cooldown",
            )
            self.failure_artifacts.append(failure)
            metrics.failure_artifacts_generated += 1
            return None, failure
        
        # Execute with retries
        backoff_delays = []
        last_result = None
        last_validation = {"valid": False, "errors": [], "warnings": []}
        
        for attempt in range(retry_budget + 1):
            start_time = time.time()
            
            try:
                result = executor()
                execution_time = time.time() - start_time
                
                # Validate
                validation = validator(result)
                last_validation = validation
                last_result = result
                
                if validation.get("valid", False):
                    # Success
                    breaker.record_success()
                    metrics.total_executions += 1
                    metrics.successful_executions += 1
                    metrics.total_execution_time_s += execution_time
                    
                    # Check for circuit breaker recovery
                    if breaker.state == "closed" and breaker.success_count == 1:
                        if breaker.failure_count > 0:
                            metrics.circuit_breaker_recoveries += 1
                    
                    return result, None
                
                # Validation failed
                if attempt < retry_budget:
                    # Calculate backoff delay
                    delay_s = backoff.calculate_delay(attempt)
                    backoff_delays.append(delay_s * 1000)  # Convert to ms
                    metrics.total_backoff_time_s += delay_s
                    time.sleep(delay_s)
                
            except Exception as e:
                execution_time = time.time() - start_time
                last_validation = {
                    "valid": False,
                    "errors": [str(e)],
                    "warnings": [],
                }
                
                if attempt < retry_budget:
                    delay_s = backoff.calculate_delay(attempt)
                    backoff_delays.append(delay_s * 1000)
                    metrics.total_backoff_time_s += delay_s
                    time.sleep(delay_s)
        
        # All retries exhausted
        breaker.record_failure()
        metrics.total_executions += 1
        metrics.failed_executions += 1
        metrics.total_retries += retry_budget
        
        # Check for circuit breaker open
        if breaker.state == "open":
            metrics.circuit_breaker_opens += 1
        
        # Generate failure artifact
        failure = GovernanceFailureV1(
            operation=operation,
            model=model,
            failure_category=FailureCategory.RETRY_EXHAUSTED,
            retry_count=retry_budget,
            retry_budget=retry_budget,
            last_error="; ".join(last_validation.get("errors", [])),
            last_validation_result=last_validation,
            input_hash=input_hash,
            circuit_breaker_state=breaker.state,
            backoff_delays_ms=backoff_delays,
            recovery_hint="Check validation errors and adjust input or model parameters",
        )
        self.failure_artifacts.append(failure)
        metrics.failure_artifacts_generated += 1
        
        return None, failure
    
    def get_metrics(self, operation: Optional[str] = None) -> Dict[str, Any]:
        """Get metrics for operation(s)."""
        if operation:
            m = self._get_metrics(operation)
            return m.to_dict()
        return {op: m.to_dict() for op, m in self.metrics.items()}
    
    def get_dashboard(self) -> Dict[str, Any]:
        """Get governance dashboard summary."""
        total_executions = sum(m.total_executions for m in self.metrics.values())
        total_successes = sum(m.successful_executions for m in self.metrics.values())
        total_failures = sum(m.failed_executions for m in self.metrics.values())
        
        open_breakers = sum(
            1 for b in self.circuit_breakers.values() if b.state == "open"
        )
        half_open_breakers = sum(
            1 for b in self.circuit_breakers.values() if b.state == "half_open"
        )
        
        return {
            "summary": {
                "total_executions": total_executions,
                "total_successes": total_successes,
                "total_failures": total_failures,
                "overall_success_rate": total_successes / total_executions if total_executions > 0 else 0.0,
                "total_failure_artifacts": len(self.failure_artifacts),
            },
            "circuit_breakers": {
                "total": len(self.circuit_breakers),
                "closed": len(self.circuit_breakers) - open_breakers - half_open_breakers,
                "open": open_breakers,
                "half_open": half_open_breakers,
            },
            "operations": {op: m.to_dict() for op, m in self.metrics.items()},
        }
    
    def get_failure_artifacts(
        self,
        operation: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Get failure artifacts."""
        artifacts = self.failure_artifacts
        if operation:
            artifacts = [a for a in artifacts if a.operation == operation]
        return [a.to_dict() for a in artifacts[-limit:]]
    
    def _get_metrics(self, operation: str) -> OperationMetrics:
        """Get or create metrics for operation."""
        if operation not in self.metrics:
            self.metrics[operation] = OperationMetrics(operation=operation)
        return self.metrics[operation]


def create_governance_runtime(
    backoff: Optional[BackoffPolicy] = None,
    breaker_policy: Optional[CircuitBreakerPolicy] = None,
) -> VaultGovernanceRuntime:
    """Create a new governance runtime instance."""
    return VaultGovernanceRuntime(
        default_backoff=backoff,
        default_breaker_policy=breaker_policy,
    )


# Export
__all__ = [
    "BackoffStrategy",
    "FailureCategory",
    "BackoffPolicy",
    "CircuitBreakerPolicy",
    "GovernanceFailureV1",
    "CircuitBreakerV2",
    "OperationMetrics",
    "VaultGovernanceRuntime",
    "create_governance_runtime",
]


if __name__ == "__main__":
    import json
    
    print("=" * 80)
    print("VAULT GOVERNANCE RUNTIME")
    print("=" * 80)
    
    # Create runtime with custom policies
    runtime = create_governance_runtime(
        backoff=BackoffPolicy(
            strategy=BackoffStrategy.EXPONENTIAL_JITTER,
            base_delay_s=0.5,
            max_delay_s=10.0,
            multiplier=2.0,
        ),
        breaker_policy=CircuitBreakerPolicy(
            failure_threshold=3,
            success_threshold=1,
            cooldown_s=5.0,
            half_open_max_calls=2,
        ),
    )
    
    # Configure operation-specific policies
    runtime.configure_operation(
        "vae_checkpoint_validation",
        backoff=BackoffPolicy(
            strategy=BackoffStrategy.EXPONENTIAL_JITTER,
            base_delay_s=1.0,
            max_delay_s=30.0,
        ),
        breaker_policy=CircuitBreakerPolicy(
            failure_threshold=5,
            cooldown_s=60.0,
        ),
    )
    
    print("\nBACKOFF POLICY DEMO")
    print("-" * 40)
    backoff = runtime.get_backoff_policy("vae_checkpoint_validation")
    print(f"Strategy: {backoff.strategy.value}")
    print(f"Delays for 5 attempts:")
    for i in range(5):
        delay = backoff.calculate_delay(i)
        print(f"  Attempt {i+1}: {delay:.2f}s")
    
    print("\nCIRCUIT BREAKER DEMO")
    print("-" * 40)
    breaker = runtime.get_circuit_breaker("vae_checkpoint_validation", "qwen3-coder-next:cloud")
    print(f"Initial state: {breaker.state}")
    print(f"Can execute: {breaker.can_execute()}")
    
    # Simulate failures
    print("\nSimulating 3 failures...")
    for i in range(3):
        breaker.record_failure()
        print(f"  Failure {i+1}: state={breaker.state}, failures={breaker.failure_count}")
    
    print(f"\nCan execute after failures: {breaker.can_execute()}")
    print(f"State: {breaker.state}")
    
    # Simulate cooldown
    print("\nSimulating cooldown (5s)...")
    breaker.last_failure_time = datetime.now(timezone.utc)
    breaker.state = "open"
    
    print(f"State after open: {breaker.state}")
    print(f"Can execute: {breaker.can_execute()}")
    
    # Dashboard
    print("\n" + "=" * 80)
    print("GOVERNANCE DASHBOARD")
    print("=" * 80)
    dashboard = runtime.get_dashboard()
    print(json.dumps(dashboard, indent=2))
    
    # Failure artifact
    print("\n" + "=" * 80)
    print("FAILURE ARTIFACT SCHEMA")
    print("=" * 80)
    failure = GovernanceFailureV1(
        operation="vae_checkpoint_validation",
        model="qwen3-coder-next:cloud",
        failure_category=FailureCategory.RETRY_EXHAUSTED,
        retry_count=3,
        retry_budget=3,
        last_error="Schema validation failed: 'verdict' is required",
        last_validation_result={"valid": False, "errors": ["'verdict' is required"]},
        input_hash="abc123",
        circuit_breaker_state="closed",
        backoff_delays_ms=[1000, 2000, 4000],
        recovery_hint="Ensure output includes 'verdict' field",
    )
    print(json.dumps(failure.to_dict(), indent=2))