"""Schema-Invalid Burn-Down Module for vae_checkpoint_validation.

Focused effort to reduce schema-invalid failures from 12 to < transport failures.

Target metrics:
- Success rate: ≥ 0.90
- Retry-adjusted success rate: ≥ 0.80
- Schema-invalid share: < transport-failure share
- Schema-invalid count: < 9 (current transport failures)
- P95 latency: < 3.0s

Strategies:
1. Tighten prompt contracts with explicit schema requirements
2. Add per-outcome retry policies
3. Implement release gates with retry-adjusted metrics
4. Track burn-down progress with error leaderboard
5. Regression testing against canonical failure cases
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import json


@dataclass
class SchemaViolation:
    """Recorded schema violation for analysis."""
    timestamp: str
    operation: str
    error: str
    field: str
    value: Any
    expected_type: str
    retry_count: int
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "operation": self.operation,
            "error": self.error,
            "field": self.field,
            "value": self.value,
            "expected_type": self.expected_type,
            "retry_count": self.retry_count,
        }


@dataclass
class PromptContract:
    """
    Tightened prompt contract for schema conformance.
    
    Includes:
    - Explicit field requirements
    - Type constraints
    - Enum values
    - Examples
    - Anti-patterns to avoid
    """
    operation: str
    schema_name: str
    required_fields: List[str]
    field_types: Dict[str, str]
    enum_values: Dict[str, List[str]]
    examples: List[Dict[str, Any]]
    anti_patterns: List[str]
    retry_feedback_template: str
    
    def generate_prompt_enhancement(self) -> str:
        """Generate prompt enhancement for schema conformance."""
        lines = [
            f"SCHEMA REQUIREMENTS for {self.operation}:",
            "",
            "Required fields (ALL must be present):",
        ]
        
        for field in self.required_fields:
            field_type = self.field_types.get(field, "any")
            enums = self.enum_values.get(field, [])
            enum_str = f" (one of: {', '.join(enums)})" if enums else ""
            lines.append(f"  - {field}: {field_type}{enum_str}")
        
        lines.extend([
            "",
            "Valid example:",
            f"  {json.dumps(self.examples[0], indent=2)}" if self.examples else "  (none provided)",
            "",
            "AVOID these anti-patterns:",
        ])
        
        for pattern in self.anti_patterns:
            lines.append(f"  - {pattern}")
        
        lines.extend([
            "",
            "CRITICAL: Output MUST be valid JSON matching the schema exactly.",
            "Missing required fields or invalid values will cause rejection.",
        ])
        
        return "\n".join(lines)
    
    def generate_retry_feedback(
        self,
        validation_errors: List[str],
        attempt: int,
    ) -> str:
        """Generate feedback for retry prompt."""
        return self.retry_feedback_template.format(
            errors="\n".join(f"  - {e}" for e in validation_errors),
            attempt=attempt,
            schema=self.generate_prompt_enhancement(),
        )


# Tightened prompt contract for vae_checkpoint_validation
VAE_CHECKPOINT_CONTRACT = PromptContract(
    operation="vae_checkpoint_validation",
    schema_name="vae_checkpoint_validation",
    required_fields=["verdict", "confidence", "metrics_summary", "recommendation"],
    field_types={
        "verdict": "string",
        "confidence": "number",
        "metrics_summary": "object",
        "recommendation": "string",
    },
    enum_values={
        "verdict": ["pass", "fail", "warning"],
    },
    examples=[
        {
            "verdict": "pass",
            "confidence": 0.95,
            "metrics_summary": {
                "reconstruction_loss": 0.02,
                "kl_divergence": 0.001,
                "quantum_coherence": 0.85,
            },
            "recommendation": "Checkpoint is valid and ready for deployment.",
        }
    ],
    anti_patterns=[
        "Missing 'verdict' field",
        "Using 'valid' instead of 'verdict'",
        "Confidence > 1.0 or < 0.0",
        "Empty metrics_summary object",
        "Verdict value not in ['pass', 'fail', 'warning']",
        "Extra fields not in schema",
    ],
    retry_feedback_template="""
VALIDATION FAILED - Attempt {attempt}

The previous output was rejected due to schema violations:
{errors}

CORRECT SCHEMA:
{schema}

Please regenerate with ALL required fields matching the schema exactly.
""",
)


@dataclass
class PerOutcomeRetryPolicy:
    """
    Retry policy keyed to outcome type.
    
    Maps each RetryOutcome to:
    - Whether to retry
    - Max retries
    - Backoff strategy
    - Feedback template
    """
    outcome_policies: Dict[str, Dict[str, Any]] = field(default_factory=lambda: {
        "success": {
            "retry": False,
            "max_retries": 0,
            "backoff": "none",
            "feedback": None,
        },
        "schema_invalid": {
            "retry": True,
            "max_retries": 3,
            "backoff": "exponential_jitter",
            "feedback": "validation_feedback",
        },
        "business_invalid": {
            "retry": True,
            "max_retries": 2,
            "backoff": "exponential_jitter",
            "feedback": "validation_feedback",
        },
        "transient": {
            "retry": True,
            "max_retries": 5,
            "backoff": "full_jitter",
            "feedback": None,
        },
        "timeout": {
            "retry": True,
            "max_retries": 3,
            "backoff": "exponential_jitter",
            "feedback": None,
        },
        "breaker_open": {
            "retry": False,
            "max_retries": 0,
            "backoff": "none",
            "feedback": None,
        },
        "non_retryable": {
            "retry": False,
            "max_retries": 0,
            "backoff": "none",
            "feedback": None,
        },
        "exhausted": {
            "retry": False,
            "max_retries": 0,
            "backoff": "none",
            "feedback": None,
        },
    })
    
    def get_policy(self, outcome: str) -> Dict[str, Any]:
        return self.outcome_policies.get(outcome, self.outcome_policies["non_retryable"])
    
    def should_retry(self, outcome: str, attempt: int) -> bool:
        policy = self.get_policy(outcome)
        if not policy["retry"]:
            return False
        return attempt < policy["max_retries"]
    
    def get_max_retries(self, outcome: str) -> int:
        return self.get_policy(outcome).get("max_retries", 0)
    
    def get_backoff(self, outcome: str) -> str:
        return self.get_policy(outcome).get("backoff", "none")
    
    def get_feedback_type(self, outcome: str) -> Optional[str]:
        return self.get_policy(outcome).get("feedback")


@dataclass
class ReleaseGate:
    """
    Release gate criteria for operation stability.
    
    An operation is considered stable when:
    - Success rate ≥ threshold
    - Schema-invalid share < transport-failure share
    - Schema-invalid count < threshold
    """
    operation: str
    min_success_rate: float = 0.90
    max_schema_invalid_share: float = 0.50  # Must be < 50% of failures
    max_schema_invalid_count: int = 9
    
    def evaluate(
        self,
        success_rate: float,
        schema_invalid_count: int,
        transport_failure_count: int,
    ) -> Dict[str, Any]:
        """Evaluate if operation passes release gate."""
        total_failures = schema_invalid_count + transport_failure_count
        schema_invalid_share = (
            schema_invalid_count / total_failures if total_failures > 0 else 0.0
        )
        
        checks = {
            "success_rate": {
                "value": success_rate,
                "threshold": self.min_success_rate,
                "pass": success_rate >= self.min_success_rate,
            },
            "schema_invalid_share": {
                "value": schema_invalid_share,
                "threshold": self.max_schema_invalid_share,
                "pass": schema_invalid_share < self.max_schema_invalid_share,
            },
            "schema_invalid_count": {
                "value": schema_invalid_count,
                "threshold": self.max_schema_invalid_count,
                "pass": schema_invalid_count < self.max_schema_invalid_count,
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
            return f"✅ {self.operation} is STABLE and passes all release gates."
        
        failures = [name for name, check in checks.items() if not check["pass"]]
        return f"❌ {self.operation} is NOT STABLE. Failed checks: {', '.join(failures)}"


@dataclass
class BurnDownTracker:
    """
    Track progress toward schema-invalid burn-down target.
    
    Records:
    - Baseline metrics
    - Current metrics
    - Improvement trend
    """
    operation: str
    baseline_schema_invalid: int
    baseline_transport: int
    baseline_success_rate: float
    target_schema_invalid: int
    target_success_rate: float
    history: List[Dict[str, Any]] = field(default_factory=list)
    
    def record(
        self,
        schema_invalid: int,
        transport: int,
        success_rate: float,
        timestamp: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Record current metrics and calculate progress."""
        if timestamp is None:
            timestamp = datetime.now(timezone.utc).isoformat()
        
        schema_invalid_reduction = self.baseline_schema_invalid - schema_invalid
        schema_invalid_target = self.baseline_schema_invalid - self.target_schema_invalid
        progress_pct = (
            schema_invalid_reduction / schema_invalid_target * 100
            if schema_invalid_target > 0 else 100.0
        )
        
        success_rate_improvement = success_rate - self.baseline_success_rate
        success_rate_target = self.target_success_rate - self.baseline_success_rate
        success_progress_pct = (
            success_rate_improvement / success_rate_target * 100
            if success_rate_target > 0 else 100.0
        )
        
        entry = {
            "timestamp": timestamp,
            "schema_invalid": schema_invalid,
            "transport": transport,
            "success_rate": success_rate,
            "schema_invalid_reduction": schema_invalid_reduction,
            "progress_pct": min(progress_pct, 100.0),
            "success_rate_improvement": success_rate_improvement,
            "success_progress_pct": min(success_progress_pct, 100.0),
            "on_track": schema_invalid <= self.target_schema_invalid and success_rate >= self.target_success_rate,
        }
        
        self.history.append(entry)
        return entry
    
    def get_status(self) -> Dict[str, Any]:
        """Get current burn-down status."""
        if not self.history:
            return {
                "status": "no_data",
                "baseline": {
                    "schema_invalid": self.baseline_schema_invalid,
                    "transport": self.baseline_transport,
                    "success_rate": self.baseline_success_rate,
                },
                "target": {
                    "schema_invalid": self.target_schema_invalid,
                    "success_rate": self.target_success_rate,
                },
            }
        
        latest = self.history[-1]
        return {
            "status": "on_track" if latest["on_track"] else "off_track",
            "baseline": {
                "schema_invalid": self.baseline_schema_invalid,
                "transport": self.baseline_transport,
                "success_rate": self.baseline_success_rate,
            },
            "current": {
                "schema_invalid": latest["schema_invalid"],
                "transport": latest["transport"],
                "success_rate": latest["success_rate"],
            },
            "target": {
                "schema_invalid": self.target_schema_invalid,
                "success_rate": self.target_success_rate,
            },
            "progress": {
                "schema_invalid_reduction": latest["schema_invalid_reduction"],
                "progress_pct": latest["progress_pct"],
                "success_rate_improvement": latest["success_rate_improvement"],
                "success_progress_pct": latest["success_progress_pct"],
            },
        }


class SchemaInvalidBurnDown:
    """
    Focused schema-invalid burn-down for vae_checkpoint_validation.
    
    Goal: Reduce schema-invalid failures from 12 to < 9
    Target: Success rate ≥ 0.90
    """
    
    def __init__(self):
        self.contract = VAE_CHECKPOINT_CONTRACT
        self.retry_policy = PerOutcomeRetryPolicy()
        self.release_gate = ReleaseGate(
            operation="vae_checkpoint_validation",
            min_success_rate=0.90,
            max_schema_invalid_share=0.50,
            max_schema_invalid_count=9,
        )
        self.tracker = BurnDownTracker(
            operation="vae_checkpoint_validation",
            baseline_schema_invalid=12,
            baseline_transport=9,
            baseline_success_rate=0.58,
            target_schema_invalid=8,  # Target < 9
            target_success_rate=0.90,
        )
        self.violations: List[SchemaViolation] = []
    
    def record_violation(
        self,
        error: str,
        field: str,
        value: Any,
        expected_type: str,
        retry_count: int,
    ) -> SchemaViolation:
        """Record a schema violation for analysis."""
        violation = SchemaViolation(
            timestamp=datetime.now(timezone.utc).isoformat(),
            operation=self.contract.operation,
            error=error,
            field=field,
            value=value,
            expected_type=expected_type,
            retry_count=retry_count,
        )
        self.violations.append(violation)
        return violation
    
    def analyze_violations(self) -> Dict[str, Any]:
        """Analyze recorded violations for patterns."""
        if not self.violations:
            return {"total": 0, "by_field": {}, "by_error": {}}
        
        by_field: Dict[str, int] = {}
        by_error: Dict[str, int] = {}
        
        for v in self.violations:
            by_field[v.field] = by_field.get(v.field, 0) + 1
            by_error[v.error] = by_error.get(v.error, 0) + 1
        
        return {
            "total": len(self.violations),
            "by_field": by_field,
            "by_error": by_error,
            "top_field": max(by_field.items(), key=lambda x: x[1]) if by_field else None,
            "top_error": max(by_error.items(), key=lambda x: x[1]) if by_error else None,
        }
    
    def get_prompt_enhancement(self) -> str:
        """Get prompt enhancement for schema conformance."""
        return self.contract.generate_prompt_enhancement()
    
    def get_retry_feedback(
        self,
        validation_errors: List[str],
        attempt: int,
    ) -> str:
        """Get feedback for retry prompt."""
        return self.contract.generate_retry_feedback(validation_errors, attempt)
    
    def evaluate_release_gate(
        self,
        success_rate: float,
        schema_invalid_count: int,
        transport_failure_count: int,
    ) -> Dict[str, Any]:
        """Evaluate if operation passes release gate."""
        return self.release_gate.evaluate(
            success_rate,
            schema_invalid_count,
            transport_failure_count,
        )
    
    def record_progress(
        self,
        schema_invalid: int,
        transport: int,
        success_rate: float,
    ) -> Dict[str, Any]:
        """Record burn-down progress."""
        return self.tracker.record(schema_invalid, transport, success_rate)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current burn-down status."""
        return {
            "release_gate": self.evaluate_release_gate(
                self.tracker.history[-1]["success_rate"] if self.tracker.history else 0.58,
                self.tracker.history[-1]["schema_invalid"] if self.tracker.history else 12,
                self.tracker.history[-1]["transport"] if self.tracker.history else 9,
            ),
            "burn_down": self.tracker.get_status(),
            "violations": self.analyze_violations(),
        }


def create_burn_down() -> SchemaInvalidBurnDown:
    """Create a burn-down instance for vae_checkpoint_validation."""
    return SchemaInvalidBurnDown()


# Export
__all__ = [
    "SchemaViolation",
    "PromptContract",
    "VAE_CHECKPOINT_CONTRACT",
    "PerOutcomeRetryPolicy",
    "ReleaseGate",
    "BurnDownTracker",
    "SchemaInvalidBurnDown",
    "create_burn_down",
]


if __name__ == "__main__":
    import json
    
    print("=" * 80)
    print("SCHEMA-INVALID BURN-DOWN FOR vae_checkpoint_validation")
    print("=" * 80)
    
    burn_down = create_burn_down()
    
    # Show prompt enhancement
    print("\n" + "=" * 80)
    print("PROMPT ENHANCEMENT")
    print("=" * 80)
    print(burn_down.get_prompt_enhancement())
    
    # Show retry feedback
    print("\n" + "=" * 80)
    print("RETRY FEEDBACK EXAMPLE")
    print("=" * 80)
    feedback = burn_down.get_retry_feedback(
        validation_errors=[
            "Missing required field: 'verdict'",
            "Invalid value for 'confidence': 1.5 (must be 0.0-1.0)",
        ],
        attempt=1,
    )
    print(feedback)
    
    # Show per-outcome retry policy
    print("\n" + "=" * 80)
    print("PER-OUTCOME RETRY POLICY")
    print("=" * 80)
    for outcome in ["schema_invalid", "business_invalid", "transient", "timeout"]:
        policy = burn_down.retry_policy.get_policy(outcome)
        print(f"\n{outcome}:")
        print(f"  Retry: {policy['retry']}")
        print(f"  Max retries: {policy['max_retries']}")
        print(f"  Backoff: {policy['backoff']}")
        print(f"  Feedback: {policy['feedback']}")
    
    # Record some violations
    print("\n" + "=" * 80)
    print("VIOLATION ANALYSIS")
    print("=" * 80)
    
    burn_down.record_violation(
        error="Missing required field",
        field="verdict",
        value=None,
        expected_type="string",
        retry_count=1,
    )
    burn_down.record_violation(
        error="Invalid enum value",
        field="verdict",
        value="valid",
        expected_type="string (pass|fail|warning)",
        retry_count=2,
    )
    burn_down.record_violation(
        error="Out of range",
        field="confidence",
        value=1.5,
        expected_type="number (0.0-1.0)",
        retry_count=1,
    )
    
    analysis = burn_down.analyze_violations()
    print(f"\nTotal violations: {analysis['total']}")
    print(f"By field: {analysis['by_field']}")
    print(f"By error: {analysis['by_error']}")
    print(f"Top field: {analysis['top_field']}")
    print(f"Top error: {analysis['top_error']}")
    
    # Simulate burn-down progress
    print("\n" + "=" * 80)
    print("BURN-DOWN PROGRESS SIMULATION")
    print("=" * 80)
    
    # Baseline: 12 schema_invalid, 9 transport, 0.58 success_rate
    # Target: <9 schema_invalid, ≥0.90 success_rate
    
    progress_points = [
        (12, 9, 0.58),   # Baseline
        (10, 9, 0.65),   # Week 1
        (8, 8, 0.75),    # Week 2
        (6, 7, 0.85),    # Week 3
        (4, 6, 0.92),    # Week 4 - Target reached
    ]
    
    for schema_invalid, transport, success_rate in progress_points:
        entry = burn_down.record_progress(schema_invalid, transport, success_rate)
        print(f"\nSchema-invalid: {schema_invalid}, Transport: {transport}, Success: {success_rate:.2f}")
        print(f"  Progress: {entry['progress_pct']:.1f}%")
        print(f"  Success progress: {entry['success_progress_pct']:.1f}%")
        print(f"  On track: {entry['on_track']}")
    
    # Final status
    print("\n" + "=" * 80)
    print("FINAL STATUS")
    print("=" * 80)
    
    status = burn_down.get_status()
    print(f"\n{json.dumps(status, indent=2)}")