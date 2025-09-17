# ========== DOSYA: sentiric-knowledge-service/app/grpc_server/service.py (YENİ DOSYA) ==========

import structlog
from app.api.v1.endpoints import query_knowledge_base
from app.core.config import settings

# Otomatik üretilen gRPC kodlarını import et
from sentiric.knowledge.v1 import knowledge_pb2, knowledge_pb2_grpc

log = structlog.get_logger(__name__)

# gRPC servis sınıfını, otomatik üretilen iskeletten türet
class KnowledgeService(knowledge_pb2_grpc.KnowledgeServiceServicer):
    
    # 'Query' RPC metodunu implemente et
    async def Query(self, request: knowledge_pb2.QueryRequest, context) -> knowledge_pb2.QueryResponse:
        log.info("gRPC Query isteği alındı", tenant_id=request.tenant_id, query=request.query)
        
        try:
            # Mevcut HTTP endpoint'inin kullandığı iş mantığını doğrudan çağır
            # Bu, kod tekrarını önler ve tutarlılığı sağlar.
            collection_name = f"{settings.VECTOR_DB_COLLECTION_PREFIX}{request.tenant_id}"
            results = await query_knowledge_base_logic(request.query, collection_name, request.top_k)
            
            # Gelen sonuçları Protobuf formatına dönüştür
            proto_results = []
            for result in results:
                # result, qdrant_client.models.ScoredPoint objesidir
                proto_results.append(
                    knowledge_pb2.QueryResult(
                        content=result.payload.get("text", ""),
                        score=result.score,
                        source=result.payload.get("source", "")
                    )
                )

            return knowledge_pb2.QueryResponse(results=proto_results)

        except Exception as e:
            log.error("gRPC Query işlenirken hata oluştu", error=str(e), exc_info=True)
            # Tonic/gRPC'nin anlayacağı bir hata formatı oluştur
            await context.abort(grpc.StatusCode.INTERNAL, "Dahili sunucu hatası")


# HTTP endpoint'indeki mantığı yeniden kullanılabilir hale getirelim
# Bu fonksiyonu `app/api/v1/endpoints.py`'den buraya taşıyabilir veya oradan import edebiliriz.
# Temizlik açısından burada yeniden tanımlamak daha iyi olabilir.
from app.services.query_service import find_similar_documents

async def query_knowledge_base_logic(query: str, collection_name: str, top_k: int):
    # Bu fonksiyon, asıl işi yapan `find_similar_documents`'ı çağırır.
    # Bu, hem HTTP hem de gRPC'nin aynı mantığı kullanmasını sağlar.
    return await find_similar_documents(query, collection_name, top_k)