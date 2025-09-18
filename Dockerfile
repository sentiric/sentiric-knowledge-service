# ======================================================================================
#    SENTIRIC KNOWLEDGE SERVICE - OPTIMIZE EDİLMİŞ VE HATASIZ DOCKERFILE v1.1
# ======================================================================================

# --- GLOBAL BUILD ARGÜMANLARI ---
ARG PYTHON_VERSION=3.11
ARG BASE_IMAGE_TAG=${PYTHON_VERSION}-slim-bullseye
ARG PYTORCH_EXTRA_INDEX_URL="https://download.pytorch.org/whl/cpu"

# ======================================================================================
#    STAGE 1: BUILDER
# ======================================================================================
FROM python:${BASE_IMAGE_TAG} AS builder

# Build argümanlarını bu aşamada da kullanılabilir yap
ARG GIT_COMMIT="unknown"
ARG BUILD_DATE="unknown"
ARG SERVICE_VERSION="0.0.0"
ARG PYTORCH_EXTRA_INDEX_URL

WORKDIR /app

# Ortam değişkenleri
ENV PIP_BREAK_SYSTEM_PACKAGES=1 \
    PIP_NO_CACHE_DIR=1 \
    PLAYWRIGHT_BROWSERS_PATH=/root/.cache/ms-playwright

# Gerekli sistem bağımlılıklarını kur
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# pip'i güncelle
RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt .
# --extra-index-url'i burada kullanarak torch kurulumunu diğerlerinden ayırmaya gerek kalmaz
RUN pip install --no-cache-dir -r requirements.txt --extra-index-url "${PYTORCH_EXTRA_INDEX_URL}"

# Playwright tarayıcılarını kur (doğru cache dizinine)
RUN playwright install --with-deps chromium

# Model önbellekleme
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"


# ======================================================================================
#    STAGE 2: PRODUCTION
# ======================================================================================
FROM python:${BASE_IMAGE_TAG}

WORKDIR /app

# Build zamanı bilgileri
ARG GIT_COMMIT
ARG BUILD_DATE
ARG SERVICE_VERSION
ENV GIT_COMMIT=${GIT_COMMIT} \
    BUILD_DATE=${BUILD_DATE} \
    SERVICE_VERSION=${SERVICE_VERSION} \
    PIP_BREAK_SYSTEM_PACKAGES=1 \
    PLAYWRIGHT_BROWSERS_PATH=/home/appuser/.cache/ms-playwright

# Çalışma zamanı sistem bağımlılıkları
RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-openbsd \
    curl \
    ca-certificates \
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdbus-1-3 libdrm2 libgbm1 libgtk-3-0 \
    libx11-6 libxcb1 libxcomposite1 libxdamage1 libxext6 libxfixes3 libxrandr2 libxrender1 libxtst6 \
    libasound2 libpangocairo-1.0-0 libharfbuzz0b libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*

# Güvenlik için root olmayan kullanıcı oluştur
RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --no-create-home --uid 1001 --ingroup appgroup appuser

# Builder'dan dosyaları kopyala ve sahipliği yeni kullanıcıya ver
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
# DÜZELTME: Doğru cache yolundan kopyala ve hedefte de doğru yere koy
COPY --from=builder --chown=appuser:appgroup /root/.cache /home/appuser/.cache

# Uygulama kodunu kopyala
COPY ./app ./app
RUN mkdir -p /app/data
RUN chown -R appuser:appgroup /app

USER appuser

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "12040", "--no-access-log"]