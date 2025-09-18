# app/loaders/__init__.py
import asyncio
import structlog # YENİ
from .file_loader import FileLoader
from .web_loader import WebLoader
from .postgres_loader import PostgresLoader
from app.db.session import get_datasources_for_tenant

log = structlog.get_logger(__name__) # YENİ

LOADER_MAP = {
    "file": FileLoader(),
    "web": WebLoader(),
    "postgres": PostgresLoader(),
}

async def get_documents_for_tenant(tenant_id: str) -> list[dict]:
    datasources = get_datasources_for_tenant(tenant_id)
    all_documents = []
    tasks = []
    
    for ds in datasources:
        source_type = ds.get("type")
        source_uri = ds.get("uri")
        
        loader = LOADER_MAP.get(source_type)
        if not loader:
            log.warning("Desteklenmeyen veri kaynağı tipi",
                           type=source_type, tenant_id=tenant_id)
            continue

        # iscoroutinefunction is deprecated in favor of iscoroutine
        if asyncio.iscoroutine(loader.load) or asyncio.iscoroutinefunction(loader.load):
            tasks.append(loader.load(source_uri))
        else:
            tasks.append(asyncio.to_thread(loader.load, source_uri))

    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for i, result in enumerate(results):
        ds = datasources[i]
        datasource_id = ds.get("id")

        if isinstance(result, Exception):
            log.error("Kaynak yüklenirken hata oluştu", 
                         type=ds.get("type"), 
                         uri=ds.get("uri"),
                         datasource_id=datasource_id,
                         error=str(result), 
                         tenant_id=tenant_id)
        else:
            log.debug("Kaynak başarıyla yüklendi", 
                        type=ds.get("type"), 
                        uri=ds.get("uri"),
                        datasource_id=datasource_id,
                        doc_count=len(result),
                        tenant_id=tenant_id)
            
            for doc in result:
                doc['datasource_id'] = datasource_id
            
            all_documents.extend(result)
            
    return all_documents