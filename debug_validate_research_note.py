"""
Debug validation of Biomimetic Intelligence Research Notes
=========================================================

Checks research notes against governance framework for biomimetic claims.
"""

import json
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum


class ValidationStatus(Enum):
    APPROVED = "approved"
    REQUIRES_REVIEW = "requires_review"
    REJECTED = "rejected"


@dataclass
class ValidationResult:
    status: ValidationStatus
    issues: List[str]
    recommendations: List[str]
    governance_compliance: bool


class ResearchNoteValidator:
    """Validate biomimetic intelligence research notes."""
    
    def __init__(self):
        # Forbidden phrases that indicate overclaiming
        self.forbidden_phrases = [
            "proof of consciousness",
            "universal truth", 
            "fundamental law",
            "deeper order in the universe",
            "consciousness detected",
            "biomimetic intelligence achieved"
        ]
    
    def validate_note(self, note_content: str) -> ValidationResult:
        """Validate a research note against governance framework."""
        issues = []
        recommendations = []
        
        # Debug: Print what we're checking
        print("DEBUG: Checking for keywords:")
        print(f"'hypothesis' in content: {'hypothesis' in note_content.lower()}")
        print(f"'null model' in content: {'null model' in note_content.lower()}")
        print(f"'validation' in content: {'validation' in note_content.lower()}")
        print(f"'FORMAL HYPOTHESIS' in content: {'FORMAL HYPOTHESIS' in note_content}")
        print(f"'NULL MODELS' in content: {'NULL MODELS' in note_content}")
        
        # Check for forbidden phrases
        forbidden_found = []
        for phrase in self.forbidden_phrases:
            if phrase.lower() in note_content.lower():
                forbidden_found.append(phrase)
                issues.append(f"Forbidden phrase detected: '{phrase}'")
        
        # Check for required elements (case insensitive, flexible matching)
        content_lower = note_content.lower()
        
        # Check for hypothesis (looking for "hypothesis" keyword or "FORMAL HYPOTHESIS")
        has_hypothesis = "hypothesis" in content_lower or "FORMAL HYPOTHESIS" in note_content
        if not has_hypothesis:
            issues.append("Missing formal hypothesis statement")
            recommendations.append("Add explicit hypothesis with equation if applicable")
        
        # Check for null model (looking for "null model" or "null models" or "NULL MODELS")
        has_null_model = ("null model" in content_lower or "null models" in content_lower or 
                         "NULL MODELS" in note_content)
        if not has_null_model:
            issues.append("No null model or baseline comparison mentioned")
            recommendations.append("Add explicit null model or baseline for validation")
        
        # Check for validation criteria
        validation_present = any(term in content_lower for term in 
                                ["validation", "experiment", "test", "measure", "predict", 
                                 "VALIDATION CONSTRAINT", "EXPERIMENT DESIGN"])
        if not validation_present:
            issues.append("No explicit validation criteria or methods")
            recommendations.append("Add measurable validation criteria")
        
        # Check for overclaiming language
        overclaim_indicators = ["prove", "demonstrate", "confirm", "verify", "achieved"] 
        overclaims = [word for word in overclaim_indicators if word in content_lower]
        if overclaims:
            issues.append(f"Overclaiming language detected: {overclaims}")
            recommendations.append("Use hypothesis-level language instead of definitive claims")
        
        # Special checks for consciousness claims
        if "conscious" in content_lower and "operational definition" not in content_lower:
            issues.append("'Conscious' mentioned without operational definition")
            recommendations.append("Provide operational definition for consciousness-related terms")
        
        # Determine status
        governance_compliance = len(forbidden_found) == 0
        if forbidden_found:
            status = ValidationStatus.REJECTED
        elif issues and any("Forbidden phrase" in issue for issue in issues):
            status = ValidationStatus.REJECTED
        elif issues:
            status = ValidationStatus.REQUIRES_REVIEW
        else:
            status = ValidationStatus.APPROVED
        
        return ValidationResult(
            status=status,
            issues=issues,
            recommendations=recommendations,
            governance_compliance=governance_compliance
        )


def validate_phi_research_note():
    """Validate the specific phi ratio integration research note."""
    
    # Read the actual file
    with open('d:/AGI-GH-REPO-11326/AGI-model/final_phi_research_note.md', 'r', encoding='utf-8') as f:
        note_content = f.read()
    
    print("DEBUG: Content preview:")
    print(note_content[:200])
    
    validator = ResearchNoteValidator()
    result = validator.validate_note(note_content)
    
    print("BIOMIMETIC INTELLIGENCE RESEARCH NOTE VALIDATION")
    print("=" * 60)
    print(f"Status: {result.status.value.upper()}")
    print(f"Governance Compliance: {'✅ PASS' if result.governance_compliance else '❌ FAIL'}")
    
    if result.issues:
        print("\n🔍 ISSUES DETECTED:")
        for issue in result.issues:
            print(f"  • {issue}")
    
    if result.recommendations:
        print("\n💡 RECOMMENDATIONS:")
        for rec in result.recommendations:
            print(f"  • {rec}")
    
    return result


if __name__ == "__main__":
    validate_phi_research_note()