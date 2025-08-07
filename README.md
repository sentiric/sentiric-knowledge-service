# 📚 Sentiric Knowledge Service

**Açıklama:** Sentiric'in AI ajanları için çok-kaynaklı ve çok-kiracılı (multi-tenant), yapılandırılmış ve aranabilir bir bilgi tabanı oluşturur ve yönetir. Bu servis, RAG (Retrieval-Augmented Generation) mimarisinin kalbidir.

**Temel Sorumluluklar:**
*   **Dinamik Veri Yükleme:** PostgreSQL'deki `datasources` tablosunu okuyarak, her bir kiracı (tenant) için farklı kaynaklardan (dosyalar, web siteleri, veritabanları) veri toplar.
*   **Vektör İndeksleme:** Toplanan verileri anlamsal olarak aranabilir vektörlere dönüştürür ve Qdrant veritabanında her kiracı için ayrı bir koleksiyonda saklar.
*   **Sorgu API'si:** `/api/v1/query` endpoint'i üzerinden, AI ajanlarının belirli bir kiracının bilgi bankasında anlamsal arama yapmasını sağlar.

**Teknoloji Yığını:**
*   **Web Çerçevesi:** FastAPI
*   **Vektör Veritabanı:** Qdrant
*   **Embedding Modeli:** `sentence-transformers`
*   **Veri Kaynağı Okuyucuları:** `psycopg2`, `requests`, `BeautifulSoup`, `playwright`

---

## 🚀 Hızlı Başlangıç

 ( yerel )
 ```bash
uvicorn app.main:app --reload --port 5055
```

 (Docker ile)

Bu servis, Sentiric platformunun bir parçasıdır ve en kolay şekilde `sentiric-infrastructure` reposundaki `docker-compose.yml` ile çalıştırılır.

1.  **Platformu Başlat:** `sentiric-infrastructure` dizininde `docker compose up --build -d` komutunu çalıştırın.
2.  **Servisin Sağlığını Kontrol Et:**
    ```bash
    curl http://localhost:5055/health
    ```
    `{"status":"ok", "project":"Sentiric Knowledge Service"}` yanıtını görmelisiniz.

---

## 🤖 Demo ve Kullanım Senaryoları

Servisin "Genesis Demo" ile gelen yeteneklerini canlı olarak test etmek ve farklı kullanım senaryolarını görmek için lütfen aşağıdaki rehberi inceleyin:

➡️ **[Canlı Demo ve Test Rehberi (DEMO.md)](DEMO.md)**

---

## 🧪 Otomatize Testleri Çalıştırma

Geliştirme ortamında, servisin doğru çalıştığını doğrulamak için `pytest` kullanabilirsiniz.

1.  **Geliştirme Bağımlılıklarını Kurun:**
    ```bash
    pip install -r requirements-dev.txt
    ```
2.  **Testleri Çalıştırın:** (Platformun Docker Compose ile çalışır durumda olduğundan emin olun)
    ```bash
    pytest -v
    ```
    Bu komut, `tests/` klasöründeki tüm testleri otomatik olarak bulup çalıştıracaktır.

---

## 🧑‍💻 Geliştiriciler İçin Ek Notlar

### Opsiyonel: Google Travel Loader'ı Aktif Etme

`google_travel_loader`, dinamik web sitelerinden veri çekmek için `playwright` kütüphanesini kullanır. Bu kütüphane ve bağımlı olduğu tarayıcılar, Docker imaj boyutunu büyük ölçüde artırdığı için varsayılan kurulumda bulunmazlar.

Bu özelliği yerel geliştirme ortamınızda aktif etmek için:

1.  Gerekli Python paketini kurun:
    ```bash
    pip install playwright
    ```
2.  Gerekli tarayıcıları indirin ve kurun:
    ```bash
    playwright install --with-deps chromium
    ```
3.  `sentiric-infrastructure/postgres-init/04_genesis_demo_data.sql` dosyasında `google_travel` veri kaynağını tanımlayan satırın başındaki yorum işaretini (`--`) kaldırın ve platformu yeniden başlatın.

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Lütfen projenin ana [Sentiric Governance](https://github.com/sentiric/sentiric-governance) reposundaki kodlama standartlarına ve katkıda bulunma rehberine göz atın.
