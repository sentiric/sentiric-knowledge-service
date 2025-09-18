# sentiric-knowledge-service/app/grpc_server/service.py
import grpc
import structlog
from app.core.config import settings
# DEĞİŞİKLİK: Doğru yerden import yapıyoruz
from app.services.query_service import find_similar_documents 
from sentiric.knowledge.v1 import knowledge_pb2, knowledge_pb2_grpc

log = structlog.get_logger(__name__)

class KnowledgeService(knowledge_pb2_grpc.KnowledgeServiceServicer):
    
    async def Query(self, request: knowledge_pb2.QueryRequest, context) -> knowledge_pb2.QueryResponse:
        log.info("gRPC Query isteği alındı", tenant_id=request.tenant_id, query=request.query)
        
        try:
            collection_name = f"{settings.VECTOR_DB_COLLECTION_PREFIX}{request.tenant_id}"
            # DEĞİŞİKLİK: Doğrudan ana iş mantığı fonksiyonunu çağırıyoruz
            results = await find_similar_documents(request.query, collection_name, request.top_k)
            
            proto_results = []
            for result in results:
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
            await context.abort(grpc.StatusCode.INTERNAL, "Dahili sunucu hatası")