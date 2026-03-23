"""Init script to create a professional `tmt-os-labs` workspace.

Usage examples:
    python init_tmt_os_labs.py --root "E:\\tmt-os-labs"    # attempt to create at E:\tmt-os-labs
    python init_tmt_os_labs.py --root ".\tmt-os-labs"     # create relative to current directory
    python init_tmt_os_labs.py --dry-run                    # show actions
"""

import argparse
import os
import sys
from pathlib import Path

STRUCTURE = {
    "client_alpha_quantum": ["data", "notebooks", "delivery", "logs"],
    "client_beta_agi": ["data", "notebooks", "delivery", "logs"],
    "tools": []
}

README_TEMPLATE = """# {folder}

Professional workspace for {folder}.

Follow the TMT-OS Labs Delivery Protocol in parent README.
"""

GITKEEP = """# Keep this folder tracked by git
"""


def create_structure(base: Path, dry_run: bool = False):
    actions = []
    actions.append(f"Create root: {base}")

    for folder, subs in STRUCTURE.items():
        folder_path = base / folder
        actions.append(f"Create folder: {folder_path}")
        for sub in subs:
            sub_path = folder_path / sub
            actions.append(f"Create subfolder: {sub_path}")

    if dry_run:
        print("[DRY RUN] The following actions would be performed:")
        print('\n'.join(actions))
        return

    base.mkdir(parents=True, exist_ok=True)

    # Create folder structure and README/.gitkeep
    (base / "README.md").write_text("# TMT-OS Labs\n\nProfessional client workspace template.\n")

    for folder, subs in STRUCTURE.items():
        folder_path = base / folder
        folder_path.mkdir(exist_ok=True)
        (folder_path / "README.md").write_text(README_TEMPLATE.format(folder=folder.replace('_', ' ').title()))
        for sub in subs:
            sub_path = folder_path / sub
            sub_path.mkdir(exist_ok=True)
            (sub_path / ".gitkeep").write_text("")

    print("[OK] Lab scaffold created at:", base)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize TMT-OS Labs scaffold")
    parser.add_argument("--root", default=r"E:\\tmt-os-labs", help="Root path to create the lab (default: E:\\tmt-os-labs)")
    parser.add_argument("--dry-run", action="store_true", help="Show actions without creating files")
    parser.add_argument("--force-local", action="store_true", help="If E: is inaccessible, force creation in current working directory")
    args = parser.parse_args()

    target = Path(args.root)

    # Try to create at requested path; if permission or drive not present, fall back
    try:
        # Quick check: resolve parent exists or can be created
        if not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
        create_structure(target, dry_run=args.dry_run)
    except PermissionError:
        print("[WARN] Permission denied when creating at", target)
        if args.force_local:
            alt = Path.cwd() / "tmt-os-labs"
            print(f"Creating locally at {alt}")
            create_structure(alt, dry_run=args.dry_run)
        else:
            print("Run this script with --force-local to create inside the current working directory, or run with elevated privileges to create at the requested root.")
            sys.exit(1)
    except Exception as e:
        print("[ERROR]", e)
        sys.exit(1)
