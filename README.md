# 🏠 SPD Imóveis - Sistema Inteligente de Busca Semântica

Um sistema completo de busca semântica de imóveis com reranking inteligente baseado em LLM, desenvolvido com FastAPI, Streamlit e ChromaDB.

## 🎯 Características Principais

- **🔍 Busca Semântica**: Encontre imóveis usando linguagem natural
- **🤖 Reranking Inteligente**: IA analisa suas preferências com Gemma3 4B
- **📊 Interface Moderna**: Dashboard intuitivo em Streamlit
- **⚡ Performance**: Vectorização com ChromaDB + embeddings otimizados
- **🐳 Containerização**: Deploy simplificado com Docker
- **🔄 Integração**: API REST completa com documentação automática

## 🏗️ Arquitetura do Sistema

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

## 🚀 Tecnologias Utilizadas

### Backend
- **FastAPI**: Framework web moderno e rápido
- **Python 3.11**: Linguagem principal
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
- **Plotly**: Visualizações e gráficos
- **Bootstrap**: Componentes UI responsivos

### DevOps
- **Docker**: Containerização
- **Docker Compose**: Orquestração de serviços
- **GitHub Actions**: CI/CD (configurável)

## 📋 Pré-requisitos

- **Docker** e **Docker Compose** instalados
- **8GB RAM** disponível (6GB para Gemma3 4B + 2GB sistema)
- **5GB espaço em disco** (modelo + dados)
- **Ollama instalado localmente** com Gemma3 4B

### Instalação do Ollama Local

```bash
# Instalar Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Baixar Gemma3 4B
ollama pull gemma3:4b

# Verificar instalação
ollama list
```

## 🛠️ Instalação e Configuração

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
# Subir todos os serviços
docker-compose up -d

# Aguardar inicialização (30-60 segundos)

# Carregar dados e testar
python init_and_test_system.py
```

## 🌐 Acesso ao Sistema

| Serviço | URL | Descrição |
|---------|-----|-----------|
| 🖥️ **Interface Principal** | http://localhost:8501 | Dashboard Streamlit |
| 📚 **API Documentation** | http://localhost:8001/docs | Swagger/OpenAPI |
| 🔍 **API Endpoint** | http://localhost:8001/search | Busca semântica |
| 🤖 **Ollama Local** | http://localhost:11434 | Servidor LLM |

## 💡 Como Usar

### 1. Busca Básica

1. Acesse http://localhost:8501
2. Digite sua busca: "apartamento 2 quartos Bueno"
3. Veja os resultados rankeados por relevância

### 2. Reranking Inteligente

1. Faça uma busca inicial
2. Clique em ❤️ (gostei) ou ❌ (não gostei) nos imóveis
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

## 🧠 Funcionamento da IA

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

## 🐛 Troubleshooting

### Problemas Comuns

**❌ "Erro de conexão com API"**
```bash
# Verificar se API está rodando
curl http://localhost:8001/
docker logs api -f
```

**❌ "Parse da resposta LLM falhou"**
```bash
# Verificar se Ollama está ativo
ollama list
curl http://localhost:11434/api/tags
```

**❌ "anuncios_salvos não encontrado"**
```bash
# Definir path manualmente
export ANUNCIOS_SALVOS_PATH="/seu/caminho"
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

## 📊 Métricas e Monitoramento

- **Tempo de Resposta**: < 200ms para buscas
- **Acurácia**: Similarity score > 0.7
- **Throughput**: 100+ consultas/minuto
- **Cache Hit Rate**: 80%+ com Redis

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/nova-funcionalidade`
3. Commit: `git commit -m 'Add nova funcionalidade'`
4. Push: `git push origin feature/nova-funcionalidade`
5. Abra Pull Request


**🏠 SPD Imóveis** - Encontre seu imóvel ideal com inteligência artificial