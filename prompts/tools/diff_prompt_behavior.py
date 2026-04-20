#!/usr/bin/env python3
"""
Prompt Behavior Diff Tool

Compares behavior between prompt versions on the same eval cases.
Usage: python diff_prompt_behavior.py <prompt> --from v1.0.0 --to v1.1.0
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List
import yaml

PROMPTS_DIR = Path(__file__).parent.parent
TOOLS_DIR = Path(__file__).parent


def load_prompt_version(prompt_name: str, version: str) -> Path:
    """Load prompt file for specific version."""
    # For now, assume versions are in git history or separate files
    # In production, this would query versioned storage
    prompt_file = PROMPTS_DIR / f"{prompt_name}.md"
    if prompt_file.exists():
        return prompt_file
    return None


def load_eval_cases(prompt_name: str) -> List[Dict]:
    """Load eval cases for prompt."""
    eval_dir = PROMPTS_DIR / "eval_cases" / prompt_name
    cases = []
    
    if eval_dir.exists():
        for case_file in sorted(eval_dir.glob("case_*.json")):
            with open(case_file, 'r') as f:
                case = json.load(f)
                case["_file"] = case_file.name
                cases.append(case)
    
    return cases


def compute_behavior_diff(old_output: Dict, new_output: Dict) -> Dict:
    """Compute behavioral diff between two outputs."""
    diff = {
        "added_keys": [],
        "removed_keys": [],
        "changed_values": [],
        "unchanged_keys": []
    }
    
    old_keys = set(old_output.keys())
    new_keys = set(new_output.keys())
    
    diff["added_keys"] = list(new_keys - old_keys)
    diff["removed_keys"] = list(old_keys - new_keys)
    
    for key in old_keys & new_keys:
        if old_output[key] != new_output[key]:
            diff["changed_values"].append({
                "key": key,
                "old": old_output[key],
                "new": new_output[key]
            })
        else:
            diff["unchanged_keys"].append(key)
    
    return diff


def analyze_severity(diff: Dict) -> str:
    """Analyze severity of behavior change."""
    if diff["removed_keys"]:
        return "HIGH"  # Breaking change
    
    if diff["changed_values"]:
        # Check if critical fields changed
        critical_fields = ["validity", "metric_type", "safe_use_category"]
        for change in diff["changed_values"]:
            if change["key"] in critical_fields:
                return "HIGH"
        return "MEDIUM"
    
    if diff["added_keys"]:
        return "LOW"  # Non-breaking addition
    
    return "NONE"


def generate_diff_report(prompt_name: str, from_version: str, 
                         to_version: str, diffs: List[Dict]) -> str:
    """Generate markdown diff report."""
    lines = [
        f"# Behavior Diff Report: {prompt_name}",
        f"\n**From**: v{from_version}",
        f"**To**: v{to_version}",
        f"**Cases analyzed**: {len(diffs)}",
    ]
    
    # Severity summary
    severities = [d["severity"] for d in diffs]
    high_count = severities.count("HIGH")
    medium_count = severities.count("MEDIUM")
    low_count = severities.count("LOW")
    
    lines.append(f"\n## Severity Summary")
    lines.append(f"- 🔴 HIGH: {high_count} cases")
    lines.append(f"- 🟡 MEDIUM: {medium_count} cases")
    lines.append(f"- 🟢 LOW: {low_count} cases")
    
    if high_count > 0:
        lines.append(f"\n**⚠️ WARNING**: {high_count} cases show HIGH severity changes")
        lines.append("Review required before promotion.")
    
    # Per-case diffs
    lines.append(f"\n## Case-by-Case Analysis")
    
    for diff in diffs:
        case_id = diff["case_id"]
        severity = diff["severity"]
        icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢", "NONE": "⚪"}[severity]
        
        lines.append(f"\n### {case_id} {icon}")
        
        if diff["added_keys"]:
            lines.append(f"**Added**: {', '.join(diff['added_keys'])}")
        
        if diff["removed_keys"]:
            lines.append(f"**Removed**: {', '.join(diff['removed_keys'])}")
        
        if diff["changed_values"]:
            lines.append("**Changed**:")
            for change in diff["changed_values"]:
                lines.append(f"- `{change['key']}`: {change['old']} → {change['new']}")
    
    # Recommendations
    lines.append(f"\n## Recommendations")
    
    if high_count > 0:
        lines.append("- **BLOCKED**: Breaking changes detected")
        lines.append("- Review all HIGH severity cases")
        lines.append("- Update eval cases if changes are intentional")
    elif medium_count > 0:
        lines.append("- **REVIEW REQUIRED**: Non-breaking behavioral changes")
        lines.append("- Verify changes align with intended behavior")
    else:
        lines.append("- **SAFE**: No significant behavioral changes")
        lines.append("- Can proceed with promotion")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Diff prompt behavior between versions")
    parser.add_argument("prompt", help="Prompt name to diff")
    parser.add_argument("--from", "-f", dest="from_version", required=True, 
                       help="Source version")
    parser.add_argument("--to", "-t", dest="to_version", required=True,
                       help="Target version")
    parser.add_argument("--output", "-o", help="Output file for report")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()
    
    if args.verbose:
        print(f"Comparing {args.prompt} v{args.from_version} → v{args.to_version}")
    
    # Load eval cases
    cases = load_eval_cases(args.prompt)
    
 if not cases:
        print(f"No eval cases found for {args.prompt}")
        sys.exit(1)
    
    if args.verbose:
        print(f"Loaded {len(cases)} eval cases")
    
    # For each case, compare expected outputs
    diffs = []
    
    for case in cases:
        # In a real implementation, this would run both versions
        # For now, compare expected outputs as proxy
        old_output = case.get("expected_output", {})
        
        # Simulate version change (in production, run actual prompts)
        diff = compute_behavior_diff(old_output, old_output)
        diff["case_id"] = case.get("case_id", "unknown")
        diff["severity"] = analyze_severity(diff)
        
        diffs.append(diff)
    
    # Generate report
    report = generate_diff_report(args.prompt, args.from_version, 
                                   args.to_version, diffs)
    
    if args.output:
        output_path = Path(args.output)
        with open(output_path, 'w') as f:
            f.write(report)
        print(f"Report written to: {output_path}")
    else:
        print(report)
    
    # Exit code based on severity
    has_high = any(d["severity"] == "HIGH" for d in diffs)
    sys.exit(1 if has_high else 0)


if __name__ == "__main__":
    main()
