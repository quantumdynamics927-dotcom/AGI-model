"""
Integrated Migration System
===========================

Uses canonical_aliases.py and field_taxonomy.py to properly classify fields
before processing them as metrics. This separates true metrics from parameters,
metadata, and provenance fields.

Date: April 15, 2026
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime

# Import canonical definitions
from canonical_aliases import (
    CANONICAL_METRICS,
    AliasResolver,
    validate_metric_value,
    MetricClass,
    GovernanceStatus
)

# Import field taxonomy
from field_taxonomy import (
    FieldClass,
    FieldDefinition,
    FIELD_TAXONOMY,
    classify_field,
    get_field_class_summary
)


@dataclass
class MigrationRecord:
    """Record of a single metric migration"""
    original_name: str
    canonical_name: str
    value: float
    metric_class: str
    governance_status: str
    valid: bool
    issues: List[str]
    notes: str


class IntegratedMigrator:
    """Production migrator using canonical alias definitions and field taxonomy."""
    
    def __init__(self):
        self.resolver = AliasResolver()
        self.stats = {
            "total_artifacts": 0,
            "total_fields": 0,
            "metrics": 0,
            "parameters": 0,
            "metadata": 0,
            "provenance": 0,
            "descriptors": 0,
            "unknown_fields": 0,
            "resolved_to_canonical": 0,
            "valid_values": 0,
            "invalid_values": 0
        }
        self.migration_log: List[Dict] = []
        self.field_classification: Dict[str, FieldClass] = {}  # Track field classifications
    
    def classify_and_filter(self, 
                           field_name: str,
                           value: float) -> Tuple[FieldDefinition, bool]:
        """
        Classify a field and determine if it should be processed as a metric.
        
        Returns:
            (FieldDefinition, should_process_as_metric)
        """
        field_def = classify_field(field_name)
        self.field_classification[field_name] = field_def.field_class
        
        # Update class counts
        if field_def.field_class == FieldClass.METRIC:
            return field_def, True
        elif field_def.field_class == FieldClass.PARAMETER:
            self.stats["parameters"] += 1
            return field_def, False
        elif field_def.field_class == FieldClass.METADATA:
            self.stats["metadata"] += 1
            return field_def, False
        elif field_def.field_class == FieldClass.PROVENANCE:
            self.stats["provenance"] += 1
            return field_def, False
        elif field_def.field_class == FieldClass.DESCRIPTOR:
            self.stats["descriptors"] += 1
            return field_def, False
        else:
            self.stats["unknown_fields"] += 1
            return field_def, False
    
    def validate_value(self, 
                       canonical_name: str,
                       value: float,
                       metric: 'CanonicalMetric' = None) -> Tuple[bool, List[str]]:
        """
        Validate a metric value against its canonical definition.
        
        Returns:
            (is_valid, list_of_issues)
        """
        issues = []
        
        if metric is None:
            return False, ["Unknown canonical metric"]
        
        # Check range constraints
        min_val, max_val = metric.valid_range
        
        if min_val is not None and value < min_val:
            issues.append(f"Value {value} < minimum {min_val}")
        
        if max_val is not None and value > max_val:
            # Special case: if value ≈ φ and metric is phi-related, it might be a target constant
            if abs(value - 1.618033988749895) < 0.01 and "phi" in canonical_name:
                issues.append(f"Value {value:.4f} ≈ φ - likely a target constant, not a measurement")
            else:
                issues.append(f"Value {value} > maximum {max_val}")
        
        # Check for negative entropy
        if "entropy" in canonical_name.lower() and value < 0:
            issues.append(f"Negative entropy ({value}) - indicates buggy partial trace")
        
        return len(issues) == 0, issues
    
    def migrate_metric(self, 
                       original_name: str,
                       value: float,
                       context: str = "") -> MigrationRecord:
        """
        Migrate a single metric using canonical alias resolution.
        
        Args:
            original_name: Original metric name from artifact
            value: Metric value
            context: File path or context for logging
            
        Returns:
            MigrationRecord with canonical name and validation status
        """
        # First, classify the field
        field_def, should_process = self.classify_and_filter(original_name, value)
        
        # If not a metric, return early with classification info
        if not should_process:
            return MigrationRecord(
                original_name=original_name,
                canonical_name=field_def.canonical_name or "N/A",
                value=value,
                metric_class=field_def.field_class.value,
                governance_status="non_metric",
                valid=True,  # Non-metrics are always "valid" for their class
                issues=[],
                notes=field_def.notes
            )
        
        # Resolve alias for metrics
        canonical_name, metric = self.resolver.resolve(original_name)
        
        # Track unknown metrics
        if canonical_name is None:
            self.stats["unknown_fields"] += 1
            
            return MigrationRecord(
                original_name=original_name,
                canonical_name="UNKNOWN",
                value=value,
                metric_class="unknown",
                governance_status="unknown",
                valid=False,
                issues=["Metric not in canonical registry"],
                notes="Requires registration in canonical_aliases.py"
            )
        
        self.stats["resolved_to_canonical"] += 1
        
        # Validate value
        is_valid, issues = self.validate_value(canonical_name, value, metric)
        
        if not is_valid:
            self.stats["invalid_values"] += 1
        else:
            self.stats["valid_values"] += 1
        
        return MigrationRecord(
            original_name=original_name,
            canonical_name=canonical_name,
            value=value,
            metric_class=metric.metric_class.value if metric else "unknown",
            governance_status=metric.governance_status.value if metric else "unknown",
            valid=is_valid,
            issues=issues,
            notes=metric.notes if metric else ""
        )
    
    def find_all_metrics(self, 
                        data: Any, 
                        prefix: str = "") -> Dict[str, float]:
        """
        Recursively find all numeric metric fields in a data structure.
        
        Returns:
            Dict mapping field paths to values
        """
        metrics = {}
        
        # Fields to skip (metadata, timestamps, file info, type analysis)
        SKIP_FIELDS = {
            'mtime', 'ctime', 'atime', 'size', 'inode', 'mode', 'uid', 'gid',
            'timestamp', 'date', 'version', 'metadata', 'id', 'uuid', 'hash',
            'created_at', 'updated_at', 'deleted_at', 'expires_at',
            'index', 'count', 'total', 'num', 'n_', 'len', 'length',
            'lineno', 'col_offset', 'end_lineno', 'end_col_offset',
            'node', 'type_of_any', 'variance', 'abstract_status',
            'data_mtime', 'file_size', 'file_path', 'filename'
        }
        
        # Patterns to skip (prefixes)
        SKIP_PREFIXES = {
            'names.', 'node.', 'type.', 'file_', 'path_', 'config.',
            'metadata.', 'cache.', 'temp_', 'tmp_'
        }
        
        if isinstance(data, dict):
            for key, value in data.items():
                path = f"{prefix}.{key}" if prefix else key
                
                # Skip metadata fields
                if key.startswith("_") or key in SKIP_FIELDS:
                    continue
                
                # Skip known non-metric prefixes
                if any(path.startswith(p) for p in SKIP_PREFIXES):
                    continue
                
                # Skip fields that are purely metadata
                key_lower = key.lower()
                if any(skip in key_lower for skip in ['_mtime', '_time', '_date', '_path', '_file', '_id', '_hash']):
                    continue
                
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    # Additional check: skip if it looks like a timestamp or count
                    if key_lower.endswith(('_count', '_index', '_num', '_total')):
                        continue
                    metrics[path] = float(value)
                elif isinstance(value, dict):
                    metrics.update(self.find_all_metrics(value, path))
                elif isinstance(value, list):
                    for i, item in enumerate(value):
                        if isinstance(item, dict):
                            metrics.update(self.find_all_metrics(item, f"{path}[{i}]"))
        
        return metrics
    
    def migrate_artifact(self, 
                        filepath: Path,
                        dry_run: bool = True) -> Dict:
        """
        Migrate all metrics in an artifact file.
        
        Args:
            filepath: Path to artifact JSON file
            dry_run: If True, don't write changes
            
        Returns:
            Migration report
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError, FileNotFoundError, PermissionError) as e:
            return {
                "filepath": str(filepath),
                "error": str(e),
                "status": "error"
            }
        
        self.stats["total_artifacts"] += 1
        
        # Find all metric fields
        metric_fields = self.find_all_metrics(data)
        self.stats["total_fields"] += len(metric_fields)
        
        # Migrate each field
        migrations = []
        summary = {
            "validated": 0,
            "passed": 0,
            "provisional": 0,
            "exploratory": 0,
            "invalid": 0,
            "unknown": 0,
            "non_metric": 0
        }
        
        for field_path, value in metric_fields.items():
            record = self.migrate_metric(field_path, value, str(filepath))
            migrations.append(asdict(record))
            
            # Update summary
            status = record.governance_status
            if status in summary:
                summary[status] += 1
            elif status == "non_metric":
                summary["non_metric"] += 1
            elif not record.valid:
                summary["invalid"] += 1
        
        # Write migrated data if not dry run
        if not dry_run:
            data["_migration_metadata"] = {
                "registry_version": "1.0.0",
                "migration_timestamp": datetime.now().isoformat(),
                "total_metrics": len(metric_fields),
                "migration_summary": summary,
                "canonical_metrics_used": len(CANONICAL_METRICS)
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
        
        return {
            "filepath": str(filepath),
            "total_fields": len(metric_fields),
            "migrations": migrations,
            "summary": summary
        }
    
    def migrate_directory(self, 
                         directory: Path,
                         pattern: str = "*.json",
                         dry_run: bool = True) -> Dict:
        """
        Migrate all artifacts in a directory.
        
        Args:
            directory: Directory to search
            pattern: File pattern to match
            dry_run: If True, don't write changes
            
        Returns:
            Complete migration report
        """
        results = []
        
        for filepath in Path(directory).rglob(pattern):
            # Skip non-artifact files
            if any(skip in str(filepath).lower() for skip in ["node_modules", ".git", "migration", "registry"]):
                continue
            
            result = self.migrate_artifact(filepath, dry_run)
            results.append(result)
        
        # Compile field classification summary
        field_class_counts = {}
        for field_name, field_class in self.field_classification.items():
            field_class_counts[field_class.value] = field_class_counts.get(field_class.value, 0) + 1
        
        return {
            "directory": str(directory),
            "total_artifacts": self.stats["total_artifacts"],
            "total_fields": self.stats["total_fields"],
            "field_classification": field_class_counts,
            "metrics_processed": self.stats["metrics"],
            "parameters": self.stats["parameters"],
            "metadata": self.stats["metadata"],
            "provenance": self.stats["provenance"],
            "descriptors": self.stats["descriptors"],
            "resolved_to_canonical": self.stats["resolved_to_canonical"],
            "unknown_fields": self.stats["unknown_fields"],
            "valid_values": self.stats["valid_values"],
            "invalid_values": self.stats["invalid_values"],
            "results": results
        }


def main():
    """Run integrated migration on all artifacts."""
    print("=" * 70)
    print("INTEGRATED MIGRATION - FIELD TAXONOMY + CANONICAL ALIAS RESOLUTION")
    print("=" * 70)
    print()
    
    migrator = IntegratedMigrator()
    
    # Find all JSON artifacts
    workspace = Path("d:/AGI-GH-REPO-11326/AGI-model")
    
    # Run migration (dry run first)
    print("Running DRY RUN migration...")
    print()
    
    report = migrator.migrate_directory(workspace, dry_run=True)
    
    print("=" * 70)
    print("MIGRATION SUMMARY")
    print("=" * 70)
    print(f"Total artifacts scanned: {report['total_artifacts']}")
    print(f"Total fields found: {report['total_fields']}")
    print()
    
    # Show field classification
    print("=" * 70)
    print("FIELD CLASSIFICATION")
    print("=" * 70)
    fc = report.get('field_classification', {})
    print(f"  📊 metrics: {fc.get('metric', 0)}")
    print(f"  ⚙️  parameters: {report.get('parameters', 0)}")
    print(f"  📁 metadata: {report.get('metadata', 0)}")
    print(f"  🔗 provenance: {report.get('provenance', 0)}")
    print(f"  🔍 descriptors: {report.get('descriptors', 0)}")
    print(f"  ❓ unknown: {report.get('unknown_fields', 0)}")
    print()
    
    # Show metric resolution
    print("=" * 70)
    print("METRIC RESOLUTION")
    print("=" * 70)
    print(f"  Resolved to canonical: {report['resolved_to_canonical']}")
    print(f"  Valid values: {report['valid_values']}")
    print(f"  Invalid values: {report['invalid_values']}")
    print()
    
    # Show governance breakdown
    print("=" * 70)
    print("GOVERNANCE STATUS BREAKDOWN (METRICS ONLY)")
    print("=" * 70)
    
    status_counts = {"validated": 0, "passed": 0, "provisional": 0, "exploratory": 0, "invalid": 0, "unknown": 0, "non_metric": 0}
    for result in report["results"]:
        if "summary" in result:
            for status, count in result["summary"].items():
                if status in status_counts:
                    status_counts[status] += count
    
    for status, count in status_counts.items():
        symbol = {
            "validated": "✅", 
            "passed": "✓", 
            "provisional": "📋", 
            "exploratory": "🔍", 
            "invalid": "❌", 
            "unknown": "❓",
            "non_metric": "➖"
        }.get(status, "?")
        print(f"  {symbol} {status}: {count}")
    
    print()
    
    # Show invalid values
    print("=" * 70)
    print("INVALID VALUES DETECTED (METRICS ONLY)")
    print("=" * 70)
    
    invalid_count = 0
    for result in report["results"]:
        if "migrations" in result:
            for migration in result["migrations"]:
                if migration.get("issues") and migration.get("governance_status") != "non_metric":
                    invalid_count += 1
                    if invalid_count <= 20:  # Show first 20
                        print(f"\n  File: {result['filepath']}")
                        print(f"  Metric: {migration['original_name']} → {migration['canonical_name']}")
                        print(f"  Value: {migration['value']}")
                        print(f"  Issues: {', '.join(migration['issues'])}")
    
    if invalid_count > 20:
        print(f"\n  ... and {invalid_count - 20} more invalid values")
    
    print()
    print("=" * 70)
    print("GOVERNANCE POLICY:")
    print("  ✅ VALIDATED: Can support claims")
    print("  ✓ PASSED: Can appear in reports")
    print("  📋 PROVISIONAL: Needs validation")
    print("  🔍 EXPLORATORY: Hypothesis-generating only")
    print("  ❌ INVALID: Must be repaired")
    print("  ❓ UNKNOWN: Must be registered in canonical_aliases.py")
    print("  ➖ NON-METRIC: Parameter/metadata/provenance (not processed)")
    print("=" * 70)
    
    # Save report
    report_path = workspace / "integrated_migration_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        # Convert Path objects to strings for JSON serialization
        report_copy = json.loads(json.dumps(report, default=str))
        json.dump(report_copy, f, indent=2)
    
    print(f"\nFull report saved to: {report_path}")


if __name__ == "__main__":
    main()