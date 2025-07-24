from app.models import Article, City, State, mock_article
from app.repositories.mongo_repository import MongoDBRepository
import mongomock
import pytest
from bson import ObjectId
#from app.models import Article  # Adjust the import path to your project
#from app.repositories.mongodb_repository import MongoDBRepository  # Adjust path too

@pytest.fixture
def mock_db():
    client = mongomock.MongoClient()
    db_name = "test_db"
    return MongoDBRepository(uri="", db_name=db_name, client=client)

@pytest.fixture
def mock_article() -> Article:
    city = City(name="Goiânia", state=State.GO)
    article = Article(title="Test", content="Content", author="Author", city=city)
    return article

def test_add_article(mock_db):
    article = mock_article()
    inserted_id = mock_db.add_article(article)
    assert isinstance(inserted_id, str)
    assert mock_db.collection.find_one({"_id": ObjectId(inserted_id)}) is not None


def test_get_article_by_id(mock_db):
    article = mock_article()
    inserted_id = mock_db.add_article(article)
    found_article = mock_db.get_article_by_id(inserted_id)
    assert found_article is not None
    assert found_article.title == "Test"


def test_get_all_articles(mock_db):
    article = mock_article()
    mock_db.add_article(article)
    mock_db.add_article(article)
    articles = mock_db.get_all_articles()
    assert len(articles) == 2


def test_update_article(mock_db):
    article = mock_article()
    inserted_id = mock_db.add_article(article)
    updated_article = Article(title="New", content="New", author="New", city=article.city)
    success = mock_db.update_article(inserted_id, updated_article)
    assert success is True
    updated = mock_db.collection.find_one({"_id": ObjectId(inserted_id)})
    assert updated["title"] == "New"


def test_delete_article(mock_db):
    article = mock_article()
    inserted_id = mock_db.add_article(article)
    success = mock_db.delete_article(inserted_id)
    assert success is True
    assert mock_db.collection.find_one({"_id": ObjectId(inserted_id)}) is None
