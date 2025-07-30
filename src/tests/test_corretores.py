import pytest
from unittest.mock import patch, Mock

class TestCorretoresRoutes:
    """Testes para as rotas de corretores"""
    
    @patch('src.app.routers.corretores.MongoRepository')
    def test_create_corretor_success(self, mock_mongo_class, client, sample_corretor):
        """Testa criação bem-sucedida de um corretor"""
        mock_mongo = Mock()
        mock_mongo.add_corretor.return_value = "507f1f77bcf86cd799439012"
        mock_mongo_class.return_value = mock_mongo
        
        response = client.post("/corretores/", json=sample_corretor)
        
        assert response.status_code == 200
        data = response.json()
        assert data["nome"] == sample_corretor["nome"]
        assert data["email"] == sample_corretor["email"]
        assert data["creci"] == sample_corretor["creci"]
        assert data["id"] == "507f1f77bcf86cd799439012"
        
        mock_mongo.add_corretor.assert_called_once()
    
    @patch('src.app.routers.corretores.MongoRepository')
    def test_read_corretores_success(self, mock_mongo_class, client, sample_corretor_in_db):
        """Testa listagem de corretores"""
        mock_mongo = Mock()
        mock_mongo.get_all_corretores.return_value = [sample_corretor_in_db]
        mock_mongo_class.return_value = mock_mongo
        
        response = client.get("/corretores/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == sample_corretor_in_db["id"]
        assert data[0]["nome"] == sample_corretor_in_db["nome"]
        assert data[0]["creci"] == sample_corretor_in_db["creci"]
    
    @patch('src.app.routers.corretores.MongoRepository')
    def test_read_corretor_by_id_success(self, mock_mongo_class, client, sample_corretor_in_db):
        """Testa busca de corretor por ID"""
        mock_mongo = Mock()
        mock_mongo.get_corretor_by_id.return_value = sample_corretor_in_db
        mock_mongo_class.return_value = mock_mongo
        
        corretor_id = sample_corretor_in_db["id"]
        response = client.get(f"/corretores/{corretor_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == corretor_id
        assert data["nome"] == sample_corretor_in_db["nome"]
    
    @patch('src.app.routers.corretores.MongoRepository')
    def test_read_corretor_by_id_not_found(self, mock_mongo_class, client):
        """Testa busca de corretor inexistente"""
        mock_mongo = Mock()
        mock_mongo.get_corretor_by_id.return_value = None
        mock_mongo_class.return_value = mock_mongo
        
        response = client.get("/corretores/507f1f77bcf86cd799439999")
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Corretor not found"
    
    @patch('src.app.routers.corretores.MongoRepository')
    def test_update_corretor_success(self, mock_mongo_class, client, sample_corretor, sample_corretor_in_db):
        """Testa atualização de corretor"""
        mock_mongo = Mock()
        mock_mongo.get_corretor_by_id.return_value = sample_corretor_in_db
        mock_mongo_class.return_value = mock_mongo
        
        corretor_id = sample_corretor_in_db["id"]
        updated_data = {**sample_corretor, "nome": "João Silva Atualizado"}
        response = client.put(f"/corretores/{corretor_id}", json=updated_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["nome"] == "João Silva Atualizado"
        assert data["id"] == corretor_id
        
        mock_mongo.update_corretor.assert_called_once()
    
    @patch('src.app.routers.corretores.MongoRepository')
    def test_update_corretor_not_found(self, mock_mongo_class, client, sample_corretor):
        """Testa atualização de corretor inexistente"""
        mock_mongo = Mock()
        mock_mongo.get_corretor_by_id.return_value = None
        mock_mongo_class.return_value = mock_mongo
        
        response = client.put("/corretores/507f1f77bcf86cd799439999", json=sample_corretor)
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Corretor not found"
    
    @patch('src.app.routers.corretores.MongoRepository')
    def test_delete_corretor_success(self, mock_mongo_class, client, sample_corretor_in_db):
        """Testa exclusão de corretor"""
        mock_mongo = Mock()
        mock_mongo.get_corretor_by_id.return_value = sample_corretor_in_db
        mock_mongo_class.return_value = mock_mongo
        
        corretor_id = sample_corretor_in_db["id"]
        response = client.delete(f"/corretores/{corretor_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Corretor deleted successfully"
        assert data["id"] == corretor_id
        
        mock_mongo.delete_corretor.assert_called_once_with(corretor_id)
    
    @patch('src.app.routers.corretores.MongoRepository')
    def test_delete_corretor_not_found(self, mock_mongo_class, client):
        """Testa exclusão de corretor inexistente"""
        mock_mongo = Mock()
        mock_mongo.get_corretor_by_id.return_value = None
        mock_mongo_class.return_value = mock_mongo
        
        response = client.delete("/corretores/507f1f77bcf86cd799439999")
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Corretor not found"
    
    def test_corretor_validation(self, client):
        """Testa validação de dados do corretor"""
        invalid_corretor = {
            "nome": "João Silva"
            # Faltam: email, telefone, creci
        }
        
        response = client.post("/corretores/", json=invalid_corretor)
        
        assert response.status_code == 422 