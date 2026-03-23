"""Node 9 — QVAE Bridge (Merkabah)

Platonic Solid: Merkabah (Star Tetrahedron)
Role: Quantum VAE Bridge, Hilbert space mapping, and Qiskit integration.

The Merkabah represents the intersection of spirit and matter (tetrahedrons),
bridging classical and quantum realms.
"""

from typing import List, Optional, Sequence, Dict, Any
import math
import logging
import numpy as np
import time
import json
import threading

# Import core constants, falling back to a default if not found
try:
    from TMT_OS.node1_base_os import PHI
except (ImportError, ModuleNotFoundError):
    PHI = 1.618033988749895

logger = logging.getLogger("node9_qvae_bridge")
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("%(asctime)s [Node9-QVAE] %(message)s"))
    logger.addHandler(ch)

DEFAULT_QUBITS = 127


class MerkabahGeometry:
    """Represents the Merkabah (Star Tetrahedron) geometry for Node 9."""

    def __init__(self):
        self.vertices = 8
        self.faces = 24
        self.edges = 12  # The 12 edges of the two tetrahedrons
        self.tetra_sun_vertices = [(1, 1, 1), (-1, -1, 1), (-1, 1, -1), (1, -1, -1)]
        self.tetra_earth_vertices = [(-1, -1, -1), (1, 1, -1), (1, -1, 1), (-1, 1, 1)]

    def get_info(self) -> Dict[str, Any]:
        """Returns the geometric properties of the Merkabah."""
        return {"vertices": self.vertices, "faces": self.faces, "edges": self.edges}


class MockQuantumBackend:
    """A mock quantum backend to simulate job execution without needing qiskit-ibm-runtime."""

    def __init__(self, backend_name: str = "mock_simulator"):
        self.backend_name = backend_name
        logger.info(f"Mock backend '{self.backend_name}' initialized.")

    def run(self, circuit: Any, shots: int = 1024) -> Dict[str, Any]:
        """Simulates running a circuit and returns a mock result with random bitstrings."""
        if not circuit:
            return {"success": False, "counts": {}}

        num_qubits = circuit.num_qubits
        counts = {}
        for _ in range(shots):
            bitstring = "".join(np.random.choice(["0", "1"], size=num_qubits))
            counts[bitstring] = counts.get(bitstring, 0) + 1
        return {"success": True, "counts": counts}


class QVAEBridge:
    """
    Node 9: QVAE Bridge
    Maps classical latent spaces to Quantum Hilbert spaces and manages simulated quantum jobs.
    """

    def __init__(self):
        self.node_id = 9
        self.node_name = "qvae_bridge"
        self.platonic_solid = "Merkabah"
        self.role = "QVAE Bridge: maps classical latent space to Wedjat Hilbert space"

        self.geometry = MerkabahGeometry()
        self.jobs: Dict[str, Dict[str, Any]] = {}
        self.mock_backend = MockQuantumBackend()

        logger.info("Node 9 (QVAE Bridge) initialized with Merkabah geometry.")

    def _import_qiskit(self):
        """Safely imports Qiskit, returning None if it's not available."""
        try:
            from qiskit import QuantumCircuit, QuantumRegister

            return QuantumCircuit, QuantumRegister
        except Exception as e:
            logger.warning(
                "Qiskit import failed: %s. Circuit generation will be unavailable.", e
            )
            return None, None

    def create_wedjat_qvae_circuit(self, num_qubits: int = DEFAULT_QUBITS) -> Any:
        """Builds the WEDJAT-127-Φ QVAE kernel circuit."""
        QuantumCircuit, QuantumRegister = self._import_qiskit()
        if not QuantumCircuit:
            return None

        try:
            qc = QuantumCircuit(num_qubits)
        except TypeError:
            qr = QuantumRegister(num_qubits, "wedjat")
            qc = QuantumCircuit(qr)

        frac = (PHI**num_qubits) % 1.0
        ry_angle = 2.0 * math.pi * frac
        for i in range(num_qubits):
            qc.h(i)
            qc.ry(ry_angle, i)

        qc.barrier()
        return qc

    def map_classical_to_quantum(self, latent_vector: List[float]) -> Any:
        """
        Maps a classical latent vector to a quantum circuit by parameterizing gates.
        This represents a simplified Hilbert space transformation.
        """
        if not latent_vector:
            logger.warning("Input latent vector is empty. Cannot create a circuit.")
            return None

        num_qubits = DEFAULT_QUBITS
        qc = self.create_wedjat_qvae_circuit(num_qubits)
        if not qc:
            return {"error": "Qiskit not available"}

        angles = self._map_latent_to_rotations(latent_vector, num_qubits)

        for i, angle in enumerate(angles):
            qc.ry(angle, i)

        return qc

    def _map_latent_to_rotations(
        self, latent: Sequence[float], num_qubits: int
    ) -> List[float]:
        """Helper to map a classical vector to a series of per-qubit rotation angles."""
        angles = []
        for i in range(num_qubits):
            v = float(latent[i % len(latent)])
            angle = (math.tanh(v) + 1.0) * math.pi  # Scale to [0, 2*pi]
            angles.append(angle)
        return angles

    def _simulate_job_execution(self, job_id: str, circuit: Any, shots: int):
        """A private method to simulate the lifecycle of a quantum job in the background."""
        if job_id not in self.jobs:
            return

        time.sleep(0.05)

        self.jobs[job_id]["status"] = "running"
        logger.info(f"Job {job_id} is now 'running' on the mock backend.")

        time.sleep(np.random.uniform(0.5, 2.0))

        result = self.mock_backend.run(circuit, shots)

        if result["success"]:
            self.jobs[job_id]["status"] = "completed"
            self.jobs[job_id]["result"] = result["counts"]
            logger.info(f"Job {job_id} completed successfully.")
        else:
            self.jobs[job_id]["status"] = "failed"
            self.jobs[job_id]["error_message"] = "Simulation failed"
            logger.error(f"Job {job_id} failed during simulation.")

    def submit_job(
        self, circuit: Any, backend_name: str = "mock_simulator", shots: int = 1024
    ) -> str:
        """
        Submits a quantum job for simulated execution in a background thread.
        """
        job_id = f"qvae_job_{int(time.time() * 1000)}"

        status = "queued"
        if not circuit or isinstance(circuit, dict):
            status = "failed"

        self.jobs[job_id] = {
            "job_id": job_id,
            "status": status,
            "backend": backend_name,
            "shots": shots,
            "timestamp": time.time(),
        }

        if status == "queued":
            thread = threading.Thread(
                target=self._simulate_job_execution, args=(job_id, circuit, shots)
            )
            thread.daemon = True
            thread.start()

        logger.info(f"Job {job_id} submitted with status: {status}")
        return job_id

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves the status and results (if available) of a submitted job."""
        return self.jobs.get(job_id)

    def get_health_status(self) -> Dict[str, Any]:
        """Returns the current health and operational status of the node."""
        active_jobs = sum(
            1 for j in self.jobs.values() if j.get("status") in ["queued", "running"]
        )
        completed_jobs = sum(
            1 for j in self.jobs.values() if j.get("status") == "completed"
        )
        return {
            "node_id": self.node_id,
            "node_name": self.node_name,
            "status": "active",
            "platonic_solid": self.platonic_solid,
            "geometry": self.geometry.get_info(),
            "active_jobs": active_jobs,
            "completed_jobs": completed_jobs,
            "total_jobs": len(self.jobs),
        }


_BRIDGE_INSTANCE = None


def get_bridge():
    """Singleton pattern to provide a global bridge instance."""
    global _BRIDGE_INSTANCE
    if _BRIDGE_INSTANCE is None:
        _BRIDGE_INSTANCE = QVAEBridge()
    return _BRIDGE_INSTANCE


def main():
    """Demonstrates the enhanced functionality of the QVAEBridge."""
    print("=" * 70)
    print("Node 9: QVAE Bridge (Enhanced Demo)")
    bridge = get_bridge()
    print(f"Platonic Solid: {bridge.platonic_solid}")
    print("=" * 70)

    # 1. Create a classical latent vector
    latent_vector = np.random.rand(10).tolist()
    print(
        f"\n1. Classical latent vector (10-dim): {['%.3f' % v for v in latent_vector[:5]]}..."
    )

    # 2. Map to a quantum circuit
    print("\n2. Mapping vector to a WEDJAT quantum circuit...")
    qc = bridge.map_classical_to_quantum(latent_vector)
    if not qc or isinstance(qc, dict):
        print(
            f"   Circuit creation failed. Error: {qc.get('error', 'Unknown') if qc else 'Qiskit not found'}"
        )
        return

    print(f"   Circuit created with {qc.num_qubits} qubits.")

    # 3. Submit the job for simulated execution
    print("\n3. Submitting job to mock quantum backend...")
    job_id = bridge.submit_job(qc)
    print(f"   Submitted job with ID: {job_id}")

    # 4. Monitor job status until it completes
    print("\n4. Monitoring job status...")
    while True:
        status_info = bridge.get_job_status(job_id)
        if not status_info:
            print("   Error: Job ID not found.")
            break

        current_status = status_info["status"]
        print(f"   Current status of {job_id}: {current_status}")

        if current_status in ["completed", "failed"]:
            print("\n5. Final job results:")
            # Only show a few results to keep output clean
            if "result" in status_info and status_info["result"]:
                result_preview = dict(list(status_info["result"].items())[:3])
                status_info["result"] = (
                    f"{result_preview} ... ({len(status_info['result'])} total outcomes)"
                )
            print(json.dumps(status_info, indent=2, default=str))
            break

        time.sleep(0.5)

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
