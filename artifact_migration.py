"""
Historical Artifact Migration System
=====================================

Migrates legacy metric fields to the new governance classes:
- validated_metric: Passed all validation, can support claims
- provisional_metric: Defined but needs validation
- exploratory_metric: Hypothesis-generating, not for claims
- invalid_metric: Known issues, preserved for audit trail

Date: April 15, 2026
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime


class MigrationStatus(Enum):
    """Status after migration"""
    VALIDATED_METRIC = "validated_metric"
    PROVISIONAL_METRIC = "provisional_metric"
    EXPLORATORY_METRIC = "exploratory_metric"
    INVALID_METRIC = "invalid_metric"
    UNKNOWN_METRIC = "unknown_metric"


@dataclass
class MetricAlias:
    """Maps legacy metric names to canonical names"""
    legacy_name: str
    canonical_name: str
    metric_class: str
    status: MigrationStatus
    notes: str


# =============================================================================
# LEGACY METRIC ALIASES
# =============================================================================

LEGACY_ALIASES: Dict[str, MetricAlias] = {
    # Phi Resonance variants
    "phi_resonance": MetricAlias(
        legacy_name="phi_resonance",
        canonical_name="phi_resonance_score",
        metric_class="NORMALIZED_SCORE",
        status=MigrationStatus.PROVISIONAL_METRIC,
        notes="Legacy name. Check if value is in [0,1]. If >1, it's a raw ratio."
    ),
    "phi_resonance_target": MetricAlias(
        legacy_name="phi_resonance_target",
        canonical_name="phi_target_constant",
        metric_class="TARGET_CONSTANT",
        status=MigrationStatus.EXPLORATORY_METRIC,
        notes="Target constant, not a measurement. Value should be φ ≈ 1.618."
    ),
    "mean_phi_resonance": MetricAlias(
        legacy_name="mean_phi_resonance",
        canonical_name="phi_resonance_score",
        metric_class="NORMALIZED_SCORE",
        status=MigrationStatus.PROVISIONAL_METRIC,
        notes="Mean of phi resonance measurements."
    ),
    "std_phi_resonance": MetricAlias(
        legacy_name="std_phi_resonance",
        canonical_name="phi_resonance_std",
        metric_class="UNBOUNDED_POSITIVE",
        status=MigrationStatus.PROVISIONAL_METRIC,
        notes="Standard deviation of phi resonance."
    ),
    "phi_resonance_variance": MetricAlias(
        legacy_name="phi_resonance_variance",
        canonical_name="phi_resonance_variance",
        metric_class="UNBOUNDED_POSITIVE",
        status=MigrationStatus.PROVISIONAL_METRIC,
        notes="Variance of phi resonance."
    ),
    
    # Phi Coherence variants
    "phi_coherence": MetricAlias(
        legacy_name="phi_coherence",
        canonical_name="phi_coherence",
        metric_class="NORMALIZED_SCORE",
        status=MigrationStatus.PROVISIONAL_METRIC,
        notes="Must be in [0,1]. Check for null model significance."
    ),
    "mean_phi_coherence": MetricAlias(
        legacy_name="mean_phi_coherence",
        canonical_name="phi_coherence",
        metric_class="NORMALIZED_SCORE",
        status=MigrationStatus.PROVISIONAL_METRIC,
        notes="Mean phi coherence."
    ),
    "std_phi_coherence": MetricAlias(
        legacy_name="std_phi_coherence",
        canonical_name="phi_coherence_std",
        metric_class="UNBOUNDED_POSITIVE",
        status=MigrationStatus.PROVISIONAL_METRIC,
        notes="Standard deviation of phi coherence."
    ),
    "phi_coherence_min": MetricAlias(
        legacy_name="phi_coherence_min",
        canonical_name="phi_coherence_threshold",
        metric_class="NORMALIZED_SCORE",
        status=MigrationStatus.EXPLORATORY_METRIC,
        notes="Minimum threshold for phi coherence."
    ),
    
    # Phi Ratio variants
    "phi_ratio": MetricAlias(
        legacy_name="phi_ratio",
        canonical_name="phi_ratio",
        metric_class="RAW_RATIO",
        status=MigrationStatus.EXPLORATORY_METRIC,
        notes="Raw ratio. Can be any positive value. Not a normalized score."
    ),
    "dna_phi_ratio": MetricAlias(
        legacy_name="dna_phi_ratio",
        canonical_name="phi_ratio",
        metric_class="RAW_RATIO",
        status=MigrationStatus.EXPLORATORY_METRIC,
        notes="DNA-based phi ratio measurement."
    ),
    "near_phi_ratio": MetricAlias(
        legacy_name="near_phi_ratio",
        canonical_name="phi_ratio_proximity",
        metric_class="NORMALIZED_SCORE",
        status=MigrationStatus.PROVISIONAL_METRIC,
        notes="Proximity to phi ratio. Should be in [0,1]."
    ),
    
    # Entanglement Entropy variants
    "entanglement_entropy": MetricAlias(
        legacy_name="entanglement_entropy",
        canonical_name="entanglement_entropy",
        metric_class="BOUNDED_ENTROPY",
        status=MigrationStatus.PROVISIONAL_METRIC,
        notes="Must be >= 0. Negative values indicate BUG - must be regenerated."
    ),
    "metrics.entanglement_entropy": MetricAlias(
        legacy_name="metrics.entanglement_entropy",
        canonical_name="entanglement_entropy",
        metric_class="BOUNDED_ENTROPY",
        status=MigrationStatus.PROVISIONAL_METRIC,
        notes="Nested path for entanglement entropy."
    ),
    
    # Quantum Coherence variants
    "quantum_coherence": MetricAlias(
        legacy_name="quantum_coherence",
        canonical_name="quantum_coherence",
        metric_class="NORMALIZED_SCORE",
        status=MigrationStatus.VALIDATED_METRIC,
        notes="Validated metric. Must be in [0,1]."
    ),
    
    # Tesseract Symmetry variants
    "tesseract_symmetry": MetricAlias(
        legacy_name="tesseract_symmetry",
        canonical_name="tesseract_symmetry",
        metric_class="NORMALIZED_SCORE",
        status=MigrationStatus.PROVISIONAL_METRIC,
        notes="4D symmetry measure. Should be in [0,1]."
    ),
    
    # Consciousness metrics
    "consciousness_level": MetricAlias(
        legacy_name="consciousness_level",
        canonical_name="consciousness_level",
        metric_class="NORMALIZED_SCORE",
        status=MigrationStatus.EXPLORATORY_METRIC,
        notes="NOT VALIDATED. No formal definition. Use with extreme caution."
    ),
    
    # Biomimetic Resonance
    "biomimetic_resonance": MetricAlias(
        legacy_name="biomimetic_resonance",
        canonical_name="biomimetic_resonance",
        metric_class="NORMALIZED_SCORE",
        status=MigrationStatus.PROVISIONAL_METRIC,
        notes="Must be in [0,1]. Values >1 indicate BUG in computation."
    ),
    
    # Platonic Alignment
    "platonic_alignment_score": MetricAlias(
        legacy_name="platonic_alignment_score",
        canonical_name="platonic_alignment_score",
        metric_class="NORMALIZED_SCORE",
        status=MigrationStatus.VALIDATED_METRIC,
        notes="Validated metric. Must be in [0,1]."
    ),
    
    # Phi Invariant Score
    "phi_invariant_score": MetricAlias(
        legacy_name="phi_invariant_score",
        canonical_name="phi_invariant_score",
        metric_class="NORMALIZED_SCORE",
        status=MigrationStatus.VALIDATED_METRIC,
        notes="Validated on IBM hardware. Should be ≈ 0.618."
    ),
}


# =============================================================================
# KNOWN INVALID VALUES
# =============================================================================

KNOWN_INVALID_PATTERNS = {
    "negative_entropy": {
        "pattern": lambda v: isinstance(v, (int, float)) and v < 0 and "entropy" in "",
        "fields": ["entanglement_entropy", "metrics.entanglement_entropy"],
        "issue": "Negative entropy indicates buggy partial trace implementation",
        "action": "mark_invalid",
        "repair": "regenerate_with_fixed_code"
    },
    "phi_out_of_range": {
        "pattern": lambda v: isinstance(v, (int, float)) and v > 1.0,
        "fields": ["phi_resonance", "phi_coherence", "biomimetic_resonance", "quantum_coherence"],
        "issue": "Value > 1.0 for normalized score metric",
        "action": "check_class",
        "repair": "verify_metric_class_or_renormalize"
    },
    "exactly_phi": {
        "pattern": lambda v: isinstance(v, (int, float)) and abs(v - 1.618033988749895) < 0.001,
        "fields": ["phi_resonance", "phi_resonance_target"],
        "issue": "Value exactly equals φ - likely a constant, not a measurement",
        "action": "reclassify_as_target_constant",
        "repair": "rename_to_phi_target_constant"
    }
}


# =============================================================================
# MIGRATION ENGINE
# =============================================================================

class ArtifactMigrator:
    """Migrates legacy artifacts to new governance classes."""
    
    def __init__(self, registry_version: str = "1.0.0"):
        self.registry_version = registry_version
        self.migration_log: List[Dict] = []
        self.stats = {
            "total_artifacts": 0,
            "total_metrics": 0,
            "validated": 0,
            "provisional": 0,
            "exploratory": 0,
            "invalid": 0,
            "unknown": 0,
            "repaired": 0
        }
    
    def classify_metric(self, 
                        metric_name: str, 
                        value: float,
                        context: str = "") -> Tuple[str, MigrationStatus, str]:
        """
        Classify a metric value into governance status.
        
        Returns:
            (canonical_name, status, notes)
        """
        # Check if in legacy aliases
        if metric_name in LEGACY_ALIASES:
            alias = LEGACY_ALIASES[metric_name]
            canonical_name = alias.canonical_name
            status = alias.status
            notes = alias.notes
            
            # Check for known invalid patterns
            if "entropy" in metric_name.lower() and value < 0:
                status = MigrationStatus.INVALID_METRIC
                notes = f"INVALID: Negative entropy ({value}). {notes}"
            
            # Check for out-of-range normalized scores
            if alias.metric_class == "NORMALIZED_SCORE" and (value < 0 or value > 1):
                if abs(value - 1.618033988749895) < 0.01:
                    # Value is exactly φ - reclassify as target constant
                    status = MigrationStatus.EXPLORATORY_METRIC
                    notes = f"RECLASSIFIED: Value {value} ≈ φ. This is a target constant, not a normalized score. {notes}"
                else:
                    status = MigrationStatus.INVALID_METRIC
                    notes = f"INVALID: Value {value} out of range [0,1] for normalized score. {notes}"
            
            return canonical_name, status, notes
        
        # Unknown metric
        return metric_name, MigrationStatus.UNKNOWN_METRIC, "Unknown metric - not in registry"
    
    def migrate_value(self, 
                      metric_name: str, 
                      value: float,
                      context: str = "") -> Dict:
        """
        Migrate a single metric value.
        
        Returns:
            Migration record with canonical name, status, and notes
        """
        canonical_name, status, notes = self.classify_metric(metric_name, value, context)
        
        record = {
            "original_name": metric_name,
            "canonical_name": canonical_name,
            "original_value": value,
            "migrated_value": value,
            "status": status.value,
            "notes": notes,
            "registry_version": self.registry_version,
            "migration_timestamp": datetime.now().isoformat()
        }
        
        # Update stats
        self.stats["total_metrics"] += 1
        if status == MigrationStatus.VALIDATED_METRIC:
            self.stats["validated"] += 1
        elif status == MigrationStatus.PROVISIONAL_METRIC:
            self.stats["provisional"] += 1
        elif status == MigrationStatus.EXPLORATORY_METRIC:
            self.stats["exploratory"] += 1
        elif status == MigrationStatus.INVALID_METRIC:
            self.stats["invalid"] += 1
        else:
            self.stats["unknown"] += 1
        
        self.migration_log.append(record)
        return record
    
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
        except (json.JSONDecodeError, UnicodeDecodeError, FileNotFoundError) as e:
            return {
                "filepath": str(filepath),
                "error": str(e),
                "status": "error"
            }
        
        self.stats["total_artifacts"] += 1
        
        # Find all metric fields
        metric_fields = self._find_metric_fields(data)
        
        migration_report = {
            "filepath": str(filepath),
            "total_fields": len(metric_fields),
            "migrations": [],
            "summary": {
                "validated": 0,
                "provisional": 0,
                "exploratory": 0,
                "invalid": 0,
                "unknown": 0
            }
        }
        
        # Migrate each field
        for field_path, value in metric_fields.items():
            if isinstance(value, (int, float)):
                record = self.migrate_value(field_path, value, str(filepath))
                migration_report["migrations"].append(record)
                migration_report["summary"][record["status"].split("_")[0]] += 1
        
        # Write migrated data if not dry run
        if not dry_run:
            # Add migration metadata
            data["_migration_metadata"] = {
                "registry_version": self.registry_version,
                "migration_timestamp": datetime.now().isoformat(),
                "total_metrics": len(metric_fields),
                "migration_summary": migration_report["summary"]
            }
            
            # Write back
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
        
        return migration_report
    
    def _find_metric_fields(self, 
                           data: dict, 
                           prefix: str = "",
                           max_depth: int = 10) -> Dict[str, float]:
        """Recursively find all numeric fields that might be metrics."""
        metrics = {}
        
        if max_depth <= 0:
            return metrics
        
        # Known metric field names
        metric_patterns = [
            "phi", "entropy", "coherence", "resonance", "symmetry",
            "alignment", "consciousness", "biomimetic", "quantum"
        ]
        
        for key, value in data.items():
            if key.startswith("_"):
                continue
                
            full_path = f"{prefix}.{key}" if prefix else key
            
            if isinstance(value, dict):
                # Recurse into nested dicts
                nested = self._find_metric_fields(value, full_path, max_depth - 1)
                metrics.update(nested)
            elif isinstance(value, (int, float)):
                # Check if key matches metric patterns
                key_lower = key.lower()
                if any(pattern in key_lower for pattern in metric_patterns):
                    metrics[full_path] = value
        
        return metrics
    
    def migrate_all_artifacts(self, 
                             root_dir: str = ".",
                             patterns: List[str] = None,
                             dry_run: bool = True) -> Dict:
        """
        Migrate all artifacts in a directory.
        
        Args:
            root_dir: Root directory to search
            patterns: File patterns to match
            dry_run: If True, don't write changes
            
        Returns:
            Complete migration report
        """
        if patterns is None:
            patterns = ["**/*analysis*.json", "**/*results*.json", "**/*report*.json"]
        
        root = Path(root_dir)
        all_files = []
        for pattern in patterns:
            all_files.extend(root.glob(pattern))
        
        # Remove duplicates
        all_files = list(set(all_files))
        
        # Filter out cache and venv directories
        all_files = [f for f in all_files if ".mypy_cache" not in str(f) 
                     and ".venv" not in str(f) 
                     and "node_modules" not in str(f)]
        
        migration_report = {
            "registry_version": self.registry_version,
            "migration_timestamp": datetime.now().isoformat(),
            "total_artifacts": len(all_files),
            "artifacts": [],
            "summary": self.stats
        }
        
        for filepath in all_files:
            report = self.migrate_artifact(filepath, dry_run)
            migration_report["artifacts"].append(report)
        
        migration_report["summary"] = self.stats
        
        return migration_report
    
    def generate_migration_report(self) -> str:
        """Generate human-readable migration report."""
        report = []
        report.append("="*70)
        report.append("HISTORICAL ARTIFACT MIGRATION REPORT")
        report.append("="*70)
        report.append(f"\nRegistry Version: {self.registry_version}")
        report.append(f"Migration Timestamp: {datetime.now().isoformat()}")
        
        report.append("\nSUMMARY:")
        report.append(f"  Total Artifacts: {self.stats['total_artifacts']}")
        report.append(f"  Total Metrics: {self.stats['total_metrics']}")
        report.append(f"  ✅ Validated: {self.stats['validated']}")
        report.append(f"  📋 Provisional: {self.stats['provisional']}")
        report.append(f"  🔍 Exploratory: {self.stats['exploratory']}")
        report.append(f"  ❌ Invalid: {self.stats['invalid']}")
        report.append(f"  ❓ Unknown: {self.stats['unknown']}")
        
        # Group by status
        validated = [r for r in self.migration_log if r["status"] == "validated_metric"]
        provisional = [r for r in self.migration_log if r["status"] == "provisional_metric"]
        exploratory = [r for r in self.migration_log if r["status"] == "exploratory_metric"]
        invalid = [r for r in self.migration_log if r["status"] == "invalid_metric"]
        unknown = [r for r in self.migration_log if r["status"] == "unknown_metric"]
        
        if validated:
            report.append("\n✅ VALIDATED METRICS (can support claims):")
            for r in validated[:10]:  # Show first 10
                report.append(f"  {r['canonical_name']}: {r['original_value']:.4f}")
            if len(validated) > 10:
                report.append(f"  ... and {len(validated) - 10} more")
        
        if provisional:
            report.append("\n📋 PROVISIONAL METRICS (need validation):")
            for r in provisional[:10]:
                report.append(f"  {r['original_name']} → {r['canonical_name']}: {r['original_value']:.4f}")
            if len(provisional) > 10:
                report.append(f"  ... and {len(provisional) - 10} more")
        
        if exploratory:
            report.append("\n🔍 EXPLORATORY METRICS (hypothesis-generating):")
            for r in exploratory[:10]:
                report.append(f"  {r['original_name']}: {r['original_value']:.4f}")
                report.append(f"    {r['notes']}")
            if len(exploratory) > 10:
                report.append(f"  ... and {len(exploratory) - 10} more")
        
        if invalid:
            report.append("\n❌ INVALID METRICS (need repair):")
            for r in invalid:
                report.append(f"  {r['original_name']}: {r['original_value']:.4f}")
                report.append(f"    {r['notes']}")
        
        if unknown:
            report.append("\n❓ UNKNOWN METRICS (not in registry):")
            for r in unknown[:10]:
                report.append(f"  {r['original_name']}: {r['original_value']:.4f}")
            if len(unknown) > 10:
                report.append(f"  ... and {len(unknown) - 10} more")
        
        report.append("\n" + "="*70)
        report.append("GOVERNANCE POLICY:")
        report.append("  - Only VALIDATED metrics can support claims")
        report.append("  - PROVISIONAL metrics need null model validation")
        report.append("  - EXPLORATORY metrics are hypothesis-generating only")
        report.append("  - INVALID metrics must be repaired or removed")
        report.append("  - UNKNOWN metrics must be added to registry")
        report.append("="*70)
        
        return "\n".join(report)
    
    def save_migration_log(self, output_path: str):
        """Save migration log to JSON."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                "registry_version": self.registry_version,
                "migration_timestamp": datetime.now().isoformat(),
                "stats": self.stats,
                "log": self.migration_log
            }, f, indent=2, default=str)
        print(f"✅ Migration log saved to: {output_path}")


# =============================================================================
# REPAIR FUNCTIONS
# =============================================================================

def repair_negative_entropy(value: float) -> Tuple[float, str]:
    """
    Repair negative entropy values.
    
    The old implementation had a buggy partial trace that could produce
    negative values. The fixed implementation always produces non-negative entropy.
    
    Returns:
        (repaired_value, repair_notes)
    """
    if value < 0:
        # Negative entropy is mathematically impossible
        # The correct value should be recomputed with fixed code
        return 0.0, f"REPAIRED: Negative entropy ({value}) set to 0. RECOMMEND: Regenerate with fixed code"
    return value, "OK"


def repair_out_of_range_normalized(value: float, metric_name: str) -> Tuple[float, str]:
    """
    Repair out-of-range normalized scores.
    
    If value > 1 for a normalized score, check if it's actually a raw ratio.
    """
    if value > 1.0:
        # Check if it's approximately phi
        if abs(value - 1.618033988749895) < 0.01:
            return value, f"RECLASSIFY: Value {value} ≈ φ. This is a TARGET CONSTANT, not a normalized score"
        # Check if it might be a raw ratio
        return value, f"WARNING: Value {value} > 1 for normalized score. Verify metric class"
    return value, "OK"


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("="*70)
    print("HISTORICAL ARTIFACT MIGRATION")
    print("="*70)
    
    migrator = ArtifactMigrator(registry_version="1.0.0")
    
    # Run migration (dry run first)
    print("\nRunning migration (dry run)...")
    report = migrator.migrate_all_artifacts(
        root_dir=".",
        dry_run=True
    )
    
    # Print report
    print(migrator.generate_migration_report())
    
    # Save migration log
    migrator.save_migration_log("migration_log.json")
    
    print("\n" + "="*70)
    print("NEXT STEPS:")
    print("  1. Review migration_log.json for all changes")
    print("  2. Run with dry_run=False to apply changes")
    print("  3. Regenerate artifacts with invalid metrics")
    print("  4. Update metric registry with unknown metrics")
    print("="*70)