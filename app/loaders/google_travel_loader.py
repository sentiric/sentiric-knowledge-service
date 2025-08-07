# app/loaders/google_travel_loader.py
import asyncio
from .base import BaseLoader
from app.core.logging import logger

# --- YENİ: Playwright'ı güvenli bir şekilde import etmeye çalış ---
try:
    from playwright.sync_api import sync_playwright, Error as PlaywrightError
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
# --- BİTTİ ---


def scrape_google_travel(search_query: str) -> list[dict]:
    # Sadece en dışına bir kontrol daha ekleyebiliriz:
    if not PLAYWRIGHT_AVAILABLE:
        logger.warning("Playwright yüklü değil, Google Travel Loader atlanıyor.")
        return []
    
    documents = []
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            url = f"https://www.google.com/travel/search?q={search_query} otelleri"
            logger.info("Google Travel'a gidiliyor", url=url, tenant_id="sentiric_travel")
            
            page.goto(url, wait_until='domcontentloaded', timeout=90000)
            
            page.wait_for_selector('div.lLL2Sc', timeout=60000)
            
            hotel_elements = page.query_selector_all('div.lLL2Sc')
            logger.info(f"{len(hotel_elements)} adet otel bulundu.", tenant_id="sentiric_travel")

            for hotel in hotel_elements[:5]:
                name_element = hotel.query_selector('div.skFvHc.YmWhb')
                name = name_element.inner_text() if name_element else "İsim Bulunamadı"

                price_element = hotel.query_selector('span.Kk3_6e')
                price = price_element.inner_text() if price_element else "Fiyat Yok"
                
                rating_element = hotel.query_selector('span.KFi5wf.lA0BZ')
                rating = rating_element.inner_text() if rating_element else "Puan Yok"
                
                text_content = f"Otel Adı: {name}. Değerlendirme Puanı: {rating}. Gecelik Fiyat: {price}."
                documents.append({"text": text_content, "source": f"google_travel:{search_query}"})
            
            browser.close()
            # --- DEĞİŞİKLİK BURADA: 'return' ifadesi try bloğunun içine alındı ---
            return documents
        except PlaywrightError as e:
            logger.error("Playwright operasyonu sırasında bir hata oluştu.", error=str(e), tenant_id="sentiric_travel")
            return []
class GoogleTravelLoader(BaseLoader):
    async def load(self, uri: str) -> list[dict]:
        if not PLAYWRIGHT_AVAILABLE:
            return [] # Eğer playwright yoksa, hiçbir şey yapma
        
        search_query = uri
        try:
            documents = await asyncio.to_thread(scrape_google_travel, search_query)
            return documents
        except Exception as e:
            logger.error("Google Travel Loader'da beklenmedik hata.", error=str(e), tenant_id="sentiric_travel")
            return []