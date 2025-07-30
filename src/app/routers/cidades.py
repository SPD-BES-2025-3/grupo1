from fastapi import APIRouter, HTTPException
from typing import List
from ..models import Cidade, CidadeInDB
from ..config import MONGO_URI, MONGO_DB_NAME

router = APIRouter()

@router.post("/cidades/")
def create_cidade(cidade: Cidade):
    from ..repositories.mongo_repository import MongoRepository
    
    mongo_repo = MongoRepository(uri=MONGO_URI, db_name=MONGO_DB_NAME)
    cidade_dict = cidade.model_dump()
    cidade_id = mongo_repo.add_cidade(cidade_dict)
    
    return {**cidade_dict, "id": cidade_id}

@router.get("/cidades/")
def read_cidades():
    from ..repositories.mongo_repository import MongoRepository
    
    mongo_repo = MongoRepository(uri=MONGO_URI, db_name=MONGO_DB_NAME)
    return mongo_repo.get_all_cidades()

@router.get("/cidades/{cidade_id}")
def read_cidade(cidade_id: str):
    from ..repositories.mongo_repository import MongoRepository
    
    mongo_repo = MongoRepository(uri=MONGO_URI, db_name=MONGO_DB_NAME)
    db_cidade = mongo_repo.get_cidade_by_id(cidade_id)
    if db_cidade is None:
        raise HTTPException(status_code=404, detail="Cidade not found")
    return db_cidade

@router.put("/cidades/{cidade_id}")
def update_cidade(cidade_id: str, cidade: Cidade):
    from ..repositories.mongo_repository import MongoRepository
    
    mongo_repo = MongoRepository(uri=MONGO_URI, db_name=MONGO_DB_NAME)
    
    # Verificar se cidade existe
    db_cidade = mongo_repo.get_cidade_by_id(cidade_id)
    if db_cidade is None:
        raise HTTPException(status_code=404, detail="Cidade not found")
    
    # Atualizar no MongoDB
    cidade_dict = cidade.model_dump()
    mongo_repo.update_cidade(cidade_id, cidade_dict)
    
    return {**cidade_dict, "id": cidade_id}

@router.delete("/cidades/{cidade_id}")
def delete_cidade(cidade_id: str):
    from ..repositories.mongo_repository import MongoRepository
    
    mongo_repo = MongoRepository(uri=MONGO_URI, db_name=MONGO_DB_NAME)
    
    # Verificar se cidade existe
    db_cidade = mongo_repo.get_cidade_by_id(cidade_id)
    if db_cidade is None:
        raise HTTPException(status_code=404, detail="Cidade not found")
    
    # Remover do MongoDB
    mongo_repo.delete_cidade(cidade_id)
    
    return {"message": "Cidade deleted successfully", "id": cidade_id}

@router.get("/cidades/estado/{estado}")
def read_cidades_by_estado(estado: str):
    """Busca todas as cidades de um estado específico"""
    from ..repositories.mongo_repository import MongoRepository
    
    mongo_repo = MongoRepository(uri=MONGO_URI, db_name=MONGO_DB_NAME)
    all_cidades = mongo_repo.get_all_cidades()
    
    # Filtrar por estado
    cidades_estado = [c for c in all_cidades if c.get("estado", "").upper() == estado.upper()]
    
    return cidades_estado