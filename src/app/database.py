from .repositories.mongo_repository import MongoRepository
from .repositories.chroma_repository import ChromaRepository
from .config import MONGO_URI, MONGO_DB_NAME, CHROMA_HOST, CHROMA_PORT

def get_mongo_repo():
    return MongoRepository(uri=MONGO_URI, db_name=MONGO_DB_NAME)

def get_chroma_repo():
    return ChromaRepository(path="./chroma_db")
