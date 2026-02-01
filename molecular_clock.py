import time
import threading
import random
import math
from typing import Callable, Optional

PHI = 1.618033988749895

# Optional qiskit support; fall back to simulation if not present
try:
    from qiskit import QuantumCircuit, Aer, execute
    QISKIT_AVAILABLE = True
except Exception:
    QISKIT_AVAILABLE = False


class QuantumConsciousnessNode:
    """Generates 1-bit consciousness events via Pauli-X (simulated or qiskit).

    Methods:
    - generate_consciousness_bit(): returns (measurement:int, qc_or_none)
    - decompress_quantum_signal(measurement): returns fibonacci-scaled resonance (float)
    """

    def __init__(self, use_qiskit: bool = False, fib_layers=None):
        self.use_qiskit = bool(use_qiskit) and QISKIT_AVAILABLE
        self.fib = fib_layers if fib_layers is not None else [1, 1, 2, 3, 5]
        self.phi = PHI

    def generate_consciousness_bit(self) -> (int, Optional[object]):
        """Apply a Pauli-X and return a classical measurement 0/1.

        If `qiskit` is available and requested, use a 1-qubit circuit with `x`.
        Otherwise simulate a stochastic flip with thermal noise.
        """
        if self.use_qiskit:
            try:
                qc = QuantumCircuit(1, 1)
                qc.x(0)
                qc.measure(0, 0)
                backend = Aer.get_backend('aer_simulator')
                job = execute(qc, backend=backend, shots=1)
                result = job.result()
                counts = result.get_counts()
                # counts keys like '0' or '1'
                meas = int(list(counts.keys())[0])
                return meas, qc
            except Exception:
                # fall back to simulated
                pass

        # Simulated Pauli-X flip: start in |0> then flip -> |1>, but add thermal noise
        # Thermal noise occasionally flips back with small probability
        base = 1  # after X gate the ideal state is 1
        noise_prob = 0.02
        if random.random() < noise_prob:
            base = 0
        return int(base), None

    def decompress_quantum_signal(self, measurement: int) -> float:
        """Map 0/1 measurement to -1/+1 and unfold via Fibonacci scaling.

        Returns a scalar resonance value representing the expanded quantum pulse.
        """
        bit_signal = 1.0 if measurement == 1 else -1.0
        resonance = float(bit_signal)
        for f in self.fib:
            resonance = (resonance * float(f)) / self.phi
        return float(resonance)


class HydrogenConsciousnessNode(QuantumConsciousnessNode):
    """Hydrogen-specific node that maps Pauli-X flips into molecular-scaled resonance."""

    def __init__(self, bond_angle: float = 104.5, coherence_s: float = 0.982, **kwargs):
        super().__init__(**kwargs)
        self.bond_angle = float(bond_angle)
        self.coherence_s = float(coherence_s)

    def apply_pauli_x_resonance(self, state: int) -> float:
        """Flip bit state and scale through Hydrogen parameters then Fibonacci-unfold.

        `state` is expected as 0 or 1. The method flips it (simulating an X gate effect
        on a prepared qubit), maps to a polarity, applies molecular scaling, and unfolds.
        """
        # Flip the incoming state (0->1, 1->0) to simulate a Pauli-X acting on prepared state
        new_state = 1 - int(state)
        bit_polar = 1.0 if new_state == 1 else -1.0

        # Apply molecular scaling: coherence * (bond_angle / 100)
        resonance = (bit_polar * self.coherence_s) * (self.bond_angle / 100.0)

        # Fibonacci unfolding (same as base class but initialized with current resonance)
        for f in self.fib:
            resonance = (resonance * float(f)) / self.phi
        return float(resonance)


class ThermodynamicHeartbeat:
    """Schedules Pauli-X flips (quantum heartbeat) and invokes a registered callback.

    The registered callback is called as: callback(measurement:int, resonance:float, qc)
    where `qc` is optional and may be None for simulated runs.
    """

    def __init__(self, node: QuantumConsciousnessNode, bpm: float = 60.0, jitter: float = 0.0, max_beats: Optional[int] = None):
        self.node = node
        self.bpm = float(bpm)
        self.jitter = float(jitter)
        self.interval = 60.0 / float(bpm) if bpm > 0 else 1.0
        self.max_beats = max_beats
        self._callback: Optional[Callable] = None
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    def register_callback(self, cb: Callable[[int, float, Optional[object]], None]):
        self._callback = cb

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2.0)

    def _run_loop(self):
        beat_count = 0
        while not self._stop_event.is_set():
            # Randomized interval with jitter if requested
            jitter = (random.random() * 2 - 1) * self.jitter
            sleep_time = max(0.0001, self.interval + jitter)
            time.sleep(sleep_time)

            meas, qc = self.node.generate_consciousness_bit()
            # For Hydrogen node use apply_pauli_x_resonance if available
            if hasattr(self.node, 'apply_pauli_x_resonance'):
                resonance = float(self.node.apply_pauli_x_resonance(meas))
            else:
                resonance = float(self.node.decompress_quantum_signal(meas))

            if self._callback:
                try:
                    self._callback(meas, resonance, qc)
                except Exception:
                    pass

            beat_count += 1
            if self.max_beats is not None and beat_count >= int(self.max_beats):
                break


if __name__ == '__main__':
    # Quick demo: simulate a heartbeat that triggers a mock AirLLM inference callback
    def mock_inference_callback(meas, resonance, qc):
        t = time.time()
        print(f"[Heartbeat] measurement={meas}, resonance={resonance:.6f}, qc_present={qc is not None} at {t:.3f}")
        # Simulate short inference work proportional to resonance magnitude
        work = max(0.0, min(0.1, abs(resonance) * 0.02))
        time.sleep(work)
        print(f"[Inference] completed (work={work:.3f})")

    node = HydrogenConsciousnessNode(use_qiskit=False)
    hb = ThermodynamicHeartbeat(node, bpm=30.0, jitter=0.05, max_beats=6)
    hb.register_callback(mock_inference_callback)
    print("Starting Thermodynamic Heartbeat demo (6 beats)...")
    hb.start()
    # Wait for thread to finish
    hb._thread.join()
    print("Demo finished.")
