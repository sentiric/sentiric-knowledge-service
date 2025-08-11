# app/services/query_service.py

import asyncio
from app.services.qdrant_service import get_qdrant_client
from app.services.embedding_service import get_embedding_model

async def find_similar_documents(query: str, collection_name: str, top_k: int) -> list:
    """
    Verilen bir sorgu metnini vektöre dönüştürür ve Qdrant'taki ilgili koleksiyonda
    anlamsal olarak en benzer dokümanları asenkron olarak bulur.

    Args:
        query: Kullanıcının arama sorgusu.
        collection_name: Arama yapılacak Qdrant koleksiyonunun adı.
        top_k: Döndürülecek en benzer sonuç sayısı.

    Returns:
        Qdrant'tan gelen sonuçların bir listesi.
    """
    client = get_qdrant_client()
    model = get_embedding_model()
    
    # model.encode() CPU-yoğun bir işlemdir. Uygulamanın event döngüsünü
    # bloke etmemek için bunu bir thread içinde çalıştırmak en iyi pratiktir.
    query_vector = await asyncio.to_thread(model.encode, query)

    # qdrant_client'in kendisi 'await' desteklemiyorsa bile (kütüphane versiyonuna bağlı),
    # ağ I/O'su yapan bu işlemi de bir thread'e taşımak en güvenlisidir.
    # Ancak modern versiyonlar genellikle async API sunar. Şimdilik en güvenli
    # yöntem olan to_thread'i kullanalım.
    search_result = await asyncio.to_thread(
        client.search,
        collection_name=collection_name,
        query_vector=query_vector.tolist(),
        limit=top_k,
    )
    
    return search_result