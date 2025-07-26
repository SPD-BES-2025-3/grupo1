from pymongo.database import Database
from typing import Optional, List, Tuple
from bson import ObjectId

from ..models import City, State

class CidadeRepository:
    def __init__(self, db: Database):
        self.collection = db["cities"]

    def get_all(self) -> List[City]:
        cities = []
        for doc in self.collection.find():
            doc["_id"] = str(doc["_id"])
            cities.append(City(**doc))

        return cities

    def find_one_by_id(self, city_id: str) -> Optional[City]:
        try:
            doc = self.collection.find_one({"_id": ObjectId(city_id)})
            if doc:
                doc["_id"] = str(doc["_id"])
                return City(**doc)
            return None
        except Exception:
            return None


    def find_one_by_name(self, nome: str, estado: State) -> Tuple[Optional[City], Optional[str]]:
        """Encontra uma cidade pelo nome e estado."""
        document = self.collection.find_one({"name": nome, "state": estado})
        if document:
            return( City(**document), document["_id"])
        return (None, None)

    def create(self, cidade_data: City) -> str:
        """Cria uma nova cidade no banco."""
        result = self.collection.insert_one(cidade_data.model_dump())
        return result.inserted_id

    def find_or_create(self, cidade_data: City) -> str:
        """
        Tenta encontrar uma cidade. Se não encontrar, cria uma nova.
        Ideal para o serviço de indexação.
        """
        cidade_existente, id = self.find_one_by_name(cidade_data.name, cidade_data.state)
        if cidade_existente:
            return id
        return self.create(cidade_data)
        
    def find_by_ids(self, ids: List[ObjectId]) -> List[City]:
        """Busca múltiplas cidades por uma lista de IDs."""
        documents = self.collection.find({"_id": {"$in": ids}})
        return [City(**doc) for doc in documents]