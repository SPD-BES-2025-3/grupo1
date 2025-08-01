from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.app.routers import imoveis, search, corretores, cidades
from src.app.services.ollama_health_service import OllamaHealthService
import logging

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Iniciando SPD Imóveis API...")
    
    # Verificar e iniciar Ollama se necessário
    ollama_service = OllamaHealthService()
    if not ollama_service.start_ollama_if_needed():
        logger.warning("⚠️ Ollama não pôde ser iniciado - funcionalidades de LLM podem não funcionar")
    else:
        status = ollama_service.get_ollama_status()
        logger.info(f"✅ Ollama configurado: {status['models']}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Finalizando SPD Imóveis API...")

app = FastAPI(
    title="SPD Imóveis API", 
    description="API de busca semântica de imóveis",
    lifespan=lifespan
)

app.include_router(imoveis.router)
app.include_router(search.router)
app.include_router(corretores.router)
app.include_router(cidades.router)

@app.get("/")
def root():
    return {"message": "SPD Imóveis API - Busca Semântica de Imóveis"}

@app.get("/health/ollama")
def ollama_health():
    """Endpoint para verificar status do Ollama."""
    ollama_service = OllamaHealthService()
    return ollama_service.get_ollama_status()
