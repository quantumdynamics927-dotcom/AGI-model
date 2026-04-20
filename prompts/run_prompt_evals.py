#!/usr/bin/env python3
"""
Prompt Evaluation Runner

Runs eval cases against prompts and generates pass/fail reports.
Usage: python run_prompt_evals.py [--prompt <name>] [--verbose]
"""

import json
import os
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Tuple
import yaml

PROMPTS_DIR = Path(__file__).parent
EVAL_CASES_DIR = PROMPTS_DIR / "eval_cases"
REPORTS_DIR = PROMPTS_DIR / "reports"


def load_manifest() -> Dict:
    """Load the prompts manifest."""
    manifest_path = PROMPTS_DIR / "prompts_manifest.yaml"
    with open(manifest_path, 'r') as f:
        return yaml.safe_load(f)


def load_eval_case(case_path: Path) -> Dict:
    """Load a single eval case."""
    with open(case_path, 'r') as f:
        return json.load(f)


def run_eval_case(prompt_name: str, case: Dict, verbose: bool = False) -> Tuple[bool, str]:
    """
    Run a single eval case.
    
    Returns (passed, message).
    For now, this validates structure and required fields.
    Full LLM-based evaluation can be added later.
    """
    case_name = case.get("name", "unknown")
    
    # Check required fields
    required = ["name", "description", "input", "expected_output"]
    missing = [f for f in required if f not in case]
    if missing:
        return False, f"Missing fields: {missing}"
    
    # Validate expected output structure matches prompt type
    expected = case.get("expected_output", {})
    
    if verbose:
        print(f"  ✓ Case '{case_name}' structure valid")
    
    return True, "Structure valid"


def run_prompt_evals(prompt_name: str = None, verbose: bool = False) -> Dict:
    """Run all eval cases for specified prompt(s)."""
    manifest = load_manifest()
    results = {
        "timestamp": "2026-04-20T00:00:00Z",
        "summary": {"total": 0, "passed": 0, "failed": 0},
        "prompts": {}
    }
    
    prompts_to_run = [p for p in manifest["prompts"] if prompt_name is None or p["name"] == prompt_name]
    
    for prompt in prompts_to_run:
        name = prompt["name"]
        risk_level = prompt.get("risk_level", "unknown")
        status = prompt.get("status", "unknown")
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"Prompt: {name} (v{prompt['version']}, {risk_level} risk, {status})")
            print(f"{'='*60}")
        
        prompt_results = {
            "version": prompt["version"],
            "risk_level": risk_level,
            "status": status,
            "cases": [],
            "passed": 0,
            "failed": 0
        }
        
        # Find eval cases for this prompt
        eval_dir = EVAL_CASES_DIR / name.replace('_', '')
        if not eval_dir.exists():
            eval_dir = EVAL_CASES_DIR / name
        
        if eval_dir.exists():
            case_files = sorted(eval_dir.glob("case_*.json"))
            
            for case_file in case_files:
                case = load_eval_case(case_file)
                passed, message = run_eval_case(name, case, verbose)
                
                case_result = {
                    "file": case_file.name,
                    "name": case.get("name", "unknown"),
                    "passed": passed,
                    "message": message
                }
                
                prompt_results["cases"].append(case_result)
                if passed:
                    prompt_results["passed"] += 1
                else:
                    prompt_results["failed"] += 1
                
                if verbose:
                    status_icon = "✓" if passed else "✗"
                    print(f"  [{status_icon}] {case.get('name', 'unknown')}: {message}")
        
        results["prompts"][name] = prompt_results
        results["summary"]["total"] += prompt_results["passed"] + prompt_results["failed"]
        results["summary"]["passed"] += prompt_results["passed"]
        results["summary"]["failed"] += prompt_results["failed"]
    
    return results


def generate_report(results: Dict) -> str:
    """Generate a markdown report."""
    lines = [
        "# Prompt Evaluation Report",
        f"\n**Generated**: {results['timestamp']}",
        f"\n## Summary",
        f"- Total cases: {results['summary']['total']}",
        f"- Passed: {results['summary']['passed']}",
        f"- Failed: {results['summary']['failed']}",
        f"- Status: {'✓ PASS' if results['summary']['failed'] == 0 else '✗ FAIL'}",
        "\n## Results by Prompt",
    ]
    
    for name, prompt_results in results["prompts"].items():
        total = prompt_results["passed"] + prompt_results["failed"]
        status = "✓" if prompt_results["failed"] == 0 else "✗"
        lines.append(f"\n### {name} (v{prompt_results['version']}) {status}")
        lines.append(f"- Risk: {prompt_results['risk_level']}")
        lines.append(f"- Status: {prompt_results['status']}")
        lines.append(f"- Cases: {prompt_results['passed']}/{total} passed")
        
        if prompt_results["cases"]:
            lines.append("\n| Case | Result | Message |")
            lines.append("|------|--------|---------|")
            for case in prompt_results["cases"]:
                icon = "✓" if case["passed"] else "✗"
                lines.append(f"| {case['name']} | {icon} | {case['message']} |")
    
    lines.append("\n---")
    lines.append("\n**Note**: This is a structural validation. Full LLM-based evaluation requires model integration.")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Run prompt evaluations")
    parser.add_argument("--prompt", help="Run specific prompt only")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--output", "-o", help="Output file (default: print to stdout)")
    args = parser.parse_args()
    
    if args.verbose:
        print("QAGI Prompt Evaluation Runner")
        print(f"Prompts dir: {PROMPTS_DIR}")
        print(f"Eval cases dir: {EVAL_CASES_DIR}")
    
    results = run_prompt_evals(args.prompt, args.verbose)
    report = generate_report(results)
    
    if args.output:
        REPORTS_DIR.mkdir(exist_ok=True)
        output_path = REPORTS_DIR / args.output
        with open(output_path, 'w') as f:
            f.write(report)
        print(f"Report written to: {output_path}")
    else:
        print(report)
    
    # Exit with error code if any failed
    sys.exit(0 if results["summary"]["failed"] == 0 else 1)


if __name__ == "__main__":
    main()
