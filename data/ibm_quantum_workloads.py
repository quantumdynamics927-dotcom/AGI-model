"""
IBM Quantum Workload Data Loader

Parses real quantum circuit execution results from IBM Quantum hardware.
These workloads contain qiskit sampler results from actual hardware backends.

Source: E:/Descargas/workloads*.zip + all_time-workloads*.csv files.
Each workload ZIP contains:
  - job-<id>-info.json   — job metadata (backend, status, created, cost)
  - job-<id>-result.json — qiskit.primitives.SamplerPubResult with BitArray outcomes

The CSV files contain aggregate workload metadata (QPU, region, usage time, status).
"""

import argparse
import json
import zipfile
import base64
import zlib
import io
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import numpy as np


# ── Constants ─────────────────────────────────────────────────────────────────

IBM_BACKENDS = {
    "ibm_fez": "IBM Fez (127 qubits, Heron r3)",
    "ibm_marrakesh": "IBM Marrakesh (127 qubits, Eagle r3)",
    "ibm_torino": "IBM Torino (133 qubits, photonic)",
    "ibm_kyiv": "IBM Kyiv (127 qubits, Eagle r3)",
    "ibm_brisbane": "IBM Brisbane (127 qubits, Eagle r3)",
    "ibm_osaka": "IBM Osaka (127 qubits, Eagle r3)",
    "ibm_nairobi": "IBM Nairobi (127 qubits, Eagle r3)",
    "ibm_casablanca": "IBM Casablanca (127 qubits, Eagle r3)",
}

SFREQ_APPROX = 1e9  # IBM reports usage in nanoseconds


# ── Dataclasses ─────────────────────────────────────────────────────────────

@dataclass
class IBMJobResult:
    job_id: str
    backend: str
    status: str
    created: str
    completed: Optional[str]
    cost: int  # IBM Quantum cost units
    usage_ns: int
    num_qubits: int
    circuit_depth: int
    num_shots: int
    # Measurement outcome statistics
    outcome_counts: Dict[str, int]
    total_shots: int
    raw_result: Dict  # full result JSON (if needed)


@dataclass
class WorkloadDataset:
    jobs: List[IBMJobResult]
    backend_counts: Dict[str, int]
    date_range: Tuple[str, str]
    total_shots: int


# ── Core Parsers ────────────────────────────────────────────────────────────

def _decode_qiskit_bytes(encoded: str) -> bytes:
    """Decode qiskit's base64+zlib encoded bytes."""
    return zlib.decompress(base64.b64decode(encoded))


def _parse_quantum_circuit(circuit_b64: str) -> dict:
    """
    Parse a qiskit QuantumCircuit from its serialized form.
    Returns a dict with basic circuit properties.
    """
    try:
        import qiskit
        from qiskit import QuantumCircuit
        raw = _decode_qiskit_bytes(circuit_b64)
        # qiskit QuantumCircuit deserialization
        import pickle
        circuit = pickle.loads(raw)
        return {
            "num_qubits": circuit.num_qubits,
            "depth": circuit.depth(),
            "num_gates": len(circuit.data),
            "num_operations": sum(len(circuit) for _ in [1]),  # count operations
            "circuit": circuit,
        }
    except Exception:
        # Can't deserialize — return basic size estimate
        raw = _decode_qiskit_bytes(circuit_b64)
        return {
            "num_qubits": -1,
            "depth": -1,
            "num_gates": -1,
            "serialized_size_bytes": len(raw),
            "circuit": None,
        }


def _parse_bit_array(bit_array_dict: dict) -> Tuple[Dict[str, int], int]:
    """
    Parse a qiskit BitArray from its dict representation.
    Returns (outcome_counts, total_shots).
    """
    array_val = bit_array_dict.get("__value__", {})
    ndarray_b64 = array_val.get("array", {}).get("__value__", "")
    if not ndarray_b64:
        return {}, 0

    try:
        raw = _decode_qiskit_bytes(ndarray_b64)
        import numpy as np
        # Qiskit BitArray stores bits as a packed bitstring
        # Each shot is a bit; we need to unpack into integer counts
        bits = np.frombuffer(raw, dtype=np.uint8)
        n_shots = len(bits)

        # Count outcomes
        counts = {}
        for b in bits:
            outcome = str(int(b))
            counts[outcome] = counts.get(outcome, 0) + 1
        return counts, n_shots
    except Exception:
        return {}, 0


def _parse_result_json(result_json: dict) -> Tuple[Dict[str, int], int, dict]:
    """
    Parse a qiskit SamplerPubResult.
    Returns (outcome_counts, total_shots, extra_metadata).
    """
    pub_results = result_json.get("__value__", {}).get("pub_results", [])
    total_shots = 0
    all_counts = {}

    for pr in pub_results:
        data = pr.get("__value__", {}).get("data", {})
        data_val = data.get("__value__", {})
        # fields is a dict {field_name: field_value}, not a list
        fields = data_val.get("fields", {})
        if isinstance(fields, dict):
            for field_name, field_val in fields.items():
                if field_name == "reg_measure" or "measure" in field_name.lower():
                    counts, shots = _parse_bit_array(field_val)
                    all_counts.update(counts)
                    total_shots += shots

    return all_counts, total_shots, {}


def load_ibm_job_result(info_json: dict, result_json: dict) -> IBMJobResult:
    """Parse info.json + result.json into an IBMJobResult."""
    job_id = info_json.get("id", "unknown")
    backend = info_json.get("backend", "unknown")
    status = info_json.get("state", {}).get("status", "unknown")
    created = info_json.get("created", "")
    cost = info_json.get("cost", 0)

    # Usage time
    usage_ns = 0
    completed = None
    state = info_json.get("state", {})
    if "completed" in state:
        completed = state.get("completed", state.get("completed_at", ""))
        # created -> completed duration
        if completed and created:
            try:
                from datetime import datetime
                c = datetime.fromisoformat(created.replace("Z", "+00:00"))
                comp = datetime.fromisoformat(completed.replace("Z", "+00:00"))
                usage_ns = int((comp - c).total_seconds() * 1e9)
            except Exception:
                pass

    # Circuit metadata
    num_qubits = -1
    circuit_depth = -1
    num_shots = 0

    params = info_json.get("params", {})
    pubs = params.get("pubs", [])
    if pubs:
        first_pub = pubs[0]
        if isinstance(first_pub, list) and len(first_pub) >= 2:
            circuit_info = first_pub[0]
            if isinstance(circuit_info, dict) and circuit_info.get("__type__") == "QuantumCircuit":
                try:
                    parsed = _parse_quantum_circuit(circuit_info.get("__value__", ""))
                    num_qubits = parsed.get("num_qubits", -1)
                    circuit_depth = parsed.get("depth", -1)
                except Exception:
                    pass

            # Third element is num_shots
            if len(first_pub) >= 3:
                num_shots = int(first_pub[2]) if first_pub[2] else 0

    # Result outcome counts
    outcome_counts, total_shots, _ = _parse_result_json(result_json)
    if not outcome_counts and num_shots > 0:
        total_shots = num_shots

    return IBMJobResult(
        job_id=job_id,
        backend=backend,
        status=status,
        created=created,
        completed=completed,
        cost=cost,
        usage_ns=usage_ns,
        num_qubits=num_qubits,
        circuit_depth=circuit_depth,
        num_shots=num_shots,
        outcome_counts=outcome_counts,
        total_shots=total_shots,
        raw_result=result_json,
    )


def load_workloads_from_zip(zip_path: str) -> List[IBMJobResult]:
    """Load all IBM Quantum job results from a workloads ZIP file."""
    results = []
    seen_ids = set()
    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()

        # Collect info/result pairs using full filename as key to avoid collision
        info_files = {n: n for n in names if n.endswith("-info.json")}
        result_files = {n.replace("-info.json", "-result.json"): n
                        for n in names if n.endswith("-info.json")}

        for info_name, _ in info_files.items():
            result_name = info_name.replace("-info.json", "-result.json")
            if result_name not in result_files:
                continue
            try:
                info_json = json.loads(zf.read(info_name))
                result_json = json.loads(zf.read(result_name))
                job_result = load_ibm_job_result(info_json, result_json)
                # Use filename-based ID to avoid collisions with duplicate internal IDs
                key = job_result.job_id if job_result.job_id != "unknown" else info_name
                if key not in seen_ids:
                    seen_ids.add(key)
                    results.append(job_result)
            except Exception as e:
                import traceback as _tb
                tb = _tb.format_exc()
                print(f"  [WARN] Failed to parse {info_name}: {e}")
                if "too many values" in str(e):
                    print(tb)
    return results


def load_all_workloads(
    downloads_dir: str = "E:/Descargas",
    workload_pattern: str = "workloads*.zip",
) -> WorkloadDataset:
    """
    Load all IBM Quantum workload ZIPs and CSV metadata files from Downloads.
    Returns a WorkloadDataset with all parsed jobs.
    """
    from pathlib import Path
    import glob

    all_jobs = []
    backend_counts: Dict[str, int] = {}

    # Load all workload ZIPs
    pattern = str(Path(downloads_dir) / workload_pattern)
    zip_files = sorted(Path(downloads_dir).glob("workloads*.zip"))

    # Also check numbered versions
    for i in range(1, 100):
        p = Path(downloads_dir) / f"workloads ({i}).zip"
        if p.exists():
            zip_files.append(p)
            if i >= 43:
                break  # max observed was 43

    print(f"[IBM Workloads] Found {len(zip_files)} workload ZIP files")
    for zip_path in zip_files:
        try:
            jobs = load_workloads_from_zip(str(zip_path))
            all_jobs.extend(jobs)
            for job in jobs:
                backend_counts[job.backend] = backend_counts.get(job.backend, 0) + 1
            print(f"  {zip_path.name}: {len(jobs)} jobs")
        except Exception as e:
            print(f"  [WARN] Failed to load {zip_path.name}: {e}")

    # Load CSV metadata files
    csv_files = sorted(Path(downloads_dir).glob("all_time-workloads*.csv"))
    csv_jobs = 0
    for csv_path in csv_files:
        try:
            with open(csv_path, "r") as f:
                header = f.readline()
                for line in f:
                    parts = line.strip().split(",")
                    if len(parts) >= 7:
                        csv_jobs += 1
            # CSV records are already reflected in ZIPs (same source)
        except Exception as e:
            print(f"  [WARN] Failed to load CSV {csv_path.name}: {e}")
    print(f"[IBM Workloads] CSV records: {csv_jobs} (may overlap with ZIPs)")

    if not all_jobs:
        raise RuntimeError(f"No IBM Quantum workload data found in {downloads_dir}")

    # Date range
    dates = [j.created for j in all_jobs if j.created]
    dates.sort()

    dataset = WorkloadDataset(
        jobs=all_jobs,
        backend_counts=backend_counts,
        date_range=(dates[0][:10], dates[-1][:10]) if dates else ("", ""),
        total_shots=sum(j.total_shots for j in all_jobs),
    )

    print(f"[IBM Workloads] Total: {len(all_jobs)} jobs, "
          f"{dataset.total_shots} shots, "
          f"backends: {dict(list(backend_counts.items())[:5])}")
    print(f"[IBM Workloads] Date range: {dataset.date_range[0]} to {dataset.date_range[1]}")

    return dataset


# ── Analysis ─────────────────────────────────────────────────────────────────

def analyze_backend_performance(dataset: WorkloadDataset) -> Dict:
    """Compute per-backend statistics."""
    from collections import defaultdict

    by_backend = defaultdict(list)
    for job in dataset.jobs:
        by_backend[job.backend].append(job)

    stats = {}
    for backend, jobs in by_backend.items():
        usage_s = [j.usage_ns / 1e9 for j in jobs if j.usage_ns > 0]
        stats[backend] = {
            "n_jobs": len(jobs),
            "mean_usage_s": float(np.mean(usage_s)) if usage_s else 0.0,
            "std_usage_s": float(np.std(usage_s)) if usage_s else 0.0,
            "total_cost": sum(j.cost for j in jobs),
            "total_shots": sum(j.total_shots for j in jobs),
            "success_rate": sum(1 for j in jobs if j.status == "Completed") / max(len(jobs), 1),
            "mean_qubits": float(np.mean([j.num_qubits for j in jobs if j.num_qubits > 0])) if jobs else 0,
        }

    return stats


def get_outcome_distribution(dataset: WorkloadDataset) -> Dict[str, float]:
    """Get global outcome probability distribution across all jobs."""
    total_counts: Dict[str, int] = {}
    total_shots = 0
    for job in dataset.jobs:
        for outcome, count in job.outcome_counts.items():
            total_counts[outcome] = total_counts.get(outcome, 0) + count
            total_shots += count

    if total_shots == 0:
        return {}
    return {k: v / total_shots for k, v in total_counts.items()}


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="IBM Quantum workload data loader")
    parser.add_argument("--dir", default="E:/Descargas", help="Directory containing workload files")
    parser.add_argument("--stats", action="store_true", help="Print backend statistics")
    parser.add_argument("--outcomes", action="store_true", help="Print outcome distribution")
    args = parser.parse_args()

    print("=" * 60)
    print("IBM QUANTUM WORKLOAD DATA LOADER")
    print("=" * 60)

    dataset = load_all_workloads(downloads_dir=args.dir)

    print(f"\nTotal jobs loaded: {len(dataset.jobs)}")
    print(f"Date range: {dataset.date_range[0]} to {dataset.date_range[1]}")
    print(f"Total quantum shots: {dataset.total_shots:,}")
    print(f"Backend distribution: {dataset.backend_counts}")

    if args.stats:
        print("\nPer-backend performance:")
        stats = analyze_backend_performance(dataset)
        for backend, s in sorted(stats.items()):
            print(f"  {backend}:")
            print(f"    jobs={s['n_jobs']}, success={s['success_rate']:.1%}, "
                  f"mean_usage={s['mean_usage_s']:.3f}s, "
                  f"shots={s['total_shots']:,}")

    if args.outcomes:
        print("\nOutcome distribution:")
        dist = get_outcome_distribution(dataset)
        for outcome, prob in sorted(dist.items(), key=lambda x: -x[1]):
            print(f"  {outcome}: {prob:.4f}")

    # Save summary
    summary_path = "ibm_workload_summary.json"
    summary = {
        "n_jobs": len(dataset.jobs),
        "date_range": list(dataset.date_range),
        "total_shots": dataset.total_shots,
        "backend_counts": dataset.backend_counts,
        "per_backend": analyze_backend_performance(dataset),
        "outcome_distribution": get_outcome_distribution(dataset),
    }
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\n[OK] Summary saved to: {summary_path}")


if __name__ == "__main__":
    main()
