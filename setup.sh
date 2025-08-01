#!/bin/bash

# 🏠 SPD Imóveis - Script de Inicialização Automática
# Autor: Sistema SPD Imóveis
# Versão: 1.0

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Função para log com timestamp e cores
log() {
    echo -e "${CYAN}[$(date '+%H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')] ✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}[$(date '+%H:%M:%S')] ⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}[$(date '+%H:%M:%S')] ❌ $1${NC}"
}

log_info() {
    echo -e "${BLUE}[$(date '+%H:%M:%S')] ℹ️  $1${NC}"
}

# Banner
show_banner() {
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                                                              ║"
    echo "║               🏠 SPD IMÓVEIS - SETUP AUTOMÁTICO              ║"
    echo "║                                                              ║"
    echo "║        Sistema Inteligente de Busca Semântica               ║"
    echo "║             com IA Gemma3 4B + ChromaDB                     ║"
    echo "║                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Verificar pré-requisitos
check_prerequisites() {
    log "🔍 Verificando pré-requisitos do sistema..."
    
    # Verificar Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker não encontrado. Instale o Docker primeiro:"
        log_info "curl -fsSL https://get.docker.com | sh"
        exit 1
    fi
    log_success "Docker encontrado: $(docker --version | cut -d' ' -f3)"
    
    # Verificar Docker Compose (priorizar plugin nativo)
    if docker compose version &> /dev/null; then
        DOCKER_COMPOSE="docker compose"
        log_success "Docker Compose (plugin) encontrado"
    elif command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE="docker-compose"
        log_success "Docker Compose (standalone) encontrado"
    else
        log_error "Docker Compose não encontrado. Instale o Docker Compose primeiro."
        exit 1
    fi
    
    # Verificar se Docker está rodando
    if ! docker info &> /dev/null; then
        log_error "Docker não está rodando. Inicie o Docker primeiro:"
        log_info "sudo systemctl start docker"
        exit 1
    fi
    log_success "Docker está rodando"
    
    # Verificar recursos do sistema
    TOTAL_RAM=$(free -g | awk '/^Mem:/{print $2}')
    if [ "$TOTAL_RAM" -lt 8 ]; then
        log_warning "Sistema tem apenas ${TOTAL_RAM}GB RAM. Recomendado: 8GB+"
        log_warning "Performance pode ser afetada"
    else
        log_success "RAM disponível: ${TOTAL_RAM}GB"
    fi
    
    # Verificar espaço em disco
    AVAILABLE_SPACE=$(df -BG . | awk 'NR==2{print $4}' | sed 's/G//')
    if [ "$AVAILABLE_SPACE" -lt 10 ]; then
        log_warning "Espaço em disco: ${AVAILABLE_SPACE}GB. Recomendado: 10GB+"
    else
        log_success "Espaço em disco: ${AVAILABLE_SPACE}GB"
    fi
}

# Verificar Ollama local
check_ollama() {
    log "🦾 Verificando instalação do Ollama local..."
    
    if ! command -v ollama &> /dev/null; then
        log_error "Ollama não encontrado no sistema!"
        echo ""
        log_info "Para instalar o Ollama, execute:"
        echo -e "${YELLOW}curl -fsSL https://ollama.com/install.sh | sh${NC}"
        echo ""
        log_info "Após a instalação, execute novamente este script."
        exit 1
    fi
    
    log_success "Ollama encontrado: $(ollama --version 2>/dev/null || echo 'versão não detectada')"
    
    # Verificar se Ollama está rodando
    if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
        log_warning "Ollama não está rodando. Iniciando..."
        ollama serve > /dev/null 2>&1 &
        sleep 3
        
        if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
            log_error "Falha ao iniciar Ollama. Inicie manualmente:"
            log_info "ollama serve"
            exit 1
        fi
    fi
    
    log_success "Ollama está rodando na porta 11434"
    
    # Verificar se Gemma3 4B está instalado
    if ollama list | grep -q "gemma3:4b"; then
        log_success "Gemma3 4B já está instalado"
    else
        log_warning "Gemma3 4B não encontrado. Baixando (~3.3GB)..."
        log_info "Isso pode levar 5-15 minutos dependendo da conexão"
        
        if ollama pull gemma3:4b; then
            log_success "Gemma3 4B baixado com sucesso!"
        else
            log_error "Falha ao baixar Gemma3 4B"
            exit 1
        fi
    fi
}

# Verificar diretório de dados
check_data_directory() {
    log "📁 Verificando diretório de dados dos imóveis..."
    
    # Possíveis localizações do diretório anuncios_salvos
    POSSIBLE_PATHS=(
        "./anuncios_salvos"
        "../anuncios_salvos"
        "$HOME/SPD/anuncios_salvos"
        "${ANUNCIOS_SALVOS_PATH}"
    )
    
    DATA_PATH=""
    for path in "${POSSIBLE_PATHS[@]}"; do
        if [ -d "$path" ] && [ -n "$(ls -A "$path" 2>/dev/null)" ]; then
            DATA_PATH="$path"
            break
        fi
    done
    
    if [ -z "$DATA_PATH" ]; then
        log_error "Diretório 'anuncios_salvos' não encontrado ou vazio!"
        echo ""
        log_info "O sistema procurou nos seguintes locais:"
        for path in "${POSSIBLE_PATHS[@]}"; do
            [ -n "$path" ] && log_info "  - $path"
        done
        echo ""
        log_info "Soluções:"
        log_info "1. Coloque o diretório 'anuncios_salvos' em um dos locais acima"
        log_info "2. Ou defina a variável: export ANUNCIOS_SALVOS_PATH='/seu/caminho'"
        echo ""
        log_info "Estrutura esperada:"
        log_info "anuncios_salvos/"
        log_info "├── 1/"
        log_info "│   ├── info.json"
        log_info "│   └── imagem_*.jpg"
        log_info "└── 2/"
        log_info "    ├── info.json"
        log_info "    └── imagem_*.jpg"
        exit 1
    fi
    
    # Contar arquivos
    JSON_COUNT=$(find "$DATA_PATH" -name "info.json" | wc -l)
    IMG_COUNT=$(find "$DATA_PATH" -name "imagem_*.jpg" 2>/dev/null | wc -l)
    
    log_success "Diretório encontrado: $DATA_PATH"
    log_success "Arquivos JSON: $JSON_COUNT"
    log_success "Imagens: $IMG_COUNT"
    
    if [ "$JSON_COUNT" -eq 0 ]; then
        log_error "Nenhum arquivo info.json encontrado!"
        exit 1
    fi
    
    # Exportar path para uso posterior
    export ANUNCIOS_SALVOS_PATH="$(realpath "$DATA_PATH")"
}

# Iniciar serviços Docker
start_docker_services() {
    log "🐳 Iniciando serviços Docker..."
    
    # Parar containers existentes se houver
    if docker ps -q --filter "name=spd_" | grep -q .; then
        log "🛑 Parando containers existentes..."
        docker stop $(docker ps -q --filter "name=spd_") 2>/dev/null || true
        docker rm $(docker ps -aq --filter "name=spd_") 2>/dev/null || true
    fi
    
    # Limpar redes e volumes órfãos
    docker network prune -f &>/dev/null || true
    
    # Subir serviços
    log "🚀 Subindo todos os serviços..."
    if $DOCKER_COMPOSE up -d; then
        log_success "Serviços Docker iniciados com sucesso"
    else
        log_error "Falha ao iniciar serviços Docker"
        exit 1
    fi
    
    # Aguardar serviços ficarem prontos
    log "⏳ Aguardando serviços ficarem prontos (60s)..."
    sleep 30
    
    # Verificar se serviços estão saudáveis
    check_services_health
}

# Verificar saúde dos serviços
check_services_health() {
    log "🏥 Verificando saúde dos serviços..."
    
    SERVICES=("mongodb:27017" "chromadb:7777" "redis:6890")
    
    for service in "${SERVICES[@]}"; do
        name=$(echo $service | cut -d: -f1)
        port=$(echo $service | cut -d: -f2)
        
        if docker exec $(docker ps -q --filter "name=$name") curl -s http://localhost:$port &>/dev/null 2>&1 || \
           nc -z localhost $port &>/dev/null 2>&1; then
            log_success "$name está saudável"
        else
            log_warning "$name pode não estar totalmente pronto"
        fi
    done
    
    # Verificar API
    sleep 10
    if curl -s http://localhost:8001/ | grep -q "SPD.*API"; then
        log_success "API está respondendo"
    else
        log_warning "API pode não estar totalmente pronta"
    fi
    
    # Verificar Streamlit
    if curl -s http://localhost:8501 &>/dev/null; then
        log_success "Interface Streamlit está acessível"
    else
        log_warning "Interface Streamlit pode não estar totalmente pronta"
    fi
}

# Carregar dados no sistema
load_system_data() {
    log "📊 Carregando dados dos imóveis no sistema..."
    
    if [ -f "docker_seed.py" ]; then
        log "🔄 Executando script de carregamento dos dados via API..."
        
        if python3 docker_seed.py; then
            log_success "Sistema inicializado com dados limpos!"
            log_info "• Dados anteriores removidos do MongoDB e ChromaDB"
            log_info "• 200 imóveis carregados do diretório anuncios_salvos"
            log_info "• Embeddings gerados e indexados no ChromaDB"
        else
            log_error "Falha ao carregar dados"
            log_info "Verifique os logs acima para mais detalhes"
            log_info "Você pode carregar manualmente executando: python3 docker_seed.py"
        fi
    elif [ -f "seed.py" ]; then
        log "🔄 Executando script de inicialização dos dados..."
        
        if python3 seed.py; then
            log_success "Dados carregados com sucesso no MongoDB e ChromaDB!"
        else
            log_error "Falha ao carregar dados"
            log_info "Verifique os logs acima para mais detalhes"
            log_info "O sistema pode ainda funcionar parcialmente"
        fi
    else
        log_warning "Scripts de inicialização não encontrados"
        log_info "Você precisará carregar os dados manualmente"
    fi
}

# Exibir informações finais
show_final_info() {
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                                                              ║${NC}"
    echo -e "${GREEN}║                   🎉 SETUP CONCLUÍDO! 🎉                    ║${NC}"
    echo -e "${GREEN}║                                                              ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    log_success "Sistema SPD Imóveis está pronto para uso!"
    echo ""
    
    echo -e "${BLUE}📋 INFORMAÇÕES DE ACESSO:${NC}"
    echo -e "${CYAN}┌─────────────────────────────────────────────────────────────┐${NC}"
    echo -e "${CYAN}│ 🖥️  Interface Principal: ${YELLOW}http://localhost:8501${CYAN}           │${NC}"
    echo -e "${CYAN}│ 📚 Documentação da API: ${YELLOW}http://localhost:8001/docs${CYAN}      │${NC}"  
    echo -e "${CYAN}│ ⚡ API Endpoints:       ${YELLOW}http://localhost:8001${CYAN}           │${NC}"
    echo -e "${CYAN}│ 🤖 Ollama Local:        ${YELLOW}http://localhost:11434${CYAN}          │${NC}"
    echo -e "${CYAN}│ 🔗 LLM Reranking:       ${YELLOW}Gemma3 4B (Funcionando)${CYAN}       │${NC}"
    echo -e "${CYAN}└─────────────────────────────────────────────────────────────┘${NC}"
    echo ""
    
    echo -e "${BLUE}🔧 COMANDOS ÚTEIS:${NC}"
    echo -e "${CYAN}┌─────────────────────────────────────────────────────────────┐${NC}"
    echo -e "${CYAN}│ Ver logs da API:        ${YELLOW}docker logs api -f${CYAN}              │${NC}"
    echo -e "${CYAN}│ Ver logs do Streamlit:  ${YELLOW}docker logs spd_streamlit -f${CYAN}    │${NC}"
    echo -e "${CYAN}│ Parar sistema:          ${YELLOW}docker compose down${CYAN}             │${NC}"
    echo -e "${CYAN}│ Reiniciar sistema:      ${YELLOW}docker compose restart${CYAN}          │${NC}"
    echo -e "${CYAN}│ Ver status containers:  ${YELLOW}docker ps${CYAN}                       │${NC}"
    echo -e "${CYAN}└─────────────────────────────────────────────────────────────┘${NC}"
    echo ""
    
    echo -e "${BLUE}🎯 COMO USAR:${NC}"
    echo -e "${CYAN}1. Acesse ${YELLOW}http://localhost:8501${CYAN} no seu navegador${NC}"
    echo -e "${CYAN}2. Digite sua busca: ${YELLOW}'apartamento 2 quartos bueno'${NC}"
    echo -e "${CYAN}3. Clique em ❤️ (gostei) ou ❌ (não gostei) nos imóveis${NC}"
    echo -e "${CYAN}4. A IA Gemma3 4B aprenderá suas preferências!${NC}"
    echo ""
    
    if [ -n "$ANUNCIOS_SALVOS_PATH" ]; then
        log_info "Dados carregados de: $ANUNCIOS_SALVOS_PATH"
    fi
    
    echo -e "${GREEN}🏠 Encontre seu imóvel ideal com inteligência artificial! 🤖${NC}"
}

# Função principal
main() {
    show_banner
    
    log "🚀 Iniciando setup do SPD Imóveis..."
    echo ""
    
    # Executar verificações e instalação
    check_prerequisites
    echo ""
    
    check_ollama
    echo ""
    
    check_data_directory
    echo ""
    
    start_docker_services
    echo ""
    
    load_system_data
    echo ""
    
    show_final_info
}

# Verificar se script está sendo executado diretamente
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # Capturar Ctrl+C
    trap 'echo -e "\n${RED}❌ Setup interrompido pelo usuário${NC}"; exit 1' INT
    
    # Executar função principal
    main "$@"
fi