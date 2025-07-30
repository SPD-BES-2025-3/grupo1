import pytest

class TestMainRoute:
    """Testes para a rota principal da API"""
    
    def test_root_endpoint(self, client):
        """Testa o endpoint raiz da API"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "SPD Imóveis API - Busca Semântica de Imóveis"
    
    def test_api_docs_available(self, client):
        """Testa se a documentação da API está disponível"""
        # FastAPI gera automaticamente docs em /docs
        response = client.get("/docs")
        assert response.status_code == 200
    
    def test_openapi_schema_available(self, client):
        """Testa se o schema OpenAPI está disponível"""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert data["info"]["title"] == "SPD Imóveis API"
        assert data["info"]["description"] == "API de busca semântica de imóveis"