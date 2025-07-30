#!/usr/bin/env python3
import sys
import os
import time

# Adicionar o diretório src ao path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, '../../..')
sys.path.insert(0, src_dir)

from app.services.message_broker_service import MessageBrokerService
from app.services.embedding_service import EmbeddingService
from app.services.indexing_service import IndexingService
from app.repositories.chroma_repository import ChromaRepository
from app.repositories.mongo_repository import MongoRepository
from app.models import ImovelInDB
from app.config import REDIS_URL, MONGO_URI, MONGO_DB_NAME
from bson import ObjectId


class UpdateWorker:
    def __init__(self):
        self.message_broker = MessageBrokerService(redis_url=REDIS_URL)
        self.embedding_service = EmbeddingService()
        self.chroma_repo = ChromaRepository(path="./chroma_db")
        self.mongo_repo = MongoRepository(uri=MONGO_URI, db_name=MONGO_DB_NAME)
        self.indexing_service = IndexingService(
            embedding_service=self.embedding_service,
            chroma_repo=self.chroma_repo
        )
        self.queue_name = "imovel_updated_queue"
        
    def process_message(self, message):
        """Processa mensagem de atualização de imóvel"""
        try:
            imovel_id = message.get("id")
            payload = message.get("payload", {})
            
            print(f"[UPDATE WORKER] Processando atualização do imóvel {imovel_id}")
            
            # Buscar dados atualizados do MongoDB (para garantir consistência)
            imovel_data = self.mongo_repo.get_imovel_by_id(imovel_id)
            if not imovel_data:
                print(f"[UPDATE WORKER] Erro: Imóvel {imovel_id} não encontrado no MongoDB")
                return False
            
            # Converter para ImovelInDB
            imovel = ImovelInDB(
                id=ObjectId(imovel_id),
                titulo=imovel_data["titulo"],
                descricao=imovel_data["descricao"],
                especificacoes=imovel_data.get("especificacoes", [])
            )
            
            # Re-indexar no ChromaDB (upsert sobrescreve o existente)
            self.indexing_service.index_single_imovel(imovel)
            
            print(f"[UPDATE WORKER] ✅ Imóvel {imovel_id} re-indexado com sucesso no ChromaDB")
            return True
            
        except Exception as e:
            print(f"[UPDATE WORKER] ❌ Erro ao processar atualização: {e}")
            return False
    
    def start(self):
        """Inicia o worker para processar mensagens de atualização"""
        print(f"[UPDATE WORKER] 🚀 Iniciado - Aguardando mensagens na queue '{self.queue_name}'")
        
        while True:
            try:
                # Buscar mensagem da queue (timeout de 5 segundos)
                message = self.message_broker.get_message(self.queue_name, timeout=5)
                
                if message:
                    success = self.process_message(message)
                    if success:
                        print(f"[UPDATE WORKER] ✅ Mensagem processada com sucesso")
                    else:
                        print(f"[UPDATE WORKER] ⚠️ Falha ao processar mensagem")
                else:
                    # Sem mensagens, aguarda um pouco
                    time.sleep(1)
                    
            except KeyboardInterrupt:
                print(f"[UPDATE WORKER] 🛑 Worker interrompido pelo usuário")
                break
            except Exception as e:
                print(f"[UPDATE WORKER] ❌ Erro no worker: {e}")
                time.sleep(5)  # Aguarda antes de tentar novamente


if __name__ == "__main__":
    worker = UpdateWorker()
    worker.start()