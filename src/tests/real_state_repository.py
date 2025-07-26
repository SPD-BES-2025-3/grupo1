import pytest
from unittest.mock import Mock
from bson import ObjectId
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult

from src.app.repositories.imobiliaria_repository import ImobiliariaRepository
from src.app.models import Real_Estate

class TestImobiliariaRepository:
    
    @pytest.fixture
    def mock_db(self):
        db = Mock()
        collection = Mock()
        db.__getitem__.return_value = collection
        return db, collection
    
    @pytest.fixture
    def repository(self, mock_db):
        db, collection = mock_db
        repo = ImobiliariaRepository(db)
        repo.collection = collection
        return repo, collection
    
    def test_get_all(self, repository):
        repo, collection = repository
        doc = {"_id": ObjectId(), "nome": "Imobiliária Teste", "telefone": "62919198379"}
        collection.find.return_value = [doc]
        
        result = repo.get_all()
        
        assert len(result) == 1
        assert result[0].nome == "Imobiliária Teste"
    
    def test_find_one_by_id_success(self, repository):
        repo, collection = repository
        doc = {"_id": ObjectId(), "nome": "Imobiliária Teste", "telefone": "62919198379"}
        collection.find_one.return_value = doc
        
        result = repo.find_one_by_id("ncuiqciqbw8g1273189hcui")
        
        assert result is not None
        assert result.nome == "Imobiliária Teste"
    
    def test_find_one_by_id_not_found(self, repository):
        repo, collection = repository
        collection.find_one.return_value = None
        
        result = repo.find_one_by_id("ncuiqciqbw8g1273189hcui")
        
        assert result is None
    
    def test_find_one_by_telefone(self, repository):
        repo, collection = repository
        doc = {"_id": ObjectId(), "nome": "Imobiliária Teste", "telefone": "62919198379"}
        collection.find_one.return_value = doc
        
        result = repo.find_one_by_telefone("62919198379")
        
        assert result is not None
        assert result.telefone == "62919198379"
    
    def test_find_one_by_nome(self, repository):
        repo, collection = repository
        doc = {"_id": ObjectId(), "nome": "Imobiliária Teste", "telefone": "62919198379"}
        collection.find_one.return_value = doc
        
        result = repo.find_one_by_nome("Imobiliária Teste")
        
        assert result is not None
        assert result.nome == "Imobiliária Teste"
    
    def test_create(self, repository):
        repo, collection = repository
        mock_result = Mock(spec=InsertOneResult)
        mock_result.inserted_id = ObjectId("ncuiqciqbw8g1273189hcui")
        collection.insert_one.return_value = mock_result
        
        real_estate = Real_Estate(nome="Nova Imobiliária", telefone="62888888888")
        result = repo.create(real_estate)
        
        assert result == "ncuiqciqbw8g1273189hcui"
    
    def test_find_or_create_finds_existing(self, repository):
        repo, collection = repository
        doc = {"_id": ObjectId("ncuiqciqbw8g1273189hcui"), "nome": "Imobiliária Teste", "telefone": "62919198379"}
        collection.find_one.return_value = doc
        
        real_estate = Real_Estate(nome="Imobiliária Teste", telefone="62919198379")
        result = repo.find_or_create(real_estate)
        
        assert result == "ncuiqciqbw8g1273189hcui"
    
    def test_find_or_create_creates_new(self, repository):
        repo, collection = repository
        collection.find_one.return_value = None
        mock_result = Mock(spec=InsertOneResult)
        mock_result.inserted_id = ObjectId("507f1f77bcf86cd799439012")
        collection.insert_one.return_value = mock_result
        
        real_estate = Real_Estate(nome="Nova Imobiliária", telefone="62888888888")
        result = repo.find_or_create(real_estate)
        
        assert result == "507f1f77bcf86cd799439012"
    
    def test_delete_one_success(self, repository):
        repo, collection = repository
        mock_result = Mock(spec=DeleteResult)
        mock_result.deleted_count = 1
        collection.delete_one.return_value = mock_result
        
        result = repo.delete_one("ncuiqciqbw8g1273189hcui")
        
        assert result is True
    
    def test_delete_one_failure(self, repository):
        repo, collection = repository
        mock_result = Mock(spec=DeleteResult)
        mock_result.deleted_count = 0
        collection.delete_one.return_value = mock_result
        
        result = repo.delete_one("ncuiqciqbw8g1273189hcui")
        
        assert result is False
    
    def test_update_one_success(self, repository):
        repo, collection = repository
        mock_result = Mock(spec=UpdateResult)
        mock_result.modified_count = 1
        collection.update_one.return_value = mock_result
        
        real_estate = Real_Estate(nome="Imobiliária Atualizada", telefone="62777777777")
        result = repo.update_one("ncuiqciqbw8g1273189hcui", real_estate)
        
        assert result is True
    
    def test_update_one_failure(self, repository):
        repo, collection = repository
        mock_result = Mock(spec=UpdateResult)
        mock_result.modified_count = 0
        collection.update_one.return_value = mock_result
        
        real_estate = Real_Estate(nome="Imobiliária Atualizada", telefone="62777777777")
        result = repo.update_one("ncuiqciqbw8g1273189hcui", real_estate)
        
        assert result is False