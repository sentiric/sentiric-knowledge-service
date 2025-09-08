# app/db/session.py

import psycopg2
from app.core.config import settings
from app.core.logging import logger

def get_db_connection():
    try:
        conn = psycopg2.connect(settings.POSTGRES_URL)
        return conn
    except Exception as e:
        logger.error("Veritabanı bağlantısı kurulamadı.", error=str(e))
        return None

def get_tenants() -> list[str]:
    conn = get_db_connection()
    if not conn: return []
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT DISTINCT tenant_id FROM datasources WHERE is_active = TRUE")
            tenants = [row[0] for row in cur.fetchall()]
            return tenants
    finally:
        conn.close()

def get_datasources_for_tenant(tenant_id: str) -> list[dict]:
    conn = get_db_connection()
    if not conn: return []
    try:
        with conn.cursor() as cur:
            # _MODIFIED_ id sütununu da seçiyoruz
            cur.execute("SELECT id, source_type, source_uri FROM datasources WHERE tenant_id = %s AND is_active = TRUE", (tenant_id,))
            sources = [{"id": row[0], "type": row[1], "uri": row[2]} for row in cur.fetchall()]
            return sources
    finally:
        conn.close()

# _NEW_ Yeni fonksiyon
def update_datasource_timestamp(datasource_id: int):
    """Belirtilen veri kaynağının last_indexed_at zaman damgasını günceller."""
    conn = get_db_connection()
    if not conn:
        logger.error("Timestamp güncellenemedi: Veritabanı bağlantısı yok.")
        return
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE datasources SET last_indexed_at = NOW() WHERE id = %s", (datasource_id,))
            conn.commit()
            logger.info("Veri kaynağı zaman damgası güncellendi.", datasource_id=datasource_id)
    except Exception as e:
        logger.error("Veri kaynağı zaman damgası güncellenirken hata.", datasource_id=datasource_id, error=str(e))
    finally:
        conn.close()