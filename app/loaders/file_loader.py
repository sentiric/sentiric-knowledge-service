# app/loaders/file_loader.py
import os
from .base import BaseLoader
from app.core.logging import logger

# 12-Factor App" prensipleri.
DATA_DIR = os.getenv("SENTIRIC_DATA_PATH", "data")

class FileLoader(BaseLoader):
    def load(self, uri: str) -> list[dict]:
        # Artık dosya yolu dinamik olarak belirleniyor.
        filepath = os.path.join(DATA_DIR, uri)
        logger.info(f"Dosya okunuyor: {filepath}")
        if not os.path.exists(filepath):
            # Dosya bulunamadığında hata fırlatmak yerine loglayıp boş liste dönüyoruz.
            # Bu, uygulamanın çökmesini engeller.
            logger.error(f"Dosya bulunamadı: {filepath}")
            raise FileNotFoundError(f"Dosya bulunamadı: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return [{"text": content, "source": uri}]