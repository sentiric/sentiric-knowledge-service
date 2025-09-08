# 📚 Sentiric Knowledge Service - Görev Listesi (v1.2 - Dayanıklılık)

Bu belge, knowledge-service'in geliştirme yol haritasını ve önceliklerini tanımlar.

---

### **FAZ 1: Çok-Kiracılı RAG Temeli (Mevcut Durum)**

**Amaç:** Servisin temel RAG yeteneklerini çoklu kiracı ve çoklu kaynak desteği ile sunmasını sağlamak.

-   [x] **Görev ID: KS-CORE-01 - FastAPI Sunucusu:** `/api/v1/query` ve `/health` endpoint'lerini sunar.
-   [x] **Görev ID: KS-CORE-02 - Çok-Kiracılı İndeksleme:** `datasources` tablosunu okuyarak her `tenant_id` için ayrı bir Qdrant koleksiyonu oluşturur.
-   [x] **Görev ID: KS-CORE-03 - Çok-Kaynaklı Veri Yükleyiciler:** `FileLoader`, `WebLoader`, `PostgresLoader` gibi farklı kaynaklardan veri okuma yeteneği.
-   [x] **Görev ID: KS-CORE-04 - Asenkron ve Paralel Yükleme:** Bir kiracıya ait tüm veri kaynaklarını `asyncio.gather` ile paralel olarak işler.
-   [x] **Görev ID: KS-CORE-05 - Vektör Arama:** Gelen sorguyu vektöre çevirip ilgili kiracının koleksiyonunda anlamsal arama yapar.

---

### **FAZ 2: Dayanıklılık ve Optimizasyon (Mevcut Odak)**

**Amaç:** Servisin başlangıç sırasındaki dayanıklılığını artırmak ve veri yönetimini daha verimli hale getirmek.

-   **Görev ID: KS-BUG-02 - Qdrant Bağlantı Zaman Aşımını Yönetme (KRİTİK)**
    -   **Durum:** ⬜ **Yapılacak (Öncelik 1)**
    -   **Problem Tanımı:** Canlı test logları, servisin başlangıçta Qdrant'a bağlanmaya çalışırken `timed out` hatası aldığını ve bu nedenle indeksleme işleminin çökerek servisin RAG yeteneklerini kaybetmesine neden olduğunu göstermektedir.
    -   **Çözüm Stratejisi:** `app/services/indexing_service.py` içindeki Qdrant ile ilgili tüm işlemleri (`setup_collection`, `client.upsert`) kapsayan bir `try...except` bloğu içine alınmalıdır. Bir `timeout` veya bağlantı hatası yakalandığında, servis çökmemeli, bunun yerine hatayı loglamalı ve bir sonraki tenant'ı işlemeye devam etmelidir. Ayrıca, `qdrant_client`'a daha uzun bir varsayılan `timeout` değeri (örneğin 60 saniye) atanmalıdır.
    -   **Kabul Kriterleri:**
        -   [ ] `qdrant_service.py` içinde `QdrantClient` oluşturulurken `timeout` parametresi artırılmalıdır.
        -   [ ] `indexing_service.py` içinde Qdrant işlemleri hata yönetimi ile sarmalanmalıdır.
        -   [ ] Qdrant servisi yavaş başlasa bile, `knowledge-service` çökmeden başlamalı ve loglarda bu durumu belirten bir `WARN` veya `ERROR` mesajı olmalıdır.

-   **Görev ID: KS-BUG-01 - Yinelenen Veri Yükleme Sorununu Giderme**
    -   **Durum:** ⬜ **Yapılacak (Öncelik 2)**
    -   **Problem Tanımı:** Başlangıç logları, her tenant için veri kaynaklarının iki kez yüklendiğini gösteriyor. Bu durum, gereksiz kaynak tüketimine neden olmaktadır.
    -   **Kabul Kriterleri:**
        -   [ ] Düzeltme uygulandıktan sonra, servisin başlangıç loglarında her bir tenant ve veri kaynağı için **sadece tek bir** "Kaynak başarıyla yüklendi" logu göründüğü doğrulanmalıdır.

---

### **FAZ 3: Gelişmiş Veri Yönetimi (Gelecek Vizyonu)**

-   [ ] **Görev ID: KS-FEAT-01 - Re-Indexing Webhook'u:** Veri kaynakları güncellendiğinde, servisi yeniden başlatmadan bilgi bankasını tazelemek için bir `/api/v1/reindex` endpoint'i oluşturmak.
-   [ ] **Görev ID: KS-FEAT-02 - Hibrit Arama (Hybrid Search):** Anlamsal aramaya ek olarak anahtar kelime tabanlı aramayı da desteklemek.