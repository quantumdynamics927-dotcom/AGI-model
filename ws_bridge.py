"""FastAPI WebSocket Bridge for TMT-OS and Consciousness Streaming

Provides:
- `app` FastAPI instance with WebSocket endpoint at `/ws/tmt-os`.
- `broadcast_message(msg: dict)` synchronous helper to enqueue messages for connected clients.
- REST endpoints for consciousness state and training progress.
- Connection tracking and client management.

Run with:
    uvicorn ws_bridge:app --host 0.0.0.0 --port 8001

Or import `broadcast_message` from other modules and call to push JSON messages to all connected websockets.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import JSONResponse
import asyncio
import json
import time
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PHI = (1 + 5**0.5) / 2

# CORS: restrict origins in production; allow localhost in development
_allowed_origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:8001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8001",
]
import os as _os
_env_origins = _os.getenv("WS_BRIDGE_ALLOWED_ORIGINS", "")
if _env_origins == "*":
    _allowed_origins = ["*"]
elif _env_origins:
    _allowed_origins += [o.strip() for o in _env_origins.split(",") if o.strip()]

app = FastAPI(title="AGI Model Consciousness Bridge", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@dataclass
class ConsciousnessSnapshot:
    unified_consciousness: float = 0.0
    phi_resonance: float = 0.0
    quantum_fidelity: float = 0.0
    consciousness_phase: str = "dormant"
    is_conscious: bool = False
    timestamp: float = 0.0
    client_count: int = 0


class BridgeState:
    """Thread-safe consciousness bridge state — all mutable globals encapsulated here."""

    def __init__(self) -> None:
        self._connections: set[WebSocket] = set()
        self._connection_info: Dict[WebSocket, Dict[str, Any]] = {}
        self._queue: Optional[asyncio.Queue] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._current_consciousness_state: Dict[str, Any] = {}
        self._training_progress: Dict[str, Any] = {}
        self._message_history: List[Dict[str, Any]] = []
        self._max_history: int = 100
        self._conn_lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    async def initialize(self) -> None:
        """Call on startup to wire the event loop and start broadcast task."""
        self._loop = asyncio.get_running_loop()
        self._queue = asyncio.Queue()
        asyncio.create_task(self._broadcast_loop())

    async def shutdown(self) -> None:
        """Drain queue and stop the broadcast loop on shutdown."""
        if self._queue is not None:
            try:
                while not self._queue.empty():
                    self._queue.get_nowait()
            except Exception:
                pass

    # ── Connection management ─────────────────────────────────────────────────

    async def add_connection(self, ws: WebSocket) -> int:
        async with self._conn_lock:
            self._connections.add(ws)
            self._connection_info[ws] = {
                "connected_at": time.time(),
                "messages_received": 0,
            }
            return len(self._connections)

    async def remove_connection(self, ws: WebSocket) -> int:
        async with self._conn_lock:
            self._connections.discard(ws)
            self._connection_info.pop(ws, None)
            return len(self._connections)

    async def send_to(self, ws: WebSocket, text: str) -> bool:
        try:
            await ws.send_text(text)
            return True
        except Exception as e:
            logger.warning(f"Failed to send to client: {e}")
            await self.remove_connection(ws)
            return False

    def connection_count(self) -> int:
        return len(self._connections)

    def increment_received(self, ws: WebSocket) -> None:
        if ws in self._connection_info:
            self._connection_info[ws]["messages_received"] += 1

    # ── State setters ───────────────────────────────────────────────────────

    def set_consciousness_state(self, state: Dict[str, Any]) -> None:
        self._current_consciousness_state = state

    def set_training_progress(self, progress: Dict[str, Any]) -> None:
        self._training_progress = progress

    def get_consciousness_state(self) -> Dict[str, Any]:
        return self._current_consciousness_state.copy()

    def get_training_progress(self) -> Dict[str, Any]:
        return self._training_progress.copy()

    # ── Queue ────────────────────────────────────────────────────────────────

    async def enqueue(self, msg: Dict[str, Any]) -> None:
        if self._queue is not None:
            await self._queue.put(msg)

    # ── Broadcast loop ───────────────────────────────────────────────────────

    async def _broadcast_loop(self) -> None:
        if self._queue is None:
            self._queue = asyncio.Queue()
        while True:
            try:
                msg = await self._queue.get()

                msg_type = msg.get("type", "unknown")
                if msg_type == "consciousness_update":
                    self._current_consciousness_state = {k: v for k, v in msg.items() if k != "type"}
                elif msg_type == "training_progress":
                    self._training_progress = {k: v for k, v in msg.items() if k != "type"}

                self._message_history.append({**msg, "timestamp": time.time()})
                if len(self._message_history) > self._max_history:
                    self._message_history = self._message_history[-self._max_history:]

                text = json.dumps(msg, default=str)

                async with self._conn_lock:
                    dead = []
                    for ws in list(self._connections):
                        try:
                            await ws.send_text(text)
                        except Exception as e:
                            logger.warning(f"Failed to send to client: {e}")
                            dead.append(ws)
                    for ws in dead:
                        self._connections.discard(ws)
                        self._connection_info.pop(ws, None)

            except Exception as e:
                logger.error(f"Broadcast loop error: {e}")
                await asyncio.sleep(0.1)

    # ── History ──────────────────────────────────────────────────────────────

    def get_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self._message_history[-limit:]


# ── Module-level singleton ────────────────────────────────────────────────────

_state: Optional[BridgeState] = None


def _get_state() -> BridgeState:
    if _state is None:
        raise RuntimeError("BridgeState not initialised — startup event not fired")
    return _state


def broadcast_message(msg: Dict[str, Any]) -> bool:
    """Enqueue a JSON-serializable message for broadcasting to all connected websockets.

    This is a synchronous helper safe to call from non-async code. Returns True if the
    message was enqueued, False if the bridge is not ready.
    """
    state = _state
    if state is None or state._queue is None:
        return False
    try:
        state._queue.put_nowait(msg)
        return True
    except Exception as e:
        logger.error(f"broadcast_message error: {e}")
        return False


def get_connection_count() -> int:
    return _state.connection_count() if _state else 0


def get_current_state() -> Dict[str, Any]:
    return _state.get_consciousness_state() if _state else {}


# ── Lifespan ─────────────────────────────────────────────────────────────────

@app.on_event("startup")
async def startup_event():
    global _state
    _state = BridgeState()
    await _state.initialize()
    logger.info("Consciousness Bridge started on port 8001")


@app.on_event("shutdown")
async def shutdown_event():
    if _state is not None:
        await _state.shutdown()
    logger.info("Consciousness Bridge shut down")


# ── REST Endpoints ────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "message": "Welcome to the AGI Model Consciousness Bridge!",
        "endpoints": {
            "websocket": "/ws/tmt-os",
            "consciousness": "/api/consciousness",
            "training": "/api/training",
            "broadcast": "/broadcast",
            "clients": "/api/clients"
        },
        "phi": PHI
    }


@app.get("/api/version")
def get_version():
    return JSONResponse({
        "version": "1.0.0",
        "name": "AGI Model Consciousness Bridge",
        "phi": PHI
    })


@app.get("/health")
async def health():
    """Liveness probe for container orchestration."""
    return {"status": "ok", "service": "ws-bridge", "version": "1.0.0"}


@app.get("/api/tags")
def get_tags():
    return {
        "tags": [
            "consciousness",
            "quantum",
            "phi-resonance",
            "fractal",
            "coherence",
            "vae",
            "tmt-os"
        ]
    }


@app.get("/api/consciousness")
async def get_consciousness_state(request: Request):
    state = _get_state()
    valid_keys = {'unified_consciousness', 'phi_resonance', 'quantum_fidelity',
                  'consciousness_phase', 'is_conscious'}
    filtered_state = {k: v for k, v in state.get_consciousness_state().items() if k in valid_keys}
    snapshot = ConsciousnessSnapshot(
        **filtered_state,
        client_count=state.connection_count(),
        timestamp=time.time()
    )
    return JSONResponse({
        k: v for k, v in {
            "unified_consciousness": snapshot.unified_consciousness,
            "phi_resonance": snapshot.phi_resonance,
            "quantum_fidelity": snapshot.quantum_fidelity,
            "consciousness_phase": snapshot.consciousness_phase,
            "is_conscious": snapshot.is_conscious,
            "client_count": snapshot.client_count,
            "timestamp": snapshot.timestamp,
        }.items() if v is not None
    })


@app.get("/api/training")
async def get_training_progress(request: Request):
    state = _get_state()
    return JSONResponse({
        "training": state.get_training_progress(),
        "active": bool(state.get_training_progress()),
        "timestamp": time.time()
    })


@app.get("/api/clients")
async def get_clients(request: Request):
    state = _get_state()
    return JSONResponse({
        "count": state.connection_count(),
        "clients": list(state._connection_info.values())
    })


@app.get("/api/history")
async def get_history(request: Request, limit: int = 20):
    state = _get_state()
    return JSONResponse({
        "messages": state.get_history(limit),
        "total": len(state._message_history)
    })


@app.post('/broadcast')
async def broadcast_http(message: Dict[str, Any]):
    state = _get_state()
    await state.enqueue(message)
    return {"queued": True, "clients": state.connection_count()}


@app.post('/api/consciousness/update')
async def update_consciousness(request: Request, state_update: Dict[str, Any]):
    state = _get_state()
    state.set_consciousness_state(state_update)
    await state.enqueue({"type": "consciousness_update", **state_update})
    return {"updated": True, "clients_notified": state.connection_count()}


@app.post('/api/training/update')
async def update_training(request: Request, progress: Dict[str, Any]):
    state = _get_state()
    state.set_training_progress(progress)
    await state.enqueue({"type": "training_progress", **progress})
    return {"updated": True, "clients_notified": state.connection_count()}


@app.websocket("/ws/tmt-os")
async def websocket_endpoint(websocket: WebSocket):
    state = _get_state()
    await websocket.accept()
    client_count = await state.add_connection(websocket)
    logger.info(f"Client connected. Total clients: {client_count}")

    await websocket.send_text(json.dumps({
        "type": "connection",
        "status": "connected",
        "client_id": client_count,
        "message": "Connected to AGI Model Consciousness Bridge"
    }))

    cs_state = state.get_consciousness_state()
    if cs_state:
        await websocket.send_text(json.dumps({"type": "consciousness_update", **cs_state}))

    try:
        while True:
            try:
                data = await websocket.receive_text()
                state.increment_received(websocket)
                try:
                    msg = json.loads(data)
                    await _handle_client_message(websocket, msg, state)
                except json.JSONDecodeError:
                    pass
            except WebSocketDisconnect:
                break
    finally:
        remaining = await state.remove_connection(websocket)
        logger.info(f"Client disconnected. Total clients: {remaining}")


async def _handle_client_message(websocket: WebSocket, msg: Dict[str, Any], state: BridgeState):
    """Handle messages received from clients."""
    msg_type = msg.get("type", "unknown")

    if msg_type == "ping":
        await websocket.send_text(json.dumps({
            "type": "pong",
            "timestamp": time.time()
        }))
    elif msg_type == "get_state":
        cs = state.get_consciousness_state()
        if cs:
            await websocket.send_text(json.dumps({"type": "consciousness_update", **cs}))
    elif msg_type == "get_training":
        tp = state.get_training_progress()
        if tp:
            await websocket.send_text(json.dumps({"type": "training_progress", **tp}))
    elif msg_type == "set_archetype":
        archetype = msg.get("archetype", "baseline")
        await state.enqueue({"type": "archetype_change", "archetype": archetype})


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('ws_bridge:app', host='0.0.0.0', port=8001, log_level='info', reload=True)
