# SPD Imóveis - Interface Streamlit

Interface web completa para o sistema de busca semântica de imóveis.

## Como usar

```bash
# Certifique-se de que a API está rodando
source venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8001

# Em outro terminal, inicie o Streamlit
streamlit run streamlit/app.py
```

## Funcionalidades

### Preview
- Exibe os 5 primeiros imóveis cadastrados
- Cartões com informações resumidas
- Botão para ver detalhes

### Chat Inteligente
- Busca semântica por linguagem natural
- Interface de chat intuitiva
- Resultados formatados e organizados

### Gerenciar Imóveis
- **Adicionar:** Formulário completo para novos imóveis
- **Listar:** Visualização de todos os imóveis cadastrados  
- **Editar:** Busca por ID ou título + formulário de edição
- **Excluir:** Lista com confirmação de exclusão

## Exemplos de Busca

- "apartamento 3 quartos"
- "casa com piscina"  
- "imóvel no centro"
- "apartamento barato"

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
        A[Usuário envia requisição DELETE para /imoveis/{id}] --> R{Router: imoveis.py};
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
    
    P --> LLM[API do LLM Externo<br>(ex: OpenAI, Google AI)];
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