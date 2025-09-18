import asyncio
from .base import BaseLoader
from app.core.logging import logger

try:
    from playwright.sync_api import sync_playwright, Error as PlaywrightError
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


def scrape_google_travel(search_query: str) -> list[dict]:
    if not PLAYWRIGHT_AVAILABLE:
        logger.warning(
            "Playwright is not installed, skipping Google Travel Loader."
        )
        return []

    documents = []
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            url = f"https://www.google.com/travel/search?q={search_query} otelleri"
            logger.info("Navigating to Google Travel", url=url)

            page.goto(url, wait_until='domcontentloaded', timeout=90000)
            page.wait_for_selector('div.lLL2Sc', timeout=60000)

            hotel_elements = page.query_selector_all('div.lLL2Sc')
            logger.info(f"{len(hotel_elements)} hotels found.")

            for hotel in hotel_elements[:5]:
                name_element = hotel.query_selector('div.skFvHc.YmWhb')
                name = name_element.inner_text() if name_element else "N/A"

                price_element = hotel.query_selector('span.Kk3_6e')
                price = price_element.inner_text() if price_element else "N/A"

                rating_element = hotel.query_selector('span.KFi5wf.lA0BZ')
                rating = rating_element.inner_text() if rating_element else "N/A"

                text_content = (
                    f"Otel Adı: {name}. Değerlendirme Puanı: {rating}. "
                    f"Gecelik Fiyat: {price}."
                )
                documents.append(
                    {"text": text_content, "source": f"google_travel:{search_query}"}
                )

            browser.close()
            return documents
        except PlaywrightError as e:
            logger.error("A Playwright error occurred during scraping.", error=str(e))
            return []


class GoogleTravelLoader(BaseLoader):
    async def load(self, uri: str) -> list[dict]:
        if not PLAYWRIGHT_AVAILABLE:
            return []

        search_query = uri
        try:
            documents = await asyncio.to_thread(scrape_google_travel, search_query)
            return documents
        except Exception as e:
            logger.error(
                "Unexpected error in Google Travel Loader.", error=str(e)
            )
            return []