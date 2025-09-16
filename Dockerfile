# sentiric-knowledge-service/Dockerfile

# --- STAGE 1: Builder ---
FROM python:3.11-slim-bullseye AS builder

WORKDIR /app

ENV PIP_BREAK_SYSTEM_PACKAGES=1 \
    HF_HOME=/app/cache/huggingface

RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# --- STAGE 2: Production ---
FROM python:3.11-slim-bullseye

RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-openbsd \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* 
    
WORKDIR /app

ENV HF_HOME=/app/cache/huggingface \
    PIP_BREAK_SYSTEM_PACKAGES=1

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder ${HF_HOME} ${HF_HOME}

COPY ./app ./app
RUN mkdir -p /app/data

# DÜZELTME: Standart komut formatı
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "12040"]