# app/services/qdrant_service.py
from qdrant_client import QdrantClient, models
from app.core.config import settings
from functools import lru_cache
from app.services.embedding_service import get_embedding_model

@lru_cache(maxsize=1)
def get_qdrant_client():
    # --- DEĞİŞİKLİK BURADA: Qdrant Cloud için tam yapılandırma ---
    
    # Eğer bir API anahtarı tanımlıysa, bu Qdrant Cloud demektir.
    if settings.QDRANT_API_KEY:
        # Bulut ortamında HTTPS kullanmalıyız.
        client = QdrantClient(
            host=settings.VECTOR_DB_HOST, 
            port=settings.VECTOR_DB_PORT,
            api_key=settings.QDRANT_API_KEY,
            https=True  # <-- EN KRİTİK DEĞİŞİKLİK
        )
    else:
        # Yerel ortamda (API anahtarı yok), standart HTTP kullanıyoruz.
        client = QdrantClient(
            host=settings.VECTOR_DB_HOST, 
            port=settings.VECTOR_DB_PORT
        )
        
    return client

# ... (setup_collection fonksiyonu aynı kalacak, hiçbir değişiklik yok) ...
def setup_collection(collection_name: str):
    client = get_qdrant_client()
    model = get_embedding_model()
    try:
        # get_collection hataya neden oluyor, çünkü 404'ü istisna olarak fırlatıyor.
        # Daha güvenilir bir yöntem, koleksiyon listesini alıp içinde var mı diye bakmaktır.
        collections_response = client.get_collections()
        collection_names = [c.name for c in collections_response.collections]
        if collection_name in collection_names:
            # Koleksiyon zaten var, bir şey yapma.
            return
        
        # Koleksiyon yoksa, yeniden oluştur.
        client.recreate_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=model.get_sentence_embedding_dimension(),
                distance=models.Distance.COSINE
            ),
        )

    except Exception as e:
        logger.error("Koleksiyon oluşturulurken veya kontrol edilirken hata oluştu.", 
                     error=str(e), 
                     collection_name=collection_name)
        # Hata durumunda uygulamayı çökertmek yerine devam etmesini sağlamak için
        # hatayı yutabilir veya özel bir istisna fırlatabiliriz.
        # Şimdilik devam etmesine izin verelim.
        pass