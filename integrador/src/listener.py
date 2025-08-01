import redis
import json
import sys
import os

# app/ ao path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from app.repositories.mongo_repository import MongoRepository
from app.repositories.chroma_repository import ChromaRepository


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
        
        chroma_path = os.getenv("CHROMA_PATH", "./chroma_db")
        self.chroma = ChromaRepository(chroma_path)

    def listen(self):
        print("⏳ Aguardando eventos Redis...")
        for message in self.pubsub.listen():
            if message['type'] != 'message':
                continue

            channel = message['channel']
            data = json.loads(message['data'])
            imovel_id = data.get('_id')
            print(f"📩 Evento recebido: {channel} com ID {imovel_id}")

            try:
                self.process_event(channel, data, imovel_id)
            except Exception as e:
                print(f"❌ Erro ao processar evento: {e}")


    def process_event(self, channel, data, imovel_id):
        if 'create' in channel:
            self.chroma.add_documents([imovel_id], [data['descricao']], [data])
        elif 'update' in channel:
            self.chroma.update_document(imovel_id, data['descricao'], data)
        elif 'delete' in channel:
            self.chroma.delete_document(imovel_id)
        else:
            print(f"⚠️ Evento desconhecido: {channel}")
