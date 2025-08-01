# 🏗️ Arquitetura do Sistema SPD Imóveis

## 📋 Visão Geral da Arquitetura

```mermaid
graph TB
    %% Frontend Layer
    subgraph "Frontend Layer"
        UI[🖥️ Streamlit UI<br/>Interface Web]
        WEB[🌐 Web Browser<br/>Cliente]
    end
    
    %% API Layer
    subgraph "API Layer"
        API[⚡ FastAPI<br/>REST API]
        DOCS[📚 Swagger/OpenAPI<br/>Documentação]
    end
    
    %% Business Logic Layer
    subgraph "Business Logic Layer"
        SEARCH[🔍 Search Service<br/>Busca Semântica]
        RERANK[🤖 LLM Reranking<br/>Inteligência Artificial]
        EMBED[🧠 Embedding Service<br/>Vetorização]
    end
    
    %% Data Layer
    subgraph "Data Layer"
        MONGO[(🗄️ MongoDB<br/>Dados Estruturados)]
        CHROMA[(🔮 ChromaDB<br/>Vetores/Embeddings)]
        REDIS[(⚡ Redis<br/>Cache)]
    end
    
    %% AI/ML Layer
    subgraph "AI/ML Layer"
        OLLAMA[🦾 Ollama<br/>Servidor LLM Local]
        GEMMA[🧠 Gemma3 4B<br/>Modelo de Linguagem]
        SENTENCE[📝 SentenceTransformers<br/>all-MiniLM-L6-v2]
    end
    
    %% External Layer
    subgraph "External Data"
        FILES[📁 anuncios_salvos<br/>Arquivos JSON/Imagens]
    end
    
    %% Connections
    WEB --> UI
    UI --> API
    API --> DOCS
    
    API --> SEARCH
    API --> RERANK
    API --> EMBED
    
    SEARCH --> CHROMA
    SEARCH --> MONGO
    SEARCH --> REDIS
    
    RERANK --> OLLAMA
    EMBED --> SENTENCE
    
    OLLAMA --> GEMMA
    
    MONGO --> FILES
    CHROMA --> SENTENCE
    
    %% Styling
    classDef frontend fill:#e1f5fe
    classDef api fill:#f3e5f5
    classDef business fill:#e8f5e8
    classDef data fill:#fff3e0
    classDef ai fill:#fce4ec
    classDef external fill:#f1f8e9
    
    class UI,WEB frontend
    class API,DOCS api
    class SEARCH,RERANK,EMBED business
    class MONGO,CHROMA,REDIS data
    class OLLAMA,GEMMA,SENTENCE ai
    class FILES external
```

## 🔄 Fluxo de Dados Principal

### 1. Busca Semântica
```mermaid
sequenceDiagram
    participant U as 👤 Usuário
    participant ST as 🖥️ Streamlit
    participant API as ⚡ FastAPI
    participant ES as 🔍 EmbedService
    participant CD as 🔮 ChromaDB
    participant MD as 🗄️ MongoDB
    participant RD as ⚡ Redis
    
    U->>ST: "apartamento 2 quartos bueno"
    ST->>API: GET /search?query=...
    
    API->>RD: Verificar cache
    alt Cache Hit
        RD-->>API: Resultados em cache
    else Cache Miss
        API->>ES: Gerar embedding da query
        ES-->>API: Vetor 384D
        API->>CD: Busca por similaridade
        CD-->>API: IDs dos imóveis similares
        API->>MD: Buscar dados completos
        MD-->>API: Informações detalhadas
        API->>RD: Armazenar em cache
    end
    
    API-->>ST: Lista de imóveis rankeados
    ST-->>U: Exibir resultados
```

### 2. Reranking Inteligente
```mermaid
sequenceDiagram
    participant U as 👤 Usuário
    participant ST as 🖥️ Streamlit
    participant API as ⚡ FastAPI
    participant LLM as 🤖 LLMService
    participant OL as 🦾 Ollama
    participant GM as 🧠 Gemma3 4B
    
    U->>ST: ❤️ Curtir imóvel A<br/>❌ Rejeitar imóvel B
    ST->>API: POST /rerank
    Note over ST,API: {liked: [A], disliked: [B],<br/>remaining: [C,D,E]}
    
    API->>LLM: Analisar preferências
    LLM->>OL: Enviar prompt estruturado
    OL->>GM: Processar com Gemma3 4B
    GM-->>OL: Resposta JSON
    OL-->>LLM: {"selected_properties": [...]}
    LLM->>LLM: Parse e validação
    LLM-->>API: Resultado estruturado
    
    API-->>ST: Imóveis rerankeados + explicação
    ST-->>U: "IA selecionou 2 imóveis:<br/>Motivo: Similar ao que você curtiu"
```

## 🏛️ Padrões Arquiteturais

### Clean Architecture
```mermaid
graph TB
    subgraph "🎯 Domain Layer (Core)"
        ENT[📦 Entities<br/>Property, User, Search]
        REPO[🔌 Repository Interfaces<br/>IPropertyRepo, ISearchRepo]
    end
    
    subgraph "💼 Application Layer"
        UC[⚙️ Use Cases<br/>SearchProperties, RerankResults]
        DTO[📄 DTOs<br/>SearchRequest, Property]
    end
    
    subgraph "🏗️ Infrastructure Layer"
        MONGO_REPO[🗄️ MongoPropertyRepo]
        CHROMA_REPO[🔮 ChromaSearchRepo]
        OLLAMA_SERV[🤖 OllamaLLMService]
    end
    
    subgraph "🎨 Presentation Layer"
        CTRL[🎮 Controllers<br/>SearchController]
        UI_STREAM[🖥️ Streamlit Pages]
    end
    
    %% Dependencies (pointing inward)
    CTRL --> UC
    UI_STREAM --> UC
    UC --> REPO
    UC --> ENT
    
    MONGO_REPO -.-> REPO
    CHROMA_REPO -.-> REPO
    OLLAMA_SERV -.-> REPO
    
    classDef domain fill:#ff9999
    classDef application fill:#99ccff
    classDef infrastructure fill:#99ff99
    classDef presentation fill:#ffcc99
    
    class ENT,REPO domain
    class UC,DTO application
    class MONGO_REPO,CHROMA_REPO,OLLAMA_SERV infrastructure
    class CTRL,UI_STREAM presentation
```

### Microserviços e Responsabilidades

```mermaid
graph LR
    subgraph "🔍 Search Service"
        S1[Embedding Generation]
        S2[Vector Search]
        S3[Result Ranking]
    end
    
    subgraph "🤖 AI Service"
        A1[Preference Analysis]
        A2[LLM Communication]
        A3[Response Parsing]
    end
    
    subgraph "📊 Data Service"
        D1[Property CRUD]
        D2[Cache Management]
        D3[File Processing]
    end
    
    subgraph "🎨 Presentation Service"
        P1[Web Interface]
        P2[API Documentation]
        P3[User Interaction]
    end
    
    P1 --> S1
    P1 --> A1
    P1 --> D1
    
    S1 --> D2
    A1 --> A2
    D1 --> D3
```

## 🔧 Configuração de Deploy

### Docker Networking
```mermaid
graph TB
    subgraph "🌐 Host Network"
        HOST[🖥️ Host Machine<br/>localhost]
        OLLAMA_LOCAL[🦾 Ollama Local<br/>:11434]
    end
    
    subgraph "🐳 Docker Network: grupo1_default"
        API[⚡ FastAPI<br/>api:8001]
        UI[🖥️ Streamlit<br/>spd_streamlit:8501]
        MONGO[🗄️ MongoDB<br/>mongodb:27017]
        CHROMA[🔮 ChromaDB<br/>chromadb:7777]
        REDIS[⚡ Redis<br/>redis:6379]
    end
    
    %% Host networking for AI components
    API -.->|host.docker.internal| OLLAMA_LOCAL
    UI -.->|localhost:8001| API
    
    %% Internal Docker networking
    API --> MONGO
    API --> CHROMA
    API --> REDIS
    
    %% External access
    HOST --> UI
    HOST --> API
```

### Volumes e Persistência
```mermaid
graph LR
    subgraph "💾 Docker Volumes"
        V1[mongo_data]
        V2[chroma_data]
        V3[redis_data]
        V4[ollama_data]
    end
    
    subgraph "📁 Host Bind Mounts"
        H1[./chroma_db]
        H2[./models]
        H3[./anuncios_salvos]
    end
    
    subgraph "🐳 Containers"
        C1[MongoDB]
        C2[ChromaDB]
        C3[Redis]
        C4[API]
        C5[Ollama]
    end
    
    V1 --- C1
    V2 --- C2
    V3 --- C3
    V4 --- C5
    
    H1 --- C4
    H2 --- C4
    H3 --- C4
```

## 📈 Escalabilidade e Performance

### Horizontal Scaling
```mermaid
graph TB
    subgraph "⚖️ Load Balancer"
        LB[🔄 nginx/HAProxy]
    end
    
    subgraph "🔄 API Replicas"
        API1[⚡ API Instance 1]
        API2[⚡ API Instance 2]
        API3[⚡ API Instance 3]
    end
    
    subgraph "🧠 AI Pool"
        AI1[🤖 Ollama + GPU 1]
        AI2[🤖 Ollama + GPU 2]
    end
    
    subgraph "💾 Data Layer"
        MONGO_CLUSTER[(🗄️ MongoDB Cluster)]
        CHROMA_CLUSTER[(🔮 ChromaDB Cluster)]
        REDIS_CLUSTER[(⚡ Redis Cluster)]
    end
    
    LB --> API1
    LB --> API2
    LB --> API3
    
    API1 --> AI1
    API2 --> AI2
    API3 --> AI1
    
    API1 --> MONGO_CLUSTER
    API2 --> MONGO_CLUSTER
    API3 --> MONGO_CLUSTER
    
    API1 --> CHROMA_CLUSTER
    API2 --> CHROMA_CLUSTER
    API3 --> CHROMA_CLUSTER
    
    API1 --> REDIS_CLUSTER
    API2 --> REDIS_CLUSTER
    API3 --> REDIS_CLUSTER
```

### Otimizações Implementadas

1. **🚀 Cache Strategy**
   - Redis para consultas frequentes
   - TTL configurável por tipo de dados
   - Cache warming para queries populares

2. **🔮 Vector Optimization**
   - Embeddings pré-computados
   - Índices otimizados no ChromaDB
   - Batch processing para novos dados

3. **🤖 AI Optimization**
   - Modelo local para baixa latência
   - Context window otimizado
   - Response streaming quando possível

4. **📊 Database Tuning**
   - Índices compostos no MongoDB
   - Connection pooling
   - Query optimization

---

Esta arquitetura garante alta performance, escalabilidade e manutenibilidade do sistema SPD Imóveis.