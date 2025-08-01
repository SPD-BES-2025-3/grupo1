import chromadb
from typing import List, Dict, Any
from uuid import UUID

class ChromaRepository:
    def __init__(self, path: str = None, host: str = None, port: int = None):
        if host and port:
            # Usar ChromaDB via HTTP
            self.client = chromadb.HttpClient(host=host, port=port)
        else:
            # Usar ChromaDB local
            self.client = chromadb.PersistentClient(path=path or "./chroma_db")
        self.collection = self.client.get_or_create_collection(name="imoveis")

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
    
    def update_document(self, id: str, document: str, metadata: Dict[str, Any]):
        """Atualiza um documento existente"""
        self.collection.update(
            ids=[id],
            documents=[document],
            metadatas=[metadata]
        )
    
    def delete_document(self, id: str):
        """Remove um documento do ChromaDB"""
        self.collection.delete(ids=[id])
    
    def upsert_documents(self, ids: List[str], documents: List[str], metadatas: List[Dict[str, Any]]):
        """Insere ou atualiza documentos"""
        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
