#Aqui ficam as configurações e variáveis de ambiente da app
import os

# Use localhost when running server locally, mongodb when running in Docker
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_URI = f"mongodb://{MONGO_HOST}:27017/"
MONGO_DB_NAME = "articles_db"
CHROMA_DB_PATH = "./chroma_db"
