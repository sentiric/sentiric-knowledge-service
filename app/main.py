from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.v1.endpoints import router as api_v1_router
from app.core.config import settings
from app.core.logging import logger
from app.services.indexing_service import run_indexing

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Uygulama başladığında çalışacak kod
    logger.info("Uygulama başlıyor...")
    logger.info("Bilgi bankası indeksleniyor...")
    run_indexing()
    logger.info("İndeksleme tamamlandı.")
    yield
    # Uygulama kapandığında çalışacak kod
    logger.info("Uygulama kapanıyor.")

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

# Metrikleri otomatik olarak expose et
Instrumentator().instrument(app).expose(app)

app.include_router(api_v1_router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}