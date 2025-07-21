from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID, uuid4

class Article(BaseModel):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    title: str
    url: str
    content: str
    summary: Optional[str] = None
    keywords: Optional[List[str]] = None

    class Config:
        allow_population_by_field_name = True
