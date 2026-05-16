#!/usr/bin/env python3
"""
Manual Circuit Runner for IBM Quantum

This script provides a simple interface for running the teleportation circuits
manually on IBM Quantum hardware.

Usage:
    python run_circuits_manually.py --circuit circuits/teleport_circuit_1.qasm --shots 1024
    python run_circuits_manually.py --all --shots 1024 --backend ibm_fez
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import sys

# Qiskit imports
try:
    from qiskit import QuantumCircuit
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False
    print("ERROR: Qiskit not available. Install with: pip install qiskit qiskit-ibm-runtime")


# Constants
PHI = 1.618033988749895
CLASSICAL_FIDELITY_THRESHOLD = 2.0 / 3.0  # ~0.667


def load_circuit(circuit_path: str) -> QuantumCircuit:
    """Load a circuit from a QASM file."""
    circuit = QuantumCircuit.from_qasm_file(circuit_path)
    print(f"✅ Loaded circuit from: {circuit_path}")
    print(f"   Qubits: {circuit.num_qubits}")
    print(f"   Depth: {circuit.depth()}")
    print(f"   Gates: {dict(circuit.count_ops())}")
    return circuit


def connect_to_ibm(token: Optional[str] = None) -> QiskitRuntimeService:
    """Connect to IBM Quantum Runtime service."""
    if token:
        service = QiskitRuntimeService(channel="ibm_quantum", token=token)
    else:
        service = QiskitRuntimeService()
    print(f"✅ Connected to IBM Quantum")
    print(f"   Channel: {service.channel}")
    return service


def select_backend(service: QiskitRuntimeService, 
                  preferred_backend: Optional[str] = None,
                  min_qubits: int = 3) -> Any:
    """Select an IBM Quantum backend."""
    backends = service.backends()
    
    # Filter to real hardware
    real_backends = [b for b in backends if not b.configuration().simulator]
    
    # Filter by qubit count
    suitable = [b for b in real_backends if b.configuration().n_qubits >= min_qubits]
    
    if not suitable:
        raise RuntimeError(f"No backends with at least {min_qubits} qubits")
    
    # Try preferred backend
    if preferred_backend:
        for b in suitable:
            if b.name == preferred_backend:
                print(f"✅ Selected backend: {b.name}")
                return b
    
    # Select least busy
    suitable.sort(key=lambda b: b.status().pending_jobs)
    selected = suitable[0]
    print(f"✅ Selected backend: {selected.name} (Queue: {selected.status().pending_jobs})")
    return selected


def run_circuit(circuit: QuantumCircuit,
                backend: Any,
                shots: int = 1024) -> Dict[str, Any]:
    """Run a circuit on IBM Quantum hardware."""
    print(f"\n📤 Running circuit on {backend.name}...")
    
    # Transpile
    print(f"   Transpiling...")
    pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
    transpiled = pm.run(circuit)
    print(f"   Transpiled depth: {transpiled.depth()}")
    
    # Run
    print(f"   Submitting job...")
    sampler = SamplerV2(backend)
    job = sampler.run([transpiled], shots=shots)
    
    job_id = job.job_id()
    print(f"   ✅ Job submitted: {job_id}")
    
    return {
        "job_id": job_id,
        "backend": backend.name,
        "shots": shots,
        "status": "RUNNING",
        "submission_time": datetime.now().isoformat()
    }


def compute_fidelity(counts: Dict[str, int], 
                     theta_y: float = np.pi/3) -> Dict[str, float]:
    """Compute teleportation fidelity from measurement counts."""
    total = sum(counts.values())
    
    # Extract Bob's qubit measurements (3rd bit)
    bob_0 = 0
    bob_1 = 0
    
    for bitstring, count in counts.items():
        # Bit ordering: c[2] is the most significant bit in Qiskit
        # For 3-bit results: bitstring[0] is c[2] (Bob's qubit)
        if len(bitstring) == 3:
            bob_bit = int(bitstring[0])  # Bob's qubit is the first bit
        else:
            bob_bit = int(bitstring[-1])  # Fallback to last bit
        
        if bob_bit == 0:
            bob_0 += count
        else:
            bob_1 += count
    
    # Measured probabilities
    p_measured_0 = bob_0 / total
    p_measured_1 = bob_1 / total
    
    # Expected probabilities for RY(θ_y)|0⟩
    expected_0 = np.cos(theta_y / 2) ** 2
    expected_1 = np.sin(theta_y / 2) ** 2
    
    # Fidelity
    fidelity = np.sqrt(expected_0 * p_measured_0) + np.sqrt(expected_1 * p_measured_1)
    
    return {
        "fidelity": float(fidelity),
        "fidelity_squared": float(fidelity ** 2),
        "expected_prob_0": float(expected_0),
        "expected_prob_1": float(expected_1),
        "measured_prob_0": float(p_measured_0),
        "measured_prob_1": float(p_measured_1),
        "bob_0_count": int(bob_0),
        "bob_1_count": int(bob_1),
        "total_shots": int(total),
        "exceeds_classical": bool(fidelity > CLASSICAL_FIDELITY_THRESHOLD)
    }


def wait_for_results(job_ids: List[str], 
                     service: QiskitRuntimeService,
                     poll_interval: int = 30) -> Dict[str, Any]:
    """Wait for jobs to complete and retrieve results."""
    import time
    
    print(f"\n⏳ Waiting for {len(job_ids)} jobs to complete...")
    
    results = {}
    completed = set()
    
    while len(completed) < len(job_ids):
        for job_id in job_ids:
            if job_id in completed:
                continue
            
            try:
                job = service.job(job_id)
                status = job.status()
                
                if status in ['COMPLETED', 'DONE', 'CANCELLED', 'ERROR', 'FAILED']:
                    print(f"   ✅ Job {job_id}: {status}")
                    completed.add(job_id)
                    
                    if status in ['COMPLETED', 'DONE']:
                        try:
                            result = job.result()
                            results[job_id] = {
                                "status": status,
                                "result": result
                            }
                        except Exception as e:
                            results[job_id] = {
                                "status": status,
                                "error": str(e)
                            }
                    else:
                        results[job_id] = {
                            "status": status,
                            "error": f"Job {status}"
                        }
                else:
                    print(f"   ⏳ Job {job_id}: {status}")
                    
            except Exception as e:
                print(f"   ⚠️ Error checking job {job_id}: {e}")
        
        if len(completed) < len(job_ids):
            time.sleep(poll_interval)
    
    return results


def analyze_results(results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Analyze job results and compute fidelity."""
    analyses = []
    
    for job_id, result_data in results.items():
        print(f"\n🔬 Analyzing job {job_id}...")
        
        if "error" in result_data:
            print(f"   ❌ Error: {result_data['error']}")
            analyses.append({
                "job_id": job_id,
                "error": result_data["error"]
            })
            continue
        
        try:
            result = result_data["result"]
            
            # Extract counts from SamplerV2 result
            if hasattr(result, 'data'):
                data = result.data
                if hasattr(data, 'c'):
                    # BitArray format
                    bit_array = data.c
                    counts = bit_array.get_counts()
                else:
                    # Legacy format
                    counts = result.get_counts()
            else:
                counts = result.get_counts()
            
            # Compute fidelity
            fidelity_metrics = compute_fidelity(counts)
            
            analysis = {
                "job_id": job_id,
                "counts": counts,
                **fidelity_metrics
            }
            
            analyses.append(analysis)
            
            print(f"   Fidelity: {fidelity_metrics['fidelity']:.4f}")
            print(f"   Exceeds classical threshold: {fidelity_metrics['exceeds_classical']}")
            
        except Exception as e:
            print(f"   ❌ Analysis error: {e}")
            analyses.append({
                "job_id": job_id,
                "error": str(e)
            })
    
    return analyses


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run teleportation circuits on IBM Quantum")
    parser.add_argument("--circuit", type=str, help="Path to a single QASM file")
    parser.add_argument("--all", action="store_true", help="Run all 4 circuits")
    parser.add_argument("--shots", type=int, default=1024, help="Shots per job (default: 1024)")
    parser.add_argument("--backend", type=str, default=None, help="Specific backend name")
    parser.add_argument("--token", type=str, default=None, help="IBM Quantum API token")
    parser.add_argument("--wait", action="store_true", help="Wait for results")
    parser.add_argument("--output", type=str, default="manual_run_results.json", help="Output file")
    
    args = parser.parse_args()
    
    if not QISKIT_AVAILABLE:
        print("ERROR: Qiskit not available")
        return
    
    print("=" * 80)
    print("IBM QUANTUM MANUAL CIRCUIT RUNNER")
    print("=" * 80)
    
    # Determine circuits to run
    circuit_dir = Path(__file__).parent / "circuits"
    
    if args.circuit:
        circuits = [Path(args.circuit)]
    elif args.all:
        circuits = [
            circuit_dir / "teleport_circuit_1.qasm",
            circuit_dir / "teleport_circuit_2.qasm",
            circuit_dir / "teleport_circuit_3.qasm",
            circuit_dir / "teleport_circuit_4.qasm"
        ]
    else:
        print("\nUsage:")
        print("  python run_circuits_manually.py --circuit <path> --shots 1024")
        print("  python run_circuits_manually.py --all --shots 1024 --backend ibm_fez")
        return
    
    # Connect to IBM Quantum
    print("\n📡 Connecting to IBM Quantum...")
    service = connect_to_ibm(args.token)
    
    # Select backend
    backend = select_backend(service, args.backend)
    
    # Load and run circuits
    job_ids = []
    run_info = []
    
    for circuit_path in circuits:
        if not circuit_path.exists():
            print(f"⚠️ Circuit not found: {circuit_path}")
            continue
        
        circuit = load_circuit(str(circuit_path))
        info = run_circuit(circuit, backend, args.shots)
        job_ids.append(info["job_id"])
        run_info.append(info)
    
    print(f"\n✅ Submitted {len(job_ids)} jobs")
    print(f"   Job IDs: {', '.join(job_ids)}")
    
    # Save job IDs
    output = {
        "timestamp": datetime.now().isoformat(),
        "backend": backend.name,
        "shots": args.shots,
        "job_ids": job_ids,
        "run_info": run_info
    }
    
    # Wait for results if requested
    if args.wait:
        results = wait_for_results(job_ids, service)
        analyses = analyze_results(results)
        
        output["results"] = {jid: r for jid, r in zip(job_ids, [results.get(jid, {}) for jid in job_ids])}
        output["analyses"] = analyses
        
        # Summary
        if analyses:
            fidelities = [a["fidelity"] for a in analyses if "fidelity" in a]
            if fidelities:
                print(f"\n📊 Summary:")
                print(f"   Best Fidelity: {max(fidelities):.4f}")
                print(f"   Mean Fidelity: {np.mean(fidelities):.4f}")
                print(f"   Above Classical Threshold: {sum(1 for f in fidelities if f > CLASSICAL_FIDELITY_THRESHOLD)}/{len(fidelities)}")
    
    # Save output
    output_path = Path(args.output)
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    
    print(f"\n✅ Results saved to: {output_path}")
    
    # Print job IDs for easy reference
    print(f"\n{'='*80}")
    print("JOB IDS FOR MANUAL TRACKING:")
    print("=" * 80)
    for job_id in job_ids:
        print(f"  {job_id}")
    print("=" * 80)


if __name__ == "__main__":
    main()