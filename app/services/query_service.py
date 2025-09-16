# sentiric-knowledge-service/app/services/query_service.py

import asyncio
from qdrant_client.http import models
from qdrant_client.http.exceptions import UnexpectedResponse
from app.services.qdrant_service import get_qdrant_client
from app.services.embedding_service import get_embedding_model
import structlog # structlog'u import et

log = structlog.get_logger(__name__) # logger'ı tanımla

async def find_similar_documents(query: str, collection_name: str, top_k: int) -> list:
    client = get_qdrant_client()
    model = get_embedding_model()
    
    query_vector = await asyncio.to_thread(model.encode, query)

    try:
        search_result = await asyncio.to_thread(
            client.search,
            collection_name=collection_name,
            query_vector=query_vector.tolist(),
            limit=top_k,
        )
        return search_result
    except UnexpectedResponse as e:
        # --- YENİ HATA YÖNETİMİ ---
        # Eğer hata "Not Found" ise, bu bir sistem hatası değil, beklenen bir durumdur.
        # Boş bir liste dönerek agent-service'in çökmesini engelliyoruz.
        if "not found" in str(e).lower() or "doesn't exist" in str(e).lower():
            log.warn(
                "Query received for a non-existent collection",
                collection_name=collection_name,
                reason="No datasources are defined for this tenant in the database."
            )
            return [] # Boş liste döndür
        else:
            # Diğer beklenmedik Qdrant hatalarını yine de yükselt
            raise e
    # --- HATA YÖNETİMİ SONU ---