Relatório Individual

Discente: Pedro Campos

Entrega 1

Nesta entrega, foquei na implementação do serviço de embedding e na integração com o banco de dados vetorial ChromaDB. As principais atividades realizadas foram:

* **Criação do Modelo de Dados:** Defini o modelo `Article` em `src/app/models.py` para representar a estrutura dos artigos que serão armazenados e indexados.

* **Implementação dos Serviços:**
    * Criei o `EmbeddingService` em `src/app/services/embedding_service.py` para gerar os embeddings dos textos.
    * Desenvolvi o `IndexingService` em `src/app/services/indexing_service.py` para orquestrar a indexação dos artigos no ChromaDB.
    * Implementei o `SearchService` em `src/app/services/search_service.py` para realizar buscas semânticas nos artigos indexados.

* **Repositório do ChromaDB:** Criei o `ChromaRepository` em `src/app/repositories/chroma_repository.py` para encapsular a lógica de interação com o ChromaDB.

* **Configuração e Integração:**
    * Adicionei as configurações do MongoDB e do ChromaDB em `src/app/config.py`.
    * Criei funções em `src/app/database.py` para gerenciar as conexões com os bancos de dados.
    * Atualizei os roteadores da aplicação (`src/app/routers/articles.py` e `src/app/routers/search.py`) para utilizar os novos serviços e repositórios.

* **Gerenciamento de Dependências:** Criei o arquivo `requirements.txt` para listar todas as dependências do projeto.

Com essas implementações, a aplicação agora é capaz de receber artigos, gerar embeddings para seus conteúdos, indexá-los no ChromaDB e realizar buscas baseadas em similaridade semântica. Acredito que essa base sólida permitirá a evolução do projeto para funcionalidades mais avançadas nas próximas entregas.

## Entrega 2

Na segunda entrega, concentrei meus esforços na implementação do sistema de reranking inteligente utilizando Large Language Models (LLM) e na criação de uma infraestrutura completa de setup automático. As principais atividades realizadas foram:

* **Sistema de Reranking com LLM:** Implementei o `LLMRerankingService` em `src/app/services/llm_reranking_service.py` que utiliza o modelo Gemma3 4B através do Ollama para realizar reordenação inteligente dos resultados de busca baseado no feedback do usuário (curtidas e descurtidas).

* **Integração com Ollama Local:** Criei o `OllamaHealthService` em `src/app/services/ollama_health_service.py` para monitoramento e inicialização automática do serviço Ollama, garantindo disponibilidade contínua do modelo LLM.

* **Sistema de Setup Automático:** Desenvolvi o script `setup.sh` que automatiza completamente a inicialização do projeto, incluindo:
    * Verificação de pré-requisitos (Docker, Ollama, recursos do sistema)
    * Detecção automática de versões do Docker Compose
    * Download e configuração do modelo Gemma3 4B
    * Inicialização orquestrada de todos os serviços

* **Script de Carregamento de Dados:** Implementei o `docker_seed.py` para carregamento automático e limpo dos 200 imóveis da pasta anuncios_salvos, com limpeza prévia dos dados duplicados no MongoDB e ChromaDB.

* **Configuração de Rede Host:** Reconfigurei o `docker-compose.yml` para utilizar host networking nos containers API e Streamlit, permitindo conectividade direta com o Ollama local sem containerização adicional.

* **Endpoints de Limpeza:** Adicionei endpoints `/imoveis/all` e `/search/clear` nos roteadores para limpeza completa dos dados no MongoDB e ChromaDB, facilitando reiniializações limpas do sistema.

* **Arquitetura de Repositórios:** Refatorei os repositórios `MongoRepository` e `ChromaRepository` para suportar tanto conexões HTTP quanto locais, melhorando a flexibilidade de deployment.

O sistema agora oferece uma experiência completa de busca semântica com reranking inteligente por LLM, onde o usuário pode curtir/descurtir imóveis e o modelo Gemma3 4B aprende suas preferências para reordenar os resultados futuros. A infraestrutura de setup permite que qualquer desenvolvedor clone o repositório e tenha o sistema funcionando em minutos através de um único comando.
