#!/usr/bin/env python3
"""
Workers simplificados para processamento assíncrono
Executa todos os workers em threads separadas
"""
import sys
import os
import time
import threading
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
from app.config import REDIS_URL, MONGO_URI, MONGO_DB_NAME
from bson import ObjectId


class WorkerManager:
    def __init__(self):
        self.redis_client = redis.from_url(REDIS_URL)
        self.embedding_service = EmbeddingService()
        self.chroma_repo = ChromaRepository(path="./chroma_db")
        self.mongo_repo = MongoRepository(uri=MONGO_URI, db_name=MONGO_DB_NAME)
        self.indexing_service = IndexingService(
            embedding_service=self.embedding_service,
            chroma_repo=self.chroma_repo
        )
        
    def create_worker(self):
        """Worker para processar criação de imóveis"""
        queue_name = "imovel_created_queue"
        print(f"[CREATE WORKER] 🚀 Iniciado - Aguardando mensagens")
        
        while True:
            try:
                result = self.redis_client.brpop(queue_name, timeout=5)
                if result:
                    _, message = result
                    data = json.loads(message.decode('utf-8'))
                    
                    imovel_id = data.get("id")
                    print(f"[CREATE WORKER] Processando imóvel {imovel_id}")
                    
                    # Buscar dados do MongoDB
                    imovel_data = self.mongo_repo.get_imovel_by_id(imovel_id)
                    if imovel_data:
                        imovel = ImovelInDB(
                            id=ObjectId(imovel_id),
                            titulo=imovel_data["titulo"],
                            descricao=imovel_data["descricao"],
                            especificacoes=imovel_data.get("especificacoes", [])
                        )
                        
                        self.indexing_service.index_single_imovel(imovel)
                        print(f"[CREATE WORKER] ✅ Imóvel {imovel_id} indexado")
                
            except Exception as e:
                print(f"[CREATE WORKER] ❌ Erro: {e}")
                time.sleep(5)
    
    def update_worker(self):
        """Worker para processar atualizações de imóveis"""
        queue_name = "imovel_updated_queue"
        print(f"[UPDATE WORKER] 🚀 Iniciado - Aguardando mensagens")
        
        while True:
            try:
                result = self.redis_client.brpop(queue_name, timeout=5)
                if result:
                    _, message = result
                    data = json.loads(message.decode('utf-8'))
                    
                    imovel_id = data.get("id")
                    print(f"[UPDATE WORKER] Processando imóvel {imovel_id}")
                    
                    # Buscar dados atualizados do MongoDB
                    imovel_data = self.mongo_repo.get_imovel_by_id(imovel_id)
                    if imovel_data:
                        imovel = ImovelInDB(
                            id=ObjectId(imovel_id),
                            titulo=imovel_data["titulo"],
                            descricao=imovel_data["descricao"],
                            especificacoes=imovel_data.get("especificacoes", [])
                        )
                        
                        self.indexing_service.index_single_imovel(imovel)
                        print(f"[UPDATE WORKER] ✅ Imóvel {imovel_id} re-indexado")
                
            except Exception as e:
                print(f"[UPDATE WORKER] ❌ Erro: {e}")
                time.sleep(5)
    
    def delete_worker(self):
        """Worker para processar exclusões de imóveis"""
        queue_name = "imovel_deleted_queue"
        print(f"[DELETE WORKER] 🚀 Iniciado - Aguardando mensagens")
        
        while True:
            try:
                result = self.redis_client.brpop(queue_name, timeout=5)
                if result:
                    _, message = result
                    data = json.loads(message.decode('utf-8'))
                    
                    imovel_id = data.get("id")
                    print(f"[DELETE WORKER] Processando imóvel {imovel_id}")
                    
                    self.indexing_service.delete_imovel_from_index(imovel_id)
                    print(f"[DELETE WORKER] ✅ Imóvel {imovel_id} removido do índice")
                
            except Exception as e:
                print(f"[DELETE WORKER] ❌ Erro: {e}")
                time.sleep(5)
    
    def start_all(self):
        """Inicia todos os workers em threads separadas"""
        print("🚀 Iniciando sistema de workers...")
        
        # Testar conexões
        try:
            self.redis_client.ping()
            print("✅ Redis conectado")
        except Exception as e:
            print(f"❌ Erro no Redis: {e}")
            return
        
        try:
            self.mongo_repo.get_all_imoveis()
            print("✅ MongoDB conectado")
        except Exception as e:
            print(f"❌ Erro no MongoDB: {e}")
            return
        
        # Iniciar workers em threads
        workers = [
            threading.Thread(target=self.create_worker, daemon=True),
            threading.Thread(target=self.update_worker, daemon=True),
            threading.Thread(target=self.delete_worker, daemon=True)
        ]
        
        for worker in workers:
            worker.start()
        
        print("📊 Todos os workers iniciados!")
        print("🔍 Pressione Ctrl+C para parar")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Parando workers...")


if __name__ == "__main__":
    manager = WorkerManager()
    manager.start_all()