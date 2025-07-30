# SPD Imóveis - Docker Setup

## Inicialização Completa via Docker

### Comando Único para Iniciar Tudo
```bash
docker-compose up -d
```

### Parar Sistema
```bash
docker-compose down
```

### Rebuild após Mudanças no Código
```bash
docker-compose up -d --build
```

## Serviços Disponíveis

| Serviço | Container | Porta | URL |
|---------|-----------|-------|-----|
| API | spd_api | 8000 | http://localhost:8000 |
| Streamlit | spd_streamlit | 8501 | http://localhost:8501 |
| MongoDB | mongo_db | 27017 | mongodb://localhost:27017 |
| ChromaDB | chroma_db | 7777 | http://localhost:7777 |
| Redis | redis_broker | 6379 | redis://localhost:6379 |
| Worker | spd_worker | - | Background |

## Arquitetura do Sistema

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Streamlit  │────│     API     │────│   Worker    │
│    :8501    │    │    :8000    │    │ (background)│
└─────────────┘    └─────────────┘    └─────────────┘
                           │                   │
                   ┌───────┴───────┐          │
                   │               │          │
            ┌──────▼──────┐ ┌──────▼──────┐   │
            │   MongoDB   │ │   ChromaDB  │   │
            │    :27017   │ │    :7777    │   │
            └─────────────┘ └─────────────┘   │
                                              │
                           ┌──────────────────┘
                           │
                    ┌──────▼──────┐
                    │    Redis    │
                    │    :6379    │
                    └─────────────┘
```

## Fluxos do Sistema

### Fluxo de Busca Semântica

```mermaid
graph TD
    A[Usuário envia query de busca<br>ex: apartamento com varanda gourmet<br>para /search] --> R{Router: search.py};
    R --> SS[Search Service];
    SS --> ES[Embedding Service: Transforma a<br>query do usuário em um vetor];
    ES --> VQ[Vetor da Query];
    SS --> VQ;
    VQ --> CR[Chroma Repository: Busca por similaridade<br>no ChromaDB usando o vetor da query];
    CR --> ChromaDB[(ChromaDB)];
    ChromaDB --> CR;
    CR --> ID_List[Retorna lista de IDs<br>de imóveis mais similares];
    ID_List --> SS;
    SS --> MR[Mongo Repository: Busca os dados<br>completos dos imóveis usando os IDs];
    MR --> MongoDB[(MongoDB)];
    MongoDB --> MR;
    MR --> Results[Resultados Completos];
    Results --> R;
    R --> RESP[API Retorna a lista de imóveis];
```

### Fluxo de Inserção/Atualização de Imóveis

```mermaid
graph TD
    subgraph API
        A[Usuário/Crawler envia dados do imóvel via POST/PUT para /imoveis] --> R{Router: imoveis.py};
        R --> S1[Service: Salva/Atualiza dados no MongoDB];
        S1 --> MB[Message Broker Service: Publica mensagem<br>ex: imovel_criado ou imovel_atualizado];
        MB --> RESP[API Retorna 200 OK / 202 Accepted];
    end

    subgraph Background_Worker
        W[Worker consome a mensagem da fila<br>create_worker.py / update_worker.py];
        MB --> W;
        W --> ES[Embedding Service: Gera o vetor<br>semântico da descrição do imóvel];
        ES --> IS[Indexing Service: Salva o ID do imóvel<br>e seu vetor no ChromaDB];
    end

    subgraph Bancos de Dados
        S1 --> MongoDB[(MongoDB<br>Dados textuais e numéricos)];
        IS --> ChromaDB[(ChromaDB<br>Vetor Semântico)];
    end
```

### Fluxo de Deleção de Imóveis

```mermaid
graph TD
    subgraph API
        A[Usuário envia requisição DELETE para /imoveis/id] --> R{Router: imoveis.py};
        R --> MB[Message Broker Service: Publica mensagem<br>ex: imovel_deletado];
        MB --> RESP[API Retorna 200 OK / 202 Accepted];
    end

    subgraph Background_Worker
        W[Worker consome a mensagem da fila<br>delete_worker.py];
        MB --> W;
        W --> D1[Repositório: Remove do MongoDB];
        W --> D2[Repositório: Remove do ChromaDB];
    end

    subgraph Bancos de Dados
        D1 --> MongoDB[(MongoDB)];
        D2 --> ChromaDB[(ChromaDB)];
    end
```

### Fluxo de Reranking com LLM

```mermaid
graph TD
    A[Início: Resultados da Busca Semântica] --> LRS[LLM Reranking Service];
    B[Query Original do Usuário] --> LRS;
    
    LRS --> P[Formata um prompt para o LLM contendo a query<br>e os detalhes dos imóveis encontrados];
    
    P --> LLM[API do LLM Externo<br> ex: OpenAI, Google AI ];
    LLM --> Reordered[LLM retorna a lista de imóveis<br>reordenada pela relevância percebida];
    
    Reordered --> FS[Final Service / Router];
    FS --> RESP[API Retorna a lista final<br>re-ranqueada para o usuário];

```

### Fluxo CRUD de Cidades e Corretores

```mermaid
graph TD
    A[Usuário envia requisição<br/>POST/PUT/GET/DELETE para<br/>/cidades ou /corretores] --> R{Router: cidades.py / corretores.py}
    R --> S[Service: Valida os dados e chama o repositório]
    S --> REPO{Mongo Repository}
    REPO --> DB[(MongoDB)]
    DB --> REPO
    REPO --> S
    S --> R
    R --> RESP[API Retorna a resposta<br/>200, 201, 404, etc]
```

## Volumes Persistentes

- `mongo_data`: Dados do MongoDB
- `chroma_data`: Dados do ChromaDB  
- `redis_data`: Dados do Redis
- `./chroma_db`: ChromaDB local (desenvolvimento)
- `./models`: Modelos de ML

## Health Checks

Todos os serviços possuem health checks configurados:
- **MongoDB**: `mongosh --eval "db.adminCommand('ping')"`
- **ChromaDB**: `curl -f http://localhost:7777/api/v1/heartbeat`
- **Redis**: `redis-cli ping`
- **API**: `curl -f http://localhost:8000/`

## Logs dos Containers

```bash
# Ver logs de todos os serviços
docker-compose logs -f

# Ver logs de um serviço específico
docker-compose logs -f api
docker-compose logs -f worker
docker-compose logs -f streamlit
```

## Comandos Úteis

```bash
# Status dos containers
docker-compose ps

# Rebuild apenas um serviço
docker-compose up -d --build api

# Executar comando em container
docker-compose exec api bash
docker-compose exec mongodb mongosh

# Limpar volumes (CUIDADO: perde dados)
docker-compose down -v
```

## Diferenças dos Scripts Python

Os scripts `start_system.py` e `stop_system.py` não são mais necessários. Todo o gerenciamento é feito pelo Docker Compose:

- ✅ **Antes**: `python start_system.py`
- ✅ **Agora**: `docker-compose up -d`

- ✅ **Antes**: `python stop_system.py`  
- ✅ **Agora**: `docker-compose down`

## Troubleshooting

### Container não inicia
```bash
docker-compose logs [service_name]
```

### Portas ocupadas
```bash
# Verificar o que está usando a porta
lsof -i :8000
lsof -i :8501
```

### Reset completo
```bash
docker-compose down -v
docker system prune -f
docker-compose up -d --build
```