import chromadb
from typing import List, Dict, Any
from uuid import UUID

class ChromaRepository:
    def __init__(self, path: str = "./chroma_db"):
        self.client = chromadb.PersistentClient(path=path)
        self.collection = self.client.get_or_create_collection(name="articles")

    def add_documents(self, ids: List[str], documents: List[str], metadatas: List[Dict[str, Any]]):
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )

    def query(self, query_embeddings: List[List[float]], n_results: int = 5) -> List[Dict[str, Any]]:
        return self.collection.query(
            query_embeddings=query_embeddings,
            n_results=n_results
        )
