#!/bin/bash
# Start script for AGI Research Console
# Starts Ollama service, pulls models, then launches Gradio

set -e

echo "=== AGI Research Console Startup ==="

# Debug: Check if ollama package is available
echo "Checking Python environment..."
python -c "import ollama; print('✅ Ollama Python client available')" || echo "❌ Ollama Python client not available"
python -c "import sys; print('Python path:', sys.path)" || echo "Could not print Python path"

# Start Ollama in background
echo "Starting Ollama service..."
ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to be ready
echo "Waiting for Ollama to initialize..."
for i in {1..30}; do
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "Ollama is ready!"
        break
    fi
    sleep 2
done

# Pull default model (small, fast)
echo "Pulling llama3.2:1b (default model)..."
ollama pull llama3.2:1b || echo "Warning: Could not pull llama3.2:1b"

# Pull escalation model (optional, larger)
echo "Pulling qwen3:1.7b (escalation model)..."
ollama pull qwen3:1.7b || echo "Warning: Could not pull qwen3:1.7b"

# List available models
echo "Available models:"
ollama list

# Start Gradio app
echo "Starting AGI Research Console..."
python research_console.py

# Cleanup on exit
trap "kill $OLLAMA_PID 2>/dev/null" EXIT