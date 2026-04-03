#!/usr/bin/env python3
"""
Run Molecular VQE in Docker Container
======================================

This script runs the molecular VQE tests inside a Docker container
with PySCF properly installed.

Usage:
    # Build and run tests
    docker-compose -f docker-compose.pyscf.yml up -d
    docker-compose -f docker-compose.pyscf.yml exec agi-pyscf python run_docker_vqe.py
    
    # Or run directly
    python run_docker_vqe.py

Author: AGI-model Quantum Computing Team
Date: April 2, 2026
"""

import sys
import subprocess
from pathlib import Path


def check_docker():
    """Check if Docker is available."""
    try:
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print(f"✅ Docker available: {result.stdout.strip()}")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    print("❌ Docker not available. Please install Docker Desktop.")
    return False


def build_image():
    """Build the Docker image."""
    print("\n📦 Building Docker image...")
    result = subprocess.run(
        ["docker", "build", "-f", "Dockerfile.pyscf", "-t", "agi-pyscf", "."],
        cwd=Path(__file__).parent
    )
    return result.returncode == 0


def run_tests():
    """Run the molecular VQE tests in Docker."""
    print("\n🧪 Running molecular VQE tests...")
    
    # Run test script inside container
    result = subprocess.run([
        "docker", "run", "--rm",
        "-v", f"{Path(__file__).parent}:/workspace",
        "-w", "/workspace",
        "agi-pyscf",
        "python", "test_dna_molecular_vqe.py"
    ])
    
    return result.returncode == 0


def run_interactive():
    """Start an interactive container."""
    print("\n🖥️ Starting interactive container...")
    print("Run 'python test_dna_molecular_vqe.py' to execute tests.")
    print("Run 'exit' to leave the container.\n")
    
    subprocess.run([
        "docker", "run", "--rm", "-it",
        "-v", f"{Path(__file__).parent}:/workspace",
        "-w", "/workspace",
        "agi-pyscf",
        "/bin/bash"
    ])


def main():
    """Main entry point."""
    print("=" * 80)
    print("AGI-model PySCF Docker Environment")
    print("=" * 80)
    
    if not check_docker():
        print("\nPlease install Docker Desktop from:")
        print("https://www.docker.com/products/docker-desktop")
        return 1
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "build":
            success = build_image()
            return 0 if success else 1
        elif sys.argv[1] == "test":
            success = run_tests()
            return 0 if success else 1
        elif sys.argv[1] == "shell":
            run_interactive()
            return 0
    
    # Default: build and run tests
    if not build_image():
        print("❌ Failed to build Docker image")
        return 1
    
    if not run_tests():
        print("❌ Tests failed")
        return 1
    
    print("\n✅ All tests passed!")
    return 0


if __name__ == "__main__":
    sys.exit(main())