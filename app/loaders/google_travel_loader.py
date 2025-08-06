import time
from playwright.sync_api import sync_playwright
from .base import BaseLoader
from app.core.logging import logger

class GoogleTravelLoader(BaseLoader):
    def load(self, uri: str) -> list[dict]:
        """
        Playwright kullanarak Google Travel'dan otel bilgilerini çeker.
        uri: Örneğin 'Antalya' gibi bir arama terimi.
        """
        search_query = uri
        documents = []
        
        browser = None # Hata durumunda kapatabilmek için dışarıda tanımla
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                url = f"https://www.google.com/travel/search?q={search_query} otelleri"
                logger.info(f"Google Travel'a gidiliyor: {url}")
                page.goto(url, wait_until='networkidle', timeout=60000)
                
                page.wait_for_selector('div[jscontroller="hvPfDb"]', timeout=30000)
                time.sleep(5)

                hotel_elements = page.query_selector_all('div.lLL2Sc')
                logger.info(f"{len(hotel_elements)} adet otel bulundu.")

                for hotel in hotel_elements[:5]: # Demo için ilk 5 oteli alalım
                    # DÜZELTME: Python'da optional chaining (?.) yoktur, if bloğu kullanılır.
                    name_element = hotel.query_selector('div.skFvHc.YmWhb')
                    name = name_element.inner_text() if name_element else "İsim Bulunamadı"

                    price_element = hotel.query_selector('span.Kk3_6e')
                    price = price_element.inner_text() if price_element else "Fiyat Yok"
                    
                    rating_element = hotel.query_selector('span.KFi5wf.lA0BZ')
                    rating = rating_element.inner_text() if rating_element else "Puan Yok"
                    
                    text_content = f"Otel Adı: {name}. Değerlendirme Puanı: {rating}. Gecelik Fiyat: {price}."
                    documents.append({"text": text_content, "source": f"google_travel:{search_query}"})
                
                browser.close()
                return documents

        except Exception as e:
            logger.error("Google Travel'dan veri çekerken hata oluştu.", error=str(e))
            if browser and browser.is_connected():
                browser.close()
            return []