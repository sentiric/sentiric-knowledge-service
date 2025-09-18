# sentiric-knowledge-service/Dockerfile
# --- STAGE 1: Builder ---
FROM python:3.11-slim-bullseye AS builder

WORKDIR /app

ENV PIP_BREAK_SYSTEM_PACKAGES=1 \
    HF_HOME=/app/cache/huggingface

# git'i kur
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# pip'i güncelle ve torch'u kur
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
# Bu komut artık doğru versiyonlarla çalışacak
RUN pip install --no-cache-dir -r requirements.txt

# Model önbellekleme (pre-caching) adımı
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

# Builder'dan kurulan kütüphaneleri ve önbelleklenmiş modeli kopyala
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder ${HF_HOME} ${HF_HOME}

COPY ./app ./app
RUN mkdir -p /app/data

# Güvenlik için root olmayan kullanıcı oluştur
RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --no-create-home --uid 1001 --ingroup appgroup appuser

# DEĞİŞİKLİK BURADA: appuser'a /app dizini üzerinde sahiplik ver
RUN chown -R appuser:appgroup /app

# Kullanıcıyı değiştir
USER appuser

# Uygulamayı başlat
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "12040", "--no-access-log"]