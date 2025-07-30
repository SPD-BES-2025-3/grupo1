from fastapi import APIRouter, HTTPException
from typing import List
from ..models import Corretor, CorretorInDB
from ..config import MONGO_URI, MONGO_DB_NAME

router = APIRouter()

@router.post("/corretores/")
def create_corretor(corretor: Corretor):
    from ..repositories.mongo_repository import MongoRepository
    
    mongo_repo = MongoRepository(uri=MONGO_URI, db_name=MONGO_DB_NAME)
    corretor_dict = corretor.model_dump()
    corretor_id = mongo_repo.add_corretor(corretor_dict)
    
    return {**corretor_dict, "id": corretor_id}

@router.get("/corretores/")
def read_corretores():
    from ..repositories.mongo_repository import MongoRepository
    
    mongo_repo = MongoRepository(uri=MONGO_URI, db_name=MONGO_DB_NAME)
    return mongo_repo.get_all_corretores()

@router.get("/corretores/{corretor_id}")
def read_corretor(corretor_id: str):
    from ..repositories.mongo_repository import MongoRepository
    
    mongo_repo = MongoRepository(uri=MONGO_URI, db_name=MONGO_DB_NAME)
    db_corretor = mongo_repo.get_corretor_by_id(corretor_id)
    if db_corretor is None:
        raise HTTPException(status_code=404, detail="Corretor not found")
    return db_corretor

@router.put("/corretores/{corretor_id}")
def update_corretor(corretor_id: str, corretor: Corretor):
    from ..repositories.mongo_repository import MongoRepository
    
    mongo_repo = MongoRepository(uri=MONGO_URI, db_name=MONGO_DB_NAME)
    
    # Verificar se corretor existe
    db_corretor = mongo_repo.get_corretor_by_id(corretor_id)
    if db_corretor is None:
        raise HTTPException(status_code=404, detail="Corretor not found")
    
    # Atualizar no MongoDB
    corretor_dict = corretor.model_dump()
    mongo_repo.update_corretor(corretor_id, corretor_dict)
    
    return {**corretor_dict, "id": corretor_id}

@router.delete("/corretores/{corretor_id}")
def delete_corretor(corretor_id: str):
    from ..repositories.mongo_repository import MongoRepository
    
    mongo_repo = MongoRepository(uri=MONGO_URI, db_name=MONGO_DB_NAME)
    
    # Verificar se corretor existe
    db_corretor = mongo_repo.get_corretor_by_id(corretor_id)
    if db_corretor is None:
        raise HTTPException(status_code=404, detail="Corretor not found")
    
    # Remover do MongoDB
    mongo_repo.delete_corretor(corretor_id)
    
    return {"message": "Corretor deleted successfully", "id": corretor_id}