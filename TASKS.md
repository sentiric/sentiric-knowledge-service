# 📚 Sentiric Knowledge Service - Görev Listesi (v1.3 - Üretim Kararlılığı)

Bu belge, knowledge-service'in geliştirme yol haritasını ve önceliklerini tanımlar.

---

### **FAZ 1: Çok-Kiracılı RAG Temeli (Tamamlandı)**

-   [x] **Görev ID: KS-CORE-01 - FastAPI Sunucusu**
-   [x] **Görev ID: KS-CORE-02 - Çok-Kiracılı İndeksleme**
-   [x] **Görev ID: KS-CORE-03 - Çok-Kaynaklı Veri Yükleyiciler**
-   [x] **Görev ID: KS-CORE-04 - Asenkron ve Paralel Yükleme**
-   [x] **Görev ID: KS-CORE-05 - Vektör Arama**

---

### **FAZ 2: Dayanıklılık ve Optimizasyon (Tamamlandı ve Doğrulandı)**

-   [x] **Görev ID: KS-BUG-02 - Qdrant Bağlantı Zaman Aşımını Yönetme (KRİTİK)**
-   [x] **Görev ID: KS-BUG-01 - Yinelenen Veri Yükleme Sorununu Giderme**

---

### **FAZ 3: Gelişmiş Veri Yönetimi (İlerleme Kaydedildi)**

-   **Görev ID: KS-FEAT-01 - Re-Indexing Webhook'u**
    -   **Durum:** ✅ **Tamamlandı**
    -   **Açıklama:** Veri kaynakları güncellendiğinde, servisi yeniden başlatmadan bilgi bankasını tazelemek için bir endpoint oluşturuldu.
    -   **Uygulama Detayları:**
        -   `/api/v1/reindex` adında yeni bir `POST` endpoint'i eklendi.
        -   Bu endpoint, `tenant_id` (opsiyonel) parametresi alarak tüm sistemi veya sadece belirli bir tenant'ı hedefleyebilir.
        -   İşlemin uzun sürebilme ihtimaline karşı, FastAPI `BackgroundTasks` kullanılarak indeksleme arka planda çalıştırılır ve API anında yanıt döner.
        -   Bir veri kaynağı başarıyla indekslendiğinde, `datasources` tablosundaki `last_indexed_at` sütunu mevcut zaman damgası ile güncellenir. Bu, hangi verinin ne zaman güncellendiğini takip etmeyi sağlar.

-   **Görev ID: KS-FEAT-02 - Hibrit Arama (Hybrid Search)**
    -   **Durum:** ⬜ **Planlandı**
    -   **Açıklama:** Anlamsal aramaya ek olarak, ürün kodları veya spesifik terimler gibi durumlar için anahtar kelime tabanlı aramayı da destekleyerek arama doğruluğunu artırmak.