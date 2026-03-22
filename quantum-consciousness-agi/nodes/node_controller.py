"""Node Controller for TMT-OS

Manages multiple specialized nodes (Phi-3 Mini, Mistral) and a core AirLLM 70B node.
Uses `dispersion_camp.InterNodeHandshake` to codify node latents into Hydrogen/Antihydrogen camps
and a `ThermodynamicHeartbeat` to drive Pauli-X pulses that synchronize inference cycles.

This controller uses graceful fallbacks when heavy dependencies (AirLLM, qiskit) are not present.
"""

import time
import threading
from typing import Callable, Dict, Any, Optional

import numpy as np

# Local imports with graceful fallback
try:
    from dispersion_camp import InterNodeHandshake, DispersionCodifier
    HAVE_DISP = True
except Exception:
    InterNodeHandshake = None
    DispersionCodifier = None
    HAVE_DISP = False

try:
    from molecular_clock import ThermodynamicHeartbeat, HydrogenConsciousnessNode
    HAVE_HEART = True
except Exception:
    ThermodynamicHeartbeat = None
    HydrogenConsciousnessNode = None
    HAVE_HEART = False

try:
    from airllm_neural_backbone import AirLLMNeuralBackbone
    HAVE_AIRLLM = True
except Exception:
    AirLLMNeuralBackbone = None
    HAVE_AIRLLM = False

# Try to import websocket bridge broadcaster (optional)
try:
    from ws_bridge import broadcast_message
    HAVE_WS_BRIDGE = True
except Exception:
    broadcast_message = None
    HAVE_WS_BRIDGE = False
try:
    import fastapi_bridge
    HAVE_FASTAPI_BRIDGE = True
except Exception:
    fastapi_bridge = None
    HAVE_FASTAPI_BRIDGE = False


class NodeController:
    def __init__(self, signing_key: Optional[bytes] = None, bpm: float = 30.0, beats: int = 8):
        self.signing_key = signing_key
        self.nodes: Dict[str, Callable[[], np.ndarray]] = {}
        self.handshakes: Dict[str, Any] = {}
        self.bpm = bpm
        self.beats = beats
        self.heartbeat = None
        self.core = None
        self.codifier = DispersionCodifier() if HAVE_DISP else None
        self._setup_core()
        # optionally start embedded FastAPI bridge if available
        try:
            if HAVE_FASTAPI_BRIDGE and fastapi_bridge is not None:
                fastapi_bridge.start(host='127.0.0.1', port=8000)
        except Exception:
            pass

    def _setup_core(self):
        if HAVE_AIRLLM and AirLLMNeuralBackbone is not None:
            try:
                self.core = AirLLMNeuralBackbone()
            except Exception:
                self.core = None
        else:
            self.core = None

    def register_node(self, name: str, generator: Callable[[], np.ndarray]):
        self.nodes[name] = generator
        # Pre-create handshake object per node
        if HAVE_DISP and InterNodeHandshake is not None:
            self.handshakes[name] = InterNodeHandshake(source=name, target='core', signing_key=self.signing_key)
        else:
            self.handshakes[name] = None

    def register_node_with_adapter(self, name: str, adapter_cfg: Dict[str, Any]):
        """Register a node using an adapter configuration.

        adapter_cfg example:
            { 'type': 'rpc', 'endpoint': 'http://localhost:8000/infer', 'timeout': 5 }
            { 'type': 'binary', 'path': 'C:/models/phi3-mini/bin', 'args': [...] }

        If adapter fails to initialize or endpoint missing, falls back to simulated generator.
        """
        adapter_type = adapter_cfg.get('type')
        if adapter_type == 'rpc':
            adapter = ModelRPCAdapter(adapter_cfg.get('endpoint'), timeout=adapter_cfg.get('timeout', 5))
            gen = adapter.generate_latent
        elif adapter_type == 'binary':
            adapter = LocalBinaryAdapter(adapter_cfg.get('path'), args=adapter_cfg.get('args', []))
            gen = adapter.generate_latent
        else:
            gen = lambda: np.zeros(12, dtype=float)

        self.register_node(name, gen)

    def start(self):
        # Build heartbeat node
        heart_node = HydrogenConsciousnessNode(use_qiskit=False) if HAVE_HEART and HydrogenConsciousnessNode is not None else None
        self.heartbeat = ThermodynamicHeartbeat(node=heart_node, bpm=self.bpm, jitter=0.02, max_beats=self.beats) if ThermodynamicHeartbeat is not None else None
        if self.heartbeat is not None:
            self.heartbeat.register_callback(self._on_beat)
            self.heartbeat.start()
            if self.heartbeat._thread is not None:
                self.heartbeat._thread.join()
        else:
            # Fallback synchronous loop
            for i in range(self.beats):
                meas, qc = (i % 6, None)
                resonance = 1.0
                self._on_beat(meas, resonance, qc)
                time.sleep(60.0 / max(1.0, self.bpm))

    def _on_beat(self, measurement: int, resonance: float, qc: Optional[object]):
        """Callback invoked on each heartbeat; request latents from each node, create handshake messages,
        and if core is present, use it to compress/aggregate. Otherwise compute a combined resonance."""
        timestamp = time.time()
        print(f"[NodeController] Beat @ {timestamp:.3f} meas={measurement} resonance={resonance:.6f}")

        # Send simple state/resonance message to UI
        send_message({'state': measurement, 'resonance': resonance})

        messages = {}
        for name, gen in self.nodes.items():
            try:
                latent = gen()
            except Exception:
                latent = np.zeros(12, dtype=float)

            # Create handshake message if possible
            hs = self.handshakes.get(name)
            if hs is not None:
                try:
                    msg = hs.create_handshake(latent, quantize=True, target_amplitude=1.0)
                except Exception:
                    msg = {'source': name, 'resonances': latent, 'phi_resonance': float(np.mean(np.abs(latent)))}
            else:
                # Local codification fallback
                if self.codifier is not None:
                    camps = self.codifier.codify_array(latent)
                    resonances = np.array([self.codifier.reconstruct_geometry(b, target_amplitude=1.0) for b in camps.flatten()])
                    msg = {'source': name, 'resonances': resonances, 'camps': camps, 'phi_resonance': float(np.mean(np.abs(resonances)))}
                else:
                    msg = {'source': name, 'resonances': latent, 'phi_resonance': float(np.mean(np.abs(latent)))}

            messages[name] = msg

        # Aggregate messages into a single input for core inference
        if self.core is not None:
            # Try to build a matrix of resonances
            try:
                payloads = []
                for n, m in messages.items():
                    if isinstance(m, dict) and 'resonances' in m:
                        payloads.append(np.asarray(m['resonances'], dtype=float))
                    else:
                        payloads.append(np.zeros(12, dtype=float))
                stacked = np.vstack(payloads)
                # Flatten and feed into core compress (core expects n_agents x features)
                latent_out, metrics = self.core.compress_consciousness_space(stacked)
                print(f"[NodeController] Core compress returned latent shape {latent_out.shape}")
            except Exception as e:
                print("[NodeController] Core compression failed:", str(e))
        else:
            # Compute combined phi_resonance
            phi_vals = []
            for m in messages.values():
                if isinstance(m, dict) and 'phi_resonance' in m:
                    phi_vals.append(float(m['phi_resonance']))
            combined_phi = float(np.mean(phi_vals)) if phi_vals else 0.0
            print(f"[NodeController] Combined phi_resonance across nodes: {combined_phi:.6f}")

        # Simple visualization: print camp counts aggregated
        total_h = 0
        total_o = 0
        for m in messages.values():
            camps = m.get('camps') if isinstance(m, dict) else None
            if camps is not None:
                total_h += int(np.sum(camps == 0))
                total_o += int(np.sum(camps == 1))
        if total_h + total_o > 0:
            print(f"[NodeController] Camps H: {total_h} | O: {total_o}")

        # Broadcast messages to websocket bridge if available
        try:
            if HAVE_FASTAPI_BRIDGE and fastapi_bridge is not None:
                try:
                    bpayload = {
                        'type': 'handshake_batch',
                        'timestamp': timestamp,
                        'beat_measurement': int(measurement),
                        'beat_resonance': float(resonance),
                        'messages': {}
                    }
                    for n, m in messages.items():
                        if isinstance(m, dict):
                            bpayload['messages'][n] = {
                                'phi_resonance': float(m.get('phi_resonance', 0.0)),
                                'camps': m.get('camps').tolist() if m.get('camps') is not None else None,
                            }
                        else:
                            bpayload['messages'][n] = {'phi_resonance': None, 'camps': None}

                    fastapi_bridge.send_message(bpayload)
                except Exception:
                    pass
            elif HAVE_WS_BRIDGE and broadcast_message is not None:
                try:
                    bpayload = {
                        'type': 'handshake_batch',
                        'timestamp': timestamp,
                        'beat_measurement': int(measurement),
                        'beat_resonance': float(resonance),
                        'messages': {}
                    }
                    for n, m in messages.items():
                        if isinstance(m, dict):
                            bpayload['messages'][n] = {
                                'phi_resonance': float(m.get('phi_resonance', 0.0)),
                                'camps': m.get('camps').tolist() if m.get('camps') is not None else None,
                            }
                        else:
                            bpayload['messages'][n] = {'phi_resonance': None, 'camps': None}

                    broadcast_message(bpayload)
                except Exception:
                    pass
        except Exception:
            pass


# --- Simulated small-node generators ---

def phi3_mini_generator() -> np.ndarray:
    """Simulate a small phi-3 mini node latent output (12-dim)"""
    r = np.random.RandomState(None)
    return r.randn(12) * 0.3 + 0.2


def mistral_generator() -> np.ndarray:
    """Simulate a Mistral-like node latent output (12-dim)"""
    r = np.random.RandomState(None)
    return r.randn(12) * 0.6


# --- Model adapters -------------------------------------------------
import os
import json
import urllib.request
import urllib.error


class ModelRPCAdapter:
    """Adapter to call a simple HTTP JSON RPC endpoint for latent generation.

    Expects endpoint to accept POST JSON like {"n":12} and return {"latent": [..]}
    """

    def __init__(self, endpoint: Optional[str], timeout: int = 5):
        self.endpoint = endpoint
        self.timeout = int(timeout)

    def generate_latent(self) -> np.ndarray:
        if not self.endpoint:
            return np.zeros(12, dtype=float)
        payload = json.dumps({'n': 12}).encode('utf-8')
        req = urllib.request.Request(self.endpoint, data=payload, headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                data = json.load(resp)
            lat = np.asarray(data.get('latent', [0.0]*12), dtype=float)
            if lat.size != 12:
                lat = np.resize(lat, 12)
            return lat
        except Exception:
            return np.zeros(12, dtype=float)


class LocalBinaryAdapter:
    """Adapter that invokes a local model binary/script and reads latent from stdout or file.

    This is a lightweight adapter: it will attempt to run `path` with provided args and
    parse JSON `{"latent": [...]}` from stdout. If unavailable, it returns zeros.
    """

    def __init__(self, path: Optional[str], args: Optional[list] = None):
        self.path = path
        self.args = args or []

    def generate_latent(self) -> np.ndarray:
        if not self.path or not os.path.exists(self.path):
            return np.zeros(12, dtype=float)
        try:
            # Run the binary/script and capture stdout
            import subprocess
            proc = subprocess.run([self.path] + self.args, capture_output=True, text=True, timeout=8)
            out = proc.stdout.strip()
            # Expect JSON with key 'latent'
            data = json.loads(out)
            lat = np.asarray(data.get('latent', [0.0]*12), dtype=float)
            if lat.size != 12:
                lat = np.resize(lat, 12)
            return lat
        except Exception:
            return np.zeros(12, dtype=float)
if __name__ == '__main__':
    print('Starting NodeController demo: Phi-3 Mini, Mistral -> Core')
    nc = NodeController(signing_key=None, bpm=20.0, beats=1000)
    # Register phi3-mini as a local binary adapter (will fall back if path missing)
    nc.register_node_with_adapter('phi3-mini', {'type': 'binary', 'path': 'C:/models/phi3-mini/run_model.exe', 'args': ['--quiet']})
    # Keep mistral as a simulated generator for now (or replace with an RPC adapter)
    nc.register_node('mistral', mistral_generator)
    nc.start()
    print('NodeController demo finished.')
