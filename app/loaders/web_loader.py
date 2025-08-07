import requests
from bs4 import BeautifulSoup
from .base import BaseLoader

class WebLoader(BaseLoader):
    def load(self, uri: str) -> list[dict]:
        response = requests.get(uri)
        response.raise_for_status() # Hata varsa exception fırlat
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Basit bir örnek: Sadece <p> etiketlerinin içeriğini al
        paragraphs = [p.get_text() for p in soup.find_all('p')]
        content = "\n".join(paragraphs)
        
        return [{"text": content, "source": uri}]