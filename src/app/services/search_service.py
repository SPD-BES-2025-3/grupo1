from typing import List, Dict, Any
# Importe seus repositórios e serviços
from ..repositories.mongo_repository import AnuncioRepository, CidadeRepository, ImobiliariaRepository
from .embedding_service import EmbeddingService

class SearchService:
    """
    Serviço que orquestra a lógica de busca semântica,
    combinando a busca vetorial com a hidratação de dados do MongoDB.
    """
    def _init_(
        self,
        anuncio_repo: AnuncioRepository,
        cidade_repo: CidadeRepository,
        imobiliaria_repo: ImobiliariaRepository,
        embed_service: EmbeddingService,
        vector_index_client: Any  # Cliente do seu BD Vetorial (ex: pinecone.Index)
    ):
        self.anuncio_repo = anuncio_repo
        self.cidade_repo = cidade_repo
        self.imobiliaria_repo = imobiliaria_repo
        self.embed_service = embed_service
        self.vector_index = vector_index_client

    def buscar_similares(self, consulta: str, top_k: int = 5) -> List[Dict[str, Any]]:
        # 1. Gera o vetor da consulta
        vetor_consulta = self.embed_service.gerar_vetor(consulta)

        # 2. Busca no Banco Vetorial pelos IDs
        resultados_vetoriais = self.vector_index.query(
            vector=vetor_consulta,
            top_k=top_k,
            include_metadata=False
        )
        ids_anuncios = [match['id'] for match in resultados_vetoriais['matches']]

        if not ids_anuncios:
            return []

        # 3. Busca os documentos de anúncios no MongoDB
        anuncios = self.anuncio_repo.find_by_ids(ids_anuncios)

        # 4. Coleta IDs para hidratação
        cidade_ids = list({anuncio['cidade_id'] for anuncio in anuncios})
        imobiliaria_ids = list({anuncio['imobiliaria_id'] for anuncio in anuncios})

        # 5. Busca os documentos de cidade e imobiliária em lote
        cidades = self.cidade_repo.find_by_ids(cidade_ids)
        imobiliarias = self.imobiliaria_repo.find_by_ids(imobiliaria_ids)

        # 6. Cria mapas para acesso rápido
        cidades_map = {str(cidade['_id']): cidade for cidade in cidades}
        imobiliarias_map = {str(imob['_id']): imob for imob in imobiliarias}

        # 7. "Hidrata" os resultados
        resultados_finais = []
        # Mantém a ordem de relevância do banco vetorial
        for anuncio_id in ids_anuncios:
            anuncio_encontrado = next((anuncio for anuncio in anuncios if str(anuncio['_id']) == anuncio_id), None)
            
            if not anuncio_encontrado:
                continue

            cidade_id_str = str(anuncio_encontrado['cidade_id'])
            imobiliaria_id_str = str(anuncio_encontrado['imobiliaria_id'])

            anuncio_detalhado = {
                **anuncio_encontrado,
                "id": anuncio_id,
                "cidade": cidades_map.get(cidade_id_str),
                "imobiliaria": imobiliarias_map.get(imobiliaria_id_str)
            }
            resultados_finais.append(anuncio_detalhado)

        return resultados_finais