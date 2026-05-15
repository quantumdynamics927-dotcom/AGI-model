"""
Observer Symmetry 3-Qubit Circuit (OBS-3Q)

Bilateral topology for testing symmetry-breaking detection.
Left reservoir (Q0) and Right reservoir (Q2) entangled with Center observer (Q1).

Reference: research/quantum_security/observer_symmetry/CIRCUIT_FAMILIES.md
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister


class InterceptionMode(Enum):
    """Interception mode for the circuit."""

    NONE = "none"
    LEFT = "left"  # Measure Q0 before center measurement
    RIGHT = "right"  # Measure Q2 before center measurement
    BILATERAL = "bilateral"  # Measure both Q0 and Q2


@dataclass
class OBS3QConfig:
    """Configuration for OBS-3Q circuit."""

    shots: int = 8192
    interception_mode: InterceptionMode = InterceptionMode.NONE
    measure_all: bool = False  # If True, measure all qubits for entropy mode


def create_obs_3q_circuit(
    config: Optional[OBS3QConfig] = None,
    interception_mode: Optional[InterceptionMode] = None,
) -> QuantumCircuit:
    """
    Create the 3-qubit bilateral observer circuit.

    Topology:
        Q0 (Left) ────■────
                      │
        Q1 (Center) ──X──── H ──── M
                      │
        Q2 (Right) ───■────

    Args:
        config: Circuit configuration (optional)
        interception_mode: Override interception mode from config

    Returns:
        QuantumCircuit with appropriate measurements
    """
    if config is None:
        config = OBS3QConfig()

    if interception_mode is not None:
        config.interception_mode = interception_mode

    # Create registers
    q = QuantumRegister(3, name="q")

    if config.measure_all:
        c = ClassicalRegister(3, name="c")
    else:
        c = ClassicalRegister(1, name="c")

    circuit = QuantumCircuit(q, c, name="OBS-3Q")

    # Step 1: Initialize bilateral structure
    circuit.h(q[0])  # Left reservoir
    circuit.h(q[2])  # Right reservoir

    # Step 2: Entangle with center
    circuit.cx(q[0], q[1])  # Left -> Center
    circuit.cx(q[2], q[1])  # Right -> Center

    # Step 3: Handle interception (intermediate measurement)
    if config.interception_mode == InterceptionMode.LEFT:
        # Add classical register for interceptor if not measuring all
        if not config.measure_all:
            c_intercept = ClassicalRegister(1, name="c_intercept")
            circuit.add_register(c_intercept)
            circuit.measure(q[0], c_intercept[0])
        else:
            # Measure Q0 early (will be overwritten by final measurement)
            circuit.measure(q[0], c[0])

    elif config.interception_mode == InterceptionMode.RIGHT:
        if not config.measure_all:
            c_intercept = ClassicalRegister(1, name="c_intercept")
            circuit.add_register(c_intercept)
            circuit.measure(q[2], c_intercept[0])
        else:
            circuit.measure(q[2], c[2])

    elif config.interception_mode == InterceptionMode.BILATERAL:
        if not config.measure_all:
            c_intercept = ClassicalRegister(2, name="c_intercept")
            circuit.add_register(c_intercept)
            circuit.measure(q[0], c_intercept[0])
            circuit.measure(q[2], c_intercept[1])
        else:
            circuit.measure(q[0], c[0])
            circuit.measure(q[2], c[2])

    # Step 4: Observer measurement
    circuit.h(q[1])  # Hadamard on center

    # Final measurement
    if config.measure_all:
        circuit.measure(q, c)
    else:
        circuit.measure(q[1], c[0])

    return circuit


def create_obs_5q_circuit(
    mirror_depth: int = 2, interception_qubits: Optional[list[int]] = None
) -> QuantumCircuit:
    """
    Create the 5-qubit mirrored topology circuit.

    Topology (mirror_depth=2):
        Q0 (Left-1) ────■────
                       │
        Q1 (Left-2) ───■─────■────
                             │
        Q2 (Center) ─────────X──── H ──── M
                             │
        Q3 (Right-2) ──■─────■────
                       │
        Q4 (Right-1) ──■────

    Args:
        mirror_depth: Number of qubits per side (1-4)
        interception_qubits: List of qubit indices to intercept

    Returns:
        QuantumCircuit with appropriate measurements
    """
    n_qubits = 2 * mirror_depth + 1
    center_idx = mirror_depth

    q = QuantumRegister(n_qubits, name="q")
    c = ClassicalRegister(1, name="c")
    circuit = QuantumCircuit(q, c, name=f"OBS-{n_qubits}Q")

    # Initialize all reservoir qubits
    for i in range(n_qubits):
        if i != center_idx:
            circuit.h(q[i])

    # Entangle left side with center
    for i in range(center_idx):
        circuit.cx(q[i], q[center_idx])

    # Entangle right side with center
    for i in range(center_idx + 1, n_qubits):
        circuit.cx(q[i], q[center_idx])

    # Handle interception
    if interception_qubits:
        c_intercept = ClassicalRegister(len(interception_qubits), name="c_intercept")
        circuit.add_register(c_intercept)
        for idx, qubit in enumerate(interception_qubits):
            circuit.measure(q[qubit], c_intercept[idx])

    # Observer measurement
    circuit.h(q[center_idx])
    circuit.measure(q[center_idx], c[0])

    return circuit


def get_circuit_info(circuit: QuantumCircuit) -> dict:
    """
    Get information about an OBS circuit.

    Args:
        circuit: The quantum circuit

    Returns:
        Dictionary with circuit information
    """
    return {
        "name": circuit.name,
        "num_qubits": circuit.num_qubits,
        "depth": circuit.depth(),
        "num_gates": len(circuit.data),
        "gate_types": {
            instr.operation.name: sum(
                1 for i in circuit.data if i.operation.name == instr.operation.name
            )
            for instr in circuit.data
        },
    }


if __name__ == "__main__":
    # Demo: Create all circuit variants
    print("OBS-3Q Circuit Variants")
    print("=" * 50)

    for mode in InterceptionMode:
        config = OBS3QConfig(interception_mode=mode)
        circuit = create_obs_3q_circuit(config)
        info = get_circuit_info(circuit)
        print(f"\n{mode.value.upper()} mode:")
        print(f"  Qubits: {info['num_qubits']}")
        print(f"  Depth: {info['depth']}")
        print(f"  Gates: {info['num_gates']}")
        print(circuit.draw(fold=60))

    print("\n" + "=" * 50)
    print("OBS-5Q Circuit (mirror_depth=2)")
    circuit_5q = create_obs_5q_circuit()
    print(circuit_5q.draw(fold=60))
