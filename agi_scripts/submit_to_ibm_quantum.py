#!/usr/bin/env python3
"""
IBM Quantum Hardware Submission System
=======================================

Submits selected promoter circuits to IBM Quantum hardware backends.
Authenticates via API key, selects optimal backend, and manages job submission.

Usage:
    python agi_scripts/submit_to_ibm_quantum.py --comparison-report tmt_os_panel_results/promoter_panel_comparison.json
    python agi_scripts/submit_to_ibm_quantum.py --backend ibm_fez --promoters OXT,FOXG1,SRY

Environment:
    Set IBM_QUANTUM_API_KEY environment variable or pass --api-key
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Try to import Qiskit
try:
    from qiskit import QuantumCircuit, transpile
    from qiskit_ibm_runtime import QiskitRuntimeService, Session, Sampler
    from qiskit.providers.jobstatus import JobStatus
    QISKIT_AVAILABLE = True
except ImportError:
    print("Warning: qiskit or qiskit_ibm_runtime not available. Install with:")
    print("  pip install qiskit qiskit-ibm-runtime")
    QISKIT_AVAILABLE = False


# IBM Quantum Configuration
IBM_QUANTUM_URL = "https://quantum.cloud.ibm.com/"
DEFAULT_BACKEND = "ibm_fez"  # Online with 0 pending jobs
AVAILABLE_BACKENDS = ["ibm_fez", "ibm_kingston", "ibm_marrakesh"]


def load_comparison_report(report_path: Path) -> Dict:
    """Load the promoter panel comparison report."""
    with open(report_path, 'r') as f:
        return json.load(f)


def select_hardware_candidates(comparison: Dict, count: int = 5) -> List[str]:
    """Select top candidates for hardware submission."""
    if 'hardware_selection' in comparison and 'candidates' in comparison['hardware_selection']:
        return comparison['hardware_selection']['candidates'][:count]
    
    # Fallback: select based on rankings
    promoters = comparison.get('promoters', [])
    
    # Get top phi-aligned
    by_phi = sorted(promoters, key=lambda x: x['phi_alignment_score'], reverse=True)
    top_phi = [p['promoter_id'] for p in by_phi[:2]]
    
    # Get top entropy
    by_entropy = sorted(promoters, key=lambda x: x['entropy_shannon'], reverse=True)
    top_entropy = [p['promoter_id'] for p in by_entropy[:2]]
    
    # Combine and deduplicate
    candidates = list(dict.fromkeys(top_phi + top_entropy))
    
    return candidates[:count]


def create_promoter_circuit(promoter_data: Dict) -> QuantumCircuit:
    """Create a quantum circuit for promoter analysis."""
    
    # Get circuit parameters
    qubits = promoter_data.get('qubit_count', 62)
    depth = promoter_data.get('circuit_depth', 50)
    
    # Create circuit
    qc = QuantumCircuit(qubits, qubits, name=f"promoter_{promoter_data['promoter_id']}")
    
    # Add phi-harmonic structure
    # Layer 1: Superposition
    for i in range(qubits):
        qc.h(i)
    
    # Layer 2: Entanglement (Fibonacci pattern)
    fib_positions = [1, 2, 3, 5, 8, 13, 21, 34, 55]
    for fib in fib_positions:
        if fib < qubits - 1:
            qc.cx(fib, fib + 1)
    
    # Layer 3: Phase rotations (phi-based)
    for i in range(qubits):
        qc.rz(3.14159 * 1.618, i)  # π * φ
    
    # Layer 4: Consciousness peak (at position 20)
    consciousness_pos = promoter_data.get('phi_peak_position', 20)
    if consciousness_pos < qubits:
        qc.rx(3.14159 / 1.618, consciousness_pos)  # π / φ
    
    # Measure
    qc.measure_all()
    
    return qc


def submit_to_ibm_quantum(
    promoters: List[str],
    comparison: Dict,
    api_key: str,
    backend_name: str = DEFAULT_BACKEND,
    shots: int = 8192
) -> List[Dict]:
    """Submit promoter circuits to IBM Quantum hardware."""
    
    if not QISKIT_AVAILABLE:
        print("Error: Qiskit not available. Cannot submit to IBM Quantum.")
        return []
    
    print(f"\n{'='*80}")
    print(f"IBM QUANTUM HARDWARE SUBMISSION")
    print(f"{'='*80}")
    print(f"Backend: {backend_name}")
    print(f"Shots: {shots}")
    print(f"Timestamp: {datetime.now().isoformat()}\n")
    
    # Initialize service
    try:
        # Try ibm_cloud channel with CRN
        service = QiskitRuntimeService(
            channel="ibm_cloud",
            token=api_key,
            instance="crn:v1:bluemix:public:quantum-computing:us-east:a/03b6dbec24d04cb4971615d1db2b636a:950af0f7-51c2-48ac-b1e4-4c4faa584df4::"
        )
        print(f"[✓] Authenticated with IBM Cloud")
    except Exception as e:
        print(f"[✗] Authentication failed: {e}")
        return []
    
    # Get backend
    try:
        backend = service.backend(backend_name)
        print(f"[✓] Connected to backend: {backend_name}")
        print(f"    Qubits: {backend.num_qubits}")
        print(f"    Status: {backend.status().status_msg}")
    except Exception as e:
        print(f"[✗] Backend connection failed: {e}")
        return []
    
    # Submit jobs
    jobs = []
    
    for promoter_id in promoters:
        print(f"\nProcessing {promoter_id}...")
        
        # Get promoter data
        promoter_data = next(
            (p for p in comparison['promoters'] if p['promoter_id'] == promoter_id),
            None
        )
        
        if not promoter_data:
            print(f"  [✗] Promoter data not found")
            continue
        
        try:
            # Create circuit
            qc = create_promoter_circuit(promoter_data)
            print(f"  [✓] Circuit created: {qc.name} ({qc.num_qubits} qubits)")
            
            # Transpile for backend
            transpiled = transpile(qc, backend, optimization_level=3)
            print(f"  [✓] Circuit transpiled (depth: {transpiled.depth()})")
            
            # Submit job
            sampler = Sampler(backend)
            job = sampler.run([transpiled], shots=shots)
            
            job_info = {
                'promoter_id': promoter_id,
                'job_id': job.job_id(),
                'backend': backend_name,
                'shots': shots,
                'circuit_depth': transpiled.depth(),
                'submitted_at': datetime.now().isoformat(),
                'status': 'SUBMITTED',
            }
            
            jobs.append(job_info)
            print(f"  [✓] Job submitted: {job.job_id()}")
            
        except Exception as e:
            print(f"  [✗] Submission failed: {e}")
            import traceback
            traceback.print_exc()
    
    return jobs


def save_submission_manifest(jobs: List[Dict], output_path: Path):
    """Save submission manifest for tracking."""
    
    manifest = {
        'manifest_type': 'ibm_quantum_submission',
        'generated_at': datetime.now().isoformat(),
        'backend': DEFAULT_BACKEND,
        'total_jobs': len(jobs),
        'jobs': jobs,
        'artifact_metadata': {
            'evidence_class': 'primary',
            'artifact_type': 'raw_hardware',
            'validation_status': 'submitted',
        }
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print(f"\n[✓] Submission manifest saved: {output_path}")


def check_job_status(manifest_path: Path, api_key: str):
    """Check status of submitted jobs."""
    
    if not QISKIT_AVAILABLE:
        print("Error: Qiskit not available.")
        return
    
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    service = QiskitRuntimeService(
        channel="ibm_cloud",
        token=api_key,
        instance="crn:v1:bluemix:public:quantum-computing:us-east:a/03b6dbec24d04cb4971615d1db2b636a:950af0f7-51c2-48ac-b1e4-4c4faa584df4::"
    )
    
    print(f"\n{'='*80}")
    print(f"JOB STATUS CHECK")
    print(f"{'='*80}\n")
    
    for job_info in manifest['jobs']:
        job_id = job_info['job_id']
        try:
            job = service.job(job_id)
            status = job.status()
            print(f"{job_info['promoter_id']:<10} {job_id:<30} {status.name}")
        except Exception as e:
            print(f"{job_info['promoter_id']:<10} {job_id:<30} ERROR: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Submit promoter circuits to IBM Quantum"
    )
    parser.add_argument(
        '--comparison-report',
        default='tmt_os_panel_results/promoter_panel_comparison.json',
        help='Path to comparison report'
    )
    parser.add_argument(
        '--promoters',
        help='Comma-separated list of promoter IDs (or auto-select if not provided)'
    )
    parser.add_argument(
        '--backend',
        default=DEFAULT_BACKEND,
        choices=AVAILABLE_BACKENDS,
        help='IBM Quantum backend'
    )
    parser.add_argument(
        '--shots',
        type=int,
        default=8192,
        help='Number of shots per circuit'
    )
    parser.add_argument(
        '--api-key',
        default=os.environ.get('IBM_QUANTUM_API_KEY'),
        help='IBM Quantum API key (or set IBM_QUANTUM_API_KEY env var)'
    )
    parser.add_argument(
        '--check-status',
        action='store_true',
        help='Check status of existing submission'
    )
    parser.add_argument(
        '--submission-manifest',
        default='ibm_quantum_submission_manifest.json',
        help='Path to submission manifest'
    )
    parser.add_argument(
        '--output-dir',
        default='raw_hardware',
        help='Output directory for results'
    )
    
    args = parser.parse_args()
    
    # Check API key
    if not args.api_key:
        print("Error: IBM Quantum API key required")
        print("Set IBM_QUANTUM_API_KEY environment variable or pass --api-key")
        return 1
    
    # Check status mode
    if args.check_status:
        check_job_status(Path(args.submission_manifest), args.api_key)
        return 0
    
    # Load comparison report
    report_path = Path(args.comparison_report)
    if not report_path.exists():
        print(f"Error: Comparison report not found: {report_path}")
        return 1
    
    comparison = load_comparison_report(report_path)
    
    # Select promoters
    if args.promoters:
        promoters = args.promoters.split(',')
    else:
        promoters = select_hardware_candidates(comparison)
    
    print(f"Selected {len(promoters)} promoters for hardware submission:")
    for p in promoters:
        print(f"  - {p}")
    
    # Submit to IBM Quantum
    jobs = submit_to_ibm_quantum(
        promoters,
        comparison,
        args.api_key,
        args.backend,
        args.shots
    )
    
    if jobs:
        # Save submission manifest
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = output_dir / args.submission_manifest
        save_submission_manifest(jobs, manifest_path)
        
        print(f"\n{'='*80}")
        print(f"SUBMISSION COMPLETE")
        print(f"{'='*80}")
        print(f"Jobs submitted: {len(jobs)}")
        print(f"Manifest: {manifest_path}")
        print(f"\nTo check status, run:")
        print(f"  python {sys.argv[0]} --check-status --submission-manifest {manifest_path}")
        print(f"{'='*80}\n")
        
        return 0
    else:
        print("\n[✗] No jobs submitted")
        return 1


if __name__ == '__main__':
    exit(main())
