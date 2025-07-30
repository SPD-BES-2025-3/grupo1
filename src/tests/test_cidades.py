import pytest
from unittest.mock import patch, Mock

class TestCidadesRoutes:
    """Testes para as rotas de cidades"""
    
    @patch('src.app.routers.cidades.MongoRepository')
    def test_create_cidade_success(self, mock_mongo_class, client, sample_cidade):
        """Testa criação bem-sucedida de uma cidade"""

        mock_mongo = Mock()
        mock_mongo.add_cidade.return_value = "507f1f77bcf86cd799439013"
        mock_mongo_class.return_value = mock_mongo
        
        response = client.post("/cidades/", json=sample_cidade)
        
        assert response.status_code == 200
        data = response.json()
        assert data["nome"] == sample_cidade["nome"]
        assert data["estado"] == sample_cidade["estado"]
        assert data["regiao"] == sample_cidade["regiao"]
        assert data["id"] == "507f1f77bcf86cd799439013"
        
        mock_mongo.add_cidade.assert_called_once()
    
    @patch('src.app.routers.cidades.MongoRepository')
    def test_read_cidades_success(self, mock_mongo_class, client, sample_cidade_in_db):
        """Testa listagem de cidades"""
        mock_mongo = Mock()
        mock_mongo.get_all_cidades.return_value = [sample_cidade_in_db]
        mock_mongo_class.return_value = mock_mongo
    
        response = client.get("/cidades/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == sample_cidade_in_db["id"]
        assert data[0]["nome"] == sample_cidade_in_db["nome"]
        assert data[0]["estado"] == sample_cidade_in_db["estado"]
    
    @patch('src.app.routers.cidades.MongoRepository')
    def test_read_cidade_by_id_success(self, mock_mongo_class, client, sample_cidade_in_db):
        """Testa busca de cidade por ID"""
        
        mock_mongo = Mock()
        mock_mongo.get_cidade_by_id.return_value = sample_cidade_in_db
        mock_mongo_class.return_value = mock_mongo
        
        cidade_id = sample_cidade_in_db["id"]
        response = client.get(f"/cidades/{cidade_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == cidade_id
        assert data["nome"] == sample_cidade_in_db["nome"]
        assert data["estado"] == sample_cidade_in_db["estado"]
    
    @patch('src.app.routers.cidades.MongoRepository')
    def test_read_cidade_by_id_not_found(self, mock_mongo_class, client):
        """Testa busca de cidade inexistente"""
        mock_mongo = Mock()
        mock_mongo.get_cidade_by_id.return_value = None
        mock_mongo_class.return_value = mock_mongo
        
        response = client.get("/cidades/507f1f77bcf86cd799439999")
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Cidade not found"
    
    @patch('src.app.routers.cidades.MongoRepository')
    def test_update_cidade_success(self, mock_mongo_class, client, sample_cidade, sample_cidade_in_db):
        """Testa atualização de cidade"""
        mock_mongo = Mock()
        mock_mongo.get_cidade_by_id.return_value = sample_cidade_in_db
        mock_mongo_class.return_value = mock_mongo
        
        cidade_id = sample_cidade_in_db["id"]
        updated_data = {**sample_cidade, "populacao": 1600000}
        response = client.put(f"/cidades/{cidade_id}", json=updated_data)

        assert response.status_code == 200
        data = response.json()
        assert data["populacao"] == 1600000
        assert data["id"] == cidade_id
        
        mock_mongo.update_cidade.assert_called_once()
    
    @patch('src.app.routers.cidades.MongoRepository')
    def test_delete_cidade_success(self, mock_mongo_class, client, sample_cidade_in_db):
        """Testa exclusão de cidade"""
        mock_mongo = Mock()
        mock_mongo.get_cidade_by_id.return_value = sample_cidade_in_db
        mock_mongo_class.return_value = mock_mongo
        
        cidade_id = sample_cidade_in_db["id"]
        response = client.delete(f"/cidades/{cidade_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Cidade deleted successfully"
        assert data["id"] == cidade_id
        
        mock_mongo.delete_cidade.assert_called_once_with(cidade_id)
    
    @patch('src.app.routers.cidades.MongoRepository')
    def test_read_cidades_by_estado_success(self, mock_mongo_class, client, sample_cidade_in_db):
        """Testa busca de cidades por estado"""
        mock_mongo = Mock()
        mock_mongo.get_all_cidades.return_value = [
            sample_cidade_in_db,
            {
                "id": "507f1f77bcf86cd799439014",
                "nome": "Anápolis",
                "estado": "GO",
                "regiao": "Centro-Oeste"
            },
            {
                "id": "507f1f77bcf86cd799439015",
                "nome": "São Paulo",
                "estado": "SP",
                "regiao": "Sudeste"
            }
        ]
        mock_mongo_class.return_value = mock_mongo
        
        response = client.get("/cidades/estado/GO")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2 
        assert all(cidade["estado"] == "GO" for cidade in data)
        assert data[0]["nome"] == "Goiânia"
        assert data[1]["nome"] == "Anápolis"
    
    @patch('src.app.routers.cidades.MongoRepository')
    def test_read_cidades_by_estado_empty(self, mock_mongo_class, client):
        """Testa busca de cidades por estado sem resultados"""
        mock_mongo = Mock()
        mock_mongo.get_all_cidades.return_value = [
            {
                "id": "507f1f77bcf86cd799439015",
                "nome": "São Paulo",
                "estado": "SP",
                "regiao": "Sudeste"
            }
        ]
        mock_mongo_class.return_value = mock_mongo
        
        response = client.get("/cidades/estado/AC")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
    
    def test_cidade_validation(self, client):
        """Testa validação de dados da cidade"""
        invalid_cidade = {
            "nome": "Goiânia"

        }
        
        response = client.post("/cidades/", json=invalid_cidade)
        
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_cidade_minimal_data(self, client):
        """Testa criação de cidade com dados mínimos"""
        minimal_cidade = {
            "nome": "Aparecida de Goiânia",
            "estado": "GO"
        }
        
        with patch('src.app.routers.cidades.MongoRepository') as mock_mongo_class:
            mock_mongo = Mock()
            mock_mongo.add_cidade.return_value = "507f1f77bcf86cd799439016"
            mock_mongo_class.return_value = mock_mongo
            
            response = client.post("/cidades/", json=minimal_cidade)
            
            assert response.status_code == 200
            data = response.json()
            assert data["nome"] == minimal_cidade["nome"]
            assert data["estado"] == minimal_cidade["estado"]