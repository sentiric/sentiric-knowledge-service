from .file_loader import FileLoader
from .web_loader import WebLoader
from .postgres_loader import PostgresLoader # YENİ
from app.db.session import get_datasources_for_tenant
from app.core.logging import logger
from .google_travel_loader import GoogleTravelLoader # YENİ
# Loader'ları tiplerine göre bir haritada tutuyoruz
LOADER_MAP = {
    "file": FileLoader(),
    "web": WebLoader(),
    "postgres": PostgresLoader(), # YENİ
    "google_travel": GoogleTravelLoader(), # YENİs
}

def get_documents_for_tenant(tenant_id: str) -> list[dict]:
    """Bir tenant için tüm veri kaynaklarını okur ve birleştirir."""
    datasources = get_datasources_for_tenant(tenant_id)
    all_documents = []
    
    for ds in datasources:
        source_type = ds.get("type")
        source_uri = ds.get("uri")
        
        loader = LOADER_MAP.get(source_type)
        if not loader:
            logger.warning(f"Desteklenmeyen veri kaynağı tipi: {source_type}")
            continue
        
        try:
            documents = loader.load(source_uri)
            all_documents.extend(documents)
            logger.info(f"Kaynak başarıyla yüklendi: {source_type} - {source_uri}")
        except Exception as e:
            logger.error(f"Kaynak yüklenirken hata: {source_type} - {source_uri}", error=str(e))
            
    return all_documents