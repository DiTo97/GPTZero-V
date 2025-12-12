# Multi-stage Dockerfile for running both API and Service

FROM ubuntu:24.04 AS base

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

RUN ln -s /usr/bin/python3 /usr/bin/python

WORKDIR /app

# Create virtual environment
RUN python -m venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Upgrade pip
RUN python -m pip install --upgrade pip

# Copy all packages
COPY packages/ /app/packages/

# Install gptzero (core SDK)
RUN cd /app/packages/gptzero && pip install --no-cache-dir -e .

# Install gptzero-api
RUN cd /app/packages/gptzero-api && pip install --no-cache-dir -e .

# Install gptzero-sdk
RUN cd /app/packages/gptzero-sdk && pip install --no-cache-dir -e .

# Install gptzero-service
RUN cd /app/packages/gptzero-service && pip install --no-cache-dir -e .

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
uvicorn gptzero_api.api:app --host 0.0.0.0 --port 8000 &\n\
API_PID=$!\n\
echo "API started with PID $API_PID"\n\
\n\
echo "Waiting for API to be ready..."\n\
sleep 5\n\
\n\
echo "Starting GPTZero Service on port 8501..."\n\
export GPTZERO_API_URL=http://localhost:8000\n\
streamlit run /app/packages/gptzero-service/src/handler.py --server.port=8501 --server.address=0.0.0.0 &\n\
SERVICE_PID=$!\n\
echo "Service started with PID $SERVICE_PID"\n\
\n\
# Wait for both processes\n\
wait $API_PID $SERVICE_PID\n\
' > /app/start.sh && chmod +x /app/start.sh

CMD ["/app/start.sh"]
