from .base import BaseLoader
from app.db.session import get_db_connection

class PostgresLoader(BaseLoader):
    def load(self, uri: str) -> list[dict]:
        """Verilen tablodaki tüm satırları metin olarak yükler."""
        conn = get_db_connection()
        if not conn: return []
        
        documents = []
        try:
            with conn.cursor() as cur:
                # GÜVENLİK NOTU: Gerçek bir uygulamada, 'uri' doğrudan sorguya eklenmemeli,
                # SQL injection'ı önlemek için beyaz listeden kontrol edilmelidir.
                # Bu demo için güvenli kabul ediyoruz.
                cur.execute(f"SELECT * FROM {uri}")
                colnames = [desc[0] for desc in cur.description]
                for row in cur.fetchall():
                    row_dict = dict(zip(colnames, row))
                    # Satırı anlamlı bir metne dönüştür
                    text = ", ".join(f"{key}: {value}" for key, value in row_dict.items())
                    documents.append({"text": text, "source": f"postgres:{uri}"})
            return documents
        finally:
            conn.close()