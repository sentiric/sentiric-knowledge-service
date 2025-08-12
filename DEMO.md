# 🤖 Sentiric Knowledge Service - "Genesis Demo" Rehberi

Bu belge, çalışan `sentiric-knowledge-service`'in yeteneklerini, `governance` dokümanlarında tanımlanan kullanım senaryoları üzerinden canlı olarak test etmek için hazırlanmıştır.

## Önkoşullar

1.  Tüm Sentiric platformunun `sentiric-infrastructure` reposundaki `make up` komutuyla çalışır durumda olması gerekmektedir.
2.  Servisin `/health` endpoint'inin `{"status":"ok", ...}` yanıtı verdiğinden emin olun:
    ```bash
    curl http://localhost:50055/health
    ```

---

## Canlı Test Senaryoları (`curl`)

Aşağıdaki komutları yeni bir terminalde çalıştırarak servisin farklı `tenant`'lar ve veri kaynakları için nasıl çalıştığını canlı olarak görebilirsiniz.

*Not: Windows Komut İstemi (`cmd.exe`) kullanıyorsanız, JSON verisini tek tırnak (`'`) yerine çift tırnak (`"`) içine almanız ve içteki çift tırnakların önüne ters eğik çizgi (`\`) koymanız gerekir.*

### Senaryo 1: 🏥 Sentiric Health (Dosya + DB'den Okuma)

*   **Acil durum protokolünü sorgula:**
    ```bash
    curl -X POST http://localhost:50055/api/v1/query -H "Content-Type: application/json" -d "{\"query\": \"bilincim kapalı ne yapmalıyım?\", \"tenant_id\": \"sentiric_health\"}"
    ```
*   **Veritabanından hizmet fiyatı sorgula:**
    ```bash
    curl -X POST http://localhost:50055/api/v1/query -H "Content-Type: application/json" -d "{\"query\": \"vip check-up için ödeme gerekli mi?\", \"tenant_id\": \"sentiric_health\"}"
    ```

### Senaryo 2: 🎟️ Sentiric Events (Veritabanından Okuma)

*   **Etkinlikleri sorgula:**
    ```bash
    curl -X POST http://localhost:50055/api/v1/query -H "Content-Type: application/json" -d "{\"query\": \"zorluda hangi konser var?\", \"tenant_id\": \"sentiric_events\"}"
    ```

### Senaryo 3: 🛡️ Veri İzolasyon Testi (En Kritik Senaryo)

*Bu test, bir kiracının başka bir kiracının verisine erişemediğini doğrular.*
```bash
# Sentiric Health tenant'ında, otel bilgisi arıyoruz.
# Beklenen sonuç: Otel bilgisi yerine, en yakın anlamsal sonuç olan sağlık hizmetlerinin dönmesi.
curl -X POST http://localhost:50055/api/v1/query -H "Content-Type: application/json" -d "{\"query\": \"jakuzili odanız var mı?\", \"tenant_id\": \"sentiric_health\"}"
```