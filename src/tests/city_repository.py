import mongomock
import pytest
from bson import ObjectId
from pymongo.collection import Collection
from pymongo.database import Database
from app.repositories.cidade_repository import CidadeRepository
from app.models import City, State
from unittest.mock import MagicMock

@pytest.fixture
def mock_db():
    client = mongomock.MongoClient()
    db = client["test_db"]
    return CidadeRepository(db)

@pytest.fixture
def mock_city() -> City:
    return City(name="Goiânia", state=State.GO)

def test_create_city(mock_db, mock_city):
    inserted_id = mock_db.create(mock_city)
    assert isinstance(inserted_id, ObjectId)
    stored = mock_db.collection.find_one({"_id": inserted_id})
    assert stored is not None
    assert stored["name"] == "Goiânia"

def test_find_one_by_id_found(mock_db, mock_city):
    inserted_id = mock_db.create(mock_city)
    found = mock_db.find_one_by_id(str(inserted_id))
    assert found is not None
    assert found.name == "Goiânia"

def test_find_one_by_id_not_found(mock_db):
    fake_id = str(ObjectId())
    found = mock_db.find_one_by_id(fake_id)
    assert found is None

def test_find_one_by_name_found(mock_db, mock_city):
    inserted_id = mock_db.create(mock_city)
    found_city, found_id = mock_db.find_one_by_name("Goiânia", State.GO)
    assert found_city is not None
    assert found_city.name == "Goiânia"
    assert found_id == inserted_id

def test_find_one_by_name_not_found(mock_db):
    city, city_id = mock_db.find_one_by_name("Cidade Fantasma", State.SP)
    assert city is None
    assert city_id is None

def test_find_or_create_existing_city(mock_db, mock_city):
    inserted_id = mock_db.create(mock_city)
    found_id = mock_db.find_or_create(mock_city)
    assert found_id == inserted_id

def test_find_or_create_new_city(mock_db):
    new_city = City(name="Nova Cidade", state=State.MT)
    found_id = mock_db.find_or_create(new_city)
    assert isinstance(found_id, ObjectId)
    doc = mock_db.collection.find_one({"_id": found_id})
    assert doc["name"] == "Nova Cidade"

def test_find_by_ids(mock_db):
    city1 = City(name="Recife", state=State.PE)
    city2 = City(name="Salvador", state=State.BA)

    id1 = mock_db.create(city1)
    id2 = mock_db.create(city2)

    result = mock_db.find_by_ids([id1, id2])
    assert len(result) == 2
    names = [c.name for c in result]
    assert "Recife" in names
    assert "Salvador" in names
