#!/bin/bash

# Script melhorado para inicializar Ollama com TinyLlama

echo "🚀 [$(date)] Iniciando Ollama Service..."

# Função para log com timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Iniciar o Ollama em background
log "Iniciando servidor Ollama..."
ollama serve &
OLLAMA_PID=$!

# Aguardar o Ollama estar pronto (com timeout)
log "Aguardando Ollama ficar pronto..."
TIMEOUT=60
COUNTER=0
while [ $COUNTER -lt $TIMEOUT ]; do
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        log "✅ Ollama está pronto!"
        break
    fi
    sleep 1
    COUNTER=$((COUNTER + 1))
    if [ $((COUNTER % 10)) -eq 0 ]; then
        log "Ainda aguardando... ($COUNTER/$TIMEOUT segundos)"
    fi
done

if [ $COUNTER -eq $TIMEOUT ]; then
    log "❌ Timeout ao aguardar Ollama iniciar"
    exit 1
fi

# Verificar se TinyLlama já está instalado
log "Verificando modelos instalados..."
if ollama list 2>/dev/null | grep -q "tinyllama"; then
    log "✅ TinyLlama já está instalado!"
else
    log "📥 TinyLlama não encontrado. Iniciando download..."
    log "Isso pode demorar alguns minutos (modelo de ~637MB)..."
    
    # Baixar com retry
    RETRY=0
    MAX_RETRY=3
    while [ $RETRY -lt $MAX_RETRY ]; do
        if ollama pull tinyllama:latest; then
            log "✅ TinyLlama baixado com sucesso!"
            break
        else
            RETRY=$((RETRY + 1))
            if [ $RETRY -lt $MAX_RETRY ]; then
                log "⚠️ Falha no download. Tentativa $RETRY de $MAX_RETRY..."
                sleep 5
            else
                log "❌ Falha ao baixar TinyLlama após $MAX_RETRY tentativas"
            fi
        fi
    done
fi

# Listar modelos disponíveis
log "📋 Modelos disponíveis:"
ollama list 2>/dev/null || log "Não foi possível listar modelos"

log "✨ Ollama Service está pronto!"
log "🔄 Mantendo container em execução..."

# Verificar periodicamente se o Ollama está rodando
while true; do
    if ! kill -0 $OLLAMA_PID 2>/dev/null; then
        log "⚠️ Processo Ollama parou. Reiniciando..."
        ollama serve &
        OLLAMA_PID=$!
    fi
    sleep 30
done