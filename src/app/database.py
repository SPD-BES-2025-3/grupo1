from pymongo import MongoClient
from app.repositories.cidade_repository import CidadeRepository
from .repositories.mongo_repository import MongoDBRepository
from .repositories.chroma_repository import ChromaRepository
from .config import MONGO_URI, MONGO_DB_NAME, CHROMA_DB_PATH

def get_mongo_repo():
    return MongoDBRepository(uri=MONGO_URI, db_name=MONGO_DB_NAME)

def get_chroma_repo():
    return ChromaRepository(path=CHROMA_DB_PATH)

def get_city_repo(uri=MONGO_URI, db_name=MONGO_DB_NAME):
    client =  MongoClient(uri)
    db = client[db_name]
    return CidadeRepository(db)