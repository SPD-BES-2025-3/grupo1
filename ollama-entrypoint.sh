#!/bin/bash

# Iniciar o Ollama em background
ollama serve &

# Aguardar o Ollama estar pronto
echo "Aguardando Ollama iniciar..."
until curl -s http://localhost:11434/api/tags > /dev/null 2>&1
do
    sleep 1
done

echo "Ollama iniciado! Baixando TinyLlama..."

# Baixar o modelo TinyLlama
ollama pull tinyllama:latest

echo "TinyLlama baixado com sucesso!"

# Manter o container rodando
wait