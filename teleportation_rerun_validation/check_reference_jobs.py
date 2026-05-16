#!/usr/bin/env python3
"""
Check Reference Job Metadata

Retrieves and displays metadata for the reference IBM Quantum teleportation jobs
without submitting new runs.

Reference Job IDs:
- d6kvddgfh9oc73emadvg
- d6kvdfs3pels739umfg0
- d6kvdjgfh9oc73emae50
- d6kvdm43pels739umfog
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Reference job IDs
REFERENCE_JOB_IDS = [
    "d6kvddgfh9oc73emadvg",
    "d6kvdfs3pels739umfg0",
    "d6kvdjgfh9oc73emae50",
    "d6kvdm43pels739umfog"
]


def check_qiskit_available() -> bool:
    """Check if Qiskit is available."""
    try:
        from qiskit_ibm_runtime import QiskitRuntimeService
        return True
    except ImportError:
        return False


def connect_to_ibm(token: Optional[str] = None) -> Any:
    """Connect to IBM Quantum Runtime service."""
    from qiskit_ibm_runtime import QiskitRuntimeService
    
    if token:
        service = QiskitRuntimeService(channel="ibm_quantum", token=token)
    else:
        service = QiskitRuntimeService()
    
    return service


def retrieve_job_metadata(service: Any, job_id: str) -> Dict[str, Any]:
    """
    Retrieve comprehensive metadata for a job.
    
    Args:
        service: QiskitRuntimeService instance
        job_id: Job ID to retrieve
        
    Returns:
        Dict containing job metadata
    """
    metadata = {
        "job_id": job_id,
        "retrieval_timestamp": datetime.now().isoformat()
    }
    
    try:
        job = service.job(job_id)
        
        # Basic job properties
        metadata["status"] = str(job.status())
        metadata["job_type"] = type(job).__name__
        
        # Backend information
        try:
            backend = job.backend()
            if hasattr(backend, 'name'):
                metadata["backend_name"] = backend.name
            if hasattr(backend, 'configuration'):
                config = backend.configuration()
                metadata["backend_qubits"] = config.n_qubits
                metadata["backend_version"] = getattr(config, 'backend_version', 'N/A')
        except Exception as e:
            metadata["backend_error"] = str(e)
        
        # Timing information
        if hasattr(job, 'creation_date'):
            metadata["creation_date"] = str(job.creation_date)
        
        # Session and tags
        if hasattr(job, 'session_id'):
            metadata["session_id"] = job.session_id
        if hasattr(job, 'tags'):
            metadata["tags"] = job.tags
        
        # Try to get result information
        try:
            result = job.result()
            
            if hasattr(result, 'metadata'):
                metadata["result_metadata"] = result.metadata
            
            # Extract counts if available
            if hasattr(result, 'get_counts'):
                try:
                    counts = result.get_counts()
                    if counts:
                        metadata["shots"] = sum(counts.values()) if isinstance(counts, dict) else len(counts)
                        metadata["counts"] = counts
                except Exception as e:
                    metadata["counts_error"] = str(e)
            
            # Extract data from SamplerV2 format
            if hasattr(result, 'data'):
                try:
                    data = result.data
                    if hasattr(data, '__dict__'):
                        metadata["result_data_keys"] = list(data.__dict__.keys())
                except Exception as e:
                    metadata["data_error"] = str(e)
            
        except Exception as e:
            metadata["result_error"] = str(e)
        
        # Try to get circuit information
        try:
            if hasattr(job, 'circuits'):
                circuits = job.circuits()
                if circuits:
                    metadata["num_circuits"] = len(circuits)
                    if hasattr(circuits[0], 'num_qubits'):
                        metadata["circuit_qubits"] = circuits[0].num_qubits
                    if hasattr(circuits[0], 'depth'):
                        metadata["circuit_depth"] = circuits[0].depth()
                    if hasattr(circuits[0], 'count_ops'):
                        metadata["circuit_ops"] = dict(circuits[0].count_ops())
        except Exception as e:
            metadata["circuit_error"] = str(e)
        
        # Cost information
        if hasattr(job, 'usage_estimation'):
            metadata["usage_estimation"] = job.usage_estimation
        
        metadata["retrieval_success"] = True
        
    except Exception as e:
        metadata["error"] = str(e)
        metadata["retrieval_success"] = False
    
    return metadata


def print_job_summary(metadata: Dict[str, Any]) -> None:
    """Print a formatted summary of job metadata."""
    job_id = metadata.get("job_id", "UNKNOWN")
    status = metadata.get("status", "UNKNOWN")
    backend = metadata.get("backend_name", "N/A")
    
    print(f"\n{'='*80}")
    print(f"Job ID: {job_id}")
    print(f"{'='*80}")
    print(f"Status: {status}")
    print(f"Backend: {backend}")
    
    if "creation_date" in metadata:
        print(f"Created: {metadata['creation_date']}")
    
    if "shots" in metadata:
        print(f"Shots: {metadata['shots']}")
    
    if "circuit_qubits" in metadata:
        print(f"Qubits: {metadata['circuit_qubits']}")
    
    if "circuit_depth" in metadata:
        print(f"Depth: {metadata['circuit_depth']}")
    
    if "circuit_ops" in metadata:
        print(f"Operations: {metadata['circuit_ops']}")
    
    if "counts" in metadata:
        counts = metadata["counts"]
        if isinstance(counts, dict):
            print(f"\nMeasurement Outcomes (top 5):")
            sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:5]
            for bitstring, count in sorted_counts:
                print(f"  |{bitstring}⟩: {count}")
    
    if "error" in metadata:
        print(f"\n❌ Error: {metadata['error']}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Check reference IBM Quantum job metadata")
    parser.add_argument("--token", type=str, default=None, help="IBM Quantum API token")
    parser.add_argument("--output", type=str, default="reference_jobs_metadata.json", help="Output file")
    parser.add_argument("--verbose", action="store_true", help="Print detailed information")
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("IBM QUANTUM REFERENCE JOB METADATA CHECK")
    print("=" * 80)
    
    # Check Qiskit availability
    if not check_qiskit_available():
        print("\n❌ ERROR: Qiskit IBM Runtime not available.")
        print("Install with: pip install qiskit qiskit-ibm-runtime")
        return
    
    # Connect to IBM Quantum
    print("\n📡 Connecting to IBM Quantum...")
    try:
        service = connect_to_ibm(token=args.token)
        print("✅ Connected successfully")
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return
    
    # Retrieve metadata for each reference job
    print(f"\n📊 Retrieving metadata for {len(REFERENCE_JOB_IDS)} reference jobs...")
    
    all_metadata = {}
    
    for job_id in REFERENCE_JOB_IDS:
        print(f"\n{'─'*80}")
        print(f"Job: {job_id}")
        
        metadata = retrieve_job_metadata(service, job_id)
        all_metadata[job_id] = metadata
        
        if args.verbose:
            print_job_summary(metadata)
        else:
            status = metadata.get("status", "UNKNOWN")
            backend = metadata.get("backend_name", "N/A")
            success = "✅" if metadata.get("retrieval_success", False) else "❌"
            print(f"  {success} Status: {status}, Backend: {backend}")
    
    # Save metadata
    output_path = Path(args.output)
    with open(output_path, 'w') as f:
        json.dump(all_metadata, f, indent=2, default=str)
    
    print(f"\n{'='*80}")
    print(f"✅ Metadata saved to: {output_path}")
    
    # Summary table
    print(f"\n{'='*80}")
    print("SUMMARY TABLE")
    print(f"{'='*80}")
    print(f"{'Job ID':<25} {'Backend':<15} {'Status':<15} {'Shots':<10}")
    print(f"{'-'*65}")
    
    for job_id, meta in all_metadata.items():
        backend = meta.get("backend_name", "N/A")
        status = meta.get("status", "N/A")
        shots = meta.get("shots", "N/A")
        print(f"{job_id:<25} {backend:<15} {status:<15} {shots:<10}")
    
    # Check if all jobs are available
    available_count = sum(1 for m in all_metadata.values() if m.get("retrieval_success", False))
    print(f"\n{'='*80}")
    print(f"Available: {available_count}/{len(REFERENCE_JOB_IDS)} reference jobs")
    
    if available_count == len(REFERENCE_JOB_IDS):
        print("✅ All reference jobs are accessible")
    else:
        print("⚠️  Some reference jobs may not be accessible")
    
    print(f"{'='*80}")


if __name__ == "__main__":
    main()