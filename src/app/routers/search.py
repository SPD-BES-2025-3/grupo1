from fastapi import APIRouter, Depends
from typing import List, Dict, Any
from ..services.search_service import SearchService
from ..services.embedding_service import EmbeddingService
from ..database import get_chroma_repo

router = APIRouter()

@router.get("/search", response_model=List[Dict[str, Any]])
def search(query: str, n_results: int = 5, chroma_repo: any = Depends(get_chroma_repo)):
    embedding_service = EmbeddingService()
    search_service = SearchService(embedding_service=embedding_service, chroma_repo=chroma_repo)
    results = search_service.search(query=query, n_results=n_results)
    return results
