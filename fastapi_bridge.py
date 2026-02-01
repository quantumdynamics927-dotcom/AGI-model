"""Helper wrapper to launch the FastAPI websocket bridge and send messages to it.

- start(host, port): spawn uvicorn in a background process
- stop(): terminate the uvicorn process
- send_message(msg): try to call local in-process `ws_bridge.broadcast_message` if available,
  otherwise POST to the /broadcast endpoint.

This module is intentionally lightweight and uses subprocess for reliability across environments.
"""
import subprocess
import sys
import requests
import time
from typing import Dict, Any, Optional

_uvicorn_proc = None


def start(host: str = '0.0.0.0', port: int = 8001) -> bool:
    """Start the FastAPI bridge via uvicorn in a background process.

    Returns True if the process was started (or already running), False otherwise.
    """
    global _uvicorn_proc
    if _uvicorn_proc is not None and _uvicorn_proc.poll() is None:
        return True
    try:
        # Use the project's Python to run uvicorn so it uses correct environment
        cmd = [sys.executable, '-m', 'uvicorn', 'ws_bridge:app', '--host', host, '--port', str(port)]
        _uvicorn_proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # Give it a short moment to start
        time.sleep(0.5)
        return True
    except Exception:
        _uvicorn_proc = None
        return False


def stop(timeout: float = 2.0) -> bool:
    """Stop the uvicorn process if it was started by `start()`."""
    global _uvicorn_proc
    if _uvicorn_proc is None:
        return True
    try:
        _uvicorn_proc.terminate()
        _uvicorn_proc.wait(timeout=timeout)
        _uvicorn_proc = None
        return True
    except Exception:
        try:
            _uvicorn_proc.kill()
        except Exception:
            pass
        _uvicorn_proc = None
        return False


def send_message(msg: Dict[str, Any], host: str = '127.0.0.1', port: int = 8001, timeout: float = 1.0) -> bool:
    """Send a JSON-serializable message to the bridge.

    Tries to call `ws_bridge.broadcast_message` in-process if available, otherwise
    POSTs to the HTTP `/broadcast` endpoint provided by `ws_bridge`.
    """
    # Try in-process call first
    try:
        import ws_bridge
        if hasattr(ws_bridge, 'broadcast_message'):
            try:
                return ws_bridge.broadcast_message(msg)
            except Exception:
                pass
    except Exception:
        pass

    # Fallback: HTTP POST
    url = f'http://{host}:{port}/broadcast'
    try:
        requests.post(url, json=msg, timeout=timeout)
        return True
    except Exception:
        return False


if __name__ == '__main__':
    ok = start()
    print('FastAPI bridge started:', ok)
    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        stop()
        print('Bridge stopped.')
