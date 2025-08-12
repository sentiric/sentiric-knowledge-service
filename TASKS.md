# 📚 Sentiric Knowledge Service - Görev Listesi

Bu belge, `knowledge-service`'in geliştirme yol haritasını ve önceliklerini tanımlar.

---

### Faz 1: Çok-Kiracılı RAG Temeli (Mevcut Durum)

Bu faz, servisin temel RAG yeteneklerini çoklu kiracı ve çoklu kaynak desteği ile sunmasını hedefler.

-   [x] **FastAPI Sunucusu:** `/api/v1/query` ve `/health` endpoint'leri.
-   [x] **Çok-Kiracılı İndeksleme:** `datasources` tablosunu okuyarak her `tenant_id` için ayrı bir Qdrant koleksiyonu oluşturma.
-   [x] **Çok-Kaynaklı Veri Yükleyiciler (`loaders`):**
    -   [x] `FileLoader`: Yerel dosya sisteminden `.txt`, `.md` okuma.
    -   [x] `WebLoader`: Statik web sayfalarından içerik çekme.
    -   [x] `PostgresLoader`: Belirtilen PostgreSQL tablolarından veri çekme.
    -   [x] `GoogleTravelLoader`: Dinamik web sitelerinden veri çekme (opsiyonel).
-   [x] **Asenkron ve Paralel Yükleme:** Bir kiracıya ait tüm veri kaynaklarını `asyncio.gather` ile paralel olarak işleme.
-   [x] **Vektör Arama:** Gelen sorguyu vektöre çevirip ilgili kiracının koleksiyonunda anlamsal arama yapma.

---

### Faz 2: Gelişmiş Veri Yönetimi ve Sorgulama (Sıradaki Öncelik)

Bu faz, veri yönetimini daha dinamik ve sorgulama yeteneklerini daha güçlü hale getirmeyi hedefler.

-   [ ] **Görev ID: KS-001 - Re-Indexing Webhook'u**
    -   **Açıklama:** Belirli bir kiracının veri kaynaklarını yeniden indekslemek için tetiklenebilecek bir `/api/v1/reindex` webhook endpoint'i oluştur. Bu, bir yönetici `dashboard-ui`'dan bir veri kaynağını güncellediğinde kullanışlı olacaktır.
    -   **Durum:** ⬜ Planlandı.

-   [ ] **Görev ID: KS-002 - Hibrit Arama (Hybrid Search)**
    -   **Açıklama:** Anlamsal (vektör) aramaya ek olarak, anahtar kelime tabanlı (sparse vector / BM25) aramayı da destekle. Bu, özellikle ürün kodları veya spesifik isimler gibi tam eşleşme gerektiren sorgularda doğruluğu artırır.
    -   **Durum:** ⬜ Planlandı.

-   [ ] **Görev ID: KS-003 - Daha Fazla Veri Yükleyici**
    -   **Açıklama:** `Notion`, `Google Docs`, `PDF` gibi popüler veri kaynakları için yeni loader'lar geliştir.
    -   **Durum:** ⬜ Planlandı.

---

### Faz 3: Güvenlik ve Erişim Kontrolü

-   [ ] **Görev ID: KS-004 - Doküman Seviyesinde Erişim Kontrolü (ACL)**
    -   **Açıklama:** Vektör veritabanındaki her bir dokümana meta veri olarak erişim rolleri (`public`, `agent_only`, `admin`) ekle. Sorgu sırasında, sorguyu yapan kullanıcının rolüne göre sadece yetkili olduğu dokümanların dönmesini sağla.
    -   **Durum:** ⬜ Planlandı.
    
---
