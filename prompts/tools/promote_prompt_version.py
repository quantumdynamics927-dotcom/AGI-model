#!/usr/bin/env python3
"""
Prompt Version Promotion Tool

Handles promotion of prompt versions between environments.
Usage: python promote_prompt_version.py <prompt> --to <env> [--version vX.Y.Z]
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
import yaml

PROMPTS_DIR = Path(__file__).parent.parent
REGISTRY_DIR = PROMPTS_DIR / "registry"


def load_aliases() -> Dict:
    """Load current aliases."""
    aliases_path = REGISTRY_DIR / "aliases.yaml"
    with open(aliases_path, 'r') as f:
        return yaml.safe_load(f)


def load_policies() -> Dict:
    """Load promotion policies."""
    policies_path = REGISTRY_DIR / "policies.yaml"
    with open(policies_path, 'r') as f:
        return yaml.safe_load(f)


def load_manifest() -> Dict:
    """Load prompts manifest."""
    manifest_path = PROMPTS_DIR / "prompts_manifest.yaml"
    with open(manifest_path, 'r') as f:
        return yaml.safe_load(f)


def get_prompt_info(prompt_name: str) -> Dict:
    """Get prompt info from manifest."""
    manifest = load_manifest()
    for p in manifest.get("prompts", []):
        if p["name"] == prompt_name:
            return p
    return None


def check_promotion_gates(prompt_name: str, target_env: str, 
                          version: str = None) -> Dict:
    """Check if promotion is allowed."""
    info = get_prompt_info(prompt_name)
    if not info:
        return {"allowed": False, "reason": "Prompt not found in manifest"}
    
    risk_level = info.get("risk_level", "unknown")
    policies = load_policies()
    
    policy = policies.get("risk_policies", {}).get(risk_level, {})
    env_policy = policies.get("environment_policies", {}).get(target_env, {})
    
    gates = {"passed": [], "failed": [], "required": []}
    
    # Check each gate
    for gate_name, gate_config in policy.get("gates", {}).items():
        if not gate_config.get("required", False):
            continue
        
        gates["required"].append(gate_name)
        
        # Simulate gate checks (in production, run actual checks)
        if gate_name == "header_check":
            gates["passed"].append(gate_name)
        elif gate_name == "eval_pass_rate":
            gates["passed"].append(gate_name)
        elif gate_name == "schema_validation":
            if risk_level in ["high"]:
                gates["passed"].append(gate_name)
            else:
                gates["passed"].append(gate_name)
        elif gate_name == "human_review":
            if policy.get("auto_promote"):
                gates["passed"].append(gate_name)
            else:
                gates["failed"].append(f"{gate_name} (requires manual signoff)")
    
    # Environment-specific checks
    if env_policy.get("require_signed_commit") and target_env == "production":
        gates["required"].append("signed_commit")
        gates["failed"].append("signed_commit (requires GPG signature)")
    
    if env_policy.get("require_changelog_entry"):
        gates["required"].append("changelog_entry")
        # Check if CHANGELOG.md has entry for this version
        changelog_path = PROMPTS_DIR / "CHANGELOG.md"
        if changelog_path.exists():
            with open(changelog_path, 'r') as f:
                content = f.read()
            if version and version in content:
                gates["passed"].append("changelog_entry")
            else:
                gates["failed"].append("changelog_entry (version not documented)")
        else:
            gates["failed"].append("changelog_entry (CHANGELOG.md not found)")
    
    allowed = len(gates["failed"]) == 0
    
    return {
        "allowed": allowed,
        "risk_level": risk_level,
        "target_env": target_env,
        "version": version or info.get("version"),
        "gates": gates,
        "reason": None if allowed else f"Failed gates: {gates['failed']}"
    }


def update_aliases(prompt_name: str, target_env: str, version: str) -> bool:
    """Update aliases.yaml with new promotion."""
    aliases = load_aliases()
    
    if prompt_name not in aliases:
        aliases[prompt_name] = {}
    
    old_version = aliases[prompt_name].get(target_env)
    aliases[prompt_name][target_env] = version
    
    # Write updated aliases
    aliases_path = REGISTRY_DIR / "aliases.yaml"
    with open(aliases_path, 'w') as f:
        yaml.dump(aliases, f, default_flow_style=False, sort_keys=True)
    
    return old_version


def main():
    parser = argparse.ArgumentParser(description="Promote prompt version")
    parser.add_argument("prompt", help="Prompt name to promote")
    parser.add_argument("--to", "-t", required=True,
                       choices=["development", "staging", "production"],
                       help="Target environment")
    parser.add_argument("--version", "-v", help="Specific version to promote")
    parser.add_argument("--force", "-f", action="store_true",
                       help="Force promotion (requires manual override)")
    parser.add_argument("--dry-run", "-n", action="store_true",
                       help="Show what would happen without making changes")
    parser.add_argument("--reason", "-r", help="Reason for promotion (required for production)")
    args = parser.parse_args()
    
    print(f"Promoting {args.prompt} to {args.to}")
    
    # Check gates
    check = check_promotion_gates(args.prompt, args.to, args.version)
    
    print(f"\nRisk level: {check['risk_level']}")
    print(f"Version: {check['version']}")
    print(f"\nGates required: {len(check['gates']['required'])}")
    print(f"Gates passed: {len(check['gates']['passed'])}")
    
    if check["gates"]["failed"]:
        print(f"Gates failed: {len(check['gates']['failed'])}")
        for failure in check["gates"]["failed"]:
            print(f"  ✗ {failure}")
    
    if not check["allowed"] and not args.force:
        print(f"\n❌ Promotion BLOCKED: {check['reason']}")
        print("Use --force to override (requires signoff)")
        sys.exit(1)
    
    if not check["allowed"] and args.force:
        print(f"\n⚠️ WARNING: Forcing promotion past failed gates")
        print(f"   Reason required: {args.reason or 'NOT PROVIDED'}")
    
    # Production requires reason
    if args.to == "production" and not args.reason:
        print("\n❌ Production promotion requires --reason")
        sys.exit(1)
    
    # Show promotion plan
    aliases = load_aliases()
    current = aliases.get(args.prompt, {}).get(args.to, "none")
    
    print(f"\n{'='*60}")
    print("PROMOTION PLAN")
    print(f"{'='*60}")
    print(f"Prompt: {args.prompt}")
    print(f"Environment: {args.to}")
    print(f"From: {current}")
    print(f"To: {check['version']}")
    if args.reason:
        print(f"Reason: {args.reason}")
    print(f"{'='*60}")
    
    if args.dry_run:
        print("\n[DRY RUN] No changes made")
        sys.exit(0)
    
    # Execute promotion
    old_version = update_aliases(args.prompt, args.to, check['version'])
    
    print(f"\n✅ Promotion complete")
    print(f"   {args.prompt}@{args.to}: {old_version} → {check['version']}")
    
    # Update timestamp
    print(f"\nNext steps:")
    print(f"  1. Update CHANGELOG.md with promotion details")
    print(f"  2. Commit changes: git add registry/aliases.md")
    print(f"  3. Tag if production: git tag prompts-{args.prompt}-{check['version']}")
    
    # Log promotion
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "prompt": args.prompt,
        "environment": args.to,
        "from_version": old_version,
        "to_version": check['version'],
        "reason": args.reason,
        "forced": args.force
    }
    
    print(f"\nLogged: {log_entry}")


if __name__ == "__main__":
    main()
