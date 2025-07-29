from fastapi import APIRouter, Depends, HTTPException, Response
from typing import List

from ..models import Real_Estate
from .dependencies import get_imobiliaria_repository

router = APIRouter()

@router.get("/real-estates/", response_model=List[Real_Estate])
def read_real_estates(repo = Depends(get_imobiliaria_repository)):
    return repo.get_all()

@router.get("/real-estates/{real_estate_id}", response_model=Real_Estate)
def read_real_estate(real_estate_id: str, repo = Depends(get_imobiliaria_repository)):
    db_real_estate = repo.find_one_by_id(real_estate_id)
    if db_real_estate is None:
        raise HTTPException(status_code=404, detail="Real estate not found")
    return db_real_estate

@router.post("/real-estates/", response_model=Real_Estate)
def create_real_estate(real_estate: Real_Estate, repo = Depends(get_imobiliaria_repository)):
    real_estate_id = repo.create(real_estate)
    created_real_estate = repo.find_one_by_id(real_estate_id)
    return created_real_estate

@router.put("/real-estates/{real_estate_id}", response_model=Real_Estate)
def update_real_estate(real_estate_id: str, real_estate: Real_Estate, repo = Depends(get_imobiliaria_repository)):
    db_real_estate = repo.find_one_by_id(real_estate_id)
    if db_real_estate is None:
        raise HTTPException(status_code=404, detail="Real estate not found")
    
    success = repo.update_one(real_estate_id, real_estate)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update real estate")
    
    updated_real_estate = repo.find_one_by_id(real_estate_id)
    return updated_real_estate

@router.delete("/real-estates/{real_estate_id}")
def delete_real_estate(real_estate_id: str, repo = Depends(get_imobiliaria_repository)):
    result = repo.delete_one(real_estate_id)
    if result is False:
        raise HTTPException(status_code=404, detail="Real estate not found")
    
    return Response(status_code=204)

@router.get("/real-estates/search/by-name/{name}", response_model=Real_Estate)
def search_real_estate_by_name(name: str, repo = Depends(get_imobiliaria_repository)):
    db_real_estate = repo.find_one_by_name(name)
    if db_real_estate is None:
        raise HTTPException(status_code=404, detail="Real estate not found")
    return db_real_estate

@router.get("/real-estates/search/by-phone/{phone}", response_model=Real_Estate)
def search_real_estate_by_phone(phone: str, repo = Depends(get_imobiliaria_repository)):
    db_real_estate = repo.find_one_by_phone(phone)
    if db_real_estate is None:
        raise HTTPException(status_code=404, detail="Real estate not found")
    return db_real_estate