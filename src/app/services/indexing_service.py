from ..services.embedding_service import EmbeddingService
from ..repositories.chroma_repository import ChromaRepository
from ..models import ImovelInDB
from typing import List

class IndexingService:
    def __init__(self, embedding_service: EmbeddingService, chroma_repo: ChromaRepository):
        self.embedding_service = embedding_service
        self.chroma_repo = chroma_repo

    def index_imoveis(self, imoveis: List[ImovelInDB]):
        contents = [f"{imovel.titulo} {imovel.descricao} {' '.join(imovel.especificacoes)}" for imovel in imoveis]
        embeddings = self.embedding_service.create_embeddings(contents)
        ids = [str(imovel.id) for imovel in imoveis]
        
        # Converter metadatas para formato compatível com ChromaDB
        metadatas = []
        for imovel in imoveis:
            metadata = {
                "id": str(imovel.id),
                "titulo": imovel.titulo,
                "descricao": imovel.descricao,
                "especificacoes": " | ".join(imovel.especificacoes)  # Converter lista para string
            }
            metadatas.append(metadata)

        self.chroma_repo.add_documents(ids=ids, documents=contents, metadatas=metadatas)
    
    def index_single_imovel(self, imovel: ImovelInDB):
        """Indexa um único imóvel"""
        content = f"{imovel.titulo} {imovel.descricao} {' '.join(imovel.especificacoes)}"
        embedding = self.embedding_service.create_embeddings([content])[0]
        imovel_id = str(imovel.id)
        
        metadata = {
            "id": imovel_id,
            "titulo": imovel.titulo,
            "descricao": imovel.descricao,
            "especificacoes": " | ".join(imovel.especificacoes)
        }
        
        self.chroma_repo.upsert_documents(
            ids=[imovel_id], 
            documents=[content], 
            metadatas=[metadata]
        )
    
    def delete_imovel_from_index(self, imovel_id: str):
        """Remove um imóvel do índice de busca"""
        self.chroma_repo.delete_document(imovel_id)
