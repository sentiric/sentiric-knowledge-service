from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.query_service import find_similar_documents
from app.core.logging import logger
from app.core.config import settings # DÜZELTME: Eksik olan import bu satır.

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    tenant_id: str
    top_k: int = 3

class QueryResponse(BaseModel):
    results: list

@router.post("/query", response_model=QueryResponse, tags=["Query"])
async def query_knowledge_base(request: QueryRequest):
    try:
        # Sorguyu tenant'a özel koleksiyonda yap
        collection_name = f"{settings.VECTOR_DB_COLLECTION_PREFIX}{request.tenant_id}"
        results = await find_similar_documents(request.query, collection_name, request.top_k)
        return {"results": results}
    except Exception as e:
        logger.error("Sorgu sırasında hata oluştu", error=str(e))
        raise HTTPException(status_code=500, detail="Dahili sunucu hatası")