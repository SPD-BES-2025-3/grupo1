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
    # 1. Preparação dos Mocks (Simulando as dependências)
    mock_anuncio_repo = MagicMock()
    mock_cidade_repo = MagicMock()
    mock_imobiliaria_repo = MagicMock()
    mock_embedding_service = MagicMock()
    mock_vector_db = MagicMock()

    # IDs que usaremos para o teste
    anuncio_id_1 = ObjectId()
    cidade_id_1 = ObjectId()
    imobiliaria_id_1 = ObjectId()

    # 2. Configurando o comportamento dos Mocks
    # Simula o retorno do serviço de embedding
    mocker.patch.object(mock_embedding_service, 'gerar_vetor', return_value=[0.1, 0.2, 0.3])

    # Simula o retorno do banco de dados vetorial
    mock_vector_db.query.return_value = {
        'matches': [{'id': str(anuncio_id_1)}]
    }

    # Simula o retorno dos repositórios do MongoDB
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

    # 3. Instanciando o Serviço com os Mocks
    search_service = SearchService(
        anuncio_repo=mock_anuncio_repo,
        cidade_repo=mock_cidade_repo,
        imobiliaria_repo=mock_imobiliaria_repo,
        embed_service=mock_embedding_service,
        vector_index_client=mock_vector_db
    )

    # 4. Executando o método a ser testado
    resultados = search_service.buscar_similares(consulta="casa com piscina", top_k=1)

    # 5. Verificações (Asserts)
    # Verifica se o resultado não está vazio
    assert len(resultados) == 1
    
    # Verifica o conteúdo do resultado hidratado
    primeiro_resultado = resultados[0]
    assert primeiro_resultado['titulo'] == 'Casa Teste'
    assert primeiro_resultado['cidade']['nome'] == 'Morrinhos'
    assert primeiro_resultado['imobiliaria']['nome'] == 'Imobiliária Teste'
    assert primeiro_resultado['id'] == str(anuncio_id_1)

    # Verifica se os mocks foram chamados como esperado
    mock_embedding_service.gerar_vetor.assert_called_once_with("casa com piscina")
    mock_vector_db.query.assert_called_once()
    mock_anuncio_repo.find_by_ids.assert_called_once_with([str(anuncio_id_1)])
    mock_cidade_repo.find_by_ids.assert_called_once_with([cidade_id_1])
    mock_imobiliaria_repo.find_by_ids.assert_called_once_with([imobiliaria_id_1])

def test_buscar_similares_sem_resultados_vetoriais(mocker):
    """
    Testa o caso em que a busca vetorial não retorna nenhum resultado.
    """
    # Preparação
    mock_vector_db = MagicMock()
    mock_vector_db.query.return_value = {'matches': []} # Nenhum resultado
    
    # ... mocks vazios para os outros componentes
    mock_anuncio_repo = MagicMock()
    mock_embedding_service = MagicMock()
    mocker.patch.object(mock_embedding_service, 'gerar_vetor', return_value=[0.1, 0.2, 0.3])
    
    search_service = SearchService(None, None, None, mock_embedding_service, mock_vector_db)

    # Execução
    resultados = search_service.buscar_similares(consulta="algo que nao existe")

    # Verificação
    assert resultados == []
    # Garante que o serviço parou e não tentou buscar no MongoDB
    mock_anuncio_repo.find_by_ids.assert_not_called()