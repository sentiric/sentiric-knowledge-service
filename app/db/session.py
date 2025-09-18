# app/db/session.py
import psycopg2
import structlog # YENİ
from app.core.config import settings

log = structlog.get_logger(__name__) # YENİ

def get_db_connection():
    try:
        conn = psycopg2.connect(settings.POSTGRES_URL)
        return conn
    except Exception as e:
        log.error("Veritabanı bağlantısı kurulamadı.", error=str(e))
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
        if conn:
            conn.close()

def get_datasources_for_tenant(tenant_id: str) -> list[dict]:
    conn = get_db_connection()
    if not conn: return []
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, source_type, source_uri FROM datasources WHERE tenant_id = %s AND is_active = TRUE", (tenant_id,))
            sources = [{"id": row[0], "type": row[1], "uri": row[2]} for row in cur.fetchall()]
            return sources
    finally:
        if conn:
            conn.close()

def update_datasource_timestamp(datasource_id: int):
    conn = get_db_connection()
    if not conn:
        log.error("Timestamp güncellenemedi: Veritabanı bağlantısı yok.")
        return
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE datasources SET last_indexed_at = NOW() WHERE id = %s", (datasource_id,))
            conn.commit()
            log.info("Veri kaynağı zaman damgası güncellendi.", datasource_id=datasource_id)
    except Exception as e:
        log.error("Veri kaynağı zaman damgası güncellenirken hata.", datasource_id=datasource_id, error=str(e))
    finally:
        if conn:
            conn.close()