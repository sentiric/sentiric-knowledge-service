# sentiric-knowledge-service/app/loaders/file_loader.py
import os
import structlog
from .base import BaseLoader

log = structlog.get_logger(__name__)
DATA_DIR = os.getenv("KNOWLEDGE_SERVICE_DATA_PATH", "/sentiric-knowledge-data")

class FileLoader(BaseLoader):
    def load(self, uri: str) -> list[dict]:
        filepath = os.path.join(DATA_DIR, uri)
        log.info(f"Dosya okunuyor: {filepath}")
        if not os.path.exists(filepath):
            log.error(f"Dosya bulunamadı: {filepath}")
            raise FileNotFoundError(f"Dosya bulunamadı: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return [{"text": content, "source": uri}]