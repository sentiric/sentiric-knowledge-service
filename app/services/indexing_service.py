# app/services/indexing_service.py
import asyncio
from qdrant_client import models
from app.services.qdrant_service import get_qdrant_client, setup_collection
from app.services.embedding_service import get_embedding_model
from app.core.config import settings
from app.core.logging import logger
from app.loaders import get_documents_for_tenant
from app.db.session import get_tenants

# --- DÜZELTME BAŞLANGICI (KS-BUG-01) ---
async def run_indexing():
    """
    Tüm tenant'ları SİRALI bir şekilde işleyerek logların karışmasını engeller.
    Her bir tenant'ın kendi veri kaynakları ise PARALEL olarak yüklenir.
    Yinelenen tenant'ları işlemekten kaçınmak için `set()` kullanılır.
    """
    logger.info("İndeksleme süreci başlatılıyor...")
    # get_tenants()'ten dönen listede yinelenenler olabileceği için set'e çeviriyoruz.
    tenants = sorted(list(set(get_tenants())))
    if not tenants:
        logger.warning("İndekslenecek tenant bulunamadı.")
        return

    client = get_qdrant_client()
    model = get_embedding_model()
    
    # Tenant'ları bir döngü içinde sırayla işle
    for tenant_id in tenants:
        # Tek bir tenant'ı indekslemek için yardımcı fonksiyonu await ile çağır
        await index_tenant(tenant_id, client, model)

    logger.info("Tüm tenantlar için indeksleme tamamlandı.")
# --- DÜZELTME SONU ---

async def index_tenant(tenant_id, client, model):
    """Tek bir tenant için asenkron indeksleme yapar."""
    tenant_logger = logger.bind(tenant_id=tenant_id)
    tenant_logger.info("Tenant işleniyor...")
    
    collection_name = f"{settings.VECTOR_DB_COLLECTION_PREFIX}{tenant_id}"
    setup_collection(collection_name)

    documents = await get_documents_for_tenant(tenant_id)
    if not documents:
        tenant_logger.warning("Tenant için doküman bulunamadı.")
        return

    tenant_logger.info(f"{len(documents)} doküman vektöre çevriliyor...")
    
    texts_to_encode = [doc['text'] for doc in documents]
    
    # model.encode CPU yoğun bir işlem olduğu için bir thread'de çalıştır.
    # show_progress_bar=False ile loglardaki karmaşayı önle.
    vectors = await asyncio.to_thread(
        model.encode, texts_to_encode, show_progress_bar=False
    )
    
    client.upsert(
        collection_name=collection_name,
        points=[
            models.PointStruct(id=i, vector=vector.tolist(), payload=doc)
            for i, (doc, vector) in enumerate(zip(documents, vectors))
        ],
        wait=True
    )
    tenant_logger.info("Tenant için indeksleme başarıyla tamamlandı.")