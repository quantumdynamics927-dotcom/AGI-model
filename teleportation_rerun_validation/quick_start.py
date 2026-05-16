#!/usr/bin/env python3
"""
Quick Start: IBM Quantum Teleportation Rerun Validation

This script provides a streamlined interface for running the validation workflow.
It handles connection setup, job submission, monitoring, and result analysis.

Usage:
    python quick_start.py                    # Check reference jobs only
    python quick_start.py --run              # Run full validation
    python quick_start.py --run --jobs 2     # Run with 2 jobs (minimum)
    python quick_start.py --run --backend ibm_fez  # Use specific backend
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from teleportation_rerun_validator import (
        TeleportationRerunValidator,
        REFERENCE_JOB_IDS,
        CLASSICAL_FIDELITY_THRESHOLD
    )
    VALIDATOR_AVAILABLE = True
except ImportError:
    VALIDATOR_AVAILABLE = False
    print("Warning: Full validator not available. Install requirements with:")
    print("  pip install -r requirements.txt")


def check_environment():
    """Check if the environment is properly set up."""
    print("\n🔍 Environment Check")
    print("=" * 60)
    
    # Check Python version
    print(f"Python: {sys.version}")
    
    # Check Qiskit
    try:
        import qiskit
        print(f"✅ Qiskit: {qiskit.__version__}")
    except ImportError:
        print("❌ Qiskit: Not installed")
        return False
    
    # Check Qiskit IBM Runtime
    try:
        import qiskit_ibm_runtime
        print(f"✅ Qiskit IBM Runtime: {qiskit_ibm_runtime.__version__}")
    except ImportError:
        print("❌ Qiskit IBM Runtime: Not installed")
        return False
    
    # Check NumPy
    try:
        import numpy
        print(f"✅ NumPy: {numpy.__version__}")
    except ImportError:
        print("❌ NumPy: Not installed")
        return False
    
    # Check if IBM Quantum credentials are saved
    try:
        from qiskit_ibm_runtime import QiskitRuntimeService
        service = QiskitRuntimeService()
        print(f"✅ IBM Quantum credentials: Saved")
        print(f"   Channel: {service.channel}")
    except Exception as e:
        print(f"⚠️  IBM Quantum credentials: Not saved or invalid")
        print(f"   Save with: QiskitRuntimeService.save_account(token='YOUR_TOKEN')")
        return False
    
    return True


def check_reference_jobs():
    """Check reference job metadata without running new jobs."""
    print("\n📊 Reference Job Check")
    print("=" * 60)
    
    try:
        from check_reference_jobs import connect_to_ibm, retrieve_job_metadata
    except ImportError:
        print("❌ Cannot import check_reference_jobs module")
        return
    
    try:
        service = connect_to_ibm()
        print("✅ Connected to IBM Quantum")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return
    
    print(f"\nReference Job IDs:")
    for job_id in REFERENCE_JOB_IDS:
        print(f"  - {job_id}")
    
    print(f"\nRetrieving metadata...")
    
    results = {}
    for job_id in REFERENCE_JOB_IDS:
        print(f"\n  Checking {job_id}...")
        metadata = retrieve_job_metadata(service, job_id)
        results[job_id] = metadata
        
        status = metadata.get("status", "UNKNOWN")
        backend = metadata.get("backend_name", "N/A")
        success = "✅" if metadata.get("retrieval_success", False) else "❌"
        
        print(f"    {success} Status: {status}, Backend: {backend}")
    
    # Save results
    output_path = Path("reference_jobs_metadata.json")
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n✅ Metadata saved to: {output_path}")
    
    # Summary
    available = sum(1 for m in results.values() if m.get("retrieval_success", False))
    print(f"\nAvailable: {available}/{len(REFERENCE_JOB_IDS)} reference jobs")


def run_validation(num_jobs: int = 4, shots: int = 1024, backend: Optional[str] = None):
    """Run the full validation workflow."""
    print("\n🚀 Running Validation")
    print("=" * 60)
    
    if not VALIDATOR_AVAILABLE:
        print("❌ Validator not available. Install requirements first.")
        return
    
    # Create validator
    validator = TeleportationRerunValidator()
    
    # Run validation
    result = validator.run_full_validation(
        num_reruns=num_jobs,
        shots=shots,
        backend_name=backend
    )
    
    # Print final result
    print("\n" + "=" * 60)
    print("VALIDATION RESULT")
    print("=" * 60)
    print(json.dumps(result, indent=2, default=str))
    
    return result


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="IBM Quantum Teleportation Rerun Validation - Quick Start",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python quick_start.py                    # Check environment and reference jobs
  python quick_start.py --run              # Run full validation (4 jobs)
  python quick_start.py --run --jobs 2     # Run with 2 jobs (minimum)
  python quick_start.py --run --backend ibm_fez  # Use specific backend
        """
    )
    
    parser.add_argument("--run", action="store_true", help="Run full validation (default: check only)")
    parser.add_argument("--jobs", type=int, default=4, help="Number of rerun jobs (default: 4)")
    parser.add_argument("--shots", type=int, default=1024, help="Shots per job (default: 1024)")
    parser.add_argument("--backend", type=str, default=None, help="Specific backend name")
    parser.add_argument("--skip-check", action="store_true", help="Skip environment check")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("IBM QUANTUM TELEPORTATION RERUN VALIDATION")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Environment check
    if not args.skip_check:
        if not check_environment():
            print("\n❌ Environment check failed. Please install missing dependencies.")
            print("   pip install -r requirements.txt")
            return
    
    # Run or check
    if args.run:
        run_validation(
            num_jobs=args.jobs,
            shots=args.shots,
            backend=args.backend
        )
    else:
        check_reference_jobs()
    
    print("\n" + "=" * 60)
    print("✅ Done")
    print("=" * 60)


if __name__ == "__main__":
    main()