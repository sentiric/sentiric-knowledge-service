# 📚 Sentiric Knowledge Service

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/framework-FastAPI-green.svg)](https://fastapi.tiangolo.com/)

**Sentiric Knowledge Service**, Sentiric'in AI ajanları için **çok-kaynaklı ve çok-kiracılı (multi-tenant)**, yapılandırılmış ve aranabilir bir bilgi tabanı oluşturur ve yönetir. Bu servis, platformun RAG (Retrieval-Augmented Generation) mimarisinin kalbidir.

## 🎯 Temel Sorumluluklar

*   **Dinamik Veri Yükleme:** PostgreSQL'deki `datasources` tablosunu okuyarak, her bir kiracı (tenant) için farklı kaynaklardan (dosyalar, web siteleri, veritabanları) paralel ve asenkron olarak veri toplar.
*   **Vektör İndeksleme:** Toplanan verileri anlamsal olarak aranabilir vektörlere dönüştürür ve **Qdrant** veritabanında her kiracı için ayrı bir koleksiyonda saklar. Bu, tam veri izolasyonu sağlar.
*   **Sorgu API'si:** `/api/v1/query` endpoint'i üzerinden, AI ajanlarının (`llm-service` aracılığıyla) belirli bir kiracının bilgi bankasında anlamsal arama yapmasını sağlar.

## 🛠️ Teknoloji Yığını

*   **Dil:** Python
*   **Web Çerçevesi:** FastAPI
*   **Vektör Veritabanı:** Qdrant
*   **Embedding Modeli:** `sentence-transformers`
*   **Veri Kaynağı Okuyucuları:** `psycopg2` (PostgreSQL), `requests` & `BeautifulSoup` (Web), `playwright` (Dinamik Web - Opsiyonel)

## 🔌 API Etkileşimleri

*   **Gelen (Sunucu):**
    *   `sentiric-llm-service` (veya doğrudan `agent-service`) (REST/JSON): `/query` endpoint'ine anlamsal arama istekleri alır.
*   **Giden (İstemci):**
    *   `PostgreSQL`: Hangi veri kaynaklarının yükleneceğini ve bu kaynakların içeriğini okumak için.
    *   `Qdrant`: Vektörleri depolamak ve aramak için.
    *   Harici Web Siteleri: Veri toplamak için.

## 🚀 Yerel Geliştirme ve Test

1.  **Platformu Başlatın:** Bu servis `postgres` ve `qdrant`'a bağımlıdır. `sentiric-infrastructure`'dan `make up` komutuyla tüm platformu başlatın.
2.  **Bağımlılıkları Kurun:** `pip install -e ".[dev]"`
3.  **Servisi Başlatın:** `uvicorn app.main:app --reload --port 50055`
4.  **Testleri Çalıştırın:** `pytest -v`

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! Lütfen projenin ana [Sentiric Governance](https://github.com/sentiric/sentiric-governance) reposundaki kodlama standartlarına ve katkıda bulunma rehberine göz atın.

---
## 🏛️ Anayasal Konum

Bu servis, [Sentiric Anayasası'nın (v11.0)](https://github.com/sentiric/sentiric-governance/blob/main/docs/blueprint/Architecture-Overview.md) **Zeka & Orkestrasyon Katmanı**'nda yer alan merkezi bir bileşendir.