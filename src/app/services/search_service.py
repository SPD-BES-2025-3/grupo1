from typing import List, Dict, Any
from ..repositories.mongo_repository import MongoRepository
from ..repositories.chroma_repository import ChromaRepository
from ..services.embedding_service import EmbeddingService

class SearchService:
    def __init__(self, embedding_service: EmbeddingService, chroma_repo: ChromaRepository, mongo_repo: MongoRepository):
        self.embedding_service = embedding_service
        self.chroma_repo = chroma_repo
        self.mongo_repo = mongo_repo

    def search(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Fluxo correto:
        1. Query → Embedding
        2. ChromaDB → Similaridade Cosseno → Top 5 IDs
        3. MongoDB → Buscar conteúdo completo por IDs
        """
        # 1. Transformar query em embedding
        query_embedding = self.embedding_service.create_embeddings([query])[0]
        
        # 2. Buscar IDs similares no ChromaDB (similaridade de cosseno)
        chroma_results = self.chroma_repo.query(query_embeddings=[query_embedding], n_results=n_results)
        
        # ChromaDB retorna: {'ids': [['id1', 'id2']], 'distances': [[0.1, 0.2]], ...}
        if not chroma_results.get('ids') or not chroma_results['ids'][0]:
            return []
        
        # 3. Obter os IDs mais similares
        similar_ids = chroma_results['ids'][0]
        distances = chroma_results.get('distances', [[]])[0] if chroma_results.get('distances') else []
        
        # 4. Buscar conteúdo completo no MongoDB usando os IDs
        imoveis = []
        for i, imovel_id in enumerate(similar_ids):
            try:
                # Buscar dados completos no MongoDB
                imovel_data = self.mongo_repo.get_imovel_by_id(imovel_id)
                if imovel_data:
                    # Adicionar score de similaridade se disponível
                    if i < len(distances):
                        imovel_data['similarity_score'] = 1 - distances[i]  # Converter distância para similaridade
                    imoveis.append(imovel_data)
            except Exception as e:
                print(f"Erro ao buscar imóvel {imovel_id} no MongoDB: {e}")
                continue
        
        return imoveis
