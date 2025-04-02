FROM ubuntu:24.04

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

WORKDIR /service

RUN python -m venv /service/.venv

ENV PATH="/service/.venv/bin:$PATH"

COPY requirements.txt .

RUN python -m pip install --upgrade pip
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY src/ ./

RUN chmod +x authenticity/resources/c2patool/v0.16.1/Linux/c2patool

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

CMD ["/service/.venv/bin/streamlit", "run", "handler.py", "--server.port=8501", "--server.address=0.0.0.0"]
