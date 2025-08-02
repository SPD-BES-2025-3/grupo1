from fastapi import APIRouter, Depends, HTTPException
from typing import List
from ..models import Imovel, ImovelInDB
from ..database import get_mongo_repo, get_chroma_repo
from ..services.embedding_service import EmbeddingService
from ..config import REDIS_URL
import redis
import json

router = APIRouter()

@router.post("/imoveis/sync-single/{imovel_id}")
def sync_single_imovel(imovel_id: str):
    """Sincroniza um imóvel específico do MongoDB para o ChromaDB"""
    try:
        from ..repositories.mongo_repository import MongoRepository
        from ..repositories.chroma_repository import ChromaRepository
        from ..config import MONGO_URI, MONGO_DB_NAME
        from bson import ObjectId
        
        mongo_repo = MongoRepository(uri=MONGO_URI, db_name=MONGO_DB_NAME)
        # Usar ChromaDB HTTP em vez de local
        from ..config import CHROMA_HOST, CHROMA_PORT
        chroma_repo = ChromaRepository(host=CHROMA_HOST, port=CHROMA_PORT)
        
        imovel_data = mongo_repo.get_imovel_by_id(imovel_id)
        if not imovel_data:
            return {"error": f"Imóvel {imovel_id} não encontrado no MongoDB"}
        
        from ..models import ImovelInDB
        imovel = ImovelInDB(
            id=str(imovel_data["id"]),
            titulo=imovel_data["titulo"],
            descricao=imovel_data["descricao"],
            especificacoes=imovel_data.get("especificacoes", [])
        )

        # Indexar diretamente sem IndexingService
        embedding_service = EmbeddingService()
        content = f"{imovel.titulo} {imovel.descricao} {' '.join(imovel.especificacoes)}"
        embeddings = embedding_service.create_embeddings([content])
        
        metadata = {
            "id": str(imovel.id),
            "titulo": imovel.titulo,
            "descricao": imovel.descricao,
            "especificacoes": " | ".join(imovel.especificacoes)
        }
        
        chroma_repo.upsert_documents([str(imovel.id)], [content], [metadata], embeddings)
        
        return {
            "message": f"Imóvel {imovel_id} sincronizado com sucesso",
            "titulo": imovel.titulo,
            "id": imovel_id
        }
        
    except Exception as e:
        return {"error": f"Erro na sincronização: {str(e)}", "imovel_id": imovel_id}

@router.post("/imoveis/sync")
def sync_mongo_to_chroma():
    """Sincroniza todos os imóveis do MongoDB para o ChromaDB"""
    try:
        from ..repositories.mongo_repository import MongoRepository
        from ..repositories.chroma_repository import ChromaRepository
        from ..config import MONGO_URI, MONGO_DB_NAME
        from bson import ObjectId
        
        mongo_repo = MongoRepository(uri=MONGO_URI, db_name=MONGO_DB_NAME)
        # Usar ChromaDB HTTP em vez de local
        from ..config import CHROMA_HOST, CHROMA_PORT
        chroma_repo = ChromaRepository(host=CHROMA_HOST, port=CHROMA_PORT)
        
        imoveis_data = mongo_repo.get_all_imoveis()
        
        if not imoveis_data:
            return {"message": "Nenhum imóvel encontrado no MongoDB", "synced": 0}
        
        from ..models import ImovelInDB
        imoveis = []
        for data in imoveis_data:
            try:
                imovel = ImovelInDB(
                    id=str(data["id"]),
                    titulo=data["titulo"],
                    descricao=data["descricao"],
                    especificacoes=data.get("especificacoes", [])
                )
                imoveis.append(imovel)
            except Exception as e:
                print(f"Erro ao processar imóvel {data.get('id', 'N/A')}: {e}")
                continue
        
        embedding_service = EmbeddingService()
        
        synced_count = 0
        for imovel in imoveis:
            try:
                # Indexar diretamente sem IndexingService
                content = f"{imovel.titulo} {imovel.descricao} {' '.join(imovel.especificacoes)}"
                embeddings = embedding_service.create_embeddings([content])
                
                metadata = {
                    "id": str(imovel.id),
                    "titulo": imovel.titulo,
                    "descricao": imovel.descricao,
                    "especificacoes": " | ".join(imovel.especificacoes)
                }
                
                chroma_repo.upsert_documents([str(imovel.id)], [content], [metadata], embeddings)
                synced_count += 1
            except Exception as e:
                print(f"Erro ao indexar imóvel {imovel.id}: {e}")
                continue
        
        return {
            "message": f"Sincronização concluída: {synced_count}/{len(imoveis_data)} imóveis indexados",
            "synced": synced_count,
            "total": len(imoveis_data)
        }
        
    except Exception as e:
        return {"error": f"Erro na sincronização: {str(e)}", "synced": 0}

@router.post("/imoveis/")
def create_imovel(imovel: Imovel):
    from ..repositories.mongo_repository import MongoRepository
    from ..config import MONGO_URI, MONGO_DB_NAME
    
    mongo_repo = MongoRepository(uri=MONGO_URI, db_name=MONGO_DB_NAME)
    imovel_dict = imovel.dict()
    imovel_id = mongo_repo.add_imovel(imovel_dict) 
    
    # Redis publish é feito pelo MongoRepository
    
    return {**imovel_dict, "id": str(imovel_id)}

@router.get("/imoveis/")
def read_imoveis():
    from ..repositories.mongo_repository import MongoRepository
    from ..config import MONGO_URI, MONGO_DB_NAME
    
    mongo_repo = MongoRepository(uri=MONGO_URI, db_name=MONGO_DB_NAME)
    return mongo_repo.get_all_imoveis()

@router.get("/imoveis/{imovel_id}")
def read_imovel(imovel_id: str):
    from ..repositories.mongo_repository import MongoRepository
    from ..config import MONGO_URI, MONGO_DB_NAME
    
    mongo_repo = MongoRepository(uri=MONGO_URI, db_name=MONGO_DB_NAME)
    db_imovel = mongo_repo.get_imovel_by_id(imovel_id)
    if db_imovel is None:
        raise HTTPException(status_code=404, detail="Imovel not found")
    return db_imovel

@router.put("/imoveis/{imovel_id}")
def update_imovel(imovel_id: str, imovel: Imovel):
    from ..repositories.mongo_repository import MongoRepository
    from ..config import MONGO_URI, MONGO_DB_NAME
    
    mongo_repo = MongoRepository(uri=MONGO_URI, db_name=MONGO_DB_NAME)
    
    db_imovel = mongo_repo.get_imovel_by_id(imovel_id)
    if db_imovel is None:
        raise HTTPException(status_code=404, detail="Imovel not found")
    
    imovel_dict = imovel.dict()
    mongo_repo.update_imovel(imovel_id, imovel_dict)
    
    # Redis publish é feito pelo MongoRepository
    
    return {**imovel_dict, "id": str(imovel_id)}

@router.delete("/imoveis/all")
def delete_all_imoveis():
    """Limpa todos os imóveis do MongoDB"""
    from ..repositories.mongo_repository import MongoRepository
    from ..config import MONGO_URI, MONGO_DB_NAME
    
    mongo_repo = MongoRepository(uri=MONGO_URI, db_name=MONGO_DB_NAME)
    
    # Conta quantos imóveis existem antes de deletar
    imoveis_antes = mongo_repo.get_all_imoveis()
    count_antes = len(imoveis_antes)
    
    # Limpa a collection
    mongo_repo.collection.delete_many({})
    
    # Publish to Redis
    r = redis.from_url(REDIS_URL)
    r.publish("imoveis.clear", json.dumps({
        "action": "clear_all",
        "deleted_count": count_antes
    }))
    
    return {
        "message": f"Todos os imóveis foram removidos do MongoDB", 
        "deleted_count": count_antes
    }

@router.delete("/imoveis/{imovel_id}")
def delete_imovel(imovel_id: str):
    from ..repositories.mongo_repository import MongoRepository
    from ..config import MONGO_URI, MONGO_DB_NAME
    
    mongo_repo = MongoRepository(uri=MONGO_URI, db_name=MONGO_DB_NAME)
    
    db_imovel = mongo_repo.get_imovel_by_id(imovel_id)
    if db_imovel is None:
        raise HTTPException(status_code=404, detail="Imovel not found")
    
    mongo_repo.delete_imovel(imovel_id)
    
    # Redis publish é feito pelo MongoRepository
    
    return {"message": "Imovel deleted successfully", "id": imovel_id}