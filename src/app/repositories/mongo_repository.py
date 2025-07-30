from pymongo import MongoClient
from bson import ObjectId
from typing import List, Dict, Any
from ..models import ImovelInDB

class MongoRepository:
    def __init__(self, uri: str, db_name: str):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.collection = self.db.imoveis
        self.corretores_collection = self.db.corretores
        self.cidades_collection = self.db.cidades

    def add_imovel(self, imovel: Dict[str, Any]) -> str:
        # Fazer cópia para não modificar o dicionário original
        imovel_copy = imovel.copy()
        result = self.collection.insert_one(imovel_copy)
        return str(result.inserted_id)

    def get_imovel_by_id(self, imovel_id: str) -> Dict[str, Any]:
        result = self.collection.find_one({"_id": ObjectId(imovel_id)})
        if result:
            result["id"] = str(result["_id"])
            del result["_id"]
        return result

    def get_all_imoveis(self) -> List[Dict[str, Any]]:
        results = list(self.collection.find())
        for result in results:
            result["id"] = str(result["_id"])
            del result["_id"]
        return results

    def update_imovel(self, imovel_id: str, imovel: Dict[str, Any]):
        self.collection.update_one({"_id": ObjectId(imovel_id)}, {"$set": imovel})

    def delete_imovel(self, imovel_id: str):
        self.collection.delete_one({"_id": ObjectId(imovel_id)})
    
    # Métodos para Corretores
    def add_corretor(self, corretor: Dict[str, Any]) -> str:
        corretor_copy = corretor.copy()
        result = self.corretores_collection.insert_one(corretor_copy)
        return str(result.inserted_id)
    
    def get_corretor_by_id(self, corretor_id: str) -> Dict[str, Any]:
        result = self.corretores_collection.find_one({"_id": ObjectId(corretor_id)})
        if result:
            result["id"] = str(result["_id"])
            del result["_id"]
        return result
    
    def get_all_corretores(self) -> List[Dict[str, Any]]:
        results = list(self.corretores_collection.find())
        for result in results:
            result["id"] = str(result["_id"])
            del result["_id"]
        return results
    
    def update_corretor(self, corretor_id: str, corretor: Dict[str, Any]):
        self.corretores_collection.update_one({"_id": ObjectId(corretor_id)}, {"$set": corretor})
    
    def delete_corretor(self, corretor_id: str):
        self.corretores_collection.delete_one({"_id": ObjectId(corretor_id)})
    
    # Métodos para Cidades
    def add_cidade(self, cidade: Dict[str, Any]) -> str:
        cidade_copy = cidade.copy()
        result = self.cidades_collection.insert_one(cidade_copy)
        return str(result.inserted_id)
    
    def get_cidade_by_id(self, cidade_id: str) -> Dict[str, Any]:
        result = self.cidades_collection.find_one({"_id": ObjectId(cidade_id)})
        if result:
            result["id"] = str(result["_id"])
            del result["_id"]
        return result
    
    def get_all_cidades(self) -> List[Dict[str, Any]]:
        results = list(self.cidades_collection.find())
        for result in results:
            result["id"] = str(result["_id"])
            del result["_id"]
        return results
    
    def update_cidade(self, cidade_id: str, cidade: Dict[str, Any]):
        self.cidades_collection.update_one({"_id": ObjectId(cidade_id)}, {"$set": cidade})
    
    def delete_cidade(self, cidade_id: str):
        self.cidades_collection.delete_one({"_id": ObjectId(cidade_id)})
