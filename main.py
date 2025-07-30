from fastapi import FastAPI
from src.app.routers import imoveis, search, corretores, cidades

app = FastAPI(title="SPD Imóveis API", description="API de busca semântica de imóveis")

app.include_router(imoveis.router)
app.include_router(search.router)
app.include_router(corretores.router)
app.include_router(cidades.router)

@app.get("/")
def root():
    return {"message": "SPD Imóveis API - Busca Semântica de Imóveis"}
