# ======================================================================================
#    SENTIRIC PYTHON SERVICE - STANDART DOCKERFILE v2.2 (Final Permissions Fix)
# ======================================================================================
ARG PYTHON_VERSION=3.11
ARG BASE_IMAGE_TAG=${PYTHON_VERSION}-slim-bullseye

# STAGE 1: BUILDER
FROM python:${BASE_IMAGE_TAG} AS builder
WORKDIR /app
ENV PIP_BREAK_SYSTEM_PACKAGES=1 PIP_NO_CACHE_DIR=1 POETRY_NO_INTERACTION=1 POETRY_VIRTUALENVS_IN_PROJECT=true \
    PLAYWRIGHT_BROWSERS_PATH=/root/.cache/ms-playwright \
    HF_HOME="/app/data/.cache/huggingface"
RUN apt-get update && apt-get install -y --no-install-recommends curl build-essential && \
    pip install --no-cache-dir --upgrade pip poetry && \
    rm -rf /var/lib/apt/lists/*
COPY poetry.lock pyproject.toml ./
RUN mkdir -p ${HF_HOME} && mkdir -p ${PLAYWRIGHT_BROWSERS_PATH}
RUN poetry install --without dev --no-root --sync && \
    poetry run playwright install --with-deps chromium

# STAGE 2: PRODUCTION
FROM python:${BASE_IMAGE_TAG}
WORKDIR /app
ARG GIT_COMMIT="unknown"
ARG BUILD_DATE="unknown"
ARG SERVICE_VERSION="0.0.0"
ENV GIT_COMMIT=${GIT_COMMIT} BUILD_DATE=${BUILD_DATE} SERVICE_VERSION=${SERVICE_VERSION} \
    PYTHONUNBUFFERED=1 PATH="/app/.venv/bin:$PATH" \
    PLAYWRIGHT_BROWSERS_PATH=/home/appuser/.cache/ms-playwright \
    HF_HOME="/app/data/.cache/huggingface"
RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-openbsd curl ca-certificates libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdbus-1-3 libdrm2 libgbm1 libgtk-3-0 libx11-6 libxcb1 libxcomposite1 \
    libxdamage1 libxext6 libxfixes3 libxrandr2 libxrender1 libxtst6 libasound2 \
    libpangocairo-1.0-0 libharfbuzz0b libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*
RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --no-create-home --uid 1001 --ingroup appgroup appuser
COPY --from=builder --chown=appuser:appgroup /app/.venv ./.venv
COPY --from=builder --chown=appuser:appgroup /app/data /app/data
COPY --from=builder --chown=appuser:appgroup /root/.cache/ms-playwright ${PLAYWRIGHT_BROWSERS_PATH}
COPY --chown=appuser:appgroup ./app ./app
# --- NİHAİ DÜZELTME BURADA ---
# /app dizininin tamamının ve alt dizinlerinin sahipliğini appuser'a veriyoruz.
RUN chown -R appuser:appgroup /app
# --- NİHAİ DÜZELTME SONU ---
USER appuser
EXPOSE 7860
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "12040", "--no-access-log"]