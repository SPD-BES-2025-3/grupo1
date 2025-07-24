from bson import ObjectId
from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class PyObjectId(ObjectId):
    @classmethod
    def _get_validators_(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, _):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def _get_pydantic_json_schema_(cls, field_schema):
        field_schema.update(type="string")

class State(str, Enum):
    AC = "Acre"
    AL = "Alagoas"
    AP = "Amapá"
    AM = "Amazonas"
    BA = "Bahia"
    CE = "Ceará"
    DF = "Distrito Federal"
    ES = "Espírito Santo"
    GO = "Goiás"
    MA = "Maranhão"
    MT = "Mato Grosso"
    MS = "Mato Grosso do Sul"
    MG = "Minas Gerais"
    PA = "Pará"
    PB = "Paraíba"
    PR = "Paraná"
    PE = "Pernambuco"
    PI = "Piauí"
    RJ = "Rio de Janeiro"
    RN = "Rio Grande do Norte"
    RS = "Rio Grande do Sul"
    RO = "Rondônia"
    RR = "Roraima"
    SC = "Santa Catarina"
    SP = "São Paulo"
    SE = "Sergipe"
    TO = "Tocantins"

class City(BaseModel):
    id: Optional[str] = None
    name: str
    state: State

class Article(BaseModel):
    id: Optional[str] = None
    title: str
    content: str
    description: Optional[str] = None
    price: Optional[float] = None
    location: Optional[str] = None
    url: Optional[str] = None
    city: City

# E nos seus modelos InDB, você usa assim:
class CidadeInDB():
    id: PyObjectId = Field(alias="_id") # O alias mapeia o "_id" do Mongo para o "id" do Pydantic
