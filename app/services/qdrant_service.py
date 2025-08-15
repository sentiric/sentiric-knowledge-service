# app/services/qdrant_service.py
from qdrant_client import QdrantClient, models
from app.core.config import settings
from functools import lru_cache
from app.services.embedding_service import get_embedding_model
from app.core.logging import logger # Logger'ı import et

@lru_cache(maxsize=1)
def get_qdrant_client():
    if settings.QDRANT_API_KEY:
        client = QdrantClient(
            host=settings.VECTOR_DB_HOST, 
            port=settings.VECTOR_DB_PORT,
            api_key=settings.QDRANT_API_KEY,
            https=True
        )
    else:
        client = QdrantClient(
            host=settings.VECTOR_DB_HOST, 
            port=settings.VECTOR_DB_PORT
        )
    return client

def setup_collection(collection_name: str):
    """
    Koleksiyonun var olup olmadığını kontrol eder. Eğer yoksa, oluşturur.
    Mevcut bir koleksiyonu silmez.
    """
    client = get_qdrant_client()
    model = get_embedding_model()
    try:
        # DÜZELTME: Koleksiyon listesini alıp içinde var mı diye bakmak daha güvenilir.
        collections_response = client.get_collections()
        collection_names = [c.name for c in collections_response.collections]
        
        if collection_name in collection_names:
            logger.info("Koleksiyon zaten mevcut, oluşturma atlanıyor.", collection_name=collection_name)
            return

        logger.info("Koleksiyon mevcut değil, yeni koleksiyon oluşturuluyor.", collection_name=collection_name)
        client.recreate_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=model.get_sentence_embedding_dimension(),
                distance=models.Distance.COSINE
            ),
        )
        logger.info("Koleksiyon başarıyla oluşturuldu.", collection_name=collection_name)

    except Exception as e:
        logger.error("Koleksiyon oluşturulurken veya kontrol edilirken hata oluştu.", 
                     error=str(e), 
                     collection_name=collection_name)
        # Hata durumunda uygulamanın çökmemesi için hatayı yutuyoruz.
        # Üretim ortamında bu durum daha dikkatli izlenmelidir.
        pass