"""Vault Governance Layer - Controlled Inference Governance.

Extends the operation config with:
- Retry strategies (plain, validation_feedback, repair_patch)
- Circuit breaker thresholds
- Schema versioning
- Idempotency tracking
- Audit logging

This transforms the config from metadata to a controlled inference governance layer.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import json


class RetryStrategy(Enum):
    """Retry strategy for failed operations."""
    PLAIN = "plain"                       # Simple retry without feedback
    VALIDATION_FEEDBACK = "validation_feedback"  # Feed validation errors back to model
    REPAIR_PATCH = "repair_patch"         # Attempt repair with patch instructions


class CircuitBreakerState(Enum):
    """Circuit breaker state for operation/model pairs."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"         # Disabled due to failures
    HALF_OPEN = "half_open"  # Testing if recovered


@dataclass(frozen=True)
class GovernanceConfig:
    """Governance configuration for a Vault operation.
    
    Extends OperationConfig with:
    - retry_strategy: How to handle retries
    - circuit_breaker_threshold: Failures before disabling
    - schema_version: Contract version
    - idempotent: Safe for automatic retry
    - audit_log_fields: Required traceability fields
    """
    operation: str
    retry_strategy: RetryStrategy
    circuit_breaker_threshold: int
    schema_version: str
    idempotent: bool
    audit_log_fields: List[str]
    max_consecutive_failures: int = 5
    recovery_timeout_s: int = 300
    enable_metrics: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "operation": self.operation,
            "retry_strategy": self.retry_strategy.value,
            "circuit_breaker_threshold": self.circuit_breaker_threshold,
            "schema_version": self.schema_version,
            "idempotent": self.idempotent,
            "audit_log_fields": self.audit_log_fields,
            "max_consecutive_failures": self.max_consecutive_failures,
            "recovery_timeout_s": self.recovery_timeout_s,
            "enable_metrics": self.enable_metrics,
        }


@dataclass
class CircuitBreaker:
    """Circuit breaker for operation/model pairs."""
    operation: str
    model: str
    state: CircuitBreakerState = CircuitBreakerState.CLOSED
    failure_count: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    
    def record_failure(self) -> None:
        """Record a failure and potentially open the circuit."""
        self.failure_count += 1
        self.last_failure_time = datetime.now(timezone.utc)
    
    def record_success(self) -> None:
        """Record a success and reset the circuit."""
        self.failure_count = 0
        self.last_success_time = datetime.now(timezone.utc)
        self.state = CircuitBreakerState.CLOSED
    
    def should_allow(self, threshold: int, recovery_timeout_s: int) -> bool:
        """Check if operation should be allowed."""
        if self.state == CircuitBreakerState.CLOSED:
            return True
        
        if self.state == CircuitBreakerState.OPEN:
            # Check if recovery timeout has passed
            if self.last_failure_time:
                elapsed = (datetime.now(timezone.utc) - self.last_failure_time).total_seconds()
                if elapsed >= recovery_timeout_s:
                    self.state = CircuitBreakerState.HALF_OPEN
                    return True
            return False
        
        # HALF_OPEN: allow one attempt
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "operation": self.operation,
            "model": self.model,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "last_success_time": self.last_success_time.isoformat() if self.last_success_time else None,
        }


@dataclass
class AuditLogEntry:
    """Audit log entry for operation execution."""
    operation: str
    model: str
    timestamp: datetime
    success: bool
    validation_result: Dict[str, Any]
    retry_count: int
    execution_time_s: float
    input_hash: str
    output_hash: str
    required_fields: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "operation": self.operation,
            "model": self.model,
            "timestamp": self.timestamp.isoformat(),
            "success": self.success,
            "validation_result": self.validation_result,
            "retry_count": self.retry_count,
            "execution_time_s": self.execution_time_s,
            "input_hash": self.input_hash,
            "output_hash": self.output_hash,
            "required_fields": self.required_fields,
        }


# Governance configurations for each operation
GOVERNANCE_CONFIGS: Dict[str, GovernanceConfig] = {
    "vae_checkpoint_validation": GovernanceConfig(
        operation="vae_checkpoint_validation",
        retry_strategy=RetryStrategy.VALIDATION_FEEDBACK,
        circuit_breaker_threshold=5,
        schema_version="1.0.0",
        idempotent=True,
        audit_log_fields=["verdict", "confidence", "metrics_summary", "timestamp"],
        max_consecutive_failures=5,
        recovery_timeout_s=300,
    ),
    
    "ci_audit_oracle": GovernanceConfig(
        operation="ci_audit_oracle",
        retry_strategy=RetryStrategy.VALIDATION_FEEDBACK,
        circuit_breaker_threshold=3,
        schema_version="1.0.0",
        idempotent=True,
        audit_log_fields=["verdict", "reason", "artifacts_checked", "timestamp"],
        max_consecutive_failures=3,
        recovery_timeout_s=180,
    ),
    
    "vae_loss_interpretation": GovernanceConfig(
        operation="vae_loss_interpretation",
        retry_strategy=RetryStrategy.VALIDATION_FEEDBACK,
        circuit_breaker_threshold=5,
        schema_version="1.0.0",
        idempotent=False,  # Recommendations may vary
        audit_log_fields=["loss_breakdown", "interpretation", "recommendation", "timestamp"],
        max_consecutive_failures=5,
        recovery_timeout_s=300,
    ),
    
    "phi_artifact_analysis": GovernanceConfig(
        operation="phi_artifact_analysis",
        retry_strategy=RetryStrategy.VALIDATION_FEEDBACK,
        circuit_breaker_threshold=5,
        schema_version="1.0.0",
        idempotent=False,  # Analysis may vary
        audit_log_fields=["phi_metrics", "analysis", "next_experiment", "timestamp"],
        max_consecutive_failures=5,
        recovery_timeout_s=300,
    ),
    
    "eval_case_generation": GovernanceConfig(
        operation="eval_case_generation",
        retry_strategy=RetryStrategy.PLAIN,  # Generation can use simple retry
        circuit_breaker_threshold=3,
        schema_version="1.0.0",
        idempotent=False,  # Generated cases may differ
        audit_log_fields=["cases", "count", "timestamp"],
        max_consecutive_failures=3,
        recovery_timeout_s=180,
    ),
    
    "research_report_generation": GovernanceConfig(
        operation="research_report_generation",
        retry_strategy=RetryStrategy.PLAIN,  # Reports can use simple retry
        circuit_breaker_threshold=3,
        schema_version="1.0.0",
        idempotent=False,  # Reports may vary
        audit_log_fields=["title", "summary", "sections", "timestamp"],
        max_consecutive_failures=3,
        recovery_timeout_s=600,
    ),
}


class VaultGovernanceLayer:
    """
    Controlled inference governance layer for Vault operations.
    
    Features:
    - Retry strategies with validation feedback
    - Circuit breaker for operation/model pairs
    - Schema versioning
    - Idempotency tracking
    - Audit logging
    """
    
    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.audit_log: List[AuditLogEntry] = []
        self.metrics: Dict[str, Dict[str, Any]] = {}
    
    def get_governance_config(self, operation: str) -> Optional[GovernanceConfig]:
        """Get governance configuration for an operation."""
        return GOVERNANCE_CONFIGS.get(operation)
    
    def get_circuit_breaker(self, operation: str, model: str) -> CircuitBreaker:
        """Get or create circuit breaker for operation/model pair."""
        key = f"{operation}:{model}"
        if key not in self.circuit_breakers:
            self.circuit_breakers[key] = CircuitBreaker(operation=operation, model=model)
        return self.circuit_breakers[key]
    
    def should_allow_operation(
        self,
        operation: str,
        model: str,
        config: Optional[GovernanceConfig] = None
    ) -> bool:
        """Check if operation should be allowed based on circuit breaker state."""
        config = config or self.get_governance_config(operation)
        if not config:
            return True
        
        breaker = self.get_circuit_breaker(operation, model)
        return breaker.should_allow(
            config.circuit_breaker_threshold,
            config.recovery_timeout_s
        )
    
    def record_execution(
        self,
        operation: str,
        model: str,
        success: bool,
        validation_result: Dict[str, Any],
        retry_count: int,
        execution_time_s: float,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        config: Optional[GovernanceConfig] = None
    ) -> AuditLogEntry:
        """Record an execution in the audit log."""
        config = config or self.get_governance_config(operation)
        
        # Extract required fields
        required_fields = {}
        if config:
            for field in config.audit_log_fields:
                if field in output_data:
                    required_fields[field] = output_data[field]
        
        # Create audit entry
        entry = AuditLogEntry(
            operation=operation,
            model=model,
            timestamp=datetime.now(timezone.utc),
            success=success,
            validation_result=validation_result,
            retry_count=retry_count,
            execution_time_s=execution_time_s,
            input_hash=self._hash_dict(input_data),
            output_hash=self._hash_dict(output_data),
            required_fields=required_fields,
        )
        
        self.audit_log.append(entry)
        
        # Update circuit breaker
        breaker = self.get_circuit_breaker(operation, model)
        if success:
            breaker.record_success()
        else:
            breaker.record_failure()
        
        # Update metrics
        self._update_metrics(operation, success, execution_time_s, retry_count)
        
        return entry
    
    def build_retry_prompt(
        self,
        operation: str,
        original_prompt: str,
        validation_result: Dict[str, Any],
        strategy: RetryStrategy
    ) -> str:
        """Build retry prompt based on strategy."""
        if strategy == RetryStrategy.PLAIN:
            return original_prompt
        
        elif strategy == RetryStrategy.VALIDATION_FEEDBACK:
            errors = validation_result.get("errors", [])
            warnings = validation_result.get("warnings", [])
            
            feedback = f"""
The previous output failed validation. Please correct and regenerate.

Validation Errors:
{json.dumps(errors, indent=2)}

Warnings:
{json.dumps(warnings, indent=2)}

Original Request:
{original_prompt}

Please fix the validation errors and provide a corrected response that satisfies the schema.
"""
            return feedback
        
        elif strategy == RetryStrategy.REPAIR_PATCH:
            errors = validation_result.get("errors", [])
            
            patch_prompt = f"""
The previous output had validation errors. Generate a JSON patch to fix them.

Errors:
{json.dumps(errors, indent=2)}

Generate a JSON patch following RFC 6902 format to correct the errors.
"""
            return patch_prompt
        
        return original_prompt
    
    def get_metrics(self, operation: Optional[str] = None) -> Dict[str, Any]:
        """Get metrics for operation(s)."""
        if operation:
            return self.metrics.get(operation, {})
        return self.metrics
    
    def get_audit_log(
        self,
        operation: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get audit log entries."""
        entries = self.audit_log
        if operation:
            entries = [e for e in entries if e.operation == operation]
        return [e.to_dict() for e in entries[-limit:]]
    
    def get_circuit_breaker_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all circuit breakers."""
        return {k: v.to_dict() for k, v in self.circuit_breakers.items()}
    
    def _hash_dict(self, data: Dict[str, Any]) -> str:
        """Create hash of dict for audit trail."""
        import hashlib
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()[:16]
    
    def _update_metrics(
        self,
        operation: str,
        success: bool,
        execution_time_s: float,
        retry_count: int
    ) -> None:
        """Update metrics for operation."""
        if operation not in self.metrics:
            self.metrics[operation] = {
                "total_executions": 0,
                "successful_executions": 0,
                "failed_executions": 0,
                "total_execution_time_s": 0.0,
                "total_retries": 0,
                "avg_execution_time_s": 0.0,
                "success_rate": 0.0,
            }
        
        m = self.metrics[operation]
        m["total_executions"] += 1
        m["total_execution_time_s"] += execution_time_s
        m["total_retries"] += retry_count
        
        if success:
            m["successful_executions"] += 1
        else:
            m["failed_executions"] += 1
        
        m["avg_execution_time_s"] = m["total_execution_time_s"] / m["total_executions"]
        m["success_rate"] = m["successful_executions"] / m["total_executions"]


def create_governance_layer() -> VaultGovernanceLayer:
    """Create a new governance layer instance."""
    return VaultGovernanceLayer()


# Export
__all__ = [
    "RetryStrategy",
    "CircuitBreakerState",
    "GovernanceConfig",
    "CircuitBreaker",
    "AuditLogEntry",
    "GOVERNANCE_CONFIGS",
    "VaultGovernanceLayer",
    "create_governance_layer",
]


if __name__ == "__main__":
    import json
    
    print("=" * 80)
    print("VAULT GOVERNANCE LAYER")
    print("=" * 80)
    
    # Print governance configs
    print("\nGOVERNANCE CONFIGURATIONS")
    print("-" * 40)
    for op, config in GOVERNANCE_CONFIGS.items():
        print(f"\n{op}:")
        print(f"  Retry Strategy: {config.retry_strategy.value}")
        print(f"  Circuit Breaker Threshold: {config.circuit_breaker_threshold}")
        print(f"  Schema Version: {config.schema_version}")
        print(f"  Idempotent: {config.idempotent}")
        print(f"  Audit Fields: {', '.join(config.audit_log_fields)}")
    
    # Demo governance layer
    print("\n" + "=" * 80)
    print("GOVERNANCE LAYER DEMO")
    print("=" * 80)
    
    gov = create_governance_layer()
    
    # Simulate execution
    print("\nSimulating vae_checkpoint_validation execution...")
    
    # Check if allowed
    allowed = gov.should_allow_operation("vae_checkpoint_validation", "qwen3-coder-next:cloud")
    print(f"  Operation allowed: {allowed}")
    
    # Record successful execution
    entry = gov.record_execution(
        operation="vae_checkpoint_validation",
        model="qwen3-coder-next:cloud",
        success=True,
        validation_result={"valid": True, "errors": [], "warnings": []},
        retry_count=0,
        execution_time_s=1.5,
        input_data={"checkpoint": "best_model.pt"},
        output_data={"verdict": "pass", "confidence": 0.95, "metrics_summary": {}, "recommendation": "OK"},
    )
    print(f"  Audit entry created: {entry.timestamp}")
    
    # Get metrics
    metrics = gov.get_metrics("vae_checkpoint_validation")
    print(f"\nMetrics:")
    print(f"  {json.dumps(metrics, indent=2)}")
    
    # Get circuit breaker status
    status = gov.get_circuit_breaker_status()
    print(f"\nCircuit Breaker Status:")
    print(f"  {json.dumps(status, indent=2)}")
    
    # Demo retry prompt
    print("\n" + "=" * 80)
    print("RETRY PROMPT DEMO")
    print("=" * 80)
    
    config = gov.get_governance_config("vae_checkpoint_validation")
    retry_prompt = gov.build_retry_prompt(
        operation="vae_checkpoint_validation",
        original_prompt="Validate checkpoint",
        validation_result={
            "valid": False,
            "errors": ["Missing required field: verdict", "Confidence out of range: 1.5"],
            "warnings": []
        },
        strategy=config.retry_strategy
    )
    print(retry_prompt)