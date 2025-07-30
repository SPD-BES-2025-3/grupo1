import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from main import app

@pytest.fixture
def client():
    """Cliente de teste para a API FastAPI"""
    return TestClient(app)

@pytest.fixture
def mock_mongo_repo():
    """Mock do repositório MongoDB"""
    mock = Mock()
    return mock

@pytest.fixture
def mock_chroma_repo():
    """Mock do repositório ChromaDB"""
    mock = Mock()
    return mock

@pytest.fixture
def sample_imovel():
    """Imóvel de exemplo para testes"""
    return {
        "titulo": "Apartamento no Setor Bueno",
        "descricao": "Excelente apartamento com 3 quartos",
        "especificacoes": ["3 quartos", "2 banheiros", "100m²"]
    }

@pytest.fixture
def sample_imovel_in_db():
    """Imóvel de exemplo com ID (como vem do banco)"""
    return {
        "id": "507f1f77bcf86cd799439011",
        "titulo": "Apartamento no Setor Bueno",
        "descricao": "Excelente apartamento com 3 quartos",
        "especificacoes": ["3 quartos", "2 banheiros", "100m²"]
    }

@pytest.fixture
def sample_corretor():
    """Corretor de exemplo para testes"""
    return {
        "nome": "João Silva",
        "email": "joao@example.com",
        "telefone": "(62) 99999-9999",
        "creci": "12345-GO",
        "ativo": True,
        "especialidades": ["Residencial", "Comercial"],
        "cidades_atendidas": ["507f1f77bcf86cd799439011"]
    }

@pytest.fixture
def sample_corretor_in_db():
    """Corretor de exemplo com ID"""
    return {
        "id": "507f1f77bcf86cd799439012",
        "nome": "João Silva",
        "email": "joao@example.com",
        "telefone": "(62) 99999-9999",
        "creci": "12345-GO",
        "ativo": True,
        "especialidades": ["Residencial", "Comercial"],
        "cidades_atendidas": ["507f1f77bcf86cd799439011"]
    }

@pytest.fixture
def sample_cidade():
    """Cidade de exemplo para testes"""
    return {
        "nome": "Goiânia",
        "estado": "GO",
        "regiao": "Centro-Oeste",
        "populacao": 1500000,
        "area_km2": 739.5
    }

@pytest.fixture
def sample_cidade_in_db():
    """Cidade de exemplo com ID"""
    return {
        "id": "507f1f77bcf86cd799439013",
        "nome": "Goiânia",
        "estado": "GO",
        "regiao": "Centro-Oeste",
        "populacao": 1500000,
        "area_km2": 739.5
    }