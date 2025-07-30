#!/usr/bin/env python3
"""
Worker único sincronizado para CREATE apenas
"""
import sys
import os
import time
import redis
import json
from datetime import datetime

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from app.services.embedding_service import EmbeddingService
from app.services.indexing_service import IndexingService
from app.repositories.chroma_repository import ChromaRepository
from app.repositories.mongo_repository import MongoRepository
from app.models import ImovelInDB
from app.config import MONGO_URI, MONGO_DB_NAME, REDIS_URL
from bson import ObjectId

class SingleWorker:
    def __init__(self):
        # Parse Redis URL
        redis_url = REDIS_URL or "redis://localhost:6379"
        if redis_url.startswith("redis://"):
            redis_url = redis_url[8:]  # Remove redis://
        host, port = redis_url.split(":")
        self.redis_client = redis.Redis(host=host, port=int(port), decode_responses=True)
        self.redis_host = host
        self.redis_port = port
        self.embedding_service = EmbeddingService()
        self.chroma_repo = ChromaRepository(path="./chroma_db")
        self.mongo_repo = MongoRepository(uri=MONGO_URI, db_name=MONGO_DB_NAME)
        self.indexing_service = IndexingService(
            embedding_service=self.embedding_service,
            chroma_repo=self.chroma_repo
        )
        
    def run(self):
        print(f"🚀 Worker único iniciado - Redis: {self.redis_host}:{self.redis_port}")
        print("📋 Processando CREATE, UPDATE e DELETE")
        
        # Testar conexões
        try:
            self.redis_client.ping()
            print(f"✅ Redis conectado em {self.redis_host}:{self.redis_port}")
        except Exception as e:
            print(f"❌ Erro Redis: {e}")
            return
            
        try:
            self.mongo_repo.get_all_imoveis()
            print("✅ MongoDB conectado")
        except Exception as e:
            print(f"❌ Erro MongoDB: {e}")
            return
        
        queues = ["imovel_created_queue", "imovel_updated_queue", "imovel_deleted_queue"]
        print(f"🔍 Aguardando mensagens em: {', '.join(queues)}")
        
        while True:
            try:
                # Processar qualquer uma das 3 filas
                result = self.redis_client.brpop(queues, timeout=5)
                if result:
                    queue_name, message = result
                    data = json.loads(message)
                    
                    event = data.get("event", "unknown")
                    imovel_id = data.get("id")
                    
                    if event == "imovel_created":
                        print(f"📥 [CREATE] Processando imóvel {imovel_id}")
                        
                        # Buscar dados do MongoDB
                        imovel_data = self.mongo_repo.get_imovel_by_id(imovel_id)
                        if imovel_data:
                            imovel = ImovelInDB(
                                id=imovel_id, 
                                titulo=imovel_data["titulo"],
                                descricao=imovel_data["descricao"],
                                especificacoes=imovel_data.get("especificacoes", [])
                            )
                            
                            self.indexing_service.index_single_imovel(imovel)
                            print(f"✅ [CREATE] Imóvel {imovel_id} indexado")
                        else:
                            print(f"❌ [CREATE] Imóvel {imovel_id} não encontrado no MongoDB")
                    
                    elif event == "imovel_updated":
                        print(f"📝 [UPDATE] Processando imóvel {imovel_id}")
                        
                        # Buscar dados atualizados do MongoDB
                        imovel_data = self.mongo_repo.get_imovel_by_id(imovel_id)
                        if imovel_data:
                            imovel = ImovelInDB(
                                id=imovel_id,
                                titulo=imovel_data["titulo"],
                                descricao=imovel_data["descricao"],
                                especificacoes=imovel_data.get("especificacoes", [])
                            )
                            
                            self.indexing_service.index_single_imovel(imovel)  # Re-indexa
                            print(f"✅ [UPDATE] Imóvel {imovel_id} re-indexado")
                        else:
                            print(f"❌ [UPDATE] Imóvel {imovel_id} não encontrado no MongoDB")
                    
                    elif event == "imovel_deleted":
                        print(f"🗑️ [DELETE] Processando imóvel {imovel_id}")
                        
                        self.indexing_service.delete_imovel_from_index(imovel_id)
                        print(f"✅ [DELETE] Imóvel {imovel_id} removido do índice")
                    
                    else:
                        print(f"❓ Evento desconhecido: {event}")
                
            except KeyboardInterrupt:
                print("\n🛑 Worker parado pelo usuário")
                break
            except Exception as e:
                print(f"❌ Erro: {e}")
                time.sleep(2)

if __name__ == "__main__":
    worker = SingleWorker()
    worker.run()