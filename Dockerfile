# Dockerfile

# --- STAGE 1: Builder ---
FROM python:3.11-slim-bullseye AS builder

WORKDIR /app

ENV PIP_BREAK_SYSTEM_PACKAGES=1 \
    HF_HOME=/app/cache/huggingface

# Sadece CPU için torch kurarak imaj boyutunu küçültüyoruz.
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Bağımlılıkları kur
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Embedding modelini build aşamasında indiriyoruz.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# --- STAGE 2: Production ---
FROM python:3.11-slim-bullseye

WORKDIR /app

ENV HF_HOME=/app/cache/huggingface \
    PIP_BREAK_SYSTEM_PACKAGES=1

# Builder'dan sadece kurulu Python paketlerini ve çalıştırılabilir dosyaları kopyala
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Builder'dan indirilmiş ve cache'lenmiş AI modelini kopyala
COPY --from=builder ${HF_HOME} ${HF_HOME}

# Uygulama kodunu ve dışarıdan bağlanacak veri klasörünü oluştur
COPY ./app ./app
RUN mkdir -p /app/data

# API sunucusunun çalışacağı port
EXPOSE 5055

# Uvicorn ile uygulamayı başlat
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5055"]