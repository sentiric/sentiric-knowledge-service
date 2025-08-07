# app/services/qdrant_service.py
from qdrant_client import QdrantClient, models
from app.core.config import settings
from functools import lru_cache
from app.services.embedding_service import get_embedding_model

# YENİ: Settings'den API key'i okuyacak şekilde güncellendi
@lru_cache(maxsize=1)
def get_qdrant_client():
    # Qdrant Cloud bir API anahtarı gerektirir, bu yüzden onu da ekliyoruz.
    # Eğer API anahtarı .env'de yoksa, None olarak ayarlanır ve yerel bağlantıda sorun çıkarmaz.
    return QdrantClient(
        host=settings.VECTOR_DB_HOST, 
        port=settings.VECTOR_DB_PORT,
        api_key=getattr(settings, 'QDRANT_API_KEY', None) # Yeni satır
    )

# ... (dosyanın geri kalanı aynı) ...
def setup_collection(collection_name: str):
    client = get_qdrant_client()
    model = get_embedding_model()
    try:
        client.get_collection(collection_name=collection_name)
    except Exception:
        client.recreate_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=model.get_sentence_embedding_dimension(),
                distance=models.Distance.COSINE
            ),
        )