from pymongo import MongoClient
from typing import List, Optional, Dict, Any
from ..models import Article
from bson import ObjectId

class MongoDBRepository:
    def __init__(self, uri: str, db_name: str, client=None):
        self.client = client if client else MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db.articles

    def add_article(self, article: Article) -> str:
        article_dict = article.model_dump(exclude={'id'})
        result = self.collection.insert_one(article_dict)
        return str(result.inserted_id)

    def get_article_by_id(self, article_id: str) -> Optional[Article]:
        try:
            doc = self.collection.find_one({"_id": ObjectId(article_id)})
            if doc:
                doc["id"] = str(doc["_id"])
                del doc["_id"]
                return Article(**doc)
            return None
        except Exception:
            return None

    def get_all_articles(self) -> List[Article]:
        articles = []
        for doc in self.collection.find():
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            articles.append(Article(**doc))
        return articles

    def update_article(self, article_id: str, article: Article) -> bool:
        try:
            article_dict = article.model_dump(exclude={'id'})
            result = self.collection.update_one(
                {"_id": ObjectId(article_id)},
                {"$set": article_dict}
            )
            return result.modified_count > 0
        except Exception:
            return False

    def delete_article(self, article_id: str) -> bool:
        try:
            result = self.collection.delete_one({"_id": ObjectId(article_id)})
            return result.deleted_count > 0
        except Exception:
            return False
