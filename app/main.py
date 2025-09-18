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
    
    # --- DEĞİŞİKLİK: Başlangıç logunu zenginleştiriyoruz ---
    log.info(
        "Uygulama başlatılıyor...",
        project=settings.PROJECT_NAME,
        version=settings.SERVICE_VERSION,
        commit=settings.GIT_COMMIT,
        build_date=settings.BUILD_DATE,
    )
    # --- DEĞİŞİKLİK SONU ---

    grpc_server = grpc.aio.server()
    knowledge_pb2_grpc.add_KnowledgeServiceServicer_to_server(KnowledgeService(), grpc_server)
    grpc_task = asyncio.create_task(serve_grpc(grpc_server))

    log.info("Başlangıç bilgi tabanı indekslemesi arka planda çalışacak.")
    try:
        await run_indexing()
        log.info("Başlangıç indekslemesi tamamlandı.")
    except Exception as e:
        log.error("Başlangıç indekslemesi sırasında kritik hata.", error=str(e), exc_info=True)
    
    yield
    
    log.info("Uygulama kapatılıyor...")
    await grpc_server.stop(grace=1)
    grpc_task.cancel()


app = FastAPI(title=settings.PROJECT_NAME, version=settings.SERVICE_VERSION, lifespan=lifespan)
log = structlog.get_logger(__name__)

@app.middleware("http")
async def logging_middleware(request: Request, call_next) -> Response:
    clear_contextvars()
    
    # Prometheus metrikleri ve basit health check'leri log kirliliği yapmasın
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

# --- DEĞİŞİKLİK: Health check endpoint'ini zenginleştiriyoruz ---
@app.get("/health", tags=["Health"])
@app.head("/health")
def health_check():
    return {
        "status": "ok", 
        "project": settings.PROJECT_NAME,
        "version": settings.SERVICE_VERSION,
        "commit": settings.GIT_COMMIT,
        "build_date": settings.BUILD_DATE
    }
# --- DEĞİŞİKLİK SONU ---

@app.get("/healthz", include_in_schema=False)
async def healthz_check():
    return Response(status_code=200)