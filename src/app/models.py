from pydantic import BaseModel, Field
from typing import Optional, List
from bson import ObjectId

#Padrão de design do Pydantic para FastAPI
#BASE                                                         VS                              INDB 
#Servem como um formulário de entrada para criar novos dados. x  Representam os dados que já estão salvos no banco de dados


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")

class Imovel(BaseModel):
    titulo: str
    descricao: str
    especificacoes: List[str]

class ImovelInDB(Imovel):
    id: str  

    class Config:
        json_encoders = {
            ObjectId: str
        }

class Corretor(BaseModel):
    nome: str
    email: str
    telefone: str
    creci: str
    ativo: bool = True
    especialidades: List[str] = []  # Ex: ["Residencial", "Comercial", "Rural"]
    cidades_atendidas: List[str] = []  # IDs das cidades que atende

class CorretorInDB(Corretor):
    id: str

    class Config:
        json_encoders = {
            ObjectId: str
        }

class Cidade(BaseModel):
    nome: str
    estado: str  # Sigla do estado (ex: "GO", "SP")
    regiao: Optional[str] = None  # Ex: "Centro-Oeste", "Sudeste"
    populacao: Optional[int] = None
    area_km2: Optional[float] = None
    
class CidadeInDB(Cidade):
    id: str
    
    class Config:
        json_encoders = {
            ObjectId: str
        }
