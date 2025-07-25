from pymongo.database import Database
from typing import Optional, Dict, Any, List
from bson import ObjectId

from ..models import CidadeSchema, CidadeInDB

class CidadeRepository:
    def _init_(self, db: Database):
        self.collection = db["cidades"]

    def find_one_by_name(self, nome: str, estado: str) -> Optional[CidadeInDB]:
        """Encontra uma cidade pelo nome e estado."""
        document = self.collection.find_one({"nome": nome, "estado": estado})
        if document:
            return CidadeInDB(**document)
        return None

    def create(self, cidade_data: CidadeSchema) -> CidadeInDB:
        """Cria uma nova cidade no banco."""
        result = self.collection.insert_one(cidade_data.model_dump())
        new_document = self.collection.find_one({"_id": result.inserted_id})
        return CidadeInDB(**new_document)

    def find_or_create(self, cidade_data: CidadeSchema) -> CidadeInDB:
        """
        Tenta encontrar uma cidade. Se não encontrar, cria uma nova.
        Ideal para o serviço de indexação.
        """
        cidade_existente = self.find_one_by_name(cidade_data.nome, cidade_data.estado)
        if cidade_existente:
            return cidade_existente
        return self.create(cidade_data)
        
    def find_by_ids(self, ids: List[ObjectId]) -> List[CidadeInDB]:
        """Busca múltiplas cidades por uma lista de IDs."""
        documents = self.collection.find({"_id": {"$in": ids}})
        return [CidadeInDB(**doc) for doc in documents]