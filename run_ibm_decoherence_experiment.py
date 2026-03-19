"""Design and optionally run a decoherence experiment on IBM Quantum.

This branch operationalizes the phi-side recommendation from the research
loop: apply a controlled information-decoherence pulse, then measure collapse
kinetics through parity loss, entropy growth, and Hamming-weight kurtosis.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


PHI = 1.618033988749895
DEFAULT_BACKEND = "ibm_fez"
DEFAULT_OUTPUT = "ibm_decoherence_experiment.json"


try:
    from qiskit import QuantumCircuit
    from qiskit.transpiler.preset_passmanagers import (
        generate_preset_pass_manager,
    )

    QISKIT_AVAILABLE = True
except ImportError:
    QuantumCircuit = None
    generate_preset_pass_manager = None
    QISKIT_AVAILABLE = False


try:
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

    IBM_RUNTIME_AVAILABLE = True
except ImportError:
    QiskitRuntimeService = None
    SamplerV2 = None
    IBM_RUNTIME_AVAILABLE = False


@dataclass(frozen=True)
class DecoherenceSweepPoint:
    label: str
    delay_ns: int
    pulse_repetitions: int
    phase_kick_rad: float
    expected_regime: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_default_sweep() -> list[DecoherenceSweepPoint]:
    return [
        DecoherenceSweepPoint(
            label="control",
            delay_ns=0,
            pulse_repetitions=0,
            phase_kick_rad=0.0,
            expected_regime="reference coherence",
        ),
        DecoherenceSweepPoint(
            label="mild",
            delay_ns=128,
            pulse_repetitions=1,
            phase_kick_rad=PHI / 32.0,
            expected_regime="small coherence drop",
        ),
        DecoherenceSweepPoint(
            label="moderate",
            delay_ns=256,
            pulse_repetitions=2,
            phase_kick_rad=PHI / 16.0,
            expected_regime="measurable parity collapse",
        ),
        DecoherenceSweepPoint(
            label="strong",
            delay_ns=512,
            pulse_repetitions=3,
            phase_kick_rad=PHI / 8.0,
            expected_regime="rapid integration loss",
        ),
        DecoherenceSweepPoint(
            label="collapse",
            delay_ns=1024,
            pulse_repetitions=4,
            phase_kick_rad=PHI / 4.0,
            expected_regime="classicalized distribution",
        ),
    ]


def build_experiment_spec(
    num_qubits: int,
    shots: int,
    backend_name: str,
) -> dict[str, Any]:
    sweep = build_default_sweep()
    return {
        "timestamp": datetime.now(UTC).isoformat(timespec="seconds"),
        "objective": (
            "Measure causal-integration collapse kinetics under controlled "
            "decoherence pulses."
        ),
        "backend": backend_name,
        "num_qubits": num_qubits,
        "shots": shots,
        "probe_state": "phi-phased GHZ chain",
        "measurement_bases": ["z_population", "x_coherence"],
        "collapse_metrics": [
            "parity_expectation",
            "distribution_entropy",
            "hamming_weight_kurtosis",
            "dominant_bitstring_probability",
        ],
        "hypothesis": (
            "Increasing delay and phase-kick depth should reduce X-basis "
            "parity, increase entropy, and flatten Hamming-weight kurtosis "
            "before the distribution fully classicalizes."
        ),
        "sweep": [point.to_dict() for point in sweep],
    }


def _require_qiskit() -> None:
    if not QISKIT_AVAILABLE:
        raise RuntimeError(
            "Qiskit is not available. Install qiskit to build experiment "
            "circuits."
        )


def create_phi_probe_circuit(
    num_qubits: int,
    sweep_point: DecoherenceSweepPoint,
    measurement_basis: str,
) -> QuantumCircuit:
    _require_qiskit()
    circuit = QuantumCircuit(num_qubits, num_qubits)

    circuit.h(0)
    circuit.rz(PHI, 0)
    for qubit in range(1, num_qubits):
        circuit.cx(0, qubit)
        circuit.rz(PHI / (qubit + 1), qubit)
    circuit.barrier()

    for repetition in range(sweep_point.pulse_repetitions):
        for qubit in range(num_qubits):
            if sweep_point.delay_ns > 0:
                circuit.delay(sweep_point.delay_ns, qubit, unit="ns")
            if sweep_point.phase_kick_rad > 0:
                direction = 1.0 if (qubit + repetition) % 2 == 0 else -1.0
                circuit.rx(direction * sweep_point.phase_kick_rad, qubit)
        circuit.barrier()

    if measurement_basis == "x_coherence":
        for qubit in range(num_qubits):
            circuit.h(qubit)
    elif measurement_basis != "z_population":
        raise ValueError(f"Unsupported measurement basis: {measurement_basis}")

    circuit.measure(range(num_qubits), range(num_qubits))
    return circuit


def build_circuit_family(num_qubits: int) -> list[dict[str, Any]]:
    family: list[dict[str, Any]] = []
    for sweep_point in build_default_sweep():
        for basis in ("z_population", "x_coherence"):
            entry = {
                "label": sweep_point.label,
                "measurement_basis": basis,
                "delay_ns": sweep_point.delay_ns,
                "pulse_repetitions": sweep_point.pulse_repetitions,
                "phase_kick_rad": sweep_point.phase_kick_rad,
                "expected_regime": sweep_point.expected_regime,
            }
            if QISKIT_AVAILABLE:
                circuit = create_phi_probe_circuit(
                    num_qubits,
                    sweep_point,
                    basis,
                )
                entry["num_gates"] = len(circuit)
                entry["depth"] = circuit.depth()
            family.append(entry)
    return family


def summarize_counts(counts: dict[str, int], shots: int) -> dict[str, float]:
    if not counts or shots <= 0:
        return {
            "parity_expectation": 0.0,
            "distribution_entropy": 0.0,
            "hamming_weight_kurtosis": 0.0,
            "dominant_bitstring_probability": 0.0,
        }

    probabilities = {
        bitstring: count / shots
        for bitstring, count in counts.items()
    }
    entropy = 0.0
    parity_expectation = 0.0
    hamming_values: list[tuple[int, float]] = []
    dominant_probability = 0.0

    for bitstring, probability in probabilities.items():
        weight = bitstring.count("1")
        hamming_values.append((weight, probability))
        entropy -= probability * math.log2(probability)
        parity_expectation += ((-1) ** weight) * probability
        dominant_probability = max(dominant_probability, probability)

    mean_weight = sum(
        weight * probability
        for weight, probability in hamming_values
    )
    variance = sum(
        ((weight - mean_weight) ** 2) * probability
        for weight, probability in hamming_values
    )
    if variance <= 1e-12:
        kurtosis = 0.0
    else:
        fourth_moment = sum(
            ((weight - mean_weight) ** 4) * probability
            for weight, probability in hamming_values
        )
        kurtosis = fourth_moment / (variance ** 2)

    return {
        "parity_expectation": round(parity_expectation, 6),
        "distribution_entropy": round(entropy, 6),
        "hamming_weight_kurtosis": round(kurtosis, 6),
        "dominant_bitstring_probability": round(dominant_probability, 6),
    }


def run_on_ibm(
    num_qubits: int,
    shots: int,
    backend_name: str,
) -> dict[str, Any]:
    _require_qiskit()
    if not IBM_RUNTIME_AVAILABLE:
        raise RuntimeError(
            "qiskit-ibm-runtime is not available. Install it to submit "
            "hardware jobs."
        )

    service = QiskitRuntimeService(channel="ibm_quantum")
    backend = service.backend(backend_name)
    circuits: list[QuantumCircuit] = []
    circuit_metadata: list[dict[str, Any]] = []

    for sweep_point in build_default_sweep():
        for basis in ("z_population", "x_coherence"):
            circuit = create_phi_probe_circuit(num_qubits, sweep_point, basis)
            circuits.append(circuit)
            circuit_metadata.append(
                {
                    "label": sweep_point.label,
                    "measurement_basis": basis,
                    "delay_ns": sweep_point.delay_ns,
                    "pulse_repetitions": sweep_point.pulse_repetitions,
                    "phase_kick_rad": sweep_point.phase_kick_rad,
                }
            )

    pass_manager = generate_preset_pass_manager(
        optimization_level=2,
        backend=backend,
    )
    transpiled_circuits = [pass_manager.run(circuit) for circuit in circuits]
    sampler = SamplerV2(backend=backend)
    job = sampler.run(transpiled_circuits, shots=shots)
    result = job.result()

    measurements: list[dict[str, Any]] = []
    for index, metadata in enumerate(circuit_metadata):
        counts = result[index].data.c.get_counts()
        measurements.append(
            {
                **metadata,
                "counts": counts,
                "summary_metrics": summarize_counts(counts, shots),
            }
        )

    return {
        "job_id": job.job_id(),
        "backend": backend_name,
        "shots": shots,
        "measurements": measurements,
    }


def write_output(payload: dict[str, Any], output_path: str) -> Path:
    output_file = Path(output_path).resolve()
    output_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return output_file


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Design or run an IBM Quantum decoherence experiment",
    )
    parser.add_argument("--num-qubits", type=int, default=8)
    parser.add_argument("--shots", type=int, default=4096)
    parser.add_argument("--backend", type=str, default=DEFAULT_BACKEND)
    parser.add_argument(
        "--output",
        type=str,
        default=DEFAULT_OUTPUT,
        help="JSON file for the experiment spec or run output",
    )
    parser.add_argument(
        "--run",
        action="store_true",
        help="Submit the designed circuit family to IBM Quantum",
    )
    args = parser.parse_args()

    experiment_spec = build_experiment_spec(
        num_qubits=args.num_qubits,
        shots=args.shots,
        backend_name=args.backend,
    )
    experiment_spec["circuit_family"] = build_circuit_family(args.num_qubits)

    if args.run:
        experiment_spec["hardware_run"] = run_on_ibm(
            num_qubits=args.num_qubits,
            shots=args.shots,
            backend_name=args.backend,
        )

    output_file = write_output(experiment_spec, args.output)
    print(f"Wrote decoherence experiment plan to {output_file}")
    if args.run:
        print(
            f"Submitted decoherence sweep to {args.backend} with job "
            f"{experiment_spec['hardware_run']['job_id']}"
        )
    else:
        print("Design-only mode completed; no IBM Quantum job was submitted.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
