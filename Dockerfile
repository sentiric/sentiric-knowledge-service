# sentiric-knowledge-service/Dockerfile
# --- STAGE 1: Builder ---
FROM python:3.11-slim-bullseye AS builder

WORKDIR /app

ENV PIP_BREAK_SYSTEM_PACKAGES=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/app/cache/huggingface

# Gerekli sistem bağımlılıklarını kur (git ve playwright için eklemeler)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# pip'i güncelle ve torch'u kur
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# YENİ: Playwright tarayıcılarını kur
RUN playwright install --with-deps chromium

# Model önbellekleme (pre-caching) adımı
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# --- STAGE 2: Production ---
FROM python:3.11-slim-bullseye

WORKDIR /app

ENV HF_HOME=/app/cache/huggingface \
    PIP_BREAK_SYSTEM_PACKAGES=1

# Çalışma zamanı sistem bağımlılıkları (playwright için gerekli olanlar dahil)
RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-openbsd \
    curl \
    ca-certificates \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libx11-6 \
    libxcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libxrender1 \
    libxtst6 \
    libasound2 \
    libpangocairo-1.0-0 \
    libharfbuzz0b \
    libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*

# Builder'dan dosyaları kopyala
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder ${HF_HOME} ${HF_HOME}
COPY --from=builder /ms-playwright /ms-playwright

# Playwright'ın tarayıcıları bulabilmesi için environment değişkeni
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

COPY ./app ./app
RUN mkdir -p /app/data

# Güvenlik için root olmayan kullanıcı oluştur
RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --no-create-home --uid 1001 --ingroup appgroup appuser

RUN chown -R appuser:appgroup /app
RUN chown -R appuser:appgroup /ms-playwright

USER appuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "12040", "--no-access-log"]