from fastapi import APIRouter, Depends, HTTPException
from typing import List

from app.repositories.mongo_repository import ArticleWithCity
from ..models import Article, City
from ..database import get_mongo_repo, get_chroma_repo
from ..services.indexing_service import IndexingService
from ..services.embedding_service import EmbeddingService

router = APIRouter()

# Dependência para o repositório
def get_repository():
    # Conexão com o MongoDB
    # Substitua com suas configurações
    return get_mongo_repo()

@router.post("/articles/index")
def index_articles(mongo_repo: any = Depends(get_mongo_repo), chroma_repo: any = Depends(get_chroma_repo)):
    articles = mongo_repo.get_all_articles()
    if not articles:
        raise HTTPException(status_code=404, detail="No articles found to index")

    embedding_service = EmbeddingService()
    indexing_service = IndexingService(embedding_service=embedding_service, chroma_repo=chroma_repo)
    indexing_service.index_articles(articles)

    return {"message": "Articles indexed successfully"}

@router.post("/articles/", response_model=Article)
def create_article(article: ArticleWithCity, repo: any = Depends(get_repository)):
    repo.add_article(article, article.city)
    return article

@router.get("/articles/", response_model=List[ArticleWithCity])
def read_articles(repo: any = Depends(get_repository)):
    return repo.get_all_articles()

@router.get("/articles/{article_id}", response_model=Article)
def read_article(article_id: str, repo: any = Depends(get_repository)):
    db_article = repo.get_article_by_id(article_id)
    if db_article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return db_article

@router.put("/articles/{article_id}", response_model=Article)
def update_article(article_id: str, article: Article, repo: any = Depends(get_repository)):
    db_article = repo.get_article_by_id(article_id)
    if db_article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    repo.update_article(article_id, article)
    return article

@router.delete("/articles/{article_id}", response_model=Article)
def delete_article(article_id: str, repo: any = Depends(get_repository)):
    db_article = repo.get_article_by_id(article_id)
    if db_article is None:
        raise HTTPException(status_code=404, detail="Article not found")
    return db_article
