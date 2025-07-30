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
from app.config import REDIS_URL


class DeleteWorker:
    def __init__(self):
        self.message_broker = MessageBrokerService(redis_url=REDIS_URL)
        self.embedding_service = EmbeddingService()
        self.chroma_repo = ChromaRepository(path="./chroma_db")
        self.indexing_service = IndexingService(
            embedding_service=self.embedding_service,
            chroma_repo=self.chroma_repo
        )
        self.queue_name = "imovel_deleted_queue"
        
    def process_message(self, message):
        """Processa mensagem de exclusão de imóvel"""
        try:
            imovel_id = message.get("id")
            payload = message.get("payload", {})
            
            print(f"[DELETE WORKER] Processando exclusão do imóvel {imovel_id}")
            
            # Remover do índice ChromaDB
            self.indexing_service.delete_imovel_from_index(imovel_id)
            
            print(f"[DELETE WORKER] ✅ Imóvel {imovel_id} removido com sucesso do ChromaDB")
            return True
            
        except Exception as e:
            print(f"[DELETE WORKER] ❌ Erro ao processar exclusão: {e}")
            return False
    
    def start(self):
        """Inicia o worker para processar mensagens de exclusão"""
        print(f"[DELETE WORKER] 🚀 Iniciado - Aguardando mensagens na queue '{self.queue_name}'")
        
        while True:
            try:
                # Buscar mensagem da queue (timeout de 5 segundos)
                message = self.message_broker.get_message(self.queue_name, timeout=5)
                
                if message:
                    success = self.process_message(message)
                    if success:
                        print(f"[DELETE WORKER] ✅ Mensagem processada com sucesso")
                    else:
                        print(f"[DELETE WORKER] ⚠️ Falha ao processar mensagem")
                else:
                    # Sem mensagens, aguarda um pouco
                    time.sleep(1)
                    
            except KeyboardInterrupt:
                print(f"[DELETE WORKER] 🛑 Worker interrompido pelo usuário")
                break
            except Exception as e:
                print(f"[DELETE WORKER] ❌ Erro no worker: {e}")
                time.sleep(5)  # Aguarda antes de tentar novamente


if __name__ == "__main__":
    worker = DeleteWorker()
    worker.start()