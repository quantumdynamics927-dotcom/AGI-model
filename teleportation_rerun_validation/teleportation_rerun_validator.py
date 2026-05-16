#!/usr/bin/env python3
"""
IBM Quantum Teleportation Rerun Validator

Re-runs and validates previously successful IBM Quantum teleportation experiments
on real hardware, computing fidelity and determining reproducibility.

Reference Job IDs:
- d6kvddgfh9oc73emadvg
- d6kvdfs3pels739umfg0
- d6kvdjgfh9oc73emae50
- d6kvdm43pels739umfog

Target Experiment:
- Teleport the single-qubit state RY(pi/3) · RZ(pi/7) |0⟩
- Use ER=EPR-inspired teleportation circuit logic
- Real hardware execution only (no simulation)
"""

import json
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
import sys

# Qiskit imports
try:
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
    from qiskit.quantum_info import Statevector, state_fidelity
    from qiskit_ibm_runtime import QiskitRuntimeService
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    QISKIT_AVAILABLE = True
except ImportError as e:
    QISKIT_AVAILABLE = False
    print(f"Warning: Qiskit not available: {e}")

# Constants
PHI = 1.618033988749895
CLASSICAL_FIDELITY_THRESHOLD = 2.0 / 3.0  # ~0.667

# Reference job IDs
REFERENCE_JOB_IDS = [
    "d6kvddgfh9oc73emadvg",
    "d6kvdfs3pels739umfg0",
    "d6kvdjgfh9oc73emae50",
    "d6kvdm43pels739umfog"
]


class TeleportationRerunValidator:
    """
    Validates IBM Quantum teleportation experiments by rerunning on hardware.
    """
    
    def __init__(self, output_dir: str = "teleportation_rerun_validation"):
        """
        Initialize the validator.
        
        Args:
            output_dir: Directory to save validation artifacts
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.service = None
        self.old_jobs_metadata = {}
        self.new_jobs_metadata = {}
        self.fidelity_results = []
        
    def connect_to_ibm(self, channel: str = "ibm_quantum", token: Optional[str] = None) -> bool:
        """
        Connect to IBM Quantum Runtime service.
        
        Args:
            channel: IBM Quantum channel ('ibm_quantum' or 'ibm_cloud')
            token: IBM Quantum API token (optional, uses saved credentials if None)
            
        Returns:
            bool: True if connection successful
        """
        if not QISKIT_AVAILABLE:
            print("ERROR: Qiskit not available. Cannot connect to IBM Quantum.")
            return False
            
        try:
            if token:
                self.service = QiskitRuntimeService(channel=channel, token=token)
            else:
                self.service = QiskitRuntimeService()
            
            print(f"✅ Connected to IBM Quantum Runtime")
            print(f"   Channel: {self.service.channel}")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to IBM Quantum: {e}")
            return False
    
    def retrieve_old_job_metadata(self, job_ids: List[str]) -> Dict[str, Any]:
        """
        Retrieve metadata for reference jobs.
        
        Args:
            job_ids: List of reference job IDs
            
        Returns:
            Dict containing metadata for each job
        """
        if not self.service:
            print("ERROR: Not connected to IBM Quantum. Call connect_to_ibm() first.")
            return {}
        
        metadata = {}
        
        for job_id in job_ids:
            print(f"\n📊 Retrieving metadata for job {job_id}...")
            
            try:
                job = self.service.job(job_id)
                
                # Extract job properties
                job_info = {
                    "job_id": job_id,
                    "backend_name": job.backend().name if hasattr(job.backend(), 'name') else str(job.backend()),
                    "status": job.status(),
                    "creation_date": str(job.creation_date) if hasattr(job, 'creation_date') else "N/A",
                    "shots": None,  # Will extract from result
                    "num_qubits": None,
                    "primitive_type": type(job).__name__,
                    "session_id": getattr(job, 'session_id', None),
                    "tags": getattr(job, 'tags', []),
                }
                
                # Try to get additional metadata from job result
                try:
                    result = job.result()
                    if hasattr(result, 'metadata'):
                        job_info["result_metadata"] = result.metadata
                    
                    # Extract shots from result
                    if hasattr(result, 'get_counts'):
                        counts = result.get_counts()
                        if counts:
                            job_info["shots"] = sum(counts.values())
                            job_info["num_qubits"] = len(list(counts.keys())[0]) if counts else None
                            job_info["counts"] = counts
                except Exception as e:
                    print(f"   Warning: Could not retrieve result for {job_id}: {e}")
                
                # Try to get circuit information
                try:
                    if hasattr(job, 'circuits'):
                        circuits = job.circuits()
                        if circuits:
                            job_info["num_circuits"] = len(circuits)
                            if hasattr(circuits[0], 'num_qubits'):
                                job_info["num_qubits"] = circuits[0].num_qubits
                except Exception as e:
                    print(f"   Warning: Could not retrieve circuit info: {e}")
                
                metadata[job_id] = job_info
                print(f"   ✅ Retrieved: Backend={job_info['backend_name']}, Status={job_info['status']}")
                
            except Exception as e:
                print(f"   ❌ Failed to retrieve job {job_id}: {e}")
                metadata[job_id] = {"error": str(e)}
        
        self.old_jobs_metadata = metadata
        return metadata
    
    def create_teleportation_circuit(self, 
                                      theta_y: float = np.pi/3, 
                                      theta_z: float = np.pi/7,
                                      use_dynamic_circuit: bool = True) -> QuantumCircuit:
        """
        Create the teleportation circuit for RY(θ_y)·RZ(θ_z)|0⟩ state.
        
        Args:
            theta_y: RY rotation angle (default: π/3)
            theta_z: RZ rotation angle (default: π/7)
            use_dynamic_circuit: Whether to use dynamic circuit (if_test) or c_if
            
        Returns:
            QuantumCircuit: The teleportation circuit
        """
        # Create quantum and classical registers
        qr = QuantumRegister(3, 'q')  # q[0]: Alice's state, q[1]: EPR pair 1, q[2]: Bob's qubit
        cr = ClassicalRegister(3, 'c')  # Classical bits for measurement
        circuit = QuantumCircuit(qr, cr, name="Teleportation")
        
        # Step 1: Prepare the state to teleport on Alice's qubit (q[0])
        # |ψ⟩ = RY(θ_y) · RZ(θ_z) |0⟩
        circuit.rz(theta_z, qr[0])
        circuit.ry(theta_y, qr[0])
        
        # Step 2: Create EPR pair (Bell state) between Alice (q[1]) and Bob (q[2])
        circuit.h(qr[1])
        circuit.cx(qr[1], qr[2])
        
        # Step 3: Alice performs Bell measurement
        circuit.cx(qr[0], qr[1])
        circuit.h(qr[0])
        
        # Step 4: Measure Alice's qubits
        circuit.measure(qr[0], cr[0])
        circuit.measure(qr[1], cr[1])
        
        # Step 5: Bob applies corrections based on Alice's measurements
        if use_dynamic_circuit:
            # Use Qiskit 1.x+ dynamic circuit syntax (if_test)
            with circuit.if_test((cr[1], 1)):
                circuit.x(qr[2])
            with circuit.if_test((cr[0], 1)):
                circuit.z(qr[2])
        else:
            # Use legacy c_if syntax (for older Qiskit versions)
            circuit.x(qr[2]).c_if(cr, 2)  # If cr[1] = 1
            circuit.z(qr[2]).c_if(cr, 1)  # If cr[0] = 1
        
        # Step 6: Measure Bob's qubit (teleported state)
        circuit.measure(qr[2], cr[2])
        
        return circuit
    
    def select_backend(self, preferred_backend: Optional[str] = None) -> Any:
        """
        Select an IBM Quantum backend for execution.
        
        Args:
            preferred_backend: Preferred backend name (optional)
            
        Returns:
            Backend object
        """
        if not self.service:
            raise RuntimeError("Not connected to IBM Quantum")
        
        # Get available backends
        backends = self.service.backends()
        
        # Filter to real hardware (not simulators)
        real_backends = [b for b in backends if not b.configuration().simulator]
        
        if not real_backends:
            raise RuntimeError("No real hardware backends available")
        
        # Try to use preferred backend if specified
        if preferred_backend:
            for backend in real_backends:
                if backend.name == preferred_backend:
                    print(f"✅ Selected preferred backend: {backend.name}")
                    return backend
        
        # Otherwise, select the least busy backend with enough qubits
        # Sort by queue size (pending jobs)
        suitable_backends = []
        for backend in real_backends:
            config = backend.configuration()
            status = backend.status()
            
            # Check if backend has enough qubits (need at least 3)
            if config.n_qubits >= 3:
                suitable_backends.append({
                    'backend': backend,
                    'name': backend.name,
                    'queue_size': status.pending_jobs,
                    'qubits': config.n_qubits
                })
        
        if not suitable_backends:
            raise RuntimeError("No suitable backends with enough qubits")
        
        # Sort by queue size
        suitable_backends.sort(key=lambda x: x['queue_size'])
        
        selected = suitable_backends[0]
        print(f"✅ Selected backend: {selected['name']} (Queue: {selected['queue_size']}, Qubits: {selected['qubits']})")
        
        return selected['backend']
    
    def submit_rerun_jobs(self, 
                          num_jobs: int = 4,
                          shots: int = 1024,
                          backend_name: Optional[str] = None,
                          theta_y: float = np.pi/3,
                          theta_z: float = np.pi/7) -> List[str]:
        """
        Submit fresh hardware runs for teleportation validation.
        
        Args:
            num_jobs: Number of jobs to submit (2-4 recommended)
            shots: Number of shots per job
            backend_name: Specific backend to use (optional)
            theta_y: RY rotation angle
            theta_z: RZ rotation angle
            
        Returns:
            List of new job IDs
        """
        if not self.service:
            raise RuntimeError("Not connected to IBM Quantum")
        
        # Select backend
        backend = self.select_backend(backend_name)
        
        # Create teleportation circuit
        circuit = self.create_teleportation_circuit(theta_y, theta_z)
        
        print(f"\n⚛️  Teleportation Circuit:")
        print(f"   Target state: RY({theta_y:.6f}) · RZ({theta_z:.6f}) |0⟩")
        print(f"   Qubits: {circuit.num_qubits}")
        print(f"   Depth: {circuit.depth()}")
        print(f"   Gates: {dict(circuit.count_ops())}")
        
        # Transpile for backend
        print(f"\n🔧 Transpiling for {backend.name}...")
        pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
        transpiled = pm.run(circuit)
        
        print(f"   Transpiled depth: {transpiled.depth()}")
        print(f"   Transpiled gates: {dict(transpiled.count_ops())}")
        
        # Submit jobs
        new_job_ids = []
        
        for i in range(num_jobs):
            print(f"\n📤 Submitting job {i+1}/{num_jobs}...")
            
            try:
                # Use Sampler primitive for execution
                from qiskit_ibm_runtime import SamplerV2 as Sampler
                
                sampler = Sampler(backend)
                job = sampler.run([transpiled], shots=shots)
                
                job_id = job.job_id()
                new_job_ids.append(job_id)
                
                print(f"   ✅ Job submitted: {job_id}")
                
                # Save initial metadata
                self.new_jobs_metadata[job_id] = {
                    "job_id": job_id,
                    "backend_name": backend.name,
                    "shots": shots,
                    "theta_y": theta_y,
                    "theta_z": theta_z,
                    "submission_time": datetime.now().isoformat(),
                    "status": "RUNNING"
                }
                
            except Exception as e:
                print(f"   ❌ Failed to submit job: {e}")
        
        return new_job_ids
    
    def monitor_jobs(self, job_ids: List[str], poll_interval: int = 30) -> Dict[str, Any]:
        """
        Monitor jobs until completion.
        
        Args:
            job_ids: List of job IDs to monitor
            poll_interval: Polling interval in seconds
            
        Returns:
            Dict containing final job statuses
        """
        if not self.service:
            raise RuntimeError("Not connected to IBM Quantum")
        
        import time
        
        print(f"\n⏳ Monitoring {len(job_ids)} jobs...")
        
        completed = {}
        
        while len(completed) < len(job_ids):
            for job_id in job_ids:
                if job_id in completed:
                    continue
                
                try:
                    job = self.service.job(job_id)
                    status = job.status()
                    
                    if status in ['COMPLETED', 'DONE', 'CANCELLED', 'ERROR', 'FAILED']:
                        completed[job_id] = {
                            "status": status,
                            "job": job
                        }
                        print(f"   ✅ Job {job_id}: {status}")
                    else:
                        print(f"   ⏳ Job {job_id}: {status}")
                        
                except Exception as e:
                    print(f"   ⚠️  Error checking job {job_id}: {e}")
            
            if len(completed) < len(job_ids):
                time.sleep(poll_interval)
        
        return completed
    
    def decode_result_data(self, result_data: Any) -> np.ndarray:
        """
        Decode measurement results from IBM Runtime format.
        
        Args:
            result_data: Raw result data from IBM Runtime
            
        Returns:
            np.ndarray: Decoded measurement outcomes
        """
        # Handle different result formats
        if hasattr(result_data, 'data'):
            # SamplerV2 format
            data = result_data.data
            if hasattr(data, 'c'):
                # BitArray format
                bit_array = data.c
                if hasattr(bit_array, 'array'):
                    # NumPy array
                    return bit_array.array
                elif hasattr(bit_array, 'get_counts'):
                    # Counts format
                    counts = bit_array.get_counts()
                    return self._counts_to_array(counts)
        
        # Legacy format
        if hasattr(result_data, 'get_counts'):
            counts = result_data.get_counts()
            return self._counts_to_array(counts)
        
        raise ValueError("Unable to decode result data")
    
    def _counts_to_array(self, counts: Dict[str, int]) -> np.ndarray:
        """Convert counts dictionary to array of outcomes."""
        outcomes = []
        for bitstring, count in counts.items():
            for _ in range(count):
                outcomes.append([int(b) for b in bitstring])
        return np.array(outcomes)
    
    def compute_fidelity(self, 
                        measurement_data: np.ndarray, 
                        theta_y: float, 
                        theta_z: float) -> Dict[str, float]:
        """
        Compute teleportation fidelity from measurement results.
        
        Args:
            measurement_data: Array of measurement outcomes (shots × 3 qubits)
            theta_y: RY rotation angle used in state preparation
            theta_z: RZ rotation angle used in state preparation
            
        Returns:
            Dict containing fidelity metrics
        """
        # Extract Bob's qubit measurements (3rd qubit, index 2)
        bob_outcomes = measurement_data[:, 2]
        
        # Count outcomes
        bob_0_count = np.sum(bob_outcomes == 0)
        bob_1_count = np.sum(bob_outcomes == 1)
        total = len(bob_outcomes)
        
        # Measured probabilities
        p_measured_0 = bob_0_count / total
        p_measured_1 = bob_1_count / total
        
        # Expected state: |ψ⟩ = RY(θ_y) · RZ(θ_z) |0⟩
        # |ψ⟩ = RY(θ_y) · RZ(θ_z) |0⟩
        # After RZ(θ_z)|0⟩ = |0⟩ (RZ on |0⟩ is just a global phase)
        # After RY(θ_y)|0⟩ = cos(θ_y/2)|0⟩ + sin(θ_y/2)|1⟩
        # So: P(0) = cos²(θ_y/2), P(1) = sin²(θ_y/2)
        
        expected_0 = np.cos(theta_y / 2) ** 2
        expected_1 = np.sin(theta_y / 2) ** 2
        
        # Fidelity calculation
        # F = √(P_expected(0) × P_measured(0)) + √(P_expected(1) × P_measured(1))
        fidelity = np.sqrt(expected_0 * p_measured_0) + np.sqrt(expected_1 * p_measured_1)
        fidelity_squared = fidelity ** 2
        
        # Additional metrics
        classical_threshold = CLASSICAL_FIDELITY_THRESHOLD
        exceeds_classical = fidelity > classical_threshold
        
        return {
            "fidelity": float(fidelity),
            "fidelity_squared": float(fidelity_squared),
            "expected_prob_0": float(expected_0),
            "expected_prob_1": float(expected_1),
            "measured_prob_0": float(p_measured_0),
            "measured_prob_1": float(p_measured_1),
            "bob_0_count": int(bob_0_count),
            "bob_1_count": int(bob_1_count),
            "total_shots": int(total),
            "exceeds_classical_threshold": bool(exceeds_classical),
            "quality": self._quality_rating(fidelity)
        }
    
    def _quality_rating(self, fidelity: float) -> str:
        """Assign quality rating based on fidelity."""
        if fidelity > 0.9:
            return "EXCELLENT ✅"
        elif fidelity > 0.8:
            return "VERY GOOD ✓"
        elif fidelity > 0.667:
            return "GOOD (above classical) ✓"
        elif fidelity > 0.5:
            return "MODERATE ⚠️"
        else:
            return "POOR ❌"
    
    def analyze_job_results(self, job_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Analyze results from completed jobs.
        
        Args:
            job_ids: List of job IDs to analyze
            
        Returns:
            List of analysis results
        """
        if not self.service:
            raise RuntimeError("Not connected to IBM Quantum")
        
        results = []
        
        for job_id in job_ids:
            print(f"\n🔬 Analyzing job {job_id}...")
            
            try:
                job = self.service.job(job_id)
                result = job.result()
                
                # Get metadata
                metadata = self.new_jobs_metadata.get(job_id, {})
                theta_y = metadata.get('theta_y', np.pi/3)
                theta_z = metadata.get('theta_z', np.pi/7)
                
                # Decode measurement data
                measurement_data = self.decode_result_data(result)
                
                # Compute fidelity
                fidelity_metrics = self.compute_fidelity(measurement_data, theta_y, theta_z)
                
                # Store results
                analysis = {
                    "job_id": job_id,
                    "backend": metadata.get('backend_name', 'unknown'),
                    "shots": metadata.get('shots', len(measurement_data)),
                    "theta_y": theta_y,
                    "theta_z": theta_z,
                    **fidelity_metrics,
                    "timestamp": datetime.now().isoformat()
                }
                
                results.append(analysis)
                
                # Update metadata
                self.new_jobs_metadata[job_id].update(analysis)
                
                print(f"   Fidelity: {fidelity_metrics['fidelity']:.4f}")
                print(f"   Quality: {fidelity_metrics['quality']}")
                print(f"   Exceeds classical threshold: {fidelity_metrics['exceeds_classical_threshold']}")
                
            except Exception as e:
                print(f"   ❌ Failed to analyze job {job_id}: {e}")
                results.append({
                    "job_id": job_id,
                    "error": str(e)
                })
        
        self.fidelity_results = results
        return results
    
    def generate_validation_report(self) -> str:
        """
        Generate a comprehensive validation report.
        
        Returns:
            str: Path to the generated report
        """
        report_lines = []
        
        # Header
        report_lines.append("# IBM Quantum Teleportation Rerun Validation Report")
        report_lines.append(f"\n**Generated**: {datetime.now().isoformat()}")
        report_lines.append(f"\n**Objective**: Validate reproducibility of teleportation experiment")
        report_lines.append(f"**Target State**: RY(π/3) · RZ(π/7) |0⟩")
        report_lines.append(f"**Classical Threshold**: F > {CLASSICAL_FIDELITY_THRESHOLD:.4f}")
        
        # Reference Jobs
        report_lines.append("\n---\n\n## Reference Job Metadata\n")
        report_lines.append("\n| Job ID | Backend | Status | Shots |")
        report_lines.append("\n|--------|---------|--------|-------|")
        
        for job_id, meta in self.old_jobs_metadata.items():
            backend = meta.get('backend_name', 'N/A')
            status = meta.get('status', 'N/A')
            shots = meta.get('shots', 'N/A')
            report_lines.append(f"\n| `{job_id}` | {backend} | {status} | {shots} |")
        
        # New Jobs
        report_lines.append("\n\n---\n\n## Rerun Job Results\n")
        report_lines.append("\n| Job ID | Backend | Shots | Fidelity | Quality | Above Classical |")
        report_lines.append("\n|--------|---------|-------|----------|---------|-----------------|")
        
        for result in self.fidelity_results:
            job_id = result.get('job_id', 'N/A')
            backend = result.get('backend', 'N/A')
            shots = result.get('shots', 'N/A')
            fidelity = result.get('fidelity', 0)
            quality = result.get('quality', 'N/A')
            above_classical = "✓" if result.get('exceeds_classical_threshold', False) else "✗"
            report_lines.append(f"\n| `{job_id}` | {backend} | {shots} | {fidelity:.4f} | {quality} | {above_classical} |")
        
        # Summary Statistics
        if self.fidelity_results:
            fidelities = [r['fidelity'] for r in self.fidelity_results if 'fidelity' in r]
            
            if fidelities:
                best_fidelity = max(fidelities)
                mean_fidelity = np.mean(fidelities)
                std_fidelity = np.std(fidelities)
                above_threshold = sum(1 for f in fidelities if f > CLASSICAL_FIDELITY_THRESHOLD)
                total_runs = len(fidelities)
                
                report_lines.append("\n\n---\n\n## Summary Statistics\n")
                report_lines.append(f"\n- **Best Fidelity**: {best_fidelity:.4f}")
                report_lines.append(f"\n- **Mean Fidelity**: {mean_fidelity:.4f} ± {std_fidelity:.4f}")
                report_lines.append(f"\n- **Runs Above Classical Threshold**: {above_threshold}/{total_runs}")
                
                # Conclusion
                report_lines.append("\n\n---\n\n## Conclusion\n")
                
                if above_threshold == total_runs:
                    conclusion = "**CONFIRMED**: All reruns exceed the classical teleportation threshold. The original result is reproducible."
                elif above_threshold >= total_runs // 2:
                    conclusion = f"**PARTIALLY CONFIRMED**: {above_threshold}/{total_runs} reruns exceed the classical threshold. The original result shows promising evidence but requires further replication."
                else:
                    conclusion = "**NOT CONFIRMED**: Insufficient reruns exceed the classical threshold. Further investigation needed."
                
                report_lines.append(f"\n{conclusion}")
                
                # Evidence Summary
                report_lines.append("\n\n### Evidence Summary\n")
                report_lines.append(f"\n- **New Job IDs**: {', '.join([r['job_id'] for r in self.fidelity_results])}")
                report_lines.append(f"\n- **Best Fidelity**: {best_fidelity:.4f} (Quality: {self._quality_rating(best_fidelity)})")
                report_lines.append(f"\n- **Reproducibility**: {above_threshold}/{total_runs} runs above classical threshold")
        
        # Save report
        report_path = self.output_dir / "validation_report.md"
        report_content = "".join(report_lines)
        
        with open(report_path, 'w') as f:
            f.write(report_content)
        
        print(f"\n✅ Validation report saved to: {report_path}")
        
        return str(report_path)
    
    def save_artifacts(self):
        """Save all validation artifacts."""
        # Save old job metadata
        old_jobs_path = self.output_dir / "old_jobs_metadata.json"
        with open(old_jobs_path, 'w') as f:
            json.dump(self.old_jobs_metadata, f, indent=2, default=str)
        print(f"✅ Saved: {old_jobs_path}")
        
        # Save new job metadata
        new_jobs_path = self.output_dir / "new_jobs_metadata.json"
        with open(new_jobs_path, 'w') as f:
            json.dump(self.new_jobs_metadata, f, indent=2, default=str)
        print(f"✅ Saved: {new_jobs_path}")
        
        # Save fidelity results
        fidelity_path = self.output_dir / "fidelity_results.csv"
        if self.fidelity_results:
            import csv
            with open(fidelity_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.fidelity_results[0].keys())
                writer.writeheader()
                writer.writerows(self.fidelity_results)
            print(f"✅ Saved: {fidelity_path}")
    
    def run_full_validation(self, 
                           num_reruns: int = 4,
                           shots: int = 1024,
                           backend_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute the complete validation workflow.
        
        Args:
            num_reruns: Number of rerun jobs to submit
            shots: Number of shots per job
            backend_name: Specific backend to use (optional)
            
        Returns:
            Dict containing validation summary
        """
        print("=" * 100)
        print("IBM QUANTUM TELEPORTATION RERUN VALIDATION")
        print("=" * 100)
        
        # Step 1: Connect to IBM Quantum
        print("\n📡 Step 1: Connecting to IBM Quantum...")
        if not self.connect_to_ibm():
            return {"error": "Failed to connect to IBM Quantum"}
        
        # Step 2: Retrieve old job metadata
        print("\n📊 Step 2: Retrieving reference job metadata...")
        self.retrieve_old_job_metadata(REFERENCE_JOB_IDS)
        
        # Step 3: Submit new jobs
        print(f"\n📤 Step 3: Submitting {num_reruns} rerun jobs...")
        new_job_ids = self.submit_rerun_jobs(num_jobs=num_reruns, shots=shots, backend_name=backend_name)
        
        if not new_job_ids:
            return {"error": "Failed to submit rerun jobs"}
        
        # Step 4: Monitor jobs
        print("\n⏳ Step 4: Monitoring jobs until completion...")
        self.monitor_jobs(new_job_ids)
        
        # Step 5: Analyze results
        print("\n🔬 Step 5: Analyzing job results...")
        self.analyze_job_results(new_job_ids)
        
        # Step 6: Generate report
        print("\n📝 Step 6: Generating validation report...")
        report_path = self.generate_validation_report()
        
        # Step 7: Save artifacts
        print("\n💾 Step 7: Saving artifacts...")
        self.save_artifacts()
        
        # Final summary
        print("\n" + "=" * 100)
        print("VALIDATION COMPLETE")
        print("=" * 100)
        
        if self.fidelity_results:
            fidelities = [r['fidelity'] for r in self.fidelity_results if 'fidelity' in r]
            above_threshold = sum(1 for f in fidelities if f > CLASSICAL_FIDELITY_THRESHOLD)
            
            summary = {
                "new_job_ids": new_job_ids,
                "best_fidelity": max(fidelities) if fidelities else 0,
                "mean_fidelity": np.mean(fidelities) if fidelities else 0,
                "runs_above_threshold": above_threshold,
                "total_runs": len(fidelities),
                "report_path": report_path,
                "reproducible": above_threshold == len(fidelities)
            }
            
            print(f"\n📊 Summary:")
            print(f"   New Job IDs: {', '.join(new_job_ids)}")
            print(f"   Best Fidelity: {summary['best_fidelity']:.4f}")
            print(f"   Mean Fidelity: {summary['mean_fidelity']:.4f}")
            print(f"   Runs Above Classical Threshold: {above_threshold}/{len(fidelities)}")
            print(f"   Reproducible: {'✓ YES' if summary['reproducible'] else '✗ NO'}")
            
            return summary
        
        return {"error": "No fidelity results computed"}


def main():
    """Main entry point for validation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="IBM Quantum Teleportation Rerun Validator")
    parser.add_argument("--num-reruns", type=int, default=4, help="Number of rerun jobs (default: 4)")
    parser.add_argument("--shots", type=int, default=1024, help="Shots per job (default: 1024)")
    parser.add_argument("--backend", type=str, default=None, help="Specific backend name")
    parser.add_argument("--output-dir", type=str, default="teleportation_rerun_validation", help="Output directory")
    parser.add_argument("--token", type=str, default=None, help="IBM Quantum API token")
    
    args = parser.parse_args()
    
    # Create validator
    validator = TeleportationRerunValidator(output_dir=args.output_dir)
    
    # Run validation
    result = validator.run_full_validation(
        num_reruns=args.num_reruns,
        shots=args.shots,
        backend_name=args.backend
    )
    
    # Print final result
    print(f"\n{'='*100}")
    print("FINAL RESULT:")
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()