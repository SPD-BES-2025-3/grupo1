import chromadb
from typing import List, Dict, Any


class ChromaRepository:
    def __init__(self, path: str = None, host: str = None, port: int = None):
        if host and port:
            print(f"Conectando ChromaDB via HTTP: {host}:{port}")
            try:
                self.client = chromadb.HttpClient(host=host, port=port)
            except Exception as e:
                print(f"Erro com HttpClient padrão: {e}")
                import chromadb.config
                settings = chromadb.config.Settings()
                settings.chroma_api_impl = "chromadb.api.fastapi.FastAPI"
                settings.chroma_server_host = host
                settings.chroma_server_http_port = port
                self.client = chromadb.Client(settings)
        else:
            print(f"Conectando ChromaDB local: {path or './chroma_db'}")
            self.client = chromadb.PersistentClient(path=path or "./chroma_db")

        print("Collection selecionada: imoveis (usando get_or_create_collection)")
        self.collection = self.client.get_or_create_collection(name="imoveis")

    def add_documents(self, ids: List[str], documents: List[str], metadatas: List[Dict[str, Any]], embeddings: List[List[float]] = None):
        if embeddings:
            print(f"ChromaRepository Debug - Recebendo embeddings: {type(embeddings)}")
            print(f"ChromaRepository Debug - Tamanho embeddings: {len(embeddings)}")
            if embeddings and len(embeddings) > 0:
                print(f"ChromaRepository Debug - Tipo primeiro embedding: {type(embeddings[0])}")
                print(f"ChromaRepository Debug - Dimensões primeiro embedding: {len(embeddings[0]) if hasattr(embeddings[0], '__len__') else 'N/A'}")
                print(f"ChromaRepository Debug - Primeiros 3 valores: {embeddings[0][:3] if hasattr(embeddings[0], '__getitem__') else 'N/A'}")
            
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings
            )
            print(f"ChromaRepository Debug - add() chamado com sucesso")
        else:
            print(f"ChromaRepository Debug - Sem embeddings, usando auto-embedding")
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
    
    def upsert_documents(self, ids: List[str], documents: List[str], metadatas: List[Dict[str, Any]], embeddings: List[List[float]] = None):
        """Insere ou atualiza documentos"""
        if embeddings:
            self.collection.upsert(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings
            )
        else:
            self.collection.upsert(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
