# 🤖 Sentiric Knowledge Service - "Genesis Demo" Rehberi

Bu belge, çalışan `sentiric-knowledge-service`'in yeteneklerini, `governance` dokümanlarında tanımlanan kullanım senaryoları üzerinden canlı olarak test etmek için hazırlanmıştır.

## Önkoşullar

1.  Tüm Sentiric platformunun `sentiric-infrastructure` reposundaki `docker compose up --build -d` komutuyla çalışır durumda olması gerekmektedir.
2.  Servisin `/health` endpoint'inin `{"status":"ok"}` yanıtı verdiğinden emin olun:
    ```bash
    curl http://localhost:5055/health
    ```

---

## Canlı Test Senaryoları (`curl`)

Aşağıdaki komutları yeni bir terminalde çalıştırarak servisin farklı `tenant`'lar ve veri kaynakları için nasıl çalıştığını canlı olarak görebilirsiniz.

**Not:** Windows Komut İstemi (`cmd.exe`) kullanıyorsanız, JSON verisini tek tırnak (`'`) yerine çift tırnak (`"`) içine almanız ve içteki çift tırnakların önüne ters eğik çizgi (`\`) koymanız gerekir. Aşağıdaki komutlar bu formata göre düzenlenmiştir.

<details>
<summary><strong>🏥 Sentiric Health - Acil Durum & Randevu (Dosya + DB'den Okuma)</strong></summary>

*   **Acil durum protokolünü sorgula:**
    ```bash
    curl -X POST http://localhost:5055/api/v1/query -H "Content-Type: application/json" -d "{\"query\": \"bilincim kapalı ne yapmalıyım?\", \"tenant_id\": \"sentiric_health\"}"
    ```
*   **Veritabanından hizmet fiyatı sorgula:**
    ```bash
    curl -X POST http://localhost:5055/api/v1/query -H "Content-Type: application/json" -d "{\"query\": \"vip check-up için ödeme gerekli mi?\", \"tenant_id\": \"sentiric_health\"}"
    ```
</details>

<details>
<summary><strong>✈️ Sentiric Travel - Otel Bilgisi (Dosyadan Okuma)</strong></summary>

*   **Otel hakkında bilgi al:**
    ```bash
    curl -X POST http://localhost:5055/api/v1/query -H "Content-Type: application/json" -d "{\"query\": \"jakuzili odanız var mı?\", \"tenant_id\": \"sentiric_travel\"}"
    ```
*   **Canlı olarak Google Travel'dan otel önerisi al (Şu anda Windows'ta desteklenmiyor):**
    *Not: Bu özellik, Windows'taki bir `asyncio` sınırlaması nedeniyle şu anda yalnızca Docker (Linux) ortamında çalışmaktadır. Yerel Windows geliştirme ortamında hata verecektir.*
    ```bash
    curl -X POST http://localhost:5055/api/v1/query -H "Content-Type: application/json" -d "{\"query\": \"Antalyada gecelik fiyatı uygun, iyi puanlı bir otel önerir misin?\", \"tenant_id\": \"sentiric_travel\"}"
    ```
</details>

<details>
<summary><strong>🍕 Sentiric Eats - Paket Servis (Dosyadan Okuma)</strong></summary>

*   **Menü içeriğini sorgula:**
    ```bash
    curl -X POST http://localhost:5055/api/v1/query -H "Content-Type: application/json" -d "{\"query\": \"karışık pizzada ne var?\", \"tenant_id\": \"sentiric_eats\"}"
    ```
</details>

<details>
<summary><strong>🎟️ Sentiric Events - Bilet Bilgisi (Veritabanından Okuma)</strong></summary>

*   **Etkinlikleri sorgula:**
    ```bash
    curl -X POST http://localhost:5055/api/v1/query -H "Content-Type: application/json" -d "{\"query\": \"zorluda hangi konser var?\", \"tenant_id\": \"sentiric_events\"}"
    ```
</details>

<details>
<summary><strong>🛡️ Veri İzolasyon Testi (En Kritik Senaryo)</strong></summary>

*Bu test, bir kiracının başka bir kiracının verisine erişemediğini doğrular.*
```bash
# Sentiric Health tenant'ında, otel bilgisi arıyoruz.
curl -X POST http://localhost:5055/api/v1/query -H "Content-Type: application/json" -d "{\"query\": \"jakuzili odanız var mı?\", \"tenant_id\": \"sentiric_health\"}"