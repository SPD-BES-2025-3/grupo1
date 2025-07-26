from pymongo import MongoClient
from typing import List, Optional

from app.repositories.cidade_repository import CidadeRepository
from ..models import Article, City
from bson import ObjectId

class ArticleWithCity(Article):
    city: City

class MongoDBRepository:
    def __init__(self, uri: str, db_name: str, client=None):
        self.client = client if client else MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db.articles
        self.city_repo = CidadeRepository(self.db)

    def add_article(self, article: Article, city: City) -> str:
        city_id = self.city_repo.find_or_create(city)
        article_dict = article.model_dump()
        article_dict["city_id"] = city_id   
        result = self.collection.insert_one(article_dict)
        return str(result.inserted_id)

    def get_article_by_id(self, article_id: str) -> Optional[ArticleWithCity]:
        try:
            doc = self.collection.find_one({"_id": ObjectId(article_id)})
            if doc:
                doc["_id"] = str(doc["_id"])
                doc["city_id"] = str(doc["city_id"])
                city = self.city_repo.find_one_by_id(doc["city_id"])
                doc["city"] = city.model_dump()
                doc["city"]["_id"] = str(doc["city_id"])
                return ArticleWithCity(**doc)
            return None
        except Exception as e:
            return None

    def get_all_articles(self) -> List[ArticleWithCity]:
        articles = []
        for doc in self.collection.find():
            doc["_id"] = str(doc["_id"])
            doc["city_id"] = str(doc["city_id"])
            city = self.city_repo.find_one_by_id(doc["city_id"])
            doc["city"] = city.model_dump()
            doc["city"]["_id"] = str(doc["city_id"])
            article = ArticleWithCity(**doc)
            articles.append(article)

        return articles

    def update_article(self, article_id: str, article: Article, city: City) -> bool:
        try:
            article_dict = article.model_dump()
            city_id = self.city_repo.find_or_create(city)
            article_dict["city_id"] = city_id   
            result = self.collection.update_one(
                {"_id": ObjectId(article_id)},
                {"$set": article_dict}
            )
            return result.modified_count > 0
        except Exception:
            return False

    def delete_article(self, article_id: str) -> bool:
        try:
            # 1. Find the article to get its city_id
            article = self.get_article_by_id(article_id)
            if not article:
                return False

            # 2. Delete the article
            result = self.collection.delete_one({"_id": ObjectId(article_id)})

            city = self.city_repo.find_one_by_id(article.city_id)
            if not city or not city.id:
                return result.deleted_count == 1

            # 3. Check if any other articles reference the same city
            other_articles = self.collection.find_one({"city_id": ObjectId(city.id)})
            if not other_articles:
                print(f"City {city.id} not referenced anymore, deleting...")
                # No other articles reference this city, delete the city
                self.city_repo.delete_one(city.id)

            return result.deleted_count == 1
        except Exception:
            return False