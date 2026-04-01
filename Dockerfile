# Dockerfile for Quantum Consciousness VAE
# Security-hardened base image with specific version
FROM python:3.11-slim-bookworm

# Security: Create non-root user early
RUN groupadd -r tmtuser && useradd -r -g tmtuser tmtuser

# Set working directory
WORKDIR /app

# Set environment variables for security and performance
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TMT_OS_ENV=production \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies with cleanup
# Using --no-install-recommends to minimize attack surface
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && apt-get upgrade -y \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
COPY pyproject.toml .

# Install Python dependencies with security checks
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt \
    && pip check

# Copy application code with proper ownership
COPY --chown=tmtuser:tmtuser . .

# Create necessary directories with proper permissions
RUN mkdir -p /app/TMT-OS/data \
    && mkdir -p /app/TMT-OS/logs \
    && mkdir -p /app/TMT-OS/cache \
    && chown -R tmtuser:tmtuser /app

# Security: Remove unnecessary packages and files
RUN apt-get purge -y --auto-remove build-essential \
    && find /usr/local -type f -name '*.pyc' -delete \
    && find /usr/local -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true

# Switch to non-root user
USER tmtuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/system/health || exit 1

# Default command
CMD ["python", "main.py", "--mode", "serve", "--host", "0.0.0.0", "--port", "8000"]
