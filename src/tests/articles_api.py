import pytest
from fastapi.testclient import TestClient
from fastapi import status
from main import app  # Your main FastAPI app instance
from app.models import Article
from app.routers.articles import router, get_repository
from unittest.mock import MagicMock
from app.database import get_chroma_repo, get_mongo_repo

# Mount the router for isolated testing if needed
app.include_router(router)

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def fake_article():
    return Article(title="Test", content="Something", author="Me")

@pytest.fixture
def mock_repo(fake_article):
    mock = MagicMock()
    mock.get_all_articles.return_value = [fake_article]
    mock.get_article_by_id.return_value = fake_article
    mock.add_article.return_value = "123"
    mock.update_article.return_value = True
    mock.delete_article.return_value = True
    return mock

@pytest.fixture
def mock_chroma_repo():
    return MagicMock()

# Override dependencies
@pytest.fixture(autouse=True)
def override_dependencies(mock_repo, mock_chroma_repo):
    app.dependency_overrides[get_mongo_repo] = lambda: mock_repo
    app.dependency_overrides[get_chroma_repo] = lambda: mock_chroma_repo
    app.dependency_overrides[get_repository] = lambda: mock_repo
    yield
    app.dependency_overrides = {}

def test_create_article(client, fake_article):
    response = client.post("/articles/", json=fake_article.dict())
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == "Test"

def test_read_articles(client):
    response = client.get("/articles/")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)

def test_read_article(client):
    response = client.get("/articles/123")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["title"] == "Test"

def test_update_article(client, fake_article):
    response = client.put("/articles/123", json=fake_article.dict())
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["content"] == "Something"

def test_delete_article(client):
    response = client.delete("/articles/123")
    assert response.status_code == status.HTTP_200_OK

def test_index_articles(client):
    response = client.post("/articles/index")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Articles indexed successfully"
