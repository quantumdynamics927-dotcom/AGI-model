#!/usr/bin/env python3
"""
Deploy Scientific Python Ecosystem to Hugging Face Spaces

This script creates a new Hugging Face Space and uploads the Gradio app.

Prerequisites:
1. Install huggingface_hub: pip install huggingface_hub
2. Login: huggingface-cli login
3. Set HF_TOKEN environment variable or use --token argument

Usage:
    python deploy_to_hf_space.py --space-name "scientific-python-quantum-agi"
"""

import os
import argparse
from pathlib import Path

try:
    from huggingface_hub import HfApi, create_repo
    HF_HUB_AVAILABLE = True
except ImportError:
    HF_HUB_AVAILABLE = False
    print("huggingface_hub not installed. Install with: pip install huggingface_hub")


def deploy_space(space_name: str, token: str = None, private: bool = False):
    """
    Deploy the Gradio app to Hugging Face Spaces.
    
    Args:
        space_name: Name for the Space (e.g., "scientific-python-quantum-agi")
        token: Hugging Face API token (optional if already logged in)
        private: Whether to make the Space private
    """
    if not HF_HUB_AVAILABLE:
        print("Error: huggingface_hub is required. Install with: pip install huggingface_hub")
        return False
    
    # Initialize API
    api = HfApi(token=token)
    
    # Get username
    user_info = api.whoami()
    username = user_info['name']
    repo_id = f"{username}/{space_name}"
    
    print(f"Creating Space: {repo_id}")
    
    # Create the Space repository
    try:
        create_repo(
            repo_id=repo_id,
            repo_type="space",
            space_sdk="gradio",
            private=private,
            exist_ok=True
        )
        print(f"Space created: https://huggingface.co/{repo_id}")
    except Exception as e:
        print(f"Error creating Space: {e}")
        return False
    
    # Get the directory containing this script
    space_dir = Path(__file__).parent
    
    # Files to upload
    files_to_upload = [
        ("app.py", "app.py"),
        ("requirements.txt", "requirements.txt"),
        ("README.md", "README.md"),
    ]
    
    # Upload files
    for local_file, remote_file in files_to_upload:
        local_path = space_dir / local_file
        if local_path.exists():
            print(f"Uploading {local_file}...")
            api.upload_file(
                path_or_fileobj=str(local_path),
                path_in_repo=remote_file,
                repo_id=repo_id,
                repo_type="space"
            )
        else:
            print(f"Warning: {local_file} not found, skipping...")
    
    print(f"\nDeployment complete!")
    print(f"Space URL: https://huggingface.co/{repo_id}")
    print(f"App URL: https://{username}-{space_name}.hf.space")
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Deploy Scientific Python Ecosystem to Hugging Face Spaces"
    )
    parser.add_argument(
        "--space-name",
        type=str,
        default="scientific-python-quantum-agi",
        help="Name for the Hugging Face Space"
    )
    parser.add_argument(
        "--token",
        type=str,
        default=None,
        help="Hugging Face API token (optional if already logged in)"
    )
    parser.add_argument(
        "--private",
        action="store_true",
        help="Make the Space private"
    )
    
    args = parser.parse_args()
    
    # Check for token in environment
    token = args.token or os.environ.get("HF_TOKEN")
    
    deploy_space(
        space_name=args.space_name,
        token=token,
        private=args.private
    )


if __name__ == "__main__":
    main()