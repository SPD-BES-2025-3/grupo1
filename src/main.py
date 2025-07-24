from fastapi import FastAPI
from app.routers import articles, search

# Cria a instância da aplicação FastAPI
app = FastAPI(
    title="API de Busca Semântica de Imóveis",
    description="Uma API para encontrar imóveis com base em descrições em linguagem natural.",
    version="1.0.0",
    contact={
        "name": "Sua Equipe",
        "url": "http://seusite.com",
    },
)

# Inclui os roteadores na aplicação principal
app.include_router(articles.router)
app.include_router(search.router)

@app.get("/", tags=["Root"])
def read_root():
    """Endpoint raiz para verificar se a API está no ar."""
    return {"message": "Bem-vindo à API de Busca Semântica. Acesse /docs para a documentação interativa."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8181, reload=True)
