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
            cur.execute("SELECT source_type, source_uri FROM datasources WHERE tenant_id = %s AND is_active = TRUE", (tenant_id,))
            sources = [{"type": row[0], "uri": row[1]} for row in cur.fetchall()]
            return sources
    finally:
        conn.close()