from qdrant_client import models
from app.services.qdrant_service import get_qdrant_client, setup_collection
from app.services.embedding_service import get_embedding_model
from app.core.config import settings
from app.core.logging import logger
from app.loaders import get_documents_for_tenant
from app.db.session import get_tenants # DB'den tenant'ları çekmek için yeni fonksiyon

def run_indexing():
    logger.info("İndeksleme süreci başlatılıyor...")
    tenants = get_tenants()
    if not tenants:
        logger.warning("İndekslenecek tenant bulunamadı.")
        return

    client = get_qdrant_client()
    model = get_embedding_model()

    for tenant_id in tenants:
        logger.info(f"Tenant işleniyor: {tenant_id}")
        collection_name = f"{settings.VECTOR_DB_COLLECTION_PREFIX}{tenant_id}"
        setup_collection(collection_name) # Her tenant için koleksiyon oluştur

        documents = get_documents_for_tenant(tenant_id)
        if not documents:
            logger.warning(f"Tenant için doküman bulunamadı: {tenant_id}")
            continue

        logger.info(f"{len(documents)} doküman parçası vektöre çevriliyor...")
        
        vectors = model.encode([doc['text'] for doc in documents]).tolist()
        
        client.upsert(
            collection_name=collection_name,
            points=[
                models.PointStruct(id=i, vector=vectors[i], payload=doc)
                for i, doc in enumerate(documents)
            ],
            wait=True
        )
        logger.info(f"Tenant için indeksleme tamamlandı: {tenant_id}")