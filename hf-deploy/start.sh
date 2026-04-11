#!/bin/bash

# Start Ollama server in background
ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to be ready
echo "Waiting for Ollama to start..."
sleep 10

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "ERROR: Ollama failed to start"
    exit 1
fi

echo "Ollama started successfully"
echo "Available models:"
curl -s http://localhost:11434/api/tags | jq -r '.models[].name'

# Start the FastAPI/Gradio app
echo "Starting Biomimetic AGI API..."
python hf-deploy/space_app.py