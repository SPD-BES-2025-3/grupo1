from .services.embedding_service import EmbeddingService
from .repositories.chroma_repository import ChromaRepository
from typing import List, Dict, Any

class SearchService:
    def __init__(self, embedding_service: EmbeddingService, chroma_repo: ChromaRepository):
        self.embedding_service = embedding_service
        self.chroma_repo = chroma_repo

    def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        query_embedding = self.embedding_service.create_embeddings([query])
        results = self.chroma_repo.query(query_embeddings=query_embedding, n_results=n_results)
        return results
