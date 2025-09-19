# sentiric-knowledge-service/app/services/qdrant_service.py
from qdrant_client import QdrantClient, models
from app.core.config import settings
from functools import lru_cache
from app.services.embedding_service import get_embedding_model
import structlog

log = structlog.get_logger(__name__)

@lru_cache(maxsize=1)
def get_qdrant_client():
    # Artırılmış timeout süresi (saniye)
    QDRANT_TIMEOUT = 60.0

    if settings.QDRANT_API_KEY:
        client = QdrantClient(
            host=settings.VECTOR_DB_HOST, 
            port=settings.VECTOR_DB_HTTP_PORT,
            api_key=settings.QDRANT_API_KEY,
            https=True,
            timeout=QDRANT_TIMEOUT
        )
    else:
        client = QdrantClient(
            host=settings.VECTOR_DB_HOST, 
            port=settings.VECTOR_DB_HTTP_PORT,
            timeout=QDRANT_TIMEOUT
        )
    log.info("Qdrant istemcisi oluşturuldu.", timeout=QDRANT_TIMEOUT)
    return client

def setup_collection(collection_name: str):
    """
    Koleksiyonun var olup olmadığını kontrol eder. Eğer yoksa, oluşturur.
    Mevcut bir koleksiyonu silmez.
    """
    client = get_qdrant_client()
    model = get_embedding_model()
    try:
        collections_response = client.get_collections()
        collection_names = [c.name for c in collections_response.collections]
        
        if collection_name in collection_names:
            log.info("Koleksiyon zaten mevcut, oluşturma atlanıyor.", collection_name=collection_name)
            return

        log.info("Koleksiyon mevcut değil, yeni koleksiyon oluşturuluyor.", collection_name=collection_name)
        client.recreate_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=model.get_sentence_embedding_dimension(),
                distance=models.Distance.COSINE
            ),
        )
        log.info("Koleksiyon başarıyla oluşturuldu.", collection_name=collection_name)

    except Exception as e:
        log.error("Koleksiyon oluşturulurken veya kontrol edilirken hata oluştu.", 
                     error=str(e), 
                     collection_name=collection_name)
        pass