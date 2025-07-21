from pymongo import MongoClient, ASCENDING
from pymongo.errors import BulkWriteError

from src import config
from typing import List

"""
Não é uma camada de persistência completa.
É só um arquivo para trabalhar diretamento com o driver do MongoDB
"""

class MongoDBStorage:
    
    #Construtor da classe
    def __init__(
                    self, 
                    uri: str, 
                    db_name: str = config.DB_NAME, 
                    collection_name: str = config.COLLECTION_NAME
                ):
        
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        self._ensure_indexes() # CHAMADA: Garante que os índices existam ao inicializar a classe
    
    def _ensure_indexes(self):
        """
        Método privado para criar os índices necessários na coleção.
        É idempotente: se o índice já existir, o MongoDB não faz nada.
        """
        print(f"Garantindo índices para a coleção '{self.collection.name}'...")
        
        # Defina aqui sua chave composta
        composite_key = [("_id", ASCENDING), ("updatedAt", ASCENDING)]
        
        self.collection.create_index(
            composite_key,
            name="anuncios_unicos",  # Nomear o índice é uma boa prática
            unique=True
        )
        
        #adicionar try-catch para tratar o sucesso da chave já existente no banco de dados 
        print("Índices garantidos.")

    def insert_property(self, property_data: dict):
        result = self.collection.insert_one(property_data)
        return result.inserted_id
    
    def insert_many_properties(self, properties_data: List[dict]):
        """Insere múltiplos registros no MongoDB, ignorando duplicatas (_id repetido)."""
        try:
            result = self.collection.insert_many(properties_data, ordered=False)
            return result.inserted_ids
        except BulkWriteError as bwe:
            # Esta lógica agora também irá capturar erros de duplicidade da sua nova chave composta!
            return bwe.details