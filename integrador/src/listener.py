import redis
import json
import sys
import os

# app/ ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from app.repositories.mongo_repository import MongoRepository
from app.repositories.chroma_repository import ChromaRepository
from app.services.embedding_service import EmbeddingService


class RedisListener:
    def __init__(self):
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        redis_host = redis_url.split("://")[1].split(":")[0]
        redis_port = int(redis_url.split(":")[-1])
        
        self.redis = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe('imoveis.create', 'imoveis.update', 'imoveis.delete')

        MONGO_URI = os.getenv("MONGO_CONNECTION_STRING", "mongodb://localhost:27017/")
        MONGO_DB_NAME = os.getenv("MONGO_DATABASE_NAME", "spd_imoveis")
        self.mongo = MongoRepository(MONGO_URI, MONGO_DB_NAME)
        
        chroma_host = os.getenv("CHROMA_HOST", "chromadb")
        chroma_port = int(os.getenv("CHROMA_PORT", "7777"))
        self.chroma = ChromaRepository(host=chroma_host, port=chroma_port)
        
        self.embedding_service = EmbeddingService()

    def listen(self):
        print("Aguardando eventos Redis...")
        for message in self.pubsub.listen():
            if message['type'] != 'message':
                continue

            channel = message['channel']
            data = json.loads(message['data'])
            imovel_id = data.get('_id')
            print(f"Evento recebido: {channel} com ID {imovel_id}")

            try:
                self.process_event(channel, data, imovel_id)
            except Exception as e:
                print(f"Erro ao processar evento: {e}")


    def process_event(self, channel, data, imovel_id):
        if 'create' in channel:
            titulo = data.get('titulo', '')
            descricao = data.get('descricao', '')
            especificacoes = data.get('especificacoes', [])
            if isinstance(especificacoes, list):
                especificacoes_str = ' '.join(especificacoes)
            else:
                especificacoes_str = str(especificacoes)
            
            content = f"{titulo} {descricao} {especificacoes_str}"
            
            embeddings = self.embedding_service.create_embeddings([content])
            print(f"Debug - Tipo embeddings: {type(embeddings)}")
            print(f"Debug - Tamanho embeddings: {len(embeddings) if embeddings else 0}")
            if embeddings and len(embeddings) > 0:
                print(f"Debug - Dimensões embedding[0]: {len(embeddings[0]) if hasattr(embeddings[0], '__len__') else 'N/A'}")
            
            # Metadata compatível com ChromaDB
            metadata = {
                "id": imovel_id,
                "titulo": titulo,
                "descricao": descricao,
                "especificacoes": " | ".join(especificacoes) if isinstance(especificacoes, list) else str(especificacoes)
            }
            
            print(f"Debug - Chamando add_documents com embeddings: {embeddings is not None}")
            print(f"Debug - Embeddings detalhado: Tipo={type(embeddings)}, Len={len(embeddings) if embeddings else 0}")
            if embeddings and len(embeddings) > 0:
                print(f"Debug - Primeiro embedding: Tipo={type(embeddings[0])}, Len={len(embeddings[0]) if hasattr(embeddings[0], '__len__') else 'N/A'}")
                print(f"Debug - Amostra valores: {embeddings[0][:3] if hasattr(embeddings[0], '__getitem__') else 'N/A'}")
            
            try:
                self.chroma.add_documents([imovel_id], [content], [metadata], embeddings)
                print(f"Debug - add_documents executado com sucesso")
            except Exception as e:
                print(f"Debug - Erro em add_documents: {e}")
                print(f"Debug - Tipo do erro: {type(e)}")
                import traceback
                traceback.print_exc()
        elif 'update' in channel:
            titulo = data.get('titulo', '')
            descricao = data.get('descricao', '')
            especificacoes = data.get('especificacoes', [])
            if isinstance(especificacoes, list):
                especificacoes_str = ' '.join(especificacoes)
            else:
                especificacoes_str = str(especificacoes)
            
            content = f"{titulo} {descricao} {especificacoes_str}"
            
            # Criar embedding para update
            embeddings = self.embedding_service.create_embeddings([content])
            
            metadata = {
                "id": imovel_id,
                "titulo": titulo,
                "descricao": descricao,
                "especificacoes": " | ".join(especificacoes) if isinstance(especificacoes, list) else str(especificacoes)
            }
            
            self.chroma.upsert_documents([imovel_id], [content], [metadata], embeddings)
        elif 'delete' in channel:
            self.chroma.delete_document(imovel_id)
        else:
            print(f"Evento desconhecido: {channel}")
