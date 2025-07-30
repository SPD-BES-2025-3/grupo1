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
