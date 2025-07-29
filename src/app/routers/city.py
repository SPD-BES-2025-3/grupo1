from fastapi import APIRouter, Depends, HTTPException, Response
from typing import List

from ..models import City
from .dependencies import get_cidade_repository

router = APIRouter()

@router.get("/cities/", response_model=List[City])
def read_cities(repo = Depends(get_cidade_repository)):
    return repo.get_all()

@router.get("/cities/{city_id}", response_model=City)
def read_city(city_id: str, repo = Depends(get_cidade_repository)):
    db_city = repo.find_one_by_id(city_id)
    if db_city is None:
        raise HTTPException(status_code=404, detail="City not found")
    return db_city

@router.post("/cities/", response_model=City)
def create_city(city: City, repo = Depends(get_cidade_repository)):
    """Cria uma nova cidade."""
    city_id = repo.create(city)
    created_city = repo.find_one_by_id(city_id)
    return created_city

@router.put("/cities/{city_id}", response_model=City)
def update_city(city_id: str, city: City, repo = Depends(get_cidade_repository)):
    db_city = repo.find_one_by_id(city_id)
    if db_city is None:
        raise HTTPException(status_code=404, detail="City not found")
    
    success = repo.update_one(city_id, city)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update city")
    
    updated_city = repo.find_one_by_id(city_id)
    return updated_city

@router.delete("/cities/{city_id}")
def delete_city(city_id: str, repo = Depends(get_cidade_repository)):
    result = repo.delete_one(city_id)
    if result is False:
        raise HTTPException(status_code=404, detail="City not found")
    
    return Response(status_code=204)

@router.get("/cities/search/by-name/{name}", response_model=City)
def search_city_by_name(name: str, state: str, repo = Depends(get_cidade_repository)):
    db_city = repo.find_one_by_name(name, state)
    if db_city is None:
        raise HTTPException(status_code=404, detail="City not found")
    return db_city
