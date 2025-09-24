# ======================================================================================
#    SENTIRIC PYTHON SERVICE - STANDART DOCKERFILE v2.0
# ======================================================================================

# --- GLOBAL BUILD ARGÜMANLARI ---
ARG PYTHON_VERSION=3.11
ARG BASE_IMAGE_TAG=${PYTHON_VERSION}-slim-bullseye

# ======================================================================================
#    STAGE 1: BUILDER - Bağımlılıkları kurar
# ======================================================================================
FROM python:${BASE_IMAGE_TAG} AS builder

WORKDIR /app

ENV PIP_BREAK_SYSTEM_PACKAGES=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    PLAYWRIGHT_BROWSERS_PATH=/home/appuser/.cache/ms-playwright

# Gerekli sistem bağımlılıkları ve Poetry kurulumu
RUN apt-get update && apt-get install -y --no-install-recommends curl build-essential && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir poetry && \
    rm -rf /var/lib/apt/lists/*

# Sadece bağımlılık tanımlarını kopyala ve kur (Docker build cache'ini optimize eder)
COPY poetry.lock pyproject.toml ./
RUN poetry install --without dev --no-root --sync && \
    playwright install --with-deps chromium

# ======================================================================================
#    STAGE 2: PRODUCTION - Hafif ve güvenli imaj
# ======================================================================================
FROM python:${BASE_IMAGE_TAG}

WORKDIR /app

# Build-time bilgileri
ARG GIT_COMMIT="unknown"
ARG BUILD_DATE="unknown"
ARG SERVICE_VERSION="0.0.0"
ENV GIT_COMMIT=${GIT_COMMIT} \
    BUILD_DATE=${BUILD_DATE} \
    SERVICE_VERSION=${SERVICE_VERSION} \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    PLAYWRIGHT_BROWSERS_PATH=/home/appuser/.cache/ms-playwright

# Çalışma zamanı sistem bağımlılıkları (Playwright için gerekli olanlar dahil)
RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-openbsd \
    curl \
    ca-certificates \
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdbus-1-3 libdrm2 libgbm1 libgtk-3-0 \
    libx11-6 libxcb1 libxcomposite1 libxdamage1 libxext6 libxfixes3 libxrandr2 libxrender1 libxtst6 \
    libasound2 libpangocairo-1.0-0 libharfbuzz0b libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*

# Root olmayan kullanıcı oluştur
RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --no-create-home --uid 1001 --ingroup appgroup appuser

# Bağımlılıkları, uygulama kodunu ve Playwright tarayıcılarını kopyala
COPY --from=builder --chown=appuser:appgroup /app/.venv ./.venv
COPY --from=builder --chown=appuser:appgroup ${PLAYWRIGHT_BROWSERS_PATH} ${PLAYWRIGHT_BROWSERS_PATH}
COPY --chown=appuser:appgroup ./app ./app

# Sahipliği ayarla ve kullanıcıyı değiştir
USER appuser

# knowledge-service için varsayılan komut
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "12040", "--no-access-log"]