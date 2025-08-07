from qdrant_client import QdrantClient, models
from app.core.config import settings
from functools import lru_cache
from app.services.embedding_service import get_embedding_model

@lru_cache(maxsize=1)
def get_qdrant_client():
    return QdrantClient(host=settings.VECTOR_DB_HOST, port=settings.VECTOR_DB_PORT)

# DÜZELTME: collection_name argümanını kabul et
def setup_collection(collection_name: str):
    """Qdrant'ta koleksiyonun var olup olmadığını kontrol eder, yoksa oluşturur."""
    client = get_qdrant_client()
    model = get_embedding_model()
    try:
        # Eğer koleksiyon varsa bir şey yapma
        client.get_collection(collection_name=collection_name)
    except Exception:
        # Koleksiyon yoksa yeniden oluştur
        client.recreate_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=model.get_sentence_embedding_dimension(),
                distance=models.Distance.COSINE
            ),
        )