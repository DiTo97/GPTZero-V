# Multi-stage Dockerfile for running both API and Service

FROM ubuntu:24.04 AS base

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt install -y \
    python3 \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Copy project files
COPY pyproject.toml uv.lock /app/
COPY packages/ /app/packages/

# Install all packages using uv
RUN uv sync --all-packages --frozen

# Make c2patool executable
RUN chmod +x /app/packages/gptzero/resources/c2patool/v0.16.1/Linux/c2patool || true

# Expose ports
EXPOSE 8000 8501

# Health check for both services
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:8000/health && curl --fail http://localhost:8501/_stcore/health

# Create startup script
RUN echo '#!/bin/bash\n\
set -e\n\
echo "Starting GPTZero API on port 8000..."\n\
uv run --package gptzero-api gptzero-api &\n\
API_PID=$!\n\
echo "API started with PID $API_PID"\n\
\n\
echo "Waiting for API to be ready..."\n\
sleep 5\n\
\n\
echo "Starting GPTZero Service on port 8501..."\n\
export GPTZERO_API_URL=http://localhost:8000\n\
uv run --package gptzero-service streamlit run /app/packages/gptzero-service/src/handler.py --server.port=8501 --server.address=0.0.0.0 &\n\
SERVICE_PID=$!\n\
echo "Service started with PID $SERVICE_PID"\n\
\n\
# Wait for both processes\n\
wait $API_PID $SERVICE_PID\n\
' > /app/start.sh && chmod +x /app/start.sh

CMD ["/app/start.sh"]
