#!/bin/bash

# Script para executar os testes

echo "🧪 Executando testes da API SPD Imóveis..."

# Instalar dependências de teste
echo "📦 Instalando dependências de teste..."
pip install -r requirements-test.txt

# Executar testes com coverage
echo "🏃 Executando testes com cobertura..."
cd src
python -m pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html

# Verificar resultado
if [ $? -eq 0 ]; then
    echo "✅ Todos os testes passaram!"
    echo "📊 Relatório de cobertura disponível em: src/htmlcov/index.html"
else
    echo "❌ Alguns testes falharam. Verifique os logs acima."
    exit 1
fi