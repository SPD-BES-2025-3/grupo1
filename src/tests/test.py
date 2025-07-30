import pytest
from bson import ObjectId
from unittest.mock import MagicMock # Usado para criar mocks

# Importe a classe que você quer testar
from app.services.search_service import SearchService

def test_buscar_similares_com_sucesso(mocker):
    """
    Testa o fluxo completo de busca, garantindo que a hidratação de dados
    ocorre corretamente.
    """
    mock_anuncio_repo = MagicMock()
    mock_cidade_repo = MagicMock()
    mock_imobiliaria_repo = MagicMock()
    mock_embedding_service = MagicMock()
    mock_vector_db = MagicMock()

    anuncio_id_1 = ObjectId()
    cidade_id_1 = ObjectId()
    imobiliaria_id_1 = ObjectId()

    mocker.patch.object(mock_embedding_service, 'gerar_vetor', return_value=[0.1, 0.2, 0.3])

    mock_vector_db.query.return_value = {
        'matches': [{'id': str(anuncio_id_1)}]
    }

    mock_anuncio_repo.find_by_ids.return_value = [
        {
            '_id': anuncio_id_1, 
            'titulo': 'Casa Teste', 
            'cidade_id': cidade_id_1, 
            'imobiliaria_id': imobiliaria_id_1
        }
    ]
    mock_cidade_repo.find_by_ids.return_value = [
        {'_id': cidade_id_1, 'nome': 'Morrinhos', 'estado': 'GO'}
    ]
    mock_imobiliaria_repo.find_by_ids.return_value = [
        {'_id': imobiliaria_id_1, 'nome': 'Imobiliária Teste'}
    ]

    search_service = SearchService(
        anuncio_repo=mock_anuncio_repo,
        cidade_repo=mock_cidade_repo,
        imobiliaria_repo=mock_imobiliaria_repo,
        embed_service=mock_embedding_service,
        vector_index_client=mock_vector_db
    )

    resultados = search_service.buscar_similares(consulta="casa com piscina", top_k=1)

    assert len(resultados) == 1
    
    primeiro_resultado = resultados[0]
    assert primeiro_resultado['titulo'] == 'Casa Teste'
    assert primeiro_resultado['cidade']['nome'] == 'Morrinhos'
    assert primeiro_resultado['imobiliaria']['nome'] == 'Imobiliária Teste'
    assert primeiro_resultado['id'] == str(anuncio_id_1)

    mock_embedding_service.gerar_vetor.assert_called_once_with("casa com piscina")
    mock_vector_db.query.assert_called_once()
    mock_anuncio_repo.find_by_ids.assert_called_once_with([str(anuncio_id_1)])
    mock_cidade_repo.find_by_ids.assert_called_once_with([cidade_id_1])
    mock_imobiliaria_repo.find_by_ids.assert_called_once_with([imobiliaria_id_1])

def test_buscar_similares_sem_resultados_vetoriais(mocker):
    """
    Testa o caso em que a busca vetorial não retorna nenhum resultado.
    """
    mock_vector_db = MagicMock()
    mock_vector_db.query.return_value = {'matches': []} # Nenhum resultado
    
    mock_anuncio_repo = MagicMock()
    mock_embedding_service = MagicMock()
    mocker.patch.object(mock_embedding_service, 'gerar_vetor', return_value=[0.1, 0.2, 0.3])
    
    search_service = SearchService(None, None, None, mock_embedding_service, mock_vector_db)

    resultados = search_service.buscar_similares(consulta="algo que nao existe")

    assert resultados == []
    mock_anuncio_repo.find_by_ids.assert_not_called()