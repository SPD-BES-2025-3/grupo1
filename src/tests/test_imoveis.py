import pytest
from unittest.mock import patch, Mock

class TestImoveisRoutes:
    """Testes para as rotas de imóveis"""
    
    @patch('src.app.routers.imoveis.MongoRepository')
    @patch('src.app.routers.imoveis.MessageBrokerService')
    def test_create_imovel_success(self, mock_broker, mock_mongo_class, client, sample_imovel):
        """Testa criação bem-sucedida de um imóvel"""
        mock_mongo = Mock()
        mock_mongo.add_imovel.return_value = "507f1f77bcf86cd799439011"
        mock_mongo_class.return_value = mock_mongo
        
        mock_broker_instance = Mock()
        mock_broker.return_value = mock_broker_instance
        
        response = client.post("/imoveis/", json=sample_imovel)
        
        assert response.status_code == 200
        data = response.json()
        assert data["titulo"] == sample_imovel["titulo"]
        assert data["id"] == "507f1f77bcf86cd799439011"
        
        mock_mongo.add_imovel.assert_called_once()
        mock_broker_instance.publish_imovel_event.assert_called_once()
    
    @patch('src.app.routers.imoveis.MongoRepository')
    def test_read_imoveis_success(self, mock_mongo_class, client, sample_imovel_in_db):
        """Testa listagem de imóveis"""
        mock_mongo = Mock()
        mock_mongo.get_all_imoveis.return_value = [sample_imovel_in_db]
        mock_mongo_class.return_value = mock_mongo
        
        response = client.get("/imoveis/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == sample_imovel_in_db["id"]
        assert data[0]["titulo"] == sample_imovel_in_db["titulo"]
    
    @patch('src.app.routers.imoveis.MongoRepository')
    def test_read_imovel_by_id_success(self, mock_mongo_class, client, sample_imovel_in_db):
        """Testa busca de imóvel por ID"""
        mock_mongo = Mock()
        mock_mongo.get_imovel_by_id.return_value = sample_imovel_in_db
        mock_mongo_class.return_value = mock_mongo
        
        imovel_id = sample_imovel_in_db["id"]
        response = client.get(f"/imoveis/{imovel_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == imovel_id
        assert data["titulo"] == sample_imovel_in_db["titulo"]
    
    @patch('src.app.routers.imoveis.MongoRepository')
    def test_read_imovel_by_id_not_found(self, mock_mongo_class, client):
        """Testa busca de imóvel inexistente"""
        mock_mongo = Mock()
        mock_mongo.get_imovel_by_id.return_value = None
        mock_mongo_class.return_value = mock_mongo
        
        response = client.get("/imoveis/507f1f77bcf86cd799439999")
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Imovel not found"
    
    @patch('src.app.routers.imoveis.MongoRepository')
    @patch('src.app.routers.imoveis.MessageBrokerService')
    def test_update_imovel_success(self, mock_broker, mock_mongo_class, client, sample_imovel, sample_imovel_in_db):
        """Testa atualização de imóvel"""
        mock_mongo = Mock()
        mock_mongo.get_imovel_by_id.return_value = sample_imovel_in_db
        mock_mongo_class.return_value = mock_mongo
        
        mock_broker_instance = Mock()
        mock_broker.return_value = mock_broker_instance
        
        imovel_id = sample_imovel_in_db["id"]
        updated_data = {**sample_imovel, "titulo": "Apartamento Atualizado"}
        response = client.put(f"/imoveis/{imovel_id}", json=updated_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["titulo"] == "Apartamento Atualizado"
        assert data["id"] == imovel_id
        
        mock_mongo.update_imovel.assert_called_once()
        mock_broker_instance.publish_imovel_event.assert_called_once()
    
    @patch('src.app.routers.imoveis.MongoRepository')
    @patch('src.app.routers.imoveis.MessageBrokerService')
    def test_delete_imovel_success(self, mock_broker, mock_mongo_class, client, sample_imovel_in_db):
        """Testa exclusão de imóvel"""
        mock_mongo = Mock()
        mock_mongo.get_imovel_by_id.return_value = sample_imovel_in_db
        mock_mongo_class.return_value = mock_mongo
        
        mock_broker_instance = Mock()
        mock_broker.return_value = mock_broker_instance
        
        imovel_id = sample_imovel_in_db["id"]
        response = client.delete(f"/imoveis/{imovel_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Imovel deleted successfully"
        assert data["id"] == imovel_id
        
        mock_mongo.delete_imovel.assert_called_once_with(imovel_id)
        mock_broker_instance.publish_imovel_event.assert_called_once()
    
    @patch('src.app.routers.imoveis.MongoRepository')
    @patch('src.app.routers.imoveis.ChromaRepository')
    @patch('src.app.routers.imoveis.EmbeddingService')
    @patch('src.app.routers.imoveis.IndexingService')
    def test_sync_mongo_to_chroma(self, mock_indexing_class, mock_embedding_class, 
                                  mock_chroma_class, mock_mongo_class, client, sample_imovel_in_db):
        """Testa sincronização MongoDB -> ChromaDB"""
        mock_mongo = Mock()
        mock_mongo.get_all_imoveis.return_value = [sample_imovel_in_db]
        mock_mongo_class.return_value = mock_mongo
        
        mock_chroma = Mock()
        mock_chroma_class.return_value = mock_chroma
        
        mock_embedding = Mock()
        mock_embedding_class.return_value = mock_embedding
        
        mock_indexing = Mock()
        mock_indexing_class.return_value = mock_indexing
        
        response = client.post("/imoveis/sync")
        
        assert response.status_code == 200
        data = response.json()
        assert data["synced"] == 1
        assert data["total"] == 1
        assert "Sincronização concluída" in data["message"]