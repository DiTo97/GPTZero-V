# Multi-stage Dockerfile for running both API and Service with optimized layer caching

# Use specific Python version for consistency
ARG PYTHON_VERSION=3.12
# Use Ubuntu 24.04 for GLIBC 2.39 compatibility (required by c2patool)
ARG PYTHON_IMAGE=ubuntu:24.04

# Stage 1: Builder - Install dependencies with uv
FROM ghcr.io/astral-sh/uv:python${PYTHON_VERSION}-bookworm-slim AS builder

# Enable bytecode compilation for faster startup
ENV UV_COMPILE_BYTECODE=1
# Use copy mode to ensure dependencies are copied to final image
ENV UV_LINK_MODE=copy
# Use system Python interpreter (no managed Python download)
ENV UV_PYTHON_DOWNLOADS=0
# Omit development dependencies
ENV UV_NO_DEV=1

WORKDIR /app

# Copy workspace configuration and package definitions
# This allows uv to understand workspace structure without copying source code
COPY pyproject.toml uv.lock ./
COPY packages/gptzero/pyproject.toml packages/gptzero/README.md ./packages/gptzero/
COPY packages/gptzero-sdk/pyproject.toml packages/gptzero-sdk/README.md ./packages/gptzero-sdk/
COPY packages/gptzero-api/pyproject.toml packages/gptzero-api/README.md ./packages/gptzero-api/
COPY packages/gptzero-service/pyproject.toml packages/gptzero-service/README.md ./packages/gptzero-service/

# Install dependencies (this layer is cached unless lock/config files change)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project --all-packages

# Then, copy the rest of the source code
COPY . /app

# Install the workspace packages (source code)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --all-packages

# Make c2patool executable
RUN chmod +x /app/packages/gptzero/resources/c2patool/v0.16.1/Linux/c2patool || true

# Stage 2: Final runtime image without uv
FROM ${PYTHON_IMAGE}

ARG PYTHON_VERSION

# Create non-root user for security
RUN groupadd --system --gid 999 appuser \
    && useradd --system --gid 999 --uid 999 --create-home appuser

# Install Python and curl for healthchecks
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        python${PYTHON_VERSION} \
        python${PYTHON_VERSION}-venv \
        curl \
    && ln -sf /usr/bin/python${PYTHON_VERSION} /usr/bin/python3 \
    && ln -sf /usr/bin/python${PYTHON_VERSION} /usr/bin/python \
    && mkdir -p /usr/local/bin \
    && ln -sf /usr/bin/python${PYTHON_VERSION} /usr/local/bin/python3 \
    && ln -sf /usr/bin/python${PYTHON_VERSION} /usr/local/bin/python \
    && rm -rf /var/lib/apt/lists/*

# Copy the application and virtual environment from builder
COPY --from=builder --chown=appuser:appuser /app /app

# Set up environment to use the virtual environment
ENV PATH="/app/.venv/bin:$PATH"
# Ensure Python uses system packages from venv
ENV VIRTUAL_ENV="/app/.venv"

# Set working directory
WORKDIR /app

# Expose ports for API and Service
EXPOSE 8000 8501

# Health check for both services
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8000/health && curl --fail http://localhost:8501/_stcore/health

# Create startup script
RUN echo '#!/bin/bash\n\
set -e\n\
echo "Starting GPTZero API on port 8000..."\n\
/app/.venv/bin/gptzero-api &\n\
API_PID=$!\n\
echo "API started with PID $API_PID"\n\
\n\
echo "Waiting for API to be ready..."\n\
sleep 5\n\
\n\
echo "Starting GPTZero Service on port 8501..."\n\
export GPTZERO_API_URL=http://localhost:8000\n\
/app/.venv/bin/streamlit run /app/packages/gptzero-service/src/handler.py --server.port=8501 --server.address=0.0.0.0 &\n\
SERVICE_PID=$!\n\
echo "Service started with PID $SERVICE_PID"\n\
\n\
# Wait for both processes\n\
wait $API_PID $SERVICE_PID\n\
' > /app/start.sh && chmod +x /app/start.sh \
    && chown appuser:appuser /app/start.sh

# Switch to non-root user
USER appuser

CMD ["/app/start.sh"]
