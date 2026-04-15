"""
Sidecar Mapping Generator
===========================

Generates sidecar mapping files that associate canonical names with legacy fields
without mutating historical artifacts. This preserves audit trails and allows
review before any write-back.

Each sidecar file contains:
- Original field path
- Canonical name (if resolved)
- Field class (metric/parameter/metadata/provenance/descriptor)
- Governance status (for metrics)
- Validation status
- Alias provenance chain

Date: April 15, 2026
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import Counter

from field_taxonomy import FieldClass, classify_field
from canonical_aliases import AliasResolver, GovernanceStatus


@dataclass
class SidecarEntry:
    """Single field mapping entry"""
    original_path: str
    field_name: str
    field_class: str
    canonical_name: Optional[str]
    governance_status: Optional[str]
    metric_class: Optional[str]
    valid_range: Optional[tuple]
    value: float
    is_valid: bool
    issues: List[str]
    alias_chain: List[str]  # Provenance: how we resolved this


@dataclass
class ArtifactSidecar:
    """Sidecar for a single artifact"""
    source_file: str
    generated_at: str
    registry_version: str
    total_fields: int
    field_breakdown: Dict[str, int]
    metric_breakdown: Dict[str, int]
    mappings: List[SidecarEntry]
    unresolved_high_frequency: List[tuple]  # (field_name, count) for review


class SidecarMappingGenerator:
    """Generates sidecar mapping files without mutating artifacts."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.resolver = AliasResolver()
        
        # Track global statistics
        self.global_stats = {
            "total_artifacts": 0,
            "total_fields": 0,
            "by_class": Counter(),
            "by_governance": Counter(),
            "unknown_fields": Counter(),
            "invalid_values": 0,
            "valid_values": 0
        }
    
    def generate_sidecar(self, artifact_path: Path) -> Optional[ArtifactSidecar]:
        """
        Generate sidecar mapping for a single artifact.
        
        Returns:
            ArtifactSidecar with complete mapping information
        """
        try:
            with open(artifact_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError, 
                FileNotFoundError, PermissionError) as e:
            return None
        
        self.global_stats["total_artifacts"] += 1
        
        # Find all fields
        fields = self._extract_fields(data)
        self.global_stats["total_fields"] += len(fields)
        
        # Generate mappings
        mappings = []
        field_breakdown = Counter()
        metric_breakdown = Counter()
        local_unknown = Counter()
        
        for field_path, value in fields.items():
            # Classify field
            field_def = classify_field(field_path)
            field_breakdown[field_def.field_class.value] += 1
            self.global_stats["by_class"][field_def.field_class.value] += 1
            
            # Build mapping entry
            entry = self._create_sidecar_entry(field_path, value, field_def)
            mappings.append(entry)
            
            # Track metrics
            if field_def.field_class == FieldClass.METRIC:
                if entry.governance_status:
                    metric_breakdown[entry.governance_status] += 1
                    self.global_stats["by_governance"][entry.governance_status] += 1
                
                if entry.is_valid:
                    self.global_stats["valid_values"] += 1
                else:
                    self.global_stats["invalid_values"] += 1
                    
                if entry.canonical_name is None:
                    local_unknown[field_def.field_name] += 1
                    self.global_stats["unknown_fields"][field_def.field_name] += 1
        
        # Get top unknowns for this artifact
        unresolved = local_unknown.most_common(10)
        
        sidecar = ArtifactSidecar(
            source_file=str(artifact_path),
            generated_at=datetime.now().isoformat(),
            registry_version="1.0.0",
            total_fields=len(fields),
            field_breakdown=dict(field_breakdown),
            metric_breakdown=dict(metric_breakdown),
            mappings=mappings,
            unresolved_high_frequency=unresolved
        )
        
        return sidecar
    
    def _extract_fields(self, data: Any, prefix: str = "") -> Dict[str, float]:
        """Extract all numeric fields from data structure."""
        fields = {}
        
        if isinstance(data, dict):
            for key, value in data.items():
                path = f"{prefix}.{key}" if prefix else key
                
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    fields[path] = float(value)
                elif isinstance(value, dict):
                    fields.update(self._extract_fields(value, path))
                elif isinstance(value, list):
                    for i, item in enumerate(value):
                        if isinstance(item, dict):
                            fields.update(self._extract_fields(item, f"{path}[{i}]"))
        
        return fields
    
    def _create_sidecar_entry(self, field_path: str, value: float, 
                              field_def) -> SidecarEntry:
        """Create a sidecar entry for a field."""
        
        # Build alias chain
        alias_chain = [field_path]
        
        # Only resolve canonical names for metrics
        if field_def.field_class == FieldClass.METRIC:
            canonical_name, metric = self.resolver.resolve(field_path)
            
            if canonical_name:
                alias_chain.append(f"resolved:{canonical_name}")
                
                # Validate
                is_valid, issues = self._validate_value(canonical_name, value, metric)
                
                return SidecarEntry(
                    original_path=field_path,
                    field_name=field_def.field_name,
                    field_class=field_def.field_class.value,
                    canonical_name=canonical_name,
                    governance_status=metric.governance_status.value if metric else None,
                    metric_class=metric.metric_class.value if metric else None,
                    valid_range=metric.valid_range if metric else None,
                    value=value,
                    is_valid=is_valid,
                    issues=issues,
                    alias_chain=alias_chain
                )
            else:
                alias_chain.append("unresolved")
                return SidecarEntry(
                    original_path=field_path,
                    field_name=field_def.field_name,
                    field_class=field_def.field_class.value,
                    canonical_name=None,
                    governance_status="unknown",
                    metric_class=None,
                    valid_range=None,
                    value=value,
                    is_valid=False,
                    issues=["Metric not in canonical registry"],
                    alias_chain=alias_chain
                )
        
        # Non-metric fields
        return SidecarEntry(
            original_path=field_path,
            field_name=field_def.field_name,
            field_class=field_def.field_class.value,
            canonical_name=None,
            governance_status=None,
            metric_class=None,
            valid_range=None,
            value=value,
            is_valid=True,
            issues=[],
            alias_chain=alias_chain
        )
    
    def _validate_value(self, canonical_name: str, value: float, metric) -> tuple:
        """Validate a value against its canonical definition."""
        if metric is None:
            return False, ["Unknown canonical metric"]
        
        issues = []
        min_val, max_val = metric.valid_range
        
        if min_val is not None and value < min_val:
            issues.append(f"Value {value} < minimum {min_val}")
        
        if max_val is not None and value > max_val:
            if abs(value - 1.618033988749895) < 0.01 and "phi" in canonical_name:
                issues.append(f"Value {value:.4f} ≈ φ - likely target constant")
            else:
                issues.append(f"Value {value} > maximum {max_val}")
        
        if "entropy" in canonical_name.lower() and value < 0:
            issues.append(f"Negative entropy ({value}) - buggy partial trace")
        
        return len(issues) == 0, issues
    
    def write_sidecar(self, sidecar: ArtifactSidecar) -> Path:
        """Write sidecar to file."""
        # Create sidecar filename: original.json -> original.sidecar.json
        source_path = Path(sidecar.source_file)
        sidecar_name = source_path.stem + ".sidecar.json"
        sidecar_path = self.output_dir / sidecar_name
        
        # Convert to serializable dict
        sidecar_dict = asdict(sidecar)
        
        with open(sidecar_path, 'w', encoding='utf-8') as f:
            json.dump(sidecar_dict, f, indent=2, default=str)
        
        return sidecar_path
    
    def generate_global_summary(self) -> Dict:
        """Generate global summary of all sidecars."""
        return {
            "generated_at": datetime.now().isoformat(),
            "registry_version": "1.0.0",
            "total_artifacts": self.global_stats["total_artifacts"],
            "total_fields": self.global_stats["total_fields"],
            "field_classification": dict(self.global_stats["by_class"]),
            "governance_breakdown": dict(self.global_stats["by_governance"]),
            "valid_values": self.global_stats["valid_values"],
            "invalid_values": self.global_stats["invalid_values"],
            "top_unknown_fields": self.global_stats["unknown_fields"].most_common(100),
            "writeback_thresholds": {
                "unknown_rate_target": 0.03,  # 3%
                "current_unknown_rate": round(
                    len(self.global_stats["unknown_fields"]) / 
                    max(self.global_stats["total_fields"], 1), 4
                ),
                "ready_for_writeback": (
                    len(self.global_stats["unknown_fields"]) / 
                    max(self.global_stats["total_fields"], 1) < 0.03
                )
            }
        }


def main():
    """Generate sidecar mappings for all artifacts."""
    print("=" * 70)
    print("SIDECAR MAPPING GENERATOR")
    print("=" * 70)
    print()
    print("Generating sidecar files without mutating artifacts...")
    print()
    
    workspace = Path("d:/AGI-GH-REPO-11326/AGI-model")
    sidecar_dir = workspace / "sidecar_mappings"
    
    generator = SidecarMappingGenerator(sidecar_dir)
    
    # Process all JSON artifacts
    artifact_count = 0
    sidecar_count = 0
    
    for artifact_path in workspace.rglob("*.json"):
        # Skip sidecars and non-artifact files
        if any(skip in str(artifact_path).lower() for skip in [
            "sidecar", "migration", "registry", "taxonomy", 
            "canonical", "node_modules", ".git", ".venv", "mypy_cache"
        ]):
            continue
        
        sidecar = generator.generate_sidecar(artifact_path)
        if sidecar:
            sidecar_path = generator.write_sidecar(sidecar)
            artifact_count += 1
            sidecar_count += 1
            
            if artifact_count % 1000 == 0:
                print(f"  Processed {artifact_count} artifacts...")
    
    # Generate global summary
    summary = generator.generate_global_summary()
    summary_path = sidecar_dir / "_global_summary.json"
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, default=str)
    
    # Print summary
    print()
    print("=" * 70)
    print("SIDECAR GENERATION COMPLETE")
    print("=" * 70)
    print(f"Artifacts processed: {artifact_count}")
    print(f"Sidecar files generated: {sidecar_count}")
    print(f"Sidecar directory: {sidecar_dir}")
    print()
    
    print("=" * 70)
    print("FIELD CLASSIFICATION SUMMARY")
    print("=" * 70)
    for field_class, count in summary["field_classification"].items():
        pct = count / summary["total_fields"] * 100 if summary["total_fields"] > 0 else 0
        print(f"  {field_class}: {count} ({pct:.1f}%)")
    print()
    
    print("=" * 70)
    print("GOVERNANCE BREAKDOWN (METRICS ONLY)")
    print("=" * 70)
    for status, count in summary["governance_breakdown"].items():
        print(f"  {status}: {count}")
    print()
    
    print("=" * 70)
    print("WRITEBACK THRESHOLD ANALYSIS")
    print("=" * 70)
    print(f"  Target unknown rate: {summary['writeback_thresholds']['unknown_rate_target']:.1%}")
    print(f"  Current unknown rate: {summary['writeback_thresholds']['current_unknown_rate']:.2%}")
    print(f"  Ready for writeback: {summary['writeback_thresholds']['ready_for_writeback']}")
    print()
    
    print("=" * 70)
    print("TOP 20 UNKNOWN FIELDS (FOR REVIEW)")
    print("=" * 70)
    for field_name, count in summary["top_unknown_fields"][:20]:
        print(f"  {field_name}: {count} occurrences")
    print()
    
    print("=" * 70)
    print("NEXT STEPS")
    print("=" * 70)
    print("1. Review sidecar files in: {sidecar_dir}")
    print("2. Register high-frequency unknowns in canonical_aliases.py")
    print("3. Re-run sidecar generation")
    print("4. When ready, apply writeback with: dry_run=False")
    print("=" * 70)


if __name__ == "__main__":
    main()
