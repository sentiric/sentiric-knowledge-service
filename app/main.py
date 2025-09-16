# sentiric-knowledge-service/app/main.py

import sys
import asyncio
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from prometheus_fastapi_instrumentator import Instrumentator
from structlog.contextvars import bind_contextvars, clear_contextvars

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from app.api.v1.endpoints import router as api_v1_router
from app.core.config import settings
from app.core.logging import logger
from app.services.indexing_service import run_indexing

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Uygulama başlıyor...", env=settings.ENV, log_level=settings.LOG_LEVEL)
    logger.info("Bilgi bankası ilk indeksleme çalıştırılıyor...")
    
    try:
        await run_indexing()
        logger.info("İlk indeksleme tamamlandı.")
    except Exception as e:
        logger.error("Başlangıç indekslemesi sırasında kritik hata oluştu. Servis çalışmaya devam edecek ancak RAG yetenekleri kısıtlı olabilir.", error=str(e), exc_info=True)
    
    yield
    logger.info("Uygulama kapanıyor.")

app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0", lifespan=lifespan)

@app.middleware("http")
async def logging_middleware(request: Request, call_next) -> Response:
    clear_contextvars()
    # YENİ: /healthz isteklerini loglamadan atla
    if request.url.path == "/healthz":
        return await call_next(request)
        
    request_id = request.headers.get("X-Request-ID") or request.headers.get("X-Trace-ID") or str(uuid.uuid4())
    bind_contextvars(request_id=request_id)
    logger.info("http.request.started", http_method=request.method, http_path=request.url.path, remote_addr=request.client.host if request.client else "unknown")
    response = await call_next(request)
    logger.info("http.request.finished", http_status_code=response.status_code)
    return response

Instrumentator().instrument(app).expose(app)
app.include_router(api_v1_router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["Health"])
@app.head("/health")
def health_check():
    return {"status": "ok", "project": settings.PROJECT_NAME}

# YENİ: Log basmayan basit sağlık kontrolü endpoint'i
@app.get("/healthz", include_in_schema=False)
async def healthz_check():
    return Response(status_code=200)