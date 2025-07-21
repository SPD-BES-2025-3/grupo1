from fastapi import APIRouter, Depends, status, HTTPException
from typing import Annotated

# Importe os modelos e serviços
from ..models import AnuncioSchema, AnuncioInDB # Supondo que você tem esses modelos
from ..services.indexing_service import IndexingService
from .dependencies import get_indexing_service

router = APIRouter(
    prefix="/api/anuncios", # Prefixo para todos os endpoints neste arquivo
    tags=["Anúncios"]        # Agrupa os endpoints na documentação do Swagger
)

@router.post("/", response_model=AnuncioInDB, status_code=status.HTTP_201_CREATED)
def create_anuncio(
    anuncio_data: AnuncioSchema,
    indexing_service: Annotated[IndexingService, Depends(get_indexing_service)]
):
    """
    Cria um novo anúncio de imóvel.

    Este endpoint recebe os dados de um anúncio, o salva no MongoDB,
    gera seu embedding vetorial e o indexa para busca semântica.
    """
    try:
        # O serviço de indexação faz todo o trabalho pesado
        # Supondo que o serviço retorna o documento criado com o ID
        anuncio_criado = indexing_service.indexar_documento(anuncio_data)
        return anuncio_criado
    except Exception as e:
        # Tratamento de erro genérico
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocorreu um erro ao indexar o anúncio: {e}"
        )