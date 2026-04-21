#!/usr/bin/env python3
"""
Prompt Header Checker

Validates YAML frontmatter in prompt files.
Usage: python check_prompt_headers.py [--fix] [--verbose]
"""

import argparse
import sys
from pathlib import Path
import yaml
import re

PROMPTS_DIR = Path(__file__).parent.parent
REQUIRED_FIELDS = [
    "name",
    "version",
    "owner",
    "purpose",
    "inputs",
    "expected_output",
    "risk_level",
    "last_validated_on"
]
OPTIONAL_FIELDS = ["status", "sha256"]
VALID_RISK_LEVELS = ["low", "medium", "high"]
VALID_STATUSES = ["draft", "validated", "deprecated"]


def extract_frontmatter(content: str) -> tuple:
    """Extract YAML frontmatter from markdown content."""
    pattern = r'^---\s*\n(.*?)\n---\s*\n'
    match = re.match(pattern, content, re.DOTALL)
    if match:
        return match.group(1), content[match.end():]
    return None, content


def check_prompt_file(file_path: Path, fix: bool = False) -> dict:
    """Check a single prompt file."""
    result = {
        "file": file_path.name,
        "valid": True,
        "errors": [],
        "warnings": []
    }
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract frontmatter
    frontmatter, body = extract_frontmatter(content)
    
    if frontmatter is None:
        result["valid"] = False
        result["errors"].append("Missing YAML frontmatter")
        return result
    
    # Parse YAML
    try:
        data = yaml.safe_load(frontmatter)
    except yaml.YAMLError as e:
        result["valid"] = False
        result["errors"].append(f"Invalid YAML: {e}")
        return result
    
    if not isinstance(data, dict):
        result["valid"] = False
        result["errors"].append("Frontmatter is not a YAML mapping")
        return result
    
    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in data:
            result["valid"] = False
            result["errors"].append(f"Missing required field: {field}")
    
    # Validate risk_level
    if "risk_level" in data:
        if data["risk_level"] not in VALID_RISK_LEVELS:
            result["valid"] = False
            result["errors"].append(f"Invalid risk_level: {data['risk_level']}")
    
    # Validate status
    if "status" in data:
        if data["status"] not in VALID_STATUSES:
            result["valid"] = False
            result["errors"].append(f"Invalid status: {data['status']}")
    
    # Check version format
    if "version" in data:
        version = data["version"]
        if not re.match(r'^v?\d+\.\d+\.\d+(-\w+)?$', str(version)):
            result["warnings"].append(f"Non-standard version format: {version}")
    
    # Check that name matches filename
    if "name" in data:
        expected_name = file_path.stem
        if data["name"] != expected_name:
            result["warnings"].append(f"Name mismatch: file='{expected_name}', header='{data['name']}'")
    
    return result


def main():
    parser = argparse.ArgumentParser(description="Check prompt file headers")
    parser.add_argument("--fix", action="store_true", help="Attempt to fix issues")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()
    
    # Find all prompt files
    prompt_files = list(PROMPTS_DIR.glob("*.md"))
    prompt_files = [f for f in prompt_files if f.name not in ["README.md", "CHANGELOG.md"]]
    
    if args.verbose:
        print(f"Checking {len(prompt_files)} prompt files...")
    
    results = []
    all_valid = True
    
    for file_path in sorted(prompt_files):
        result = check_prompt_file(file_path, args.fix)
        results.append(result)
        
        if not result["valid"]:
            all_valid = False
        
        if args.verbose or not result["valid"]:
            status = "✓" if result["valid"] else "✗"
            print(f"[{status}] {result['file']}")
            
            for error in result["errors"]:
                print(f"  ERROR: {error}")
            for warning in result["warnings"]:
                print(f"  WARNING: {warning}")
    
    # Summary
    valid_count = sum(1 for r in results if r["valid"])
    print(f"\n{valid_count}/{len(results)} files valid")
    
    sys.exit(0 if all_valid else 1)


if __name__ == "__main__":
    main()
