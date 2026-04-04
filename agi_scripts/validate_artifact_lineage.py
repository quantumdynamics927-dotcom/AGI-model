#!/usr/bin/env python3
"""
Artifact Lineage Validator
==========================

Validates DNA agent artifacts for proper classification, lineage integrity,
and evidence class consistency.

Usage:
    python agi_scripts/validate_artifact_lineage.py [artifact_path]
    python agi_scripts/validate_artifact_lineage.py --all
    python agi_scripts/validate_artifact_lineage.py --dir dna_34bp_results/

Exit codes:
    0 = All validations passed
    1 = Validation failures detected
    2 = Invalid arguments or runtime error
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime


# Evidence class hierarchy
EVIDENCE_CLASS_PRIMARY = "primary"
EVIDENCE_CLASS_SECONDARY = "secondary"
EVIDENCE_CLASS_INTERPRETIVE = "interpretive"

# Artifact types
ARTIFACT_TYPE_RAW_HARDWARE = "raw_hardware"
ARTIFACT_TYPE_DERIVED_METRICS = "derived_metrics"
ARTIFACT_TYPE_RECONSTRUCTED = "reconstructed"
ARTIFACT_TYPE_NARRATIVE = "narrative_report"

# Valid combinations
VALID_ARTIFACT_TYPES = {
    ARTIFACT_TYPE_RAW_HARDWARE,
    ARTIFACT_TYPE_DERIVED_METRICS,
    ARTIFACT_TYPE_RECONSTRUCTED,
    ARTIFACT_TYPE_NARRATIVE,
}

ARTIFACT_TO_EVIDENCE_CLASS = {
    ARTIFACT_TYPE_RAW_HARDWARE: EVIDENCE_CLASS_PRIMARY,
    ARTIFACT_TYPE_DERIVED_METRICS: EVIDENCE_CLASS_SECONDARY,
    ARTIFACT_TYPE_RECONSTRUCTED: EVIDENCE_CLASS_SECONDARY,  # Machine-produced analysis
    ARTIFACT_TYPE_NARRATIVE: EVIDENCE_CLASS_INTERPRETIVE,   # Human-readable prose
}


class ValidationError:
    """Represents a single validation error."""
    
    def __init__(self, artifact_id: str, field: str, message: str, severity: str = "error"):
        self.artifact_id = artifact_id
        self.field = field
        self.message = message
        self.severity = severity  # 'error', 'warning', 'info'
    
    def __str__(self):
        return f"[{self.severity.upper()}] {self.artifact_id}::{self.field}: {self.message}"


class ArtifactValidator:
    """Validates DNA agent artifacts for lineage integrity."""
    
    def __init__(self):
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []
        self.infos: List[ValidationError] = []
    
    def validate_artifact(self, artifact_path: Path) -> bool:
        """Validate a single artifact file. Returns True if valid."""
        artifact_id = artifact_path.stem
        
        try:
            with open(artifact_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(ValidationError(artifact_id, "file", f"Invalid JSON: {e}"))
            return False
        except Exception as e:
            self.errors.append(ValidationError(artifact_id, "file", f"Cannot read: {e}"))
            return False
        
        # Check for required top-level evidence_class field
        if 'artifact_metadata' not in data:
            self.errors.append(ValidationError(
                artifact_id, "artifact_metadata",
                "Missing artifact_metadata - artifact is unclassified",
                "error"
            ))
            return False
        
        metadata = data['artifact_metadata']
        
        # Validate evidence_class
        evidence_class = metadata.get('evidence_class')
        if not evidence_class:
            self.errors.append(ValidationError(
                artifact_id, "evidence_class",
                "Required field 'evidence_class' is missing",
                "error"
            ))
        elif evidence_class not in {EVIDENCE_CLASS_PRIMARY, EVIDENCE_CLASS_SECONDARY, EVIDENCE_CLASS_INTERPRETIVE}:
            self.errors.append(ValidationError(
                artifact_id, "evidence_class",
                f"Invalid evidence_class: {evidence_class}",
                "error"
            ))
        
        # Validate artifact_type
        artifact_type = metadata.get('artifact_type')
        if not artifact_type:
            self.errors.append(ValidationError(
                artifact_id, "artifact_type",
                "Required field 'artifact_type' is missing",
                "error"
            ))
        elif artifact_type not in VALID_ARTIFACT_TYPES:
            self.errors.append(ValidationError(
                artifact_id, "artifact_type",
                f"Invalid artifact_type: {artifact_type}",
                "error"
            ))
        
        # Validate evidence_class matches artifact_type
        if artifact_type and evidence_class:
            expected_evidence = ARTIFACT_TO_EVIDENCE_CLASS.get(artifact_type)
            if evidence_class != expected_evidence:
                self.errors.append(ValidationError(
                    artifact_id, "consistency",
                    f"evidence_class '{evidence_class}' does not match artifact_type '{artifact_type}' (expected '{expected_evidence}')",
                    "error"
                ))
        
        # Validate artifact_id
        if not metadata.get('artifact_id'):
            self.errors.append(ValidationError(
                artifact_id, "artifact_id",
                "Missing artifact_id for lineage tracking",
                "error"
            ))
        
        # Validate parent_artifacts for derived/reconstructed
        if artifact_type in {ARTIFACT_TYPE_DERIVED_METRICS, ARTIFACT_TYPE_RECONSTRUCTED, ARTIFACT_TYPE_NARRATIVE}:
            parent_artifacts = metadata.get('parent_artifacts', [])
            
            if artifact_type == ARTIFACT_TYPE_DERIVED_METRICS and len(parent_artifacts) != 1:
                self.errors.append(ValidationError(
                    artifact_id, "parent_artifacts",
                    f"Derived metrics must have exactly 1 parent (found {len(parent_artifacts)})",
                    "error"
                ))
            
            if artifact_type == ARTIFACT_TYPE_RECONSTRUCTED and len(parent_artifacts) == 0:
                self.warnings.append(ValidationError(
                    artifact_id, "parent_artifacts",
                    "Reconstructed artifact should reference parent artifacts",
                    "warning"
                ))
        
        # Validate data_lineage
        data_lineage = metadata.get('data_lineage', {})
        
        if artifact_type == ARTIFACT_TYPE_RECONSTRUCTED:
            sources = data_lineage.get('sources', [])
            if len(sources) == 0:
                self.warnings.append(ValidationError(
                    artifact_id, "data_lineage.sources",
                    "Reconstructed artifact should list source directories",
                    "warning"
                ))
            
            if data_lineage.get('derived_from_prior_runs') is not True:
                self.warnings.append(ValidationError(
                    artifact_id, "data_lineage.derived_from_prior_runs",
                    "Reconstructed artifact should have derived_from_prior_runs=true",
                    "warning"
                ))
        
        # Validate provenance for raw hardware
        if artifact_type == ARTIFACT_TYPE_RAW_HARDWARE:
            provenance = metadata.get('provenance')
            if not provenance:
                self.warnings.append(ValidationError(
                    artifact_id, "provenance",
                    "Raw hardware should have provenance metadata (backend, vendor_job_id, etc.)",
                    "warning"
                ))
            elif not provenance.get('vendor_job_id'):
                self.warnings.append(ValidationError(
                    artifact_id, "provenance.vendor_job_id",
                    "Raw hardware should have vendor_job_id",
                    "warning"
                ))
        
        # Validate audit_note
        if not metadata.get('audit_note'):
            self.warnings.append(ValidationError(
                artifact_id, "audit_note",
                "Missing audit_note for forensic review",
                "warning"
            ))
        
        # Validate transform_chain for reconstructed
        if artifact_type == ARTIFACT_TYPE_RECONSTRUCTED:
            transform_chain = data_lineage.get('transform_chain', [])
            if len(transform_chain) == 0:
                self.warnings.append(ValidationError(
                    artifact_id, "transform_chain",
                    "Reconstructed artifact should document transform chain",
                    "warning"
                ))
        
        # Check for raw_hardware claiming to be primary without proper provenance
        if artifact_type == ARTIFACT_TYPE_RAW_HARDWARE:
            if not metadata.get('provenance', {}).get('vendor_job_id'):
                self.errors.append(ValidationError(
                    artifact_id, "claim",
                    "Artifact claims to be raw_hardware but lacks vendor_job_id provenance",
                    "error"
                ))
        
        # Check for reconstructed claiming to be primary
        if artifact_type == ARTIFACT_TYPE_RECONSTRUCTED and evidence_class == EVIDENCE_CLASS_PRIMARY:
            self.errors.append(ValidationError(
                artifact_id, "claim",
                "Reconstructed artifact cannot claim evidence_class='primary'",
                "error"
            ))
        
        # Validate directory placement
        expected_dir = {
            ARTIFACT_TYPE_RAW_HARDWARE: "raw_hardware",
            ARTIFACT_TYPE_DERIVED_METRICS: "derived_metrics",
            ARTIFACT_TYPE_RECONSTRUCTED: "reconstructed",
            ARTIFACT_TYPE_NARRATIVE: "narrative_reports",
        }.get(artifact_type)
        
        if expected_dir and expected_dir not in str(artifact_path.parent):
            self.warnings.append(ValidationError(
                artifact_id, "placement",
                f"Artifact type '{artifact_type}' should be in '{expected_dir}/' directory (found in {artifact_path.parent.name})",
                "warning"
            ))
        
        return len([e for e in self.errors if e.artifact_id == artifact_id and e.severity == "error"]) == 0
    
    def print_report(self):
        """Print validation report."""
        print("\n" + "="*80)
        print("ARTIFACT LINEAGE VALIDATION REPORT")
        print("="*80)
        
        total_errors = len([e for e in self.errors if e.severity == "error"])
        total_warnings = len(self.warnings)
        total_infos = len(self.infos)
        
        if total_errors == 0 and total_warnings == 0:
            print("\n[OK] All validations passed!")
        else:
            print(f"\nErrors: {total_errors}, Warnings: {total_warnings}, Infos: {total_infos}\n")
            
            if self.errors:
                print("ERRORS:")
                for error in self.errors:
                    print(f"  {error}")
            
            if self.warnings:
                print("\nWARNINGS:")
                for warning in self.warnings:
                    print(f"  {warning}")
            
            if self.infos:
                print("\nINFOS:")
                for info in self.infos:
                    print(f"  {info}")
        
        print("\n" + "="*80)
        return total_errors == 0


def validate_all_artifacts(base_dir: Path) -> bool:
    """Validate all artifacts in the directory tree."""
    validator = ArtifactValidator()
    
    # Find all JSON files in artifact directories
    artifact_dirs = [
        base_dir / "raw_hardware",
        base_dir / "derived_metrics",
        base_dir / "reconstructed",
        base_dir / "narrative_reports",
        base_dir / "legacy_unclassified",
    ]
    
    total_files = 0
    valid_files = 0
    
    for artifact_dir in artifact_dirs:
        if not artifact_dir.exists():
            continue
        
        for json_file in artifact_dir.glob("*.json"):
            total_files += 1
            if validator.validate_artifact(json_file):
                valid_files += 1
    
    # Also check root level for unclassified files
    root_json_files = list(base_dir.glob("dna_agent_*.json"))
    if root_json_files:
        print(f"\n[!] WARNING: Found {len(root_json_files)} unclassified files in root directory:")
        for f in root_json_files:
            print(f"    - {f.name}")
        print("    Run migration to classify these files.")
    
    validator.print_report()
    
    print(f"\nFiles validated: {valid_files}/{total_files}")
    
    return valid_files == total_files and len(root_json_files) == 0


def main():
    parser = argparse.ArgumentParser(
        description="Validate DNA agent artifact lineage and classification"
    )
    parser.add_argument(
        "artifact",
        nargs="?",
        help="Path to specific artifact file to validate"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Validate all artifacts in dna_34bp_results/"
    )
    parser.add_argument(
        "--dir",
        default="dna_34bp_results",
        help="Base directory to scan for artifacts (default: dna_34bp_results)"
    )
    
    args = parser.parse_args()
    
    if args.artifact:
        # Validate single file
        artifact_path = Path(args.artifact)
        if not artifact_path.exists():
            print(f"[ERROR] File not found: {artifact_path}")
            sys.exit(2)
        
        validator = ArtifactValidator()
        is_valid = validator.validate_artifact(artifact_path)
        validator.print_report()
        sys.exit(0 if is_valid else 1)
    
    elif args.all:
        # Validate all artifacts
        base_dir = Path(args.dir)
        if not base_dir.exists():
            print(f"[ERROR] Directory not found: {base_dir}")
            sys.exit(2)
        
        is_valid = validate_all_artifacts(base_dir)
        sys.exit(0 if is_valid else 1)
    
    else:
        parser.print_help()
        sys.exit(2)


if __name__ == "__main__":
    main()
