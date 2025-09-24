# sentiric-knowledge-service/app/main.py
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
from app.grpc_server.service import KnowledgeService
from app.services.indexing_service import run_indexing
from sentiric.knowledge.v1 import knowledge_pb2_grpc

SERVICE_NAME = "knowledge-service"

def load_server_credentials():
    log = structlog.get_logger(__name__)
    if not all([settings.KNOWLEDGE_SERVICE_KEY_PATH, settings.KNOWLEDGE_SERVICE_CERT_PATH, settings.GRPC_TLS_CA_PATH]):
        log.warn("mTLS sertifika yolları tam olarak yapılandırılmamış. gRPC sunucusu başlatılamayacak.")
        return None
    
    log.info("gRPC için mTLS sertifikaları yükleniyor...")
    try:
        private_key = open(settings.KNOWLEDGE_SERVICE_KEY_PATH, 'rb').read()
        certificate_chain = open(settings.KNOWLEDGE_SERVICE_CERT_PATH, 'rb').read()
        root_ca = open(settings.GRPC_TLS_CA_PATH, 'rb').read()
        return grpc.ssl_server_credentials(
            private_key_certificate_chain_pairs=[(private_key, certificate_chain)],
            root_certificates=root_ca,
            require_client_auth=True
        )
    except Exception as e:
        log.critical("mTLS sertifikaları yüklenirken hata oluştu.", error=str(e))
        return None

async def serve_grpc(server: grpc.aio.Server):
    log = structlog.get_logger(__name__)
    listen_addr = f"0.0.0.0:{settings.KNOWLEDGE_SERVICE_GRPC_PORT}"
    
    credentials = load_server_credentials()
    if not credentials:
        log.warn("gRPC sunucusu için mTLS kimlik bilgileri yüklenemedi, sunucu başlatılmıyor.")
        return

    server.add_secure_port(listen_addr, credentials)
    log.info("Güvenli (mTLS) gRPC sunucusu dinlemeye başlıyor...", address=listen_addr)
    await server.start()
    await server.wait_for_termination()

async def run_indexing_background(app: FastAPI):
    log = structlog.get_logger(__name__)
    log.info("Arka plan indeksleme görevi başlatıldı.")
    try:
        await run_indexing()
        app.state.model_ready = True
        log.info("Başlangıç indekslemesi tamamlandı. Model durumu 'HAZIR' olarak ayarlandı.")
    except Exception as e:
        log.critical("Başlangıç indekslemesi sırasında kritik hata.", error=str(e), exc_info=True)

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
        mode=settings.KNOWLEDGE_SERVICE_APP_MODE # DÜZELTME
    )

    app.state.model_ready = False
    
    grpc_server = None
    grpc_task = None
    if settings.KNOWLEDGE_SERVICE_APP_MODE.upper() == "HYBRID": # DÜZELTME
        grpc_server = grpc.aio.server()
        knowledge_pb2_grpc.add_KnowledgeServiceServicer_to_server(KnowledgeService(app), grpc_server)
        grpc_task = asyncio.create_task(serve_grpc(grpc_server))
    else:
        log.info("HTTP_ONLY modunda çalışılıyor, gRPC sunucusu atlandı.")

    asyncio.create_task(run_indexing_background(app))
    
    yield
    
    log.info("Uygulama kapatılıyor...")
    if grpc_server and grpc_task:
        await grpc_server.stop(grace=1)
        grpc_task.cancel()

app = FastAPI(title=settings.PROJECT_NAME, version=settings.SERVICE_VERSION, lifespan=lifespan)

@app.middleware("http")
async def logging_middleware(request: Request, call_next) -> Response:
    log = structlog.get_logger(__name__)
    clear_contextvars()
    if request.url.path in ["/healthz", "/metrics"]:
        return await call_next(request)
    trace_id = request.headers.get("X-Request-ID") or request.headers.get("X-Trace-ID") or str(uuid.uuid4())
    bind_contextvars(trace_id=trace_id)
    log.info("İstek alındı", http_method=request.method, http_path=request.url.path)
    response = await call_next(request)
    log.info("İstek tamamlandı", http_status_code=response.status_code)
    return response

app.include_router(api_v1_router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["Health"])
@app.head("/health")
def health_check(request: Request):
    log = structlog.get_logger(__name__)
    is_ready = getattr(request.app.state, 'model_ready', False)
    status_code = 200 if is_ready else 503
    
    response_data = {
        "status": "ok" if is_ready else "loading_model",
        "model_ready": is_ready,
        "project": settings.PROJECT_NAME,
        "version": settings.SERVICE_VERSION,
        "app_mode": settings.KNOWLEDGE_SERVICE_APP_MODE, # DÜZELTME
    }
    
    if not is_ready:
        log.warn("Health check: Model henüz yüklenmedi, 503 yanıtı veriliyor.", **response_data)
    
    return Response(content=str(response_data), status_code=status_code, media_type="application/json")

@app.get("/healthz", include_in_schema=False)
async def healthz_check():
    return Response(status_code=200)

Instrumentator().instrument(app).expose(app)