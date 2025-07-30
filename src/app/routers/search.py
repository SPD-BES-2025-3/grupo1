from fastapi import APIRouter, Depends
from typing import List, Dict, Any
from pydantic import BaseModel
from ..services.search_service import SearchService
from ..services.embedding_service import EmbeddingService
from ..services.llm_reranking_service import LLMRerankingService
from ..database import get_chroma_repo, get_mongo_repo

router = APIRouter()

@router.get("/search-test")
def search_test():
    return {"message": "Search endpoint is working", "test": True}

@router.get("/search/")
def search_imoveis(query: str = "casa com piscina", n_results: int = 30):
    """
    Busca semântica por imóveis - Implementação correta da arquitetura
    Fluxo: Query → Embedding → ChromaDB (similaridade cosseno) → MongoDB (conteúdo completo)
    """
    try:
        from ..repositories.mongo_repository import MongoRepository
        from ..repositories.chroma_repository import ChromaRepository
        from ..config import MONGO_URI, MONGO_DB_NAME
        
        mongo_repo = MongoRepository(uri=MONGO_URI, db_name=MONGO_DB_NAME)
        chroma_repo = ChromaRepository(path="./chroma_db")
        
        embedding_service = EmbeddingService()
        search_service = SearchService(
            embedding_service=embedding_service, 
            chroma_repo=chroma_repo, 
            mongo_repo=mongo_repo
        )
        
        results = search_service.search(query=query, n_results=n_results)
        
        return {
            "query": query,
            "results": results,
            "total_found": len(results),
            "search_type": "semantic_cosine_similarity", #
            "architecture": "ChromaDB (embeddings) + MongoDB (content)"
        }
        
    except Exception as e:
        from pymongo import MongoClient
        
        try:
            client = MongoClient("mongodb://localhost:27017")
            db = client["spd_imoveis"]
            collection = db["imoveis"]
            
            fallback_results = list(collection.find({
                "$or": [
                    {"titulo": {"$regex": query, "$options": "i"}},
                    {"descricao": {"$regex": query, "$options": "i"}}
                ]
            }).limit(n_results))
            
            for result in fallback_results:
                result["id"] = str(result["_id"])
                del result["_id"]
            
            return {
                "query": query,
                "results": fallback_results,
                "total_found": len(fallback_results),
                "search_type": "textual_fallback",
                "note": f"Fallback usado devido ao erro: {str(e)}"
            }
            
        except Exception as fallback_error:
            return {
                "query": query,
                "results": [],
                "total_found": 0,
                "error": f"Erro na busca: {str(fallback_error)}"
            }

class FeedbackRequest(BaseModel):
    query: str
    liked_properties: List[Dict[str, Any]]
    disliked_properties: List[Dict[str, Any]]
    remaining_properties: List[Dict[str, Any]]

@router.post("/rerank/")
def rerank_with_feedback(feedback: FeedbackRequest):
    """
    Re-ranking inteligente usando LLM baseado no feedback do usuário
    """
    try:
        llm_service = LLMRerankingService()
        
        llm_response = llm_service.rerank_properties(
            query=feedback.query,
            liked_properties=feedback.liked_properties,
            disliked_properties=feedback.disliked_properties,
            remaining_properties=feedback.remaining_properties
        )
        
        from ..repositories.mongo_repository import MongoRepository
        from ..config import MONGO_URI, MONGO_DB_NAME
        
        mongo_repo = MongoRepository(uri=MONGO_URI, db_name=MONGO_DB_NAME)
        
        enhanced_results = []
        decision_reasoning = ""
        
        if isinstance(llm_response, dict) and "selected_properties" in llm_response:
            decision_reasoning = llm_response.get("decision_reasoning", "")
            selected_properties = llm_response.get("selected_properties", [])
        else:
            selected_properties = llm_response if isinstance(llm_response, list) else []
        
        for item in selected_properties:
            imovel_id = item.get("id")
            if imovel_id:
                imovel_data = mongo_repo.get_imovel_by_id(imovel_id)
                if imovel_data:
                    imovel_data["llm_reason"] = item.get("reason", "Selecionado pela IA")
                    enhanced_results.append(imovel_data)
        
        return {
            "query": feedback.query,
            "reranked_results": enhanced_results,
            "total_found": len(enhanced_results),
            "decision_reasoning": decision_reasoning,
            "method": "llm_selection_from_remaining",
            "model": "gemma3:latest"
        }
        
    except Exception as e:
        return {
            "query": feedback.query,
            "reranked_results": [],
            "total_found": 0,
            "error": f"Erro no re-ranking: {str(e)}"
        }