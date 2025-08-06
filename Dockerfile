# --- STAGE 1: Builder ---
FROM python:3.11-slim-bullseye AS builder

WORKDIR /app

# pip'in sanal ortamlar dışında da çalışmasına izin ver
ENV PIP_BREAK_SYSTEM_PACKAGES=1 \
    HF_HOME=/app/cache/huggingface

# Sadece CPU için torch kurarak imaj boyutunu küçült
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Bağımlılıkları SİSTEM GENELİNE kur
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# YENİ: Playwright için gerekli tarayıcıları indir ve kur
RUN python -m playwright install --with-deps chromium

# Modeli indir
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"


# --- STAGE 2: Production ---
FROM python:3.11-slim-bullseye

WORKDIR /app

# Cache ve PATH'i üretim ortamı için ayarla
ENV HF_HOME=/app/cache/huggingface \
    # Bu değişken, production imajında da bulunursa iyi olur
    PIP_BREAK_SYSTEM_PACKAGES=1 

# Builder'dan SİSTEM GENELİNDEKİ paketleri kopyala
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
# uvicorn gibi çalıştırılabilir dosyaların olduğu bin klasörünü de kopyala
COPY --from=builder /usr/local/bin /usr/local/bin

# Builder'dan indirilmiş ve cache'lenmiş modeli kopyala
COPY --from=builder ${HF_HOME} ${HF_HOME}

# Uygulama kodunu kopyala
COPY ./app ./app
COPY ./data ./data

EXPOSE 5055
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5055"]