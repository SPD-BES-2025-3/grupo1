# app/services/indexing_service.py

from typing import Any
from ..models import AnuncioRawInput, AnuncioSchema, AnuncioInDB
from ..repositories.anuncio_repository import AnuncioRepository
from ..repositories.cidade_repository import CidadeRepository
from ..repositories.imobiliaria_repository import ImobiliariaRepository
from .embedding_service import EmbeddingService

class IndexingService:
    def __init__(
        self,
        anuncio_repo: AnuncioRepository,
        cidade_repo: CidadeRepository,
        imobiliaria_repo: ImobiliariaRepository,
        embed_service: EmbeddingService,
        vector_index_client: Any
    ):
        self.anuncio_repo = anuncio_repo
        self.cidade_repo = cidade_repo
        self.imobiliaria_repo = imobiliaria_repo
        self.embed_service = embed_service
        self.vector_index = vector_index_client

    def indexar_anuncio(self, anuncio_raw: AnuncioRawInput) -> AnuncioInDB:
        """
        Processo completo de indexação de um novo anúncio.
        """
        cidade_doc = self.cidade_repo.find_or_create(anuncio_raw.cidade)
        imobiliaria_doc = self.imobiliaria_repo.find_or_create(anuncio_raw.imobiliaria)

        anuncio_para_criar = AnuncioSchema(
            titulo=anuncio_raw.titulo,
            descricao=anuncio_raw.descricao,
            preco=anuncio_raw.preco,
            area_m2=anuncio_raw.area_m2,
            quartos=anuncio_raw.quartos,
            banheiros=anuncio_raw.banheiros,
            endereco=anuncio_raw.endereco,
            url_origem=anuncio_raw.url_origem,
            cidade_id=cidade_doc.id,  
            imobiliaria_id=imobiliaria_doc.id 
        )
        
        anuncio_criado = self.anuncio_repo.create(anuncio_para_criar)
        print(f"Anúncio {anuncio_criado.id} criado no MongoDB.")

        texto_para_vetorizar = (
            f"Imóvel à venda em {cidade_doc.nome}, {cidade_doc.estado}. "
            f"Título: {anuncio_criado.titulo}. "
            f"Descrição: {anuncio_criado.descricao}. "
            f"Características: {anuncio_criado.quartos} quartos, {anuncio_criado.banheiros} banheiros, "
            f"{anuncio_criado.area_m2} metros quadrados. "
            f"Preço: R$ {anuncio_criado.preco}."
        )
        
        vetor = self.embed_service.gerar_vetor(texto_para_vetorizar)

        self.vector_index.upsert(vectors=[(str(anuncio_criado.id), vetor)])
        print(f"Vetor para o anúncio {anuncio_criado.id} indexado no banco vetorial.")

        return anuncio_criado