import redis
import json
from datetime import datetime
from typing import Dict, Any
from bson import ObjectId


class MessageBrokerService:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = redis.from_url(redis_url)
    
    def _clean_payload(self, data):
        """Remove ObjectIds e outros tipos não serializáveis do payload"""
        if isinstance(data, dict):
            cleaned = {}
            for key, value in data.items():
                if key == '_id':  # Pular _id do MongoDB
                    continue
                cleaned[key] = self._clean_payload(value)
            return cleaned
        elif isinstance(data, list):
            return [self._clean_payload(item) for item in data]
        elif isinstance(data, ObjectId):
            return str(data)  # Converter ObjectId para string
        else:
            return data
        
    def publish_imovel_event(self, event: str, imovel_id: str, payload: Dict[str, Any] = None):
        """
        Publica evento de imóvel na queue apropriada
        
        Args:
            event: Tipo do evento ('imovel_created', 'imovel_updated', 'imovel_deleted')
            imovel_id: ID do imóvel
            payload: Dados adicionais do evento
        """
        # Limpar payload de ObjectIds e outros tipos não serializáveis
        clean_payload = self._clean_payload(payload) if payload else {}
        
        message = {
            "event": event,
            "id": imovel_id,
            "timestamp": datetime.utcnow().isoformat(),
            "payload": clean_payload
        }
        
        queue_name = f"{event}_queue"
        
        try:
            self.redis_client.lpush(queue_name, json.dumps(message))
            return True
        except Exception as e:
            print(f"Erro ao publicar evento {event}: {e}")
            return False
    
    def get_message(self, queue_name: str, timeout: int = 5):
        """
        Consome mensagem de uma queue específica
        
        Args:
            queue_name: Nome da queue
            timeout: Timeout em segundos para aguardar mensagem
            
        Returns:
            Dict com dados da mensagem ou None se timeout
        """
        try:
            result = self.redis_client.brpop(queue_name, timeout=timeout)
            if result:
                _, message = result
                return json.loads(message.decode('utf-8'))
            return None
        except Exception as e:
            print(f"Erro ao consumir mensagem da queue {queue_name}: {e}")
            return None
    
    def get_queue_size(self, queue_name: str) -> int:
        """Retorna o tamanho atual da queue"""
        try:
            return self.redis_client.llen(queue_name)
        except Exception as e:
            print(f"Erro ao obter tamanho da queue {queue_name}: {e}")
            return 0
    
    def clear_queue(self, queue_name: str):
        """Limpa uma queue específica"""
        try:
            self.redis_client.delete(queue_name)
            return True
        except Exception as e:
            print(f"Erro ao limpar queue {queue_name}: {e}")
            return False