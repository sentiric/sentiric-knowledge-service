import os
from .base import BaseLoader
from app.core.logging import logger

DATA_DIR = "data" # Bu klasör artık tenant'a özel dosyaları tutacak

class FileLoader(BaseLoader):
    def load(self, uri: str) -> list[dict]:
        filepath = os.path.join(DATA_DIR, uri)
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Dosya bulunamadı: {filepath}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Gerçekte burada metni daha küçük parçalara (chunks) bölme mantığı olur
        return [{"text": content, "source": uri}]