"""Setup script to prepare TMT-OS-Labs-Portal locally.

- Creates Windows junctions to your core repositories and research workspace.
- Safe: will not overwrite existing paths; will print instructions when admin rights are required.
"""
import os
import subprocess
from pathlib import Path

LABS_ROOT = r"E:\AGI model\tmt-os-labs"
CORE_ROOT = r"E:\tmt-os"
PROJECT_ROOT = Path(__file__).resolve().parent


def create_junction(link_name: str, target: str):
    dest = PROJECT_ROOT / link_name
    if dest.exists():
        print(f"[*] {link_name} already exists. Skipping.")
        return
    print(f"[*] Creating Junction: {link_name} -> {target}")
    cmd = f'mklink /J "{dest}" "{target}"'
    try:
        subprocess.check_call(cmd, shell=True)
    except subprocess.CalledProcessError:
        print("[WARN] Junction creation failed. You may need elevated permissions.")
        print(f"Run as Administrator and re-run: {cmd}")


def rename_repo_if_found(old_name: str, new_name: str):
    cwd = Path.cwd()
    old = cwd / old_name
    new = cwd / new_name
    if old.exists() and not new.exists():
        print(f"[*] Renaming {old_name} -> {new_name}")
        old.rename(new)
    elif new.exists():
        print(f"[*] {new_name} already exists. Skipping rename.")
    else:
        print(f"[*] {old_name} not found in {cwd}. Skipping rename.")


def initialize_portal():
    print("Initializing TMT-OS Labs Portal at:", PROJECT_ROOT)
    # Optionally rename FlowGenio-Landing if it's present
    rename_repo_if_found('FlowGenio-Landing', 'TMT-OS-Labs-Portal')

    create_junction('src/core', CORE_ROOT)
    create_junction('src/agi_model', r"E:\AGI model")
    create_junction('research_workspace', LABS_ROOT)

    print("\n[OK] Portal connected to E: Drive.")
    print("Next: Install dependencies: pip install -r requirements_tmt.txt")


if __name__ == "__main__":
    initialize_portal()
