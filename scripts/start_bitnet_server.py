#!/usr/bin/env python3
"""
BitNet Server Launcher for AGI MODEL Project

This script starts a local inference server that exposes BitNet Llama 8B
through an OpenAI-compatible API endpoint.

Usage:
    python scripts/start_bitnet_server.py [--port 8080] [--model-path PATH]

The server will be available at: http://localhost:8080/v1

Compatible with:
    - Continue.dev extension
    - Cline extension
    - Any OpenAI-compatible client
"""

import argparse
import subprocess
import os
from pathlib import Path

# Project constants
PHI = 1.618033988749895
DEFAULT_PORT = 8080
DEFAULT_MODEL_PATH = Path.home() / ".cache" / "bitnet" / "llama-3-8b-1.58bit.gguf"

def check_bitnet_installation():
    """Check if BitNet.cpp is installed and accessible."""
    # Project-local BitNet installation (recommended)
    project_paths = [
        Path("E:/AGI model/BitNet/build/bin/Release/llama-server.exe"),
        Path("E:/AGI model/BitNet/build/bin/llama-server.exe"),
        Path("E:/AGI model/BitNet/build/bin/llama-server"),
    ]

    for path in project_paths:
        if path.exists():
            print(f"[OK] BitNet server found at: {path}")
            return str(path)

    # Try system-wide locations
    alt_paths = [
        Path.home() / "BitNet" / "build" / "bin" / "Release" / "llama-server.exe",
        Path.home() / "BitNet" / "build" / "bin" / "llama-server.exe",
        Path("C:/BitNet/build/bin/Release/llama-server.exe"),
        Path("/usr/local/bin/llama-server"),
    ]

    for path in alt_paths:
        if path.exists():
            print(f"[OK] BitNet server found at: {path}")
            return str(path)

    return None

def check_model_exists(model_path: Path) -> bool:
    """Verify the model file exists."""
    if model_path.exists():
        size_mb = model_path.stat().st_size / (1024 * 1024)
        print(f"[OK] Model found: {model_path} ({size_mb:.1f} MB)")
        return True
    return False

def start_server_bitnet(bitnet_path: str, model_path: Path, port: int):
    """Start BitNet.cpp server with OpenAI-compatible API."""
    threads = os.cpu_count() or 4
    cmd = [
        bitnet_path,
        "-m", str(model_path),
        "--port", str(port),
        "--host", "127.0.0.1",
        "-c", "4096",
        "-t", str(threads),
        "-n", "4096",
        "-ngl", "0",
        "--temp", "0.7",
        "-cb",
    ]

    print(f"\n[STARTING] BitNet server on port {port}")
    print(f"[THREADS] {threads}")
    print(f"[MODEL] {model_path}")
    print("=" * 60)
    print(f"API Endpoint: http://localhost:{port}/v1/chat/completions")
    print(f"Health Check: http://localhost:{port}/health")
    print("=" * 60)
    print("\nPress Ctrl+C to stop the server\n")

    try:
        subprocess.run(cmd, check=False)
    except KeyboardInterrupt:
        print("\n[STOPPED] Server shutdown complete")

def start_server_ollama(model_name: str, port: int):
    """Fallback: Start Ollama server if BitNet is not available."""
    print("\n[FALLBACK] Using Ollama as BitNet alternative")

    # Pull model if needed
    subprocess.run(["ollama", "pull", model_name], check=False)

    # Set environment for custom port
    env = os.environ.copy()
    env["OLLAMA_HOST"] = f"127.0.0.1:{port}"

    cmd = ["ollama", "serve"]

    print(f"\n[STARTING] Ollama server on port {port}")
    print("=" * 60)
    print(f"API Endpoint: http://localhost:{port}/api")
    print(f"Model: {model_name}")
    print("=" * 60)
    print("\nPress Ctrl+C to stop the server\n")

    try:
        subprocess.run(cmd, env=env, check=False)
    except KeyboardInterrupt:
        print("\n[STOPPED] Server shutdown complete")

def print_setup_instructions():
    """Print detailed instructions for setting up BitNet on Windows."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║           BitNet.cpp Installation Instructions               ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  1. Clone the repository:                                    ║
║     git clone https://github.com/microsoft/BitNet.git        ║
║     cd BitNet                                                ║
║                                                              ║
║  2. Build with CMake:                                        ║
║     mkdir build && cd build                                  ║
║     cmake ..                                                 ║
║     cmake --build . --config Release                         ║
║                                                              ║
║  3. Download model (Llama 3 8B 1.58-bit):                    ║
║     huggingface-cli download microsoft/Llama3-8B-1.58-100B   ║
║         --local-dir ~/.cache/bitnet/                         ║
║                                                              ║
║  4. Add to PATH and run this script again                    ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║  Alternative: Use Ollama (easier setup)                      ║
║     1. Install Ollama: https://ollama.ai                     ║
║     2. Run: ollama pull llama3:8b                            ║
║     3. Run this script with --use-ollama                     ║
╚══════════════════════════════════════════════════════════════╝
""")

def main():
    parser = argparse.ArgumentParser(
        description="Start BitNet inference server for AGI MODEL project"
    )
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=DEFAULT_PORT,
        help=f"Server port (default: {DEFAULT_PORT})"
    )
    parser.add_argument(
        "--model-path", "-m",
        type=Path,
        default=DEFAULT_MODEL_PATH,
        help=f"Path to GGUF model file"
    )
    parser.add_argument(
        "--use-ollama",
        action="store_true",
        help="Use Ollama instead of BitNet.cpp"
    )
    parser.add_argument(
        "--ollama-model",
        default="llama3:8b",
        help="Ollama model name (default: llama3:8b)"
    )

    args = parser.parse_args()

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║          AGI MODEL - Local Inference Server                  ║
║                   φ = {PHI}                         ║
╚══════════════════════════════════════════════════════════════╝
""")

    if args.use_ollama:
        start_server_ollama(args.ollama_model, args.port)
        return

    # Check BitNet installation
    bitnet_path = check_bitnet_installation()

    if not bitnet_path:
        print("[ERROR] BitNet.cpp not found in PATH")
        print_setup_instructions()

        # Offer Ollama fallback
        response = input("\nWould you like to use Ollama instead? [y/N]: ")
        if response.lower() == 'y':
            start_server_ollama(args.ollama_model, args.port)
        return

    # Check model exists
    if not check_model_exists(args.model_path):
        print(f"\n[ERROR] Model not found: {args.model_path}")
        print("\nDownload the model with:")
        print(f"  huggingface-cli download microsoft/Llama3-8B-1.58-100B --local-dir {args.model_path.parent}")
        return

    # Start server
    start_server_bitnet(bitnet_path, args.model_path, args.port)

if __name__ == "__main__":
    main()
