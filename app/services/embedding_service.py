from sentence_transformers import SentenceTransformer
from app.core.config import settings
from functools import lru_cache

@lru_cache(maxsize=1)
def get_embedding_model():
    """Modeli sadece bir kez yüklemek için cache kullanır."""
    print(f"Embedding modeli yükleniyor: {settings.EMBEDDING_MODEL_NAME}")
    model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
    print("Embedding modeli yüklendi.")
    return model