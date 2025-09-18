# sentiric-knowledge-service/app/services/query_service.py
import asyncio
import structlog
from qdrant_client.http.exceptions import UnexpectedResponse
from app.services.qdrant_service import get_qdrant_client
from app.services.embedding_service import get_embedding_model

log = structlog.get_logger(__name__)

async def find_similar_documents(query: str, collection_name: str, top_k: int) -> list:
    """
    Verilen bir metin sorgusuna anlamsal olarak en yakın dokümanları Qdrant'ta arar.
    """
    client = get_qdrant_client()
    model = get_embedding_model()
    
    # model.encode senkron bir işlem olduğu için ana event loop'u bloklamamak
    # adına to_thread ile çalıştırılır.
    query_vector = await asyncio.to_thread(model.encode, query)

    try:
        # client.search de senkron bir I/O operasyonu olduğu için to_thread kullanılır.
        search_result = await asyncio.to_thread(
            client.search,
            collection_name=collection_name,
            query_vector=query_vector.tolist(),
            limit=top_k,
        )
        return search_result
    except UnexpectedResponse as e:
        # Eğer sorgulanan koleksiyon (tenant'a ait veri) henüz oluşturulmamışsa,
        # bu bir sistem hatası değildir. Boş liste dönerek akışın devam etmesini sağlarız.
        if "not found" in str(e).lower() or "doesn't exist" in str(e).lower():
            log.warn(
                "Mevcut olmayan bir koleksiyon için sorgu alındı",
                collection_name=collection_name,
                reason="Bu tenant için veritabanında henüz bir veri kaynağı tanımlanmamış olabilir."
            )
            return []  # Hata fırlatmak yerine boş liste döndür
        else:
            # Diğer beklenmedik Qdrant hatalarını logla ve yeniden fırlat
            log.error("Qdrant araması sırasında beklenmedik hata", error=str(e), exc_info=True)
            raise e
    except Exception as e:
        log.error("find_similar_documents içinde genel bir hata oluştu", error=str(e), exc_info=True)
        raise e