# Dockerfile for Ollama Biomimetic AGI Demo on Hugging Face Spaces
# Optimized for GPU inference with Ollama

FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04

# Security: Create non-root user
RUN groupadd -r agiuser && useradd -r -g agiuser agiuser

# Set working directory
WORKDIR /app

# Environment variables for performance and security
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    OLLAMA_HOST=0.0.0.0 \
    OLLAMA_ORIGINS="*" \
    HF_HOME="/app/cache"

# Install system dependencies including Ollama
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    wget \
    git \
    build-essential \
    && curl -fsSL https://ollama.ai/install.sh | sh \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python and dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 \
    python3-pip \
    python3.11-venv \
    && ln -s /usr/bin/python3.11 /usr/local/bin/python \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir fastapi uvicorn[standard] huggingface_hub gradio

# Copy application code
COPY --chown=agiuser:agiuser . .

# Create necessary directories
RUN mkdir -p /app/cache /app/models \
    && chown -R agiuser:agiuser /app

# Download models (llama3.2:1b and qwen3:1.7b)
RUN ollama pull llama3.2:1b \
    && ollama pull qwen3:1.7b

# Expose ports
# Hugging Face Spaces uses port 7860
# Ollama API uses port 11434
EXPOSE 7860
EXPOSE 11434

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:11434/api/tags || exit 1

# Start script
COPY hf-deploy/start.sh .
RUN chmod +x start.sh

USER agiuser

# Start the application
CMD ["./start.sh"]
