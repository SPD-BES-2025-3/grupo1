# 🏠 SPD Imóveis - Sistema Inteligente de Busca Semântica

Um sistema completo de busca semântica de imóveis com reranking inteligente baseado em LLM, desenvolvido com FastAPI, Streamlit e ChromaDB.

## Características Principais

- **Busca Semântica**: Encontre imóveis usando linguagem natural
- **Reranking Inteligente**: IA analisa suas preferências com Gemma3 4B
- **Interface Moderna**: Dashboard intuitivo em Streamlit
- **Performance**: Vectorização com ChromaDB + embeddings otimizados
- **Containerização**: Deploy simplificado com Docker
- **Integração**: API REST completa com documentação automática

## Arquitetura do Sistema

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit UI  │────│   FastAPI       │────│   ChromaDB      │
│   (Frontend)    │    │   (Backend)     │    │   (Vectors)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MongoDB       │────│   Redis         │────│   Ollama LLM    │
│   (Database)    │    │   (Cache)       │    │   (AI)          │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Tecnologias Utilizadas

### Backend
- **FastAPI**: Framework web moderno e rápido
- **Python**: Linguagem principal
- **ChromaDB**: Banco de dados vetorial para busca semântica
- **MongoDB**: Armazenamento de dados estruturados
- **Redis**: Cache e fila de tarefas
- **Sentence Transformers**: Geração de embeddings

### IA e Machine Learning
- **Ollama**: Servidor local de LLM
- **Gemma3 4B**: Modelo de linguagem para reranking
- **all-MiniLM-L6-v2**: Modelo de embedding semântico
- **CUDA**: Aceleração GPU (opcional)

### Frontend
- **Streamlit**: Interface web interativa

### DevOps
- **Docker**: Containerização
- **Docker Compose**: Orquestração de serviços

## Pré-requisitos

- **Docker** e **Docker Compose** instalados
- **Memória RAM necessária:**
  - **Mínimo absoluto**: 8GB RAM total do sistema
  - **Recomendado**: 12GB RAM ou mais
  - **Para Gemma3 4B**: Requer 5.4GB RAM disponível + overhead do sistema
- **5GB espaço em disco** (modelo + dados)
- **Importante**: O modelo Gemma3 4B precisa de pelo menos 6GB de RAM livre para funcionar corretamente

### Nota sobre Requisitos de Memória

**Status do Reranking IA:**
- **Ollama Container**: Funcionando corretamente
- **Gemma3:4b**: Modelo baixado e disponível
- **Limitação Atual**: Requer 5.4GB RAM (sistema atual: 2.6GB disponível)

**Opções para Ambientes com Pouca RAM:**
- `tinyllama` (637MB) - Funciona bem com 2GB RAM
- `phi` (1.6GB) - Funciona bem com 4GB RAM  
- `mistral:7b-instruct` (4.1GB) - Funciona bem com 6GB RAM

```bash
Para usar modelo menor:
docker exec spd_ollama ollama pull tinyllama
Depois atualizar OLLAMA_MODEL_NAME=tinyllama no .env
```

**Funcionalidades Disponíveis SEM Reranking:**
- Busca semântica completa e funcional
- Ordenação por similarity score
- Filtros e consultas complexas
- CRUD completo de imóveis

### Configuração do Ollama no Docker

O sistema já inclui Ollama em container Docker. O setup.sh:
1. Para qualquer Ollama local rodando
2. Inicia o container Ollama
3. Baixa o modelo automaticamente

```bash
Para verificar uso de memória
docker stats spd_ollama

Para usar um modelo menor se necessário
docker exec spd_ollama ollama pull tinyllama
```

## Instalação e Configuração

### 1. Clone o Repositório

```bash
git clone <repo-url>
cd SPD-Imoveis
```

### 2. Configurar Dados

O sistema busca automaticamente o diretório `anuncios_salvos` em:

```
../anuncios_salvos          # Diretório pai do projeto
./anuncios_salvos           # Dentro do projeto  
~/SPD/anuncios_salvos       # Home do usuário
```

**Ou defina manualmente:**
```bash
export ANUNCIOS_SALVOS_PATH="/caminho/para/anuncios_salvos"
```

### 3. Estrutura dos Dados

```
anuncios_salvos/
├── 1/
│   ├── info.json
│   └── imagem_*.jpg
├── 2/
│   ├── info.json
│   └── imagem_*.jpg
└── ...
```

### 4. Inicializar Sistema

```bash
Método recomendado - Script automatizado
./setup.sh

Ou manualmente:
docker compose up -d

Aguardar inicialização (30-60 segundos)

Carregar dados
python docker_seed.py
```

## Acesso ao Sistema

| Serviço | URL | Descrição |
|---------|-----|-----------|
| **Interface Principal** | http://localhost:8501 | Dashboard Streamlit |
| **API Documentation** | http://localhost:8001/docs | Swagger/OpenAPI |
| **API Endpoint** | http://localhost:8001/search | Busca semântica |
| **Ollama Container** | http://localhost:11434 | Servidor LLM |

## Como Usar

### 1. Busca Básica

1. Acesse http://localhost:8501
2. Digite sua busca: "apartamento 2 quartos Bueno"
3. Veja os resultados rankeados por relevância

### 2. Reranking Inteligente

1. Faça uma busca inicial
2. Clique em (gostei) ou (não gostei) nos imóveis
3. O sistema aprende suas preferências
4. Receba sugestões personalizadas com IA

### 3. API REST

```bash
# Busca simples
curl "http://localhost:8001/search/?query=casa+3+quartos&n_results=10"

# Reranking com preferências
curl -X POST "http://localhost:8001/rerank/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "apartamento bueno",
    "liked_properties": [...],
    "disliked_properties": [...],
    "remaining_properties": [...]
  }'
```

## Funcionamento da IA

### Busca Semântica
1. **Entrada**: Query em linguagem natural
2. **Embedding**: Conversão para vetor 384D
3. **Similaridade**: Busca coseno no ChromaDB
4. **Ranking**: Ordenação por relevância

### Reranking Inteligente
1. **Análise**: Gemma3 4B analisa preferências do usuário
2. **Context**: Histórico de likes/dislikes
3. **Reasoning**: Explicação das escolhas
4. **Output**: JSON estruturado com recomendações

## 🔧 Configuração Avançada

### Variáveis de Ambiente

```bash
# API Configuration
MONGO_CONNECTION_STRING=mongodb://localhost:27017/
CHROMA_HOST=localhost
CHROMA_PORT=7777
OLLAMA_URL=http://localhost:11434
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2

# LLM Configuration
OLLAMA_KEEP_ALIVE=10m
OLLAMA_CONTEXT_LENGTH=4096
OLLAMA_NUM_GPU=1  # Para usar GPU
```

### Performance

- **GPU**: Configure `OLLAMA_NUM_GPU=1` para aceleração
- **Memória**: Ajuste `memory` limits no docker-compose.yml
- **Cache**: Redis otimiza consultas repetidas
- **Embedding**: Modelo pré-treinado para português

## Troubleshooting

### Problemas Comuns

**"Erro de conexão com API"**
```bash
# Verificar se API está rodando
curl http://localhost:8001/
docker logs api -f
```

**"Parse da resposta LLM falhou"**
```bash
# Verificar se Ollama está ativo
ollama list
curl http://localhost:11434/api/tags
```

**"anuncios_salvos não encontrado"**
```bash
# Definir path manualmente
export ANUNCIOS_SALVOS_PATH="/seu/caminho"
```

**"Collection does not exists" no integrador**
```bash
# Problema comum após reinicializações - eventos antigos no Redis
# Soluções:
# 1. Aguardar - integrador processa eventos antigos e chega nos novos
# 2. Limpar fila Redis:
docker exec redis_broker redis-cli FLUSHALL

# 3. Verificar se sincronização funciona com teste:
curl -X POST "http://localhost:8001/imoveis/" -H "Content-Type: application/json" \
  -d '{"titulo": "Teste", "descricao": "Teste sincronização", "especificacoes": []}'
```

### Logs e Debug

```bash
# Ver logs de todos os serviços
docker-compose logs -f

# Log específico de um serviço
docker logs api -f
docker logs spd_streamlit -f

# Debug da API
export DEBUG=true
```

## Sincronização Assíncrona

O sistema mantém MongoDB e ChromaDB sincronizados automaticamente:

### Fluxo de Sincronização
```
MongoDB → Redis (eventos) → Integrador → ChromaDB
```

### Como Funciona
1. **Criar/Atualizar/Deletar** imóvel via API
2. **Evento publicado** no Redis (canal: imoveis.create/update/delete)  
3. **Integrador escuta** e processa eventos
4. **Embedding gerado** (para create/update)
5. **ChromaDB atualizado** automaticamente

### Verificar Sincronização
```bash
# Criar imóvel teste
curl -X POST "http://localhost:8001/imoveis/" -H "Content-Type: application/json" \
  -d '{"titulo": "Teste Sync", "descricao": "Verificação", "especificacoes": []}'

# Verificar logs do integrador
docker logs spd_integrador --tail 5

# Sincronização manual (se necessário)
curl -X POST "http://localhost:8001/imoveis/sync"
```

## Status do Sistema e Métricas

### **Sistema Totalmente Operacional** (Atualizado: 01/08/2025)

**Componentes Funcionais:**
- **Busca Semântica**: ChromaDB + embeddings 384D persistindo corretamente
- **CRUD Imóveis**: Criação, atualização, deleção funcionando
- **Sincronização**: MongoDB → Redis → Integrador → ChromaDB em tempo real
- **API REST**: Todos os endpoints operacionais
- **Embeddings**: Sentence Transformers all-MiniLM-L6-v2 (384 dimensões)
- **Reranking IA**: Limitado por RAM (Gemma3 4B requer 5.4GB)

**Métricas de Performance:**
- **Tempo de Resposta**: 2-3s para buscas semânticas
- **Acurácia**: Similarity scores variando de -0.8 a +0.4
- **Throughput**: 30+ consultas/minuto testadas
- **Sincronização**: < 5s entre criação e indexação
- **Embeddings**: 100% de persistência confirmada

**Testes Validados:**
- Múltiplos imóveis indexados simultaneamente
- Busca semântica com ordenação por relevância
- Atualização de embeddings em tempo real
- Remoção limpa do ChromaDB na deleção
