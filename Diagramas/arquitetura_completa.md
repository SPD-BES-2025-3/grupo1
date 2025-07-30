# 🏗️ Arquitetura Completa - Sistema de Busca Semântica para Imóveis

## 📊 Diagrama da Solução Completa

```mermaid
graph TB
    %% Frontend Layer
    UI[🖥️ Streamlit Frontend]
    CHAT[💬 Chat Interface]
    MANAGE[⚙️ Gerenciar Imóveis]
    PREVIEW[📋 Preview Imóveis]

    %% API Layer
    API[🔌 FastAPI Backend<br/>Port 8001]
    
    %% Routers
    SEARCH_ROUTER[🔍 Search Router<br/>/search/ /rerank/]
    IMOVEL_ROUTER[🏠 Imóveis Router<br/>/imoveis/]
    
    %% Services Layer
    SEARCH_SERVICE[🔍 Search Service<br/>Semantic Search]
    EMBEDDING_SERVICE[🧠 Embedding Service<br/>SentenceTransformers]
    INDEXING_SERVICE[📚 Indexing Service<br/>Sync DBs]
    LLM_SERVICE[🤖 LLM Reranking Service<br/>Ollama + Gemma3]
    
    %% Repository Layer
    MONGO_REPO[📄 MongoDB Repository<br/>Text Storage]
    CHROMA_REPO[🎯 ChromaDB Repository<br/>Vector Storage]
    
    %% Database Layer
    MONGO[(🍃 MongoDB<br/>spd_imoveis)]
    CHROMA[(🎯 ChromaDB<br/>./chroma_db)]
    
    %% External Services
    OLLAMA[🦙 Ollama Server<br/>Port 11434<br/>gemma3:latest]
    
    %% Frontend Connections
    UI --> CHAT
    UI --> MANAGE
    UI --> PREVIEW
    
    %% API Connections
    CHAT --> API
    MANAGE --> API
    PREVIEW --> API
    
    %% Router Layer
    API --> SEARCH_ROUTER
    API --> IMOVEL_ROUTER
    
    %% Service Connections
    SEARCH_ROUTER --> SEARCH_SERVICE
    SEARCH_ROUTER --> LLM_SERVICE
    IMOVEL_ROUTER --> INDEXING_SERVICE
    
    SEARCH_SERVICE --> EMBEDDING_SERVICE
    SEARCH_SERVICE --> MONGO_REPO
    SEARCH_SERVICE --> CHROMA_REPO
    
    LLM_SERVICE --> OLLAMA
    LLM_SERVICE --> MONGO_REPO
    
    INDEXING_SERVICE --> EMBEDDING_SERVICE
    INDEXING_SERVICE --> MONGO_REPO
    INDEXING_SERVICE --> CHROMA_REPO
    
    %% Repository to Database
    MONGO_REPO --> MONGO
    CHROMA_REPO --> CHROMA
    
    %% Styling
    classDef frontend fill:#e1f5fe
    classDef api fill:#f3e5f5
    classDef service fill:#e8f5e8
    classDef repository fill:#fff3e0
    classDef database fill:#ffebee
    classDef external fill:#f1f8e9
    
    class UI,CHAT,MANAGE,PREVIEW frontend
    class API,SEARCH_ROUTER,IMOVEL_ROUTER api
    class SEARCH_SERVICE,EMBEDDING_SERVICE,INDEXING_SERVICE,LLM_SERVICE service
    class MONGO_REPO,CHROMA_REPO repository
    class MONGO,CHROMA database
    class OLLAMA external
```

## 🔄 Fluxo 1: Chat com Busca Semântica + Re-ranking LLM

```mermaid
sequenceDiagram
    participant U as 👤 Usuário
    participant ST as 🖥️ Streamlit
    participant API as 🔌 FastAPI
    participant SS as 🔍 Search Service
    participant ES as 🧠 Embedding Service
    participant CR as 🎯 ChromaDB Repo
    participant MR as 📄 MongoDB Repo
    participant LLM as 🤖 LLM Service
    participant OL as 🦙 Ollama
    
    %% Busca Inicial
    U->>ST: "preciso de casa perto de escola"
    ST->>API: GET /search?query=...&n_results=10
    API->>SS: search(query, 10)
    SS->>ES: create_embeddings([query])
    ES-->>SS: [embedding_vector]
    SS->>CR: query(embeddings, 10)
    CR-->>SS: {ids: [id1,id2...id10]}
    SS->>MR: get_imovel_by_id(id) for each
    MR-->>SS: [full_properties_data]
    SS-->>API: 10 properties
    API-->>ST: {results: [10 properties]}
    
    %% Mostrar 5 + Interface Feedback
    ST->>ST: Divide: 5 para mostrar, 5 reserva
    ST-->>U: Mostra 5 imóveis + botões 👍👎
    
    %% Feedback do Usuário
    U->>ST: 👍 imóvel A, 👎 imóvel B
    U->>ST: Clica "🚀 Melhorar Busca com IA"
    
    %% Re-ranking com LLM
    ST->>API: POST /rerank/ {liked: [A], disliked: [B], remaining: [5 restantes]}
    API->>LLM: rerank_properties(feedback)
    LLM->>LLM: _build_prompt(analysis_prompt)
    LLM->>OL: POST /api/generate {model: gemma3, prompt}
    OL-->>LLM: {response: "JSON decision"}
    LLM->>LLM: _parse_llm_response()
    LLM-->>API: {selected_properties: [id3, id7], reasoning}
    API->>MR: get_full_data(selected_ids)
    MR-->>API: [enhanced_results]
    API-->>ST: {reranked_results: [2-4 properties], reasoning}
    ST-->>U: "🤖 IA selecionou X imóveis baseado em seus gostos"
```

## 🏠 Fluxo 2: Gerenciamento de Imóveis (CRUD)

```mermaid
sequenceDiagram
    participant U as 👤 Usuário
    participant ST as 🖥️ Streamlit
    participant API as 🔌 FastAPI
    participant IS as 📚 Indexing Service
    participant ES as 🧠 Embedding Service
    participant MR as 📄 MongoDB Repo
    participant CR as 🎯 ChromaDB Repo
    participant M as 🍃 MongoDB
    participant C as 🎯 ChromaDB
    
    %% Adicionar Imóvel
    rect rgb(230, 255, 230)
        note over U,C: ➕ ADICIONAR IMÓVEL
        U->>ST: Preenche formulário (título, descrição, specs)
        ST->>API: POST /imoveis/ {imovel_data}
        API->>MR: add_imovel(data)
        MR->>M: insert_one(document)
        M-->>MR: {inserted_id: "abc123"}
        MR-->>API: "abc123"
        
        %% Indexação Automática
        API->>IS: index_single_imovel(imovel_with_id)
        IS->>ES: create_embeddings([content])
        ES-->>IS: [embedding_vector]
        IS->>CR: upsert_documents(id, content, metadata)
        CR->>C: Store vector + metadata
        C-->>CR: ✅
        CR-->>IS: ✅
        IS-->>API: ✅
        API-->>ST: {status: 200, id: "abc123"}
        ST-->>U: "✅ Imóvel adicionado com sucesso!"
    end
    
    %% Editar Imóvel
    rect rgb(255, 245, 230)
        note over U,C: ✏️ EDITAR IMÓVEL
        U->>ST: Busca por ID/título
        ST->>API: GET /imoveis/
        API->>MR: get_all_imoveis()
        MR-->>API: [all_properties]
        API-->>ST: [properties]
        ST->>ST: Filtra por critério
        ST-->>U: Mostra formulário preenchido
        
        U->>ST: Modifica dados + "💾 Salvar"
        ST->>API: PUT /imoveis/{id} {updated_data}
        API->>MR: update_imovel(id, data)
        MR->>M: update_one({_id}, {$set: data})
        M-->>MR: ✅
        MR-->>API: updated_imovel
        
        %% Re-indexação
        API->>IS: index_single_imovel(updated_imovel)
        IS->>ES: create_embeddings([new_content])
        ES-->>IS: [new_embedding]
        IS->>CR: upsert_documents(same_id, new_content)
        CR->>C: Update vector + metadata
        IS-->>API: ✅
        API-->>ST: {status: 200}
        ST-->>U: "✅ Imóvel atualizado!"
    end
    
    %% Excluir Imóvel
    rect rgb(255, 230, 230)
        note over U,C: 🗑️ EXCLUIR IMÓVEL
        U->>ST: Lista imóveis + "🗑️ Excluir"
        ST->>ST: Confirmação "Tem certeza?"
        U->>ST: "✅ Sim, excluir"
        ST->>API: DELETE /imoveis/{id}
        API->>MR: delete_imovel(id)
        MR->>M: delete_one({_id: id})
        M-->>MR: ✅
        
        %% Remover do índice
        API->>IS: delete_imovel_from_index(id)
        IS->>CR: delete_document(id)
        CR->>C: Remove vector + metadata
        IS-->>API: ✅
        API-->>ST: {status: 200}
        ST-->>U: "✅ Imóvel excluído!"
    end
```

## 🧠 Componentes da Arquitetura

### 🎨 **Frontend Layer (Streamlit)**
- **Chat Interface**: Busca conversacional + feedback system
- **Gerenciar Imóveis**: CRUD completo (Create, Read, Update, Delete)
- **Preview**: Visualização dos primeiros 5 imóveis

### 🔌 **API Layer (FastAPI)**
- **Search Router**: `/search/` (busca semântica) + `/rerank/` (LLM re-ranking)
- **Imóveis Router**: `/imoveis/` (CRUD operations)

### ⚙️ **Services Layer**
- **Search Service**: Orquestra busca semântica (ChromaDB → MongoDB)
- **Embedding Service**: SentenceTransformers (all-MiniLM-L6-v2)
- **Indexing Service**: Sincronização MongoDB ↔ ChromaDB
- **LLM Reranking Service**: Integração Ollama + Gemma3

### 🗃️ **Repository Layer**
- **MongoDB Repository**: CRUD text data
- **ChromaDB Repository**: Vector operations

### 💾 **Database Layer**
- **MongoDB**: Armazenamento de texto (título, descrição, especificações)
- **ChromaDB**: Armazenamento de vetores + metadata

### 🤖 **External Services**
- **Ollama Server**: Servidor LLM local (Gemma3:latest)

## 🔑 Características Arquiteturais

### ✅ **Clean Architecture**
- **Dependency Inversion**: Services dependem de abstrações (repositories)
- **Single Responsibility**: Cada camada tem responsabilidade específica
- **Separation of Concerns**: Frontend, API, Business Logic, Data isolados

### 🚀 **Performance & Scalability**
- **Dual Database**: MongoDB (text) + ChromaDB (vectors) otimizado para cada tipo
- **Embedding Cache**: Vetores pré-computados para busca rápida
- **Async Operations**: FastAPI com async/await

### 🔒 **Reliability**
- **Fallback Mechanisms**: TF-IDF quando embeddings falham
- **Error Handling**: Try/catch em todas as camadas
- **Data Consistency**: Transações sincronizadas entre MongoDB e ChromaDB

### 🧪 **AI Integration**
- **Semantic Search**: SentenceTransformers para similaridade semântica
- **LLM Re-ranking**: Gemma3 para análise de preferências
- **Human-in-the-loop**: Feedback explícito para melhoria contínua

## 📈 Fluxo de Dados

1. **Ingestão**: Seed → MongoDB → Embedding → ChromaDB
2. **Busca**: Query → Embedding → ChromaDB (similarity) → MongoDB (content)
3. **Feedback**: User likes/dislikes → LLM analysis → Smart selection
4. **CRUD**: Frontend → API → MongoDB + ChromaDB sync

Esta arquitetura garante **escalabilidade**, **manutenibilidade** e **performance** para um sistema de busca semântica de imóveis com re-ranking inteligente! 🏗️✨