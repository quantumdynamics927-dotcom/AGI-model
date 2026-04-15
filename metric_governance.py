"""
Metric Governance Rules
=======================

Hard rules that enforce scientific rigor:
1. FAIL/MISSING metrics are automatically downgraded to exploratory_annotation
2. Reports cannot display metrics not in registry
3. Only PASS metrics can contribute to supported claims
4. Batch validation over all artifacts

Date: April 15, 2026
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class MetricStatus(Enum):
    """Validation status for metrics"""
    VALIDATED = "VALIDATED"      # Passed all tests, hardware-backed
    PASSED = "PASSED"            # Passed numerical validity
    WARN = "WARN"                # Valid but not significant vs null
    FAIL = "FAIL"                # Range violation
    CLASS_ERROR = "CLASS_ERROR" # Wrong metric type
    MISSING = "MISSING"          # Not in registry
    PROVISIONAL = "PROVISIONAL" # Defined but needs validation
    EXPLORATORY = "EXPLORATORY"  # Downgraded, not for claims


class ClaimStatus(Enum):
    """Status of scientific claims"""
    SUPPORTED = "SUPPORTED"      # Strong evidence, validated metrics
    WEAKENED = "WEAKENED"        # Some evidence, but issues found
    PROVISIONAL = "PROVISIONAL" # Needs more validation
    FAILED = "FAILED"           # Evidence contradicts claim
    PENDING = "PENDING"          # Not yet evaluated


@dataclass
class MetricGovernance:
    """Governance rules for metric usage"""
    
    # Rule 1: Status thresholds for different uses
    CLAIM_THRESHOLD = MetricStatus.PASSED      # Minimum status to support claims
    REPORT_THRESHOLD = MetricStatus.WARN       # Minimum status to appear in reports
    EVIDENCE_THRESHOLD = MetricStatus.VALIDATED # Minimum status for primary evidence
    
    # Rule 2: Automatic downgrade rules
    DOWNGRADE_TO_EXPLORATORY = [MetricStatus.FAIL, MetricStatus.MISSING, MetricStatus.CLASS_ERROR]
    
    # Rule 3: Provisional handling
    PROVISIONAL_STATUS = [MetricStatus.PROVISIONAL, MetricStatus.WARN]
    
    @staticmethod
    def can_support_claim(metric_status: MetricStatus) -> bool:
        """Check if metric can contribute to a supported claim."""
        return metric_status in [
            MetricStatus.VALIDATED,
            MetricStatus.PASSED
        ]
    
    @staticmethod
    def can_appear_in_report(metric_status: MetricStatus) -> bool:
        """Check if metric can appear in reports (with annotation if needed)."""
        return metric_status not in [
            MetricStatus.FAIL,
            MetricStatus.MISSING,
            MetricStatus.CLASS_ERROR
        ]
    
    @staticmethod
    def get_annotation(metric_status: MetricStatus) -> str:
        """Get required annotation for metric based on status."""
        annotations = {
            MetricStatus.VALIDATED: "",
            MetricStatus.PASSED: "",
            MetricStatus.WARN: "⚠️ Not significant vs null model",
            MetricStatus.FAIL: "❌ RANGE VIOLATION - Downgraded to exploratory",
            MetricStatus.CLASS_ERROR: "🔤 TYPE ERROR - Downgraded to exploratory",
            MetricStatus.MISSING: "📋 NOT IN REGISTRY - Downgraded to exploratory",
            MetricStatus.PROVISIONAL: "📋 Provisional - Needs validation",
            MetricStatus.EXPLORATORY: "🔍 Exploratory - Not for claims"
        }
        return annotations.get(metric_status, "Unknown status")
    
    @staticmethod
    def downgrade_to_exploratory(metric_status: MetricStatus) -> MetricStatus:
        """Apply hard rule: FAIL/MISSING metrics become exploratory."""
        if metric_status in MetricGovernance.DOWNGRADE_TO_EXPLORATORY:
            return MetricStatus.EXPLORATORY
        return metric_status


class MetricRegistryEnforcer:
    """Enforces registry rules across the project."""
    
    def __init__(self, registry_path: str = None):
        self.registry_path = registry_path or "metrics_registry.json"
        self.registry = self._load_registry()
        self.governance = MetricGovernance()
    
    def _load_registry(self) -> dict:
        """Load metric registry."""
        try:
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"metrics": {}}
    
    def metric_exists(self, metric_name: str) -> bool:
        """Check if metric is in registry."""
        return metric_name in self.registry.get("metrics", {})
    
    def get_metric_class(self, metric_name: str) -> Optional[str]:
        """Get the class of a metric from registry."""
        if metric_name in self.registry.get("metrics", {}):
            return self.registry["metrics"][metric_name].get("classification")
        return None
    
    def get_metric_range(self, metric_name: str) -> Optional[Tuple[float, float]]:
        """Get the valid range for a metric."""
        if metric_name in self.registry.get("metrics", {}):
            output_range = self.registry["metrics"][metric_name].get("output_range", {})
            min_val = output_range.get("min")
            max_val = output_range.get("max")
            return (min_val, max_val)
        return None
    
    def validate_metric_for_report(self, 
                                   metric_name: str, 
                                   value: float,
                                   status: MetricStatus) -> Tuple[bool, str, str]:
        """
        Validate metric for inclusion in report.
        
        Returns:
            (can_include, display_value, annotation)
        """
        # Rule 1: Must be in registry
        if not self.metric_exists(metric_name):
            return False, str(value), "📋 NOT IN REGISTRY"
        
        # Rule 2: Check status
        if not self.governance.can_appear_in_report(status):
            # Downgrade to exploratory
            return False, str(value), self.governance.get_annotation(status)
        
        # Rule 3: Check range
        valid_range = self.get_metric_range(metric_name)
        if valid_range:
            min_val, max_val = valid_range
            if min_val is not None and value < min_val:
                return False, str(value), f"❌ Below minimum {min_val}"
            if max_val is not None and value > max_val:
                return False, str(value), f"❌ Above maximum {max_val}"
        
        # Include with appropriate annotation
        annotation = self.governance.get_annotation(status)
        return True, f"{value:.4f}", annotation
    
    def validate_metric_for_claim(self,
                                  metric_name: str,
                                  status: MetricStatus) -> Tuple[bool, str]:
        """
        Validate metric for supporting a claim.
        
        Returns:
            (can_support, reason)
        """
        # Rule 1: Must be in registry
        if not self.metric_exists(metric_name):
            return False, f"Metric '{metric_name}' not in registry"
        
        # Rule 2: Must have sufficient status
        if not self.governance.can_support_claim(status):
            return False, f"Metric status '{status.value}' insufficient for claims (need PASSED or VALIDATED)"
        
        # Rule 3: Must have equation defined
        metric_def = self.registry["metrics"][metric_name]
        if "equation" not in metric_def:
            return False, f"Metric '{metric_name}' has no equation defined"
        
        return True, "Metric can support claims"


class ClaimUpdater:
    """Updates claim status based on metric validation."""
    
    def __init__(self, claims_path: str = None):
        self.claims_path = claims_path or "CLAIMS_MATRIX.md"
        self.governance = MetricGovernance()
    
    def update_claim_status(self,
                           claim_id: str,
                           metric_results: Dict[str, MetricStatus]) -> ClaimStatus:
        """
        Update claim status based on supporting metrics.
        
        Rules:
        - All metrics VALIDATED/PASSED → SUPPORTED
        - Any metric WARN → PROVISIONAL
        - Any metric FAIL/MISSING → WEAKENED
        - All metrics FAIL → FAILED
        """
        if not metric_results:
            return ClaimStatus.PENDING
        
        statuses = list(metric_results.values())
        
        # Check for failures
        if all(s in [MetricStatus.FAIL, MetricStatus.MISSING, MetricStatus.CLASS_ERROR] 
               for s in statuses):
            return ClaimStatus.FAILED
        
        # Check for any failures
        if any(s in [MetricStatus.FAIL, MetricStatus.MISSING, MetricStatus.CLASS_ERROR] 
               for s in statuses):
            return ClaimStatus.WEAKENED
        
        # Check for warnings
        if any(s == MetricStatus.WARN for s in statuses):
            return ClaimStatus.PROVISIONAL
        
        # All passed or validated
        if all(s in [MetricStatus.VALIDATED, MetricStatus.PASSED] for s in statuses):
            return ClaimStatus.SUPPORTED
        
        return ClaimStatus.PROVISIONAL
    
    def generate_claim_report(self,
                             claim_id: str,
                             claim_statement: str,
                             metric_results: Dict[str, Tuple[float, MetricStatus]]) -> str:
        """Generate a formatted claim report."""
        status = self.update_claim_status(claim_id, {k: v[1] for k, v in metric_results.items()})
        
        report = []
        report.append(f"### Claim {claim_id}")
        report.append(f"**Statement**: {claim_statement}")
        report.append(f"**Status**: {status.value}")
        report.append("")
        report.append("| Metric | Value | Status | Can Support |")
        report.append("|--------|-------|--------|--------------|")
        
        for metric_name, (value, metric_status) in metric_results.items():
            can_support = self.governance.can_support_claim(metric_status)
            support_icon = "✅" if can_support else "❌"
            report.append(f"| {metric_name} | {value:.4f} | {metric_status.value} | {support_icon} |")
        
        return "\n".join(report)


class BatchValidator:
    """Validates all artifacts in the project."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.enforcer = MetricRegistryEnforcer()
        self.governance = MetricGovernance()
        self.results: Dict[str, Dict] = {}
    
    def find_artifacts(self) -> List[Path]:
        """Find all artifact files that might contain metrics."""
        patterns = [
            "**/*analysis*.json",
            "**/*results*.json",
            "**/*report*.json",
            "**/*metrics*.json",
            "**/*evidence*.json",
        ]
        
        artifacts = []
        for pattern in patterns:
            artifacts.extend(self.project_root.glob(pattern))
        
        return list(set(artifacts))
    
    def extract_metrics_from_json(self, filepath: Path) -> Dict[str, float]:
        """Extract metric values from a JSON file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return {}
        
        metrics = {}
        
        # Known metric keys to look for
        metric_keys = [
            "phi_resonance", "phi_coherence", "biomimetic_resonance",
            "entanglement_entropy", "quantum_coherence", "platonic_alignment_score",
            "tesseract_symmetry", "phi_ratio", "neural_efficiency",
            "structural_redundancy", "consciousness_level", "phi_invariant_score"
        ]
        
        def extract_from_dict(d: dict, prefix: str = ""):
            for key, value in d.items():
                full_key = f"{prefix}.{key}" if prefix else key
                
                if isinstance(value, dict):
                    extract_from_dict(value, full_key)
                elif isinstance(value, (int, float)):
                    # Check if key matches any metric pattern
                    for metric_key in metric_keys:
                        if metric_key.lower() in key.lower():
                            metrics[full_key] = float(value)
                            break
        
        extract_from_dict(data)
        return metrics
    
    def validate_artifact(self, filepath: Path) -> Dict:
        """Validate all metrics in an artifact."""
        metrics = self.extract_metrics_from_json(filepath)
        
        validation_results = {}
        for metric_name, value in metrics.items():
            # Check if in registry
            if not self.enforcer.metric_exists(metric_name):
                status = MetricStatus.MISSING
            else:
                # Check range
                valid_range = self.enforcer.get_metric_range(metric_name)
                if valid_range:
                    min_val, max_val = valid_range
                    if min_val is not None and value < min_val:
                        status = MetricStatus.FAIL
                    elif max_val is not None and value > max_val:
                        status = MetricStatus.FAIL
                    else:
                        status = MetricStatus.PASSED
                else:
                    status = MetricStatus.PROVISIONAL
            
            # Apply governance rules
            final_status = self.governance.downgrade_to_exploratory(status)
            can_support = self.governance.can_support_claim(final_status)
            
            validation_results[metric_name] = {
                "value": value,
                "status": status.value,
                "final_status": final_status.value,
                "can_support_claim": can_support,
                "annotation": self.governance.get_annotation(final_status)
            }
        
        return {
            "filepath": str(filepath),
            "metrics_found": len(metrics),
            "validation_results": validation_results,
            "summary": {
                "passed": sum(1 for r in validation_results.values() 
                             if r["final_status"] in ["VALIDATED", "PASSED"]),
                "warnings": sum(1 for r in validation_results.values() 
                               if r["final_status"] == "WARN"),
                "failed": sum(1 for r in validation_results.values() 
                             if r["final_status"] == "FAIL"),
                "missing": sum(1 for r in validation_results.values() 
                               if r["final_status"] == "MISSING"),
                "exploratory": sum(1 for r in validation_results.values() 
                                   if r["final_status"] == "EXPLORATORY")
            }
        }
    
    def validate_all_artifacts(self) -> Dict:
        """Validate all artifacts in the project."""
        artifacts = self.find_artifacts()
        
        all_results = {
            "total_artifacts": len(artifacts),
            "artifacts": {}
        }
        
        for artifact in artifacts:
            try:
                result = self.validate_artifact(artifact)
                all_results["artifacts"][str(artifact)] = result
            except Exception as e:
                all_results["artifacts"][str(artifact)] = {
                    "error": str(e)
                }
        
        # Compute overall summary
        all_results["overall_summary"] = {
            "total_metrics": sum(
                r.get("metrics_found", 0) 
                for r in all_results["artifacts"].values() 
                if isinstance(r, dict) and "metrics_found" in r
            ),
            "total_passed": sum(
                r.get("summary", {}).get("passed", 0)
                for r in all_results["artifacts"].values()
                if isinstance(r, dict) and "summary" in r
            ),
            "total_failed": sum(
                r.get("summary", {}).get("failed", 0)
                for r in all_results["artifacts"].values()
                if isinstance(r, dict) and "summary" in r
            ),
            "total_missing": sum(
                r.get("summary", {}).get("missing", 0)
                for r in all_results["artifacts"].values()
                if isinstance(r, dict) and "summary" in r
            )
        }
        
        self.results = all_results
        return all_results
    
    def generate_report(self) -> str:
        """Generate a comprehensive validation report."""
        report = []
        report.append("="*70)
        report.append("BATCH VALIDATION REPORT")
        report.append("="*70)
        
        summary = self.results.get("overall_summary", {})
        report.append(f"\nOVERALL SUMMARY:")
        report.append(f"  Total artifacts: {self.results.get('total_artifacts', 0)}")
        report.append(f"  Total metrics: {summary.get('total_metrics', 0)}")
        report.append(f"  ✅ Passed: {summary.get('total_passed', 0)}")
        report.append(f"  ❌ Failed: {summary.get('total_failed', 0)}")
        report.append(f"  📋 Missing: {summary.get('total_missing', 0)}")
        
        report.append(f"\nARTIFACT DETAILS:")
        for filepath, result in self.results.get("artifacts", {}).items():
            if "error" in result:
                report.append(f"\n  ❌ {filepath}")
                report.append(f"     Error: {result['error']}")
                continue
            
            report.append(f"\n  📄 {filepath}")
            report.append(f"     Metrics found: {result.get('metrics_found', 0)}")
            
            for metric_name, metric_result in result.get("validation_results", {}).items():
                status_icon = "✅" if metric_result["final_status"] in ["VALIDATED", "PASSED"] else \
                             "⚠️" if metric_result["final_status"] == "WARN" else \
                             "❌" if metric_result["final_status"] in ["FAIL", "MISSING"] else "📋"
                report.append(f"     {status_icon} {metric_name}: {metric_result['value']:.4f} [{metric_result['final_status']}]")
                if metric_result["annotation"]:
                    report.append(f"        {metric_result['annotation']}")
        
        report.append("\n" + "="*70)
        report.append("GOVERNANCE RULES APPLIED:")
        report.append("  1. FAIL/MISSING metrics → downgraded to EXPLORATORY")
        report.append("  2. Only PASSED/VALIDATED metrics can support claims")
        report.append("  3. All metrics must be in registry to appear in reports")
        report.append("="*70)
        
        return "\n".join(report)
    
    def save_results(self, output_path: str):
        """Save validation results to JSON."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, default=str)
        print(f"✅ Results saved to: {output_path}")


if __name__ == "__main__":
    import sys
    
    print("="*70)
    print("METRIC GOVERNANCE ENFORCER")
    print("="*70)
    
    # Initialize enforcer
    enforcer = MetricRegistryEnforcer()
    
    # Test governance rules
    print("\nGOVERNANCE RULES:")
    print(f"  CLAIM_THRESHOLD: {MetricGovernance.CLAIM_THRESHOLD.value}")
    print(f"  REPORT_THRESHOLD: {MetricGovernance.REPORT_THRESHOLD.value}")
    print(f"  EVIDENCE_THRESHOLD: {MetricGovernance.EVIDENCE_THRESHOLD.value}")
    
    # Test status checks
    print("\nSTATUS CHECKS:")
    test_cases = [
        ("phi_coherence", 0.6952, MetricStatus.WARN),
        ("biomimetic_resonance", 1.1249, MetricStatus.FAIL),
        ("entanglement_entropy", 1.2422, MetricStatus.PASSED),
        ("unknown_metric", 0.5, MetricStatus.MISSING),
    ]
    
    for metric_name, value, status in test_cases:
        can_support = MetricGovernance.can_support_claim(status)
        can_report = MetricGovernance.can_appear_in_report(status)
        annotation = MetricGovernance.get_annotation(status)
        final_status = MetricGovernance.downgrade_to_exploratory(status)
        
        print(f"\n  {metric_name} = {value}:")
        print(f"    Status: {status.value}")
        print(f"    Can support claim: {can_support}")
        print(f"    Can appear in report: {can_report}")
        print(f"    Final status: {final_status.value}")
        if annotation:
            print(f"    Annotation: {annotation}")
    
    # Run batch validation
    print("\n" + "="*70)
    print("BATCH VALIDATION")
    print("="*70)
    
    validator = BatchValidator(project_root=".")
    validator.validate_all_artifacts()
    print(validator.generate_report())
    
    # Save results
    validator.save_results("batch_validation_results.json")