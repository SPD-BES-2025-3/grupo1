from pymongo.database import Database
from typing import Optional, List, Tuple
from bson import ObjectId

from ..models import City, State

def doc_to_model(doc):
    doc["_id"] = str(doc["_id"])
    return(City(**doc))

class CidadeRepository:
    def __init__(self, db: Database):
        self.collection = db["cities"]

    def get_all(self) -> List[City]:
        cities = []
        for doc in self.collection.find():
            cities.append(doc_to_model(doc))

        return cities

    def find_one_by_id(self, city_id: str) -> Optional[City]:
        try:
            doc = self.collection.find_one({"_id": ObjectId(city_id)})
            if doc:
                return doc_to_model(doc)
            return None
        except Exception:
            return None


    def find_one_by_name(self, nome: str, estado: State) -> Optional[City]:
        """Encontra uma cidade pelo nome e estado."""
        document = self.collection.find_one({"name": nome, "state": estado})
        if document:
            return doc_to_model(document)
        return None

    def create(self, cidade_data: City) -> str:
        """Cria uma nova cidade no banco."""
        result = self.collection.insert_one(cidade_data.model_dump())
        return result.inserted_id

    def find_or_create(self, cidade_data: City) -> str:
        """
        Tenta encontrar uma cidade. Se não encontrar, cria uma nova.
        Ideal para o serviço de indexação.
        """
        cidade_existente = self.find_one_by_name(cidade_data.name, cidade_data.state)
        if cidade_existente:
            return cidade_existente.id
        return self.create(cidade_data)
        
    def find_by_ids(self, ids: List[ObjectId]) -> List[City]:
        """Busca múltiplas cidades por uma lista de IDs."""
        documents = self.collection.find({"_id": {"$in": ids}})
        return [doc_to_model(doc) for doc in documents]
    
    def delete_one(self, id: str) -> bool:
        try:
            result = self.collection.delete_one({"_id": ObjectId(id)})
            return result.deleted_count == 1
        except Exception as e:
            print(e)
            return False
