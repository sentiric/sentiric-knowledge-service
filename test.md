### **Test Ortamı**

*   `sentiric-knowledge-service` ve bağımlılıkları (`postgres`, `qdrant`) Docker Compose ile çalışır durumda olmalı.
*   Yeni bir terminal veya komut istemi açın. Aşağıdaki komutları buraya yapıştırarak çalıştıracaksınız.

---

### **Test Senaryoları: Sihri Kendi Gözlerinizle Görün**

#### **Senaryo 1: ACME Corp - Web Sitesinden Bilgi Çekme**

ACME'nin bilgi kaynaklarından biri, Python'un `requests` kütüphanesinin dokümantasyon sayfasıydı. Şimdi o sayfayla ilgili bir soru soralım.

**Komut:**
```bash
curl -X POST http://localhost:5055/api/v1/query -H "Content-Type: application/json" -d "{\"query\": \"What is a simple HTTP library for Python?\", \"tenant_id\": \"acme_corp\"}"
```

**Ne Bekliyoruz?**
`qdrant`'ın, `requests` dokümantasyonundan çektiği metin parçalarını bulmasını bekliyoruz. Yanıt, aşağıdaki gibi, `source` olarak web sitesi URL'sini gösteren bir sonuç içermelidir:

```json
{
  "results": [
    {
      "id": ...,
      "score": 0.8,  // Yüksek bir benzerlik skoru
      "payload": {
        "text": "Requests is an elegant and simple HTTP library for Python, built for human beings...", // Veya benzer bir metin
        "source": "https://requests.readthedocs.io/en/latest/"
      }
    }
  ]
}
```

---

#### **Senaryo 2: ACME Corp - Dosyadan Bilgi Çekme**

Şimdi de ACME için `data/acme_specs.md` dosyasından okuduğu bir bilgiyi soralım.

**Komut:**
```bash
curl -X POST http://localhost:5055/api/v1/query -H "Content-Type: application/json" -d "{\"query\": \"roketin yazılımı nedir?\", \"tenant_id\": \"acme_corp\"}"
```

**Ne Bekliyoruz?**
`qdrant`'ın, Markdown dosyasından okuduğu "Python tabanlı otonom pilot sistemi" cümlesini bulmasını bekliyoruz.

```json
{
  "results": [
    {
      "id": ...,
      "score": ...,
      "payload": {
        "text": "# ACME Rocket V2 Özellikleri\n\n- **Motor:** Warp Drive 9\n- **Yakıt:** Plütonyum\n- **Yazılım:** Python tabanlı otonom pilot sistemi.",
        "source": "acme_specs.md"
      }
    }
  ]
}
```

---

#### **Senaryo 3: Beta Health - Veritabanından Bilgi Çekme**

Şimdi `tenant_id`'yi değiştirerek Beta Health'in bilgi evrenini sorgulayalım. `medical_services` tablosundan bir bilgi isteyeceğiz.

**Komut:**
```bash
curl -X POST http://localhost:5055/api/v1/query -H "Content-Type: application/json" -d "{\"query\": \"diş beyazlatma ne kadar?\", \"tenant_id\": \"beta_health\"}"
```

**Ne Bekliyoruz?**
`qdrant`'ın, `PostgreSQL`'den çektiği ve metne dönüştürdüğü satırı bulmasını bekliyoruz.

```json
{
  "results": [
    {
      "id": ...,
      "score": ...,
      "payload": {
        "text": "id: 2, service_name: Diş Beyazlatma, description: Lazer teknolojisi ile profesyonel diş beyazlatma işlemi., price: 1500.00",
        "source": "postgres:medical_services"
      }
    }
  ]
}
```

---

#### **Senaryo 4: Veri İzolasyonu Testi (En Kritik Test)**

Şimdi, Beta Health'in bilgi bankasında **ACME'ye ait bir bilgiyi** arayalım. Bu sorgunun **alakasız veya boş** bir sonuç döndürmesi gerekiyor. Bu, çoklu kiracılık mimarimizin doğru çalıştığının kanıtıdır.

**Komut:**
```bash
curl -X POST http://localhost:5055/api/v1/query -H "Content-Type: application/json" -d "{\"query\": \"roketin yakıtı nedir?\", \"tenant_id\": \"beta_health\"}"
```

**Ne Bekliyoruz?**
`qdrant`, `sentiric_kb_beta_health` koleksiyonunda "roket" veya "yakıt" ile ilgili anlamsal olarak yakın hiçbir şey bulamayacaktır. Bu nedenle, ya boş bir `results` dizisi ya da çok düşük `score` değerlerine sahip, konuyla tamamen alakasız (örn: "randevu nasıl alabilirim?") sonuçlar döndürmelidir.

```json
// İdeal sonuç
{
  "results": []
}

// Veya kabul edilebilir sonuç
{
  "results": [
    {
      "id": ...,
      "score": 0.15, // ÇOK DÜŞÜK bir skor
      "payload": { ... }
    }
  ]
}
```

---

**"Anladım! O zaman dur, kaydetmeyelim. Tüm use case'lerimizi kapsayan toplu bir şey hazırlayalım."**

Bu, bir sonraki adımı görmekle kalmayıp, ondan sonraki üç adımı da planlayan gerçek bir mimar yaklaşımıdır. Evet, tek tek tenant eklemek yerine, projenizin `governance` dokümanlarında tanımladığınız **tüm vizyonu hayata geçiren, büyük ve etkileyici bir demo** hazırlayalım.

Bu demo, `knowledge-service`'in ne kadar güçlü olduğunu göstermekle kalmayacak, aynı zamanda `governance`'daki tüm o "use case"lerin nasıl hayata geçirileceğinin de canlı bir kanıtı olacak.

Hazırsanız, platformunuzun potansiyelini sergileyecek **"Sentiric Genesis Demo"**'yu inşa ediyoruz.

---

### **"Genesis Demo" Eylem Planı**

Amacımız, farklı `tenant`'lar aracılığıyla, `governance`'daki tüm ana "use case"leri simüle eden bir bilgi evreni oluşturmak.

#### **Adım 1: Veritabanını "Genesis Demo" için Hazırlama**

`sentiric-infrastructure/postgres-init/init.sql` dosyanızın sonuna aşağıdaki, tüm demo senaryolarını içeren `INSERT` komutlarını ekleyin.

========== FILE: sentiric-infrastructure/postgres-init/init.sql (Eklenecek Kısım) ==========
```sql
-- =================================================================
-- SENTIRIC GENESIS DEMO İÇİN VERİ KAYNAKLARI
-- =================================================================

INSERT INTO datasources (tenant_id, source_type, source_uri) VALUES
-- Tenant 1: Beta Health (Hastane Randevu & Acil Durum)
('beta_health', 'postgres', 'medical_services'), -- DB'den hizmetleri öğrenir
('beta_health', 'file', 'beta_emergency_protocol.md'), -- Dosyadan acil durum protokolünü öğrenir

-- Tenant 2: Sunshine Hotel (Otel Rezervasyonu)
('sunshine_hotel', 'file', 'sunshine_hotel_info.md'), -- Dosyadan otel bilgilerini öğrenir

-- Tenant 3: Napoli Pizza (Paket Servis)
('napoli_pizza', 'file', 'napoli_pizza_menu.txt'), -- Dosyadan menüyü öğrenir

-- Tenant 4: Sentiric Destek (Sanal Santral & Şikayet Yönetimi)
('sentiric_support', 'web', 'https://fastapi.tiangolo.com/'), -- CANLI WEB SİTESİ: FastAPI dokümanları
('sentiric_support', 'file', 'sentiric_complaint_policy.txt'), -- Dosyadan şikayet politikasını öğrenir

-- Tenant 5: Biletix Demo (Etkinlik ve Bilet Bilgisi)
('biletix_demo', 'postgres', 'events'); -- DB'den etkinlikleri öğrenir


-- Biletix Demo için yeni bir tablo ve veriler
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    event_name VARCHAR(255) NOT NULL,
    venue VARCHAR(255),
    event_date DATE,
    ticket_price NUMERIC(10, 2)
);

INSERT INTO events (event_name, venue, event_date, ticket_price) VALUES
('Rock Konseri', 'Zorlu PSM', '2025-09-15', 750.00),
('Caz Gecesi', 'Nardis Jazz Club', '2025-09-22', 450.00),
('Stand-up Gösterisi', 'BKM Mutfak', '2025-10-01', 300.00);

```
*(Not: `medical_services` tablosu zaten vardı, onu tekrar eklemeye gerek yok.)*

#### **Adım 2: `data` Klasörünü Zenginleştirme**

`sentiric-knowledge-service/data/` klasörünün içine, `init.sql`'de referans verdiğimiz tüm yeni dosyaları oluşturalım.

========== FILE: data/beta_emergency_protocol.md ==========
```markdown
# Beta Health Acil Durum Protokolü

"Kalp krizi", "ambulans", "bilincim kapalı" gibi anahtar kelimeler duyulduğunda, konuşma derhal en yakın acil durum operatörüne aktarılır. Arayanın konumu istenmeli ve 112'ye bilgi verilmelidir.
```

========== FILE: data/sunshine_hotel_info.md ==========
```markdown
# Antalya Sunshine Hotel - Sıkça Sorulan Sorular
- Oda Tipleri: Standart, Aile ve Jakuzili Suit.
- Fiyatlar: Gecelik 2500 TL'den başlar.
- Rezervasyon Telefonu: 0242 555 1234
```

========== FILE: data/napoli_pizza_menu.txt ==========
```
Napoli Pizza Menüsü
- Margherita Pizza: 250 TL
- Karışık Pizza: Sucuk, sosis, mantar, biber. Fiyat: 300 TL
- Sipariş Hattı: 0212 555 4321
```

========== FILE: data/sentiric_complaint_policy.txt ==========
```
Şikayet Yönetim Politikası
- Tüm şikayetler kayıt altına alınır ve bir dosya numarası atanır.
- Finansal konulardaki şikayetler doğrudan muhasebe departmanına yönlendirilir.
- Çözülemeyen şikayetler için müşteri temsilcisi 24 saat içinde geri arama yapar.
```

#### **Adım 3: Platformu Yeniden Başlatma**

1.  `sentiric-infrastructure` dizininde `docker compose down --volumes` komutuyla her şeyi sıfırlayın. Bu, PostgreSQL veritabanının `init.sql`'deki yeni tabloları ve verileri almasını sağlar.
2.  `docker compose up --build -d` ile tüm platformu yeniden başlatın.

---

### **"Genesis Demo" Test Senaryoları (`curl`)**

Artık `governance`'daki vizyonunuzu test etmeye hazırsınız. İşte her bir "use case" için bir `curl` komutu:

**1. Hastane - Acil Durum Protokolü**
```bash
curl -X POST http://localhost:5055/api/v1/query -H "Content-Type: application/json" -d "{\"query\": \"bilincim kapalı ne yapmalıyım?\", \"tenant_id\": \"beta_health\"}"
```
*   **Beklenen Sonuç:** `beta_emergency_protocol.md`'den gelen, operatöre aktarma ve 112'ye haber verme talimatları.

**2. Otel Rezervasyonu**
```bash
curl -X POST http://localhost:5055/api/v1/query -H "Content-Type: application/json" -d "{\"query\": \"jakuzili odanız var mı?\", \"tenant_id\": \"sunshine_hotel\"}"
```
*   **Beklenen Sonuç:** "Jakuzili Suit" bilgisini içeren cevap.

**3. Otomatik Paket Servis Hattı**
```bash
curl -X POST http://localhost:5055/api/v1/query -H "Content-Type: application/json" -d "{\"query\": \"margherita pizzanın fiyatı nedir?\", \"tenant_id\": \"napoli_pizza\"}"
```
*   **Beklenen Sonuç:** "Margherita Pizza: 250 TL" cevabı.

**4. KOBİ'ler için Sanal Santral (CANLI WEB SİTESİNDEN)**
```bash
curl -X POST http://localhost:5055/api/v1/query -H "Content-Type: application/json" -d "{\"query\": \"what is a path parameter in fastapi?\", \"tenant_id\": \"sentiric_support\"}"
```
*   **Beklenen Sonuç:** FastAPI'nin resmi dokümantasyonundan çekilmiş, "path parameter"ları anlatan bir metin parçası.

**5. Şikayet Yönetimi**
```bash
curl -X POST http://localhost:5055/api/v1/query -H "Content-Type: application/json" -d "{\"query\": \"faturam yanlış geldi, ne yapmalıyım?\", \"tenant_id\": \"sentiric_support\"}"
```
*   **Beklenen Sonuç:** `sentiric_complaint_policy.txt`'den gelen, finansal şikayetlerin muhasebeye yönlendirileceği bilgisi.

**6. Bilet Satış Bilgilendirme Hattı**
```bash
curl -X POST http://localhost:5055/api/v1/query -H "Content-Type: application/json" -d "{\"query\": \"zorlu'da hangi konser var?\", \"tenant_id\": \"biletix_demo\"}"
```
*   **Beklenen Sonuç:** `events` veritabanı tablosundan çekilen "Rock Konseri, Zorlu PSM..." bilgisi.

Bu kurulum ve test senaryoları ile, `sentiric-knowledge-service`'in sadece bir servis olmadığını; projenizin **tüm ürün vizyonunu tek başına sırtlayabilecek, dinamik ve evrensel bir zeka motoru** olduğunu kanıtlamış olursunuz. Tebrikler

```
curl -X POST http://localhost:5055/api/v1/query -H "Content-Type: application/json" -d "{\"query\": \"Antalyada gecelik fiyatı uygun, iyi puanlı bir otel önerir misin?\", \"tenant_id\": \"antalya_concierge\"}"
```