"""FastAPI WebSocket Bridge for TMT-OS

Provides:
- `app` FastAPI instance with WebSocket endpoint at `/ws/tmt-os`.
- `broadcast_message(msg: dict)` synchronous helper to enqueue messages for connected clients.

Run with:
    uvicorn ws_bridge:app --host 0.0.0.0 --port 8000

Or import `broadcast_message` from other modules and call to push JSON messages to all connected websockets.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import asyncio
import json
from typing import Set, Dict, Any, Optional

app = FastAPI()

_connections: Set[WebSocket] = set()
_queue: Optional[asyncio.Queue] = None
_loop: Optional[asyncio.AbstractEventLoop] = None


@app.on_event("startup")
async def startup_event():
    global _queue, _loop
    _loop = asyncio.get_event_loop()
    _queue = asyncio.Queue()
    # start background task to broadcast queued messages
    asyncio.create_task(_broadcast_loop())


@app.on_event("shutdown")
async def shutdown_event():
    # drain queue and close connections
    if _queue is not None:
        try:
            while not _queue.empty():
                await _queue.get()
        except Exception:
            pass


async def _broadcast_loop():
    global _queue
    if _queue is None:
        _queue = asyncio.Queue()
    while True:
        try:
            msg = await _queue.get()
            text = json.dumps(msg)
            to_remove = []
            for ws in list(_connections):
                try:
                    await ws.send_text(text)
                except Exception:
                    to_remove.append(ws)
            for ws in to_remove:
                try:
                    _connections.remove(ws)
                except KeyError:
                    pass
        except Exception:
            # ensure the loop continues even if a single broadcast fails
            await asyncio.sleep(0.1)


@app.post('/broadcast')
async def http_broadcast(message: Dict[str, Any]):
    """HTTP endpoint to enqueue a message for websocket broadcast.

    Accepts a JSON body and enqueues it for all connected websockets.
    """
    global _queue
    if _queue is None:
        return {'queued': False, 'reason': 'bridge_not_ready'}
    await _queue.put(message)
    return {'queued': True}


@app.websocket("/ws/tmt-os")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    _connections.add(websocket)
    try:
        while True:
            # keep the connection alive by awaiting receives (clients may send pings)
            try:
                data = await websocket.receive_text()
                # optional: if client sends subscription or ping, we can respond
                # for now, just ignore client messages
            except WebSocketDisconnect:
                break
    finally:
        try:
            _connections.remove(websocket)
        except Exception:
            pass


@app.post("/broadcast")
async def http_broadcast(payload: Dict[str, Any]):
    """HTTP endpoint to broadcast a JSON payload to all connected websocket clients.

    This lets external processes (or local adapters) POST messages to the bridge.
    """
    if _queue is None:
        return {"ok": False, "reason": "bridge-not-running"}
    await _queue.put(payload)
    return {"ok": True}


def broadcast_message(msg: Dict[str, Any]) -> bool:
    """Enqueue a JSON-serializable message for broadcasting to all connected websockets.

    This is a synchronous helper safe to call from non-async code. It uses
    `asyncio.run_coroutine_threadsafe` when the FastAPI event loop is running.
    Returns True if the message was enqueued, False otherwise.
    """
    global _loop, _queue
    if _loop is None or _queue is None:
        # bridge not running
        return False
    try:
        fut = asyncio.run_coroutine_threadsafe(_queue.put(msg), _loop)
        fut.result(timeout=1.0)
        return True
    except Exception:
        return False


if __name__ == '__main__':
    # simple run guard; prefer using uvicorn externally
    import uvicorn
    uvicorn.run('ws_bridge:app', host='0.0.0.0', port=8001, log_level='info')
