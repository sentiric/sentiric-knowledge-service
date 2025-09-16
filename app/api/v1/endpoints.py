# sentiric-knowledge-service/app/api/v1/endpoints.py

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional
import structlog
from app.services.query_service import find_similar_documents
from app.services.indexing_service import trigger_reindexing
from app.core.config import settings

router = APIRouter()
log = structlog.get_logger(__name__)

class QueryRequest(BaseModel):
    query: str
    tenant_id: str
    top_k: int = 3

class QueryResponse(BaseModel):
    results: list

class ReindexRequest(BaseModel):
    tenant_id: Optional[str] = Field(None, description="Eğer belirtilirse sadece bu tenant yeniden indekslenir. Boş bırakılırsa tüm sistem indekslenir.")

class ReindexResponse(BaseModel):
    message: str
    tenant_id: Optional[str]

@router.post("/query", response_model=QueryResponse, tags=["Query"])
async def query_knowledge_base(request: QueryRequest):
    try:
        collection_name = f"{settings.VECTOR_DB_COLLECTION_PREFIX}{request.tenant_id}"
        results = await find_similar_documents(request.query, collection_name, request.top_k)
        return {"results": results}
    except Exception as e:
        log.error("Sorgu sırasında hata oluştu", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Dahili sunucu hatası")

@router.post("/reindex", response_model=ReindexResponse, tags=["Admin"])
async def reindex_knowledge_base(request: ReindexRequest, background_tasks: BackgroundTasks):
    """
    Bilgi tabanını yeniden indeksler. Bu işlem uzun sürebileceği için arka planda çalışır.
    """
    target = request.tenant_id if request.tenant_id else "ALL"
    log.info("Re-index isteği alındı.", target=target)
    
    background_tasks.add_task(trigger_reindexing, tenant_id=request.tenant_id)
    
    return {
        "message": "Re-indexing process started in the background.",
        "tenant_id": request.tenant_id
    }