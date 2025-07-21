from fastapi import Depends
from typing import Annotated

# Importe os componentes necessários
from ..database import get_mongo_client, get_vector_db_index
from ..repositories.mongo_repository import AnuncioRepository, CidadeRepository, ImobiliariaRepository
from ..services.embedding_service import embedding_service
from ..services.indexing_service import IndexingService
from ..services.search_service import SearchService

# Esta abordagem de "fábricas" de dependências ajuda a instanciar os serviços
# apenas quando uma requisição chega, e facilita a substituição por mocks nos testes.

def get_anuncio_repository():
    db = get_mongo_client()
    return AnuncioRepository(db)

def get_cidade_repository():
    db = get_mongo_client()
    return CidadeRepository(db)

def get_imobiliaria_repository():
    db = get_mongo_client()
    return ImobiliariaRepository(db)

def get_indexing_service(
    anuncio_repo: Annotated[AnuncioRepository, Depends(get_anuncio_repository)],
    cidade_repo: Annotated[CidadeRepository, Depends(get_cidade_repository)],
    imobiliaria_repo: Annotated[ImobiliariaRepository, Depends(get_imobiliaria_repository)]
) -> IndexingService:
    """Constrói e retorna uma instância do IndexingService."""
    return IndexingService(
        anuncio_repo=anuncio_repo,
        cidade_repo=cidade_repo,
        imobiliaria_repo=imobiliaria_repo,
        embed_service=embedding_service,
        vector_index_client=get_vector_db_index()
    )

def get_search_service(
    anuncio_repo: Annotated[AnuncioRepository, Depends(get_anuncio_repository)],
    cidade_repo: Annotated[CidadeRepository, Depends(get_cidade_repository)],
    imobiliaria_repo: Annotated[ImobiliariaRepository, Depends(get_imobiliaria_repository)]
) -> SearchService:
    """Constrói e retorna uma instância do SearchService."""
    return SearchService(
        anuncio_repo=anuncio_repo,
        cidade_repo=cidade_repo,
        imobiliaria_repo=imobiliaria_repo,
        embed_service=embedding_service,
        vector_index_client=get_vector_db_index()
    )