### File: `sentiric-knowledge-service/app/loaders/postgres_loader.py`

from .base import BaseLoader
from app.db.session import get_db_connection
from psycopg2 import sql # YENİ: Güvenli sorgu oluşturmak için import

class PostgresLoader(BaseLoader):
    def load(self, uri: str) -> list[dict]:
        """Verilen tablodaki tüm satırları metin olarak yükler."""
        conn = get_db_connection()
        if not conn: return []
        
        documents = []
        try:
            with conn.cursor() as cur:
                # GÜVENLİK DÜZELTMESİ: SQL enjeksiyonunu önlemek için sorguyu güvenli bir şekilde oluştur.
                # 'uri' artık bir SQL tanımlayıcısı (Identifier) olarak ele alınır,
                # rastgele bir komut olarak değil.
                query = sql.SQL("SELECT * FROM {}").format(sql.Identifier(uri))
                cur.execute(query)
                
                colnames = [desc[0] for desc in cur.description]
                for row in cur.fetchall():
                    row_dict = dict(zip(colnames, row))
                    # Satırı anlamlı bir metne dönüştür
                    text = ", ".join(f"{key}: {value}" for key, value in row_dict.items())
                    documents.append({"text": text, "source": f"postgres:{uri}"})
            return documents
        finally:
            conn.close()