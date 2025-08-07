# app/loaders/__init__.py
import asyncio # YENİ
from .file_loader import FileLoader
from .web_loader import WebLoader
from .postgres_loader import PostgresLoader
from .google_travel_loader import GoogleTravelLoader
from app.db.session import get_datasources_for_tenant
from app.core.logging import logger

LOADER_MAP = {
    "file": FileLoader(),
    "web": WebLoader(),
    "postgres": PostgresLoader(),
    # "google_travel": GoogleTravelLoader(), # Windows da çalışmadı?
}

# DİKKAT: Fonksiyon artık 'async'
async def get_documents_for_tenant(tenant_id: str) -> list[dict]:
    """Bir tenant için tüm veri kaynaklarını okur ve birleştirir."""
    datasources = get_datasources_for_tenant(tenant_id)
    all_documents = []
    
    # Asenkron ve senkron loader'ları çalıştırmak için bir görev listesi oluştur
    tasks = []
    
    for ds in datasources:
        source_type = ds.get("type")
        source_uri = ds.get("uri")
        
        loader = LOADER_MAP.get(source_type)
        if not loader:
            logger.warning("Desteklenmeyen veri kaynağı tipi", type=source_type, tenant_id=tenant_id)
            continue

        # Loader'ın load metodu asenkron mu kontrol et
        if asyncio.iscoroutinefunction(loader.load):
            tasks.append(loader.load(source_uri))
        else:
            # Senkron ise, onu da bir thread'de çalıştırarak bloklamayı önle
            tasks.append(asyncio.to_thread(loader.load, source_uri))

    # Tüm veri yükleme görevlerini paralel olarak çalıştır
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            ds = datasources[i]
            logger.error("Kaynak yüklenirken hata oluştu", 
                         type=ds.get("type"), 
                         uri=ds.get("uri"), 
                         error=str(result), 
                         tenant_id=tenant_id)
        else:
            ds = datasources[i]
            logger.info("Kaynak başarıyla yüklendi", 
                        type=ds.get("type"), 
                        uri=ds.get("uri"),
                        doc_count=len(result),
                        tenant_id=tenant_id)
            all_documents.extend(result)
            
    return all_documents