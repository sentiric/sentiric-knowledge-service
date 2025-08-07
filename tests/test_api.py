# tests/test_api.py
import os
import pytest
import httpx
from httpx import AsyncClient

# Test edilecek servisin adresini ortam değişkeninden al, yoksa varsayılan kullan
BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:50055")
API_URL = f"{BASE_URL}/api/v1/query"

# Pytest'i asenkron testler için yapılandır
pytestmark = pytest.mark.asyncio

# Tüm testlerde kullanılacak bir HTTP istemcisi oluştur
@pytest.fixture(scope="module")
async def async_client() -> AsyncClient:
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        yield client

# Sağlık kontrolü testi
async def test_health_check(async_client: AsyncClient):
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

# "Genesis Demo" Test Senaryoları - governance dokümanlarındaki kullanım senaryolarını doğrular
@pytest.mark.parametrize("tenant_id, query, expected_snippet", [
    # 1. Sentiric Health - Acil Durum Protokolü (Dosyadan Okuma)
    ("sentiric_health", "bilincim kapalı ne yapmalıyım?", "acil durum operatörüne aktarılır"),
    
    # 2. Sentiric Health - Ön Ödemeli Hizmet (Veritabanından Okuma)
    ("sentiric_health", "vip check-up için ödeme gerekli mi?", "Kapsamlı sağlık taraması"),

    # 3. Sentiric Travel - Otel Bilgisi (Dosyadan Okuma)
    ("sentiric_travel", "jakuzili odanız var mı?", "Jakuzili Suit"),

    # 4. Sentiric Travel - Concierge (Dinamik Web Scraping)
    ("sentiric_travel", "Antalya'da otel önerir misin?", "Otel Adı:"),
    
    # 5. Sentiric Eats - Paket Servis (Dosyadan Okuma)
    ("sentiric_eats", "karışık pizzada ne var?", "Sucuk, sosis, mantar, biber"),
    
    # 6. Sentiric Support - Şikayet Yönetimi (Dosyadan Okuma)
    ("sentiric_support", "faturam yanlış geldi", "muhasebe departmanına yönlendirilir"),
    
    # 7. Sentiric Events - Bilet Bilgisi (Veritabanından Okuma)
    ("sentiric_events", "zorlu'da hangi konser var?", "Rock Konseri"),
])
async def test_genesis_queries(async_client: AsyncClient, tenant_id, query, expected_snippet):
    response = await async_client.post(API_URL, json={"query": query, "tenant_id": tenant_id})
    assert response.status_code == 200, f"API isteği başarısız oldu: {response.text}"
    
    data = response.json()
    assert "results" in data, "Yanıt 'results' anahtarı içermiyor"
    assert len(data["results"]) > 0, f"'{query}' sorgusu için hiçbir sonuç dönmedi"
    
    # Dönen sonuçlardan en az birinin beklenen metin parçasını içerdiğini kontrol et
    payload_texts = [result["payload"]["text"] for result in data["results"]]
    assert any(expected_snippet in text for text in payload_texts), \
        f"Query '{query}' için '{expected_snippet}' bulunamadı. Dönen metinler: {payload_texts}"

# Veri İzolasyon Testi
async def test_tenant_isolation(async_client: AsyncClient):
    # Sentiric Health tenant'ında, Sentiric Travel'a ait bir bilgiyi ara
    response = await async_client.post(API_URL, json={"query": "jakuzili odanız var mı?", "tenant_id": "sentiric_health"})
    assert response.status_code == 200
    
    data = response.json()
    assert "results" in data
    
    is_isolated = True
    if len(data["results"]) > 0:
        for result in data["results"]:
            # Eğer alakasız bir sonuç yüksek bir skorla dönerse, bu bir sızıntıdır.
            if "Jakuzili Suit" in result["payload"]["text"] and result["score"] > 0.5:
                is_isolated = False
                break
    
    assert is_isolated, "Veri izolasyonu başarısız! Bir tenant, başka bir tenant'ın verisini yüksek skorla gördü."