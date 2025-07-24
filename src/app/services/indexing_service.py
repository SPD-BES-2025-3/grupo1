from .embedding_service import EmbeddingService
from ..repositories.chroma_repository import ChromaRepository
from ..models import Article
from typing import List

class IndexingService:
    def __init__(self, embedding_service: EmbeddingService, chroma_repo: ChromaRepository):
        self.embedding_service = embedding_service
        self.chroma_repo = chroma_repo

    def index_articles(self, articles: List[Article]):
        contents = [article.content for article in articles]
        embeddings = self.embedding_service.create_embeddings(contents)
        ids = [str(article.id) for article in articles]
        metadatas = [article.dict() for article in articles]

        self.chroma_repo.add_documents(ids=ids, documents=contents, metadatas=metadatas)
