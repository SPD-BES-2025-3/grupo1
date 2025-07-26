from fastapi import APIRouter, Depends
from typing import List

from ..models import City
from ..database import get_city_repo

router = APIRouter()

# Dependência para o repositório
def get_city_repository():
    return get_city_repo()

@router.get("/cities/", response_model=List[City])
def read_cities(repo: any = Depends(get_city_repository)):
    return repo.get_all()
