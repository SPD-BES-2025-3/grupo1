import pytest
from unittest.mock import patch, Mock

class TestSearchRoutes:
    """Testes para as rotas de busca"""
    
    def test_search_test_endpoint(self, client):
        """Testa o endpoint de teste da busca"""
        response = client.get("/search-test")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Search endpoint is working"
        assert data["test"] is True
    
    @patch('src.app.routers.search.MongoRepository')
    @patch('src.app.routers.search.ChromaRepository')
    @patch('src.app.routers.search.SearchService')
    def test_search_imoveis_success(self, mock_search_class, mock_chroma_class, 
                                   mock_mongo_class, client, sample_imovel_in_db):
        """Testa busca semântica de imóveis"""
        # Configurar mocks
        mock_mongo = Mock()
        mock_mongo_class.return_value = mock_mongo
        
        mock_chroma = Mock()
        mock_chroma_class.return_value = mock_chroma
        
        mock_search = Mock()
        mock_search.search.return_value = {
            "results": [sample_imovel_in_db],
            "metadata": {
                "query": "casa com piscina",
                "total_results": 1
            }
        }
        mock_search_class.return_value = mock_search
        
        # Fazer requisição
        response = client.get("/search/?query=casa com piscina&n_results=5")
        
        # Verificações
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert len(data["results"]) == 1
        assert data["results"][0]["id"] == sample_imovel_in_db["id"]
    
    @patch('src.app.routers.search.MongoRepository')
    @patch('src.app.routers.search.ChromaRepository')
    @patch('src.app.routers.search.SearchService')
    def test_search_imoveis_no_results(self, mock_search_class, mock_chroma_class, 
                                      mock_mongo_class, client):
        """Testa busca sem resultados"""
        # Configurar mocks
        mock_mongo = Mock()
        mock_mongo_class.return_value = mock_mongo
        
        mock_chroma = Mock()
        mock_chroma_class.return_value = mock_chroma
        
        mock_search = Mock()
        mock_search.search.return_value = {
            "results": [],
            "metadata": {
                "query": "castelo medieval",
                "total_results": 0
            }
        }
        mock_search_class.return_value = mock_search
        
        # Fazer requisição
        response = client.get("/search/?query=castelo medieval")
        
        # Verificações
        assert response.status_code == 200
        data = response.json()
        assert data["results"] == []
        assert data["metadata"]["total_results"] == 0
    
    @patch('src.app.routers.search.LLMRerankingService')
    def test_rerank_with_feedback_success(self, mock_llm_class, client, sample_imovel_in_db):
        """Testa re-ranking com feedback do usuário"""
        # Configurar mock
        mock_llm = Mock()
        mock_llm.rerank_properties.return_value = {
            "decision_reasoning": "Selecionei imóveis similares aos curtidos",
            "should_show_more": True,
            "selected_properties": [
                {"id": "507f1f77bcf86cd799439014", "reason": "Similar ao que foi curtido"}
            ]
        }
        mock_llm_class.return_value = mock_llm
        
        # Dados da requisição
        rerank_data = {
            "query": "apartamento 3 quartos",
            "liked_properties": [sample_imovel_in_db],
            "disliked_properties": [],
            "remaining_properties": [
                {
                    "id": "507f1f77bcf86cd799439014",
                    "titulo": "Apartamento no Setor Marista",
                    "descricao": "Apartamento com 3 quartos",
                    "especificacoes": ["3 quartos", "2 vagas"]
                }
            ]
        }
        
        # Fazer requisição
        response = client.post("/rerank/", json=rerank_data)
        
        # Verificações
        assert response.status_code == 200
        data = response.json()
        assert "decision_reasoning" in data
        assert "selected_properties" in data
        assert len(data["selected_properties"]) == 1
        assert data["selected_properties"][0]["id"] == "507f1f77bcf86cd799439014"
    
    @patch('src.app.routers.search.LLMRerankingService')
    def test_rerank_with_llm_failure(self, mock_llm_class, client, sample_imovel_in_db):
        """Testa re-ranking quando LLM falha (usa fallback)"""
        # Configurar mock para simular falha
        mock_llm = Mock()
        mock_llm.rerank_properties.return_value = {
            "decision_reasoning": "IA não configurada - usando seleção automática",
            "should_show_more": True,
            "selected_properties": [
                {"id": "507f1f77bcf86cd799439014", "reason": "Fallback conservador - LLM indisponível"}
            ]
        }
        mock_llm_class.return_value = mock_llm
        
        # Dados da requisição
        rerank_data = {
            "query": "casa com piscina",
            "liked_properties": [],
            "disliked_properties": [],
            "remaining_properties": [
                {
                    "id": "507f1f77bcf86cd799439014",
                    "titulo": "Casa no Alphaville",
                    "descricao": "Casa com piscina",
                    "especificacoes": ["4 quartos", "piscina"]
                }
            ]
        }
        
        # Fazer requisição
        response = client.post("/rerank/", json=rerank_data)
        
        # Verificações
        assert response.status_code == 200
        data = response.json()
        assert "Fallback" in data["selected_properties"][0]["reason"] or "IA não configurada" in data["decision_reasoning"]