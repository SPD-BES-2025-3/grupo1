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
        self.redis = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe('imoveis.create', 'imoveis.update', 'imoveis.delete')


        MONGO_URI = "mongodb://localhost:27017/"
        MONGO_DB_NAME = "spd_imoveis"
        self.mongo = MongoRepository(MONGO_URI, MONGO_DB_NAME)
        self.chroma = ChromaRepository("./chroma_db")

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
