"""
Parity Witness 3-Qubit Circuit (PW-3Q)

Parity extraction circuit for correlation-based tamper detection.
Data qubits (D0, D1) with parity ancilla (A).

Reference: research/quantum_security/parity_witness_tamper/CIRCUIT_FAMILIES.md
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, List

import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister


class InterceptionMode(Enum):
    """Interception mode for the circuit."""
    NONE = "none"
    D0 = "d0"        # Measure D0 before parity extraction
    D1 = "d1"        # Measure D1 before parity extraction
    BOTH = "both"    # Measure both D0 and D1


class CircuitVariant(Enum):
    """Circuit variant type."""
    BASIC = "basic"           # PW-3Q: Basic parity witness
    ENTANGLED = "entangled"   # PW-3Q-E: Entangled data qubits
    COHERENCE = "coherence"   # PW-3Q-C: Phase-sensitive


@dataclass
class PW3QConfig:
    """Configuration for PW-3Q circuit."""
    shots: int = 8192
    variant: CircuitVariant = CircuitVariant.BASIC
    interception_mode: InterceptionMode = InterceptionMode.NONE
    measure_all: bool = False  # If True, measure all qubits for joint analysis
    phase_angle: Optional[float] = None  # For coherence variant


def create_pw_3q_circuit(
    config: Optional[PW3QConfig] = None,
    interception_mode: Optional[InterceptionMode] = None,
    variant: Optional[CircuitVariant] = None
) -> QuantumCircuit:
    """
    Create the 3-qubit parity witness circuit.
    
    Topology (Basic):
        D0 ────H────■────
                    │
        D1 ────H────■────
                    │
        A  ────────X──── H ──── M
    
    Args:
        config: Circuit configuration (optional)
        interception_mode: Override interception mode from config
        variant: Override circuit variant from config
        
    Returns:
        QuantumCircuit with appropriate measurements
    """
    if config is None:
        config = PW3QConfig()
    
    if interception_mode is not None:
        config.interception_mode = interception_mode
    if variant is not None:
        config.variant = variant
    
    # Create registers
    # q[0] = D0 (data qubit 0)
    # q[1] = D1 (data qubit 1)
    # q[2] = A  (parity ancilla)
    q = QuantumRegister(3, name='q')
    
    if config.measure_all:
        c = ClassicalRegister(3, name='c')
    else:
        c = ClassicalRegister(1, name='c')
    
    circuit = QuantumCircuit(q, c, name=f'PW-3Q-{config.variant.value}')
    
    # Step 1: Prepare data qubits
    if config.variant == CircuitVariant.ENTANGLED:
        # Create Bell pair between D0 and D1
        circuit.h(q[0])
        circuit.cx(q[0], q[1])
    else:
        # Independent superposition
        circuit.h(q[0])
        circuit.h(q[1])
    
    # Step 2: Handle interception (intermediate measurement)
    if config.interception_mode == InterceptionMode.D0:
        if not config.measure_all:
            c_intercept = ClassicalRegister(1, name='c_intercept')
            circuit.add_register(c_intercept)
            circuit.measure(q[0], c_intercept[0])
        else:
            circuit.measure(q[0], c[0])
    
    elif config.interception_mode == InterceptionMode.D1:
        if not config.measure_all:
            c_intercept = ClassicalRegister(1, name='c_intercept')
            circuit.add_register(c_intercept)
            circuit.measure(q[1], c_intercept[0])
        else:
            circuit.measure(q[1], c[1])
    
    elif config.interception_mode == InterceptionMode.BOTH:
        if not config.measure_all:
            c_intercept = ClassicalRegister(2, name='c_intercept')
            circuit.add_register(c_intercept)
            circuit.measure(q[0], c_intercept[0])
            circuit.measure(q[1], c_intercept[1])
        else:
            circuit.measure(q[0], c[0])
            circuit.measure(q[1], c[1])
    
    # Step 3: Extract parity to ancilla
    circuit.cx(q[0], q[2])
    circuit.cx(q[1], q[2])
    
    # Step 4: Apply phase rotation for coherence variant
    if config.variant == CircuitVariant.COHERENCE and config.phase_angle is not None:
        circuit.rz(config.phase_angle, q[0])
        circuit.rz(config.phase_angle, q[1])
    
    # Step 5: Parity measurement
    circuit.h(q[2])
    
    if config.measure_all:
        circuit.measure(q, c)
    else:
        circuit.measure(q[2], c[0])
    
    return circuit


def create_pw_4q_circuit(
    interception_side: Optional[str] = None
) -> QuantumCircuit:
    """
    Create the 4-qubit mirrored parity witness circuit.
    
    Topology:
        D0 ────■────
               │
        D1 ────■────
               │
        A_L ───X──── H ──── M_L
        
        D2 ────■────
               │
        D3 ────■────
               │
        A_R ───X──── H ──── M_R
    
    Args:
        interception_side: Which side to intercept (None, 'left', 'right', 'both')
        
    Returns:
        QuantumCircuit with appropriate measurements
    """
    q = QuantumRegister(6, name='q')
    # q[0] = D0, q[1] = D1, q[2] = A_L (left side)
    # q[3] = D2, q[4] = D3, q[5] = A_R (right side)
    c = ClassicalRegister(2, name='c')
    circuit = QuantumCircuit(q, c, name='PW-4Q')
    
    # Left side
    circuit.h(q[0])
    circuit.h(q[1])
    
    # Right side
    circuit.h(q[3])
    circuit.h(q[4])
    
    # Handle interception
    if interception_side in ('left', 'both'):
        c_intercept = ClassicalRegister(2, name='c_intercept_l')
        circuit.add_register(c_intercept)
        circuit.measure(q[0], c_intercept[0])
        circuit.measure(q[1], c_intercept[1])
    
    if interception_side in ('right', 'both'):
        c_intercept_r = ClassicalRegister(2, name='c_intercept_r')
        circuit.add_register(c_intercept_r)
        circuit.measure(q[3], c_intercept_r[0])
        circuit.measure(q[4], c_intercept_r[1])
    
    # Left parity extraction
    circuit.cx(q[0], q[2])
    circuit.cx(q[1], q[2])
    circuit.h(q[2])
    
    # Right parity extraction
    circuit.cx(q[3], q[5])
    circuit.cx(q[4], q[5])
    circuit.h(q[5])
    
    # Measure ancillas
    circuit.measure(q[2], c[0])
    circuit.measure(q[5], c[1])
    
    return circuit


def create_coherence_sweep_circuits(
    phase_angles: List[float],
    interception_mode: InterceptionMode = InterceptionMode.NONE
) -> List[QuantumCircuit]:
    """
    Create a set of coherence-sensitive circuits for phase sweep.
    
    Args:
        phase_angles: List of phase angles to test
        interception_mode: Interception mode
        
    Returns:
        List of circuits, one per phase angle
    """
    circuits = []
    for angle in phase_angles:
        config = PW3QConfig(
            variant=CircuitVariant.COHERENCE,
            interception_mode=interception_mode,
            phase_angle=angle
        )
        circuits.append(create_pw_3q_circuit(config))
    return circuits


def get_circuit_info(circuit: QuantumCircuit) -> dict:
    """
    Get information about a PW circuit.
    
    Args:
        circuit: The quantum circuit
        
    Returns:
        Dictionary with circuit information
    """
    return {
        'name': circuit.name,
        'num_qubits': circuit.num_qubits,
        'depth': circuit.depth(),
        'num_gates': len(circuit.data),
        'gate_types': {
            instr.operation.name: sum(
                1 for i in circuit.data if i.operation.name == instr.operation.name
            )
            for instr in circuit.data
        }
    }


if __name__ == '__main__':
    # Demo: Create all circuit variants
    print("PW-3Q Circuit Variants")
    print("=" * 50)
    
    for variant in CircuitVariant:
        for mode in [InterceptionMode.NONE, InterceptionMode.D0]:
            config = PW3QConfig(variant=variant, interception_mode=mode)
            circuit = create_pw_3q_circuit(config)
            info = get_circuit_info(circuit)
            print(f"\n{variant.value.upper()} - {mode.value}:")
            print(f"  Qubits: {info['num_qubits']}")
            print(f"  Depth: {info['depth']}")
            print(f"  Gates: {info['num_gates']}")
            print(circuit.draw(fold=60))
    
    print("\n" + "=" * 50)
    print("PW-4Q Mirrored Circuit")
    circuit_4q = create_pw_4q_circuit()
    print(circuit_4q.draw(fold=60))