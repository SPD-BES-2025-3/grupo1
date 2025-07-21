# grupo1
Repositório do grupo 1



## Descrição dos Componentes

### Diretório Raiz

-   **`app/`**: Contém todo o código-fonte da aplicação FastAPI. É o pacote principal do projeto.
-   **`tests/`**: Destinado a todos os testes (unitários, de integração, etc.). Mantê-los separados do código da aplicação é uma boa prática.
-   **`.env.example`**: Um arquivo de exemplo que mostra quais variáveis de ambiente são necessárias para executar o projeto. Nunca deve conter dados sensíveis.
-   **`.gitignore`**: Especifica arquivos e diretórios que o Git deve ignorar (ex: ambientes virtuais, arquivos de cache, `.env`).
-   **`main.py`**: O ponto de entrada da aplicação. É aqui que a instância principal do FastAPI é criada e os roteadores são incluídos.
-   **`requirements.txt`**: Lista todas as dependências Python do projeto, permitindo uma fácil instalação com `pip install -r requirements.txt`.
-   **`seed.py`**: Um script utilitário para popular os bancos de dados com dados de exemplo, útil para testes e demonstrações.
-   **`README.md`**: Este arquivo, contendo a documentação principal do projeto.

### Diretório `app/`

-   **`config.py`**: Centraliza o carregamento e o gerenciamento de configurações e segredos (chaves de API, strings de conexão) a partir de variáveis de ambiente.
-   **`database.py`**: Gerencia a criação e o acesso às conexões com os bancos de dados (MongoDB e o Banco de Dados Vetorial).
-   **`models.py`**: Define os "schemas" de dados da aplicação usando Pydantic, garantindo a validação, serialização e documentação automática dos dados.
-   **`repositories/`**: Camada de acesso a dados. Contém a lógica de baixo nível para interagir diretamente com os bancos de dados (ex: `pymongo` para fazer queries).
-   **`services/`**: Camada de serviço (lógica de negócio). Orquestra as operações, utilizando os repositórios e outros serviços para executar tarefas complexas (ex: `IndexingService` usa o repositório e o serviço de embedding).
-   **`routers/`**: Define os endpoints (rotas) da API. Cada arquivo agrupa endpoints relacionados (ex: `articles.py` para tudo relacionado a artigos), mantendo o `main.py` limpo e organizado.
