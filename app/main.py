import asyncio
# import sys
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
    log = structlog.get_logger("lifespan")
    log.info("Application starting up...")

    grpc_server = grpc.aio.server()
    knowledge_pb2_grpc.add_KnowledgeServiceServicer_to_server(KnowledgeService(), grpc_server)
    grpc_task = asyncio.create_task(serve_grpc(grpc_server))

    log.info("Initial knowledge base indexing will run in the background.")
    try:
        await run_indexing()
        log.info("Initial indexing completed.")
    except Exception as e:
        log.error("Critical error during initial indexing.", error=str(e), exc_info=True)
    
    yield
    
    log.info("Application shutting down...")
    await grpc_server.stop(grace=1)
    grpc_task.cancel()


app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0", lifespan=lifespan)
log = structlog.get_logger(__name__)

@app.middleware("http")
async def logging_middleware(request: Request, call_next) -> Response:
    clear_contextvars()
    
    if request.url.path == "/healthz":
        return await call_next(request)
        
    request_id = request.headers.get("X-Request-ID") or request.headers.get("X-Trace-ID") or str(uuid.uuid4())
    bind_contextvars(request_id=request_id)
    
    log.info("Request received", http_method=request.method, http_path=request.url.path)
    response = await call_next(request)
    log.info("Request completed", http_status_code=response.status_code)
    return response

Instrumentator().instrument(app).expose(app)
app.include_router(api_v1_router, prefix=settings.API_V1_STR)

@app.get("/health", tags=["Health"])
@app.head("/health")
def health_check():
    return {"status": "ok", "project": settings.PROJECT_NAME}

@app.get("/healthz", include_in_schema=False)
async def healthz_check():
    return Response(status_code=200)