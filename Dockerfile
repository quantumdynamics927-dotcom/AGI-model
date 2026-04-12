# Dockerfile for Quantum Consciousness VAE
# Security-hardened multi-stage build with optimized size
# Stage 1: Builder
FROM python:3.11-slim-bookworm AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# Install build dependencies (will be discarded)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install to a separate location
COPY requirements.txt pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir --target=/install -r requirements.txt \
    && find /install -type f -name '*.pyc' -delete \
    && find /install -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true \
    && find /install -type f -name '*.pyo' -delete \
    && find /install -type d -name 'tests' -exec rm -rf {} + 2>/dev/null || true \
    && find /install -type d -name 'test' -exec rm -rf {} + 2>/dev/null || true

# Stage 2: Runtime
FROM python:3.11-slim-bookworm

# Security: Create non-root user early
RUN groupadd -r tmtuser && useradd -r -g tmtuser tmtuser

# Set working directory
WORKDIR /app

# Set environment variables for security and performance
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TMT_OS_ENV=production \
    PYTHONPATH=/app:/app/lib \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install minimal runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && apt-get upgrade -y \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Copy installed packages from builder with final ownership
COPY --from=builder --chown=tmtuser:tmtuser /install /app/lib

# Copy application code with proper ownership
COPY --chown=tmtuser:tmtuser . .

# Create necessary writable directories without recursively re-owning dependencies
RUN install -d -o tmtuser -g tmtuser /app/TMT-OS/data \
    && install -d -o tmtuser -g tmtuser /app/TMT-OS/logs \
    && install -d -o tmtuser -g tmtuser /app/TMT-OS/cache

# Security: Remove unnecessary files
RUN find /app -type f -name '*.pyc' -delete \
    && find /app -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true \
    && find /app -type f -name '*.pyo' -delete

# Switch to non-root user
USER tmtuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/system/health || exit 1

# Default command
CMD ["python", "main.py", "--mode", "serve", "--host", "0.0.0.0", "--port", "8000"]
