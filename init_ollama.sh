#!/bin/bash

# Script para inicializar Ollama com modelo leve

echo "🚀 Inicializando Ollama com TinyLlama..."

# Aguardar Ollama estar pronto
echo "⏳ Aguardando Ollama iniciar..."
until curl -s http://localhost:11435/api/tags > /dev/null 2>&1
do
    echo -n "."
    sleep 2
done
echo " ✅"

# Verificar se TinyLlama já está instalado
if curl -s http://localhost:11435/api/tags | grep -q "tinyllama"
then
    echo "✅ TinyLlama já está instalado!"
else
    echo "📥 Baixando TinyLlama (modelo leve - ~637MB)..."
    docker exec ollama_service ollama pull tinyllama:latest
    echo "✅ TinyLlama instalado com sucesso!"
fi

echo "📊 Modelos disponíveis:"
curl -s http://localhost:11435/api/tags | jq -r '.models[] | .name'

echo "✨ Ollama pronto para uso com TinyLlama!"