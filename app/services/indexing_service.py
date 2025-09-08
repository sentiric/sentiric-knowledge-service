# app/services/indexing_service.py

import asyncio
import uuid
from qdrant_client import models
from app.services.qdrant_service import get_qdrant_client, setup_collection
from app.services.embedding_service import get_embedding_model
from app.core.config import settings
from app.core.logging import logger
from app.loaders import get_documents_for_tenant
from app.db.session import get_tenants, update_datasource_timestamp

async def run_indexing():
    """Tüm aktif tenantlar için başlangıç indekslemesini çalıştırır."""
    logger.info("İndeksleme süreci başlatılıyor...")
    tenants = sorted(list(set(get_tenants())))
    if not tenants:
        logger.warning("İndekslenecek tenant bulunamadı.")
        return

    client = get_qdrant_client()
    model = get_embedding_model()
    
    for tenant_id in tenants:
        await index_tenant(tenant_id, client, model)

    logger.info("Tüm tenantlar için indeksleme tamamlandı.")

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
    
    vectors = await asyncio.to_thread(
        model.encode, texts_to_encode, show_progress_bar=False
    )
    
    # _MODIFIED_ Her noktaya benzersiz bir ID ata (UUID) ve datasource_id'yi payload'da tut
    points_to_upsert = []
    processed_datasource_ids = set()
    for doc, vector in zip(documents, vectors):
        point_id = str(uuid.uuid4())
        payload = {
            "text": doc.get("text"),
            "source": doc.get("source"),
            "datasource_id": doc.get("datasource_id")
        }
        points_to_upsert.append(
            models.PointStruct(id=point_id, vector=vector.tolist(), payload=payload)
        )
        if doc.get("datasource_id"):
            processed_datasource_ids.add(doc.get("datasource_id"))

    if not points_to_upsert:
        tenant_logger.warning("Vektöre çevrilecek doküman bulunamadı.")
        return

    client.upsert(
        collection_name=collection_name,
        points=points_to_upsert,
        wait=True
    )
    
    # _NEW_ Başarıyla işlenen her veri kaynağının timestamp'ini güncelle
    for ds_id in processed_datasource_ids:
        await asyncio.to_thread(update_datasource_timestamp, ds_id)
        
    tenant_logger.info("Tenant için indeksleme başarıyla tamamlandı.")

# _NEW_ Yeniden indekslemeyi yöneten yeni fonksiyon
async def trigger_reindexing(tenant_id: str | None = None):
    """
    Yeniden indekslemeyi tetikler.
    Eğer tenant_id verilirse sadece o tenant'ı, verilmezse tüm sistemi yeniden indeksler.
    """
    logger.info("Yeniden indeksleme tetiklendi.", target_tenant=tenant_id or "ALL")
    if tenant_id:
        client = get_qdrant_client()
        model = get_embedding_model()
        await index_tenant(tenant_id, client, model)
    else:
        await run_indexing()
    logger.info("Yeniden indeksleme tamamlandı.", target_tenant=tenant_id or "ALL")