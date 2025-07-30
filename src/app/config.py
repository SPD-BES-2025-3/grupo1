import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_CONNECTION_STRING", "mongodb://localhost:27017/")
MONGO_DB_NAME = os.getenv("MONGO_DATABASE_NAME", "spd_imoveis")

CHROMA_HOST = os.getenv("CHROMA_HOST", "localhost")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "7777"))
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "imoveis")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")

API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

DEBUG = os.getenv("DEBUG", "True").lower() == "true"
