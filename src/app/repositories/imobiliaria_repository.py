from pymongo.database import Database
from typing import Optional, List
from bson import ObjectId

from ..models import Real_Estate

def doc_to_model(doc):
    doc["_id"] = str(doc["_id"])
    return Real_Estate(**doc)

class ImobiliariaRepository:
    def __init__(self, db: Database):
        self.collection = db["real_estates"]
        
    def get_all(self) -> List[Real_Estate]:
        real_estates = []
        for doc in self.collection.find():
            real_estates.append(doc_to_model(doc))
        return real_estates
    
    def find_one_by_id(self, real_estate_id: str) -> Optional[Real_Estate]:
        """Encontra uma imobiliária através do ID"""
        try:
            doc = self.collection.find_one({"_id": ObjectId(real_estate_id)})
            if doc:
                return doc_to_model(doc)
            return None
        except Exception:
            return None
    
    def find_one_by_phone(self, phone: str) -> Optional[Real_Estate]:
        """Encontra uma imobiliária através do telefone."""
        document = self.collection.find_one({"phone": phone})
        if document:
            return doc_to_model(document)
        return None
    
    def find_one_by_name(self, name: str) -> Optional[Real_Estate]:
        """Encontra uma imobiliária através do nome"""
        document = self.collection.find_one({"name": name})
        if document:
            return doc_to_model(document)
        return None
    
    def create(self, real_estate_data: Real_Estate) -> str:
        """Cria uma nova imobiliária no banco."""
        result = self.collection.insert_one(real_estate_data.model_dump())
        return str(result.inserted_id)
    
    def find_or_create(self, real_estate_data: Real_Estate) -> str:
        """Tenta encontrar uma imobiliária. Se não encontrar, cria uma nova"""
        """Por telefone:"""
        if real_estate_data.phone:
            real_estate_existente = self.find_one_by_phone(real_estate_data.phone)
            if real_estate_existente:
                return real_estate_existente.id
        
        """Por nome:"""
        if real_estate_data.name:
            real_estate_existente = self.find_one_by_name(real_estate_data.name)
            if real_estate_existente:
                return real_estate_existente.id

        return self.create(real_estate_data)
    
    def find_by_ids(self, ids: List[ObjectId]) -> List[Real_Estate]:
        """Busca várias imobiliárias através de uma lista de IDs"""
        documents = self.collection.find({"_id": {"$in": ids}})
        return [doc_to_model(doc) for doc in documents]
    
    def delete_one(self, id: str) -> bool:
        try:
            result = self.collection.delete_one({"_id": ObjectId(id)})
            return result.deleted_count == 1
        except Exception as e:
            print(e)
            return False
        
    def update_one(self, real_estate_id: str, real_estate_data: Real_Estate) -> bool:
        """Atualiza uma imobiliária existente"""
        try:
            real_estate_dict = real_estate_data.model_dump()
            result = self.collection.update_one(
                {"_id": ObjectId(real_estate_id)},
                {"$set": real_estate_dict}
            )
            return result.modified_count > 0
        except Exception as e:
            print(e)
            return False