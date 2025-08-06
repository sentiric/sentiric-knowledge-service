from app.services.qdrant_service import get_qdrant_client
from app.services.embedding_service import get_embedding_model
# Artık config'e doğrudan ihtiyacı yok

async def find_similar_documents(query: str, collection_name: str, top_k: int):
    client = get_qdrant_client()
    model = get_embedding_model()
    
    query_vector = model.encode(query).tolist()

    search_result = client.search(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=top_k,
    )
    return search_result