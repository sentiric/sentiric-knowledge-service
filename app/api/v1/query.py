from fastapi import APIRouter
from pydantic import BaseModel
from app.services.qdrant_service import get_qdrant_client, get_embedding_model
from app.core.config import settings

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    top_k: int = 3

class QueryResponse(BaseModel):
    results: list

@router.post("/query", response_model=QueryResponse)
def query_knowledge_base(request: QueryRequest):
    """
    Verilen bir sorgu için bilgi bankasında anlamsal arama yapar.
    """
    client = get_qdrant_client()
    model = get_embedding_model()

    query_vector = model.encode(request.query).tolist()

    search_result = client.search(
        collection_name=settings.QDRANT_COLLECTION_NAME,
        query_vector=query_vector,
        limit=request.top_k,
    )

    return {"results": search_result}