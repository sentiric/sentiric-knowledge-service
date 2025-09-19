# --- YENİ İÇERİK ---
import asyncio
import uuid
from contextlib import asynccontextmanager

import grpc
import structlog
from fastapi import FastAPI, Request, Response
from prometheus_fastapi_instrumentator import Instrumentator
from structlog.contextvars import bind_contextvars, clear_contextvars

from app.api.v1.endpoints import router as api_v1_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.services.indexing_service import run_indexing
from app.grpc_server.service import KnowledgeService
from sentiric.knowledge.v1 import knowledge_pb2_grpc

SERVICE_NAME = "knowledge-service"

async def serve_grpc(server: grpc.aio.Server):
    log = structlog.get_logger(__name__)
    listen_addr = f"0.0.0.0:{settings.KNOWLEDGE_SERVICE_GRPC_PORT}"
    server.add_insecure_port(listen_addr)
    log.info("gRPC sunucusu dinlemeye başlıyor...", address=listen_addr)
    await server.start()
    await server.wait_for_termination()

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(log_level=settings.LOG_LEVEL, env=settings.ENV)
    log = structlog.get_logger().bind(service=SERVICE_NAME)
    
    log.info(
        "Uygulama başlatılıyor...",
        project=settings.PROJECT_NAME,
        version=settings.SERVICE_VERSION,
        commit=settings.GIT_COMMIT,
        build_date=settings.BUILD_DATE,
    )

    # --- YENİ MANTIK BAŞLANGICI ---
    # 1. Modelin hazır olmadığını varsayılan olarak ayarla
    app.state.model_ready = False
    log.info("Model durumu 'HAZIR DEĞİL' olarak ayarlandı.")

    # 2. gRPC sunucusunu hemen başlat
    grpc_server = grpc.aio.server()
    knowledge_pb2_grpc.add_KnowledgeServiceServicer_to_server(KnowledgeService(app), grpc_server)
    grpc_task = asyncio.create_task(serve_grpc(grpc_server))

    # 3. HTTP ve gRPC sunucuları başladıktan sonra, ağır işi arka planda yap
    # Bu, 'yield'den önce çalışır ve ana olay döngüsünü bloke etmez.
    async def initial_indexing_task():
        log.info("Arka plan indeksleme görevi başlatıldı.")
        try:
            await run_indexing()
            app.state.model_ready = True
            log.info("Başlangıç indekslemesi tamamlandı. Model durumu 'HAZIR' olarak ayarlandı.")
        except Exception as e:
            log.critical("Başlangıç indekslemesi sırasında kritik hata.", error=str(e), exc_info=True)
            # Hata durumunda bile sunucunun çalışmaya devam etmesini sağlayabiliriz,
            # ama sağlık durumu 'false' kalır.
    
    asyncio.create_task(initial_indexing_task())
    
    yield # Bu noktada FastAPI sunucusu istekleri kabul etmeye başlar
    # --- YENİ MANTIK SONU ---
    
    log.info("Uygulama kapatılıyor...")
    await grpc_server.stop(grace=1)
    grpc_task.cancel()

app_version = settings.SERVICE_VERSION if settings.SERVICE_VERSION else "0.1.0-local"
app = FastAPI(title=settings.PROJECT_NAME, version=app_version, lifespan=lifespan)
log = structlog.get_logger(__name__)

# ... (Middleware aynı kalır) ...
@app.middleware("http")
async def logging_middleware(request: Request, call_next) -> Response:
    clear_contextvars()
    if request.url.path in ["/healthz", "/metrics"]:
        return await call_next(request)
    trace_id = request.headers.get("X-Request-ID") or request.headers.get("X-Trace-ID") or str(uuid.uuid4())
    bind_contextvars(trace_id=trace_id)
    log.info("İstek alındı", http_method=request.method, http_path=request.url.path)
    response = await call_next(request)
    log.info("İstek tamamlandı", http_status_code=response.status_code)
    return response

Instrumentator().instrument(app).expose(app)
app.include_router(api_v1_router, prefix=settings.API_V1_STR)

# --- DEĞİŞTİRİLMİŞ HEALTHCHECK ---
@app.get("/health", tags=["Health"])
@app.head("/health")
def health_check(request: Request):
    is_ready = getattr(request.app.state, 'model_ready', False)
    status_code = 200 if is_ready else 503 # Model hazır değilse 503 Service Unavailable döndür
    
    response_data = {
        "status": "ok" if is_ready else "loading_model",
        "model_ready": is_ready,
        "project": settings.PROJECT_NAME,
        "version": settings.SERVICE_VERSION,
    }
    
    if not is_ready:
        log.warn("Health check: Model henüz yüklenmedi, 503 yanıtı veriliyor.", **response_data)
    
    return Response(content=str(response_data), status_code=status_code, media_type="application/json")
# --- DEĞİŞİKLİK SONU ---

@app.get("/healthz", include_in_schema=False)
async def healthz_check(request: Request):
    # Bu basit check, sadece portun açık olup olmadığını kontrol eder.
    return Response(status_code=200)