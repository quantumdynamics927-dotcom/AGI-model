"""TMT Vault Operation Configuration Schema.

Implements the validated task taxonomy with:
- Temperature defaults by task type
- Output mode specifications
- Validation profiles
- Fallback models and token limits
- Retry budgets and timeouts
- Schema enforcement with additionalProperties: false
- Post-generation validation dispatcher

Reference: https://docs.ollama.com/capabilities/structured-outputs
Reference: https://ollama.com/blog/structured-outputs
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional, Callable
import json
import jsonschema
from jsonschema import validate, ValidationError


class OutputMode(Enum):
    """Output mode for Vault operations."""
    STRICT_JSON = "strict_json"           # Schema-locked JSON verdict
    ANALYSIS_JSON = "analysis_json"       # Structured analysis JSON
    MIXED_REPORT = "mixed_report"         # Structured sections or markdown


class ValidationProfile(Enum):
    """Validation profile for Vault operations."""
    NUMERIC_VERDICT = "numeric_verdict"           # Checkpoint/CI verdicts
    TRAINING_DIAGNOSIS = "training_diagnosis"     # VAE loss interpretation
    ARTIFACT_INTERPRETATION = "artifact_interpretation"  # Phi/IIT analysis
    DATASET_GENERATION = "dataset_generation"     # Eval case generation
    CI_VERDICT = "ci_verdict"                     # CI audit oracle
    TECHNICAL_SUMMARY = "technical_summary"        # Research reports


class TaskGroup(Enum):
    """Task grouping for Vault operations."""
    JUDGMENT = "judgment"       # Checkpoint validation, CI audit
    DIAGNOSTIC = "diagnostic"   # Loss interpretation, phi analysis
    GENERATION = "generation"   # Eval case generation
    REPORTING = "reporting"     # Research reports


# JSON Schemas for each operation (with additionalProperties: false)
OPERATION_SCHEMAS: Dict[str, Dict[str, Any]] = {
    "vae_checkpoint_validation": {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "additionalProperties": False,
        "required": ["verdict", "confidence", "metrics_summary", "recommendation"],
        "properties": {
            "verdict": {"type": "string", "enum": ["pass", "warn", "fail"]},
            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
            "metrics_summary": {"type": "object"},
            "recommendation": {"type": "string"},
        }
    },
    
    "ci_audit_oracle": {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "additionalProperties": False,
        "required": ["verdict", "reason", "artifacts_checked"],
        "properties": {
            "verdict": {"type": "string", "enum": ["pass", "warn", "fail"]},
            "reason": {"type": "string"},
            "artifacts_checked": {"type": "array", "items": {"type": "string"}},
        }
    },
    
    "vae_loss_interpretation": {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "additionalProperties": False,
        "required": ["loss_breakdown", "interpretation", "recommendation"],
        "properties": {
            "loss_breakdown": {"type": "object"},
            "interpretation": {"type": "string"},
            "recommendation": {"type": "string"},
        }
    },
    
    "phi_artifact_analysis": {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "additionalProperties": False,
        "required": ["phi_metrics", "analysis", "next_experiment"],
        "properties": {
            "phi_metrics": {"type": "object"},
            "analysis": {"type": "string"},
            "next_experiment": {"type": "string"},
        }
    },
    
    "eval_case_generation": {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "additionalProperties": False,
        "required": ["cases"],
        "properties": {
            "cases": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["prompt", "expected_behavior", "category"],
                    "properties": {
                        "prompt": {"type": "string"},
                        "expected_behavior": {"type": "string"},
                        "category": {"type": "string"},
                    }
                }
            }
        }
    },
    
    "research_report_generation": {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "additionalProperties": True,  # Mixed report allows flexibility
        "required": ["title", "summary", "sections"],
        "properties": {
            "title": {"type": "string"},
            "summary": {"type": "string"},
            "sections": {"type": "array"},
            "metadata": {"type": "object"},
        }
    },
}


@dataclass(frozen=True)
class OperationConfig:
    """Configuration for a single Vault operation.
    
    Production-ready with:
    - Retry budget and timeout
    - Schema enforcement
    - Validator name
    - OpenAI compatibility flag
    """
    operation: str
    purpose: str
    task_group: TaskGroup
    output_mode: OutputMode
    validation_profile: ValidationProfile
    default_model: str
    fallback_model: str
    temperature: float
    max_tokens: int
    env_var: str
    schema_name: str
    validator_name: str
    retry_budget: int = 3
    timeout_s: int = 300
    requires_schema: bool = True
    supports_openai_compat: bool = True
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "operation": self.operation,
            "purpose": self.purpose,
            "task_group": self.task_group.value,
            "output_mode": self.output_mode.value,
            "validation_profile": self.validation_profile.value,
            "default_model": self.default_model,
            "fallback_model": self.fallback_model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "env_var": self.env_var,
            "schema_name": self.schema_name,
            "validator_name": self.validator_name,
            "retry_budget": self.retry_budget,
            "timeout_s": self.timeout_s,
            "requires_schema": self.requires_schema,
            "supports_openai_compat": self.supports_openai_compat,
            "description": self.description,
        }
    
    def get_schema(self) -> Optional[Dict[str, Any]]:
        """Get the JSON schema for this operation."""
        return OPERATION_SCHEMAS.get(self.schema_name)


# Validated operation configurations
VAULT_OPERATIONS: Dict[str, OperationConfig] = {
    # Judgment Tasks (temperature = 0)
    "vae_checkpoint_validation": OperationConfig(
        operation="vae_checkpoint_validation",
        purpose="Judge post-training checkpoint health from summary metrics",
        task_group=TaskGroup.JUDGMENT,
        output_mode=OutputMode.STRICT_JSON,
        validation_profile=ValidationProfile.NUMERIC_VERDICT,
        default_model="qwen3-coder-next:cloud",
        fallback_model="llama3.2:1b",
        temperature=0.0,
        max_tokens=512,
        env_var="AGI_OLLAMA_MODEL_VAE_CHECKPOINT_VALIDATION",
        schema_name="vae_checkpoint_validation",
        validator_name="validate_checkpoint_verdict",
        retry_budget=3,
        timeout_s=120,
        requires_schema=True,
        description="Schema-locked JSON verdict for checkpoint health. Low temperature for deterministic rule-based judgment.",
    ),
    
    "ci_audit_oracle": OperationConfig(
        operation="ci_audit_oracle",
        purpose="Render short structured audit verdicts from CI artifacts",
        task_group=TaskGroup.JUDGMENT,
        output_mode=OutputMode.STRICT_JSON,
        validation_profile=ValidationProfile.CI_VERDICT,
        default_model="qwen3-coder-next:cloud",
        fallback_model="llama3.2:1b",
        temperature=0.0,
        max_tokens=256,
        env_var="AGI_OLLAMA_MODEL_CI_AUDIT_ORACLE",
        schema_name="ci_audit_oracle",
        validator_name="validate_ci_verdict",
        retry_budget=3,
        timeout_s=60,
        requires_schema=True,
        description="Compact pass/warn/fail audit decisions. Lowest temperature for highest consistency.",
    ),
    
    # Diagnostic Tasks (temperature = 0.1)
    "vae_loss_interpretation": OperationConfig(
        operation="vae_loss_interpretation",
        purpose="Interpret VAE smoke-test loss components and recommend one training adjustment",
        task_group=TaskGroup.DIAGNOSTIC,
        output_mode=OutputMode.ANALYSIS_JSON,
        validation_profile=ValidationProfile.TRAINING_DIAGNOSIS,
        default_model="qwen3-coder-next:cloud",
        fallback_model="llama3.2:1b",
        temperature=0.1,
        max_tokens=768,
        env_var="AGI_OLLAMA_MODEL_VAE_LOSS_INTERPRETATION",
        schema_name="vae_loss_interpretation",
        validator_name="validate_loss_interpretation",
        retry_budget=3,
        timeout_s=180,
        requires_schema=True,
        description="Numerically careful analysis with one recommendation. Near-zero temperature for deterministic output.",
    ),
    
    "phi_artifact_analysis": OperationConfig(
        operation="phi_artifact_analysis",
        purpose="Interpret phi/IIT-oriented artifacts and propose the next experiment",
        task_group=TaskGroup.DIAGNOSTIC,
        output_mode=OutputMode.ANALYSIS_JSON,
        validation_profile=ValidationProfile.ARTIFACT_INTERPRETATION,
        default_model="qwen3-coder-next:cloud",
        fallback_model="llama3.2:1b",
        temperature=0.2,
        max_tokens=1024,
        env_var="AGI_OLLAMA_MODEL_PHI_ARTIFACT_ANALYSIS",
        schema_name="phi_artifact_analysis",
        validator_name="validate_phi_analysis",
        retry_budget=3,
        timeout_s=240,
        requires_schema=True,
        description="Analytical interpretation with moderate context use. Slightly higher temperature for nuanced analysis.",
    ),
    
    # Generation Tasks (temperature = 0)
    "eval_case_generation": OperationConfig(
        operation="eval_case_generation",
        purpose="Generate schema-valid regression and edge-case prompts for Vault eval datasets",
        task_group=TaskGroup.GENERATION,
        output_mode=OutputMode.STRICT_JSON,
        validation_profile=ValidationProfile.DATASET_GENERATION,
        default_model="qwen3-coder-next:cloud",
        fallback_model="llama3.2:1b",
        temperature=0.0,
        max_tokens=2048,
        env_var="AGI_OLLAMA_MODEL_EVAL_CASE_GENERATION",
        schema_name="eval_case_generation",
        validator_name="validate_eval_cases",
        retry_budget=3,
        timeout_s=300,
        requires_schema=True,
        description="Schema-locked JSON array generation. Zero temperature for deterministic schema compliance.",
    ),
    
    # Reporting Tasks (temperature = 0.3)
    "research_report_generation": OperationConfig(
        operation="research_report_generation",
        purpose="Turn validated AGI and IBM artifacts into concise technical research summaries",
        task_group=TaskGroup.REPORTING,
        output_mode=OutputMode.MIXED_REPORT,
        validation_profile=ValidationProfile.TECHNICAL_SUMMARY,
        default_model="qwen3-coder-next:cloud",
        fallback_model="llama3.2:1b",
        temperature=0.3,
        max_tokens=4096,
        env_var="AGI_OLLAMA_MODEL_RESEARCH_REPORT_GENERATION",
        schema_name="research_report_generation",
        validator_name="validate_research_report",
        retry_budget=2,
        timeout_s=600,
        requires_schema=False,
        description="Mixed structured sections or markdown. Higher temperature for narrative flexibility while staying grounded.",
    ),
}


def get_operation_config(operation: str) -> Optional[OperationConfig]:
    """Get configuration for a specific operation."""
    return VAULT_OPERATIONS.get(operation)


def get_operations_by_group(group: TaskGroup) -> Dict[str, OperationConfig]:
    """Get all operations in a task group."""
    return {
        op: config for op, config in VAULT_OPERATIONS.items()
        if config.task_group == group
    }


def get_operations_by_output_mode(mode: OutputMode) -> Dict[str, OperationConfig]:
    """Get all operations with a specific output mode."""
    return {
        op: config for op, config in VAULT_OPERATIONS.items()
        if config.output_mode == mode
    }


def get_schema_operations() -> Dict[str, OperationConfig]:
    """Get all operations that require schema enforcement."""
    return {
        op: config for op, config in VAULT_OPERATIONS.items()
        if config.requires_schema
    }


def describe_all_operations() -> Dict[str, Dict[str, Any]]:
    """Get all operation configurations as dictionaries."""
    return {op: config.to_dict() for op, config in VAULT_OPERATIONS.items()}


def get_temperature_defaults() -> Dict[str, float]:
    """Get temperature defaults by task group."""
    return {
        TaskGroup.JUDGMENT.value: 0.0,
        TaskGroup.DIAGNOSTIC.value: 0.15,  # Average of 0.1 and 0.2
        TaskGroup.GENERATION.value: 0.0,
        TaskGroup.REPORTING.value: 0.3,
    }


def get_token_limits() -> Dict[str, int]:
    """Get max_tokens limits by operation."""
    return {op: config.max_tokens for op, config in VAULT_OPERATIONS.items()}


def validate_operation_config(operation: str) -> bool:
    """Validate that an operation has a complete configuration."""
    config = get_operation_config(operation)
    if not config:
        return False
    
    # Check required fields
    required = [
        config.operation,
        config.default_model,
        config.fallback_model,
        config.env_var,
    ]
    
    return all(required)


def validate_operation_output(operation: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate operation output against its JSON schema.
    
    Production-ready validation dispatcher that:
    - Checks schema compliance
    - Validates business logic
    - Returns structured result
    
    Args:
        operation: Operation name (e.g., "vae_checkpoint_validation")
        payload: Parsed JSON output from the operation
        
    Returns:
        Dict with keys: valid, errors, warnings
    """
    config = get_operation_config(operation)
    if not config:
        return {
            "valid": False,
            "errors": [f"Unknown operation: {operation}"],
            "warnings": []
        }
    
    result = {"valid": True, "errors": [], "warnings": []}
    
    # Schema validation
    if config.requires_schema:
        schema = config.get_schema()
        if schema:
            try:
                validate(instance=payload, schema=schema)
            except ValidationError as e:
                result["valid"] = False
                result["errors"].append(f"Schema validation failed: {e.message}")
                result["errors"].append(f"Path: {list(e.absolute_path)}")
        else:
            result["warnings"].append(f"No schema defined for {operation}")
    
    # Business logic validation by operation type
    if operation == "vae_checkpoint_validation":
        if "verdict" not in payload:
            result["errors"].append("Missing required field: verdict")
            result["valid"] = False
        elif payload["verdict"] not in ["pass", "warn", "fail"]:
            result["errors"].append(f"Invalid verdict value: {payload['verdict']}")
            result["valid"] = False
        
        if "confidence" in payload:
            if not 0 <= payload["confidence"] <= 1:
                result["errors"].append(f"Confidence out of range: {payload['confidence']}")
                result["valid"] = False
    
    elif operation == "ci_audit_oracle":
        if "verdict" not in payload:
            result["errors"].append("Missing required field: verdict")
            result["valid"] = False
        elif payload["verdict"] not in ["pass", "warn", "fail"]:
            result["errors"].append(f"Invalid verdict value: {payload['verdict']}")
            result["valid"] = False
    
    elif operation == "vae_loss_interpretation":
        if "recommendation" not in payload:
            result["warnings"].append("Missing recommendation field")
    
    elif operation == "phi_artifact_analysis":
        if "next_experiment" not in payload:
            result["warnings"].append("Missing next_experiment field")
    
    elif operation == "eval_case_generation":
        if "cases" in payload:
            if not isinstance(payload["cases"], list):
                result["errors"].append("cases must be an array")
                result["valid"] = False
            elif len(payload["cases"]) == 0:
                result["warnings"].append("Empty cases array")
    
    elif operation == "research_report_generation":
        # Mixed report - more lenient validation
        if "title" not in payload:
            result["warnings"].append("Missing title field")
    
    return result


def validate_with_retry(
    operation: str,
    payload: Dict[str, Any],
    retry_budget: Optional[int] = None
) -> Dict[str, Any]:
    """
    Validate with retry budget tracking.
    
    Args:
        operation: Operation name
        payload: Parsed JSON output
        retry_budget: Override config retry budget
        
    Returns:
        Validation result with retry info
    """
    config = get_operation_config(operation)
    budget = retry_budget if retry_budget is not None else (config.retry_budget if config else 3)
    
    validation_result = validate_operation_output(operation, payload)
    validation_result["retry_budget"] = budget
    validation_result["retries_remaining"] = budget if validation_result["valid"] else budget - 1
    
    return validation_result


# Export for CLI usage
__all__ = [
    "OutputMode",
    "ValidationProfile", 
    "TaskGroup",
    "OperationConfig",
    "OPERATION_SCHEMAS",
    "VAULT_OPERATIONS",
    "get_operation_config",
    "get_operations_by_group",
    "get_operations_by_output_mode",
    "get_schema_operations",
    "describe_all_operations",
    "get_temperature_defaults",
    "get_token_limits",
    "validate_operation_config",
    "validate_operation_output",
    "validate_with_retry",
]


if __name__ == "__main__":
    import json
    
    print("=" * 80)
    print("TMT VAULT OPERATION CONFIGURATION (Production-Ready)")
    print("=" * 80)
    
    # Print by task group
    for group in TaskGroup:
        ops = get_operations_by_group(group)
        print(f"\n{group.value.upper()} TASKS ({len(ops)} operations)")
        print("-" * 40)
        for op, config in ops.items():
            print(f"  {op}:")
            print(f"    Temperature: {config.temperature}")
            print(f"    Max Tokens: {config.max_tokens}")
            print(f"    Retry Budget: {config.retry_budget}")
            print(f"    Timeout: {config.timeout_s}s")
            print(f"    Output Mode: {config.output_mode.value}")
            print(f"    Model: {config.default_model}")
            print(f"    Schema: {config.schema_name}")
            print(f"    Validator: {config.validator_name}")
    
    # Print temperature defaults
    print("\n" + "=" * 80)
    print("TEMPERATURE DEFAULTS BY TASK GROUP")
    print("=" * 80)
    for group, temp in get_temperature_defaults().items():
        print(f"  {group}: {temp}")
    
    # Print schema requirements
    print("\n" + "=" * 80)
    print("SCHEMA-REQUIRED OPERATIONS")
    print("=" * 80)
    schema_ops = get_schema_operations()
    print(f"  {len(schema_ops)}/{len(VAULT_OPERATIONS)} operations require schema enforcement")
    for op in schema_ops:
        config = get_operation_config(op)
        print(f"  - {op} (schema: {config.schema_name})")
    
    # Print retry budgets
    print("\n" + "=" * 80)
    print("RETRY BUDGETS AND TIMEOUTS")
    print("=" * 80)
    for op, config in VAULT_OPERATIONS.items():
        print(f"  {op}: retry={config.retry_budget}, timeout={config.timeout_s}s")
    
    # Demo validation
    print("\n" + "=" * 80)
    print("VALIDATION DEMO")
    print("=" * 80)
    
    # Test valid payload
    test_valid = {
        "verdict": "pass",
        "confidence": 0.95,
        "metrics_summary": {"loss": 0.1},
        "recommendation": "Checkpoint is healthy"
    }
    result = validate_operation_output("vae_checkpoint_validation", test_valid)
    print(f"\nValid payload test:")
    print(f"  Result: {result}")
    
    # Test invalid payload
    test_invalid = {
        "verdict": "invalid",
        "confidence": 1.5
    }
    result = validate_operation_output("vae_checkpoint_validation", test_invalid)
    print(f"\nInvalid payload test:")
    print(f"  Result: {result}")
    
    # Export full config as JSON
    print("\n" + "=" * 80)
    print("FULL CONFIGURATION (JSON)")
    print("=" * 80)
    print(json.dumps(describe_all_operations(), indent=2))