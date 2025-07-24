from bson import ObjectId
from pydantic import BaseModel, Field
from typing import Optional

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
        
class Article(BaseModel):
    id: Optional[str] = None
    title: str
    content: str
    description: Optional[str] = None
    price: Optional[float] = None
    location: Optional[str] = None
    url: Optional[str] = None

# E nos seus modelos InDB, você usa assim:
class CidadeInDB():
    id: PyObjectId = Field(alias="_id") # O alias mapeia o "_id" do Mongo para o "id" do Pydantic
